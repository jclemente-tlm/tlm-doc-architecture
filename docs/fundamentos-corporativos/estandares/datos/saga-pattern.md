---
id: saga-pattern
sidebar_position: 6
title: Saga Pattern
description: Transacciones distribuidas mediante compensación para mantener consistencia eventual
---

# Saga Pattern

## Contexto

Este estándar define **Saga Pattern**: patrón para gestionar **transacciones distribuidas** mediante secuencia de transacciones locales con **compensación** en caso de fallo. Microservicios NO pueden usar transacciones ACID tradicionales que abarcan múltiples bases de datos. Complementa el [lineamiento de Consistencia Eventual](../../lineamientos/datos/02-consistencia-eventual.md) proporcionando mecanismo para **rollback distribuido**.

---

## Concepto Fundamental

```yaml
# ACID Transaction (Monolith) vs Saga (Microservices)

Traditional ACID (Single Database):

  BEGIN TRANSACTION;
    INSERT INTO orders (customer_id, total) VALUES (123, 100);
    UPDATE inventory SET stock = stock - 5 WHERE product_id = 'P001';
    INSERT INTO payments (order_id, amount) VALUES (order_id, 100);
    UPDATE customer_balance SET balance = balance - 100 WHERE customer_id = 123;
  COMMIT;  -- ✅ All or nothing (atomicity)

  Problems in Microservices:
    ❌ Orders DB, Inventory DB, Payments DB are SEPARATE databases
    ❌ Can't use single ACID transaction spanning multiple DBs
    ❌ 2-Phase Commit (2PC) has availability issues

Saga Pattern (Distributed Transaction):

  Scenario: User places order for product P001 (stock: 10, price: $100)

  Services involved:
    - Sales Service (Orders DB)
    - Inventory Service (Inventory DB)
    - Billing Service (Payments DB)

  Saga Steps (Happy Path):

    Step 1: Sales Service
      - Create order (status: PENDING)
      - Publish: OrderCreated event
      - ✅ SUCCESS → Continue to Step 2

    Step 2: Inventory Service (triggered by OrderCreated event)
      - Reserve stock (stock: 10 → 5)
      - Publish: StockReserved event
      - ✅ SUCCESS → Continue to Step 3

    Step 3: Billing Service (triggered by StockReserved event)
      - Charge customer ($100)
      - Publish: PaymentCompleted event
      - ✅ SUCCESS → Continue to Step 4

    Step 4: Sales Service (triggered by PaymentCompleted event)
      - Update order (status: CONFIRMED)
      - ✅ SAGA COMPLETE

  Saga Steps (Failure Scenario):

    Step 1: Sales Service
      - Create order (status: PENDING)
      - Publish: OrderCreated event
      - ✅ SUCCESS

    Step 2: Inventory Service
      - Reserve stock
      - ✅ SUCCESS

    Step 3: Billing Service
      - Charge customer → ❌ FAILS (insufficient funds)
      - Publish: PaymentFailed event
      - ❌ COMPENSATION TRIGGERED

    Compensation Step 2': Inventory Service (rollback)
      - Release reserved stock (stock: 5 → 10)
      - Publish: StockReleased event
      - ✅ COMPENSATED

    Compensation Step 1': Sales Service (rollback)
      - Update order (status: CANCELLED)
      - Publish: OrderCancelled event
      - ✅ SAGA ABORTED

  Result: System returns to consistent state (order cancelled, stock restored)
```

## Saga Types

```yaml
# Two Saga Orchestration Patterns

1. Choreography (Event-Driven):

   - Services communicate via events (Kafka)
   - No central coordinator
   - Each service knows next step

   Pros:
     ✅ Loose coupling (services independent)
     ✅ No single point of failure
     ✅ Scalable (add services easily)

   Cons:
     ❌ Hard to track saga state (distributed)
     ❌ Cyclic dependencies risk (A→B→C→A)
     ❌ Complex debugging (trace across services)

2. Orchestration (Centralized):

   - Central orchestrator coordinates saga
   - Orchestrator tells services what to do
   - Services only respond to orchestrator

   Pros:
     ✅ Easy to track state (in orchestrator DB)
     ✅ Clear flow visualization
     ✅ Simple rollback logic (orchestrator decides)

   Cons:
     ❌ Orchestrator is single point of failure
     ❌ Orchestrator couples services (knows all)
     ❌ Orchestrator can become bottleneck

Recommendation: Choreography for simple sagas (2-3 steps), Orchestration for complex (4+ steps)
```

## Implementation: Choreography

```csharp
// ✅ Saga Choreography (Event-Driven)

// Step 1: Sales Service - Create Order

public class OrderService : IOrderService
{
    private readonly IOrderRepository _orderRepo;
    private readonly IEventPublisher _eventPublisher;

    public async Task<Guid> CreateOrderAsync(CreateOrderCommand cmd)
    {
        // ✅ Step 1: Local transaction (create order)
        var order = new Order
        {
            OrderId = Guid.NewGuid(),
            CustomerId = cmd.CustomerId,
            Items = cmd.Items,
            Total = cmd.Items.Sum(i => i.Price * i.Quantity),
            Status = OrderStatus.PENDING,  // ✅ Not CONFIRMED yet
            CreatedAt = DateTime.UtcNow
        };

        await _orderRepo.SaveAsync(order);

        // ✅ Publish event (trigger next step)
        await _eventPublisher.PublishAsync(new OrderCreatedEvent
        {
            OrderId = order.OrderId,
            CustomerId = order.CustomerId,
            Items = order.Items.Select(i => new OrderItemEvent
            {
                ProductId = i.ProductId,
                Quantity = i.Quantity,
                Price = i.Price
            }).ToList(),
            Total = order.Total
        });

        return order.OrderId;
    }
}

// Step 2: Inventory Service - Reserve Stock

public class StockReservationHandler : IEventHandler<OrderCreatedEvent>
{
    private readonly IInventoryRepository _inventoryRepo;
    private readonly IEventPublisher _eventPublisher;

    public async Task HandleAsync(OrderCreatedEvent @event)
    {
        try
        {
            // ✅ Step 2: Local transaction (reserve stock)
            foreach (var item in @event.Items)
            {
                var product = await _inventoryRepo.GetByIdAsync(item.ProductId);

                if (product.Stock < item.Quantity)
                {
                    // ❌ Insufficient stock → COMPENSATION
                    await _eventPublisher.PublishAsync(new StockReservationFailedEvent
                    {
                        OrderId = @event.OrderId,
                        ProductId = item.ProductId,
                        Reason = "Insufficient stock",
                        RequestedQuantity = item.Quantity,
                        AvailableStock = product.Stock
                    });
                    return;
                }

                product.ReserveStock(item.Quantity);
            }

            await _inventoryRepo.SaveAsync();

            // ✅ Publish success event (trigger next step)
            await _eventPublisher.PublishAsync(new StockReservedEvent
            {
                OrderId = @event.OrderId,
                Items = @event.Items
            });
        }
        catch (Exception ex)
        {
            // ❌ Error → COMPENSATION
            await _eventPublisher.PublishAsync(new StockReservationFailedEvent
            {
                OrderId = @event.OrderId,
                Reason = ex.Message
            });
        }
    }
}

// Step 3: Billing Service - Process Payment

public class PaymentHandler : IEventHandler<StockReservedEvent>
{
    private readonly IPaymentService _paymentService;
    private readonly IEventPublisher _eventPublisher;

    public async Task HandleAsync(StockReservedEvent @event)
    {
        try
        {
            // ✅ Step 3: Charge customer
            var payment = await _paymentService.ChargeAsync(new ChargeRequest
            {
                OrderId = @event.OrderId,
                Amount = @event.Items.Sum(i => i.Price * i.Quantity)
            });

            // ✅ Publish success (saga complete)
            await _eventPublisher.PublishAsync(new PaymentCompletedEvent
            {
                OrderId = @event.OrderId,
                PaymentId = payment.PaymentId,
                Amount = payment.Amount
            });
        }
        catch (Exception ex)
        {
            // ❌ Payment failed → COMPENSATION
            await _eventPublisher.PublishAsync(new PaymentFailedEvent
            {
                OrderId = @event.OrderId,
                Reason = ex.Message
            });
        }
    }
}

// Step 4: Sales Service - Confirm Order (Final Step)

public class OrderConfirmationHandler : IEventHandler<PaymentCompletedEvent>
{
    private readonly IOrderRepository _orderRepo;

    public async Task HandleAsync(PaymentCompletedEvent @event)
    {
        var order = await _orderRepo.GetByIdAsync(@event.OrderId);

        // ✅ Update order status (saga complete)
        order.Status = OrderStatus.CONFIRMED;
        order.ConfirmedAt = DateTime.UtcNow;

        await _orderRepo.SaveAsync(order);

        // ✅ Optionally publish OrderConfirmed event
        await _eventPublisher.PublishAsync(new OrderConfirmedEvent
        {
            OrderId = @event.OrderId
        });
    }
}

// COMPENSATION: Inventory Service - Release Stock

public class StockReleaseHandler : IEventHandler<PaymentFailedEvent>
{
    private readonly IInventoryRepository _inventoryRepo;
    private readonly IEventPublisher _eventPublisher;

    public async Task HandleAsync(PaymentFailedEvent @event)
    {
        // ✅ Compensate: Release reserved stock
        var items = await _inventoryRepo.GetReservedItemsAsync(@event.OrderId);

        foreach (var item in items)
        {
            item.ReleaseStock();
        }

        await _inventoryRepo.SaveAsync();

        // ✅ Publish compensation event
        await _eventPublisher.PublishAsync(new StockReleasedEvent
        {
            OrderId = @event.OrderId
        });
    }
}

// COMPENSATION: Sales Service - Cancel Order

public class OrderCancellationHandler : IEventHandler<PaymentFailedEvent>
{
    private readonly IOrderRepository _orderRepo;

    public async Task HandleAsync(PaymentFailedEvent @event)
    {
        var order = await _orderRepo.GetByIdAsync(@event.OrderId);

        // ✅ Compensate: Cancel order
        order.Status = OrderStatus.CANCELLED;
        order.CancellationReason = @event.Reason;
        order.CancelledAt = DateTime.UtcNow;

        await _orderRepo.SaveAsync(order);
    }
}
```

## Implementation: Orchestration

```csharp
// ✅ Saga Orchestration (Centralized Coordinator)

// Orchestrator State Machine

public class OrderSagaOrchestrator
{
    private readonly IEventPublisher _eventPublisher;
    private readonly ISagaStateRepository _sagaRepo;

    public async Task StartAsync(CreateOrderCommand cmd)
    {
        // ✅ Create saga state
        var saga = new SagaState
        {
            SagaId = Guid.NewGuid(),
            OrderId = Guid.NewGuid(),
            CustomerId = cmd.CustomerId,
            Items = cmd.Items,
            CurrentStep = SagaStep.CreateOrder,
            Status = SagaStatus.InProgress,
            StartedAt = DateTime.UtcNow
        };

        await _sagaRepo.SaveAsync(saga);

        // ✅ Execute Step 1
        await ExecuteStepAsync(saga);
    }

    private async Task ExecuteStepAsync(SagaState saga)
    {
        switch (saga.CurrentStep)
        {
            case SagaStep.CreateOrder:
                await _eventPublisher.PublishAsync(new CreateOrderCommand
                {
                    SagaId = saga.SagaId,
                    OrderId = saga.OrderId,
                    CustomerId = saga.CustomerId,
                    Items = saga.Items
                });
                break;

            case SagaStep.ReserveStock:
                await _eventPublisher.PublishAsync(new ReserveStockCommand
                {
                    SagaId = saga.SagaId,
                    OrderId = saga.OrderId,
                    Items = saga.Items
                });
                break;

            case SagaStep.ProcessPayment:
                await _eventPublisher.PublishAsync(new ProcessPaymentCommand
                {
                    SagaId = saga.SagaId,
                    OrderId = saga.OrderId,
                    Amount = saga.Items.Sum(i => i.Price * i.Quantity)
                });
                break;

            case SagaStep.ConfirmOrder:
                await _eventPublisher.PublishAsync(new ConfirmOrderCommand
                {
                    SagaId = saga.SagaId,
                    OrderId = saga.OrderId
                });
                saga.Status = SagaStatus.Completed;
                await _sagaRepo.SaveAsync(saga);
                break;
        }
    }

    // ✅ Handle service responses
    public async Task HandleStepCompletedAsync(StepCompletedEvent @event)
    {
        var saga = await _sagaRepo.GetBySagaIdAsync(@event.SagaId);

        if (saga == null || saga.Status != SagaStatus.InProgress)
            return;

        // ✅ Move to next step
        saga.CurrentStep = GetNextStep(saga.CurrentStep);
        await _sagaRepo.SaveAsync(saga);

        await ExecuteStepAsync(saga);
    }

    // ✅ Handle failures (trigger compensation)
    public async Task HandleStepFailedAsync(StepFailedEvent @event)
    {
        var saga = await _sagaRepo.GetBySagaIdAsync(@event.SagaId);

        if (saga == null)
            return;

        // ✅ Start compensation
        saga.Status = SagaStatus.Compensating;
        saga.FailureReason = @event.Reason;
        await _sagaRepo.SaveAsync(saga);

        await CompensateAsync(saga);
    }

    private async Task CompensateAsync(SagaState saga)
    {
        // ✅ Rollback in reverse order
        var completedSteps = GetCompletedSteps(saga);

        foreach (var step in completedSteps.Reverse())
        {
            switch (step)
            {
                case SagaStep.CreateOrder:
                    await _eventPublisher.PublishAsync(new CancelOrderCommand
                    {
                        SagaId = saga.SagaId,
                        OrderId = saga.OrderId
                    });
                    break;

                case SagaStep.ReserveStock:
                    await _eventPublisher.PublishAsync(new ReleaseStockCommand
                    {
                        SagaId = saga.SagaId,
                        OrderId = saga.OrderId
                    });
                    break;

                case SagaStep.ProcessPayment:
                    await _eventPublisher.PublishAsync(new RefundPaymentCommand
                    {
                        SagaId = saga.SagaId,
                        OrderId = saga.OrderId
                    });
                    break;
            }
        }

        saga.Status = SagaStatus.Compensated;
        saga.CompensatedAt = DateTime.UtcNow;
        await _sagaRepo.SaveAsync(saga);
    }
}

// Saga State (Database)

public class SagaState
{
    public Guid SagaId { get; set; }
    public Guid OrderId { get; set; }
    public Guid CustomerId { get; set; }
    public List<OrderItem> Items { get; set; }
    public SagaStep CurrentStep { get; set; }
    public SagaStatus Status { get; set; }
    public string FailureReason { get; set; }
    public DateTime StartedAt { get; set; }
    public DateTime? CompensatedAt { get; set; }
}

public enum SagaStep
{
    CreateOrder = 1,
    ReserveStock = 2,
    ProcessPayment = 3,
    ConfirmOrder = 4
}

public enum SagaStatus
{
    InProgress,
    Completed,
    Compensating,
    Compensated,
    Failed
}
```

## Idempotency

```csharp
// ✅ Idempotent Event Handlers (Critical for Sagas)

public class IdempotentStockReservationHandler : IEventHandler<OrderCreatedEvent>
{
    private readonly IInventoryRepository _inventoryRepo;
    private readonly IEventPublisher _eventPublisher;
    private readonly IIdempotencyService _idempotency;

    public async Task HandleAsync(OrderCreatedEvent @event)
    {
        // ✅ Check if already processed (duplicate event)
        var idempotencyKey = $"stock-reservation-{@event.OrderId}";

        if (await _idempotency.HasProcessedAsync(idempotencyKey))
        {
            // ✅ Already processed, skip (idempotent)
            return;
        }

        try
        {
            // Process reservation...

            // ✅ Mark as processed
            await _idempotency.MarkProcessedAsync(idempotencyKey);
        }
        catch (Exception ex)
        {
            // ❌ Failed, do NOT mark as processed (allow retry)
            throw;
        }
    }
}

// Idempotency Service (Redis)

public class IdempotencyService : IIdempotencyService
{
    private readonly IConnectionMultiplexer _redis;

    public async Task<bool> HasProcessedAsync(string key)
    {
        var db = _redis.GetDatabase();
        return await db.KeyExistsAsync($"idempotency:{key}");
    }

    public async Task MarkProcessedAsync(string key)
    {
        var db = _redis.GetDatabase();
        await db.StringSetAsync($"idempotency:{key}", "processed", TimeSpan.FromDays(7));
    }
}
```

## Monitoring

```yaml
# ✅ Saga Monitoring & Alerting

Metrics:

  Saga Duration:
    - Metric: saga_duration_seconds
    - Labels: saga_name, status (completed/compensated/failed)
    - Alert: > 30 seconds (investigate slow saga)

  Saga Success Rate:
    - Metric: saga_completion_rate
    - Target: > 95% (compensations < 5%)
    - Alert: < 90% (too many failures)

  Compensation Count:
    - Metric: saga_compensations_total
    - Alert: Spike (investigate root cause)

Distributed Tracing (X-Ray):

  Trace Saga across services:
    1. Sales Service: CreateOrder (100ms)
    2. Inventory Service: ReserveStock (150ms)
    3. Billing Service: ProcessPayment (500ms)
    4. Sales Service: ConfirmOrder (50ms)

    Total: 800ms

  Identify bottlenecks:
    - Billing Service taking 500ms (payment gateway slow)

Saga State Dashboard (Grafana):

  Panels:
    - Active Sagas (InProgress count)
    - Completed Sagas (last 1h)
    - Compensated Sagas (failures)
    - Average Duration per Saga Type
    - Compensation Rate Trend

Alerts:

  - Saga stuck > 5 minutes (timeout)
  - Compensation rate > 10% (investigate)
  - Specific saga failed > 3 times (manual intervention)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar compensación para cada paso del saga
- **MUST** garantizar idempotency en event handlers
- **MUST** persistir estado del saga (recovery from failures)
- **MUST** usar event ordering (Kafka partitions por OrderId)
- **MUST** timeout sagas stalled > 5 min
- **MUST** log cada paso del saga (distributed tracing)

### SHOULD (Fuertemente recomendado)

- **SHOULD** elegir choreography para sagas simples (2-3 steps)
- **SHOULD** elegir orchestration para sagas complejos (4+ steps)
- **SHOULD** monitorear compensation rate (< 5% target)
- **SHOULD** implementar circuit breaker (avoid cascading failures)

### MUST NOT (Prohibido)

- **MUST NOT** usar ACID transactions cross-services
- **MUST NOT** omit compensation logic (leaves inconsistent state)
- **MUST NOT** process duplicate events (must be idempotent)
- **MUST NOT** allow sagas without timeout (infinite retries)

---

## Referencias

- [Lineamiento: Consistencia Eventual](../../lineamientos/datos/02-consistencia-eventual.md)
- [Transactional Outbox](../../guias-arquitectura/transactional-outbox.md)
- [Event-Driven Architecture](../arquitectura/event-driven-architecture.md)
- [Compensating Transactions](./compensating-transactions.md)
- [Idempotency](../desarrollo/idempotency.md)
