---
sidebar_position: 6
title: Vista de Tiempo de Ejecución
description: Flujos de ejecución clave del API Gateway con Kong OSS.
---

# 6. Vista de Tiempo de Ejecución

## Flujo 1: Request Autenticado

```mermaid
sequenceDiagram
    participant C as Cliente
    participant ALB as ALB
    participant K as API Gateway (Kong)
    participant B as Backend Service

    C->>ALB: HTTPS (Bearer JWT)
    ALB->>K: HTTP (JWT forwarded)
    K->>K: Plugin jwt: verifica firma contra JWKS cacheado de Keycloak
    alt JWT inválido o expirado
        K-->>C: 401 Unauthorized
    else JWT válido
        K->>K: Plugin request-transformer: Authorization → X-Forwarded-Authorization
        K->>B: HTTP + X-Forwarded-Authorization: Bearer <token>
        B-->>K: Respuesta
        K-->>C: Respuesta final
    end
```

> Kong cachea las claves JWKS de Keycloak. La rotación de claves se propaga automáticamente al expirar el cache TTL.

## Flujo 2: Rate Limiting

> Redis (ElastiCache) está pendiente de implementación (DT-06). Actualmente el plugin usa `policy: local` (contador por instancia). El flujo siguiente describe el comportamiento objetivo con Redis.

```mermaid
sequenceDiagram
    participant C as Cliente
    participant K as API Gateway (Kong)
    participant R as Redis (ElastiCache)
    participant B as Backend Service

    C->>K: Request (con tenant header)
    K->>R: INCR counter[tenant:route:window]
    R-->>K: counter = N
    alt N > límite configurado
        K-->>C: 429 Too Many Requests
    else N <= límite
        K->>B: Request normal
        B-->>K: Respuesta
        K-->>C: Respuesta + RateLimit-Remaining
    end
```

## Flujo 3: Resiliencia de Upstream (Health Checks)

```mermaid
sequenceDiagram
    participant K as API Gateway (Kong)
    participant T1 as Target A
    participant T2 as Target B

    loop Cada 30s (health check activo)
        K->>T1: GET /health/live
        alt HTTP 200
            K->>K: Target A marcado HEALTHY
        else HTTP 5xx / timeout
            K->>K: Target A marcado UNHEALTHY
        end
    end
    Note over K: Health check pasivo: 3 fallos consecutivos marcan UNHEALTHY
    Note over K,T2: Tráfico redirigido automáticamente a targets HEALTHY
```
