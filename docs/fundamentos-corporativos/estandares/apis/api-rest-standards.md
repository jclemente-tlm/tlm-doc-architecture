---
id: api-rest-standards
sidebar_position: 1
title: Estándares REST APIs
description: Estándar completo de APIs REST con ASP.NET Core - diseño, seguridad, documentación, versionado, validación, performance y observabilidad
---

# Estándar Técnico — APIs REST Completo

---

## 1. Propósito

Establecer estándares completos para APIs REST con ASP.NET Core 8.0+: diseño RESTful, seguridad JWT/OAuth2, documentación OpenAPI, versionado, validación de contratos, manejo de errores, performance, rate limiting, paginación y deprecación.

---

## 2. Alcance

**Aplica a:**

- APIs REST públicas y privadas
- Microservicios con HTTP endpoints
- Backend-for-Frontend (BFF) APIs
- Portal de desarrolladores y documentación
- Contratos de API y versionado

**No aplica a:**

- APIs GraphQL (estándar separado)
- gRPC services
- WebSockets

---

## 3. Tecnologías Aprobadas

| Componente           | Tecnología             | Versión mínima | Observaciones             |
| -------------------- | ---------------------- | -------------- | ------------------------- |
| **Framework**        | ASP.NET Core           | 8.0+           | Framework base de API     |
| **Serialización**    | System.Text.Json       | 8.0+           | JSON camelCase built-in   |
| **Mapeo**            | Mapster                | 7.4+           | Mapeo DTOs ↔ entidades    |
| **Validación**       | FluentValidation       | 11.9+          | Validación declarativa    |
| **Autenticación**    | Microsoft.Identity     | 8.0+           | JWT Bearer + OAuth2       |
| **Documentación**    | Swashbuckle.AspNetCore | 6.5+           | OpenAPI/Swagger           |
| **Versionado**       | Asp.Versioning.Http    | 8.0+           | Versionado de APIs        |
| **Rate Limiting**    | AspNetCoreRateLimit    | 5.0+           | Control de tráfico        |
| **Contract Testing** | Pact                   | 4.0+           | Consumer-driven contracts |
| **Protocolo**        | HTTPS/TLS 1.3, HTTP/2  | -              | TLS 1.3 mínimo            |

---

## 4. Diseño RESTful

### 4.1. Convenciones de URIs

- Recursos en plural: `/api/v1/users`, `/api/v1/orders`
- Nombres en minúsculas con guiones: `/api/v1/purchase-orders`
- Identificadores al final: `/api/v1/users/{id}`
- Subrecursos anidados: `/api/v1/users/{id}/orders`
- NO verbos en URIs (usar métodos HTTP)

### 4.2. Métodos HTTP

- `GET` - Lectura (idempotente, sin side effects)
- `POST` - Creación (retorna 201 + Location header)
- `PUT` - Actualización completa (idempotente)
- `PATCH` - Actualización parcial
- `DELETE` - Eliminación (idempotente, retorna 204)

### 4.3. Status Codes HTTP

- `200 OK` - GET exitoso con body
- `201 Created` - POST exitoso (incluir Location header)
- `204 No Content` - PUT/DELETE/PATCH exitoso sin body
- `400 Bad Request` - Validación falló
- `401 Unauthorized` - Sin autenticación
- `403 Forbidden` - Sin autorización
- `404 Not Found` - Recurso no existe
- `409 Conflict` - Conflicto de estado
- `429 Too Many Requests` - Rate limit excedido
- `500 Internal Server Error` - Error del servidor

### 4.4. Formato JSON

- JSON camelCase para request/response
- Omitir propiedades `null` en responses
- Fechas en formato ISO 8601 UTC: `2024-01-15T10:30:00Z`
- Enumeraciones como strings (no números)
- Moneda: `{ "amount": 1234.56, "currency": "PEN" }`
- Porcentajes: decimal (`0.18` = 18%)

### 4.5. DTOs (Data Transfer Objects)

- DTOs separados para requests/responses
- NO exponer entidades de dominio directamente
- Validación en DTOs de entrada
- Mapeo explícito DTO ↔ Entidad
- Proyecciones SQL con `Select()` para evitar over-fetching
- DTOs específicos por endpoint (summary vs details)

### 4.6. Database per Service

**Principio fundamental:** Cada microservicio accede SOLO a su propia base de datos. El acceso a datos de otros servicios debe ocurrir EXCLUSIVAMENTE mediante sus APIs.

**Prohibiciones:**

- ❌ Connection strings a BD de otros servicios
- ❌ Queries SQL cross-service
- ❌ Shared databases entre bounded contexts
- ❌ Foreign keys entre bases de datos de servicios diferentes

**Cumplimiento:**

- Network policies bloquean acceso cross-service a DBs
- Detectar violaciones en code review
- Ver [Bounded Contexts](../arquitectura/bounded-contexts.md) para más detalles

### 4.7. Configuración Mínima

```csharp
// Program.cs
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

### 4.7. Ejemplo Controller RESTful

```csharp
[ApiController]
[Route("api/v1/users")]
public class UsersController : ControllerBase
{
    private readonly IUserService _service;
    private readonly IMapper _mapper;

    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<UserDto>), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetUsers()
    {
        var users = await _service.GetAllAsync();
        return Ok(_mapper.Map<IEnumerable<UserDto>>(users));
    }

    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetUser(Guid id)
    {
        var user = await _service.GetByIdAsync(id);
        if (user == null) return NotFound();
        return Ok(_mapper.Map<UserDto>(user));
    }

    [HttpPost]
    [ProducesResponseType(typeof(UserDto), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateUser([FromBody] CreateUserRequest request)
    {
        var user = await _service.CreateAsync(request);
        var dto = _mapper.Map<UserDto>(user);
        return CreatedAtAction(nameof(GetUser), new { id = dto.Id }, dto);
    }

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

---

## 5. Seguridad y Autenticación

### 5.1. JWT Bearer (Obligatorio)

- Autenticación JWT Bearer con RS256
- Validación de issuer, audience, lifetime, signing key
- ClockSkew máximo 5 minutos
- Tokens en header `Authorization: Bearer {token}`

### 5.2. Configuración de Seguridad

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Jwt:Authority"];
        options.Audience = builder.Configuration["Jwt:Audience"];

        options.TokenValidationParameters = new()
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidAlgorithms = new[] { SecurityAlgorithms.RsaSha256 },
            ClockSkew = TimeSpan.FromMinutes(5)
        };
    });

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowedOrigins", policy =>
    {
        policy.WithOrigins("https://app.talma.com")
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

var app = builder.Build();
app.UseHttpsRedirection();
app.UseCors("AllowedOrigins");
app.UseAuthentication();
app.UseAuthorization();
```

### 5.3. Headers Obligatorios de Trazabilidad

| Header             | Propósito                               | Formato | Generado por          |
| ------------------ | --------------------------------------- | ------- | --------------------- |
| `X-Correlation-ID` | Tracking end-to-end de request          | UUID v4 | API Gateway o Cliente |
| `X-Request-ID`     | ID único del request individual         | UUID v4 | API Gateway           |
| `X-Tenant-ID`      | Identificador de tenant (multi-tenancy) | String  | Cliente autenticado   |

### 5.4. Rate Limiting

```csharp
builder.Services.AddMemoryCache();
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
    options.InstanceName = "RateLimit_";
});

builder.Services.Configure<IpRateLimitOptions>(options =>
{
    options.GeneralRules = new List<RateLimitRule>
    {
        new() { Endpoint = "*", Period = "1m", Limit = 100 },
        new() { Endpoint = "GET:/api/*", Period = "1m", Limit = 1000 },
        new() { Endpoint = "POST:/api/*", Period = "1m", Limit = 50 }
    };
});

app.UseIpRateLimiting();
```

### 5.5. Headers de Rate Limiting

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1640995200
Retry-After: 3600
```

---

## 6. Versionado de APIs

### 6.1. Estrategia: URL Versioning

- Versionado en URL: `/api/v{version}/`
- Header `api-supported-versions` obligatorio
- Período de deprecación mínimo: 6 meses (público), 3 meses (privado)

### 6.2. Configuración de Versionado

```csharp
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
    options.ApiVersionReader = new UrlSegmentApiVersionReader();
});

builder.Services.AddVersionedApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV";
    options.SubstituteApiVersionInUrl = true;
});
```

### 6.3. Ejemplo de Versionado

```csharp
[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/users")]
public class UsersV1Controller : ControllerBase
{
    [HttpGet]
    public IActionResult GetUsers() => Ok(new { version = "v1" });
}

[ApiController]
[ApiVersion("2.0")]
[Route("api/v{version:apiVersion}/users")]
public class UsersV2Controller : ControllerBase
{
    [HttpGet]
    public IActionResult GetUsers() => Ok(new { version = "v2", newField = "added" });
}
```

---

## 7. Deprecación de APIs

### 7.1. Headers de Deprecación

```http
Deprecation: true
Sunset: Tue, 31 Dec 2024 23:59:59 GMT
Link: <https://docs.talma.com/migration/v1-to-v2>; rel="deprecation"
```

### 7.2. Middleware de Deprecación

```csharp
public class DeprecationMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        var endpoint = context.GetEndpoint();
        var deprecation = endpoint?.Metadata.GetMetadata<DeprecatedAttribute>();

        if (deprecation != null)
        {
            context.Response.Headers["Deprecation"] = "true";
            context.Response.Headers["Sunset"] = deprecation.SunsetDate.ToString("r");
            context.Response.Headers["Link"] = $"<{deprecation.MigrationGuideUrl}>; rel=\"deprecation\"";
        }

        await _next(context);
    }
}

[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class DeprecatedAttribute : Attribute
{
    public DateTime SunsetDate { get; }
    public string MigrationGuideUrl { get; }

    public DeprecatedAttribute(string sunsetDate, string migrationGuideUrl)
    {
        SunsetDate = DateTime.Parse(sunsetDate);
        MigrationGuideUrl = migrationGuideUrl;
    }
}
```

### 7.3. API Desactivada (410 Gone)

```csharp
[HttpGet]
public IActionResult GetLegacy()
{
    return StatusCode(410, new
    {
        error = "Gone",
        message = "This API version was sunset on 2024-12-31",
        migrationGuide = "https://docs.talma.com/migration/v1-to-v2",
        newEndpoint = "/api/v2/users"
    });
}
```

---

## 8. Validación y Manejo de Errores

### 8.1. FluentValidation

```csharp
builder.Services.AddValidatorsFromAssemblyContaining<Program>();
builder.Services.AddFluentValidationAutoValidation();

public class CreateUserRequestValidator : AbstractValidator<CreateUserRequest>
{
    public CreateUserRequestValidator()
    {
        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress()
            .Must(HaveValidDomain).WithMessage("Solo emails @talma.com permitidos");

        RuleFor(x => x.Name)
            .NotEmpty()
            .Length(2, 100);
    }

    private bool HaveValidDomain(string email) => email?.EndsWith("@talma.com") ?? false;
}
```

### 8.2. Problem Details (RFC 7807)

```csharp
builder.Services.AddProblemDetails(options =>
{
    options.IncludeExceptionDetails = (ctx, ex) => builder.Environment.IsDevelopment();

    options.Map<ValidationException>(ex => new StatusCodeProblemDetails(400)
    {
        Title = "Validation Error",
        Detail = ex.Message,
        Type = "https://docs.talma.com/errors/validation"
    });

    options.Map<NotFoundException>(ex => new StatusCodeProblemDetails(404)
    {
        Title = "Not Found",
        Detail = ex.Message,
        Type = "https://docs.talma.com/errors/not-found"
    });
});

app.UseProblemDetails();
```

### 8.3. Formato de Error Estándar

```json
{
  "type": "https://docs.talma.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "La solicitud contiene errores de validación",
  "errors": [
    { "field": "email", "issue": "El formato no es válido" },
    { "field": "name", "issue": "Es un campo requerido" }
  ],
  "traceId": "00-abc123-def456-00"
}
```

---

## 9. Paginación

### 9.1. Offset-based Pagination

```csharp
public record PagedRequest
{
    [Range(1, int.MaxValue)]
    public int Page { get; init; } = 1;

    [Range(1, 100)]
    public int PageSize { get; init; } = 20;
}

public record PagedResult<T>
{
    public IEnumerable<T> Items { get; init; }
    public int Page { get; init; }
    public int PageSize { get; init; }
    public int TotalCount { get; init; }
    public int TotalPages { get; init; }
    public bool HasPreviousPage => Page > 1;
    public bool HasNextPage => Page < TotalPages;
}

[HttpGet]
public async Task<IActionResult> GetUsers([FromQuery] PagedRequest request)
{
    var totalCount = await _service.CountAsync();
    var users = await _service.GetPagedAsync(request.Page, request.PageSize);

    var result = new PagedResult<UserDto>
    {
        Items = users,
        Page = request.Page,
        PageSize = request.PageSize,
        TotalCount = totalCount,
        TotalPages = (int)Math.Ceiling(totalCount / (double)request.PageSize)
    };

    Response.Headers["Link"] = GenerateLinkHeader(result, Request);
    return Ok(result);
}
```

### 9.2. Link Header (RFC 8288)

```http
Link: <https://api.talma.com/users?page=1>; rel="first",
      <https://api.talma.com/users?page=2>; rel="prev",
      <https://api.talma.com/users?page=4>; rel="next",
      <https://api.talma.com/users?page=10>; rel="last"
```

### 9.3. Cursor-based Pagination

```csharp
public record CursorRequest
{
    public string? Cursor { get; init; }
    [Range(1, 100)]
    public int Limit { get; init; } = 20;
}

public record CursorResult<T>
{
    public IEnumerable<T> Items { get; init; }
    public string? NextCursor { get; init; }
    public bool HasMore { get; init; }
}

[HttpGet("cursor")]
public async Task<IActionResult> GetUsersCursor([FromQuery] CursorRequest request)
{
    var decodedCursor = request.Cursor != null ? DecodeCursor(request.Cursor) : DateTime.MinValue;
    var users = await _service.GetByCursorAsync(decodedCursor, request.Limit + 1);

    var hasMore = users.Count() > request.Limit;
    var items = users.Take(request.Limit).ToList();

    var result = new CursorResult<UserDto>
    {
        Items = items,
        NextCursor = hasMore ? EncodeCursor(items.Last().CreatedAt) : null,
        HasMore = hasMore
    };

    return Ok(result);
}
```

---

## 10. Performance

### 10.1. Compresión

```csharp
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
});

app.UseResponseCompression();
```

### 10.2. Cache

```csharp
builder.Services.AddMemoryCache();
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
    options.InstanceName = "TalmaAPI_";
});

[HttpGet]
public async Task<IActionResult> GetUsers([FromQuery] PagedQuery query)
{
    var cacheKey = $"users_page{query.Page}_limit{query.Limit}";

    if (!_cache.TryGetValue(cacheKey, out PagedResponse<UserDto> result))
    {
        var users = await _context.Users
            .Skip((query.Page - 1) * query.Limit)
            .Take(query.Limit)
            .ToListAsync();

        result = new PagedResponse<UserDto> { Data = _mapper.Map<List<UserDto>>(users) };
        _cache.Set(cacheKey, result, TimeSpan.FromMinutes(10));
    }

    return Ok(result);
}
```

---

## 11. Documentación OpenAPI/Swagger

### 11.1. Configuración Swagger

```csharp
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Version = "v1",
        Title = "Talma API",
        Description = "API corporativa de Talma",
        Contact = new OpenApiContact
        {
            Name = "Arquitectura Talma",
            Email = "arquitectura@talma.com",
            Url = new Uri("https://docs.talma.com")
        }
    });

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
                Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = "Bearer" }
            },
            Array.Empty<string>()
        }
    });

    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);
    options.EnableAnnotations();
    options.ExampleFilters();
});

builder.Services.AddSwaggerExamplesFromAssemblyOf<Program>();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "Talma API v1");
        options.RoutePrefix = "swagger";
        options.DocumentTitle = "Talma API - Documentación";
    });
}
```

### 11.2. XML Documentation

```csharp
/// <summary>
/// Gestión de usuarios del sistema
/// </summary>
[ApiController]
[Route("api/v1/users")]
public class UsersController : ControllerBase
{
    /// <summary>
    /// Obtiene todos los usuarios del sistema
    /// </summary>
    /// <returns>Lista de usuarios activos</returns>
    /// <response code="200">Lista retornada exitosamente</response>
    /// <response code="401">No autenticado</response>
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<UserDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<IActionResult> GetUsers()
    {
        var users = await _service.GetAllAsync();
        return Ok(users);
    }
}
```

---

## 12. Validación de Contratos

### 12.1. OpenAPI Schema con Validaciones

```yaml
components:
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
          pattern: '^[a-zA-Z0-9._%+-]+@talma\.com$'
          maxLength: 100
        firstName:
          type: string
          minLength: 2
          maxLength: 50
          pattern: '^[a-zA-Z\s]+$'
        lastName:
          type: string
          minLength: 2
          maxLength: 50
        age:
          type: integer
          minimum: 18
          maximum: 120
        role:
          type: string
          enum: [Developer, Manager, Admin]
      additionalProperties: false
```

### 12.2. Contract Testing con Pact

```csharp
// Consumer test
public class UsersApiConsumerTests : IClassFixture<PactFixture>
{
    [Fact]
    public async Task GetUser_WhenUserExists_ReturnsUser()
    {
        _pact
            .UponReceiving("A request to get user by ID")
            .Given("User 123 exists")
            .WithRequest(HttpMethod.Get, "/api/v1/users/123")
            .WillRespond()
            .WithStatus(200)
            .WithJsonBody(new { id = "123", email = "juan.perez@talma.com" });

        await _pact.VerifyAsync(async ctx =>
        {
            var client = new HttpClient { BaseAddress = ctx.MockServerUri };
            var response = await client.GetAsync("/api/v1/users/123");
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        });
    }
}
```

### 12.3. CI/CD Contract Validation

```yaml
# .github/workflows/contract-validation.yml
name: Contract Validation
on:
  pull_request:
    paths:
      - "swagger.json"
      - "src/**/*.cs"
jobs:
  validate-contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: Check breaking changes
        run: |
          git show origin/main:swagger.json > base-swagger.json
          dotnet run --urls http://localhost:5000 &
          sleep 5
          curl http://localhost:5000/swagger/v1/swagger.json > current-swagger.json
          docker run --rm -v ${PWD}:/specs openapitools/openapi-diff \
            /specs/base-swagger.json /specs/current-swagger.json \
            --fail-on-incompatible
      - name: Run Pact tests
        run: dotnet test --filter Category=ContractTest
```

---

## 13. Prohibiciones

- ❌ Exponer entidades de dominio directamente
- ❌ Verbos en URIs, status codes genéricos, recursos en singular
- ❌ Documentación desactualizada, ejemplos inválidos, credenciales hardcoded
- ❌ Rate limiting in-memory en producción
- ❌ Colecciones sin paginación, page size `>100`
- ❌ Breaking changes sin versionado major
- ❌ Stack traces en producción, errores sin traceId
- ❌ Swagger UI en producción con Try-it-out habilitado
- ❌ Specs OpenAPI sin ejemplos

---

## 14. Validación y Auditoría

```bash
# Validar spec OpenAPI
docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli validate \
  -i /local/swagger.json

# Comparar specs para breaking changes
docker run --rm -v ${PWD}:/specs openapitools/openapi-diff \
  /specs/v1.0.0.json /specs/v1.1.0.json

# Tests de contrato
dotnet test --filter Category=ContractTest

# Verificar rate limiting
for i in {1..150}; do curl https://api.talma.com/api/v1/users; done

# Verificar compresión
curl -H "Accept-Encoding: br" -I https://api.talma.com/api/v1/users

# Verificar paginación
curl -I "https://api.talma.com/api/v1/users?page=1&pageSize=20"
```

**Métricas de cumplimiento:**

| Métrica                     | Umbral           | Verificación                         |
| --------------------------- | ---------------- | ------------------------------------ |
| Responses camelCase         | 100%             | Verificar JSON output                |
| URIs en plural              | 100%             | Revisar rutas                        |
| Status codes apropiados     | 100%             | POST retorna 201, DELETE retorna 204 |
| DTOs en uso                 | 100%             | No entidades expuestas               |
| HTTPS habilitado            | 100%             | curl -I retorna 308 redirect         |
| JWT con RS256               | 100%             | Verificar header alg en token        |
| Rate limiting activo        | 100%             | Request 151 retorna 429              |
| Endpoints documentados      | 100%             | Comparar spec vs routes              |
| Ejemplos en endpoints       | 100%             | Verificar examples en spec           |
| Schemas con validaciones    | 100%             | Verificar required, pattern, min/max |
| Tests de contrato passing   | 100%             | CI/CD status                         |
| Breaking changes bloqueados | 0 en minor/patch | oasdiff en CI                        |
| Page size máximo respetado  | 100 items        | Validación runtime                   |
| Tiempo respuesta paginación | `<200ms`         | Performance monitoring               |
| Latencia p95                | `<200ms`         | Grafana Mimir                        |
| Compresión habilitada       | 100%             | Header Content-Encoding: br          |
| Cache hit rate              | `>70%`           | Redis MONITOR                        |

---

## 15. Validación de Schemas

Validar requests/responses con **FluentValidation** o Data Annotations. DTOs con Required/Range/MaxLength. Responses 400 con detalles de validación. Para Kafka events, JSON Schema embebido en mensaje (NO Schema Registry). OpenAPI schemas completos en Swagger.

---

## 16. Referencias

- [ADR-004: Autenticación SSO](../../decisiones-de-arquitectura/adr-004-autenticacion-sso.md)
- [ADR-008: Gateway de APIs](../../decisiones-de-arquitectura/adr-008-gateway-apis.md)
- [ADR-017: Versionado de APIs](../../decisiones-de-arquitectura/adr-017-versionado-apis.md)
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [RFC 7807: Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807)
- [RFC 8288: Web Linking (Link header)](https://datatracker.ietf.org/doc/html/rfc8288)
- [RFC 8594: Sunset HTTP Header](https://datatracker.ietf.org/doc/html/rfc8594)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Pact Documentation](https://docs.pact.io/)
- [AspNetCoreRateLimit](https://github.com/stefanprodan/AspNetCoreRateLimit)
- [Microsoft API Guidelines](https://github.com/microsoft/api-guidelines)
- [Stripe API Docs](https://stripe.com/docs/api)
- [Semantic Versioning](https://semver.org/)
