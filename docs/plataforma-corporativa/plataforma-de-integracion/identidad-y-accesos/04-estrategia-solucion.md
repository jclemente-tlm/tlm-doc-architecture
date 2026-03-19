---
sidebar_position: 4
title: Estrategia de Solución
description: Decisiones tecnológicas y patrones aplicados en el Servicio de Identidad.
---

# 4. Estrategia de Solución

## Decisiones Tecnológicas

| Decisión                | Alternativas Evaluadas                           | Seleccionada            |
| ----------------------- | ------------------------------------------------ | ----------------------- |
| Proveedor de Identidad  | Auth0, Okta, `Keycloak`                          | `Keycloak 26.4.4`      |
| Multi-tenancy           | Single tenant (`realm`), multi-tenant (`realms`) | Multi-tenant (`realms`) |
| Federación de Identidad | Solo externo, híbrido                            | Híbrido _(planificada)_ |
| Base de Datos           | MySQL, `PostgreSQL`                              | `PostgreSQL 16+`        |
| Despliegue              | VM, contenedores, serverless                     | Contenedor en `EC2`     |

## Patrones Aplicados

- Multi-tenancy: un `realm` por país/función, con aislamiento total de datos y configuración. Se definen 5 tenants: `tlm-corp` (corporativo), `tlm-pe` (Perú), `tlm-mx` (México), `tlm-ec` (Ecuador, pendiente), `tlm-co` (Colombia, pendiente).
- Federación híbrida _(planificada)_: LDAP para países con AD activo; SAML/OIDC para Google Workspace y sistemas externos. Actualmente sin IdPs externos configurados.
- Validación JWT delegada a Kong: proceso local con JWKS cacheados, sin llamadas a Keycloak por request.
- Configuración como código: definiciones de realms exportadas como JSON (`keycloak/realms/*.json`), importadas automáticamente al iniciar Keycloak (`--import-realm`).
- Despliegue por ambiente: contenedor Docker en instancias EC2 gestionado con Docker Compose. 2 ambientes de infraestructura (`nonprod`, `prod`) que cubren 3 ambientes lógicos (`dev`, `qa`, `prod`). Base de datos PostgreSQL en RDS para todos los ambientes desplegados.
- Tema corporativo: `talma-theme` con branding Talma para login, account y admin; i18n (`es`/`en`).
- Observabilidad: métricas y health checks habilitados en puerto `9000`.
