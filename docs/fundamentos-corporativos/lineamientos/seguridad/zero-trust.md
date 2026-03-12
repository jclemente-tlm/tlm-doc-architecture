---
id: zero-trust
sidebar_position: 2
title: Zero Trust
description: Ningún componente es confiable por defecto, toda interacción se evalúa
---

# Zero Trust

Ningún componente, usuario o sistema es confiable por defecto; toda interacción debe evaluarse explícitamente. Asumir confianza implícita por pertenecer a una red o entorno amplifica el impacto de errores y compromisos de seguridad. Zero Trust elimina supuestos implícitos, reduce riesgos de accesos indebidos y movimientos laterales, estableciendo que la confianza se define, valida y limita según el contexto de cada interacción. La confianza es contextual, limitada y no permanente.

**Este lineamiento aplica a:** interacciones entre componentes y servicios, acceso de usuarios y sistemas a recursos, integraciones internas y externas, arquitecturas distribuidas y multi-tenant.

## Prácticas Obligatorias

- [Aplicar Zero Trust networking y microsegmentación de red](../../estandares/seguridad/zero-trust-networking.md#zero-trust-networking)
- [Implementar mTLS entre servicios (autenticación y cifrado mutuos)](../../estandares/seguridad/zero-trust-networking.md#mutual-tls-mtls)
- [Evaluar cada petición explícitamente sin asumir confianza implícita](../../estandares/seguridad/zero-trust-verification.md)
- [Asumir brechas (assume breach) y diseñar para contención](../../estandares/seguridad/zero-trust-verification.md)
- [Implementar auditoría continua de accesos e interacciones](../../estandares/seguridad/security-governance.md)

## Referencias Relacionadas

- [Arquitectura Segura](arquitectura-segura.md)
- [Defensa en Profundidad](defensa-en-profundidad.md)
- [Mínimo Privilegio](minimo-privilegio.md)
- [Segmentación y Aislamiento](segmentacion-y-aislamiento.md)
