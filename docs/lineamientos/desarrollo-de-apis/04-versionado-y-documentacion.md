---
title: "Versionado y documentación"
sidebar_position: 4
---

Esta guía define las estrategias de versionado y documentación de APIs para garantizar evolución compatible y mantenibilidad.

## 📊 Estrategias de versionado

### Versionado por URL (Recomendado)

```http
GET /api/v1/users
GET /api/v2/users
GET /api/v1.5/users  # Para versiones menores
```

**Ventajas:**

- Simplicidad y claridad
- Fácil routing y cache
- Compatible con proxies/CDNs

### Implementación con ASP.NET Core

```csharp
// Program.cs
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),
        new QueryStringApiVersionReader("version"),
        new HeaderApiVersionReader("X-Version")
    );
});

builder.Services.AddVersionedApiExplorer(setup =>
{
    setup.GroupNameFormat = "'v'VVV";
    setup.SubstituteApiVersionInUrl = true;
});

// Controller
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0")]
[ApiVersion("2.0")]
public class UsersController : ControllerBase
{
    [HttpGet]
    [MapToApiVersion("1.0")]
    public async Task<ActionResult<UserV1Dto[]>> GetUsersV1()
    {
        // Implementación v1
    }

    [HttpGet]
    [MapToApiVersion("2.0")]
    public async Task<ActionResult<UserV2Dto[]>> GetUsersV2()
    {
        // Implementación v2 con campos adicionales
    }
}
```

## 📋 Política de versionado

### Semantic Versioning adaptado para APIs

```text
MAJOR.MINOR.PATCH

MAJOR: Cambios incompatibles (breaking changes)
- Eliminar endpoints
- Cambiar estructura de respuesta existente
- Cambiar tipos de datos
- Cambiar semántica de operaciones

MINOR: Funcionalidad nueva compatible
- Nuevos endpoints
- Nuevos campos opcionales en respuestas
- Nuevos parámetros opcionales

PATCH: Correcciones de bugs
- Fixes de lógica de negocio
- Mejoras de performance
- Correcciones de documentación
```

### Compatibilidad hacia atrás

```csharp
// Estrategia: Mantener versiones anteriores funcionando
public class UserService
{
    public async Task<UserV1Dto> GetUserV1Async(int id)
    {
        var user = await _repository.GetUserAsync(id);

        // Mapear solo campos compatibles con v1
        return new UserV1Dto
        {
            Id = user.Id,
            Name = user.Name,
            Email = user.Email,
            Active = user.Active
        };
    }

    public async Task<UserV2Dto> GetUserV2Async(int id)
    {
        var user = await _repository.GetUserAsync(id);

        // Incluir nuevos campos en v2
        return new UserV2Dto
        {
            Id = user.Id,
            Name = user.Name,
            Email = user.Email,
            Active = user.Active,
            Department = user.Department,    // Nuevo en v2
            CreatedAt = user.CreatedAt,      // Nuevo en v2
            Permissions = user.Permissions   // Nuevo en v2
        };
    }
}
```

### Deprecación de versiones

```csharp
[ApiController]
[ApiVersion("1.0", Deprecated = true)]
[ApiVersion("2.0")]
public class UsersController : ControllerBase
{
    [HttpGet]
    [MapToApiVersion("1.0")]
    [ProducesResponseType(200)]
    public async Task<ActionResult<UserV1Dto[]>> GetUsersV1()
    {
        // Agregar header de deprecación
        Response.Headers.Add("Sunset", "2024-12-31T23:59:59Z");
        Response.Headers.Add("Deprecation", "true");
        Response.Headers.Add("Link", "</api/v2/users>; rel=\"successor-version\"");

        return await GetUsersV1Internal();
    }
}
```

## 📚 Documentación con OpenAPI/Swagger

### Configuración avanzada

```csharp
builder.Services.AddSwaggerGen(options =>
{
    // Configurar múltiples versiones
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Version = "v1.0",
        Title = "Talma API v1",
        Description = "API REST para gestión de usuarios y recursos - Versión 1",
        Contact = new OpenApiContact
        {
            Name = "Equipo de Desarrollo",
            Email = "desarrollo@talma.pe",
            Url = new Uri("https://talma.pe/support")
        },
        License = new OpenApiLicense
        {
            Name = "Uso interno Talma",
            Url = new Uri("https://talma.pe/license")
        }
    });

    options.SwaggerDoc("v2", new OpenApiInfo
    {
        Version = "v2.0",
        Title = "Talma API v2",
        Description = "API REST para gestión de usuarios y recursos - Versión 2"
    });

    // Incluir comentarios XML
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);

    // Configurar autenticación
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header usando el esquema Bearer",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
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
            new string[] {}
        }
    });

    // Filtros personalizados
    options.DocumentFilter<SecurityRequirementsDocumentFilter>();
    options.OperationFilter<SwaggerDefaultValues>();
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "Talma API v1");
        options.SwaggerEndpoint("/swagger/v2/swagger.json", "Talma API v2");
        options.RoutePrefix = "swagger";
        options.DisplayRequestDuration();
        options.EnableDeepLinking();
        options.EnableFilter();
    });
}
```

### Documentación rica con atributos

```csharp
/// <summary>
/// Obtiene la lista paginada de usuarios
/// </summary>
/// <param name="query">Parámetros de consulta y filtrado</param>
/// <returns>Lista paginada de usuarios</returns>
/// <response code="200">Lista de usuarios obtenida exitosamente</response>
/// <response code="400">Parámetros de consulta inválidos</response>
/// <response code="401">Token de acceso requerido</response>
/// <response code="403">Sin permisos para acceder a usuarios</response>
[HttpGet]
[ProducesResponseType(typeof(PagedResponse<UserDto>), 200)]
[ProducesResponseType(typeof(ApiError), 400)]
[ProducesResponseType(typeof(ApiError), 401)]
[ProducesResponseType(typeof(ApiError), 403)]
public async Task<ActionResult<PagedResponse<UserDto>>> GetUsers(
    [FromQuery] UserQuery query)
{
    var users = await _userService.GetUsersAsync(query);
    return Ok(users);
}

/// <summary>
/// Crea un nuevo usuario en el sistema
/// </summary>
/// <param name="request">Datos del usuario a crear</param>
/// <returns>Usuario creado con su ID asignado</returns>
/// <remarks>
/// Ejemplo de request:
///
///     POST /api/v1/users
///     {
///         "name": "Juan Pérez",
///         "email": "juan.perez@talma.pe",
///         "phone": "+51987654321",
///         "age": 30,
///         "roles": ["user"]
///     }
///
/// </remarks>
/// <response code="201">Usuario creado exitosamente</response>
/// <response code="400">Datos de entrada inválidos</response>
/// <response code="422">Error de lógica de negocio (ej: email duplicado)</response>
[HttpPost]
[ProducesResponseType(typeof(ApiResponse<UserDto>), 201)]
[ProducesResponseType(typeof(ApiError), 400)]
[ProducesResponseType(typeof(ApiError), 422)]
public async Task<ActionResult<ApiResponse<UserDto>>> CreateUser(
    [FromBody] CreateUserRequest request)
{
    // Implementation...
}
```

### Modelos con documentación

```csharp
/// <summary>
/// Datos básicos de un usuario del sistema
/// </summary>
public class UserDto
{
    /// <summary>
    /// Identificador único del usuario
    /// </summary>
    /// <example>12345</example>
    public int Id { get; set; }

    /// <summary>
    /// Nombre completo del usuario
    /// </summary>
    /// <example>Juan Pérez García</example>
    [Required]
    public string Name { get; set; }

    /// <summary>
    /// Dirección de correo electrónico (debe ser dominio Talma)
    /// </summary>
    /// <example>juan.perez@talma.pe</example>
    [Required]
    public string Email { get; set; }

    /// <summary>
    /// Estado activo del usuario
    /// </summary>
    /// <example>true</example>
    public bool Active { get; set; }

    /// <summary>
    /// Fecha y hora de creación del usuario (UTC)
    /// </summary>
    /// <example>2024-01-15T10:30:00Z</example>
    public DateTime CreatedAt { get; set; }
}

/// <summary>
/// Parámetros para crear un nuevo usuario
/// </summary>
public class CreateUserRequest
{
    /// <summary>
    /// Nombre completo del usuario (2-100 caracteres, solo letras)
    /// </summary>
    /// <example>María González</example>
    [Required(ErrorMessage = "El nombre es obligatorio")]
    [StringLength(100, MinimumLength = 2)]
    public string Name { get; set; }

    /// <summary>
    /// Correo electrónico válido del dominio Talma
    /// </summary>
    /// <example>maria.gonzalez@talma.pe</example>
    [Required(ErrorMessage = "El email es obligatorio")]
    [EmailAddress]
    public string Email { get; set; }

    /// <summary>
    /// Número de teléfono (opcional)
    /// </summary>
    /// <example>+51987654321</example>
    [Phone]
    public string Phone { get; set; }
}
```

## 🔧 Mejores prácticas

### Estructura de archivos de documentación

```text
docs/
├── api/
│   ├── v1/
│   │   ├── users.md
│   │   ├── orders.md
│   │   └── authentication.md
│   ├── v2/
│   │   ├── users.md
│   │   └── orders.md
│   ├── changelog.md
│   ├── migration-guide.md
│   └── postman-collections/
│       ├── v1.json
│       └── v2.json
```

### Changelog y guías de migración

```markdown
# API Changelog

## v2.0.0 (2024-03-01)

### Breaking Changes
- `GET /api/v1/users` ahora requiere paginación obligatoria
- Campo `user.created_date` renombrado a `user.created_at`
- Eliminado endpoint deprecado `POST /api/v1/login`

### New Features
- Nuevo endpoint `GET /api/v2/users/{id}/permissions`
- Agregado soporte para filtrado por múltiples campos
- Nuevo campo `user.department` en respuestas

### Bug Fixes
- Corregida validación de email para dominios internacionales
- Mejorada performance en consultas paginadas

## Migration Guide v1 → v2

### Required Changes
1. **Paginación**: Agregar parámetros `page` y `limit`
2. **Campo renamed**: `created_date` → `created_at`
3. **Autenticación**: Migrar de `/login` a `/auth/token`

### Code Examples

```javascript
// v1
fetch('/api/v1/users')

// v2
fetch('/api/v2/users?page=1&limit=20')
```

### Testing de compatibilidad

```csharp
[Fact]
public async Task GetUsers_V1_MaintainsCompatibility()
{
    // Arrange
    var client = _factory.CreateClient();
    client.DefaultRequestHeaders.Add("X-Version", "1.0");

    // Act
    var response = await client.GetAsync("/api/v1/users");

    // Assert
    response.StatusCode.Should().Be(HttpStatusCode.OK);

    var content = await response.Content.ReadAsStringAsync();
    var users = JsonSerializer.Deserialize<UserV1Dto[]>(content);

    // Verificar que v1 no incluye campos nuevos de v2
    users.First().Should().NotHaveProperty("Department");
    users.First().Should().NotHaveProperty("Permissions");
}
```

## 📖 Referencias

### ADRs relacionados

- [ADR-002: Estándar para APIs REST](/docs/adrs/adr-002-estandard-apis-rest)
- [ADR-017: Versionado de APIs](/docs/adrs/adr-017-versionado-apis)

### Recursos externos

- [Microsoft API Versioning](https://github.com/microsoft/aspnet-api-versioning)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Semantic Versioning](https://semver.org/)
- [API Evolution Best Practices](https://blog.postman.com/api-versioning-best-practices/)
