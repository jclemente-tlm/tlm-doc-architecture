---
sidebar_position: 9
title: Decisiones de Arquitectura
description: Decisiones arquitectónicas relevantes del API Gateway con Kong OSS.
---

# 9. Decisiones de Arquitectura

## Decisión Principal

| ADR     | Decisión                              | Estado                | Referencia                                           |
| ------- | ------------------------------------- | --------------------- | ---------------------------------------------------- |
| ADR-010 | Kong OSS como API Gateway corporativo | Aceptado (Enero 2026) | [ADR-010](../../../adrs/adr-010-kong-api-gateway.md) |

Ver el ADR completo para la comparativa de alternativas (YARP, AWS API Gateway, Traefik, NGINX Plus, Apigee).

## Decisiones Locales al API Gateway

### DEC-01: Configuración Declarativa con deck

- **Estado**: Aceptado
- **Contexto**: Kong puede gestionarse vía Admin API imperativamente o vía `deck` (declarativo/GitOps).
- **Decisión**: Toda la configuración se gestiona con `deck` y archivos YAML en repositorio Git.
- **Consecuencias**: Trazabilidad completa, entornos reproducibles, integración natural con CI/CD. El estado real de Kong siempre debe coincidir con el repositorio.

### DEC-02: Rate Limiting con Redis (ElastiCache)

- **Estado**: Aceptado _(pendiente de implementación — ver DT-06)_
- **Contexto**: Kong ofrece rate limiting local (por instancia) o distribuido (Redis). Con múltiples instancias ECS, el conteo local es inconsistente.
- **Decisión**: Plugin `rate-limiting` con `policy: redis` apuntando a ElastiCache.
- **Consecuencias**: Límites coherentes entre instancias. Dependencia de disponibilidad de Redis (mitigada con Redis Cluster).

### DEC-03: Validación JWT Local en Kong

- **Estado**: Aceptado
- **Contexto**: La validación JWT puede hacerse en Kong (con JWKS cacheado) o delegarse al backend.
- **Decisión**: Kong valida JWT con el plugin `jwt` usando las claves públicas de Keycloak. Los backends reciben requests ya autenticados con headers enriquecidos.
- **Consecuencias**: Reducción de latencia (sin llamada a Keycloak por request). Ventana de inconsistencia al rotar claves (mitigada con TTL de cache corto).

### DEC-04: Kong en Modo DB (PostgreSQL)

- **Estado**: Aceptado
- **Contexto**: Kong soporta modo DB-less (sin base de datos) o modo DB (PostgreSQL/Cassandra). El modo DB-less no soporta el Admin API dinámico.
- **Decisión**: Kong en modo DB con PostgreSQL RDS para clustering nativo y Admin API habilitado.
- **Consecuencias**: Capacidad de clustering entre instancias ECS y uso de `deck`. Dependencia de disponibilidad de RDS (mitigada con Multi-AZ).
