---
title: "Diseño y arquitectura de APIs"
sidebar_position: 1
---

Esta guía establece los principios fundamentales para el diseño de APIs REST bien estructuradas, escalables y mantenibles en Talma.

## 🎯 Principios de diseño

### RESTful design

- **Recursos como sustantivos**: Usar sustantivos para endpoints (`/users`, `/orders`)
- **Verbos HTTP apropiados**: GET, POST, PUT, DELETE, PATCH según la operación
- **Representación uniforme**: Consistencia en estructura de URLs y respuestas
- **Sin estado**: Cada request debe contener toda la información necesaria

### Naming conventions

```http
✅ CORRECTO
GET    /api/v1/users              # Obtener lista de usuarios
GET    /api/v1/users/123          # Obtener usuario específico
POST   /api/v1/users              # Crear nuevo usuario
PUT    /api/v1/users/123          # Actualizar usuario completo
PATCH  /api/v1/users/123          # Actualizar campos específicos
DELETE /api/v1/users/123          # Eliminar usuario

GET    /api/v1/users/123/orders   # Obtener órdenes del usuario
POST   /api/v1/users/123/orders   # Crear orden para el usuario

❌ INCORRECTO
GET    /api/v1/getUsers           # Verbo en URL
POST   /api/v1/user               # Singular en colección
GET    /api/v1/users/delete/123   # Verbo en lugar de método HTTP
```

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

## 📋 Estructura de respuesta estándar

### 📌 Elementos obligatorios

Toda respuesta debe incluir los siguientes atributos en la raíz:

- `status`: "success" o "error".
- `data`: objeto o arreglo; en caso de error debe ser `null`.
- `errors`: arreglo de errores; en éxito debe ser `[]`.
- `meta`: objeto que debe contener al menos `trace_id` y `timestamp`.

#### Atributos opcionales dentro de `meta`

- `tenant`: identificador del tenant (si aplica multi-tenant).
- `pagination`: información de paginación (por ejemplo: `page`, `size`, `total`).
- `links`: enlaces relacionados.
- `extra`: extensiones futuras (warnings, flags, etc.).

### ✅ Respuestas exitosas

#### Recurso único

```json
{
  "status": "success",
  "data": {
    "id": "123",
    "name": "Juan Pérez",
    "email": "juan.perez@talma.pe",
    "active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "errors": [],
  "meta": {
    "timestamp": "2024-01-15T10:30:01Z",
    "trace_id": "c1d2e3f4-5678-90ab-cdef-1234567890ab"
  }
}
```

#### Colección con paginación y atributos opcionales

```json
{
  "status": "success",
  "data": [
    {
      "id": "123",
      "name": "Juan Pérez",
      "email": "juan.perez@talma.pe",
      "active": true,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "124",
      "name": "Ana Gómez",
      "email": "ana.gomez@talma.pe",
      "active": true,
      "created_at": "2024-01-15T11:00:00Z"
    }
  ],
  "errors": [],
  "meta": {
    "timestamp": "2024-01-15T10:30:01Z",
    "trace_id": "a9b8c7d6-5432-10fe-dcba-0987654321ff",
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 150,
      "total_pages": 8
    },
    "links": {
      "self": "/api/v1/users?page=1",
      "next": "/api/v1/users?page=2",
      "last": "/api/v1/users?page=8"
    },
    "tenant": "talma-pe"
  }
}
```

### ❌ Respuestas de error

#### Error de validación

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
    "timestamp": "2024-01-15T10:30:01Z",
    "trace_id": "de9f8c7b-6543-21fe-cdba-123456789abc"
  }
}
```

#### Recurso no encontrado

```json
{
  "status": "error",
  "data": null,
  "errors": [
    {
      "code": "USER_NOT_FOUND",
      "message": "El usuario no existe",
      "details": [
        { "field": "id", "issue": "No se encontró ningún usuario con el identificador '999'" }
      ]
    }
  ],
  "meta": {
    "timestamp": "2024-01-15T10:30:01Z",
    "trace_id": "12ab34cd-5678-90ef-gh12-34567890abcd"
  }
}
```

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

## 🏗️ Implementación con ASP.NET Core

### Controller base pattern

```csharp
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    private readonly IMapper _mapper;

    public UsersController(IUserService userService, IMapper mapper)
    {
        _userService = userService;
        _mapper = mapper;
    }

    [HttpGet]
    [ProducesResponseType(typeof(PagedResponse<UserDto>), 200)]
    public async Task<ActionResult<PagedResponse<UserDto>>> GetUsers(
        [FromQuery] UserQuery query)
    {
        var users = await _userService.GetUsersAsync(query);

        var response = new PagedResponse<UserDto>
        {
            Status = "success",
            Data = _mapper.Map<IEnumerable<UserDto>>(users.Items),
            Meta = new MetaData
            {
                Pagination = new PaginationMeta
                {
                    Page = users.Page,
                    PerPage = users.PerPage,
                    Total = users.Total,
                    TotalPages = users.TotalPages
                }
            },
            Links = new Dictionary<string, string>
            {
                { "self", $"/api/v1/users?page={users.Page}" },
                { "next", users.HasNext ? $"/api/v1/users?page={users.Page + 1}" : null },
                { "last", $"/api/v1/users?page={users.TotalPages}" }
            }.Where(x => x.Value != null).ToDictionary(x => x.Key, x => x.Value),
            TraceId = HttpContext.TraceIdentifier
        };

        return Ok(response);
    }

    [HttpGet("{id}")]
    [ProducesResponseType(typeof(ApiResponse<UserDto>), 200)]
    [ProducesResponseType(typeof(ApiResponse<object>), 404)]
    public async Task<ActionResult<ApiResponse<UserDto>>> GetUser(string id)
    {
        var user = await _userService.GetUserByIdAsync(id);
        if (user == null)
        {
            var errorResponse = new ApiResponse<object>
            {
                Status = "error",
                Error = new ErrorInfo
                {
                    Code = "USER_NOT_FOUND",
                    Message = "El usuario no existe",
                    Details = new List<ErrorDetail>
                    {
                        new() { Field = "id", Issue = $"No se encontró ningún usuario con el identificador '{id}'" }
                    }
                },
                Meta = new MetaData(),
                TraceId = HttpContext.TraceIdentifier
            };

            return NotFound(errorResponse);
        }

        var response = new ApiResponse<UserDto>
        {
            Status = "success",
            Data = _mapper.Map<UserDto>(user),
            Meta = new MetaData(),
            TraceId = HttpContext.TraceIdentifier
        };

        return Ok(response);
    }

    [HttpPost]
    [ProducesResponseType(typeof(ApiResponse<UserDto>), 201)]
    [ProducesResponseType(typeof(ApiResponse<object>), 400)]
    public async Task<ActionResult<ApiResponse<UserDto>>> CreateUser(
        [FromBody] CreateUserRequest request)
    {
        if (!ModelState.IsValid)
        {
            var errorResponse = new ApiResponse<object>
            {
                Status = "error",
                Error = new ErrorInfo
                {
                    Code = "VALIDATION_FAILED",
                    Message = "La solicitud contiene errores de validación",
                    Details = ModelState.SelectMany(x => x.Value.Errors.Select(e => new ErrorDetail
                    {
                        Field = x.Key,
                        Issue = e.ErrorMessage
                    })).ToList()
                },
                Meta = new MetaData(),
                TraceId = HttpContext.TraceIdentifier
            };

            return BadRequest(errorResponse);
        }

        var user = await _userService.CreateUserAsync(request);
        var response = new ApiResponse<UserDto>
        {
            Status = "success",
            Data = _mapper.Map<UserDto>(user),
            Meta = new MetaData(),
            TraceId = HttpContext.TraceIdentifier
        };

        return CreatedAtAction(nameof(GetUser),
            new { id = user.Id }, response);
    }
}
```

### DTOs y modelos de respuesta

```csharp
public class ApiResponse<T>
{
    [JsonPropertyName("status")]
    public string Status { get; set; } = "success";
    [JsonPropertyName("data")]
    public T Data { get; set; } // null en error
    [JsonPropertyName("errors")]
    public List<ErrorInfo> Errors { get; set; } = new(); // [] en éxito
    [JsonPropertyName("meta")]
    public MetaData Meta { get; set; } = new();
}

public class MetaData
{
    [JsonPropertyName("trace_id")]
    public string TraceId { get; set; }
    [JsonPropertyName("timestamp")]
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    [JsonPropertyName("tenant")]
    public string Tenant { get; set; } // opcional
    [JsonPropertyName("pagination")]
    public PaginationMeta Pagination { get; set; } // opcional
    [JsonPropertyName("links")]
    public Dictionary<string, string> Links { get; set; } // opcional
    [JsonPropertyName("extra")]
    public object Extra { get; set; } // extensiones futuras
}

public class ErrorInfo
{
    [JsonPropertyName("code")]
    public string Code { get; set; }
    [JsonPropertyName("message")]
    public string Message { get; set; }
    [JsonPropertyName("details")]
    public List<ErrorDetail> Details { get; set; } = new();
}

public class ErrorDetail
{
    [JsonPropertyName("field")]
    public string Field { get; set; }
    [JsonPropertyName("issue")]
    public string Issue { get; set; }
}

public class PaginationMeta
{
    [JsonPropertyName("page")]
    public int Page { get; set; }
    [JsonPropertyName("size")]
    public int Size { get; set; }
    [JsonPropertyName("total")]
    public int Total { get; set; }
    [JsonPropertyName("total_pages")]
    public int TotalPages { get; set; }
}

public class UserDto
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    [JsonPropertyName("name")]
    public string Name { get; set; }
    [JsonPropertyName("email")]
    public string Email { get; set; }
    [JsonPropertyName("active")]
    public bool Active { get; set; }
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}

public class CreateUserRequest
{
    [Required]
    [StringLength(100, MinimumLength = 2)]
    [JsonPropertyName("name")]
    public string Name { get; set; }

    [Required]
    [EmailAddress]
    [JsonPropertyName("email")]
    public string Email { get; set; }

    [Phone]
    [JsonPropertyName("phone")]
    public string Phone { get; set; }
}
```

## 📖 Referencias

### ADRs relacionados

- [ADR-002: Estándar para APIs REST](/docs/adrs/adr-002-estandard-apis-rest)
- [ADR-017: Versionado de APIs](/docs/adrs/adr-017-versionado-apis)
- [ADR-008: Gateway de APIs](/docs/adrs/adr-008-gateway-apis)

### Recursos externos

- [REST API Design Best Practices](https://restfulapi.net/)
- [HTTP Status Code Registry](https://www.iana.org/assignments/http-status-codes/)
- [JSON:API Specification](https://jsonapi.org/)
