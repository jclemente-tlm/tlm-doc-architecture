---
sidebar_position: 9
title: Decisiones de Arquitectura
description: Decisiones arquitectónicas del Servicio de Identidad.
---

# 9. Decisiones de Arquitectura

## Decisión Principal

| ADR     | Decision                                   | Estado                 | Referencia                                                     |
| ------- | ------------------------------------------ | ---------------------- | -------------------------------------------------------------- |
| ADR-003 | Keycloak como IdP corporativo centralizado | Aceptado (Agosto 2025) | [ADR-003](../../../adrs/adr-003-keycloak-sso-autenticacion.md) |

Ver el ADR completo para la comparativa de alternativas (Auth0, AWS Cognito, Azure AD B2C, Google Identity Platform).

## Decisiones Locales al Servicio de Identidad

### DEC-01: Multi-tenant con un realm por país

- **Estado**: Aceptado
- **Contexto**: Keycloak soporta múltiples estrategias de multi-tenancy: realm único con grupos, o un `realm` por tenant. La operación en cuatro países (PE, EC, CO, MX) con regulaciones y datos independientes exige aislamiento real.
- **Decisión**: Un `realm` de Keycloak por país/tenant: `pe`, `ec`, `co`, `mx`.
- **Consecuencias**: Aislamiento total de usuarios, sesiones, configuración y políticas por país. Mayor número de realms a gestionar; mitigado con automatización Terraform/IaC.

### DEC-02: PostgreSQL como backend de Keycloak

- **Estado**: Aceptado
- **Contexto**: Keycloak soporta H2 (solo desarrollo), MySQL, PostgreSQL y MariaDB. H2 no es apto para producción; se necesita alta disponibilidad y compatibilidad con RDS Aurora.
- **Decisión**: PostgreSQL 15+ sobre AWS RDS Aurora Multi-AZ.
- **Consecuencias**: Alta disponibilidad con failover automático. Backups gestionados por RDS. Sin personalización del modelo de datos interno de Keycloak.

### DEC-03: Configuración vía IaC + Terraform (sin cambios manuales)

- **Estado**: Aceptado
- **Contexto**: La consola de administración de Keycloak permite cambios manuales que no quedan registrados en repositorio ni son reproducibles.
- **Decisión**: Toda la configuración de realms, clientes, roles y proveedores de identidad se gestiona vía Terraform (provider `mrparkers/keycloak`). Los cambios manuales en consola están prohibidos en staging y producción.
- **Consecuencias**: Configuración versionada, reproducible y auditada. Cambios requieren PR y pipeline CI/CD.

### DEC-04: Federación híbrida (LDAP + SAML/OIDC)

- **Estado**: Aceptado
- **Contexto**: Algunos países tienen directorios LDAP corporativos activos (Microsoft AD); otros usan Google Workspace (OIDC) o sistemas legacy con SAML.
- **Decisión**: Federación híbrida por realm: LDAP para países con AD activo; SAML/OIDC para Google Workspace y sistemas externos. Usuarios locales para cuentas de servicio y casos sin federación disponible.
- **Consecuencias**: Flexibilidad por país. Cada realm puede tener configuración de federación diferente.

### DEC-05: Validación JWT local en Kong (sin introspection por request)

- **Estado**: Aceptado
- **Contexto**: La validación de tokens puede hacerse en el gateway consultando a Keycloak (token introspection endpoint) o localmente con las claves JWKS públicas.
- **Decisión**: Kong (ADR-010) valida JWT localmente usando el endpoint JWKS de cada realm (`/realms/{tenant}/protocol/openid-connect/certs`). Keycloak no recibe llamadas por cada request.
- **Consecuencias**: Latencia de validación < 10ms (local vs ~50ms introspection remota). Ventana de inconsistencia al revocar tokens; mitigada con `exp` claim corto (15 min) y TTL corto de cache JWKS.
