---
id: saga-pattern
sidebar_position: 6
title: Patrón Saga para Transacciones Distribuidas
description: Estándar para implementación de Sagas con MassTransit usando orchestration-based pattern para transacciones distribuidas con compensating actions
---

# Estándar Técnico — Patrón Saga para Transacciones Distribuidas

---

## 1. Propósito

Garantizar consistencia eventual en transacciones distribuidas mediante Saga Pattern con compensating transactions, state management y orquestación de flujos multi-servicio.

---

## 2. Alcance

**Aplica a:**

- Transacciones multi-servicio (Order → Payment → Inventory → Shipping)
- Workflows de negocio complejos
- Procesos de larga duración (long-running)
- Operaciones que requieren consistencia eventual
- Compensating transactions por fallos

**No aplica a:**

- Transacciones dentro de un mismo bounded context
- Operaciones ACID simples en una DB
- Queries read-only
- Eventos fire-and-forget sin compensación

---

## 3. Tecnologías Aprobadas

| Componente              | Tecnología       | Versión mínima | Observaciones          |
| ----------------------- | ---------------- | -------------- | ---------------------- |
| **Saga Framework**      | MassTransit      | 8.0+           | State machine sagas    |
| **Message Broker**      | Apache Kafka     | 3.6+           | Event sourcing         |
| **State Storage**       | PostgreSQL       | 14+            | Saga state persistence |
| **Alternative Storage** | Redis            | 7.0+           | Lightweight sagas      |
| **Serialization**       | System.Text.Json | .NET 8+        | Event serialization    |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Diseño de Saga

- [ ] **Orchestration-based:** preferir sobre choreography para flujos complejos
- [ ] **Idempotencia:** todos los handlers deben ser idempotentes
- [ ] **Compensating actions:** definir rollback para cada step
- [ ] **Timeout:** timeout por step y global
- [ ] **State persistence:** estado de saga en DB

### State Machine

- [ ] Estados claramente definidos (Pending, Processing, Completed, Failed, Compensating)
- [ ] Transiciones válidas documentadas
- [ ] Events que disparan transiciones
- [ ] Correlation ID para trackear saga instance

### Compensating Transactions

- [ ] Compensación definida para cada operación no-idempotente
- [ ] Orden inverso de compensación (LIFO)
- [ ] Log de acciones compensadas
- [ ] Partial rollback posible

### Telemetría

- [ ] Log de inicio/fin de saga
- [ ] Métricas de duración de saga
- [ ] Alertas para sagas stuck (>timeout)
- [ ] Dashboard de sagas en proceso
- [ ] Distributed tracing con correlation ID

### Error Handling

- [ ] Retry transient errors antes de compensar
- [ ] Dead letter queue para mensajes fallidos
- [ ] Manual intervention para errores irrecuperables
- [ ] Alertas para sagas en estado Failed

---

## 5. Prohibiciones

- ❌ 2PC (Two-Phase Commit) distribuido
- ❌ Transacciones distribuidas con locks
- ❌ Saga sin compensating actions
- ❌ State management in-memory (debe persistirse)
- ❌ Choreography para flujos con >5 pasos
- ❌ Sagas sin timeout
- ❌ Handlers no-idempotentes

---

## 6. Configuración Mínima

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// MassTransit con Saga State Machine
builder.Services.AddMassTransit(x =>
{
    // Registrar saga state machine
    x.AddSagaStateMachine<OrderSaga, OrderSagaState>()
        .EntityFrameworkRepository(r =>
        {
            r.ConcurrencyMode = ConcurrencyMode.Pessimistic;
            r.AddDbContext<DbContext, SagaDbContext>((provider, cfg) =>
            {
                cfg.UseNpgsql(builder.Configuration.GetConnectionString("Sagas"));
            });
        });

    // Configurar con Kafka
    x.UsingInMemory((context, cfg) =>
    {
        cfg.ConfigureEndpoints(context);
    });
    // Nota: Para producción configurar con Kafka transport
    // Ver documentación: https://masstransit.io/documentation/transports/kafka
});

var app = builder.Build();
app.Run();
```

```csharp
// OrderSagaState.cs - Estado de la saga
public class OrderSagaState : SagaStateMachineInstance
{
    public Guid CorrelationId { get; set; }
    public string CurrentState { get; set; }

    // Datos del pedido
    public Guid OrderId { get; set; }
    public decimal TotalAmount { get; set; }
    public Guid CustomerId { get; set; }

    // IDs de transacciones para compensación
    public Guid? PaymentId { get; set; }
    public Guid? InventoryReservationId { get; set; }
    public Guid? ShippingId { get; set; }

    // Timestamps
    public DateTime CreatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }

    // Retry
    public int RetryCount { get; set; }
}
```

---

## 7. Ejemplos

### Saga State Machine completa

```csharp
public class OrderSaga : MassTransitStateMachine<OrderSagaState>
{
    public OrderSaga()
    {
        InstanceState(x => x.CurrentState);

        // Estados
        State(() => Submitted);
        State(() => PaymentProcessing);
        State(() => InventoryReserving);
        State(() => ShippingScheduling);
        State(() => Completed);
        State(() => Compensating);
        State(() => Failed);

        // Eventos
        Event(() => OrderSubmitted, x => x.CorrelateById(m => m.Message.OrderId));
        Event(() => PaymentCompleted, x => x.CorrelateById(m => m.Message.OrderId));
        Event(() => PaymentFailed, x => x.CorrelateById(m => m.Message.OrderId));
        Event(() => InventoryReserved, x => x.CorrelateById(m => m.Message.OrderId));
        Event(() => InventoryReserveFailed, x => x.CorrelateById(m => m.Message.OrderId));
        Event(() => ShippingScheduled, x => x.CorrelateById(m => m.Message.OrderId));
        Event(() => ShippingFailed, x => x.CorrelateById(m => m.Message.OrderId));

        // Flujo principal
        Initially(
            When(OrderSubmitted)
                .Then(context =>
                {
                    context.Saga.OrderId = context.Message.OrderId;
                    context.Saga.TotalAmount = context.Message.TotalAmount;
                    context.Saga.CustomerId = context.Message.CustomerId;
                    context.Saga.CreatedAt = DateTime.UtcNow;
                })
                .ThenAsync(context => Console.Out.WriteLineAsync(
                    $"Saga {context.Saga.CorrelationId}: Order submitted"))
                .TransitionTo(PaymentProcessing)
                .PublishAsync(context => context.Init<ProcessPayment>(new
                {
                    OrderId = context.Saga.OrderId,
                    Amount = context.Saga.TotalAmount,
                    CustomerId = context.Saga.CustomerId
                }))
        );

        During(PaymentProcessing,
            // Payment successful
            When(PaymentCompleted)
                .Then(context => context.Saga.PaymentId = context.Message.PaymentId)
                .ThenAsync(context => Console.Out.WriteLineAsync(
                    $"Saga {context.Saga.CorrelationId}: Payment completed"))
                .TransitionTo(InventoryReserving)
                .PublishAsync(context => context.Init<ReserveInventory>(new
                {
                    OrderId = context.Saga.OrderId,
                    Items = context.Message.Items
                })),

            // Payment failed - compensate
            When(PaymentFailed)
                .ThenAsync(context => Console.Out.WriteLineAsync(
                    $"Saga {context.Saga.CorrelationId}: Payment failed. Canceling order."))
                .TransitionTo(Failed)
                .PublishAsync(context => context.Init<CancelOrder>(new
                {
                    OrderId = context.Saga.OrderId,
                    Reason = "Payment failed"
                }))
        );

        During(InventoryReserving,
            // Inventory reserved
            When(InventoryReserved)
                .Then(context => context.Saga.InventoryReservationId = context.Message.ReservationId)
                .ThenAsync(context => Console.Out.WriteLineAsync(
                    $"Saga {context.Saga.CorrelationId}: Inventory reserved"))
                .TransitionTo(ShippingScheduling)
                .PublishAsync(context => context.Init<ScheduleShipping>(new
                {
                    OrderId = context.Saga.OrderId,
                    CustomerId = context.Saga.CustomerId
                })),

            // Inventory failed - compensate payment
            When(InventoryReserveFailed)
                .ThenAsync(context => Console.Out.WriteLineAsync(
                    $"Saga {context.Saga.CorrelationId}: Inventory reserve failed. Compensating..."))
                .TransitionTo(Compensating)
                .PublishAsync(context => context.Init<RefundPayment>(new
                {
                    PaymentId = context.Saga.PaymentId!.Value,
                    Reason = "Inventory unavailable"
                }))
        );

        During(ShippingScheduling,
            // Shipping scheduled - saga complete
            When(ShippingScheduled)
                .Then(context =>
                {
                    context.Saga.ShippingId = context.Message.ShippingId;
                    context.Saga.CompletedAt = DateTime.UtcNow;
                })
                .ThenAsync(context => Console.Out.WriteLineAsync(
                    $"Saga {context.Saga.CorrelationId}: Order completed successfully!"))
                .TransitionTo(Completed)
                .Finalize(),

            // Shipping failed - compensate inventory and payment
            When(ShippingFailed)
                .ThenAsync(context => Console.Out.WriteLineAsync(
                    $"Saga {context.Saga.CorrelationId}: Shipping failed. Compensating..."))
                .TransitionTo(Compensating)
                .PublishAsync(context => context.Init<ReleaseInventory>(new
                {
                    ReservationId = context.Saga.InventoryReservationId!.Value
                }))
                .PublishAsync(context => context.Init<RefundPayment>(new
                {
                    PaymentId = context.Saga.PaymentId!.Value,
                    Reason = "Shipping unavailable"
                }))
        );

        SetCompletedWhenFinalized();
    }

    // Estados
    public State Submitted { get; private set; }
    public State PaymentProcessing { get; private set; }
    public State InventoryReserving { get; private set; }
    public State ShippingScheduling { get; private set; }
    public State Completed { get; private set; }
    public State Compensating { get; private set; }
    public State Failed { get; private set; }

    // Eventos
    public Event<OrderSubmittedEvent> OrderSubmitted { get; private set; }
    public Event<PaymentCompletedEvent> PaymentCompleted { get; private set; }
    public Event<PaymentFailedEvent> PaymentFailed { get; private set; }
    public Event<InventoryReservedEvent> InventoryReserved { get; private set; }
    public Event<InventoryReserveFailedEvent> InventoryReserveFailed { get; private set; }
    public Event<ShippingScheduledEvent> ShippingScheduled { get; private set; }
    public Event<ShippingFailedEvent> ShippingFailed { get; private set; }
}
```

### Consumers idempotentes

```csharp
public class ProcessPaymentConsumer : IConsumer<ProcessPayment>
{
    private readonly IPaymentService _paymentService;
    private readonly IPublishEndpoint _publishEndpoint;

    public async Task Consume(ConsumeContext<ProcessPayment> context)
    {
        var orderId = context.Message.OrderId;

        // Idempotencia: verificar si ya procesado
        var existing = await _paymentService.GetByOrderIdAsync(orderId);
        if (existing != null)
        {
            // Ya procesado - publicar evento completado
            await _publishEndpoint.Publish(new PaymentCompletedEvent
            {
                OrderId = orderId,
                PaymentId = existing.Id,
                Items = Array.Empty<OrderItem>() // Desde DB
            });
            return;
        }

        try
        {
            var payment = await _paymentService.ProcessAsync(
                orderId,
                context.Message.Amount,
                context.Message.CustomerId);

            await _publishEndpoint.Publish(new PaymentCompletedEvent
            {
                OrderId = orderId,
                PaymentId = payment.Id,
                Items = context.Message.Items
            });
        }
        catch (PaymentException ex)
        {
            await _publishEndpoint.Publish(new PaymentFailedEvent
            {
                OrderId = orderId,
                Reason = ex.Message
            });
        }
    }
}
```

### Monitoring de sagas

```csharp
public class SagaMonitoringService : BackgroundService
{
    private readonly ISagaRepository<OrderSagaState> _repository;
    private readonly ILogger<SagaMonitoringService> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            // Buscar sagas stuck (>15 minutos en proceso)
            var stuckSagas = await _repository
                .Where(s => s.CurrentState != nameof(OrderSaga.Completed) &&
                           s.CurrentState != nameof(OrderSaga.Failed) &&
                           s.CreatedAt < DateTime.UtcNow.AddMinutes(-15))
                .ToListAsync(stoppingToken);

            foreach (var saga in stuckSagas)
            {
                _logger.LogWarning(
                    "Saga {CorrelationId} stuck in state {State} for {Duration} minutes",
                    saga.CorrelationId,
                    saga.CurrentState,
                    (DateTime.UtcNow - saga.CreatedAt).TotalMinutes);

                // Alertar para intervención manual
            }

            await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
        }
    }
}
```

---

## 8. Validación y Auditoría

```bash
# Verificar sagas en proceso
psql -h localhost -U postgres -d sagas -c "
  SELECT correlation_id, current_state, created_at,
         NOW() - created_at as duration
  FROM order_saga_state
  WHERE current_state NOT IN ('Completed', 'Failed')
  ORDER BY created_at DESC;
"

# Métricas de sagas
curl http://localhost:5000/metrics | grep saga
```

**Métricas de cumplimiento:**

| Métrica                        | Umbral     | Verificación |
| ------------------------------ | ---------- | ------------ |
| Sagas con compensating actions | 100%       | Code review  |
| Handlers idempotentes          | 100%       | Unit tests   |
| Saga completion rate           | >95%       | Metrics      |
| Average saga duration          | <5 minutos | Metrics      |
| Stuck sagas                    | <1%        | Monitoring   |

**Checklist de auditoría:**

- [ ] State machine definido con todos los estados
- [ ] Compensating actions para cada step
- [ ] Handlers idempotentes
- [ ] State persistence en DB
- [ ] Timeouts configurados
- [ ] Monitoring de sagas stuck
- [ ] Distributed tracing

---

## 9. Referencias

- [MassTransit Sagas](https://masstransit.io/documentation/patterns/saga)
- [Microservices Patterns - Chris Richardson](https://microservices.io/patterns/data/saga.html)
- [Martin Fowler - Saga](https://martinfowler.com/articles/201701-event-driven.html)
- [AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-standard-vs-express.html)
- [Temporal Workflows](https://temporal.io/)
- [Distributed Sagas - Caitie McCaffrey](https://www.youtube.com/watch?v=0UTOLRTwOX0)
