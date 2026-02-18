---
id: distributed-tracing
sidebar_position: 3
title: Distributed Tracing
description: Tracing distribuido con OpenTelemetry y W3C Trace Context
---

# Distributed Tracing

## Contexto

Este estándar define cómo implementar distributed tracing con OpenTelemetry siguiendo W3C Trace Context para correlacionar requests a través de múltiples servicios. Complementa el [lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) especificando **cómo** rastrear flujos end-to-end.

---

## Stack Tecnológico

| Componente          | Tecnología                  | Versión | Uso                           |
| ------------------- | --------------------------- | ------- | ----------------------------- |
| **Framework**       | ASP.NET Core                | 8.0+    | Framework base                |
| **Instrumentación** | OpenTelemetry .NET          | 1.7+    | SDK de tracing                |
| **Exportador**      | OpenTelemetry.Exporter.OTLP | 1.7+    | Export a Grafana Alloy        |
| **Propagación**     | W3C Trace Context           | 1.0     | Header traceparent/tracestate |
| **Collector**       | Grafana Alloy               | 1.0+    | Recolector OTLP               |
| **Storage**         | Grafana Tempo               | 2.3+    | Almacenamiento traces         |
| **Visualización**   | Grafana                     | 10.0+   | Traces y correlación          |

### Dependencias NuGet

```xml
<PackageReference Include="OpenTelemetry" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Exporter.OpenTelemetryProtocol" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Extensions.Hosting" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Instrumentation.AspNetCore" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Instrumentation.Http" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Instrumentation.EntityFrameworkCore" Version="1.0.0-beta.8" />
```

---

## Implementación Técnica

### Configuración Base OpenTelemetry

```csharp
// Program.cs
using OpenTelemetry.Trace;
using OpenTelemetry.Resources;

var builder = WebApplication.CreateBuilder(args);

// ✅ Configurar OpenTelemetry Tracing
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService(
            serviceName: "orders-api",
            serviceVersion: "1.0.0",
            serviceInstanceId: Environment.MachineName
        )
        .AddAttributes(new Dictionary<string, object>
        {
            ["deployment.environment"] = builder.Environment.EnvironmentName,
            ["service.namespace"] = "talma.orders"
        })
    )
    .WithTracing(tracing => tracing
        // ✅ Instrumentación automática ASP.NET Core
        .AddAspNetCoreInstrumentation(options =>
        {
            options.RecordException = true;
            options.EnrichWithHttpRequest = (activity, httpRequest) =>
            {
                activity.SetTag("http.client_ip", httpRequest.HttpContext.Connection.RemoteIpAddress?.ToString());
                activity.SetTag("http.user_agent", httpRequest.Headers["User-Agent"].ToString());
            };
            options.EnrichWithHttpResponse = (activity, httpResponse) =>
            {
                activity.SetTag("http.response_content_length", httpResponse.ContentLength);
            };
        })

        // ✅ Instrumentación automática HttpClient
        .AddHttpClientInstrumentation(options =>
        {
            options.RecordException = true;
            options.EnrichWithHttpRequestMessage = (activity, httpRequest) =>
            {
                activity.SetTag("http.request.method", httpRequest.Method.Method);
            };
        })

        // ✅ Instrumentación Entity Framework Core
        .AddEntityFrameworkCoreInstrumentation(options =>
        {
            options.SetDbStatementForText = true;
            options.SetDbStatementForStoredProcedure = true;
            options.EnrichWithIDbCommand = (activity, command) =>
            {
                activity.SetTag("db.rows_affected", command.ExecuteNonQuery());
            };
        })

        // ✅ Source custom
        .AddSource("Talma.Orders.Api")

        // ✅ Sampling: 100% en desarrollo, 10% en producción
        .SetSampler(builder.Environment.IsDevelopment()
            ? new AlwaysOnSampler()
            : new TraceIdRatioBasedSampler(0.1))

        // ✅ Exportar a Grafana Tempo via OTLP
        .AddOtlpExporter(options =>
        {
            options.Endpoint = new Uri("http://grafana-alloy:4317");
            options.Protocol = OpenTelemetry.Exporter.OtlpExportProtocol.Grpc;
        })
    );

var app = builder.Build();
app.Run();
```

### W3C Trace Context - Propagación de Headers

```http
# Request entrante con traceparent
GET /api/v1/orders/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: api.talma.com
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: talma=t61rcWkgMzE

# Formato traceparent:
# version-trace-id-parent-id-trace-flags
# 00-{traceId:32hex}-{spanId:16hex}-{flags:2hex}

# ✅ ASP.NET Core automáticamente:
# 1. Extrae traceparent del request
# 2. Crea nuevo span con parent-id
# 3. Propaga traceparent a downstream calls
```

### Spans Automáticos

```csharp
// ✅ ASP.NET Core crea spans automáticos para:
// - HTTP requests (GET /api/v1/orders/{id})
// - HTTP responses (status code, duration)
// - Exceptions (stack traces automáticos)

// ✅ HttpClient crea spans automáticos para:
// - HTTP calls a otros servicios
// - DNS resolution
// - Connection establishment

// ✅ EF Core crea spans automáticos para:
// - SELECT queries
// - INSERT/UPDATE/DELETE operations
// - Connection open/close

// Ejemplo de trace automático:
// orders-api: GET /api/v1/orders/550e8400-e29b-41d4-a716-446655440000
//   ├─ db: SELECT * FROM orders WHERE id = $1
//   ├─ http: GET http://customer-api/api/v1/customers/3fa85f64
//   │  └─ db: SELECT * FROM customers WHERE id = $1
//   └─ http: POST http://notification-api/api/v1/notifications
//      └─ kafka: SEND order.created
```

### Custom Spans

```csharp
using System.Diagnostics;

public class OrderService
{
    private static readonly ActivitySource _activitySource = new("Talma.Orders.Api", "1.0.0");

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        // ✅ Crear span custom
        using var activity = _activitySource.StartActivity(
            "ProcessOrder",
            ActivityKind.Internal
        );

        // ✅ Agregar tags
        activity?.SetTag("order.customer_id", request.CustomerId);
        activity?.SetTag("order.item_count", request.Items.Count);
        activity?.SetTag("order.country", request.Country);

        try
        {
            // Validación
            using (var validationActivity = _activitySource.StartActivity("ValidateOrder"))
            {
                await ValidateOrderAsync(request);
                validationActivity?.SetTag("validation.result", "success");
            }

            // Cálculo de precio
            using (var pricingActivity = _activitySource.StartActivity("CalculatePricing"))
            {
                var totalAmount = CalculateTotalAmount(request.Items);
                pricingActivity?.SetTag("pricing.total_amount", totalAmount);
                pricingActivity?.SetTag("pricing.currency", "USD");
            }

            // Persistencia
            using (var saveActivity = _activitySource.StartActivity("SaveOrder"))
            {
                var order = await SaveOrderAsync(request);
                saveActivity?.SetTag("db.order_id", order.Id);
            }

            // ✅ Marcar como exitoso
            activity?.SetStatus(ActivityStatusCode.Ok);

            return order;
        }
        catch (ValidationException ex)
        {
            // ✅ Registrar exception
            activity?.RecordException(ex);
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);

            // ✅ Tags de error
            activity?.SetTag("error.type", "validation");
            activity?.SetTag("error.message", ex.Message);

            throw;
        }
        catch (Exception ex)
        {
            activity?.RecordException(ex);
            activity?.SetStatus(ActivityStatusCode.Error, "Unexpected error");
            activity?.SetTag("error.type", "internal");

            throw;
        }
    }
}
```

### Spans para Operaciones de Larga Duración

```csharp
public class BackgroundOrderProcessor
{
    private static readonly ActivitySource _activitySource = new("Talma.Orders.Processor", "1.0.0");

    public async Task ProcessPendingOrdersAsync()
    {
        using var activity = _activitySource.StartActivity(
            "ProcessPendingOrders",
            ActivityKind.Internal
        );

        var pendingOrders = await GetPendingOrdersAsync();
        activity?.SetTag("orders.pending_count", pendingOrders.Count);

        var successCount = 0;
        var errorCount = 0;

        foreach (var order in pendingOrders)
        {
            // ✅ Span por cada orden procesada
            using var orderActivity = _activitySource.StartActivity(
                "ProcessSingleOrder",
                ActivityKind.Internal
            );

            orderActivity?.SetTag("order.id", order.Id);
            orderActivity?.SetTag("order.number", order.OrderNumber);

            try
            {
                await ProcessOrderAsync(order);
                successCount++;
                orderActivity?.SetStatus(ActivityStatusCode.Ok);
            }
            catch (Exception ex)
            {
                errorCount++;
                orderActivity?.RecordException(ex);
                orderActivity?.SetStatus(ActivityStatusCode.Error);
            }
        }

        activity?.SetTag("orders.processed_success", successCount);
        activity?.SetTag("orders.processed_errors", errorCount);
        activity?.SetStatus(ActivityStatusCode.Ok);
    }
}
```

### Propagación Manual de Trace Context

```csharp
public class OrderEventPublisher
{
    private static readonly ActivitySource _activitySource = new("Talma.Orders.Events", "1.0.0");

    public async Task PublishOrderCreatedAsync(Order order)
    {
        using var activity = _activitySource.StartActivity(
            "PublishOrderCreated",
            ActivityKind.Producer  // ✅ Producer for messaging
        );

        activity?.SetTag("messaging.system", "kafka");
        activity?.SetTag("messaging.destination", "order.created");
        activity?.SetTag("messaging.message_id", Guid.NewGuid().ToString());

        var orderEvent = new OrderCreatedEvent
        {
            OrderId = order.Id,
            OrderNumber = order.OrderNumber,
            CustomerId = order.CustomerId,
            TotalAmount = order.TotalAmount,
            CreatedAt = order.CreatedAt
        };

        // ✅ Propagar trace context en message headers
        var headers = new Headers();

        if (Activity.Current != null)
        {
            headers.Add("traceparent", Encoding.UTF8.GetBytes(Activity.Current.Id));

            if (!string.IsNullOrEmpty(Activity.Current.TraceStateString))
            {
                headers.Add("tracestate", Encoding.UTF8.GetBytes(Activity.Current.TraceStateString));
            }
        }

        var message = new Message<string, string>
        {
            Key = order.Id.ToString(),
            Value = JsonSerializer.Serialize(orderEvent),
            Headers = headers
        };

        await _kafkaProducer.ProduceAsync("order.created", message);

        activity?.SetTag("messaging.kafka.partition", message.Partition.Value);
        activity?.SetTag("messaging.kafka.offset", message.Offset.Value);
        activity?.SetStatus(ActivityStatusCode.Ok);
    }
}

// Consumer side
public class OrderCreatedConsumer
{
    private static readonly ActivitySource _activitySource = new("Talma.Notifications.Consumer", "1.0.0");

    public async Task ConsumeAsync(ConsumeResult<string, string> result)
    {
        // ✅ Extraer trace context de headers
        string? traceparent = null;
        string? tracestate = null;

        if (result.Message.Headers.TryGetLastBytes("traceparent", out var traceparentBytes))
        {
            traceparent = Encoding.UTF8.GetString(traceparentBytes);
        }

        if (result.Message.Headers.TryGetLastBytes("tracestate", out var tracestateBytes))
        {
            tracestate = Encoding.UTF8.GetString(tracestateBytes);
        }

        // ✅ Crear span como hijo del producer
        using var activity = _activitySource.StartActivity(
            "ConsumeOrderCreated",
            ActivityKind.Consumer,
            parentId: traceparent  // ✅ Link to producer span
        );

        if (!string.IsNullOrEmpty(tracestate))
        {
            activity?.SetTag("tracestate", tracestate);
        }

        activity?.SetTag("messaging.system", "kafka");
        activity?.SetTag("messaging.source", result.Topic);
        activity?.SetTag("messaging.kafka.partition", result.Partition.Value);
        activity?.SetTag("messaging.kafka.offset", result.Offset.Value);

        try
        {
            var orderEvent = JsonSerializer.Deserialize<OrderCreatedEvent>(result.Message.Value);

            await ProcessOrderCreatedEventAsync(orderEvent);

            activity?.SetStatus(ActivityStatusCode.Ok);
        }
        catch (Exception ex)
        {
            activity?.RecordException(ex);
            activity?.SetStatus(ActivityStatusCode.Error);
            throw;
        }
    }
}
```

### Sampling Strategies

```csharp
// ✅ 1. AlwaysOnSampler - 100% traces (Development)
.SetSampler(new AlwaysOnSampler())

// ✅ 2. TraceIdRatioBasedSampler - % aleatorio (Production)
.SetSampler(new TraceIdRatioBasedSampler(0.1))  // 10%

// ✅ 3. ParentBasedSampler - Heredar decisión del parent
.SetSampler(new ParentBasedSampler(
    new TraceIdRatioBasedSampler(0.1)
))

// ✅ 4. Custom Sampler - Basado en atributos
public class CustomSampler : Sampler
{
    public override SamplingResult ShouldSample(in SamplingParameters samplingParameters)
    {
        // Siempre samplear errores
        if (samplingParameters.Tags.Any(t => t.Key == "http.status_code" && t.Value.ToString().StartsWith("5")))
        {
            return new SamplingResult(SamplingDecision.RecordAndSample);
        }

        // Samplear 100% endpoints críticos
        if (samplingParameters.Tags.Any(t => t.Key == "http.route" && t.Value.ToString().Contains("/orders")))
        {
            return new SamplingResult(SamplingDecision.RecordAndSample);
        }

        // 10% para el resto
        return new TraceIdRatioBasedSampler(0.1).ShouldSample(samplingParameters);
    }
}
```

### Visualización en Grafana

```promql
# Buscar traces por TraceID
# Grafana → Explore → Tempo datasource
# Query: Trace ID = 4bf92f3577b34da6a3ce929d0e0e4736

# Buscar traces por tags
{
  resource.service.name="orders-api" &&
  span.http.status_code >= 500
}

# Buscar traces lentos
{
  resource.service.name="orders-api" &&
  duration > 1s
}

# Link desde logs a traces
# En Grafana Loki, derivar TraceID desde logs:
{
  job="orders-api"
}
| json
| __trace_id__=`TraceId`
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar OpenTelemetry SDK para tracing en .NET
- **MUST** propagar W3C Trace Context (traceparent header)
- **MUST** instrumentar ASP.NET Core automáticamente
- **MUST** instrumentar HttpClient automáticamente
- **MUST** crear spans custom para operaciones de negocio críticas
- **MUST** registrar exceptions en spans con `RecordException()`
- **MUST** establecer status de span (Ok, Error)
- **MUST** exportar traces a Grafana Tempo via OTLP
- **MUST** incluir resource attributes (service.name, environment)
- **MUST** propagar trace context en mensajes Kafka

### SHOULD (Fuertemente recomendado)

- **SHOULD** instrumentar Entity Framework Core automáticamente
- **SHOULD** agregar tags relevantes a spans (customer_id, country, etc.)
- **SHOULD** usar ActivityKind apropiado (Server, Client, Producer, Consumer, Internal)
- **SHOULD** implementar sampling en producción (10-20%)
- **SHOULD** enriquecer spans con información de negocio
- **SHOULD** crear spans para operaciones asíncronas largas
- **SHOULD** incluir baggage para propagar contexto de negocio

### MAY (Opcional)

- **MAY** usar custom samplers basados en atributos
- **MAY** implementar tail sampling para errores
- **MAY** agregar links entre spans relacionados
- **MAY** usar exemplares para link metrics → traces

### MUST NOT (Prohibido)

- **MUST NOT** samplear traces con errores (siempre capturar)
- **MUST NOT** incluir información sensible en tags
- **MUST NOT** crear spans excesivos en hot paths
- **MUST NOT** bloquear requests esperando export de traces
- **MUST NOT** hardcodear trace IDs

---

## Referencias

- [Lineamiento: Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md)
- Estándares relacionados:
  - [Structured Logging](structured-logging.md)
  - [Métricas](metrics-standards.md)
  - [Correlation IDs](correlation-ids.md)
- Especificaciones:
  - [OpenTelemetry Tracing](https://opentelemetry.io/docs/specs/otel/trace/)
  - [W3C Trace Context](https://www.w3.org/TR/trace-context/)
  - [Grafana Tempo](https://grafana.com/docs/tempo/)
