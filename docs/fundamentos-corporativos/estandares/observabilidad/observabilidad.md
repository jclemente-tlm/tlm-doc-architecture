sidebar_position: 1
title: Observabilidad
slug: /estandares/observabilidad
summary: Estándar unificado para logging estructurado, métricas, health checks, tracing distribuido y correlation IDs en microservicios y APIs.
description: Consolidado de prácticas y requisitos para observabilidad integral: logging estructurado, métricas, health checks, tracing distribuido y correlation IDs, alineado a OpenTelemetry y Grafana Stack.

---

# Estándar Técnico — Observabilidad

## 1. Propósito

Definir los lineamientos obligatorios para implementar observabilidad integral en microservicios y APIs, abarcando logging estructurado, métricas, health checks, tracing distribuido y correlation IDs, para facilitar troubleshooting, monitoreo proactivo y trazabilidad extremo a extremo.

**Aplica a:**

- Todos los microservicios y APIs REST
- Workers y procesadores de eventos (Kafka, SQS)
- Servicios containerizados (ECS Fargate, Docker)

**No aplica a:**

- Scripts batch ejecutados por scheduler (cron)
- Funciones serverless (Lambda health es responsabilidad de AWS)

## 3. Tecnologías Aprobadas

| Componente      | Tecnología / Versión mínima                         |
| --------------- | --------------------------------------------------- |
| Logging         | Serilog 3.1+, OpenTelemetry 1.7+, Grafana Loki 2.9+ |
| Métricas        | OpenTelemetry 1.7+, Grafana Mimir 2.10+             |
| Tracing         | OpenTelemetry 1.7+, Grafana Tempo 2.3+              |
| Health Checks   | AspNetCore.HealthChecks 8.0+                        |
| Correlation IDs | W3C Trace Context 1.0, UUID v4                      |

## 4. Requisitos Obligatorios 🔴

- Logging estructurado en formato JSON en producción
- Incluir `X-Correlation-ID` en todos los logs y propagación HTTP
- Propagación de traceparent/tracestate (W3C Trace Context)
- Endpoints `/health/live` y `/health/ready` (timeout <500ms, sin autenticación)
- Métricas HTTP: latency (p50/p95/p99), throughput, error rate
- Golden Signals: Latency, Traffic, Errors, Saturation
- Instrumentación automática: HTTP, gRPC, DB, colas
- Sampling adaptativo: 100% errores, 10% exitosos
- Enmascaramiento de datos sensibles en logs (passwords, tokens, PII)
- Retención mínima: Error 90d, Warning/Info 30d

## 5. Prohibiciones ❌

- Logs en texto plano en producción
- Console.WriteLine() en código productivo
- Health checks sin timeout o únicos (deben ser liveness y readiness separados)
- Falta de propagación de correlation ID o traceparent
- Métricas sin granularidad (solo contadores globales)
- Logging de datos sensibles sin enmascarar

## 6. Configuración / Implementación

builder.Services.AddOpenTelemetry()

### Logging estructurado con Serilog y OpenTelemetry

```csharp
// Program.cs
Log.Logger = new LoggerConfiguration()
        .Enrich.FromLogContext()
        .Enrich.WithProperty("Environment", env.EnvironmentName)
        .WriteTo.Console(new JsonFormatter())
        .CreateLogger();

builder.Services.AddOpenTelemetry()
        .WithTracing(tracing => tracing
                .AddAspNetCoreInstrumentation()
                .AddHttpClientInstrumentation()
                .AddOtlpExporter(opt =>
                {
                        opt.Endpoint = new Uri("http://tempo:4317"); // Grafana Tempo OTLP endpoint
                }))
        .WithMetrics(metrics => metrics
                .AddAspNetCoreInstrumentation()
                .AddRuntimeInstrumentation()
                .AddOtlpExporter(opt =>
                {
                        opt.Endpoint = new Uri("http://mimir:4317"); // Grafana Mimir OTLP endpoint
                }));
```

### Ejemplo de span manual (tracing)

```csharp
var tracerProvider = Sdk.CreateTracerProviderBuilder()
        .AddSource("MyApp")
        .AddOtlpExporter()
        .Build();

var tracer = tracerProvider.GetTracer("MyApp");
using (var span = tracer.StartActiveSpan("ProcesarPedido"))
{
        span.SetAttribute("pedido.id", 1234);
        // ... lógica de negocio ...
        span.SetStatus(Status.Ok);
}
```

### Ejemplo de métrica personalizada

```csharp
var meter = new Meter("MyApp.Metrics", "1.0.0");
var requestCounter = meter.CreateCounter<long>("http_requests_total");
requestCounter.Add(1, new KeyValuePair<string, object>("endpoint", "/api/values"));
```

### Ejemplo de consulta PromQL (Grafana Mimir)

```promql
sum(rate(http_server_requests_duration_seconds_count{job="myapp"}[5m])) by (status_code)
```

### Ejemplo de configuración OTLP Exporter (appsettings.json)

```json
{
  "OpenTelemetry": {
    "Tracing": {
      "OtlpExporter": {
        "Endpoint": "http://tempo:4317"
      }
    },
    "Metrics": {
      "OtlpExporter": {
        "Endpoint": "http://mimir:4317"
      }
    }
  }
}
```

### Middleware para Correlation ID

```csharp
public class CorrelationIdMiddleware
{
    private readonly RequestDelegate _next;
    private const string CorrelationIdHeader = "X-Correlation-ID";

    public async Task InvokeAsync(HttpContext context, ILogger<CorrelationIdMiddleware> logger)
    {
        string correlationId = context.Request.Headers[CorrelationIdHeader].FirstOrDefault()
            ?? Guid.NewGuid().ToString();

        context.Items["CorrelationId"] = correlationId;
        context.Response.Headers[CorrelationIdHeader] = correlationId;

        using (logger.BeginScope(new Dictionary<string, object>
        {
            ["CorrelationId"] = correlationId
        }))
        {
            await _next(context);
        }
    }
}
```

### Health Checks en .NET

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "database", tags: new[] { "ready" })
    .AddRedis(redisConnection, name: "cache", tags: new[] { "ready" });

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false
});
app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```

### Ejemplo de métrica personalizada

```csharp
var meter = new Meter("MyApp.Metrics", "1.0.0");
var requestCounter = meter.CreateCounter<long>("http_requests_total");
requestCounter.Add(1, new KeyValuePair<string, object>("endpoint", "/api/values"));
```

### Ejemplo de log estructurado con correlation y trace ID

```json
{
  "timestamp": "2026-02-04T12:34:56.789Z",
  "level": "Information",
  "message": "User login successful",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
  "spanId": "00f067aa0ba902b7"
}
```

## 7. Validación

### Script de validación de health checks

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health/live
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health/ready
```

### Validación de logs y métricas

- Verificar logs en formato JSON con correlationId y traceId
- Validar que los endpoints de health checks respondan <500ms
- Confirmar que las métricas estén expuestas vía OpenTelemetry
- Revisar retención y enmascaramiento de datos sensibles

## 8. Referencias

- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [Grafana Loki](https://grafana.com/oss/loki/)
- [Grafana Mimir](https://grafana.com/oss/mimir/)
- [Grafana Tempo](https://grafana.com/oss/tempo/)
- [Serilog](https://serilog.net/)
- [Health Checks ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)

---

> **Nota:** Este estándar consolida y reemplaza los archivos: logging.md, metrics-monitoring.md, distributed-tracing.md, correlation-ids.md, health-checks.md. Todos los equipos deben migrar a este documento único y mantenerlo actualizado.
