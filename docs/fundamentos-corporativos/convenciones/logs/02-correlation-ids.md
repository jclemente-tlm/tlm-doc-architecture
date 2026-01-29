---
id: correlation-ids
sidebar_position: 2
title: Correlation IDs
description: Convención para propagación de IDs de correlación entre servicios
---

## 1. Principio

Cada request debe tener un ID único (Correlation ID) que se propague a través de todos los servicios para facilitar el rastreo end-to-end de transacciones.

## 2. Reglas

### Regla 1: Generar en API Gateway o Cliente

- **Generado por**: API Gateway o primer servicio que recibe el request
- **Formato**: UUID v4 (Guid en .NET)
- **Header**: `X-Correlation-ID`
- **Propagación**: A TODOS los servicios downstream

```csharp
// Middleware ASP.NET Core
public class CorrelationIdMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers["X-Correlation-ID"].FirstOrDefault()
            ?? Guid.NewGuid().ToString();

        context.Request.Headers["X-Correlation-ID"] = correlationId;
        context.Response.Headers["X-Correlation-ID"] = correlationId;

        await _next(context);
    }
}
```

### Regla 2: Request ID por Servicio

Además del Correlation ID (que es único por transacción end-to-end), cada servicio genera su propio Request ID:

- **X-Correlation-ID**: Mismo para toda la transacción (e.g., desde frontend hasta DB)
- **X-Request-ID**: Único por cada hop/servicio

```
Frontend Request
└─ X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000
   │
   ├─ API Gateway
   │  └─ X-Request-ID: 7f3d6b2a-8c1e-4d5f-9a2b-3c4d5e6f7890
   │
   ├─ User Service
   │  └─ X-Request-ID: 9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d
   │
   └─ Order Service
      └─ X-Request-ID: 1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d
```

### Regla 3: Incluir en TODOS los Logs

```csharp
// .NET - Structured Logging
_logger.LogInformation(
    "User created. UserId={UserId}, CorrelationId={CorrelationId}",
    userId, correlationId);

_logger.LogInformation(
    "Order placed. OrderId={OrderId}, CorrelationId={CorrelationId}, RequestId={RequestId}",
    orderId, correlationId, requestId);
```

**Output JSON:**

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "message": "Order placed",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "requestId": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
  "orderId": 123,
  "userId": 456,
  "service": "order-service",
  "environment": "prod"
}
```

### Regla 4: Propagación en HTTP Clients

#### .NET HttpClient

```csharp
public class CorrelationIdDelegatingHandler : DelegatingHandler
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var correlationId = _httpContextAccessor.HttpContext?
            .Request.Headers["X-Correlation-ID"].ToString();

        if (!string.IsNullOrEmpty(correlationId))
        {
            request.Headers.Add("X-Correlation-ID", correlationId);
        }

        // Generar nuevo Request-ID para este hop
        request.Headers.Add("X-Request-ID", Guid.NewGuid().ToString());

        return await base.SendAsync(request, cancellationToken);
    }
}

// Configuración
services.AddHttpClient<IUserService, UserService>()
    .AddHttpMessageHandler<CorrelationIdDelegatingHandler>();
```

### Regla 5: Incluir en Respuestas

Retornar el Correlation ID en headers de respuesta:

```csharp
// ASP.NET Core
Response.Headers["X-Correlation-ID"] = correlationId;
Response.Headers["X-Request-ID"] = requestId;

return Ok(new { data = result });
```

### Regla 6: Propagación en Mensajería

#### Kafka (.NET)

```csharp
// Producer
var message = new Message<string, string>
{
    Key = orderId.ToString(),
    Value = JsonSerializer.Serialize(orderData),
    Headers = new Headers
    {
        { "X-Correlation-ID", Encoding.UTF8.GetBytes(correlationId) },
        { "X-Request-ID", Encoding.UTF8.GetBytes(requestId) }
    }
};

await producer.ProduceAsync("order-created", message);

// Consumer
var consumeResult = consumer.Consume();
var correlationIdBytes = consumeResult.Message.Headers
    .FirstOrDefault(h => h.Key == "X-Correlation-ID")?.GetValueBytes();
var correlationId = correlationIdBytes != null
    ? Encoding.UTF8.GetString(correlationIdBytes)
    : Guid.NewGuid().ToString();

_logger.LogInformation("Processing order event. CorrelationId={CorrelationId}, OrderId={OrderId}",
    correlationId, consumeResult.Message.Key);
```

#### SQS

```csharp
// Enviar mensaje
await sqsClient.SendMessageAsync(new SendMessageRequest
{
    QueueUrl = queueUrl,
    MessageBody = JsonSerializer.Serialize(order),
    MessageAttributes = new Dictionary<string, MessageAttributeValue>
    {
        ["X-Correlation-ID"] = new MessageAttributeValue
        {
            DataType = "String",
            StringValue = correlationId
        }
    }
});

// Recibir mensaje
var correlationId = message.MessageAttributes["X-Correlation-ID"].StringValue;
_logger.LogInformation("Processing SQS message. CorrelationId={CorrelationId}", correlationId);
```

## 3. Búsqueda en Logs Centralizados

### CloudWatch Insights

```sql
fields @timestamp, message, correlationId, service, level
| filter correlationId = "550e8400-e29b-41d4-a716-446655440000"
| sort @timestamp asc
```

### Datadog

```
correlationId:550e8400-e29b-41d4-a716-446655440000
```

### Elasticsearch/Kibana

```json
{
  "query": {
    "match": {
      "correlationId": "550e8400-e29b-41d4-a716-446655440000"
    }
  },
  "sort": [{ "@timestamp": "asc" }]
}
```

## 4. Trace Completo End-to-End

Ejemplo de logs con mismo Correlation ID:

```json
[
  {
    "timestamp": "2024-01-15T10:30:00.100Z",
    "service": "api-gateway",
    "level": "INFO",
    "message": "Incoming request",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "requestId": "7f3d6b2a-8c1e-4d5f-9a2b-3c4d5e6f7890",
    "method": "POST",
    "path": "/api/v1/orders"
  },
  {
    "timestamp": "2024-01-15T10:30:00.250Z",
    "service": "user-service",
    "level": "INFO",
    "message": "Fetching user",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "requestId": "9a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d",
    "userId": 123
  },
  {
    "timestamp": "2024-01-15T10:30:00.400Z",
    "service": "order-service",
    "level": "INFO",
    "message": "Creating order",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "requestId": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "userId": 123,
    "totalAmount": 1234.56
  },
  {
    "timestamp": "2024-01-15T10:30:00.600Z",
    "service": "payment-service",
    "level": "INFO",
    "message": "Processing payment",
    "correlationId": "550e8400-e29b-41d4-a716-446655440000",
    "requestId": "2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e",
    "orderId": 456,
    "amount": 1234.56
  }
]
```

## 5. Integración con APM (Application Performance Monitoring)

### OpenTelemetry

```typescript
import { trace, SpanStatusCode } from "@opentelemetry/api";

const tracer = trace.getTracer("order-service");

export async function createOrder(orderData: OrderDto) {
  const span = tracer.startSpan("createOrder");
  const correlationId = asyncLocalStorage.getStore()?.correlationId;

  span.setAttribute("correlationId", correlationId);
  span.setAttribute("userId", orderData.userId);

  try {
    const order = await orderRepository.create(orderData);
    span.setStatus({ code: SpanStatusCode.OK });
    return order;
  } catch (error) {
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message,
    });
    throw error;
  } finally {
    span.end();
  }
}
```

## 6. Herramientas de Validación

### Middleware de Validación

```csharp
public class CorrelationIdMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        // Obtener o generar Correlation-ID
        var correlationId = context.Request.Headers["X-Correlation-ID"]
            .FirstOrDefault() ?? Guid.NewGuid().ToString();

        // Validar formato UUID
        if (!Guid.TryParse(correlationId, out _))
        {
            context.Response.StatusCode = 400;
            await context.Response.WriteAsJsonAsync(new
            {
                error = "X-Correlation-ID must be a valid UUID"
            });
            return;
        }

        // Agregar a response headers
        context.Response.Headers.Add("X-Correlation-ID", correlationId);

        // Almacenar en HttpContext.Items para acceso posterior
        context.Items["CorrelationId"] = correlationId;

        await _next(context);
    }
}
```

## 📖 Referencias

### Estándares relacionados

- [Logging Estructurado](/docs/fundamentos-corporativos/estandares/observabilidad/logging)

### Convenciones relacionadas

- [Headers HTTP](/docs/fundamentos-corporativos/convenciones/apis/headers-http)
- [Niveles de Log](./01-niveles-log.md)

### Recursos externos

- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [OpenTelemetry](https://opentelemetry.io/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
