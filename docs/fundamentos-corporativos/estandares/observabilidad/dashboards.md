---
id: dashboards
sidebar_position: 7
title: Dashboards Operacionales
description: Dashboards para monitoreo operacional basados en SLOs y métricas golden signals
---

# Dashboards Operacionales

## Contexto

Este estándar define la estructura y contenido de dashboards para monitoreo operacional. Complementa el [lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) especificando **qué visualizar** para detectar y debuggear problemas eficientemente.

---

## Stack Tecnológico

| Componente        | Tecnología    | Versión | Uso                |
| ----------------- | ------------- | ------- | ------------------ |
| **Visualization** | Grafana       | 10.0+   | Dashboards         |
| **Metrics**       | Grafana Mimir | 2.10+   | Fuente de métricas |
| **Logs**          | Grafana Loki  | 2.9+    | Fuente de logs     |
| **Traces**        | Grafana Tempo | 2.3+    | Fuente de trazas   |

---

## Implementación Técnica

### Jerarquía de Dashboards

```yaml
# ✅ Tres niveles de dashboards
Nivel 1: Overview (Executive/Management)
  - SLO compliance de TODOS los servicios
  - Error budget burn rate
  - Incidentes activos
  - Tendencias de negocio

Nivel 2: Service Dashboard (On-call Engineers)
  - RED metrics de UN servicio
  - SLO tracking
  - Dependencias (USE metrics)
  - Logs recientes

Nivel 3: Deep Dive (Debugging)
  - Traces individuales
  - Query analysis
  - Correlación logs + traces + metrics
  - Resource usage detallado
```

### Dashboard L1: Overview

```json
{
  "dashboard": {
    "title": "Platform Overview - SLO Compliance",
    "tags": ["platform", "slo", "overview"],
    "timezone": "America/Lima",
    "refresh": "1m",
    "time": {
      "from": "now-7d",
      "to": "now"
    },
    "panels": [
      {
        "title": "SLO Compliance - All Services (Last 30 days)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(sli_http_requests_successful_total[30d])) by (service) / sum(rate(sli_http_requests_total[30d])) by (service) * 100",
            "legendFormat": "{{service}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "mode": "absolute",
              "steps": [
                { "value": 0, "color": "red" },
                { "value": 99.5, "color": "yellow" },
                { "value": 99.9, "color": "green" }
              ]
            },
            "unit": "percent",
            "decimals": 3
          }
        },
        "gridPos": { "h": 8, "w": 24, "x": 0, "y": 0 }
      },
      {
        "title": "Error Budget Burn Rate (Last 1h vs. Last 30d avg)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "(1 - (sum(rate(sli_http_requests_successful_total[1h])) by (service) / sum(rate(sli_http_requests_total[1h])) by (service))) / (1 - 0.999)",
            "legendFormat": "{{service}} - 1h burn rate"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "lineWidth": 2
            },
            "unit": "short",
            "thresholds": {
              "steps": [
                { "value": 0, "color": "green" },
                { "value": 2, "color": "yellow" },
                { "value": 10, "color": "red" }
              ]
            }
          }
        },
        "gridPos": { "h": 8, "w": 24, "x": 0, "y": 8 }
      },
      {
        "title": "Active Incidents",
        "type": "table",
        "targets": [
          {
            "expr": "ALERTS{alertstate=\"firing\", severity=\"critical\"}",
            "format": "table",
            "instant": true
          }
        ],
        "transformations": [
          {
            "id": "organize",
            "options": {
              "includeByName": {
                "alertname": true,
                "service": true,
                "severity": true,
                "Time": true
              }
            }
          }
        ],
        "gridPos": { "h": 8, "w": 24, "x": 0, "y": 16 }
      }
    ]
  }
}
```

### Dashboard L2: Service Dashboard

```json
{
  "dashboard": {
    "title": "Orders API - Service Dashboard",
    "tags": ["service", "orders-api", "red"],
    "templating": {
      "list": [
        {
          "name": "service",
          "type": "constant",
          "current": {
            "value": "orders-api"
          }
        },
        {
          "name": "interval",
          "type": "interval",
          "options": [
            { "text": "1m", "value": "1m" },
            { "text": "5m", "value": "5m" },
            { "text": "15m", "value": "15m" }
          ],
          "current": {
            "value": "5m"
          }
        }
      ]
    },
    "panels": [
      {
        "title": "🎯 SLO Compliance (30d rolling)",
        "type": "gauge",
        "targets": [
          {
            "expr": "sum(rate(sli_http_requests_successful_total{service=\"$service\"}[30d])) / sum(rate(sli_http_requests_total{service=\"$service\"}[30d])) * 100"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                { "value": 0, "color": "red" },
                { "value": 99.5, "color": "yellow" },
                { "value": 99.9, "color": "green" }
              ]
            },
            "unit": "percent",
            "decimals": 4,
            "min": 99,
            "max": 100
          }
        },
        "gridPos": { "h": 8, "w": 8, "x": 0, "y": 0 }
      },
      {
        "title": "📊 Request Rate",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"$service\"}[$interval])) by (method, endpoint)",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps",
            "custom": {
              "drawStyle": "line",
              "lineWidth": 1,
              "fillOpacity": 10
            }
          }
        },
        "gridPos": { "h": 8, "w": 16, "x": 8, "y": 0 }
      },
      {
        "title": "❌ Error Rate (%)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{service=\"$service\", status=~\"5..\"}[$interval])) / sum(rate(http_requests_total{service=\"$service\"}[$interval])) * 100",
            "legendFormat": "5xx errors"
          },
          {
            "expr": "sum(rate(http_requests_total{service=\"$service\", status=~\"4..\"}[$interval])) / sum(rate(http_requests_total{service=\"$service\"}[$interval])) * 100",
            "legendFormat": "4xx errors"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "custom": {
              "lineWidth": 2
            },
            "thresholds": {
              "steps": [
                { "value": 0, "color": "green" },
                { "value": 0.1, "color": "yellow" },
                { "value": 1, "color": "red" }
              ]
            }
          }
        },
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 }
      },
      {
        "title": "⏱️ Latency Percentiles",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, sum(rate(http_request_duration_bucket{service=\"$service\"}[$interval])) by (le))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_bucket{service=\"$service\"}[$interval])) by (le))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_bucket{service=\"$service\"}[$interval])) by (le))",
            "legendFormat": "P99"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ms",
            "custom": {
              "lineWidth": 2
            }
          },
          "overrides": [
            {
              "matcher": { "id": "byName", "options": "P50" },
              "properties": [
                { "id": "color", "value": { "fixedColor": "green" } }
              ]
            },
            {
              "matcher": { "id": "byName", "options": "P95" },
              "properties": [
                { "id": "color", "value": { "fixedColor": "yellow" } }
              ]
            },
            {
              "matcher": { "id": "byName", "options": "P99" },
              "properties": [
                { "id": "color", "value": { "fixedColor": "red" } }
              ]
            }
          ]
        },
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 }
      },
      {
        "title": "🗄️ Database Connection Pool (USE)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "db_connection_pool_utilization{service=\"$service\"}",
            "legendFormat": "Utilization %"
          },
          {
            "expr": "db_connection_pool_queue_size{service=\"$service\"}",
            "legendFormat": "Queue Size"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "custom": {
              "lineWidth": 2
            }
          },
          "overrides": [
            {
              "matcher": { "id": "byName", "options": "Utilization %" },
              "properties": [
                { "id": "unit", "value": "percent" },
                {
                  "id": "thresholds",
                  "value": {
                    "steps": [
                      { "value": 0, "color": "green" },
                      { "value": 70, "color": "yellow" },
                      { "value": 90, "color": "red" }
                    ]
                  }
                }
              ]
            }
          ]
        },
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 16 }
      },
      {
        "title": "☁️ External API Calls",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(http_client_requests_total{service=\"$service\"}[$interval])) by (target_service, status_code)",
            "legendFormat": "{{target_service}} - {{status_code}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "reqps"
          }
        },
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 16 }
      },
      {
        "title": "📝 Recent Error Logs",
        "type": "logs",
        "targets": [
          {
            "expr": "{service=\"$service\"} | json | Level=\"Error\" or Level=\"Critical\"",
            "refId": "A"
          }
        ],
        "options": {
          "showTime": true,
          "showLabels": false,
          "showCommonLabels": true,
          "wrapLogMessage": true,
          "enableLogDetails": true
        },
        "gridPos": { "h": 8, "w": 24, "x": 0, "y": 24 }
      }
    ]
  }
}
```

### Dashboard L3: Deep Dive - Tracing

```json
{
  "dashboard": {
    "title": "Orders API - Trace Analysis",
    "tags": ["tracing", "orders-api", "debugging"],
    "panels": [
      {
        "title": "🔍 Trace Explorer",
        "type": "traces",
        "datasource": "Tempo",
        "targets": [
          {
            "query": "{ service.name=\"orders-api\" && status=error }",
            "queryType": "traceql"
          }
        ],
        "gridPos": { "h": 12, "w": 24, "x": 0, "y": 0 }
      },
      {
        "title": "Slowest Endpoints (by P99)",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, histogram_quantile(0.99, sum(rate(http_request_duration_bucket{service=\"orders-api\"}[5m])) by (le, endpoint)))",
            "format": "table",
            "instant": true
          }
        ],
        "transformations": [
          {
            "id": "organize",
            "options": {
              "renameByName": {
                "Value": "Latency (ms)",
                "endpoint": "Endpoint"
              }
            }
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 12 }
      },
      {
        "title": "Span Duration by Operation",
        "type": "heatmap",
        "targets": [
          {
            "expr": "sum(increase(traces_spanmetrics_duration_bucket{service=\"orders-api\"}[5m])) by (le, span_name)",
            "format": "heatmap"
          }
        ],
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 12 }
      }
    ]
  }
}
```

### Panel de Correlación (Logs + Traces)

```json
{
  "title": "Correlation: Logs ↔ Traces",
  "type": "logs",
  "targets": [
    {
      "expr": "{service=\"$service\"} | json | TraceId=\"${__data.fields[\"Trace ID\"]}\"",
      "refId": "A"
    }
  ],
  "options": {
    "showTime": true,
    "enableLogDetails": true,
    "dedupStrategy": "none"
  },
  "fieldConfig": {
    "defaults": {
      "links": [
        {
          "title": "View Trace in Tempo",
          "url": "/explore?orgId=1&left={\"datasource\":\"Tempo\",\"queries\":[{\"query\":\"${__data.fields[\\\"TraceId\\\"]}\"}]}"
        }
      ]
    }
  }
}
```

### Dashboard de Negocio

```json
{
  "dashboard": {
    "title": "Business Metrics - Orders",
    "tags": ["business", "orders"],
    "panels": [
      {
        "title": "💰 Order Volume (by Country)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(business_orders_created_total[5m])) by (country)",
            "legendFormat": "{{country}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "ops",
            "custom": {
              "fillOpacity": 20,
              "stacking": {
                "mode": "normal"
              }
            }
          }
        },
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 }
      },
      {
        "title": "💵 Revenue (by Payment Method)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate(business_revenue_total[5m])) by (payment_method)",
            "legendFormat": "{{payment_method}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyUSD"
          }
        },
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 }
      },
      {
        "title": "🚫 Order Failures (by Reason)",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum(increase(business_order_failures_total[1h])) by (failure_reason)",
            "legendFormat": "{{failure_reason}}"
          }
        ],
        "options": {
          "legend": {
            "displayMode": "table",
            "values": ["value", "percent"]
          }
        },
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 }
      }
    ]
  }
}
```

### Variables de Dashboard

```json
{
  "templating": {
    "list": [
      {
        "name": "service",
        "type": "query",
        "datasource": "Mimir",
        "query": "label_values(http_requests_total, service)",
        "multi": false,
        "includeAll": false,
        "refresh": 1
      },
      {
        "name": "interval",
        "type": "interval",
        "options": [
          { "text": "30s", "value": "30s" },
          { "text": "1m", "value": "1m" },
          { "text": "5m", "value": "5m" },
          { "text": "15m", "value": "15m" }
        ],
        "auto": true,
        "auto_count": 30,
        "auto_min": "10s"
      },
      {
        "name": "country",
        "type": "query",
        "datasource": "Mimir",
        "query": "label_values(http_requests_total{service=\"$service\"}, country)",
        "multi": true,
        "includeAll": true,
        "refresh": 2
      }
    ]
  }
}
```

### Annotations (Eventos importantes)

```json
{
  "annotations": {
    "list": [
      {
        "name": "Deployments",
        "datasource": "Mimir",
        "enable": true,
        "expr": "deployment_event{service=\"$service\"}",
        "iconColor": "blue",
        "textFormat": "Deploy v{{version}}"
      },
      {
        "name": "Incidents",
        "datasource": "Mimir",
        "enable": true,
        "expr": "ALERTS{alertstate=\"firing\", service=\"$service\", severity=\"critical\"}",
        "iconColor": "red",
        "textFormat": "🚨 {{alertname}}"
      },
      {
        "name": "Scale Events",
        "datasource": "Mimir",
        "enable": true,
        "expr": "kube_deployment_spec_replicas{deployment=\"orders-api\"}",
        "iconColor": "green",
        "textFormat": "Scaled to {{value}} replicas"
      }
    ]
  }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** crear dashboard L2 (Service Dashboard) para cada servicio
- **MUST** incluir RED metrics (Rate, Errors, Duration)
- **MUST** mostrar SLO compliance (30d rolling)
- **MUST** incluir panel de logs recientes
- **MUST** usar variables de template ($service, $interval)
- **MUST** configurar thresholds según SLOs
- **MUST** incluir links a runbooks en panel descriptions
- **MUST** configurar auto-refresh (1m o 5m)

### SHOULD (Fuertemente recomendado)

- **SHOULD** crear dashboard L1 (Overview) para vista ejecutiva
- **SHOULD** incluir USE metrics para dependencias (DB, cache)
- **SHOULD** configurar annotations para deployments
- **SHOULD** incluir panel de correlación logs ↔ traces
- **SHOULD** usar emojis en títulos para facilitar escaneo visual
- **SHOULD** agrupar paneles por función (RED, dependencies, logs)
- **SHOULD** exportar dashboards como código (JSON en Git)

### MAY (Opcional)

- **MAY** crear dashboard L3 (Deep Dive) para tracing
- **MAY** incluir business metrics
- **MAY** configurar drill-down links entre dashboards
- **MAY** usar heatmaps para distribuciones
- **MAY** implementar dashboard folders (por equipo, dominio)

### MUST NOT (Prohibido)

- **MUST NOT** crear dashboards sin variables ($service)
- **MUST NOT** usar colores sin significado (rojo = bueno)
- **MUST NOT** incluir paneles sin datos (queries vacíos)
- **MUST NOT** duplicar información entre dashboards
- **MUST NOT** usar más de 15 paneles en dashboard L2
- **MUST NOT** omitir unidades en axes (ms, %, reqps)

---

## Referencias

- [Lineamiento: Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md)
- Estándares relacionados:
  - [SLIs y SLOs](slo-sla.md)
  - [Métricas](metrics-standards.md)
  - [Alertas](alerting.md)
- Especificaciones:
  - [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
  - [USE Method](http://www.brendangregg.com/usemethod.html)
  - [RED Method](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/)
