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

### DEC-01: Multi-tenant con realms por país y corporativo

- **Estado**: Aceptado
- **Contexto**: Keycloak soporta múltiples estrategias de multi-tenancy: realm único con grupos, o un `realm` por tenant. La operación en múltiples países con regulaciones y datos independientes exige aislamiento real. Adicionalmente, se requiere un realm corporativo para servicios transversales.
- **Decisión**: Un `realm` por país/tenant más un realm corporativo, con nomenclatura `tlm-{código}`. Se definen 5 tenants: `tlm-corp` (corporativo), `tlm-pe` (Perú), `tlm-mx` (México), `tlm-ec` (Ecuador), `tlm-co` (Colombia). Actualmente configurados los 3 primeros.
- **Consecuencias**: Aislamiento total de usuarios, sesiones, configuración y políticas por tenant. El realm corporativo (`tlm-corp`) centraliza servicios internos (Grafana, herramientas). Realms `tlm-ec` y `tlm-co` pendientes de creación y configuración.

### DEC-02: PostgreSQL como backend de Keycloak

- **Estado**: Aceptado
- **Contexto**: Keycloak soporta H2 (solo desarrollo), MySQL, PostgreSQL y MariaDB. H2 no es apto para producción; se necesita alta disponibilidad y compatibilidad con RDS Aurora.
- **Decisión**: PostgreSQL 16+ sobre AWS RDS (nonprod y prod) o contenedor `postgres:16-alpine` (desarrollo local).
- **Consecuencias**: Alta disponibilidad con failover automático en producción. Backups gestionados por RDS. En desarrollo local, PostgreSQL se levanta como contenedor en Docker Compose.

### DEC-03: Configuración vía realm JSON export + Docker Compose

- **Estado**: Aceptado
- **Contexto**: La consola de administración de Keycloak permite cambios manuales que no quedan registrados en repositorio ni son reproducibles.
- **Decisión**: La configuración de realms, clientes, roles y scopes se exporta como JSON y se versiona en el repositorio `tlm-infra-keycloak` (`keycloak/realms/*.json`). Los realms se importan automáticamente al iniciar Keycloak (`--import-realm`). El despliegue se ejecuta como contenedor Docker en instancias EC2, gestionado con Docker Compose por ambiente (`local`, `nonprod`, `prod`). Se mantienen 2 ambientes de infraestructura (`nonprod` para dev/qa, `prod`) y 3 ambientes lógicos (`dev`, `qa`, `prod`).
- **Consecuencias**: Configuración versionada en Git y reproducible. Despliegue controlado por Makefile. Para importación manual existe `scripts/import-realms.sh`.

### DEC-04: Federación híbrida (LDAP + SAML/OIDC)

- **Estado**: Planificado
- **Contexto**: Algunos países tienen directorios LDAP corporativos activos (Microsoft AD); otros usan Google Workspace (OIDC) o sistemas legacy con SAML.
- **Decisión**: Federación híbrida por realm: LDAP para países con AD activo; SAML/OIDC para Google Workspace y sistemas externos. Usuarios locales para cuentas de servicio y casos sin federación disponible.
- **Implementación actual**: No hay Identity Providers configurados en ninguno de los realms. Todos los usuarios se gestionan localmente por realm.
- **Consecuencias**: Flexibilidad por país. Cada realm puede tener configuración de federación diferente una vez implementada.

### DEC-05: Validación JWT local en Kong (sin introspection por request)

- **Estado**: Aceptado
- **Contexto**: La validación de tokens puede hacerse en el gateway consultando a Keycloak (token introspection endpoint) o localmente con las claves JWKS públicas.
- **Decisión**: Kong (ADR-010) valida JWT localmente usando el endpoint JWKS de cada realm (`/auth/realms/{tenant}/protocol/openid-connect/certs`). Keycloak no recibe llamadas por cada request.
- **Consecuencias**: Latencia de validación < 10ms (local vs ~50ms introspection remota). Ventana de inconsistencia al revocar tokens; mitigada con `exp` claim corto (5 min / 300s) y TTL corto de cache JWKS.
