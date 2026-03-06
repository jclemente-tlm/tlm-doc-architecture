---
id: dashboards
sidebar_position: 4
title: Dashboards en Grafana
description: Estándar para diseño, estructura y gestión de dashboards en Grafana con PromQL y LogQL.
tags: [observabilidad, dashboards, grafana, promql, logql]
---

# Dashboards en Grafana

## Contexto

Este estándar define cómo estructurar, escribir queries y gestionar dashboards de Grafana para visualizar métricas y logs de los servicios. Complementa el lineamiento [Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) asegurando visibilidad centralizada del comportamiento de las aplicaciones en producción.

---

## Stack Tecnológico

| Componente           | Tecnología | Versión | Uso                               |
| -------------------- | ---------- | ------- | --------------------------------- |
| **Visualización**    | Grafana    | 10.2+   | Dashboards, paneles y exploración |
| **Query (métricas)** | PromQL     | —       | Consultas sobre Grafana Mimir     |
| **Query (logs)**     | LogQL      | —       | Consultas sobre Grafana Loki      |

---

## ¿Qué son los Dashboards?

Visualizaciones en Grafana que combinan múltiples paneles (gráficas, tablas, stats) para mostrar el estado de una aplicación o sistema en tiempo real. Cada servicio debe tener al menos un dashboard de overview.

**Componentes clave:**

- **Panels** — Gráficas individuales (time series, gauge, stat, table, logs)
- **Variables** — Filtros dinámicos que parametrizan queries (environment, service, instance)
- **Queries** — LogQL para Loki y PromQL para Mimir
- **Rows** — Agrupación visual de paneles por categoría

**Beneficios:**

- ✅ Visibilidad centralizada del estado de cada servicio
- ✅ Diagnóstico rápido de problemas sin acceder a infraestructura
- ✅ Análisis de tendencias para toma de decisiones
- ✅ Dashboard as code: versionado, revisable y reproducible

---

## Estructura de Dashboard

Organización recomendada para el dashboard de overview de cada servicio:

```
📊 [Service Name] - Overview
├── Row: Key Metrics
│   ├── Request Rate (time series)
│   ├── Error Rate (time series)
│   ├── P95 Latency (stat + gauge)
│   └── Active Connections (gauge)
│
├── Row: HTTP Metrics
│   ├── Requests por Status Code (time series)
│   ├── Distribución de Latencia (heatmap)
│   └── Top 10 Endpoints más lentos (table)
│
├── Row: Business Metrics
│   ├── Órdenes Creadas (counter)
│   ├── Tasa de Error de Negocio (time series)
│   └── Distribución de importes (histogram)
│
├── Row: Infrastructure
│   ├── CPU Usage (time series)
│   ├── Memory Usage (time series)
│   └── GC Collections (time series)
│
└── Row: Logs
    └── Errores Recientes (logs panel)
```

---

## Queries PromQL

Consultas sobre Grafana Mimir para los paneles más comunes:

```promql
# Tasa de requests por endpoint (últimos 5 minutos)
rate(http_server_request_duration_seconds_count{service="customer-service"}[5m])

# Tasa de errores HTTP 5xx
sum(rate(http_server_request_duration_seconds_count{
  service="customer-service",
  status_code=~"5.."
}[5m]))

# Porcentaje de errores sobre total de requests
(
  sum(rate(http_server_request_duration_seconds_count{
    service="customer-service", status_code=~"5.."
  }[5m]))
  /
  sum(rate(http_server_request_duration_seconds_count{
    service="customer-service"
  }[5m]))
) * 100

# P95 de latencia
histogram_quantile(0.95,
  rate(http_server_request_duration_seconds_bucket{service="customer-service"}[5m]))

# Órdenes creadas por minuto
rate(orders_created_total{service="customer-service"}[1m]) * 60

# Uso de memoria heap (en GB)
process_runtime_dotnet_gc_heap_size_bytes{service="customer-service"} / 1024 / 1024 / 1024
```

---

## Queries LogQL

Consultas sobre Grafana Loki para el panel de logs y análisis:

```logql
# Logs de errores en tiempo real
{service="customer-service"} |= "level=Error" | json

# Filtrar por correlation ID específico
{service="customer-service"} | json | CorrelationId="trace-abc-123"

# Conteo de errores por minuto
sum by (level) (
  count_over_time({service="customer-service"} | json | level="Error" [1m])
)

# Logs de pagos fallidos con contexto
{service="customer-service"} |= "Payment failed"
  | json
  | line_format "{{.timestamp}} [{{.CustomerId}}] {{.message}}"

# Latencia promedio de requests desde logs (si está en el mensaje)
avg_over_time(
  {service="customer-service"} |= "HTTP" | json | unwrap Duration [5m]
)
```

---

## Dashboard como Código

Los dashboards deben estar versionados en Git y gestionados con Terraform.

```hcl
# terraform/modules/grafana/dashboards.tf

resource "grafana_dashboard" "customer_service" {
  config_json = file("${path.module}/dashboards/customer-service.json")
  folder      = grafana_folder.services.id
  message     = "Managed by Terraform"
}

resource "grafana_folder" "services" {
  title = "Services"
}

resource "grafana_data_source" "mimir" {
  name = "Mimir"
  type = "prometheus"
  url  = var.mimir_endpoint

  json_data_encoded = jsonencode({
    httpMethod = "POST"
  })
}

resource "grafana_data_source" "loki" {
  name = "Loki"
  type = "loki"
  url  = var.loki_endpoint

  json_data_encoded = jsonencode({
    maxLines = 1000
  })
}
```

El JSON del dashboard se genera desde Grafana UI y se exporta, o se escribe manualmente. Las variables de entorno e instancia permiten reutilizar el mismo dashboard en múltiples entornos:

```json
{
  "templating": {
    "list": [
      {
        "name": "environment",
        "type": "custom",
        "options": ["production", "staging", "development"],
        "current": { "value": "production" }
      },
      {
        "name": "instance",
        "type": "query",
        "datasource": "Mimir",
        "query": "label_values(http_server_request_duration_seconds_count{service=\"customer-service\"}, instance)"
      }
    ]
  }
}
```

:::tip
Usa `$environment` y `$instance` como variables en las queries PromQL/LogQL para hacer los dashboards reutilizables entre entornos sin modificar el JSON.
:::

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** crear al menos un dashboard de Grafana por servicio
- **MUST** incluir paneles de: Request Rate, Error Rate, Latencia (P95) y Resource Usage
- **MUST** usar variables de template para filtrado por environment e instance
- **MUST** versionar todos los dashboards en Git (dashboard as code con Terraform)

### SHOULD (Fuertemente recomendado)

- **SHOULD** separar los dashboards de métricas de negocio de las métricas de infraestructura
- **SHOULD** configurar el intervalo de refresco automático en máximo 30 segundos para producción
- **SHOULD** incluir un panel de logs de errores recientes en el dashboard principal
- **SHOULD** agregar anotaciones de despliegues para correlacionar cambios con anomalías

### MUST NOT (Prohibido)

- **MUST NOT** crear dashboards manualmente sin exportarlos y commitearlos al repositorio
- **MUST NOT** usar queries sin filtro de servicio (pueden devolver datos de todos los servicios)

---

## Referencias

- [Lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) — lineamiento que origina este estándar
- [Métricas con OpenTelemetry](./metrics.md) — fuente de datos PromQL para paneles
- [Structured Logging](./structured-logging.md) — fuente de datos LogQL para paneles de logs
- [Alertas](./alerting.md) — alertas asociadas a los paneles de este dashboard
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/) — referencia oficial
- [PromQL Reference](https://prometheus.io/docs/prometheus/latest/querying/basics/) — sintaxis de queries
- [LogQL Reference](https://grafana.com/docs/loki/latest/query/) — sintaxis de queries Loki
