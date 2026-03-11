---
sidebar_position: 8
title: Conceptos Transversales
description: Patrones y configuraciones aplicadas transversalmente en el API Gateway Kong OSS.
---

# 8. Conceptos Transversales

## Autenticación y Autorización (Plugin `jwt`)

Kong valida los JWT emitidos por Keycloak sin reenviar el token al backend.

- Validación local contra claves JWKS cacheadas de Keycloak (sin llamada a Keycloak por request).
- Configuración clave: `claims_to_verify: [exp, nbf]`, `key_claim_name: iss`, header `Authorization`.
- Sin JWT válido → `401 Unauthorized` antes de llegar al backend.

Headers inyectados al backend tras validación exitosa:

| Header                    | Contenido               |
| ------------------------- | ----------------------- |
| `X-Consumer-ID`           | ID del consumer de Kong |
| `X-Consumer-Username`     | Username / tenant ID    |
| `X-Credential-Identifier` | Claim `sub` del JWT     |

## Rate Limiting (Plugin `rate-limiting`)

- `policy: redis` — contadores distribuidos en ElastiCache; coherentes entre instancias Kong. **_(Redis pendiente de implementación — DT-06; actualmente usando `policy: local`)_**
- `limit_by: consumer` — límite por tenant; configurable por IP, header o servicio.
- Límites de referencia: `1000 req/min`, `50000 req/hora` por consumer (ajustable por ruta).

Respuesta al cliente cuando se supera el límite (`429`):

| Header                | Descripción                           |
| --------------------- | ------------------------------------- |
| `RateLimit-Limit`     | Límite configurado                    |
| `RateLimit-Remaining` | Requests restantes en la ventana      |
| `RateLimit-Reset`     | Segundos hasta el reset de la ventana |

## CORS (Plugin `cors`)

Permite acceso desde aplicaciones web en dominios `*.talma.com` y `*.talmaaereo.com`.
Métodos permitidos: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`. Credenciales habilitadas (`credentials: true`).

> La config completa de orígenes y headers se gestiona en `kong.yml` del repositorio de infraestructura.

## Observabilidad

### Métricas → Mimir/Grafana (Plugin `prometheus`)

Plugin habilitado globalmente. Expone métricas en `kong-host:8001/metrics`; scrapeadas por Prometheus con Mimir como backend a largo plazo. Dashboards en Grafana con alertas sobre latencia p95 y tasa de errores 5xx.

Métricas clave: `kong_latency_bucket`, `kong_http_requests_total`, `kong_upstream_target_health`.

### Trazas → Tempo (Plugin `zipkin`)

Kong envía trazas al endpoint Zipkin-compatible de Tempo (`tempo-svc:9411`).

- `sample_ratio: 0.1` en producción (10%); `1.0` solo en staging/desarrollo.
- `header_type: b3` para propagación de contexto.

### Logs → Loki

Kong emite logs en JSON por `stdout`. En ECS Fargate, Fluent Bit (FireLens sidecar) los reenvía a Loki.
Labels indexados: `job=kong`, `env`, `status`, `route`.

## Multi-tenancy (Kong Workspaces)

Cada país/cliente tiene su propio **Workspace** en Kong. La configuración entre workspaces está aislada.

```
Kong Workspaces:
├── default          # Configuración global compartida
├── pe               # Perú
├── ec               # Ecuador
├── co               # Colombia
└── mx               # México
```

El plugin `request-transformer` inyecta el header `X-Tenant-ID` en cada ruta:

```yaml
plugins:
  - name: request-transformer
    config:
      add:
        headers:
          - "X-Tenant-ID: pe"
          - "X-Correlation-ID: $(request_id)"
```

## Headers de Seguridad (Plugin `response-transformer`)

Añadidos en todas las respuestas al cliente:

| Header                      | Valor                                 |
| --------------------------- | ------------------------------------- |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options`    | `nosniff`                             |
| `X-Frame-Options`           | `DENY`                                |
| `Referrer-Policy`           | `strict-origin-when-cross-origin`     |

Headers internos eliminados de la respuesta: `X-Kong-Upstream-Status`, `Server`.
