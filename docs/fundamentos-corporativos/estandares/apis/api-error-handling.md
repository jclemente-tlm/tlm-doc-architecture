---
id: api-error-handling
sidebar_position: 5
title: Manejo de Errores en APIs
description: Estándar para el manejo consistente de errores en APIs usando el wrapper ApiResponse, códigos de error de negocio, códigos de estado HTTP y logging estructurado.
tags: [apis, error-handling, rest, response-wrapper]
---

# Manejo de Errores en APIs

## Contexto

Este estándar define cómo manejar, reportar y registrar errores de manera consistente en todas las APIs. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Propósito:** Respuestas de error predecibles, diagnóstico rápido, experiencia de usuario clara.

---

## Stack Tecnológico

| Componente        | Tecnología       | Versión | Uso                   |
| ----------------- | ---------------- | ------- | --------------------- |
| **Framework**     | ASP.NET Core     | 8.0+    | Manejo de excepciones |
| **Logging**       | Serilog          | 3.1+    | Logs estructurados    |
| **Validación**    | FluentValidation | 11.0+   | Errores de validación |
| **Observability** | OpenTelemetry    | 1.7+    | Trazas de errores     |

---

## Formato de Error: Wrapper ApiResponse

Todos los errores usan el mismo wrapper `ApiResponse<object>` definido en [Estándares REST](./api-rest-standards.md).

**Estructura:**

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_FAILED",
      "message": "La solicitud contiene errores de validación",
      "details": [
        { "field": "email", "issue": "El formato no es válido" },
        { "field": "name", "issue": "Es un campo requerido" }
      ]
    }
  ],
  "meta": {
    "traceId": "c1d2e3f4-5678-90ab-cdef-1234567890ab",
    "timestamp": "2024-01-15T10:30:01Z"
  }
}
```

**Campos obligatorios en cada item de `errors`:**

- `code`: Identificador único del tipo de error (_SCREAMING_SNAKE_CASE_)
- `message`: Resumen legible del error para el desarrollador
- `details`: Array de `{ field, issue }` para errores de campo (puede ser `[]`)

**Códigos de error estándar:**

```csharp
public static class ErrorCodes
{
    // Errores de cliente (4xx)
    public const string ValidationFailed    = "VALIDATION_FAILED";
    public const string NotFound            = "NOT_FOUND";
    public const string Unauthorized        = "UNAUTHORIZED";
    public const string Forbidden           = "FORBIDDEN";
    public const string Conflict            = "CONFLICT";
    public const string BusinessRuleViolated = "BUSINESS_RULE_VIOLATED";
    public const string RateLimitExceeded   = "RATE_LIMIT_EXCEEDED";

    // Errores de servidor (5xx)
    public const string InternalError       = "INTERNAL_ERROR";
    public const string ServiceUnavailable  = "SERVICE_UNAVAILABLE";
}
```

Los equipos pueden definir códigos específicos del dominio siguiendo el patrón: `RESOURCE_REASON`
(ej: `ORDER_ALREADY_SHIPPED`, `CUSTOMER_EMAIL_DUPLICATE`).

---

## Códigos de Estado HTTP

| Código | Uso                         | Ejemplo                       |
| ------ | --------------------------- | ----------------------------- |
| 400    | Request inválido            | JSON malformado               |
| 401    | No autenticado              | Token faltante o expirado     |
| 403    | Sin permisos                | Intento de acceso denegado    |
| 404    | Recurso no encontrado       | Customer no existe            |
| 409    | Conflicto de estado         | Email duplicado               |
| 422    | Validación de negocio falló | Edad < 18, saldo insuficiente |
| 429    | Rate limit excedido         | Demasiados requests           |
| 500    | Error interno no controlado | Excepción no manejada         |
| 503    | Servicio no disponible      | Dependencia externa caída     |

---

## Tipos de Error

Los errores del dominio se expresan como excepciones tipadas que `ApiExceptionHandler` convierte automáticamente en `ApiResponse<object>`. La jerarquía completa está en [Excepciones Personalizadas](#excepciones-personalizadas).

| Excepción                     | HTTP | Código de error           |
| ----------------------------- | ---- | ------------------------- |
| `ValidationException`         | 400  | `VALIDATION_FAILED`       |
| `NotFoundException`           | 404  | `NOT_FOUND`               |
| `ConflictException`           | 409  | `CONFLICT`                |
| `BusinessRuleException`       | 422  | código específico dominio |
| `UnauthorizedAccessException` | 403  | `FORBIDDEN`               |
| `ServiceUnavailableException` | 503  | `SERVICE_UNAVAILABLE`     |
| Cualquier otra `Exception`    | 500  | `INTERNAL_ERROR`          |

---

## Implementación

### Configuración Global

```csharp
// ApiExceptionHandler.cs
// Middleware global que convierte excepciones en ApiResponse<object>
public class ApiExceptionHandler : IExceptionHandler
{
    private readonly ILogger<ApiExceptionHandler> _logger;
    private readonly IHostEnvironment _env;

    public ApiExceptionHandler(ILogger<ApiExceptionHandler> logger, IHostEnvironment env)
    {
        _logger = logger;
        _env = env;
    }

    public async ValueTask<bool> TryHandleAsync(
        HttpContext context,
        Exception exception,
        CancellationToken cancellationToken)
    {
        var (statusCode, code, message, details) = exception switch
        {
            ValidationException ve => (
                StatusCodes.Status400BadRequest,
                ErrorCodes.ValidationFailed,
                "La solicitud contiene errores de validación",
                ve.Errors.Select(e => new ErrorDetail
                {
                    Field = char.ToLowerInvariant(e.PropertyName[0]) + e.PropertyName[1..],
                    Issue = e.ErrorMessage
                }).ToList()),

            NotFoundException nfe => (
                StatusCodes.Status404NotFound,
                ErrorCodes.NotFound,
                nfe.Message,
                (List<ErrorDetail>)[]),

            BusinessRuleException bre => (
                StatusCodes.Status422UnprocessableEntity,
                bre.RuleCode,
                bre.Message,
                (List<ErrorDetail>)[]),

            ConflictException ce => (
                StatusCodes.Status409Conflict,
                ErrorCodes.Conflict,
                ce.Message,
                (List<ErrorDetail>)[]),

            UnauthorizedAccessException => (
                StatusCodes.Status403Forbidden,
                ErrorCodes.Forbidden,
                "No tiene permisos para realizar esta acción",
                (List<ErrorDetail>)[]),

            _ => (
                StatusCodes.Status500InternalServerError,
                ErrorCodes.InternalError,
                _env.IsDevelopment() ? exception.Message : "Ocurrió un error inesperado.",
                (List<ErrorDetail>)[])
        };

        // Log según gravedad
        if (statusCode >= 500)
            _logger.LogError(exception, "Error no controlado: {Message}", exception.Message);
        else
            _logger.LogWarning(exception, "Error de cliente [{Code}]: {Message}", code, message);

        context.Response.StatusCode = statusCode;
        context.Response.ContentType = "application/json";

        var response = new ApiResponse<object>
        {
            Status = "error",
            Data   = null,
            Errors = [new ErrorInfo { Code = code, Message = message, Details = details }],
            Meta   = new MetaData
            {
                TraceId   = context.TraceIdentifier,
                Timestamp = DateTime.UtcNow
            }
        };

        await context.Response.WriteAsJsonAsync(response, cancellationToken);
        return true;
    }
}

// Program.cs
builder.Services.AddExceptionHandler<ApiExceptionHandler>();
app.UseExceptionHandler();
```

### Excepciones Personalizadas

```csharp
// Excepciones base
public abstract class DomainException : Exception
{
    protected DomainException(string message) : base(message) { }
    protected DomainException(string message, Exception innerException)
        : base(message, innerException) { }
}

// Not Found
public class NotFoundException : DomainException
{
    public NotFoundException(string resourceName, object key)
        : base($"{resourceName} con ID '{key}' no fue encontrado")
    {
        ResourceName = resourceName;
        Key = key;
    }

    public string ResourceName { get; }
    public object Key { get; }
}

// Business Rule Violation
public class BusinessRuleException : DomainException
{
    public BusinessRuleException(string ruleCode, string message)
        : base(message)
    {
        RuleCode = ruleCode;
    }

    public string RuleCode { get; }
}

// Conflict
public class ConflictException : DomainException
{
    public ConflictException(string message) : base(message) { }
}

// Service Unavailable
public class ServiceUnavailableException : DomainException
{
    public ServiceUnavailableException(string serviceName, Exception innerException)
        : base($"El servicio '{serviceName}' no está disponible", innerException)
    {
        ServiceName = serviceName;
    }

    public string ServiceName { get; }
}
```

### Uso en Controllers

```csharp
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
public class CustomersController : ControllerBase
{
    private readonly ICustomerService _customerService;
    private readonly ILogger<CustomersController> _logger;

    public CustomersController(
        ICustomerService customerService,
        ILogger<CustomersController> logger)
    {
        _customerService = customerService;
        _logger = logger;
    }

    // Controllers solo lanzar excepciones — ApiExceptionHandler las convierte al wrapper
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(ApiResponse<CustomerDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ApiResponse<CustomerDto>>> GetById(Guid id)
    {
        var customer = await _customerService.GetByIdAsync(id);
        if (customer is null)
            throw new NotFoundException(nameof(Customer), id);

        return Ok(ApiResponse<CustomerDto>.Success(
            customer,
            new MetaData { TraceId = HttpContext.TraceIdentifier }));
    }

    [HttpPost]
    [ProducesResponseType(typeof(ApiResponse<CustomerDto>), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status409Conflict)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status422UnprocessableEntity)]
    public async Task<ActionResult<ApiResponse<CustomerDto>>> Create(
        [FromBody] CreateCustomerRequest request)
    {
        var customer = await _customerService.CreateAsync(request);
        var response = ApiResponse<CustomerDto>.Success(
            customer,
            new MetaData { TraceId = HttpContext.TraceIdentifier });
        return CreatedAtAction(nameof(GetById), new { id = customer.Id }, response);
    }

    [HttpPost("{id}/cancel")]
    [ProducesResponseType(typeof(ApiResponse<OrderDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status422UnprocessableEntity)]
    public async Task<ActionResult<ApiResponse<OrderDto>>> CancelOrder(Guid id)
    {
        var order = await _orderService.GetByIdAsync(id);
        if (order is null)
            throw new NotFoundException(nameof(Order), id);

        if (order.Status == OrderStatus.Shipped)
            throw new BusinessRuleException(
                "ORDER_ALREADY_SHIPPED",
                "No se puede cancelar un pedido que ya fue enviado");

        var cancelled = await _orderService.CancelAsync(id);
        return Ok(ApiResponse<OrderDto>.Success(
            cancelled,
            new MetaData { TraceId = HttpContext.TraceIdentifier }));
    }
}
```

### Uso en Services

```csharp
public class CustomerService : ICustomerService
{
    private readonly AppDbContext _context;
    private readonly ILogger<CustomerService> _logger;

    public CustomerService(AppDbContext context, ILogger<CustomerService> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<CustomerDto?> GetByIdAsync(Guid id)
    {
        var customer = await _context.Customers
            .FirstOrDefaultAsync(c => c.Id == id);

        // Retornar null — el controller lanza NotFoundException
        return customer != null
            ? customer.Adapt<CustomerDto>()
            : null;
    }

    public async Task<CustomerDto> CreateAsync(CreateCustomerRequest request)
    {
        // Validar email único
        var existingCustomer = await _context.Customers
            .FirstOrDefaultAsync(c => c.Email == request.Email);

        if (existingCustomer != null)
            throw new ConflictException(
                $"Ya existe un cliente con el email '{request.Email}'");

        // Validar documento único
        var existingDocument = await _context.Customers
            .FirstOrDefaultAsync(c =>
                c.DocumentType == request.Document.Type &&
                c.DocumentNumber == request.Document.Number);

        if (existingDocument != null)
            throw new ConflictException(
                $"Ya existe un cliente con el documento {request.Document.Type}-{request.Document.Number}");

        var customer = new Customer
        {
            Id             = Guid.NewGuid(),
            Name           = request.Name,
            Email          = request.Email,
            Phone          = request.Phone,
            DocumentType   = request.Document.Type,
            DocumentNumber = request.Document.Number,
            CreatedAt      = DateTime.UtcNow
        };

        _context.Customers.Add(customer);

        try
        {
            await _context.SaveChangesAsync();
        }
        catch (DbUpdateException ex)
        {
            _logger.LogError(ex, "Error al guardar cliente en base de datos");
            throw new ServiceUnavailableException("Database", ex);
        }

        return customer.Adapt<CustomerDto>();
    }
}
```

---

:::note Errores de validación
Cuando `FluentValidation` o Data Annotations detectan un error, `ApiExceptionHandler` lo convierte automáticamente en `ApiResponse<object>` con `status: "error"`, código `VALIDATION_FAILED` y `errors[].details` por campo — sin código adicional en el controller.

Para definir validadores ver [Contratos de APIs — Validación](./api-contracts.md#validación-con-fluentvalidation).
:::

---

:::note Resiliencia y dependencias externas
Para manejo de errores en llamadas a servicios externos (retry, circuit breaker, timeout) ver [Patrones de Resiliencia](../arquitectura/resilience-patterns.md).
:::

---

## Logging de Errores

Loggear por tipo de excepción permite ajustar el nivel según gravedad y reducir ruido:

```csharp
catch (NotFoundException ex)          => _logger.LogWarning(ex, "Recurso no encontrado: {ResourceName} ID={Key}", ex.ResourceName, ex.Key);
catch (ValidationException ex)        => _logger.LogWarning("Validación: {Errors}", string.Join(", ", ex.Errors.Select(e => $"{e.PropertyName}: {e.ErrorMessage}")));
catch (BusinessRuleException ex)      => _logger.LogWarning(ex, "Regla violada: {RuleCode}", ex.RuleCode);
catch (ServiceUnavailableException ex)=> _logger.LogError(ex, "Servicio no disponible: {ServiceName}", ex.ServiceName);
catch (Exception ex)                  => _logger.LogError(ex, "Error no controlado: {Message}", ex.Message);
```

:::note Configuración de Serilog
Para la configuración completa de Serilog con enrichment, sinks y niveles ver [Structured Logging](../observabilidad/structured-logging.md).
:::

---

## Monitoreo y Observabilidad

:::note Métricas de errores
Para implementar métricas de errores (counters, histogramas por tipo de excepción) ver [Métricas y Estándares](../observabilidad/metrics-standards.md).
:::

---

## Ejemplos de Respuestas

### Error de Validación (400)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_FAILED",
      "message": "La solicitud contiene errores de validación",
      "details": [
        { "field": "email", "issue": "El formato del email es inválido" },
        {
          "field": "phone",
          "issue": "El teléfono debe estar en formato E.164"
        },
        { "field": "document.number", "issue": "Número de documento inválido" }
      ]
    }
  ],
  "meta": {
    "traceId": "0HN1JQFQ3K7QK:00000001",
    "timestamp": "2026-02-18T10:30:00Z"
  }
}
```

### Recurso No Encontrado (404)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "NOT_FOUND",
      "message": "Customer con ID 'f7c8e3a1-2b4d-4e6f-9a8b-1c2d3e4f5a6b' no fue encontrado",
      "details": []
    }
  ],
  "meta": {
    "traceId": "0HN1JQFQ3K7QK:00000002",
    "timestamp": "2026-02-18T10:31:00Z"
  }
}
```

### Regla de Negocio Violada (422)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "ORDER_ALREADY_SHIPPED",
      "message": "No se puede cancelar un pedido que ya fue enviado",
      "details": []
    }
  ],
  "meta": {
    "traceId": "0HN1JQFQ3K7QK:00000003",
    "timestamp": "2026-02-18T10:32:00Z"
  }
}
```

### Conflicto (409)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "CONFLICT",
      "message": "Ya existe un cliente con el email 'john.doe@example.com'",
      "details": []
    }
  ],
  "meta": {
    "traceId": "0HN1JQFQ3K7QK:00000004",
    "timestamp": "2026-02-18T10:33:00Z"
  }
}
```

### Servicio No Disponible (503)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "SERVICE_UNAVAILABLE",
      "message": "El servicio 'ExternalApi' no está disponible",
      "details": []
    }
  ],
  "meta": {
    "traceId": "0HN1JQFQ3K7QK:00000005",
    "timestamp": "2026-02-18T10:34:00Z"
  }
}
```

### Error Interno (500)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "INTERNAL_ERROR",
      "message": "Ocurrió un error inesperado. Por favor contacte al soporte.",
      "details": []
    }
  ],
  "meta": {
    "traceId": "0HN1JQFQ3K7QK:00000006",
    "timestamp": "2026-02-18T10:35:00Z"
  }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar `ApiResponse<object>` con `status: "error"` para todas las respuestas de error
- **MUST** retornar códigos de estado HTTP apropiados (no siempre 200)
- **MUST** incluir `meta.traceId` en todas las respuestas de error
- **MUST** usar `code` en _SCREAMING_SNAKE_CASE_ para identificar el tipo de error
- **MUST** loggear todos los errores con contexto suficiente
- **MUST** evitar exponer información sensible en mensajes de error
- **MUST** evitar stack traces en producción
- **MUST** mapear excepciones de dominio en `ApiExceptionHandler`
- **MUST** validar requests antes de procesarlos

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar logging estructurado (Serilog)
- **SHOULD** incluir correlation ID en logs y respuestas
- **SHOULD** implementar métricas de errores (counters, histograms)
- **SHOULD** diferenciar errores de cliente (4xx) vs servidor (5xx)
- **SHOULD** usar códigos de error específicos del dominio (`ORDER_ALREADY_SHIPPED`, no sólo `BUSINESS_RULE_VIOLATED`)
- **SHOULD** implementar alertas para errores 5xx

### MAY (Opcional)

- **MAY** incluir sugerencias de remediación en `detail`
- **MAY** incluir timestamp en respuestas de error
- **MAY** usar diferentes niveles de log según tipo de error

### MUST NOT (Prohibido)

- **MUST NOT** exponer detalles de implementación interna
- **MUST NOT** incluir stack traces en producción
- **MUST NOT** loggear información sensible (passwords, tokens)
- **MUST NOT** usar código 500 para errores de validación o negocio
- **MUST NOT** retornar HTML para APIs JSON

---

## Referencias

- [RFC 7807 - Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc7807.html) — Especificación Problem Details
- [RFC 9110 - HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) — Semántica HTTP
- [ASP.NET Core IExceptionHandler](https://learn.microsoft.com/aspnet/core/web-api/handle-errors) — Manejo de errores en ASP.NET Core
- [Serilog](https://serilog.net/) — Logging estructurado
- [Estándares REST](./api-rest-standards.md) — Estándar relacionado
- [Resiliencia](../arquitectura/resilience-patterns.md) — Estándar relacionado
- [Structured Logging](../observabilidad/structured-logging.md) — Configuración de logging
