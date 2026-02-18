---
id: async-messaging
sidebar_position: 1
title: Mensajería Asíncrona
description: Implementación técnica de mensajería asíncrona con Apache Kafka y Transactional Outbox
---

# Mensajería Asíncrona

## Contexto

Este estándar define la implementación técnica para mensajería asíncrona entre servicios usando Apache Kafka. Complementa el [lineamiento de Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) especificando **cómo** y **con qué** tecnologías implementar la comunicación asíncrona.

**Decisión arquitectónica:** [ADR-008: Apache Kafka para mensajería asíncrona](../../../decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona.md)

---

## Stack Tecnológico

| Componente          | Tecnología           | Versión | Uso                           |
| ------------------- | -------------------- | ------- | ----------------------------- |
| **Event Streaming** | Apache Kafka (KRaft) | 3.6+    | Broker de mensajería          |
| **Cliente .NET**    | Confluent.Kafka      | 2.3+    | Producer/Consumer para .NET 8 |
| **Base de Datos**   | PostgreSQL           | 14+     | Transactional Outbox pattern  |
| **Formato**         | JSON                 | -       | Serialización de mensajes     |
| **Autenticación**   | SASL/SCRAM-SHA-512   | -       | Obligatorio en producción     |
| **Encriptación**    | TLS 1.3              | -       | Obligatorio en producción     |
| **Infraestructura** | AWS ECS Fargate      | -       | Despliegue de brokers Kafka   |
| **Secrets**         | AWS Secrets Manager  | -       | Credenciales SASL y TLS       |

### Dependencias NuGet

```xml
<PackageReference Include="Confluent.Kafka" Version="2.3.0" />
<PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />
```

---

## Patrón Transactional Outbox

Garantiza atomicidad entre operaciones de base de datos y publicación de eventos usando PostgreSQL. El evento se persiste en la misma transacción que el cambio de negocio, eliminando inconsistencias.

### 1. Tabla Outbox

```sql
CREATE TABLE outbox_events (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type    VARCHAR(100) NOT NULL,
    aggregate_id      UUID NOT NULL,
    event_type        VARCHAR(100) NOT NULL,
    event_payload     JSONB NOT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    processed_at      TIMESTAMP NULL,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    retry_count       INT NOT NULL DEFAULT 0,

    INDEX idx_processing (processing_status, created_at)
        WHERE processing_status = 'PENDING'
);
```

### 2. Modelo de Evento

```csharp
public class OutboxEvent
{
    public Guid Id { get; init; }
    public string AggregateType { get; init; } = null!;
    public Guid AggregateId { get; init; }
    public string EventType { get; init; } = null!;
    public string EventPayload { get; init; } = null!; // JSON serializado
    public DateTime CreatedAt { get; init; }
    public DateTime? ProcessedAt { get; set; }
    public OutboxStatus ProcessingStatus { get; set; }
    public int RetryCount { get; set; }
}

public enum OutboxStatus
{
    PENDING,
    PROCESSING,
    COMPLETED,
    FAILED
}
```

### 3. Guardar Evento en Transacción

```csharp
public class OrderService
{
    private readonly ApplicationDbContext _context;

    public async Task CreateOrderAsync(CreateOrderCommand command)
    {
        await using var transaction = await _context.Database.BeginTransactionAsync();

        try
        {
            // 1. Operación de negocio
            var order = new Order
            {
                Id = Guid.NewGuid(),
                CustomerId = command.CustomerId,
                TotalAmount = command.TotalAmount,
                Status = OrderStatus.Created,
                CreatedAt = DateTime.UtcNow
            };

            _context.Orders.Add(order);

            // 2. Evento en Outbox (misma transacción)
            var @event = new OrderCreatedEvent(
                order.Id,
                order.CustomerId,
                order.TotalAmount,
                order.CreatedAt
            );

            var outboxEvent = new OutboxEvent
            {
                Id = Guid.NewGuid(),
                AggregateType = "Order",
                AggregateId = order.Id,
                EventType = "OrderCreated",
                EventPayload = JsonSerializer.Serialize(@event),
                CreatedAt = DateTime.UtcNow,
                ProcessingStatus = OutboxStatus.PENDING
            };

            _context.OutboxEvents.Add(outboxEvent);

            // 3. Commit atómico
            await _context.SaveChangesAsync();
            await transaction.CommitAsync();
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}
```

---

## Configuración Kafka

### Configuración appsettings.json

```json
{
  "Kafka": {
    "BootstrapServers": "kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092",
    "SecurityProtocol": "SaslSsl",
    "SaslMechanism": "ScramSha512",

    "Producer": {
      "Acks": "All",
      "EnableIdempotence": true,
      "MaxInFlight": 5,
      "CompressionType": "Snappy",
      "LingerMs": 10
    },

    "Consumer": {
      "AutoOffsetReset": "Earliest",
      "EnableAutoCommit": false,
      "SessionTimeoutMs": 45000,
      "MaxPollIntervalMs": 300000
    }
  },

  "OutboxProcessor": {
    "BatchSize": 50,
    "PollingIntervalMs": 5000,
    "MaxRetries": 3
  }
}
```

### Producer Configuration

```csharp
var producerConfig = new ProducerConfig
{
    BootstrapServers = configuration["Kafka:BootstrapServers"],
    SecurityProtocol = SecurityProtocol.SaslSsl,
    SaslMechanism = SaslMechanism.ScramSha512,
    SaslUsername = await secretsManager.GetSecretAsync("kafka-username"),
    SaslPassword = await secretsManager.GetSecretAsync("kafka-password"),

    // Garantías de entrega
    Acks = Acks.All,
    EnableIdempotence = true,
    MaxInFlight = 5,

    // Performance
    CompressionType = CompressionType.Snappy,
    LingerMs = 10,
    BatchSize = 16384,

    ClientId = $"{serviceName}-producer-{Environment.MachineName}"
};
```

### Consumer Configuration

```csharp
var consumerConfig = new ConsumerConfig
{
    BootstrapServers = configuration["Kafka:BootstrapServers"],
    SecurityProtocol = SecurityProtocol.SaslSsl,
    SaslMechanism = SaslMechanism.ScramSha512,
    SaslUsername = await secretsManager.GetSecretAsync("kafka-username"),
    SaslPassword = await secretsManager.GetSecretAsync("kafka-password"),

    GroupId = $"{serviceName}-consumer-group",

    // Control manual de offsets (CRÍTICO para idempotencia)
    EnableAutoCommit = false,
    EnableAutoOffsetStore = false,
    AutoOffsetReset = AutoOffsetReset.Earliest,

    SessionTimeoutMs = 45000,
    MaxPollIntervalMs = 300000,

    ClientId = $"{serviceName}-consumer-{Environment.MachineName}"
};
```

---

## Outbox Processor

Procesa eventos pendientes en la tabla Outbox y los publica a Kafka.

```csharp
public class OutboxProcessor : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly IProducer<string, string> _producer;
    private readonly OutboxProcessorConfig _config;

    private async Task ProcessPendingEventsAsync(CancellationToken ct)
    {
        using var scope = _serviceProvider.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();

        var pendingEvents = await dbContext.OutboxEvents
            .Where(e => e.ProcessingStatus == OutboxStatus.PENDING)
            .OrderBy(e => e.CreatedAt)
            .Take(_config.BatchSize)
            .ToListAsync(ct);

        foreach (var outboxEvent in pendingEvents)
        {
            try
            {
                outboxEvent.ProcessingStatus = OutboxStatus.PROCESSING;
                await dbContext.SaveChangesAsync(ct);

                var message = new Message<string, string>
                {
                    Key = outboxEvent.AggregateId.ToString(),
                    Value = outboxEvent.EventPayload
                };

                var topic = $"{outboxEvent.AggregateType.ToLower()}.{outboxEvent.EventType.ToLower()}";
                await _producer.ProduceAsync(topic, message, ct);

                outboxEvent.ProcessingStatus = OutboxStatus.COMPLETED;
                outboxEvent.ProcessedAt = DateTime.UtcNow;
                await dbContext.SaveChangesAsync(ct);
            }
            catch (Exception ex)
            {
                outboxEvent.RetryCount++;
                outboxEvent.ProcessingStatus = outboxEvent.RetryCount >= _config.MaxRetries
                    ? OutboxStatus.FAILED
                    : OutboxStatus.PENDING;

                await dbContext.SaveChangesAsync(ct);
                _logger.LogError(ex, "Error procesando evento {EventId}", outboxEvent.Id);
            }
        }
    }
}
```

---

## Consumer con Idempotencia

```csharp
public class OrderCreatedConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IServiceProvider _serviceProvider;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("order.ordercreated");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var result = _consumer.Consume(stoppingToken);

                using var scope = _serviceProvider.CreateScope();
                var handler = scope.ServiceProvider.GetRequiredService<IOrderCreatedHandler>();

                var @event = JsonSerializer.Deserialize<OrderCreatedEvent>(result.Message.Value);

                await handler.HandleAsync(@event, stoppingToken);

                _consumer.Commit(result); // Commit manual después de procesamiento exitoso
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error consumiendo evento");
                // Implementar Dead Letter Queue si falla después de N reintentos
            }
        }
    }
}

public class OrderCreatedHandler : IOrderCreatedHandler
{
    private readonly ApplicationDbContext _db;

    public async Task HandleAsync(OrderCreatedEvent evt, CancellationToken ct)
    {
        // Verificar idempotencia
        var alreadyProcessed = await _db.ProcessedEvents
            .AnyAsync(e => e.EventId == evt.EventId, ct);

        if (alreadyProcessed)
        {
            _logger.LogWarning("Evento duplicado {EventId}, omitiendo", evt.EventId);
            return;
        }

        using var transaction = await _db.Database.BeginTransactionAsync(ct);

        try
        {
            // Lógica de negocio
            await _db.Invoices.AddAsync(new Invoice
            {
                OrderId = evt.OrderId,
                CustomerId = evt.CustomerId,
                Amount = evt.TotalAmount
            }, ct);

            // Marcar como procesado
            await _db.ProcessedEvents.AddAsync(new ProcessedEvent
            {
                EventId = evt.EventId,
                EventType = evt.EventType,
                ProcessedAt = DateTime.UtcNow
            }, ct);

            await _db.SaveChangesAsync(ct);
            await transaction.CommitAsync(ct);
        }
        catch
        {
            await transaction.RollbackAsync(ct);
            throw;
        }
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar Transactional Outbox pattern para atomicidad entre BD y Kafka
- **MUST** configurar productores con `Acks=All` y `EnableIdempotence=true`
- **MUST** configurar consumidores con `EnableAutoCommit=false` (commit manual)
- **MUST** implementar idempotencia en consumidores verificando `event_id` procesados
- **MUST** incluir metadata en eventos: `event_id`, `event_type`, `timestamp`, `correlation_id`
- **MUST** usar TLS 1.3 (`SecurityProtocol=SaslSsl`)
- **MUST** autenticar con SASL/SCRAM-SHA-512
- **MUST** externalizar credenciales a AWS Secrets Manager
- **MUST** usar naming de eventos en pasado ("OrderCreated", no "CreateOrder")
- **MUST** particionar por clave de negocio (`Message.Key = aggregateId`)

### SHOULD (Fuertemente recomendado)

- **SHOULD** comprimir con Snappy (`CompressionType=Snappy`)
- **SHOULD** configurar retención mínima 7 días (recomendado 30 días)
- **SHOULD** naming de topics: `{domain}.{entity}.{event}` (ej: `order.ordercreated`)
- **SHOULD** implementar Dead Letter Queue para mensajes fallidos
- **SHOULD** logging estructurado con correlation_id para trazabilidad

### MUST NOT (Prohibido)

- **MUST NOT** hardcodear credenciales en código o appsettings.json
- **MUST NOT** usar `EnableAutoCommit=true` en consumidores críticos
- **MUST NOT** bloquear threads (usar `ProduceAsync`, no `Produce`)
- **MUST NOT** crear topics manualmente (usar Terraform para IaC)

---

## Comandos CLI Esenciales

### Verificar Conectividad

```bash
# Listar topics
kafka-topics --bootstrap-server kafka.talma.com:9092 \
  --command-config client.properties --list

# Describir topic
kafka-topics --bootstrap-server kafka.talma.com:9092 \
  --command-config client.properties \
  --describe --topic order.ordercreated
```

### Verificar Consumer Lag

```bash
kafka-consumer-groups --bootstrap-server kafka.talma.com:9092 \
  --command-config client.properties \
  --describe --group billing-service-consumer
```

### client.properties

```properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
  username="${KAFKA_USERNAME}" \
  password="${KAFKA_PASSWORD}";
```

---

## Referencias

- [Lineamiento: Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)
- [ADR-008: Apache Kafka para mensajería asíncrona](../../../decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona.md)
- [Guía: Transactional Outbox Pattern](../../guias-arquitectura/transactional-outbox.md)
- Estándares relacionados:
  - [Documentar contratos de eventos](../apis/event-contracts.md)
  - [Diseñar eventos como hechos del dominio](event-design.md)
  - [Implementar consumidores idempotentes](idempotency.md)
  - [Configurar garantías de entrega](message-delivery-guarantees.md)
  - [Implementar Dead Letter Queue](dead-letter-queue.md)
  - [Mantener catálogo de eventos](event-catalog.md)
