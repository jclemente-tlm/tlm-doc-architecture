---
id: observabilidad
sidebar_position: 5
title: Observabilidad
description: Observabilidad como requisito arquitectónico desde el diseño
---

# Observabilidad

Los servicios distribuidos deben instrumentar trazas, métricas y logs como requisito arquitectónico desde el diseño, no como adición posterior. Sin observabilidad integrada, los fallos se propagan silenciosamente entre servicios, el debugging en producción requiere acceso directo a instancias y el MTTR se extiende innecesariamente. Instrumentar structured logging, métricas RED/USE y distributed tracing desde el inicio permite detectar degradaciones antes de que impacten usuarios, correlacionar eventos a través de múltiples servicios y reducir el tiempo de respuesta ante incidentes.

**Este lineamiento aplica a:** servicios backend, APIs REST, microservicios, workers, procesos batch y funciones serverless.

## Prácticas Obligatorias

- [Implementar structured logging en JSON](../../estandares/observabilidad/structured-logging.md)
- [Emitir métricas siguiendo RED/USE](../../estandares/observabilidad/metrics.md)
- [Implementar distributed tracing con W3C Trace Context](../../estandares/observabilidad/distributed-tracing.md#1-distributed-tracing)
- [Usar correlation IDs entre servicios](../../estandares/observabilidad/distributed-tracing.md#2-correlation-ids)
- [Definir SLIs, SLOs y SLAs](../../estandares/observabilidad/distributed-tracing.md#3-slo-sla)
- [Configurar alertas basadas en SLOs](../../estandares/observabilidad/alerting.md)
- [Implementar dashboards operacionales](../../estandares/observabilidad/dashboards.md)
