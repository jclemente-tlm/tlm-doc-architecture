---
id: zero-trust
sidebar_position: 2
title: Zero Trust
description: Ningún componente es confiable por defecto, toda interacción se evalúa
---

# Zero Trust

Ningún componente, usuario o sistema es confiable por defecto; toda interacción debe evaluarse explícitamente. Asumir confianza implícita por pertenecer a una red o entorno amplifica el impacto de errores y compromisos de seguridad. Zero Trust elimina supuestos implícitos, reduce riesgos de accesos indebidos y movimientos laterales, estableciendo que la confianza se define, valida y limita según el contexto de cada interacción. La confianza es contextual, limitada y no permanente.

**Este lineamiento aplica a:** interacciones entre componentes y servicios, acceso de usuarios y sistemas a recursos, integraciones internas y externas, arquitecturas distribuidas y multi-tenant.

## Estándares Obligatorios

- [Implementar autenticación explícita para toda interacción](../../estandares/seguridad/authentication.md)
- [Aplicar principios Zero Trust en arquitectura de red](../../estandares/seguridad/network-security.md#zero-trust)
- [Definir límites de confianza explícitos](../../estandares/seguridad/security-architecture.md#trust-boundaries)
- [Evaluar acceso según identidad, contexto y propósito](../../estandares/seguridad/authorization.md)
- [Implementar trazabilidad completa de interacciones](../../estandares/observabilidad/observability.md)

## Referencias Relacionadas

- [Seguridad desde el Diseño](01-seguridad-desde-el-diseno.md)
- [Defensa en Profundidad](03-defensa-en-profundidad.md)
- [Mínimo Privilegio](04-minimo-privilegio.md)
- [Segmentación y Aislamiento](06-segmentacion-y-aislamiento.md)
