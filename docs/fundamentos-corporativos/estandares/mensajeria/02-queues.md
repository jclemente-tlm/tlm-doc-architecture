---
id: queues
sidebar_position: 2
title: Colas de Mensajes
description: Estándares para message queues con AWS SQS, RabbitMQ 3.12+ y patrones de retry
---

# Estándar Técnico — Colas de Mensajes

---

## 1. Propósito
Implementar colas de mensajes con AWS SQS (Standard/FIFO) o RabbitMQ 3.12+, Dead Letter Queue (DLQ) con max receives = 3, long polling (20s), consumidores idempotentes y MassTransit 8.1+ para abstracción.

---

## 2. Alcance

**Aplica a:**
- Procesamiento asíncrono (emails, reportes)
- Desacoplamiento con garantía de entrega
- Manejo de picos de carga (load leveling)
- Workflows secuenciales (FIFO queues)
- Retry automático de operaciones

**No aplica a:**
- Event-driven multi-consumidor (usar Kafka)
- Comunicación tiempo real (usar WebSockets)
- Broadcasting múltiples servicios (usar Kafka)
- Transferencia archivos (usar S3 + SQS notification)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **AWS Managed** | AWS SQS | - | Colas Standard/FIFO |
| **Cliente .NET** | AWSSDK.SQS | 3.7+ | Cliente AWS SQS |
| **On-premise** | RabbitMQ | 3.12+ | Message broker |
| **Cliente RabbitMQ** | RabbitMQ.Client | 6.6+ | Cliente .NET |
| **Abstracción** | MassTransit | 8.1+ | Framework mensajería |
| **Cliente Node.js** | amqplib | 0.10+ | Cliente RabbitMQ |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] AWS SQS Standard (alto throughput) o FIFO (orden garantizado)
- [ ] Queue naming: `{environment}-{service}-{purpose}`
- [ ] Dead Letter Queue (DLQ) con maxReceiveCount = 3
- [ ] Long polling (20s) para reducir latencia/costos
- [ ] Message envelope: messageId, timestamp, correlationId, payload
- [ ] Consumidores idempotentes (at-least-once delivery)
- [ ] Visibility timeout: 6x el tiempo de procesamiento
- [ ] Mensaje <256KB (usar S3 para payloads grandes)
- [ ] Retention: 4 días (default), 14 días (crítico)
- [ ] Monitoring con CloudWatch (ApproximateAgeOfOldestMessage, NumberOfMessagesVisible)
- [ ] FIFO para workflows secuenciales (MessageGroupId)
- [ ] MassTransit para abstracción (opcional)

---

## 5. Prohibiciones

- ❌ Queues sin DLQ configurada
- ❌ Short polling (usar long polling)
- ❌ Mensajes >256KB (usar S3 Extended Client)
- ❌ Consumidores NO idempotentes
- ❌ Visibility timeout <tiempo procesamiento
- ❌ FIFO sin MessageGroupId (pierde orden)
- ❌ Queues sin monitoring (CloudWatch)

---

## 6. Configuración Mínima

### AWS SQS - Producer (C#)
```csharp
using Amazon.SQS;
using Amazon.SQS.Model;

public class SqsPublisher
{
    private readonly IAmazonSQS _sqsClient;

    public async Task SendMessageAsync<T>(string queueUrl, T message)
    {
        var envelope = new MessageEnvelope<T>
        {
            MessageId = Guid.NewGuid().ToString(),
            Timestamp = DateTime.UtcNow,
            CorrelationId = Activity.Current?.Id ?? Guid.NewGuid().ToString(),
            Payload = message
        };

        var request = new SendMessageRequest
        {
            QueueUrl = queueUrl,
            MessageBody = JsonSerializer.Serialize(envelope),
            MessageAttributes = new Dictionary<string, MessageAttributeValue>
            {
                ["MessageType"] = new MessageAttributeValue
                {
                    DataType = "String",
                    StringValue = typeof(T).Name
                }
            }
        };

        // Para FIFO queues
        if (queueUrl.EndsWith(".fifo"))
        {
            request.MessageGroupId = "default";
            request.MessageDeduplicationId = envelope.MessageId;
        }

        await _sqsClient.SendMessageAsync(request);
    }
}
```

### AWS SQS - Consumer (C#)
```csharp
public class SqsConsumer : BackgroundService
{
    private readonly IAmazonSQS _sqsClient;
    private readonly string _queueUrl;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var request = new ReceiveMessageRequest
        {
            QueueUrl = _queueUrl,
            MaxNumberOfMessages = 10,
            WaitTimeSeconds = 20, // Long polling
            MessageAttributeNames = new List<string> { "All" },
            VisibilityTimeout = 300 // 5 minutos
        };

        while (!stoppingToken.IsCancellationRequested)
        {
            var response = await _sqsClient.ReceiveMessageAsync(request, stoppingToken);

            foreach (var message in response.Messages)
            {
                try
                {
                    // Procesamiento idempotente
                    await ProcessMessageAsync(message);

                    // Eliminar mensaje (ACK)
                    await _sqsClient.DeleteMessageAsync(_queueUrl, message.ReceiptHandle);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing message {MessageId}", message.MessageId);
                    // Mensaje irá a DLQ después de maxReceiveCount
                }
            }
        }
    }
}
```

### Terraform - SQS con DLQ
```hcl
resource "aws_sqs_queue" "orders_dlq" {
  name = "prod-orders-dlq"
  message_retention_seconds = 1209600 # 14 días
}

resource "aws_sqs_queue" "orders_queue" {
  name = "prod-orders-processing"
  visibility_timeout_seconds = 300
  message_retention_seconds = 345600 # 4 días
  receive_wait_time_seconds = 20 # Long polling
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.orders_dlq.arn
    maxReceiveCount     = 3
  })
}
```

---

## 7. Validación

```bash
# Enviar mensaje de prueba
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/prod-orders-processing \
  --message-body '{"orderId": "123"}'

# Recibir mensajes
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/prod-orders-processing \
  --max-number-of-messages 10 \
  --wait-time-seconds 20

# Ver métricas CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/SQS \
  --metric-name ApproximateNumberOfMessagesVisible \
  --dimensions Name=QueueName,Value=prod-orders-processing \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| DLQ configurada | 100% | `redrive_policy` |
| Long polling | 100% | `receive_wait_time_seconds = 20` |
| Visibility timeout | ≥6x procesamiento | CloudWatch metrics |
| Mensajes <256KB | 100% | Validación en producer |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Kafka](01-kafka-eventos.md)
- [Mensajería Asíncrona - ADR](../../decisiones-de-arquitectura/adr-012-mensajeria-asincrona.md)
- [AWS SQS Documentation](https://docs.aws.amazon.com/sqs/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [MassTransit](https://masstransit.io/)
