---
id: validacion-y-errores
sidebar_position: 3
title: Validación y manejo de errores
description: Mejores prácticas para validación de entrada y manejo consistente de errores en APIs REST
---

# Validación y manejo de errores

Esta guía define las mejores prácticas para validación de entrada y manejo consistente de errores en APIs REST.

## 🔍 Validación de entrada

### Principios de validación

- **Validar todo**: Nunca confíes en los datos de entrada
- **Fallar rápido**: Validar antes de procesar lógica de negocio
- **Mensajes claros**: Proporcionar feedback útil al cliente
- **Consistencia**: Usar estructura estándar de respuesta para todos los errores

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

### Estructura estándar de respuesta de error

Siguiendo el estándar definido en los lineamientos de desarrollo de APIs:

```csharp
public class ApiResponse<T>
{
    public string Status { get; set; } = "success";
    public T Data { get; set; }
    public ErrorInfo Error { get; set; }
    public MetaData Meta { get; set; } = new();
    public Dictionary<string, string> Links { get; set; }
}

public class MetaData
{
    public string TraceId { get; set; }
    public DateTime Timestamp { get; set; }
    // Otros campos de meta si aplica
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

public class MetaData
{
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public List<WarningInfo> Warnings { get; set; } = new();
}

public class WarningInfo
{
    public string Code { get; set; }
    public string Message { get; set; }
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
            Meta = new MetaData(),
            TraceId = Activity.Current?.Id ?? context.TraceIdentifier
        };
                "field": "name",
                "field": "userName",
        switch (exception)
        {
            case ValidationException validationEx:
            "name": "Juan Pérez",
            "userName": "jperez",
                {
                    Code = "VALIDATION_FAILED",
                    Message = "La solicitud contiene errores de validación",
                    Details = validationEx.Errors.SelectMany(kvp =>
                        kvp.Value.Select(error => new ErrorDetail
                        {
                            Field = kvp.Key,
                            Issue = error
                        })).ToList()
                };
                response.StatusCode = 400;
                break;

            case NotFoundException notFoundEx:
                errorResponse.Error = new ErrorInfo
                {
                    Code = "RESOURCE_NOT_FOUND",
                    Message = notFoundEx.Message,
                    Details = new List<ErrorDetail>()
                };
                response.StatusCode = 404;
                break;

            case UnauthorizedException unauthorizedEx:
                errorResponse.Error = new ErrorInfo
                {
                    Code = "UNAUTHORIZED_ACCESS",
                    Message = "Credenciales inválidas o sesión expirada",
                    Details = new List<ErrorDetail>()
                };
                response.StatusCode = 401;
                break;

            case ForbiddenException forbiddenEx:
                errorResponse.Error = new ErrorInfo
                {
                    Code = "FORBIDDEN_ACCESS",
                    Message = "No tienes permisos para realizar esta acción",
                    Details = new List<ErrorDetail>()
                };
                response.StatusCode = 403;
                break;

            case BusinessLogicException businessEx:
                errorResponse.Error = new ErrorInfo
                {
                    Code = businessEx.ErrorCode ?? "BUSINESS_LOGIC_ERROR",
                    Message = businessEx.Message,
                    Details = businessEx.Details ?? new List<ErrorDetail>()
                };
                response.StatusCode = 422;
                break;

            default:
                _logger.LogError(exception, "Error interno no controlado");
                errorResponse.Error = new ErrorInfo
                {
                    Code = "INTERNAL_SERVER_ERROR",
                    Message = "Ocurrió un error interno. Contacta al administrador.",
                    Details = new List<ErrorDetail>()
                };
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
                Error = new ErrorInfo
                {
                    Code = "VALIDATION_FAILED",
                    Message = "La solicitud contiene errores de validación",
                    Details = validationResult.Errors.Select(error => new ErrorDetail
                    {
                        Field = error.PropertyName,
                        Issue = error.ErrorMessage
                    }).ToList()
                },
                Meta = new MetaData(),
                TraceId = Activity.Current?.Id ?? HttpContext.TraceIdentifier
            };

            return BadRequest(errorResponse);
        }

        var result = await _userService.CreateUserAsync(request);
        if (!result.IsSuccess)
        {
            var businessErrorResponse = new ApiResponse<object>
            {
                Status = "error",
                Error = new ErrorInfo
                {
                    Code = result.ErrorCode,
                    Message = result.Error,
                    Details = new List<ErrorDetail>()
                },
                Meta = new MetaData(),
                TraceId = Activity.Current?.Id ?? HttpContext.TraceIdentifier
            };

            return UnprocessableEntity(businessErrorResponse);
        }

        var successResponse = new ApiResponse<UserDto>
        {
            Status = "success",
            Data = _mapper.Map<UserDto>(result.Value),
            Meta = new MetaData(),
            TraceId = Activity.Current?.Id ?? HttpContext.TraceIdentifier
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
                Error = new ErrorInfo
                {
                    Code = "USER_NOT_FOUND",
                    Message = "El usuario no existe",
                    Details = new List<ErrorDetail>
                    {
                        new() { Field = "id", Issue = $"No se encontró ningún usuario con el identificador '{id}'" }
                    }
                },
                Meta = new MetaData(),
                TraceId = Activity.Current?.Id ?? HttpContext.TraceIdentifier
            };

            return NotFound(errorResponse);
        }

        var response = new ApiResponse<UserDto>
        {
            Status = "success",
            Data = _mapper.Map<UserDto>(user),
            Meta = new MetaData(),
            TraceId = Activity.Current?.Id ?? HttpContext.TraceIdentifier
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

## ✅ Ejemplos de respuestas

### Error de validación (400)

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "La solicitud contiene errores de validación",
    "details": [
      {
        "field": "userName",
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
  },
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
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Ya existe un usuario con este email",
    "details": []
  },
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
  "error": {
    "code": "FORBIDDEN_ACCESS",
    "message": "No tienes permisos para realizar esta acción",
    "details": []
  },
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
    "userName": "Juan Pérez",
    "email": "juan.perez@talma.pe",
    "active": true,
    "createdAt": "2025-09-22T10:30:00Z"
  },
  "meta": {
    "traceId": "abc123-def456-789012",
    "timestamp": "2025-09-22T10:30:01Z"
  }
}
```

## 📖 Referencias

### ADRs relacionados

- [ADR-002: Estándar para APIs REST](/docs/adrs/adr-002-estandard-apis-rest)
- [ADR-016: Logging estructurado](/docs/adrs/adr-016-logging-estructurado)

### Recursos externos

- [FluentValidation Documentation](https://docs.fluentvalidation.net/)
- [ASP.NET Core Model Validation](https://docs.microsoft.com/en-us/aspnet/core/mvc/models/validation)
- [System.Text.Json Documentation](https://docs.microsoft.com/en-us/dotnet/standard/serialization/system-text-json-overview)
