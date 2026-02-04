---
id: api-rest
sidebar_position: 1
title: APIs REST
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

## 8. Convenciones de Nomenclatura de Endpoints

### 8.1. Estructura Base

- **Formato**: `/api/v{version}/{recurso}[/{id}][/{sub-recurso}]`
- **Ejemplo**: `/api/v1/users`, `/api/v1/users/123`, `/api/v1/users/123/orders`

### 8.2. Nombres de Recursos en Plural

- **Formato**: Sustantivos en plural, kebab-case
- **Ejemplo**: `/api/v1/users`, `/api/v1/order-items`, `/api/v1/payment-methods`

### 8.3. Kebab-Case para Recursos Compuestos

- **Formato**: `kebab-case` (palabras separadas por guiones)
- **Ejemplo**: `/api/v1/order-items`, `/api/v1/payment-methods`, `/api/v1/user-profiles`

### 8.4. Sub-recursos y Relaciones

- **Formato**: `/{recurso}/{id}/{sub-recurso}`
- **Ejemplo**: `/api/v1/users/123/orders`, `/api/v1/orders/456/items`

### 8.5. Acciones No-CRUD (Excepciones)

- **Formato**: `POST /{recurso}/{id}/{accion}`
- **Ejemplo**: `POST /api/v1/orders/123/cancel`, `POST /api/v1/users/456/activate`

### 8.6. Filtrado, Ordenamiento y Búsqueda

Usar query parameters, **no** incluir en path:

- **Formato**: `GET /{recurso}?{filter}&{sort}`
- **Ejemplo**: `/api/v1/users?status=active&sort=createdAt`

### 8.7. Mapeo HTTP Methods

| Operación           | Method | Endpoint            | Respuesta           |
| ------------------- | ------ | ------------------- | ------------------- |
| Listar todos        | GET    | `/api/v1/users`     | 200 + array         |
| Obtener uno         | GET    | `/api/v1/users/123` | 200 + objeto        |
| Crear               | POST   | `/api/v1/users`     | 201 + objeto creado |
| Actualizar completo | PUT    | `/api/v1/users/123` | 200 + objeto        |
| Actualizar parcial  | PATCH  | `/api/v1/users/123` | 200 + objeto        |
| Eliminar            | DELETE | `/api/v1/users/123` | 204 sin body        |

---

## 9. Convenciones de Headers HTTP

### 9.1. Headers Obligatorios de Trazabilidad

| Header             | Propósito                               | Formato | Generado por          |
| ------------------ | --------------------------------------- | ------- | --------------------- |
| `X-Correlation-ID` | Tracking end-to-end de request          | UUID v4 | API Gateway o Cliente |
| `X-Request-ID`     | ID único del request individual         | UUID v4 | API Gateway           |
| `X-Tenant-ID`      | Identificador de tenant (multi-tenancy) | String  | Cliente autenticado   |

```http
GET /api/v1/users HTTP/1.1
Host: api.talma.com
X-Correlation-ID: 550e8400-e29b-41d4-a716-446655440000
X-Request-ID: 7f3d6b2a-8c1e-4d5f-9a2b-3c4d5e6f7890
X-Tenant-ID: tlm-pe
Authorization: Bearer eyJhbGc...
```

### 9.2. Headers de Autenticación

- **Formato**: `Authorization: Bearer {token}`
- **Ejemplo**: `Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5...`

### 9.3. Headers de Content Negotiation

| Header            | Uso                        | Valores                               |
| ----------------- | -------------------------- | ------------------------------------- |
| `Content-Type`    | Tipo de contenido enviado  | `application/json`, `application/xml` |
| `Accept`          | Tipo de contenido esperado | `application/json`, `application/xml` |
| `Accept-Language` | Idioma preferido           | `es-ES`, `en-US`                      |
| `Accept-Encoding` | Compresión aceptada        | `gzip`, `deflate`, `br`               |

### 9.4. Headers de Rate Limiting

| Header                  | Propósito                | Ejemplo      |
| ----------------------- | ------------------------ | ------------ |
| `X-RateLimit-Limit`     | Límite total de requests | `1000`       |
| `X-RateLimit-Remaining` | Requests restantes       | `243`        |
| `X-RateLimit-Reset`     | Timestamp de reset       | `1672531200` |
| `Retry-After`           | Segundos para reintentar | `3600`       |

### 9.5. Headers de Seguridad

| Header                      | Propósito              | Valor                                 |
| --------------------------- | ---------------------- | ------------------------------------- |
| `Strict-Transport-Security` | HSTS                   | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options`    | Prevenir MIME sniffing | `nosniff`                             |
| `X-Frame-Options`           | Prevenir clickjacking  | `DENY` o `SAMEORIGIN`                 |
| `X-XSS-Protection`          | XSS protection         | `1; mode=block`                       |

---

## 10. Convenciones de Formato de Respuestas

### 10.1. Estructura Base Envelope

Toda respuesta **debe** incluir:

- **`status`**: `"success"` o `"error"`
- **`data`**: Objeto o array con los datos; `null` en caso de error
- **`errors`**: Array de errores; `[]` vacío en caso de éxito
- **`meta`**: Objeto con `traceId` y `timestamp`

### 10.2. Respuesta Exitosa - Objeto Único

```json
{
  "status": "success",
  "data": {
    "id": "123",
    "name": "Juan Pérez",
    "email": "juan.perez@talma.pe",
    "active": true,
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "errors": [],
  "meta": {
    "traceId": "c1d2e3f4-5678-90ab-cdef-1234567890ab",
    "timestamp": "2024-01-15T10:30:01Z"
  }
}
```

### 10.3. Respuesta Exitosa - Colección con Paginación

```json
{
  "status": "success",
  "data": [
    { "id": "123", "name": "Juan Pérez" },
    { "id": "124", "name": "Ana Gómez" }
  ],
  "errors": [],
  "meta": {
    "traceId": "a9b8c7d6-5432-10fe-dcba-0987654321ff",
    "timestamp": "2024-01-15T10:30:01Z",
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 150,
      "totalPages": 8
    },
    "links": {
      "self": "/api/v1/users?page=1",
      "next": "/api/v1/users?page=2",
      "last": "/api/v1/users?page=8"
    },
    "tenant": "tlm-pe"
  }
}
```

### 10.4. Respuesta de Error - Validación

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_FAILED",
      "message": "La solicitud contiene errores de validación",
      "details": [
        { "field": "email", "issue": "El formato no es válido" },
        { "field": "name", "issue": "Es un campo requerido" }
      ]
    }
  ],
  "meta": {
    "traceId": "de9f8c7b-6543-21fe-cdba-123456789abc",
    "timestamp": "2024-01-15T10:30:01Z"
  }
}
```

---

## 11. Convenciones de Fechas y Moneda

### 11.1. Fechas y Horas en ISO 8601 UTC

- **Formato**: `YYYY-MM-DDTHH:mm:ss.sssZ`
- **Ejemplo**: `"2024-01-15T10:30:00.000Z"`
- **Zona Horaria**: Siempre UTC (terminar en `Z`)

```json
{
  "createdAt": "2024-01-15T10:30:00.000Z",
  "updatedAt": "2024-01-15T14:45:30.123Z"
}
```

### 11.2. Solo Fecha (sin hora)

- **Formato**: `YYYY-MM-DD`
- **Ejemplo**: `"2024-01-15"`

```json
{
  "birthDate": "1985-03-20",
  "expirationDate": "2024-12-31"
}
```

### 11.3. Moneda con Código ISO 4217

- **Formato**: Objeto con `amount` (decimal) + `currency` (código ISO)

```json
{
  "price": {
    "amount": 1234.56,
    "currency": "PEN"
  }
}
```

### 11.4. Porcentajes como Decimal

- **Formato**: Número decimal (1.00 = 100%)
- **Ejemplo**: `0.15` para 15%, `1.00` para 100%

```json
{
  "taxRate": 0.18, // 18% IGV
  "discountRate": 0.1 // 10% descuento
}
```

### 11.5. Tabla de Formatos de Datos

| Tipo de Dato | Formato                    | Ejemplo                                    |
| ------------ | -------------------------- | ------------------------------------------ |
| Fecha y hora | `YYYY-MM-DDTHH:mm:ss.sssZ` | `"2024-01-15T10:30:00.000Z"`               |
| Solo fecha   | `YYYY-MM-DD`               | `"2024-01-15"`                             |
| Moneda       | `{ amount, currency }`     | `{ "amount": 1234.56, "currency": "PEN" }` |
| Porcentaje   | Decimal                    | `0.18` (= 18%)                             |
| Booleano     | `true`/`false`             | `true`                                     |

---

## 12. Referencias

- [API Security](./api-security.md) - Autenticación y autorización
- [Versioning](./versioning.md) - Versionado de APIs
- [Error Handling](./error-handling.md) - Validación y errores
- [C# y .NET](../codigo/csharp-dotnet.md) - DTOs y mapeo
- [ASP.NET Core Web API](https://learn.microsoft.com/aspnet/core/web-api/)
- [REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)
- [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html)
- [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html)
