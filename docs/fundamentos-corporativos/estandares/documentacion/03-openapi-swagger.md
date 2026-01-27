---
id: openapi-swagger
sidebar_position: 3
title: Documentación de APIs con OpenAPI
description: Estándares para documentar APIs REST usando OpenAPI 3.1+, Swagger UI 5.0+ y Spectral
---

## 1. Propósito

Este estándar define cómo documentar APIs REST con OpenAPI Specification (OAS) para garantizar documentación precisa, interactiva y siempre actualizada. Establece:
- **OpenAPI 3.1+** como especificación estándar para APIs REST
- **Swagger UI** para interfaz interactiva de pruebas
- **Generación automática** desde código (.NET, TypeScript)
- **Validación con Spectral** para cumplir reglas de estilo
- **Versionado** sincronizado con API

Permite onboarding rápido de consumidores, testing interactivo y contratos API como código.

**Versión**: 1.0  
**Última actualización**: 2025-08-08

## 2. Alcance

### Aplica a:
- APIs REST públicas (para clientes externos)
- APIs REST internas (entre microservicios)
- APIs gateway (Kong, API Gateway AWS)
- SDKs generados automáticamente desde OpenAPI

### No aplica a:
- APIs gRPC (usar Protocol Buffers .proto)
- APIs GraphQL (usar Schema Definition Language)
- WebSockets/SignalR (documentar en arc42)
- APIs legacy sin documentación (requieren plan de migración)

## 3. Tecnologías Obligatorias

| Tecnología | Versión Mínima | Propósito |
|------------|----------------|-----------|
| **OpenAPI Specification** | 3.1+ | Especificación estándar de APIs REST (YAML/JSON) |
| **Swagger UI** | 5.0+ | Interfaz web interactiva para probar APIs |
| **Swashbuckle.AspNetCore** | 6.5+ | Generación automática de OpenAPI desde ASP.NET Core |
| **NSwag** | 14.0+ | Generación de clientes TypeScript/C# desde OpenAPI |
| **Spectral** | 6.11+ | Linter para validar especificaciones OpenAPI |
| **Redoc** | 2.1+ | Documentación estática elegante (alternativa a Swagger UI) |

## 4. Especificaciones Técnicas

### 4.1 Generación Automática con Swashbuckle (.NET)

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Talma Users API",
        Version = "v1",
        Description = "API para gestión de usuarios, autenticación y autorización",
        Contact = new OpenApiContact
        {
            Name = "Equipo de Arquitectura",
            Email = "arquitectura@talma.com",
            Url = new Uri("https://docs.talma.com")
        },
        License = new OpenApiLicense
        {
            Name = "Propietario - Uso interno Talma",
            Url = new Uri("https://talma.com/license")
        }
    });

    // Incluir comentarios XML
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);

    // Soporte para autenticación JWT
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using Bearer scheme. Example: 'Bearer {token}'",
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

    // Usar convenciones de naming
    options.CustomSchemaIds(type => type.FullName?.Replace("+", "."));
});

var app = builder.Build();

// Habilitar Swagger en todos los ambientes (desarrollo y producción)
app.UseSwagger();
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/swagger/v1/swagger.json", "Talma Users API v1");
    options.RoutePrefix = "api-docs"; // Accesible en /api-docs
    options.DisplayRequestDuration();
    options.EnableDeepLinking();
    options.EnableFilter();
});

app.Run();
```

### 4.2 Documentar Endpoints con XML Comments

```csharp
/// <summary>
/// Obtiene un usuario por su ID
/// </summary>
/// <param name="userId">ID único del usuario (UUID)</param>
/// <param name="cancellationToken">Token de cancelación</param>
/// <returns>Datos del usuario</returns>
/// <response code="200">Usuario encontrado</response>
/// <response code="404">Usuario no encontrado</response>
/// <response code="401">No autenticado</response>
[HttpGet("{userId:guid}")]
[ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
[ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
[ProducesResponseType(StatusCodes.Status401Unauthorized)]
public async Task<ActionResult<UserDto>> GetUser(
    Guid userId,
    CancellationToken cancellationToken)
{
    var user = await _userService.GetUserAsync(userId, cancellationToken);
    
    if (user == null)
        return NotFound(new ProblemDetails
        {
            Title = "Usuario no encontrado",
            Status = StatusCodes.Status404NotFound,
            Detail = $"No existe usuario con ID {userId}"
        });

    return Ok(user);
}
```

### 4.3 Schemas Reutilizables

```csharp
/// <summary>
/// Datos de un usuario
/// </summary>
public class UserDto
{
    /// <summary>
    /// ID único del usuario
    /// </summary>
    /// <example>3fa85f64-5717-4562-b3fc-2c963f66afa6</example>
    public Guid UserId { get; set; }

    /// <summary>
    /// Nombre completo del usuario
    /// </summary>
    /// <example>Juan Pérez</example>
    [Required]
    [MaxLength(200)]
    public string FullName { get; set; } = string.Empty;

    /// <summary>
    /// Email corporativo
    /// </summary>
    /// <example>juan.perez@talma.com</example>
    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// Indica si el usuario está activo
    /// </summary>
    public bool IsActive { get; set; }

    /// <summary>
    /// Fecha de creación (UTC)
    /// </summary>
    public DateTime CreatedAt { get; set; }
}
```

### 4.4 Especificación OpenAPI Resultante (YAML)

```yaml
openapi: 3.1.0
info:
  title: Talma Users API
  version: v1
  description: API para gestión de usuarios, autenticación y autorización
  contact:
    name: Equipo de Arquitectura
    email: arquitectura@talma.com
servers:
  - url: https://api.talma.com/v1
    description: Producción
  - url: https://api-dev.talma.com/v1
    description: Desarrollo

paths:
  /users/{userId}:
    get:
      summary: Obtiene un usuario por su ID
      operationId: getUser
      tags:
        - Users
      parameters:
        - name: userId
          in: path
          required: true
          description: ID único del usuario (UUID)
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Usuario encontrado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserDto'
        '404':
          description: Usuario no encontrado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ProblemDetails'
        '401':
          description: No autenticado
      security:
        - Bearer: []

components:
  schemas:
    UserDto:
      type: object
      required:
        - fullName
        - email
      properties:
        userId:
          type: string
          format: uuid
          example: 3fa85f64-5717-4562-b3fc-2c963f66afa6
        fullName:
          type: string
          maxLength: 200
          example: Juan Pérez
        email:
          type: string
          format: email
          example: juan.perez@talma.com
        isActive:
          type: boolean
        createdAt:
          type: string
          format: date-time

  securitySchemes:
    Bearer:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

## 5. Buenas Prácticas

### 5.1 Versionado en URL

```csharp
// ✅ Versionado explícito en URL
[ApiController]
[Route("api/v{version:apiVersion}/users")]
[ApiVersion("1.0")]
public class UsersV1Controller : ControllerBase { }

[ApiController]
[Route("api/v{version:apiVersion}/users")]
[ApiVersion("2.0")]
public class UsersV2Controller : ControllerBase { }
```

### 5.2 Ejemplos Completos

```csharp
options.SwaggerDoc("v1", new OpenApiInfo
{
    // ...
});

// Agregar ejemplos de requests/responses
options.SchemaFilter<ExampleSchemaFilter>();

public class ExampleSchemaFilter : ISchemaFilter
{
    public void Apply(OpenApiSchema schema, SchemaFilterContext context)
    {
        if (context.Type == typeof(CreateUserRequest))
        {
            schema.Example = new OpenApiObject
            {
                ["fullName"] = new OpenApiString("Ana García"),
                ["email"] = new OpenApiString("ana.garcia@talma.com"),
                ["roleId"] = new OpenApiString("admin")
            };
        }
    }
}
```

### 5.3 Validación con Spectral

```yaml
# .spectral.yml
extends: spectral:oas
rules:
  operation-description: error
  operation-tags: error
  operation-operationId: error
  no-$ref-siblings: error
  path-params: error
  oas3-valid-media-example: warn
```

```bash
# Validar especificación
spectral lint openapi.yaml
```

## 6. Antipatrones

### 6.1 ❌ Sin Documentar Códigos de Error

**Problema**:
```csharp
// ❌ Solo documenta caso exitoso
[HttpGet("{id}")]
[ProducesResponseType(typeof(UserDto), 200)]
public async Task<ActionResult<UserDto>> GetUser(int id) { }
```

**Solución**:
```csharp
// ✅ Documenta todos los casos
[HttpGet("{id}")]
[ProducesResponseType(typeof(UserDto), 200)]
[ProducesResponseType(typeof(ProblemDetails), 404)]
[ProducesResponseType(typeof(ValidationProblemDetails), 400)]
[ProducesResponseType(401)]
public async Task<ActionResult<UserDto>> GetUser(int id) { }
```

### 6.2 ❌ Sin Ejemplos

**Problema**:
```yaml
# ❌ Schema sin ejemplos
UserDto:
  type: object
  properties:
    fullName:
      type: string
```

**Solución**:
```yaml
# ✅ Schema con ejemplos
UserDto:
  type: object
  properties:
    fullName:
      type: string
      example: Juan Pérez
```

### 6.3 ❌ Documentación Desactualizada

**Problema**:
```csharp
// ❌ XML comments desactualizados
/// <summary>
/// Obtiene todos los usuarios (obsoleto: ahora usa paginación)
/// </summary>
[HttpGet]
public async Task<ActionResult<PagedResult<UserDto>>> GetUsers() { }
```

**Solución**:
```csharp
// ✅ Documentación actualizada
/// <summary>
/// Obtiene usuarios con paginación
/// </summary>
/// <param name="pageNumber">Número de página (base 1)</param>
/// <param name="pageSize">Tamaño de página (máximo 100)</param>
[HttpGet]
public async Task<ActionResult<PagedResult<UserDto>>> GetUsers(
    [FromQuery] int pageNumber = 1,
    [FromQuery] int pageSize = 20) { }
```

### 6.4 ❌ Sin Seguridad Documentada

**Problema**:
```yaml
# ❌ Endpoint sin seguridad documentada
paths:
  /users:
    get:
      # No indica que requiere autenticación
```

**Solución**:
```yaml
# ✅ Seguridad explícita
paths:
  /users:
    get:
      security:
        - Bearer: []
```

## 7. Validación y Testing

### 7.1 Tests de Especificación OpenAPI

```csharp
[Fact]
public async Task OpenApiSpec_IsValid()
{
    var response = await _client.GetAsync("/swagger/v1/swagger.json");
    response.StatusCode.Should().Be(HttpStatusCode.OK);

    var spec = await response.Content.ReadAsStringAsync();
    var document = JsonDocument.Parse(spec);

    document.RootElement.GetProperty("openapi").GetString()
        .Should().StartWith("3.");
}
```

### 7.2 Generación de Clientes

```bash
# Generar cliente TypeScript desde OpenAPI
nswag openapi2tsclient /input:openapi.json /output:clients/UsersApiClient.ts

# Generar cliente C# desde OpenAPI
nswag openapi2csclient /input:openapi.json /output:clients/UsersApiClient.cs
```

## 8. Referencias

### Lineamientos Relacionados
- [Diseño de APIs](/docs/fundamentos-corporativos/lineamientos/arquitectura/diseno-de-apis)

### Estándares Relacionados
- [Diseño REST](../apis/01-diseno-rest.md)
- [Versionado de APIs](../apis/04-versionado.md)
- [arc42](./01-arc42.md)

### ADRs Relacionados
- [ADR-002: Estándar de APIs REST](/docs/decisiones-de-arquitectura/adr-002-estandard-apis-rest)
- [ADR-017: Versionado de APIs](/docs/decisiones-de-arquitectura/adr-017-versionado-apis)

### Recursos Externos
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Swagger Documentation](https://swagger.io/docs/)
- [Spectral Rulesets](https://meta.stoplight.io/docs/spectral/4dec24461f3af-open-api-rules)

## 9. Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-08-08 | Equipo de Arquitectura | Versión inicial con template de 9 secciones |
