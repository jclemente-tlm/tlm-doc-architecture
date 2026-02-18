---
id: api-error-handling
sidebar_position: 4
title: Manejo de Errores en APIs
description: Gestión consistente de errores usando RFC 7807 Problem Details
---

# Manejo de Errores en APIs

## Contexto

Este estándar define cómo manejar errores en APIs REST de forma consistente usando RFC 7807 Problem Details. Complementa el [lineamiento de APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md) especificando **cómo** estructurar respuestas de error, códigos de estado, y mensajes legibles.

---

## Stack Tecnológico

| Componente       | Tecnología       | Versión | Uso                      |
| ---------------- | ---------------- | ------- | ------------------------ |
| **Framework**    | ASP.NET Core     | 8.0+    | Framework base           |
| **Validación**   | FluentValidation | 11.0+   | Validación de requests   |
| **Logging**      | Serilog          | 3.1+    | Logging estructurado     |
| **Trazabilidad** | OpenTelemetry    | 1.7+    | Correlation IDs y traces |

### Dependencias NuGet

```xml
<PackageReference Include="FluentValidation.AspNetCore" Version="11.3.0" />
<PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
<PackageReference Include="OpenTelemetry.Extensions.Hosting" Version="1.7.0" />
```

---

## Implementación Técnica

### RFC 7807 Problem Details - Estructura Base

```csharp
// Respuesta de error estándar RFC 7807
{
  "type": "https://api.talma.com/errors/validation-failed",
  "title": "Validation failed",
  "status": 400,
  "detail": "One or more validation errors occurred",
  "instance": "/api/v1/orders",
  "traceId": "00-a1b2c3d4e5f6789012345678901234-1234567890abcdef-01",
  "errors": {
    "CustomerId": ["Customer ID is required"],
    "TotalAmount": ["Total amount must be greater than zero"]
  }
}

// Campos estándar:
// - type: URI único del tipo de error (para docs)
// - title: Resumen corto legible
// - status: Código HTTP
// - detail: Explicación detallada
// - instance: Path del request que falló
// - traceId: Correlation ID para troubleshooting
// - errors: Detalles adicionales (validaciones, campos, etc.)
```

### Middleware Global de Errores

```csharp
// Middleware/GlobalExceptionHandlerMiddleware.cs
using Microsoft.AspNetCore.Diagnostics;
using System.Diagnostics;

public class GlobalExceptionHandlerMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionHandlerMiddleware> _logger;
    private readonly IHostEnvironment _env;

    public GlobalExceptionHandlerMiddleware(
        RequestDelegate next,
        ILogger<GlobalExceptionHandlerMiddleware> logger,
        IHostEnvironment env)
    {
        _next = next;
        _logger = logger;
        _env = env;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        var traceId = Activity.Current?.Id ?? context.TraceIdentifier;

        _logger.LogError(
            exception,
            "Unhandled exception occurred. TraceId: {TraceId}, Path: {Path}",
            traceId,
            context.Request.Path
        );

        var problemDetails = exception switch
        {
            ValidationException validationEx => new ValidationProblemDetails
            {
                Type = "https://api.talma.com/errors/validation-failed",
                Title = "Validation failed",
                Status = StatusCodes.Status400BadRequest,
                Detail = validationEx.Message,
                Instance = context.Request.Path,
                Errors = validationEx.Errors
                    .GroupBy(e => e.PropertyName)
                    .ToDictionary(
                        g => g.Key,
                        g => g.Select(e => e.ErrorMessage).ToArray()
                    )
            },

            NotFoundException notFoundEx => new ProblemDetails
            {
                Type = "https://api.talma.com/errors/not-found",
                Title = "Resource not found",
                Status = StatusCodes.Status404NotFound,
                Detail = notFoundEx.Message,
                Instance = context.Request.Path
            },

            ConflictException conflictEx => new ProblemDetails
            {
                Type = "https://api.talma.com/errors/conflict",
                Title = "Conflict",
                Status = StatusCodes.Status409Conflict,
                Detail = conflictEx.Message,
                Instance = context.Request.Path
            },

            UnauthorizedException unauthorizedEx => new ProblemDetails
            {
                Type = "https://api.talma.com/errors/unauthorized",
                Title = "Unauthorized",
                Status = StatusCodes.Status401Unauthorized,
                Detail = unauthorizedEx.Message,
                Instance = context.Request.Path
            },

            ForbiddenException forbiddenEx => new ProblemDetails
            {
                Type = "https://api.talma.com/errors/forbidden",
                Title = "Forbidden",
                Status = StatusCodes.Status403Forbidden,
                Detail = forbiddenEx.Message,
                Instance = context.Request.Path
            },

            BusinessRuleException businessEx => new ProblemDetails
            {
                Type = "https://api.talma.com/errors/business-rule-violation",
                Title = "Business rule violation",
                Status = StatusCodes.Status422UnprocessableEntity,
                Detail = businessEx.Message,
                Instance = context.Request.Path
            },

            _ => new ProblemDetails
            {
                Type = "https://api.talma.com/errors/internal-server-error",
                Title = "Internal server error",
                Status = StatusCodes.Status500InternalServerError,
                Detail = _env.IsDevelopment()
                    ? exception.Message
                    : "An unexpected error occurred. Please contact support.",
                Instance = context.Request.Path
            }
        };

        // ✅ MUST: Incluir TraceId para correlación
        problemDetails.Extensions["traceId"] = traceId;

        // ✅ Development: Incluir stack trace
        if (_env.IsDevelopment() && exception is not ValidationException)
        {
            problemDetails.Extensions["stackTrace"] = exception.StackTrace;
        }

        context.Response.StatusCode = problemDetails.Status ?? StatusCodes.Status500InternalServerError;
        context.Response.ContentType = "application/problem+json";

        await context.Response.WriteAsJsonAsync(problemDetails);
    }
}

// Program.cs
app.UseMiddleware<GlobalExceptionHandlerMiddleware>();
```

### Excepciones de Dominio Personalizadas

```csharp
// Exceptions/DomainException.cs
public abstract class DomainException : Exception
{
    protected DomainException(string message) : base(message) { }
    protected DomainException(string message, Exception innerException)
        : base(message, innerException) { }
}

// Recurso no encontrado
public class NotFoundException : DomainException
{
    public NotFoundException(string resourceName, object key)
        : base($"{resourceName} with ID {key} was not found") { }
}

// Conflicto (duplicado, estado inválido)
public class ConflictException : DomainException
{
    public ConflictException(string message) : base(message) { }
}

// Regla de negocio violada
public class BusinessRuleException : DomainException
{
    public BusinessRuleException(string message) : base(message) { }
}

// No autorizado
public class UnauthorizedException : DomainException
{
    public UnauthorizedException(string message = "Authentication required")
        : base(message) { }
}

// Prohibido
public class ForbiddenException : DomainException
{
    public ForbiddenException(string message = "Access denied")
        : base(message) { }
}

// Uso:
if (order == null)
    throw new NotFoundException(nameof(Order), orderId);

if (existingOrder != null)
    throw new ConflictException($"Order with number {orderNumber} already exists");

if (order.Status != OrderStatus.Pending)
    throw new BusinessRuleException("Only pending orders can be cancelled");
```

### Validación con FluentValidation

```csharp
// Validators/CreateOrderRequestValidator.cs
using FluentValidation;

public class CreateOrderRequestValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderRequestValidator()
    {
        RuleFor(x => x.CustomerId)
            .NotEmpty()
            .WithMessage("Customer ID is required")
            .NotEqual(Guid.Empty)
            .WithMessage("Customer ID must be a valid GUID");

        RuleFor(x => x.Items)
            .NotEmpty()
            .WithMessage("Order must have at least one item")
            .Must(items => items.Count <= 50)
            .WithMessage("Order cannot have more than 50 items");

        RuleForEach(x => x.Items)
            .SetValidator(new CreateOrderItemValidator());

        RuleFor(x => x.ShippingAddress)
            .NotNull()
            .WithMessage("Shipping address is required")
            .SetValidator(new AddressValidator());
    }
}

public class CreateOrderItemValidator : AbstractValidator<CreateOrderItemRequest>
{
    public CreateOrderItemValidator()
    {
        RuleFor(x => x.ProductId)
            .NotEmpty()
            .WithMessage("Product ID is required");

        RuleFor(x => x.Quantity)
            .GreaterThan(0)
            .WithMessage("Quantity must be greater than zero")
            .LessThanOrEqualTo(100)
            .WithMessage("Quantity cannot exceed 100 units per item");

        RuleFor(x => x.UnitPrice)
            .GreaterThan(0)
            .WithMessage("Unit price must be greater than zero");
    }
}

// Program.cs
builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddValidatorsFromAssemblyContaining<CreateOrderRequestValidator>();

// Controller - automático
[HttpPost]
public async Task<ActionResult<OrderDto>> CreateOrder(
    [FromBody] CreateOrderRequest request) // ✅ Validación automática
{
    // Si llega aquí, request es válido
    var order = await _orderService.CreateOrderAsync(request);
    return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
}

// Respuesta de error de validación:
// HTTP/1.1 400 Bad Request
// {
//   "type": "https://api.talma.com/errors/validation-failed",
//   "title": "Validation failed",
//   "status": 400,
//   "detail": "One or more validation errors occurred",
//   "instance": "/api/v1/orders",
//   "traceId": "00-abc123...",
//   "errors": {
//     "CustomerId": ["Customer ID is required"],
//     "Items": ["Order must have at least one item"],
//     "Items[0].Quantity": ["Quantity must be greater than zero"]
//   }
// }
```

### Errores por Código de Estado

#### 400 Bad Request

```csharp
// Validación de input
[HttpPost]
public async Task<ActionResult> UpdateOrderStatus(
    Guid id,
    [FromBody] UpdateStatusRequest request)
{
    if (id != request.OrderId)
    {
        return BadRequest(new ProblemDetails
        {
            Type = "https://api.talma.com/errors/id-mismatch",
            Title = "ID mismatch",
            Status = StatusCodes.Status400BadRequest,
            Detail = "The ID in the URL does not match the ID in the request body",
            Instance = HttpContext.Request.Path
        });
    }

    // ...
}
```

#### 404 Not Found

```csharp
[HttpGet("{id}")]
public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
{
    var order = await _orderService.GetOrderByIdAsync(id);

    if (order == null)
    {
        return NotFound(new ProblemDetails
        {
            Type = "https://api.talma.com/errors/not-found",
            Title = "Order not found",
            Status = StatusCodes.Status404NotFound,
            Detail = $"Order with ID {id} does not exist",
            Instance = HttpContext.Request.Path
        });
    }

    return Ok(order);
}
```

#### 409 Conflict

```csharp
[HttpPost]
public async Task<ActionResult<OrderDto>> CreateOrder(
    [FromBody] CreateOrderRequest request)
{
    var existingOrder = await _orderService
        .GetOrderByNumberAsync(request.OrderNumber);

    if (existingOrder != null)
    {
        return Conflict(new ProblemDetails
        {
            Type = "https://api.talma.com/errors/duplicate",
            Title = "Order already exists",
            Status = StatusCodes.Status409Conflict,
            Detail = $"Order with number {request.OrderNumber} already exists",
            Instance = HttpContext.Request.Path
        });
    }

    // ...
}
```

#### 422 Unprocessable Entity (Business Rules)

```csharp
[HttpPost("{id}/cancel")]
public async Task<ActionResult<OrderDto>> CancelOrder(Guid id)
{
    var order = await _orderService.GetOrderByIdAsync(id);

    if (order == null)
        return NotFound();

    if (order.Status is OrderStatus.Shipped or OrderStatus.Delivered)
    {
        return UnprocessableEntity(new ProblemDetails
        {
            Type = "https://api.talma.com/errors/invalid-state-transition",
            Title = "Cannot cancel order",
            Status = StatusCodes.Status422UnprocessableEntity,
            Detail = $"Orders in '{order.Status}' status cannot be cancelled",
            Instance = HttpContext.Request.Path
        });
    }

    await _orderService.CancelOrderAsync(id);
    return Ok(order);
}
```

#### 429 Too Many Requests (Rate Limiting)

```csharp
// Middleware de rate limiting
services.AddRateLimiter(options =>
{
    options.OnRejected = async (context, cancellationToken) =>
    {
        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
        context.HttpContext.Response.ContentType = "application/problem+json";

        var problemDetails = new ProblemDetails
        {
            Type = "https://api.talma.com/errors/rate-limit-exceeded",
            Title = "Rate limit exceeded",
            Status = StatusCodes.Status429TooManyRequests,
            Detail = "Too many requests. Please try again later.",
            Instance = context.HttpContext.Request.Path
        };

        problemDetails.Extensions["retryAfter"] = context.Lease.TryGetMetadata(
            MetadataName.RetryAfter,
            out var retryAfter) ? retryAfter.TotalSeconds : 60;

        await context.HttpContext.Response.WriteAsJsonAsync(
            problemDetails,
            cancellationToken: cancellationToken
        );
    };
});

// Response:
// HTTP/1.1 429 Too Many Requests
// Retry-After: 60
// {
//   "type": "https://api.talma.com/errors/rate-limit-exceeded",
//   "title": "Rate limit exceeded",
//   "status": 429,
//   "detail": "Too many requests. Please try again later.",
//   "instance": "/api/v1/orders",
//   "retryAfter": 60
// }
```

#### 500 Internal Server Error

```csharp
// Manejado por middleware global
// NO incluir detalles sensibles en producción
{
  "type": "https://api.talma.com/errors/internal-server-error",
  "title": "Internal server error",
  "status": 500,
  "detail": "An unexpected error occurred. Please contact support with trace ID.",
  "instance": "/api/v1/orders",
  "traceId": "00-a1b2c3d4e5f6789012345678901234-1234567890abcdef-01"
}

// ✅ Development: Incluir stack trace
{
  // ... campos estándar
  "stackTrace": "   at Talma.Orders.Api.Services.OrderService..."
}
```

### Logging de Errores

```csharp
// Program.cs - Configurar Serilog
using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.File("logs/app-.log", rollingInterval: RollingInterval.Day)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithProperty("Application", "Orders.Api")
    .CreateLogger();

builder.Host.UseSerilog();

// Middleware - Log con contexto
_logger.LogError(
    exception,
    "Order creation failed. OrderNumber: {OrderNumber}, CustomerId: {CustomerId}, TraceId: {TraceId}",
    request.OrderNumber,
    request.CustomerId,
    context.TraceIdentifier
);

// Log estructurado JSON:
// {
//   "Timestamp": "2024-01-15T10:30:00.000Z",
//   "Level": "Error",
//   "MessageTemplate": "Order creation failed. OrderNumber: {OrderNumber}...",
//   "Properties": {
//     "OrderNumber": "ORD-2024-001234",
//     "CustomerId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
//     "TraceId": "00-abc123...",
//     "Application": "Orders.Api",
//     "MachineName": "orders-api-pod-1"
//   },
//   "Exception": "..."
// }
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar RFC 7807 Problem Details para todos los errores
- **MUST** incluir campos obligatorios: `type`, `title`, `status`, `detail`, `instance`
- **MUST** incluir `traceId` para correlación con logs
- **MUST** usar códigos de estado HTTP apropiados (400, 404, 409, 422, 500)
- **MUST** retornar `application/problem+json` como Content-Type
- **MUST** implementar middleware global para excepciones no manejadas
- **MUST** validar input con FluentValidation
- **MUST** loggear errores 5xx con nivel ERROR
- **MUST** ocultar detalles sensibles en Producción (stack traces, conexiones DB)
- **MUST** usar excepciones de dominio personalizadas (`NotFoundException`, `ConflictException`)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar URIs públicos en campo `type` (docs de error)
- **SHOULD** incluir información adicional en `extensions` cuando sea útil
- **SHOULD** proporcionar mensajes de error legibles para humanos
- **SHOULD** loggear context adicional (IDs, user, operation)
- **SHOULD** implementar rate limiting con respuestas 429
- **SHOULD** incluir `Retry-After` header en errores 429 y 503
- **SHOULD** usar ProblemDetails en controllers vía helper methods

### MAY (Opcional)

- **MAY** incluir sugerencias de corrección en `detail`
- **MAY** incluir links a documentación en `type` URI
- **MAY** agregar `correlationId` adicional al `traceId`
- **MAY** implementar error budgets y alertas

### MUST NOT (Prohibido)

- **MUST NOT** exponer stack traces en Producción
- **MUST NOT** incluir información sensible (passwords, tokens, PII)
- **MUST NOT** retornar HTML en APIs REST
- **MUST NOT** usar `200 OK` con payload de error
- **MUST NOT** usar códigos de estado genéricos (siempre 200 o 500)
- **MUST NOT** loggear información sensible (passwords, tarjetas de crédito)

---

## Referencias

- [Lineamiento: APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md)
- Estándares relacionados:
  - [Estándares REST](api-rest-standards.md)
  - [Documentación OpenAPI](openapi-specification.md)
- Especificaciones:
  - [RFC 7807: Problem Details](https://tools.ietf.org/html/rfc7807)
  - [FluentValidation Documentation](https://docs.fluentvalidation.net/)
  - [Serilog Best Practices](https://github.com/serilog/serilog/wiki/Best-Practices)
