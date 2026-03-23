---
sidebar_position: 8
title: Conceptos Transversales
description: Patrones y configuraciones aplicadas transversalmente en el API Gateway Kong OSS.
---

# 8. Conceptos Transversales

## Autenticación y Autorización

### Autenticación (Plugin `jwt`)

Kong valida los JWT RS256 emitidos por Keycloak usando la **clave pública RSA embebida** en `_consumers.yaml`. No hay llamada a Keycloak en tiempo de ejecución.

- `key_claim_name: iss` — el claim `iss` del JWT (issuer URL del realm) identifica al consumer.
- `claims_to_verify: [exp]` — se verifica expiración del token.
- `run_on_preflight: false` — las peticiones OPTIONS de CORS no requieren JWT.
- Sin JWT válido → `401 Unauthorized` antes de llegar al backend.

Headers propagados al backend tras validación exitosa:

| Header                      | Contenido                                            |
| --------------------------- | ---------------------------------------------------- |
| `X-Consumer-ID`             | ID interno del consumer de Kong                      |
| `X-Consumer-Username`       | Nombre del consumer (`tlm-mx-realm`, etc.)           |
| `X-Credential-Identifier`   | Claim `iss` del JWT (issuer URL del realm)           |
| `X-Forwarded-Authorization` | Header `Authorization` original reenviado al backend |

### Autorización Coarse-Grained (Plugin `acl`)

Cada sistema define el grupo ACL que puede acceder a él. Los consumers tienen grupos asignados en `_consumers.yaml`.

```yaml
# En _consumers.yaml
- username: tlm-pe-realm
  acls:
    - group: sisbon-users
    - group: talenthub-users

# En sisbon.yaml (plugins del service)
- name: acl
  config:
    allow: [sisbon-users]
    hide_groups_header: true
```

> La autorización fine-grained (roles específicos dentro del sistema) es responsabilidad del backend; Kong solo hace el primer filtro por sistema.

## Multi-tenancy (Consumers por Tenant)

Cada tenant (realm) tiene su propio Consumer en Kong con clave pública RSA independiente. El discriminador es el claim `iss` del JWT:

| Claim `iss` (issuer)            | Kong Consumer  | ACL Groups                        |
| ------------------------------- | -------------- | --------------------------------- |
| `http://.../auth/realms/tlm-mx` | `tlm-mx-realm` | `sisbon-users`                    |
| `http://.../auth/realms/tlm-pe` | `tlm-pe-realm` | `sisbon-users`, `talenthub-users` |

Para agregar un nuevo tenant: crear realm en Keycloak + agregar consumer en `_consumers.yaml` de los 3 entornos + `make sync-local → nonprod → prod`.

## Observabilidad

### Métricas → Grafana/Mimir (Plugin `prometheus`)

Plugin habilitado globalmente con:

- `status_code_metrics: true` — número de requests por código de respuesta.
- `latency_metrics: true` — p50/p95/p99 de latencia Kong y upstream.
- `upstream_health_metrics: true` — estado de salud de upstreams.
- `bandwidth_metrics: true` — bytes transferidos.

Endpoint de métricas: `kong-host:8001/metrics` (scrapeado por Prometheus/Mimir).

### Correlación de Requests (Plugin `correlation-id`)

Plugin habilitado globalmente:

- Genera un UUID por request en el header `X-Correlation-ID`.
- `echo_downstream: true` — el header se devuelve en la respuesta al cliente.
- Permite correlacionar logs de Kong con logs del backend usando el mismo ID.

## Integración con Servicios Externos (Plugin `request-transformer`)

Para TalentHub ATS, el plugin adapta el request del ecosistema Talma al API externo:

```yaml
plugins:
  - name: request-transformer
    config:
      add:
        headers:
          - x-api-key:<valor-desde-secrets>
      remove:
        headers:
          - Authorization # Elimina el JWT corporativo
      replace:
        uri: /uat//lmbExGen?operacion=TALMA_CREAR_POSICION_V1&bcode=<valor>
```

> La `x-api-key` de TalentHub **no debe estar en texto plano en el YAML**. Ver DT-01.

## Rate Limiting (Plugin `rate-limiting`)

Throttling por consumer (tenant) con `policy: local`:

| Entorno  | Sistema | Límite/min | Límite/hora |
| -------- | ------- | ---------- | ----------- |
| DEV / QA | Sisbon  | 200        | 2,000       |
| DEV / QA | ATS     | 50         | 500         |
| PROD     | Sisbon  | 1,000      | 10,000      |
| PROD     | ATS     | 50         | 500         |

Headers de respuesta al cliente cuando se supera el límite (`429`):

| Header                | Descripción                           |
| --------------------- | ------------------------------------- |
| `RateLimit-Limit`     | Límite configurado                    |
| `RateLimit-Remaining` | Requests restantes en la ventana      |
| `RateLimit-Reset`     | Segundos hasta el reset de la ventana |

> `policy: local` significa que los contadores son por instancia Kong. Con múltiples instancias, el límite efectivo es `N * límite_configurado`. Redis como backend distribuido está pendiente (DT-06).

## Protección de Payload (Plugin `request-size-limiting`)

Configurado uniformemente en `1 MB` para todos los servicios. Si el payload supera el límite, Kong devuelve `413 Request Entity Too Large` sin llegar al backend.
