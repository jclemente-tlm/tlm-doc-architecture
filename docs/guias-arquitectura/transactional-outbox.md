# Transactional Outbox Pattern

> **Guía de implementación** para garantizar atomicidad entre PostgreSQL y Kafka.

- **Decisión arquitectónica**: Ver [ADR-008: Kafka Mensajería Asíncrona](/docs/adrs/adr-008-kafka-mensajeria-asincrona)

---

## 📋 Propósito

Garantizar que los eventos publicados a Kafka ([ADR-008](/docs/adrs/adr-008-kafka-mensajeria-asincrona)) sean consistentes con las transacciones en PostgreSQL ([ADR-006](/docs/adrs/adr-006-postgresql-base-datos)), resolviendo el problema de **dual-write**.

## 🎯 Casos de Uso

- Publicar eventos de dominio después de guardar entidades
- Garantizar que servicios downstream reciban notificaciones
- Mantener consistencia eventual entre microservicios
- Implementar SAGA patterns distribuidos

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│  Servicio (API)                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │ BEGIN TRANSACTION                                 │  │
│  │                                                   │  │
│  │  1. INSERT INTO pedidos (...)                     │  │
│  │  2. INSERT INTO outbox_events (event_data)        │  │
│  │                                                   │  │
│  │ COMMIT  ← ATOMICIDAD GARANTIZADA                  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Outbox Publisher (Background Service)                  │
│                                                         │
│  while (true):                                          │
│    events = SELECT * FROM outbox_events                 │
│             WHERE published = false                     │
│                                                         │
│    foreach event:                                       │
│      kafka.Publish(event)                               │
│      UPDATE outbox_events SET published = true          │
│                                                         │
│    sleep(5 seconds)                                     │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
                  ┌──────────┐
                  │  Kafka   │
                  └──────────┘
```

---

## 📐 Esquema de Base de Datos

### Tabla Outbox Events

```sql
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identificación del agregado
    aggregate_type VARCHAR(255) NOT NULL,
    aggregate_id UUID NOT NULL,

    -- Evento
    event_type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,

    -- Control de procesamiento
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at TIMESTAMP NULL,
    published BOOLEAN NOT NULL DEFAULT FALSE,

    -- Retry y error handling
    retry_count INT NOT NULL DEFAULT 0,
    error_message TEXT NULL,

    -- Multi-tenancy
    tenant_id VARCHAR(50) NOT NULL,

    -- Trazabilidad
    correlation_id VARCHAR(255) NULL,                   -- TraceId de la request HTTP que originó el evento

    -- Garantía de orden
    sequence_number BIGSERIAL NOT NULL
);

-- Índice para polling eficiente
CREATE INDEX idx_outbox_pending
ON outbox_events (published, created_at, tenant_id)
WHERE NOT published;

-- Índice para orden por agregado
CREATE INDEX idx_outbox_aggregate
ON outbox_events (aggregate_type, aggregate_id, sequence_number);

-- Índice para limpieza de eventos antiguos
CREATE INDEX idx_outbox_cleanup
ON outbox_events (published, published_at)
WHERE published = true;
```

### Descripción de Campos

| Campo             | Tipo           | Nulo | Descripción                                                                                                                                                               |
| ----------------- | -------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`              | `UUID`         | No   | Identificador único del evento. Se usa como `id` en el envelope CloudEvents — garantía de idempotencia en consumidores.                                                   |
| `aggregate_type`  | `VARCHAR(255)` | No   | Nombre del agregado que originó el evento. Ej: `"Pedido"`, `"Cliente"`.                                                                                                   |
| `aggregate_id`    | `UUID`         | No   | ID de la instancia del agregado. Se usa como `Key` del mensaje Kafka para garantizar orden dentro de la partición.                                                        |
| `event_type`      | `VARCHAR(255)` | No   | Tipo de evento siguiendo la convención CloudEvents: `com.talma.{dominio}.{Evento}`. Ej: `com.talma.pedidos.PedidoCreado`.                                                 |
| `payload`         | `JSONB`        | No   | Datos de negocio del evento (solo el `data` del mensaje, sin metadata de transporte).                                                                                     |
| `created_at`      | `TIMESTAMP`    | No   | Momento en que ocurrió el hecho de negocio. Se mapea al campo `time` del envelope CloudEvents.                                                                            |
| `published_at`    | `TIMESTAMP`    | Sí   | Momento en que el Publisher confirmó la publicación en Kafka. `NULL` mientras no se haya publicado.                                                                       |
| `published`       | `BOOLEAN`      | No   | Indica si el evento ya fue publicado. El Publisher usa este campo para el polling (`WHERE NOT published`).                                                                |
| `retry_count`     | `INT`          | No   | Número de intentos fallidos de publicación. Al llegar a 5 el evento se mueve a la DLQ.                                                                                    |
| `error_message`   | `TEXT`         | Sí   | Último error registrado al intentar publicar. Útil para diagnóstico.                                                                                                      |
| `tenant_id`       | `VARCHAR(50)`  | No   | Identificador del tenant. Formato: `tlm-{país}`. Valores válidos: `tlm-pe`, `tlm-mx`, `tlm-ec`, `tlm-co`, `tlm-corp`. Se propaga al envelope CloudEvents como `tenantid`. |
| `correlation_id`  | `VARCHAR(255)` | Sí   | `TraceId` de OpenTelemetry de la request HTTP que originó el evento. Permite trazabilidad end-to-end en Tempo/Grafana.                                                    |
| `sequence_number` | `BIGSERIAL`    | No   | Número de secuencia auto-incremental generado por PostgreSQL. Define el orden de procesamiento en el Publisher.                                                           |

### Política de Retención (opcional)

```sql
-- Eliminar eventos publicados después de 7 días
CREATE OR REPLACE FUNCTION cleanup_outbox_events()
RETURNS void AS $$
BEGIN
    DELETE FROM outbox_events
    WHERE published = true
      AND published_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Job programado (usando pg_cron o similar)
-- SELECT cron.schedule('cleanup-outbox', '0 2 * * *', 'SELECT cleanup_outbox_events()');
```

---

## 💻 Implementación en .NET

### 1. Entidad Outbox Event

```csharp
public class OutboxEvent
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string AggregateType { get; set; } = default!;
    public Guid AggregateId { get; set; }
    public string EventType { get; set; } = default!;
    public string Payload { get; set; } = default!; // JSON serializado
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? PublishedAt { get; set; }
    public bool Published { get; set; }
    public int RetryCount { get; set; }
    public string? ErrorMessage { get; set; }
    public string TenantId { get; set; } = default!;
    public string? CorrelationId { get; set; }         // TraceId de la request HTTP que originó el evento
    public long SequenceNumber { get; set; }
}
```

### 2. Configuración EF Core

```csharp
public class AppDbContext : DbContext
{
    public DbSet<Pedido> Pedidos { get; set; }
    public DbSet<OutboxEvent> OutboxEvents { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<OutboxEvent>(entity =>
        {
            entity.ToTable("outbox_events");
            entity.HasKey(e => e.Id);

            entity.Property(e => e.AggregateType).HasMaxLength(255).IsRequired();
            entity.Property(e => e.EventType).HasMaxLength(255).IsRequired();
            entity.Property(e => e.Payload).HasColumnType("jsonb").IsRequired();
            entity.Property(e => e.TenantId).HasMaxLength(50).IsRequired();
            entity.Property(e => e.CorrelationId).HasMaxLength(255);
            entity.Property(e => e.SequenceNumber).ValueGeneratedOnAdd(); // BIGSERIAL — generado por PostgreSQL

            entity.HasIndex(e => new { e.Published, e.CreatedAt, e.TenantId })
                  .HasFilter("NOT published");

            entity.HasIndex(e => new { e.AggregateType, e.AggregateId, e.SequenceNumber });
        });
    }
}
```

### 3. Uso en Servicio de Aplicación

```csharp
public class PedidoService
{
    private readonly AppDbContext _db;
    private readonly ITenantContext _tenantContext;

    public async Task<Pedido> CrearPedidoAsync(CrearPedidoCommand cmd)
    {
        using var transaction = await _db.Database.BeginTransactionAsync();

        try
        {
            // 1. Persistir datos de negocio
            var pedido = new Pedido
            {
                Id = Guid.NewGuid(),
                ClienteId = cmd.ClienteId,
                Total = cmd.Items.Sum(i => i.Precio),
                TenantId = _tenantContext.TenantId
            };
            _db.Pedidos.Add(pedido);

            // 2. Agregar evento a outbox (misma transacción)
            // EventType: convención com.{org}.{dominio}.{Evento}
            var evento = new OutboxEvent
            {
                AggregateType = "Pedido",
                AggregateId   = pedido.Id,
                EventType     = "com.talma.pedidos.PedidoCreado",
                CorrelationId = Activity.Current?.TraceId.ToString(), // using System.Diagnostics
                Payload       = JsonSerializer.Serialize(new PedidoCreadoEvent
                {
                    PedidoId  = pedido.Id,
                    ClienteId = pedido.ClienteId,
                    Total     = pedido.Total,
                    TenantId  = pedido.TenantId
                }),
                TenantId = _tenantContext.TenantId
            };
            _db.OutboxEvents.Add(evento);

            // 3. Commit atómico (ambas escrituras o ninguna)
            await _db.SaveChangesAsync();
            await transaction.CommitAsync();

            return pedido;
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}
```

### 4. Publisher Background Service

```csharp
public class OutboxPublisher : BackgroundService
{
    private readonly IServiceProvider _services;
    private readonly ILogger<OutboxPublisher> _logger;
    private readonly OutboxMetrics _metrics;
    private readonly string _source;

    public OutboxPublisher(
        IServiceProvider services,
        ILogger<OutboxPublisher> logger,
        OutboxMetrics metrics,
        IConfiguration configuration)
    {
        _services = services;
        _logger = logger;
        _metrics = metrics;
        _source = configuration["Kafka:Source"] ?? "unknown-service"; // appsettings.json → Kafka:Source
    }

    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        _logger.LogInformation("Outbox Publisher iniciado");

        while (!ct.IsCancellationRequested)
        {
            try
            {
                await ProcessPendingEventsAsync(ct);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error procesando eventos outbox");
            }

            await Task.Delay(TimeSpan.FromSeconds(5), ct);
        }
    }

    private async Task ProcessPendingEventsAsync(CancellationToken ct)
    {
        using var scope = _services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        var kafka = scope.ServiceProvider.GetRequiredService<IProducer<string, string>>();

        // FOR UPDATE SKIP LOCKED: evita que múltiples instancias procesen el mismo lote
        var events = await db.OutboxEvents
            .Where(e => !e.Published)
            .OrderBy(e => e.SequenceNumber)
            .Take(100)
            .FromSql($"""
                SELECT * FROM outbox_events
                WHERE NOT published
                ORDER BY sequence_number
                LIMIT 100
                FOR UPDATE SKIP LOCKED
                """)
            .ToListAsync(ct);

        if (!events.Any())
        {
            _metrics.UpdatePendingCount(0);
            return;
        }

        _logger.LogInformation("Procesando {Count} eventos pendientes", events.Count);
        _metrics.UpdatePendingCount(events.Count);

        foreach (var evt in events)
        {
            await PublishEventAsync(evt, kafka, ct);
        }

        await db.SaveChangesAsync(ct);
    }

    private async Task PublishEventAsync(
        OutboxEvent evt,
        IProducer<string, string> kafka,
        CancellationToken ct)
    {
        using var timer = _metrics.MeasurePublishLatency();

        try
        {
            // Construir envelope CloudEvents 1.0 — toda la metadata viaja en el value
            var cloudEvent = JsonSerializer.Serialize(new
            {
                specversion     = "1.0",
                id              = evt.Id.ToString(),
                source          = _source,
                type            = evt.EventType,
                time            = evt.CreatedAt.ToString("O"),
                datacontenttype = "application/json",
                dataversion     = "1.0",
                tenantid        = evt.TenantId,
                correlationid   = evt.CorrelationId,
                data            = JsonSerializer.Deserialize<JsonElement>(evt.Payload)
            });

            var result = await kafka.ProduceAsync(
                evt.EventType,
                new Message<string, string>
                {
                    Key   = evt.AggregateId.ToString(),
                    Value = cloudEvent
                },
                ct
            );

            evt.Published = true;
            evt.PublishedAt = DateTime.UtcNow;

            _metrics.IncrementPublished(evt.EventType);
            _logger.LogInformation(
                "Evento publicado: {EventId} | Topic: {Topic} | Partition: {Partition} | Offset: {Offset}",
                evt.Id, result.Topic, result.Partition.Value, result.Offset.Value
            );
        }
        catch (ProduceException<string, string> ex)
        {
            evt.RetryCount++;
            evt.ErrorMessage = ex.Error.Reason;

            if (evt.RetryCount >= 5)
            {
                _logger.LogError(
                    "Evento {EventId} movido a DLQ después de {Retries} intentos: {Error}",
                    evt.Id, evt.RetryCount, ex.Error.Reason
                );

                // Publicar a dead-letter queue
                await kafka.ProduceAsync(
                    "dead-letter-queue",
                    new Message<string, string>
                    {
                        Key = evt.Id.ToString(),
                        Value = JsonSerializer.Serialize(new
                        {
                            OriginalEvent = evt,
                            Error = ex.Error.Reason,
                            Timestamp = DateTime.UtcNow
                        })
                    },
                    ct
                );

                evt.Published = true; // Marcar como procesado
                _metrics.IncrementDeadLetter(evt.EventType);
            }
            else
            {
                _logger.LogWarning(
                    "Error publicando evento {EventId}, reintento {Retry}/5: {Error}",
                    evt.Id, evt.RetryCount, ex.Error.Reason
                );
                _metrics.IncrementRetry(evt.EventType);
            }
        }
    }
}
```

### 5. Registro en Program.cs

```csharp
// Outbox Publisher
builder.Services.AddSingleton<OutboxMetrics>();
builder.Services.AddHostedService<OutboxPublisher>();

// Kafka Producer (singleton para reutilización)
builder.Services.AddSingleton<IProducer<string, string>>(sp =>
{
    var config = new ProducerConfig
    {
        BootstrapServers = builder.Configuration["Kafka:BootstrapServers"],
        ClientId = $"{Environment.MachineName}-{Guid.NewGuid()}",
        Acks = Acks.All, // Garantía de escritura
        EnableIdempotence = true, // Evita duplicados en retries
        MaxInFlight = 5,
        MessageSendMaxRetries = 3,
        CompressionType = CompressionType.Snappy
    };

    return new ProducerBuilder<string, string>(config)
        .SetKeySerializer(Serializers.Utf8)
        .SetValueSerializer(Serializers.Utf8)
        .Build();
});
```

---

## � Formato del Mensaje Kafka: CloudEvents 1.0

El **Outbox Pattern** garantiza la entrega del evento; **CloudEvents 1.0** define el formato del mensaje publicado en Kafka. Son responsabilidades separadas: la tabla `outbox_events` almacena los datos de negocio, y el `OutboxPublisher` construye el envelope al momento de publicar.

**Registro en la tabla** (`payload` = datos de negocio):

```json
{
  "id": "a3f1c2d4-8e71-4b92-bc3a-1234567890ab",
  "aggregate_type": "Pedido",
  "aggregate_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_type": "com.talma.pedidos.PedidoCreado",
  "correlation_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "payload": {
    "pedidoId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "clienteId": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "total": 250.0,
    "tenantId": "tlm-pe"
  },
  "tenant_id": "tlm-pe",
  "created_at": "2026-03-31T14:22:01.123Z",
  "published_at": null,
  "published": false,
  "retry_count": 0,
  "sequence_number": 1042
}
```

**Mensaje en Kafka** (envelope CloudEvents construido por el Publisher):

```json
{
  "specversion": "1.0",
  "id": "a3f1c2d4-8e71-4b92-bc3a-1234567890ab",
  "source": "pedidos-service",
  "type": "com.talma.pedidos.PedidoCreado",
  "time": "2026-03-31T14:22:01.123Z",
  "datacontenttype": "application/json",
  "dataversion": "1.0",
  "tenantid": "tlm-pe",
  "correlationid": "4bf92f3577b34da6a3ce929d0e0e4736",
  "data": {
    "pedidoId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "clienteId": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "total": 250.0,
    "tenantId": "tlm-pe"
  }
}
```

| Campo CloudEvents | Origen                            | Descripción                                                                                          |
| ----------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `specversion`     | Constante                         | Siempre `"1.0"` — versión del estándar CloudEvents.                                                  |
| `id`              | `OutboxEvent.Id`                  | UUID del registro en `outbox_events`. Los consumidores lo usan para garantizar idempotencia.         |
| `source`          | `appsettings.json → Kafka:Source` | Nombre del servicio emisor. Ej: `"pedidos-service"`.                                                 |
| `type`            | `OutboxEvent.EventType`           | Tipo de evento. Convención: `com.talma.{dominio}.{Evento}`. Ej: `com.talma.pedidos.PedidoCreado`.    |
| `time`            | `OutboxEvent.CreatedAt`           | Timestamp del hecho de negocio (no del momento de publicación).                                      |
| `datacontenttype` | Constante                         | Siempre `"application/json"`.                                                                        |
| `dataversion`     | Constante                         | Siempre `"1.0"`. Versión del esquema de `data` — permite evolución sin romper consumidores.          |
| `tenantid`        | `OutboxEvent.TenantId`            | Extensión corporativa de multi-tenancy. Valores: `tlm-pe`, `tlm-mx`, `tlm-ec`, `tlm-co`, `tlm-corp`. |
| `correlationid`   | `OutboxEvent.CorrelationId`       | `TraceId` de OpenTelemetry de la request HTTP original. Permite trazabilidad end-to-end en Tempo.    |
| `data`            | `OutboxEvent.Payload`             | Datos de negocio del evento, deserializados desde el JSONB almacenado en la tabla.                   |

---

## �📊 Observabilidad

### Métricas OpenTelemetry

```csharp
// using System.Diagnostics.Metrics; using System.Diagnostics;
public class OutboxMetrics
{
    private readonly Counter<long> _publishedEvents;
    private readonly Counter<long> _retryEvents;
    private readonly Counter<long> _deadLetterEvents;
    private readonly Histogram<double> _publishLatency;
    private int _pendingCount;

    public OutboxMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Outbox");

        _publishedEvents  = meter.CreateCounter<long>(
            "outbox.events.published",
            description: "Total de eventos publicados exitosamente");

        _retryEvents = meter.CreateCounter<long>(
            "outbox.events.retried",
            description: "Total de reintentos de publicación");

        _deadLetterEvents = meter.CreateCounter<long>(
            "outbox.events.dead_letter",
            description: "Total de eventos enviados a DLQ");

        _publishLatency = meter.CreateHistogram<double>(
            "outbox.publish.duration",
            unit: "s",
            description: "Latencia de publicación de eventos");

        meter.CreateObservableGauge(
            "outbox.events.pending",
            () => _pendingCount,
            description: "Número de eventos pendientes de publicar");
    }

    public void IncrementPublished(string eventType) =>
        _publishedEvents.Add(1, new KeyValuePair<string, object?>("event_type", eventType));

    public void IncrementRetry(string eventType) =>
        _retryEvents.Add(1, new KeyValuePair<string, object?>("event_type", eventType));

    public void IncrementDeadLetter(string eventType) =>
        _deadLetterEvents.Add(1, new KeyValuePair<string, object?>("event_type", eventType));

    public void UpdatePendingCount(int count) => _pendingCount = count;

    public IDisposable MeasurePublishLatency() => new LatencyTimer(_publishLatency);

    private sealed class LatencyTimer : IDisposable
    {
        private readonly Histogram<double> _histogram;
        private readonly long _start = Stopwatch.GetTimestamp();

        public LatencyTimer(Histogram<double> histogram) => _histogram = histogram;

        public void Dispose() =>
            _histogram.Record(Stopwatch.GetElapsedTime(_start).TotalSeconds);
    }
}
```

### Dashboard Grafana (queries)

```promql
# Tasa de eventos publicados por minuto
rate(outbox_events_published_total[1m])

# Eventos pendientes
outbox_events_pending

# Latencia p99 de publicación
histogram_quantile(0.99, rate(outbox_publish_duration_seconds_bucket[5m]))

# Tasa de errores (eventos en DLQ)
rate(outbox_events_dead_letter_total[5m])
```

---

## ⚠️ Consideraciones Importantes

### Idempotencia en Consumidores

Los consumidores de Kafka **DEBEN** manejar eventos duplicados (at-least-once delivery):

```csharp
public class PedidoEventHandler
{
    private readonly AppDbContext _db;
    private readonly ILogger<PedidoEventHandler> _logger;

    public PedidoEventHandler(AppDbContext db, ILogger<PedidoEventHandler> logger)
    {
        _db = db;
        _logger = logger;
    }

    // messageValue = Value del mensaje Kafka (envelope CloudEvents serializado como JSON)
    public async Task HandlePedidoCreadoAsync(string messageValue)
    {
        // Deserializar el envelope CloudEvents 1.0
        var envelope = JsonSerializer.Deserialize<JsonElement>(messageValue);
        var eventId  = envelope.GetProperty("id").GetString()!;
        var data     = JsonSerializer.Deserialize<PedidoCreadoEvent>(
                           envelope.GetProperty("data").GetRawText())!;

        // Verificar si ya procesamos este evento (campo 'id' del envelope)
        var alreadyProcessed = await _db.ProcessedEvents
            .AnyAsync(e => e.EventId == eventId);

        if (alreadyProcessed)
        {
            _logger.LogInformation("Evento {EventId} ya procesado, ignorando", eventId);
            return;
        }

        // Procesar evento con los datos de negocio
        await ProcesarPedidoAsync(data);

        // Marcar como procesado
        _db.ProcessedEvents.Add(new ProcessedEvent { EventId = eventId });
        await _db.SaveChangesAsync();
    }
}
```

### Orden de Eventos

Kafka garantiza orden dentro de una partición. Usando `AggregateId` como `Key` del mensaje (ver `PublishEventAsync`), todos los eventos del mismo agregado van a la misma partición — el orden queda garantizado sin configuración adicional.

### Performance

- **Overhead por transacción**: ~30-50ms (INSERT adicional en outbox)
- **Latencia de publicación**: 5-10s (configurable con polling interval)
- **Throughput**: 1K-10K eventos/seg (suficiente para mayoría de casos)

### Cuándo NO usar Outbox

- **Eventos en tiempo real crítico** (< 1s de latencia): considerar CDC (Debezium)
- **Alto volumen** (> 100K eventos/seg): CDC es más eficiente
- **Eventos no críticos**: best-effort directo a Kafka puede ser suficiente

---

## 🔗 Referencias

- [Transactional Outbox Pattern - Microservices.io](https://microservices.io/patterns/data/transactional-outbox.html)
- [Saga Pattern - Microsoft](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga)
- [CloudEvents 1.0 — Especificación CNCF](https://cloudevents.io/)
- [CloudEvents — Kafka Protocol Binding](https://github.com/cloudevents/spec/blob/main/cloudevents/bindings/kafka-protocol-binding.md)
- [Implementing the Outbox Pattern](https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/)
- [ADR-008: Kafka Mensajería Asíncrona](../adrs/adr-008-kafka-mensajeria-asincrona.md)
- [ADR-006: PostgreSQL Base de Datos](../adrs/adr-006-postgresql-base-datos.md)

---

**Última actualización:** Marzo 2026
**Mantenido por:** Equipo de Arquitectura
