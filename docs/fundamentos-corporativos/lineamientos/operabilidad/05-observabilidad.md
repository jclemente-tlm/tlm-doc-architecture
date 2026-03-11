---
id: observabilidad
sidebar_position: 5
title: Observabilidad
description: Observabilidad como requisito arquitectónico desde el diseño
---

# Observabilidad

En sistemas distribuidos, las fallas pueden propagarse silenciosamente afectando la experiencia del usuario sin síntomas evidentes. La observabilidad integrada desde el diseño reduce el MTTR hasta 10x comparado con implementaciones reactivas, facilitando la identificación de cuellos de botella, degradación de performance y la correlación de eventos a través de múltiples servicios.

**Este lineamiento aplica a:** servicios backend, APIs REST, microservicios, workers, procesos batch y funciones serverless.

## Estándares Obligatorios

- [Implementar structured logging en JSON](../../estandares/observabilidad/structured-logging.md)
- [Emitir métricas siguiendo RED/USE](../../estandares/observabilidad/metrics.md)
- [Implementar distributed tracing con W3C Trace Context](../../estandares/observabilidad/distributed-tracing.md#1-distributed-tracing)
- [Usar correlation IDs entre servicios](../../estandares/observabilidad/distributed-tracing.md#2-correlation-ids)
- [Definir SLIs, SLOs y SLAs](../../estandares/observabilidad/distributed-tracing.md#3-slo-sla)
- [Configurar alertas basadas en SLOs](../../estandares/observabilidad/alerting.md)
- [Implementar dashboards operacionales](../../estandares/observabilidad/dashboards.md)
