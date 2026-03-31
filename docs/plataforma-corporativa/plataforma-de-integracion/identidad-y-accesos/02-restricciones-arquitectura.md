---
sidebar_position: 2
title: Restricciones de Arquitectura
description: Limitaciones técnicas y organizativas del Servicio de Identidad.
---

# 2. Restricciones de la Arquitectura

## Restricciones Técnicas

| Categoría     | Restricción                        | Impacto en la arquitectura                    |
| ------------- | ---------------------------------- | --------------------------------------------- |
| Plataforma    | `Keycloak 26.4.4`                  | Define IdP, APIs y federación                 |
| Base de datos | `PostgreSQL 16+` (RDS)               | Esquema multi-tenant, alta disponibilidad       |
| Contenedores  | `Docker`                             | Portabilidad y despliegue                       |
| Despliegue    | Contenedor en `EC2` + `Docker Compose` | 2 ambientes infra (nonprod, prod); 3 lógicos (dev, qa, prod) |
| Protocolos    | `OAuth2`/`OIDC`, `SAML`              | Interoperabilidad y seguridad                   |
| Imagen        | `quay.io/keycloak/keycloak:26.4.4`   | Imagen oficial de Keycloak                      |
| Ruta base     | `/auth`                              | Todos los endpoints bajo `/auth`                |

## Restricciones de Seguridad y Compliance

| Aspecto      | Requerimiento           | Referencia                               |
| ------------ | ----------------------- | ---------------------------------------- |
| Cumplimiento | GDPR, ISO 27001, SOX    | Ver referencias                          |
| MFA          | Obligatorio para admins | Acceso crítico                           |
| Cifrado      | `TLS 1.3`, `AES-256`    | Protección de datos en tránsito y reposo |
| Token        | `JWT RS256`             | Integridad y autenticidad                |

## Restricciones Organizativas y Operativas

| Área           | Restricción                        | Impacto                       |
| -------------- | ---------------------------------- | ----------------------------- |
| Operaciones    | DevOps 24/7                        | Soporte continuo              |
| Multi-tenancy  | Aislamiento por `tenant` (`realm`) | Independencia de clientes     |
| Documentación  | Arc42 + ADR                        | Trazabilidad de decisiones    |
| Automatización | `Docker Compose`, CI/CD            | Despliegue seguro y repetible |

## Observabilidad

| Herramienta      | Propósito           | Integración                         |
| ---------------- | ------------------- | ----------------------------------- |
| Prometheus/Mimir | Métricas            | Exportador Keycloak → Mimir/Grafana |
| Loki             | Logs centralizados  | Logging estructurado vía Fluent Bit |
| Tempo            | Trazas distribuidas | OTLP (OpenTelemetry)                |

> CloudWatch solo se usa para monitoreo de infraestructura AWS (EC2, RDS, ALB); logs de aplicación van a Loki.
