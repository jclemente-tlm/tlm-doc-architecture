---
id: observability
sidebar_position: 8
title: Observabilidad
description: Estándares unificados para logging estructurado, métricas, tracing distribuido, correlation IDs y health checks
---

# Estándar Técnico — Observabilidad

## 1. Propósito

Garantizar visibilidad end-to-end en arquitecturas distribuidas mediante logging estructurado JSON, métricas OpenTelemetry, distributed tracing con W3C Trace Context, correlation IDs inmutables y health checks para orquestadores (AWS ECS Fargate, ECS, ALB).

## 2. Alcance

**Aplica a:**

- APIs REST (.NET) y microservicios backend
- Workers, background jobs, Lambdas AWS
- Sistemas distribuidos con SLOs definidos (uptime 99.9%, latencia p95 `<200ms`)
- Servicios containerizados detrás de load balancers

**No aplica a:**

- Logs de infraestructura (Docker, AWS ECS) - usar Loki directamente
- Aplicaciones frontend (usar Grafana Faro o similar)
- Scripts batch sin estado (solo logs inicio/fin)
- Funciones Lambda (health checks responsabilidad de AWS)

## 3. Tecnologías Aprobadas

| Componente            | Tecnología                                   | Versión mínima | Observaciones                          |
| --------------------- | -------------------------------------------- | -------------- | -------------------------------------- |
| **Logger**            | Serilog + Serilog.AspNetCore                 | 3.1+ / 8.0+    | Logging estructurado .NET              |
| **OpenTelemetry**     | OpenTelemetry .NET                           | 1.7+           | Instrumentación automática             |
| **Health Checks**     | AspNetCore.HealthChecks                      | 8.0+           | Endpoints /health/live y /health/ready |
| **Health Checks DB**  | HealthChecks.NpgSql, HealthChecks.Oracle     | 8.0+           | Checks PostgreSQL, Oracle              |
| **Exportador**        | OpenTelemetry.Exporter.OpenTelemetryProtocol | 1.7+           | OTLP a Grafana Alloy                   |
| **Collector**         | Grafana Alloy                                | 1.0+           | Recolector OpenTelemetry               |
| **Logs TSDB**         | Grafana Loki                                 | 2.9+           | Almacenamiento logs agregados          |
| **Métricas TSDB**     | Grafana Mimir                                | 2.10+          | Almacenamiento métricas                |
| **Tracing**           | Grafana Tempo                                | 2.3+           | Distributed tracing                    |
| **Visualización**     | Grafana                                      | 10.0+          | Dashboards y alertas                   |
| **Estándar contexto** | W3C Trace Context                            | 1.0            | Propagación traceparent/tracestate     |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

## 4. Logging Estructurado

### Requisitos Obligatorios 🔴

- [ ] Formato JSON estructurado en producción (NO texto plano)
- [ ] Correlation ID único por request (header `X-Correlation-ID`)
- [ ] Niveles de log: Information, Warning, Error, Critical (NO Trace/Debug en prod)
- [ ] Enmascaramiento de datos sensibles: passwords, tokens, API keys, PII
- [ ] Enrichers: MachineName, EnvironmentName, Application, Version
- [ ] Request logging automático: HTTP method, path, status code, elapsed time
- [ ] Logs a stdout/stderr (NO archivos en contenedores)
- [ ] Retención: Error=90d, Warning/Info=30d, Debug=7d
- [ ] Contexto en excepciones: UserId, CorrelationId, RequestPath
- [ ] Logs estructurados vía `ILogger<T>` (.NET)

### Prohibiciones

- ❌ Logs en texto plano en producción
- ❌ `Console.WriteLine()` directo (usar `ILogger<T>` estructurado)
- ❌ Passwords, tokens, API keys sin enmascarar
- ❌ Logs síncronos que bloquean requests (usar async sinks)
- ❌ Nivel Trace/Debug en producción (filtrar con MinimumLevel)
- ❌ Logs sin correlation ID en arquitecturas distribuidas

### Configuración Mínima

```csharp
// Program.cs
using Serilog;

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithProperty("Application", "TalmaAPI")
    .WriteTo.Console(new JsonFormatter())
    .WriteTo.OpenTelemetry(options => {
        options.Endpoint = "http://grafana-alloy:4317";
    })
    .CreateLogger();

builder.Host.UseSerilog();

// Middleware Correlation ID
app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-ID"].FirstOrDefault() ?? Guid.NewGuid().ToString();
    using (LogContext.PushProperty("CorrelationId", correlationId))
        await next();
});
```

## 5. Métricas y Monitoreo

### Requisitos Obligatorios 🔴

- [ ] Endpoint `/health/live` (liveness check) - responde 200 si app está viva
- [ ] Endpoint `/health/ready` (readiness check) - valida DB, cache, APIs externas
- [ ] Health checks con timeout 3s (evitar bloqueo prolongado)
- [ ] Métricas HTTP: latencia p50/p95/p99, throughput, error rate
- [ ] Métricas de infraestructura: CPU, memoria, threads, GC (.NET)
- [ ] Distributed tracing con trace ID único por request
- [ ] Correlation ID propagado entre servicios (header `X-Correlation-ID`)
- [ ] Exportación OpenTelemetry a Grafana Mimir (métricas) y Tempo (traces)
- [ ] Alertas en Grafana para: error rate >1%, latencia p95 >500ms, uptime `<99.9%`
- [ ] Golden Signals monitoreados: Latency, Traffic, Errors, Saturation

### Prohibiciones

- ❌ Health checks sin timeout (pueden bloquear probes indefinidamente)
- ❌ Health check `/health` único (separar liveness/readiness)
- ❌ Métricas solo en logs (usar métricas estructuradas exportables)
- ❌ Distributed tracing deshabilitado en arquitecturas de microservicios
- ❌ Alarmas sin umbrales definidos (evitar alertas sin contexto)
- ❌ Métricas de negocio mezcladas con métricas técnicas (separar namespaces)

### Configuración Mínima

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Health Checks
builder.Services.AddHealthChecks()
    .AddNpgSql(builder.Configuration.GetConnectionString("DefaultConnection")!,
               name: "postgres", tags: new[] { "ready" }, timeout: TimeSpan.FromSeconds(3))
    .AddRedis(builder.Configuration.GetConnectionString("Redis")!,
              name: "redis", tags: new[] { "ready" })
    .AddCheck("self", () => HealthCheckResult.Healthy(), tags: new[] { "live" });

// OpenTelemetry Metrics
builder.Services.AddOpenTelemetry()
    .WithMetrics(m => m
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter(options => {
            options.Endpoint = new Uri("http://grafana-alloy:4317");
        }));

var app = builder.Build();

app.MapHealthChecks("/health/live", new() { Predicate = c => c.Tags.Contains("live") });
app.MapHealthChecks("/health/ready", new() { Predicate = c => c.Tags.Contains("ready") });

app.Run();
```

## 6. Distributed Tracing

### Requisitos Obligatorios 🔴

- [ ] Propagación de W3C Trace Context (`traceparent`, `tracestate`) en headers HTTP y metadata de mensajes
- [ ] Instrumentación automática de HTTP clients, gRPC, database drivers
- [ ] Spans con atributos estándar: `http.method`, `http.status_code`, `db.statement`, `messaging.system`
- [ ] Sampling adaptativo: 100% errores, 10% requests exitosos en producción
- [ ] Integración con logs: `trace_id` y `span_id` en contexto de logging

### Configuración Mínima

```csharp
// Program.cs
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("mi-servicio"))
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddSqlClientInstrumentation()
        .AddOtlpExporter(options =>
        {
            options.Endpoint = new Uri("http://alloy:4317");
        }));
```

### Propagación Manual en Mensajería

```csharp
// Producer
var activity = Activity.Current;
message.Attributes["traceparent"] = activity?.Id;

// Consumer
Activity.Current = new Activity("ProcessMessage")
    .SetParentId(message.Attributes["traceparent"]);
```

## 7. Correlation IDs

### Header HTTP Estándar

```
X-Correlation-ID: <UUID v4>
```

**Reglas:**

- Generado por API Gateway o primer servicio si no existe
- Propagado en **todos** los headers HTTP downstream
- Inmutable: nunca se regenera durante el flujo
- Formato: UUID v4 (ejemplo: `550e8400-e29b-41d4-a716-446655440000`)

### Requisitos Obligatorios 🔴

- [ ] Incluir `X-Correlation-ID` en **todos** los logs estructurados
- [ ] Propagar en headers HTTP de llamadas downstream
- [ ] Incluir en headers de mensajes Apache Kafka
- [ ] Retornar en response headers para debugging
- [ ] Validar formato UUID v4, rechazar si inválido

### Implementación Middleware

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

### Propagación en HttpClient

```csharp
services.AddHttpClient("downstream-service")
    .AddHeaderPropagation(options =>
        options.Headers.Add("X-Correlation-ID"));

services.AddHeaderPropagation();
```

### Contexto de Mensajería

```json
{
  "messageAttributes": {
    "correlationId": {
      "dataType": "String",
      "stringValue": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

### Relación con Tracing

`X-Correlation-ID` complementa W3C Trace Context:

- **Correlation ID:** Identificador de negocio, inmutable, generado en entry point
- **Trace ID:** Identificador técnico OpenTelemetry, puede variar por servicio

Ambos deben estar presentes en logs para máxima trazabilidad.

## 8. Health Checks

### Tipos de Health Checks

#### Liveness Probe

**Propósito:** Detectar si el proceso está "vivo" (no bloqueado, no deadlocked).

**Criterio:** Responde 200 OK si el proceso puede responder requests básicos.

**Acción en fallo:** Orquestador reinicia el contenedor.

**Endpoint:** `GET /health/live`

#### Readiness Probe

**Propósito:** Detectar si el servicio está listo para recibir tráfico (DB conectada, dependencias disponibles).

**Criterio:** Responde 200 OK si todas las dependencias críticas están funcionales.

**Acción en fallo:** Orquestador retira el pod del pool de balanceo (no lo reinicia).

**Endpoint:** `GET /health/ready`

### Requisitos Obligatorios 🔴

- [ ] Ambos endpoints deben responder en `<500ms` (timeout corto para evitar cascading failures)
- [ ] NO autenticar health checks (públicos para orquestadores)
- [ ] Readiness debe validar: DB connection pool, APIs externas críticas, colas de mensajes
- [ ] Liveness debe ser simple y rápido (solo validar proceso vivo)
- [ ] Responder con código HTTP apropiado:
  - `200 OK`: Healthy
  - `503 Service Unavailable`: Unhealthy
- [ ] Incluir detalles en response body:

```json
{
  "status": "Healthy",
  "checks": {
    "database": "Healthy",
    "cache": "Degraded",
    "externalApi": "Healthy"
  },
  "duration": "00:00:00.0234567"
}
```

### Implementación con Microsoft.Extensions.Diagnostics.HealthChecks

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "database", tags: new[] { "ready" })
    .AddRedis(redisConnection, name: "cache", tags: new[] { "ready" })
    .AddUrlGroup(new Uri("https://api.externa.com/health"), name: "externalApi", tags: new[] { "ready" });

var app = builder.Build();

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false // No ejecuta checks, solo ping
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready"),
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});
```

### AWS ECS Fargate Probes

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: mi-servicio
      livenessProbe:
        httpGet:
          path: /health/live
          port: 8080
        initialDelaySeconds: 10
        periodSeconds: 10
        timeoutSeconds: 1
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /health/ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 5
        timeoutSeconds: 1
        failureThreshold: 2
```

### AWS ECS Task Definition

```json
{
  "healthCheck": {
    "command": [
      "CMD-SHELL",
      "curl -f http://localhost:8080/health/live || exit 1"
    ],
    "interval": 30,
    "timeout": 5,
    "retries": 3,
    "startPeriod": 60
  }
}
```

### Mejores Prácticas

- **Liveness ligero:** NO validar dependencias externas (evitar false positives)
- **Readiness exhaustivo:** Validar DB, cache, APIs críticas
- **Timeouts cortos:** `<500ms` para evitar timeout cascades
- **Degradación parcial:** Readiness puede retornar 200 con warnings si puede operar parcialmente
- **Métricas:** Emitir métrica de health check failures para alertas

## 9. Validación

### Logging

**Comandos de validación:**

```bash
# Verificar formato JSON
jq . logs/app.json

# Verificar correlation IDs
grep "CorrelationId" logs/app.json | jq '.CorrelationId'

# Verificar niveles de log
jq '.Level' logs/app.json | sort | uniq

# Verificar NO hay passwords sin enmascarar
grep -i "password" logs/app.json

# Tests unitarios
dotnet test --filter Category=Logging
```

**Métricas de cumplimiento:**

| Métrica                   | Target | Verificación                       |
| ------------------------- | ------ | ---------------------------------- | --------------------- |
| Logs en JSON              | 100%   | `jq` parse exitoso                 |
| Correlation ID presente   | 100%   | `grep CorrelationId`               |
| Passwords enmascarados    | 100%   | `grep -i password` retorna 0       |
| Nivel Debug/Trace en prod | 0%     | Grafana Loki query: `{app="talma"} | = "Debug" or "Trace"` |

### Métricas y Health Checks

**Comandos de validación:**

```bash
# Health checks
curl http://localhost:8080/health/live
curl http://localhost:8080/health/ready

# Métricas (exportadas a Grafana Alloy)
curl http://localhost:8080/metrics | grep http_request_duration

# Distributed tracing (verificar trace ID en logs)
curl -H "X-Correlation-ID: test-123" http://localhost:8080/api/users
grep "test-123" logs/app.json

# Tests de health checks
dotnet test --filter Category=HealthChecks
```

**Métricas de cumplimiento:**

| Métrica                   | Target   | Verificación                                                    |
| ------------------------- | -------- | --------------------------------------------------------------- | ---- | -------------------- |
| Uptime                    | ≥ 99.9%  | Grafana Mimir: `up{job="talma-api"}`                            |
| Latencia p95              | `<200ms` | Grafana Mimir: `http_request_duration_seconds{quantile="0.95"}` |
| Error rate                | `<1%`    | `http_requests_total{status=~"5.."} / http_requests_total`      |
| Health check timeout      | ≤ 3s     | Código: `timeout: TimeSpan.FromSeconds(3)`                      |
| Traces con correlation ID | 100%     | Grafana Loki: `{app="talma"}                                    | json | correlationId != ""` |

### Distributed Tracing

**Pre-producción:**

- Verificar propagación de `traceparent` en llamadas HTTP/gRPC
- Confirmar visualización de traces en Grafana Tempo
- Validar correlación trace ↔ logs vía `trace_id`

**Post-producción:**

- P95 latency por servicio visible en dashboards
- Alertas configuradas para spans con errores

### Correlation IDs

**Criterios de Aceptación:**

- Logs de servicios diferentes comparten mismo `CorrelationId` para un request
- Header presente en responses HTTP
- Queries en Grafana/Loki por `correlationId` retornan flujo completo

### Health Checks

**Pre-producción:**

- Simular fallo de DB y validar readiness retorna 503
- Validar liveness no se afecta por fallo de dependencias
- Confirmar tiempos de respuesta `<500ms` bajo carga

**Post-producción:**

- Monitorear restarts automáticos por liveness failures
- Alertas si >10% pods unhealthy por >5min

## 10. Prohibiciones Generales

- ❌ Logs en texto plano en producción
- ❌ Health checks sin timeout
- ❌ Métricas solo en logs (usar métricas estructuradas exportables)
- ❌ Distributed tracing deshabilitado en arquitecturas de microservicios
- ❌ Passwords, tokens, API keys sin enmascarar
- ❌ Logs síncronos que bloquean requests
- ❌ Nivel Trace/Debug en producción
- ❌ Alarmas sin umbrales definidos

## 10. SLOs y SLAs

Definir **SLOs** (Service Level Objectives) por servicio: Availability ≥99.9%, Latency p95 `<500ms`, Error rate `<1%`. Implementar **error budgets** (1-SLO) para balancear reliability y velocidad de desarrollo. Alertas basadas en **burn rate** de error budget, no métricas absolutas.

**Referencia:** [Google SRE - SLO](https://sre.google/sre-book/service-level-objectives/)

---

## 11. Prohibiciones Generales

- [ADR-016: Logging Estructurado](../../decisiones-de-arquitectura/adr-016-logging-estructurado.md)
- [ADR-021: Observabilidad](../../decisiones-de-arquitectura/adr-021-observabilidad.md)
- [Serilog Documentation](https://serilog.net/)
- [OpenTelemetry Documentation](https://opentelemetry.io/)
- [AspNetCore.HealthChecks](https://github.com/Xabaril/AspNetCore.Diagnostics.HealthChecks)
- [W3C Trace Context Specification](https://www.w3.org/TR/trace-context/)
- [Microsoft Docs - Health Checks](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks)
