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

- [Implementar seguridad en múltiples capas](../../estandares/seguridad/security-governance.md#4-defense-in-depth)
- [Aplicar seguridad perimetral](../../estandares/seguridad/network-security.md#5-perimetersecurity)
- [Implementar seguridad de red](../../estandares/seguridad/network-security.md)
- [Aplicar seguridad de aplicación](../../estandares/seguridad/security-governance.md#3-application-security-owasp-top-10)
- [Implementar seguridad de datos](../../estandares/seguridad/data-protection.md)
- [Configurar WAF y protección DDoS](../../estandares/seguridad/network-security.md)

## Referencias Relacionadas

- [Arquitectura Segura](01-arquitectura-segura.md)
- [Zero Trust](02-zero-trust.md)
- [Segmentación y Aislamiento](06-segmentacion-y-aislamiento.md)
