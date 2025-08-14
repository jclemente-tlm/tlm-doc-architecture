---
title: "Observability.Shared"
sidebar_position: 2
---

## Objetivo

Paquete NuGet que unifica la **observabilidad** de todos los microservicios .NET 8: logging, métricas, tracing y health checks. Facilita la instrumentación consistente sin necesidad de desarrollos adicionales.

## Stack

- Logging: **Serilog**
- Métricas: **Prometheus**
- Logs centralizados: **Loki**
- Tracing distribuido: **Jaeger**
- Dashboard: **Grafana**

## Componentes

```
Observability.Shared/
│
├── Logging/
│   └── SerilogConfig.cs
├── Metrics/
│   └── PrometheusMetrics.cs
├── Tracing/
│   └── JaegerTracing.cs
├── HealthChecks/
│   └── DbHealthCheck.cs
└── Extensions/
    └── ServiceCollectionExtensions.cs  // AddObservability()
```

## Integración en microservicios .NET 8

```csharp
var builder = WebApplication.CreateBuilder(args);

// Registra logging, métricas, tracing y health checks
builder.Services.AddObservability(builder.Configuration);

var app = builder.Build();

// Middleware opcional para tracing/logging
app.UseObservability();

app.Run();
```

## Configuración

- Toda la configuración (endpoints, niveles de log, métricas y tracing) se maneja desde `appsettings.json` o variables de entorno.
- Permite cambiar backend de observabilidad sin despliegues adicionales.
- Los dashboards en Grafana y Jaeger pueden configurar autorefresh de paneles según necesidad.

## Buenas prácticas

- Usar los **enrichers estándar**: ApplicationName, Environment, RequestId, CorrelationId.
- Mantener métricas y health checks consistentes entre servicios.
- Evitar logging pesado en loops críticos para no saturar Loki.

---
