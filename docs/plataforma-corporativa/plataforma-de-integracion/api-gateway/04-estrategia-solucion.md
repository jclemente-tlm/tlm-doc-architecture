---
sidebar_position: 4
title: Estrategia de Solución
description: Decisiones tecnológicas y de diseño clave del API Gateway con Kong OSS.
---

# 4. Estrategia de Solución

## Decisiones Tecnológicas

| Dimensión | Decisión | Justificación |
|---|---|---|
| API Gateway | **Kong OSS** | Agnosticidad, plugins maduros, escalabilidad enterprise (ADR-010) |
| Configuración | **deck YAML** (declarativo) | GitOps, trazabilidad, reproducibilidad en todos los entornos |
| Autenticación | **Plugin `jwt`** + Keycloak JWKS URI | Validación local de JWT; Keycloak como fuente de verdad |
| Rate limiting | **Plugin `rate-limiting`** + Redis | Ventana deslizante distribuida entre instancias |
| Observabilidad | **Plugin `prometheus`** + plugin `zipkin` | Stack Prometheus/Grafana corporativo (Grafana, Mimir, Tempo) |
| Resiliencia | **Upstream health checks** (activos + pasivos) | Detección automática de backends degradados |
| Multi-tenancy | **Kong Workspaces** + headers de tenant | Aislamiento de configuración por país/cliente |
| Despliegue | **AWS ECS Fargate** + Terraform | Infraestructura como código, sin gestión de servidores |

## Modelo de Configuración Declarativa

Toda la configuración de Kong se gestiona con `deck` (ADR-010):

```
kong.yml           # Configuración declarativa (Services, Routes, Plugins, Upstreams)
    ↓ deck validate     (CI: validación antes del merge)
    ↓ deck diff         (revisión de cambios en PR)
    ↓ deck sync         (CD: aplicación en despliegue)
```

Esta estrategia garantiza que el estado real de Kong siempre coincide con el repositorio.

## Flujo de Autenticación

```
Cliente → Kong (Plugin jwt) → Verifica firma JWT contra JWKS de Keycloak
                            → Extrae claims (tenant, roles)
                            → Enruta al backend con headers enriquecidos (X-Consumer-ID, X-Tenant-ID)
```

## Enrutamiento Multi-tenant

Cada país/cliente tiene su propio `Workspace` en Kong y sus propias `Routes` con host o prefijo de path diferenciado.
Los backends reciben el header `X-Tenant-ID` inyectado por el plugin `request-transformer`.
