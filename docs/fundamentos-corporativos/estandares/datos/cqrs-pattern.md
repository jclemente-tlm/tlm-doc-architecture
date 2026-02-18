---
id: cqrs-pattern
sidebar_position: 2
title: CQRS Pattern
description: Command Query Responsibility Segregation - separación de lectura y escritura para escalabilidad
---

# CQRS Pattern

## Contexto

Este estándar define **CQRS (Command Query Responsibility Segregation)**: separación de **modelos de lectura y escritura**. Queries (lecturas) usan modelo optimizado para consultas. Commands (escrituras) usan modelo optimizado para transacciones. Permite escalar read y write independientemente. Complementa [Event Sourcing](./event-sourcing.md) y [Consistency Models](./consistency-models.md).

---

## Concepto Fundamental

```yaml
# ✅ CQRS Pattern

Traditional Architecture (Same Model):

  Client → API → Single Model → Database

  - Read: SELECT * FROM orders WHERE customer_id = ?
  - Write: INSERT INTO orders (...) VALUES (...)

  Problems:
    - Read model optimized for normalization (3NF)
    - Write queries complex (joins, aggregations slow)
    - Can't scale read and write independently
    - ORM impedance mismatch (complex queries)

CQRS Architecture (Separate Models):

  Client → API → [Write Model] → Write Database (PostgreSQL)
                       ↓
                   Events (Kafka)
                       ↓
                 [Read Model] → Read Database (ElasticSearch)
                       ↑
  Client → API ────────┘

  - Writes: Use normalized PostgreSQL (ACID transactions)
  - Reads: Use denormalized ElasticSearch (fast queries)
  - Eventual consistency (read model synced via events)

Benefits:
  ✅ Independent Scaling: Scale reads (add replicas) without affecting writes
  ✅ Optimized Models: Write normalized, read denormalized
  ✅ Performance: Reads fast (no joins), writes transactional (ACID)
  ✅ Separation: Different teams can work on read/write independently

Trade-offs:
  ⚠️ Complexity: Two models instead of one
  ⚠️ Eventual Consistency: Read model lags behind write model
  ⚠️ Data Duplication: Same data in multiple stores
```

## Write Model (Commands)

```yaml
# ✅ Write Model (Transactional, Normalized)

Domain Model:

  public class Order
  {
      public Guid Id { get; private set; }
      public Guid CustomerId { get; private set; }
      public OrderStatus Status { get; private set; }
      public DateTime CreatedAt { get; private set; }

      private List<OrderLine> _lines = new();
      public IReadOnlyList<OrderLine> Lines => _lines.AsReadOnly();

      // ✅ Domain methods (business logic)
      public void AddLine(Guid productId, int quantity, decimal price)
      {
          if (Status != OrderStatus.Draft)
              throw new InvalidOperationException("Cannot modify submitted order");

          _lines.Add(new OrderLine
          {
              Id = Guid.NewGuid(),
              ProductId = productId,
              Quantity = quantity,
              UnitPrice = price
          });
      }

      public void Submit()
      {
          if (!_lines.Any())
              throw new InvalidOperationException("Order must have at least one line");

          Status = OrderStatus.Submitted;
      }

      public decimal GetTotal() => _lines.Sum(l => l.Quantity * l.UnitPrice);
  }

  public class OrderLine
  {
      public Guid Id { get; set; }
      public Guid ProductId { get; set; }
      public int Quantity { get; set; }
      public decimal UnitPrice { get; set; }
  }

Command (Write Operation):

  public record CreateOrderCommand(
      Guid CustomerId,
      List<OrderLineDto> Lines
  ) : IRequest<Guid>;

  public class CreateOrderCommandHandler : IRequestHandler<CreateOrderCommand, Guid>
  {
      private readonly IOrderRepository _repository;
      private readonly IEventPublisher _eventPublisher;

      public async Task<Guid> Handle(CreateOrderCommand command, CancellationToken ct)
      {
          // ✅ Create domain entity
          var order = new Order();
          order.Create(command.CustomerId);

          foreach (var line in command.Lines)
          {
              order.AddLine(line.ProductId, line.Quantity, line.UnitPrice);
          }

          order.Submit();

          // ✅ Persist to write database
          await _repository.SaveAsync(order);

          // ✅ Publish event
          await _eventPublisher.PublishAsync(new OrderCreatedEvent
          {
              OrderId = order.Id,
              CustomerId = order.CustomerId,
              Total = order.GetTotal(),
              Lines = order.Lines.Select(l => new OrderLineDto
              {
                  ProductId = l.ProductId,
                  Quantity = l.Quantity,
                  UnitPrice = l.UnitPrice
              }).ToList(),
              CreatedAt = order.CreatedAt
          });

          return order.Id;
      }
  }

Database Schema (Normalized):

  -- ✅ Write Model (PostgreSQL)

  CREATE TABLE orders (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
  );

  CREATE TABLE order_lines (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id),
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
  );

  CREATE INDEX idx_orders_customer ON orders(customer_id);
  CREATE INDEX idx_lines_order ON order_lines(order_id);
```

## Read Model (Queries)

```yaml
# ✅ Read Model (Denormalized, Optimized for Queries)

Read Model Document:

  public class OrderReadModel
  {
      public Guid OrderId { get; set; }
      public Guid CustomerId { get; set; }
      public string CustomerName { get; set; }
      public string CustomerEmail { get; set; }
      public string Status { get; set; }
      public decimal Total { get; set; }
      public DateTime CreatedAt { get; set; }

      // ✅ Denormalized (no joins needed)
      public List<OrderLineReadModel> Lines { get; set; }
  }

  public class OrderLineReadModel
  {
      public Guid ProductId { get; set; }
      public string ProductName { get; set; }  // ✅ Denormalized from Product
      public string ProductImage { get; set; }  // ✅ Denormalized
      public int Quantity { get; set; }
      public decimal UnitPrice { get; set; }
      public decimal Subtotal { get; set; }
  }

Query (Read Operation):

  public record GetOrdersByCustomerQuery(
      Guid CustomerId,
      int Page,
      int PageSize
  ) : IRequest<List<OrderReadModel>>;

  public class GetOrdersByCustomerQueryHandler : IRequestHandler<GetOrdersByCustomerQuery, List<OrderReadModel>>
  {
      private readonly IElasticClient _elasticClient;

      public async Task<List<OrderReadModel>> Handle(GetOrdersByCustomerQuery query, CancellationToken ct)
      {
          // ✅ Query read database (ElasticSearch)
          var response = await _elasticClient.SearchAsync<OrderReadModel>(s => s
              .Index("orders")
              .From((query.Page - 1) * query.PageSize)
              .Size(query.PageSize)
              .Query(q => q
                  .Term(t => t.Field(f => f.CustomerId).Value(query.CustomerId))
              )
              .Sort(sort => sort
                  .Descending(f => f.CreatedAt)
              )
          );

          return response.Documents.ToList();
      }
  }

Query with Full-Text Search:

  public record SearchOrdersQuery(
      string SearchTerm,
      int Page,
      int PageSize
  ) : IRequest<List<OrderReadModel>>;

  public class SearchOrdersQueryHandler : IRequestHandler<SearchOrdersQuery, List<OrderReadModel>>
  {
      private readonly IElasticClient _elasticClient;

      public async Task<List<OrderReadModel>> Handle(SearchOrdersQuery query, CancellationToken ct)
      {
          // ✅ Full-text search (not possible on normalized DB without performance hit)
          var response = await _elasticClient.SearchAsync<OrderReadModel>(s => s
              .Index("orders")
              .From((query.Page - 1) * query.PageSize)
              .Size(query.PageSize)
              .Query(q => q
                  .MultiMatch(mm => mm
                      .Query(query.SearchTerm)
                      .Fields(f => f
                          .Field(ff => ff.CustomerName)
                          .Field(ff => ff.CustomerEmail)
                          .Field(ff => ff.Lines.First().ProductName)
                      )
                  )
              )
          );

          return response.Documents.ToList();
      }
  }

Read Model Storage (ElasticSearch):

  # Index mapping (denormalized document)

  PUT /orders
  {
    "mappings": {
      "properties": {
        "orderId": { "type": "keyword" },
        "customerId": { "type": "keyword" },
        "customerName": { "type": "text" },
        "customerEmail": { "type": "keyword" },
        "status": { "type": "keyword" },
        "total": { "type": "scaled_float", "scaling_factor": 100 },
        "createdAt": { "type": "date" },
        "lines": {
          "type": "nested",
          "properties": {
            "productId": { "type": "keyword" },
            "productName": { "type": "text" },
            "productImage": { "type": "keyword" },
            "quantity": { "type": "integer" },
            "unitPrice": { "type": "scaled_float", "scaling_factor": 100 },
            "subtotal": { "type": "scaled_float", "scaling_factor": 100 }
          }
        }
      }
    }
  }
```

## Event Synchronization

```yaml
# ✅ Sync Write Model → Read Model via Events

Event Publisher (Write Side):

  public interface IEventPublisher
  {
      Task PublishAsync<TEvent>(TEvent @event) where TEvent : IEvent;
  }

  public class KafkaEventPublisher : IEventPublisher
  {
      private readonly IProducer<string, string> _producer;

      public async Task PublishAsync<TEvent>(TEvent @event) where TEvent : IEvent
      {
          var topic = @event.GetType().Name;  // "OrderCreatedEvent"
          var key = @event.AggregateId.ToString();
          var value = JsonSerializer.Serialize(@event);

          await _producer.ProduceAsync(topic, new Message<string, string>
          {
              Key = key,
              Value = value
          });
      }
  }

Domain Events:

  public record OrderCreatedEvent : IEvent
  {
      public Guid AggregateId => OrderId;
      public Guid OrderId { get; init; }
      public Guid CustomerId { get; init; }
      public string CustomerName { get; init; }
      public string CustomerEmail { get; init; }
      public decimal Total { get; init; }
      public List<OrderLineDto> Lines { get; init; }
      public DateTime CreatedAt { get; init; }
  }

  public record OrderStatusChangedEvent : IEvent
  {
      public Guid AggregateId => OrderId;
      public Guid OrderId { get; init; }
      public string OldStatus { get; init; }
      public string NewStatus { get; init; }
      public DateTime ChangedAt { get; init; }
  }

Event Consumer (Read Side):

  public class OrderEventConsumer : BackgroundService
  {
      private readonly IConsumer<string, string> _consumer;
      private readonly IElasticClient _elasticClient;

      protected override async Task ExecuteAsync(CancellationToken stoppingToken)
      {
          _consumer.Subscribe(new[] { "OrderCreatedEvent", "OrderStatusChangedEvent" });

          while (!stoppingToken.IsCancellationRequested)
          {
              var consumeResult = _consumer.Consume(stoppingToken);

              var eventType = consumeResult.Topic;
              var eventJson = consumeResult.Message.Value;

              switch (eventType)
              {
                  case "OrderCreatedEvent":
                      await HandleOrderCreated(eventJson);
                      break;

                  case "OrderStatusChangedEvent":
                      await HandleOrderStatusChanged(eventJson);
                      break;
              }

              _consumer.Commit(consumeResult);
          }
      }

      private async Task HandleOrderCreated(string eventJson)
      {
          var @event = JsonSerializer.Deserialize<OrderCreatedEvent>(eventJson);

          // ✅ Build read model
          var readModel = new OrderReadModel
          {
              OrderId = @event.OrderId,
              CustomerId = @event.CustomerId,
              CustomerName = @event.CustomerName,
              CustomerEmail = @event.CustomerEmail,
              Status = "Submitted",
              Total = @event.Total,
              CreatedAt = @event.CreatedAt,
              Lines = @event.Lines.Select(l => new OrderLineReadModel
              {
                  ProductId = l.ProductId,
                  ProductName = l.ProductName,
                  ProductImage = l.ProductImage,
                  Quantity = l.Quantity,
                  UnitPrice = l.UnitPrice,
                  Subtotal = l.Quantity * l.UnitPrice
              }).ToList()
          };

          // ✅ Index in ElasticSearch
          await _elasticClient.IndexDocumentAsync(readModel);
      }

      private async Task HandleOrderStatusChanged(string eventJson)
      {
          var @event = JsonSerializer.Deserialize<OrderStatusChangedEvent>(eventJson);

          // ✅ Update read model (partial update)
          await _elasticClient.UpdateAsync<OrderReadModel>(@event.OrderId, u => u
              .Doc(new { Status = @event.NewStatus })
          );
      }
  }
```

## API Layer (CQRS Routing)

```yaml
# ✅ API Routes Commands vs Queries

Commands (POST/PUT/DELETE):

  [ApiController]
  [Route("api/orders")]
  public class OrderCommandsController : ControllerBase
  {
      private readonly IMediator _mediator;

      [HttpPost]
      public async Task<IActionResult> CreateOrder([FromBody] CreateOrderCommand command)
      {
          var orderId = await _mediator.Send(command);
          return CreatedAtAction(nameof(GetOrder), new { id = orderId }, null);
      }

      [HttpPut("{id}/status")]
      public async Task<IActionResult> UpdateOrderStatus(Guid id, [FromBody] UpdateOrderStatusCommand command)
      {
          command = command with { OrderId = id };
          await _mediator.Send(command);
          return NoContent();
      }

      [HttpDelete("{id}")]
      public async Task<IActionResult> CancelOrder(Guid id)
      {
          await _mediator.Send(new CancelOrderCommand(id));
          return NoContent();
      }
  }

Queries (GET):

  [ApiController]
  [Route("api/orders")]
  public class OrderQueriesController : ControllerBase
  {
      private readonly IMediator _mediator;

      [HttpGet("{id}")]
      public async Task<ActionResult<OrderReadModel>> GetOrder(Guid id)
      {
          var order = await _mediator.Send(new GetOrderByIdQuery(id));

          if (order == null)
              return NotFound();

          return order;
      }

      [HttpGet("customer/{customerId}")]
      public async Task<ActionResult<List<OrderReadModel>>> GetOrdersByCustomer(
          Guid customerId,
          [FromQuery] int page = 1,
          [FromQuery] int pageSize = 20)
      {
          var orders = await _mediator.Send(new GetOrdersByCustomerQuery(customerId, page, pageSize));
          return orders;
      }

      [HttpGet("search")]
      public async Task<ActionResult<List<OrderReadModel>>> SearchOrders(
          [FromQuery] string q,
          [FromQuery] int page = 1,
          [FromQuery] int pageSize = 20)
      {
          var orders = await _mediator.Send(new SearchOrdersQuery(q, page, pageSize));
          return orders;
      }
  }
```

## Consistency Considerations

```yaml
# ✅ Handling Eventual Consistency

Consistency Lag:

  Timeline:
    t1: Client creates order → Write model saved (PostgreSQL)
    t2: Event published (Kafka)
    t3: Event consumed (lag ~2 seconds)
    t4: Read model updated (ElasticSearch)

  Problem: Client redirects to order details page at t2 → 404 Not Found

  Solution 1: Return Order Data in Create Response

    [HttpPost]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderCommand command)
    {
        var orderId = await _mediator.Send(command);

        // ✅ Return order data immediately (from write model)
        var order = await _orderRepository.GetByIdAsync(orderId);

        return CreatedAtAction(nameof(GetOrder), new { id = orderId }, order);
    }

  Solution 2: Poll Until Read Model Updated

    async function createOrder(data) {
      const response = await fetch('/api/orders', {
        method: 'POST',
        body: JSON.stringify(data)
      });

      const orderId = response.headers.get('Location').split('/').pop();

      // ✅ Poll until order appears in read model
      let order = null;
      for (let i = 0; i < 10; i++) {
        order = await fetch(`/api/orders/${orderId}`);
        if (order.ok) break;
        await sleep(500);  // Wait 500ms
      }

      return order;
    }

  Solution 3: Read-After-Write Consistency Flag

    [HttpGet("{id}")]
    public async Task<ActionResult<OrderReadModel>> GetOrder(
        Guid id,
        [FromQuery] bool consistentRead = false)
    {
        if (consistentRead)
        {
            // ✅ Read from write database (PostgreSQL)
            var order = await _orderRepository.GetByIdAsync(id);
            return MapToReadModel(order);
        }
        else
        {
            // ✅ Read from read database (ElasticSearch, eventually consistent)
            var order = await _mediator.Send(new GetOrderByIdQuery(id));
            return order;
        }
    }

    // Client usage
    const order = await fetch(`/api/orders/${orderId}?consistentRead=true`);

Idempotent Event Handling:

  private async Task HandleOrderCreated(string eventJson)
  {
      var @event = JsonSerializer.Deserialize<OrderCreatedEvent>(eventJson);

      // ✅ Check if already processed
      var exists = await _elasticClient.DocumentExistsAsync<OrderReadModel>(@event.OrderId);

      if (exists)
      {
          _logger.LogWarning("Order {OrderId} already indexed, skipping", @event.OrderId);
          return;  // ✅ Idempotent (safe to replay event)
      }

      // Process event...
  }
```

## Monitoring

```yaml
# ✅ CQRS Health Monitoring

Event Lag:

  # CloudWatch metric: Time between event published and consumed

  var lag = DateTime.UtcNow - @event.CreatedAt;

  cloudwatch.PutMetric(new MetricDatum
  {
      MetricName = "EventProcessingLag",
      Value = lag.TotalSeconds,
      Unit = StandardUnit.Seconds
  });

  # Alert if lag > 10 seconds

Read/Write Consistency:

  # Compare counts periodically

  var writeCount = await _dbContext.Orders.CountAsync();
  var readCount = await _elasticClient.CountAsync<OrderReadModel>();

  var diff = Math.Abs(writeCount - readCount);

  if (diff > 100)
  {
      _logger.LogWarning("Read/Write model out of sync: {WriteCount} vs {ReadCount}",
          writeCount, readCount);
  }

Failed Events:

  # Dead letter queue for failed event processing

  try
  {
      await HandleOrderCreated(eventJson);
  }
  catch (Exception ex)
  {
      _logger.LogError(ex, "Failed to process OrderCreatedEvent");

      // ✅ Send to DLQ for manual review
      await _deadLetterQueue.SendAsync(new
      {
          Topic = "OrderCreatedEvent",
          Payload = eventJson,
          Error = ex.Message,
          Timestamp = DateTime.UtcNow
      });
  }
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** separar write model (PostgreSQL) y read model (ElasticSearch/Redis) para servicios con high read/write ratio
- **MUST** publicar eventos después de cada write (Order Kafka)
- **MUST** usar read model para queries complejas (search, aggregations)
- **MUST** implementar idempotent event handlers (safe event replay)
- **MUST** monitorear event processing lag (alert if > 10s)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar MediatR para commands/queries (CQRS pattern enforcement)
- **SHOULD** documentar eventual consistency lag (set expectations)
- **SHOULD** proveer consistentRead flag para critical reads
- **SHOULD** usar dead letter queue para failed events

### MUST NOT (Prohibido)

- **MUST NOT** query write database para read-heavy operations (use read model)
- **MUST NOT** write directamente a read model (always via events)
- **MUST NOT** assume immediate consistency (eventual consistency by design)
- **MUST NOT** usar CQRS si read/write patterns son similares (overhead no justificado)

---

## Referencias

- [Event Sourcing](./event-sourcing.md)
- [Consistency Models](./consistency-models.md)
- [Saga Pattern](./saga-pattern.md)
- [Database Per Service](./database-per-service.md)
- [Event-Driven Architecture](../../estilos-arquitectonicos/event-driven.md)
