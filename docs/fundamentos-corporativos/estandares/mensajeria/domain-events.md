---
id: domain-events
sidebar_position: 5
title: Domain Events
description: Estándar para modelado de eventos de dominio en arquitectura event-driven, incluyendo naming, payload, versionado y publicación asíncrona.
---

# Estándar Técnico — Domain Events

---

## 1. Propósito

Modelar eventos de dominio siguiendo **Event-Driven Architecture** y **Domain-Driven Design (DDD)**, garantizando comunicación asíncrona desacoplada entre bounded contexts mediante eventos inmutables y versionados.

---

## 2. Alcance

**Aplica a:**

- Comunicación entre microservicios (bounded contexts)
- Event sourcing (almacenar eventos como source of truth)
- Notificaciones asíncronas (emails, webhooks)
- Integración con sistemas externos
- Auditoria y trazabilidad

**No aplica a:**

- Comandos síncronos (usar APIs REST/gRPC)
- Request-response inmediatos (usar HTTP)
- Eventos de infraestructura (logs, métricas)

---

## 3. Conceptos Clave

### 3.1 Domain Event vs Command

| Aspecto           | **Domain Event**                    | **Command**                |
| ----------------- | ----------------------------------- | -------------------------- |
| **Tiempo verbal** | Pasado (`OrderCreated`)             | Imperativo (`CreateOrder`) |
| **Intención**     | Notificar algo que YA ocurrió       | Solicitar que algo ocurra  |
| **Handlers**      | 0..N (múltiples subscriptores)      | 1 (un único handler)       |
| **Fallo**         | NO afecta transacción original      | Puede rechazar comando     |
| **Idempotencia**  | Crítica (eventos pueden duplicarse) | Deseable                   |

**Ejemplo:**

```csharp
// ❌ MAL: Comando disfrazado de evento
public record CreateOrderEvent(string UserId, decimal Total);

// ✅ BIEN: Evento de dominio
public record OrderCreatedEvent(Guid OrderId, string UserId, decimal Total, DateTime CreatedAt);
```

### 3.2 Características de Domain Events

- **Inmutables**: NO se modifican después de creados
- **Pasado**: Representan hechos que YA ocurrieron
- **Negocio**: Nombrados en lenguaje del dominio (Ubiquitous Language)
- **Versionados**: Incluyen versión de schema para evolución
- **Metadata**: Timestamp, correlation ID, causation ID

---

## 4. Requisitos Obligatorios 🔴

### 4.1 Naming Convention

- [ ] Tiempo pasado: `{Entity}{Action}Event` (ej: `OrderCreatedEvent`, `PaymentProcessedEvent`)
- [ ] Lenguaje del dominio (ubiquitous language)
- [ ] Verbos de negocio, NO técnicos:
  - ✅ `OrderCanceledEvent`
  - ❌ `OrderDeletedEvent` (delete es técnico, cancelar es negocio)

### 4.2 Estructura del Evento

```csharp
public record OrderCreatedEvent
{
    // Metadata obligatoria
    public Guid EventId { get; init; } = Guid.NewGuid();
    public string EventType { get; init; } = nameof(OrderCreatedEvent);
    public int Version { get; init; } = 1; // Schema version
    public DateTime OccurredAt { get; init; } = DateTime.UtcNow;
    public Guid CorrelationId { get; init; } // Trace request completo
    public Guid? CausationId { get; init; } // Evento que causó este evento

    // Payload del evento (datos de negocio)
    public Guid OrderId { get; init; }
    public string UserId { get; init; }
    public decimal Total { get; init; }
    public string Country { get; init; }
    public List<OrderLineDto> Lines { get; init; }
}

public record OrderLineDto(string ProductId, int Quantity, decimal Price);
```

**Campos obligatorios:**

- [ ] `EventId`: UUID único del evento
- [ ] `EventType`: Nombre del tipo de evento (para deserialización)
- [ ] `Version`: Schema version (1, 2, 3...)
- [ ] `OccurredAt`: Timestamp UTC
- [ ] `CorrelationId`: Para tracing distribuido
- [ ] Payload: Datos mínimos necesarios (NO enviar entidad completa)

### 4.3 Versionado de Schema

Cuando el schema del evento cambia:

```csharp
// v1
public record OrderCreatedEventV1
{
    public int Version => 1;
    public Guid OrderId { get; init; }
    public string UserId { get; init; }
    public decimal Total { get; init; }
}

// v2: Agregamos campo Country
public record OrderCreatedEventV2
{
    public int Version => 2;
    public Guid OrderId { get; init; }
    public string UserId { get; init; }
    public decimal Total { get; init; }
    public string Country { get; init; } // Nuevo campo
}
```

**Estrategias de migración:**

1. **Weak schema**: Consumidores ignoran campos desconocidos
2. **Upcasting**: Transformar v1 → v2 en consumers
3. **Event versioning**: Publicar ambas versiones temporalmente

### 4.4 Publicación

- [ ] **Outbox pattern** para garantizar consistencia transaccional:
  1. Guardar evento en tabla `outbox` en misma transacción que cambio de BD
  2. Background job publica eventos a Apache Kafka
  3. Marcar evento como publicado
- [ ] **At-least-once delivery**: Eventos pueden duplicarse (idempotencia obligatoria)
- [ ] **Asíncrono**: NO bloquear transacción esperando publicación
- [ ] **Retry con backoff** para fallos de publicación

### 4.5 Consumo

- [ ] **Idempotencia**: Procesar mismo evento múltiples veces = mismo resultado
- [ ] **Deduplicación**: Almacenar `EventId` procesados (cache/BD)
- [ ] **Dead-letter queue (DLQ)**: Eventos que fallan después de N retries
- [ ] **Logging**: Registrar `EventId`, `CorrelationId` para trazabilidad

---

## 5. Configuración Mínima

### 5.1 Outbox Pattern (.NET)

```csharp
// Entity Framework DbContext
public class OrdersDbContext : DbContext
{
    public DbSet<Order> Orders { get; set; }
    public DbSet<OutboxMessage> OutboxMessages { get; set; }
}

public class OutboxMessage
{
    public Guid Id { get; set; }
    public string EventType { get; set; }
    public string Payload { get; set; } // JSON serializado
    public DateTime CreatedAt { get; set; }
    public DateTime? PublishedAt { get; set; }
}

// Service: Guardar evento en outbox
public async Task CreateOrderAsync(CreateOrderRequest request, CancellationToken ct)
{
    using var transaction = await _dbContext.Database.BeginTransactionAsync(ct);

    try
    {
        // 1. Cambio de negocio
        var order = new Order { UserId = request.UserId, Total = request.Total };
        _dbContext.Orders.Add(order);

        // 2. Guardar evento en outbox (misma transacción)
        var @event = new OrderCreatedEvent
        {
            OrderId = order.Id,
            UserId = order.UserId,
            Total = order.Total,
            CorrelationId = _correlationContext.CorrelationId
        };

        _dbContext.OutboxMessages.Add(new OutboxMessage
        {
            Id = @event.EventId,
            EventType = @event.EventType,
            Payload = JsonSerializer.Serialize(@event),
            CreatedAt = DateTime.UtcNow
        });

        await _dbContext.SaveChangesAsync(ct);
        await transaction.CommitAsync(ct);
    }
    catch
    {
        await transaction.RollbackAsync(ct);
        throw;
    }
}

// Background job: Publicar eventos pendientes
public class OutboxPublisherJob : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var pendingMessages = await _dbContext.OutboxMessages
                .Where(m => m.PublishedAt == null)
                .OrderBy(m => m.CreatedAt)
                .Take(100)
                .ToListAsync(ct);

            foreach (var message in pendingMessages)
            {
                try
                {
                    // Publicar a Apache Kafka
                    await _eventBus.PublishAsync(message.EventType, message.Payload, ct);

                    // Marcar como publicado
                    message.PublishedAt = DateTime.UtcNow;
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to publish event {EventId}", message.Id);
                }
            }

            await _dbContext.SaveChangesAsync(ct);
            await Task.Delay(TimeSpan.FromSeconds(5), ct);
        }
    }
}
```

### 5.2 Consumer con Idempotencia (SQS)

```csharp
public class OrderCreatedEventHandler
{
    private readonly IProcessedEventsCache _cache; // Redis o DB

    public async Task HandleAsync(OrderCreatedEvent @event, CancellationToken ct)
    {
        // Deduplicación
        if (await _cache.ExistsAsync(@event.EventId))
        {
            _logger.LogInformation("Event {EventId} already processed, skipping", @event.EventId);
            return;
        }

        try
        {
            // Lógica de negocio
            await _notificationService.SendOrderConfirmationAsync(@event.UserId, @event.OrderId, ct);

            // Marcar como procesado (TTL 7 días)
            await _cache.SetAsync(@event.EventId, DateTime.UtcNow, TimeSpan.FromDays(7));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process event {EventId}", @event.EventId);
            throw; // SQS retry
        }
    }
}
```

### 5.3 AWS SNS/SQS

```yaml
# CloudFormation
OrderCreatedTopic:
  Type: AWS::SNS::Topic
  Properties:
    TopicName: order-created-events

NotificationServiceQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: notification-service-queue
    VisibilityTimeout: 300
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt NotificationServiceDLQ.Arn
      maxReceiveCount: 3 # Después de 3 retries → DLQ

NotificationServiceDLQ:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: notification-service-dlq

NotificationServiceSubscription:
  Type: AWS::SNS::Subscription
  Properties:
    Protocol: sqs
    TopicArn: !Ref OrderCreatedTopic
    Endpoint: !GetAtt NotificationServiceQueue.Arn
```

---

## 6. Prohibiciones

- ❌ Eventos en presente/imperativo (`CreateOrder`, `ProcessPayment`)
- ❌ Eventos sin versionado (schema evoluciona)
- ❌ Payload con entidad completa (enviar solo datos necesarios)
- ❌ Eventos sin `CorrelationId` (imposible tracing)
- ❌ Publicación síncrona bloqueando transacción
- ❌ Consumers NO idempotentes (eventos se duplican)
- ❌ Sin dead-letter queue (eventos perdidos)

---

## 7. Validación

**Checklist de cumplimiento:**

- [ ] Eventos nombrados en pasado (`OrderCreatedEvent`)
- [ ] Metadata obligatoria presente (EventId, Version, OccurredAt, CorrelationId)
- [ ] Outbox pattern implementado (transaccionalidad)
- [ ] Consumers idempotentes (deduplicación por EventId)
- [ ] DLQ configurado para retries fallidos
- [ ] Versionado de schema documentado
- [ ] Logs incluyen CorrelationId para tracing

**Métricas de cumplimiento:**

| Métrica                       | Target           | Verificación       |
| ----------------------------- | ---------------- | ------------------ |
| Eventos publicados            | 100% via outbox  | DB audit           |
| Eventos duplicados procesados | 0 (idempotencia) | Logs analysis      |
| Eventos en DLQ                | <1%              | CloudWatch metrics |
| Schema versioning             | 100% eventos     | Code review        |

---

## 8. Referencias

- [Martin Fowler — Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)
- [DDD — Domain Events](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-events-design-implementation)
- [AWS EventBridge](https://docs.aws.amazon.com/eventbridge/)
- [Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)
- [ADR-012: Mensajería Asíncrona](../../../decisiones-de-arquitectura/adr-012-mensajeria-asincrona.md)
