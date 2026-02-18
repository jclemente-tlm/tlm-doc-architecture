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

- [Implementar autenticación mutua](../../estandares/seguridad/mutual-authentication.md)
- [Aplicar Zero Trust networking](../../estandares/seguridad/zero-trust-networking.md)
- [Evaluar cada petición explícitamente](../../estandares/seguridad/explicit-verification.md)
- [Asumir brechas (assume breach)](../../estandares/seguridad/assume-breach.md)
- [Implementar micro-segmentación](../../estandares/seguridad/micro-segmentation.md)
- [Usar mTLS entre servicios](../../estandares/seguridad/mtls.md)
- [Implementar auditoría continua](../../estandares/seguridad/continuous-audit.md)
- [Aplicar context-aware access](../../estandares/seguridad/context-aware-access.md)

## Referencias Relacionadas

- [Arquitectura Segura](01-arquitectura-segura.md)
- [Defensa en Profundidad](03-defensa-en-profundidad.md)
- [Mínimo Privilegio](04-minimo-privilegio.md)
- [Segmentación y Aislamiento](06-segmentacion-y-aislamiento.md)
