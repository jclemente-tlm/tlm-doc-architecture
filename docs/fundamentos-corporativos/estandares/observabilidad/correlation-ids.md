---
id: correlation-ids
sidebar_position: 4
title: Correlation IDs
description: Correlación de requests con X-Correlation-ID entre servicios
---

# Correlation IDs

## Contexto

Este estándar define cómo usar Correlation IDs (X-Correlation-ID) para rastrear requests a través de múltiples servicios y flujos asíncronos. Complementa el [lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) y [distributed tracing](distributed-tracing.md) proporcionando un identificador simple para troubleshooting.

---

## Stack Tecnológico

| Componente      | Tecnología    | Versión | Uso                          |
| --------------- | ------------- | ------- | ---------------------------- |
| **Framework**   | ASP.NET Core  | 8.0+    | Framework base               |
| **Logger**      | Serilog       | 3.1+    | Logging estructurado         |
| **Tracing**     | OpenTelemetry | 1.7+    | Distributed tracing          |
| **API Gateway** | Kong          | 3.4+    | Generación de Correlation ID |

---

## Implementación Técnica

### Middleware de Correlation ID

```csharp
// Middleware/CorrelationIdMiddleware.cs
using Serilog.Context;

public class CorrelationIdMiddleware
{
    private readonly RequestDelegate _next;
    private const string CorrelationIdHeader = "X-Correlation-ID";

    public CorrelationIdMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // ✅ Extraer o generar Correlation ID
        var correlationId = context.Request.Headers[CorrelationIdHeader].FirstOrDefault()
            ?? Guid.NewGuid().ToString();

        // ✅ Agregar a LogContext para incluir en todos los logs
        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            // ✅ Agregar a response headers
            context.Response.OnStarting(() =>
            {
                context.Response.Headers[CorrelationIdHeader] = correlationId;
                return Task.CompletedTask;
            });

            // ✅ Agregar a HttpContext.Items para acceso en controllers
            context.Items["CorrelationId"] = correlationId;

            // ✅ Agregar como Activity tag (OpenTelemetry)
            if (Activity.Current != null)
            {
                Activity.Current.SetTag("correlation.id", correlationId);
            }

            await _next(context);
        }
    }
}

// Program.cs
app.UseMiddleware<CorrelationIdMiddleware>();
```

### Propagación en HttpClient

```csharp
// Services/HttpClientCorrelationHandler.cs
public class HttpClientCorrelationHandler : DelegatingHandler
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private const string CorrelationIdHeader = "X-Correlation-ID";

    public HttpClientCorrelationHandler(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        // ✅ Propagar Correlation ID a downstream services
        var correlationId = _httpContextAccessor.HttpContext?.Items["CorrelationId"]?.ToString();

        if (!string.IsNullOrEmpty(correlationId))
        {
            request.Headers.Add(CorrelationIdHeader, correlationId);
        }

        return await base.SendAsync(request, cancellationToken);
    }
}

// Program.cs - Registrar handler
builder.Services.AddHttpContextAccessor();

builder.Services.AddHttpClient<ICustomerApiClient, CustomerApiClient>()
    .AddHttpMessageHandler<HttpClientCorrelationHandler>();

builder.Services.AddTransient<HttpClientCorrelationHandler>();
```

### Uso en Servicios

```csharp
public class OrderService
{
    private readonly ILogger<OrderService> _logger;
    private readonly IHttpContextAccessor _httpContextAccessor;

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        var correlationId = _httpContextAccessor.HttpContext?.Items["CorrelationId"]?.ToString();

        // ✅ Logs automáticamente incluyen CorrelationId por LogContext
        _logger.LogInformation(
            "Creating order for customer {CustomerId}",
            request.CustomerId
        );

        // Output:
        // {
        //   "Timestamp": "2024-01-15T10:30:00Z",
        //   "Message": "Creating order for customer 3fa85f64...",
        //   "Properties": {
        //     "CustomerId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        //     "CorrelationId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        //   }
        // }

        var order = await CreateOrderInternalAsync(request);

        return order;
    }
}
```

### Propagación en Kafka Messages

```csharp
public class OrderEventPublisher
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private readonly IProducer<string, string> _producer;

    public async Task PublishOrderCreatedAsync(Order order)
    {
        var correlationId = _httpContextAccessor.HttpContext?.Items["CorrelationId"]?.ToString()
            ?? Guid.NewGuid().ToString();

        var orderEvent = new OrderCreatedEvent
        {
            OrderId = order.Id,
            CorrelationId = correlationId,  // ✅ En payload
            OrderNumber = order.OrderNumber,
            CreatedAt = order.CreatedAt
        };

        var message = new Message<string, string>
        {
            Key = order.Id.ToString(),
            Value = JsonSerializer.Serialize(orderEvent),
            Headers = new Headers
            {
                // ✅ En headers también
                { "X-Correlation-ID", Encoding.UTF8.GetBytes(correlationId) }
            }
        };

        await _producer.ProduceAsync("order.created", message);

        _logger.LogInformation(
            "Published OrderCreated event for order {OrderId}",
            order.Id
        );
    }
}

// Consumer
public class OrderCreatedConsumer
{
    public async Task ConsumeAsync(ConsumeResult<string, string> result)
    {
        // ✅ Extraer Correlation ID de headers
        string? correlationId = null;

        if (result.Message.Headers.TryGetLastBytes("X-Correlation-ID", out var headerBytes))
        {
            correlationId = Encoding.UTF8.GetString(headerBytes);
        }

        // ✅ Si no está en headers, extraer del payload
        var orderEvent = JsonSerializer.Deserialize<OrderCreatedEvent>(result.Message.Value);
        correlationId ??= orderEvent.CorrelationId;

        // ✅ Agregar a LogContext
        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            _logger.LogInformation(
                "Processing OrderCreated event for order {OrderId}",
                orderEvent.OrderId
            );

            await ProcessEventAsync(orderEvent);
        }
    }
}
```

### Kong API Gateway - Generación de Correlation ID

```yaml
# Kong plugin: correlation-id
plugins:
  - name: correlation-id
    config:
      header_name: X-Correlation-ID
      generator: uuid
      echo_downstream: true # Include in response


# Si request no tiene X-Correlation-ID, Kong lo genera
# Si request tiene X-Correlation-ID, Kong lo propaga
# Kong siempre retorna X-Correlation-ID en response
```

### Búsqueda en Grafana Loki

```promql
# Buscar todos los logs de un request específico
{
  job="orders-api"
}
| json
| CorrelationId="a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# Buscar logs relacionados a través de múltiples servicios
{
  job=~"orders-api|customer-api|notification-api"
}
| json
| CorrelationId="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
| line_format "{{.Timestamp}} [{{.job}}] {{.Message}}"

# Timeline de un request completo
{
  job=~"orders-api|customer-api|notification-api"
}
| json
| CorrelationId="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
| unwrap Timestamp
| sort by Timestamp asc
```

### Background Jobs y Workers

```csharp
public class OrderProcessorWorker : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var orders = await GetPendingOrdersAsync();

            foreach (var order in orders)
            {
                // ✅ Generar Correlation ID único por cada orden procesada
                var correlationId = Guid.NewGuid().ToString();

                using (LogContext.PushProperty("CorrelationId", correlationId))
                using (var activity = Activity.Current?.Source.StartActivity("ProcessOrder"))
                {
                    activity?.SetTag("correlation.id", correlationId);

                    try
                    {
                        _logger.LogInformation(
                            "Processing order {OrderId}",
                            order.Id
                        );

                        await ProcessOrderAsync(order, correlationId);

                        _logger.LogInformation(
                            "Order {OrderId} processed successfully",
                            order.Id
                        );
                    }
                    catch (Exception ex)
                    {
                        _logger.LogError(
                            ex,
                            "Failed to process order {OrderId}",
                            order.Id
                        );
                    }
                }
            }

            await Task.Delay(TimeSpan.FromSeconds(30), stoppingToken);
        }
    }

    private async Task ProcessOrderAsync(Order order, string correlationId)
    {
        // ✅ Propagar Correlation ID a llamadas HTTP
        using var httpClient = _httpClientFactory.CreateClient();
        httpClient.DefaultRequestHeaders.Add("X-Correlation-ID", correlationId);

        await httpClient.PostAsync(
            "http://payment-api/api/v1/payments",
            JsonContent.Create(new { orderId = order.Id })
        );
    }
}
```

### Extension Methods para Acceso Rápido

```csharp
// Extensions/CorrelationIdExtensions.cs
public static class CorrelationIdExtensions
{
    private const string CorrelationIdKey = "CorrelationId";

    public static string GetCorrelationId(this HttpContext context)
    {
        return context.Items[CorrelationIdKey]?.ToString()
            ?? context.TraceIdentifier;
    }

    public static void SetCorrelationId(this HttpContext context, string correlationId)
    {
        context.Items[CorrelationIdKey] = correlationId;
    }

    public static string GetCorrelationId(this IHttpContextAccessor httpContextAccessor)
    {
        return httpContextAccessor.HttpContext?.GetCorrelationId()
            ?? Guid.NewGuid().ToString();
    }
}

// Uso en controller
[HttpGet("{id}")]
public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
{
    var correlationId = HttpContext.GetCorrelationId();

    _logger.LogInformation(
        "Fetching order {OrderId} with correlation {CorrelationId}",
        id,
        correlationId
    );

    return Ok(await _orderService.GetOrderAsync(id));
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar middleware para extraer/generar X-Correlation-ID
- **MUST** incluir Correlation ID en todos los logs via LogContext
- **MUST** propagar Correlation ID en headers HTTP downstream
- **MUST** retornar Correlation ID en response headers
- **MUST** incluir Correlation ID en mensajes Kafka (headers y payload)
- **MUST** usar formato UUID para Correlation IDs
- **MUST** generar nuevo Correlation ID si no se recibe
- **MUST** agregar Correlation ID como tag de OpenTelemetry Activity

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Kong API Gateway para generar Correlation IDs en edge
- **SHOULD** implementar DelegatingHandler para propagación automática
- **SHOULD** incluir Correlation ID en ProblemDetails (errores)
- **SHOULD** documentar Correlation ID en OpenAPI spec
- **SHOULD** generar Correlation ID único por cada job en workers

### MAY (Opcional)

- **MAY** usar formato personalizado para Correlation IDs (ej: tenant-uuid)
- **MAY** implementar jerarquía de IDs (causation-id, correlation-id)
- **MAY** incluir Correlation ID en métricas customizadas

### MUST NOT (Prohibido)

- **MUST NOT** modificar Correlation ID una vez establecido
- **MUST NOT** usar identificadores secuenciales predecibles
- **MUST NOT** incluir información sensible en Correlation ID
- **MUST NOT** reutilizar Correlation IDs entre requests diferentes

---

## Referencias

- [Lineamiento: Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md)
- Estándares relacionados:
  - [Structured Logging](structured-logging.md)
  - [Distributed Tracing](distributed-tracing.md)
  - [Métricas](metrics-standards.md)
- Especificaciones:
  - [Kong Correlation ID Plugin](https://docs.konghq.com/hub/kong-inc/correlation-id/)
  - [Serilog LogContext](https://github.com/serilog/serilog/wiki/Enrichment)
