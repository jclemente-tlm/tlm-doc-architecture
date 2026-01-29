---
id: diseno-rest
sidebar_position: 1
title: Diseño REST
description: Estándar para diseño de APIs REST con ASP.NET Core, versionado, autenticación y documentación OpenAPI
---

# Estándar Técnico — Diseño REST

---

## 1. Propósito
Definir implementación técnica de APIs REST con ASP.NET Core 8.0+, JSON camelCase, versionado URL, autenticación JWT, validación FluentValidation y documentación OpenAPI/Swagger.

---

## 2. Alcance

**Aplica a:**
- APIs REST públicas y privadas
- Microservicios con HTTP endpoints
- Backend-for-Frontend (BFF) APIs

**No aplica a:**
- APIs GraphQL (estándar separado)
- gRPC services
- WebSockets

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Framework** | ASP.NET Core | 8.0+ | Framework base de API |
| **API Gateway** | Kong | 3.5+ | Gestión centralizada de APIs |
| **IAM** | Keycloak | 23.0+ | Autenticación y autorización |
| **Versionado** | AspNetCore.Mvc.Versioning | 5.0+ | URL versioning (v1, v2) |
| **Documentación** | Swashbuckle.AspNetCore | 6.5+ | OpenAPI/Swagger |
| **Validación** | FluentValidation.AspNetCore | 11.0+ | Validación entrada |
| **Mapeo** | Mapster | 7.4+ | Mapeo de objetos (DTOs) |
| **Autenticación** | AspNetCore.Authentication.JwtBearer | 8.0+ | JWT Bearer |
| **Logging** | Serilog.AspNetCore | 8.0+ | Logging estructurado |
| **Protocolo** | HTTPS/TLS 1.3, HTTP/2 | - | TLS 1.3 mínimo |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] JSON camelCase para request/response
- [ ] Versionado URL: `/api/v1/users`, `/api/v2/users`
- [ ] Autenticación JWT Bearer obligatoria (excepto endpoints públicos documentados)
- [ ] Validación FluentValidation en controllers
- [ ] Responses con status codes HTTP semánticos (200, 201, 400, 401, 404, 500)
- [ ] HTTPS/TLS 1.3 en todos los entornos
- [ ] CORS configurado explícitamente (NO permitir `*` en prod)
- [ ] Rate limiting por IP/usuario configurado
- [ ] Health checks en `/health/live` y `/health/ready`
- [ ] OpenAPI/Swagger con autenticación JWT configurada
- [ ] Logging estructurado con correlation IDs
- [ ] DTOs para requests/responses (NO exponer entidades de dominio)

---

## 5. Prohibiciones

- ❌ Exponer entidades de dominio directamente en responses
- ❌ CORS con `AllowAnyOrigin()` en producción
- ❌ HTTP sin TLS (usar HTTPS siempre)
- ❌ Versionado en query string o headers (usar URL)
- ❌ Validación manual con `if` (usar FluentValidation)
- ❌ Status codes genéricos (usar 201 Created, 204 NoContent, etc.)

---

## 6. Configuración Mínima

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// JSON camelCase
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    });

// Versionado
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ApiVersionReader = new UrlSegmentApiVersionReader();
});

// FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<Program>();
builder.Services.AddFluentValidationAutoValidation();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

```csharp
// Controller ejemplo
[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/users")]
public class UsersController : ControllerBase
{
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetUser(Guid id)
    {
        var user = await _service.GetUserAsync(id);
        return user == null ? NotFound() : Ok(user);
    }
}
```

---

## 7. Validación

```bash
# Verificar versionado
curl https://api.talma.com/api/v1/users

# Verificar autenticación JWT
curl -H "Authorization: Bearer <token>" https://api.talma.com/api/v1/users

# Verificar Swagger
curl https://api.talma.com/swagger/v1/swagger.json

# Verificar health checks
curl https://api.talma.com/health/ready

# Tests de integración
dotnet test --filter Category=API
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Endpoints con JWT | 100% | Excepto `/health`, `/swagger` |
| Responses camelCase | 100% | Verificar JSON output |
| HTTPS habilitado | 100% | `curl -I` retorna 308 redirect |
| Swagger documentado | 100% | `/swagger` accesible |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-004: Autenticación SSO](../../../decisiones-de-arquitectura/adr-004-keycloak-sso-autenticacion.md)
- [Seguridad de APIs](./02-seguridad-apis.md)
- [Versionado de APIs](./04-versionado.md)
- [OpenAPI/Swagger](../../documentacion/03-openapi-swagger.md)
- [ASP.NET Core Web API](https://learn.microsoft.com/aspnet/core/web-api/)
- [REST API Guidelines](https://github.com/microsoft/api-guidelines)
