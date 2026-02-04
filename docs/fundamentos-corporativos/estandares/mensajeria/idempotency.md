---
id: idempotency
sidebar_position: 5
title: Idempotencia
description: Estándar para implementar procesamiento idempotente en mensajería, evitando duplicados con deduplication keys y registros de procesamiento
---

# Estándar Técnico — Idempotencia

---

## 1. Propósito

Garantizar que mensajes procesados múltiples veces produzcan el mismo resultado (idempotencia), evitando duplicación de operaciones críticas (pagos, pedidos) mediante deduplication keys y registros de procesamiento en PostgreSQL.

---

## 2. Alcance

**Aplica a:**

- Consumers de Kafka
- Operaciones no idempotentes por naturaleza (CREATE, UPDATE con side effects)
- Procesamiento asíncrono de eventos
- Integraciones con sistemas externos
- Webhooks y callbacks

**No aplica a:**

- Operaciones naturalmente idempotentes (GET, DELETE por ID)
- Logs y métricas (no críticas)
- Eventos informativos sin side effects

---

## 3. Tecnologías Aprobadas

| Componente              | Tecnología      | Versión mínima | Observaciones                 |
| ----------------------- | --------------- | -------------- | ----------------------------- |
| **Message Broker**      | Apache Kafka    | 3.6+           | At-least-once delivery        |
| **Deduplication Store** | PostgreSQL      | 14+            | Processed events table        |
| **Caching**             | Redis           | 7.2+           | TTL-based deduplication       |
| **Distributed Lock**    | Redis (RedLock) | 7.2+           | Para operaciones at-most-once |
| **Client Library**      | Confluent.Kafka | 2.0+           | .NET consumer                 |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Idempotency Key

- [ ] **Message ID**: Usar `id` de CloudEvents como deduplication key
- [ ] **Business Key**: Para reintentos de cliente (OrderId, TransactionId)
- [ ] **Uniqueness**: UUID v7 (timestamp-sortable)
- [ ] **Persistence**: Registrar en tabla `processed_events` antes de ejecutar operación

### Procesamiento

- [ ] **Check-Execute-Ack**: Verificar si ya fue procesado → Ejecutar → Confirmar
- [ ] **Atomic**: Registro + operación en misma transacción DB
- [ ] **TTL**: Retener registros por 7-30 días (según volumen)
- [ ] **Retry-safe**: Múltiples reintentos producen mismo resultado

### Monitoring

- [ ] **Duplicados detectados**: Métrica de cuántos eventos se rechazaron por duplicados
- [ ] **Latencia**: Tiempo de consulta a `processed_events`
- [ ] **Alertas**: Si tasa de duplicados > 5% → investigar

---

## 5. Patrón de Implementación

### Base de Datos - Processed Events

```sql
-- Tabla para deduplicación
CREATE TABLE processed_events (
    id UUID PRIMARY KEY,              -- CloudEvents.id
    event_type VARCHAR(100) NOT NULL, -- CloudEvents.type
    source VARCHAR(255) NOT NULL,     -- CloudEvents.source
    processed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    checksum VARCHAR(64),             -- SHA256 del payload (opcional)
    result_status VARCHAR(50),        -- success, failed, skipped

    -- Index para consultas rápidas
    CONSTRAINT unique_event UNIQUE (id)
);

CREATE INDEX idx_processed_events_type_time
  ON processed_events(event_type, processed_at DESC);

CREATE INDEX idx_processed_events_source
  ON processed_events(source, processed_at DESC);

-- Cleanup automático de eventos antiguos (30 días)
CREATE OR REPLACE FUNCTION cleanup_old_processed_events()
RETURNS void AS $$
BEGIN
  DELETE FROM processed_events
  WHERE processed_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Ejecutar diariamente
-- SELECT cron.schedule('cleanup-processed-events', '0 2 * * *', 'SELECT cleanup_old_processed_events();');
```

### .NET - Idempotent Consumer

```csharp
// Services/IdempotentEventProcessor.cs
public class IdempotentEventProcessor
{
    private readonly ApplicationDbContext _dbContext;
    private readonly ILogger<IdempotentEventProcessor> _logger;

    public async Task<ProcessingResult> ProcessEventAsync(
        CloudEvent cloudEvent,
        Func<CloudEvent, Task> handler,
        CancellationToken cancellationToken = default)
    {
        var eventId = Guid.Parse(cloudEvent.Id!);

        // 1. Check: Ya fue procesado?
        var alreadyProcessed = await _dbContext.ProcessedEvents
            .AnyAsync(e => e.Id == eventId, cancellationToken);

        if (alreadyProcessed)
        {
            _logger.LogWarning(
                "Event {EventId} of type {EventType} already processed. Skipping.",
                eventId,
                cloudEvent.Type);

            return ProcessingResult.Duplicate;
        }

        // 2. Execute + Record en transacción atómica
        using var transaction = await _dbContext.Database.BeginTransactionAsync(cancellationToken);

        try
        {
            // Registrar ANTES de ejecutar (para evitar race condition)
            var processedEvent = new ProcessedEvent
            {
                Id = eventId,
                EventType = cloudEvent.Type!,
                Source = cloudEvent.Source!.ToString(),
                ProcessedAt = DateTime.UtcNow,
                Checksum = ComputeChecksum(cloudEvent.Data),
                ResultStatus = "processing"
            };

            _dbContext.ProcessedEvents.Add(processedEvent);
            await _dbContext.SaveChangesAsync(cancellationToken);

            // Ejecutar handler
            await handler(cloudEvent);

            // Actualizar estado
            processedEvent.ResultStatus = "success";
            await _dbContext.SaveChangesAsync(cancellationToken);

            await transaction.CommitAsync(cancellationToken);

            _logger.LogInformation(
                "Event {EventId} processed successfully",
                eventId);

            return ProcessingResult.Success;
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync(cancellationToken);

            _logger.LogError(ex,
                "Failed to process event {EventId}",
                eventId);

            return ProcessingResult.Failed;
        }
    }

    private static string ComputeChecksum(object? data)
    {
        if (data == null) return string.Empty;

        var json = JsonSerializer.Serialize(data);
        var bytes = Encoding.UTF8.GetBytes(json);
        var hash = SHA256.HashData(bytes);

        return Convert.ToHexString(hash);
    }
}

public enum ProcessingResult
{
    Success,
    Duplicate,
    Failed
}
```

### Consumer con Idempotencia

```csharp
// Consumers/PaymentCreatedConsumer.cs
public class PaymentCreatedConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IdempotentEventProcessor _processor;
    private readonly ILogger<PaymentCreatedConsumer> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("payment.created");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var consumeResult = _consumer.Consume(stoppingToken);
                var cloudEvent = JsonSerializer.Deserialize<CloudEvent>(consumeResult.Message.Value)!;

                // Procesamiento idempotente
                var result = await _processor.ProcessEventAsync(
                    cloudEvent,
                    async (evt) =>
                    {
                        var payload = JsonSerializer.Deserialize<PaymentCreatedEvent>(evt.Data!.ToString()!);
                        await HandlePaymentCreatedAsync(payload!);
                    },
                    stoppingToken);

                // Confirmar solo si fue procesado o duplicado (no si falló)
                if (result is ProcessingResult.Success or ProcessingResult.Duplicate)
                {
                    _consumer.Commit(consumeResult);
                }
                else
                {
                    // No hacer commit, Kafka reintenta automáticamente
                    _logger.LogWarning("Event processing failed, will retry");
                    await Task.Delay(5000, stoppingToken); // Backoff
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error consuming message");
            }
        }
    }

    private async Task HandlePaymentCreatedAsync(PaymentCreatedEvent evt)
    {
        // Lógica de negocio
        // Esta función se ejecuta UNA SOLA VEZ gracias a idempotencia
    }
}
```

---

## 6. Redis para Deduplicación Rápida

### Caso de Uso: Alta Frecuencia

Si tienes millones de eventos, consultar PostgreSQL por cada mensaje puede ser lento. Usa Redis como caché con TTL:

```csharp
public class RedisIdempotencyCache
{
    private readonly IConnectionMultiplexer _redis;
    private readonly TimeSpan _ttl = TimeSpan.FromHours(24);

    public async Task<bool> TryMarkAsProcessedAsync(Guid eventId)
    {
        var db = _redis.GetDatabase();
        var key = $"processed:event:{eventId}";

        // SET NX (set if not exists) con TTL
        var wasSet = await db.StringSetAsync(
            key,
            DateTime.UtcNow.ToString("O"),
            _ttl,
            When.NotExists);

        return wasSet; // true = primera vez, false = duplicado
    }
}

// Uso
var isFirstTime = await _cache.TryMarkAsProcessedAsync(eventId);

if (!isFirstTime)
{
    _logger.LogWarning("Duplicate event {EventId}, skipping", eventId);
    return ProcessingResult.Duplicate;
}

// Procesar...
```

**Ventajas:**

- Muy rápido (< 1ms)
- TTL automático (cleanup gratis)
- Reduce carga en PostgreSQL

**Desventajas:**

- Si Redis falla, podrían haber duplicados
- No es persistente (solo caché)

➡️ **Recomendación**: Usar Redis + PostgreSQL en conjunto:

- Redis para chequeo rápido (mayoría de casos)
- PostgreSQL como backup y para auditoría

---

## 7. Idempotency en APIs (HTTP)

### Cliente Envía Idempotency Key

```http
POST /api/payments HTTP/1.1
Host: api.talma.com
Authorization: Bearer <token>
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "amount": 100.00,
  "currency": "PEN",
  "customerId": "cust_123"
}
```

### API Almacena Resultado

```csharp
[HttpPost]
public async Task<IActionResult> CreatePayment(
    [FromBody] CreatePaymentRequest request,
    [FromHeader(Name = "Idempotency-Key")] Guid? idempotencyKey)
{
    if (idempotencyKey == null)
    {
        return BadRequest("Idempotency-Key header is required");
    }

    // Check si ya existe
    var existing = await _dbContext.IdempotentRequests
        .FirstOrDefaultAsync(r => r.IdempotencyKey == idempotencyKey);

    if (existing != null)
    {
        // Retornar resultado guardado
        return StatusCode(
            existing.StatusCode,
            JsonSerializer.Deserialize<object>(existing.ResponseBody));
    }

    // Procesar nueva request
    var payment = await _paymentService.CreateAsync(request);

    // Guardar resultado para futuras requests
    var idempotentRequest = new IdempotentRequest
    {
        IdempotencyKey = idempotencyKey.Value,
        StatusCode = 201,
        ResponseBody = JsonSerializer.Serialize(payment),
        CreatedAt = DateTime.UtcNow
    };

    _dbContext.IdempotentRequests.Add(idempotentRequest);
    await _dbContext.SaveChangesAsync();

    return CreatedAtAction(nameof(GetPayment), new { id = payment.Id }, payment);
}
```

---

## 8. Validación de Cumplimiento

```bash
# Verificar tabla processed_events existe
psql -h localhost -U app_user -d app_db -c "\d processed_events"

# Consultar eventos duplicados detectados
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  event_type,
  COUNT(*) as total_processed,
  COUNT(CASE WHEN result_status = 'duplicate' THEN 1 END) as duplicates
FROM processed_events
WHERE processed_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type;
EOF

# Verificar tasa de duplicados (debe ser < 5%)
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  ROUND(
    100.0 * COUNT(CASE WHEN result_status = 'duplicate' THEN 1 END) / COUNT(*),
    2
  ) as duplicate_rate_pct
FROM processed_events
WHERE processed_at > NOW() - INTERVAL '24 hours';
EOF
```

---

## 9. Referencias

**Patterns:**

- [Idempotent Receiver Pattern (Enterprise Integration Patterns)](https://www.enterpriseintegrationpatterns.com/patterns/messaging/IdempotentReceiver.html)
- [At-Least-Once Delivery (Kafka)](https://kafka.apache.org/documentation/#semantics)

**IETF:**

- [RFC 7231 - HTTP Idempotent Methods](https://datatracker.ietf.org/doc/html/rfc7231#section-4.2.2)

**Stripe:**

- [Idempotent Requests (Stripe API)](https://stripe.com/docs/api/idempotent_requests)
