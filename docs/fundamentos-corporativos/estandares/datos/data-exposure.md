---
id: data-exposure
sidebar_position: 3
title: Data Exposure
description: Exponer datos únicamente mediante APIs o eventos, nunca por acceso directo a BD
---

# Data Exposure

## Contexto

Este estándar establece **Data Exposure**: datos SOLO se exponen mediante **APIs o eventos**, NUNCA acceso directo a base de datos. Compartir BD genera acoplamiento oculto. Complementa el [lineamiento de Datos por Dominio](../../lineamientos/datos/01-datos-por-dominio.md) mediante **contratos explícitos**.

---

## Concepto Fundamental

```yaml
# ❌ WRONG: Direct Database Access

Sales Service DB (PostgreSQL)
     │
     ├─► Sales Service (owner) ✅
     ├─► Billing Service (reads orders) ❌ Direct query
     ├─► Analytics Service (reads all) ❌ Direct query
     └─► Reporting Tool (SQL queries) ❌ Direct query

Problems:
  - Schema changes break consumers
  - No versioning (backward compatibility)
  - Bypass business rules (direct UPDATE)
  - No audit trail
  - Performance impact (unoptimized queries)
  - Security (consumers see ALL data)

# ✅ CORRECT: API/Event-Based Exposure

Sales Service (Owner)
  ├─ Internal: PostgreSQL (private)
  └─ Public Contracts:
      ├─► REST API: GET /api/orders/:id
      ├─► Events: OrderCreated, OrderApproved
      └─► GraphQL (opcional): Query orders

Billing Service:
  - Consumes: OrderApproved event
  - Calls: GET /api/orders/:id (si necesita detalles)
  - NO acceso directo a Sales DB ✅

Benefits:
  ✅ Decoupling (Sales cambia BD sin romper consumers)
  ✅ Versioning (v1, v2 APIs coexisten)
  ✅ Business rules enforced (via Service logic)
  ✅ Audit trail (API logs)
  ✅ Performance (Service optimiza queries)
  ✅ Security (consumers ven solo lo autorizado)
```

## API-Based Exposure

```csharp
// ✅ Sales Service: Expone datos via REST API

[ApiController]
[Route("api/orders")]
[Authorize]
public class OrdersController : ControllerBase
{
    private readonly IOrderQueryService _orderQuery;

    // ✅ Public API para consumers
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(OrderDto), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> GetOrder(Guid id)
    {
        // ✅ Business rules enforced
        var customerId = User.GetCustomerId();

        var order = await _orderQuery.GetByIdAsync(id);

        if (order == null)
            return NotFound();

        // ✅ Authorization (user sees only own orders)
        if (order.CustomerId != customerId && !User.IsAdmin())
            return Forbid();

        // ✅ DTO filters sensitive fields
        return Ok(OrderDto.FromEntity(order));
    }

    // ✅ Query endpoint (filtered by caller)
    [HttpGet]
    public async Task<IActionResult> GetOrders(
        [FromQuery] DateTime? from,
        [FromQuery] DateTime? to,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var customerId = User.GetCustomerId();

        var orders = await _orderQuery.GetByCustomerAsync(
            customerId, from, to, page, pageSize);

        return Ok(orders.Select(OrderDto.FromEntity));
    }
}

// ✅ DTO controls what's exposed
public class OrderDto
{
    public Guid OrderId { get; set; }
    public DateTime CreatedAt { get; set; }
    public decimal Total { get; set; }
    public string Status { get; set; }
    public List<OrderItemDto> Items { get; set; }

    // ❌ NOT exposed: InternalNotes, CostPrice, Margin

    public static OrderDto FromEntity(Order order)
    {
        return new OrderDto
        {
            OrderId = order.OrderId,
            CreatedAt = order.CreatedAt,
            Total = order.Total,
            Status = order.Status.ToString(),
            Items = order.Lines.Select(OrderItemDto.FromEntity).ToList()
        };
    }
}
```

## Event-Based Exposure

```csharp
// ✅ Sales Service: Publica eventos (async exposure)

public class OrderService : IOrderService
{
    private readonly IOrderRepository _orderRepo;
    private readonly IEventPublisher _eventPublisher;

    public async Task<Guid> ApproveOrderAsync(Guid orderId)
    {
        var order = await _orderRepo.GetByIdAsync(orderId);

        order.Approve();
        await _orderRepo.SaveAsync(order);

        // ✅ Publish event (consumers subscribe)
        await _eventPublisher.PublishAsync(new OrderApprovedEvent
        {
            OrderId = order.OrderId,
            CustomerId = order.CustomerId,
            Total = order.Total,
            ApprovedAt = DateTime.UtcNow,
            Items = order.Lines.Select(l => new OrderItemEvent
            {
                ProductId = l.ProductId,
                Quantity = l.Quantity,
                Price = l.UnitPrice
            }).ToList()
        });

        return orderId;
    }
}

// ✅ Consumer: Billing Service (subscribed to event)
public class OrderApprovedEventHandler : IEventHandler<OrderApprovedEvent>
{
    private readonly IInvoiceService _invoiceService;

    public async Task HandleAsync(OrderApprovedEvent @event)
    {
        // ✅ Usa datos del evento (no query directo a Sales DB)
        await _invoiceService.CreateInvoiceAsync(new CreateInvoiceCommand
        {
            OrderId = @event.OrderId,
            CustomerId = @event.CustomerId,
            Amount = @event.Total,
            Items = @event.Items
        });
    }
}
```

## Query Patterns

```yaml
# ✅ Patrones para exponer datos

Pattern 1: REST API (Synchronous)

  Use Case: Consumer necesita datos on-demand

  Example:
    GET /api/orders/:id
    GET /api/customers/:id/orders

  Benefits:
    - Request-response (immediate)
    - Familiar (HTTP/JSON)
    - Easy testing (curl, Postman)

  Considerations:
    - Versioning (v1, v2)
    - Pagination (large result sets)
    - Rate limiting (DoS protection)
    - Caching (performance)

Pattern 2: Events (Asynchronous)

  Use Case: Consumer reacciona a cambios

  Example:
    OrderCreated → Fulfillment starts picking
    OrderApproved → Billing creates invoice
    OrderShipped → Notification sends email

  Benefits:
    - Decoupling (fire-and-forget)
    - Scalability (async processing)
    - Eventual consistency

  Considerations:
    - Schema evolution (backward compatible)
    - Idempotency (duplicate events)
    - Dead letter queue (failed processing)

Pattern 3: GraphQL (Flexible)

  Use Case: Consumer necesita múltiples recursos

  Example:
    query {
      order(id: "abc-123") {
        orderId
        total
        customer { name, email }
        items { product { name }, quantity }
      }
    }

  Benefits:
    - Single request (reduce round-trips)
    - Client specifies fields (no over-fetching)
    - Strongly typed

  Considerations:
    - N+1 problem (use DataLoader)
    - Complex authorization
    - Query cost (depth limiting)

Pattern 4: Sync Query API (Cross-Domain)

  Cuando consumer necesita JOIN cross-services:

  ❌ WRONG:
    - Billing queries Sales DB + Catalog DB (direct)

  ✅ CORRECT:
    - Billing llama GET /api/orders/:id (Sales API)
    - Billing llama GET /api/products/:id (Catalog API)
    - Billing hace join en memory

  Alternative (BFF Pattern):
    - Backend-for-Frontend service
    - Hace las llamadas y join
    - Expone composite API
```

## Anti-Patterns

```yaml
# ❌ Violaciones comunes

1. Shared Database (Direct Query):

   # Multiple services → Same DB
   services:
     sales:
       database: postgres://sales-db
     billing:
       database: postgres://sales-db  ← ❌ Same DB

   Problem: Schema change breaks billing

2. Database View Sharing:

   -- Sales Service creates view
   CREATE VIEW public.orders_view AS
     SELECT order_id, customer_id, total FROM orders;

   -- Billing queries view
   SELECT * FROM orders_view;  ← ❌ Direct access

   Problem: Still coupling (view API no versionado)

3. Database Replication:

   Sales DB (master)
     → Replicates to →
   Billing DB (read replica)  ← ❌ Direct replica

   Problem: Mismo schema, same coupling

4. Data Warehouse ETL:

   ✅ PERMITIDO (Exception):
     - Analytics warehouse puede leer múltiples DBs
     - Batch ETL (nightly)
     - Reporting only (no operational writes)

   ⚠️ Con precaución:
     - Usa read replicas (no impactar prod)
     - Schema changes → Fix ETL jobs
     - Consider event-based approach (Kafka → Warehouse)

5. Admin Tool Direct Access:

   ❌ Admin panel → Direct SQL queries

   ✅ Admin panel → Admin API:
     POST /api/admin/orders/:id/cancel
     (Service logs action, enforces rules)
```

## Monitoring

```yaml
# ✅ Detectar acceso directo a BD

CloudTrail / RDS Logs:
  Alert on:
    - New DB connection from unknown IP
    - DB user created (should be service accounts only)
    - Schema changes from non-pipeline source

VPC Flow Logs:
  Monitor:
    - Billing Service → Sales DB port 5432 ❌
    - Expected: Billing → Sales API port 443 ✅

Metrics:
  API Usage:
    - GET /api/orders/:id (per consumer service)
    - Track: Latency, error rate, volume

  Event Publishing:
    - OrderCreated published count
    - Consumer lag (Kafka consumer group)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** exponer datos mediante APIs REST o eventos
- **MUST** prohibir acceso directo a BD cross-service
- **MUST** usar DTOs para filtrar campos sensibles
- **MUST** versionar APIs (v1, v2)
- **MUST** enforce authorization en API layer
- **MUST** validar esquemas de eventos (JSON Schema)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar GraphQL si consumers necesitan flexible queries
- **SHOULD** implement rate limiting (API protection)
- **SHOULD** paginar result sets grandes
- **SHOULD** cache responses (Redis)

### MUST NOT (Prohibido)

- **MUST NOT** permitir cross-service database queries
- **MUST NOT** compartir DB credentials cross-services
- **MUST NOT** exponer internal tables vía views públicas
- **MUST NOT** bypass API layer (except Analytics ETL con read replica)

---

## Referencias

- [Lineamiento: Datos por Dominio](../../lineamientos/datos/01-datos-por-dominio.md)
- [Database Per Service](./database-per-service.md)
- [No Shared Database](./no-shared-database.md)
- [API Standards](../apis/api-standards.md)
- [Event-Driven Architecture](../arquitectura/event-driven-architecture.md)
