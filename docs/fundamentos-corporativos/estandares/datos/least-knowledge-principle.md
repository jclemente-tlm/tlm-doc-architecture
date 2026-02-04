---
id: least-knowledge-principle
sidebar_position: 8
title: Principle of Least Knowledge
description: Estándar para aplicar el principio de mínimo conocimiento en acceso a datos, limitando dependencias innecesarias
---

# Estándar Técnico — Principle of Least Knowledge (Law of Demeter)

---

## 1. Propósito

Minimizar acoplamiento entre servicios limitando el conocimiento que cada servicio tiene sobre las estructuras de datos de otros, exponiendo solo información esencial y ocultando detalles de implementación.

---

## 2. Alcance

**Aplica a:**

- Diseño de APIs públicas entre servicios
- DTOs y contratos de API
- Event schemas
- GraphQL queries
- Denormalización de datos

**No aplica a:**

- Queries internos dentro del mismo bounded context
- Database schema interno (no expuesto)
- Debug/admin endpoints (con autorización estricta)

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología       | Versión mínima | Observaciones                   |
| -------------- | ---------------- | -------------- | ------------------------------- |
| **DTOs**       | Record types     | C# 10+         | Immutable DTOs                  |
| **Mapping**    | Mapster          | 7.4+           | Entity → DTO mappings           |
| **Projection** | EF Core Select   | 8.0+           | Proyecciones SQL eficientes     |
| **GraphQL**    | HotChocolate     | 13.0+          | Proyecciones con @skip/@include |
| **Validation** | FluentValidation | 11.8+          | Input validation                |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Exposición Mínima de Datos

- [ ] **Exponer solo campos necesarios** para el caso de uso
- [ ] No exponer entities completas de EF Core
- [ ] DTOs específicos por endpoint/operación
- [ ] Proyecciones SQL para evitar over-fetching
- [ ] Pagination obligatoria para colecciones

### Navegación Limitada

- [ ] **No chain navigation** en responses (ej: `order.customer.address.city`)
- [ ] Links HATEOAS para navegar a recursos relacionados
- [ ] Máximo 2 niveles de anidación en responses
- [ ] Embedded objects solo si siempre necesarios juntos

### Ocultar Detalles de Implementación

- [ ] No exponer IDs internos de BD (usar UUIDs públicos)
- [ ] No exponer nombres de tablas/columnas
- [ ] No exponer versiones internas (row_version, timestamps internos)
- [ ] Enums como strings, no integers

### Versionado de Contratos

- [ ] Backward compatibility en evolución de DTOs
- [ ] Campos nuevos opcionales
- [ ] Deprecation warnings antes de remover campos
- [ ] Versioning explícito de APIs

---

## 5. Prohibiciones

- ❌ Exponer entities de EF Core directamente como DTOs
- ❌ Incluir toda la entity graph en response (circular references)
- ❌ Navigation properties automáticas sin control
- ❌ Exponer detalles de schema de BD
- ❌ Responses con datos no solicitados
- ❌ Tight coupling a estructura interna de otros servicios
- ❌ Magic strings para nombres de campos

---

## 6. Configuración Mínima

### DTOs Específicos por Caso de Uso

```csharp
// ❌ MAL: Exponer entity directamente
[HttpGet("{id}")]
public async Task<Order> GetOrder(Guid id)  // NO!
{
    return await _context.Orders
        .Include(o => o.Items)
        .Include(o => o.Customer)  // Lazy loading podría exponer todo
        .FirstOrDefaultAsync(o => o.Id == id);
}

// ✅ BIEN: DTO específico
[HttpGet("{id}")]
public async Task<ActionResult<OrderSummaryDto>> GetOrder(Guid id)
{
    var order = await _context.Orders
        .Where(o => o.Id == id)
        .Select(o => new OrderSummaryDto  // Proyección SQL
        {
            Id = o.Id,
            TotalAmount = o.TotalAmount,
            Status = o.Status,
            CreatedAt = o.CreatedAt,

            // Solo customer ID, no todo el objeto
            CustomerId = o.CustomerId,

            // Counts, no arrays completos
            ItemCount = o.Items.Count
        })
        .FirstOrDefaultAsync();

    if (order == null)
        return NotFound();

    return Ok(order);
}

// DTOs/OrderSummaryDto.cs - Vista mínima
public record OrderSummaryDto
{
    public Guid Id { get; init; }
    public decimal TotalAmount { get; init; }
    public string Status { get; init; }
    public DateTime CreatedAt { get; init; }

    // Referencia, no embedded object completo
    public Guid CustomerId { get; init; }

    // HATEOAS link en lugar de objeto completo
    public string CustomerHref { get; init; }

    // Agregado en lugar de array completo
    public int ItemCount { get; init; }
}

// DTOs/OrderDetailsDto.cs - Vista completa para endpoint específico
public record OrderDetailsDto
{
    public Guid Id { get; init; }
    public decimal TotalAmount { get; init; }
    public string Status { get; init; }
    public DateTime CreatedAt { get; init; }

    // Embedded customer summary (solo lo necesario)
    public CustomerSummaryDto Customer { get; init; }

    // Items incluidos en details view
    public List<OrderItemDto> Items { get; init; }

    // HATEOAS links
    public OrderLinks Links { get; init; }
}

public record CustomerSummaryDto
{
    public Guid Id { get; init; }
    public string Name { get; init; }
    public string Email { get; init; }
    // NO incluir address, phone, etc. a menos que sean necesarios
}
```

### HATEOAS Links

```csharp
// DTOs/OrderDto.cs
public record OrderDto
{
    public Guid Id { get; init; }
    public decimal TotalAmount { get; init; }
    public string Status { get; init; }

    // Links en lugar de embedded objects
    [JsonPropertyName("_links")]
    public OrderLinks Links { get; init; }
}

public record OrderLinks
{
    public Link Self { get; init; }
    public Link Customer { get; init; }
    public Link Items { get; init; }
    public Link Payment { get; init; }
}

public record Link
{
    public string Href { get; init; }
    public string Method { get; init; } = "GET";
}

// Controllers/OrdersController.cs
[HttpGet("{id}")]
public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
{
    var order = await _orderService.GetOrderAsync(id);

    if (order == null)
        return NotFound();

    var dto = new OrderDto
    {
        Id = order.Id,
        TotalAmount = order.TotalAmount,
        Status = order.Status.ToString(),
        Links = new OrderLinks
        {
            Self = new Link
            {
                Href = Url.Action(nameof(GetOrder), new { id })
            },
            Customer = new Link
            {
                Href = $"/api/v1/customers/{order.CustomerId}"
            },
            Items = new Link
            {
                Href = Url.Action(nameof(GetOrderItems), new { orderId = id })
            },
            Payment = new Link
            {
                Href = $"/api/v1/payments?orderId={id}"
            }
        }
    };

    return Ok(dto);
}
```

### Proyecciones con EF Core

```csharp
// Services/OrderService.cs
public class OrderService
{
    private readonly OrdersDbContext _context;

    // ❌ MAL: Cargar todo el graph
    public async Task<Order> GetOrderWithEverythingAsync(Guid id)
    {
        return await _context.Orders
            .Include(o => o.Items)
                .ThenInclude(i => i.Product)
                    .ThenInclude(p => p.Category)  // Exceso de navigation
            .Include(o => o.Customer)
                .ThenInclude(c => c.Addresses)  // No necesario
            .FirstOrDefaultAsync(o => o.Id == id);
    }

    // ✅ BIEN: Proyección solo de lo necesario
    public async Task<OrderSummaryProjection> GetOrderSummaryAsync(Guid id)
    {
        return await _context.Orders
            .Where(o => o.Id == id)
            .Select(o => new OrderSummaryProjection
            {
                OrderId = o.Id,
                TotalAmount = o.TotalAmount,
                Status = o.Status,
                CreatedAt = o.CreatedAt,

                // Solo campos necesarios del customer
                CustomerName = o.Customer.Name,
                CustomerEmail = o.Customer.Email,
                // NO incluir customer.Addresses, etc.

                // Agregados eficientes
                ItemCount = o.Items.Count,
                TotalQuantity = o.Items.Sum(i => i.Quantity),

                // Top 3 items más caros (sin traer todos)
                TopItems = o.Items
                    .OrderByDescending(i => i.UnitPrice * i.Quantity)
                    .Take(3)
                    .Select(i => new OrderItemProjection
                    {
                        ProductName = i.Product.Name,
                        Quantity = i.Quantity,
                        Subtotal = i.UnitPrice * i.Quantity
                    })
                    .ToList()
            })
            .FirstOrDefaultAsync();
    }
}
```

### Pagination Obligatoria

```csharp
// Controllers/OrdersController.cs
[HttpGet]
public async Task<ActionResult<PagedResult<OrderSummaryDto>>> GetOrders(
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 20,
    [FromQuery] string? status = null)
{
    // Validar pageSize
    if (pageSize > 100)
        pageSize = 100;  // Máximo 100 items

    var query = _context.Orders.AsQueryable();

    if (!string.IsNullOrEmpty(status))
        query = query.Where(o => o.Status.ToString() == status);

    var totalCount = await query.CountAsync();

    var orders = await query
        .OrderByDescending(o => o.CreatedAt)
        .Skip((page - 1) * pageSize)
        .Take(pageSize)
        .Select(o => new OrderSummaryDto
        {
            Id = o.Id,
            TotalAmount = o.TotalAmount,
            Status = o.Status.ToString(),
            CreatedAt = o.CreatedAt,
            CustomerId = o.CustomerId,
            ItemCount = o.Items.Count
        })
        .ToListAsync();

    var result = new PagedResult<OrderSummaryDto>
    {
        Items = orders,
        Page = page,
        PageSize = pageSize,
        TotalCount = totalCount,
        TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize),
        Links = new PaginationLinks
        {
            Self = Url.Action(nameof(GetOrders), new { page, pageSize, status }),
            First = Url.Action(nameof(GetOrders), new { page = 1, pageSize, status }),
            Last = Url.Action(nameof(GetOrders), new { page = (int)Math.Ceiling(totalCount / (double)pageSize), pageSize, status }),
            Next = page < Math.Ceiling(totalCount / (double)pageSize)
                ? Url.Action(nameof(GetOrders), new { page = page + 1, pageSize, status })
                : null,
            Prev = page > 1
                ? Url.Action(nameof(GetOrders), new { page = page - 1, pageSize, status })
                : null
        }
    };

    return Ok(result);
}
```

### GraphQL con Proyecciones

```csharp
// GraphQL/OrderQueries.cs
public class OrderQueries
{
    // Cliente puede solicitar solo campos que necesita
    [UseProjection]  // HotChocolate proyecta automáticamente
    [UseFiltering]
    [UseSorting]
    public IQueryable<OrderDto> GetOrders(
        [Service] OrdersDbContext context)
    {
        return context.Orders
            .Select(o => new OrderDto
            {
                Id = o.Id,
                TotalAmount = o.TotalAmount,
                Status = o.Status.ToString(),
                CreatedAt = o.CreatedAt,

                // Cliente decide si incluir customer
                Customer = new CustomerDto
                {
                    Id = o.Customer.Id,
                    Name = o.Customer.Name,
                    Email = o.Customer.Email
                },

                // Cliente decide si incluir items
                Items = o.Items.Select(i => new OrderItemDto
                {
                    ProductId = i.ProductId,
                    ProductName = i.Product.Name,
                    Quantity = i.Quantity,
                    UnitPrice = i.UnitPrice
                }).ToList()
            });
    }
}

// Query GraphQL - cliente solicita solo lo necesario
// query {
//   orders {
//     id
//     totalAmount
//     status
//     customer {
//       name
//     }
//     # NO solicitar items si no son necesarios
//   }
// }
```

---

## 7. Ejemplos

### Máximo 2 Niveles de Anidación

```csharp
// ✅ BIEN: 2 niveles máximo
public record OrderDto
{
    public Guid Id { get; init; }

    // Nivel 1: customer
    public CustomerDto Customer { get; init; }
}

public record CustomerDto
{
    public Guid Id { get; init; }
    public string Name { get; init; }

    // Nivel 2: primaryAddress (último nivel)
    public AddressDto PrimaryAddress { get; init; }
}

// ❌ MAL: Múltiples niveles de anidación
public record OrderDto
{
    public CustomerDto Customer { get; init; }
}

public record CustomerDto
{
    public AddressDto Address { get; init; }
}

public record AddressDto
{
    public CityDto City { get; init; }  // Nivel 3 - demasiado profundo
}

public record CityDto
{
    public CountryDto Country { get; init; }  // Nivel 4 - muy profundo
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] No entities de EF Core expuestas directamente
- [ ] DTOs específicos por endpoint
- [ ] Proyecciones SQL (Select) para performance
- [ ] HATEOAS links para navegación
- [ ] Pagination en endpoints de colecciones
- [ ] Máximo 2 niveles de anidación
- [ ] Enums como strings

### Métricas

```promql
# Response size promedio
histogram_quantile(0.95, api_response_size_bytes)

# Over-fetching (queries que cargan muchos datos)
pg_stat_statements_mean_exec_time > 100
```

### Code Review Checklist

```csharp
// Buscar anti-patterns
// ❌ return _context.Orders.Include(o => o.Customer).ToList();
// ❌ public Order GetOrder(Guid id)
// ❌ .Include(o => o.Items).ThenInclude(i => i.Product).ThenInclude(p => p.Category)
```

---

## 9. Referencias

**Teoría:**

- Law of Demeter (Principle of Least Knowledge)
- Martin Fowler - "Data Transfer Object"
- Eric Evans - "Domain-Driven Design"

**Documentación:**

- [EF Core Projections](https://learn.microsoft.com/en-us/ef/core/querying/how-query-works)
- [AutoMapper Documentation](https://docs.automapper.org/)
- [HATEOAS REST Constraint](https://restfulapi.net/hateoas/)

**Buenas prácticas:**

- RESTful API Design Rulebook (O'Reilly)
- "Clean Architecture" - Robert C. Martin
