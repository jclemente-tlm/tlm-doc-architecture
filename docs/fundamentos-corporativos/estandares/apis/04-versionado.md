---
id: versionado
sidebar_position: 4
title: Versionado de APIs
description: Estándar de versionado de APIs REST con URL versioning, semantic versioning, estrategias de deprecación y compatibilidad hacia atrás
---

# Estándar: Versionado de APIs

## 1. Propósito

Definir la estrategia técnica obligatoria de **versionado de APIs REST** en Talma usando URL versioning, semantic versioning adaptado, políticas de deprecación y compatibilidad hacia atrás para garantizar evolución controlada sin romper clientes existentes.

## 2. Alcance

### Aplica a

- ✅ Todas las APIs REST públicas
- ✅ APIs de integración con sistemas externos
- ✅ Microservicios con contratos públicos
- ✅ APIs con múltiples consumidores

### NO aplica a

- ❌ APIs internas temporales (POCs)
- ❌ Endpoints administrativos internos sin SLA

## 3. Tecnologías Obligatorias

### Stack de Versionado

| Tecnología                               | Versión Mínima | Propósito                       |
| ---------------------------------------- | -------------- | ------------------------------- |
| **Microsoft.AspNetCore.Mvc.Versioning** | 5.0+           | Versionado de APIs en ASP.NET   |
| **Asp.Versioning.Mvc.ApiExplorer**       | 6.0+           | Exploración de versiones        |
| **Swashbuckle.AspNetCore**               | 6.5+           | Documentación multi-versión     |

### Estrategias de Versionado (Recomendación)

| Estrategia           | Formato                              | Recomendación | Uso                     |
| -------------------- | ------------------------------------ | ------------- | ----------------------- |
| **URL Segment**      | `/api/v1/users`, `/api/v2/users`     | ✅ Recomendado | APIs públicas estándar  |
| Query String         | `/api/users?version=1`               | ⚠️ Alternativo | APIs con cache complejo |
| Header               | `X-API-Version: 1`                   | ⚠️ Alternativo | APIs con muchas versiones|
| Media Type           | `Accept: application/vnd.api.v1+json`| ❌ No usar     | Complejo y poco claro   |

| Media Type           | `Accept: application/vnd.api.v1+json`| ❌ No usar     | Complejo y poco claro   |

## 4. Configuración Técnica Obligatoria

### 4.1 Configuración ASP.NET Core con URL Versioning

```csharp
// Program.cs
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Versioning;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

// ✅ Configuración de versionado
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true; // Si no especifica, usa v1.0
    options.ReportApiVersions = true; // Header: api-supported-versions, api-deprecated-versions
    
    // ✅ URL Segment (recomendado)
    options.ApiVersionReader = new UrlSegmentApiVersionReader();
    
    // Alternativas (comentadas):
    // options.ApiVersionReader = new QueryStringApiVersionReader("version");
    // options.ApiVersionReader = new HeaderApiVersionReader("X-API-Version");
    
    // Combinar múltiples estrategias:
    // options.ApiVersionReader = ApiVersionReader.Combine(
    //     new UrlSegmentApiVersionReader(),
    //     new QueryStringApiVersionReader("version"),
    //     new HeaderApiVersionReader("X-API-Version")
    // );
});

// ✅ API Explorer para Swagger
builder.Services.AddVersionedApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV"; // Formato: v1, v2, v2.1
    options.SubstituteApiVersionInUrl = true;
});

var app = builder.Build();

// Middleware
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

### 4.2 Controller con Múltiples Versiones

```csharp
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0")]
[ApiVersion("2.0")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly IMapper _mapper;

    public UsersController(IUserService userService, IMapper mapper)
    {
        _userService = userService;
        _mapper = mapper;
    }

    /// <summary>
    /// Obtiene lista de usuarios - Versión 1.0
    /// </summary>
    [HttpGet]
    [MapToApiVersion("1.0")]
    [ProducesResponseType(typeof(List<UserV1Dto>), 200)]
    public async Task<ActionResult<List<UserV1Dto>>> GetUsersV1()
    {
        var users = await _userService.GetAllUsersAsync();
        var dtos = _mapper.Map<List<UserV1Dto>>(users);
        return Ok(dtos);
    }

    /// <summary>
    /// Obtiene lista de usuarios - Versión 2.0 (con campos adicionales)
    /// </summary>
    [HttpGet]
    [MapToApiVersion("2.0")]
    [ProducesResponseType(typeof(List<UserV2Dto>), 200)]
    public async Task<ActionResult<List<UserV2Dto>>> GetUsersV2()
    {
        var users = await _userService.GetAllUsersAsync();
        var dtos = _mapper.Map<List<UserV2Dto>>(users);
        return Ok(dtos);
    }

    /// <summary>
    /// Crea un usuario - Disponible en v1 y v2
    /// </summary>
    [HttpPost]
    [MapToApiVersion("1.0")]
    [MapToApiVersion("2.0")]
    [ProducesResponseType(typeof(UserDto), 201)]
    public async Task<ActionResult<UserDto>> CreateUser([FromBody] CreateUserRequest request)
    {
        var user = await _userService.CreateUserAsync(request);
        return CreatedAtAction(nameof(GetUserV2), new { id = user.Id }, user);
    }
}
```

### 4.3 DTOs Versionados

```csharp
// V1 - DTO original
public class UserV1Dto
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public bool Active { get; set; }
}

// V2 - DTO con campos adicionales
public class UserV2Dto
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public bool Active { get; set; }
    
    // ✅ Nuevos campos en v2
    public string Department { get; set; }
    public DateTime CreatedAt { get; set; }
    public List<string> Permissions { get; set; }
}
```

### 4.4 Swagger Multi-Versión

```csharp
using Microsoft.OpenApi.Models;

builder.Services.AddSwaggerGen(options =>
{
    // ✅ Documento para v1
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Version = "v1.0",
        Title = "Talma API v1",
        Description = "API REST para gestión de usuarios - Versión 1 (Stable)",
        Contact = new OpenApiContact
        {
            Name = "Equipo de Arquitectura",
            Email = "arquitectura@talma.com"
        }
    });

    // ✅ Documento para v2
    options.SwaggerDoc("v2", new OpenApiInfo
    {
        Version = "v2.0",
        Title = "Talma API v2",
        Description = "API REST para gestión de usuarios - Versión 2 (Latest)",
        Contact = new OpenApiContact
        {
            Name = "Equipo de Arquitectura",
            Email = "arquitectura@talma.com"
        }
    });

    // XML Comments
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);

    // Operación filtrada por versión
    options.DocInclusionPredicate((version, apiDesc) =>
    {
        var versions = apiDesc.ActionDescriptor
            .GetApiVersionModel(ApiVersionMapping.Explicit | ApiVersionMapping.Implicit);
        
        return versions.DeclaredApiVersions.Any(v => $"v{v}" == version);
    });
});

// Configurar UI de Swagger
app.UseSwagger();
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/swagger/v1/swagger.json", "API v1");
    options.SwaggerEndpoint("/swagger/v2/swagger.json", "API v2");
});
```

## 5. Ejemplos de Implementación

### 5.1 Semantic Versioning Adaptado

```
MAJOR.MINOR.PATCH

MAJOR (v1 → v2): Breaking Changes
  - ❌ Eliminar endpoints
  - ❌ Renombrar campos existentes
  - ❌ Cambiar tipos de datos (string → int)
  - ❌ Cambiar semántica de operaciones
  - ❌ Hacer obligatorio un campo opcional

MINOR (v1.0 → v1.1): Cambios compatibles
  - ✅ Nuevos endpoints
  - ✅ Nuevos campos opcionales en respuestas
  - ✅ Nuevos parámetros opcionales en requests
  
PATCH (v1.1.0 → v1.1.1): Bug fixes
  - ✅ Correcciones de bugs
  - ✅ Mejoras de performance
  - ✅ Actualizaciones de documentación
```

### 5.2 Estrategia de Deprecación

```csharp
// Marcar versión como deprecated
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0", Deprecated = true)] // ✅ Marcar como deprecated
[ApiVersion("2.0")]
public class UsersController : ControllerBase
{
    [HttpGet]
    [MapToApiVersion("1.0")]
    public async Task<ActionResult<List<UserV1Dto>>> GetUsersV1()
    {
        // ✅ Agregar headers de deprecación
        Response.Headers.Append("Sunset", "2026-12-31T23:59:59Z"); // RFC 8594
        Response.Headers.Append("Deprecation", "true"); // RFC 8594
        Response.Headers.Append("Link", "</api/v2/users>; rel=\"successor-version\"");
        
        _logger.LogWarning(
            "API v1 deprecated endpoint accessed: {Endpoint}. Client: {UserAgent}",
            HttpContext.Request.Path,
            HttpContext.Request.Headers.UserAgent
        );

        var users = await _userService.GetAllUsersAsync();
        return Ok(_mapper.Map<List<UserV1Dto>>(users));
    }

    [HttpGet]
    [MapToApiVersion("2.0")]
    public async Task<ActionResult<List<UserV2Dto>>> GetUsersV2()
    {
        var users = await _userService.GetAllUsersAsync();
        return Ok(_mapper.Map<List<UserV2Dto>>(users));
    }
}
```

**Response headers de v1 (deprecated)**:

```http
HTTP/1.1 200 OK
Sunset: 2026-12-31T23:59:59Z
Deprecation: true
Link: </api/v2/users>; rel="successor-version"
api-supported-versions: 1.0, 2.0
api-deprecated-versions: 1.0
```

### 5.3 Changelog y Migration Guide

**CHANGELOG.md**:

```markdown
# Changelog

## [2.0.0] - 2026-01-27

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

## Migration Guide v1 → v2

### Required Changes

1. **Paginación**: Agregar parámetros `page` y `limit`
2. **Campo renamed**: `created_date` → `created_at`
3. **Endpoint**: Migrar de `/login` a `/auth/token`

### Code Examples

```javascript
// v1
fetch('/api/v1/users');

// v2
fetch('/api/v2/users?page=1&limit=20');
```
```

## 6. Mejores Prácticas

### 6.1 Compatibilidad Hacia Atrás

```csharp
// ✅ BIEN - Mantener ambas versiones funcionando
public class UserService
{
    public async Task<UserV1Dto> GetUserV1Async(Guid id)
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

    public async Task<UserV2Dto> GetUserV2Async(Guid id)
    {
        var user = await _repository.GetUserAsync(id);
        
        // Incluir todos los campos de v2
        return new UserV2Dto
        {
            Id = user.Id,
            Name = user.Name,
            Email = user.Email,
            Active = user.Active,
            Department = user.Department,
            CreatedAt = user.CreatedAt,
            Permissions = user.Permissions
        };
    }
}
```

### 6.2 Política de Soporte de Versiones

```
Versión Actual (v2):   Soporte completo (bugs + features)
Versión Anterior (v1): Soporte de bugs críticos (6 meses)
Versión -2 (v0):       Deprecated (3 meses de gracia)
Versión -3:            Eliminada

Timeline:
  t0: v2 release
  t+6m: v1 deprecated (solo bugs críticos)
  t+9m: v1 sunset (eliminada)
```

### 6.3 Testing de Compatibilidad

```csharp
public class VersioningIntegrationTests : IClassFixture<IntegrationTestFactory>
{
    private readonly HttpClient _client;

    public VersioningIntegrationTests(IntegrationTestFactory factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetUsers_V1_ReturnsOnlyV1Fields()
    {
        // Act
        var response = await _client.GetAsync("/api/v1/users");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        
        var users = await response.Content.ReadFromJsonAsync<List<UserV1Dto>>();
        users.Should().NotBeNull();
        
        // Verificar que v1 NO incluye campos de v2
        var firstUser = users.First();
        firstUser.Should().NotHaveProperty(nameof(UserV2Dto.Department));
        firstUser.Should().NotHaveProperty(nameof(UserV2Dto.Permissions));
    }

    [Fact]
    public async Task GetUsers_V2_ReturnsAllFields()
    {
        // Act
        var response = await _client.GetAsync("/api/v2/users");

        // Assert
        var users = await response.Content.ReadFromJsonAsync<List<UserV2Dto>>();
        
        var firstUser = users.First();
        firstUser.Department.Should().NotBeNullOrEmpty();
        firstUser.Permissions.Should().NotBeNull();
    }

    [Fact]
    public async Task GetUsers_V1Deprecated_ReturnsDeprecationHeaders()
    {
        // Act
        var response = await _client.GetAsync("/api/v1/users");

        // Assert
        response.Headers.Should().ContainKey("Sunset");
        response.Headers.Should().ContainKey("Deprecation");
        response.Headers.GetValues("Deprecation").Should().Contain("true");
    }
}
```

## 7. Antipatrones (NO Hacer)

### ❌ Antipatrón 1: Modificar Endpoints Existentes Sin Versionar

```csharp
// ❌ MAL - Cambiar respuesta de v1 existente (rompe clientes)
[HttpGet]
public async Task<ActionResult<UserDto>> GetUsers()
{
    var users = await _userService.GetAllUsersAsync();
    
    // ❌ Agregamos campo nuevo directamente a v1
    return Ok(users.Select(u => new {
        u.Id,
        u.Name,
        u.Email,
        u.Department // ❌ Breaking change en v1
    }));
}

// ✅ BIEN - Crear nueva versión
[ApiVersion("1.0")]
[ApiVersion("2.0")]
[HttpGet]
[MapToApiVersion("1.0")]
public async Task<ActionResult<UserV1Dto>> GetUsersV1()
{
    // v1 sin cambios
    return Ok(_mapper.Map<List<UserV1Dto>>(users));
}

[HttpGet]
[MapToApiVersion("2.0")]
public async Task<ActionResult<UserV2Dto>> GetUsersV2()
{
    // v2 con campo nuevo
    return Ok(_mapper.Map<List<UserV2Dto>>(users));
}
```

**Problema**: Clientes de v1 reciben campos inesperados, parseo falla.  
**Solución**: Crear v2, mantener v1 sin cambios.

### ❌ Antipatrón 2: No Documentar Breaking Changes

```csharp
// ❌ MAL - Hacer breaking change sin avisar
[ApiVersion("2.0")] // Sin deprecar v1, sin changelog, sin migration guide
public class UsersController : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult> GetUsers()
    {
        // Campo "created_date" ahora se llama "created_at"
        // ❌ No hay documentación del cambio
    }
}

// ✅ BIEN - Documentar cambios + periodo de transición
[ApiVersion("1.0", Deprecated = true)] // Marcar deprecated
[ApiVersion("2.0")]
public class UsersController : ControllerBase
{
    // Crear CHANGELOG.md y MIGRATION_GUIDE.md
    // Agregar headers Sunset, Deprecation
    // Logging de uso de v1 para análisis
}
```

**Problema**: Clientes se rompen sin aviso previo.  
**Solución**: CHANGELOG.md + headers de deprecación + 6 meses de gracia.

### ❌ Antipatrón 3: Mantener Demasiadas Versiones Simultáneas

```csharp
// ❌ MAL - Mantener v1, v2, v3, v4, v5 simultáneamente
[ApiVersion("1.0")]
[ApiVersion("2.0")]
[ApiVersion("3.0")]
[ApiVersion("4.0")]
[ApiVersion("5.0")] // ❌ Costo de mantenimiento insostenible
public class UsersController : ControllerBase { }

// ✅ BIEN - Máximo 2-3 versiones activas
[ApiVersion("3.0", Deprecated = true)] // Deprecated
[ApiVersion("4.0")] // Estable
[ApiVersion("5.0")] // Latest
public class UsersController : ControllerBase
{
    // v1 y v2 ya eliminadas
}
```

**Problema**: Costo de mantenimiento, testing y debugging crece exponencialmente.  
**Solución**: Política estricta: máximo 2-3 versiones activas, eliminar deprecated después de 6 meses.

### ❌ Antipatrón 4: Usar Query String o Headers para APIs Públicas

```csharp
// ❌ MAL - Query string (no cacheable, complejo)
options.ApiVersionReader = new QueryStringApiVersionReader("version");
// URL: /api/users?version=2 ❌

// ❌ MAL - Header (invisible, difícil de debuggear)
options.ApiVersionReader = new HeaderApiVersionReader("X-API-Version");
// Header: X-API-Version: 2 ❌

// ✅ BIEN - URL Segment (claro, cacheable, RESTful)
options.ApiVersionReader = new UrlSegmentApiVersionReader();
// URL: /api/v2/users ✅
```

**Problema**: Query string y headers dificultan cache, debugging y descubrimiento de API.  
**Solución**: URL Segment para APIs públicas (simple, claro, cacheable).

## 8. Validación y Cumplimiento

### 8.1 Checklist de Implementación

- [ ] **ApiVersioning** configurado con URL Segment
- [ ] **Swagger** con documentación multi-versión
- [ ] **DTOs versionados** (V1Dto, V2Dto) separados
- [ ] **MapToApiVersion** en cada endpoint
- [ ] **Deprecated** marcado en versiones antiguas
- [ ] **Headers de deprecación** (Sunset, Deprecation, Link)
- [ ] **CHANGELOG.md** actualizado con breaking changes
- [ ] **MIGRATION_GUIDE.md** para cada major version
- [ ] **Tests de compatibilidad** para cada versión
- [ ] **Logging** de uso de versiones deprecated

### 8.2 Métricas de Cumplimiento

| Métrica                                | Target | Verificación                         |
| -------------------------------------- | ------ | ------------------------------------ |
| APIs con versionado implementado       | 100%   | Configuración de ApiVersioning       |
| Versiones activas simultáneas          | ≤ 3    | Conteo de ApiVersion attributes      |
| Tiempo de soporte de versiones deprecated | 6 meses | Política documentada               |
| Breaking changes documentados          | 100%   | CHANGELOG.md actualizado             |
| Endpoints con MapToApiVersion          | 100%   | Code review                          |

## 9. Referencias

### Estándares Relacionados

- [Diseño REST](./01-diseno-rest.md) - Implementación técnica de APIs
- [Seguridad APIs](./02-seguridad-apis.md) - Seguridad en múltiples versiones

### Convenciones Relacionadas

- [Naming Endpoints](../../convenciones/apis/01-naming-endpoints.md) - Nomenclatura con versiones
- [Formato Respuestas](../../convenciones/apis/03-formato-respuestas.md) - Estructura de respuestas

### Lineamientos Relacionados

- [Desarrollo de APIs](../../lineamientos/desarrollo/desarrollo-de-apis.md) - Lineamientos de APIs
- [Evolución y Cambios Controlados](../../lineamientos/arquitectura/03-evolucion-y-cambios-controlados.md) - Gestión de cambios

### Principios Relacionados

- [Contratos de Comunicación](../../principios/arquitectura/06-contratos-de-comunicacion.md) - Fundamento de versionado
- [Evolución Controlada](../../principios/arquitectura/04-evolucion-controlada.md) - Cambios sin romper clientes

### ADRs Relacionados

- [ADR-002: Estándar para APIs REST](../../../decisiones-de-arquitectura/adr-002-estandard-apis-rest.md)
- [ADR-017: Versionado de APIs](../../../decisiones-de-arquitectura/adr-017-versionado-apis.md)

### Documentación Externa

- [Microsoft API Versioning](https://github.com/microsoft/aspnet-api-versioning) - Librería oficial
- [Semantic Versioning](https://semver.org/) - SemVer specification
- [RFC 8594 - Sunset Header](https://www.rfc-editor.org/rfc/rfc8594) - Deprecación estándar
- [API Evolution Best Practices](https://www.postman.com/api-platform/api-versioning/) - Postman Guide

---

**Última actualización**: 27 de enero 2026  
**Responsable**: Equipo de Arquitectura
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
///         "userName": "jperez",
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

````markdown
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
fetch("/api/v1/users");

// v2
fetch("/api/v2/users?page=1&limit=20");
```
````

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

### Lineamientos relacionados

- [Desarrollo de APIs](/docs/fundamentos-corporativos/lineamientos/desarrollo/desarrollo-de-apis)
- [Evolución y Cambios Controlados](/docs/fundamentos-corporativos/lineamientos/arquitectura/evolucion-y-cambios-controlados)

### ADRs relacionados

- [ADR-002: Estándar para APIs REST](/docs/adrs/adr-002-estandard-apis-rest)
- [ADR-017: Versionado de APIs](/docs/adrs/adr-017-versionado-apis)

### Recursos externos

- [Microsoft API Versioning](https://github.com/microsoft/aspnet-api-versioning)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Semantic Versioning](https://semver.org/)
- [API Evolution Best Practices](https://blog.postman.com/api-versioning-best-practices/)
