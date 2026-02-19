---
title: "ADR-014: Grafana Stack Observabilidad"
sidebar_position: 14
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

- **Grafana Stack OSS** (Loki + Mimir + Tempo + Grafana + Alloy)
- **ELK Stack** (Elasticsearch + Logstash + Kibana)
- **Datadog** (SaaS observabilidad completo)
- **Splunk Observability Cloud** (Enterprise observabilidad)
- **AWS CloudWatch + X-Ray** (nativo AWS)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                             | Grafana Stack (Loki+Mimir+Tempo)                  | ELK Stack                                   | Datadog                                         | Splunk Observability                             | AWS CloudWatch + X-Ray                |
| ------------------------------------ | ------------------------------------------------- | ------------------------------------------- | ----------------------------------------------- | ------------------------------------------------ | ------------------------------------- |
| **Agnosticidad**                     | ✅ OSS, multi-cloud                               | ✅ OSS, multi-cloud                         | ❌ Lock-in SaaS                                 | ⚠️ On-prem/SaaS                                  | ❌ Lock-in AWS                        |
| **Madurez**                          | ✅ Alta (2014, observability std)                 | ✅ Muy alta (2010, ELK standard)            | ✅ Muy alta (2010, SaaS líder)                  | ✅ Muy alta (2003, enterprise)                   | ✅ Alta (2009, AWS native)            |
| **Adopción**                         | ✅ Alta (Grafana + stack moderno)                 | ✅ Muy alta (65K⭐, logging std)            | ✅ Muy alta (25K+ clientes)                     | ✅ Muy alta (analytics líder)                    | ✅ Alta (AWS monitoring std)          |
| **Modelo de gestión**                | ⚠️ Self-hosted                                    | ⚠️ Self-hosted                              | ✅ Gestionado (SaaS)                            | ⚠️ Híbrido                                       | ✅ Gestionado (AWS)                   |
| **Complejidad operativa**            | ⚠️ Alta (1 FTE, 10-20h/sem)                       | ⚠️ Alta (1 FTE, 10-20h/sem)                 | ✅ Baja (0.25 FTE, `<5h/sem)`                     | ⚠️ Alta (1 FTE, 10-20h/sem)                      | ✅ Baja (0.25 FTE, `<5h/sem)`           |
| **Integración .NET**                 | ✅ OpenTelemetry.\* (5M+ DL/mes, .NET 6+, nativo) | ✅ Serilog.Sinks.Elasticsearch (5M+ DL/mes) | ✅ Datadog.Trace (1M+ DL/mes, APM completo)     | ✅ Splunk.Logging.\* (500K+ DL/mes)              | ✅ AWSSDK.CloudWatch (10M+ DL/mes)    |
| **Multi-tenancy**                    | ✅ Orgs + data sources                            | ⚠️ Indices/Spaces                           | ✅ Nativo (orgs/teams)                          | ✅ Tenants nativos                               | ⚠️ Por accounts                       |
| **Latencia**                         | ✅ p95 `<100ms `queries                             | ⚠️ +100-200ms (requiere tuning)             | ✅ `<200ms `queries                               | ✅ `<150ms `queries                                | ✅ `<500ms `queries                     |
| **Rendimiento**                      | ✅ 10K+ series ingest                             | ✅ 10K+ events/seg                          | ✅ 100K+ metrics/min                            | ✅ 100K+ metrics/seg                             | ✅ 50K+ metrics/min                   |
| **Escalabilidad**                    | ✅ Hasta 1M+ series, 100K métricas/min (Grafana)  | ✅ Hasta multi-TB logs/día (Elastic scale)  | ✅ Hasta 100K+ hosts, 1M métricas/min (Datadog) | ✅ Hasta PB-scale logs, 500K events/seg (Splunk) | ✅ Hasta 1M+ metrics/min máx (AWS)    |
| **Correlación logs-métricas-trazas** | ✅ Trace ID linking automático                    | ⚠️ Manual/APM adicional                     | ✅ Trace ID propagation                         | ✅ Correlación automática                        | ✅ X-Ray integration                  |
| **Alertas**                          | ✅ Grafana Alerting integrado                     | ✅ Watcher/Alerting                         | ✅ Alertas avanzadas                            | ✅ Alertas ML/AI                                 | ✅ CloudWatch Alarms                  |
| **Políticas de retención**           | ✅ Ilimitado (configurable por componente)        | ✅ Configurable por índice                  | ⚠️ 15 meses máximo (Datadog)                    | ⚠️ 90 días default (New Relic)                   | ✅ Configurable (CloudWatch Logs)     |
| **Límites de cardinalidad**          | ✅ Loki low cardinality, Mimir millones series    | ⚠️ Alto costo con alta cardinalidad         | ⚠️ Límites estrictos (custom metrics caro)      | ⚠️ Límites en custom attributes                  | ⚠️ Límites estrictos (custom metrics) |
| **Estrategias de muestreo**          | ✅ Tempo tail-based sampling                      | ⚠️ Manual APM agents                        | ✅ Intelligent sampling                         | ✅ Adaptive sampling                             | ⚠️ Head-based sampling (X-Ray)        |
| **Canales de notificación**          | ✅ Email, Slack, PagerDuty, Webhook, MS Teams     | ✅ Email, Slack, PagerDuty, Webhook         | ✅ 50+ integrations                             | ✅ 30+ integrations                              | ✅ SNS, Lambda, Systems Manager       |
| **Federación de fuentes de datos**   | ✅ Multiple datasources, mixed queries            | ✅ Cross-cluster search                     | ⚠️ Limitado (por cuenta/plan)                   | ⚠️ Limitado (por cuenta)                         | ⚠️ Cross-account queries (setup)      |
| **Costos**                           | ✅ $0 licencia + ~$200-500/mes infra              | ✅ $0 licencia + ~$300-600/mes infra        | ❌ $15-31/host/mes (~$18K-37K/año 100 hosts)    | ❌ $150/GB ingestión (~$450K/año 10GB/día)       | ⚠️ $1-3/GB ingestión (~$12-36K/año)   |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona el **Grafana Stack OSS** con:

- **Logs:** Loki (almacenamiento y consulta de logs)
- **Métricas:** Mimir (almacenamiento de métricas escalable)
- **Trazas:** Tempo (rastreo distribuido)
- **Dashboards:** Grafana (visualización unificada)
- **Recolección:** Alloy (recolector de métricas, logs y trazas)
- **Alertas:** Grafana Alerting (alertas unificadas)

### Justificación

- **Stack unificado Grafana:** Loki, Mimir y Tempo comparten arquitectura común
- **Alloy como recolector universal:** Reemplaza múltiples agentes (Promtail, Prometheus Agent, OpenTelemetry Collector)
- Observabilidad completa con correlación nativa entre logs, métricas y trazas
- Stack OSS evita lock-in y reduce costos 80% vs SaaS
- Integración nativa con .NET 8 via OpenTelemetry SDK
- Grafana como única UI para logs, métricas y trazas
- **Mimir:** Escalabilidad horizontal para métricas (compatible con Prometheus)
- **Tempo:** Rastreo distribuido con bajo overhead
- **Loki:** Indexación eficiente de logs sin indexar contenido completo
- Retención flexible por tipo de telemetría
- Compatibilidad con Serilog (ADR-016)

### Alternativas descartadas

- **ELK Stack:** mayor complejidad operativa, Elasticsearch resource-intensive (memoria, CPU, storage), costos de licenciamiento X-Pack/Platinum features, tuning complejo para scale, correlación logs-métricas-trazas requiere Elastic APM adicional
- **Datadog:** costos prohibitivos a escala (US$15-31/host/mes = US$180K-372K/año para 100 hosts), lock-in SaaS, vendor risk, menor control sobre datos sensibles
- **Splunk Observability Cloud:** costos enterprise prohibitivos (US$150/GB ingestión = US$450K/año para 10GB/día), complejidad licenciamiento, más orientado a analytics/SIEM que observabilidad moderna, pricing por volumen dificulta predicción
- **CloudWatch + X-Ray:** lock-in AWS, visualización básica limitada, costos variables crecientes con escala, no portable multi-cloud, CloudWatch Insights consultas costosas
- **Prometheus standalone:** Mimir ofrece mejor escalabilidad horizontal, HA nativa, retención long-term S3/GCS, menor complejidad operativa vs Thanos

---

## ⚠️ CONSECUENCIAS

### Positivas

- **Stack unificado:** Loki, Mimir y Tempo comparten arquitectura y operación
- **Alloy simplifica recolección:** Un solo agente para logs, métricas y trazas
- Visibilidad completa del stack con correlación nativa
- Costos predecibles (solo infraestructura)
- Flexibilidad para migrar entre clouds manteniendo observabilidad
- Grafana como única herramienta de visualización
- **Escalabilidad horizontal:** Mimir y Tempo escalan independientemente
- **Eficiencia de almacenamiento:** Loki no indexa contenido completo de logs

### Negativas (Riesgos y Mitigaciones)

- **Operación self-managed:** Requiere equipo SRE con expertise
  - _Mitigación:_ Terraform + Helm charts oficiales de Grafana Labs
- **Curva de aprendizaje:** Mimir, Tempo y Alloy son tecnologías más nuevas
  - _Mitigación:_ Documentación de Grafana Labs, training interno
- **Alta disponibilidad:** Requiere arquitectura distribuida para cada componente
  - _Mitigación:_ Despliegue en múltiples AZs con S3/GCS como backend
- **Migración desde Prometheus:** Si se usa Prometheus actualmente
  - _Mitigación:_ Mimir es compatible con API de Prometheus (drop-in replacement)

---

## 📚 REFERENCIAS

- [Grafana Loki](https://grafana.com/oss/loki/)
- [Grafana Mimir](https://grafana.com/oss/mimir/)
- [Grafana Tempo](https://grafana.com/oss/tempo/)
- [Grafana Alloy](https://grafana.com/docs/alloy/)
- [Grafana](https://grafana.com/)
- [ELK Stack](https://www.elastic.co/elastic-stack)
- [Datadog](https://www.datadoghq.com/)
- [New Relic](https://newrelic.com/)
- [Splunk](https://www.splunk.com/)
- [AWS CloudWatch](https://aws.amazon.com/cloudwatch/)
- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [Serilog](https://serilog.net/)
- [ADR-016: Logging Estructurado](./adr-016-logging-estructurado.md)

---

**Decisión tomada por:** Equipo de Arquitectura + SRE
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
