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
- **Stack Comercial SaaS** (Datadog, New Relic, Dynatrace)
- **AWS CloudWatch + X-Ray** (nativo AWS)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | Grafana Stack (Loki+Mimir+Tempo) | ELK Stack               | SaaS (Datadog)           | AWS CloudWatch + X-Ray |
| ------------------- | -------------------------------- | ----------------------- | ------------------------ | ---------------------- |
| **Agnosticidad**    | ✅ OSS, multi-cloud              | ✅ OSS, multi-cloud     | ❌ Lock-in vendor        | ❌ Lock-in AWS         |
| **Operación**       | ⚠️ Self-managed                  | ⚠️ Self-managed         | ✅ Gestionado            | ✅ Gestionado          |
| **Correlación**     | ✅ OpenTelemetry nativo          | ⚠️ Manual               | ✅ Nativa                | ✅ Nativa              |
| **Ecosistema .NET** | ✅ OpenTelemetry SDK             | ✅ Serilog/Elastic      | ✅ APM integrado         | ✅ AWS SDK             |
| **Costos**          | ✅ Solo infraestructura          | ✅ Solo infraestructura | ❌ Alto por host/métrica | ⚠️ Pago por uso        |
| **Visualización**   | ✅ Grafana unificado             | ✅ Kibana maduro        | ✅ Dashboards avanzados  | ⚠️ CloudWatch básico   |
| **Performance**     | ✅ Alta escala, optimizado       | ⚠️ Requiere tuning      | ✅ Optimizado            | ✅ Bueno               |
| **Alertas**         | ✅ Grafana Alerting integrado    | ✅ Watcher/Alerting     | ✅ Alertas avanzadas     | ✅ CloudWatch Alarms   |

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

- **ELK Stack:** mayor complejidad operativa, Elasticsearch resource-intensive, costos de licenciamiento
- **SaaS (Datadog):** costos prohibitivos a escala (~US$180K/año), lock-in vendor
- **CloudWatch + X-Ray:** lock-in AWS, visualización básica, costos variables altos, no portable
- **Prometheus standalone:** Mimir ofrece mejor escalabilidad y alta disponibilidad
- **Jaeger:** Tempo tiene mejor integración con Grafana Stack y menor overhead

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
- [OpenTelemetry .NET](https://opentelemetry.io/docs/instrumentation/net/)
- [Serilog](https://serilog.net/)
- [ADR-016: Logging Estructurado](./adr-016-logging-estructurado.md)

---

**Decisión tomada por:** Equipo de Arquitectura + SRE
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
