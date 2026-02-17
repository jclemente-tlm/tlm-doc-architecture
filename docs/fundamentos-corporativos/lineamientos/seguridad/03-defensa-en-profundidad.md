---
id: defensa-en-profundidad
sidebar_position: 3
title: Defensa en Profundidad
description: Múltiples capas de protección independientes en la arquitectura
---

# Defensa en Profundidad

La arquitectura debe incorporar múltiples capas de protección independientes, para que la falla o evasión de un control no comprometa la seguridad del sistema. Ningún control es infalible: las configuraciones fallan, los accesos pueden ser mal otorgados y los mecanismos de protección pueden ser evadidos. La defensa en profundidad establece que la seguridad no depende de un único control, sino de la combinación coherente de múltiples barreras complementarias que limitan el alcance y propagación de incidentes.

**Este lineamiento aplica a:** componentes y servicios, acceso a datos y recursos críticos, integraciones internas y externas, flujos de información dentro de la arquitectura.

## Estándares Obligatorios

- [Eliminar puntos únicos de falla en seguridad](../../estandares/seguridad/security-architecture.md#7-reducción-de-superficie-de-ataque)
- [Diseñar capas de seguridad independientes y complementarias](../../estandares/seguridad/security-architecture.md#6-defense-in-depth)
- [Limitar acceso y capacidades progresivamente](../../estandares/seguridad/authorization.md)
- [Facilitar detección, contención y aislamiento de incidentes](../../estandares/observabilidad/observability.md)
- [Distribuir controles en distintos niveles arquitectónicos](../../estandares/seguridad/network-security.md)

## Referencias Relacionadas

- [Seguridad desde el Diseño](01-seguridad-desde-el-diseno.md)
- [Zero Trust](02-zero-trust.md)
- [Segmentación y Aislamiento](06-segmentacion-y-aislamiento.md)
