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
// DTO resultado paginado
public record PagedResult<T>
{
    public T[] Items { get; init; } = Array.Empty<T>();
    public int Page { get; init; }
    public int PageSize { get; init; }
    public int TotalCount { get; init; }
    public int TotalPages => (int)Math.Ceiling((double)TotalCount / PageSize);
    public bool HasPreviousPage => Page > 1;
    public bool HasNextPage => Page < TotalPages;
    public PaginationLinks? Links { get; init; }
}

public record PaginationLinks
{
    public string? First { get; init; }
    public string? Previous { get; init; }
    public string? Next { get; init; }
    public string? Last { get; init; }
}
```

```csharp
// Controller
[HttpGet]
[ProducesResponseType(typeof(PagedResult<CustomerDto>), StatusCodes.Status200OK)]
public async Task<ActionResult<PagedResult<CustomerDto>>> GetAll(
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 20,
    [FromQuery] string? sortBy = null,
    [FromQuery] string sortOrder = "asc")
{
    if (page < 1) page = 1;
    if (pageSize < 1 || pageSize > 100) pageSize = 20;

    var result = await _customerService.GetPagedAsync(page, pageSize, sortBy, sortOrder);

    result = result with
    {
        Links = new PaginationLinks
        {
            First    = Url.Action(nameof(GetAll), new { page = 1, pageSize }),
            Previous = result.HasPreviousPage
                ? Url.Action(nameof(GetAll), new { page = page - 1, pageSize }) : null,
            Next     = result.HasNextPage
                ? Url.Action(nameof(GetAll), new { page = page + 1, pageSize }) : null,
            Last     = Url.Action(nameof(GetAll), new { page = result.TotalPages, pageSize })
        }
    };

    Response.Headers.Append("X-Total-Count", result.TotalCount.ToString());
    Response.Headers.Append("X-Page", result.Page.ToString());
    Response.Headers.Append("X-Page-Size", result.PageSize.ToString());

    return Ok(result);
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
        .ProjectTo<CustomerDto>(_mapper.ConfigurationProvider)
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
public record CursorPagedResult<T>
{
    public T[] Items { get; init; } = Array.Empty<T>();
    public string? NextCursor { get; init; }
    public string? PreviousCursor { get; init; }
    public bool HasMore { get; init; }
}

[HttpGet("feed")]
public async Task<ActionResult<CursorPagedResult<EventDto>>> GetFeed(
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
        .ProjectTo<EventDto>(_mapper.ConfigurationProvider)
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

    return Ok(new CursorPagedResult<EventDto>
    {
        Items = resultItems, NextCursor = nextCursor, HasMore = hasMore
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
- **MUST** incluir metadata de paginación en la respuesta (`total`, `page`, `pageSize`, `totalPages`)
- **MUST** implementar un `pageSize` máximo y forzarlo si el cliente envía un valor mayor
- **MUST** retornar `400` si los parámetros de paginación son inválidos (negativos, no numéricos)

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir links HATEOAS de paginación (`first`, `previous`, `next`, `last`)
- **SHOULD** exponer `X-Total-Count` como header de respuesta
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
- [Estándares REST](./rest-standards.md) — Base HTTP y status codes
- [Contratos de APIs](./api-contracts.md) — DTOs y validación
