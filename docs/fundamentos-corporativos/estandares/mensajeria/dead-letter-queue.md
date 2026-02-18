---
id: dead-letter-queue
sidebar_position: 12
title: Dead Letter Queue
description: Implementación de Dead Letter Queue para gestionar eventos no procesables
---

# Dead Letter Queue

## Contexto

Este estándar define cómo implementar Dead Letter Queue (DLQ) para gestionar eventos que no pueden ser procesados después de múltiples reintentos. Complementa el [lineamiento de Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) especificando **cómo** capturar, almacenar y reprocesar eventos fallidos sin bloquear el flujo principal.

**Decisión arquitectónica:** [ADR-008: Apache Kafka para mensajería asíncrona](../../../decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona.md)

---

## Stack Tecnológico

| Componente         | Tecnología      | Versión | Uso                                |
| ------------------ | --------------- | ------- | ---------------------------------- |
| **Lenguaje**       | .NET 8 (C#)     | 8.0+    | Implementación de DLQ handlers     |
| **Mensajería**     | Apache Kafka    | 3.6+    | Topics de DLQ                      |
| **Cliente Kafka**  | Confluent.Kafka | 2.3+    | Producer/Consumer .NET             |
| **Base de Datos**  | PostgreSQL      | 14+     | Almacenamiento de eventos fallidos |
| **Observabilidad** | Grafana + Loki  | -       | Alertas y monitoreo de DLQ         |

### Dependencias NuGet

```xml
<PackageReference Include="Confluent.Kafka" Version="2.3.0" />
<PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />
<PackageReference Include="Serilog" Version="3.1.0" />
```

---

## Implementación Técnica

### Arquitectura DLQ

```
[Producer] → [order.ordercreated] → [Consumer]
                                         ↓ (falla 3 veces)
                                    [order.ordercreated.dlq]
                                         ↓
                                   [DLQ Handler]
                                         ↓
                                   [PostgreSQL: failed_events]
                                         ↓
                                   [Admin Dashboard]
                                         ↓
                                   [Reprocessing/Fix]
```

### Naming Convention de Topics DLQ

```
Original Topic: {domain}.{entity}.{event}
DLQ Topic:      {domain}.{entity}.{event}.dlq

Ejemplos:
order.ordercreated          → order.ordercreated.dlq
payment.paymentprocessed    → payment.paymentprocessed.dlq
inventory.stockupdated      → inventory.stockupdated.dlq
```

### Tabla de Eventos Fallidos

```sql
CREATE TABLE failed_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id            UUID NOT NULL,
    event_type          VARCHAR(100) NOT NULL,
    topic               VARCHAR(200) NOT NULL,
    partition_num       INT NOT NULL,
    offset_value        BIGINT NOT NULL,
    message_key         TEXT,
    message_value       TEXT NOT NULL,
    error_message       TEXT NOT NULL,
    stack_trace         TEXT,
    retry_count         INT NOT NULL DEFAULT 0,
    first_failed_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    last_failed_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    status              VARCHAR(20) NOT NULL DEFAULT 'FAILED',
    reprocessed_at      TIMESTAMP NULL,
    reprocessed_by      VARCHAR(100),

    INDEX idx_event_id (event_id),
    INDEX idx_status (status, first_failed_at),
    INDEX idx_event_type (event_type)
);

CREATE TYPE failed_event_status AS ENUM (
    'FAILED',        -- Fallo inicial
    'INVESTIGATING', -- En investigación
    'FIXED',         -- Corregido y reprocesado
    'DISCARDED'      -- Descartado permanentemente
);
```

### Modelo de Evento Fallido

```csharp
public class FailedEvent
{
    public Guid Id { get; init; }
    public Guid EventId { get; init; }
    public string EventType { get; init; } = null!;
    public string Topic { get; init; } = null!;
    public int PartitionNum { get; init; }
    public long OffsetValue { get; init; }
    public string? MessageKey { get; init; }
    public string MessageValue { get; init; } = null!;
    public string ErrorMessage { get; init; } = null!;
    public string? StackTrace { get; init; }
    public int RetryCount { get; init; }
    public DateTime FirstFailedAt { get; init; }
    public DateTime LastFailedAt { get; set; }
    public FailedEventStatus Status { get; set; }
    public DateTime? ReprocessedAt { get; set; }
    public string? ReprocessedBy { get; set; }
}

public enum FailedEventStatus
{
    FAILED,
    INVESTIGATING,
    FIXED,
    DISCARDED
}
```

### Consumer con Retry y DLQ

```csharp
public class OrderCreatedConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IProducer<string, string> _dlqProducer;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<OrderCreatedConsumer> _logger;
    private const int MaxRetries = 3;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("order.ordercreated");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var result = _consumer.Consume(stoppingToken);

                var success = await ProcessWithRetriesAsync(
                    result,
                    stoppingToken
                );

                if (success)
                {
                    _consumer.Commit(result);
                }
                else
                {
                    // Enviar a DLQ después de agotar reintentos
                    await SendToDLQAsync(result, stoppingToken);
                    _consumer.Commit(result); // Commit para no bloquear
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error crítico en consumer");
            }
        }
    }

    private async Task<bool> ProcessWithRetriesAsync(
        ConsumeResult<string, string> result,
        CancellationToken ct)
    {
        int retryCount = 0;
        Exception? lastException = null;

        while (retryCount < MaxRetries)
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();
                var handler = scope.ServiceProvider
                    .GetRequiredService<IOrderCreatedHandler>();

                var evt = JsonSerializer.Deserialize<OrderCreatedEvent>(
                    result.Message.Value
                );

                await handler.HandleAsync(evt, ct);

                _logger.LogInformation(
                    "Evento procesado exitosamente | EventId={EventId} Retry={Retry}",
                    evt.EventId,
                    retryCount
                );

                return true; // Éxito
            }
            catch (Exception ex)
            {
                lastException = ex;
                retryCount++;

                _logger.LogWarning(ex,
                    "Error procesando evento, reintento {Retry}/{Max} | Offset={Offset}",
                    retryCount,
                    MaxRetries,
                    result.Offset.Value
                );

                if (retryCount < MaxRetries)
                {
                    // Backoff exponencial: 1s, 2s, 4s
                    var delay = TimeSpan.FromSeconds(Math.Pow(2, retryCount - 1));
                    await Task.Delay(delay, ct);
                }
            }
        }

        _logger.LogError(lastException,
            "Evento falló después de {MaxRetries} reintentos | Offset={Offset}",
            MaxRetries,
            result.Offset.Value
        );

        return false; // Fallo después de todos los reintentos
    }

    private async Task SendToDLQAsync(
        ConsumeResult<string, string> result,
        CancellationToken ct)
    {
        var dlqTopic = $"{result.Topic}.dlq";

        var dlqMessage = new Message<string, string>
        {
            Key = result.Message.Key,
            Value = result.Message.Value,
            Headers = new Headers(result.Message.Headers)
            {
                // Metadata adicional
                { "original_topic", Encoding.UTF8.GetBytes(result.Topic) },
                { "original_partition", BitConverter.GetBytes(result.Partition.Value) },
                { "original_offset", BitConverter.GetBytes(result.Offset.Value) },
                { "failed_at", Encoding.UTF8.GetBytes(DateTime.UtcNow.ToString("o")) },
                { "retry_count", BitConverter.GetBytes(MaxRetries) }
            }
        };

        try
        {
            await _dlqProducer.ProduceAsync(dlqTopic, dlqMessage, ct);

            _logger.LogWarning(
                "Evento enviado a DLQ | Topic={DLQTopic} OriginalOffset={Offset}",
                dlqTopic,
                result.Offset.Value
            );
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Error enviando evento a DLQ | Topic={DLQTopic}",
                dlqTopic
            );
        }
    }
}
```

### DLQ Handler (Persistencia en PostgreSQL)

```csharp
public class DLQHandler : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<DLQHandler> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // Suscribirse a todos los topics DLQ
        _consumer.Subscribe(new Regex(@"\.dlq$"));

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var result = _consumer.Consume(stoppingToken);

                using var scope = _serviceProvider.CreateScope();
                var dbContext = scope.ServiceProvider
                    .GetRequiredService<ApplicationDbContext>();

                // Extraer metadata de headers
                var originalTopic = GetHeader(result, "original_topic");
                var originalPartition = GetHeaderInt(result, "original_partition");
                var originalOffset = GetHeaderLong(result, "original_offset");
                var failedAt = GetHeader(result, "failed_at");
                var retryCount = GetHeaderInt(result, "retry_count");

                // Deserializar para obtener EventId y EventType
                var eventEnvelope = JsonSerializer.Deserialize<EventEnvelope>(
                    result.Message.Value
                );

                // Persistir en PostgreSQL
                var failedEvent = new FailedEvent
                {
                    Id = Guid.NewGuid(),
                    EventId = eventEnvelope.EventId,
                    EventType = eventEnvelope.EventType,
                    Topic = originalTopic,
                    PartitionNum = originalPartition,
                    OffsetValue = originalOffset,
                    MessageKey = result.Message.Key,
                    MessageValue = result.Message.Value,
                    ErrorMessage = "Falló después de múltiples reintentos",
                    RetryCount = retryCount,
                    FirstFailedAt = DateTime.Parse(failedAt),
                    LastFailedAt = DateTime.UtcNow,
                    Status = FailedEventStatus.FAILED
                };

                await dbContext.FailedEvents.AddAsync(failedEvent, stoppingToken);
                await dbContext.SaveChangesAsync(stoppingToken);

                _consumer.Commit(result);

                _logger.LogInformation(
                    "Evento fallido persistido | EventId={EventId} EventType={EventType}",
                    failedEvent.EventId,
                    failedEvent.EventType
                );

                // Alertar si es crítico
                if (IsCriticalEvent(failedEvent.EventType))
                {
                    await SendAlertAsync(failedEvent, stoppingToken);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error en DLQ Handler");
            }
        }
    }

    private string GetHeader(ConsumeResult<string, string> result, string key)
    {
        var header = result.Message.Headers.FirstOrDefault(h => h.Key == key);
        return header != null ? Encoding.UTF8.GetString(header.GetValueBytes()) : "";
    }

    private int GetHeaderInt(ConsumeResult<string, string> result, string key)
    {
        var header = result.Message.Headers.FirstOrDefault(h => h.Key == key);
        return header != null ? BitConverter.ToInt32(header.GetValueBytes()) : 0;
    }

    private long GetHeaderLong(ConsumeResult<string, string> result, string key)
    {
        var header = result.Message.Headers.FirstOrDefault(h => h.Key == key);
        return header != null ? BitConverter.ToInt64(header.GetValueBytes()) : 0;
    }

    private bool IsCriticalEvent(string eventType)
    {
        return eventType.Contains("Payment") ||
               eventType.Contains("Order") ||
               eventType.Contains("Invoice");
    }

    private async Task SendAlertAsync(FailedEvent evt, CancellationToken ct)
    {
        _logger.LogCritical(
            "⚠️ EVENTO CRÍTICO EN DLQ | EventType={EventType} EventId={EventId}",
            evt.EventType,
            evt.EventId
        );

        // Integración con sistema de alertas (Grafana, PagerDuty, etc.)
        // await _alertService.SendAsync(...);
    }
}
```

### Reprocesamiento Manual

```csharp
public class FailedEventReprocessor
{
    private readonly ApplicationDbContext _dbContext;
    private readonly IServiceProvider _serviceProvider;

    public async Task<ReprocessResult> ReprocessEventAsync(
        Guid failedEventId,
        string reprocessedBy,
        CancellationToken ct)
    {
        var failedEvent = await _dbContext.FailedEvents
            .FirstOrDefaultAsync(e => e.Id == failedEventId, ct);

        if (failedEvent == null)
            throw new NotFoundException($"Failed event {failedEventId} not found");

        if (failedEvent.Status != FailedEventStatus.FAILED)
            throw new InvalidOperationException("Event already processed");

        try
        {
            // Actualizar estado
            failedEvent.Status = FailedEventStatus.INVESTIGATING;
            await _dbContext.SaveChangesAsync(ct);

            // Obtener handler apropiado
            var handlerType = GetHandlerType(failedEvent.EventType);
            using var scope = _serviceProvider.CreateScope();
            var handler = scope.ServiceProvider.GetRequiredService(handlerType);

            // Deserializar y procesar
            var evt = JsonSerializer.Deserialize(
                failedEvent.MessageValue,
                GetEventType(failedEvent.EventType)
            );

            await ((dynamic)handler).HandleAsync((dynamic)evt, ct);

            // Marcar como corregido
            failedEvent.Status = FailedEventStatus.FIXED;
            failedEvent.ReprocessedAt = DateTime.UtcNow;
            failedEvent.ReprocessedBy = reprocessedBy;
            await _dbContext.SaveChangesAsync(ct);

            return ReprocessResult.Success(failedEventId);
        }
        catch (Exception ex)
        {
            // Revertir estado
            failedEvent.Status = FailedEventStatus.FAILED;
            await _dbContext.SaveChangesAsync(ct);

            return ReprocessResult.Failure(failedEventId, ex.Message);
        }
    }

    public async Task<int> ReprocessBatchAsync(
        List<Guid> failedEventIds,
        string reprocessedBy,
        CancellationToken ct)
    {
        int successCount = 0;

        foreach (var id in failedEventIds)
        {
            var result = await ReprocessEventAsync(id, reprocessedBy, ct);
            if (result.Success)
                successCount++;
        }

        return successCount;
    }

    public async Task DiscardEventAsync(Guid failedEventId, string reason, CancellationToken ct)
    {
        var failedEvent = await _dbContext.FailedEvents.FindAsync(failedEventId);
        if (failedEvent != null)
        {
            failedEvent.Status = FailedEventStatus.DISCARDED;
            failedEvent.ErrorMessage += $" | DISCARDED: {reason}";
            await _dbContext.SaveChangesAsync(ct);
        }
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** enviar eventos a DLQ después de agotar reintentos (recomendado 3)
- **MUST** persistir eventos fallidos en PostgreSQL para análisis
- **MUST** incluir metadata completa: `event_id`, `event_type`, `original_topic`, `original_offset`, `error_message`, `retry_count`
- **MUST** hacer commit del offset después de enviar a DLQ (no bloquear topic principal)
- **MUST** usar naming convention `{topic}.dlq` para topics de DLQ
- **MUST** implementar backoff exponencial entre reintentos
- **MUST** alertar cuando eventos críticos llegan a DLQ
- **MUST** proveer mecanismo de reprocesamiento manual

### SHOULD (Fuertemente recomendado)

- **SHOULD** categorizar eventos por severidad (crítico, warning, info)
- **SHOULD** monitorear tamaño de DLQ (alerta si > 100 eventos)
- **SHOULD** implementar limpieza automática de eventos antiguos en DLQ (90+ días)
- **SHOULD** capturar stack trace completo de errores
- **SHOULD** automatizar reprocesamiento de errores transitorios conocidos
- **SHOULD** proveer dashboard de administración de DLQ

### MAY (Opcional)

- **MAY** implementar diferentes niveles de DLQ (dlq.retry, dlq.permanent)
- **MAY** enviar notificaciones por email/Slack cuando hay eventos críticos en DLQ
- **MAY** implementar análisis automático de patrones de error

### MUST NOT (Prohibido)

- **MUST NOT** hacer commit sin enviar a DLQ (pierde el evento)
- **MUST NOT** bloquear topic principal por eventos no procesables
- **MUST NOT** reintentar indefinidamente sin límite
- **MUST NOT** perder metadata del evento original

---

## Monitoreo y Alertas

### Métricas Clave

```yaml
# Prometheus metrics
dlq_events_total{topic, event_type}          # Total eventos en DLQ
dlq_events_by_status{status}                 # Por estado (FAILED, FIXED, etc.)
dlq_processing_duration_seconds              # Tiempo de reprocesamiento
dlq_reprocess_success_rate                   # Tasa de éxito en reprocesamiento
```

### Alertas Recomendadas

```yaml
groups:
  - name: dlq_alerts
    rules:
      - alert: DLQSizeHigh
        expr: dlq_events_total{status="FAILED"} > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "DLQ tiene >100 eventos fallidos"

      - alert: CriticalEventInDLQ
        expr: increase(dlq_events_total{event_type=~".*Payment.*|.*Order.*"}[5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Evento crítico en DLQ"

      - alert: DLQProcessingStalled
        expr: rate(dlq_events_total[10m]) == 0 and dlq_events_total > 0
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "DLQ no está procesando eventos"
```

---

## Anti-Patrones

### ❌ #1: Commit Sin Enviar a DLQ

```csharp
// ❌ INCORRECTO
try {
    await ProcessEventAsync(evt);
    consumer.Commit(result);
} catch {
    // ❌ No envía a DLQ, evento se pierde
}

// ✅ CORRECTO
try {
    await ProcessEventAsync(evt);
} catch {
    await SendToDLQAsync(result);
}
consumer.Commit(result);
```

### ❌ #2: Reintentos Sin Límite

```csharp
// ❌ INCORRECTO
while (true) {
    try {
        await ProcessEventAsync(evt);
        break;
    } catch {
        // ❌ Loop infinito
    }
}

// ✅ CORRECTO
for (int i = 0; i < MaxRetries; i++) {
    try {
        await ProcessEventAsync(evt);
        return;
    } catch {
        if (i == MaxRetries - 1)
            await SendToDLQAsync(result);
    }
}
```

### ❌ #3: Perder Metadata Original

```csharp
// ❌ INCORRECTO
await _dlqProducer.ProduceAsync(dlqTopic, new Message<string, string> {
    Value = result.Message.Value
    // ❌ Pierde topic, partition, offset originales
});

// ✅ CORRECTO
await _dlqProducer.ProduceAsync(dlqTopic, new Message<string, string> {
    Value = result.Message.Value,
    Headers = new Headers {
        { "original_topic", ... },
        { "original_partition", ... },
        { "original_offset", ... },
        { "error_message", ... }
    }
});
```

---

## Referencias

- [Lineamiento: Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)
- [ADR-008: Apache Kafka para mensajería asíncrona](../../../decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona.md)
- Estándares relacionados:
  - [Mensajería Asíncrona](async-messaging.md)
  - [Idempotencia](idempotency.md)
  - [Garantías de Entrega](message-delivery-guarantees.md)
- Patrones externos:
  - [Dead Letter Queue Pattern](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html)
