---
id: api-versioning
sidebar_position: 3
title: Versionamiento de APIs
description: Estrategias para versionar APIs REST, evolucionar contratos sin romper clientes y gestionar deprecación usando Expand-Contract.
tags:
  [
    apis,
    rest,
    versionamiento,
    backward-compatibility,
    expand-contract,
    deprecacion,
    asp-versioning,
  ]
---

# Versionamiento de APIs

## Contexto

Este estándar define cómo versionar APIs REST para que múltiples versiones coexistan y los clientes migren gradualmente. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Cuándo aplicar:** Toda API ya desplegada en producción que va a recibir cambios. Obligatorio para APIs expuestas a otros equipos o externos.

---

## Stack Tecnológico

| Componente         | Tecnología             | Versión | Uso                           |
| ------------------ | ---------------------- | ------- | ----------------------------- |
| **Versionamiento** | Asp.Versioning.Mvc     | 8.0+    | Versionamiento de APIs        |
| **Documentación**  | Swashbuckle.AspNetCore | 6.5+    | Swagger multi-versión         |
| **Framework**      | ASP.NET Core           | 8.0+    | Construcción de APIs          |
| **Serialización**  | System.Text.Json       | 8.0+    | Manejo de campos desconocidos |

---

## Estrategias de Versionamiento

| Estrategia       | Ejemplo                                 | Pros                 | Contras                  |
| ---------------- | --------------------------------------- | -------------------- | ------------------------ |
| **URI Path**     | `/api/v1/customers`                     | Explícito, cacheable | URIs cambian             |
| **Query String** | `/api/customers?api-version=1.0`        | URI estable          | Menos visible            |
| **Header**       | `X-API-Version: 1.0`                    | URI limpia           | No cacheable fácilmente  |
| **Media Type**   | `Accept: application/vnd.talma.v1+json` | RESTful puro         | Complejo para el cliente |

:::tip Estrategia recomendada
Usar **URI Path** como estrategia principal (`/api/v1/`). Es la más explícita, cacheable y fácil de debuggear. Combinar con Header como alternativa para clientes que lo prefieran.
:::

---

## Implementación

```csharp
// Program.cs
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true; // Header: api-supported-versions

    options.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),               // /api/v{version}/
        new HeaderApiVersionReader("X-API-Version"),    // Header
        new QueryStringApiVersionReader("api-version")  // Query string
    );
})
.AddApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV";
    options.SubstituteApiVersionInUrl = true;
});
```

```csharp
// Controller con múltiples versiones
[ApiController]
[Route("api/v{version:apiVersion}/[controller]")]
[ApiVersion("1.0")]
[ApiVersion("2.0")]
public class CustomersController : ControllerBase
{
    // Endpoint disponible en v1 y v2
    [HttpGet]
    [MapToApiVersion("1.0")]
    [MapToApiVersion("2.0")]
    public async Task<ActionResult<ApiResponse<CustomerDto[]>>> GetAll(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var version = HttpContext.GetRequestedApiVersion();

        if (version?.MajorVersion == 2)
            return Ok(await _customerService.GetPagedV2Async(page, pageSize));

        return Ok(await _customerService.GetPagedAsync(page, pageSize));
    }

    // Endpoint solo en v2
    [HttpGet("search")]
    [MapToApiVersion("2.0")]
    public async Task<ActionResult<CustomerDto[]>> Search([FromQuery] string query)
        => Ok(await _customerService.SearchAsync(query));
}

// Marcar versión como deprecada
[ApiVersion("1.0", Deprecated = true)]
[ApiVersion("2.0")]
public class OrdersController : ControllerBase
{
    // Headers de respuesta incluirán: api-deprecated-versions: 1.0
}
```

---

## Swagger con Múltiples Versiones

```csharp
// Generar un documento Swagger por versión
builder.Services.ConfigureOptions<ConfigureSwaggerOptions>();

public class ConfigureSwaggerOptions : IConfigureOptions<SwaggerGenOptions>
{
    private readonly IApiVersionDescriptionProvider _provider;

    public ConfigureSwaggerOptions(IApiVersionDescriptionProvider provider)
        => _provider = provider;

    public void Configure(SwaggerGenOptions options)
    {
        foreach (var description in _provider.ApiVersionDescriptions)
        {
            options.SwaggerDoc(description.GroupName, new OpenApiInfo
            {
                Title   = $"Customer API {description.ApiVersion}",
                Version = description.ApiVersion.ToString(),
                Description = description.IsDeprecated
                    ? "⚠️ Esta versión está deprecada y será removida próximamente"
                    : null
            });
        }
    }
}

// UI con selector de versión
app.UseSwaggerUI(options =>
{
    foreach (var description in app.DescribeApiVersions())
    {
        options.SwaggerEndpoint(
            $"/swagger/{description.GroupName}/swagger.json",
            description.GroupName.ToUpperInvariant());
    }
});
```

---

## Compatibilidad Hacia Atrás

### Cambios Seguros vs Incompatibles

**Cambios seguros** — compatibles, no requieren nueva versión MAJOR:

✅ Agregar endpoint nuevo
✅ Agregar campo opcional al request
✅ Agregar campo a la response
✅ Agregar valor a un enum (requiere manejo de `Unknown`)
✅ Deprecar endpoint con aviso

**Cambios incompatibles** — requieren nueva versión MAJOR:

❌ Remover endpoint
❌ Remover campo de response
❌ Cambiar tipo de un campo existente
❌ Convertir campo opcional en requerido
❌ Cambiar semántica de comportamiento existente

---

### Estrategia Expand-Contract

Para migraciones de campos incompatibles sin romper clientes:

```csharp
// Fase 1 EXPAND: Soportar campo viejo Y nuevo simultáneamente
public record CreateOrderRequest
{
    // Campo viejo: mantener durante el período de transición
    [Obsolete("Use CustomerId instead. Will be removed in v2.0")]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    public string? Customer { get; init; }

    // Campo nuevo
    public Guid? CustomerId { get; init; }

    public OrderItemDto[] Items { get; init; } = Array.Empty<OrderItemDto>();
}

// Controller: aceptar ambos durante la transición
[HttpPost]
public async Task<ActionResult<ApiResponse<OrderDto>>> Create(CreateOrderRequest request)
{
    Guid customerId;

    if (request.CustomerId.HasValue)
        customerId = request.CustomerId.Value;
    else if (!string.IsNullOrEmpty(request.Customer))
        customerId = await _customerService.GetIdByLegacyCodeAsync(request.Customer);
    else
        throw new ValidationException("CustomerId es requerido");

    var order = await _orderService.CreateAsync(customerId, request.Items);
    return CreatedAtAction(nameof(GetById), new { id = order.Id },
        ApiResponse<OrderDto>.Success(order, new MetaData { TraceId = HttpContext.TraceIdentifier }));
}

// Fase 2 CONTRACT (en v2.0): eliminar el campo legacy
// public record CreateOrderRequest
// {
//     public required Guid CustomerId { get; init; }
//     public OrderItemDto[] Items { get; init; } = Array.Empty<OrderItemDto>();
// }
```

---

### Enums Extensibles

Los clientes no deben fallar al recibir un valor de enum desconocido:

```csharp
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum OrderStatus
{
    Unknown    = 0,  // ✅ Valor por defecto para valores no reconocidos
    Pending    = 1,
    Processing = 2,
    Shipped    = 3,
    Delivered  = 4,
    Cancelled  = 5,
    Refunded   = 6   // ✅ Agregar nuevos valores es compatible
}

// Configuración: clientes viejos mapean valores desconocidos a Unknown
builder.Services.AddControllers().AddJsonOptions(options =>
{
    options.JsonSerializerOptions.Converters.Add(
        new JsonStringEnumConverter(allowIntegerValues: false));
    options.JsonSerializerOptions.UnmappedMemberHandling = JsonUnmappedMemberHandling.Skip;
});
```

---

### Deprecación de Endpoints

```csharp
[HttpGet("legacy-search")]
[Obsolete("Usar GET /api/v1/customers con parámetro ?query= en su lugar")]
public async Task<ActionResult<ApiResponse<CustomerDto[]>>> LegacySearch([FromQuery] string name)
{
    // RFC 8594: Sunset header comunica fecha de retiro
    Response.Headers.Append("Sunset", "Sat, 31 Dec 2026 23:59:59 GMT");
    Response.Headers.Append("Warning",
        "299 - \"Este endpoint está deprecado. " +
        "Usar GET /api/v1/customers?query={name}\"");

    return Ok(ApiResponse<CustomerDto[]>.Success(
        await _customerService.SearchByNameAsync(name),
        new MetaData { TraceId = HttpContext.TraceIdentifier }));
}
```

---

### Versionamiento Semántico

```text
API Version: MAJOR.MINOR.PATCH

MAJOR — Cambios incompatibles (breaking changes):
  - Remover endpoints o campos
  - Cambiar tipos de datos
  - Cambiar semántica de un endpoint

MINOR — Nuevas funcionalidades compatibles:
  - Agregar endpoints
  - Agregar campos opcionales al request
  - Agregar campos a la response

PATCH — Bug fixes compatibles:
  - Correcciones de errores sin cambio de contrato
  - Mejoras de performance

Ejemplos:
  v1.0.0 → v1.1.0: Agregar campo Address (compatible, MINOR)
  v1.1.0 → v1.1.1: Fix validación email (compatible, PATCH)
  v1.1.1 → v2.0.0: Remover campo legacy Customer (BREAKING, MAJOR)
```

---

## Beneficios en Práctica

| Sin estrategia de versión/compatibilidad    | Con versionamiento + Expand-Contract     |
| ------------------------------------------- | ---------------------------------------- |
| Cambios rompen clientes sin previo aviso    | Clientes migran a su ritmo               |
| Rollback complejo de toda la API            | Versiones coexisten hasta deprecación    |
| Coordinación síncrona con todos los equipos | Despliegues independientes               |
| Imposible evolucionar contratos públicos    | Evolución controlada con semántica clara |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** versionar toda API expuesta externamente o a otros equipos
- **MUST** usar versionamiento semántico (MAJOR.MINOR.PATCH)
- **MUST** soportar al menos 2 versiones MAJOR simultáneamente durante la transición
- **MUST** reportar versiones soportadas via header (`api-supported-versions`)
- **MUST** mantener compatibilidad hacia atrás en versiones MINOR y PATCH
- **MUST** deprecar endpoints al menos 6 meses antes de removerlos
- **MUST** usar estrategia Expand-Contract para cambios de contrato incompatibles
- **MUST** incluir header `Sunset` (RFC 8594) en endpoints deprecados
- **MUST** comunicar deprecación en Swagger (`Deprecated = true`)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar URI Path como estrategia principal de versionamiento
- **SHOULD** marcar versiones con `Deprecated = true` antes de retirarlas
- **SHOULD** generar documentación Swagger independiente por versión
- **SHOULD** incluir header `Warning` en responses de endpoints deprecados
- **SHOULD** agregar valor `Unknown = 0` en todos los enums de API
- **SHOULD** comunicar cambios incompatibles con al menos 3 meses de anticipación

### MUST NOT (Prohibido)

- **MUST NOT** hacer cambios incompatibles en versiones MINOR o PATCH
- **MUST NOT** remover una versión sin al menos 6 meses de deprecación previa
- **MUST NOT** romper clientes existentes en versiones MINOR o PATCH
- **MUST NOT** remover endpoints sin período de deprecación previo

---

## Referencias

- [Asp.Versioning.Mvc](https://github.com/dotnet/aspnet-api-versioning) — Librería de versionamiento
- [ASP.NET Core API Versioning](https://learn.microsoft.com/aspnet/core/web-api/) — Documentación oficial
- [RFC 8594 - Sunset Header](https://www.rfc-editor.org/rfc/rfc8594.html) — Estándar de deprecación HTTP
- [API Evolution Patterns](https://www.martinfowler.com/articles/enterpriseREST.html) — Expand-Contract y patrones
- [Contratos de APIs](./api-contracts.md) — Documentación OpenAPI
- [Estándares REST](./api-rest-standards.md) — Base HTTP
