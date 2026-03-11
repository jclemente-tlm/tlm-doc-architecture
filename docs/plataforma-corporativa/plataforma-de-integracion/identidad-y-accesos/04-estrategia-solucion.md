---
sidebar_position: 4
title: Estrategia de Solución
description: Decisiones tecnológicas y patrones aplicados en el Servicio de Identidad.
---

# 4. Estrategia de Solución

## Decisiones Tecnológicas

| Decisión                | Alternativas Evaluadas                           | Seleccionada            |
| ----------------------- | ------------------------------------------------ | ----------------------- |
| Proveedor de Identidad  | Auth0, Okta, `Keycloak`                          | `Keycloak`              |
| Multi-tenancy           | Single tenant (`realm`), multi-tenant (`realms`) | Multi-tenant (`realms`) |
| Federación de Identidad | Solo externo, híbrido                            | Híbrido                 |
| Base de Datos           | MySQL, `PostgreSQL`                              | `PostgreSQL`            |
| Despliegue              | VM, contenedores, serverless                     | Contenedores            |

## Patrones Aplicados

- Multi-tenancy: un `realm` de Keycloak por país, con aislamiento total de datos y configuración.
- Federación híbrida: LDAP para países con AD activo; SAML/OIDC para Google Workspace y sistemas externos.
- Validación JWT delegada a Kong: proceso local con JWKS cacheados, sin llamadas a Keycloak por request.
- Infraestructura como código: `Terraform` para configuración de realms, clientes y roles; cambios manuales prohibidos en staging y producción.
- Observabilidad: métricas vía Prometheus → Mimir/Grafana; logs → Loki; trazas → Tempo.
