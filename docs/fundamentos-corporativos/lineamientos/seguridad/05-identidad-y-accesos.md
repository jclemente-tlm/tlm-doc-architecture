---
id: identidad-y-accesos
sidebar_position: 5
title: Identidad y Accesos
description: Gestión de identidades, autenticación y autorización
---

# Identidad y Accesos

La gestión fragmentada de identidades genera credenciales dispersas, permisos excesivos y ausencia de trazabilidad que facilitan accesos no autorizados y dificultan auditorías de seguridad. Esta fragmentación multiplica vectores de ataque y debilita controles de cumplimiento. Centralizar identidades mediante federación SSO, aplicar mínimo privilegio y autenticación multifactor, junto con gestión segura de identidades de servicios, establece controles consistentes, reduce superficie de ataque y permite auditoría completa de accesos en toda la plataforma.

**Este lineamiento aplica a:** Aplicaciones web y móviles, APIs internas y externas, servicios backend, acceso a infraestructura y plataforma, e integraciones entre sistemas.

## Estándares Obligatorios

- [Implementar SSO con Keycloak/OIDC](../../estandares/seguridad/sso-implementation.md)
- [Aplicar MFA obligatorio](../../estandares/seguridad/mfa.md)
- [Implementar federación de identidades](../../estandares/seguridad/identity-federation.md)
- [Gestionar identidades de servicios](../../estandares/seguridad/service-identity.md)
- [Implementar OAuth 2.0 / OIDC](../../estandares/seguridad/oauth-oidc.md)
- [Gestionar ciclo de vida de identidades](../../estandares/seguridad/identity-lifecycle.md)
- [No almacenar credenciales en código](../../estandares/seguridad/no-hardcoded-credentials.md)
- [Implementar password policies](../../estandares/seguridad/password-policies.md)
- [Rotar credenciales automáticamente](../../estandares/seguridad/credential-rotation.md)
