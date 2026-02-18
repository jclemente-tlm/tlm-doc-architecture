---
id: observabilidad
sidebar_position: 6
title: Observabilidad
description: Observabilidad como requisito arquitectónico desde el diseño
---

# Observabilidad

En sistemas distribuidos, las fallas pueden propagarse silenciosamente afectando la experiencia del usuario sin síntomas evidentes. La observabilidad integrada desde el diseño reduce el MTTR hasta 10x comparado con implementaciones reactivas, facilitando la identificación de cuellos de botella, degradación de performance y la correlación de eventos a través de múltiples servicios.

**Este lineamiento aplica a:** servicios backend, APIs REST, microservicios, workers, procesos batch y funciones serverless.

## Estándares Obligatorios

- [Implementar structured logging en JSON](../../estandares/observabilidad/structured-logging.md)
- [Emitir métricas siguiendo RED/USE](../../estandares/observabilidad/metrics-standards.md)
- [Implementar distributed tracing con W3C Trace Context](../../estandares/observabilidad/distributed-tracing.md)
- [Usar correlation IDs entre servicios](../../estandares/observabilidad/correlation-ids.md)
- [Configurar health checks liveness y readiness](../../estandares/infraestructura/health-checks.md)
- [Definir SLIs, SLOs y SLAs](../../estandares/observabilidad/slo-sla.md)
- [Configurar alertas basadas en SLOs](../../estandares/observabilidad/alerting.md)
- [Implementar dashboards operacionales](../../estandares/observabilidad/dashboards.md)
- [Integrar con stack de observabilidad corporativo](../../estandares/observabilidad/observability-stack.md)
