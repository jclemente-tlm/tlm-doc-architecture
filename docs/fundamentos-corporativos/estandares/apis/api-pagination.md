---
id: api-pagination
sidebar_position: 5
title: Paginación de APIs
description: Patrones de paginación para colecciones grandes con offset y cursor
---

# Paginación de APIs

## Contexto

Este estándar define cómo implementar paginación en endpoints que retornan colecciones grandes. Complementa el [lineamiento de APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md) especificando **cómo** paginar datos eficientemente usando estrategias offset-based y cursor-based.

---

## Stack Tecnológico

| Componente        | Tecnología       | Versión | Uso                      |
| ----------------- | ---------------- | ------- | ------------------------ |
| **Framework**     | ASP.NET Core     | 8.0+    | Framework base           |
| **ORM**           | Entity Framework | 8.0+    | Acceso a datos           |
| **Base de Datos** | PostgreSQL       | 14+     | Base de datos relacional |

### Dependencias NuGet

```xml
<PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
<PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />
```

---

## Implementación Técnica

### Offset-Based Pagination (Recomendada para mayoría de casos)

```csharp
// Request
GET /api/v1/orders?page=2&pageSize=20&sortBy=createdAt&sortOrder=desc

// DTO de respuesta paginada
public record PagedResult<T>
{
    public List<T> Items { get; init; } = new();
    public int Page { get; init; }
    public int PageSize { get; init; }
    public int TotalCount { get; init; }
    public int TotalPages { get; init; }
    public bool HasPreviousPage { get; init; }
    public bool HasNextPage { get; init; }
}

// Controller
[HttpGet]
[ProducesResponseType(typeof(PagedResult<OrderDto>), StatusCodes.Status200OK)]
public async Task<ActionResult<PagedResult<OrderDto>>> GetOrders(
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 20,
    [FromQuery] string sortBy = "createdAt",
    [FromQuery] string sortOrder = "desc")
{
    // ✅ Validar parámetros
    if (page < 1)
        page = 1;

    if (pageSize < 1 || pageSize > 100)
        pageSize = 20;

    var result = await _orderService.GetOrdersPagedAsync(
        page,
        pageSize,
        sortBy,
        sortOrder
    );

    return Ok(result);
}

// Service
public async Task<PagedResult<OrderDto>> GetOrdersPagedAsync(
    int page,
    int pageSize,
    string sortBy,
    string sortOrder)
{
    var query = _dbContext.Orders.AsQueryable();

    // ✅ MUST: Obtener total antes de paginar
    var totalCount = await query.CountAsync();

    // ✅ Aplicar ordenamiento
    query = sortBy.ToLower() switch
    {
        "createdAt" => sortOrder.ToLower() == "asc"
            ? query.OrderBy(o => o.CreatedAt)
            : query.OrderByDescending(o => o.CreatedAt),
        "totalAmount" => sortOrder.ToLower() == "asc"
            ? query.OrderBy(o => o.TotalAmount)
            : query.OrderByDescending(o => o.TotalAmount),
        _ => query.OrderByDescending(o => o.CreatedAt) // Default
    };

    // ✅ Aplicar paginación
    var items = await query
        .Skip((page - 1) * pageSize)
        .Take(pageSize)
        .Select(o => new OrderDto
        {
            Id = o.Id,
            OrderNumber = o.OrderNumber,
            CustomerId = o.CustomerId,
            TotalAmount = o.TotalAmount,
            Status = o.Status,
            CreatedAt = o.CreatedAt
        })
        .ToListAsync();

    var totalPages = (int)Math.Ceiling(totalCount / (double)pageSize);

    return new PagedResult<OrderDto>
    {
        Items = items,
        Page = page,
        PageSize = pageSize,
        TotalCount = totalCount,
        TotalPages = totalPages,
        HasPreviousPage = page > 1,
        HasNextPage = page < totalPages
    };
}
```

### Response con Metadata en Headers (Alternativa)

```csharp
[HttpGet]
public async Task<ActionResult<List<OrderDto>>> GetOrders(
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 20)
{
    var result = await _orderService.GetOrdersPagedAsync(page, pageSize);

    // ✅ Incluir metadata en headers
    Response.Headers["X-Page"] = page.ToString();
    Response.Headers["X-Page-Size"] = pageSize.ToString();
    Response.Headers["X-Total-Count"] = result.TotalCount.ToString();
    Response.Headers["X-Total-Pages"] = result.TotalPages.ToString();

    // ✅ Links de navegación (RFC 8288)
    var links = new List<string>();
    var baseUrl = $"{Request.Scheme}://{Request.Host}{Request.Path}";

    if (result.HasPreviousPage)
    {
        links.Add($"<{baseUrl}?page={page - 1}&pageSize={pageSize}>; rel=\"prev\"");
        links.Add($"<{baseUrl}?page=1&pageSize={pageSize}>; rel=\"first\"");
    }

    if (result.HasNextPage)
    {
        links.Add($"<{baseUrl}?page={page + 1}&pageSize={pageSize}>; rel=\"next\"");
        links.Add($"<{baseUrl}?page={result.TotalPages}&pageSize={pageSize}>; rel=\"last\"");
    }

    if (links.Any())
        Response.Headers["Link"] = string.Join(", ", links);

    return Ok(result.Items);
}

// Response:
// HTTP/1.1 200 OK
// X-Page: 2
// X-Page-Size: 20
// X-Total-Count: 150
// X-Total-Pages: 8
// Link: <https://api.talma.com/api/v1/orders?page=1&pageSize=20>; rel="first",
//       <https://api.talma.com/api/v1/orders?page=1&pageSize=20>; rel="prev",
//       <https://api.talma.com/api/v1/orders?page=3&pageSize=20>; rel="next",
//       <https://api.talma.com/api/v1/orders?page=8&pageSize=20>; rel="last"
```

### Cursor-Based Pagination (Para datos de alta frecuencia)

```csharp
// Request
GET /api/v1/orders?cursor=eyJpZCI6IjU1MGU4NDAwLWUyOWItNDFkNCIsInRpbWVzdGFtcCI6IjIwMjQtMDEtMTVUMTA6MzA6MDBaIn0&limit=20

// DTO de respuesta cursor-based
public record CursorPagedResult<T>
{
    public List<T> Items { get; init; } = new();
    public string? NextCursor { get; init; }
    public string? PreviousCursor { get; init; }
    public bool HasMore { get; init; }
}

// Cursor structure (Base64 encoded)
public record Cursor
{
    public Guid Id { get; init; }
    public DateTime Timestamp { get; init; }

    public string Encode()
    {
        var json = JsonSerializer.Serialize(this);
        return Convert.ToBase64String(Encoding.UTF8.GetBytes(json));
    }

    public static Cursor? Decode(string? encodedCursor)
    {
        if (string.IsNullOrEmpty(encodedCursor))
            return null;

        try
        {
            var json = Encoding.UTF8.GetString(Convert.FromBase64String(encodedCursor));
            return JsonSerializer.Deserialize<Cursor>(json);
        }
        catch
        {
            return null;
        }
    }
}

// Controller
[HttpGet]
[ProducesResponseType(typeof(CursorPagedResult<OrderDto>), StatusCodes.Status200OK)]
public async Task<ActionResult<CursorPagedResult<OrderDto>>> GetOrders(
    [FromQuery] string? cursor = null,
    [FromQuery] int limit = 20)
{
    // ✅ Validar limit
    if (limit < 1 || limit > 100)
        limit = 20;

    var result = await _orderService.GetOrdersCursorPagedAsync(cursor, limit);

    return Ok(result);
}

// Service
public async Task<CursorPagedResult<OrderDto>> GetOrdersCursorPagedAsync(
    string? encodedCursor,
    int limit)
{
    var cursor = Cursor.Decode(encodedCursor);

    var query = _dbContext.Orders.AsQueryable();

    // ✅ Filtrar desde cursor (forward pagination)
    if (cursor != null)
    {
        query = query.Where(o =>
            o.CreatedAt < cursor.Timestamp ||
            (o.CreatedAt == cursor.Timestamp && o.Id.CompareTo(cursor.Id) < 0)
        );
    }

    // ✅ Ordenar por timestamp + ID (estable)
    query = query.OrderByDescending(o => o.CreatedAt)
                 .ThenByDescending(o => o.Id);

    // ✅ Obtener limit + 1 para saber si hay más
    var items = await query
        .Take(limit + 1)
        .Select(o => new OrderDto
        {
            Id = o.Id,
            OrderNumber = o.OrderNumber,
            CustomerId = o.CustomerId,
            TotalAmount = o.TotalAmount,
            Status = o.Status,
            CreatedAt = o.CreatedAt
        })
        .ToListAsync();

    var hasMore = items.Count > limit;

    if (hasMore)
        items.RemoveAt(items.Count - 1);

    // ✅ Generar next cursor
    string? nextCursor = null;
    if (hasMore && items.Any())
    {
        var lastItem = items.Last();
        nextCursor = new Cursor
        {
            Id = lastItem.Id,
            Timestamp = lastItem.CreatedAt
        }.Encode();
    }

    return new CursorPagedResult<OrderDto>
    {
        Items = items,
        NextCursor = nextCursor,
        HasMore = hasMore
    };
}

// Response:
// {
//   "items": [...],
//   "nextCursor": "eyJpZCI6IjU1MGU4NDAwLWUyOWItNDFkNCIsInRpbWVzdGFtcCI6IjIwMjQtMDEtMTVUMTA6MzA6MDBaIn0",
//   "hasMore": true
// }
```

### Paginación con Filtros

```csharp
// Request
GET /api/v1/orders?status=Pending&customerId=3fa85f64-5717-4562-b3fc-2c963f66afa6&page=1&pageSize=20

// DTO de filtros
public record OrderFilters
{
    public OrderStatus? Status { get; init; }
    public Guid? CustomerId { get; init; }
    public decimal? MinAmount { get; init; }
    public decimal? MaxAmount { get; init; }
    public DateTime? CreatedFrom { get; init; }
    public DateTime? CreatedTo { get; init; }
}

// Controller
[HttpGet]
public async Task<ActionResult<PagedResult<OrderDto>>> GetOrders(
    [FromQuery] OrderFilters filters,
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 20)
{
    var result = await _orderService.GetOrdersFilteredPagedAsync(
        filters,
        page,
        pageSize
    );

    return Ok(result);
}

// Service
public async Task<PagedResult<OrderDto>> GetOrdersFilteredPagedAsync(
    OrderFilters filters,
    int page,
    int pageSize)
{
    var query = _dbContext.Orders.AsQueryable();

    // ✅ Aplicar filtros
    if (filters.Status.HasValue)
        query = query.Where(o => o.Status == filters.Status.Value);

    if (filters.CustomerId.HasValue)
        query = query.Where(o => o.CustomerId == filters.CustomerId.Value);

    if (filters.MinAmount.HasValue)
        query = query.Where(o => o.TotalAmount >= filters.MinAmount.Value);

    if (filters.MaxAmount.HasValue)
        query = query.Where(o => o.TotalAmount <= filters.MaxAmount.Value);

    if (filters.CreatedFrom.HasValue)
        query = query.Where(o => o.CreatedAt >= filters.CreatedFrom.Value);

    if (filters.CreatedTo.HasValue)
        query = query.Where(o => o.CreatedAt <= filters.CreatedTo.Value);

    // ✅ MUST: COUNT después de filtros
    var totalCount = await query.CountAsync();

    // ✅ Ordenar y paginar
    var items = await query
        .OrderByDescending(o => o.CreatedAt)
        .Skip((page - 1) * pageSize)
        .Take(pageSize)
        .Select(o => new OrderDto { /* mapeo */ })
        .ToListAsync();

    var totalPages = (int)Math.Ceiling(totalCount / (double)pageSize);

    return new PagedResult<OrderDto>
    {
        Items = items,
        Page = page,
        PageSize = pageSize,
        TotalCount = totalCount,
        TotalPages = totalPages,
        HasPreviousPage = page > 1,
        HasNextPage = page < totalPages
    };
}
```

### Performance - Índices de Base de Datos

```sql
-- ✅ MUST: Índice para paginación offset-based
CREATE INDEX idx_orders_created_at_id
ON orders (created_at DESC, id DESC);

-- ✅ MUST: Índice para filtros comunes
CREATE INDEX idx_orders_customer_status_created
ON orders (customer_id, status, created_at DESC);

-- ✅ MUST: Índice compuesto para cursor pagination
CREATE INDEX idx_orders_cursor
ON orders (created_at DESC, id DESC)
INCLUDE (order_number, total_amount, status);

-- ✅ Performance con EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT id, order_number, customer_id, total_amount, status, created_at
FROM orders
WHERE status = 'Pending'
ORDER BY created_at DESC
LIMIT 20 OFFSET 40;
```

### Estrategia de Paginación - Cuándo Usar Cada Una

```csharp
// ✅ Offset-Based: Usar cuando...
// - Necesitas saltar a página específica (página 5, 10, etc.)
// - Datos relativamente estáticos
// - Necesitas total de páginas
// - UI requiere navegación por número de página
GET /api/v1/orders?page=5&pageSize=20

// ✅ Cursor-Based: Usar cuando...
// - Datos de alta frecuencia (feeds, actividad en tiempo real)
// - Scroll infinito (mobile apps)
// - Inserción constante de nuevos registros
// - Mejor performance en datasets grandes
// - No necesitas saltar a página específica
GET /api/v1/orders?cursor=abc123&limit=20

// ❌ EVITAR: Offset grande en tablas grandes
// Offset 100000 en tabla de 1M registros = ⚠️ LENTO
GET /api/v1/orders?page=5000&pageSize=20  // ❌ Escanea 100,000 registros

// ✅ PREFERIR: Cursor para datasets grandes
GET /api/v1/orders?cursor=lastItemCursor&limit=20  // ✅ Escanea desde cursor
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar paginación en todos los endpoints que retornan colecciones
- **MUST** usar offset-based como estrategia por defecto
- **MUST** limitar `pageSize` máximo (recomendado: 100)
- **MUST** usar `pageSize` por defecto de 20 si no se especifica
- **MUST** validar que `page` >= 1
- **MUST** retornar metadata de paginación (`totalCount`, `totalPages`, `hasNext`, `hasPrevious`)
- **MUST** crear índices apropiados para campos de ordenamiento
- **MUST** ordenar resultados de forma determinística (incluir ID en sort para estabilidad)
- **MUST** usar cursor-based para feeds en tiempo real o scroll infinito

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir links de navegación en headers (`Link: rel="next"`)
- **SHOULD** incluir metadata en response body (preferido sobre headers)
- **SHOULD** soportar ordenamiento configurable (`sortBy`, `sortOrder`)
- **SHOULD** usar cursor-based para tablas > 1M registros con offsets grandes
- **SHOULD** cachear COUNT queries cuando sea posible
- **SHOULD** documentar parámetros de paginación en OpenAPI

### MAY (Opcional)

- **MAY** soportar búsqueda full-text con paginación
- **MAY** implementar prefetching en cursor pagination
- **MAY** retornar hint de "estimated total" para performance

### MUST NOT (Prohibido)

- **MUST NOT** retornar colecciones sin paginar si pueden crecer
- **MUST NOT** permitir `pageSize` ilimitado
- **MUST NOT** usar offset pagination para scroll infinito (usar cursor)
- **MUST NOT** permitir `pageSize` > 100 (riesgo de timeout)
- **MUST NOT** hacer COUNT en cada request sin cache para tablas gigantes

---

## Referencias

- [Lineamiento: APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md)
- Estándares relacionados:
  - [Estándares REST](api-rest-standards.md)
  - [Documentación OpenAPI](openapi-specification.md)
- Especificaciones:
  - [RFC 8288: Web Linking](https://tools.ietf.org/html/rfc8288)
  - [GraphQL Cursor Connections](https://relay.dev/graphql/connections.htm)
  - [Postgres Performance: Pagination](https://www.postgresql.org/docs/current/queries-limit.html)
