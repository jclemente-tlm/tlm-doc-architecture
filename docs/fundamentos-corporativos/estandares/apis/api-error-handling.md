---
id: api-error-handling
sidebar_position: 6
title: Manejo de Errores en APIs
description: Estándar para el manejo consistente de errores en APIs usando RFC 7807 Problem Details, códigos de estado HTTP y logging estructurado.
tags: [apis, error-handling, rest, problem-details, rfc7807]
---

# Manejo de Errores en APIs

## Contexto

Este estándar define cómo manejar, reportar y registrar errores de manera consistente en todas las APIs. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Propósito:** Respuestas de error predecibles, diagnóstico rápido, experiencia de usuario clara.

---

## Stack Tecnológico

| Componente          | Tecnología                        | Versión | Uso                     |
| ------------------- | --------------------------------- | ------- | ----------------------- |
| **Framework**       | ASP.NET Core                      | 8.0+    | Manejo de excepciones   |
| **Problem Details** | Hellang.Middleware.ProblemDetails | 6.5+    | RFC 7807 implementation |
| **Logging**         | Serilog                           | 3.1+    | Logs estructurados      |
| **Validación**      | FluentValidation                  | 11.0+   | Errores de validación   |
| **Observability**   | OpenTelemetry                     | 1.7+    | Trazas de errores       |

---

## Formato de Error: RFC 7807

**Estructura:**

```json
{
  "type": "https://docs.talma.com/errors/validation-error",
  "title": "Uno o más errores de validación ocurrieron",
  "status": 400,
  "detail": "El campo 'email' no tiene un formato válido",
  "instance": "/api/v1/customers",
  "traceId": "0HN1JQFQ3K7QK:00000001",
  "errors": {
    "email": ["El formato del email es inválido"],
    "phone": ["El teléfono debe estar en formato E.164"]
  }
}
```

**Campos obligatorios:**

- `type`: URI que identifica el tipo de error
- `title`: Resumen legible del error
- `status`: Código de estado HTTP
- `detail`: Explicación específica del error (opcional)
- `instance`: URI de la petición que causó el error

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

```csharp
public static class ErrorTypes
{
    // Errores de cliente (4xx)
    public const string ValidationError = "https://docs.talma.com/errors/validation-error";
    public const string NotFound = "https://docs.talma.com/errors/not-found";
    public const string Unauthorized = "https://docs.talma.com/errors/unauthorized";
    public const string Forbidden = "https://docs.talma.com/errors/forbidden";
    public const string Conflict = "https://docs.talma.com/errors/conflict";
    public const string BusinessRule = "https://docs.talma.com/errors/business-rule";
    public const string RateLimit = "https://docs.talma.com/errors/rate-limit";

    // Errores de servidor (5xx)
    public const string InternalError = "https://docs.talma.com/errors/internal-error";
    public const string ServiceUnavailable = "https://docs.talma.com/errors/service-unavailable";
    public const string DependencyFailure = "https://docs.talma.com/errors/dependency-failure";
}
```

---

## Implementación

### Configuración Global

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Configurar Problem Details con Hellang.Middleware
builder.Services.AddProblemDetails(options =>
{
    // Mapear excepciones a Problem Details
    options.Map<ValidationException>(ex => new ProblemDetails
    {
        Type = ErrorTypes.ValidationError,
        Title = "Errores de validación",
        Status = StatusCodes.Status400BadRequest,
        Detail = ex.Message,
        Extensions =
        {
            ["errors"] = ex.Errors.GroupBy(e => e.PropertyName)
                .ToDictionary(
                    g => ToCamelCase(g.Key),
                    g => g.Select(e => e.ErrorMessage).ToArray())
        }
    });

    options.Map<NotFoundException>(ex => new ProblemDetails
    {
        Type = ErrorTypes.NotFound,
        Title = "Recurso no encontrado",
        Status = StatusCodes.Status404NotFound,
        Detail = ex.Message
    });

    options.Map<BusinessRuleException>(ex => new ProblemDetails
    {
        Type = ErrorTypes.BusinessRule,
        Title = "Regla de negocio violada",
        Status = StatusCodes.Status422UnprocessableEntity,
        Detail = ex.Message,
        Extensions =
        {
            ["ruleCode"] = ex.RuleCode
        }
    });

    options.Map<ConflictException>(ex => new ProblemDetails
    {
        Type = ErrorTypes.Conflict,
        Title = "Conflicto de recursos",
        Status = StatusCodes.Status409Conflict,
        Detail = ex.Message
    });

    options.Map<UnauthorizedAccessException>(ex => new ProblemDetails
    {
        Type = ErrorTypes.Forbidden,
        Title = "Acceso denegado",
        Status = StatusCodes.Status403Forbidden,
        Detail = "No tiene permisos para realizar esta acción"
    });

    // Errores no manejados (500)
    options.Map<Exception>(ex => new ProblemDetails
    {
        Type = ErrorTypes.InternalError,
        Title = "Error interno del servidor",
        Status = StatusCodes.Status500InternalServerError,
        Detail = builder.Environment.IsDevelopment()
            ? ex.Message
            : "Ocurrió un error inesperado. Por favor contacte al soporte."
    });

    // Agregar información adicional a todos los errores
    options.CustomizeProblemDetails = context =>
    {
        context.ProblemDetails.Instance = context.HttpContext.Request.Path;
        context.ProblemDetails.Extensions["traceId"] = context.HttpContext.TraceIdentifier;
        context.ProblemDetails.Extensions["timestamp"] = DateTime.UtcNow;

        // En desarrollo, incluir stack trace
        if (builder.Environment.IsDevelopment() &&
            context.Exception != null)
        {
            context.ProblemDetails.Extensions["stackTrace"] = context.Exception.StackTrace;
        }
    };

    // Incluir Problem Details en respuestas
    options.IncludeExceptionDetails = (ctx, ex) => builder.Environment.IsDevelopment();
});

var app = builder.Build();

// ⚠️ IMPORTANTE: UseProblemDetails debe ir ANTES de UseAuthentication/UseAuthorization
app.UseProblemDetails();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();
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

    /// <summary>
    /// Obtiene un cliente por ID
    /// </summary>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(CustomerDto), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<CustomerDto>> GetById(Guid id)
    {
        // ✅ Lanzar excepción, middleware la convierte a Problem Details
        var customer = await _customerService.GetByIdAsync(id);

        if (customer == null)
            throw new NotFoundException(nameof(Customer), id);

        return Ok(customer);
    }

    /// <summary>
    /// Crea un nuevo cliente
    /// </summary>
    [HttpPost]
    [ProducesResponseType(typeof(CustomerDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status409Conflict)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status422UnprocessableEntity)]
    public async Task<ActionResult<CustomerDto>> Create(
        [FromBody] CreateCustomerRequest request)
    {
        try
        {
            var customer = await _customerService.CreateAsync(request);

            return CreatedAtAction(
                nameof(GetById),
                new { id = customer.Id },
                customer);
        }
        catch (ConflictException ex)
        {
            // Ya manejado por middleware, solo para logging
            _logger.LogWarning(ex, "Conflicto al crear cliente: {Email}", request.Email);
            throw; // Re-lanzar para que middleware lo maneje
        }
    }

    /// <summary>
    /// Cancela un pedido
    /// </summary>
    [HttpPost("{id}/cancel")]
    [ProducesResponseType(typeof(OrderDto), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status422UnprocessableEntity)]
    public async Task<ActionResult<OrderDto>> CancelOrder(Guid id)
    {
        var order = await _orderService.GetByIdAsync(id);

        if (order == null)
            throw new NotFoundException(nameof(Order), id);

        // Validación de regla de negocio
        if (order.Status == OrderStatus.Shipped)
        {
            throw new BusinessRuleException(
                "ORDER_ALREADY_SHIPPED",
                "No se puede cancelar un pedido que ya fue enviado");
        }

        var cancelled = await _orderService.CancelAsync(id);
        return Ok(cancelled);
    }
}
```

### Servicio con Manejo de Errores

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

        // Retornar null, controller lanza NotFoundException
        return customer != null
            ? _mapper.Map<CustomerDto>(customer)
            : null;
    }

    public async Task<CustomerDto> CreateAsync(CreateCustomerRequest request)
    {
        // Validar email único
        var existingCustomer = await _context.Customers
            .FirstOrDefaultAsync(c => c.Email == request.Email);

        if (existingCustomer != null)
        {
            throw new ConflictException(
                $"Ya existe un cliente con el email '{request.Email}'");
        }

        // Validar documento único
        var existingDocument = await _context.Customers
            .FirstOrDefaultAsync(c =>
                c.DocumentType == request.Document.Type &&
                c.DocumentNumber == request.Document.Number);

        if (existingDocument != null)
        {
            throw new ConflictException(
                $"Ya existe un cliente con el documento {request.Document.Type}-{request.Document.Number}");
        }

        var customer = new Customer
        {
            Id = Guid.NewGuid(),
            Name = request.Name,
            Email = request.Email,
            Phone = request.Phone,
            DocumentType = request.Document.Type,
            DocumentNumber = request.Document.Number,
            CreatedAt = DateTime.UtcNow
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

        return _mapper.Map<CustomerDto>(customer);
    }
}
```

---

## Validación de Requests

### FluentValidation con Errores Estructurados

```csharp
// Validador
public class CreateCustomerRequestValidator : AbstractValidator<CreateCustomerRequest>
{
    public CreateCustomerRequestValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty()
            .WithMessage("El nombre es requerido")
            .WithErrorCode("REQUIRED_FIELD")
            .Length(2, 100)
            .WithMessage("El nombre debe tener entre 2 y 100 caracteres")
            .WithErrorCode("INVALID_LENGTH");

        RuleFor(x => x.Email)
            .NotEmpty()
            .WithMessage("El email es requerido")
            .WithErrorCode("REQUIRED_FIELD")
            .EmailAddress()
            .WithMessage("El formato del email es inválido")
            .WithErrorCode("INVALID_FORMAT");

        RuleFor(x => x.Phone)
            .Matches(@"^\+\d{10,15}$")
            .When(x => !string.IsNullOrEmpty(x.Phone))
            .WithMessage("El teléfono debe estar en formato E.164 (+51987654321)")
            .WithErrorCode("INVALID_FORMAT");

        RuleFor(x => x.Document)
            .NotNull()
            .WithMessage("El documento es requerido")
            .WithErrorCode("REQUIRED_FIELD")
            .SetValidator(new DocumentDtoValidator());
    }
}

// Resultado de validación para Problem Details
public class ValidationProblemDetailsResult : IActionResult
{
    private readonly ValidationResult _validationResult;

    public ValidationProblemDetailsResult(ValidationResult validationResult)
    {
        _validationResult = validationResult;
    }

    public async Task ExecuteResultAsync(ActionContext context)
    {
        var problemDetails = new ValidationProblemDetails
        {
            Type = ErrorTypes.ValidationError,
            Title = "Uno o más errores de validación ocurrieron",
            Status = StatusCodes.Status400BadRequest,
            Instance = context.HttpContext.Request.Path,
            Extensions =
            {
                ["traceId"] = context.HttpContext.TraceIdentifier
            }
        };

        foreach (var error in _validationResult.Errors)
        {
            var propertyName = ToCamelCase(error.PropertyName);

            if (!problemDetails.Errors.ContainsKey(propertyName))
            {
                problemDetails.Errors[propertyName] = new[] { error.ErrorMessage };
            }
            else
            {
                var existingErrors = problemDetails.Errors[propertyName].ToList();
                existingErrors.Add(error.ErrorMessage);
                problemDetails.Errors[propertyName] = existingErrors.ToArray();
            }
        }

        context.HttpContext.Response.StatusCode = StatusCodes.Status400BadRequest;
        await context.HttpContext.Response.WriteAsJsonAsync(problemDetails);
    }

    private static string ToCamelCase(string str)
    {
        if (string.IsNullOrEmpty(str) || !char.IsUpper(str[0]))
            return str;

        return char.ToLowerInvariant(str[0]) + str[1..];
    }
}
```

---

## Manejo de Errores en Dependencias Externas

### Circuit Breaker con Error Handling

```csharp
public class ExternalApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ExternalApiClient> _logger;
    private readonly IAsyncPolicy<HttpResponseMessage> _resiliencePolicy;

    public ExternalApiClient(
        HttpClient httpClient,
        ILogger<ExternalApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;

        // Política de resiliencia con manejo de errores
        var retry = Policy
            .Handle<HttpRequestException>()
            .Or<TimeoutException>()
            .OrResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
            .WaitAndRetryAsync(
                retryCount: 3,
                sleepDurationProvider: attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt)),
                onRetry: (outcome, timespan, retryCount, context) =>
                {
                    _logger.LogWarning(
                        "Retry {RetryCount} después de {Delay}ms: {Reason}",
                        retryCount,
                        timespan.TotalMilliseconds,
                        outcome.Exception?.Message ?? "HTTP " + outcome.Result.StatusCode);
                });

        var circuitBreaker = Policy
            .Handle<HttpRequestException>()
            .OrResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
            .CircuitBreakerAsync(
                handledEventsAllowedBeforeBreaking: 5,
                durationOfBreak: TimeSpan.FromSeconds(30),
                onBreak: (outcome, duration) =>
                {
                    _logger.LogError(
                        "Circuit breaker OPEN por {Duration}s: {Reason}",
                        duration.TotalSeconds,
                        outcome.Exception?.Message ?? "HTTP " + outcome.Result.StatusCode);
                },
                onReset: () =>
                {
                    _logger.LogInformation("Circuit breaker RESET");
                });

        _resiliencePolicy = Policy.WrapAsync(retry, circuitBreaker);
    }

    public async Task<CustomerData> GetCustomerAsync(string customerId)
    {
        try
        {
            var response = await _resiliencePolicy.ExecuteAsync(async () =>
                await _httpClient.GetAsync($"/customers/{customerId}"));

            if (!response.IsSuccessStatusCode)
            {
                throw new ServiceUnavailableException(
                    "ExternalApi",
                    new HttpRequestException($"HTTP {response.StatusCode}"));
            }

            return await response.Content.ReadFromJsonAsync<CustomerData>()
                ?? throw new InvalidOperationException("Response body was null");
        }
        catch (BrokenCircuitException ex)
        {
            _logger.LogError(ex, "Circuit breaker está abierto para ExternalApi");
            throw new ServiceUnavailableException("ExternalApi", ex);
        }
        catch (Exception ex) when (ex is not ServiceUnavailableException)
        {
            _logger.LogError(ex, "Error al llamar a ExternalApi");
            throw new ServiceUnavailableException("ExternalApi", ex);
        }
    }
}
```

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
  "type": "https://docs.talma.com/errors/validation-error",
  "title": "Uno o más errores de validación ocurrieron",
  "status": 400,
  "instance": "/api/v1/customers",
  "traceId": "0HN1JQFQ3K7QK:00000001",
  "timestamp": "2026-02-18T10:30:00Z",
  "errors": {
    "email": ["El formato del email es inválido"],
    "phone": ["El teléfono debe estar en formato E.164"],
    "document.number": [
      "Número de documento inválido para el tipo especificado"
    ]
  }
}
```

### Recurso No Encontrado (404)

```json
{
  "type": "https://docs.talma.com/errors/not-found",
  "title": "Recurso no encontrado",
  "status": 404,
  "detail": "Customer con ID 'f7c8e3a1-2b4d-4e6f-9a8b-1c2d3e4f5a6b' no fue encontrado",
  "instance": "/api/v1/customers/f7c8e3a1-2b4d-4e6f-9a8b-1c2d3e4f5a6b",
  "traceId": "0HN1JQFQ3K7QK:00000002",
  "timestamp": "2026-02-18T10:31:00Z"
}
```

### Regla de Negocio Violada (422)

```json
{
  "type": "https://docs.talma.com/errors/business-rule",
  "title": "Regla de negocio violada",
  "status": 422,
  "detail": "No se puede cancelar un pedido que ya fue enviado",
  "instance": "/api/v1/orders/a1b2c3d4-e5f6-7890-abcd-ef1234567890/cancel",
  "traceId": "0HN1JQFQ3K7QK:00000003",
  "timestamp": "2026-02-18T10:32:00Z",
  "ruleCode": "ORDER_ALREADY_SHIPPED"
}
```

### Conflicto (409)

```json
{
  "type": "https://docs.talma.com/errors/conflict",
  "title": "Conflicto de recursos",
  "status": 409,
  "detail": "Ya existe un cliente con el email 'john.doe@example.com'",
  "instance": "/api/v1/customers",
  "traceId": "0HN1JQFQ3K7QK:00000004",
  "timestamp": "2026-02-18T10:33:00Z"
}
```

### Servicio No Disponible (503)

```json
{
  "type": "https://docs.talma.com/errors/service-unavailable",
  "title": "Servicio no disponible",
  "status": 503,
  "detail": "El servicio 'ExternalApi' no está disponible",
  "instance": "/api/v1/customers/f7c8e3a1-2b4d-4e6f-9a8b-1c2d3e4f5a6b",
  "traceId": "0HN1JQFQ3K7QK:00000005",
  "timestamp": "2026-02-18T10:34:00Z"
}
```

### Error Interno (500)

```json
{
  "type": "https://docs.talma.com/errors/internal-error",
  "title": "Error interno del servidor",
  "status": 500,
  "detail": "Ocurrió un error inesperado. Por favor contacte al soporte.",
  "instance": "/api/v1/customers",
  "traceId": "0HN1JQFQ3K7QK:00000006",
  "timestamp": "2026-02-18T10:35:00Z"
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar RFC 7807 Problem Details para todos los errores
- **MUST** retornar códigos de estado HTTP apropiados
- **MUST** incluir `traceId` en todas las respuestas de error
- **MUST** loggear todos los errores con contexto suficiente
- **MUST** evitar exponer información sensible en mensajes de error
- **MUST** evitar stack traces en producción
- **MUST** mapear excepciones de dominio a Problem Details
- **MUST** validar requests antes de procesarlos

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar logging estructurado (Serilog)
- **SHOULD** incluir correlation ID en logs y respuestas
- **SHOULD** implementar métricas de errores (counters, histograms)
- **SHOULD** diferenciar errores de cliente (4xx) vs servidor (5xx)
- **SHOULD** incluir URIs descriptivas en campo `type`
- **SHOULD** usar códigos de error específicos para reglas de negocio
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
- [ASP.NET Core Error Handling](https://learn.microsoft.com/aspnet/core/web-api/handle-errors) — Manejo de errores en ASP.NET Core
- [Hellang.Middleware.ProblemDetails](https://github.com/khellang/Middleware) — Middleware RFC 7807
- [Serilog](https://serilog.net/) — Logging estructurado
- [Estándares REST](./rest-standards.md) — Estándar relacionado
- [Resiliencia](../arquitectura/resilience-patterns.md) — Estándar relacionado
- [Structured Logging](../observabilidad/structured-logging.md) — Configuración de logging
