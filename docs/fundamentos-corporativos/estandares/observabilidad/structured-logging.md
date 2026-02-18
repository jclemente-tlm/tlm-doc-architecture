---
id: structured-logging
sidebar_position: 1
title: Structured Logging
description: Logging estructurado en JSON con Serilog para .NET
---

# Structured Logging

## Contexto

Este estándar define cómo implementar logging estructurado en formato JSON para facilitar búsqueda, análisis y correlación de logs en Grafana Loki. Complementa el [lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) especificando **cómo** generar logs consultables y estructurados.

---

## Stack Tecnológico

| Componente    | Tecnología            | Versión | Uso                              |
| ------------- | --------------------- | ------- | -------------------------------- |
| **Framework** | ASP.NET Core          | 8.0+    | Framework base                   |
| **Logger**    | Serilog               | 3.1+    | Logging estructurado             |
| **ASP.NET**   | Serilog.AspNetCore    | 8.0+    | Integración ASP.NET Core         |
| **JSON Sink** | Serilog.Sinks.Console | 5.0+    | Output JSON a stdout             |
| **Enrichers** | Serilog.Enrichers.\*  | -       | Context enrich (machine, thread) |
| **Storage**   | Grafana Loki          | 2.9+    | Almacenamiento logs              |

### Dependencias NuGet

```xml
<PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
<PackageReference Include="Serilog.Sinks.Console" Version="5.0.1" />
<PackageReference Include="Serilog.Enrichers.Environment" Version="2.3.0" />
<PackageReference Include="Serilog.Enrichers.Thread" Version="3.1.0" />
<PackageReference Include="Serilog.Expressions" Version="4.0.0" />
```

---

## Implementación Técnica

### Configuración Base

```csharp
// Program.cs
using Serilog;
using Serilog.Events;

// ✅ Configurar Serilog ANTES de CreateBuilder
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft.AspNetCore", LogEventLevel.Warning)
    .MinimumLevel.Override("Microsoft.EntityFrameworkCore", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithThreadId()
    .Enrich.WithProperty("Application", "Orders.Api")
    .Enrich.WithProperty("Environment", Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Production")
    .WriteTo.Console(
        outputTemplate: "[{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz}] [{Level:u3}] {Message:lj}{NewLine}{Exception}",
        restrictedToMinimumLevel: LogEventLevel.Information
    )
    .WriteTo.Console(
        new Serilog.Formatting.Json.JsonFormatter(),
        restrictedToMinimumLevel: LogEventLevel.Information
    )
    .CreateLogger();

try
{
    Log.Information("Starting Orders API");

    var builder = WebApplication.CreateBuilder(args);

    // ✅ Usar Serilog como proveedor de logging
    builder.Host.UseSerilog();

    // ... configuración servicios

    var app = builder.Build();

    // ✅ Request logging enriquecido
    app.UseSerilogRequestLogging(options =>
    {
        options.MessageTemplate = "HTTP {RequestMethod} {RequestPath} responded {StatusCode} in {Elapsed:0.0000} ms";
        options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
        {
            diagnosticContext.Set("RequestHost", httpContext.Request.Host.Value);
            diagnosticContext.Set("RequestScheme", httpContext.Request.Scheme);
            diagnosticContext.Set("UserAgent", httpContext.Request.Headers["User-Agent"].ToString());
            diagnosticContext.Set("ClientIP", httpContext.Connection.RemoteIpAddress?.ToString());
            diagnosticContext.Set("CorrelationId", httpContext.TraceIdentifier);
        };
    });

    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Application terminated unexpectedly");
}
finally
{
    Log.CloseAndFlush();
}
```

### Niveles de Log

```csharp
public class OrderService
{
    private readonly ILogger<OrderService> _logger;

    public OrderService(ILogger<OrderService> logger)
    {
        _logger = logger;
    }

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        // ✅ VERBOSE: Detalles exhaustivos (desarrollo solamente)
        _logger.LogTrace(
            "Creating order with {ItemCount} items for customer {CustomerId}",
            request.Items.Count,
            request.CustomerId
        );

        // ✅ DEBUG: Información diagnóstica (desarrollo/staging)
        _logger.LogDebug(
            "Order validation started. Items: {@Items}",
            request.Items
        );

        // ✅ INFORMATION: Eventos importantes del flujo normal
        _logger.LogInformation(
            "Order {OrderNumber} created successfully for customer {CustomerId}. Total: {TotalAmount:C}",
            order.OrderNumber,
            order.CustomerId,
            order.TotalAmount
        );

        // ✅ WARNING: Comportamiento inesperado pero recuperable
        if (order.TotalAmount > 10000)
        {
            _logger.LogWarning(
                "High-value order detected. OrderId: {OrderId}, Amount: {TotalAmount:C}",
                order.Id,
                order.TotalAmount
            );
        }

        // ✅ ERROR: Fallo en operación pero aplicación continúa
        try
        {
            await _notificationService.SendOrderConfirmationAsync(order);
        }
        catch (Exception ex)
        {
            _logger.LogError(
                ex,
                "Failed to send order confirmation. OrderId: {OrderId}",
                order.Id
            );
            // Continuar - no es crítico
        }

        // ✅ CRITICAL: Fallo crítico que puede afectar disponibilidad
        try
        {
            await _dbContext.SaveChangesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogCritical(
                ex,
                "CRITICAL: Database unavailable. Failed to persist order {OrderNumber}",
                order.OrderNumber
            );
            throw;
        }

        return order;
    }
}

// Output JSON:
// {
//   "Timestamp": "2024-01-15T10:30:00.1234567Z",
//   "Level": "Information",
//   "MessageTemplate": "Order {OrderNumber} created successfully...",
//   "Message": "Order ORD-2024-001234 created successfully...",
//   "Properties": {
//     "OrderNumber": "ORD-2024-001234",
//     "CustomerId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
//     "TotalAmount": 299.99,
//     "SourceContext": "OrderService",
//     "Application": "Orders.Api",
//     "Environment": "Production",
//     "MachineName": "orders-api-pod-1",
//     "ThreadId": 42
//   }
// }
```

### Structured Logging con Message Templates

```csharp
// ✅ CORRECTO: Message templates con propiedades estructuradas
_logger.LogInformation(
    "Order {OrderId} status changed from {OldStatus} to {NewStatus} by user {UserId}",
    orderId,
    oldStatus,
    newStatus,
    userId
);

// ❌ INCORRECTO: String interpolation (no estructurado)
_logger.LogInformation($"Order {orderId} status changed from {oldStatus} to {newStatus}");

// ✅ CORRECTO: Serializar objeto complejo con @
_logger.LogDebug(
    "Processing order request: {@OrderRequest}",
    request
);

// ✅ CORRECTO: ToString() explícito con $
_logger.LogInformation(
    "Order ID: {OrderId:D}",  // Formato GUID sin guiones
    order.Id
);

// ✅ CORRECTO: Formateo de moneda
_logger.LogInformation(
    "Payment processed: {Amount:C} in {Currency}",
    amount,
    currency
);

// ✅ CORRECTO: No loggear información sensible
_logger.LogInformation(
    "User authenticated: {UserId}",
    userId  // ❌ NO loggear: password, token, credit card
);
```

### Log Context Enrichment

```csharp
using Serilog.Context;

public async Task<Order> ProcessOrderAsync(Guid orderId)
{
    // ✅ Agregar contexto temporal con LogContext
    using (LogContext.PushProperty("OrderId", orderId))
    using (LogContext.PushProperty("Operation", "ProcessOrder"))
    {
        _logger.LogInformation("Starting order processing");

        // Todos los logs dentro de este scope incluyen OrderId y Operation
        var order = await _orderRepository.GetAsync(orderId);

        if (order == null)
        {
            _logger.LogWarning("Order not found");  // Incluye OrderId automáticamente
            return null;
        }

        _logger.LogInformation("Order retrieved successfully");

        await ProcessPaymentAsync(order);
        await ShipOrderAsync(order);

        _logger.LogInformation("Order processing completed");

        return order;
    }
}

// Output:
// {
//   "Message": "Starting order processing",
//   "Properties": {
//     "OrderId": "550e8400-e29b-41d4-a716-446655440000",
//     "Operation": "ProcessOrder",
//     ...
//   }
// }
```

### Correlación con TraceId

```csharp
// Middleware para agregar TraceId a todos los logs
public class CorrelationIdMiddleware
{
    private readonly RequestDelegate _next;

    public CorrelationIdMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context, ILogger<CorrelationIdMiddleware> logger)
    {
        var correlationId = context.Request.Headers["X-Correlation-ID"].FirstOrDefault()
            ?? context.TraceIdentifier;

        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            context.Response.Headers["X-Correlation-ID"] = correlationId;

            logger.LogDebug("Request started with correlation ID {CorrelationId}", correlationId);

            await _next(context);
        }
    }
}

// Program.cs
app.UseMiddleware<CorrelationIdMiddleware>();
```

### Logging en Background Services

```csharp
public class OrderProcessorWorker : BackgroundService
{
    private readonly ILogger<OrderProcessorWorker> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Worker started at {StartTime}", DateTimeOffset.Now);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessPendingOrdersAsync(stoppingToken);
                await Task.Delay(TimeSpan.FromSeconds(30), stoppingToken);
            }
            catch (OperationCanceledException)
            {
                _logger.LogInformation("Worker stopping gracefully");
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(
                    ex,
                    "Unhandled exception in worker loop. Continuing..."
                );
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }

        _logger.LogInformation("Worker stopped at {StopTime}", DateTimeOffset.Now);
    }
}
```

### Configuración por Ambiente

```json
// appsettings.json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft.AspNetCore": "Warning",
        "Microsoft.EntityFrameworkCore": "Warning",
        "System.Net.Http.HttpClient": "Warning"
      }
    }
  }
}

// appsettings.Development.json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Debug",
      "Override": {
        "Talma.Orders": "Trace"
      }
    }
  }
}

// appsettings.Production.json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "System": "Warning"
      }
    }
  }
}
```

### Envío a Grafana Loki

```csharp
// Docker Compose - Grafana Alloy como collector
// Serilog escribe JSON a stdout → Docker captura → Alloy recolecta → Loki almacena

// Program.cs - Solo escribir a stdout en formato JSON
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(new Serilog.Formatting.Json.JsonFormatter())
    .CreateLogger();

// docker-compose.yml
services:
  orders-api:
    image: orders-api:latest
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

// Grafana Alloy config
loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}

loki.source.docker "containers" {
  host = "unix:///var/run/docker.sock"
  targets = discovery.docker.containers.targets
  forward_to = [loki.write.default.receiver]
  labels = {
    job = "docker",
  }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Serilog para structured logging en .NET
- **MUST** escribir logs en formato JSON a stdout
- **MUST** usar message templates (no string interpolation)
- **MUST** incluir propiedades estructuradas en todos los logs
- **MUST** incluir CorrelationId en todos los logs de request
- **MUST** usar niveles de log apropiados (Information, Warning, Error, Critical)
- **MUST** enriquecer logs con Application, Environment, MachineName
- **MUST** configurar mínimo nivel Information en producción
- **MUST** loggear inicio y fin de operaciones críticas

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar LogContext para contexto temporal
- **SHOULD** loggear duración de operaciones importantes
- **SHOULD** incluir UserAgent y ClientIP en logs HTTP
- **SHOULD** usar structured logging en catch blocks
- **SHOULD** agregar custom properties relevantes al dominio
- **SHOULD** configurar override para reducir verbosidad de Microsoft.\*
- **SHOULD** rotar logs locales con límite de tamaño

### MAY (Opcional)

- **MAY** usar filtros dinámicos de log level en runtime
- **MAY** implementar sampling para requests de alto volumen
- **MAY** agregar performance counters como propiedades

### MUST NOT (Prohibido)

- **MUST NOT** loggear información sensible (passwords, tokens, PII, credit cards)
- **MUST NOT** usar string interpolation en lugar de message templates
- **MUST NOT** loggear objetos sin estructura (ToString() genérico)
- **MUST NOT** usar Console.WriteLine en lugar de ILogger
- **MUST NOT** loggear stack traces en nivel Information
- **MUST NOT** dejar Debug/Trace habilitado en producción

---

## Referencias

- [Lineamiento: Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md)
- Estándares relacionados:
  - [Métricas](metrics-standards.md)
  - [Distributed Tracing](distributed-tracing.md)
  - [Correlation IDs](correlation-ids.md)
- Especificaciones:
  - [Serilog Documentation](https://serilog.net/)
  - [Structured Logging Best Practices](https://github.com/serilog/serilog/wiki/Structured-Data)
  - [Grafana Loki](https://grafana.com/docs/loki/)
