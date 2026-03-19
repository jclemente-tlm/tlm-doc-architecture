---
sidebar_position: 4
title: Estrategia de Solución
description: Decisiones tecnológicas y patrones aplicados en el Servicio de Identidad.
---

# 4. Estrategia de Solución

## Decisiones Tecnológicas

| Dimensión               | Decisión                | Justificación                                                  |
| ----------------------- | ----------------------- | -------------------------------------------------------------- |
| Proveedor de Identidad  | `Keycloak 26.4.4`      | Open source, multi-tenant nativo, protocolo OIDC/SAML completo (ADR-003) |
| Multi-tenancy           | Multi-tenant (`realms`) | Regulaciones y datos independientes por país exigen aislamiento real      |
| Federación de Identidad | Híbrido _(planificada)_ | Países con AD activo (LDAP) y otros con Google Workspace (OIDC)          |
| Base de Datos           | `PostgreSQL 16+`        | Compatibilidad con RDS, alta disponibilidad, soporte corporativo         |
| Despliegue              | Contenedor en `EC2`     | Consistencia con modelo de infraestructura actual; Docker Compose         |

## Patrones Aplicados

- Multi-tenancy: un `realm` por país/función, con aislamiento total de datos y configuración. Se definen 5 tenants: `tlm-corp` (corporativo), `tlm-pe` (Perú), `tlm-mx` (México), `tlm-ec` (Ecuador, pendiente), `tlm-co` (Colombia, pendiente).
- Federación híbrida _(planificada)_: LDAP para países con AD activo; SAML/OIDC para Google Workspace y sistemas externos. Actualmente sin IdPs externos configurados.
- Validación JWT delegada a Kong: proceso local con JWKS cacheados, sin llamadas a Keycloak por request.
- Configuración como código: definiciones de realms exportadas como JSON (`keycloak/realms/*.json`), importadas automáticamente al iniciar Keycloak (`--import-realm`).
- Despliegue por ambiente: contenedor Docker en instancias EC2 gestionado con Docker Compose. 2 ambientes de infraestructura (`nonprod`, `prod`) que cubren 3 ambientes lógicos (`dev`, `qa`, `prod`). Base de datos PostgreSQL en RDS para todos los ambientes desplegados.
- Tema corporativo: `talma-theme` con branding Talma para login, account y admin; i18n (`es`/`en`).
- Observabilidad: métricas y health checks habilitados en puerto `9000`.
