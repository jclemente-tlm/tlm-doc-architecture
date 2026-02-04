---
id: identidad-y-accesos
sidebar_position: 2
title: Identidad y Accesos
description: Gestión de identidades, autenticación y autorización
---

# Identidad y Accesos

La gestión fragmentada de identidades genera credenciales dispersas, permisos excesivos y ausencia de trazabilidad que facilitan accesos no autorizados y dificultan auditorías de seguridad. Esta fragmentación multiplica vectores de ataque y debilita controles de cumplimiento. Centralizar identidades mediante federación SSO, aplicar mínimo privilegio y autenticación multifactor, junto con gestión segura de identidades de servicios, establece controles consistentes, reduce superficie de ataque y permite auditoría completa de accesos en toda la plataforma.

**Este lineamiento aplica a:** Aplicaciones web y móviles, APIs internas y externas, servicios backend, acceso a infraestructura y plataforma, e integraciones entre sistemas.

## Estándares Obligatorios

- [Usar identidad federada y SSO corporativo para usuarios](../../estandares/seguridad/identity-access-management.md#4-autenticación-sso)
- [Implementar autenticación multifactor (MFA) para accesos críticos](../../estandares/seguridad/identity-access-management.md#43-multi-factor-authentication-mfa)
- [Aplicar mínimo privilegio en autorizaciones](../../estandares/seguridad/identity-access-management.md#rbac)
- [Gestionar identidades de servicios](../../estandares/seguridad/identity-access-management.md)
- [No almacenar credenciales en código o configuración](../../estandares/seguridad/secrets-key-management.md)
