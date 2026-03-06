---
id: api-rest-standards
sidebar_position: 1
title: Estándares de APIs REST
description: Principios REST, convenciones HTTP, estructura de URIs, filtrado y búsqueda, wrapper de respuesta estándar y códigos de estado para APIs consistentes.
tags: [apis, rest, http, uri, status-codes, response-wrapper, filtering]
---

# Estándares de APIs REST

## Contexto

Este estándar define los principios REST y convenciones HTTP base para toda API de la organización. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Cuándo aplicar:** Siempre. Es la base obligatoria de toda API REST, independientemente del dominio.

---

## Stack Tecnológico

| Componente        | Tecnología       | Versión | Uso                  |
| ----------------- | ---------------- | ------- | -------------------- |
| **Framework**     | ASP.NET Core     | 8.0+    | Construcción de APIs |
| **Serialización** | System.Text.Json | 8.0+    | JSON serialization   |
| **Mapeo**         | Mapster          | 7.3+    | DTOs ↔ entidades     |

---

## Principios REST

**Restricciones fundamentales:**

- **Recursos como sustantivos**: Usar sustantivos para endpoints (`/users`, `/orders`)
- **Verbos HTTP apropiados**: GET, POST, PUT, DELETE, PATCH según la operación
- **Representación uniforme**: Consistencia en estructura de URLs y respuestas
- **Sin estado**: Cada request debe contener toda la información necesaria
- **Respuestas cacheables**: Usar headers HTTP de caché (`Cache-Control`, `ETag`) cuando aplique

**Verbos HTTP:**

| Verbo  | Uso                   | Idempotente | Safe |
| ------ | --------------------- | ----------- | ---- |
| GET    | Leer recursos         | ✅          | ✅   |
| POST   | Crear recursos        | ❌          | ❌   |
| PUT    | Reemplazar recurso    | ✅          | ❌   |
| PATCH  | Actualización parcial | ❌          | ❌   |
| DELETE | Eliminar recurso      | ✅          | ❌   |

**Códigos de Estado:**

| Código | Significado           | Uso                                   |
| ------ | --------------------- | ------------------------------------- |
| 200    | OK                    | GET/PUT exitoso                       |
| 201    | Created               | POST exitoso, recurso creado          |
| 204    | No Content            | DELETE exitoso, sin body              |
| 400    | Bad Request           | Datos inválidos                       |
| 401    | Unauthorized          | Falta autenticación                   |
| 403    | Forbidden             | Sin permisos                          |
| 404    | Not Found             | Recurso no existe                     |
| 409    | Conflict              | Conflicto de estado (duplicado, etc.) |
| 422    | Unprocessable Entity  | Validación de negocio falló           |
| 429    | Too Many Requests     | Rate limit excedido                   |
| 500    | Internal Server Error | Error no controlado                   |
| 503    | Service Unavailable   | Servicio no disponible temporalmente  |

---

## Estructura de URIs

```csharp
// ✅ BUENO: Sustantivos en plural, jerarquía clara
GET    /api/v1/customers
GET    /api/v1/customers/{id}
POST   /api/v1/customers
PUT    /api/v1/customers/{id}
DELETE /api/v1/customers/{id}
PATCH  /api/v1/customers/{id}

// Recursos anidados (máximo 2 niveles)
GET    /api/v1/customers/{customerId}/orders
GET    /api/v1/customers/{customerId}/orders/{orderId}

// Acciones no-CRUD (verbos cuando sea inevitable)
POST   /api/v1/orders/{id}/cancel
POST   /api/v1/orders/{id}/ship
POST   /api/v1/invoices/{id}/send

// ❌ MALO: Verbos en URI
POST   /api/v1/createCustomer
GET    /api/v1/getCustomers

// ❌ MALO: Anidamiento excesivo
GET    /api/v1/customers/{id}/orders/{orderId}/items/{itemId}/details
```

### Jerarquía de un dominio

Representación de la estructura de recursos para un dominio completo:

```
/api/v1/companies/{companyId}
├── /users                           # Usuarios de la compañía
├── /departments                     # Departamentos
│   └── /{departmentId}/employees    # Empleados del departamento
└── /orders                          # Órdenes de la compañía
    └── /{orderId}/items             # Ítems de la orden
```

---

## Filtrado y Búsqueda

Query params estandarizados para colecciones GET. Usar la convención `filter[campo]` para filtros exactos.

### Parámetros disponibles

| Parámetro       | Ejemplo                 | Descripción                               |
| --------------- | ----------------------- | ----------------------------------------- |
| `filter[campo]` | `filter[status]=active` | Filtro exacto por campo                   |
| `search`        | `search=acme`           | Búsqueda de texto libre (multi-campo)     |
| `fields`        | `fields=id,name,email`  | Proyección: reduce campos en la respuesta |
| `sort`          | `sort=createdAt`        | Campo por el que ordenar                  |
| `order`         | `order=desc`            | Dirección: `asc` (default) o `desc`       |

### Ejemplos de uso

```
# Filtros exactos
GET /api/v1/customers?filter[status]=active&filter[country]=PE

# Búsqueda de texto libre
GET /api/v1/customers?search=acme corp

# Proyección de campos (payload reducido)
GET /api/v1/customers?fields=id,name,email

# Ordenamiento
GET /api/v1/customers?sort=createdAt&order=desc

# Combinado con paginación
GET /api/v1/customers?filter[status]=active&sort=name&order=asc&page=1&pageSize=20
```

### Implementación C\#

```csharp
public record CustomerFilterRequest
{
    [FromQuery(Name = "filter[status]")]  public string? Status  { get; init; }
    [FromQuery(Name = "filter[country]")] public string? Country { get; init; }
    [FromQuery] public string? Search { get; init; }
    [FromQuery] public string? Fields { get; init; }
    [FromQuery] public string  Sort   { get; init; } = "createdAt";
    [FromQuery] public string  Order  { get; init; } = "asc";
}

[HttpGet]
[ProducesResponseType(typeof(ApiResponse<CustomerDto[]>), StatusCodes.Status200OK)]
public async Task<ActionResult<ApiResponse<CustomerDto[]>>> GetAll(
    [FromQuery] CustomerFilterRequest filter,
    [FromQuery] int page     = 1,
    [FromQuery] int pageSize = 20)
{
    var result = await _customerService.GetFilteredAsync(filter, page, pageSize);
    return Ok(new ApiResponse<CustomerDto[]>
    {
        Status = "success",
        Data   = result.Items,
        Meta   = new MetaData
        {
            TraceId    = HttpContext.TraceIdentifier,
            Pagination = new PaginationMeta
            {
                Page       = result.Page,
                Size       = result.PageSize,
                Total      = result.TotalCount,
                TotalPages = result.TotalPages
            }
        }
    });
}
```

---

## Estructura de Respuesta

Toda API en Talma usa el wrapper `ApiResponse<T>` como shape uniforme para éxito y error.

### Elementos obligatorios

| Campo    | Tipo          | En éxito       | En error    | Descripción                  |
| -------- | ------------- | -------------- | ----------- | ---------------------------- |
| `status` | `string`      | `"success"`    | `"error"`   | Estado de la operación       |
| `data`   | `T` / `null`  | Objeto o array | `null`      | Datos de la respuesta        |
| `errors` | `ErrorInfo[]` | `[]`           | Con errores | Detalle de errores           |
| `meta`   | `MetaData`    | Obligatorio    | Obligatorio | Contexto, traceId, timestamp |

### Atributos de `meta`

| Campo        | Obligatorio | Descripción                                          |
| ------------ | ----------- | ---------------------------------------------------- |
| `traceId`    | ✅          | Identificador para trazabilidad                      |
| `timestamp`  | ✅          | Fecha/hora UTC de la respuesta                       |
| `tenant`     | Opcional    | País/tenant (`tlm-pe`, `tlm-ec`, `tlm-co`, `tlm-mx`) |
| `pagination` | Opcional    | Metadata de paginación (solo en colecciones)         |
| `links`      | Opcional    | Links de navegación                                  |
| `extra`      | Opcional    | Extensiones futuras (warnings, flags)                |

### Modelos C\#

```csharp
public class ApiResponse<T>
{
    public string Status { get; set; } = "success";
    public T? Data { get; set; }
    public List<ErrorInfo> Errors { get; set; } = new();
    public MetaData Meta { get; set; } = new();

    public static ApiResponse<T> Success(T data, MetaData? meta = null) =>
        new() { Status = "success", Data = data, Meta = meta ?? new() };
}

public class MetaData
{
    public string TraceId { get; set; } = default!;
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string? Tenant { get; set; }           // tlm-pe, tlm-ec, tlm-co, tlm-mx
    public PaginationMeta? Pagination { get; set; }
    public Dictionary<string, string>? Links { get; set; }
    public object? Extra { get; set; }
}

public class ErrorInfo
{
    public string Code { get; set; } = default!;
    public string Message { get; set; } = default!;
    public List<ErrorDetail> Details { get; set; } = new();
}

public class ErrorDetail
{
    public string Field { get; set; } = default!;
    public string Issue { get; set; } = default!;
}

public class PaginationMeta
{
    public int Page { get; set; }
    public int Size { get; set; }
    public int Total { get; set; }
    public int TotalPages { get; set; }
}
```

### Respuesta exitosa — recurso único

```json
{
  "status": "success",
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Acme Corporation",
    "email": "contact@acme.com",
    "active": true,
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "errors": [],
  "meta": {
    "traceId": "c1d2e3f4-5678-90ab-cdef-1234567890ab",
    "timestamp": "2024-01-15T10:30:01Z",
    "tenant": "tlm-pe"
  }
}
```

### Respuesta exitosa — colección paginada

```json
{
  "status": "success",
  "data": [
    { "id": "3fa85f64", "name": "Acme Corporation", "active": true },
    { "id": "4bc96a75", "name": "Beta Corp", "active": true }
  ],
  "errors": [],
  "meta": {
    "traceId": "a9b8c7d6-5432-10fe-dcba-0987654321ff",
    "timestamp": "2024-01-15T10:30:01Z",
    "tenant": "tlm-pe",
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 150,
      "totalPages": 8
    },
    "links": {
      "self": "/api/v1/customers?page=1",
      "next": "/api/v1/customers?page=2",
      "last": "/api/v1/customers?page=8"
    }
  }
}
```

> Para el shape de error ver [Manejo de Errores en APIs](./api-error-handling.md).
> Para estrategias de paginación (offset, cursor, keyset) ver [Paginación de APIs](./api-pagination.md).

---

## Implementación

```csharp
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[Produces("application/json")]
public class CustomersController : ControllerBase
{
    private readonly ICustomerService _customerService;
    private readonly ILogger<CustomersController> _logger;

    public CustomersController(
        ICustomerService customerService,
        ILogger<CustomersController> logger)
    {
        _customerService = customerService;
        _logger = logger;
    }

    [HttpGet]
    [ProducesResponseType(typeof(ApiResponse<CustomerDto[]>), StatusCodes.Status200OK)]
    public async Task<ActionResult<ApiResponse<CustomerDto[]>>> GetAll(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var result = await _customerService.GetPagedAsync(page, pageSize);
        return Ok(new ApiResponse<CustomerDto[]>
        {
            Status = "success",
            Data   = result.Items,
            Meta   = new MetaData
            {
                TraceId    = HttpContext.TraceIdentifier,
                Pagination = new PaginationMeta
                {
                    Page       = result.Page,
                    Size       = result.PageSize,
                    Total      = result.TotalCount,
                    TotalPages = result.TotalPages
                },
                Links = new Dictionary<string, string>
                {
                    ["self"] = $"/api/v1/customers?page={result.Page}",
                    ["next"] = result.HasNextPage ? $"/api/v1/customers?page={result.Page + 1}" : null!,
                    ["last"] = $"/api/v1/customers?page={result.TotalPages}"
                }.Where(x => x.Value != null).ToDictionary(x => x.Key, x => x.Value)
            }
        });
    }

    [HttpGet("{id}")]
    [ProducesResponseType(typeof(ApiResponse<CustomerDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ApiResponse<CustomerDto>>> GetById(Guid id)
    {
        var customer = await _customerService.GetByIdAsync(id);
        if (customer is null)
            throw new NotFoundException(nameof(Customer), id); // Manejado por middleware
        return Ok(ApiResponse<CustomerDto>.Success(
            customer,
            new MetaData { TraceId = HttpContext.TraceIdentifier }));
    }

    [HttpPost]
    [ProducesResponseType(typeof(ApiResponse<CustomerDto>), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<ApiResponse<CustomerDto>>> Create([FromBody] CreateCustomerRequest request)
    {
        var customer = await _customerService.CreateAsync(request);
        var response = ApiResponse<CustomerDto>.Success(
            customer,
            new MetaData { TraceId = HttpContext.TraceIdentifier });
        return CreatedAtAction(nameof(GetById), new { id = customer.Id }, response);
    }

    [HttpPut("{id}")]
    [ProducesResponseType(typeof(ApiResponse<CustomerDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ApiResponse<CustomerDto>>> Update(Guid id, [FromBody] UpdateCustomerRequest request)
    {
        var customer = await _customerService.UpdateAsync(id, request);
        if (customer is null)
            throw new NotFoundException(nameof(Customer), id);
        return Ok(ApiResponse<CustomerDto>.Success(
            customer,
            new MetaData { TraceId = HttpContext.TraceIdentifier }));
    }

    [HttpDelete("{id}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(typeof(ApiResponse<object>), StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Delete(Guid id)
    {
        var deleted = await _customerService.DeleteAsync(id);
        if (!deleted) throw new NotFoundException(nameof(Customer), id);
        return NoContent();
    }
}
```

---

## Configuración Global

```csharp
// Program.cs
builder.Services.AddControllers(options =>
{
    options.ReturnHttpNotAcceptable = true;
})
.AddJsonOptions(options =>
{
    options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
});

// Registro del middleware de excepciones que retorna ApiResponse<object>
builder.Services.AddExceptionHandler<ApiExceptionHandler>();
builder.Services.AddProblemDetails(); // Solo para compatibilidad con ASP.NET Core pipeline
```

---

## Beneficios en Práctica

| Sin estándares REST                             | Con estándares REST                                        |
| ----------------------------------------------- | ---------------------------------------------------------- |
| URIs inconsistentes (`/getUser`, `/deleteUser`) | URIs predecibles (`GET /users/{id}`, `DELETE /users/{id}`) |
| Códigos de estado arbitrarios                   | Semántica HTTP correcta                                    |
| Respuestas no cacheables                        | Cache HTTP funciona correctamente                          |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar verbos HTTP correctamente (GET=read, POST=create, PUT=replace, PATCH=update, DELETE=delete)
- **MUST** usar códigos de estado HTTP apropiados
- **MUST** usar sustantivos en plural para URIs de colecciones (`/customers`, no `/customer`)
- **MUST** retornar JSON como formato por defecto
- **MUST** implementar idempotencia para PUT y DELETE
- **MUST** usar `ApiResponse<T>` como wrapper de respuesta en todos los endpoints
- **MUST** incluir `meta.traceId` en toda respuesta
- **MUST** retornar `data: null` y `errors` con contenido en respuestas de error

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar ETags para caching
- **SHOULD** soportar compresión (gzip, brotli)
- **SHOULD** implementar rate limiting
- **SHOULD** incluir CORS para APIs públicas
- **SHOULD** incluir headers de trazabilidad (X-Request-ID, X-Correlation-ID)

### MAY (Opcional)

- **MAY** soportar múltiples formatos de respuesta (JSON, XML) via content negotiation
- **MAY** incluir API health checks (`/health`, `/ready`)
- **MAY** soportar filtrado, ordenamiento y búsqueda en colecciones (ver [Filtrado y Búsqueda](#filtrado-y-búsqueda))

### MUST NOT (Prohibido)

- **MUST NOT** usar verbos en URIs (`/getCustomers`, `/createOrder`)
- **MUST NOT** usar códigos de estado genéricos (evitar siempre 200 con error en body)
- **MUST NOT** exponer detalles de implementación interna, stack traces ni información sensible en URIs o respuestas

---

## Monitoreo y Observabilidad

:::note Métricas de APIs
Para métricas de requests (latencia, status codes, throughput) ver [Métricas y Estándares](../observabilidad/metrics.md).
:::

---

## Referencias

- [RFC 9110 - HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) — Semántica HTTP
- [RFC 9457 - Problem Details](https://www.rfc-editor.org/rfc/rfc9457.html) — Problem Details (referencia para estructura de errores)
- [ASP.NET Core Web APIs](https://learn.microsoft.com/aspnet/core/web-api/) — Documentación oficial
- [REST API Design Rulebook (O'Reilly)](https://www.oreilly.com/library/view/rest-api-design/9781449317904/) — Patrones REST
- [Contratos de APIs](./api-contracts.md) — Estándar relacionado
- [Manejo de Errores en APIs](./api-error-handling.md) — Estándar relacionado
