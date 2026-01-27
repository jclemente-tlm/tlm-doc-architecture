---
id: performance
sidebar_position: 5
title: Performance de APIs
description: Estándar técnico obligatorio para optimizar el rendimiento de APIs REST con paginación, caching, compresión, async y rate limiting
---

# Performance de APIs

## 1. Propósito

Definir la configuración técnica obligatoria para optimizar el rendimiento de las APIs REST en Talma mediante:
- **Paginación eficiente** con límites y cursores
- **Caching estratégico** con IMemoryCache y Distributed Cache
- **Compresión Brotli/Gzip** para reducir tamaño de respuestas
- **Operaciones asíncronas** (async/await) para I/O-bound
- **Rate Limiting** para prevenir abuso y saturación

Garantiza SLAs de ≤200ms (p95), throughput escalable y experiencia de usuario fluida.

## 2. Alcance

### Aplica a:

- ✅ Todas las APIs REST públicas expuestas a frontend/mobile
- ✅ APIs de integración con alto tráfico (>1000 req/min)
- ✅ Endpoints que consultan datos de BD o servicios externos
- ✅ APIs de reportería con grandes volúmenes de datos

### NO aplica a:

- ❌ Webhooks internos de bajo tráfico
- ❌ POCs o demos sin SLA definido
- ❌ Scripts de administración one-time
- ❌ Endpoints de health check simplificados

## 3. Tecnologías Obligatorias

| Categoría          | Tecnología / Configuración                | Versión   | Justificación                           |
| ------------------ | ----------------------------------------- | --------- | --------------------------------------- |
| **Paginación**     | ASP.NET Core Paging                       | 8.0+      | Skip/Take eficiente con EF Core         |
| **Caching**        | `IMemoryCache` (memoria)                  | 8.0+      | Cache L1 rápido (hot paths)             |
|                    | `IDistributedCache` (Redis)               | 8.0+      | Cache distribuido escalable             |
| **Compresión**     | Brotli (prioridad), Gzip (fallback)       | Nativo    | Reduce tamaño 70-80%                    |
| **Async**          | `async/await`, `Task`, `ValueTask`        | C# 12+    | No bloquea threads de I/O               |
| **Rate Limiting**  | `AspNetCoreRateLimit`                     | 5.0+      | Protección contra abuso                 |
| **Monitoreo**      | Application Insights, Prometheus          | Latest    | Métricas de latencia/throughput         |

| **Monitoreo**      | Application Insights, Prometheus          | Latest    | Métricas de latencia/throughput         |

## 4. Configuración Técnica Obligatoria

### 4.1 Paginación con PagedQuery

```csharp
// DTOs/PagedQuery.cs
using System.ComponentModel.DataAnnotations;

public class PagedQuery
{
    [Range(1, int.MaxValue, ErrorMessage = "Page debe ser >= 1")]
    public int Page { get; set; } = 1;

    [Range(1, 100, ErrorMessage = "Limit debe estar entre 1 y 100")]
    public int Limit { get; set; } = 20;

    public string Sort { get; set; } = "id";
    
    [RegularExpression("^(asc|desc)$", ErrorMessage = "Order debe ser asc o desc")]
    public string Order { get; set; } = "asc";
}

public class PagedResponse<T>
{
    public List<T> Data { get; set; }
    public MetaData Meta { get; set; }
}

public class MetaData
{
    public PaginationMeta Pagination { get; set; }
}

public class PaginationMeta
{
    public int Page { get; set; }
    public int PerPage { get; set; }
    public int Total { get; set; }
    public int TotalPages { get; set; }
    public string NextPage { get; set; }
    public string PrevPage { get; set; }
}
```

### 4.2 Caching con IMemoryCache

```csharp
// Program.cs
builder.Services.AddMemoryCache();
builder.Services.AddDistributedMemoryCache(); // Para desarrollo
// builder.Services.AddStackExchangeRedisCache(options => { ... }); // Producción

// Services/UserService.cs
public class UserService
{
    private readonly IMemoryCache _cache;
    private readonly IDistributedCache _distributedCache;
    private readonly IUserRepository _repository;
    private readonly ILogger<UserService> _logger;

    public UserService(
        IMemoryCache cache,
        IDistributedCache distributedCache,
        IUserRepository repository,
        ILogger<UserService> logger)
    {
        _cache = cache;
        _distributedCache = distributedCache;
        _repository = repository;
        _logger = logger;
    }

    public async Task<UserDto> GetUserAsync(Guid id, CancellationToken ct)
    {
        var cacheKey = $"user:{id}";

        // ✅ Intentar desde cache L1 (memoria)
        if (_cache.TryGetValue(cacheKey, out UserDto cachedUser))
        {
            _logger.LogInformation("Cache hit (L1): {CacheKey}", cacheKey);
            return cachedUser;
        }

        // ✅ Intentar desde cache distribuido (Redis)
        var cachedBytes = await _distributedCache.GetAsync(cacheKey, ct);
        if (cachedBytes != null)
        {
            var cachedData = JsonSerializer.Deserialize<UserDto>(cachedBytes);
            
            // Poblar L1 cache
            _cache.Set(cacheKey, cachedData, TimeSpan.FromMinutes(5));
            
            _logger.LogInformation("Cache hit (L2): {CacheKey}", cacheKey);
            return cachedData;
        }

        // ✅ Cache miss - consultar BD
        _logger.LogInformation("Cache miss: {CacheKey}", cacheKey);
        var user = await _repository.GetUserByIdAsync(id, ct);
        if (user == null) return null;

        var userDto = _mapper.Map<UserDto>(user);

        // Cachear en L1 (5 min) y L2 (15 min)
        var cacheOptions = new MemoryCacheEntryOptions()
            .SetAbsoluteExpiration(TimeSpan.FromMinutes(5));
        
        _cache.Set(cacheKey, userDto, cacheOptions);

        var distributedOptions = new DistributedCacheEntryOptions()
            .SetAbsoluteExpiration(TimeSpan.FromMinutes(15));
        
        var bytes = JsonSerializer.SerializeToUtf8Bytes(userDto);
        await _distributedCache.SetAsync(cacheKey, bytes, distributedOptions, ct);

        return userDto;
    }

    public async Task InvalidateUserCacheAsync(Guid id)
    {
        var cacheKey = $"user:{id}";
        _cache.Remove(cacheKey);
        await _distributedCache.RemoveAsync(cacheKey);
        
        _logger.LogInformation("Cache invalidated: {CacheKey}", cacheKey);
    }
}
```

### 4.3 Compresión Brotli/Gzip

```csharp
// Program.cs
using Microsoft.AspNetCore.ResponseCompression;
using System.IO.Compression;

builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true; // ✅ Habilitar para HTTPS
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
    
    // ✅ Comprimir solo ciertos MIME types
    options.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(new[]
    {
        "application/json",
        "application/xml",
        "text/plain",
        "text/csv"
    });
});

// ✅ Configurar nivel de compresión
builder.Services.Configure<BrotliCompressionProviderOptions>(options =>
{
    options.Level = CompressionLevel.Fastest; // Balance velocidad/compresión
});

builder.Services.Configure<GzipCompressionProviderOptions>(options =>
{
    options.Level = CompressionLevel.Fastest;
});

var app = builder.Build();

// ✅ Middleware de compresión (antes de UseStaticFiles)
app.UseResponseCompression();
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
```

### 4.4 Async/Await Patterns

```csharp
// ✅ Controller con async/await
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;

    [HttpGet]
    public async Task<ActionResult<PagedResponse<UserDto>>> GetUsers(
        [FromQuery] PagedQuery query,
        CancellationToken ct) // ✅ Soporte para cancelación
    {
        var result = await _userService.GetPagedUsersAsync(query, ct);
        return Ok(result);
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<UserDto>> GetUser(Guid id, CancellationToken ct)
    {
        var user = await _userService.GetUserAsync(id, ct);
        
        if (user == null)
            return NotFound();
        
        return Ok(user);
    }

    [HttpPost]
    public async Task<ActionResult<UserDto>> CreateUser(
        [FromBody] CreateUserRequest request,
        CancellationToken ct)
    {
        var user = await _userService.CreateUserAsync(request, ct);
        
        return CreatedAtAction(
            nameof(GetUser),
            new { id = user.Id },
            user
        );
    }
}

// ✅ Repository con async/await y EF Core
public class UserRepository : IUserRepository
{
    private readonly AppDbContext _context;

    public async Task<List<User>> GetPagedUsersAsync(
        int skip,
        int take,
        CancellationToken ct)
    {
        return await _context.Users
            .AsNoTracking() // ✅ Optimización para consultas read-only
            .OrderBy(u => u.Id)
            .Skip(skip)
            .Take(take)
            .ToListAsync(ct);
    }

    public async Task<User> GetUserByIdAsync(Guid id, CancellationToken ct)
    {
        return await _context.Users
            .AsNoTracking()
            .FirstOrDefaultAsync(u => u.Id == id, ct);
    }
}
```

### 4.5 Rate Limiting

```csharp
// Program.cs
using AspNetCoreRateLimit;

builder.Services.AddMemoryCache();
builder.Services.Configure<IpRateLimitOptions>(builder.Configuration.GetSection("IpRateLimiting"));
builder.Services.AddInMemoryRateLimiting();
builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();

var app = builder.Build();

// ✅ Middleware de rate limiting (antes de UseAuthorization)
app.UseIpRateLimiting();

// appsettings.json
{
  "IpRateLimiting": {
    "EnableEndpointRateLimiting": true,
    "StackBlockedRequests": false,
    "RealIpHeader": "X-Real-IP",
    "ClientIdHeader": "X-ClientId",
    "HttpStatusCode": 429,
    "GeneralRules": [
      {
        "Endpoint": "*",
        "Period": "1m",
        "Limit": 60
      },
      {
        "Endpoint": "*",
        "Period": "1h",
        "Limit": 1000
      }
    ]
  }
}
```

```

## 5. Ejemplos de Implementación

### 5.1 Endpoint con Paginación y Caching

```csharp
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0")]
public class ProductsController : ControllerBase
{
    private readonly IProductService _productService;

    public ProductsController(IProductService productService)
    {
        _productService = productService;
    }

    /// <summary>
    /// Obtiene lista paginada de productos con cache
    /// </summary>
    [HttpGet]
    [ResponseCache(Duration = 60, VaryByQueryKeys = new[] { "page", "limit", "sort" })]
    public async Task<ActionResult<PagedResponse<ProductDto>>> GetProducts(
        [FromQuery] PagedQuery query,
        CancellationToken ct)
    {
        var result = await _productService.GetPagedProductsAsync(query, ct);
        
        // ✅ Agregar headers de paginación
        Response.Headers.Append("X-Total-Count", result.Meta.Pagination.Total.ToString());
        Response.Headers.Append("X-Page", result.Meta.Pagination.Page.ToString());
        Response.Headers.Append("X-Per-Page", result.Meta.Pagination.PerPage.ToString());

        return Ok(result);
    }

    /// <summary>
    /// Obtiene producto por ID (con cache)
    /// </summary>
    [HttpGet("{id:guid}")]
    [ResponseCache(Duration = 300, VaryByQueryKeys = new[] { "id" })]
    public async Task<ActionResult<ProductDto>> GetProduct(Guid id, CancellationToken ct)
    {
        var product = await _productService.GetProductAsync(id, ct);
        
        if (product == null)
            return NotFound();

        return Ok(product);
    }

    /// <summary>
    /// Actualiza producto (invalida cache)
    /// </summary>
    [HttpPut("{id:guid}")]
    public async Task<ActionResult<ProductDto>> UpdateProduct(
        Guid id,
        [FromBody] UpdateProductRequest request,
        CancellationToken ct)
    {
        var product = await _productService.UpdateProductAsync(id, request, ct);
        
        // ✅ Invalidar cache después de actualizar
        await _productService.InvalidateProductCacheAsync(id);

        return Ok(product);
    }
}
```

### 5.2 Service con Multi-Level Caching

```csharp
public class ProductService : IProductService
{
    private readonly IMemoryCache _cache;
    private readonly IDistributedCache _distributedCache;
    private readonly IProductRepository _repository;
    private readonly ILogger<ProductService> _logger;

    public async Task<PagedResponse<ProductDto>> GetPagedProductsAsync(
        PagedQuery query,
        CancellationToken ct)
    {
        var cacheKey = $"products:page:{query.Page}:limit:{query.Limit}:sort:{query.Sort}";

        // ✅ Cache L1 (memoria)
        if (_cache.TryGetValue(cacheKey, out PagedResponse<ProductDto> cached))
        {
            _logger.LogDebug("Cache hit (L1): {CacheKey}", cacheKey);
            return cached;
        }

        // ✅ Cache L2 (Redis)
        var cachedBytes = await _distributedCache.GetAsync(cacheKey, ct);
        if (cachedBytes != null)
        {
            var cachedData = JsonSerializer.Deserialize<PagedResponse<ProductDto>>(cachedBytes);
            
            _cache.Set(cacheKey, cachedData, TimeSpan.FromMinutes(2));
            _logger.LogDebug("Cache hit (L2): {CacheKey}", cacheKey);
            
            return cachedData;
        }

        // ✅ Query BD
        var skip = (query.Page - 1) * query.Limit;
        var products = await _repository.GetPagedProductsAsync(skip, query.Limit, ct);
        var total = await _repository.GetTotalCountAsync(ct);

        var result = new PagedResponse<ProductDto>
        {
            Data = _mapper.Map<List<ProductDto>>(products),
            Meta = new MetaData
            {
                Pagination = new PaginationMeta
                {
                    Page = query.Page,
                    PerPage = query.Limit,
                    Total = total,
                    TotalPages = (int)Math.Ceiling(total / (double)query.Limit),
                    NextPage = query.Page < (int)Math.Ceiling(total / (double)query.Limit)
                        ? $"/api/v1/products?page={query.Page + 1}&limit={query.Limit}"
                        : null,
                    PrevPage = query.Page > 1
                        ? $"/api/v1/products?page={query.Page - 1}&limit={query.Limit}"
                        : null
                }
            }
        };

        // ✅ Cachear en L1 (2 min) y L2 (10 min)
        _cache.Set(cacheKey, result, TimeSpan.FromMinutes(2));
        
        var bytes = JsonSerializer.SerializeToUtf8Bytes(result);
        await _distributedCache.SetAsync(
            cacheKey,
            bytes,
            new DistributedCacheEntryOptions { AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10) },
            ct
        );

        return result;
    }
}
```

### 5.3 N+1 Query Problem - Solución con EF Core

```csharp
// ❌ MAL - Consultas N+1
public async Task<List<OrderDto>> GetOrdersWithCustomersAsync()
{
    var orders = await _context.Orders.ToListAsync();

    // ❌ Por cada order, hace una query adicional (N+1)
    foreach (var order in orders)
    {
        order.Customer = await _context.Customers.FindAsync(order.CustomerId);
    }

    return _mapper.Map<List<OrderDto>>(orders);
}

// ✅ BIEN - Eager Loading con Include
public async Task<List<OrderDto>> GetOrdersWithCustomersAsync(CancellationToken ct)
{
    var orders = await _context.Orders
        .AsNoTracking()
        .Include(o => o.Customer) // ✅ JOIN en una sola query
        .Include(o => o.OrderItems)
            .ThenInclude(oi => oi.Product) // ✅ Cargar productos
        .OrderByDescending(o => o.CreatedAt)
        .ToListAsync(ct);

    return _mapper.Map<List<OrderDto>>(orders);
}

// ✅ MEJOR - Projection con Select (evita mapear entidades completas)
public async Task<List<OrderSummaryDto>> GetOrderSummariesAsync(CancellationToken ct)
{
    return await _context.Orders
        .AsNoTracking()
        .Select(o => new OrderSummaryDto
        {
            Id = o.Id,
            OrderNumber = o.OrderNumber,
            CustomerName = o.Customer.Name,
            TotalAmount = o.TotalAmount,
            ItemCount = o.OrderItems.Count,
            CreatedAt = o.CreatedAt
        })
        .OrderByDescending(o => o.CreatedAt)
        .ToListAsync(ct);
}
```

## 6. Mejores Prácticas

### 6.1 Compresión Selectiva

```csharp
// ✅ Comprimir solo respuestas grandes (>1KB)
[HttpGet]
public async Task<ActionResult<List<ProductDto>>> GetProducts([FromQuery] PagedQuery query)
{
    var products = await _productService.GetPagedProductsAsync(query);

    // ✅ Agregar header para indicar tamaño sin comprimir
    Response.Headers.Append("X-Original-Size", JsonSerializer.Serialize(products).Length.ToString());

    return Ok(products);
}
```

### 6.2 Async All the Way

```csharp
// ❌ MAL - Bloquear con .Result o .Wait()
public IActionResult GetUser(Guid id)
{
    var user = _userService.GetUserAsync(id).Result; // ❌ Deadlock potential
    return Ok(user);
}

// ✅ BIEN - Async de punta a punta
public async Task<ActionResult<UserDto>> GetUser(Guid id, CancellationToken ct)
{
    var user = await _userService.GetUserAsync(id, ct);
    return Ok(user);
}

// ✅ Usar ValueTask para hot paths
public async ValueTask<UserDto> GetUserAsync(Guid id, CancellationToken ct)
{
    // ValueTask evita allocations si el resultado ya está disponible
    if (_cache.TryGetValue(id, out UserDto cached))
        return cached;

    return await _repository.GetUserByIdAsync(id, ct);
}
```

### 6.3 Invalidación de Cache Estratégica

```csharp
public class ProductService
{
    private const string CacheKeyPrefix = "products";

    public async Task InvalidateProductCacheAsync(Guid productId)
    {
        // ✅ Invalidar cache específico
        var specificKey = $"{CacheKeyPrefix}:{productId}";
        _cache.Remove(specificKey);
        await _distributedCache.RemoveAsync(specificKey);

        // ✅ Invalidar cache de listados (contienen el producto modificado)
        var listKeys = new[]
        {
            $"{CacheKeyPrefix}:list:all",
            $"{CacheKeyPrefix}:list:category:{product.CategoryId}"
        };

        foreach (var key in listKeys)
        {
            _cache.Remove(key);
            await _distributedCache.RemoveAsync(key);
        }
    }

    // ✅ Usar Cache Aside Pattern con tiempo de expiración
    public async Task<ProductDto> GetProductAsync(Guid id, CancellationToken ct)
    {
        var cacheKey = $"{CacheKeyPrefix}:{id}";

        if (_cache.TryGetValue(cacheKey, out ProductDto cached))
            return cached;

        var product = await _repository.GetProductByIdAsync(id, ct);
        if (product == null) return null;

        var dto = _mapper.Map<ProductDto>(product);

        // ✅ TTL más largo para datos que cambian poco
        var ttl = product.Category == "Featured" 
            ? TimeSpan.FromMinutes(5)  // Featured products cambian más
            : TimeSpan.FromMinutes(30); // Otros cambian menos

        _cache.Set(cacheKey, dto, ttl);

        return dto;
    }
}
```

## 7. Antipatrones (NO Hacer)

### ❌ Antipatrón 1: Consultas Sin Paginación

```csharp
// ❌ MAL - Cargar todos los registros en memoria
[HttpGet]
public async Task<ActionResult<List<UserDto>>> GetAllUsers()
{
    var users = await _context.Users.ToListAsync(); // ❌ 10,000+ registros
    return Ok(users);
}

// ✅ BIEN - Paginación obligatoria
[HttpGet]
public async Task<ActionResult<PagedResponse<UserDto>>> GetUsers(
    [FromQuery] PagedQuery query,
    CancellationToken ct)
{
    if (query.Limit > 100)
    {
        return BadRequest("Límite máximo permitido: 100");
    }

    var skip = (query.Page - 1) * query.Limit;
    var users = await _context.Users
        .AsNoTracking()
        .OrderBy(u => u.Id)
        .Skip(skip)
        .Take(query.Limit)
        .ToListAsync(ct);

    var total = await _context.Users.CountAsync(ct);

    return Ok(new PagedResponse<UserDto>
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
    });
}
```

**Problema**: Consultas sin paginación consumen memoria excesiva (OutOfMemoryException), timeout de queries, saturación de red.  
**Solución**: Implementar paginación obligatoria con límite máximo de 100 registros por página.

### ❌ Antipatrón 2: Bloquear Threads con Código Síncrono

```csharp
// ❌ MAL - Operaciones síncronas que bloquean threads
[HttpGet("{id}")]
public ActionResult<UserDto> GetUser(Guid id)
{
    Thread.Sleep(1000); // ❌ Bloquea thread del pool
    
    var user = _context.Users.Find(id); // ❌ Síncrono
    return Ok(user);
}

// ✅ BIEN - Async/await libera threads durante I/O
[HttpGet("{id:guid}")]
public async Task<ActionResult<UserDto>> GetUser(Guid id, CancellationToken ct)
{
    await Task.Delay(1000, ct); // ✅ No bloquea thread

    var user = await _context.Users
        .AsNoTracking()
        .FirstOrDefaultAsync(u => u.Id == id, ct); // ✅ Async
    
    if (user == null)
        return NotFound();

    return Ok(_mapper.Map<UserDto>(user));
}
```

**Problema**: Código síncrono agota el thread pool bajo alta carga, reduce throughput de 100 req/s a 10 req/s.  
**Solución**: Async/await en toda la pila (controller → service → repository), usar `CancellationToken`.

### ❌ Antipatrón 3: Cache Sin Estrategia de Invalidación

```csharp
// ❌ MAL - Cachear sin invalidar cuando cambian datos
public class ProductService
{
    public async Task<ProductDto> GetProductAsync(Guid id)
    {
        var cacheKey = $"product:{id}";

        if (_cache.TryGetValue(cacheKey, out ProductDto cached))
            return cached;

        var product = await _repository.GetProductByIdAsync(id);
        
        // ❌ Cache infinito, nunca se invalida
        _cache.Set(cacheKey, product, new MemoryCacheEntryOptions());
        
        return product;
    }

    public async Task UpdateProductAsync(Guid id, UpdateProductRequest request)
    {
        await _repository.UpdateProductAsync(id, request);
        // ❌ No invalida cache, clientes ven datos desactualizados
    }
}

// ✅ BIEN - Cache con TTL e invalidación explícita
public class ProductService
{
    public async Task<ProductDto> GetProductAsync(Guid id, CancellationToken ct)
    {
        var cacheKey = $"product:{id}";

        if (_cache.TryGetValue(cacheKey, out ProductDto cached))
            return cached;

        var product = await _repository.GetProductByIdAsync(id, ct);
        var dto = _mapper.Map<ProductDto>(product);

        // ✅ TTL de 15 minutos
        _cache.Set(cacheKey, dto, TimeSpan.FromMinutes(15));

        return dto;
    }

    public async Task<ProductDto> UpdateProductAsync(
        Guid id,
        UpdateProductRequest request,
        CancellationToken ct)
    {
        var product = await _repository.UpdateProductAsync(id, request, ct);

        // ✅ Invalidar cache explícitamente
        await InvalidateProductCacheAsync(id);

        return _mapper.Map<ProductDto>(product);
    }

    private async Task InvalidateProductCacheAsync(Guid id)
    {
        var cacheKey = $"product:{id}";
        _cache.Remove(cacheKey);
        await _distributedCache.RemoveAsync(cacheKey);
    }
}
```

**Problema**: Cache sin invalidación causa datos stale (obsoletos), inconsistencias entre clientes.  
**Solución**: TTL razonable (5-30 min) + invalidación explícita al UPDATE/DELETE.

### ❌ Antipatrón 4: No Habilitar Compresión o Usar Nivel Inadecuado

```csharp
// ❌ MAL - Sin compresión (payload 500KB)
builder.Services.AddControllers();
// ❌ No hay AddResponseCompression()

// ❌ MAL - Compresión con nivel óptimo (lento)
builder.Services.Configure<BrotliCompressionProviderOptions>(options =>
{
    options.Level = CompressionLevel.Optimal; // ❌ CPU-intensive, latencia alta
});

// ✅ BIEN - Compresión con nivel balanceado
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
    
    options.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(new[]
    {
        "application/json"
    });
});

builder.Services.Configure<BrotliCompressionProviderOptions>(options =>
{
    options.Level = CompressionLevel.Fastest; // ✅ Balance velocidad/compresión
});

var app = builder.Build();
app.UseResponseCompression(); // ✅ Middleware habilitado
```

**Problema**: Sin compresión → 500KB payload, latencia alta en redes lentas. Compresión Optimal → latencia server +50ms.  
**Solución**: Habilitar compresión Brotli/Gzip con nivel `Fastest` (reduce 70-80% tamaño con overhead mínimo).

## 8. Validación y Cumplimiento

### 8.1 Checklist de Implementación

- [ ] **Paginación** implementada en todos los endpoints de listado
- [ ] **Límite máximo** de 100 registros por página
- [ ] **IMemoryCache** configurado para cache L1 (hot paths)
- [ ] **IDistributedCache** (Redis) configurado para cache L2
- [ ] **TTL de cache** definido (5-30 min según volatilidad)
- [ ] **Invalidación de cache** implementada en UPDATE/DELETE
- [ ] **Compresión Brotli/Gzip** habilitada con nivel `Fastest`
- [ ] **Async/await** en toda la pila (controller → service → repository)
- [ ] **CancellationToken** pasado en métodos async
- [ ] **AsNoTracking()** usado en queries read-only
- [ ] **Rate Limiting** configurado (60 req/min, 1000 req/hora)
- [ ] **Métricas** de latencia/throughput monitoreadas (Application Insights)

### 8.2 Métricas de Cumplimiento

| Métrica                              | Target       | Verificación                        |
| ------------------------------------ | ------------ | ----------------------------------- |
| Latencia p95 endpoints GET           | ≤ 200ms      | Application Insights                |
| Latencia p95 endpoints POST/PUT      | ≤ 500ms      | Application Insights                |
| Throughput APIs públicas             | ≥ 1000 req/s | Load testing (k6, JMeter)           |
| Cache hit rate                       | ≥ 70%        | Logs de cache hits/misses           |
| Tamaño payload con compresión        | ≤ 50KB       | Network tab (dev tools)             |
| Endpoints con paginación             | 100%         | Code review                         |
| Queries N+1 detectadas               | 0            | EF Core Logging + SQL Profiler     |

## 9. Referencias

### Estándares Relacionados

- [Diseño REST](./01-diseno-rest.md) - Implementación técnica de APIs
- [Versionado](./04-versionado.md) - Versionado compatible con caching

### Convenciones Relacionadas

- [Naming Endpoints](../../convenciones/apis/01-naming-endpoints.md) - Nomenclatura de endpoints
- [Formato Respuestas](../../convenciones/apis/03-formato-respuestas.md) - Estructura de paginación

### Lineamientos Relacionados

- [Desarrollo de APIs](../../lineamientos/desarrollo/desarrollo-de-apis.md) - Lineamientos de APIs
- [Optimización y Eficiencia](../../lineamientos/arquitectura/05-optimizacion-y-eficiencia.md) - Performance sistémico

### Principios Relacionados

- [Eficiencia y Optimización](../../principios/arquitectura/08-eficiencia-optimizacion.md) - Fundamento de performance
- [Escalabilidad](../../principios/arquitectura/03-escalabilidad.md) - Diseño para crecimiento

### ADRs Relacionados

- [ADR-002: Estándar para APIs REST](../../../decisiones-de-arquitectura/adr-002-estandard-apis-rest.md)
- [ADR-011: Cache Distribuido](../../../decisiones-de-arquitectura/adr-011-cache-distribuido.md)

### Documentación Externa

- [ASP.NET Core Performance Best Practices](https://learn.microsoft.com/en-us/aspnet/core/performance/performance-best-practices) - Microsoft Docs
- [EF Core Performance](https://learn.microsoft.com/en-us/ef/core/performance/) - EF Core optimization
- [Response Compression Middleware](https://learn.microsoft.com/en-us/aspnet/core/performance/response-compression) - Compression guide
- [AspNetCoreRateLimit](https://github.com/stefanprodan/AspNetCoreRateLimit) - Rate limiting library

---

**Última actualización**: 27 de enero 2026  
**Responsable**: Equipo de Arquitectura
