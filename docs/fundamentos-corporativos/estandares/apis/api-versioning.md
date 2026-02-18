---
id: api-versioning
sidebar_position: 2
title: Versionado de APIs
description: Estrategias de versionado para evolución controlada de APIs
---

# Versionado de APIs

## Contexto

Este estándar define las estrategias de versionado que deben usar todas las APIs de Talma para evolucionar sin romper integraciones existentes. Complementa el [lineamiento de APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md) especificando **cómo** gestionar cambios que rompen compatibilidad (breaking changes).

---

## Stack Tecnológico

| Componente        | Tecnología             | Versión | Uso                          |
| ----------------- | ---------------------- | ------- | ---------------------------- |
| **Framework**     | ASP.NET Core           | 8.0+    | Framework base               |
| **Versionado**    | Asp.Versioning.Http    | 8.0+    | Gestión de versiones de APIs |
| **Documentación** | Swashbuckle.AspNetCore | 6.5+    | Swagger multi-versión        |
| **API Gateway**   | Kong                   | 3.4+    | Routing por versión          |

### Dependencias NuGet

```xml
<PackageReference Include="Asp.Versioning.Http" Version="8.0.0" />
<PackageReference Include="Asp.Versioning.Mvc.ApiExplorer" Version="8.0.0" />
<PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
```

---

## Implementación Técnica

### Estrategia Recomendada: URL Path Versioning

```csharp
// ✅ PREFERIDO: Versión en URL path
GET    /api/v1/orders
GET    /api/v2/orders
POST   /api/v1/orders
PUT    /api/v2/orders/{id}

// ⚠️  ALTERNATIVA: Header versioning (para casos específicos)
GET    /api/orders
Header: X-API-Version: 1

// ❌ EVITAR: Query parameter (no cacheable correctamente)
GET    /api/orders?version=1

// ❌ EVITAR: Content negotiation (complejo para clientes)
GET    /api/orders
Accept: application/vnd.talma.v1+json
```

### Configuración Base

```csharp
// Program.cs
using Asp.Versioning;

var builder = WebApplication.CreateBuilder(args);

// ✅ Configurar versionado
builder.Services.AddApiVersioning(options =>
{
    // Versión por defecto para requests sin versión especificada
    options.DefaultApiVersion = new ApiVersion(1, 0);

    // Asumir v1 si no se especifica versión
    options.AssumeDefaultVersionWhenUnspecified = true;

    // Reportar versiones disponibles en headers
    options.ReportApiVersions = true;

    // Estrategia: URL Path (recomendado)
    options.ApiVersionReader = new UrlSegmentApiVersionReader();

    // ⚠️ ALTERNATIVA: Multiple strategies
    // options.ApiVersionReader = ApiVersionReader.Combine(
    //     new UrlSegmentApiVersionReader(),
    //     new HeaderApiVersionReader("X-API-Version")
    // );
}).AddApiExplorer(options =>
{
    // Formato de grupo por versión para Swagger
    options.GroupNameFormat = "'v'VVV"; // v1, v2
    options.SubstituteApiVersionInUrl = true;
});

var app = builder.Build();

// Response Headers:
// X-API-Supported-Versions: 1.0, 2.0
// X-API-Deprecated-Versions: 1.0
```

### V1 - Versión Inicial

```csharp
namespace Talma.Orders.Api.V1.Controllers;

[ApiController]
[Route("api/v{version:apiVersion}/orders")]
[ApiVersion("1.0")]
public class OrdersController : ControllerBase
{
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(OrderV1Dto), StatusCodes.Status200OK)]
    public async Task<ActionResult<OrderV1Dto>> GetOrder(Guid id)
    {
        var order = await _orderService.GetOrderAsync(id);

        if (order == null)
            return NotFound();

        // DTO V1
        return Ok(new OrderV1Dto
        {
            Id = order.Id,
            OrderNumber = order.OrderNumber,
            CustomerId = order.CustomerId,
            TotalAmount = order.TotalAmount,
            Status = order.Status.ToString(),
            CreatedAt = order.CreatedAt
        });
    }

    [HttpPost]
    [ProducesResponseType(typeof(OrderV1Dto), StatusCodes.Status201Created)]
    public async Task<ActionResult<OrderV1Dto>> CreateOrder(
        [FromBody] CreateOrderV1Request request)
    {
        var order = await _orderService.CreateOrderAsync(request);

        return CreatedAtAction(
            nameof(GetOrder),
            new { version = "1.0", id = order.Id },
            order
        );
    }
}
```

### V2 - Breaking Change (Nueva Estructura)

```csharp
namespace Talma.Orders.Api.V2.Controllers;

[ApiController]
[Route("api/v{version:apiVersion}/orders")]
[ApiVersion("2.0")]
public class OrdersController : ControllerBase
{
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(OrderV2Dto), StatusCodes.Status200OK)]
    public async Task<ActionResult<OrderV2Dto>> GetOrder(Guid id)
    {
        var order = await _orderService.GetOrderAsync(id);

        if (order == null)
            return NotFound();

        // DTO V2: Cambio breaking - Status ahora es objeto complejo
        return Ok(new OrderV2Dto
        {
            Id = order.Id,
            OrderNumber = order.OrderNumber,
            Customer = new CustomerSummary
            {
                Id = order.CustomerId,
                Name = order.Customer.Name,
                Email = order.Customer.Email
            },
            Pricing = new PricingDetails
            {
                SubTotal = order.SubTotal,
                TaxAmount = order.TaxAmount,
                DiscountAmount = order.DiscountAmount,
                TotalAmount = order.TotalAmount,
                Currency = order.Currency
            },
            Status = new OrderStatus
            {
                Code = order.Status.ToString(),
                Description = order.Status.GetDescription(),
                Timestamp = order.StatusUpdatedAt
            },
            CreatedAt = order.CreatedAt
        });
    }

    [HttpPost]
    [ProducesResponseType(typeof(OrderV2Dto), StatusCodes.Status201Created)]
    public async Task<ActionResult<OrderV2Dto>> CreateOrder(
        [FromBody] CreateOrderV2Request request)
    {
        var order = await _orderService.CreateOrderAsync(request);

        return CreatedAtAction(
            nameof(GetOrder),
            new { version = "2.0", id = order.Id },
            order
        );
    }
}
```

### Deprecación de Versiones

```csharp
[ApiController]
[Route("api/v{version:apiVersion}/orders")]
[ApiVersion("1.0", Deprecated = true)]  // ✅ Marcar como deprecado
[ApiVersion("2.0")]                      // ✅ Versión actual
public class OrdersController : ControllerBase
{
    // ...
}

// Response Headers:
// X-API-Deprecated-Versions: 1.0
// X-API-Supported-Versions: 1.0, 2.0
// Sunset: Sat, 31 Dec 2024 23:59:59 GMT   // RFC 8594
```

### Swagger Multi-Versión

```csharp
// Program.cs
builder.Services.AddSwaggerGen(options =>
{
    var provider = builder.Services.BuildServiceProvider()
        .GetRequiredService<IApiVersionDescriptionProvider>();

    // Un documento Swagger por versión
    foreach (var description in provider.ApiVersionDescriptions)
    {
        options.SwaggerDoc(
            description.GroupName,
            new OpenApiInfo
            {
                Title = $"Orders API {description.ApiVersion}",
                Version = description.ApiVersion.ToString(),
                Description = description.IsDeprecated
                    ? "⚠️ ESTA VERSIÓN ESTÁ DEPRECADA. Migrar a v2."
                    : "API de gestión de órdenes"
            }
        );
    }

    options.OperationFilter<RemoveVersionParameterOperationFilter>();
    options.DocumentFilter<ReplaceVersionWithExactValueInPathDocumentFilter>();
});

// Middleware
app.UseSwagger();
app.UseSwaggerUI(options =>
{
    var provider = app.Services.GetRequiredService<IApiVersionDescriptionProvider>();

    foreach (var description in provider.ApiVersionDescriptions)
    {
        options.SwaggerEndpoint(
            $"/swagger/{description.GroupName}/swagger.json",
            description.GroupName.ToUpperInvariant()
        );
    }
});

// URLs Swagger:
// https://api.talma.com/swagger/v1/swagger.json
// https://api.talma.com/swagger/v2/swagger.json
// https://api.talma.com/swagger/index.html
```

### Versionado de DTOs

```csharp
// V1 DTOs
namespace Talma.Orders.Api.V1.Models;

public record OrderV1Dto
{
    public Guid Id { get; init; }
    public string OrderNumber { get; init; }
    public Guid CustomerId { get; init; }
    public decimal TotalAmount { get; init; }
    public string Status { get; init; }  // String simple
    public DateTime CreatedAt { get; init; }
}

// V2 DTOs
namespace Talma.Orders.Api.V2.Models;

public record OrderV2Dto
{
    public Guid Id { get; init; }
    public string OrderNumber { get; init; }

    // ✅ Breaking: CustomerId → Customer (objeto completo)
    public CustomerSummary Customer { get; init; }

    // ✅ Breaking: TotalAmount → Pricing (objeto detallado)
    public PricingDetails Pricing { get; init; }

    // ✅ Breaking: Status → OrderStatus (objeto completo)
    public OrderStatus Status { get; init; }

    public DateTime CreatedAt { get; init; }
}

public record CustomerSummary
{
    public Guid Id { get; init; }
    public string Name { get; init; }
    public string Email { get; init; }
}

public record PricingDetails
{
    public decimal SubTotal { get; init; }
    public decimal TaxAmount { get; init; }
    public decimal DiscountAmount { get; init; }
    public decimal TotalAmount { get; init; }
    public string Currency { get; init; }
}

public record OrderStatus
{
    public string Code { get; init; }
    public string Description { get; init; }
    public DateTime Timestamp { get; init; }
}
```

### Mapeo entre Versiones

```csharp
// Mapeo V1
public class OrderMappingV1
{
    public static OrderV1Dto ToDto(Order order)
    {
        return new OrderV1Dto
        {
            Id = order.Id,
            OrderNumber = order.OrderNumber,
            CustomerId = order.CustomerId,
            TotalAmount = order.TotalAmount,
            Status = order.Status.ToString(),
            CreatedAt = order.CreatedAt
        };
    }
}

// Mapeo V2
public class OrderMappingV2
{
    public static OrderV2Dto ToDto(Order order)
    {
        return new OrderV2Dto
        {
            Id = order.Id,
            OrderNumber = order.OrderNumber,
            Customer = new CustomerSummary
            {
                Id = order.Customer.Id,
                Name = order.Customer.Name,
                Email = order.Customer.Email
            },
            Pricing = new PricingDetails
            {
                SubTotal = order.SubTotal,
                TaxAmount = order.TaxAmount,
                DiscountAmount = order.DiscountAmount,
                TotalAmount = order.TotalAmount,
                Currency = order.Currency.ToString()
            },
            Status = new OrderStatus
            {
                Code = order.Status.ToString(),
                Description = order.Status.GetDescription(),
                Timestamp = order.StatusUpdatedAt
            },
            CreatedAt = order.CreatedAt
        };
    }
}
```

### Kong Gateway - Routing por Versión

```yaml
# Kong configuration
services:
  - name: orders-api-v1
    url: http://orders-api:8080/api/v1
    routes:
      - name: orders-v1-route
        paths:
          - /api/v1/orders

  - name: orders-api-v2
    url: http://orders-api:8080/api/v2
    routes:
      - name: orders-v2-route
        paths:
          - /api/v2/orders

plugins:
  # Rate limiting por versión
  - name: rate-limiting
    service: orders-api-v1
    config:
      minute: 100 # V1 deprecada: límite bajo

  - name: rate-limiting
    service: orders-api-v2
    config:
      minute: 1000 # V2 actual: límite normal
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar versionado URL path (`/api/v1/orders`) como estrategia primaria
- **MUST** versionar cuando hay breaking changes:
  - Eliminación de campos
  - Cambio de tipos de datos
  - Cambio de estructura (flat → nested)
  - Cambio de semántica de endpoints
  - Cambio de códigos de estado
- **MUST** usar versionado Major (`v1`, `v2`) no Minor (`v1.1`, `v1.2`)
- **MUST** soportar al menos 2 versiones simultáneamente durante período de transición
- **MUST** documentar breaking changes en release notes
- **MUST** marcar versiones deprecadas con `[ApiVersion("1.0", Deprecated = true)]`
- **MUST** incluir headers `X-API-Supported-Versions` y `X-API-Deprecated-Versions`
- **MUST** anunciar deprecación con 6 meses de anticipación mínimo

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar namespaces separados por versión (`V1.Controllers`, `V2.Controllers`)
- **SHOULD** usar DTOs dedicados por versión (`OrderV1Dto`, `OrderV2Dto`)
- **SHOULD** incluir header `Sunset` (RFC 8594) con fecha de fin de vida
- **SHOULD** documentar cada versión en Swagger separado
- **SHOULD** mantener backward compatibility dentro de la misma versión major
- **SHOULD** usar feature flags para habilitar/deshabilitar versiones en runtime
- **SHOULD** monitorear uso de versiones deprecadas con métricas

### MAY (Opcional)

- **MAY** soportar header versioning (`X-API-Version`) adicional a URL
- **MAY** implementar fallback automático a versión por defecto
- **MAY** ofrecer endpoint de migración automatizada (`POST /api/migrate/v1-to-v2`)

### MUST NOT (Prohibido)

- **MUST NOT** cambiar contratos existentes sin incrementar versión major
- **MUST NOT** eliminar versiones sin período de deprecación (mínimo 6 meses)
- **MUST NOT** usar query parameters para versionado (`?version=1`)
- **MUST NOT** versionar con fechas (`/api/2024-01-01/orders`)
- **MUST NOT** tener más de 3 versiones activas simultáneamente

---

## Ciclo de Vida de Versiones

```
v1.0 Released
    │
    ├─────────────── 6 meses uso activo ─────────────┐
    │                                                  │
    v2.0 Released (v1 marcada deprecada)             │
    │                                                  │
    ├─────────────── 6 meses deprecación ────────────┤
    │                                                  │
    v1.0 Sunset (retirada)                           │
    │                                                  │
    v2.0 es ahora única versión                      │
    │                                                  │
    v3.0 Released (v2 marcada deprecada)             │
    │                                                  │
    └──────────────── Continúa ciclo ─────────────────┘

Timeline:
- T+0: v1 lanzada
- T+6m: v2 lanzada, v1 deprecada
- T+12m: v1 retirada
- T+18m: v3 lanzada, v2 deprecada
- T+24m: v2 retirada
```

---

## Referencias

- [Lineamiento: APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md)
- Estándares relacionados:
  - [Estándares REST](api-rest-standards.md)
  - [Documentación OpenAPI](openapi-specification.md)
  - [Retrocompatibilidad](api-backward-compatibility.md)
- Especificaciones:
  - [Microsoft API Versioning](https://github.com/dotnet/aspnet-api-versioning)
  - [RFC 8594: Sunset Header](https://tools.ietf.org/html/rfc8594)
  - [Semantic Versioning](https://semver.org/)
