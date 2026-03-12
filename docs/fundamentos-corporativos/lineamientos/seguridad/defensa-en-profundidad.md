---
id: defensa-en-profundidad
sidebar_position: 3
title: Defensa en Profundidad
description: Múltiples capas de protección independientes en la arquitectura
---

# Defensa en Profundidad

La arquitectura debe incorporar múltiples capas de protección independientes, para que la falla o evasión de un control no comprometa la seguridad del sistema. Ningún control es infalible: las configuraciones fallan, los accesos pueden ser mal otorgados y los mecanismos de protección pueden ser evadidos. La defensa en profundidad establece que la seguridad no depende de un único control, sino de la combinación coherente de múltiples barreras complementarias que limitan el alcance y propagación de incidentes.

**Este lineamiento aplica a:** componentes y servicios, acceso a datos y recursos críticos, integraciones internas y externas, flujos de información dentro de la arquitectura.

## Prácticas Obligatorias

- [Implementar seguridad en múltiples capas independientes](../../estandares/seguridad/security-governance.md#4-defense-in-depth)
- [Aislar entornos e infraestructura por niveles de confianza](../../estandares/seguridad/environment-isolation.md)
- [Aplicar segmentación de red, WAF y protección DDoS](../../estandares/seguridad/network-segmentation.md)
- [Aplicar controles de seguridad en capa de aplicación](../../estandares/seguridad/security-governance.md)
- [Implementar seguridad de datos en reposo y en tránsito](../../estandares/seguridad/data-protection.md)

## Referencias Relacionadas

- [Arquitectura Segura](arquitectura-segura.md)
- [Zero Trust](zero-trust.md)
- [Segmentación y Aislamiento](segmentacion-y-aislamiento.md)
