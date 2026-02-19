# Transactional Outbox Pattern

> **Guía de implementación** para garantizar atomicidad entre PostgreSQL y Kafka.

- **Decisión arquitectónica**: Ver [ADR-008: Kafka Mensajería Asíncrona](/docs/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona)

---

## 📋 Propósito

Garantizar que los eventos publicados a Kafka ([ADR-008](/docs/decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona)) sean consistentes con las transacciones en PostgreSQL ([ADR-006](/docs/decisiones-de-arquitectura/adr-006-postgresql-base-datos)), resolviendo el problema de **dual-write**.

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
│  ┌───────────────────────────────────────────────────┐ │
│  │ BEGIN TRANSACTION                                 │ │
│  │                                                   │ │
│  │  1. INSERT INTO pedidos (...)                    │ │
│  │  2. INSERT INTO outbox_events (event_data)       │ │
│  │                                                   │ │
│  │ COMMIT  ← ATOMICIDAD GARANTIZADA                 │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Outbox Publisher (Background Service)                  │
│                                                         │
│  while (true):                                          │
│    events = SELECT * FROM outbox_events                │
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
            var evento = new OutboxEvent
            {
                AggregateType = "Pedido",
                AggregateId = pedido.Id,
                EventType = "PedidoCreado",
                Payload = JsonSerializer.Serialize(new PedidoCreadoEvent
                {
                    PedidoId = pedido.Id,
                    ClienteId = pedido.ClienteId,
                    Total = pedido.Total,
                    TenantId = pedido.TenantId
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

    public OutboxPublisher(
        IServiceProvider services,
        ILogger<OutboxPublisher> logger,
        OutboxMetrics metrics)
    {
        _services = services;
        _logger = logger;
        _metrics = metrics;
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

        var events = await db.OutboxEvents
            .Where(e => !e.Published)
            .OrderBy(e => e.SequenceNumber)
            .Take(100)
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
            await PublishEventAsync(evt, kafka, db, ct);
        }

        await db.SaveChangesAsync(ct);
    }

    private async Task PublishEventAsync(
        OutboxEvent evt,
        IProducer<string, string> kafka,
        AppDbContext db,
        CancellationToken ct)
    {
        using var timer = _metrics.MeasurePublishLatency();

        try
        {
            var result = await kafka.ProduceAsync(
                evt.EventType,
                new Message<string, string>
                {
                    Key = evt.AggregateId.ToString(),
                    Value = evt.Payload,
                    Headers = new Headers
                    {
                        { "tenant-id", Encoding.UTF8.GetBytes(evt.TenantId) },
                        { "event-id", Encoding.UTF8.GetBytes(evt.Id.ToString()) },
                        { "event-type", Encoding.UTF8.GetBytes(evt.EventType) },
                        { "created-at", Encoding.UTF8.GetBytes(evt.CreatedAt.ToString("O")) }
                    }
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

## 📊 Observabilidad

### Métricas Prometheus

```csharp
public class OutboxMetrics
{
    private static readonly Counter PublishedEvents = Metrics
        .CreateCounter(
            "outbox_events_published_total",
            "Total de eventos publicados exitosamente",
            new CounterConfiguration { LabelNames = new[] { "event_type" } }
        );

    private static readonly Counter RetryEvents = Metrics
        .CreateCounter(
            "outbox_events_retry_total",
            "Total de reintentos de publicación",
            new CounterConfiguration { LabelNames = new[] { "event_type" } }
        );

    private static readonly Counter DeadLetterEvents = Metrics
        .CreateCounter(
            "outbox_events_dead_letter_total",
            "Total de eventos enviados a DLQ",
            new CounterConfiguration { LabelNames = new[] { "event_type" } }
        );

    private static readonly Gauge PendingEvents = Metrics
        .CreateGauge(
            "outbox_events_pending",
            "Número de eventos pendientes de publicar"
        );

    private static readonly Histogram PublishLatency = Metrics
        .CreateHistogram(
            "outbox_publish_latency_seconds",
            "Latencia de publicación de eventos",
            new HistogramConfiguration
            {
                Buckets = Histogram.ExponentialBuckets(0.001, 2, 10)
            }
        );

    public void IncrementPublished(string eventType) =>
        PublishedEvents.WithLabels(eventType).Inc();

    public void IncrementRetry(string eventType) =>
        RetryEvents.WithLabels(eventType).Inc();

    public void IncrementDeadLetter(string eventType) =>
        DeadLetterEvents.WithLabels(eventType).Inc();

    public void UpdatePendingCount(int count) =>
        PendingEvents.Set(count);

    public IDisposable MeasurePublishLatency() =>
        PublishLatency.NewTimer();
}
```

### Dashboard Grafana (queries)

```promql
# Tasa de eventos publicados por minuto
rate(outbox_events_published_total[1m])

# Eventos pendientes
outbox_events_pending

# Latencia p99 de publicación
histogram_quantile(0.99, rate(outbox_publish_latency_seconds_bucket[5m]))

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

    public async Task HandlePedidoCreadoAsync(PedidoCreadoEvent evt)
    {
        // Verificar si ya procesamos este evento
        var yaProcessed = await _db.ProcessedEvents
            .AnyAsync(e => e.EventId == evt.EventId);

        if (yaProcessed)
        {
            _logger.LogInformation("Evento {EventId} ya procesado, ignorando", evt.EventId);
            return;
        }

        // Procesar evento
        await ProcesarPedidoAsync(evt);

        // Marcar como procesado
        _db.ProcessedEvents.Add(new ProcessedEvent { EventId = evt.EventId });
        await _db.SaveChangesAsync();
    }
}
```

### Orden de Eventos

Los eventos **por agregado** mantienen orden garantizado (mismo `aggregate_id` → misma partition key):

```csharp
// Kafka garantiza orden dentro de la misma partición
var message = new Message<string, string>
{
    Key = evt.AggregateId.ToString(), // ← Mismo agregado = misma partición
    Value = evt.Payload
};
```

### Performance

- **Overhead por transacción**: ~30-50ms (INSERT adicional en outbox)
- **Latencia de publicación**: 5-10s (configurable con polling interval)
- **Throughput**: 1K-10K eventos/seg (suficiente para mayoría de casos)

### Cuándo NO usar Outbox

- **Eventos en tiempo real crítico** (`<1slatencia`): considerar CDC (Debezium)
- **Alto volumen** (`>100Keventos/seg`): CDC es más eficiente
- **Eventos no críticos**: best-effort directo a Kafka puede ser suficiente

---

## 🔗 Referencias

- [Transactional Outbox Pattern - Microservices.io](https://microservices.io/patterns/data/transactional-outbox.html)
- [Saga Pattern - Microsoft](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga)
- [Implementing the Outbox Pattern](https://debezium.io/blog/2019/02/19/reliable-microservices-data-exchange-with-the-outbox-pattern/)
- [ADR-008: Kafka Mensajería Asíncrona](../decisiones-de-arquitectura/adr-008-kafka-mensajeria-asincrona.md)
- [ADR-006: PostgreSQL Base de Datos](../decisiones-de-arquitectura/adr-006-postgresql-base-datos.md)

---

**Última actualización:** Febrero 2026
**Mantenido por:** Equipo de Arquitectura
