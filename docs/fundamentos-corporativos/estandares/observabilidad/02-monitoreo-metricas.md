---
id: monitoreo-metricas
sidebar_position: 2
title: Monitoreo y Métricas  
description: Estándares para health checks ASP.NET Core 8.0+, métricas OpenTelemetry 1.6+ y distributed tracing
---

# Estándar Técnico — Monitoreo y Métricas

---

## 1. Propósito
Garantizar disponibilidad y detectar anomalías mediante health checks (/health/live, /health/ready), métricas de performance (latencia p95, error rate) con OpenTelemetry y distributed tracing para correlacionar requests entre microservicios.

---

## 2. Alcance

**Aplica a:**
- APIs REST (.NET) con dependencies (PostgreSQL, Redis, APIs externas)
- Microservicios con SLOs definidos (uptime 99.9%, latencia p95 < 200ms)
- Sistemas distribuidos (distributed tracing obligatorio)

**No aplica a:**
- Aplicaciones frontend (usar Grafana Faro o similar)
- Scripts batch sin estado (solo logs inicio/fin)
- Lambdas AWS (usar OpenTelemetry)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Health Checks** | AspNetCore.HealthChecks | 8.0+ | Endpoints /health/live y /health/ready |
| **Health Checks DB** | HealthChecks.NpgSql, HealthChecks.Oracle | 8.0+ | Checks PostgreSQL, Oracle |
| **OpenTelemetry** | OpenTelemetry .NET | 1.7+ | Instrumentación automática |
| **Exportador** | OpenTelemetry.Exporter.OpenTelemetryProtocol | 1.7+ | OTLP a Grafana Alloy |
| **Collector** | Grafana Alloy | 1.0+ | Recolector OpenTelemetry |
| **Métricas TSDB** | Grafana Mimir | 2.10+ | Almacenamiento métricas |
| **Tracing** | Grafana Tempo | 2.3+ | Distributed tracing |
| **Visualización** | Grafana | 10.0+ | Dashboards y alertas |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Endpoint `/health/live` (liveness check) - responde 200 si app está viva
- [ ] Endpoint `/health/ready` (readiness check) - valida DB, cache, APIs externas
- [ ] Health checks con timeout 3s (evitar bloqueo prolongado)
- [ ] Métricas HTTP: latencia p50/p95/p99, throughput, error rate
- [ ] Métricas de infraestructura: CPU, memoria, threads, GC (.NET)
- [ ] Distributed tracing con trace ID único por request
- [ ] Correlation ID propagado entre servicios (header `X-Correlation-ID`)
- [ ] Exportación OpenTelemetry a Grafana Mimir (métricas) y Tempo (traces)
- [ ] Alertas en Grafana para: error rate > 1%, latencia p95 > 500ms, uptime < 99.9%
- [ ] Golden Signals monitoreados: Latency, Traffic, Errors, Saturation

---

## 5. Prohibiciones

- ❌ Health checks sin timeout (pueden bloquear probes indefinidamente)
- ❌ Health check `/health` único (separar liveness/readiness)
- ❌ Métricas solo en logs (usar métricas estructuradas exportables)
- ❌ Distributed tracing deshabilitado en arquitecturas de microservicios
- ❌ Alarmas sin umbrales definidos (evitar alertas sin contexto)
- ❌ Métricas de negocio mezcladas con métricas técnicas (separar namespaces)

---

## 6. Configuración Mínima

### .NET
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

---

## 7. Validación

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

| Métrica | Target | Verificación |
|---------|--------|--------------|
| Uptime | ≥ 99.9% | Grafana Mimir: `up{job="talma-api"}` |
| Latencia p95 | < 200ms | Grafana Mimir: `http_request_duration_seconds{quantile="0.95"}` |
| Error rate | < 1% | `http_requests_total{status=~"5.."} / http_requests_total` |
| Health check timeout | ≤ 3s | Código: `timeout: TimeSpan.FromSeconds(3)` |
| Traces con correlation ID | 100% | Grafana Loki: `{app="talma"} | json | correlationId != ""` |

---

## 8. Referencias

- [ADR-021: Observabilidad](../../../decisiones-de-arquitectura/adr-021-observabilidad.md)
- [Logging Estructurado](./01-logging.md)
- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [AspNetCore.HealthChecks](https://github.com/Xabaril/AspNetCore.Diagnostics.HealthChecks)
