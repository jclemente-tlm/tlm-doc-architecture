---
id: monitoreo-metricas
sidebar_position: 2
title: Monitoreo y Métricas
description: Estándares para health checks, métricas, distributed tracing y monitoreo de APIs
---

## 1. Principios de Monitoreo

- **Proactividad**: Detectar problemas antes que los usuarios
- **Métricas relevantes**: Medir lo que importa para el negocio y operación
- **Alertas accionables**: Solo alertar cuando requiere acción humana
- **Trazabilidad**: Seguir requests a través de servicios distribuidos
- **SLOs definidos**: Service Level Objectives medibles

## 2. Métricas de Performance

### Implementación con OpenTelemetry (.NET)

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

### Configuración de exportadores

```csharp
// Program.cs
builder.Services.AddOpenTelemetry()
    .WithMetrics(metrics =>
    {
        metrics
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddRuntimeInstrumentation()
            .AddPrometheusExporter();
    });

var app = builder.Build();

// Endpoint para Prometheus
app.MapPrometheusScrapingEndpoint();
```

## 3. Health Checks

### Health checks básicos

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddDbContext<ApplicationDbContext>(
        name: "database",
        tags: new[] { "db", "ready" })
    .AddRedis(
        builder.Configuration.GetConnectionString("Redis"),
        name: "redis-cache",
        tags: new[] { "cache", "ready" })
    .AddCheck<ExternalApiHealthCheck>(
        "external-api",
        tags: new[] { "external", "ready" })
    .AddCheck("memory", () =>
    {
        var allocated = GC.GetTotalMemory(false);
        var threshold = 500_000_000; // 500MB

        return allocated < threshold
            ? HealthCheckResult.Healthy($"Memory usage: {allocated:N0} bytes")
            : HealthCheckResult.Unhealthy($"Memory usage too high: {allocated:N0} bytes");
    }, tags: new[] { "memory" });

var app = builder.Build();

// Endpoints de health checks
app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse,
    AllowCachingResponses = false
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready"),
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false // Solo verifica que la app responde
});
```

### Health check personalizado

```csharp
public class ExternalApiHealthCheck : IHealthCheck
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ExternalApiHealthCheck> _logger;

    public ExternalApiHealthCheck(
        HttpClient httpClient,
        ILogger<ExternalApiHealthCheck> logger)
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
            var response = await _httpClient.GetAsync(
                "/api/health",
                cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                var responseTime = response.Headers.TryGetValues("X-Response-Time", out var values)
                    ? values.FirstOrDefault()
                    : "unknown";

                return HealthCheckResult.Healthy(
                    $"External API is responsive (response time: {responseTime}ms)");
            }

            return HealthCheckResult.Degraded(
                $"External API returned {response.StatusCode}");
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Health check failed for external API");
            return HealthCheckResult.Unhealthy(
                "External API is unreachable",
                ex);
        }
        catch (TaskCanceledException)
        {
            return HealthCheckResult.Unhealthy(
                "External API health check timeout");
        }
    }
}
```

## 4. Distributed Tracing

### Configuración con OpenTelemetry

```csharp
// Program.cs
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing =>
    {
        tracing
            .AddSource("Talma.Api")
            .SetResourceBuilder(ResourceBuilder.CreateDefault()
                .AddService("talma-api")
                .AddAttributes(new Dictionary<string, object>
                {
                    ["environment"] = builder.Environment.EnvironmentName,
                    ["version"] = Assembly.GetExecutingAssembly()
                        .GetName().Version?.ToString() ?? "unknown"
                }))
            .AddAspNetCoreInstrumentation(options =>
            {
                options.RecordException = true;
                options.Filter = httpContext =>
                {
                    // No rastrear health checks
                    return !httpContext.Request.Path.StartsWithSegments("/health");
                };
                options.EnrichWithHttpRequest = (activity, request) =>
                {
                    activity.SetTag("http.request.user_agent",
                        request.Headers["User-Agent"].ToString());
                };
                options.EnrichWithHttpResponse = (activity, response) =>
                {
                    activity.SetTag("http.response.content_length",
                        response.ContentLength);
                };
            })
            .AddEntityFrameworkCoreInstrumentation(options =>
            {
                options.SetDbStatementForText = true;
                options.SetDbStatementForStoredProcedure = true;
            })
            .AddHttpClientInstrumentation()
            .AddRedisInstrumentation()
            .AddJaegerExporter(options =>
            {
                options.AgentHost = builder.Configuration["Jaeger:AgentHost"];
                options.AgentPort = int.Parse(
                    builder.Configuration["Jaeger:AgentPort"] ?? "6831");
            });
    });
```

### Uso en código

```csharp
public class UserService
{
    private readonly ActivitySource _activitySource = new("Talma.Api");
    private readonly IUserRepository _repository;

    public async Task<User> GetUserAsync(int userId)
    {
        using var activity = _activitySource.StartActivity(
            "GetUser",
            ActivityKind.Internal);

        activity?.SetTag("user.id", userId);
        activity?.SetTag("operation", "read");

        try
        {
            var user = await _repository.GetUserAsync(userId);

            if (user == null)
            {
                activity?.SetStatus(ActivityStatusCode.Error, "User not found");
                activity?.SetTag("user.found", false);
                return null;
            }

            activity?.SetTag("user.found", true);
            activity?.SetTag("user.email", user.Email);
            activity?.SetStatus(ActivityStatusCode.Ok);

            return user;
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            throw;
        }
    }
}
```

## 5. Métricas de Negocio

### Custom metrics

```csharp
public class BusinessMetrics
{
    private readonly Meter _meter;
    private readonly Counter<long> _ordersCreated;
    private readonly Counter<long> _ordersCancelled;
    private readonly Histogram<double> _orderValue;

    public BusinessMetrics(IMeterFactory meterFactory)
    {
        _meter = meterFactory.Create("Talma.Business");

        _ordersCreated = _meter.CreateCounter<long>(
            "orders_created_total",
            description: "Total number of orders created");

        _ordersCancelled = _meter.CreateCounter<long>(
            "orders_cancelled_total",
            description: "Total number of orders cancelled");

        _orderValue = _meter.CreateHistogram<double>(
            "order_value_usd",
            unit: "USD",
            description: "Order value in USD");
    }

    public void RecordOrderCreated(string country, double value)
    {
        _ordersCreated.Add(1, new TagList { { "country", country } });
        _orderValue.Record(value, new TagList { { "country", country } });
    }

    public void RecordOrderCancelled(string country, string reason)
    {
        _ordersCancelled.Add(1, new TagList
        {
            { "country", country },
            { "reason", reason }
        });
    }
}
```

## 6. Dashboards y Alertas

### Métricas clave a monitorear

#### Golden Signals (SRE Google)

1. **Latency**: Tiempo de respuesta de requests
2. **Traffic**: Cantidad de requests por segundo
3. **Errors**: Tasa de errores (4xx, 5xx)
4. **Saturation**: Uso de recursos (CPU, memoria, conexiones)

#### RED Method (para servicios)

1. **Rate**: Requests por segundo
2. **Errors**: Tasa de errores
3. **Duration**: Latencia de requests

#### USE Method (para recursos)

1. **Utilization**: % de uso del recurso
2. **Saturation**: Trabajo en cola
3. **Errors**: Errores del recurso

### Configuración de alertas (ejemplo con Prometheus)

```yaml
# prometheus-alerts.yml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for {{ $labels.endpoint }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s for {{ $labels.endpoint }}"

      - alert: HealthCheckFailed
        expr: up{job="talma-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"
```

## 7. Integración con AWS CloudWatch

### Envío de métricas custom

```csharp
public class CloudWatchMetrics
{
    private readonly IAmazonCloudWatch _cloudWatch;

    public CloudWatchMetrics(IAmazonCloudWatch cloudWatch)
    {
        _cloudWatch = cloudWatch;
    }

    public async Task PublishMetricAsync(
        string metricName,
        double value,
        StandardUnit unit,
        Dictionary<string, string> dimensions)
    {
        var request = new PutMetricDataRequest
        {
            Namespace = "Talma/API",
            MetricData = new List<MetricDatum>
            {
                new MetricDatum
                {
                    MetricName = metricName,
                    Value = value,
                    Unit = unit,
                    TimestampUtc = DateTime.UtcNow,
                    Dimensions = dimensions.Select(d => new Dimension
                    {
                        Name = d.Key,
                        Value = d.Value
                    }).ToList()
                }
            }
        };

        await _cloudWatch.PutMetricDataAsync(request);
    }
}
```

## 8. Checklist de Monitoreo

- [ ] **Health checks**: /health, /health/ready, /health/live configurados
- [ ] **Métricas básicas**: Request rate, latency, errors exportadas
- [ ] **Distributed tracing**: Correlation IDs en logs y traces
- [ ] **Alertas configuradas**: Para SLOs críticos
- [ ] **Dashboards creados**: Visibilidad de métricas clave
- [ ] **Métricas de negocio**: KPIs relevantes instrumentados
- [ ] **Retention policies**: Configuradas según compliance

## 📖 Referencias

### Lineamientos relacionados

- [Observabilidad](/docs/fundamentos-corporativos/lineamientos/arquitectura/observabilidad)

### Estándares relacionados

- [Logging Estructurado](/docs/fundamentos-corporativos/estandares/observabilidad/logging)
- [Performance de APIs](/docs/fundamentos-corporativos/estandares/apis/performance)

### ADRs relacionados

- [ADR-021: Observabilidad](/docs/decisiones-de-arquitectura/adr-021-observabilidad)

### Recursos externos

- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Google SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)
