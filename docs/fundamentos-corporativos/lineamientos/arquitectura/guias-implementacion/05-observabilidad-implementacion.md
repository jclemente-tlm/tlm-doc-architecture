---
id: observabilidad-implementacion
sidebar_position: 5
title: Guía de Implementación - Observabilidad
description: Decisiones, checklists y métricas para implementar observabilidad
---

# Guía de Implementación - Observabilidad

Esta guía complementa el [lineamiento de Observabilidad](../05-observabilidad.md) con detalles de implementación, validación y cumplimiento.

## Decisiones de Arquitectura Requeridas

Antes de implementar observabilidad, los equipos deben tomar las siguientes decisiones y documentarlas en ADRs:

- **Estrategia de logging:** niveles, formato JSON, destino centralizado
- **Métricas clave por servicio:** latencia (p50/p95/p99), tasa de errores, throughput, saturación
- **Implementación de tracing distribuido:** OpenTelemetry recomendado como estándar de industria
- **Esquema de correlación de requests:** W3C Trace Context o compatible
- **Dashboards operacionales y alertas:** umbrales definidos
- **Estrategia de retención:** logs y métricas (compliance, análisis, costo)

---

## Checklist Pre-producción

Validar antes de desplegar a producción:

- ☐ Logs estructurados implementados y verificados en code reviews
- ☐ Métricas clave definidas (RED/USE/Four Golden Signals)
- ☐ Tracing distribuido probado end-to-end en entornos inferiores
- ☐ Health checks y readiness probes validados
- ☐ Identificadores de correlación propagados en todas las llamadas

---

## Checklist Post-producción

Verificar después del despliegue:

- ☐ Alertas configuradas, probadas y documentadas con runbooks vinculados
- ☐ Dashboards de monitoreo activos y revisados regularmente
- ☐ Estrategia documentada en ADRs

---

## Métricas de Cumplimiento

| Métrica                                    | Objetivo       | Criticidad |
| ------------------------------------------ | -------------- | ---------- |
| Logs en formato estructurado (JSON)        | >95%           | Alta       |
| Servicios con health checks funcionales    | 100%           | Crítica    |
| MTTR - Identificación de servicio causante | `<5 min (P95)` | Alta       |
| Servicios con tracing distribuido          | 100%           | Alta       |
| Cobertura de métricas RED/USE              | >90%           | Media      |

---

## Referencias

- [Lineamiento de Observabilidad](../05-observabilidad.md)
- [Principios de Operabilidad](../../principios/operabilidad.md)
- [OpenTelemetry Documentation](https://opentelemetry.io/)
