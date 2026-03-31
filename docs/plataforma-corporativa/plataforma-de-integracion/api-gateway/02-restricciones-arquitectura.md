---
sidebar_position: 2
title: Restricciones de Arquitectura
description: Limitaciones técnicas y organizativas que aplican al API Gateway con Kong OSS.
---

# 2. Restricciones de Arquitectura

## Restricciones Técnicas

| Restricción            | Valor                                              | Razón                                       |
| ---------------------- | -------------------------------------------------- | ------------------------------------------- |
| Tecnología de gateway  | Kong Gateway 3.9.1                                 | ADR-010, agnosticidad tecnológica           |
| Admin UI               | Konga 0.14.9 + nginx 1.29.3 (reverse proxy)        | Acceso centralizado vía path `/konga/`      |
| Configuración          | Declarativa vía `decK` (YAML por entorno)          | Trazabilidad, GitOps, reproducibilidad      |
| Base de datos de Kong  | PostgreSQL (RDS en nonprod/prod; contenedor local) | Modo DB para clustering nativo              |
| Base de datos de Konga | MySQL 5.7                                          | Requerimiento de Konga OSS                  |
| Identity provider      | Keycloak (ADR-003)                                 | SSO corporativo, JWT RS256 por realm        |
| Multi-tenancy          | Un tenant (realm) por scope (`tlm-{scope}`)        | Aislamiento criptográfico por tenant        |
| Rate limiting          | `policy: local` por consumer                       | Redis pendiente de implementación (DT-06)   |
| TLS                    | Terminación en ALB; TLS 1.3 mínimo                 | Estándar corporativo de seguridad           |
| Tamaño máx. de payload | 1 MB (plugin `request-size-limiting`)              | Uniforme para todos los servicios (ADR-010) |
| Reintentos en POST     | `retries: 0`                                       | Operaciones no idempotentes (ADR-009)       |

## Restricciones Organizativas

| Restricción         | Descripción                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| Propiedad operativa | El equipo de Plataforma es responsable del ciclo de vida de Kong                                  |
| Plugins permitidos  | Solo plugins del Kong Hub oficial; plugins custom requieren aprobación de Arquitectura            |
| Tenants soportados  | `tlm-mx`, `tlm-pe`, `tlm-ec`, `tlm-co`, `tlm-corp`; nuevos tenants siguen el patrón `tlm-{scope}` |
| Secretos            | Nunca en repositorio; se inyectan vía variables de entorno (`.env`, AWS Secrets Manager en prod)  |
| Patrón de rutas     | `/api/{sistema}` en PROD; `/api-qa/{sistema}` en QA; `/api-dev/{sistema}` en DEV/local            |

## Restricciones de Proceso

| Restricción              | Descripción                                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Gestión de configuración | Cambios exploratorios vía Konga; cambios definitivos en `config/kong/{env}/*.yaml` vía PR + `make sync-{env}` |
| Ciclo de despliegue      | `make sync-local` → `make sync-nonprod` → `make sync-prod` (siempre en orden ascendente)                      |
| Cambios de seguridad     | Rutas y plugins de seguridad requieren aprobación del equipo de Seguridad antes del merge                     |
| Rotación de claves       | Al rotar claves en Keycloak, actualizar `rsa_public_key` en `_consumers.yaml` de los 3 entornos               |
