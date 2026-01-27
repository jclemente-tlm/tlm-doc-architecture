---
id: monitoreo-metricas
sidebar_position: 2
title: Monitoreo y Métricas  
description: Estándares para health checks ASP.NET Core 8.0+, métricas OpenTelemetry 1.6+ y distributed tracing
---

## 1. Propósito

Este estándar define cómo implementar monitoreo proactivo, recolección de métricas y distributed tracing en aplicaciones de Talma para garantizar disponibilidad, detectar anomalías antes que afecten a usuarios y medir SLOs (Service Level Objectives). Establece:
- **Health checks** (/health/live, /health/ready) para Kubernetes liveness/readiness probes
- **Métricas de performance** (latencia p95, error rate, throughput) con OpenTelemetry
- **Distributed tracing** para seguir requests a través de microservicios con Jaeger/AWS X-Ray
- **Alertas accionables** basadas en SLOs (99.9% uptime, p95 < 200ms)
- **Golden Signals** (Latency, Traffic, Errors, Saturation)

Permite detectar degradación de servicio y correlacionar métricas con logs mediante correlation IDs.

**Versión**: 1.0  
**Última actualización**: 2025-08-08

## 2. Alcance

### Aplica a:
- APIs REST (ASP.NET Core 8.0+, Express.js 4.18+) con health checks
- Microservicios con dependencies (PostgreSQL, Redis, APIs externas)
- Aplicaciones con SLOs definidos (uptime, latency, error rate)
- Sistemas con arquitectura de microservicios (distributed tracing obligatorio)
- Métricas de negocio (órdenes/minuto, pagos procesados, usuarios activos)

### No aplica a:
- Aplicaciones frontend (usar Datadog RUM o CloudWatch RUM)
- Scripts batch sin estado (solo logs de inicio/fin)
- Lambdas AWS (CloudWatch Metrics automático)
- Sistemas legacy sin instrumentación (requieren plan de modernización)

## 3. Tecnologías Obligatorias

| Tecnología | Versión Mínima | Propósito |
|------------|----------------|-----------|
| **OpenTelemetry .NET** | 1.6+ | Instrumentación de métricas y distributed tracing para .NET |
| **OpenTelemetry SDK** | 1.6+ | Exportación de métricas a Prometheus, Jaeger, AWS X-Ray, CloudWatch |
| **AspNetCore.HealthChecks** | 8.0+ | Health checks para ASP.NET Core (/health endpoints) |
| **AspNetCore.HealthChecks.NpgSql** | 8.0+ | Health check para PostgreSQL |
| **AspNetCore.HealthChecks.Redis** | 8.0+ | Health check para Redis |
| **Prometheus.AspNetCore** | 8.2+ | Exportación de métricas en formato Prometheus (/metrics) |
| **Jaeger** | 1.50+ | Distributed tracing backend (alternativa: AWS X-Ray) |
| **AWS CloudWatch** | - | Métricas, logs y alarmas centralizadas en AWS |
| **prom-client** (Node.js) | 15.0+ | Métricas Prometheus para Node.js/TypeScript |

## 4. Especificaciones Técnicas

### 4.1 Health Checks (.NET)

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddHealthChecks()
    .AddNpgSql(
        connectionString: builder.Configuration.GetConnectionString("DefaultConnection")!,
        name: "postgres",
        tags: new[] { "db", "ready" },
        timeout: TimeSpan.FromSeconds(3))
    .AddRedis(
        redisConnectionString: builder.Configuration.GetConnectionString("Redis")!,
        name: "redis",
        tags: new[] { "cache", "ready" })
    .AddUrlGroup(
        new Uri("https://payment-api.talma.com/health"),
        name: "payment-api",
        tags: new[] { "external", "ready" })
    .AddCheck("self", () => HealthCheckResult.Healthy(), tags: new[] { "live" });

var app = builder.Build();

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("live")
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});

app.Run();
```

### 4.2 Métricas con OpenTelemetry

```csharp
builder.Services.AddOpenTelemetry()
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddRuntimeInstrumentation()
        .AddMeter("Talma.Api")
        .AddPrometheusExporter());

app.MapPrometheusScrapingEndpoint();

public class ApiMetrics
{
    private readonly Meter _meter;
    private readonly Counter<long> _requestCounter;
    private readonly Histogram<double> _requestDuration;

    public ApiMetrics(IMeterFactory meterFactory)
    {
        _meter = meterFactory.Create("Talma.Api");
        _requestCounter = _meter.CreateCounter<long>("http_requests_total");
        _requestDuration = _meter.CreateHistogram<double>("http_request_duration_seconds");
    }

    public void RecordRequest(string method, string endpoint, int statusCode, double duration)
    {
        var tags = new TagList { { "method", method }, { "endpoint", endpoint }, { "status_code", statusCode.ToString() } };
        _requestCounter.Add(1, tags);
        _requestDuration.Record(duration, tags);
    }
}
```

### 4.3 Distributed Tracing

```csharp
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddSource("Talma.Api")
        .AddAspNetCoreInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddJaegerExporter());

public class UserService
{
    private readonly ActivitySource _activitySource = new("Talma.Api");

    public async Task<User?> GetUserAsync(Guid userId)
    {
        using var activity = _activitySource.StartActivity("GetUser");
        activity?.SetTag("user.id", userId);
        
        var user = await _repository.GetUserAsync(userId);
        activity?.SetTag("user.found", user != null);
        
        return user;
    }
}
```

### 4.4 Métricas de Negocio

```csharp
public class BusinessMetrics
{
    private readonly Meter _meter;
    private readonly Counter<long> _ordersCreated;
    private readonly Histogram<double> _orderValue;

    public BusinessMetrics(IMeterFactory meterFactory)
    {
        _meter = meterFactory.Create("Talma.Business");
        _ordersCreated = _meter.CreateCounter<long>("orders_created_total");
        _orderValue = _meter.CreateHistogram<double>("order_value_usd", unit: "USD");
    }

    public void RecordOrderCreated(string country, double value)
    {
        _ordersCreated.Add(1, new TagList { { "country", country } });
        _orderValue.Record(value, new TagList { { "country", country } });
    }
}
```

## 5. Buenas Prácticas

### 5.1 Golden Signals (SRE Google)

1. **Latency**: p50, p95, p99 de tiempo de respuesta
2. **Traffic**: Requests por segundo
3. **Errors**: Tasa de errores (4xx, 5xx)
4. **Saturation**: CPU, memoria, conexiones DB

### 5.2 SLOs (Service Level Objectives)

```yaml
# Ejemplo de SLOs
api_availability_slo: 99.9%  # 43 minutos downtime/mes
api_latency_p95_slo: 200ms
api_error_rate_slo: 1%
```

### 5.3 Alertas Accionables

```yaml
# prometheus-alerts.yml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Error rate > 5%"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency > 1s"
```

## 6. Antipatrones

### 6.1 ❌ Health Checks sin Dependencies

**Problema**:
```csharp
app.MapHealthChecks("/health", new HealthCheckOptions
{
    Predicate = _ => true
});
// Solo verifica que la app responda, no las dependencies
```

**Solución**:
```csharp
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString)
    .AddRedis(redisConnection);
```

### 6.2 ❌ Métricas sin Dimensiones

**Problema**:
```csharp
_requestCounter.Add(1); // Sin tags, imposible filtrar
```

**Solución**:
```csharp
_requestCounter.Add(1, new TagList { { "endpoint", "/api/users" }, { "method", "GET" } });
```

### 6.3 ❌ Alertas sin For Duration

**Problema**:
```yaml
- alert: HighErrorRate
  expr: rate(http_errors_total[1m]) > 0.01
  # Alerta inmediata, genera ruido
```

**Solución**:
```yaml
- alert: HighErrorRate
  expr: rate(http_errors_total[5m]) > 0.01
  for: 5m # Espera 5 minutos antes de alertar
```

### 6.4 ❌ Tracing de Health Checks

**Problema**:
```csharp
.AddAspNetCoreInstrumentation() // Incluye /health en traces
```

**Solución**:
```csharp
.AddAspNetCoreInstrumentation(options =>
{
    options.Filter = ctx => !ctx.Request.Path.StartsWithSegments("/health");
})
```

## 7. Validación y Testing

### 7.1 Tests de Health Checks

```csharp
[Fact]
public async Task HealthCheck_AllDependenciesHealthy_ReturnsHealthy()
{
    var response = await _client.GetAsync("/health");
    
    response.StatusCode.Should().Be(HttpStatusCode.OK);
    var content = await response.Content.ReadAsStringAsync();
    content.Should().Contain("\"status\":\"Healthy\"");
}
```

### 7.2 Tests de Métricas

```csharp
[Fact]
public async Task Metrics_AfterRequest_RecordsMetric()
{
    await _client.GetAsync("/api/users");
    
    var metricsResponse = await _client.GetAsync("/metrics");
    var metrics = await metricsResponse.Content.ReadAsStringAsync();
    
    metrics.Should().Contain("http_requests_total");
}
```

## 8. Referencias

### Lineamientos Relacionados
- [Observabilidad](/docs/fundamentos-corporativos/lineamientos/arquitectura/observabilidad)

### Estándares Relacionados
- [Logging Estructurado](./01-logging.md)
- [Performance de APIs](../apis/05-performance.md)

### ADRs Relacionados
- [ADR-021: Observabilidad](/docs/decisiones-de-arquitectura/adr-021-observabilidad)

### Recursos Externos
- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/)

## 9. Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-08-08 | Equipo de Arquitectura | Versión inicial con template de 9 secciones |
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
