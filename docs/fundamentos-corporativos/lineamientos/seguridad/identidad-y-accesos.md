---
id: identidad-y-accesos
sidebar_position: 5
title: Identidad y Accesos
description: Gestión de identidades, autenticación y autorización
---

# Identidad y Accesos

La gestión fragmentada de identidades genera credenciales dispersas, permisos excesivos y ausencia de trazabilidad que facilitan accesos no autorizados y dificultan auditorías de seguridad. Esta fragmentación multiplica vectores de ataque y debilita controles de cumplimiento. Centralizar identidades mediante federación SSO, aplicar mínimo privilegio y autenticación multifactor, junto con gestión segura de identidades de servicios, establece controles consistentes, reduce superficie de ataque y permite auditoría completa de accesos en toda la plataforma.

**Este lineamiento aplica a:** aplicaciones web y móviles, APIs internas y externas, servicios backend, acceso a infraestructura y plataforma, e integraciones entre sistemas.

## Prácticas Obligatorias

- [Implementar Single Sign-On corporativo](../../estandares/seguridad/sso-mfa-rbac.md)
- [Aplicar autenticación multi-factor obligatoria](../../estandares/seguridad/sso-mfa-rbac.md)
- [Implementar federación de identidades](../../estandares/seguridad/iam-advanced.md)
- [Gestionar identidades de servicios (service accounts, workload identity)](../../estandares/seguridad/iam-advanced.md)
- [Gestionar ciclo de vida de identidades](../../estandares/seguridad/iam-advanced.md)
- [Implementar políticas de contraseñas](../../estandares/seguridad/iam-advanced.md)
- [Nombrar recursos de Keycloak con nomenclatura estándar](../../estandares/seguridad/keycloak-resource-naming.md)
- [Autenticar APIs con JWT para servicios internos](../../estandares/seguridad/api-authentication.md)

## Referencias Relacionadas

- [Zero Trust](./zero-trust.md)
- [Mínimo Privilegio](./minimo-privilegio.md)
- [Arquitectura Segura](./arquitectura-segura.md)
- [Protección de Datos](./proteccion-de-datos.md)
