---
id: performance
sidebar_position: 5
title: Performance de APIs
description: Estándar técnico obligatorio para optimizar el rendimiento de APIs REST con paginación, caching, compresión, async y rate limiting
---

# Estándar Técnico — Performance de APIs

---

## 1. Propósito
Garantizar SLA ≤1200ms p95 mediante paginación con límites (max 100 items), caching estratificado (memoria + Redis), compresión Brotli/Gzip, operaciones asíncronas y rate limiting anti-abuso.

---

## 2. Alcance

**Aplica a:**
- APIs REST públicas con alto tráfico (>1000 req/min)
- Endpoints que consultan BD o servicios externos
- APIs de reporteía con grandes volúmenes

**No aplica a:**
- Webhooks internos de bajo tráfico
- POCs sin SLA definido
- Endpoints health check simplificados

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Paginación** | ASP.NET Core Paging | 8.0+ | Skip/Take con EF Core |
| **Cache L1** | IMemoryCache | 8.0+ | Cache en memoria (hot paths) |
| **Cache L2** | IDistributedCache + Redis | 8.0+ | Cache distribuido escalable |
| **Compresión** | Brotli (prioridad), Gzip | Nativo | Reduce tamaño 70-80% |
| **Async** | async/await, Task, ValueTask | C# 12+ | No bloquea threads |
| **Rate Limiting** | AspNetCoreRateLimit | 5.0+ | Protección anti-abuso |
| **Monitoreo** | OpenTelemetry, Prometheus | 1.6+ | Métricas latencia/throughput |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Paginación obligatoria en colecciones (limit max 100 items)
- [ ] Cache IMemoryCache para datos hot (expiración 5-15 min)
- [ ] Cache Redis para datos compartidos entre instancias
- [ ] Compresión Brotli habilitada (fallback Gzip)
- [ ] Operaciones I/O asíncronas (async/await)
- [ ] Rate limiting: 100 req/min por IP
- [ ] Query optimization con EF Core (evitar N+1)
- [ ] DTOs ligeros (NO lazy loading en responses)
- [ ] Métricas de latencia p50/p95/p99 monitoreadas
- [ ] Response time target: p95 < 200ms
- [ ] Cache-Control headers configurados
- [ ] ETags para recursos cacheables

---

## 5. Prohibiciones

- ❌ Retornar colecciones sin paginación
- ❌ Operaciones síncronas en I/O (usar async/await)
- ❌ Lazy loading de relaciones en APIs
- ❌ Cache sin expiración (TTL obligatorio)
- ❌ Consultas N+1 (usar Include/ThenInclude)
- ❌ Responses sin compresión (>1KB sin comprimir)

---

## 6. Configuración Mínima

```csharp
// Program.cs
using Microsoft.AspNetCore.ResponseCompression;

// Compresión Brotli/Gzip
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
});

// Cache
builder.Services.AddMemoryCache();
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
    options.InstanceName = "TalmaAPI_";
});

var app = builder.Build();
app.UseResponseCompression();
```

```csharp
// Controller con paginación y cache
[HttpGet]
public async Task<IActionResult> GetUsers([FromQuery] PagedQuery query)
{
    var cacheKey = $"users_page{query.Page}_limit{query.Limit}";
    
    if (!_cache.TryGetValue(cacheKey, out PagedResponse<UserDto> result))
    {
        var users = await _context.Users
            .Skip((query.Page - 1) * query.Limit)
            .Take(query.Limit)
            .ToListAsync();
        
        var total = await _context.Users.CountAsync();
        
        result = new PagedResponse<UserDto>
        {
            Data = _mapper.Map<List<UserDto>>(users),
            Meta = new MetaData
            {
                Pagination = new PaginationMeta
                {
                    Page = query.Page,
                    PerPage = query.Limit,
                    Total = total,
                    TotalPages = (int)Math.Ceiling(total / (double)query.Limit)
                }
            }
        };
        
        _cache.Set(cacheKey, result, TimeSpan.FromMinutes(10));
    }
    
    return Ok(result);
}

public class PagedQuery
{
    [Range(1, int.MaxValue)]
    public int Page { get; set; } = 1;
    
    [Range(1, 100)]
    public int Limit { get; set; } = 20;
}
```

---

## 7. Validación

```bash
# Verificar paginación
curl "https://api.talma.com/api/v1/users?page=1&limit=20"

# Verificar compresión
curl -H "Accept-Encoding: br" -I https://api.talma.com/api/v1/users
# Header: Content-Encoding: br

# Verificar cache headers
curl -I https://api.talma.com/api/v1/users
# Header: Cache-Control: public, max-age=600

# Benchmark performance
ab -n 1000 -c 10 https://api.talma.com/api/v1/users

# Tests de performance
dotnet test --filter Category=Performance
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Latencia p95 | < 200ms | Prometheus `http_request_duration_seconds` |
| Compresión habilitada | 100% | Header `Content-Encoding: br` |
| Colecciones con paginación | 100% | Verificar parámetros `page`/`limit` |
| Cache hit rate | > 70% | Redis MONITOR |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Diseño REST](./01-diseno-rest.md)
- [Monitoreo y Métricas](../observabilidad/02-monitoreo-metricas.md)
- [ASP.NET Core Performance Best Practices](https://learn.microsoft.com/aspnet/core/performance/performance-best-practices)
- [EF Core Performance](https://learn.microsoft.com/ef/core/performance/)
