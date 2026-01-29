---
title: "ADR-021: Stack de Observabilidad Unificado"
sidebar_position: 21
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos multi-tenant distribuidos requieren observabilidad completa (logs, métricas, trazas) que permita:

- **Telemetría unificada** con correlación entre logs, métricas y trazas
- **Troubleshooting distribuido** en arquitectura de microservicios
- **Multi-tenancy** con segregación por país/tenant
- **Alertas proactivas** basadas en SLOs/SLIs
- **Dashboards ejecutivos** para métricas de negocio
- **Performance analysis** y detección de cuellos de botella
- **Integración nativa con .NET 8+** y OpenTelemetry
- **Stack OSS** para evitar lock-in y costos variables

Alternativas evaluadas:

- **Stack Completo OSS** (Prometheus + Grafana + Loki + Jaeger + OpenTelemetry)
- **ELK Stack** (Elasticsearch + Logstash + Kibana)
- **Stack Comercial SaaS** (Datadog, New Relic, Dynatrace)
- **AWS CloudWatch + X-Ray** (nativo AWS)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | Prometheus + Grafana + Loki + Jaeger | ELK Stack | SaaS (Datadog) | AWS CloudWatch + X-Ray |
|----------------------|--------------------------------------|-----------|----------------|----------------------|
| **Agnosticidad**     | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ❌ Lock-in vendor | ❌ Lock-in AWS |
| **Operación**        | 🟡 Self-managed | 🟡 Self-managed | ✅ Gestionado | ✅ Gestionado |
| **Correlación**      | ✅ OpenTelemetry | 🟡 Manual | ✅ Nativa | ✅ Nativa |
| **Ecosistema .NET**  | ✅ OpenTelemetry SDK | ✅ Serilog/Elastic | ✅ APM integrado | ✅ AWS SDK |
| **Costos**           | ✅ Solo infraestructura | ✅ Solo infraestructura | ❌ Alto por host/métrica | 🟡 Pago por uso |
| **Visualización**    | ✅ Grafana excelente | ✅ Kibana maduro | ✅ Dashboards avanzados | 🟡 CloudWatch básico |
| **Performance**      | ✅ Alta escala | 🟡 Requiere tuning | ✅ Optimizado | ✅ Bueno |
| **Alertas**          | ✅ AlertManager flexible | ✅ Watcher/Alerting | ✅ Alertas avanzadas | ✅ CloudWatch Alarms |

### Matriz de Decisión

| Solución                  | Agnosticidad | Correlación | Costos | Visualización | Recomendación         |
|--------------------------|--------------|-------------|--------|---------------|-----------------------|
| **Prometheus + Grafana + Loki + Jaeger** | Excelente    | Excelente   | Excelente | Excelente     | ✅ **Seleccionada**    |
| **ELK Stack**            | Excelente    | Buena       | Excelente | Muy buena     | 🟡 Alternativa         |
| **Datadog/New Relic**    | Mala         | Excelente   | Mala   | Excelente     | ❌ Descartada          |
| **AWS CloudWatch**       | Mala         | Buena       | Media  | Básica        | ❌ Descartada          |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 10 microservicios, 100M métricas/mes, 500GB logs/mes, retención 30 días

| Solución         | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|------------------|---------------|----------------|---------------|--------------|
| Prometheus Stack | OSS           | US$12,000      | US$24,000     | US$36,000    |
| ELK Stack        | OSS           | US$18,000      | US$36,000     | US$54,000    |
| Datadog          | US$180K       | US$0           | US$0          | US$180,000   |
| CloudWatch       | Pago por uso  | US$0           | US$0          | US$72,000    |

---

## ✔️ DECISIÓN

Se selecciona el **Stack OSS Unificado** con:

- **Métricas:** Prometheus + Grafana
- **Logs:** Serilog + Loki + Grafana
- **Trazas:** OpenTelemetry + Jaeger
- **Dashboards:** Grafana (unificado)
- **Alertas:** AlertManager

## Justificación

- Observabilidad completa (3 pilares) con correlación via OpenTelemetry
- Stack OSS evita lock-in y reduce costos 80% vs SaaS
- Integración nativa con .NET 8 via OpenTelemetry SDK
- Grafana como única UI para logs, métricas y trazas
- Escalabilidad probada en entornos enterprise
- Retención flexible por tipo de telemetría
- Compatibilidad con Serilog (ADR-016)

## Alternativas descartadas

- **ELK Stack:** mayor complejidad operativa, Elasticsearch resource-intensive
- **SaaS (Datadog):** costos prohibitivos a escala (~US$180K/año)
- **CloudWatch:** lock-in AWS, visualización básica, costos variables altos

---

## ⚠️ CONSECUENCIAS

### Positivas
- Visibilidad completa del stack con correlación logs-métricas-trazas
- Costos predecibles (solo infraestructura)
- Flexibilidad para migrar entre clouds manteniendo observabilidad
- Grafana como única herramienta de visualización

### Negativas
- Operación self-managed (requiere equipo SRE)
- Curva de aprendizaje Prometheus/Loki/Jaeger
- Requiere automatización con Terraform para alta disponibilidad

### Implementación requerida
- Todos los servicios .NET deben instrumentar con OpenTelemetry SDK
- Serilog configurado con sink a Loki (JSON estructurado)
- Métricas custom exportadas a Prometheus
- Trace IDs propagados en headers HTTP
- Dashboards Grafana por servicio y por SLO
- Alertas en AlertManager para SLIs críticos

---

## 🏗️ ARQUITECTURA DE DESPLIEGUE

```yaml
Observabilidad Stack:
  Métricas:
    - Prometheus: scraping, TSDB, retention 30d
    - Grafana: visualización, dashboards, alertas
  
  Logs:
    - Serilog: structured logging (.NET)
    - Loki: log aggregation, indexing
    - Grafana: queries, visualización
  
  Trazas:
    - OpenTelemetry SDK: instrumentación .NET
    - Jaeger: distributed tracing, UI
    - Grafana: visualización integrada
  
  Correlación:
    - TraceID/SpanID en logs vía Serilog enrichers
    - Exemplars en Prometheus vinculan métricas → trazas
    - Grafana Explore: navegación unificada
```

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs del Stack de Observabilidad

- **Disponibilidad Prometheus:** > 99.9%
- **Latencia de ingesta Loki:** < 500ms p95
- **Retención métricas:** 30 días
- **Retención logs:** 30 días (hot), 90 días (cold)
- **Retención trazas:** 7 días (sampling 10%)

### SLOs de Servicios

- **Error rate:** < 1%
- **Latency p95:** < 200ms
- **Saturation:** CPU < 70%, Memory < 80%
- **Availability:** > 99.5%

---

## 📚 REFERENCIAS

- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Loki](https://grafana.com/oss/loki/)
- [Jaeger](https://www.jaegertracing.io/)
- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [Serilog](https://serilog.net/)
- [ADR-016: Logging Estructurado](./adr-016-logging-estructurado.md)

---

**Decisión tomada por:** Equipo de Arquitectura + SRE
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
