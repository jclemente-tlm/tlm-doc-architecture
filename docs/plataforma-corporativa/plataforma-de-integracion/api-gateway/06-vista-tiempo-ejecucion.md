---
sidebar_position: 6
title: Vista de Tiempo de Ejecución
description: Flujos de ejecución clave del API Gateway con Kong OSS.
---

# 6. Vista de Tiempo de Ejecución

## Flujo 1: Request Autenticado (Sisbon)

```mermaid
sequenceDiagram
    participant C as Cliente (backend Talma)
    participant ALB as ALB
    participant K as Kong Gateway
    participant B as Sisbon NLB :8080

    C->>ALB: HTTPS POST /api/sisbon/bonificaciones/kilos-ingresados (Bearer JWT)
    ALB->>K: HTTP POST /api/sisbon/... (JWT forwarded)
    K->>K: Plugin jwt: verifica firma RS256 contra public key de tlm-mx-realm
    alt JWT inválido o expirado
        K-->>C: 401 Unauthorized
    else JWT válido
        K->>K: Plugin acl: verifica que consumer esté en sisbon-users
        alt Consumer sin acceso al grupo
            K-->>C: 403 Forbidden
        else Acceso permitido
            K->>K: Plugin rate-limiting: incrementa contador [consumer:route:ventana]
            alt Límite superado
                K-->>C: 429 Too Many Requests (RateLimit-* headers)
            else Dentro del límite
                K->>K: Plugin request-transformer: añade X-Forwarded-Authorization
                K->>K: Plugin request-size-limiting: verifica payload ≤ 1MB
                K->>B: HTTP POST /bonificaciones/kilos-ingresados (strip_path=true)
                B-->>K: Respuesta
                K-->>C: Respuesta + X-Correlation-ID header
            end
        end
    end
```

> Kong valida JWT localmente usando la clave pública RSA embebida en `_consumers.yaml`. **No hay llamada a Keycloak en tiempo de ejecución.** La clave se actualiza manualmente al rotar en Keycloak.

## Flujo 2: Integración Externa (TalentHub ATS)

```mermaid
sequenceDiagram
    participant G as Gestal Backend (Talma)
    participant K as Kong Gateway
    participant TH as TalentHub ATS API

    G->>K: POST /api-dev/gestal/ats (Bearer JWT tlm-pe)
    K->>K: Plugin jwt: verifica token tlm-pe-realm
    K->>K: Plugin acl: verifica talenthub-users
    K->>K: Plugin request-transformer:
    Note over K: • Elimina header Authorization
    Note over K: • Añade x-api-key: <api-key>
    Note over K: • Reescribe URI → /uat//lmbExGen?operacion=TALMA_CREAR_POSICION_V1&bcode=...
    K->>TH: POST /uat//lmbExGen?... (x-api-key, sin JWT)
    TH-->>K: Respuesta TalentHub
    K-->>G: Respuesta + X-Correlation-ID
```

> Kong actúa como adaptador: el backend de Talma usa JWT corporativo y Kong lo traduce a la autenticación por API key que requiere TalentHub. La API key **no debe estar en el repositorio**; debe migrarse a AWS Secrets Manager (DT-01).

## Flujo 3: Arranque con deck Bootstrap

```mermaid
sequenceDiagram
    participant DC as docker-compose up
    participant M as kong-migrations
    participant K as Kong
    participant B as kong-deck-bootstrap

    DC->>M: Inicia kong-migrations
    M->>M: kong migrations up (PostgreSQL)
    M-->>DC: Exit 0
    DC->>K: Inicia kong (depends_on: migrations)
    K->>K: Conecta a PostgreSQL, carga configuración
    DC->>B: Inicia kong-deck-bootstrap (depends_on: kong)
    B->>B: wait-for-kong.sh: GET /status → retry hasta 200
    B->>K: deck sync config/kong/{env}/*.yaml
    K-->>B: Configuración aplicada
    B-->>DC: Exit 0 (restart: "no")
```
