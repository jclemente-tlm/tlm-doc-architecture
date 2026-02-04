---
id: slos-slas
sidebar_position: 7
title: SLOs y SLAs
description: Estándar para Service Level Indicators (SLI), Objectives (SLO) y Agreements (SLA) con error budgets, monitoring y alerting según Google SRE
---

# Estándar Técnico — SLOs y SLAs

---

## 1. Propósito

Definir Service Level Indicators (SLI), Service Level Objectives (SLO) y Service Level Agreements (SLA) con error budgets para balancear reliability y velocity, implementando monitoring con Prometheus/Grafana y alerting basado en burn rate.

---

## 2. Alcance

**Aplica a:**

- APIs públicas y privadas
- Servicios backend
- Integraciones críticas
- Bases de datos
- Message brokers

**No aplica a:**

- Ambientes de desarrollo
- Features experimentales (beta)

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología         | Versión mínima | Observaciones      |
| ------------------- | ------------------ | -------------- | ------------------ |
| **Metrics**         | Prometheus         | 2.45+          | Time-series DB     |
| **Dashboards**      | Grafana            | 10.0+          | Visualización      |
| **Alerting**        | Alertmanager       | 0.26+          | Alert routing      |
| **Instrumentation** | OpenTelemetry      | 1.0+           | Metrics collection |
| **SLO Tracking**    | Grafana SLO plugin | -              | SLO dashboards     |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### SLIs (Service Level Indicators)

- [ ] **Availability**: % de requests exitosos (HTTP 2xx/3xx)
- [ ] **Latency**: p50, p95, p99 response time
- [ ] **Throughput**: Requests por segundo
- [ ] **Error rate**: % de errores (HTTP 5xx)

### SLOs (Service Level Objectives)

- [ ] **Availability target**: ≥99.9% (3 nines)
- [ ] **Latency target**: p95 < 500ms, p99 < 1000ms
- [ ] **Error budget**: 0.1% (43.2 min/mes downtime)
- [ ] **Measurement window**: 30 días rolling

### SLAs (Service Level Agreements)

- [ ] **Availability guarantee**: ≥99.5% (menor que SLO)
- [ ] **Penalties**: Créditos por incumplimiento
- [ ] **Exclusions**: Mantenimiento planificado, fuerza mayor

### Alerting

- [ ] **Burn rate alerts**: No alertar en % directo, usar burn rate
- [ ] **Multi-window**: Ventanas 1h (fast burn) + 6h (slow burn)
- [ ] **Actionable**: Alerts con runbooks claros

---

## 5. Definiciones (Google SRE)

### Conceptos Clave

```text
SLI (Service Level Indicator)
  - Métrica cuantitativa de un aspecto del servicio
  - Ejemplos: availability, latency, throughput
  - Medición: ratio de good events / valid events

SLO (Service Level Objective)
  - Target value o rango para un SLI
  - Ejemplo: 99.9% de requests con latency < 500ms
  - Interno: No tiene penalidades

SLA (Service Level Agreement)
  - Contrato con penalidades por incumplimiento
  - Ejemplo: 99.5% availability o crédito de servicio
  - Externo: Con clientes

Error Budget
  - 100% - SLO = margen de error permitido
  - Ejemplo: SLO 99.9% → Error Budget 0.1%
  - Uso: Balancear reliability vs velocity
```

### Relación SLI → SLO → SLA

```text
SLI: availability = successful_requests / total_requests = 99.95%
SLO: availability ≥ 99.9% (target interno)
SLA: availability ≥ 99.5% (garantía contractual)

✅ SLI (99.95%) > SLO (99.9%) > SLA (99.5%) → TODO OK
```

---

## 6. SLOs Recomendados por Servicio

### Payment API (Crítico)

```yaml
slos:
  availability:
    target: 99.9% # 3 nines
    measurement: 30d # Rolling 30 días
    error_budget: 0.1% # 43.2 min/mes downtime

  latency:
    p95: 500ms
    p99: 1000ms
    measurement: 30d

  error_rate:
    target: < 0.1% # Menos de 0.1% errores 5xx
    measurement: 30d

sla:
  availability: 99.5% # 2 nines (menor que SLO)
  penalties:
    - threshold: < 99.5%
      credit: 10%
    - threshold: < 99.0%
      credit: 25%
```

### Customer API (Estándar)

```yaml
slos:
  availability:
    target: 99.5% # 2.5 nines
    error_budget: 0.5% # 216 min/mes downtime

  latency:
    p95: 1000ms
    p99: 2000ms

sla:
  availability: 99.0%
```

---

## 7. Prometheus - Métricas SLI

### Instrumentación .NET

```csharp
// Metrics/SliMetrics.cs
using Prometheus;

public class SliMetrics
{
    // Counter de requests totales
    private static readonly Counter RequestsTotal = Metrics
        .CreateCounter(
            "http_requests_total",
            "Total HTTP requests",
            new[] { "method", "endpoint", "status_code" });

    // Histogram de latencia
    private static readonly Histogram RequestDuration = Metrics
        .CreateHistogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            new HistogramConfiguration
            {
                LabelNames = new[] { "method", "endpoint" },
                Buckets = new[] { 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0 }
            });

    public static void RecordRequest(string method, string endpoint, int statusCode, double durationSeconds)
    {
        RequestsTotal.WithLabels(method, endpoint, statusCode.ToString()).Inc();
        RequestDuration.WithLabels(method, endpoint).Observe(durationSeconds);
    }
}

// Middleware/SliMiddleware.cs
public class SliMiddleware
{
    private readonly RequestDelegate _next;

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

            SliMetrics.RecordRequest(
                context.Request.Method,
                context.Request.Path,
                context.Response.StatusCode,
                stopwatch.Elapsed.TotalSeconds);
        }
    }
}

// Program.cs
app.UseMiddleware<SliMiddleware>();
app.MapMetrics();  // /metrics endpoint para Prometheus
```

### PromQL - Calcular SLIs

```promql
# SLI: Availability (% de requests exitosos)
availability_30d =
  sum(rate(http_requests_total{status_code=~"2..|3.."}[30d]))
  /
  sum(rate(http_requests_total[30d]))
  * 100

# SLI: Error rate (% de errores 5xx)
error_rate_30d =
  sum(rate(http_requests_total{status_code=~"5.."}[30d]))
  /
  sum(rate(http_requests_total[30d]))
  * 100

# SLI: Latency p95
latency_p95 =
  histogram_quantile(0.95,
    sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
  )

# SLI: Latency p99
latency_p99 =
  histogram_quantile(0.99,
    sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
  )
```

---

## 8. Error Budget

### Cálculo

```text
SLO: 99.9% availability
Error Budget: 100% - 99.9% = 0.1%

En 30 días (43,200 minutos):
Downtime permitido = 43,200 * 0.001 = 43.2 minutos

En 7 días:
Downtime permitido = 10,080 * 0.001 = 10.08 minutos
```

### Consumo de Error Budget

```promql
# Error budget consumido (30 días)
error_budget_consumed =
  (
    1 - (sum(rate(http_requests_total{status_code=~"2..|3.."}[30d]))
         / sum(rate(http_requests_total[30d])))
  )
  / 0.001  # Error budget total (0.1%)
  * 100    # Porcentaje consumido

# Error budget restante
error_budget_remaining = 100 - error_budget_consumed
```

### Políticas de Error Budget

```yaml
error_budget_policy:
  # > 50% error budget restante: Velocity normal
  - remaining: "> 50%"
    policy: "Deploy features normalmente"

  # 25-50% error budget restante: Precaución
  - remaining: "25-50%"
    policy: "Revisar rollouts, aumentar testing"

  # < 25% error budget restante: Congelar features
  - remaining: "< 25%"
    policy: "Feature freeze, solo hotfixes de reliability"

  # Error budget agotado
  - remaining: "0%"
    policy: "STOP deployments, focus 100% en reliability"
```

---

## 9. Alerting - Burn Rate

### Multi-Window Multi-Burn-Rate Alerts

```yaml
# prometheus/alerts.yml
groups:
  - name: slo_alerts
    rules:
      # Fast burn (1 hora): Consumiendo error budget a 14.4x
      - alert: ErrorBudgetFastBurn
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[1h]))
            / sum(rate(http_requests_total[1h]))
          ) > (14.4 * 0.001)  # 14.4x error budget (0.1%)
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error budget consuming too fast (1h window)"
          description: "At this rate, error budget will be consumed in 2 days"

      # Slow burn (6 horas): Consumiendo error budget a 6x
      - alert: ErrorBudgetSlowBurn
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[6h]))
            / sum(rate(http_requests_total[6h]))
          ) > (6 * 0.001)  # 6x error budget
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Error budget consuming steadily (6h window)"

      # Latency SLO violation
      - alert: LatencySloViolation
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 0.5  # p95 > 500ms
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 latency exceeds 500ms SLO"
```

---

## 10. Grafana - SLO Dashboard

### Dashboard JSON

```json
{
  "dashboard": {
    "title": "Payment API - SLOs",
    "panels": [
      {
        "title": "Availability (30d)",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status_code=~\"2..|3..\"}[30d])) / sum(rate(http_requests_total[30d])) * 100"
          }
        ],
        "thresholds": [
          { "value": 99.9, "color": "green" },
          { "value": 99.5, "color": "yellow" },
          { "value": 0, "color": "red" }
        ]
      },
      {
        "title": "Error Budget Remaining (30d)",
        "targets": [
          {
            "expr": "100 - ((1 - (sum(rate(http_requests_total{status_code=~\"2..|3..\"}[30d])) / sum(rate(http_requests_total[30d])))) / 0.001 * 100)"
          }
        ]
      },
      {
        "title": "Latency p95 vs SLO (500ms)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) * 1000",
            "legendFormat": "p95"
          }
        ],
        "thresholds": [{ "value": 500, "color": "red" }]
      }
    ]
  }
}
```

---

## 11. Validación de Cumplimiento

```bash
# Verificar métricas expuestas
curl http://localhost:8080/metrics | grep http_requests_total

# Query Prometheus: Availability actual
curl -G 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=sum(rate(http_requests_total{status_code=~"2..|3.."}[30d])) / sum(rate(http_requests_total[30d])) * 100'

# Verificar alerts configurados
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.type=="alerting")'

# Test: Simular carga y verificar SLI
for i in {1..1000}; do
  curl -s http://localhost:8080/api/payments > /dev/null
done
```

---

## 12. Referencias

**Google SRE:**

- [Google SRE Book - Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)

**Prometheus:**

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Histogram and Summary](https://prometheus.io/docs/practices/histograms/)
