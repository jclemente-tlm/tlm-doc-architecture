---
id: rest-conventions
sidebar_position: 1
title: Convenciones REST
description: Estándar de convenciones REST para diseño de APIs con ASP.NET Core, URIs, verbos HTTP, JSON y DTOs
---

# Estándar Técnico — Convenciones REST

---

## 1. Propósito

Definir convenciones REST fundamentales para APIs con ASP.NET Core 8.0+: URIs de recursos, verbos HTTP semánticos, JSON camelCase, status codes apropiados y uso de DTOs.

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

| Componente        | Tecnología            | Versión mínima | Observaciones           |
| ----------------- | --------------------- | -------------- | ----------------------- |
| **Framework**     | ASP.NET Core          | 8.0+           | Framework base de API   |
| **Serialización** | System.Text.Json      | 8.0+           | JSON camelCase built-in |
| **Mapeo**         | Mapster               | 7.4+           | Mapeo DTOs ↔ entidades  |
| **Protocolo**     | HTTPS/TLS 1.3, HTTP/2 | -              | TLS 1.3 mínimo          |

> Para versionado ver [Versioning](./versioning.md), para seguridad ver [API Security](./api-security.md), para validación ver [Error Handling](./error-handling.md).

---

## 4. Requisitos Obligatorios 🔴

### Convenciones de URIs

- [ ] Recursos en plural: `/api/v1/users`, `/api/v1/orders`
- [ ] Nombres en minúsculas con guiones: `/api/v1/purchase-orders`
- [ ] Identificadores al final: `/api/v1/users/{id}`
- [ ] Subrecursos anidados: `/api/v1/users/{id}/orders`
- [ ] NO verbos en URIs (usar métodos HTTP)

### Métodos HTTP

- [ ] `GET` para lectura (idempotente, sin side effects)
- [ ] `POST` para creación (retorna 201 + Location header)
- [ ] `PUT` para actualización completa (idempotente)
- [ ] `PATCH` para actualización parcial
- [ ] `DELETE` para eliminación (idempotente, retorna 204)

### Formato JSON

- [ ] JSON camelCase para request/response
- [ ] Omitir propiedades `null` en responses
- [ ] Fechas en formato ISO 8601 UTC: `"2024-01-15T10:30:00Z"`
- [ ] Enumeraciones como strings (no números)

### Status Codes HTTP

- [ ] `200 OK` - GET exitoso con body
- [ ] `201 Created` - POST exitoso (incluir Location header)
- [ ] `204 No Content` - PUT/DELETE/PATCH exitoso sin body
- [ ] `400 Bad Request` - Validación falló
- [ ] `401 Unauthorized` - Sin autenticación
- [ ] `403 Forbidden` - Sin autorización
- [ ] `404 Not Found` - Recurso no existe
- [ ] `500 Internal Server Error` - Error del servidor

### DTOs (Data Transfer Objects)

- [ ] DTOs separados para requests/responses
- [ ] NO exponer entidades de dominio directamente
- [ ] Validación en DTOs de entrada
- [ ] Mapeo explícito DTO ↔ Entidad

### Health Checks

- [ ] Endpoint `/health/live` para liveness (proceso activo)
- [ ] Endpoint `/health/ready` para readiness (deps disponibles)

---

## 5. Prohibiciones

- ❌ Exponer entidades de dominio directamente en responses
- ❌ Verbos en URIs (`/api/v1/getUser`, `/api/v1/createOrder`)
- ❌ Status codes genéricos (usar códigos semánticos)
- ❌ Nombres de recursos en singular (`/api/v1/user`)
- ❌ Propiedades PascalCase en JSON (usar camelCase)
- ❌ Fechas en formatos no estándar
- ❌ HTTP sin TLS (usar HTTPS siempre)

---

## 6. Configuración Mínima

```csharp
// Program.cs - Configuración básica REST
var builder = WebApplication.CreateBuilder(args);

// JSON camelCase
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    });

var app = builder.Build();

app.UseHttpsRedirection();
app.MapControllers();
app.Run();
```

### Ejemplo de Controller RESTful

```csharp
[ApiController]
[Route("api/v1/users")]
public class UsersController : ControllerBase
{
    private readonly IUserService _service;
    private readonly IMapper _mapper;

    // GET /api/v1/users
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<UserDto>), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetUsers()
    {
        var users = await _service.GetAllAsync();
        return Ok(_mapper.Map<IEnumerable<UserDto>>(users));
    }

    // GET /api/v1/users/{id}
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetUser(Guid id)
    {
        var user = await _service.GetByIdAsync(id);
        if (user == null) return NotFound();
        return Ok(_mapper.Map<UserDto>(user));
    }

    // POST /api/v1/users
    [HttpPost]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateUser([FromBody] CreateUserRequest request)
    {
        var user = await _service.CreateAsync(request);
        var dto = _mapper.Map<UserDto>(user);
        return CreatedAtAction(nameof(GetUser), new { id = dto.Id }, dto);
    }

    // PUT /api/v1/users/{id}
    [HttpPut("{id}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> UpdateUser(Guid id, [FromBody] UpdateUserRequest request)
    {
        var exists = await _service.ExistsAsync(id);
        if (!exists) return NotFound();
        await _service.UpdateAsync(id, request);
        return NoContent();
    }

    // DELETE /api/v1/users/{id}
    [HttpDelete("{id}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> DeleteUser(Guid id)
    {
        var exists = await _service.ExistsAsync(id);
        if (!exists) return NotFound();
        await _service.DeleteAsync(id);
        return NoContent();
    }
}
```

### Ejemplo de DTOs

```csharp
// Response DTO
public record UserDto
{
    public Guid Id { get; init; }
    public string Email { get; init; }
    public string FirstName { get; init; }
    public string LastName { get; init; }
    public DateTime CreatedAt { get; init; }
}

// Request DTO
public record CreateUserRequest
{
    public string Email { get; init; }
    public string FirstName { get; init; }
    public string LastName { get; init; }
}
```

---

## 7. Validación

```bash
# Verificar JSON camelCase
curl https://api.talma.com/api/v1/users | jq .

# Verificar status codes
curl -I https://api.talma.com/api/v1/users
curl -I -X POST https://api.talma.com/api/v1/users

# Verificar health checks
curl https://api.talma.com/health/live
curl https://api.talma.com/health/ready

# Tests unitarios
dotnet test --filter Category=REST
```

**Métricas de cumplimiento:**

| Métrica                 | Target | Verificación                         |
| ----------------------- | ------ | ------------------------------------ |
| Responses camelCase     | 100%   | Verificar JSON output                |
| URIs en plural          | 100%   | Revisar rutas                        |
| Status codes apropiados | 100%   | POST retorna 201, DELETE retorna 204 |
| DTOs en uso             | 100%   | No entidades expuestas               |

---

## 8. Referencias

- [API Security](./api-security.md) - Autenticación y autorización
- [Versioning](./versioning.md) - Versionado de APIs
- [Error Handling](./error-handling.md) - Validación y errores
- [ASP.NET Core Web API](https://learn.microsoft.com/aspnet/core/web-api/)
- [REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)
