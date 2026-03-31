---
sidebar_position: 8
title: Conceptos Transversales
description: Patrones y configuraciones aplicadas transversalmente en el stack de observabilidad.
---

# 8. Conceptos Transversales

## Multi-Tenancy via Header HTTP

El mecanismo central es el header `X-Scope-OrgID`, estándar del stack LGTM. Los **agentes Alloy envían dos headers**: `X-Tenant` (= `TENANT_ID`) y `X-Environment` (= `ENVIRONMENT`). El **Envoy Lua filter** los lee y construye `X-Scope-OrgID` según la ruta HTTP de la señal:

```
Alloy envía: X-Tenant: {TENANT_ID}  +  X-Environment: {ENVIRONMENT}

Envoy Lua construye X-Scope-OrgID:
  /loki/*                    → logs-{X-Tenant}-{X-Environment}    (ej. logs-tlm-pe-prod)
  /mimir/* o /api/v1/push   → metrics-{X-Environment}             (ej. metrics-prod)
  /traces/* o opentelemetry → traces-{X-Environment}              (ej. traces-prod)
```

Todos los backends tienen habilitada la autenticación multi-tenant:

- Loki: `auth_enabled: true`
- Mimir: `multitenancy_enabled: true`
- Tempo: `multitenancy_enabled: true`

## Correlación entre Señales (Logs ↔ Trazas ↔ Métricas)

Grafana permite navegar entre las tres señales usando campos comunes propagados por OpenTelemetry:

| Campo                  | Propagado por         | Uso en correlación                                                                       |
| ---------------------- | --------------------- | ---------------------------------------------------------------------------------------- |
| `traceId`              | SDK OTel .NET         | Enlace log → traza (Derived Fields configurados en `datasources.yaml`, autoprovisioning) |
| `serviceInstanceId`    | Alloy label `cluster` | Enlace métrica → host → log                                                              |
| `job` / `service.name` | Label en Alloy        | Filtro cruzado en dashboards                                                             |

El SDK OpenTelemetry para .NET (`OpenTelemetry.*`) inyecta automáticamente `traceId` y `spanId` en los logs estructurados de Serilog cuando la traza activa está en contexto.

> Los **Derived Fields** de los data sources de Loki quedan configurados automáticamente vía `ui/config/grafana/datasources.yaml`. El regex `[Tt]race[Ii]d":"(\w+)"` se aplica en los data sources `loki-dev`, `loki-qa` y `loki-prod`, enlazando a los data sources de Tempo correspondientes (`traces-dev`, `traces-qa`, `traces-prod`).

## Integración con .NET 8+

Las aplicaciones .NET configuran OpenTelemetry apuntando al agente Alloy local:

```csharp
// Trazas → Alloy OTLP gRPC
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter(opt => opt.Endpoint = new Uri("http://localhost:14317")));

// Métricas → Alloy OTLP
builder.Services.AddOpenTelemetry()
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddOtlpExporter(opt => opt.Endpoint = new Uri("http://localhost:14317")));
```

Los logs usan Serilog con sink estructurado a stdout (Docker captura, Alloy los recolecta):

```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(new JsonFormatter())         // Alloy recoge stdout
    .Enrich.WithTraceIdAndSpanId()               // Correlación con trazas
    .CreateLogger();
```

## Calidad y Seguridad en el Pipeline de Logs

### Rate Limiting

El pipeline `logs-docker.alloy` aplica control de tasa vía `stage.limit` para proteger a Loki de picos de escritura:

- Límite: **1.000 logs/segundo** por agente
- Burst: **2.000 logs** en pico
- Comportamiento al superar el límite: los logs en exceso se descartan (con métrica `loki_process_dropped_lines_total` incrementada)

### Filtro de Seguridad

Antes de envía a Loki, el pipeline aplica `stage.drop` para eliminar líneas que contengan datos sensibles:

```
Patrones descartados: password|secret|key|token|credit_card
```

> El filtro opera sobre el contenido raw del log antes del parseo JSON, garantizando que credenciales nunca lleguen al almacenamiento.

### Logs Descartados por Tamaño o Edad

- Logs con tamaño **> 8 KB**: descartados (loki rechaza entradas muy grandes)
- Logs con timestamp **> 24 horas** en el pasado: descartados (fuera del window de ingestación de Loki)

### WAL (Write-Ahead Log)

Alloy habilita WAL para absorber fallos transitorios de red sin pérdida de datos:

| Señal    | Configuración WAL                                    |
| -------- | ---------------------------------------------------- |
| Logs     | `loki.write` WAL, `max_segment_age = 2h`             |
| Métricas | `prometheus.remote_write` WAL habilitado por defecto |

## Almacenamiento en MinIO

Todos los backends (Loki, Mimir, Tempo) usan MinIO como capa de almacenamiento S3-compatible. Las credenciales se inyectan via variables de entorno. El modo de operación es **monolítico** (monolithic-mode), adecuado para el volumen actual:

- Loki: `monolithic-mode-logs.yaml` — todos los componentes en un proceso
- Mimir: `monolithic-mode-metrics.yaml` — mismo patrón
- Tempo: directamente sin modo explícito, configuración simplificada

> La migración a modo distribuido (microservices-mode) está disponible si el volumen de datos supera las capacidades del modo monolítico.

## Observabilidad del Stack (Meta-Observabilidad)

El propio stack se monitorea a sí mismo:

| Señal de Meta-Observabilidad            | Fuente                                                    |
| --------------------------------------- | --------------------------------------------------------- |
| Métricas de Loki (ingestión, latencia)  | Loki `/metrics` scrapeado por Alloy del mismo host server |
| Métricas de Mimir (queries, ingestión)  | Mimir `/metrics` interno                                  |
| Métricas de Tempo (trazas ingestadas)   | Tempo `/metrics` interno                                  |
| Métricas de Envoy (upstream, latencia)  | Envoy Admin `:9901/stats`                                 |
| Métricas de MinIO (almacenamiento, I/O) | MinIO Prometheus endpoint                                 |
| Métricas de cAdvisor                    | Contenedores del host server                              |

## Seguridad

- **Red**: backends no expuestos directamente; todo el tráfico pasa por Envoy.
- **Credenciales**: archivos `.env` fuera de Git; rotación periódica definida en `docs/SECURITY.md`.
- **Autenticación Grafana**: SSO con Keycloak (ADR-003); roles de viewer/editor/admin por equipo.
- **Aislamiento de tenants**: un usuario con acceso al tenant `tlm-pe` no puede ver datos del tenant `tlm-mx` a nivel de backend.

## Política de Retención

| Backend | Retención por defecto     | Configurable en                                                  |
| ------- | ------------------------- | ---------------------------------------------------------------- |
| Loki    | 30 días                   | `loki/monolithic-mode-logs.yaml` → `retention_period`            |
| Mimir   | 90 días                   | `mimir/monolithic-mode-metrics.yaml` → `blocks_retention_period` |
| Tempo   | 14 días                   | Config de Tempo → `max_block_duration`                           |
| MinIO   | Sin expiración automática | Lifecycle policy del bucket                                      |
