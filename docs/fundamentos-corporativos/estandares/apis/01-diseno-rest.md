---
id: diseno-rest
sidebar_position: 1
title: Diseño REST
description: Estándar para diseño de APIs REST con ASP.NET Core, versionado, autenticación y documentación OpenAPI
---

# Estándar: Diseño REST

## 1. Propósito

Definir la implementación técnica de APIs REST en Talma usando **ASP.NET Core 8.0+**, incluyendo configuración de versionado, autenticación JWT, serialización JSON, validación y documentación OpenAPI.

> **Nota**: Este estándar define **CÓMO implementar** APIs técnicamente. Para nomenclatura de endpoints, consulta [Convenciones - Naming Endpoints](../../convenciones/apis/01-naming-endpoints.md).

## 2. Alcance

### Aplica a

- ✅ Todas las APIs REST públicas y privadas
- ✅ APIs de integración con sistemas externos
- ✅ Microservicios que exponen HTTP endpoints
- ✅ Backend-for-Frontend (BFF) APIs

### NO aplica a

- ❌ APIs GraphQL (estándar separado)
- ❌ gRPC services (estándar separado)
- ❌ WebSockets (protocolo diferente)

## 3. Tecnologías Obligatorias

### Stack Principal

| Tecnología                                 | Versión Mínima | Propósito                       |
| ------------------------------------------ | -------------- | ------------------------------- |
| **ASP.NET Core**                           | 8.0+           | Framework base de API           |
| **Microsoft.AspNetCore.Mvc.Versioning**    | 5.0+           | Versionado de APIs              |
| **Swashbuckle.AspNetCore**                 | 6.5+           | Documentación OpenAPI/Swagger   |
| **FluentValidation.AspNetCore**            | 11.0+          | Validación de entrada           |
| **AutoMapper**                             | 12.0+          | Mapeo de DTOs                   |
| **Microsoft.AspNetCore.Authentication.Jwt** | 8.0+           | Autenticación JWT               |
| **Serilog.AspNetCore**                     | 8.0+           | Logging estructurado            |

### Versiones de Protocolo

- **HTTPS/TLS**: 1.3 mínimo
- **HTTP**: 2.0 preferido, 1.1 compatible
- **JSON**: Serialización estándar para request/response

## 4. Configuración Técnica Obligatoria

### 4.1 Configuración de Proyecto (Program.cs)

```csharp
// Program.cs - ASP.NET Core 8.0+
var builder = WebApplication.CreateBuilder(args);

// ✅ 1. Configuración de Controllers
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        // camelCase para JSON
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    });

// ✅ 2. Versionado de API
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true; // Header: api-supported-versions
    options.ApiVersionReader = new UrlSegmentApiVersionReader();
});

// ✅ 3. API Explorer para Swagger
builder.Services.AddVersionedApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV";
    options.SubstituteApiVersionInUrl = true;
});

// ✅ 4. AutoMapper
builder.Services.AddAutoMapper(typeof(Program));

// ✅ 5. FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<Program>();
builder.Services.AddFluentValidationAutoValidation();

// ✅ 6. HTTPS Redirection
builder.Services.AddHttpsRedirection(options =>
{
    options.RedirectStatusCode = StatusCodes.Status308PermanentRedirect;
    options.HttpsPort = 443;
});

var app = builder.Build();

// ✅ Middleware Pipeline
app.UseHttpsRedirection();       // HTTPS obligatorio
app.UseAuthentication();         // JWT
app.UseAuthorization();          // Autorización basada en claims
app.MapControllers();
app.Run();
```

### 4.2 Autenticación JWT (RS256)

```csharp
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Jwt:Authority"];
        options.Audience = builder.Configuration["Jwt:Audience"];
        
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 }, // ✅ RS256 obligatorio
            ClockSkew = TimeSpan.FromMinutes(5)
        };

        options.Events = new JwtBearerEvents
        {
            OnAuthenticationFailed = context =>
            {
                context.Response.Headers.Append("X-Auth-Error", context.Exception.Message);
                return Task.CompletedTask;
            }
        };
    });
```

### 4.3 Documentación OpenAPI (Swagger)

```csharp
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Talma API",
        Version = "v1",
        Description = "API REST para operaciones de Talma",
        Contact = new OpenApiContact
        {
            Name = "Equipo de Arquitectura",
            Email = "arquitectura@talma.com"
        }
    });

    // ✅ JWT Bearer Authentication
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header usando Bearer scheme. Ejemplo: 'Bearer {token}'",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.Http,
        Scheme = "bearer",
        BearerFormat = "JWT"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });

    // ✅ XML Comments
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);
});
```

### 4.4 CORS (Cross-Origin Resource Sharing)

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("TalmaPolicy", policy =>
    {
        policy.WithOrigins(
            "https://portal.talma.com",
            "https://app.talma.com"
        )
        .AllowAnyMethod()
        .AllowAnyHeader()
        .AllowCredentials();
    });
});

app.UseCors("TalmaPolicy");
```

## 5. Ejemplos de Implementación

### 5.1 Controller con Versionado

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace Talma.Api.Controllers;

[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/[controller]")]
[Authorize]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly IMapper _mapper;
    private readonly ILogger<UsersController> _logger;

    public UsersController(
        IUserService userService,
        IMapper mapper,
        ILogger<UsersController> logger)
    {
        _userService = userService;
        _mapper = mapper;
        _logger = logger;
    }

    /// <summary>
    /// Obtiene un usuario por ID
    /// </summary>
    /// <param name="id">ID del usuario</param>
    /// <returns>Usuario encontrado</returns>
    /// <response code="200">Usuario encontrado</response>
    /// <response code="404">Usuario no encontrado</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<UserResponse>> GetUser(Guid id)
    {
        var user = await _userService.GetByIdAsync(id);
        
        if (user == null)
        {
            return NotFound(new ProblemDetails
            {
                Status = StatusCodes.Status404NotFound,
                Title = "Usuario no encontrado",
                Detail = $"No existe usuario con ID {id}"
            });
        }

        var response = _mapper.Map<UserResponse>(user);
        return Ok(response);
    }

    /// <summary>
    /// Crea un nuevo usuario
    /// </summary>
    /// <param name="request">Datos del usuario</param>
    /// <returns>Usuario creado</returns>
    [HttpPost]
    [ProducesResponseType(typeof(UserResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<UserResponse>> CreateUser(
        [FromBody] CreateUserRequest request)
    {
        var user = await _userService.CreateAsync(request);
        var response = _mapper.Map<UserResponse>(user);

        return CreatedAtAction(
            nameof(GetUser),
            new { id = response.Id },
            response
        );
    }
}
```

### 5.2 DTOs con Validación FluentValidation

```csharp
// Request DTO
public record CreateUserRequest
{
    public string UserName { get; init; } = string.Empty;
    public string Email { get; init; } = string.Empty;
    public string FirstName { get; init; } = string.Empty;
    public string LastName { get; init; } = string.Empty;
}

// Validator
public class CreateUserRequestValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserRequestValidator()
    {
        RuleFor(x => x.UserName)
            .NotEmpty().WithMessage("UserName es requerido")
            .Length(3, 50).WithMessage("UserName debe tener entre 3 y 50 caracteres")
            .Matches("^[a-zA-Z0-9_-]+$").WithMessage("UserName solo acepta letras, números, guiones y guion bajo");

        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email es requerido")
            .EmailAddress().WithMessage("Email no válido");

        RuleFor(x => x.FirstName)
            .NotEmpty().WithMessage("FirstName es requerido")
            .MaximumLength(100);

        RuleFor(x => x.LastName)
            .NotEmpty().WithMessage("LastName es requerido")
            .MaximumLength(100);
    }
}
```

### 5.3 Manejo de Códigos HTTP

```csharp
// ✅ 200 OK - Operación exitosa con datos
[HttpGet]
public async Task<ActionResult<IEnumerable<UserResponse>>> GetUsers()
{
    var users = await _userService.GetAllAsync();
    return Ok(users);
}

// ✅ 201 Created - Recurso creado
[HttpPost]
public async Task<ActionResult<UserResponse>> CreateUser(CreateUserRequest request)
{
    var user = await _userService.CreateAsync(request);
    return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
}

// ✅ 204 No Content - Eliminación exitosa
[HttpDelete("{id}")]
public async Task<IActionResult> DeleteUser(Guid id)
{
    await _userService.DeleteAsync(id);
    return NoContent();
}

// ✅ 404 Not Found - Recurso no encontrado
[HttpGet("{id}")]
public async Task<ActionResult<UserResponse>> GetUser(Guid id)
{
    var user = await _userService.GetByIdAsync(id);
    return user == null ? NotFound() : Ok(user);
}

// ✅ 400 Bad Request - Validación fallida (automático con FluentValidation)
// ✅ 401 Unauthorized - Sin autenticación (automático con [Authorize])
// ✅ 403 Forbidden - Sin permisos
[HttpPost("admin")]
[Authorize(Roles = "Admin")]
public async Task<IActionResult> AdminAction()
{
    // Retorna 403 si no tiene rol Admin
    return Ok();
}
```

## 6. Mejores Prácticas

### 6.1 Principios REST

1. **Recursos como sustantivos** - Usar sustantivos (no verbos) en endpoints
2. **Stateless** - Cada request debe ser autónomo (no depender de estado previo)
3. **Cacheable** - Usar headers de cache apropiados (`Cache-Control`, `ETag`)
4. **Uniform Interface** - Estructura consistente en todos los endpoints

### 6.2 Seguridad

```csharp
// ✅ HTTPS Obligatorio
app.UseHttpsRedirection();

// ✅ Autenticación JWT
app.UseAuthentication();

// ✅ Autorización basada en Claims
[Authorize(Policy = "TenantAccess")]
public class OrdersController : ControllerBase { }

// ✅ Rate Limiting (ASP.NET Core 8.0+)
builder.Services.AddRateLimiter(options =>
{
    options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
        RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: context.User.Identity?.Name ?? context.Request.Headers.Host.ToString(),
            factory: _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 100,
                Window = TimeSpan.FromMinutes(1)
            }));
});
```

### 6.3 Observabilidad

```csharp
// ✅ Logging estructurado con Correlation ID
builder.Services.AddSingleton<IHttpContextAccessor, HttpContextAccessor>();

app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-ID"].FirstOrDefault()
        ?? Guid.NewGuid().ToString();
    
    context.Items["CorrelationId"] = correlationId;
    context.Response.Headers.Append("X-Correlation-ID", correlationId);
    
    await next();
});

// ✅ Logging en Controller
_logger.LogInformation(
    "Usuario {UserId} obtenido. CorrelationId: {CorrelationId}",
    id,
    HttpContext.Items["CorrelationId"]
);
```

### 6.4 Performance

```csharp
// ✅ Paginación obligatoria para colecciones grandes
[HttpGet]
public async Task<ActionResult<PagedResponse<UserResponse>>> GetUsers(
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 20)
{
    if (pageSize > 100)
        return BadRequest("PageSize máximo es 100");

    var users = await _userService.GetPagedAsync(page, pageSize);
    return Ok(users);
}

// ✅ Response Compression
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<GzipCompressionProvider>();
    options.Providers.Add<BrotliCompressionProvider>();
});

// ✅ Caching con ETag
[HttpGet("{id}")]
public async Task<ActionResult<UserResponse>> GetUser(Guid id)
{
    var user = await _userService.GetByIdAsync(id);
    var etag = $"\"{user.UpdatedAt.Ticks}\"";
    
    if (Request.Headers["If-None-Match"] == etag)
        return StatusCode(StatusCodes.Status304NotModified);
    
    Response.Headers.Append("ETag", etag);
    return Ok(user);
}
```

## 7. Antipatrones (NO Hacer)

### ❌ Antipatrón 1: Verbos en endpoints

```csharp
// ❌ MAL - Usar verbos en URL
[HttpGet("getUserById/{id}")]
[HttpPost("createUser")]
[HttpPost("deleteUser/{id}")]

// ✅ BIEN - Usar recursos + HTTP methods
[HttpGet("{id}")]           // GET /api/v1/users/123
[HttpPost("")]              // POST /api/v1/users
[HttpDelete("{id}")]        // DELETE /api/v1/users/123
```

**Problema**: Viola principios REST, URLs no son predecibles.  
**Solución**: Usar HTTP methods correctos con recursos sustantivos.

### ❌ Antipatrón 2: Retornar 200 OK para errores

```csharp
// ❌ MAL - Siempre retornar 200 con status en body
return Ok(new { status = "error", message = "Usuario no encontrado" });

// ✅ BIEN - Usar códigos HTTP correctos
return NotFound(new ProblemDetails
{
    Status = StatusCodes.Status404NotFound,
    Title = "Usuario no encontrado"
});
```

**Problema**: Clientes HTTP no pueden manejar errores correctamente.  
**Solución**: Usar códigos HTTP apropiados (4xx para errores de cliente, 5xx para servidor).

### ❌ Antipatrón 3: Autenticación casera (custom tokens)

```csharp
// ❌ MAL - Token custom en header X-Auth-Token
if (Request.Headers["X-Auth-Token"] != "mi-token-secreto")
    return Unauthorized();

// ✅ BIEN - JWT estándar con RS256
[Authorize] // Usa JWT automáticamente
public class UsersController : ControllerBase { }
```

**Problema**: Tokens inseguros, no estándar, difíciles de renovar.  
**Solución**: Usar JWT con RS256, integración con Identity Provider (Okta, Auth0, Azure AD).

### ❌ Antipatrón 4: Devolución de entidades de dominio directamente

```csharp
// ❌ MAL - Retornar entidad de dominio con todos los campos internos
[HttpGet("{id}")]
public async Task<User> GetUser(Guid id)
{
    return await _dbContext.Users.FindAsync(id); // Expone Password, InternalId, etc.
}

// ✅ BIEN - Usar DTOs con AutoMapper
[HttpGet("{id}")]
public async Task<ActionResult<UserResponse>> GetUser(Guid id)
{
    var user = await _userService.GetByIdAsync(id);
    var response = _mapper.Map<UserResponse>(user); // Solo campos públicos
    return Ok(response);
}
```

**Problema**: Exposición de datos sensibles, acoplamiento con modelo de dominio.  
**Solución**: Siempre usar DTOs (Data Transfer Objects) para request/response.

## 8. Validación y Cumplimiento

### 8.1 Checklist de Implementación

- [ ] **ASP.NET Core 8.0+** configurado con `Program.cs` mínimo
- [ ] **Versionado de API** habilitado con `ApiVersioning`
- [ ] **Autenticación JWT** con RS256
- [ ] **HTTPS/TLS 1.3** obligatorio en producción
- [ ] **FluentValidation** configurado para todos los DTOs
- [ ] **Swagger/OpenAPI** generado automáticamente
- [ ] **AutoMapper** configurado para DTOs
- [ ] **Logging estructurado** con Serilog y correlation IDs
- [ ] **Rate Limiting** configurado (100 req/min por usuario)
- [ ] **Response Compression** habilitado (Gzip/Brotli)
- [ ] **CORS** configurado solo para orígenes permitidos
- [ ] **XML Comments** habilitados para documentación
- [ ] **Códigos HTTP** correctos (200, 201, 204, 400, 401, 403, 404, 500)
- [ ] **DTOs** separados de entidades de dominio

### 8.2 Validación Automática en CI/CD

```yaml
# .github/workflows/api-validation.yml
- name: Validate API Standards
  run: |
    # Verificar que todas las APIs usan HTTPS
    grep -r "UseHttpsRedirection" src/ || exit 1
    
    # Verificar JWT RS256
    grep -r "RsaSha256" src/ || exit 1
    
    # Verificar FluentValidation
    grep -r "AddFluentValidationAutoValidation" src/ || exit 1
```

### 8.3 Métricas de Cumplimiento

| Métrica                                | Target | Verificación                               |
| -------------------------------------- | ------ | ------------------------------------------ |
| APIs con versionado                    | 100%   | Presencia de `ApiVersioning`               |
| Endpoints con autenticación            | 95%+   | `[Authorize]` en controllers               |
| DTOs con validación                    | 100%   | Validators para cada Request DTO           |
| Swagger documentation coverage         | 100%   | XML comments en todos los endpoints        |
| HTTPS en producción                    | 100%   | `UseHttpsRedirection` configurado          |
| Uso correcto de códigos HTTP           | 95%+   | Revisión de code reviews                   |
| Response time P95 < 500ms              | 95%+   | Monitoreo con Application Insights         |

## 9. Referencias

### Estándares Relacionados

- [Seguridad APIs](./02-seguridad-apis.md) - JWT, HTTPS, CORS
- [Validación y Errores](./03-validacion-y-errores.md) - FluentValidation, RFC 7807
- [Versionado](./04-versionado.md) - Estrategias de versionado
- [Performance](./05-performance.md) - Caching, compresión, paginación

### Convenciones Relacionadas

- [Naming Endpoints](../../convenciones/apis/01-naming-endpoints.md) - Nomenclatura de recursos y endpoints
- [Headers HTTP](../../convenciones/apis/02-headers-http.md) - Headers obligatorios (Correlation-ID, etc.)
- [Formato Respuestas](../../convenciones/apis/03-formato-respuestas.md) - Estructura JSON envelope
- [Formato Fechas y Moneda](../../convenciones/apis/04-formato-fechas-moneda.md) - ISO 8601, ISO 4217

### Lineamientos Relacionados

- [Desarrollo de APIs](../../lineamientos/desarrollo/desarrollo-de-apis.md) - Lineamientos generales
- [Observabilidad](../../lineamientos/arquitectura/05-observabilidad.md) - Logging y monitoreo

### Principios Relacionados

- [Contratos de Comunicación](../../principios/arquitectura/06-contratos-de-comunicacion.md) - Fundamento de APIs estables
- [Seguridad desde el Diseño](../../principios/seguridad/01-seguridad-desde-el-diseno.md) - Fundamento de seguridad
- [Observabilidad desde el Diseño](../../principios/arquitectura/05-observabilidad-desde-el-diseno.md) - Fundamento de trazabilidad

### ADRs Relacionados

- [ADR-002: Estándar para APIs REST](../../../decisiones-de-arquitectura/adr-002-estandard-apis-rest.md)
- [ADR-008: Gateway de APIs](../../../decisiones-de-arquitectura/adr-008-gateway-apis.md)
- [ADR-017: Versionado de APIs](../../../decisiones-de-arquitectura/adr-017-versionado-apis.md)

### Documentación Externa

- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [ASP.NET Core Web API](https://learn.microsoft.com/en-us/aspnet/core/web-api/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [RFC 7231 - HTTP/1.1 Semantics](https://www.rfc-editor.org/rfc/rfc7231)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

---

**Última actualización**: 26 de enero 2026  
**Responsable**: Equipo de Arquitectura
