---
id: rate-limiting-pagination
sidebar_position: 8
title: Rate Limiting y Paginación
description: Rate limiting con AspNetCoreRateLimit, paginación cursor-based y offset-based, headers RFC 6585 y Redis distribuido
---

# Estándar Técnico — Rate Limiting y Paginación

---

## 1. Propósito

Proteger APIs de abuso mediante rate limiting con AspNetCoreRateLimit, Redis distribuido, headers RFC 6585 (429 Too Many Requests), y paginación eficiente con cursor-based para datasets grandes y offset-based para casos simples.

---

## 2. Alcance

**Aplica a:**

- APIs REST públicas (rate limits estrictos)
- APIs privadas (rate limits permisivos)
- Endpoints que retornan colecciones
- Protección contra DDoS y abuso
- Consumo justo de recursos

**No aplica a:**

- Endpoints internos de salud (`/health`)
- Endpoints de métricas (`/metrics`)
- WebSockets (usar throttling diferente)

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología          | Versión mínima | Observaciones                     |
| ----------------- | ------------------- | -------------- | --------------------------------- |
| **Rate Limiting** | AspNetCoreRateLimit | 5.0+           | Middleware rate limiting          |
| **Cache**         | Redis               | 7.0+           | Almacén distribuido de contadores |
| **Cliente Redis** | StackExchange.Redis | 2.6+           | Cliente .NET para Redis           |
| **Paginación**    | PagedList.Core      | 1.17+          | Helper paginación offset          |
| **Headers**       | RFC 6585            | -              | Status 429 Too Many Requests      |
| **Headers**       | RFC 8288            | -              | Link header para paginación       |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Rate Limiting

- [ ] Rate limits por IP para APIs públicas
- [ ] Rate limits por API key/cliente para APIs autenticadas
- [ ] Redis distribuido para contadores (no in-memory)
- [ ] Headers de rate limit en responses (X-RateLimit-\*)
- [ ] Status code 429 Too Many Requests cuando se excede
- [ ] Header `Retry-After` con segundos para reintentar
- [ ] Diferentes límites por endpoint (lectura vs escritura)
- [ ] Whitelist de IPs corporativas

#### Límites Estándar

- **APIs públicas sin auth:** 100 req/min por IP
- **APIs autenticadas:** 1000 req/min por API key
- **Endpoints de escritura:** 50% del límite de lectura
- **Burst allowance:** 20% adicional por ventana corta

### Paginación

- [ ] Paginación obligatoria en endpoints de colecciones
- [ ] Límite máximo de resultados: 100 items por página
- [ ] Default page size: 20 items
- [ ] Query params: `page` y `pageSize` (offset) o `cursor` y `limit` (cursor-based)
- [ ] Metadata en response: `totalCount`, `page`, `pageSize`, `hasNextPage`
- [ ] Link header (RFC 8288) con `first`, `prev`, `next`, `last`
- [ ] Cursor-based para datasets grandes (>10k registros)
- [ ] Offset-based para datasets pequeños (<10k registros)

### Headers Estándar

#### Rate Limiting (GitHub style)

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1640995200
X-RateLimit-Used: 13
Retry-After: 3600
```

#### Paginación (Link header RFC 8288)

```http
Link: <https://api.talma.com/users?page=1>; rel="first",
      <https://api.talma.com/users?page=2>; rel="prev",
      <https://api.talma.com/users?page=4>; rel="next",
      <https://api.talma.com/users?page=10>; rel="last"
```

---

## 5. Prohibiciones

- ❌ Rate limiting in-memory en producción (no escala)
- ❌ Colecciones sin paginación
- ❌ Page size >100 items
- ❌ Omitir headers de rate limit
- ❌ 500 Internal Server Error cuando se excede rate limit (usar 429)
- ❌ Offset-based para datasets muy grandes (performance)
- ❌ Paginación sin metadata de total count

---

## 6. Configuración Mínima

### Rate Limiting con AspNetCoreRateLimit

```csharp
// Program.cs
using AspNetCoreRateLimit;

var builder = WebApplication.CreateBuilder(args);

// Rate limiting configuration
builder.Services.AddMemoryCache();

// Redis distribuido
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
    options.InstanceName = "RateLimit_";
});

builder.Services.Configure<IpRateLimitOptions>(options =>
{
    options.EnableEndpointRateLimiting = true;
    options.StackBlockedRequests = false;
    options.HttpStatusCode = 429;
    options.RealIpHeader = "X-Real-IP";
    options.ClientIdHeader = "X-ClientId";

    // Reglas globales
    options.GeneralRules = new List<RateLimitRule>
    {
        new RateLimitRule
        {
            Endpoint = "*",
            Period = "1m",
            Limit = 100
        },
        new RateLimitRule
        {
            Endpoint = "GET:/api/*",
            Period = "1m",
            Limit = 1000
        },
        new RateLimitRule
        {
            Endpoint = "POST:/api/*",
            Period = "1m",
            Limit = 50
        }
    };
});

// Whitelist IPs corporativas
builder.Services.Configure<IpRateLimitPolicies>(options =>
{
    options.IpWhitelist = new List<string>
    {
        "10.0.0.0/8",      // Red interna
        "172.16.0.0/12",   // VPN
        "192.168.0.0/16"   // Corporativo
    };
});

builder.Services.AddSingleton<IIpPolicyStore, DistributedCacheIpPolicyStore>();
builder.Services.AddSingleton<IRateLimitCounterStore, DistributedCacheRateLimitCounterStore>();
builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();
builder.Services.AddSingleton<IProcessingStrategy, AsyncKeyLockProcessingStrategy>();

var app = builder.Build();

// Middleware
app.UseIpRateLimiting();
app.MapControllers();
app.Run();
```

```json
// appsettings.json
{
  "ConnectionStrings": {
    "Redis": "localhost:6379,ssl=false,abortConnect=false"
  },
  "IpRateLimiting": {
    "EnableEndpointRateLimiting": true,
    "StackBlockedRequests": false,
    "RealIpHeader": "X-Real-IP",
    "HttpStatusCode": 429,
    "GeneralRules": [
      {
        "Endpoint": "*",
        "Period": "1m",
        "Limit": 100
      }
    ]
  }
}
```

### Paginación Offset-based

```csharp
// DTOs
public record PagedRequest
{
    [Range(1, int.MaxValue)]
    public int Page { get; init; } = 1;

    [Range(1, 100)]
    public int PageSize { get; init; } = 20;
}

public record PagedResult<T>
{
    public IEnumerable<T> Items { get; init; }
    public int Page { get; init; }
    public int PageSize { get; init; }
    public int TotalCount { get; init; }
    public int TotalPages { get; init; }
    public bool HasPreviousPage => Page > 1;
    public bool HasNextPage => Page < TotalPages;
}

// Controller
[HttpGet]
[ProducesResponseType(typeof(PagedResult<UserDto>), StatusCodes.Status200OK)]
public async Task<IActionResult> GetUsers([FromQuery] PagedRequest request)
{
    var totalCount = await _service.CountAsync();
    var users = await _service
        .GetPagedAsync(request.Page, request.PageSize);

    var result = new PagedResult<UserDto>
    {
        Items = users,
        Page = request.Page,
        PageSize = request.PageSize,
        TotalCount = totalCount,
        TotalPages = (int)Math.Ceiling(totalCount / (double)request.PageSize)
    };

    // Link header
    Response.Headers["Link"] = GenerateLinkHeader(result, Request);

    return Ok(result);
}

private string GenerateLinkHeader<T>(PagedResult<T> result, HttpRequest request)
{
    var baseUrl = $"{request.Scheme}://{request.Host}{request.Path}";
    var links = new List<string>();

    links.Add($"<{baseUrl}?page=1&pageSize={result.PageSize}>; rel=\"first\"");

    if (result.HasPreviousPage)
        links.Add($"<{baseUrl}?page={result.Page - 1}&pageSize={result.PageSize}>; rel=\"prev\"");

    if (result.HasNextPage)
        links.Add($"<{baseUrl}?page={result.Page + 1}&pageSize={result.PageSize}>; rel=\"next\"");

    links.Add($"<{baseUrl}?page={result.TotalPages}&pageSize={result.PageSize}>; rel=\"last\"");

    return string.Join(", ", links);
}
```

### Paginación Cursor-based

```csharp
// DTOs
public record CursorRequest
{
    public string? Cursor { get; init; }

    [Range(1, 100)]
    public int Limit { get; init; } = 20;
}

public record CursorResult<T>
{
    public IEnumerable<T> Items { get; init; }
    public string? NextCursor { get; init; }
    public string? PreviousCursor { get; init; }
    public bool HasMore { get; init; }
}

// Controller
[HttpGet("cursor")]
public async Task<IActionResult> GetUsersCursor([FromQuery] CursorRequest request)
{
    var decodedCursor = request.Cursor != null
        ? DecodeCursor(request.Cursor)
        : DateTime.MinValue;

    var users = await _service
        .GetByCursorAsync(decodedCursor, request.Limit + 1); // +1 para hasMore

    var hasMore = users.Count() > request.Limit;
    var items = users.Take(request.Limit).ToList();

    var result = new CursorResult<UserDto>
    {
        Items = items,
        NextCursor = hasMore ? EncodeCursor(items.Last().CreatedAt) : null,
        HasMore = hasMore
    };

    return Ok(result);
}

private string EncodeCursor(DateTime timestamp)
{
    var bytes = Encoding.UTF8.GetBytes(timestamp.ToString("O"));
    return Convert.ToBase64String(bytes);
}

private DateTime DecodeCursor(string cursor)
{
    var bytes = Convert.FromBase64String(cursor);
    var timestamp = Encoding.UTF8.GetString(bytes);
    return DateTime.Parse(timestamp);
}
```

---

## 7. Ejemplos

### Response con headers de rate limiting

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1640995200
X-RateLimit-Used: 13

{
  "items": [...],
  "page": 1,
  "pageSize": 20,
  "totalCount": 150,
  "totalPages": 8
}
```

### Response 429 Too Many Requests

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995260

{
  "type": "https://docs.talma.com/errors/rate-limit",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Límite de 100 requests por minuto excedido. Reintentar en 60 segundos.",
  "traceId": "00-abc123-def456-00"
}
```

### Paginación offset-based

```bash
# Request
curl "https://api.talma.com/api/v1/users?page=3&pageSize=20"

# Response
HTTP/1.1 200 OK
Link: <https://api.talma.com/api/v1/users?page=1&pageSize=20>; rel="first",
      <https://api.talma.com/api/v1/users?page=2&pageSize=20>; rel="prev",
      <https://api.talma.com/api/v1/users?page=4&pageSize=20>; rel="next",
      <https://api.talma.com/api/v1/users?page=8&pageSize=20>; rel="last"

{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "juan.perez@talma.com",
      "firstName": "Juan",
      "lastName": "Pérez"
    }
  ],
  "page": 3,
  "pageSize": 20,
  "totalCount": 150,
  "totalPages": 8,
  "hasPreviousPage": true,
  "hasNextPage": true
}
```

### Paginación cursor-based

```bash
# Primera página
curl "https://api.talma.com/api/v1/users/cursor?limit=20"

{
  "items": [...],
  "nextCursor": "MjAyNC0wMS0xNVQxMDozMDowMFo=",
  "hasMore": true
}

# Siguiente página
curl "https://api.talma.com/api/v1/users/cursor?cursor=MjAyNC0wMS0xNVQxMDozMDowMFo=&limit=20"

{
  "items": [...],
  "nextCursor": "MjAyNC0wMS0xNlQwODoyMDowMFo=",
  "previousCursor": "MjAyNC0wMS0xNVQxMDozMDowMFo=",
  "hasMore": true
}
```

---

## 8. Validación y Auditoría

```bash
# Verificar rate limiting
for i in {1..150}; do
  curl -w "\nStatus: %{http_code}\n" https://api.talma.com/api/v1/users
done

# Verificar headers de rate limit
curl -I https://api.talma.com/api/v1/users | grep -i "x-ratelimit"

# Verificar paginación
curl -I "https://api.talma.com/api/v1/users?page=1&pageSize=20" | grep -i "link"

# Load testing con Artillery
artillery quick --count 200 --num 10 https://api.talma.com/api/v1/users

# Monitorear Redis counters
redis-cli --scan --pattern "RateLimit_*"
redis-cli get "RateLimit_127.0.0.1_*"

# Validar metadata de paginación
curl "https://api.talma.com/api/v1/users?page=1" | jq '{totalCount, page, pageSize, totalPages}'
```

**Métricas de cumplimiento:**

| Métrica                        | Umbral        | Verificación           |
| ------------------------------ | ------------- | ---------------------- |
| Requests bloqueados (429)      | <1% legítimos | Logs de rate limit     |
| Tiempo respuesta paginación    | <200ms        | Performance monitoring |
| Headers rate limit presentes   | 100%          | Tests automatizados    |
| Page size máximo respetado     | 100 items     | Validación runtime     |
| Redis availability             | 99.9%         | Health checks          |
| Cursor-based para >10k records | 100%          | Code review            |

---

## 9. Referencias

- [RFC 6585 - 429 Too Many Requests](https://datatracker.ietf.org/doc/html/rfc6585)
- [RFC 8288 - Web Linking (Link header)](https://datatracker.ietf.org/doc/html/rfc8288)
- [AspNetCoreRateLimit](https://github.com/stefanprodan/AspNetCoreRateLimit)
- [GitHub REST API Rate Limiting](https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api)
- [Stripe API Pagination](https://stripe.com/docs/api/pagination)
- [Twitter API Cursor-based Pagination](https://developer.twitter.com/en/docs/twitter-api/pagination)
- [Google API Design - List Pagination](https://cloud.google.com/apis/design/design_patterns#list_pagination)
- [Redis Distributed Rate Limiting](https://redis.io/docs/manual/patterns/distributed-locks/)
