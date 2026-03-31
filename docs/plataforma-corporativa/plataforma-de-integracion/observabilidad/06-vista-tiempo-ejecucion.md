---
sidebar_position: 6
title: Vista de Tiempo de Ejecución
description: Flujos de ingestión, routing multi-tenant y correlación de señales en el stack de observabilidad.
---

# 6. Vista de Tiempo de Ejecución

## Flujo 1: Ingestión de Logs desde Servicio .NET

```mermaid
sequenceDiagram
    participant APP as Servicio .NET\n(API Orders - Perú)
    participant ALLOY as Alloy Agent\n(pe-prod)
    participant ENVOY as Envoy Proxy\n:8080
    participant LOKI as Loki\n:3100

    APP->>ALLOY: stdout log JSON\n{level, message, traceId, ...}
    ALLOY->>ALLOY: Enriquece con labels\n{job, cluster=tlm-pe-prod-01, env=prod}
    ALLOY->>ENVOY: POST /loki/api/v1/push\nX-Tenant: tlm-pe\nX-Environment: prod
    ENVOY->>ENVOY: Lua filter: /loki/* \u2192 X-Scope-OrgID: logs-tlm-pe-prod
    ENVOY->>LOKI: POST /loki/api/v1/push\nX-Scope-OrgID: logs-tlm-pe-prod
    LOKI->>LOKI: Persiste en tenant logs-tlm-pe-prod
    Note over LOKI: Chunks escritos en MinIO\nbucket: loki-data/{logs-tlm-pe-prod}/
```

## Flujo 2: Ingestión de Métricas de Infraestructura

```mermaid
sequenceDiagram
    participant CAD as cAdvisor\n:8080
    participant NE as node-exporter\n:9100
    participant ALLOY as Alloy Agent
    participant ENVOY as Envoy Proxy
    participant MIMIR as Mimir\n:9009
    participant MEM as Memcached

    CAD->>ALLOY: Scrape /metrics (cada 30s)\ncpu, memory, network por contenedor
    NE->>ALLOY: Scrape /metrics (cada 30s)\ncpu, disk, mem, net del host EC2
    ALLOY->>ALLOY: otelcol.exporter.prometheus\n\u2192 prometheus.remote_write + labels\n{cluster=tlm-pe-prod-01, env=prod}
    ALLOY->>ENVOY: POST /mimir/api/v1/push\nX-Tenant: tlm-pe\nX-Environment: prod
    ENVOY->>ENVOY: Lua filter: /mimir/* \u2192 X-Scope-OrgID: metrics-prod
    ENVOY->>MIMIR: POST /api/v1/push\nX-Scope-OrgID: metrics-prod
    MIMIR->>MIMIR: Ingesta en tenant metrics-prod
    Note over MIMIR: Bloques TSDB escritos en MinIO
    MIMIR->>MEM: Almacena resultado de\nqueries frecuentes en caché
```

## Flujo 3: Ingestión de Trazas OTLP desde .NET

```mermaid
sequenceDiagram
    participant APP as Servicio .NET\n(orders - Perú prod)
    participant ALLOY as Alloy Agent
    participant ENVOY as Envoy Proxy\n:4317 gRPC
    participant TEMPO as Tempo\n:3200

    APP->>ALLOY: OTLP gRPC :14317\nSpan {traceId, spanId, service.name=orders}
    ALLOY->>ALLOY: otlp_resource_processor\ninyecta {cluster, environment, tenant_id}
    ALLOY->>ALLOY: traces_batch_processor\nbatch: 2s / 2000 spans
    ALLOY->>ENVOY: OTLP gRPC :4317\nX-Tenant: tlm-pe\nX-Environment: prod
    ENVOY->>ENVOY: Lua filter: opentelemetry \u2192 X-Scope-OrgID: traces-prod
    ENVOY->>TEMPO: OTLP gRPC\nX-Scope-OrgID: traces-prod
    TEMPO->>TEMPO: Persiste traza en tenant traces-prod
    Note over TEMPO: Bloques en MinIO\nbucket: tempo-data/{traces-prod}/
```

## Flujo 4: Consulta con Correlación Log → Traza en Grafana

```mermaid
sequenceDiagram
    participant DEV as Desarrollador
    participant GF as Grafana
    participant LOKI as Loki
    participant TEMPO as Tempo

    DEV->>GF: Abre dashboard, filtra\nerror en Perú prod, últimas 2h
    GF->>LOKI: LogQL: {job="orders"} |= "error"\nX-Scope-OrgID: logs-tlm-pe-prod
    LOKI-->>GF: Log entries con traceId=abc123
    DEV->>GF: Clic en traceId=abc123
    Note over GF: Derived field autoprovisioned\nen datasources.yaml detecta traceId
    GF->>TEMPO: GET /api/traces/abc123\nX-Scope-OrgID: traces-prod
    TEMPO-->>GF: Trace completa con spans
    GF-->>DEV: Vista Trace + Log correlacionado
```

## Manejo de Errores

| Escenario                                                        | Comportamiento                                                                |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Agente Alloy no alcanza a Envoy                                  | Reintento con backoff exponencial; logs en buffer interno de Alloy            |
| Envoy no alcanza a Loki/Mimir/Tempo                              | HTTP 503 al agente; Alloy reintenta hasta `max_retries`                       |
| MinIO no disponible                                              | Loki/Mimir/Tempo acumulan en WAL local hasta que MinIO recupere               |
| Tenant desconocido (falta `X-Tenant` o `X-Environment` en Alloy) | Envoy no puede construir `X-Scope-OrgID`; backend rechaza con HTTP 400        |
| Memcached no disponible                                          | Mimir responde queries directamente desde los bloques (mayor latencia)        |
| Grafana sin datos en tenant                                      | Query vacía; no hay error si el tenant existe pero no tiene datos en el rango |
