---
id: delivery-guarantees
sidebar_position: 2
title: Garantías de Entrega
description: Estándar para garantías de entrega en mensajería Kafka: at-most-once, at-least-once y exactly-once con idempotent producer y transactional consumer
---

# Estándar Técnico — Garantías de Entrega

---

## 1. Propósito

Definir garantías de entrega de mensajes en Apache Kafka: at-most-once (puede perderse), at-least-once (puede duplicarse) y exactly-once (entrega exacta una vez), implementando idempotent producers, transactional consumers y deduplication keys.

---

## 2. Alcance

**Aplica a:**

- Productores de eventos Kafka
- Consumidores de eventos Kafka
- Pipelines de procesamiento de eventos
- Integraciones asíncronas

**No aplica a:**

- Comunicación síncrona HTTP (request/response)
- Notificaciones fire-and-forget

---

## 3. Tecnologías Aprobadas

| Componente         | Tecnología         | Versión mínima | Observaciones  |
| ------------------ | ------------------ | -------------- | -------------- |
| **Message Broker** | Apache Kafka Kraft | 3.5+           | Self-managed   |
| **Producer**       | Confluent.Kafka    | 2.3+           | .NET client    |
| **Consumer**       | Confluent.Kafka    | 2.3+           | .NET client    |
| **Idempotency**    | Deduplication keys | -              | CloudEvents.id |
| **Transactions**   | Kafka transactions | -              | Exactly-once   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Semánticas de Entrega

- [ ] **At-least-once**: Por defecto para eventos críticos
- [ ] **Exactly-once**: Para operaciones financieras/transaccionales
- [ ] **NO at-most-once**: Evitar para datos importantes

### Productores

- [ ] **Idempotent producer**: `enable.idempotence=true`
- [ ] **Acks=all**: Esperar confirmación de todas las réplicas
- [ ] **Retry infinite**: `retries=int.MaxValue` con backoff
- [ ] **Message key**: Usar para ordenamiento por partición

### Consumidores

- [ ] **Manual commit**: `enable.auto.commit=false`
- [ ] **Commit after processing**: Solo después de éxito
- [ ] **Deduplication**: Validar `CloudEvents.id` procesado
- [ ] **Idempotent processing**: Operaciones retry-safe

### Transaccional (Exactly-Once)

- [ ] **Transactional ID**: Único por producer
- [ ] **Read committed**: Consumidores solo leen transacciones completas
- [ ] **Atomic operations**: Consume-Transform-Produce en transacción

---

## 5. At-Least-Once (Más Común)

### Producer - Idempotent

```csharp
// Services/KafkaProducerService.cs
public class KafkaProducerService
{
    private readonly IProducer<string, string> _producer;

    public KafkaProducerService(IConfiguration configuration)
    {
        var config = new ProducerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],

            // At-least-once configuration
            Acks = Acks.All,                    // Esperar confirmación de todas las réplicas
            EnableIdempotence = true,            // Evitar duplicados en retry
            MaxInFlight = 5,                     // Max requests in-flight

            // Retry configuration
            MessageSendMaxRetries = int.MaxValue,  // Retry infinito
            RetryBackoffMs = 100,                   // 100ms initial backoff
            RequestTimeoutMs = 30000,               // 30s timeout

            // Compression
            CompressionType = CompressionType.Snappy,

            // Client ID
            ClientId = $"payment-service-{Environment.MachineName}"
        };

        _producer = new ProducerBuilder<string, string>(config)
            .SetErrorHandler((_, e) => Console.WriteLine($"Error: {e.Reason}"))
            .Build();
    }

    public async Task<DeliveryResult<string, string>> ProduceAsync(
        string topic,
        string key,
        string message)
    {
        try
        {
            var result = await _producer.ProduceAsync(
                topic,
                new Message<string, string>
                {
                    Key = key,        // Importante: Para ordenamiento en partición
                    Value = message,
                    Headers = new Headers
                    {
                        { "correlation-id", Encoding.UTF8.GetBytes(Guid.NewGuid().ToString()) }
                    }
                });

            return result;
        }
        catch (ProduceException<string, string> e)
        {
            // Log error y propagar (retry en capa superior)
            Console.WriteLine($"Failed to deliver message: {e.Error.Reason}");
            throw;
        }
    }
}
```

### Consumer - Manual Commit After Processing

```csharp
// Workers/PaymentEventConsumer.cs
public class PaymentEventConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IPaymentService _paymentService;

    public PaymentEventConsumer(IConfiguration configuration, IPaymentService paymentService)
    {
        var config = new ConsumerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],
            GroupId = "payment-service",

            // At-least-once configuration
            EnableAutoCommit = false,            // Manual commit
            AutoOffsetReset = AutoOffsetReset.Earliest,

            // Performance
            FetchMinBytes = 1,
            FetchWaitMaxMs = 500,

            // Security
            SecurityProtocol = SecurityProtocol.Plaintext  // En prod: usar SSL
        };

        _consumer = new ConsumerBuilder<string, string>(config).Build();
        _paymentService = paymentService;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("payment.created");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var consumeResult = _consumer.Consume(stoppingToken);

                // Procesar mensaje
                await ProcessMessageAsync(consumeResult.Message.Value);

                // ✅ COMMIT solo después de procesamiento exitoso
                _consumer.Commit(consumeResult);

                Console.WriteLine($"Committed offset {consumeResult.Offset}");
            }
            catch (ConsumeException e)
            {
                Console.WriteLine($"Consume error: {e.Error.Reason}");
                // NO commit, retry en siguiente poll
            }
            catch (Exception e)
            {
                Console.WriteLine($"Processing error: {e.Message}");
                // NO commit, retry en siguiente poll
                await Task.Delay(1000, stoppingToken);  // Backoff antes de retry
            }
        }

        _consumer.Close();
    }

    private async Task ProcessMessageAsync(string message)
    {
        // Deduplicar usando CloudEvents.id
        var cloudEvent = JsonSerializer.Deserialize<CloudEvent>(message);

        if (await _paymentService.IsEventProcessedAsync(cloudEvent.Id))
        {
            Console.WriteLine($"Event {cloudEvent.Id} already processed, skipping");
            return;  // Idempotencia: ya procesado
        }

        // Procesar evento
        await _paymentService.ProcessPaymentAsync(cloudEvent);

        // Registrar como procesado
        await _paymentService.MarkEventAsProcessedAsync(cloudEvent.Id);
    }
}
```

---

## 6. Exactly-Once (Transaccional)

### Transactional Producer

```csharp
// Services/TransactionalKafkaProducer.cs
public class TransactionalKafkaProducer
{
    private readonly IProducer<string, string> _producer;

    public TransactionalKafkaProducer(IConfiguration configuration)
    {
        var config = new ProducerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],

            // Exactly-once configuration
            TransactionalId = $"payment-service-{Guid.NewGuid()}",  // Único por instancia
            EnableIdempotence = true,
            Acks = Acks.All,
            MaxInFlight = 5
        };

        _producer = new ProducerBuilder<string, string>(config).Build();

        // Inicializar transacciones
        _producer.InitTransactions(TimeSpan.FromSeconds(30));
    }

    public async Task ProduceTransactionalAsync(
        string topic,
        string key,
        string message)
    {
        _producer.BeginTransaction();

        try
        {
            // Producir mensaje dentro de transacción
            await _producer.ProduceAsync(
                topic,
                new Message<string, string> { Key = key, Value = message });

            // Commit transacción
            _producer.CommitTransaction();
        }
        catch (Exception e)
        {
            // Rollback en caso de error
            _producer.AbortTransaction();
            throw;
        }
    }
}
```

### Transactional Consumer (Consume-Transform-Produce)

```csharp
// Pattern: Leer de topic A, procesar y escribir a topic B en transacción
public async Task ConsumeTransformProduceAsync()
{
    var consumerConfig = new ConsumerConfig
    {
        GroupId = "payment-processor",
        BootstrapServers = _configuration["Kafka:BootstrapServers"],
        EnableAutoCommit = false,
        IsolationLevel = IsolationLevel.ReadCommitted  // Solo leer transacciones completas
    };

    var producerConfig = new ProducerConfig
    {
        BootstrapServers = _configuration["Kafka:BootstrapServers"],
        TransactionalId = "payment-processor-txn",
        EnableIdempotence = true
    };

    using var consumer = new ConsumerBuilder<string, string>(consumerConfig).Build();
    using var producer = new ProducerBuilder<string, string>(producerConfig).Build();

    producer.InitTransactions(TimeSpan.FromSeconds(30));
    consumer.Subscribe("payment.requested");

    while (true)
    {
        var consumeResult = consumer.Consume();

        // Iniciar transacción
        producer.BeginTransaction();

        try
        {
            // 1. Procesar mensaje
            var processedEvent = ProcessPayment(consumeResult.Message.Value);

            // 2. Producir resultado a otro topic
            await producer.ProduceAsync(
                "payment.processed",
                new Message<string, string>
                {
                    Key = consumeResult.Message.Key,
                    Value = processedEvent
                });

            // 3. Commit offsets del consumer dentro de transacción
            producer.SendOffsetsToTransaction(
                new[] { new TopicPartitionOffset(consumeResult.TopicPartition, consumeResult.Offset + 1) },
                consumer.ConsumerGroupMetadata,
                TimeSpan.FromSeconds(30));

            // 4. Commit transacción (atómico: consume + produce)
            producer.CommitTransaction();
        }
        catch (Exception e)
        {
            // Rollback: no se commitea offset ni se produce mensaje
            producer.AbortTransaction();
            Console.WriteLine($"Transaction aborted: {e.Message}");
        }
    }
}
```

---

## 7. Deduplication - PostgreSQL

### Tabla de Eventos Procesados

```sql
CREATE TABLE processed_events (
    event_id VARCHAR(255) PRIMARY KEY,  -- CloudEvents.id (UUID v7)
    event_type VARCHAR(100) NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tenant_id VARCHAR(2) NOT NULL,

    CONSTRAINT chk_event_id_uuid CHECK (event_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
);

CREATE INDEX idx_processed_events_tenant ON processed_events(tenant_id, processed_at);

-- TTL: Eliminar eventos procesados > 30 días
CREATE INDEX idx_processed_events_ttl ON processed_events(processed_at) WHERE processed_at < NOW() - INTERVAL '30 days';
```

### .NET - Check Deduplication

```csharp
public async Task<bool> IsEventProcessedAsync(string eventId)
{
    return await _dbContext.ProcessedEvents
        .AnyAsync(e => e.EventId == eventId);
}

public async Task MarkEventAsProcessedAsync(string eventId, string eventType, string tenantId)
{
    _dbContext.ProcessedEvents.Add(new ProcessedEvent
    {
        EventId = eventId,
        EventType = eventType,
        ProcessedAt = DateTime.UtcNow,
        TenantId = tenantId
    });

    await _dbContext.SaveChangesAsync();
}
```

---

## 8. Comparación de Semánticas

| Semántica         | Garantía             | Duplicados | Pérdidas   | Complejidad | Uso Recomendado             |
| ----------------- | -------------------- | ---------- | ---------- | ----------- | --------------------------- |
| **At-most-once**  | Entrega 0 o 1 vez    | ❌ No      | ✅ Posible | Baja        | Logs, métricas              |
| **At-least-once** | Entrega ≥1 vez       | ✅ Posible | ❌ No      | Media       | Eventos negocio (con dedup) |
| **Exactly-once**  | Entrega exacta 1 vez | ❌ No      | ❌ No      | Alta        | Transacciones financieras   |

---

## 9. Validación de Cumplimiento

```bash
# Verificar idempotent producer habilitado
kafka-configs.sh --bootstrap-server localhost:9092 \
  --describe --entity-type brokers --all | grep idempotence

# Verificar transactional IDs
kafka-transactions.sh --bootstrap-server localhost:9092 --list

# Monitorear consumer lag (at-least-once: lag debe ser bajo)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group payment-service

# Test: Producir evento duplicado
echo '{"id":"test-123","type":"payment.created"}' | \
  kafka-console-producer.sh --topic payment.created --bootstrap-server localhost:9092

# Verificar deduplicación en BD
psql -h localhost -U app_user -d app_db <<EOF
SELECT COUNT(*) FROM processed_events WHERE event_id = 'test-123';
-- Esperado: 1 (solo una vez procesado)
EOF
```

---

## 10. Referencias

**Kafka:**

- [Kafka Delivery Semantics](https://kafka.apache.org/documentation/#semantics)
- [Exactly-Once Semantics](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
- [Idempotent Producer](https://kafka.apache.org/documentation/#producerconfigs_enable.idempotence)

**Patterns:**

- [Transactional Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)
