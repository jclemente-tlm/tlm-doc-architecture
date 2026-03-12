---
id: dead-letter-queue
sidebar_position: 8
title: Dead Letter Queue
description: Estándares para implementar Dead Letter Queue (DLQ) en Kafka y manejar mensajes fallidos con retry policy.
tags: [mensajeria, kafka, dlq, dead-letter-queue, retry]
---

# Dead Letter Queue

## Contexto

Este estándar define cómo implementar Dead Letter Queue (DLQ) para manejar mensajes Kafka que fallan consistentemente después de múltiples reintentos. Cubre retry policy, estructura de mensajes DLQ, monitoreo y estrategias de reprocesamiento. Complementa el lineamiento [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/comunicacion-asincrona-y-eventos.md).

---

## Stack Tecnológico

| Componente            | Tecnología           | Versión | Uso                           |
| --------------------- | -------------------- | ------- | ----------------------------- |
| **Message Broker**    | Apache Kafka (Kraft) | 3.6+    | Event streaming y DLQ topics  |
| **Producer/Consumer** | Confluent.Kafka      | 2.3+    | Cliente Kafka para .NET       |
| **Retry Policy**      | Polly                | -       | Retry con backoff exponencial |
| **Monitoring**        | Grafana Stack        | -       | Alertas en DLQ                |
| **Observability**     | OpenTelemetry        | 1.7+    | Tracing de mensajes fallidos  |

---

## Dead Letter Queue

### ¿Qué es Dead Letter Queue (DLQ)?

Topic Kafka separado donde se envían mensajes que fallan consistentemente después de múltiples reintentos, evitando que bloqueen el procesamiento de mensajes subsiguientes.

**Propósito:** Aislar mensajes problemáticos (poison messages) para análisis y resolución manual, sin detener el flujo de mensajes sanos.

**Componentes clave:**

- **Retry policy**: Cuántos reintentos antes de enviar a DLQ
- **DLQ topic**: Topic separado (`{original-topic}.dlq`)
- **Error metadata**: Información del error para debugging
- **Reprocessing mechanism**: Forma de reprocesar mensajes desde DLQ

**Beneficios:**
✅ Previene poison messages de bloquear cola
✅ Preserva mensajes fallidos para análisis
✅ Permite procesamiento continuo de mensajes sanos
✅ Facilita debugging (todos los errores en un lugar)

### Implementación con Retry Policy

```csharp
using Polly;
using Polly.Retry;

public class ResilientConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IProducer<string, string> _dlqProducer;
    private readonly ILogger<ResilientConsumer> _logger;
    private readonly AsyncRetryPolicy _retryPolicy;

    public ResilientConsumer(IConfiguration configuration, ILogger<ResilientConsumer> logger)
    {
        var consumerConfig = new ConsumerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],
            GroupId = "order-processor-group",
            EnableAutoCommit = false
        };

        var producerConfig = new ProducerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"]
        };

        _consumer = new ConsumerBuilder<string, string>(consumerConfig).Build();
        _dlqProducer = new ProducerBuilder<string, string>(producerConfig).Build();
        _logger = logger;

        // Retry: 3 intentos con backoff exponencial (1s, 2s, 4s)
        _retryPolicy = Policy
            .Handle<Exception>(ex => IsRetriableException(ex))
            .WaitAndRetryAsync(
                retryCount: 3,
                sleepDurationProvider: retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                onRetry: (exception, timeSpan, retryCount, context) =>
                {
                    _logger.LogWarning(exception,
                        "Retry {RetryCount}/3 after {Delay}ms: {Message}",
                        retryCount, timeSpan.TotalMilliseconds, exception.Message);
                });
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("order.created");

        while (!stoppingToken.IsCancellationRequested)
        {
            var result = _consumer.Consume(stoppingToken);

            try
            {
                // Procesar con retry automático
                await _retryPolicy.ExecuteAsync(async () =>
                {
                    await ProcessMessageAsync(result.Message.Value);
                });

                _consumer.Commit(result);
                _logger.LogInformation("Message processed successfully: {Offset}", result.Offset.Value);
            }
            catch (Exception ex)
            {
                // Todos los retries fallaron → enviar a DLQ
                await SendToDLQAsync(result, ex);

                // Commit offset para avanzar (mensaje ya en DLQ)
                _consumer.Commit(result);

                _logger.LogError(ex, "Message sent to DLQ after max retries: {Offset}", result.Offset.Value);
            }
        }
    }

    private async Task SendToDLQAsync(ConsumeResult<string, string> result, Exception ex)
    {
        var dlqTopic = $"{result.Topic}.dlq";  // order.created.dlq

        var dlqMessage = new Message<string, string>
        {
            Key = result.Message.Key,
            Value = result.Message.Value,
            Headers = new Headers(result.Message.Headers)  // Copiar headers originales
        };

        // Agregar metadata de error
        dlqMessage.Headers.Add("dlq.original-topic", Encoding.UTF8.GetBytes(result.Topic));
        dlqMessage.Headers.Add("dlq.original-partition", BitConverter.GetBytes(result.Partition.Value));
        dlqMessage.Headers.Add("dlq.original-offset", BitConverter.GetBytes(result.Offset.Value));
        dlqMessage.Headers.Add("dlq.error-message", Encoding.UTF8.GetBytes(ex.Message));
        dlqMessage.Headers.Add("dlq.error-type", Encoding.UTF8.GetBytes(ex.GetType().Name));
        dlqMessage.Headers.Add("dlq.timestamp", Encoding.UTF8.GetBytes(DateTimeOffset.UtcNow.ToString("O")));
        dlqMessage.Headers.Add("dlq.consumer-group", Encoding.UTF8.GetBytes("order-processor-group"));

        await _dlqProducer.ProduceAsync(dlqTopic, dlqMessage);

        _logger.LogWarning("Message sent to DLQ topic {DlqTopic}: key={Key}, error={Error}",
            dlqTopic, result.Message.Key, ex.Message);
    }

    private bool IsRetriableException(Exception ex)
    {
        return ex switch
        {
            HttpRequestException => true,    // Servicio externo down
            TimeoutException => true,        // Timeout de red
            NpgsqlException => true,         // DB temporal issue
            ValidationException => false,    // Datos inválidos
            JsonException => false,          // Malformed JSON
            ArgumentException => false,      // Argumento inválido
            _ => true
        };
    }
}
```

### DLQ Message Structure

```json
{
  "key": "customer-123",
  "value": "{\"event_id\":\"...\",\"order_id\":\"..\"}",
  "headers": {
    "event-type": "order.created",
    "event-version": "2.0",
    "dlq.original-topic": "order.created",
    "dlq.original-partition": "2",
    "dlq.original-offset": "12345",
    "dlq.error-message": "Payment gateway returned 500 Internal Server Error",
    "dlq.error-type": "HttpRequestException",
    "dlq.timestamp": "2026-02-19T15:30:00Z",
    "dlq.consumer-group": "order-processor-group"
  }
}
```

### DLQ Monitoring Consumer

```csharp
// Consumer separado para monitorear DLQ y generar alertas
public class DLQMonitoringConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly ILogger<DLQMonitoringConsumer> _logger;
    private readonly IAlertService _alertService;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("*.dlq");  // Todos los topics DLQ

        while (!stoppingToken.IsCancellationRequested)
        {
            var result = _consumer.Consume(stoppingToken);

            var originalTopic = Encoding.UTF8.GetString(
                result.Message.Headers.First(h => h.Key == "dlq.original-topic").GetValueBytes());
            var errorMessage = Encoding.UTF8.GetString(
                result.Message.Headers.First(h => h.Key == "dlq.error-message").GetValueBytes());
            var errorType = Encoding.UTF8.GetString(
                result.Message.Headers.First(h => h.Key == "dlq.error-type").GetValueBytes());

            _logger.LogError(
                "DLQ message detected: topic={Topic}, original-topic={OriginalTopic}, error={ErrorType}: {ErrorMessage}",
                result.Topic, originalTopic, errorType, errorMessage);

            await _alertService.SendAlertAsync(
                $"DLQ Alert: {originalTopic}",
                $"Message failed processing: {errorMessage}");

            _consumer.Commit(result);
        }
    }
}
```

### DLQ Reprocessing

```csharp
// Herramienta para reprocesar mensajes desde DLQ
public class DLQReprocessingService
{
    private readonly IConsumer<string, string> _dlqConsumer;
    private readonly IProducer<string, string> _producer;
    private readonly ILogger<DLQReprocessingService> _logger;

    public async Task ReprocessAsync(string dlqTopic, CancellationToken cancellationToken)
    {
        _dlqConsumer.Subscribe(dlqTopic);

        var reprocessedCount = 0;
        var failedCount = 0;

        while (!cancellationToken.IsCancellationRequested)
        {
            var result = _dlqConsumer.Consume(TimeSpan.FromSeconds(5));
            if (result == null) break;  // No más mensajes

            try
            {
                var originalTopic = Encoding.UTF8.GetString(
                    result.Message.Headers.First(h => h.Key == "dlq.original-topic").GetValueBytes());

                // Republicar a topic original (sin headers DLQ)
                var message = new Message<string, string>
                {
                    Key = result.Message.Key,
                    Value = result.Message.Value,
                    Headers = new Headers(
                        result.Message.Headers.Where(h => !h.Key.StartsWith("dlq.")))
                };

                await _producer.ProduceAsync(originalTopic, message);
                _dlqConsumer.Commit(result);
                reprocessedCount++;

                _logger.LogInformation("Message reprocessed from DLQ: {Key} → {OriginalTopic}",
                    result.Message.Key, originalTopic);
            }
            catch (Exception ex)
            {
                failedCount++;
                _logger.LogError(ex, "Failed to reprocess message from DLQ: {Key}", result.Message.Key);
            }
        }

        _logger.LogInformation("DLQ reprocessing completed: {Reprocessed} reprocessed, {Failed} failed",
            reprocessedCount, failedCount);
    }
}
```

### DLQ Best Practices

**Naming convention:**

```
{original-topic}.dlq

Ejemplos:
order.created → order.created.dlq
payment.completed → payment.completed.dlq
```

**Retention:** DLQ topics deben tener retention mayor que topics principales (30 días vs 7 días).

**Reprocessing strategy:**

1. Investigar causa raíz (logs, error messages en headers)
2. Fixear el problema (deploy fix si es bug)
3. Reprocesar mensajes desde DLQ al topic original
4. Verificar éxito (monitoring)

### Terraform: Provisioning de DLQ Topics

```hcl
locals {
  main_topics = ["order.created", "payment.completed", "inventory.reserved"]
  dlq_topics  = [for topic in local.main_topics : "${topic}.dlq"]
}

resource "null_resource" "create_dlq_topics" {
  for_each = toset(local.dlq_topics)

  provisioner "local-exec" {
    command = <<-EOT
      kafka-topics.sh --create \
        --bootstrap-server ${aws_msk_cluster.kafka.bootstrap_brokers} \
        --topic ${each.value} \
        --partitions 3 \
        --replication-factor 3 \
        --config retention.ms=2592000000 \
        --config cleanup.policy=delete
    EOT
  }
  # Retention: 30 días (2592000000 ms) vs 7 días en topics normales
}
```

---

## Monitoreo y Alertas

### Métricas DLQ

```csharp
var messagesSentToDLQ = meter.CreateCounter<long>(
    "messages.dlq.sent",
    description: "Total messages sent to DLQ");

var dlqSize = meter.CreateObservableGauge<long>(
    "messages.dlq.size",
    () => GetDLQSizeAsync(),
    description: "Current number of messages in DLQ");
```

### Alertas Recomendadas

**DLQ Alerts:**

- ⚠️ **DLQ message count > 0** → Investigar causa (idealmente DLQ vacío)
- 🚨 **DLQ message count > 100** → Problema sistémico, requiere acción inmediata
- 🚨 **DLQ growth rate > 10 msgs/min** → Consumer con problema crítico

**Retry Alerts:**

- ⚠️ **Retry rate > 10%** → Alta tasa de errores transitorios
- 🚨 **Retry rate > 50%** → Servicio downstream posiblemente down

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar DLQ para todos los consumers críticos
- **MUST** usar naming convention `{original-topic}.dlq` para DLQ topics
- **MUST** implementar retry policy (mínimo 3 reintentos con backoff exponencial)
- **MUST** incluir metadata de error en headers de mensajes DLQ (`dlq.original-topic`, `dlq.error-message`, `dlq.timestamp`)
- **MUST** configurar alertas cuando mensajes llegan a DLQ
- **MUST** definir proceso para revisar y reprocesar mensajes desde DLQ

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar retention mayor en DLQ topics (30 días vs 7 días en topics normales)
- **SHOULD** distinguir entre errores retriable y non-retriable en retry policy
- **SHOULD** implementar consumer separado para monitorear DLQ topics
- **SHOULD** incluir correlation_id en eventos para rastrear mensajes desde origen hasta DLQ
- **SHOULD** logear todos los envíos a DLQ con severidad ERROR
- **SHOULD** implementar métricas para contar mensajes en DLQ por topic
- **SHOULD** documentar proceso de reprocessing de DLQ en runbooks

### MAY (Opcional)

- **MAY** implementar DLQ secundario para mensajes que fallan incluso después de reprocessing
- **MAY** usar AWS S3 para archivar mensajes DLQ antiguos (long-term storage)
- **MAY** implementar UI para visualizar mensajes en DLQ y trigger reprocessing

### MUST NOT (Prohibido)

- **MUST NOT** dejar mensajes bloqueando consumer indefinidamente (siempre enviar a DLQ después de max retries)
- **MUST NOT** perder metadata de error al enviar a DLQ (incluir stacktrace, timestamp, retry count)
- **MUST NOT** ignorar mensajes en DLQ (deben ser monitoreados y resueltos)

---

## Referencias

- [Kafka Documentation - Delivery Semantics](https://kafka.apache.org/documentation/#semantics)
- [AWS - Dead Letter Queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Polly Documentation](https://github.com/App-vNext/Polly)
- [Microsoft - Transient fault handling](https://docs.microsoft.com/en-us/azure/architecture/best-practices/transient-faults)
- [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/comunicacion-asincrona-y-eventos.md) — Lineamiento relacionado
- [Message Delivery Guarantees](./message-delivery-guarantees.md)
- [Idempotencia en Eventos](./idempotency.md)
