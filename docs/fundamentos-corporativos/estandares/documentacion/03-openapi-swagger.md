---
id: openapi-swagger
sidebar_position: 3
title: Documentación de APIs con OpenAPI
description: Estándares para documentar APIs REST usando OpenAPI 3.1+, Swagger UI 5.0+ y Spectral
---

# Estándar Técnico — Documentación de APIs con OpenAPI

---

## 1. Propósito
Garantizar documentación interactiva de APIs REST usando OpenAPI 3.1+, generada automáticamente con Swashbuckle.AspNetCore 6.5+, validada con Spectral y publicada en Swagger UI 5.0+.

---

## 2. Alcance

**Aplica a:**
- APIs REST públicas (clientes externos)
- APIs REST internas (microservicios)
- APIs gateway (Kong, AWS API Gateway)
- SDKs generados desde OpenAPI

**No aplica a:**
- APIs gRPC (usar Protocol Buffers .proto)
- APIs GraphQL (usar Schema Definition Language)
- WebSockets/SignalR (documentar en arc42)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Spec** | OpenAPI Specification | 3.1+ | YAML/JSON |
| **UI** | Swagger UI | 5.0+ | Interfaz interactiva |
| **Generator** | Swashbuckle.AspNetCore | 6.5+ | ASP.NET Core |
| **Linter** | Spectral | 6.11+ | Validación reglas |
| **Client Gen** | NSwag | 14.0+ | Clientes C# |
| **Alternativa** | Redoc | 2.1+ | Documentación estática |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] OpenAPI 3.1+ generado automáticamente
- [ ] Swashbuckle.AspNetCore 6.5+ (.NET)
- [ ] Swagger UI habilitado en `/api-docs`
- [ ] Información de contacto y licencia
- [ ] XML comments (C#) para descripciones
- [ ] ProducesResponseType para cada endpoint
- [ ] Esquemas de seguridad (Bearer JWT)
- [ ] Versionado en URL (`/api/v1/users`)
- [ ] Ejemplos de request/response
- [ ] Validación con Spectral (CI/CD)
- [ ] Generación de clientes con NSwag
- [ ] Publicación en portal de desarrolladores

---

## 5. Prohibiciones

- ❌ Documentación manual desactualizada
- ❌ OpenAPI <3.0 (usar 3.1+)
- ❌ Endpoints sin ejemplos de response
- ❌ Schemas genéricos sin propiedades
- ❌ Swagger UI deshabilitado en producción
- ❌ Secrets/tokens en ejemplos
- ❌ Descripciones vacías

---

## 6. Configuración Mínima

### C# con Swashbuckle
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
        Description = "Gestión de usuarios, autenticación y autorización",
        Contact = new OpenApiContact
        {
            Name = "Arquitectura",
            Email = "arquitectura@talma.com"
        }
    });

    // XML comments
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);

    // JWT Security
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization: Bearer {token}",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.Http,
        Scheme = "bearer",
        BearerFormat = "JWT"
    });
});

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/swagger/v1/swagger.json", "Talma Users API v1");
    options.RoutePrefix = "api-docs";
});

app.Run();
```

```xml
<!-- .csproj -->
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <NoWarn>$(NoWarn);1591</NoWarn>
</PropertyGroup>
```

```csharp
/// <summary>
/// Obtiene un usuario por su ID
/// </summary>
/// <param name="userId">ID único del usuario (UUID)</param>
/// <response code="200">Usuario encontrado</response>
/// <response code="404">Usuario no encontrado</response>
[HttpGet("{userId:guid}")]
[ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
[ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
public async Task<ActionResult<UserDto>> GetUser(Guid userId)
{
    // ...
}
```

### Validación con Spectral
```yaml
# .spectral.yaml
extends: [["spectral:oas", "all"]]
rules:
  operation-description: error
  operation-operationId: error
  operation-tags: error
  no-$ref-siblings: error
```

```bash
# Validar OpenAPI spec
spectral lint swagger.json
```

---

## 7. Validación

```bash
# Generar OpenAPI desde app
curl http://localhost:5000/swagger/v1/swagger.json > swagger.json

# Validar con Spectral
spectral lint swagger.json

# Generar cliente C#
nswag openapi2csclient /input:swagger.json /output:clients/UsersClient.cs
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| OpenAPI 3.1+ | 100% | `"openapi": "3.1.0"` |
| Endpoints documentados | 100% | Swagger UI |
| XML comments | 100% | C# controllers |
| Spectral validation | 0 errors | CI/CD pipeline |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [arc42](01-arc42.md)
- [C4 Model](02-c4-model.md)
- [Diseño REST](../apis/01-diseno-rest.md)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Swashbuckle](https://github.com/domaindrivendev/Swashbuckle.AspNetCore)
- [Spectral](https://stoplight.io/open-source/spectral)
