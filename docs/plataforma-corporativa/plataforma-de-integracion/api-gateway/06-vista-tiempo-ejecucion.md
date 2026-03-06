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
    participant ALB as ALB (TLS Off)
    participant K as Kong Proxy
    participant KC as Keycloak (JWKS)
    participant B as Backend Service

    C->>ALB: HTTPS POST /api/v1/...  (Bearer JWT)
    ALB->>K: HTTP (JWT forwarded)
    K->>K: Plugin jwt: verifica firma JWT
contra JWKS cacheado de Keycloak
    alt JWT inválido o expirado
        K-->>C: 401 Unauthorized
    else JWT válido
        K->>K: Plugin request-transformer:
añade X-Consumer-ID, X-Tenant-ID
        K->>B: HTTP + headers enriquecidos
        B-->>K: Respuesta del backend
        K->>K: Plugin response-transformer:
elimina cabeceras internas
        K-->>C: Respuesta final
    end
```

> Kong cachea las claves JWKS de Keycloak. La rotación de claves se propaga automáticamente al expirar el cache TTL.

## Flujo 2: Rate Limiting

```mermaid
sequenceDiagram
    participant C as Cliente
    participant K as Kong Proxy
    participant R as Redis (ElastiCache)
    participant B as Backend Service

    C->>K: Request (con tenant header)
    K->>R: INCR counter[tenant:route:window]
    R-->>K: counter = N
    alt N > límite configurado
        K-->>C: 429 Too Many Requests
RateLimit-Remaining: 0
    else N <= límite
        K->>B: Request normal
        B-->>K: Respuesta
        K-->>C: Respuesta (RateLimit-Remaining: N_restante)
    end
```

## Flujo 3: Health Check de Upstream

```mermaid
sequenceDiagram
    participant K as Kong Upstream Logic
    participant T as Target (backend instance)

    loop Cada 30s (health check activo)
        K->>T: GET /health/live
        alt HTTP 200
            K->>K: Target marcado HEALTHY
        else HTTP 5xx o timeout
            K->>K: Target marcado UNHEALTHY (excluido del balanceo)
        end
    end
    Note over K: Health check pasivo: 3 fallos consecutivos → UNHEALTHY
```

## Flujo 4: Circuit Breaker (Health Check Pasivo)

```mermaid
sequenceDiagram
    participant C as Cliente
    participant K as Kong Proxy
    participant T1 as Target A (UNHEALTHY)
    participant T2 as Target B (HEALTHY)

    C->>K: Request
    K->>K: Target A en estado UNHEALTHY
    K->>T2: Enruta a Target B
    T2-->>K: Respuesta OK
    K-->>C: Respuesta (transparente para cliente)
```

Kong no implementa circuit breaker como estado de máquina explícito; usa exclusión de targets por health checks pasivos.
Para resiliencia adicional, el backend debe implementar patrones de resiliencia internos.

## Flujo 5: Sync de Configuración (deck)

```mermaid
sequenceDiagram
    participant DEV as Developer / CI
    participant GIT as Repositorio Git
    participant CI as Pipeline CI/CD
    participant DA as deck CLI
    participant K as Kong Admin API

    DEV->>GIT: PR con cambios en kong.yml
    CI->>DA: deck validate kong.yml
    DA-->>CI: OK / Error de validación
    CI->>DA: deck diff --state kong.yml
    DA->>K: Consulta estado actual
    K-->>DA: Estado actual
    DA-->>CI: Diff de cambios
    CI->>DA: deck sync --state kong.yml (solo en merge/despliegue)
    DA->>K: Aplica cambios mínimos
    K-->>DA: OK
```
