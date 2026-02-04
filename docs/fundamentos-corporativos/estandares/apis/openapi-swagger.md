---
id: openapi-swagger
sidebar_position: 6
title: Documentación OpenAPI/Swagger
description: Estándar para documentación OpenAPI 3.1+ con Swashbuckle, XML comments, ejemplos, seguridad y generación automática de spec
---

# Estándar Técnico — Documentación OpenAPI/Swagger

---

## 1. Propósito

Garantizar documentación completa, precisa y actualizada de APIs mediante OpenAPI 3.1+ con Swashbuckle.AspNetCore, XML documentation comments, ejemplos ejecutables, schemas detallados, seguridad documentada y generación automática desde código.

---

## 2. Alcance

**Aplica a:**

- APIs REST públicas y privadas
- Documentación de endpoints, DTOs y seguridad
- Generación automática de especificación OpenAPI
- Swagger UI para testing interactivo
- Generación de SDKs desde spec

**No aplica a:**

- APIs GraphQL (usa GraphQL introspection)
- gRPC (usa protobuf reflection)
- WebSockets (no estandarizado en OpenAPI)

---

## 3. Tecnologías Aprobadas

| Componente      | Tecnología                         | Versión mínima | Observaciones            |
| --------------- | ---------------------------------- | -------------- | ------------------------ |
| **Spec**        | OpenAPI                            | 3.1+           | Especificación formal    |
| **Generador**   | Swashbuckle.AspNetCore             | 6.5+           | Generación automática    |
| **Anotaciones** | Swashbuckle.AspNetCore.Annotations | 6.5+           | Metadata adicional       |
| **Ejemplos**    | Swashbuckle.AspNetCore.Filters     | 7.0+           | Ejemplos ejecutables     |
| **Validación**  | Swashbuckle.AspNetCore.Newtonsoft  | 6.5+           | Opcional para Newtonsoft |
| **CLI**         | OpenAPI Generator                  | 7.0+           | Generación de clientes   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Configuración OpenAPI

- [ ] OpenAPI 3.1 como versión mínima
- [ ] `info` con versión semántica, título, descripción, contacto
- [ ] `servers` con URLs de dev, staging, production
- [ ] `tags` para agrupar endpoints por dominio
- [ ] `components/schemas` para todos los DTOs
- [ ] `components/securitySchemes` para autenticación
- [ ] `externalDocs` con links a documentación adicional

### Documentación de Endpoints

- [ ] XML documentation comments en todos los controllers
- [ ] `summary` y `description` en cada endpoint
- [ ] `remarks` con ejemplos de uso
- [ ] `response` tags para cada status code posible
- [ ] `param` tags para parámetros de ruta, query, header
- [ ] Atributos `[ProducesResponseType]` en actions
- [ ] Atributos `[Produces]` y `[Consumes]` para content types

### Schemas y DTOs

- [ ] `type` explícito para cada propiedad (string, integer, boolean, etc.)
- [ ] `format` para tipos específicos (email, uuid, date-time, uri)
- [ ] `required` array con campos obligatorios
- [ ] `pattern` para validaciones regex
- [ ] `minLength`, `maxLength`, `minimum`, `maximum` según validaciones
- [ ] `enum` para valores fijos
- [ ] `example` realista en cada schema
- [ ] `deprecated: true` para propiedades deprecadas

### Ejemplos

- [ ] Ejemplos en request bodies
- [ ] Ejemplos en responses
- [ ] Múltiples ejemplos para casos de éxito/error
- [ ] Ejemplos ejecutables en Swagger UI

### Seguridad

- [ ] `securitySchemes` definido (Bearer JWT, OAuth2, API Key)
- [ ] `security` aplicado globalmente o por endpoint
- [ ] Scopes OAuth2 documentados
- [ ] Flows OAuth2 definidos (authorizationCode, clientCredentials)

### Generación Automática

- [ ] Spec generado automáticamente en build
- [ ] Versionado del spec sincronizado con versión de API
- [ ] Spec publicado en `/swagger/v1/swagger.json`
- [ ] Swagger UI accesible en `/swagger`

---

## 5. Prohibiciones

- ❌ Documentación desactualizada vs código real
- ❌ Schemas sin tipos explícitos (`type: object` genérico)
- ❌ Endpoints sin documentación XML
- ❌ Ejemplos inválidos o inconsistentes
- ❌ Swagger UI en producción con Try-it-out expuesto públicamente
- ❌ Credenciales hardcoded en ejemplos
- ❌ Omitir status codes de error (400, 401, 404, 500)

---

## 6. Configuración Mínima

```csharp
// Program.cs
using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.Filters;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

builder.Services.AddSwaggerGen(options =>
{
    // Info básica
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Version = "v1",
        Title = "Talma Users API",
        Description = "API para gestión de usuarios corporativos de Talma",
        TermsOfService = new Uri("https://talma.com/terms"),
        Contact = new OpenApiContact
        {
            Name = "Arquitectura Talma",
            Email = "arquitectura@talma.com",
            Url = new Uri("https://docs.talma.com")
        },
        License = new OpenApiLicense
        {
            Name = "Uso interno Talma",
            Url = new Uri("https://talma.com/license")
        }
    });

    // Servers
    options.AddServer(new OpenApiServer
    {
        Url = "https://api.talma.com",
        Description = "Producción"
    });
    options.AddServer(new OpenApiServer
    {
        Url = "https://api-staging.talma.com",
        Description = "Staging"
    });
    options.AddServer(new OpenApiServer
    {
        Url = "https://localhost:5001",
        Description = "Desarrollo local"
    });

    // Seguridad JWT Bearer
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = @"JWT Authorization header usando Bearer scheme.
                        Ejemplo: 'Bearer {token}'",
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

    // XML Comments
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);

    // Annotations
    options.EnableAnnotations();

    // Ejemplos
    options.ExampleFilters();

    // Ordenar por tags
    options.TagActionsBy(api => new[] { api.GroupName ?? api.ActionDescriptor.RouteValues["controller"] });
    options.OrderActionsBy(api => $"{api.ActionDescriptor.RouteValues["controller"]}_{api.HttpMethod}");
});

builder.Services.AddSwaggerExamplesFromAssemblyOf<Program>();

var app = builder.Build();

// Swagger en desarrollo
if (app.Environment.IsDevelopment())
{
    app.UseSwagger(c =>
    {
        c.RouteTemplate = "swagger/{documentName}/swagger.json";
    });

    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Talma Users API v1");
        c.RoutePrefix = "swagger";
        c.DocumentTitle = "Talma Users API";
        c.EnableDeepLinking();
        c.DisplayRequestDuration();
        c.EnableTryItOutByDefault();
    });
}

app.MapControllers();
app.Run();
```

```xml
<!-- .csproj - Habilitar XML documentation -->
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <NoWarn>$(NoWarn);1591</NoWarn> <!-- Suprimir warning de XML comments faltantes -->
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
  <PackageReference Include="Swashbuckle.AspNetCore.Annotations" Version="6.5.0" />
  <PackageReference Include="Swashbuckle.AspNetCore.Filters" Version="7.0.12" />
</ItemGroup>
```

---

## 7. Ejemplos

### Controller con documentación completa

```csharp
/// <summary>
/// Gestión de usuarios del sistema
/// </summary>
[ApiController]
[Route("api/v1/users")]
[Produces("application/json")]
[SwaggerTag("Operaciones CRUD de usuarios corporativos")]
public class UsersController : ControllerBase
{
    /// <summary>
    /// Obtiene lista de usuarios activos
    /// </summary>
    /// <remarks>
    /// Ejemplo de request:
    ///
    ///     GET /api/v1/users?page=1&pageSize=20
    ///
    /// </remarks>
    /// <param name="page">Número de página (1-based)</param>
    /// <param name="pageSize">Tamaño de página (1-100)</param>
    /// <returns>Lista paginada de usuarios</returns>
    /// <response code="200">Lista retornada exitosamente</response>
    /// <response code="400">Parámetros inválidos</response>
    /// <response code="401">No autenticado</response>
    [HttpGet]
    [ProducesResponseType(typeof(PagedResult<UserDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetUsers(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var users = await _service.GetPagedAsync(page, pageSize);
        return Ok(users);
    }

    /// <summary>
    /// Obtiene un usuario por ID
    /// </summary>
    /// <param name="id">ID único del usuario (GUID)</param>
    /// <returns>Detalles del usuario</returns>
    /// <response code="200">Usuario encontrado</response>
    /// <response code="404">Usuario no existe</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetUser(Guid id)
    {
        var user = await _service.GetByIdAsync(id);
        if (user == null) return NotFound();
        return Ok(user);
    }

    /// <summary>
    /// Crea un nuevo usuario
    /// </summary>
    /// <param name="request">Datos del usuario a crear</param>
    /// <returns>Usuario creado con ID asignado</returns>
    /// <response code="201">Usuario creado exitosamente</response>
    /// <response code="400">Datos inválidos</response>
    /// <response code="409">Email ya existe</response>
    [HttpPost]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status409Conflict)]
    public async Task<IActionResult> CreateUser([FromBody] CreateUserRequest request)
    {
        var user = await _service.CreateAsync(request);
        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }
}
```

### DTOs con anotaciones

```csharp
/// <summary>
/// Datos para crear un usuario
/// </summary>
public record CreateUserRequest
{
    /// <summary>
    /// Email corporativo del usuario
    /// </summary>
    /// <example>juan.perez@talma.com</example>
    [Required]
    [EmailAddress]
    [SwaggerSchema("Email corporativo (solo @talma.com)")]
    public string Email { get; init; }

    /// <summary>
    /// Nombre del usuario
    /// </summary>
    /// <example>Juan</example>
    [Required]
    [StringLength(50, MinimumLength = 2)]
    [SwaggerSchema("Nombre (2-50 caracteres)")]
    public string FirstName { get; init; }

    /// <summary>
    /// Apellido del usuario
    /// </summary>
    /// <example>Pérez</example>
    [Required]
    [StringLength(50, MinimumLength = 2)]
    public string LastName { get; init; }

    /// <summary>
    /// Rol del usuario en el sistema
    /// </summary>
    /// <example>Developer</example>
    [SwaggerSchema("Rol del usuario")]
    public UserRole Role { get; init; } = UserRole.Developer;
}

/// <summary>
/// Roles disponibles en el sistema
/// </summary>
public enum UserRole
{
    /// <summary>Desarrollador</summary>
    Developer,
    /// <summary>Gerente</summary>
    Manager,
    /// <summary>Administrador</summary>
    Admin
}
```

### Ejemplos ejecutables

```csharp
public class CreateUserRequestExample : IExamplesProvider<CreateUserRequest>
{
    public CreateUserRequest GetExamples()
    {
        return new CreateUserRequest
        {
            Email = "juan.perez@talma.com",
            FirstName = "Juan",
            LastName = "Pérez",
            Role = UserRole.Developer
        };
    }
}

public class UserDtoExample : IExamplesProvider<UserDto>
{
    public UserDto GetExamples()
    {
        return new UserDto
        {
            Id = Guid.Parse("550e8400-e29b-41d4-a716-446655440000"),
            Email = "juan.perez@talma.com",
            FirstName = "Juan",
            LastName = "Pérez",
            Role = UserRole.Developer,
            CreatedAt = new DateTime(2024, 1, 15, 10, 30, 0, DateTimeKind.Utc),
            IsActive = true
        };
    }
}
```

### OpenAPI spec generado

```yaml
openapi: 3.0.1
info:
  title: Talma Users API
  description: API para gestión de usuarios corporativos de Talma
  contact:
    name: Arquitectura Talma
    email: arquitectura@talma.com
    url: https://docs.talma.com
  version: v1
servers:
  - url: https://api.talma.com
    description: Producción
  - url: https://api-staging.talma.com
    description: Staging
paths:
  /api/v1/users:
    post:
      tags:
        - Users
      summary: Crea un nuevo usuario
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUserRequest"
            examples:
              default:
                value:
                  email: juan.perez@talma.com
                  firstName: Juan
                  lastName: Pérez
                  role: Developer
      responses:
        "201":
          description: Usuario creado exitosamente
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserDto"
        "400":
          description: Datos inválidos
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ProblemDetails"
components:
  securitySchemes:
    Bearer:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    CreateUserRequest:
      required:
        - email
        - firstName
        - lastName
      type: object
      properties:
        email:
          type: string
          format: email
        firstName:
          maxLength: 50
          minLength: 2
          type: string
        lastName:
          maxLength: 50
          minLength: 2
          type: string
        role:
          $ref: "#/components/schemas/UserRole"
    UserRole:
      enum:
        - Developer
        - Manager
        - Admin
      type: string
security:
  - Bearer: []
```

---

## 8. Validación y Auditoría

```bash
# Generar y guardar spec
curl http://localhost:5000/swagger/v1/swagger.json > swagger.json

# Validar spec
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli validate \
  -i /local/swagger.json

# Linting de spec
npx @redocly/cli lint swagger.json

# Generar cliente C#
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i /local/swagger.json \
  -g csharp \
  -o /local/generated-client

# Comparar versiones
docker run --rm -v ${PWD}:/specs openapitools/openapi-diff \
  /specs/v1.0.0.json /specs/v1.1.0.json

# Verificar cobertura de documentación
dotnet build /p:TreatWarningsAsErrors=true
```

**Métricas de cumplimiento:**

| Métrica                   | Umbral                | Verificación               |
| ------------------------- | --------------------- | -------------------------- |
| Endpoints documentados    | 100%                  | Comparar routes vs spec    |
| XML comments              | 100% controllers/DTOs | Build warnings             |
| Ejemplos en schemas       | 100%                  | Validar spec               |
| Status codes documentados | 100% endpoints        | Revisar `responses`        |
| Spec válido OpenAPI 3.1   | Sí                    | openapi-generator validate |

---

## 9. Referencias

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Swashbuckle Documentation](https://github.com/domaindrivendev/Swashbuckle.AspNetCore)
- [Microsoft XML Documentation Comments](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Redocly CLI](https://redocly.com/docs/cli/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Azure API Design Guidelines](https://github.com/microsoft/api-guidelines)
