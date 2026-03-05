---
id: api-versioning
sidebar_position: 3
title: Versionamiento de APIs
description: Estrategias para versionar APIs REST y evolucionar contratos sin romper clientes existentes.
tags: [apis, rest, versionamiento, asp-versioning]
---

# Versionamiento de APIs

## Contexto

Este estándar define cómo versionar APIs REST para que múltiples versiones coexistan y los clientes migren gradualmente. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Cuándo aplicar:** Toda API ya desplegada en producción que va a recibir cambios. Obligatorio para APIs expuestas a otros equipos o externos.

---

## Stack Tecnológico

| Componente         | Tecnología             | Versión | Uso                    |
| ------------------ | ---------------------- | ------- | ---------------------- |
| **Versionamiento** | Asp.Versioning.Mvc     | 8.0+    | Versionamiento de APIs |
| **Documentación**  | Swashbuckle.AspNetCore | 6.5+    | Swagger multi-versión  |
| **Framework**      | ASP.NET Core           | 8.0+    | Construcción de APIs   |

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
    public async Task<ActionResult<PagedResult<CustomerDto>>> GetAll(
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

## Beneficios en Práctica

| Sin versionamiento                       | Con versionamiento                       |
| ---------------------------------------- | ---------------------------------------- |
| Cambios rompen clientes sin previo aviso | Clientes migran a su ritmo               |
| Rollback complejo                        | Versiones coexisten hasta deprecación    |
| Imposible evolucionar contratos públicos | Evolución controlada con semántica clara |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** versionar toda API expuesta externamente o a otros equipos
- **MUST** usar versionamiento semántico (MAJOR.MINOR.PATCH)
- **MUST** soportar al menos 2 versiones MAJOR simultáneamente durante la transición
- **MUST** reportar versiones soportadas via header (`api-supported-versions`)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar URI Path como estrategia principal de versionamiento
- **SHOULD** marcar versiones con `Deprecated = true` antes de retirarlas
- **SHOULD** generar documentación Swagger independiente por versión

### MUST NOT (Prohibido)

- **MUST NOT** hacer cambios incompatibles en versiones MINOR o PATCH
- **MUST NOT** remover una versión sin al menos 6 meses de deprecación previa

---

## Referencias

- [Asp.Versioning.Mvc](https://github.com/dotnet/aspnet-api-versioning) — Librería de versionamiento
- [ASP.NET Core API Versioning](https://learn.microsoft.com/aspnet/core/web-api/) — Documentación oficial
- [Compatibilidad Hacia Atrás](./backward-compatibility.md) — Estrategias de evolución
- [Contratos de APIs](./api-contracts.md) — Documentación OpenAPI
- [Estándares REST](./api-rest-standards.md) — Base HTTP
