---
id: alerting
sidebar_position: 5
title: Alertas con Grafana
description: Estándar para definición de alertas, canales de notificación y runbooks usando Grafana Alerting.
tags: [observabilidad, alertas, grafana, pagerduty]
---

# Alertas con Grafana

## Contexto

Este estándar define cómo configurar alertas proactivas que detecten problemas antes de que impacten a los usuarios. Complementa el lineamiento [Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) asegurando que el equipo sea notificado en forma oportuna y con contexto suficiente para actuar.

---

## Stack Tecnológico

| Componente           | Tecnología        | Versión | Uso                                        |
| -------------------- | ----------------- | ------- | ------------------------------------------ |
| **Alerting Engine**  | Grafana Alerting  | 10.2+   | Evaluación de reglas y despacho de alertas |
| **Query (métricas)** | PromQL / Mimir    | —       | Condiciones basadas en métricas            |
| **Query (logs)**     | LogQL / Loki      | —       | Condiciones basadas en patrones de log     |
| **Notificación**     | Teams / PagerDuty | —       | Canales de notificación por severidad      |

---

## ¿Qué es Alerting?

Sistema de notificaciones automáticas cuando métricas o logs superan umbrales configurados, indicando que se requiere atención humana. Una alerta bien definida siempre implica una acción concreta; si no hay acción posible, no debe existir la alerta.

**Componentes clave:**

- **Alert rules** — Condiciones PromQL/LogQL que disparan la alerta
- **Evaluation interval** — Frecuencia de evaluación (ej. cada 1 minuto)
- **For duration** — Tiempo que la condición debe sostenerse antes de disparar
- **Notification channels** — Destinos según severidad (Email, Teams, PagerDuty)
- **Runbooks** — Documentación de cómo responder a cada alerta

**Beneficios:**

- ✅ Detección proactiva de problemas antes de impactar usuarios
- ✅ Reducción del MTTR (Mean Time To Recovery)
- ✅ Visibilidad de degradación gradual (no solo caídas totales)
- ✅ Historial de alertas como documentación de incidentes

---

## Estructura de Reglas de Alerta

Reglas base que todo servicio debe definir:

```yaml
# grafana/alerts/customer-service.yaml

apiVersion: 1
groups:
  - name: customer-service-alerts
    interval: 1m
    rules:

      # Servicio caído
      - uid: service-down
        title: Service Down
        condition: A
        data:
          - refId: A
            datasourceUid: mimir
            model:
              expr: up{service="customer-service"} == 0
        for: 1m
        annotations:
          summary: Customer Service está CAÍDO
          description: El servicio ha sido inalcanzable por 1 minuto
          runbook_url: https://wiki.talma.com/runbooks/customer-service/service-down
        labels:
          severity: critical
          team: platform
          oncall: "true"

      # Alta tasa de errores
      - uid: high-error-rate
        title: High Error Rate
        condition: A
        data:
          - refId: A
            datasourceUid: mimir
            model:
              expr: |
                (sum(rate(http_server_request_duration_seconds_count{
                  service="customer-service",
                  status_code=~"5.."
                }[5m])) / sum(rate(http_server_request_duration_seconds_count{
                  service="customer-service"
                }[5m]))) * 100 > 5
        for: 5m
        annotations:
          summary: Customer Service tiene alta tasa de errores
          description: Tasa de errores es {{ $value }}% (umbral: 5%)
          runbook_url: https://wiki.talma.com/runbooks/customer-service/high-error-rate
        labels:
          severity: warning
          team: platform

      # Alta latencia P95
      - uid: high-latency
        title: High P95 Latency
        condition: A
        data:
          - refId: A
            datasourceUid: mimir
            model:
              expr: |
                histogram_quantile(0.95,
                  rate(http_server_request_duration_seconds_bucket{
                    service="customer-service"
                  }[5m])
                ) > 1
        for: 10m
        annotations:
          summary: Customer Service tiene latencia P95 alta
          description: Latencia P95 es {{ $value }}s (umbral: 1s)
          runbook_url: https://wiki.talma.com/runbooks/customer-service/high-latency
        labels:
          severity: warning
          team: platform

      # Uso de memoria alto
      - uid: high-memory
        title: High Memory Usage
        condition: A
        data:
          - refId: A
            datasourceUid: mimir
            model:
              expr: |
                process_runtime_dotnet_gc_heap_size_bytes{
                  service="customer-service"
                } / 1024 / 1024 / 1024 > 2
        for: 15m
        annotations:
          summary: Customer Service usa mucha memoria
          description: Memoria heap es {{ $value }}GB (umbral: 2GB)
        labels:
          severity: warning
          team: platform
```

---

## Canales de Notificación

```yaml
# grafana/notification-policies.yaml

apiVersion: 1
contactPoints:
  - name: platform-team-email
    type: email
    settings:
      addresses: platform-team@talma.com
      singleEmail: true

  - name: platform-team-teams
    type: teams
    settings:
      url: https://outlook.office.com/webhook/xxx

  - name: oncall-pagerduty
    type: pagerduty
    settings:
      integrationKey: ${PAGERDUTY_INTEGRATION_KEY}
      severity: critical

policies:
  - receiver: platform-team-email
    group_by: [alertname, service]
    group_wait: 30s
    group_interval: 5m
    repeat_interval: 4h
    matchers:
      - severity = warning

  - receiver: oncall-pagerduty
    group_by: [alertname]
    group_wait: 10s
    group_interval: 1m
    repeat_interval: 30m
    matchers:
      - severity = critical
      - oncall = "true"
```

---

## Niveles de Severidad

| Severidad    | Descripción                               | Ejemplo                        | Acción esperada       | Canal             |
| ------------ | ----------------------------------------- | ------------------------------ | --------------------- | ----------------- |
| **Info**     | Informativo, no requiere acción           | Despliegue completado          | Ninguna               | Teams (info)      |
| **Warning**  | Situación anormal, monitorear             | Error rate > 5%, Latencia > 1s | Investigar en horas   | Email + Teams     |
| **Critical** | Problema serio, requiere acción inmediata | Servicio caído, Errors > 20%   | Actuar inmediatamente | PagerDuty + Email |

---

## Runbook Template

Cada alerta crítica debe tener un runbook documentado. Ejemplo para alta tasa de errores:

````markdown
# Runbook: High Error Rate

## Alerta

- **Severidad**: Warning
- **Umbral**: Error rate > 5% por 5 minutos

## Causas probables

1. Servicio downstream caído (Payment Gateway, Inventory)
2. Pool de conexiones de BD agotado
3. Bug reciente desplegado
4. Spike de tráfico inusual

## Diagnóstico

1. **Verificar dashboard**:
   - Customer Service Overview → panel Error Rate
   - Filtrar por endpoint para identificar el afectado

2. **Revisar logs de errores**:

   ```logql
   {service="customer-service"} |= "level=Error" | json
   ```

3. **Verificar servicios downstream**:
   - Dashboard Payment Service
   - Métricas de pool de conexiones a BD

4. **Verificar despliegues recientes**:
   - GitHub Actions → últimos 30 minutos

## Resolución

- **Si Payment Gateway caído**: escalar al equipo de Payment
- **Si pool BD agotado**: reiniciar pods (escalado horizontal)
- **Si bug reciente**: rollback del despliegue
- **Si spike de tráfico**: validar si es legítimo y escalar horizontalmente

## Escalación

- Sin resolución en 30 min → escalar al Tech Lead
- Error rate > 20% → página oncall inmediatamente
````

---

## Prevención de Alert Fatigue

```yaml
# Estrategias para evitar saturación de alertas

# 1. Grouping: Agrupa alertas relacionadas en un solo mensaje
policies:
  - group_by: [alertname, service, severity]
    group_wait: 30s     # Espera 30s para agrupar más alertas del mismo batch

# 2. Repeat interval: Evita reintentos frecuentes
policies:
  - repeat_interval: 4h   # Misma alerta máximo 1 vez cada 4h

# 3. Inhibition: Suprime warnings si ya hay un critical del mismo servicio
inhibit_rules:
  - source_matchers:
      - severity = critical
    target_matchers:
      - severity = warning
    equal: [service]

# 4. For duration: Solo alerta si la condición se sostiene (evita flapping)
rules:
  - uid: high-error-rate
    for: 5m   # La condición debe cumplirse 5 minutos seguidos antes de alertar
```

:::warning
Una alerta sin runbook es ruido. Si el equipo no sabe cómo responderla, no debe existir o debe ser reclasificada como `info`.
:::

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** definir alertas para: Service Down, High Error Rate y High Latency en cada servicio
- **MUST** incluir `annotations` con `summary`, `description` y `runbook_url` en cada alerta
- **MUST** configurar canales de notificación diferenciados por severidad (warning vs critical)
- **MUST** documentar un runbook para cada alerta con severidad critical

### SHOULD (Fuertemente recomendado)

- **SHOULD** configurar `for` duration mínima de 5 minutos en alertas de warning (evitar flapping)
- **SHOULD** usar inhibition rules para suprimir warnings cuando hay un critical del mismo servicio
- **SHOULD** configurar `repeat_interval` de al menos 4 horas para alertas de warning
- **SHOULD** usar agrupamiento por `service` y `alertname` para reducir notificaciones

### MUST NOT (Prohibido)

- **MUST NOT** crear alertas sin documentación de runbook
- **MUST NOT** configurar `repeat_interval` menor a 15 minutos (excepto critical)
- **MUST NOT** crear alertas que no requieran acción humana (convertirlas a métricas de dashboard)
- **MUST NOT** usar `severity: critical` para condiciones que pueden esperar hasta el día siguiente

---

## Referencias

- [Lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) — lineamiento que origina este estándar
- [Métricas con OpenTelemetry](./metrics.md) — fuente de métricas para las alert rules
- [Dashboards en Grafana](./dashboards.md) — visualización para diagnóstico desde las alertas
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/) — documentación oficial
