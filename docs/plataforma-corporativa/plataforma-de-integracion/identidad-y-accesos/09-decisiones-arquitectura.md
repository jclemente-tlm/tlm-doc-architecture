---
sidebar_position: 9
title: Decisiones de Arquitectura
description: Decisiones arquitectonicas del Servicio de Identidad.
---

# 9. Decisiones de Arquitectura

## Decision Principal

| ADR | Decision | Estado | Referencia |
|---|---|---|---|
| ADR-003 | Keycloak como IdP corporativo centralizado | Aceptado (Agosto 2025) | [ADR-003](../../../adrs/adr-003-keycloak-sso-autenticacion.md) |

Ver el ADR completo para la comparativa de alternativas (Auth0, AWS Cognito, Azure AD B2C, Google Identity Platform).

## Decisiones Locales al Servicio de Identidad

### DEC-01: Multi-tenant con un realm por pais

- **Estado**: Aceptado
- **Contexto**: Keycloak soporta multiples estrategias de multi-tenancy: realm unico con grupos, o un `realm` por tenant. La operacion en cuatro paises (PE, EC, CO, MX) con regulaciones y datos independientes exige aislamiento real.
- **Decision**: Un `realm` de Keycloak por pais/tenant: `pe`, `ec`, `co`, `mx`.
- **Consecuencias**: Aislamiento total de usuarios, sesiones, configuracion y politicas por pais. Mayor numero de realms a gestionar; mitigado con automatizacion Terraform/IaC.

### DEC-02: PostgreSQL como backend de Keycloak

- **Estado**: Aceptado
- **Contexto**: Keycloak soporta H2 (solo desarrollo), MySQL, PostgreSQL y MariaDB. H2 no es apto para produccion; se necesita alta disponibilidad y compatibilidad con RDS Aurora.
- **Decision**: PostgreSQL 15+ sobre AWS RDS Aurora Multi-AZ.
- **Consecuencias**: Alta disponibilidad con failover automatico. Backups gestionados por RDS. Sin personalizacion del modelo de datos interno de Keycloak.

### DEC-03: Configuracion via IaC + Terraform (sin cambios manuales)

- **Estado**: Aceptado
- **Contexto**: La consola de administracion de Keycloak permite cambios manuales que no quedan registrados en repositorio ni son reproducibles.
- **Decision**: Toda la configuracion de realms, clientes, roles y proveedores de identidad se gestiona via Terraform (provider `mrparkers/keycloak`). Los cambios manuales en consola estan prohibidos en staging y produccion.
- **Consecuencias**: Configuracion versionada, reproducible y auditada. Cambios requieren PR y pipeline CI/CD.

### DEC-04: Federacion hibrida (LDAP + SAML/OIDC)

- **Estado**: Aceptado
- **Contexto**: Algunos paises tienen directorios LDAP corporativos activos (Microsoft AD); otros usan Google Workspace (OIDC) o sistemas legacy con SAML.
- **Decision**: Federacion hibrida por realm: LDAP para paises con AD activo; SAML/OIDC para Google Workspace y sistemas externos. Usuarios locales para cuentas de servicio y casos sin federacion disponible.
- **Consecuencias**: Flexibilidad por pais. Cada realm puede tener configuracion de federacion diferente.

### DEC-05: Validacion JWT local en Kong (sin introspection por request)

- **Estado**: Aceptado
- **Contexto**: La validacion de tokens puede hacerse en el gateway consultando a Keycloak (token introspection endpoint) o localmente con las claves JWKS publicas.
- **Decision**: Kong (ADR-010) valida JWT localmente usando el endpoint JWKS de cada realm (`/realms/{tenant}/protocol/openid-connect/certs`). Keycloak no recibe llamadas por cada request.
- **Consecuencias**: Latencia de validacion < 10ms (local vs ~50ms introspection remota). Ventana de inconsistencia al revocar tokens; mitigada con `exp` claim corto (15 min) y TTL corto de cache JWKS.
