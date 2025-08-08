# 8. Conceptos transversales

## 8.1 Seguridad

| Aspecto | Implementación | Tecnología |
|---------|----------------|-------------|
| **Autenticación** | `JWT validation` | `OAuth2/OIDC` |
| **Autorización** | `Claims-based`, `RBAC` | `.NET 8` |
| **Rate limiting** | Por IP/Usuario | `Redis` |
| **CORS** | Configuración dinámica | `ASP.NET Core` |
| **Cifrado** | `TLS 1.3` | `HTTPS` |

### 8.1.1 Autenticación y autorización

El API Gateway implementa un modelo de seguridad basado en `OAuth2/OIDC` con `JWT tokens` para garantizar acceso seguro a todos los servicios corporativos.

```csharp
// Configuración de autenticación JWT
public void ConfigureServices(IServiceCollection services)
{
    services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
        .AddJwtBearer(options =>
        {
            options.Authority = "https://identity.corporate-services.local";
            options.RequireHttpsMetadata = true;
            options.TokenValidationParameters = new TokenValidationParameters
            {
                ValidateIssuer = true,
                ValidateAudience = true,
                ValidateLifetime = true,
                ValidateIssuerSigningKey = true,
                ClockSkew = TimeSpan.FromMinutes(5),
                RoleClaimType = "roles",
                NameClaimType = "sub"
            };

            // Caché de validación de tokens
            options.Events = new JwtBearerEvents
            {
                OnTokenValidated = async context =>
                {
                    var tokenCache = context.HttpContext.RequestServices
                        .GetRequiredService<ITokenCache>();
                    await tokenCache.SetValidTokenAsync(context.SecurityToken as JwtSecurityToken);
                }
            };
        });

    services.AddAuthorization(options =>
    {
        options.AddPolicy("RequireValidUser", policy =>
            policy.RequireAuthenticatedUser()
                  .RequireClaim("tenant_id"));

        options.AddPolicy("RequireAdminRole", policy =>
            policy.RequireRole("admin"));
    });
}
```

### 8.1.2 Cabeceras de seguridad y protección

```csharp
public class CabecerasSeguridadMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        // Cabeceras de seguridad estándar
        var response = context.Response;

        response.Headers.Add("X-Content-Type-Options", "nosniff");
        response.Headers.Add("X-Frame-Options", "DENY");
        response.Headers.Add("X-XSS-Protection", "1; mode=block");
        response.Headers.Add("Referrer-Policy", "strict-origin-when-cross-origin");
        response.Headers.Add("Permissions-Policy",
            "camera=(), microphone=(), location=(), payment=()");

        // Política de Seguridad de Contenido
        response.Headers.Add("Content-Security-Policy",
            "default-src 'self'; " +
            "script-src 'self' 'unsafe-inline'; " +
            "style-src 'self' 'unsafe-inline'; " +
            "img-src 'self' data: https:; " +
            "connect-src 'self'; " +
            "font-src 'self'; " +
            "base-uri 'self'");

        // HSTS para HTTPS
        if (context.Request.IsHttps)
        {
            response.Headers.Add("Strict-Transport-Security",
                "max-age=31536000; includeSubDomains; preload");
        }

        await _next(context);
    }
}
```

### 8.1.3 Rate limiting y throttling

```csharp
public class RateLimitingService : IRateLimitingService
{
    private readonly IMemoryCache _cache;
    private readonly IConfiguration _config;

    public async Task<RateLimitResult> CheckRateLimitAsync(string clientId, string endpoint)
    {
        var policy = await GetPolicyForClientAsync(clientId);
        var key = $"rate_limit:{clientId}:{endpoint}";

        var currentCount = _cache.Get<int>(key);

        if (currentCount >= policy.Limit)
        {
            return new RateLimitResult
            {
                IsAllowed = false,
                Limit = policy.Limit,
                Remaining = 0,
                ResetTime = GetResetTime(key)
            };
        }

        // Incrementar contador
        var newCount = currentCount + 1;
        _cache.Set(key, newCount, policy.Window);

        return new RateLimitResult
        {
            IsAllowed = true,
            Limit = policy.Limit,
            Remaining = policy.Limit - newCount,
            ResetTime = GetResetTime(key)
        };
    }

    private async Task<RateLimitPolicy> GetPolicyForClientAsync(string clientId)
    {
        var clientTier = await GetClientTierAsync(clientId);

        return clientTier switch
        {
            "premium" => new RateLimitPolicy { Limit = 10000, Window = TimeSpan.FromMinutes(1) },
            "standard" => new RateLimitPolicy { Limit = 1000, Window = TimeSpan.FromMinutes(1) },
            "basic" => new RateLimitPolicy { Limit = 100, Window = TimeSpan.FromMinutes(1) },
            _ => new RateLimitPolicy { Limit = 10, Window = TimeSpan.FromMinutes(1) }
        };
    }
}
```

## 8.2 Observabilidad y monitoreo

| Tipo | Herramienta | Propósito |
|------|-------------|----------|
| **Logs** | `Serilog` | Registro requests/eventos |
| **Métricas** | `Prometheus` | Monitoreo performance |
| **Tracing** | `OpenTelemetry`, `Jaeger` | Trazabilidad requests |
| **Health** | Health Checks | Estado gateway |

- Stack de observabilidad: `Grafana` (dashboards), `Prometheus` (métricas), `Loki` (logs), `Jaeger` (tracing distribuido).
- Dashboards y alertas preconfiguradas para latencia, errores 5xx, disponibilidad y saturación de recursos.
- Exporters y anotaciones automáticas en los contenedores para scraping de métricas y logs estructurados.

### 8.2.1 Logging estructurado

```csharp
// Configuración de Serilog
public static IHostBuilder CreateHostBuilder(string[] args) =>
    Host.CreateDefaultBuilder(args)
        .UseSerilog((context, services, configuration) =>
        {
            configuration
                .ReadFrom.Configuration(context.Configuration)
                .Enrich.FromLogContext()
                .Enrich.WithProperty("ServiceName", "api-gateway")
                .Enrich.WithProperty("Version", Assembly.GetExecutingAssembly().GetName().Version)
                .Enrich.WithCorrelationId()
                .WriteTo.Console(new JsonFormatter())
                .WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri("http://elasticsearch:9200"))
                {
                    IndexFormat = "api-gateway-{0:yyyy.MM.dd}",
                    AutoRegisterTemplate = true
                });
        });

// Middleware de correlación
public class CorrelationMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<CorrelationMiddleware> _logger;

    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = GetOrCreateCorrelationId(context);

        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            context.Response.Headers.Add("X-Correlation-ID", correlationId);

            _logger.LogInformation("Request started: {Method} {Path}",
                context.Request.Method, context.Request.Path);

            await _next(context);

            _logger.LogInformation("Request completed: {Method} {Path} -> {StatusCode}",
                context.Request.Method, context.Request.Path, context.Response.StatusCode);
        }
    }

    private string GetOrCreateCorrelationId(HttpContext context)
    {
        return context.Request.Headers["X-Correlation-ID"].FirstOrDefault()
            ?? context.TraceIdentifier
            ?? Guid.NewGuid().ToString();
    }
}
```

### 8.2.2 Métricas y telemetría

```csharp
public class MetricsMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IMetrics _metrics;
    private readonly Counter<long> _requestCounter;
    private readonly Histogram<double> _requestDuration;

    public MetricsMiddleware(RequestDelegate next, IMetrics metrics)
    {
        _next = next;
        _metrics = metrics;

        _requestCounter = _metrics.CreateCounter<long>(
            "api_gateway_requests_total",
            "Total number of HTTP requests");

        _requestDuration = _metrics.CreateHistogram<double>(
            "api_gateway_request_duration_seconds",
            "Duration of HTTP requests");
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        var tags = new TagList
        {
            ["method"] = context.Request.Method,
            ["endpoint"] = GetEndpointName(context),
            ["tenant_id"] = context.Items["TenantId"]?.ToString() ?? "unknown"
        };

        try
        {
            await _next(context);

            tags["status_code"] = context.Response.StatusCode.ToString();
            tags["status_class"] = GetStatusClass(context.Response.StatusCode);
        }
        catch (Exception ex)
        {
            tags["status_code"] = "500";
            tags["status_class"] = "5xx";
            tags["exception_type"] = ex.GetType().Name;
            throw;
        }
        finally
        {
            stopwatch.Stop();

            _requestCounter.Add(1, tags);
            _requestDuration.Record(stopwatch.Elapsed.TotalSeconds, tags);
        }
    }

    private static string GetStatusClass(int statusCode) =>
        statusCode switch
        {
            >= 200 and < 300 => "2xx",
            >= 300 and < 400 => "3xx",
            >= 400 and < 500 => "4xx",
            >= 500 => "5xx",
            _ => "unknown"
        };
}
```

### 8.2.3 Trazabilidad distribuida

```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddOpenTelemetry()
        .WithTracing(builder =>
        {
            builder
                .SetSampler(new AlwaysOnSampler())
                .AddAspNetCoreInstrumentation(options =>
                {
                    options.RecordException = true;
                    options.EnableGrpcAspNetCoreSupport = true;
                    options.Filter = (httpContext) =>
                    {
                        // No tracing para health checks
                        return !httpContext.Request.Path.StartsWithSegments("/health");
                    };
                })
                .AddHttpClientInstrumentation()
                .AddJaegerExporter()
                .AddConsoleExporter();
        });
}

// Enriquecimiento de spans
public class TracingEnrichmentMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        using var activity = Activity.Current;

        if (activity != null)
        {
            // Agregar información de contexto al span
            activity.SetTag("http.method", context.Request.Method);
            activity.SetTag("http.url", context.Request.GetDisplayUrl());
            activity.SetTag("user.id", context.User.FindFirst("sub")?.Value);
            activity.SetTag("tenant.id", context.Items["TenantId"]?.ToString());
            activity.SetTag("client.id", GetClientId(context));

            if (context.Request.Headers.ContainsKey("User-Agent"))
            {
                activity.SetTag("http.user_agent", context.Request.Headers["User-Agent"].ToString());
            }
        }

        await _next(context);

        if (activity != null)
        {
            activity.SetTag("http.status_code", context.Response.StatusCode);

            if (context.Response.StatusCode >= 400)
            {
                activity.SetStatus(ActivityStatusCode.Error, $"HTTP {context.Response.StatusCode}");
            }
        }
    }
}
```

## 8.3 Resiliencia y manejo de errores

| Patrón | Implementación | Propósito |
|---------|----------------|----------|
| **Circuit Breaker** | `Polly` | Protección fallos |
| **Retry** | Políticas exponenciales | Recuperación automática |
| **Timeout** | Por endpoint | Prevención bloqueos |

### 8.3.1 Patrón circuit breaker

```csharp
public class CircuitBreakerService : ICircuitBreakerService
{
    private readonly ConcurrentDictionary<string, CircuitBreakerState> _circuitBreakers;
    private readonly ILogger<CircuitBreakerService> _logger;

    public async Task<T> ExecuteAsync<T>(string key, Func<Task<T>> operation, CircuitBreakerOptions options)
    {
        var circuitBreaker = _circuitBreakers.GetOrAdd(key, _ => new CircuitBreakerState(options));

        if (circuitBreaker.State == CircuitState.Open)
        {
            if (DateTime.UtcNow < circuitBreaker.NextAttempt)
            {
                throw new CircuitBreakerOpenException($"Circuit breaker {key} is open");
            }

            // Half-open: intentar una operación
            circuitBreaker.State = CircuitState.HalfOpen;
        }

        try
        {
            var result = await operation();

            // Éxito: reset del circuit breaker
            circuitBreaker.Reset();
            return result;
        }
        catch (Exception ex)
        {
            circuitBreaker.RecordFailure();

            if (circuitBreaker.ShouldOpen())
            {
                circuitBreaker.Open();
                _logger.LogWarning("Circuit breaker {Key} opened due to failures", key);
            }

            throw;
        }
    }
}

public class CircuitBreakerState
{
    public CircuitState State { get; set; } = CircuitState.Closed;
    public int FailureCount { get; private set; }
    public DateTime NextAttempt { get; private set; }
    private readonly CircuitBreakerOptions _options;

    public void RecordFailure()
    {
        FailureCount++;
    }

    public bool ShouldOpen()
    {
        return FailureCount >= _options.FailureThreshold;
    }

    public void Open()
    {
        State = CircuitState.Open;
        NextAttempt = DateTime.UtcNow.Add(_options.OpenDuration);
    }

    public void Reset()
    {
        State = CircuitState.Closed;
        FailureCount = 0;
        NextAttempt = DateTime.MinValue;
    }
}
```

### 8.3.2 Políticas de reintentos

```csharp
public class RetryPolicyService
{
    public static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
    {
        return Policy
            .Handle<HttpRequestException>()
            .Or<TaskCanceledException>()
            .OrResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode && IsRetriableStatusCode(r.StatusCode))
            .WaitAndRetryAsync(
                retryCount: 3,
                sleepDurationProvider: retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)) +
                    TimeSpan.FromMilliseconds(Random.Shared.Next(0, 1000)), // Jitter
                onRetry: (outcome, timespan, retryCount, context) =>
                {
                    var logger = context.GetLogger();
                    logger?.LogWarning("Retry attempt {RetryCount} for {OperationKey} in {Delay}ms",
                        retryCount, context.OperationKey, timespan.TotalMilliseconds);
                });
    }

    private static bool IsRetriableStatusCode(HttpStatusCode statusCode)
    {
        return statusCode switch
        {
            HttpStatusCode.InternalServerError => true,
            HttpStatusCode.BadGateway => true,
            HttpStatusCode.ServiceUnavailable => true,
            HttpStatusCode.GatewayTimeout => true,
            HttpStatusCode.TooManyRequests => true,
            _ => false
        };
    }
}
```

## 8.4 Rendimiento y caching

### 8.4.1 Estrategia de caching multinivel

```csharp
public class MultiLevelCacheService : ICacheService
{
    private readonly IMemoryCache _l1Cache;  // Nivel 1: In-memory
    private readonly IDistributedCache _l2Cache;  // Nivel 2: Redis
    private readonly ILogger<MultiLevelCacheService> _logger;

    public async Task<T> GetAsync<T>(string key, Func<Task<T>> valueFactory, TimeSpan expiration)
    {
        // L1 Cache check
        if (_l1Cache.TryGetValue(key, out T cachedValue))
        {
            _logger.LogDebug("Cache hit (L1): {Key}", key);
            return cachedValue;
        }

        // L2 Cache check
        var serializedValue = await _l2Cache.GetStringAsync(key);
        if (serializedValue != null)
        {
            var deserializedValue = JsonSerializer.Deserialize<T>(serializedValue);

            // Populate L1 cache
            _l1Cache.Set(key, deserializedValue, TimeSpan.FromMinutes(2));

            _logger.LogDebug("Cache hit (L2): {Key}", key);
            return deserializedValue;
        }

        // Cache miss: execute value factory
        _logger.LogDebug("Cache miss: {Key}", key);
        var value = await valueFactory();

        // Store in both caches
        await SetAsync(key, value, expiration);

        return value;
    }

    public async Task SetAsync<T>(string key, T value, TimeSpan expiration)
    {
        // Set in L1 cache (shorter TTL)
        _l1Cache.Set(key, value, TimeSpan.FromMinutes(Math.Min(2, expiration.TotalMinutes)));

        // Set in L2 cache (full TTL)
        var serializedValue = JsonSerializer.Serialize(value);
        await _l2Cache.SetStringAsync(key, serializedValue, new DistributedCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = expiration
        });
    }

    public async Task RemoveAsync(string key)
    {
        _l1Cache.Remove(key);
        await _l2Cache.RemoveAsync(key);
    }
}
```

### 8.4.2 Agrupación de conexiones y reutilización

```csharp
public class HttpClientService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IOptions<HttpClientOptions> _options;

    public HttpClient CreateClient(string serviceName)
    {
        return _httpClientFactory.CreateClient(serviceName);
    }
}

// Startup configuration
public void ConfigureServices(IServiceCollection services)
{
    // HTTP client con pooling y circuit breaker
    services.AddHttpClient("identity-service", client =>
    {
        client.BaseAddress = new Uri("http://identity-service:8080");
        client.Timeout = TimeSpan.FromSeconds(30);
        client.DefaultRequestHeaders.Add("User-Agent", "ApiGateway/1.0");
    })
    .AddPolicyHandler(GetRetryPolicy())
    .AddPolicyHandler(GetCircuitBreakerPolicy())
    .ConfigurePrimaryHttpMessageHandler(() => new HttpClientHandler
    {
        MaxConnectionsPerServer = 20,
        PooledConnectionLifetime = TimeSpan.FromMinutes(2)
    });
}
```

## 8.5 Multi-tenancy

### 8.5.1 Resolución de contexto de tenant

```csharp
public class TenantContextMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ITenantResolver _tenantResolver;

    public async Task InvokeAsync(HttpContext context)
    {
        var tenantId = ExtractTenantId(context);

        if (!string.IsNullOrEmpty(tenantId))
        {
            var tenant = await _tenantResolver.ResolveTenantAsync(tenantId);
            if (tenant != null)
            {
                context.Items["Tenant"] = tenant;
                context.Items["TenantId"] = tenantId;

                // Enriquecer request headers para servicios downstream
                context.Request.Headers.Add("X-Tenant-ID", tenantId);
                context.Request.Headers.Add("X-Tenant-Region", tenant.Region);
                context.Request.Headers.Add("X-Tenant-Tier", tenant.Tier);
            }
        }

        await _next(context);
    }

    private string ExtractTenantId(HttpContext context)
    {
        // 1. JWT claims
        var tenantFromJwt = context.User?.FindFirst("tenant_id")?.Value;
        if (!string.IsNullOrEmpty(tenantFromJwt))
            return tenantFromJwt;

        // 2. Header explícito
        var tenantFromHeader = context.Request.Headers["X-Tenant-ID"].FirstOrDefault();
        if (!string.IsNullOrEmpty(tenantFromHeader))
            return tenantFromHeader;

        // 3. Subdomain (tenant.api.corporate-services.com)
        var host = context.Request.Host.Host;
        if (host.Contains('.'))
        {
            var parts = host.Split('.');
            if (parts.Length >= 3 && parts[1] == "api")
                return parts[0];
        }

        return null;
    }
}
```

### 8.5.2 Configuración específica por tenant

```csharp
public class TenantConfigurationService : ITenantConfigurationService
{
    private readonly ICacheService _cache;
    private readonly ITenantRepository _tenantRepository;

    public async Task<TenantConfiguration> GetConfigurationAsync(string tenantId)
    {
        var cacheKey = $"tenant_config:{tenantId}";

        return await _cache.GetAsync(cacheKey, async () =>
        {
            var tenant = await _tenantRepository.GetByIdAsync(tenantId);

            return new TenantConfiguration
            {
                TenantId = tenantId,
                Name = tenant.Name,
                Region = tenant.Region,
                Tier = tenant.Tier,
                Features = tenant.Features,
                RateLimits = tenant.RateLimits,
                CustomHeaders = tenant.CustomHeaders,
                RoutingRules = tenant.RoutingRules
            };
        }, TimeSpan.FromMinutes(5));
    }
}
```

---

> Todos los conceptos transversales están alineados a los ADRs, modelos C4/Structurizr DSL y cumplen con los requisitos de seguridad, observabilidad, resiliencia y multi-tenancy definidos para el API Gateway.
