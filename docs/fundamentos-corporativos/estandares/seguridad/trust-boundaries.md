---
id: trust-boundaries
sidebar_position: 3
title: Trust Boundaries
description: Definir límites de confianza explícitos entre componentes y validar datos en fronteras
---

# Trust Boundaries

## Contexto

Este estándar define **trust boundaries** (límites de confianza): fronteras donde cambia nivel de confianza entre componentes. Todo dato cruzando boundary DEBE ser validado. Complementa el [lineamiento de Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md) estableciendo **controles explícitos en fronteras**.

---

## Conceptos Fundamentales

```yaml
# ✅ Trust Boundary = Frontera donde cambia la confianza

Definición:
  - Separación entre zonas con diferentes niveles de confianza
  - Datos cruzando boundary NO pueden ser confiados automáticamente
  - Validación/sanitización OBLIGATORIA en boundary

Tipos de Boundaries:

  1. External → Internal:
     - Internet → API Gateway
     - Partner API → Integration layer
     - User input → Application

     Validación: Input validation, authentication, rate limiting

  2. Internal → Trusted:
     - Application → Database
     - Service → Secrets Manager
     - Lambda → S3

     Validación: Authorization, data sanitization

  3. Untrusted Process → Trusted Process:
     - User-uploaded file → File processor
     - External webhook → Event handler
     - Third-party library → Core business logic

     Validación: Schema validation, sandboxing, signature verification

Propiedades de Boundaries:
  ✅ Explícito (documentado en diagrama)
  ✅ Enforced (validación automática, no opcional)
  ✅ Auditable (logs de qué cruza boundary)
  ✅ Fail-safe (default deny)
```

## Identificar Trust Boundaries

```yaml
# ✅ Mapear boundaries en arquitectura

Sales Service (Talma): ┌──────────────────────────────────────────────────────┐
  │ UNTRUSTED ZONE (Internet)                            │
  │ - Usuarios anónimos                                  │
  │ - Bots, scrapers                                     │
  │ - Atacantes potenciales                              │
  └──────────────────────────────────────────────────────┘
  │
  ═════════════════╪═════════════════  ← BOUNDARY 1
  │
  ┌────────────▼─────────────┐
  │ AWS WAF                  │
  │ - OWASP rules            │
  │ - Rate limiting          │
  │ - Geo-blocking           │
  └────────────┬─────────────┘
  │
  ─────────────────╪─────────────────  ← BOUNDARY 2
  │
  ┌────────────▼─────────────┐
  │ Kong API Gateway         │
  │ - JWT validation         │
  │ - Input size limits      │
  │ - Schema validation      │
  └────────────┬─────────────┘
  │
  ═════════════════╪═════════════════  ← BOUNDARY 3 (MAJOR)
  │
  ┌──────────────────────▼───────────────────────────────┐
  │ SEMI-TRUSTED ZONE (DMZ)                              │
  │ - Autenticado pero no completamente confiado         │
  │                                                       │
  │    ┌──────────────────────────────────┐              │
  │    │ Sales Service (ECS Task)         │              │
  │    │ - FluentValidation (input)       │              │
  │    │ - Business rules enforcement     │              │
  │    │ - Output encoding                │              │
  │    └──────────┬───────────────────────┘              │
  │               │                                       │
  └───────────────┼───────────────────────────────────────┘
  │
  ─────────╪─────────────────────────  ← BOUNDARY 4
  │
  ┌───────────────▼───────────────────────────────────────┐
  │ TRUSTED ZONE (Data Layer)                             │
  │ - Solo componentes autorizados                        │
  │ - Private subnet, no internet                         │
  │                                                        │
  │    ┌──────────────────────────────────┐               │
  │    │ PostgreSQL RDS                   │               │
  │    │ - IAM authentication             │               │
  │    │ - Row-level security             │               │
  │    │ - Encryption at rest             │               │
  │    └──────────────────────────────────┘               │
  └────────────────────────────────────────────────────────┘

Controls per Boundary:
  BOUNDARY 1 (Internet → WAF): ✅ Block malicious IPs (GeoIP, reputation)
    ✅ Rate limiting (1000 req/5min per IP)
    ✅ SQL injection patterns
    ✅ XSS patterns
    ✅ Invalid HTTP methods

  BOUNDARY 2 (WAF → Gateway): ✅ TLS 1.3 only
    ✅ Valid certificates
    ✅ Request size < 10MB

  BOUNDARY 3 (Gateway → Application): ← CRITICAL
    ✅ JWT validation (signature, expiry)
    ✅ Scope/claims verification
    ✅ Schema validation (JSON Schema)
    ✅ Content-Type enforcement
    ✅ Authorization (can user access resource?)

  BOUNDARY 4 (Application → Database):
    ✅ Parameterized queries (no SQL injection)
    ✅ IAM authentication (no passwords)
    ✅ TLS encrypted connection
    ✅ Row-level filtering (user sees only own data)
```

## Validation at Boundaries

```csharp
// ✅ BOUNDARY 3: Kong Gateway → Sales Service

// API Gateway (Kong) - First validation layer
{
  "name": "request-validator",
  "config": {
    "body_schema": {
      "type": "object",
      "required": ["customerId", "items"],
      "properties": {
        "customerId": {
          "type": "string",
          "format": "uuid"
        },
        "items": {
          "type": "array",
          "minItems": 1,
          "maxItems": 100,
          "items": {
            "type": "object",
            "required": ["productId", "quantity"],
            "properties": {
              "productId": { "type": "string", "format": "uuid" },
              "quantity": { "type": "integer", "minimum": 1, "maximum": 999 }
            }
          }
        }
      }
    }
  }
}
// Si falla: 400 Bad Request (antes de llegar a app)

// Sales Service - Second validation layer (defense in depth)
[ApiController]
[Route("api/orders")]
public class OrdersController : ControllerBase
{
    [HttpPost]
    [Authorize] // JWT validation (Gateway already did, but verify again)
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
    {
        // ✅ TRUST BOUNDARY: Externo → Interno
        // Aunque Gateway validó, NO confiamos ciegamente

        // Re-validation (defense in depth)
        var validator = new CreateOrderRequestValidator();
        var validationResult = await validator.ValidateAsync(request);

        if (!validationResult.IsValid)
        {
            _logger.LogWarning(
                "Invalid order request from user {UserId}. Errors: {Errors}",
                User.GetUserId(),
                string.Join(", ", validationResult.Errors));

            return BadRequest(new { Errors = validationResult.Errors });
        }

        // ✅ Authorization (boundary enforcement)
        var customerId = Guid.Parse(User.GetCustomerId());

        if (request.CustomerId != customerId)
        {
            _logger.LogWarning(
                "User {UserId} attempted to create order for different customer {CustomerId}",
                User.GetUserId(), request.CustomerId);

            return Forbid(); // 403 Forbidden
        }

        // ✅ Business validation
        var command = new CreateOrderCommand
        {
            CustomerId = customerId, // Use authenticated ID, not request
            Items = request.Items
        };

        var orderId = await _orderService.CreateOrderAsync(command);

        return CreatedAtAction(nameof(GetOrder), new { id = orderId }, new { OrderId = orderId });
    }
}

// ✅ BOUNDARY 4: Application → Database

public class OrderRepository : IOrderRepository
{
    private readonly SalesDbContext _context;
    private readonly ICurrentUserService _currentUser;

    public async Task<Order?> GetByIdAsync(Guid orderId)
    {
        // ✅ TRUST BOUNDARY: Application → Data
        // Enforce row-level security (user sees only own orders)

        var customerId = _currentUser.GetCustomerId();

        // Parameterized query (no SQL injection)
        return await _context.Orders
            .Where(o => o.OrderId == orderId
                     && o.CustomerId == customerId) // ← Row-level security
            .FirstOrDefaultAsync();
    }

    public async Task SaveAsync(Order order)
    {
        // ✅ Validate before persisting
        if (order.CustomerId != _currentUser.GetCustomerId())
            throw new UnauthorizedAccessException("Cannot save order for different customer");

        // ✅ Sanitize data (prevent stored XSS)
        order.Notes = HtmlEncoder.Default.Encode(order.Notes);

        await _context.Orders.AddAsync(order);
        await _context.SaveChangesAsync();
    }
}
```

## Cross-Boundary Data Flow

```yaml
# ✅ Validar datos en CADA boundary que cruzan

Example: User crea orden con promoción

1. User Browser → Kong Gateway:

   Request:
     POST /api/orders
     { customerId: "guid", items: [...], promoCode: "SAVE20" }

   Boundary Controls:
     ✅ WAF: Size < 10MB, no malicious patterns
     ✅ Gateway: JWT valid, rate limit OK
     ✅ Gateway: JSON Schema valid

   Pass → Forward to Application

2. Kong Gateway → Sales Service:

   Boundary Controls:
     ✅ JWT re-validation (defense in depth)
     ✅ FluentValidation (business rules)
     ✅ Authorization (user owns customerId)

   Pass → Process order

3. Sales Service → Promo Service:

   Request:
     GET /api/promos/SAVE20
     Header: Authorization: Bearer <service-jwt>

   Boundary Controls:
     ✅ Service-to-service JWT (mTLS opcional)
     ✅ Promo Service valida JWT
     ✅ Rate limiting (100 req/min per service)

   Response:
     { code: "SAVE20", discount: 0.20, valid: true }

   ✅ Sales validates response schema
   ✅ Sales validates discount < 1.0 (sanity check)

4. Sales Service → PostgreSQL:

   Boundary Controls:
     ✅ Parameterized query (no SQL injection)
     ✅ IAM authentication
     ✅ TLS connection
     ✅ Row-level security (CustomerId filter)

   Query:
     INSERT INTO orders (order_id, customer_id, total, discount)
     VALUES (@orderId, @customerId, @total, @discount)

   Pass → Order saved

5. Sales Service → Kafka:

   Event:
     OrderCreated { OrderId, CustomerId, Total }

   Boundary Controls:
     ✅ Event schema validation (JSON Schema)
     ✅ SASL authentication (Kafka)
     ✅ TLS encryption

   Pass → Event published

Result: 5 boundaries crossed, 5 validaciones ejecutadas
```

## Boundary Violations

```yaml
# ❌ Ejemplos de violaciones comunes

1. Trust Boundary Bypass:

   ❌ Mal:
     // Frontend envía "isAdmin: true" en request
     POST /api/orders
     { customerId: "...", isAdmin: true }

     // Backend confía ciegamente
     if (request.IsAdmin) {
       ApplyAdminDiscount();
     }

   ✅ Bien:
     // Backend obtiene roles de JWT (trusted source)
     var roles = User.GetRoles(); // From validated JWT
     if (roles.Contains("Admin")) {
       ApplyAdminDiscount();
     }

2. Insufficient Validation:

   ❌ Mal:
     // Solo Gateway valida, Application confía
     [HttpPost]
     public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
     {
       // ❌ No validation, confía que Gateway hizo bien
       await _orderService.CreateAsync(request);
     }

   ✅ Bien:
     // Defense in depth: re-validate en Application
     [HttpPost]
     public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
     {
       var validation = await _validator.ValidateAsync(request);
       if (!validation.IsValid) return BadRequest();

       await _orderService.CreateAsync(request);
     }

3. Data Leakage across Boundaries:

   ❌ Mal:
     // Exponer más datos de los necesarios
     public async Task<Order> GetOrderAsync(Guid orderId)
     {
       var order = await _orderRepo.GetByIdAsync(orderId);
       return order; // ← Incluye CustomerId, InternalNotes, CostPrice
     }

   ✅ Bien:
     // DTO filtra campos sensibles
     public async Task<OrderDto> GetOrderAsync(Guid orderId)
     {
       var order = await _orderRepo.GetByIdAsync(orderId);

       return new OrderDto
       {
         OrderId = order.OrderId,
         Items = order.Items.Select(i => new OrderItemDto
         {
           ProductId = i.ProductId,
           Quantity = i.Quantity,
           // ❌ NO exponer: CostPrice (solo SalePrice)
           Price = i.SalePrice
         }).ToList(),
         Total = order.Total
         // ❌ NO exponer: InternalNotes, Margin
       };
     }
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** identificar y documentar trust boundaries en architecture diagrams
- **MUST** validar datos en CADA boundary cruzado
- **MUST** aplicar authentication en boundaries externos
- **MUST** aplicar authorization para recursos protegidos
- **MUST** usar parameterized queries (no string concatenation)
- **MUST** sanitizar datos antes de storage
- **MUST** log accesos cross-boundary (audit trail)

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar defense in depth (múltiples validaciones)
- **SHOULD** usar DTOs/schemas explícitos en boundaries
- **SHOULD** aplicar mTLS para service-to-service (producción)
- **SHOULD** validar tamaño de request (DoS prevention)

### MUST NOT (Prohibido)

- **MUST NOT** confiar datos de fuente no validada
- **MUST NOT** exponer boundary controls en mensajes de error
- **MUST NOT** permitir boundary bypass (ej: skip validation)
- **MUST NOT** confiar client-provided security claims

---

## Referencias

- [Lineamiento: Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md)
- [Security by Design](./security-by-design.md)
- [Threat Modeling](./threat-modeling.md)
- [API Security](../apis/api-security.md)
