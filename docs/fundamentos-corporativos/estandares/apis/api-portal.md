---
id: api-portal
sidebar_position: 10
title: Portal de Desarrolladores
description: Portal de desarrolladores con Swagger UI, OpenAPI 3.1, documentación interactiva, ejemplos de código y autenticación
---

# Estándar Técnico — Portal de Desarrolladores

---

## 1. Propósito

Establecer un portal de desarrolladores centralizado con Swagger UI, OpenAPI 3.1+, documentación interactiva, ejemplos ejecutables, guías de integración y autenticación OAuth2, accesible en `/swagger` y `/docs`.

---

## 2. Alcance

**Aplica a:**

- APIs REST públicas y privadas
- Documentación interactiva de endpoints
- Portal de desarrolladores centralizado
- Guías de integración y quick-start
- Sandbox/playground para testing

**No aplica a:**

- APIs internas experimentales (no públicas)
- Documentación de arquitectura (usar arc42)
- Documentación de código interno (usar XML docs)

---

## 3. Tecnologías Aprobadas

| Componente   | Tecnología             | Versión mínima | Observaciones                |
| ------------ | ---------------------- | -------------- | ---------------------------- |
| **Spec**     | OpenAPI                | 3.1+           | Especificación formal        |
| **UI**       | Swashbuckle.AspNetCore | 6.5+           | Swagger UI + generación spec |
| **Portal**   | Docusaurus             | 3.0+           | Portal estático de docs      |
| **Ejemplos** | Redocly                | -              | Alternativa a Swagger UI     |
| **Testing**  | Swagger UI Try-It-Out  | -              | Consola interactiva          |
| **Hosting**  | AWS S3 + CloudFront    | -              | CDN estático                 |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Documentación OpenAPI

- [ ] Spec OpenAPI 3.1+ generado automáticamente
- [ ] `info` con versión, título, descripción, contacto
- [ ] `servers` con URLs de dev, staging, production
- [ ] `components/schemas` para todos los DTOs
- [ ] `components/securitySchemes` para OAuth2/JWT
- [ ] `tags` para agrupar endpoints por módulo
- [ ] Descripciones detalladas en cada endpoint
- [ ] Ejemplos de request/response en cada operación
- [ ] Status codes documentados (200, 400, 401, 404, 500)

### Swagger UI

- [ ] Interfaz en `/swagger` (desarrollo) y `/docs` (producción)
- [ ] Try-it-out habilitado en desarrollo
- [ ] Try-it-out deshabilitado en producción (solo lectura)
- [ ] Autenticación OAuth2 integrada en UI
- [ ] Temas personalizados con branding corporativo
- [ ] Deep linking a endpoints específicos

### Portal de Desarrolladores

- [ ] Landing page con quick-start guide
- [ ] Guías de autenticación (OAuth2, API Keys)
- [ ] Ejemplos de código (C#, Python, JavaScript)
- [ ] Changelog de versiones
- [ ] Status page de APIs (uptime)
- [ ] Sandbox/playground para testing
- [ ] Contacto de soporte técnico

### Contenido Mínimo

- [ ] Descripción de cada endpoint (qué hace)
- [ ] Parámetros con tipos, formatos y validaciones
- [ ] Respuestas con schemas completos
- [ ] Ejemplos realistas de payloads
- [ ] Rate limits documentados
- [ ] Códigos de error con descripciones

---

## 5. Prohibiciones

- ❌ Swagger UI en producción con Try-it-out habilitado (seguridad)
- ❌ Specs OpenAPI sin ejemplos
- ❌ Documentación desactualizada vs código
- ❌ Exponer endpoints internos en portal público
- ❌ Credenciales hardcoded en ejemplos
- ❌ Documentación sin versionado

---

## 6. Configuración Mínima

```csharp
// Program.cs
using Microsoft.OpenApi.Models;

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Version = "v1",
        Title = "Talma API",
        Description = "API corporativa de Talma para gestión de recursos",
        Contact = new OpenApiContact
        {
            Name = "Arquitectura Talma",
            Email = "arquitectura@talma.com",
            Url = new Uri("https://docs.talma.com")
        },
        License = new OpenApiLicense
        {
            Name = "Uso interno Talma",
        }
    });

    // JWT Bearer auth
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

    // XML comments
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);

    // Ejemplos
    options.EnableAnnotations();
    options.ExampleFilters();
});

builder.Services.AddSwaggerExamplesFromAssemblyOf<Program>();

var app = builder.Build();

// Solo en desarrollo
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "Talma API v1");
        options.RoutePrefix = "swagger";
        options.DocumentTitle = "Talma API - Documentación";
        options.EnableTryItOutByDefault();
    });
}
```

```csharp
// Controller con documentación XML
/// <summary>
/// Gestión de usuarios del sistema
/// </summary>
[ApiController]
[Route("api/v1/users")]
[Produces("application/json")]
public class UsersController : ControllerBase
{
    /// <summary>
    /// Obtiene todos los usuarios del sistema
    /// </summary>
    /// <remarks>
    /// Ejemplo de request:
    ///
    ///     GET /api/v1/users
    ///
    /// </remarks>
    /// <returns>Lista de usuarios activos</returns>
    /// <response code="200">Lista de usuarios retornada exitosamente</response>
    /// <response code="401">No autenticado</response>
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<UserDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetUsers()
    {
        var users = await _service.GetAllAsync();
        return Ok(users);
    }

    /// <summary>
    /// Crea un nuevo usuario
    /// </summary>
    /// <param name="request">Datos del usuario a crear</param>
    /// <returns>Usuario creado</returns>
    /// <response code="201">Usuario creado exitosamente</response>
    /// <response code="400">Datos de entrada inválidos</response>
    [HttpPost]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateUser([FromBody] CreateUserRequest request)
    {
        var user = await _service.CreateAsync(request);
        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }
}
```

```csharp
// Ejemplo de request con Swashbuckle.AspNetCore.Filters
public class CreateUserRequestExample : IExamplesProvider<CreateUserRequest>
{
    public CreateUserRequest GetExamples()
    {
        return new CreateUserRequest
        {
            Email = "juan.perez@talma.com",
            FirstName = "Juan",
            LastName = "Pérez",
            Role = "Developer"
        };
    }
}
```

```xml
<!-- .csproj - Habilitar XML documentation -->
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <NoWarn>$(NoWarn);1591</NoWarn>
</PropertyGroup>

<ItemGroup>
  <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
  <PackageReference Include="Swashbuckle.AspNetCore.Annotations" Version="6.5.0" />
  <PackageReference Include="Swashbuckle.AspNetCore.Filters" Version="7.0.12" />
</ItemGroup>
```

---

## 7. Ejemplos

### Portal de Desarrolladores (Docusaurus)

````mdx
---
title: Quick Start
---

# Quick Start - Talma API

## 1. Obtener API Key

Solicita tu API key en el [portal de desarrolladores](https://developers.talma.com).

## 2. Autenticación

```bash
curl -X POST https://auth.talma.com/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_SECRET"
```
````

## 3. Primera llamada

```bash
curl https://api.talma.com/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## SDKs disponibles

- [C# SDK](https://github.com/talma/talma-dotnet-sdk)
- [Python SDK](https://github.com/talma/talma-python-sdk)
- [JavaScript SDK](https://github.com/talma/talma-js-sdk)

````

### OpenAPI spec con ejemplos

```yaml
openapi: 3.1.0
info:
  title: Talma API
  version: 1.0.0
  contact:
    email: arquitectura@talma.com
servers:
  - url: https://api.talma.com
    description: Producción
  - url: https://api-staging.talma.com
    description: Staging
paths:
  /api/v1/users:
    post:
      summary: Crear usuario
      tags:
        - Users
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            examples:
              developer:
                summary: Crear desarrollador
                value:
                  email: juan.perez@talma.com
                  firstName: Juan
                  lastName: Pérez
                  role: Developer
      responses:
        '201':
          description: Usuario creado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserDto'
              examples:
                success:
                  value:
                    id: 550e8400-e29b-41d4-a716-446655440000
                    email: juan.perez@talma.com
                    firstName: Juan
                    lastName: Pérez
                    role: Developer
                    createdAt: '2024-01-15T10:30:00Z'
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    CreateUserRequest:
      type: object
      required:
        - email
        - firstName
        - lastName
      properties:
        email:
          type: string
          format: email
          example: juan.perez@talma.com
        firstName:
          type: string
          minLength: 2
          maxLength: 50
          example: Juan
````

---

## 8. Validación y Auditoría

```bash
# Verificar OpenAPI spec válido
curl https://api.talma.com/swagger/v1/swagger.json | \
  docker run --rm -i openapitools/openapi-generator-cli validate -i -

# Verificar ejemplos en spec
curl https://api.talma.com/swagger/v1/swagger.json | jq '.paths | .. | .examples? | select(. != null)'

# Generar cliente desde spec
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate \
  -i https://api.talma.com/swagger/v1/swagger.json \
  -g csharp \
  -o /local/generated-client

# Auditar documentación
npx @redocly/cli lint https://api.talma.com/swagger/v1/swagger.json
```

**Métricas de cumplimiento:**

| Métrica                   | Umbral                  | Verificación                 |
| ------------------------- | ----------------------- | ---------------------------- |
| Endpoints documentados    | 100%                    | Comparar spec vs routes      |
| Ejemplos en endpoints     | 100%                    | Verificar `examples` en spec |
| Documentación actualizada | Sincronizada con código | CI/CD checks                 |
| Portal accesible          | 99.9% uptime            | Health checks                |
| Tiempo de carga portal    | <2s                     | Performance monitoring       |

---

## 9. Referencias

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Swashbuckle Documentation](https://github.com/domaindrivendev/Swashbuckle.AspNetCore)
- [Docusaurus](https://docusaurus.io/)
- [Redocly](https://redocly.com/)
- [Stripe API Docs](https://stripe.com/docs/api) (ejemplo excelencia)
- [Twilio API Docs](https://www.twilio.com/docs/usage/api) (ejemplo excelencia)
- [Azure API Documentation Best Practices](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design)
