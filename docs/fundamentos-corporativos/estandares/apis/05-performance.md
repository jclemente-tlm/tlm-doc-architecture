---
id: performance
sidebar_position: 5
title: Performance de APIs
description: Mejores prácticas para optimización de performance en APIs REST
---

## ⚡ Optimización de performance

### Paginación eficiente

```csharp
public class PagedQuery
{
    [Range(1, int.MaxValue)]
    public int Page { get; set; } = 1;

    [Range(1, 100)]  // Límite máximo por página
    public int Limit { get; set; } = 20;

    public string Sort { get; set; } = "id";
    public string Order { get; set; } = "asc";
}

[HttpGet]
public async Task<ActionResult<PagedResponse<UserDto>>> GetUsers(
    [FromQuery] PagedQuery query)
{
    // Usar skip/take para paginación eficiente
    var users = await _context.Users
        .OrderBy(u => u.Id)
        .Skip((query.Page - 1) * query.Limit)
        .Take(query.Limit)
        .Select(u => new UserDto
        {
            Id = u.Id,
            Name = u.Name,
            Email = u.Email
        })
        .ToListAsync();

    var total = await _context.Users.CountAsync();

    return Ok(new PagedResponse<UserDto>
    {
        Data = users,
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
    });
}
```

### Caching estratégico

```csharp
public class UserService
{
    private readonly IMemoryCache _cache;
    private readonly IUserRepository _repository;

    public UserService(IMemoryCache cache, IUserRepository repository)
    {
        _cache = cache;
        _repository = repository;
    }

    public async Task<UserDto> GetUserAsync(int id)
    {
        var cacheKey = $"user_{id}";

        if (_cache.TryGetValue(cacheKey, out UserDto cachedUser))
            return cachedUser;

        var user = await _repository.GetUserAsync(id);
        if (user == null) return null;

        var userDto = _mapper.Map<UserDto>(user);

        // Cache por 15 minutos
        _cache.Set(cacheKey, userDto, TimeSpan.FromMinutes(15));

        return userDto;
    }

    public async Task InvalidateUserCacheAsync(int id)
    {
        var cacheKey = $"user_{id}";
        _cache.Remove(cacheKey);
    }
}

// Controller con Response Caching
[HttpGet("{id}")]
[ResponseCache(Duration = 300, VaryByQueryKeys = new[] { "id" })]
public async Task<ActionResult<UserDto>> GetUser(int id)
{
    var user = await _userService.GetUserAsync(id);
    if (user == null) return NotFound();

    // Agregar ETag para cache del cliente
    var etag = GenerateETag(user);
    Response.Headers.ETag = etag;

    if (Request.Headers.IfNoneMatch.Contains(etag))
        return StatusCode(304); // Not Modified

    return Ok(user);
}
```

### Compresión de respuestas

```csharp
// Program.cs
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
    options.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(new[]
    {
        "application/json",
        "application/xml"
    });
});

builder.Services.Configure<BrotliCompressionProviderOptions>(options =>
{
    options.Level = CompressionLevel.Optimal;
});

var app = builder.Build();
app.UseResponseCompression();
```

### Async/await patterns

```csharp
// ✅ CORRECTO - Patrón async eficiente
public async Task<ActionResult<IEnumerable<UserDto>>> GetUsersWithOrdersAsync()
{
    // Ejecutar consultas en paralelo
    var usersTask = _context.Users.ToListAsync();
    var ordersTask = _context.Orders.ToListAsync();

    await Task.WhenAll(usersTask, ordersTask);

    var users = usersTask.Result;
    var orders = ordersTask.Result;

    // Procesar resultados...
    return Ok(ProcessUsersAndOrders(users, orders));
}

// ❌ INCORRECTO - Bloqueo del hilo
public async Task<ActionResult<UserDto>> GetUserBadExample(int id)
{
    var user = _userService.GetUserAsync(id).Result; // Bloquea
    return Ok(user);
}

// ❌ INCORRECTO - Consultas secuenciales innecesarias
public async Task<ActionResult<UserDto>> GetUserSequential(int id)
{
    var user = await _userService.GetUserAsync(id);
    var orders = await _orderService.GetUserOrdersAsync(id); // Podría ser paralelo
    var profile = await _profileService.GetUserProfileAsync(id);

    return Ok(new { user, orders, profile });
}
```

### Rate limiting

```csharp
// Program.cs
builder.Services.AddMemoryCache();
builder.Services.Configure<IpRateLimitOptions>(options =>
{
    options.EnableEndpointRateLimiting = true;
    options.StackBlockedRequests = false;
    options.HttpStatusCode = 429;
    options.RealIpHeader = "X-Real-IP";
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
            Endpoint = "POST:/api/*/users",
            Period = "1h",
            Limit = 10
        }
    };
});

builder.Services.AddSingleton<IIpPolicyStore, MemoryCacheIpPolicyStore>();
builder.Services.AddSingleton<IRateLimitCounterStore, MemoryCacheRateLimitCounterStore>();
builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();
builder.Services.AddSingleton<IProcessingStrategy, AsyncKeyLockProcessingStrategy>();

var app = builder.Build();
app.UseIpRateLimiting();
```

## 📋 Checklist de performance

### Pre-deployment

- [ ] **Paginación**: Implementada en endpoints de listado
- [ ] **Caching**: Configurado para datos frecuentemente consultados
- [ ] **Compresión**: Habilitada para responses JSON/XML
- [ ] **Async/await**: Usado consistentemente sin bloqueos
- [ ] **Database queries**: Optimizadas con índices apropiados
- [ ] **N+1 queries**: Identificadas y resueltas
- [ ] **Response size**: Minimizado con DTOs específicos
- [ ] **Rate limiting**: Configurado por tipo de endpoint

## 📖 Referencias

### ADRs relacionados

- [ADR-011: Cache distribuido](/docs/decisiones-de-arquitectura/adr-011-cache-distribuido)

### Recursos externos

- [ASP.NET Core Performance Best Practices](https://docs.microsoft.com/en-us/aspnet/core/performance/performance-best-practices)
- [HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
