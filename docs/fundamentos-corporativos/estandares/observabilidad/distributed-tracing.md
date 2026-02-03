---
id: tracing-distribuido
sidebar_position: 3
title: Tracing Distribuido
description: Implementación de trazas distribuidas con W3C Trace Context y OpenTelemetry
---

# Estándar Técnico — Tracing Distribuido

## 1. Propósito

Rastrear requests a través de múltiples servicios en arquitecturas distribuidas, permitiendo identificar latencias, cuellos de botella y errores en flujos end-to-end.

## 2. Alcance

**Aplica a:**

- Microservicios REST/gRPC
- Procesamiento de mensajes asíncronos (Apache Kafka)
- Funciones serverless (AWS Lambda)
- Integraciones con APIs externas

**No aplica a:**

- Procesos batch de larga duración (>5min) sin interacción de usuario
- Scripts de migración únicos

## 3. Tecnologías Aprobadas

| Componente               | Tecnología           | Versión mínima |
| ------------------------ | -------------------- | -------------- |
| **Estándar de contexto** | W3C Trace Context    | 1.0            |
| **Instrumentación**      | OpenTelemetry SDK    | 1.7+           |
| **Backend**              | Grafana Tempo        | 2.3+           |
| **Collector**            | Grafana Alloy (OTLP) | 1.0+           |

## 4. Requisitos Obligatorios

- Propagación de W3C Trace Context (`traceparent`, `tracestate`) en headers HTTP y metadata de mensajes
- Instrumentación automática de HTTP clients, gRPC, database drivers
- Spans con atributos estándar: `http.method`, `http.status_code`, `db.statement`, `messaging.system`
- Sampling adaptativo: 100% errores, 10% requests exitosos en producción
- Integración con logs: `trace_id` y `span_id` en contexto de logging

## 5. Ejemplo de Implementación

### .NET con OpenTelemetry

```csharp
// Program.cs
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("mi-servicio"))
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddSqlClientInstrumentation()
        .AddOtlpExporter(options =>
        {
            options.Endpoint = new Uri("http://alloy:4317");
        }));
```

### Propagación manual en mensajería

```csharp
// Producer
var activity = Activity.Current;
message.Attributes["traceparent"] = activity?.Id;

// Consumer
Activity.Current = new Activity("ProcessMessage")
    .SetParentId(message.Attributes["traceparent"]);
```

## 6. Validación

**Pre-producción:**

- Verificar propagación de `traceparent` en llamadas HTTP/gRPC
- Confirmar visualización de traces en Grafana Tempo
- Validar correlación trace ↔ logs vía `trace_id`

**Post-producción:**

- P95 latency por servicio visible en dashboards
- Alertas configuradas para spans con errores

## 7. Referencias

- [W3C Trace Context Specification](https://www.w3.org/TR/trace-context/)
- [OpenTelemetry Tracing](https://opentelemetry.io/docs/concepts/signals/traces/)
- [Lineamiento de Observabilidad](../../lineamientos/arquitectura/05-observabilidad.md)
