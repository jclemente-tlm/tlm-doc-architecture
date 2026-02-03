---
id: correlation-ids
sidebar_position: 4
title: Identificadores de Correlación
description: Uso de correlation IDs para rastrear requests en sistemas distribuidos
---

# Estándar Técnico — Identificadores de Correlación

## 1. Propósito

Rastrear un request de usuario a través de múltiples servicios, logs y eventos asíncronos mediante un identificador único inmutable (`X-Correlation-ID`).

## 2. Alcance

**Aplica a:**

- Todas las APIs REST y microservicios
- Procesamiento de mensajes (Apache Kafka, eventos)
- Integraciones síncronas y asíncronas

## 3. Estándar de Implementación

### Header HTTP

```
X-Correlation-ID: <UUID v4>
```

**Reglas:**

- Generado por API Gateway o primer servicio si no existe
- Propagado en **todos** los headers HTTP downstream
- Inmutable: nunca se regenera durante el flujo
- Formato: UUID v4 (ejemplo: `550e8400-e29b-41d4-a716-446655440000`)

### Contexto de Mensajería

```json
{
  "messageAttributes": {
    "correlationId": {
      "dataType": "String",
      "stringValue": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

## 4. Requisitos Obligatorios

- Incluir `X-Correlation-ID` en **todos** los logs estructurados
- Propagar en headers HTTP de llamadas downstream
- Incluir en headers de mensajes Apache Kafka
- Retornar en response headers para debugging
- Validar formato UUID v4, rechazar si inválido

## 5. Ejemplo de Implementación

### .NET Middleware

```csharp
public class CorrelationIdMiddleware
{
    private readonly RequestDelegate _next;
    private const string CorrelationIdHeader = "X-Correlation-ID";

    public async Task InvokeAsync(HttpContext context, ILogger<CorrelationIdMiddleware> logger)
    {
        string correlationId = context.Request.Headers[CorrelationIdHeader].FirstOrDefault()
            ?? Guid.NewGuid().ToString();

        context.Items["CorrelationId"] = correlationId;
        context.Response.Headers[CorrelationIdHeader] = correlationId;

        using (logger.BeginScope(new Dictionary<string, object>
        {
            ["CorrelationId"] = correlationId
        }))
        {
            await _next(context);
        }
    }
}
```

### Propagación en HttpClient

```csharp
services.AddHttpClient("downstream-service")
    .AddHeaderPropagation(options =>
        options.Headers.Add("X-Correlation-ID"));

services.AddHeaderPropagation();
```

## 6. Validación

**Criterios de Aceptación:**

- Logs de servicios diferentes comparten mismo `CorrelationId` para un request
- Header presente en responses HTTP
- Queries en Grafana/Loki por `correlationId` retornan flujo completo

## 7. Relación con Tracing

`X-Correlation-ID` complementa W3C Trace Context:

- **Correlation ID:** Identificador de negocio, inmutable, generado en entry point
- **Trace ID:** Identificador técnico OpenTelemetry, puede variar por servicio

Ambos deben estar presentes en logs para máxima trazabilidad.

## 8. Referencias

- [Estándar de Logging](./01-logging.md)
- [Tracing Distribuido](./03-tracing-distribuido.md)
- [Lineamiento de Observabilidad](../../lineamientos/arquitectura/05-observabilidad.md)
