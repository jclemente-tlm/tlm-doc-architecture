---
id: slo-sla
sidebar_position: 5
title: SLIs, SLOs y SLAs
description: Definición de Service Level Indicators, Objectives y Agreements
---

# SLIs, SLOs y SLAs

## Contexto

Este estándar define cómo establecer Service Level Indicators (SLIs), Service Level Objectives (SLOs) y Service Level Agreements (SLAs) para medir y garantizar niveles de servicio. Complementa el [lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) especificando **qué** medir y **qué** objetivos cumplir.

---

## Stack Tecnológico

| Componente          | Tecnología       | Versión | Uso                       |
| ------------------- | ---------------- | ------- | ------------------------- |
| **Storage**         | Grafana Mimir    | 2.10+   | Almacenamiento métricas   |
| **Visualización**   | Grafana          | 10.0+   | Dashboards y SLO tracking |
| **Alerting**        | Grafana Alerting | 10.0+   | Alertas basadas en SLOs   |
| **Instrumentación** | OpenTelemetry    | 1.7+    | Métricas                  |

---

## Implementación Técnica

### SLI - Service Level Indicators (Qué Medir)

```yaml
# SLIs comunes por servicio REST API
slis:
  # ✅ Availability - Uptime del servicio
  availability:
    description: "% de requests exitosos (no 5xx)"
    metric: "http.server.request.duration"
    good_events: "status_code < 500"
    total_events: "all requests"
    formula: "success_rate = good_events / total_events * 100"

  # ✅ Latency - Tiempo de respuesta
  latency:
    description: "% de requests que responden en < 500ms"
    metric: "http.server.request.duration"
    good_events: "duration < 500ms"
    total_events: "all requests"
    formula: "fast_requests = good_events / total_events * 100"

  # ✅ Quality - Requests sin errores de validación
  quality:
    description: "% de requests sin errores 4xx (excepto 404, 429)"
    metric: "http.server.request.duration"
    good_events: "status_code not in [400, 422]"
    total_events: "all requests"
    formula: "quality_rate = good_events / total_events * 100"

  # ✅ Throughput - Capacidad de procesamiento
  throughput:
    description: "Requests procesados por segundo"
    metric: "http.server.request.duration"
    formula: "rate(http_server_request_duration_count[5m])"
```

### SLO - Service Level Objectives (Objetivos)

```yaml
# orders-api SLOs
service: orders-api
slos:
  # ✅ SLO de Availability
  - name: availability_slo
    sli: availability
    objective: 99.9% # "three nines"
    window: 30d # Rolling 30 días
    error_budget: 0.1% # 1 - 0.999 = 0.001 = 0.1%
    # Error budget = 43.2 minutos de downtime por mes

  # ✅ SLO de Latency
  - name: latency_p95_slo
    sli: latency
    objective: 95% # 95% de requests < 500ms
    threshold: 500ms
    percentile: p95
    window: 7d

  - name: latency_p99_slo
    sli: latency
    objective: 99% # 99% de requests < 1000ms
    threshold: 1000ms
    percentile: p99
    window: 7d

  # ✅ SLO de Quality
  - name: quality_slo
    sli: quality
    objective: 99.5% # 99.5% sin errores 4xx
    window: 30d
    error_budget: 0.5%

# Cálculo de Error Budget
# Objective: 99.9% availability
# Error Budget: 100% - 99.9% = 0.1%
# En 30 días (43,200 minutos):
#   - Allowed downtime: 43,200 * 0.001 = 43.2 minutos/mes
#   - Max error requests: Total requests * 0.001
```

### Implementación de SLIs con Métricas

```csharp
// SLI Metrics Implementation
using System.Diagnostics.Metrics;

public class SliMetrics
{
    private static readonly Meter _meter = new("Talma.Orders.SLI", "1.0.0");

    // ✅ Counter de requests totales
    private static readonly Counter<long> _totalRequests = _meter.CreateCounter<long>(
        name: "sli.http.requests.total",
        unit: "requests",
        description: "Total HTTP requests"
    );

    // ✅ Counter de requests exitosos (no 5xx)
    private static readonly Counter<long> _successfulRequests = _meter.CreateCounter<long>(
        name: "sli.http.requests.successful",
        unit: "requests",
        description: "Successful HTTP requests (status < 500)"
    );

    // ✅ Histogram de latencia
    private static readonly Histogram<double> _requestDuration = _meter.CreateHistogram<double>(
        name: "sli.http.request.duration",
        unit: "ms",
        description: "HTTP request duration for SLI tracking"
    );

    public void RecordRequest(HttpContext context, TimeSpan duration)
    {
        var statusCode = context.Response.StatusCode;
        var endpoint = context.Request.Path.Value;

        // Total requests
        _totalRequests.Add(1, new TagList
        {
            { "endpoint", endpoint },
            { "method", context.Request.Method }
        });

        // Successful requests (availability SLI)
        if (statusCode < 500)
        {
            _successfulRequests.Add(1, new TagList
            {
                { "endpoint", endpoint }
            });
        }

        // Latency SLI
        _requestDuration.Record(
            duration.TotalMilliseconds,
            new TagList
            {
                { "endpoint", endpoint },
                { "status_code", statusCode.ToString() },
                { "fast", duration.TotalMilliseconds < 500 ? "true" : "false" }
            }
        );
    }
}

// Middleware para capturar SLIs
public class SliMiddleware
{
    private readonly RequestDelegate _next;
    private readonly SliMetrics _sliMetrics;

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
            _sliMetrics.RecordRequest(context, stopwatch.Elapsed);
        }
    }
}
```

### Queries PromQL para SLOs

```promql
# ✅ Availability SLO (99.9%)
# Success rate = successful requests / total requests
sum(rate(sli_http_requests_successful_total[30d]))
/
sum(rate(sli_http_requests_total[30d]))
* 100

# ✅ Resultado esperado: >= 99.9

# ✅ Error Budget Remaining
# Current success rate vs target
(
  sum(rate(sli_http_requests_successful_total[30d]))
  /
  sum(rate(sli_http_requests_total[30d]))
  - 0.999  # SLO target
)
* 100
/ 0.1  # Error budget

# ✅ Resultado:
# > 0 = Error budget remaining
# < 0 = SLO violated

# ✅ Latency SLO P95 < 500ms
histogram_quantile(0.95,
  sum(rate(sli_http_request_duration_bucket[7d])) by (le)
)
< 500

# ✅ Latency SLO P99 < 1000ms
histogram_quantile(0.99,
  sum(rate(sli_http_request_duration_bucket[7d])) by (le)
)
< 1000

# ✅ % de requests rápidos (< 500ms)
sum(rate(sli_http_request_duration_count{fast="true"}[7d]))
/
sum(rate(sli_http_request_duration_count[7d]))
* 100

# ✅ Quality SLO (no 4xx excepto 404, 429)
sum(rate(sli_http_requests_total{status_code!~"400|422"}[30d]))
/
sum(rate(sli_http_requests_total[30d]))
* 100
```

### SLA - Service Level Agreements

```yaml
# SLA Example - Orders API
service: orders-api
version: v1
effective_date: 2024-01-01

sla:
  # ✅ Commitment con clientes externos
  availability:
    commitment: 99.5% # Menor que SLO interno (99.9%)
    measurement_period: monthly
    exclusions:
      - planned_maintenance # Ventanas de mantenimiento notificadas
      - force_majeure # Eventos fuera de control
      - customer_errors # Errores 4xx causados por cliente

  latency:
    p95_threshold: 1000ms # Más laxo que SLO interno (500ms)
    measurement_period: monthly

  support:
    response_time:
      critical: 30m # P0: Servicio down
      high: 2h # P1: Degradación significativa
      medium: 8h # P2: Funcionalidad parcial afectada
      low: 24h # P3: Minor issues

  penalties:
    # Si disponibilidad < 99.5%
    - threshold: 99.5%
      penalty: 10% service credit
    - threshold: 99.0%
      penalty: 25% service credit
    - threshold: 98.0%
      penalty: 50% service credit

# ✅ SLO vs SLA
# SLO (interno): 99.9% - Objetivo operacional
# SLA (externo): 99.5% - Compromiso contractual
# Buffer: 0.4% - Margen para manejar incidentes sin violar SLA
```

### Documentación de SLOs por Servicio

````markdown
# orders-api SLOs

## Availability

- **Objetivo:** 99.9% uptime (three nines)
- **Medición:** % de requests con status code < 500
- **Ventana:** Rolling 30 días
- **Error Budget:** 43.2 minutos/mes
- **Query:**
  ```promql
  sum(rate(sli_http_requests_successful_total{service="orders-api"}[30d]))
  /
  sum(rate(sli_http_requests_total{service="orders-api"}[30d]))
  * 100
  ```
````

## Latency

- **Objetivo:** 95% de requests < 500ms (p95)
- **Medición:** Percentil 95 de duración HTTP
- **Ventana:** Rolling 7 días
- **Query:**
  ```promql
  histogram_quantile(0.95,
    sum(rate(sli_http_request_duration_bucket{service="orders-api"}[7d])) by (le)
  )
  ```

## Quality

- **Objetivo:** 99.5% sin errores de validación
- **Medición:** % de requests sin 400/422
- **Ventana:** Rolling 30 días
- **Error Budget:** 0.5%

````

### Error Budget Policy

```yaml
# error-budget-policy.yml
service: orders-api

policy:
  # ✅ Error budget healthy (> 50% remaining)
  - condition: error_budget_remaining > 50%
    actions:
      - allow_deployments: true
      - allow_experiments: true
      - allow_feature_flags: true
      - focus: "New features and optimizations"

  # ⚠️ Error budget warning (10-50% remaining)
  - condition: 10% < error_budget_remaining <= 50%
    actions:
      - allow_deployments: true
      - allow_experiments: false  # Pause experiments
      - require_review: true
      - focus: "Stability and bug fixes"

  # 🔴 Error budget exhausted (< 10% remaining)
  - condition: error_budget_remaining <= 10%
    actions:
      - freeze_deployments: true  # Excepto hotfixes
      - stop_experiments: true
      - disable_feature_flags: optional
      - focus: "Incident response and reliability"
      - postmortem_required: true

  # 💥 SLO violated
  - condition: slo_violated
    actions:
      - freeze_deployments: true
      - incident_severity: P1
      - notify: ["oncall", "engineering-manager", "product-owner"]
      - focus: "Immediate mitigation"
      - postmortem_required: true
      - review_slo: true  # Revisar si SLO es realista
````

### Dashboard de SLO en Grafana

```json
{
  "dashboard": {
    "title": "Orders API - SLO Dashboard",
    "panels": [
      {
        "title": "Availability SLO (99.9%)",
        "targets": [
          {
            "expr": "sum(rate(sli_http_requests_successful_total{service=\"orders-api\"}[30d])) / sum(rate(sli_http_requests_total{service=\"orders-api\"}[30d])) * 100",
            "legendFormat": "Current Availability"
          }
        ],
        "thresholds": [
          { "value": 99.9, "color": "green" },
          { "value": 99.5, "color": "yellow" },
          { "value": 99.0, "color": "red" }
        ]
      },
      {
        "title": "Error Budget Remaining",
        "targets": [
          {
            "expr": "((sum(rate(sli_http_requests_successful_total[30d])) / sum(rate(sli_http_requests_total[30d])) - 0.999) * 100 / 0.1) * 100",
            "legendFormat": "Error Budget %"
          }
        ]
      },
      {
        "title": "Latency P95 (Target: < 500ms)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(sli_http_request_duration_bucket{service=\"orders-api\"}[7d])) by (le))",
            "legendFormat": "P95 Latency"
          }
        ]
      }
    ]
  }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** definir SLIs para availability, latency y quality
- **MUST** establecer SLOs cuantificables (ej: 99.9% availability)
- **MUST** calcular error budgets basados en SLOs
- **MUST** medir SLOs con métricas de OpenTelemetry
- **MUST** usar ventanas rolling (30d, 7d) no calendarios
- **MUST** documentar SLOs en README del servicio
- **MUST** implementar Error Budget Policy
- **MUST** crear dashboards de SLO en Grafana
- **MUST** hacer SLO más estricto que SLA (buffer)

### SHOULD (Fuertemente recomendado)

- **SHOULD** definir múltiples SLOs (availability + latency + quality)
- **SHOULD** usar percentiles (p95, p99) para latencia
- **SHOULD** revisar SLOs trimestralmente
- **SHOULD** congelar deploys cuando error budget < 10%
- **SHOULD** hacer postmortem cuando SLO se viola
- **SHOULD** alertar en 80% error budget consumido
- **SHOULD** incluir error budget en planning

### MAY (Opcional)

- **MAY** definir SLOs por endpoint crítico
- **MAY** usar SLOs multiventana (7d, 30d, 90d)
- **MAY** implementar SLOs por tenant/cliente
- **MAY** usar SLI burn rate para alertas tempranas

### MUST NOT (Prohibido)

- **MUST NOT** usar SLO = 100% (imposible de alcanzar)
- **MUST NOT** cambiar SLOs frecuentemente (estabilidad)
- **MUST NOT** ignorar error budget en decisiones de deploy
- **MUST NOT** medir SLOs con métricas no observables
- **MUST NOT** hacer SLA más estricto que SLO (no hay buffer)

---

## Referencias

- [Lineamiento: Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md)
- Estándares relacionados:
  - [Métricas](metrics-standards.md)
  - [Alerting](alerting.md)
  - [Dashboards](dashboards.md)
- Especificaciones:
  - [Google SRE Book - SLIs, SLOs, SLAs](https://sre.google/sre-book/service-level-objectives/)
  - [Implementing SLOs](https://sre.google/workbook/implementing-slos/)
  - [Error Budgets](https://sre.google/workbook/error-budget-policy/)
