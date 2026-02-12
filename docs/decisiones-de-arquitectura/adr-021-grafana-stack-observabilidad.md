---
title: "ADR-021: Grafana Stack Observabilidad"
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

- **Grafana Stack OSS** (Loki + Mimir + Tempo + Grafana + Alloy)
- **ELK Stack** (Elasticsearch + Logstash + Kibana)
- **Datadog** (SaaS líder APM y observabilidad)
- **New Relic** (SaaS APM enterprise)
- **Splunk** (Enterprise logging y analytics)
- **AWS CloudWatch + X-Ray** (nativo AWS)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | Grafana Stack (Loki+Mimir+Tempo) | ELK Stack               | Datadog                 | New Relic                | Splunk                      | AWS CloudWatch + X-Ray |
| ------------------- | -------------------------------- | ----------------------- | ----------------------- | ------------------------ | --------------------------- | ---------------------- |
| **Agnosticidad**    | ✅ OSS, multi-cloud              | ✅ OSS, multi-cloud     | ❌ Lock-in SaaS         | ❌ Lock-in SaaS          | ⚠️ Enterprise on-prem       | ❌ Lock-in AWS         |
| **Operación**       | ⚠️ Self-managed                  | ⚠️ Self-managed         | ✅ Gestionado           | ✅ Gestionado            | ⚠️ On-prem/cloud gestionado | ✅ Gestionado          |
| **Correlación**     | ✅ OpenTelemetry nativo          | ⚠️ Manual               | ✅ Nativa               | ✅ Nativa                | ✅ Nativa                   | ✅ Nativa              |
| **Ecosistema .NET** | ✅ OpenTelemetry SDK             | ✅ Serilog/Elastic      | ✅ APM integrado        | ✅ .NET Agent nativo     | ✅ .NET instrumentation     | ✅ AWS SDK             |
| **Costos**          | ✅ Solo infraestructura          | ✅ Solo infraestructura | ❌ US$15-31/host/mes    | ❌ US$99-349/usuario/mes | ❌ US$150/GB ingestión      | ⚠️ Pago por uso        |
| **Visualización**   | ✅ Grafana unificado             | ✅ Kibana maduro        | ✅ Dashboards avanzados | ✅ UI intuitiva          | ✅ SPL queries poderosas    | ⚠️ CloudWatch básico   |
| **Performance**     | ✅ Alta escala, optimizado       | ⚠️ Requiere tuning      | ✅ Optimizado           | ✅ Optimizado            | ✅ Enterprise-scale         | ✅ Bueno               |
| **Alertas**         | ✅ Grafana Alerting integrado    | ✅ Watcher/Alerting     | ✅ Alertas avanzadas    | ✅ Alertas ML            | ✅ Alertas sofisticadas     | ✅ CloudWatch Alarms   |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona el **Grafana Stack OSS** con:

- **Logs:** Loki (almacenamiento y consulta de logs)
- **Métricas:** Mimir (almacenamiento de métricas escalable)
- **Trazas:** Tempo (rastreo distribuido)
- **Dashboards:** Grafana (visualización unificada)
- **Recolección:** Alloy (recolector de métricas, logs y trazas)
- **Alertas:** Grafana Alerting (alertas unificadas)

## Justificación

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

## Alternativas descartadas

- **ELK Stack:** mayor complejidad operativa, Elasticsearch resource-intensive (memoria, CPU, storage), costos de licenciamiento X-Pack/Platinum features, tuning complejo para scale
- **Datadog:** costos prohibitivos a escala (US$15-31/host/mes = US$180K-372K/año para 100 hosts), lock-in SaaS, vendor risk, menor control sobre datos sensibles
- **New Relic:** costos enterprise altos (US$99-349/usuario/mes + data ingestion), modelo pricing complejo, lock-in SaaS, menor flexibilidad customización
- **Splunk:** costos enterprise prohibitivos (US$150/GB ingestión = US$450K/año para 10GB/día), complejidad licenciamiento, orientado a security analytics no DevOps observability
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
