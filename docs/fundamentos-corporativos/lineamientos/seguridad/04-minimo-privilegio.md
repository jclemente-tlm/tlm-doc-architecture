---
id: minimo-privilegio
sidebar_position: 4
title: Mínimo Privilegio
description: Práctica de seguridad que establece que cada usuario, componente o sistema debe operar con el nivel mínimo de privilegios necesario para cumplir su función.
tags: [lineamiento, seguridad, least-privilege, iam, rbac]
---

# Mínimo Privilegio

Todo usuario, componente o sistema debe operar con el nivel mínimo de privilegios necesario para cumplir su función, y solo durante el tiempo requerido. Los privilegios excesivos amplifican el impacto de errores de configuración, fallos de software, credenciales comprometidas y accesos indebidos. Cuando los sistemas otorgan más permisos de los necesarios, un fallo localizado puede convertirse en incidente sistémico. El mínimo privilegio reduce el radio de impacto y facilita control, auditoría y corrección de incidentes.

**Este lineamiento aplica a:** usuarios finales y operadores, servicios y componentes, integraciones internas y externas, acceso a datos, APIs, eventos y recursos de infraestructura.

## Estándares Obligatorios

- [Implementar RBAC (Role-Based Access Control)](../../estandares/seguridad/identity-access-management.md#3-role-based-access-control-rbac)
- [Aplicar ABAC cuando corresponda](../../estandares/seguridad/identity-access-management.md#4-attribute-based-access-control-abac)
- [Implementar Just-In-Time (JIT) access](../../estandares/seguridad/identity-access-management.md#7-just-in-time-jit-access)
- [Realizar access reviews periódicos](../../estandares/seguridad/identity-access-management.md)
- [Aplicar segregation of duties](../../estandares/seguridad/security-governance.md#6-segregation-of-duties)
- [Usar service accounts con permisos mínimos](../../estandares/seguridad/identity-access-management.md#8-service-accounts)

## Referencias Relacionadas

- [Seguridad desde el Diseño](../../principios/02-seguridad-desde-el-diseno.md)
- [Zero Trust](02-zero-trust.md)
- [Defensa en Profundidad](03-defensa-en-profundidad.md)
