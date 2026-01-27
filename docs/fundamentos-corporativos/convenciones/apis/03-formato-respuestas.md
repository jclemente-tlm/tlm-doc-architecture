---
id: formato-respuestas
sidebar_position: 3
title: Formato de Respuestas
description: Convención para formatos estándar de respuestas API usando envelope pattern
---

## 1. Principio

Todas las respuestas de API deben usar un formato consistente tipo envelope que incluya status, data, errors y metadata para facilitar el manejo uniforme en clientes.

## 2. Estructura Base

### Elementos Obligatorios

Toda respuesta **debe** incluir los siguientes campos en la raíz:

- **`status`**: `"success"` o `"error"`
- **`data`**: Objeto o array con los datos; `null` en caso de error
- **`errors`**: Array de errores; `[]` vacío en caso de éxito
- **`meta`**: Objeto con metadata que debe contener al menos `traceId` y `timestamp`

### Elementos Opcionales en `meta`

- **`tenant`**: Identificador del tenant (para multi-tenancy)
- **`pagination`**: Información de paginación (`page`, `size`, `total`, `totalPages`)
- **`links`**: Enlaces HATEOAS relacionados
- **`extra`**: Extensiones futuras (warnings, flags, etc.)

## 3. Reglas

### Regla 1: Respuesta Exitosa - Objeto Único

```json
{
  "status": "success",
  "data": {
    "id": "123",
    "name": "Juan Pérez",
    "userName": "jperez",
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

### Regla 2: Respuesta Exitosa - Colección con Paginación

```json
{
  "status": "success",
  "data": [
    {
      "id": "123",
      "name": "Juan Pérez",
      "email": "juan.perez@talma.pe"
    },
    {
      "id": "124",
      "name": "Ana Gómez",
      "email": "ana.gomez@talma.pe"
    }
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

### Regla 3: Respuesta de Error - Validación

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
        { "field": "name", "issue": "Es un campo requerido" },
        { "field": "userName", "issue": "Es un campo requerido" }
      ]
    }
  ],
  "meta": {
    "traceId": "de9f8c7b-6543-21fe-cdba-123456789abc",
    "timestamp": "2024-01-15T10:30:01Z"
  }
}
```

### Regla 4: Respuesta de Error - Recurso No Encontrado

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "USER_NOT_FOUND",
      "message": "El usuario no existe",
      "details": [
        {
          "field": "id",
          "issue": "No se encontró ningún usuario con el identificador '999'"
        }
      ]
    }
  ],
  "meta": {
    "traceId": "12ab34cd-5678-90ef-gh12-34567890abcd",
    "timestamp": "2024-01-15T10:30:01Z"
  }
}
```

### Regla 5: Códigos HTTP Estándar

| Código                    | Escenario                           | Envelope Status | Data  | Errors |
| ------------------------- | ----------------------------------- | --------------- | ----- | ------ |
| 200 OK                    | Operación exitosa (GET, PUT, PATCH) | `success`       | Datos | `[]`   |
| 201 Created               | Recurso creado (POST)               | `success`       | Datos | `[]`   |
| 204 No Content            | Eliminación exitosa (DELETE)        | N/A             | N/A   | N/A    |
| 400 Bad Request           | Validación fallida                  | `error`         | null  | Array  |
| 401 Unauthorized          | No autenticado                      | `error`         | null  | Array  |
| 403 Forbidden             | No autorizado                       | `error`         | null  | Array  |
| 404 Not Found             | Recurso no encontrado               | `error`         | null  | Array  |
| 409 Conflict              | Conflicto (duplicado)               | `error`         | null  | Array  |
| 422 Unprocessable Entity  | Lógica de negocio fallida           | `error`         | null  | Array  |
| 500 Internal Server Error | Error del servidor                  | `error`         | null  | Array  |

**Nota**: `204 No Content` no devuelve body, por lo tanto no usa envelope.

## 4. Tabla de Referencia Rápida

| Escenario                | Status | Body                                        |
| ------------------------ | ------ | ------------------------------------------- |
| Usuario creado           | 201    | `{status, data, errors, meta}` + `Location` |
| Usuario actualizado      | 200    | `{status, data, errors, meta}`              |
| Usuario eliminado        | 204    | Sin body                                    |
| Lista usuarios paginada  | 200    | `{status, data, errors, meta.pagination}`   |
| Validación fallida       | 400    | `{status:"error", data:null, errors:[...]}` |
| No autorizado            | 403    | `{status:"error", data:null, errors:[...]}` |
| Usuario no encontrado    | 404    | `{status:"error", data:null, errors:[...]}` |
| Email duplicado          | 409    | `{status:"error", data:null, errors:[...]}` |
| Regla de negocio fallida | 422    | `{status:"error", data:null, errors:[...]}` |

## 5. Estructura Detallada de Errores

### Error de Lógica de Negocio

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "ORDER_ALREADY_DELIVERED",
      "message": "No se puede cancelar una orden ya entregada",
      "details": [
        {
          "field": "orderId",
          "issue": "La orden 123 fue entregada el 2024-01-10"
        }
      ]
    }
  ],
  "meta": {
    "traceId": "7f3d6b2a-8c1e-4d5f-9a2b-3c4d5e6f7890",
    "timestamp": "2024-01-15T10:30:00Z",
    "extra": {
      "orderId": 123,
      "currentStatus": "delivered",
      "deliveredAt": "2024-01-10T15:20:00Z"
    }
  }
}
```

## 6. Headers HTTP Importantes

### Header Location en 201 Created

```http
HTTP/1.1 201 Created
Location: /api/v1/users/123
Content-Type: application/json

{
  "status": "success",
  "data": {
    "id": 123,
    "name": "Juan Pérez"
  },
  "errors": [],
  "meta": {
    "traceId": "...",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Código 204 Sin Body

```http
HTTP/1.1 204 No Content
```

## 7. Implementación .NET

### DTOs de Respuesta

```csharp
public class ApiResponse<T>
{
    public string Status { get; set; } = "success";
    public T Data { get; set; }
    public List<ErrorInfo> Errors { get; set; } = new();
    public MetaData Meta { get; set; } = new();
}

public class MetaData
{
    public string TraceId { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string Tenant { get; set; }
    public PaginationMeta Pagination { get; set; }
    public Dictionary<string, string> Links { get; set; }
    public object Extra { get; set; }
}

public class ErrorInfo
{
    public string Code { get; set; }
    public string Message { get; set; }
    public List<ErrorDetail> Details { get; set; } = new();
}

public class ErrorDetail
{
    public string Field { get; set; }
    public string Issue { get; set; }
}

public class PaginationMeta
{
    public int Page { get; set; }
    public int Size { get; set; }
    public int Total { get; set; }
    public int TotalPages { get; set; }
}
```

### Ejemplo de Controller

```csharp
[HttpGet("{id}")]
[ProducesResponseType(typeof(ApiResponse<UserDto>), 200)]
[ProducesResponseType(typeof(ApiResponse<object>), 404)]
public async Task<ActionResult<ApiResponse<UserDto>>> GetUser(string id)
{
    var user = await _userService.GetUserByIdAsync(id);

    if (user == null)
    {
        return NotFound(new ApiResponse<object>
        {
            Status = "error",
            Data = null,
            Errors = new List<ErrorInfo>
            {
                new ErrorInfo
                {
                    Code = "USER_NOT_FOUND",
                    Message = "El usuario no existe",
                    Details = new List<ErrorDetail>
                    {
                        new() { Field = "id", Issue = $"No se encontró usuario '{id}'" }
                    }
                }
            },
            Meta = new MetaData { TraceId = HttpContext.TraceIdentifier }
        });
    }

    return Ok(new ApiResponse<UserDto>
    {
        Status = "success",
        Data = _mapper.Map<UserDto>(user),
        Errors = new List<ErrorInfo>(),
        Meta = new MetaData { TraceId = HttpContext.TraceIdentifier }
    });
}
```

## 8. Implementación TypeScript

### Tipos de Respuesta

```typescript
export interface ApiResponse<T> {
  status: "success" | "error";
  data: T | null;
  errors: ErrorInfo[];
  meta: MetaData;
}

export interface MetaData {
  traceId: string;
  timestamp: string;
  tenant?: string;
  pagination?: PaginationMeta;
  links?: Record<string, string>;
  extra?: any;
}

export interface ErrorInfo {
  code: string;
  message: string;
  details: ErrorDetail[];
}

export interface ErrorDetail {
  field: string;
  issue: string;
}

export interface PaginationMeta {
  page: number;
  size: number;
  total: number;
  totalPages: number;
}
```

### Ejemplo de Handler

```typescript
export const getUser = async (req: Request, res: Response) => {
  const { id } = req.params;
  const user = await userService.getUserById(id);

  if (!user) {
    return res.status(404).json({
      status: "error",
      data: null,
      errors: [
        {
          code: "USER_NOT_FOUND",
          message: "El usuario no existe",
          details: [{ field: "id", issue: `No se encontró usuario '${id}'` }],
        },
      ],
      meta: {
        traceId: req.headers["x-trace-id"] || uuidv4(),
        timestamp: new Date().toISOString(),
      },
    });
  }

  return res.status(200).json({
    status: "success",
    data: user,
    errors: [],
    meta: {
      traceId: req.headers["x-trace-id"] || uuidv4(),
      timestamp: new Date().toISOString(),
    },
  });
};
```

## 6. Headers HTTP Importantes

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

## 7. Checklist

- [ ] Respuestas exitosas usan estructura envelope con `status`, `data`, `errors`, `meta`
- [ ] Errores siguen RFC 7807 Problem Details
- [ ] Paginación incluye metadata completa (`page`, `size`, `total`, `totalPages`)
- [ ] camelCase en todos los campos JSON
- [ ] Fechas en formato ISO 8601 UTC
- [ ] Montos en formato decimal (2 decimales)
- [ ] Arrays vacíos en lugar de null
- [ ] Códigos HTTP correctos según operación
- [ ] `traceId` presente en todas las respuestas
- [ ] Documentación actualizada en OpenAPI/Swagger

## 8. Referencias

### Estándares Relacionados

- [Validación y Errores](../../estandares/apis/03-validacion-y-errores.md) - RFC 7807 y FluentValidation
- [Diseño REST](../../estandares/apis/01-diseno-rest.md) - Estructura de APIs
- [Performance](../../estandares/apis/05-performance.md) - Paginación y caching

### Lineamientos Relacionados

- [Diseño de APIs](../../lineamientos/arquitectura/06-diseno-de-apis.md) - Lineamientos de diseño

### Principios Relacionados

- [Contratos de Comunicación](../../principios/arquitectura/06-contratos-de-comunicacion.md) - Contratos estables
- [Simplicidad Intencional](../../principios/arquitectura/07-simplicidad-intencional.md) - Respuestas simples

### Otras Convenciones

- [Headers HTTP](./02-headers-http.md) - Convenciones de headers
- [Formato Fechas y Moneda](./04-formato-fechas-moneda.md) - Formatos de datos específicos
- [Naming Endpoints](./01-naming-endpoints.md) - Nomenclatura de recursos

### Documentación Externa

- [Microsoft REST API Guidelines - Responses](https://github.com/microsoft/api-guidelines/blob/vNext/Guidelines.md)
- [JSON API Specification](https://jsonapi.org/)
- [RFC 7807 - Problem Details](https://www.rfc-editor.org/rfc/rfc7807)

---

**Última revisión**: 26 de enero 2026  
**Responsable**: Equipo de Arquitectura
