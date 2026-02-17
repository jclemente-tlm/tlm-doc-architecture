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

- [Generar logs estructurados en formato JSON](../../estandares/observabilidad/observability.md#2-logging)
- [Emitir métricas siguiendo metodología RED/USE](../../estandares/observabilidad/observability.md#3-métricas)
- [Implementar trazas distribuidas con W3C Trace Context](../../estandares/observabilidad/observability.md#4-trazas-distribuidas)
- [Usar identificadores de correlación entre servicios](../../estandares/observabilidad/observability.md)
- [Configurar health checks para orquestadores](../../estandares/observabilidad/observability.md)
