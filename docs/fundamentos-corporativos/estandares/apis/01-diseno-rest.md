---
id: diseno-rest
sidebar_position: 1
title: Diseño REST
description: Principios fundamentales para diseño de APIs REST estructuradas, escalables y mantenibles
---

# Diseño REST

Esta guía establece los principios fundamentales para el diseño de APIs REST bien estructuradas, escalables y mantenibles en Talma.

## 🎯 Principios de diseño

### RESTful design

- **Recursos como sustantivos**: Usar sustantivos para endpoints (`/users`, `/orders`)
- **Verbos HTTP apropiados**: GET, POST, PUT, DELETE, PATCH según la operación
- **Representación uniforme**: Consistencia en estructura de URLs y respuestas
- **Sin estado**: Cada request debe contener toda la información necesaria

> Para convenciones de naming de endpoints, consulta [Convenciones - Naming Endpoints](/docs/fundamentos-corporativos/convenciones/apis/naming-endpoints).

## 📊 Estructura de recursos

### Jerarquía de recursos

```text
/api/v1/companies/{company-id}
├── /users                    # Usuarios de la compañía
├── /departments              # Departamentos
│   └── /{dept-id}/employees  # Empleados del departamento
└── /projects                 # Proyectos de la compañía
    └── /{project-id}/tasks   # Tareas del proyecto
```

### Paginación y filtros

```http
GET /api/v1/users?page=1&limit=20&sort=name&order=asc
GET /api/v1/users?filter[department]=IT&filter[active]=true
GET /api/v1/users?search=juan&fields=id,name,email
```

> Para estructura de respuesta JSON (envelope, errores, paginación), consulta [Convenciones - Formato de Respuestas](/docs/fundamentos-corporativos/convenciones/apis/formato-respuestas).

## 🔧 Códigos de estado HTTP

### Uso apropiado de status codes

```text
2xx Success
200 OK          - Operación exitosa con datos
201 Created     - Recurso creado exitosamente
204 No Content  - Operación exitosa sin datos de respuesta

4xx Client Error
400 Bad Request        - Request malformado o datos inválidos
401 Unauthorized       - Autenticación requerida
403 Forbidden         - Usuario autenticado sin permisos
404 Not Found         - Recurso no encontrado
409 Conflict          - Conflicto con estado actual del recurso
422 Unprocessable     - Datos válidos pero lógica de negocio falla

5xx Server Error
500 Internal Server Error - Error interno no especificado
502 Bad Gateway          - Error de gateway/proxy
503 Service Unavailable  - Servicio temporalmente no disponible
```

## 🏗️ Tecnologías y Herramientas Obligatorias

### ASP.NET Core Web API

**Versión mínima**: 8.0+

**Librerías requeridas**:

- `Microsoft.AspNetCore.Mvc.Versioning` (5.0+) - API Versioning
- `Microsoft.AspNetCore.Mvc.Versioning.ApiExplorer` (5.0+) - API Explorer
- `AutoMapper` (12.0+) - Mapeo de DTOs
- `Swashbuckle.AspNetCore` (6.5+) - Documentación OpenAPI

**Configuración obligatoria**:

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Controllers con versionado
builder.Services.AddControllers();
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
});

// JSON camelCase
builder.Services.Configure<JsonOptions>(options =>
{
    options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});

// HTTPS
builder.Services.AddHttpsRedirection(options =>
{
    options.RedirectStatusCode = StatusCodes.Status308PermanentRedirect;
    options.HttpsPort = 443;
});

var app = builder.Build();

// HTTPS obligatorio
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

### Seguridad y Autenticación

**HTTPS/TLS**: Versión mínima TLS 1.3
**JWT**: Algoritmo RS256 obligatorio
**OAuth 2.0**: Para autenticación de usuarios

```csharp
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
            ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 }
        };
    });
```

### Validación

**FluentValidation**: 11.0+
Obligatorio para validación de entrada (ver [Validación y Errores](/docs/fundamentos-corporativos/estandares/apis/validacion-y-errores))

```csharp
builder.Services.AddValidatorsFromAssemblyContaining<Program>();
```

### Documentación OpenAPI

**Swashbuckle**: 6.5+

```csharp
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Talma API",
        Version = "v1",
        Description = "API REST de Talma"
    });

    // JWT Bearer
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header usando Bearer scheme",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.Http,
        Scheme = "bearer"
    });
});
```

## 📖 Referencias

### Convenciones relacionadas

- [Convenciones - Naming Endpoints](/docs/fundamentos-corporativos/convenciones/apis/naming-endpoints) - Nombres de endpoints, recursos, verbos HTTP
- [Convenciones - Formato de Respuestas](/docs/fundamentos-corporativos/convenciones/apis/formato-respuestas) - Estructura JSON envelope, errores, paginación

### Lineamientos relacionados

- [Desarrollo de APIs](/docs/fundamentos-corporativos/lineamientos/desarrollo/desarrollo-de-apis)
- [Desacoplamiento](/docs/fundamentos-corporativos/lineamientos/arquitectura/desacoplamiento)

### ADRs relacionados

- [ADR-002: Estándar para APIs REST](/docs/adrs/adr-002-estandard-apis-rest)
- [ADR-017: Versionado de APIs](/docs/adrs/adr-017-versionado-apis)
- [ADR-008: Gateway de APIs](/docs/adrs/adr-008-gateway-apis)

### Recursos externos

- [REST API Design Best Practices](https://restfulapi.net/)
- [HTTP Status Code Registry](https://www.iana.org/assignments/http-status-codes/)
- [JSON:API Specification](https://jsonapi.org/)
