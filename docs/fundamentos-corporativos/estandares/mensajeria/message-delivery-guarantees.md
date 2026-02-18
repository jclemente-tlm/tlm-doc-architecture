---
id: message-delivery-guarantees
sidebar_position: 11
title: Garantías de Entrega
description: Configuración de garantías de entrega en Apache Kafka (at-most-once, at-least-once, exactly-once)
---

# Garantías de Entrega

## Contexto

Este estándar define cómo configurar y gestionar las garantías de entrega en Apache Kafka. Complementa el [lineamiento de Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) especificando **cómo** configurar producers y consumers para lograr las garantías de entrega requeridas según el contexto de negocio.

**Decisión arquitectónica:** [ADR-008: Apache Kafka para mensajería asíncrona](../../../decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona.md)

---

## Stack Tecnológico

| Componente        | Tecnología      | Versión | Uso                                   |
| ----------------- | --------------- | ------- | ------------------------------------- |
| **Lenguaje**      | .NET 8 (C#)     | 8.0+    | Implementación de producers/consumers |
| **Mensajería**    | Apache Kafka    | 3.6+    | Broker de mensajería                  |
| **Cliente Kafka** | Confluent.Kafka | 2.3+    | Producer/Consumer .NET                |
| **Base de Datos** | PostgreSQL      | 14+     | Transaccional Outbox + Idempotencia   |

### Dependencias NuGet

```xml
<PackageReference Include="Confluent.Kafka" Version="2.3.0" />
<PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />
```

---

## Implementación Técnica

### Niveles de Garantía

Kafka ofrece tres niveles de garantía de entrega. La elección depende del caso de uso:

| Garantía          | Descripción                          | Casos de Uso                          | Riesgo              |
| ----------------- | ------------------------------------ | ------------------------------------- | ------------------- |
| **At-Most-Once**  | Mensaje se envía máximo 1 vez        | Métricas, logs no críticos            | Pérdida de mensajes |
| **At-Least-Once** | Mensaje se entrega al menos 1 vez    | Eventos de negocio (con idempotencia) | Duplicados          |
| **Exactly-Once**  | Mensaje se procesa exactamente 1 vez | Transacciones financieras             | Complejidad alta    |

**Recomendación Talma:** **At-Least-Once + Idempotencia** para la mayoría de casos (balance eficiencia/confiabilidad).

---

### At-Least-Once Delivery

Configuración estándar para eventos de negocio. Combina confiabilidad con simplicidad.

#### Producer Configuration

```csharp
var producerConfig = new ProducerConfig
{
    BootstrapServers = configuration["Kafka:BootstrapServers"],
    SecurityProtocol = SecurityProtocol.SaslSsl,
    SaslMechanism = SaslMechanism.ScramSha512,

    // Garantías de entrega at-least-once
    Acks = Acks.All,              // Esperar ACK de todos los in-sync replicas
    EnableIdempotence = true,     // Elimina duplicados del producer
    MaxInFlight = 5,              // Máximo 5 requests en paralelo

    // Retries
    MessageSendMaxRetries = int.MaxValue,  // Reintentos infinitos
    RequestTimeoutMs = 30000,              // Timeout por request: 30s

    // Durabilidad
    CompressionType = CompressionType.Snappy,
    LingerMs = 10,
    BatchSize = 16384,

    ClientId = $"{serviceName}-producer"
};

var producer = new ProducerBuilder<string, string>(producerConfig)
    .SetErrorHandler((_, error) =>
    {
        _logger.LogError("Kafka error: {Reason}", error.Reason);
    })
    .Build();
```

#### Consumer Configuration

```csharp
var consumerConfig = new ConsumerConfig
{
    BootstrapServers = configuration["Kafka:BootstrapServers"],
    SecurityProtocol = SecurityProtocol.SaslSsl,
    SaslMechanism = SaslMechanism.ScramSha512,

    GroupId = $"{serviceName}-consumer-group",

    // Control manual de offsets (CRÍTICO)
    EnableAutoCommit = false,           // Commit manual obligatorio
    EnableAutoOffsetStore = false,      // Store manual
    AutoOffsetReset = AutoOffsetReset.Earliest,

    // Timeouts
    SessionTimeoutMs = 45000,           // 45 segundos
    MaxPollIntervalMs = 300000,         // 5 minutos entre polls

    ClientId = $"{serviceName}-consumer"
};

var consumer = new ConsumerBuilder<string, string>(consumerConfig)
    .Build();

consumer.Subscribe("order.ordercreated");

while (!cancellationToken.IsCancellationRequested)
{
    var result = consumer.Consume(cancellationToken);

    try
    {
        // Procesar evento (con idempotencia)
        await ProcessEventAsync(result.Message.Value, cancellationToken);

        // Commit SOLO después de procesamiento exitoso
        consumer.Commit(result);

        _logger.LogInformation(
            "Evento procesado y committed | Offset={Offset}",
            result.Offset.Value
        );
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Error procesando evento");
        // NO hacer commit - Kafka reentregará el mensaje
        throw;
    }
}
```

---

### Exactly-Once Semantics (EOS)

Para casos críticos donde duplicados son inaceptables (ej: transacciones financieras).

#### Producer con Transacciones

```csharp
var producerConfig = new ProducerConfig
{
    BootstrapServers = configuration["Kafka:BootstrapServers"],
    SecurityProtocol = SecurityProtocol.SaslSsl,
    SaslMechanism = SaslMechanism.ScramSha512,

    // Exactly-Once Semantics
    TransactionalId = $"{serviceName}-{Environment.MachineName}-{Guid.NewGuid()}",
    EnableIdempotence = true,
    Acks = Acks.All,
    MaxInFlight = 5,

    ClientId = $"{serviceName}-transactional-producer"
};

var producer = new ProducerBuilder<string, string>(producerConfig).Build();

// Inicializar transacciones
producer.InitTransactions(TimeSpan.FromSeconds(30));

try
{
    // Iniciar transacción
    producer.BeginTransaction();

    // Publicar múltiples mensajes atómicamente
    await producer.ProduceAsync("order.ordercreated",
        new Message<string, string> { Key = orderId, Value = eventJson });

    await producer.ProduceAsync("inventory.reserved",
        new Message<string, string> { Key = orderId, Value = inventoryJson });

    // Commit transaccional
    producer.CommitTransaction();

    _logger.LogInformation("Transacción Kafka committed exitosamente");
}
catch (Exception ex)
{
    _logger.LogError(ex, "Error en transacción, haciendo abort");
    producer.AbortTransaction();
    throw;
}
```

#### Consumer con Read Committed

```csharp
var consumerConfig = new ConsumerConfig
{
    BootstrapServers = configuration["Kafka:BootstrapServers"],
    SecurityProtocol = SecurityProtocol.SaslSsl,
    SaslMechanism = SaslMechanism.ScramSha512,

    GroupId = $"{serviceName}-consumer-group",

    // Leer solo mensajes committed
    IsolationLevel = IsolationLevel.ReadCommitted,  // ← CRÍTICO para EOS

    EnableAutoCommit = false,
    EnableAutoOffsetStore = false,
    AutoOffsetReset = AutoOffsetReset.Earliest,

    SessionTimeoutMs = 45000,
    MaxPollIntervalMs = 300000,

    ClientId = $"{serviceName}-eos-consumer"
};
```

---

### At-Most-Once Delivery

Para datos no críticos (métricas, logs) donde performance > confiabilidad.

#### Producer Fire-and-Forget

```csharp
var producerConfig = new ProducerConfig
{
    BootstrapServers = configuration["Kafka:BootstrapServers"],

    // At-Most-Once (sin garantías)
    Acks = Acks.Leader,           // Solo esperar ACK del leader
    EnableIdempotence = false,    // Sin idempotencia
    MessageSendMaxRetries = 0,    // Sin retries
    RequestTimeoutMs = 5000,      // Timeout corto

    CompressionType = CompressionType.Snappy,
    LingerMs = 10,

    ClientId = $"{serviceName}-fire-forget-producer"
};

// Enviar sin esperar confirmación
producer.Produce("metrics.cpu.usage",
    new Message<string, string> { Key = hostId, Value = metricsJson },
    deliveryReport =>
    {
        if (deliveryReport.Error.IsError)
        {
            _logger.LogWarning("Métrica perdida: {Error}", deliveryReport.Error.Reason);
            // No reintentar
        }
    }
);
```

#### Consumer con Auto-Commit

```csharp
var consumerConfig = new ConsumerConfig
{
    BootstrapServers = configuration["Kafka:BootstrapServers"],
    GroupId = $"{serviceName}-metrics-consumer",

    // Auto-commit (puede perder mensajes si consumer falla)
    EnableAutoCommit = true,
    AutoCommitIntervalMs = 5000,

    AutoOffsetReset = AutoOffsetReset.Latest,  // Procesar solo nuevos

    ClientId = $"{serviceName}-metrics-consumer"
};

var consumer = new ConsumerBuilder<string, string>(consumerConfig).Build();
consumer.Subscribe("metrics.cpu.usage");

while (!cancellationToken.IsCancellationRequested)
{
    var result = consumer.Consume(cancellationToken);

    try
    {
        ProcessMetric(result.Message.Value);
        // No commit manual - auto-commit se encarga
    }
    catch
    {
        // Ignorar errores - métrica se pierde pero continúa
    }
}
```

---

### Patrón Transactional Outbox (Exactly-Once End-to-End)

Combina transacción de BD con publicación a Kafka para garantía exactly-once completa.

```csharp
public class OrderService
{
    private readonly ApplicationDbContext _dbContext;

    public async Task CreateOrderAsync(CreateOrderCommand command)
    {
        // 1. Transacción atómica en PostgreSQL
        await using var transaction = await _dbContext.Database.BeginTransactionAsync();

        try
        {
            // Crear orden
            var order = new Order { ... };
            _dbContext.Orders.Add(order);

            // Guardar evento en Outbox (misma transacción)
            var outboxEvent = new OutboxEvent
            {
                EventId = Guid.NewGuid(),
                EventType = "OrderCreated",
                EventPayload = JsonSerializer.Serialize(new OrderCreatedEvent(...)),
                ProcessingStatus = OutboxStatus.PENDING
            };
            _dbContext.OutboxEvents.Add(outboxEvent);

            // Commit atómico
            await _dbContext.SaveChangesAsync();
            await transaction.CommitAsync();

            // 2. Outbox Processor publicará a Kafka de forma idempotente
            // (ejecuta en background service separado)
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}

// Outbox Processor con exactly-once
public class OutboxProcessor : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var pendingEvents = await _dbContext.OutboxEvents
                .Where(e => e.ProcessingStatus == OutboxStatus.PENDING)
                .ToListAsync(ct);

            foreach (var evt in pendingEvents)
            {
                try
                {
                    // Publicar a Kafka
                    await _producer.ProduceAsync(
                        topic: GetTopicName(evt.EventType),
                        message: new Message<string, string>
                        {
                            Key = evt.AggregateId.ToString(),
                            Value = evt.EventPayload
                        },
                        ct
                    );

                    // Marcar como procesado
                    evt.ProcessingStatus = OutboxStatus.COMPLETED;
                    evt.ProcessedAt = DateTime.UtcNow;
                    await _dbContext.SaveChangesAsync(ct);
                }
                catch (Exception ex)
                {
                    evt.RetryCount++;
                    if (evt.RetryCount >= 3)
                        evt.ProcessingStatus = OutboxStatus.FAILED;

                    await _dbContext.SaveChangesAsync(ct);
                }
            }

            await Task.Delay(TimeSpan.FromSeconds(5), ct);
        }
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar **At-Least-Once + Idempotencia** como configuración por defecto para eventos de negocio
- **MUST** configurar `Acks=All` y `EnableIdempotence=true` en producers
- **MUST** configurar `EnableAutoCommit=false` en consumers (commit manual)
- **MUST** hacer commit SOLO después de procesamiento exitoso del evento
- **MUST** implementar idempotencia en consumers para manejar duplicados
- **MUST** configurar `MessageSendMaxRetries=int.MaxValue` para eventos críticos
- **MUST** usar Transactional Outbox pattern para atomicidad BD + Kafka
- **MUST** logear eventos perdidos o fallidos

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Exactly-Once Semantics solo para transacciones financieras/críticas
- **SHOULD** configurar `IsolationLevel=ReadCommitted` cuando se usan transacciones Kafka
- **SHOULD** monitorear lag de consumers para detectar problemas
- **SHOULD** implementar Dead Letter Queue para mensajes no procesables
- **SHOULD** configurar `SessionTimeoutMs=45000` y `MaxPollIntervalMs=300000`

### MAY (Opcional)

- **MAY** usar At-Most-Once para métricas y logs no críticos
- **MAY** ajustar `LingerMs` y `BatchSize` según throughput requerido
- **MAY** usar transacciones Kafka para atomicidad multi-mensaje

### MUST NOT (Prohibido)

- **MUST NOT** usar `EnableAutoCommit=true` para eventos de negocio críticos
- **MUST NOT** hacer commit antes de procesar evento exitosamente
- **MUST NOT** asumir que Kafka nunca duplicará mensajes (siempre implementar idempotencia)
- **MUST NOT** usar At-Most-Once para eventos que afectan estado de negocio

---

## Matriz de Decisión

| Caso de Uso                   | Garantía Recomendada                | Configuración Clave                                            |
| ----------------------------- | ----------------------------------- | -------------------------------------------------------------- |
| **Eventos de negocio**        | At-Least-Once + Idempotencia        | `Acks=All`, `EnableIdempotence=true`, `EnableAutoCommit=false` |
| **Transacciones financieras** | Exactly-Once (Transactional Outbox) | Outbox pattern + idempotencia consumer                         |
| **Métricas / Logs**           | At-Most-Once                        | `Acks=Leader`, `Retries=0`, `EnableAutoCommit=true`            |
| **Notificaciones**            | At-Least-Once                       | Igual que eventos de negocio                                   |
| **Auditoría**                 | Exactly-Once                        | Transactional Outbox + EOS                                     |

---

## Troubleshooting

### Problema: Mensajes Duplicados

**Síntoma:** Mismo `event_id` procesado múltiples veces

**Causa:** At-Least-Once sin idempotencia

**Solución:**


```csharp
// Implementar verificación de idempotencia
if (await _db.ProcessedEvents.AnyAsync(e => e.EventId == evt.EventId))
{
    _logger.LogWarning("Evento duplicado detectado, omitiendo");
    return;
}
```

### Problema: Mensajes Perdidos

**Síntoma:** Eventos no llegan a consumers


**Causa posible 1:** `Acks=None` o `Acks=Leader` con broker caído

```csharp
// Solución: Usar Acks=All
Acks = Acks.All
```


**Causa posible 2:** `EnableAutoCommit=true` + consumer crash

```csharp
// Solución: Commit manual
EnableAutoCommit = false;
consumer.Commit(result);  // Solo después de procesar
```

### Problema: Consumer Lag Creciente

**Síntoma:** Offset lag aumenta constantemente


**Causa:** Procesamiento muy lento vs tasa de eventos

**Solución:**

```csharp
// 1. Aumentar timeout
MaxPollIntervalMs = 600000  // 10 minutos

// 2. Escalar consumers horizontalmente
// Aumentar partitions en topic + más instancias consumer

// 3. Optimizar procesamiento (batch, async I/O)
```

---

## Referencias

- [Lineamiento: Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)
- [ADR-008: Apache Kafka para mensajería asíncrona](../../../decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona.md)
- [Guía: Transactional Outbox Pattern](../../guias-arquitectura/transactional-outbox.md)
- Estándares relacionados:
  - [Mensajería Asíncrona](async-messaging.md)
  - [Idempotencia](idempotency.md)
  - [Dead Letter Queue](dead-letter-queue.md)
- Documentación externa:
  - [Kafka Delivery Semantics](https://kafka.apache.org/documentation/#semantics)
  - [Exactly-Once Semantics in Kafka](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
