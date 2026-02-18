---
id: alerting
sidebar_position: 6
title: Alertas Basadas en SLOs
description: Sistema de alertas basado en SLOs para reducir falsos positivos
---

# Alertas Basadas en SLOs

## Contexto

Este estándar define cómo configurar alertas basadas en SLOs para detectar problemas reales minimizando falsos positivos. Complementa el [lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) y el estándar de [SLOs](slo-sla.md) especificando **cuándo** y **cómo** alertar.

---

## Stack Tecnológico

| Componente       | Tecnología       | Versión | Uso                     |
| ---------------- | ---------------- | ------- | ----------------------- |
| **Alerting**     | Grafana Alerting | 10.0+   | Motor de alertas        |
| **Storage**      | Grafana Mimir    | 2.10+   | Métricas para alertas   |
| **Notification** | Slack, PagerDuty | -       | Canales de notificación |

---

## Implementación Técnica

### Principios de Alertas

```yaml
# ✅ Alert sobre SYMPTOMS no CAUSES
# ❌ MAL: "CPU > 80%" (causa)
# ✅ BIEN: "Latency p95 > 1000ms" (síntoma)

# ✅ Alert sobre USER IMPACT
# ❌ MAL: "Database connection pool saturated"
# ✅ BIEN: "Error rate > 5%" (usuarios afectados)

# ✅ Alert sobre SLO BURN RATE
# ❌ MAL: "1 request failed"
# ✅ BIEN: "Burning error budget 10x faster than expected"

# ✅ Alert ACTIONABLE
# ❌ MAL: "Something is wrong"
# ✅ BIEN: "Orders API availability < 99% - Check logs with correlation ID"
```

### Multiwindow Multi-Burn-Rate Alerts

```yaml
# Grafana Alert - Availability SLO (99.9%)
alert: OrdersAPI_Availability_Fast_Burn
annotations:
  summary: "Orders API availability degraded significantly"
  description: |
    Current error rate is consuming error budget 10x faster than target.
    - Current availability: {{ $values.availability }}%
    - Target: 99.9%
    - Error budget burn rate: {{ $values.burn_rate }}x
    - Time window: 1h
  runbook_url: "https://wiki.talma.com/runbooks/orders-api-availability"
expr: |
  # ✅ Ventana corta (1h) - Detecta incidentes críticos rápido
  (
    1 - (
      sum(rate(sli_http_requests_successful_total{service="orders-api"}[1h]))
      /
      sum(rate(sli_http_requests_total{service="orders-api"}[1h]))
    )
  ) > 0.01  # Error rate > 1% (10x el budget de 0.1%)

  AND

  # ✅ Ventana larga (6h) - Confirma tendencia
  (
    1 - (
      sum(rate(sli_http_requests_successful_total{service="orders-api"}[6h]))
      /
      sum(rate(sli_http_requests_total{service="orders-api"}[6h]))
    )
  ) > 0.01

for: 2m # Esperar 2 minutos para confirmar
severity: critical
labels:
  service: orders-api
  slo: availability
  burn_rate: fast
  oncall: true
```

```yaml
# Slow Burn Alert - Detecta degradación gradual
alert: OrdersAPI_Availability_Slow_Burn
annotations:
  summary: "Orders API availability degrading slowly"
  description: |
    Error rate is consuming error budget faster than sustainable.
    - Current availability: {{ $values.availability }}%
    - Target: 99.9%
    - Error budget burn rate: {{ $values.burn_rate }}x
    - Time window: 6h
expr: |
  # ✅ Ventana media (6h)
  (
    1 - (
      sum(rate(sli_http_requests_successful_total{service="orders-api"}[6h]))
      /
      sum(rate(sli_http_requests_total{service="orders-api"}[6h]))
    )
  ) > 0.002  # Error rate > 0.2% (2x el budget)

  AND

  # ✅ Ventana muy larga (3d)
  (
    1 - (
      sum(rate(sli_http_requests_successful_total{service="orders-api"}[3d]))
      /
      sum(rate(sli_http_requests_total{service="orders-api"}[3d]))
    )
  ) > 0.002

for: 15m
severity: warning
labels:
  service: orders-api
  slo: availability
  burn_rate: slow
  oncall: false
```

### Alertas de Latencia

```yaml
# Fast Burn - Latencia P95
alert: OrdersAPI_Latency_P95_Fast_Burn
annotations:
  summary: "Orders API latency P95 significantly elevated"
  description: |
    95% of requests are slower than target.
    - Current P95: {{ $values.p95 }}ms
    - Target: < 500ms
    - Time window: 30m
expr: |
  histogram_quantile(0.95,
    sum(rate(sli_http_request_duration_bucket{service="orders-api"}[30m])) by (le)
  ) > 500  # Umbral: 500ms

  AND

  histogram_quantile(0.95,
    sum(rate(sli_http_request_duration_bucket{service="orders-api"}[2h])) by (le)
  ) > 500

for: 5m
severity: critical
labels:
  service: orders-api
  slo: latency
  percentile: p95
```

```yaml
# Latencia P99 - Más permisivo
alert: OrdersAPI_Latency_P99_Critical
annotations:
  summary: "Orders API latency P99 extremely high"
  description: |
    99% of requests are significantly slower than acceptable.
    - Current P99: {{ $values.p99 }}ms
    - Target: < 1000ms
expr: |
  histogram_quantile(0.99,
    sum(rate(sli_http_request_duration_bucket{service="orders-api"}[15m])) by (le)
  ) > 1000

for: 5m
severity: warning
labels:
  service: orders-api
  slo: latency
  percentile: p99
```

### Alertas de Error Budget

```yaml
# Error Budget < 25% remaining
alert: OrdersAPI_ErrorBudget_Low
annotations:
  summary: "Orders API error budget critically low"
  description: |
    Only {{ $values.remaining }}% of error budget remains.
    - SLO: 99.9% availability
    - Error budget: 0.1% (43.2 min/month)
    - Remaining: {{ $values.remaining }}%
    - Action: Freeze non-critical deployments
  runbook_url: "https://wiki.talma.com/runbooks/error-budget-policy"
expr: |
  (
    (
      sum(rate(sli_http_requests_successful_total{service="orders-api"}[30d]))
      /
      sum(rate(sli_http_requests_total{service="orders-api"}[30d]))
      - 0.999  # SLO target
    )
    / 0.001  # Error budget
  ) * 100 < 25  # < 25% remaining

for: 10m
severity: warning
labels:
  service: orders-api
  type: error_budget
  action_required: true
```

### Alertas de Dependencias

```yaml
# Database connection pool saturation
alert: OrdersAPI_Database_ConnectionPool_Saturated
annotations:
  summary: "Database connection pool near saturation"
  description: |
    Connection pool usage is critically high, may cause request timeouts.
    - Current utilization: {{ $values.utilization }}%
    - Queue size: {{ $values.queue_size }}
    - Action: Check slow queries, consider scaling
expr: |
  db_connection_pool_utilization{service="orders-api"} > 90
  OR
  db_connection_pool_queue_size{service="orders-api"} > 10

for: 5m
severity: warning
labels:
  service: orders-api
  component: database
```

```yaml
# Kafka consumer lag
alert: OrdersAPI_Kafka_ConsumerLag_High
annotations:
  summary: "Kafka consumer lag critically high"
  description: |
    Consumer is falling behind, messages may be delayed.
    - Topic: {{ $labels.topic }}
    - Lag: {{ $values.lag }}ms
    - Action: Check consumer health, consider scaling
expr: |
  kafka_consumer_lag_ms{service="orders-api"} > 60000  # 1 minute lag

for: 10m
severity: warning
labels:
  service: orders-api
  component: kafka
```

### Configuración de Notificaciones

```yaml
# Grafana Contact Points
contact_points:
  # ✅ Critical → PagerDuty (24/7 on-call)
  - name: pagerduty_oncall
    type: pagerduty
    settings:
      integration_key: $PAGERDUTY_KEY
      severity: critical
      auto_resolve: true

  # ✅ Warning → Slack (durante horas laborales)
  - name: slack_engineering
    type: slack
    settings:
      url: $SLACK_WEBHOOK_URL
      channel: "#alerts-orders-api"
      username: Grafana Alerts
      title: "{{ .GroupLabels.alertname }}"
      text: "{{ .Annotations.description }}"

  # ✅ Info → Email
  - name: email_team
    type: email
    settings:
      addresses: ["orders-team@talma.com"]

# Notification Policies
notification_policies:
  - match:
      severity: critical
      oncall: true
    contact_point: pagerduty_oncall
    continue: true # También enviar a Slack

  - match:
      severity: critical
    contact_point: slack_engineering
    mute_time_intervals: [weekends, nights]

  - match:
      severity: warning
    contact_point: slack_engineering
    mute_time_intervals: [weekends, nights]
    group_wait: 30s
    group_interval: 5m
    repeat_interval: 4h
```

### Mute Time Intervals

```yaml
# No alertar en horarios específicos (excepto critical)
mute_time_intervals:
  - name: weekends
    time_intervals:
      - weekdays: [saturday, sunday]
        times:
          - start_time: "00:00"
            end_time: "23:59"

  - name: nights
    time_intervals:
      - weekdays: [monday, tuesday, wednesday, thursday, friday]
        times:
          - start_time: "22:00"
            end_time: "08:00"

  - name: planned_maintenance
    time_intervals:
      - times:
          - start_time: "2024-02-20T02:00:00Z"
            end_time: "2024-02-20T06:00:00Z"
```

### Runbook Template

```markdown
# Runbook: Orders API Availability Degraded

## Severity: Critical

## Symptoms

- Error rate > 1% (10x normal)
- Users experiencing 5xx errors
- SLO at risk

## Impact

- Orders cannot be created
- Users see "Service Unavailable" errors
- Revenue impact: High

## Diagnosis

1. Check dashboard: https://grafana.talma.com/d/orders-api-slo
2. Search recent errors in Loki:
```

{service="orders-api"} | json | Level="Error"

````
3. Check recent deployments in CI/CD
4. Review traces in Tempo for failed requests

## Mitigation
1. If recent deployment: **Rollback immediately**
```bash
kubectl rollout undo deployment/orders-api
````

2. If database issue: **Scale up connection pool** or **failover to replica**
3. If external API down: **Enable circuit breaker** or **use cached data**

## Resolution

1. Identify root cause from logs/traces
2. Apply permanent fix
3. Monitor SLO recovery
4. Update postmortem

## Escalation

- Primary: @oncall-orders
- Secondary: @engineering-manager-orders
- Escalate after: 30 minutes

```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** alertar sobre síntomas (user impact) no causas
- **MUST** usar multiwindow multi-burn-rate alerts
- **MUST** configurar al menos 2 ventanas (fast burn + slow burn)
- **MUST** incluir runbook URL en anotaciones
- **MUST** usar severidades (critical, warning, info)
- **MUST** configurar contact points apropiados por severidad
- **MUST** incluir contexto en descripciones (valores actuales, targets)
- **MUST** establecer período `for` para evitar flapping
- **MUST** crear runbooks para todas las alertas críticas

### SHOULD (Fuertemente recomendado)

- **SHOULD** alertar en error budget < 25%
- **SHOULD** usar PagerDuty para alertas critical + oncall
- **SHOULD** usar Slack para alertas warning
- **SHOULD** configurar mute intervals para off-hours (warnings)
- **SHOULD** agrupar alertas relacionadas (group_by)
- **SHOULD** auto-resolver alertas cuando condición se normaliza
- **SHOULD** incluir links a dashboards y queries en anotaciones

### MAY (Opcional)

- **MAY** usar alertas predictivas (forecasting)
- **MAY** implementar escalation chains
- **MAY** integrar con ticketing system (Jira)
- **MAY** usar inhibit rules para suprimir alertas dependientes

### MUST NOT (Prohibido)

- **MUST NOT** alertar sobre cada request fallido (usar burn rate)
- **MUST NOT** enviar todas las alertas a on-call
- **MUST NOT** alertar sin runbook para critical alerts
- **MUST NOT** usar thresholds estáticos sin relación a SLOs
- **MUST NOT** ignorar alertas repetidas (alert fatigue)
- **MUST NOT** silenciar alertas permanentemente

---

## Referencias

- [Lineamiento: Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md)
- Estándares relacionados:
  - [SLIs y SLOs](slo-sla.md)
  - [Métricas](metrics-standards.md)
  - [Dashboards](dashboards.md)
- Especificaciones:
  - [Google SRE - Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
  - [Multiwindow Multi-Burn-Rate Alerts](https://sre.google/workbook/alerting-on-slos/#6-multiwindow-multi-burn-rate-alerts)
  - [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
```
