---
sidebar_position: 4
title: Estrategia de Solución
description: Decisiones de diseño principales y modelo de multi-tenancy del stack de observabilidad.
---

# 4. Estrategia de Solución

## Decisiones de Diseño Principales

| Decisión                 | Opción elegida                               | Alternativas descartadas                                                       |
| ------------------------ | -------------------------------------------- | ------------------------------------------------------------------------------ |
| Stack de observabilidad  | Grafana OSS (Loki + Mimir + Tempo)           | ELK Stack, Datadog, Splunk, CloudWatch                                         |
| Multi-tenancy            | Header `X-Scope-OrgID` via Envoy Lua filter  | Schema por tenant (BD), prefijo en label                                       |
| Recolector de telemetría | Grafana Alloy                                | Promtail + Prometheus Agent + OTel Collector (3 agentes)                       |
| Almacenamiento           | MinIO S3-compatible                          | Disco local, AWS S3 nativo                                                     |
| Despliegue               | Docker Compose en EC2                        | Kubernetes, ECS Fargate                                                        |
| Protocolo de ingestión   | OTLP (gRPC + HTTP) + Prometheus Remote Write | Logs/trazas via OTLP; métricas via Prometheus RW (Mimir no acepta OTLP nativo) |

## Modelo de Multi-Tenancy Estratégica

El sistema aplica criterios de tenant distintos según el tipo de señal, optimizando para el caso de uso de cada una:

```
┌─────────────────────────────────────────────────────────┐
│              ESTRATEGIA DE TENANT                        │
├──────────────────┬──────────────────┬───────────────────┤
│  LOGS (Loki)     │ MÉTRICAS (Mimir) │  TRAZAS (Tempo)   │
│  Tenant = País   │ Tenant = Ambiente│ Tenant = Servicio │
│                  │                  │                   │
│  tlm-pe          │  dev             │  orders           │
│  tlm-mx          │  qa              │  payments         │
│  tlm-co          │  staging         │  notifications    │
│  tlm-ec          │  prod            │                   │
│  tlm-pe-orders   │                  │                   │
├──────────────────┼──────────────────┼───────────────────┤
│ Razón: compliance│ Razón: dashboards│ Razón: integridad │
│ regulatorio por  │ consolidados de  │ de spans en trace │
│ localización     │ ambiente         │ distribuida       │
└──────────────────┴──────────────────┴───────────────────┘
```

## Modelo de 3 Capas

El stack se despliega en 3 capas independientes que pueden ejecutarse en hosts distintos:

| Capa       | Componentes                                                | Repositorio Docker Compose  |
| ---------- | ---------------------------------------------------------- | --------------------------- |
| **Server** | Envoy + Loki + Mimir + Tempo + MinIO + Memcached           | `server/docker-compose.yml` |
| **Agents** | Grafana Alloy + cAdvisor + node-exporter (por país/región) | `agents/docker-compose.yml` |
| **UI**     | Grafana                                                    | `ui/docker-compose.yml`     |

## Flujo de Datos por Señal

### Logs

```
Servicio .NET → (stdout/OTLP) → Alloy Agent
  → X-Tenant: tlm-pe + X-Environment: prod
  → Envoy :8080/loki/api/v1/push  → Lua filter: X-Scope-OrgID: logs-tlm-pe-prod
  → Loki (auth_enabled: true) → MinIO bucket: loki-data
```

### Métricas

```
cAdvisor + node-exporter → Alloy Agent (scrape Prometheus, 30s)
  → otelcol.exporter.prometheus → prometheus.remote_write
  → X-Tenant: tlm-pe + X-Environment: prod
  → Envoy :8080/mimir/api/v1/push  → Lua filter: X-Scope-OrgID: metrics-prod
  → Mimir (multitenancy_enabled: true) → MinIO bucket: mimir-blocks
  → Memcached (cache de queries de rango)
```

### Trazas

```
Servicio .NET → OTLP gRPC :14317 → Alloy Agent
  → otlp_resource_processor → traces_batch_processor
  → X-Tenant: tlm-pe + X-Environment: prod
  → Envoy :4317 gRPC  → Lua filter: X-Scope-OrgID: traces-prod
  → Tempo (multitenancy_enabled: true) → MinIO bucket: tempo-data
```

## Naming Convention de Tenants

| Variable de configuración | Propósito                                                                                                         |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `TENANT_ID`               | Identifica el país/org del agente. Parte del tenant de logs: `logs-{TENANT_ID}-{ENVIRONMENT}`                     |
| `ENVIRONMENT`             | Ambiente del agente (`dev`/`qa`/`prod`). Define el tenant de métricas (`metrics-{ENV}`) y trazas (`traces-{ENV}`) |
| `SERVICE_NAME`            | Nombre del agente / servicio. Usado en labels de métricas y enrichment de spans                                   |
| `COMPONENT`               | Clasificación del componente: `infra`, `application`, `middleware`, `agent`                                       |
| `CLUSTER_NAME`            | Identificador del clúster o región (`tlm-pe-prod-01`); label en métricas y logs                                   |
