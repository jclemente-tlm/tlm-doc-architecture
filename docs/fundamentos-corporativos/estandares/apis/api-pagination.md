---
id: api-pagination
sidebar_position: 4
title: Paginación de APIs
description: Estrategias de paginación offset-based y cursor-based para endpoints que retornan colecciones.
tags: [apis, rest, paginacion, cursor, offset]
---

# Paginación de APIs

## Contexto

Este estándar define cómo paginar colecciones grandes para mejorar performance y experiencia de usuario. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Cuándo aplicar:** Todo endpoint que retorne una colección de recursos.

---

## Stack Tecnológico

| Componente        | Tecnología       | Versión | Uso                  |
| ----------------- | ---------------- | ------- | -------------------- |
| **Framework**     | ASP.NET Core     | 8.0+    | Construcción de APIs |
| **ORM**           | Entity Framework | 8.0+    | Consultas paginadas  |
| **Serialización** | System.Text.Json | 8.0+    | JSON serialization   |

---

## Estrategias de Paginación

| Estrategia       | Uso                           | Pros                  | Contras                    |
| ---------------- | ----------------------------- | --------------------- | -------------------------- |
| **Offset/Limit** | Páginas tradicionales, saltos | Simple, navegable     | Performance O(n) en offset |
| **Cursor-based** | Feeds infinitos, tiempo real  | Performance constante | No permite saltar páginas  |
| **Keyset**       | Ordenamiento por campo único  | Performance O(1)      | Requiere índice            |

---

## Paginación Offset-based

```csharp
// Modelo interno del servicio — NO es la respuesta API directa
// El controller lo mapea a ApiResponse<T[]> con meta.pagination
public record PagedResult<T>
{
    public T[] Items { get; init; } = Array.Empty<T>();
    public int Page { get; init; }
    public int PageSize { get; init; }
    public int TotalCount { get; init; }
    public int TotalPages => (int)Math.Ceiling((double)TotalCount / PageSize);
    public bool HasPreviousPage => Page > 1;
    public bool HasNextPage => Page < TotalPages;
}
```

```csharp
// Controller — retorna ApiResponse<CustomerDto[]> con paginación en meta
[HttpGet]
[ProducesResponseType(typeof(ApiResponse<CustomerDto[]>), StatusCodes.Status200OK)]
public async Task<ActionResult<ApiResponse<CustomerDto[]>>> GetAll(
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 20,
    [FromQuery] string? sortBy = null,
    [FromQuery] string sortOrder = "asc")
{
    if (page < 1) page = 1;
    if (pageSize < 1 || pageSize > 100) pageSize = 20;

    var result = await _customerService.GetPagedAsync(page, pageSize, sortBy, sortOrder);

    return Ok(new ApiResponse<CustomerDto[]>
    {
        Status = "success",
        Data   = result.Items,
        Meta   = new MetaData
        {
            TraceId    = HttpContext.TraceIdentifier,
            Pagination = new PaginationMeta
            {
                Page       = result.Page,
                Size       = result.PageSize,
                Total      = result.TotalCount,
                TotalPages = result.TotalPages
            },
            Links = new Dictionary<string, string>
            {
                ["first"]    = Url.Action(nameof(GetAll), new { page = 1, pageSize })!,
                ["previous"] = result.HasPreviousPage
                    ? Url.Action(nameof(GetAll), new { page = page - 1, pageSize })! : null!,
                ["next"]     = result.HasNextPage
                    ? Url.Action(nameof(GetAll), new { page = page + 1, pageSize })! : null!,
                ["last"]     = Url.Action(nameof(GetAll), new { page = result.TotalPages, pageSize })!
            }.Where(x => x.Value != null).ToDictionary(x => x.Key, x => x.Value)
        }
    });
}
```

```csharp
// Servicio con Entity Framework
public async Task<PagedResult<CustomerDto>> GetPagedAsync(
    int page, int pageSize, string? sortBy, string? sortOrder)
{
    var query = _context.Customers.AsQueryable();

    query = sortBy?.ToLower() switch
    {
        "name"      => sortOrder == "desc"
            ? query.OrderByDescending(c => c.Name)      : query.OrderBy(c => c.Name),
        "createdat" => sortOrder == "desc"
            ? query.OrderByDescending(c => c.CreatedAt) : query.OrderBy(c => c.CreatedAt),
        _           => query.OrderBy(c => c.Id)
    };

    var totalCount = await query.CountAsync();
    var items = await query
        .Skip((page - 1) * pageSize)
        .Take(pageSize)
        .ProjectToType<CustomerDto>()
        .ToArrayAsync();

    return new PagedResult<CustomerDto>
    {
        Items = items, Page = page, PageSize = pageSize, TotalCount = totalCount
    };
}
```

---

## Paginación Cursor-based

Usar para feeds infinitos (timelines, streams de eventos, notificaciones).

```csharp
[HttpGet("feed")]
public async Task<ActionResult<ApiResponse<EventDto[]>>> GetFeed(
    [FromQuery] string? cursor = null,
    [FromQuery] int limit = 20)
{
    DateTime? afterTimestamp = null;
    Guid? afterId = null;

    if (!string.IsNullOrEmpty(cursor))
    {
        try
        {
            var decoded = Encoding.UTF8.GetString(Convert.FromBase64String(cursor));
            var parts = decoded.Split('|');
            afterTimestamp = DateTime.Parse(parts[0]);
            afterId = Guid.Parse(parts[1]);
        }
        catch
        {
            return BadRequest("Cursor inválido");
        }
    }

    var query = _context.Events.AsQueryable();

    if (afterTimestamp.HasValue && afterId.HasValue)
    {
        query = query.Where(e =>
            e.CreatedAt < afterTimestamp.Value ||
            (e.CreatedAt == afterTimestamp.Value && e.Id.CompareTo(afterId.Value) < 0));
    }

    var items = await query
        .OrderByDescending(e => e.CreatedAt)
        .ThenByDescending(e => e.Id)
        .Take(limit + 1) // +1 para detectar si hay más páginas
        .ProjectToType<EventDto>()
        .ToArrayAsync();

    var hasMore = items.Length > limit;
    var resultItems = hasMore ? items[..limit] : items;

    string? nextCursor = null;
    if (hasMore && resultItems.Length > 0)
    {
        var last = resultItems[^1];
        var cursorData = $"{last.CreatedAt:O}|{last.Id}";
        nextCursor = Convert.ToBase64String(Encoding.UTF8.GetBytes(cursorData));
    }

    return Ok(new ApiResponse<EventDto[]>
    {
        Status = "success",
        Data   = resultItems,
        Meta   = new MetaData
        {
            TraceId = HttpContext.TraceIdentifier,
            Extra   = new { hasMore, nextCursor }
        }
    });
}
```

---

## Beneficios en Práctica

| Sin paginación                  | Con paginación                  |
| ------------------------------- | ------------------------------- |
| Respuestas de cientos de MB     | Payloads acotados y predecibles |
| Timeouts en colecciones grandes | Latencia constante              |
| OOM en el servidor              | Uso de memoria controlado       |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** paginar todo endpoint que retorne colecciones (límite máximo: 100 items por página)
- **MUST** incluir metadata de paginación en `meta.pagination` del wrapper (`total`, `page`, `size`, `totalPages`)
- **MUST** implementar un `pageSize` máximo y forzarlo si el cliente envía un valor mayor
- **MUST** retornar `400` si los parámetros de paginación son inválidos (negativos, no numéricos)

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir links de navegación en `meta.links` (`first`, `previous`, `next`, `last`)
- **SHOULD** usar cursor-based pagination para feeds infinitos o colecciones en tiempo real
- **SHOULD** soportar ordenamiento (`sortBy`, `sortOrder`) en endpoints paginados

### MAY (Opcional)

- **MAY** soportar filtrado adicional (`filter`, `search`) en colecciones
- **MAY** implementar keyset pagination para ordenamiento por campo único con alto volumen

### MUST NOT (Prohibido)

- **MUST NOT** retornar colecciones sin paginar en endpoints de producción
- **MUST NOT** permitir `pageSize` mayor a 100 (riesgo de OOM y timeouts)

---

## Referencias

- [RFC 8288 - Web Linking](https://www.rfc-editor.org/rfc/rfc8288.html) — Links de paginación HATEOAS
- [ASP.NET Core Web APIs](https://learn.microsoft.com/aspnet/core/web-api/) — Documentación oficial
- [Cursor-based Pagination](https://use-the-index-luke.com/no-offset) — Referencia técnica
- [Estándares REST](./api-rest-standards.md) — Base HTTP y status codes
- [Contratos de APIs](./api-contracts.md) — DTOs y validación
