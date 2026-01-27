---
id: validacion-y-errores
sidebar_position: 3
title: Validación y Manejo de Errores
description: Estándar para validación de entrada con FluentValidation, manejo de errores con RFC 7807 Problem Details y middleware global de excepciones
---

# Estándar: Validación y Manejo de Errores

## 1. Propósito

Definir la implementación técnica obligatoria para **validación de entrada** y **manejo consistente de errores** en APIs REST, usando FluentValidation 11+, RFC 7807 Problem Details, middleware global de excepciones y logging estructurado.

> **Nota**: Para formatos de respuesta JSON (envelope, códigos HTTP), consulta [Convenciones - Formato de Respuestas](../../convenciones/apis/03-formato-respuestas.md).

## 2. Alcance

### Aplica a

- ✅ Validación de DTOs de entrada (requests)
- ✅ Validación de lógica de negocio
- ✅ Manejo de excepciones globales
- ✅ Respuestas de error consistentes (RFC 7807)

### NO aplica a

- ❌ Validación en frontend (responsabilidad del cliente)
- ❌ Validación de entidades de dominio (use domain validation patterns)

## 3. Tecnologías Obligatorias

### Stack de Validación y Errores

| Tecnología                          | Versión Mínima | Propósito                           |
| ----------------------------------- | -------------- | ----------------------------------- |
| **FluentValidation**                | 11.0+          | Validación de DTOs (recomendado)    |
| **FluentValidation.AspNetCore**     | 11.0+          | Integración con ASP.NET Core        |
| **Hellang.Middleware.ProblemDetails**| 6.5+          | RFC 7807 Problem Details middleware |
| **Serilog.AspNetCore**              | 8.0+           | Logging estructurado de errores     |

### Estándares Web

- **RFC 7807**: Problem Details for HTTP APIs (formato de error estándar)
- **Códigos HTTP**: Uso correcto de 4xx (client errors) y 5xx (server errors)

### Implementación con FluentValidation (Recomendado)

```csharp
public class CreateUserRequestValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserRequestValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("El nombre es obligatorio")
            .Length(2, 100).WithMessage("El nombre debe tener entre 2 y 100 caracteres")
            .Matches(@"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$")
            .WithMessage("El nombre solo puede contener letras y espacios");

        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("El email es obligatorio")
            .EmailAddress().WithMessage("El formato del email no es válido")
            .MaximumLength(255).WithMessage("El email es demasiado largo")
            .Must(HaveValidDomain).WithMessage("Solo se permiten emails de dominios: talma.pe, talma.com");

        RuleFor(x => x.Phone)
            .Matches(@"^\+?[\d\s\-\(\)]{7,15}$")
            .WithMessage("El formato del teléfono no es válido")
            .When(x => !string.IsNullOrEmpty(x.Phone));

        RuleFor(x => x.Age)
            .InclusiveBetween(18, 120)
            .WithMessage("La edad debe estar entre 18 y 120 años");

        RuleFor(x => x.Roles)
            .NotEmpty().WithMessage("Debe seleccionar al menos un rol")
            .Must(roles => roles.All(role => IsValidRole(role)))
            .WithMessage("Uno o más roles no son válidos");
    }

    private static bool HaveValidDomain(string email)
    {
        if (string.IsNullOrEmpty(email)) return true;

        var allowedDomains = new[] { "talma.pe", "talma.com" };
        var domain = email.Split('@').LastOrDefault()?.ToLower();
        return allowedDomains.Contains(domain);
    }

    private static bool IsValidRole(string role)
    {
        var validRoles = new[] { "Admin", "User", "Manager", "Operator" };
        return validRoles.Contains(role);
    }
}

public class CreateUserRequest
{
    public string Name { get; set; }
    public string Email { get; set; }
    public string Phone { get; set; }
    public int Age { get; set; }
    public List<string> Roles { get; set; } = new();
}
```

### Implementación alternativa con Data Annotations

```csharp
public class CreateUserRequest
{
    [Required(ErrorMessage = "El nombre es obligatorio")]
    [StringLength(100, MinimumLength = 2,
        ErrorMessage = "El nombre debe tener entre 2 y 100 caracteres")]
    [RegularExpression(@"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$",
        ErrorMessage = "El nombre solo puede contener letras y espacios")]
    public string Name { get; set; }

    [Required(ErrorMessage = "El email es obligatorio")]
    [EmailAddress(ErrorMessage = "El formato del email no es válido")]
    [StringLength(255, ErrorMessage = "El email es demasiado largo")]
    [ValidEmailDomain]
    public string Email { get; set; }

    [Phone(ErrorMessage = "El formato del teléfono no es válido")]
    [StringLength(15, ErrorMessage = "Teléfono demasiado largo")]
    public string Phone { get; set; }

    [Range(18, 120, ErrorMessage = "La edad debe estar entre 18 y 120 años")]
    public int Age { get; set; }

    [Required]
    [MinLength(1, ErrorMessage = "Debe seleccionar al menos un rol")]
    public List<string> Roles { get; set; } = new();
}
```

### Validación personalizada con Data Annotations

```csharp
public class ValidEmailDomainAttribute : ValidationAttribute
{
    private readonly string[] _allowedDomains = { "talma.pe", "talma.com" };

    protected override ValidationResult IsValid(object value, ValidationContext validationContext)
    {
        if (value is string email && !string.IsNullOrEmpty(email))
        {
            var domain = email.Split('@').LastOrDefault();
            if (!_allowedDomains.Contains(domain?.ToLower()))
            {
                return new ValidationResult(
                    $"Solo se permiten emails de dominios: {string.Join(", ", _allowedDomains)}");
            }
        }
        return ValidationResult.Success;
    }
}
```

### Validación a nivel de negocio

```csharp
public class UserService
{
    public async Task<Result<User>> CreateUserAsync(CreateUserRequest request)
    {
        // Validaciones de negocio
        if (await EmailExistsAsync(request.Email))
            return Result<User>.Failure("EMAIL_EXISTS", "Ya existe un usuario con este email");

        if (await IsRestrictedUsernameAsync(request.Name))
            return Result<User>.Failure("RESTRICTED_USERNAME", "Nombre de usuario no permitido");

        if (!await HasValidLicenseForNewUserAsync())
            return Result<User>.Failure("NO_LICENSES", "No hay licencias disponibles");

        // Crear usuario...
        var user = new User { /* ... */ };
        return Result<User>.Success(user);
    }
}

public class Result<T>
{
    public bool IsSuccess { get; private set; }
    public T Value { get; private set; }
    public string ErrorCode { get; private set; }
    public string Error { get; private set; }

    private Result(bool isSuccess, T value, string errorCode, string error)
    {
        IsSuccess = isSuccess;
        Value = value;
        ErrorCode = errorCode;
        Error = error;
    }

    public static Result<T> Success(T value) => new(true, value, null, null);
    public static Result<T> Failure(string errorCode, string error) => new(false, default, errorCode, error);
}
```

## ⚠️ Manejo de errores

### Herramientas Obligatorias

- **Middleware global**: Captura y manejo centralizado de excepciones
- **Excepciones personalizadas**: Jerarquía de excepciones de negocio
- **Logging estructurado**: ILogger + contexto (ver [ADR-016](/docs/adrs/adr-016-logging-estructurado))
- **Activity/TraceId**: Propagación de correlation ID

### Estructura de Respuesta de Error

> **Importante**: La estructura de respuesta estándar está definida en [Convenciones - Formato de Respuestas](/docs/fundamentos-corporativos/convenciones/apis/formato-respuestas).

```csharp
public class ApiResponse<T>
{
    public string Status { get; set; } = "success";
    public T Data { get; set; }
    public List<ErrorInfo> Errors { get; set; } = new();
    public MetaData Meta { get; set; } = new();
}

public class ErrorInfo
{
    public string Code { get; set; }
    public string Message { get; set; }
    public List<ErrorDetail> Details { get; set; } = new();
}

public class ErrorDetail
{
    public string Field { get; set; }
    public string Issue { get; set; }
}
```

### Middleware de manejo global de errores

```csharp
public class GlobalExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;

    public GlobalExceptionMiddleware(RequestDelegate next, ILogger<GlobalExceptionMiddleware> logger)
    {
        _next = next;
        _logger = logger;
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
        var response = context.Response;
        response.ContentType = "application/json";

        var errorResponse = new ApiResponse<object>
        {
            Status = "error",
            Data = null,
            Errors = new List<ErrorInfo>(),
            Meta = new MetaData()
        };

        switch (exception)
        {
            case ValidationException validationEx:
                errorResponse.Errors.Add(new ErrorInfo
                {
                    Code = "VALIDATION_FAILED",
                    Message = "La solicitud contiene errores de validación",
                    Details = validationEx.Errors.SelectMany(kvp =>
                        kvp.Value.Select(error => new ErrorDetail
                        {
                            Field = kvp.Key,
                            Issue = error
                        })).ToList()
                });
                response.StatusCode = 400;
                break;

            case NotFoundException notFoundEx:
                errorResponse.Errors.Add(new ErrorInfo
                {
                    Code = "RESOURCE_NOT_FOUND",
                    Message = notFoundEx.Message,
                    Details = new List<ErrorDetail>()
                });
                response.StatusCode = 404;
                break;

            case UnauthorizedException unauthorizedEx:
                errorResponse.Errors.Add(new ErrorInfo
                {
                    Code = "UNAUTHORIZED_ACCESS",
                    Message = "Credenciales inválidas o sesión expirada",
                    Details = new List<ErrorDetail>()
                });
                response.StatusCode = 401;
                break;

            case ForbiddenException forbiddenEx:
                errorResponse.Errors.Add(new ErrorInfo
                {
                    Code = "FORBIDDEN_ACCESS",
                    Message = "No tienes permisos para realizar esta acción",
                    Details = new List<ErrorDetail>()
                });
                response.StatusCode = 403;
                break;

            case BusinessLogicException businessEx:
                errorResponse.Errors.Add(new ErrorInfo
                {
                    Code = businessEx.ErrorCode ?? "BUSINESS_LOGIC_ERROR",
                    Message = businessEx.Message,
                    Details = businessEx.Details ?? new List<ErrorDetail>()
                });
                response.StatusCode = 422;
                break;

            default:
                _logger.LogError(exception, "Error interno no controlado");
                errorResponse.Errors.Add(new ErrorInfo
                {
                    Code = "INTERNAL_SERVER_ERROR",
                    Message = "Ocurrió un error interno. Contacta al administrador.",
                    Details = new List<ErrorDetail>()
                });
                response.StatusCode = 500;
                break;
        }

        var json = JsonSerializer.Serialize(errorResponse, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        });

        await response.WriteAsync(json);
    }
}

// Excepciones personalizadas
public class BusinessLogicException : Exception
{
    public string ErrorCode { get; }
    public List<ErrorDetail> Details { get; }

    public BusinessLogicException(string errorCode, string message, List<ErrorDetail> details = null)
        : base(message)
    {
        ErrorCode = errorCode;
        Details = details ?? new List<ErrorDetail>();
    }
}

public class ValidationException : Exception
{
    public Dictionary<string, string[]> Errors { get; }

    public ValidationException(Dictionary<string, string[]> errors)
        : base("Errores de validación")
    {
        Errors = errors;
    }
}
```

### Controller con manejo de errores y FluentValidation

```csharp
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly IValidator<CreateUserRequest> _validator;

    public UsersController(IUserService userService, IValidator<CreateUserRequest> validator)
    {
        _userService = userService;
        _validator = validator;
    }

    [HttpPost]
    [ProducesResponseType(typeof(ApiResponse<UserDto>), 201)]
    [ProducesResponseType(typeof(ApiResponse<object>), 400)]
    [ProducesResponseType(typeof(ApiResponse<object>), 422)]
    public async Task<ActionResult<ApiResponse<UserDto>>> CreateUser(
        [FromBody] CreateUserRequest request)
    {
        // Validación con FluentValidation
        var validationResult = await _validator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            var errorResponse = new ApiResponse<object>
            {
                Status = "error",
                Data = null,
                Errors = new List<ErrorInfo>
                {
                    new ErrorInfo
                    {
                        Code = "VALIDATION_FAILED",
                        Message = "La solicitud contiene errores de validación",
                        Details = validationResult.Errors.Select(error => new ErrorDetail
                        {
                            Field = error.PropertyName,
                            Issue = error.ErrorMessage
                        }).ToList()
                    }
                },
                Meta = new MetaData()
            };

            return BadRequest(errorResponse);
        }

        var result = await _userService.CreateUserAsync(request);
        if (!result.IsSuccess)
        {
            var businessErrorResponse = new ApiResponse<object>
            {
                Status = "error",
                Data = null,
                Errors = new List<ErrorInfo>
                {
                    new ErrorInfo
                    {
                        Code = result.ErrorCode,
                        Message = result.Error,
                        Details = new List<ErrorDetail>()
                    }
                },
                Meta = new MetaData()
            };

            return UnprocessableEntity(businessErrorResponse);
        }

        var successResponse = new ApiResponse<UserDto>
        {
            Status = "success",
            Data = _mapper.Map<UserDto>(result.Value),
            Errors = new List<ErrorInfo>(),
            Meta = new MetaData()
        };

        return CreatedAtAction(nameof(GetUser),
            new { id = result.Value.Id }, successResponse);
    }

    [HttpGet("{id}")]
    [ProducesResponseType(typeof(ApiResponse<UserDto>), 200)]
    [ProducesResponseType(typeof(ApiResponse<object>), 404)]
    public async Task<ActionResult<ApiResponse<UserDto>>> GetUser(string id)
    {
        var user = await _userService.GetUserByIdAsync(id);
        if (user == null)
        {
            var errorResponse = new ApiResponse<object>
            {
                Status = "error",
                Data = null,
                Errors = new List<ErrorInfo>
                {
                    new ErrorInfo
                    {
                        Code = "USER_NOT_FOUND",
                        Message = "El usuario no existe",
                        Details = new List<ErrorDetail>
                        {
                            new() { Field = "id", Issue = $"No se encontró ningún usuario con el identificador '{id}'" }
                        }
                    }
                },
                Meta = new MetaData()
            };

            return NotFound(errorResponse);
        }

        var response = new ApiResponse<UserDto>
        {
            Status = "success",
            Data = _mapper.Map<UserDto>(user),
            Errors = new List<ErrorInfo>(),
            Meta = new MetaData()
        };

        return Ok(response);
    }
}
```

## 🔧 Configuración en Program.cs

### Configuración con FluentValidation (Recomendado)

```csharp
var builder = WebApplication.CreateBuilder(args);

// Configurar controladores
builder.Services.AddControllers();

// Configurar FluentValidation
builder.Services.AddFluentValidationAutoValidation(config =>
{
    // Deshabilitar validación automática de DataAnnotations
    config.DisableDataAnnotationsValidation = true;
});

builder.Services.AddFluentValidationClientsideAdapters();
builder.Services.AddValidatorsFromAssemblyContaining<CreateUserRequestValidator>();

// Configurar comportamiento de APIs
builder.Services.Configure<ApiBehaviorOptions>(options =>
{
    // Deshabilitar respuesta automática de ModelState para manejarla manualmente
    options.SuppressModelStateInvalidFilter = true;
});

// Configurar JSON
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    options.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});

// Otros servicios
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddAutoMapper(typeof(Program));

var app = builder.Build();

// Middleware de manejo global de errores (debe ir primero)
app.UseMiddleware<GlobalExceptionMiddleware>();

// Otros middlewares...
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.Run();
```

### Configuración alternativa con Data Annotations

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

// Configurar validación
builder.Services.Configure<ApiBehaviorOptions>(options =>
{
    // Personalizar respuesta de validación automática
    options.InvalidModelStateResponseFactory = context =>
    {
        var errors = context.ModelState
            .Where(x => x.Value.Errors.Count > 0)
            .SelectMany(x => x.Value.Errors.Select(e => new ErrorDetail
            {
                Field = x.Key,
                Issue = e.ErrorMessage
            }))
            .ToList();

        var errorResponse = new ApiResponse<object>
        {
            Status = "error",
            Error = new ErrorInfo
            {
                Code = "VALIDATION_FAILED",
                Message = "La solicitud contiene errores de validación",
                Details = errors
            },
            Meta = new MetaData(),
            TraceId = Activity.Current?.Id ?? context.HttpContext.TraceIdentifier
        };

        return new BadRequestObjectResult(errorResponse);
    };
});

var app = builder.Build();

// Middleware de manejo global de errores
app.UseMiddleware<GlobalExceptionMiddleware>();

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

## ✅ Ejemplos de Respuestas

> **Nota**: Los ejemplos completos están en [Convenciones - Formato de Respuestas](/docs/fundamentos-corporativos/convenciones/apis/formato-respuestas).

### Error de validación (400)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_FAILED",
      "message": "La solicitud contiene errores de validación",
      "details": [
        {
          "field": "name",
          "issue": "El nombre es obligatorio"
        },
        {
          "field": "email",
          "issue": "El formato del email no es válido"
        },
        {
          "field": "email",
          "issue": "Solo se permiten emails de dominios: talma.pe, talma.com"
        },
        {
          "field": "age",
          "issue": "La edad debe estar entre 18 y 120 años"
        }
      ]
    }
  ],
  "meta": {
    "traceId": "c1d2e3f4-5678-90ab-cdef-1234567890ab",
    "timestamp": "2025-09-22T10:30:00Z"
  }
}
```

### Error de lógica de negocio (422)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "EMAIL_EXISTS",
      "message": "Ya existe un usuario con este email",
      "details": []
    }
  ],
  "meta": {
    "traceId": "de9f8c7b-6543-21fe-cdba-123456789abc",
    "timestamp": "2025-09-22T10:30:00Z"
  }
}
```

### Error de autorización (403)

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "FORBIDDEN_ACCESS",
      "message": "No tienes permisos para realizar esta acción",
      "details": []
    }
  ],
  "meta": {
    "traceId": "12ab34cd-5678-90ef-gh12-34567890abcd",
    "timestamp": "2025-09-22T10:30:00Z"
  }
}
```

### Respuesta exitosa para referencia

```json
{
  "status": "success",
  "data": {
    "id": "usr_123",
    "name": "Juan Pérez",
    "email": "juan.perez@talma.pe",
    "active": true,
    "createdAt": "2025-09-22T10:30:00Z"
  },
  "errors": [],
  "meta": {
    "traceId": "abc123-def456-789012",
    "timestamp": "2025-09-22T10:30:01Z"
  }
}
```

```

## 7. Antipatrones (NO Hacer)

### ❌ Antipatrón 1: Retornar 200 OK con error en el body

```csharp
// ❌ MAL - Retornar 200 OK con status="error" en body
[HttpPost]
public async Task<IActionResult> CreateUser(CreateUserRequest request)
{
    if (string.IsNullOrEmpty(request.Email))
    {
        return Ok(new { status = "error", message = "Email requerido" }); // ❌ 200 OK
    }
    // ...
}

// ✅ BIEN - Usar códigos HTTP correctos
[HttpPost]
public async Task<IActionResult> CreateUser(CreateUserRequest request)
{
    var validationResult = await _validator.ValidateAsync(request);
    if (!validationResult.IsValid)
    {
        return BadRequest(new ApiResponse<object> // ✅ 400 Bad Request
        {
            Status = "error",
            Errors = MapValidationErrors(validationResult.Errors)
        });
    }
    // ...
}
```

**Problema**: Clientes HTTP no pueden distinguir errores de éxitos (status code = 200).  
**Solución**: Usar códigos HTTP apropiados (400, 404, 422, 500) según el tipo de error.

### ❌ Antipatrón 2: No Validar Entrada (Confiar en el Cliente)

```csharp
// ❌ MAL - No validar entrada
[HttpPost]
public async Task<IActionResult> CreateUser(CreateUserRequest request)
{
    var user = await _userService.CreateAsync(request); // ❌ Sin validación
    return Ok(user);
}

// ✅ BIEN - Validar con FluentValidation
[HttpPost]
public async Task<IActionResult> CreateUser(CreateUserRequest request)
{
    var validationResult = await _validator.ValidateAsync(request);
    if (!validationResult.IsValid)
    {
        return BadRequest(MapValidationErrors(validationResult));
    }
    
    var user = await _userService.CreateAsync(request);
    return Ok(user);
}
```

**Problema**: Datos inválidos llegan a la BD (SQL injection, XSS, data corruption).  
**Solución**: Siempre validar entrada con FluentValidation o Data Annotations.

### ❌ Antipatrón 3: Mensajes de Error Genéricos

```csharp
// ❌ MAL - Mensaje genérico sin detalles
catch (Exception ex)
{
    return StatusCode(500, new { error = "Error" }); // ❌ No útil
}

// ✅ BIEN - Mensajes específicos con traceId
catch (Exception ex)
{
    _logger.LogError(ex, "Error creando usuario: {Email}", request.Email);
    
    return StatusCode(500, new ApiResponse<object>
    {
        Status = "error",
        Errors = new List<ErrorInfo>
        {
            new()
            {
                Code = "INTERNAL_SERVER_ERROR",
                Message = "Error interno. Contacta soporte con el traceId.",
                Details = new()
            }
        },
        Meta = new() { TraceId = HttpContext.TraceIdentifier }
    });
}
```

**Problema**: Usuarios no saben qué falló, soporte no puede debuggear.  
**Solución**: Mensajes claros + traceId + logging estructurado.

### ❌ Antipatrón 4: Exponer Stack Traces en Producción

```csharp
// ❌ MAL - Exponer stack trace al cliente
catch (Exception ex)
{
    return StatusCode(500, new 
    { 
        error = ex.Message,
        stackTrace = ex.StackTrace // ❌ Información sensible
    });
}

// ✅ BIEN - Solo en Development, no en Production
catch (Exception ex)
{
    _logger.LogError(ex, "Error interno");
    
    var errorResponse = new ApiResponse<object>
    {
        Status = "error",
        Errors = new List<ErrorInfo>
        {
            new()
            {
                Code = "INTERNAL_SERVER_ERROR",
                Message = _env.IsDevelopment() 
                    ? ex.Message // Solo en dev
                    : "Error interno del servidor",
                Details = new()
            }
        }
    };
    
    return StatusCode(500, errorResponse);
}
```

**Problema**: Stack traces revelan estructura de código, rutas, versiones (vulnerabilidad de seguridad).  
**Solución**: Solo mostrar stack trace en Development, mensajes genéricos en Production.

## 8. Validación y Cumplimiento

### 8.1 Checklist de Implementación

- [ ] **FluentValidation 11+** configurado
- [ ] **Validators** para todos los DTOs de entrada
- [ ] **Middleware global** de excepciones implementado
- [ ] **RFC 7807 Problem Details** (o estructura envelope consistente)
- [ ] **Códigos HTTP correctos** (400, 404, 422, 500)
- [ ] **Logging estructurado** de errores con traceId
- [ ] **Excepciones personalizadas** (ValidationException, NotFoundException, etc.)
- [ ] **Mensajes de error claros** con campo/issue detallado
- [ ] **No exponer stack traces** en producción
- [ ] **Validación de negocio** separada de validación de input

### 8.2 Métricas de Cumplimiento

| Métrica                              | Target | Verificación                          |
| ------------------------------------ | ------ | ------------------------------------- |
| DTOs con validadores                 | 100%   | Cada Request DTO tiene Validator      |
| Uso de códigos HTTP correctos        | 95%+   | Code review, auditoría de responses   |
| Errores loggeados con traceId        | 100%   | Logs en Application Insights          |
| Endpoints con manejo de errores      | 100%   | Middleware global activo              |
| Respuestas con estructura consistente| 100%   | `ApiResponse<T>` en todos los endpoints |

## 9. Referencias

### Estándares Relacionados

- [Diseño REST](./01-diseno-rest.md) - Implementación técnica de APIs
- [Seguridad APIs](./02-seguridad-apis.md) - Validación de seguridad

### Convenciones Relacionadas

- [Formato Respuestas](../../convenciones/apis/03-formato-respuestas.md) - Estructura JSON y códigos HTTP

### Lineamientos Relacionados

- [Desarrollo de APIs](../../lineamientos/desarrollo/desarrollo-de-apis.md) - Lineamientos de APIs
- [Observabilidad](../../lineamientos/arquitectura/05-observabilidad.md) - Logging y tracing

### Principios Relacionados

- [Calidad desde el Diseño](../../principios/arquitectura/08-calidad-desde-el-diseno.md) - Fundamento de validación
- [Simplicidad Intencional](../../principios/arquitectura/07-simplicidad-intencional.md) - Mensajes claros

### ADRs Relacionados

- [ADR-002: Estándar para APIs REST](../../../decisiones-de-arquitectura/adr-002-estandard-apis-rest.md)
- [ADR-016: Logging Estructurado](../../../decisiones-de-arquitectura/adr-016-logging-estructurado.md)

### Documentación Externa

- [FluentValidation Documentation](https://docs.fluentvalidation.net/) - Librería de validación
- [RFC 7807 - Problem Details](https://www.rfc-editor.org/rfc/rfc7807) - Formato estándar de errores
- [ASP.NET Core Model Validation](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation) - Microsoft Docs
- [Hellang.Middleware.ProblemDetails](https://github.com/khellang/Middleware) - Middleware RFC 7807

---

**Última actualización**: 27 de enero 2026  
**Responsable**: Equipo de Arquitectura
