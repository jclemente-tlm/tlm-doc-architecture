---
id: structured-logging
sidebar_position: 1
title: Structured Logging
description: Estándar para logging estructurado en formato JSON usando Serilog y Grafana Loki.
tags: [observabilidad, logging, serilog, loki]
---

# Structured Logging

## Contexto

Este estándar define la práctica de logging estructurado en formato JSON con contexto rico para análisis y correlación. Complementa el lineamiento [Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) asegurando que los logs sean machine-readable, fáciles de buscar y correlacionables entre servicios.

---

## Stack Tecnológico

| Componente          | Tecnología    | Versión | Uso                                  |
| ------------------- | ------------- | ------- | ------------------------------------ |
| **Logging Library** | Serilog       | 3.1+    | Logging estructurado en .NET         |
| **Log Aggregation** | Grafana Loki  | 2.9+    | Almacenamiento y consulta de logs    |
| **Agent**           | Grafana Alloy | 1.0+    | Recolección y reenvío de logs a Loki |

---

## ¿Qué es Structured Logging?

Práctica de escribir logs en formato estructurado (JSON) con campos bien definidos en lugar de cadenas de texto plano, facilitando búsqueda, filtrado y análisis automatizado.

**Componentes clave:**

- **Formato estructurado** — JSON con propiedades tipadas (string, number, bool)
- **Niveles de log** — Trace, Debug, Information, Warning, Error, Critical
- **Enriquecimiento de contexto** — Correlation ID, user ID, tenant ID, request path
- **Semantic logging** — Templates con parámetros nombrados, no concatenación de cadenas

**Beneficios:**

- ✅ Búsqueda rápida por campos específicos en Grafana Loki
- ✅ Correlación de logs entre servicios con correlation ID
- ✅ Agregaciones y estadísticas sobre propiedades tipadas
- ✅ Mejor debugging en producción sin necesidad de redespliegue

### Ejemplo Comparativo

```csharp
// ❌ MALO: Concatenación de strings (no estructurado)
_logger.LogInformation("Creating order for customer " + command.CustomerId +
    " with total " + command.Total);

// Resultado: string plano, imposible filtrar por CustomerId o Total en Loki

// ✅ BUENO: Template con parámetros nombrados
using (_logger.BeginScope(new Dictionary<string, object>
{
    ["CustomerId"] = command.CustomerId,
    ["CorrelationId"] = Activity.Current?.Id ?? Guid.NewGuid().ToString()
}))
{
    _logger.LogInformation(
        "Creating order: {TotalAmount} {Currency}",
        command.Total,
        command.Currency);

    var order = await _repository.CreateAsync(command);

    _logger.LogInformation(
        "Order created: {OrderId} {Status}",
        order.Id,
        order.Status);
}

// Resultado JSON en Loki:
// {
//   "timestamp": "2026-02-19T15:30:00Z",
//   "level": "Information",
//   "message": "Creating order: 99.99 USD",
//   "properties": {
//     "TotalAmount": 99.99,
//     "Currency": "USD",
//     "CustomerId": "123",
//     "CorrelationId": "trace-abc-123"
//   }
// }
```

---

## Configuración Serilog

```csharp
// Program.cs
using Serilog;
using Serilog.Enrichers.Span;
using Serilog.Formatting.Compact;

var builder = WebApplication.CreateBuilder(args);

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft.AspNetCore", LogEventLevel.Warning)
    .MinimumLevel.Override("Microsoft.EntityFrameworkCore", LogEventLevel.Warning)

    // Enrichers: agregan contexto automático a todos los logs
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithEnvironmentName()
    .Enrich.WithProperty("Application", "customer-service")
    .Enrich.WithProperty("Version", "1.2.3")
    .Enrich.WithSpan()  // Agrega OpenTelemetry trace/span IDs

    // Sinks
    .WriteTo.Console(
        outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
    .WriteTo.File(
        formatter: new CompactJsonFormatter(),  // JSON estructurado para Alloy
        path: "logs/customer-service-.json",
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 7)

    .CreateLogger();

builder.Host.UseSerilog();

var app = builder.Build();

// Middleware: enriquece logs con contexto del request HTTP
app.UseSerilogRequestLogging(options =>
{
    options.MessageTemplate =
        "HTTP {RequestMethod} {RequestPath} responded {StatusCode} in {Elapsed:0.0000} ms";

    options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
    {
        diagnosticContext.Set("RequestHost", httpContext.Request.Host.Value);
        diagnosticContext.Set("UserAgent", httpContext.Request.Headers["User-Agent"].ToString());

        if (httpContext.User.Identity?.IsAuthenticated == true)
        {
            diagnosticContext.Set("UserId", httpContext.User.FindFirst("sub")?.Value);
            diagnosticContext.Set("TenantId", httpContext.User.FindFirst("tenant_id")?.Value);
        }
    };
});

app.Run();
```

:::note Configurado por Plataforma
La configuración de Grafana Alloy para recolectar y reenviar los archivos de log a Loki es responsabilidad del equipo de Plataforma.
Ver [Plataforma Corporativa](../../../plataforma-corporativa/) para detalles de infraestructura.
:::

---

## Niveles de Log

| Nivel           | Cuándo usar                              | Ejemplos                                | En producción    |
| --------------- | ---------------------------------------- | --------------------------------------- | ---------------- |
| **Trace**       | Información muy detallada para debugging | "Entering method X with params Y"       | ❌ Deshabilitado |
| **Debug**       | Información útil solo en desarrollo      | "SQL query generada: SELECT \* FROM..." | ❌ Deshabilitado |
| **Information** | Eventos significativos del flujo normal  | "Order created", "Payment processed"    | ✅ Habilitado    |
| **Warning**     | Situación inusual pero manejada          | "Retry attempt 2/3", "Cache miss"       | ✅ Habilitado    |
| **Error**       | Error que requiere atención              | "Payment failed", "DB connection lost"  | ✅ Habilitado    |
| **Critical**    | Error catastrófico (caída inminente)     | "Out of memory", "All DB replicas down" | ✅ Habilitado    |

:::warning
Debug y Trace generan volumen excesivo en producción y aumentan los costos de almacenamiento en Loki. Habilitarlos solo en entornos locales o staging con ventana de tiempo acotada.
:::

---

## Enriquecimiento de Contexto

Propagación del correlation ID desde el header HTTP hacia todos los logs del request:

```csharp
public class ContextEnrichmentMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        using (LogContext.PushProperty("CorrelationId", GetOrCreateCorrelationId(context)))
        using (LogContext.PushProperty("RequestId", context.TraceIdentifier))
        using (LogContext.PushProperty("ClientIp", context.Connection.RemoteIpAddress?.ToString()))
        {
            await _next(context);
        }
    }

    private string GetOrCreateCorrelationId(HttpContext context)
    {
        // Propagar correlation ID desde header si existe
        if (context.Request.Headers.TryGetValue("X-Correlation-ID", out var correlationId))
            return correlationId.ToString();

        // Usar OpenTelemetry trace ID para correlación con trazas
        return Activity.Current?.TraceId.ToString() ?? Guid.NewGuid().ToString();
    }
}

app.UseMiddleware<ContextEnrichmentMiddleware>();
```

---

## Patrones de Escritura de Logs

```csharp
// ✅ BUENO: Template con parámetros nombrados
_logger.LogInformation(
    "Order {OrderId} created for customer {CustomerId} with total {Total}",
    order.Id,
    customer.Id,
    order.Total);

// ❌ MALO: Interpolación de strings
_logger.LogInformation($"Order {order.Id} created for customer {customer.Id}");

// ✅ BUENO: Scope para contexto compartido en un bloque
using (_logger.BeginScope("Processing batch {BatchId}", batchId))
{
    foreach (var item in batch)
    {
        // Todos los logs en este scope incluyen BatchId automáticamente
        _logger.LogInformation("Processing item {ItemId}", item.Id);
    }
}

// ✅ BUENO: Pasar exception como primer argumento (preserva stacktrace)
catch (PaymentGatewayException ex)
{
    _logger.LogError(
        ex,
        "Payment failed for order {OrderId}: {Reason}",
        payment.OrderId,
        ex.Reason);
    throw;
}

// ❌ MALO: Loguear solo el mensaje (pierde stacktrace y contexto)
catch (Exception ex)
{
    _logger.LogError(ex.Message);
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Serilog 3.1+ para logging estructurado en formato JSON
- **MUST** incluir correlation ID en todos los logs de request
- **MUST** usar log templates con parámetros nombrados (no concatenación ni interpolación)
- **MUST** configurar nivel mínimo `Information` en producción
- **MUST** agregar enrichers: `FromLogContext`, `WithMachineName`, `WithEnvironmentName`
- **MUST** usar `UseSerilogRequestLogging()` para logs automáticos de HTTP

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar `LogContext.PushProperty` para enriquecer logs con contexto del dominio
- **SHOULD** incluir excepción como primer argumento en `LogError` para preservar stacktrace
- **SHOULD** enriquecer logs con `UserId` y `TenantId` cuando el usuario esté autenticado
- **SHOULD** agregar `WithSpan()` (Serilog.Enrichers.Span) para correlacionar logs con trazas

### MUST NOT (Prohibido)

- **MUST NOT** loguear información sensible (contraseñas, tokens, datos PII sin enmascarar)
- **MUST NOT** usar concatenación o interpolación de strings en log messages
- **MUST NOT** habilitar niveles Debug o Trace en producción

---

## Referencias

- [Lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) — lineamiento que origina este estándar
- [Distributed Tracing](./distributed-tracing.md) — correlación de logs con trazas distribuidas
- [Métricas con OpenTelemetry](./metrics.md) — complementa este estándar con métricas numéricas
- [Serilog Documentation](https://serilog.net/) — documentación oficial
- [Grafana Loki](https://grafana.com/docs/loki/latest/) — consulta de logs agregados
