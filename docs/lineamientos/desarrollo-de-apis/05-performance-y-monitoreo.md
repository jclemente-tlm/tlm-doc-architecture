---
title: "Performance y monitoreo"
sidebar_position: 5
---

Esta guía establece las mejores prácticas para optimización de performance y monitoreo efectivo de APIs REST.

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

## 📊 Monitoreo y métricas

### Métricas de performance

```csharp
public class ApiMetrics
{
    private readonly IMeterFactory _meterFactory;
    private readonly Meter _meter;
    private readonly Counter<long> _requestCounter;
    private readonly Histogram<double> _requestDuration;
    private readonly Histogram<long> _requestSize;
    private readonly Counter<long> _errorCounter;

    public ApiMetrics(IMeterFactory meterFactory)
    {
        _meterFactory = meterFactory;
        _meter = _meterFactory.Create("Talma.Api");

        _requestCounter = _meter.CreateCounter<long>(
            "http_requests_total",
            description: "Total number of HTTP requests");

        _requestDuration = _meter.CreateHistogram<double>(
            "http_request_duration_seconds",
            description: "HTTP request duration in seconds");

        _requestSize = _meter.CreateHistogram<long>(
            "http_request_size_bytes",
            description: "HTTP request size in bytes");

        _errorCounter = _meter.CreateCounter<long>(
            "http_errors_total",
            description: "Total number of HTTP errors");
    }

    public void RecordRequest(string method, string endpoint, int statusCode, double duration)
    {
        var tags = new TagList
        {
            { "method", method },
            { "endpoint", endpoint },
            { "status_code", statusCode.ToString() }
        };

        _requestCounter.Add(1, tags);
        _requestDuration.Record(duration, tags);

        if (statusCode >= 400)
            _errorCounter.Add(1, tags);
    }
}

// Middleware de métricas
public class MetricsMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ApiMetrics _metrics;

    public MetricsMiddleware(RequestDelegate next, ApiMetrics metrics)
    {
        _next = next;
        _metrics = metrics;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            await _next(context);
        }
        finally
        {
            stopwatch.Stop();

            var method = context.Request.Method;
            var endpoint = context.Request.Path.Value;
            var statusCode = context.Response.StatusCode;
            var duration = stopwatch.Elapsed.TotalSeconds;

            _metrics.RecordRequest(method, endpoint, statusCode, duration);
        }
    }
}
```

### Health checks

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddDbContext<ApplicationDbContext>()
    .AddRedis(builder.Configuration.GetConnectionString("Redis"))
    .AddCheck<ExternalApiHealthCheck>("external-api")
    .AddCheck("memory", () =>
    {
        var allocated = GC.GetTotalMemory(false);
        var threshold = 500_000_000; // 500MB

        return allocated < threshold
            ? HealthCheckResult.Healthy($"Memory usage: {allocated:N0} bytes")
            : HealthCheckResult.Unhealthy($"Memory usage too high: {allocated:N0} bytes");
    });

var app = builder.Build();

app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false
});

// Health check personalizado
public class ExternalApiHealthCheck : IHealthCheck
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ExternalApiHealthCheck> _logger;

    public ExternalApiHealthCheck(HttpClient httpClient, ILogger<ExternalApiHealthCheck> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _httpClient.GetAsync("/api/health", cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                return HealthCheckResult.Healthy("External API is responsive");
            }

            return HealthCheckResult.Unhealthy(
                $"External API returned {response.StatusCode}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Health check failed for external API");
            return HealthCheckResult.Unhealthy(
                "External API is unreachable", ex);
        }
    }
}
```

### Logging estructurado

```csharp
public class UserController : ControllerBase
{
    private readonly ILogger<UserController> _logger;

    public UserController(ILogger<UserController> logger)
    {
        _logger = logger;
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<UserDto>> GetUser(int id)
    {
        using var activity = Activity.StartActivity("GetUser");
        activity?.SetTag("user.id", id);

        _logger.LogInformation("Getting user {UserId}", id);

        var stopwatch = Stopwatch.StartNew();

        try
        {
            var user = await _userService.GetUserAsync(id);

            if (user == null)
            {
                _logger.LogWarning("User {UserId} not found", id);
                return NotFound();
            }

            stopwatch.Stop();

            _logger.LogInformation(
                "Successfully retrieved user {UserId} in {ElapsedMs}ms",
                id, stopwatch.ElapsedMilliseconds);

            return Ok(user);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Error retrieving user {UserId} after {ElapsedMs}ms",
                id, stopwatch.ElapsedMilliseconds);
            throw;
        }
    }
}

// Configuración de logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddJsonConsole(options =>
{
    options.IncludeScopes = true;
    options.TimestampFormat = "yyyy-MM-dd HH:mm:ss.fff zzz";
    options.JsonWriterOptions = new JsonWriterOptions
    {
        Indented = false
    };
});
```

### Distributed tracing

```csharp
// Program.cs
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing =>
    {
        tracing
            .AddAspNetCoreInstrumentation(options =>
            {
                options.RecordException = true;
                options.Filter = httpContext =>
                {
                    // No rastrear health checks
                    return !httpContext.Request.Path.StartsWithSegments("/health");
                };
            })
            .AddEntityFrameworkCoreInstrumentation(options =>
            {
                options.SetDbStatementForText = true;
                options.SetDbStatementForStoredProcedure = true;
            })
            .AddHttpClientInstrumentation()
            .AddRedisInstrumentation()
            .AddJaegerExporter();
    });

// En el controller
public async Task<ActionResult<UserDto>> GetUser(int id)
{
    using var activity = Activity.StartActivity("GetUser");
    activity?.SetTag("user.id", id);
    activity?.SetTag("operation", "read");

    var user = await _userService.GetUserAsync(id);

    activity?.SetTag("user.found", user != null);
    activity?.SetStatus(user != null ? ActivityStatusCode.Ok : ActivityStatusCode.Error);

    return user != null ? Ok(user) : NotFound();
}
```

## 📈 Rate limiting

### Implementación con AspNetCoreRateLimit

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

builder.Services.Configure<IpRateLimitPolicies>(options =>
{
    options.IpRules = new List<IpRateLimitPolicy>
    {
        new IpRateLimitPolicy
        {
            Ip = "127.0.0.1",
            Rules = new List<RateLimitRule>
            {
                new RateLimitRule
                {
                    Endpoint = "*",
                    Period = "1m",
                    Limit = 1000  // Mayor límite para desarrollo
                }
            }
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

### Monitoring

- [ ] **Métricas**: Request duration, error rates, throughput
- [ ] **Health checks**: Database, external services, memoria
- [ ] **Logging**: Estructurado con correlation IDs
- [ ] **Alertas**: Configuradas para SLAs críticos
- [ ] **Dashboards**: Visibilidad de performance en tiempo real

## 📖 Referencias

### ADRs relacionados

- [ADR-011: Cache distribuido](/docs/adrs/adr-011-cache-distribuido)
- [ADR-016: Logging estructurado](/docs/adrs/adr-016-logging-estructurado)

### Recursos externos

- [ASP.NET Core Performance Best Practices](https://docs.microsoft.com/en-us/aspnet/core/performance/performance-best-practices)
- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [Rate Limiting in ASP.NET Core](https://docs.microsoft.com/en-us/aspnet/core/performance/rate-limit)
- [HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
