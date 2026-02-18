---
id: idempotency
sidebar_position: 10
title: Idempotencia
description: Implementación de consumidores idempotentes para prevenir procesamiento duplicado de eventos
---

# Idempotencia

## Contexto

Este estándar define cómo implementar consumidores idempotentes que pueden procesar el mismo evento múltiples veces sin efectos secundarios duplicados. Complementa el [lineamiento de Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) especificando **cómo** garantizar que los consumidores sean idempotentes usando PostgreSQL como registro de eventos procesados.

**Decisión arquitectónica:** [ADR-012: Apache Kafka para mensajería asíncrona](../../../decisiones-de-arquitectura/adr-012-kafka-mensajeria-asincrona.md)

---

## Stack Tecnológico

| Componente        | Tecnología      | Versión | Uso                            |
| ----------------- | --------------- | ------- | ------------------------------ |
| **Lenguaje**      | .NET 8 (C#)     | 8.0+    | Lógica de consumidores         |
| **Base de Datos** | PostgreSQL      | 14+     | Registro de eventos procesados |
| **ORM**           | EF Core         | 8.0+    | Acceso a datos                 |
| **Mensajería**    | Apache Kafka    | 3.6+    | Recepción de eventos           |
| **Cliente Kafka** | Confluent.Kafka | 2.3+    | Consumer implementation        |

### Dependencias NuGet

```xml
<PackageReference Include="Confluent.Kafka" Version="2.3.0" />
<PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />
```

---

## Implementación Técnica

### Tabla de Eventos Procesados

```sql
CREATE TABLE processed_events (
    event_id            UUID PRIMARY KEY,
    event_type          VARCHAR(100) NOT NULL,
    aggregate_id        UUID NOT NULL,
    processed_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    processing_duration_ms INT NOT NULL,
    consumer_name       VARCHAR(100) NOT NULL,

    INDEX idx_aggregate (aggregate_id, event_type),
    INDEX idx_processed_at (processed_at)
);

-- Índice para limpieza de eventos antiguos
CREATE INDEX idx_cleanup ON processed_events (processed_at)
WHERE processed_at < NOW() - INTERVAL '90 days';
```

### Modelo de Evento Procesado

```csharp
public class ProcessedEvent
{
    public Guid EventId { get; init; }
    public string EventType { get; init; } = null!;
    public Guid AggregateId { get; init; }
    public DateTime ProcessedAt { get; init; }
    public int ProcessingDurationMs { get; init; }
    public string ConsumerName { get; init; } = null!;
}

public class ApplicationDbContext : DbContext
{
    public DbSet<ProcessedEvent> ProcessedEvents { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<ProcessedEvent>(entity =>
        {
            entity.HasKey(e => e.EventId);
            entity.Property(e => e.EventType).HasMaxLength(100).IsRequired();
            entity.Property(e => e.ConsumerName).HasMaxLength(100).IsRequired();

            entity.HasIndex(e => new { e.AggregateId, e.EventType });
            entity.HasIndex(e => e.ProcessedAt);
        });
    }
}
```

### Patrón: Check-Process-Register

```csharp
public interface IIdempotentEventHandler<TEvent>
{
    Task HandleAsync(TEvent evt, CancellationToken ct);
}

public class IdempotentEventHandler<TEvent> : IIdempotentEventHandler<TEvent>
    where TEvent : IEvent
{
    private readonly ApplicationDbContext _dbContext;
    private readonly IEventProcessor<TEvent> _processor;
    private readonly ILogger<IdempotentEventHandler<TEvent>> _logger;
    private readonly string _consumerName;

    public async Task HandleAsync(TEvent evt, CancellationToken ct)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            // 1. CHECK: Verificar si ya fue procesado
            var alreadyProcessed = await _dbContext.ProcessedEvents
                .AnyAsync(e => e.EventId == evt.EventId, ct);

            if (alreadyProcessed)
            {
                _logger.LogWarning(
                    "Evento duplicado detectado | EventId={EventId} EventType={EventType}",
                    evt.EventId,
                    evt.EventType
                );
                return; // Salir sin procesar
            }

            // 2. PROCESS: Ejecutar lógica de negocio en transacción
            await using var transaction = await _dbContext.Database
                .BeginTransactionAsync(ct);

            try
            {
                // Procesar evento
                await _processor.ProcessAsync(evt, ct);

                // 3. REGISTER: Registrar como procesado (misma transacción)
                await _dbContext.ProcessedEvents.AddAsync(new ProcessedEvent
                {
                    EventId = evt.EventId,
                    EventType = evt.EventType,
                    AggregateId = evt.AggregateId,
                    ProcessedAt = DateTime.UtcNow,
                    ProcessingDurationMs = (int)stopwatch.ElapsedMilliseconds,
                    ConsumerName = _consumerName
                }, ct);

                await _dbContext.SaveChangesAsync(ct);
                await transaction.CommitAsync(ct);

                _logger.LogInformation(
                    "Evento procesado exitosamente | EventId={EventId} Duration={Duration}ms",
                    evt.EventId,
                    stopwatch.ElapsedMilliseconds
                );
            }
            catch
            {
                await transaction.RollbackAsync(ct);
                throw;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Error procesando evento | EventId={EventId} EventType={EventType}",
                evt.EventId,
                evt.EventType
            );
            throw;
        }
    }
}
```

### Consumer Idempotent Completo

```csharp
public class OrderCreatedConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<OrderCreatedConsumer> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("order.ordercreated");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var result = _consumer.Consume(stoppingToken);

                using var scope = _serviceProvider.CreateScope();
                var handler = scope.ServiceProvider
                    .GetRequiredService<IIdempotentEventHandler<OrderCreatedEvent>>();

                var evt = JsonSerializer.Deserialize<OrderCreatedEvent>(
                    result.Message.Value
                );

                // Handler maneja idempotencia internamente
                await handler.HandleAsync(evt, stoppingToken);

                // Commit solo después de procesamiento exitoso
                _consumer.Commit(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error en consumer");
                // Implementar retry logic o DLQ
            }
        }
    }
}
```

### Procesador de Negocio Específico

```csharp
public interface IEventProcessor<TEvent>
{
    Task ProcessAsync(TEvent evt, CancellationToken ct);
}

public class OrderCreatedProcessor : IEventProcessor<OrderCreatedEvent>
{
    private readonly ApplicationDbContext _dbContext;
    private readonly IEmailService _emailService;

    public async Task ProcessAsync(OrderCreatedEvent evt, CancellationToken ct)
    {
        // Lógica de negocio (ejecutada solo si evento no fue procesado antes)

        // 1. Crear factura
        var invoice = new Invoice
        {
            Id = Guid.NewGuid(),
            OrderId = evt.Payload.OrderId,
            CustomerId = evt.Payload.CustomerId,
            Amount = evt.Payload.TotalAmount,
            Currency = evt.Payload.Currency,
            CreatedAt = DateTime.UtcNow
        };

        await _dbContext.Invoices.AddAsync(invoice, ct);

        // 2. Enviar notificación (operación externa)
        await _emailService.SendOrderConfirmationAsync(
            evt.Payload.CustomerEmail,
            evt.Payload.OrderId,
            ct
        );

        // No guardar cambios aquí - el handler lo hace en la misma transacción
    }
}
```

### Idempotencia con Operaciones Externas

Cuando hay llamadas a servicios externos (APIs, emails, etc.) que no pueden revertirse:

```csharp
public class IdempotentExternalOperationHandler
{
    private readonly ApplicationDbContext _dbContext;
    private readonly IExternalService _externalService;

    public async Task HandleAsync(OrderCreatedEvent evt, CancellationToken ct)
    {
        // 1. Verificar evento ya procesado
        var processed = await _dbContext.ProcessedEvents
            .FirstOrDefaultAsync(e => e.EventId == evt.EventId, ct);

        if (processed != null)
        {
            _logger.LogWarning("Evento duplicado, operación externa ya ejecutada");
            return;
        }

        await using var transaction = await _dbContext.Database
            .BeginTransactionAsync(ct);

        try
        {
            // 2. Registrar intención ANTES de operación externa
            var intentRecord = new ProcessedEvent
            {
                EventId = evt.EventId,
                EventType = evt.EventType,
                AggregateId = evt.AggregateId,
                ProcessedAt = DateTime.UtcNow,
                ProcessingDurationMs = 0,
                ConsumerName = "order-notifier"
            };

            await _dbContext.ProcessedEvents.AddAsync(intentRecord, ct);
            await _dbContext.SaveChangesAsync(ct);
            await transaction.CommitAsync(ct);

            // 3. Ejecutar operación externa DESPUÉS de commit
            // Si falla, el registro existe y no se reintentará
            await _externalService.NotifyAsync(evt, ct);

            _logger.LogInformation(
                "Operación externa completada | EventId={EventId}",
                evt.EventId
            );
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync(ct);
            _logger.LogError(ex, "Error en operación externa");
            throw;
        }
    }
}
```

### Idempotencia con Idempotency Key

Para APIs externas que soportan idempotency keys:

```csharp
public class PaymentProcessor
{
    private readonly IPaymentGateway _paymentGateway;

    public async Task ProcessPaymentAsync(PaymentRequestedEvent evt, CancellationToken ct)
    {
        // Usar EventId como idempotency key
        var paymentResult = await _paymentGateway.ChargeAsync(new PaymentRequest
        {
            IdempotencyKey = evt.EventId.ToString(),  // ← Clave de idempotencia
            Amount = evt.Amount,
            Currency = evt.Currency,
            CustomerId = evt.CustomerId,
            Description = $"Order {evt.OrderId}"
        }, ct);

        // Gateway garantiza que mismo idempotencyKey no procesa 2 veces
        // Aunque este método se llame múltiples veces
    }
}
```

### Limpieza de Eventos Antiguos

```csharp
public class ProcessedEventsCleanupService : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly TimeSpan _retentionPeriod = TimeSpan.FromDays(90);
    private readonly TimeSpan _cleanupInterval = TimeSpan.FromHours(24);

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();
                var dbContext = scope.ServiceProvider
                    .GetRequiredService<ApplicationDbContext>();

                var cutoffDate = DateTime.UtcNow - _retentionPeriod;

                var deletedCount = await dbContext.Database
                    .ExecuteSqlInterpolatedAsync(
                        $"DELETE FROM processed_events WHERE processed_at < {cutoffDate}",
                        stoppingToken
                    );

                _logger.LogInformation(
                    "Limpieza de eventos completada | Eliminados={Count}",
                    deletedCount
                );

                await Task.Delay(_cleanupInterval, stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error en limpieza de eventos");
                await Task.Delay(TimeSpan.FromMinutes(5), stoppingToken);
            }
        }
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** verificar si evento ya fue procesado antes de ejecutar lógica de negocio
- **MUST** registrar eventos procesados en la misma transacción que cambios de negocio
- **MUST** usar `event_id` como identificador único para deduplicación
- **MUST** hacer commit de Kafka solo después de registro exitoso en BD
- **MUST** hacer operaciones idempotentes cuando no se puede usar transacción (APIs externas)
- **MUST** usar índices en tabla `processed_events` para performance
- **MUST** implementar limpieza periódica de eventos antiguos
- **MUST** logear eventos duplicados detectados

### SHOULD (Fuertemente recomendado)

- **SHOULD** almacenar `processing_duration_ms` para análisis de performance
- **SHOULD** almacenar `consumer_name` para troubleshooting
- **SHOULD** retener eventos procesados al menos 30 días (recomendado 90 días)
- **SHOULD** usar idempotency keys cuando APIs externas las soporten
- **SHOULD** monitorear tasa de eventos duplicados
- **SHOULD** registrar intención antes de operaciones externas no reversibles

### MAY (Opcional)

- **MAY** almacenar hash del payload para validación adicional
- **MAY** implementar TTL automático en PostgreSQL
- **MAY** usar Redis como caché de eventos recientes para performance

### MUST NOT (Prohibido)

- **MUST NOT** hacer commit de Kafka antes de procesar evento
- **MUST NOT** confiar solo en `EnableIdempotence` del producer (no suficiente en consumer)
- **MUST NOT** procesar eventos fuera de transacción cuando hay cambios en BD
- **MUST NOT** asumir que eventos nunca se duplicarán

---

## Estrategias de Idempotencia

### 1. Database Transaction (Preferido)

```csharp
// ✅ Idempotencia garantizada por transacción
await using var tx = await db.BeginTransactionAsync();
if (!await db.ProcessedEvents.AnyAsync(e => e.EventId == evt.EventId))
{
    await ProcessBusinessLogic(evt);
    await db.ProcessedEvents.AddAsync(new ProcessedEvent { ... });
    await db.SaveChangesAsync();
}
await tx.CommitAsync();
```

### 2. Natural Idempotency (Operaciones SET)

```csharp
// ✅ Operación naturalmente idempotente (asignar valor, no acumular)
public async Task UpdateCustomerEmailAsync(CustomerEmailChangedEvent evt)
{
    var customer = await db.Customers.FindAsync(evt.CustomerId);
    customer.Email = evt.NewEmail;  // SET operation (idempotent)
    await db.SaveChangesAsync();
}

// ❌ Operación NO idempotente (acumulación)
public async Task ProcessPaymentAsync(PaymentReceivedEvent evt)
{
    var account = await db.Accounts.FindAsync(evt.AccountId);
    account.Balance += evt.Amount;  // ❌ Si se procesa 2 veces, duplica balance
    await db.SaveChangesAsync();
}
```

### 3. Idempotency Key en APIs Externas

```csharp
// ✅ API externa con idempotency key
await paymentGateway.ProcessAsync(new
{
    IdempotencyKey = evt.EventId,
    Amount = evt.Amount
});
```

---

## Anti-Patrones

### ❌ #1: No Verificar Duplicados

```csharp
// ❌ INCORRECTO
public async Task HandleAsync(OrderCreatedEvent evt)
{
    var invoice = new Invoice { ... };
    await db.Invoices.AddAsync(invoice);
    await db.SaveChangesAsync();
    // ❌ Si evento se repite, crea factura duplicada
}

// ✅ CORRECTO
public async Task HandleAsync(OrderCreatedEvent evt)
{
    if (await db.ProcessedEvents.AnyAsync(e => e.EventId == evt.EventId))
        return;

    var invoice = new Invoice { ... };
    await db.Invoices.AddAsync(invoice);
    await db.ProcessedEvents.AddAsync(new ProcessedEvent { ... });
    await db.SaveChangesAsync();
}
```

### ❌ #2: Commit Kafka Antes de Procesar

```csharp
// ❌ INCORRECTO
var result = consumer.Consume();
consumer.Commit(result);  // ❌ Commit antes de procesar
await HandleAsync(evt);   // Si falla, evento se pierde

// ✅ CORRECTO
var result = consumer.Consume();
await HandleAsync(evt);   // Procesar primero
consumer.Commit(result);  // Commit después de éxito
```

### ❌ #3: Operaciones Acumulativas sin Check

```csharp
// ❌ INCORRECTO
account.Balance += payment.Amount;  // ❌ Duplica si evento se repite

// ✅ CORRECTO
if (!await IsProcessedAsync(payment.EventId))
{
    account.Balance += payment.Amount;
    await MarkAsProcessedAsync(payment.EventId);
}
```

---

## Referencias

- [Lineamiento: Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)
- [ADR-012: Apache Kafka para mensajería asíncrona](../../../decisiones-de-arquitectura/adr-012-kafka-mensajeria-asincrona.md)
- Estándares relacionados:
  - [Mensajería Asíncrona](async-messaging.md)
  - [Diseño de Eventos](event-design.md)
  - [Garantías de Entrega](message-delivery-guarantees.md)
