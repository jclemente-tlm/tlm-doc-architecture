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
- APIs REST (.NET, Node.js) con dependencies (PostgreSQL, Redis, APIs externas)
- Microservicios con SLOs definidos (uptime 99.9%, latencia p95 < 200ms)
- Sistemas distribuidos (distributed tracing obligatorio)

**No aplica a:**
- Aplicaciones frontend (usar Datadog RUM / CloudWatch RUM)
- Scripts batch sin estado (solo logs inicio/fin)
- Lambdas AWS (CloudWatch Metrics automático)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Health Checks .NET** | AspNetCore.HealthChecks | 8.0+ | Endpoints /health/live y /health/ready |
| **Health Checks DB** | HealthChecks.NpgSql, HealthChecks.Redis | 8.0+ | Checks para PostgreSQL, Redis |
| **Métricas .NET** | OpenTelemetry.Instrumentation.AspNetCore | 1.6+ | Auto-instrumentación HTTP |
| **Métricas Node.js** | prom-client | 15.0+ | Exportación formato Prometheus |
| **Tracing** | Jaeger, AWS X-Ray | 1.50+ | Distributed tracing backend |
| **Exportación** | Prometheus.AspNetCore | 8.2+ | Endpoint /metrics formato Prometheus |
| **Centralización** | AWS CloudWatch | - | Métricas, logs, alarmas centralizadas |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Endpoint `/health/live` (liveness probe K8s) - responde 200 si app está viva
- [ ] Endpoint `/health/ready` (readiness probe K8s) - valida DB, cache, APIs externas
- [ ] Health checks con timeout 3s (evitar bloqueo prolongado)
- [ ] Métricas HTTP: latencia p50/p95/p99, throughput, error rate
- [ ] Métricas de infraestructura: CPU, memoria, threads, GC (.NET)
- [ ] Distributed tracing con trace ID único por request
- [ ] Correlation ID propagado entre servicios (header `X-Correlation-ID`)
- [ ] Exportación formato Prometheus en endpoint `/metrics`
- [ ] Alarmas CloudWatch para: error rate > 1%, latencia p95 > 500ms, uptime < 99.9%
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
        .AddPrometheusExporter());

var app = builder.Build();

app.MapHealthChecks("/health/live", new() { Predicate = c => c.Tags.Contains("live") });
app.MapHealthChecks("/health/ready", new() { Predicate = c => c.Tags.Contains("ready") });
app.MapPrometheusScrapingEndpoint("/metrics");

app.Run();
```

### Node.js
```typescript
import promClient from 'prom-client';
import express from 'express';

const app = express();
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

// Health Checks
app.get('/health/live', (req, res) => res.status(200).json({ status: 'UP' }));
app.get('/health/ready', async (req, res) => {
  try {
    await db.query('SELECT 1'); // PostgreSQL check
    await redis.ping();          // Redis check
    res.status(200).json({ status: 'UP' });
  } catch (error) {
    res.status(503).json({ status: 'DOWN', error: error.message });
  }
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

---

## 7. Validación

**Comandos de validación:**

```bash
# Health checks
curl http://localhost:8080/health/live
curl http://localhost:8080/health/ready

# Métricas Prometheus
curl http://localhost:8080/metrics | grep http_request_duration

# Distributed tracing (verificar trace ID en logs)
curl -H "X-Correlation-ID: test-123" http://localhost:8080/api/users
grep "test-123" logs/app.json

# Tests de health checks
dotnet test --filter Category=HealthChecks
npm test -- --grep "health checks"
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|
| Uptime | ≥ 99.9% | CloudWatch Metric `ServiceAvailability` |
| Latencia p95 | < 200ms | Prometheus `http_request_duration_seconds{quantile="0.95"}` |
| Error rate | < 1% | `http_requests_total{status=~"5.."} / http_requests_total` |
| Health check timeout | ≤ 3s | Código: `timeout: TimeSpan.FromSeconds(3)` |
| Traces con correlation ID | 100% | CloudWatch Insights: `fields @timestamp | filter correlationId exists` |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-021: Observabilidad](../../../decisiones-de-arquitectura/adr-021-observabilidad.md)
- [Logging Estructurado](./01-logging.md)
- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [AspNetCore.HealthChecks](https://github.com/Xabaril/AspNetCore.Diagnostics.HealthChecks)
