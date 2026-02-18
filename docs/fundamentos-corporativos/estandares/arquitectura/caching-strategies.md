---
id: caching-strategies
sidebar_position: 2
title: Estrategias de Caché Distribuido
description: Patrones y prácticas para implementar caché distribuido con Redis
---

# Estrategias de Caché Distribuido

## Contexto

Este estándar define estrategias de caché distribuido para reducir latencia y carga en bases de datos. Complementa el [lineamiento de Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md) especificando **qué, cómo y cuándo cachear** para optimizar rendimiento sin sacrificar consistencia.

---

## Stack Tecnológico

| Componente        | Tecnología          | Versión | Uso                      |
| ----------------- | ------------------- | ------- | ------------------------ |
| **Cache**         | Redis               | 7.0+    | Cache distribuido        |
| **Client**        | StackExchange.Redis | 2.7+    | Cliente .NET para Redis  |
| **Abstraction**   | IDistributedCache   | 8.0+    | Abstracción ASP.NET Core |
| **Cloud Service** | Amazon ElastiCache  | -       | Redis managed service    |
| **Serialization** | System.Text.Json    | 8.0+    | Serialización eficiente  |

---

## Implementación Técnica

### Patrones de Caché

```csharp
/// <summary>
/// ✅ Cache-Aside (Lazy Loading) - Patrón más común
/// </summary>
public class CacheAsideService
{
    private readonly IDistributedCache _cache;
    private readonly IProductRepository _repository;

    public async Task<Product?> GetProductAsync(string productId)
    {
        var cacheKey = $"product:{productId}";

        // 1. Intentar leer del cache
        var cached = await _cache.GetStringAsync(cacheKey);
        if (cached != null)
        {
            return JsonSerializer.Deserialize<Product>(cached);
        }

        // 2. Cache miss: cargar de base de datos
        var product = await _repository.GetByIdAsync(productId);
        if (product == null)
            return null;

        // 3. Escribir en cache para futuros requests
        await _cache.SetStringAsync(
            cacheKey,
            JsonSerializer.Serialize(product),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(15)
            });

        return product;
    }

    public async Task UpdateProductAsync(Product product)
    {
        // 1. Actualizar base de datos
        await _repository.UpdateAsync(product);

        // 2. Invalidar cache
        await _cache.RemoveAsync($"product:{product.Id}");

        // O alternativamente: actualizar cache inmediatamente
        // await _cache.SetStringAsync(...);
    }
}

/// <summary>
/// ✅ Read-Through Cache - Cache maneja la carga
/// </summary>
public class ReadThroughCacheService
{
    private readonly IDistributedCache _cache;
    private readonly IProductRepository _repository;

    public async Task<Product?> GetProductAsync(string productId)
    {
        var cacheKey = $"product:{productId}";

        return await _cache.GetOrCreateAsync(
            cacheKey,
            async () =>
            {
                // Este delegate solo se ejecuta en cache miss
                var product = await _repository.GetByIdAsync(productId);
                return product;
            },
            new DistributedCacheEntryOptions
            {
                SlidingExpiration = TimeSpan.FromMinutes(15),
                AbsoluteExpirationRelativeToNow = TimeSpan.FromHours(1)
            });
    }
}

/// <summary>
/// ✅ Write-Through Cache - Escrituras síncronas a cache y DB
/// </summary>
public class WriteThroughCacheService
{
    private readonly IDistributedCache _cache;
    private readonly IProductRepository _repository;

    public async Task CreateProductAsync(Product product)
    {
        // 1. Escribir a base de datos
        await _repository.CreateAsync(product);

        // 2. Escribir a cache inmediatamente
        await _cache.SetStringAsync(
            $"product:{product.Id}",
            JsonSerializer.Serialize(product),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30)
            });
    }
}

/// <summary>
/// ✅ Write-Behind (Write-Back) - Escrituras asíncronas
/// </summary>
public class WriteBehindCacheService
{
    private readonly IDistributedCache _cache;
    private readonly IBackgroundJobQueue _jobQueue;

    public async Task UpdateProductAsync(Product product)
    {
        // 1. Escribir a cache inmediatamente (baja latencia)
        await _cache.SetStringAsync(
            $"product:{product.Id}",
            JsonSerializer.Serialize(product),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30)
            });

        // 2. Encolar escritura a DB (procesamiento asíncrono)
        await _jobQueue.EnqueueAsync(new PersistProductJob
        {
            ProductId = product.Id
        });
    }
}
```

### Extension Methods para IDistributedCache

```csharp
public static class DistributedCacheExtensions
{
    /// <summary>
    /// ✅ GetOrCreate con tipo genérico
    /// </summary>
    public static async Task<T?> GetOrCreateAsync<T>(
        this IDistributedCache cache,
        string key,
        Func<Task<T?>> factory,
        DistributedCacheEntryOptions? options = null)
    {
        // Intentar leer del cache
        var cached = await cache.GetStringAsync(key);
        if (cached != null)
        {
            return JsonSerializer.Deserialize<T>(cached);
        }

        // Cache miss: ejecutar factory
        var value = await factory();
        if (value == null)
            return default;

        // Guardar en cache
        await cache.SetStringAsync(
            key,
            JsonSerializer.Serialize(value),
            options ?? new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5)
            });

        return value;
    }

    /// <summary>
    /// ✅ Set con tipo genérico
    /// </summary>
    public static async Task SetAsync<T>(
        this IDistributedCache cache,
        string key,
        T value,
        TimeSpan? expiration = null)
    {
        await cache.SetStringAsync(
            key,
            JsonSerializer.Serialize(value),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = expiration ?? TimeSpan.FromMinutes(15)
            });
    }

    /// <summary>
    /// ✅ Get con tipo genérico
    /// </summary>
    public static async Task<T?> GetAsync<T>(
        this IDistributedCache cache,
        string key)
    {
        var cached = await cache.GetStringAsync(key);
        return cached == null ? default : JsonSerializer.Deserialize<T>(cached);
    }

    /// <summary>
    /// ✅ Invalidación de múltiples keys con patrón
    /// </summary>
    public static async Task RemoveByPatternAsync(
        this IDistributedCache cache,
        string pattern)
    {
        // Requiere StackExchange.Redis directamente
        if (cache is not IConnectionMultiplexer multiplexer)
            throw new InvalidOperationException("This operation requires StackExchange.Redis");

        var endpoints = multiplexer.GetEndPoints();
        foreach (var endpoint in endpoints)
        {
            var server = multiplexer.GetServer(endpoint);
            var keys = server.Keys(pattern: pattern);

            foreach (var key in keys)
            {
                await cache.RemoveAsync(key.ToString());
            }
        }
    }
}
```

### Estrategias de Invalidación

```csharp
/// <summary>
/// ✅ Invalidación explícita en updates
/// </summary>
public class ProductService
{
    private readonly IDistributedCache _cache;
    private readonly IProductRepository _repository;

    public async Task UpdateProductAsync(Product product)
    {
        await _repository.UpdateAsync(product);

        // Invalidar cache del producto
        await _cache.RemoveAsync($"product:{product.Id}");

        // Invalidar caches relacionados
        await _cache.RemoveAsync($"products:category:{product.CategoryId}");
        await _cache.RemoveAsync("products:featured");
    }

    /// <summary>
    /// ✅ Invalidación por TTL (Time To Live)
    /// </summary>
    public async Task<IEnumerable<Product>> GetFeaturedProductsAsync()
    {
        return await _cache.GetOrCreateAsync(
            "products:featured",
            async () => await _repository.GetFeaturedAsync(),
            new DistributedCacheEntryOptions
            {
                // ✅ Expiración absoluta: cache se invalida automáticamente
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30)
            });
    }

    /// <summary>
    /// ✅ Sliding expiration: resetea TTL en cada acceso
    /// </summary>
    public async Task<Product?> GetProductWithSlidingAsync(string productId)
    {
        return await _cache.GetOrCreateAsync(
            $"product:{productId}",
            async () => await _repository.GetByIdAsync(productId),
            new DistributedCacheEntryOptions
            {
                // ✅ Se extiende 15min en cada acceso
                SlidingExpiration = TimeSpan.FromMinutes(15),
                // ✅ Pero nunca más de 1 hora total
                AbsoluteExpirationRelativeToNow = TimeSpan.FromHours(1)
            });
    }
}

/// <summary>
/// ✅ Invalidación por eventos (Event-Driven)
/// </summary>
public class ProductEventHandler : INotificationHandler<ProductUpdatedEvent>
{
    private readonly IDistributedCache _cache;

    public async Task Handle(ProductUpdatedEvent notification, CancellationToken ct)
    {
        // Invalidar cuando se publica evento de actualización
        await _cache.RemoveAsync($"product:{notification.ProductId}");
        await _cache.RemoveAsync($"products:category:{notification.CategoryId}");
    }
}
```

### Cache Warming (Pre-calentamiento)

```csharp
/// <summary>
/// ✅ Pre-calentar cache en startup
/// </summary>
public class CacheWarmingService : IHostedService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<CacheWarmingService> _logger;

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        using var scope = _serviceProvider.CreateScope();
        var cache = scope.ServiceProvider.GetRequiredService<IDistributedCache>();
        var repository = scope.ServiceProvider.GetRequiredService<IProductRepository>();

        _logger.LogInformation("Warming up cache...");

        // Pre-cargar productos más populares
        var popularProducts = await repository.GetMostViewedAsync(100);
        foreach (var product in popularProducts)
        {
            await cache.SetAsync(
                $"product:{product.Id}",
                product,
                TimeSpan.FromHours(1));
        }

        // Pre-cargar categorías
        var categories = await repository.GetCategoriesAsync();
        await cache.SetAsync("categories:all", categories, TimeSpan.FromHours(6));

        _logger.LogInformation("Cache warmed up with {Count} items",
            popularProducts.Count() + 1);
    }

    public Task StopAsync(CancellationToken cancellationToken) => Task.CompletedTask;
}
```

### Configuración de Redis

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Configurar StackExchange.Redis
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration["Redis:ConnectionString"];
    options.InstanceName = "tlm-catalog-";

    options.ConfigurationOptions = new ConfigurationOptions
    {
        EndPoints = { builder.Configuration["Redis:ConnectionString"] },
        AbortOnConnectFail = false,  // ✅ No abortar si Redis no disponible
        ConnectTimeout = 5000,
        SyncTimeout = 5000,
        AsyncTimeout = 5000,
        ConnectRetry = 3,
        ReconnectRetryPolicy = new ExponentialRetry(1000),

        // ✅ SSL/TLS para ElastiCache en producción
        Ssl = builder.Environment.IsProduction(),
        SslProtocols = System.Security.Authentication.SslProtocols.Tls12
    };
});

// ✅ Registrar IConnectionMultiplexer para operaciones avanzadas
builder.Services.AddSingleton<IConnectionMultiplexer>(sp =>
    ConnectionMultiplexer.Connect(builder.Configuration["Redis:ConnectionString"]));
```

### Configuración de ElastiCache (Terraform)

```hcl
# Redis Cluster
resource "aws_elasticache_replication_group" "catalog_cache" {
  replication_group_id       = "tlm-catalog-cache"
  replication_group_description = "Catalog service cache"

  engine                     = "redis"
  engine_version             = "7.0"
  parameter_group_name       = "default.redis7.cluster.on"

  # ✅ Cluster mode habilitado para escalabilidad
  automatic_failover_enabled = true
  multi_az_enabled           = true
  num_cache_clusters         = 3  # 1 primary + 2 replicas

  node_type                  = "cache.r6g.large"
  port                       = 6379

  # ✅ Seguridad
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token_enabled         = true
  auth_token                 = random_password.redis_auth.result

  # ✅ Backup
  snapshot_retention_limit   = 5
  snapshot_window            = "03:00-05:00"

  # ✅ Mantenimiento
  maintenance_window         = "sun:05:00-sun:07:00"

  subnet_group_name          = aws_elasticache_subnet_group.cache.name
  security_group_ids         = [aws_security_group.cache.id]

  tags = {
    Environment = "production"
    Service     = "catalog"
  }
}
```

### Métricas de Cache

```csharp
public class CacheMetricsMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IDistributedCache _cache;
    private readonly Counter<long> _cacheHits;
    private readonly Counter<long> _cacheMisses;
    private readonly Histogram<double> _cacheLatency;

    public CacheMetricsMiddleware(
        RequestDelegate next,
        IDistributedCache cache,
        IMeterFactory meterFactory)
    {
        _next = next;
        _cache = cache;

        var meter = meterFactory.Create("Talma.Catalog.Cache");
        _cacheHits = meter.CreateCounter<long>("cache.hits", "hits");
        _cacheMisses = meter.CreateCounter<long>("cache.misses", "misses");
        _cacheLatency = meter.CreateHistogram<double>("cache.latency", "ms");
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Decorar GetStringAsync para métricas
        var originalCache = context.RequestServices.GetRequiredService<IDistributedCache>();
        context.RequestServices = new MetricsDecoratedCache(
            originalCache,
            _cacheHits,
            _cacheMisses,
            _cacheLatency);

        await _next(context);
    }
}

// PromQL queries para dashboards
/*
# Cache hit rate
sum(rate(cache_hits_total[5m])) /
(sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m]))) * 100

# Cache latency P95
histogram_quantile(0.95, sum(rate(cache_latency_bucket[5m])) by (le))

# Eviction rate
rate(redis_evicted_keys_total[5m])
*/
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar IDistributedCache para caché distribuido
- **MUST** configurar TTL (Time To Live) en todas las entradas
- **MUST** invalidar cache explícitamente en updates/deletes
- **MUST** usar keys descriptivos con prefijo (`product:123`)
- **MUST** serializar con System.Text.Json
- **MUST** configurar connection pooling en Redis client
- **MUST** manejar cache misses gracefully (fallback a DB)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Cache-Aside para la mayoría de casos
- **SHOULD** cachear queries costosos (> 100ms)
- **SHOULD** usar sliding expiration para datos frecuentemente accedidos
- **SHOULD** implementar métricas (hit rate, latency)
- **SHOULD** usar ElastiCache en producción con replicación
- **SHOULD** configurar retry policy para transient failures
- **SHOULD** documentar qué se cachea y por cuánto tiempo

### MAY (Opcional)

- **MAY** implementar cache warming para datos críticos
- **MAY** usar Write-Behind para escrituras de alta frecuencia
- **MAY** implementar cache tagging para invalidación por grupos
- **MAY** usar Redis Streams para event-driven invalidation
- **MAY** implementar two-level cache (L1: memoria, L2: Redis)

### MUST NOT (Prohibido)

- **MUST NOT** cachear datos sensibles sin encriptar
- **MUST NOT** usar cache sin TTL (puede crecer indefinidamente)
- **MUST NOT** cachear datos que cambian frecuentemente (< 1 min)
- **MUST NOT** asumir que cache siempre está disponible
- **MUST NOT** usar cache como único storage (debe ser reproducible)
- **MUST NOT** cachear objetos muy grandes (> 1MB)

---

## Referencias

- [Lineamiento: Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md)
- Estándares relacionados:
  - [Diseño Stateless](stateless-design.md)
  - [Optimización de Base de Datos](../../estandares/datos/database-optimization.md)
- Especificaciones:
  - [Microsoft: Distributed Caching in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/performance/caching/distributed)
  - [AWS ElastiCache Best Practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/BestPractices.html)
  - [Caching Patterns](https://aws.amazon.com/caching/best-practices/)
