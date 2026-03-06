---
sidebar_position: 8
title: Conceptos Transversales
description: Patrones y configuraciones aplicadas transversalmente en el API Gateway Kong OSS.
---

# 8. Conceptos Transversales

## Autenticación y Autorización (Plugin `jwt`)

Kong valida los JWT emitidos por Keycloak sin reenviar el token al backend para validación.

```yaml
# kong.yml — Plugin jwt a nivel de service o global
plugins:
  - name: jwt
    config:
      uri_param_names: []
      cookie_names: []
      header_names:
        - Authorization
      claims_to_verify:
        - exp
        - nbf
      key_claim_name: iss
      secret_is_base64: false
      anonymous: ~           # sin anónimo; rechaza si no hay JWT válido
```

El endpoint JWKS de Keycloak se configura en la entidad `Consumer` o via `jwt_secrets`.
El flujo de validación es local (sin llamada a Keycloak en cada request), con cache hasta la rotación de claves.

Headers inyectados al backend tras validación exitosa:

| Header | Contenido |
|---|---|
| `X-Consumer-ID` | ID del consumer de Kong |
| `X-Consumer-Username` | Username / tenant ID |
| `X-Credential-Identifier` | Claim `sub` del JWT |

## Rate Limiting (Plugin `rate-limiting`)

```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 1000          # 1000 req/min por consumer
      hour: 50000
      policy: redis
      redis_host: redis-host.cache.amazonaws.com
      redis_port: 6379
      redis_ssl: true
      limit_by: consumer    # o: ip, header, service
      hide_client_headers: false
      error_code: 429
      error_message: "Rate limit exceeded"
```

Respuesta al cliente cuando se supera el límite:

| Header | Descripción |
|---|---|
| `RateLimit-Limit` | Límite configurado |
| `RateLimit-Remaining` | Requests restantes en la ventana |
| `RateLimit-Reset` | Segundos hasta el reset de la ventana |

## CORS (Plugin `cors`)

```yaml
plugins:
  - name: cors
    config:
      origins:
        - "https://*.talma.com"
        - "https://*.talmaaereo.com"
      methods:
        - GET
        - POST
        - PUT
        - DELETE
        - OPTIONS
      headers:
        - Authorization
        - Content-Type
        - X-Correlation-ID
      exposed_headers:
        - X-Kong-Upstream-Latency
      credentials: true
      max_age: 3600
      preflight_continue: false
```

## Observabilidad

### Métricas (Plugin `prometheus`)

```yaml
plugins:
  - name: prometheus
    config:
      per_consumer: true
      status_code_metrics: true
      latency_metrics: true
      bandwidth_metrics: true
      upstream_health_metrics: true
```

Las métricas se exponen en `kong-host:8001/metrics` y son scrapeadas por Prometheus.
Dashboards en Grafana con alertas sobre latencia p95, tasa de errores 5xx y health de upstreams.

### Trazas Distribuidas (Plugin `zipkin`)

```yaml
plugins:
  - name: zipkin
    config:
      http_endpoint: http://tempo-svc:9411/api/v2/spans
      sample_ratio: 1.0         # 100% en desarrollo; reducir en producción
      include_credential: true
      traceid_byte_count: 16
      header_type: b3
```

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

```yaml
plugins:
  - name: response-transformer
    config:
      add:
        headers:
          - "Strict-Transport-Security: max-age=31536000; includeSubDomains"
          - "X-Content-Type-Options: nosniff"
          - "X-Frame-Options: DENY"
          - "Referrer-Policy: strict-origin-when-cross-origin"
      remove:
        headers:
          - "X-Kong-Upstream-Status"
          - "Server"
```
