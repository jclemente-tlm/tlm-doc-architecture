---
id: slo-sla
sidebar_position: 6
title: SLO y SLA
description: Estándar para definición de Service Level Objectives (SLOs), Service Level Agreements (SLAs) y gestión de error budget con Grafana y Mimir.
tags: [observabilidad, slo, sla, grafana, mimir]
---

# SLO y SLA

## Contexto

Este estándar define cómo establecer, medir y gestionar Service Level Objectives (SLOs) y Service Level Agreements (SLAs) usando métricas de OpenTelemetry y Grafana. Complementa el lineamiento [Observabilidad](../../lineamientos/arquitectura/observabilidad.md) asegurando que la confiabilidad del servicio se mida con datos objetivos y se gestione con un error budget explícito.

**Conceptos incluidos:**

- **SLO (Service Level Objective)** — Objetivo interno de confiabilidad medible
- **SLA (Service Level Agreement)** — Acuerdo contractual con penalidades
- **Error budget** — Margen de error permitido que guía decisiones de desarrollo

---

## Stack Tecnológico

| Componente         | Tecnología         | Versión | Uso                            |
| ------------------ | ------------------ | ------- | ------------------------------ |
| **SLO Monitoring** | Grafana SLO Plugin | —       | Definición y tracking de SLOs  |
| **Métricas**       | Grafana Mimir      | 2.10+   | Fuente de SLIs vía PromQL      |
| **Visualización**  | Grafana            | 10.2+   | Dashboards de SLO compliance   |
| **IaC**            | Terraform          | 1.5+    | Definición de SLOs como código |

---

## ¿Qué son SLO y SLA?

- **SLO (Service Level Objective)**: Objetivo interno de confiabilidad que el equipo se compromete a alcanzar (ej. "P95 latency < 500ms")
- **SLA (Service Level Agreement)**: Acuerdo contractual con clientes sobre nivel de servicio, con penalidades si no se cumple (ej. "99.9% uptime")

**Propósito:** Medir objetivamente la confiabilidad del servicio, establecer expectativas claras, priorizar mejoras.

**Componentes clave:**

- **SLI (Service Level Indicator)**: Métrica que mide comportamiento (ej. latency, error rate, availability)
- **SLO Target**: Umbral objetivo (ej. 99.9%)
- **SLO Window**: Período de medición (ej. 30 días)
- **Error budget**: Margen de error permitido (100% - SLO)

**Beneficios:**

- ✅ Objetividad en calidad de servicio
- ✅ Priorización de trabajo (si SLO en riesgo → top priority)
- ✅ Balance desarrollo features vs confiabilidad
- ✅ Transparencia con stakeholders

---

## Categorías de SLI

| Categoría        | SLI                                    | Descripción                | Fuente              |
| ---------------- | -------------------------------------- | -------------------------- | ------------------- |
| **Availability** | `successful_requests / total_requests` | % de requests exitosos     | HTTP 2xx vs 5xx     |
| **Latency**      | `P95(request_duration) < threshold`    | 95% requests bajo umbral   | request_duration_ms |
| **Throughput**   | `requests_per_second`                  | Capacidad de procesamiento | request count       |
| **Correctness**  | `successful_validations / total`       | % datos correctos          | validation errors   |

---

## Ejemplo: Definir SLOs

```yaml
# SLOs para Customer Service

slos:
  # 1. Availability
  - name: availability
    description: Percentage of successful HTTP requests
    sli:
      ratio:
        numerator: http_server_request_duration_seconds_count{status_code!~"5.."}
        denominator: http_server_request_duration_seconds_count
    target: 99.9 # 99.9% availability
    window: 30d
    error_budget: 0.1 # 0.1% = 43 minutos downtime por mes

  # 2. Latency
  - name: latency-p95
    description: 95th percentile request latency
    sli:
      latency:
        query: |
          histogram_quantile(0.95,
            rate(http_server_request_duration_seconds_bucket[5m])
          )
        threshold: 0.5 # 500ms
    target: 99.0 # 99% de ventanas de 5min bajo 500ms
    window: 30d

  # 3. Error rate
  - name: error-rate
    description: Percentage of failed requests
    sli:
      ratio:
        numerator: http_server_request_duration_seconds_count{status_code=~"5.."}
        denominator: http_server_request_duration_seconds_count
    target: 99.0 # <1% error rate
    window: 30d
```

---

## Implementación con Grafana

```hcl
# terraform/modules/grafana/slo.tf

resource "grafana_slo" "customer_service_availability" {
  name        = "Customer Service - Availability"
  description = "99.9% of HTTP requests should be successful"

  query {
    type = "freeform"

    freeform {
      query = <<-EOT
        sum(rate(http_server_request_duration_seconds_count{
          service="customer-service",
          status_code!~"5.."
        }[5m]))
        /
        sum(rate(http_server_request_duration_seconds_count{
          service="customer-service"
        }[5m]))
      EOT
    }
  }

  objectives {
    value  = 99.9
    window = "30d"
  }

  destination_datasource {
    uid = grafana_data_source.mimir.uid
  }

  label {
    key   = "service"
    value = "customer-service"
  }

  label {
    key   = "team"
    value = "platform"
  }
}

resource "grafana_slo" "customer_service_latency" {
  name        = "Customer Service - Latency P95"
  description = "P95 latency should be below 500ms"

  query {
    type = "freeform"

    freeform {
      query = <<-EOT
        histogram_quantile(0.95,
          rate(http_server_request_duration_seconds_bucket{
            service="customer-service"
          }[5m])
        ) < 0.5
      EOT
    }
  }

  objectives {
    value  = 99.0
    window = "30d"
  }

  destination_datasource {
    uid = grafana_data_source.mimir.uid
  }
}
```

---

## Dashboard de SLO

```json
{
  "dashboard": {
    "title": "Customer Service - SLOs",
    "panels": [
      {
        "title": "Availability SLO",
        "type": "stat",
        "targets": [
          {
            "expr": "avg_over_time(slo:customer_service:availability:ratio[30d]) * 100",
            "legendFormat": "Current"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                { "value": 0, "color": "red" },
                { "value": 99.0, "color": "yellow" },
                { "value": 99.9, "color": "green" }
              ]
            }
          }
        }
      },
      {
        "title": "Error Budget Remaining",
        "type": "gauge",
        "targets": [
          {
            "expr": "(1 - (slo:customer_service:availability:error_budget_consumed / slo:customer_service:availability:error_budget_total)) * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                { "value": 0, "color": "red" },
                { "value": 20, "color": "yellow" },
                { "value": 50, "color": "green" }
              ]
            }
          }
        }
      },
      {
        "title": "SLO Compliance (30 días)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "avg_over_time(slo:customer_service:availability:ratio[30d]) * 100",
            "legendFormat": "Availability"
          },
          {
            "expr": "99.9",
            "legendFormat": "SLO Target"
          }
        ]
      }
    ]
  }
}
```

---

## Error Budget Policy

```markdown
# Error Budget Policy - Customer Service

## SLO Targets

- **Availability**: 99.9% (43 min downtime/mes)
- **Latency P95**: < 500ms en 99% ventanas 5min
- **Error Rate**: < 1%

## Error Budget

- **Total budget**: 0.1% (43 minutos downtime por mes)
- **Calculation**: `(1 - SLO_target) * total_requests`

## Actions by Error Budget Status

### ✅ Budget > 50% (Healthy)

- **Development**: Normal velocity, features + tech debt balance
- **Deployments**: Normal cadence (daily)
- **Risk tolerance**: Can take calculated risks

### ⚠️ Budget 20-50% (Warning)

- **Development**: Prioritize reliability over features (70/30)
- **Deployments**: Reduce frequency (2-3x/week), increase review
- **Risk tolerance**: Conservative, no risky changes

### 🚨 Budget < 20% (Critical)

- **Development**: STOP features, 100% focus on reliability
- **Deployments**: Freeze (only critical fixes con approval)
- **Risk tolerance**: Zero tolerance, rollback aggressive
- **Escalation**: Tech Lead + Product Manager notified

### ❌ Budget Exhausted (Breach)

- **Action**: Full incident response, root cause analysis mandatory
- **Deployment**: Complete freeze until SLO recovered
- **Communication**: Stakeholders + customers notified
- **Postmortem**: Required within 48h
```

---

## Ejemplo de SLA

```markdown
# Service Level Agreement - Customer Service API

**Effective Date**: 2026-01-01
**Version**: 1.0

## Service Description

Customer Service API provides REST endpoints for customer and order management.

## Service Levels

### 1. Availability

- **Commitment**: 99.9% uptime monthly (excluding planned maintenance)
- **Measurement**: Successful HTTP responses (2xx, 3xx, 4xx) / Total requests
- **Downtime allowance**: 43 minutes per month

### 2. Performance

- **Commitment**: 95th percentile response time < 500ms
- **Measurement**: P95 of HTTP request duration
- **Endpoints covered**: All `/api/*` endpoints

### 3. Support Response Times

- **Critical (P1)**: < 1 hour
- **High (P2)**: < 4 hours
- **Medium (P3)**: < 24 hours
- **Low (P4)**: < 72 hours

## Exclusions

This SLA does not cover:

- Client-side errors (4xx excluding 429 rate limit)
- Third-party service failures beyond our control
- Scheduled maintenance (with 7 days notice)
- Force majeure events

## Service Credits (if SLA breached)

| Availability  | Service Credit |
| ------------- | -------------- |
| 99.0% - 99.9% | 10%            |
| 95.0% - 99.0% | 25%            |
| < 95.0%       | 50%            |

## Requesting Credit

- Must be requested within 30 days of incident
- Provide correlation IDs demonstrating breach
- Credits applied to next billing cycle
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** definir al menos 2 SLOs por servicio: Availability y Latency P95
- **MUST** medir SLOs desde métricas reales de OpenTelemetry (no estimaciones)
- **MUST** documentar SLOs en el README del servicio
- **MUST** crear dashboard Grafana mostrando SLO compliance y error budget
- **MUST** establecer una error budget policy con acciones concretas por estado

### SHOULD (Fuertemente recomendado)

- **SHOULD** definir SLO para error rate (< 1%)
- **SHOULD** configurar alerta cuando error budget < 20%
- **SHOULD** incluir SLA en documentación orientada al cliente
- **SHOULD** definir SLOs como código con Terraform (no manualmente en Grafana)

### MAY (Opcional)

- **MAY** crear SLOs adicionales (throughput, correctness)
- **MAY** automatizar reportes semanales de SLO compliance

### MUST NOT (Prohibido)

- **MUST NOT** definir SLOs sin métricas reales como base (no percepciones)
- **MUST NOT** ignorar el error budget exhausted — requiere acción inmediata

---

## Referencias

- [Lineamiento de Observabilidad](../../lineamientos/arquitectura/observabilidad.md) — lineamiento que origina este estándar
- [Métricas con OpenTelemetry](./metrics.md) — fuente de SLIs vía PromQL/Mimir
- [Alertas con Grafana](./alerting.md) — alertas basadas en error budget
- [Dashboards en Grafana](./dashboards.md) — visualización de SLO compliance
- [Distributed Tracing](./distributed-tracing.md) — trazabilidad que complementa los SLOs
- [Google SRE Book - SLOs](https://sre.google/sre-book/service-level-objectives/) — referencia canónica de SLOs
- [Grafana SLO Plugin](https://grafana.com/docs/grafana-cloud/alerting-and-irm/slo/) — tracking de SLOs en Grafana
- [Implementing SLOs](https://sre.google/workbook/implementing-slos/) — guía práctica de implementación
