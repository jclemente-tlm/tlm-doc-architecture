---
id: formato-respuestas
sidebar_position: 3
title: Formato de Respuestas
description: Convención para formatos estándar de respuestas API
---

## 1. Principio

Las respuestas de API deben tener un formato consistente que facilite el manejo de éxitos, errores y paginación en clientes.

## 2. Reglas

### Regla 1: Respuestas Exitosas - Objeto Único

- **Formato**: JSON plano con el objeto directamente
- **Ejemplo correcto**:

```json
{
  "id": 123,
  "name": "Juan Pérez",
  "email": "juan.perez@talma.com",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

- **Ejemplo incorrecto**:

```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "Juan Pérez"
  }
}
```

### Regla 2: Respuestas Exitosas - Colecciones (sin paginación)

- **Formato**: Array directo

```json
[
  { "id": 1, "name": "Usuario 1" },
  { "id": 2, "name": "Usuario 2" }
]
```

### Regla 3: Respuestas con Paginación

- **Formato**: Envelope con metadata

```json
{
  "data": [
    { "id": 1, "name": "Usuario 1" },
    { "id": 2, "name": "Usuario 2" }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 156,
    "totalPages": 8
  },
  "links": {
    "self": "/api/v1/users?page=1&pageSize=20",
    "first": "/api/v1/users?page=1&pageSize=20",
    "prev": null,
    "next": "/api/v1/users?page=2&pageSize=20",
    "last": "/api/v1/users?page=8&pageSize=20"
  }
}
```

### Regla 4: Respuestas de Error (RFC 7807)

- **Formato**: Problem Details for HTTP APIs

```json
{
  "type": "https://api.talma.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "El campo 'email' es requerido",
  "instance": "/api/v1/users",
  "correlationId": "550e8400-e29b-41d4-a716-446655440000",
  "errors": {
    "email": ["El campo es requerido", "Debe ser un email válido"],
    "age": ["Debe ser mayor a 18"]
  }
}
```

### Regla 5: Códigos HTTP Estándar

| Código                    | Escenario                           | Response Body                     |
| ------------------------- | ----------------------------------- | --------------------------------- |
| 200 OK                    | Operación exitosa (GET, PUT, PATCH) | Objeto o array                    |
| 201 Created               | Recurso creado (POST)               | Objeto creado + header `Location` |
| 204 No Content            | Eliminación exitosa (DELETE)        | Sin body                          |
| 400 Bad Request           | Validación fallida                  | Problem Details                   |
| 401 Unauthorized          | No autenticado                      | Problem Details                   |
| 403 Forbidden             | No autorizado                       | Problem Details                   |
| 404 Not Found             | Recurso no encontrado               | Problem Details                   |
| 409 Conflict              | Conflicto (e.g., duplicado)         | Problem Details                   |
| 422 Unprocessable Entity  | Lógica de negocio fallida           | Problem Details                   |
| 500 Internal Server Error | Error del servidor                  | Problem Details                   |

## 3. Estructura de Errores Detallados

```json
{
  "type": "https://api.talma.com/errors/business-rule-violation",
  "title": "Business Rule Violation",
  "status": 422,
  "detail": "No se puede cancelar una orden ya entregada",
  "instance": "/api/v1/orders/123/cancel",
  "correlationId": "7f3d6b2a-8c1e-4d5f-9a2b-3c4d5e6f7890",
  "timestamp": "2024-01-15T10:30:00Z",
  "businessRuleCode": "ORDER_ALREADY_DELIVERED",
  "metadata": {
    "orderId": 123,
    "currentStatus": "delivered",
    "deliveredAt": "2024-01-10T15:20:00Z"
  }
}
```

## 4. Campos Comunes en Respuestas

### Campos Obligatorios en Errores

- ✅ `type` - URL del tipo de error
- ✅ `title` - Descripción breve
- ✅ `status` - Código HTTP
- ✅ `detail` - Mensaje específico
- ✅ `correlationId` - ID de trazabilidad

### Campos Opcionales

- `instance` - URI del request que falló
- `errors` - Errores de validación por campo
- `timestamp` - Cuándo ocurrió el error
- `metadata` - Información adicional contextual

## 5. Tabla de Referencia Rápida

| Escenario                       | Status | Body                                               |
| ------------------------------- | ------ | -------------------------------------------------- |
| Usuario creado                  | 201    | `{ "id": 123, "name": "..." }` + header `Location` |
| Usuario actualizado             | 200    | `{ "id": 123, "name": "..." }`                     |
| Usuario eliminado               | 204    | Sin body                                           |
| Lista usuarios (sin paginación) | 200    | `[{}, {}]`                                         |
| Lista usuarios (con paginación) | 200    | `{ "data": [], "pagination": {} }`                 |
| Validación fallida              | 400    | Problem Details con `errors`                       |
| No autorizado                   | 403    | Problem Details                                    |
| Usuario no encontrado           | 404    | Problem Details                                    |
| Email duplicado                 | 409    | Problem Details                                    |
| Regla de negocio fallida        | 422    | Problem Details con `businessRuleCode`             |

## 6. Headers de Respuesta

### Respuesta 201 Created

```http
HTTP/1.1 201 Created
Location: /api/v1/users/123
Content-Type: application/json

{
  "id": 123,
  "name": "Juan Pérez",
  "email": "juan.perez@talma.com"
}
```

### Respuesta 204 No Content

```http
HTTP/1.1 204 No Content
```

## 7. HATEOAS (Opcional)

Para APIs de nivel avanzado, incluir links hipermedia:

```json
{
  "id": 123,
  "name": "Juan Pérez",
  "status": "active",
  "links": {
    "self": { "href": "/api/v1/users/123" },
    "orders": { "href": "/api/v1/users/123/orders" },
    "deactivate": {
      "href": "/api/v1/users/123/deactivate",
      "method": "POST"
    }
  }
}
```

## 8. Herramientas de Validación

### Clase Problem Details (.NET)

```csharp
public class ProblemDetailsResponse
{
    public string Type { get; set; } = "about:blank";
    public string Title { get; set; }
    public int Status { get; set; }
    public string Detail { get; set; }
    public string Instance { get; set; }
    public string CorrelationId { get; set; }
    public Dictionary<string, string[]> Errors { get; set; }
}
```

### Middleware de Errores (.NET)

```csharp
app.UseExceptionHandler(builder =>
{
    builder.Run(async context =>
    {
        var exceptionFeature = context.Features.Get<IExceptionHandlerFeature>();
        var exception = exceptionFeature?.Error;

        var problemDetails = new ProblemDetailsResponse
        {
            Type = "https://api.talma.com/errors/internal-server-error",
            Title = "Internal Server Error",
            Status = 500,
            Detail = exception?.Message,
            Instance = context.Request.Path,
            CorrelationId = context.Request.Headers["X-Correlation-ID"]
        };

        context.Response.StatusCode = 500;
        await context.Response.WriteAsJsonAsync(problemDetails);
    });
});
```

### Middleware TypeScript

```typescript
export const errorHandler: ErrorRequestHandler = (err, req, res, next) => {
  const problemDetails = {
    type: "https://api.talma.com/errors/internal-server-error",
    title: "Internal Server Error",
    status: 500,
    detail: err.message,
    instance: req.path,
    correlationId: req.headers["x-correlation-id"],
    timestamp: new Date().toISOString(),
  };

  res.status(500).json(problemDetails);
};
```

## 📖 Referencias

### Estándares relacionados

- [Validación y Errores](/docs/fundamentos-corporativos/estandares/apis/validacion-y-errores)
- [Diseño REST](/docs/fundamentos-corporativos/estandares/apis/diseno-rest)

### Convenciones relacionadas

- [Headers HTTP](./02-headers-http.md)
- [Formato de Fechas](./04-formato-fechas-moneda.md)

### Recursos externos

- [RFC 7807 - Problem Details](https://datatracker.ietf.org/doc/html/rfc7807)
- [Microsoft REST API Guidelines - Responses](https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md#7102-error-condition-responses)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
