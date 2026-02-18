---
id: openapi-specification
sidebar_position: 3
title: Especificación OpenAPI
description: Documentación de APIs con OpenAPI 3.0 usando Swashbuckle
---

# Especificación OpenAPI

## Contexto

Este estándar define cómo documentar APIs REST usando OpenAPI 3.0 (Swagger). Complementa el [lineamiento de APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md) especificando cómo generar documentación interactiva, ejemplos, validaciones y contratos legibles por máquinas.

---

## Stack Tecnológico

| Componente      | Tecnología              | Versión | Uso                          |
| --------------- | ----------------------- | ------- | ---------------------------- |
| **Framework**   | ASP.NET Core            | 8.0+    | Framework base               |
| **OpenAPI**     | Swashbuckle.AspNetCore  | 6.5+    | Generación de especificación |
| **Anotaciones** | Swashbuckle.Annotations | 6.5+    | Metadata enriquecido         |
| **Validación**  | FluentValidation        | 11.0+   | Reglas de validación         |

### Dependencias NuGet

```xml
<PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
<PackageReference Include="Swashbuckle.AspNetCore.Annotations" Version="6.5.0" />
<PackageReference Include="Swashbuckle.AspNetCore.Filters" Version="7.0.12" />
```

---

## Implementación Técnica

### Configuración Base

```csharp
// Program.cs
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSwaggerGen(options =>
{
    // ✅ Metadata básica
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Version = "v1",
        Title = "Orders API",
        Description = "API de gestión de órdenes para plataforma Talma",
        Contact = new OpenApiContact
        {
            Name = "Equipo de Arquitectura",
            Email = "arquitectura@talma.com",
            Url = new Uri("https://github.com/talma/orders-api")
        },
        License = new OpenApiLicense
        {
            Name = "Uso interno - Talma",
            Url = new Uri("https://talma.com/licenses")
        }
    });

    // ✅ Comentarios XML
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);

    // ✅ Anotaciones
    options.EnableAnnotations();

    // ✅ Ejemplos
    options.ExampleFilters();

    // ✅ Autenticación JWT
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header usando esquema Bearer. Ejemplo: \"Bearer {token}\"",
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
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

builder.Services.AddSwaggerExamplesFromAssemblyOf<Program>();

var app = builder.Build();

// ✅ MUST: Habilitar solo en Development y Staging
if (!app.Environment.IsProduction())
{
    app.UseSwagger(options =>
    {
        options.RouteTemplate = "swagger/{documentName}/swagger.json";
    });

    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "Orders API V1");
        options.RoutePrefix = "swagger";

        // ✅ Configuración UI
        options.DisplayRequestDuration();
        options.EnableDeepLinking();
        options.EnableFilter();
        options.ShowExtensions();
        options.EnableValidator();
        options.DocExpansion(Swashbuckle.AspNetCore.SwaggerUI.DocExpansion.None);
    });
}

// URL: https://api-dev.talma.com/swagger/index.html
```

### Documentación de Controllers

```csharp
using Microsoft.AspNetCore.Mvc;
using Swashbuckle.AspNetCore.Annotations;

/// <summary>
/// Gestión de órdenes
/// </summary>
[ApiController]
[Route("api/v{version:apiVersion}/orders")]
[Produces("application/json")]
[SwaggerTag("Operaciones de creación, lectura, actualización y eliminación de órdenes")]
public class OrdersController : ControllerBase
{
    /// <summary>
    /// Obtiene una orden por su ID
    /// </summary>
    /// <param name="id">Identificador único de la orden (UUID)</param>
    /// <returns>Detalles de la orden</returns>
    /// <response code="200">Orden encontrada exitosamente</response>
    /// <response code="404">Orden no encontrada</response>
    /// <response code="401">No autenticado</response>
    [HttpGet("{id}")]
    [SwaggerOperation(
        Summary = "Obtener orden por ID",
        Description = "Retorna los detalles completos de una orden específica",
        OperationId = "GetOrderById",
        Tags = new[] { "Orders" }
    )]
    [SwaggerResponse(StatusCodes.Status200OK, "Orden encontrada", typeof(OrderDto))]
    [SwaggerResponse(StatusCodes.Status404NotFound, "Orden no encontrada", typeof(ProblemDetails))]
    [SwaggerResponse(StatusCodes.Status401Unauthorized, "No autenticado")]
    [ProducesResponseType(typeof(OrderDto), StatusCodes.Status200OK)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
    {
        var order = await _orderService.GetOrderByIdAsync(id);

        if (order == null)
            return NotFound(new ProblemDetails
            {
                Title = "Order not found",
                Detail = $"Order with ID {id} does not exist",
                Status = StatusCodes.Status404NotFound
            });

        return Ok(order);
    }

    /// <summary>
    /// Crea una nueva orden
    /// </summary>
    /// <param name="request">Datos de la orden a crear</param>
    /// <returns>Orden creada</returns>
    /// <remarks>
    /// Ejemplo de request:
    ///
    ///     POST /api/v1/orders
    ///     {
    ///       "customerId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    ///       "items": [
    ///         {
    ///           "productId": "5fa85f64-5717-4562-b3fc-2c963f66afa6",
    ///           "quantity": 2,
    ///           "unitPrice": 99.99
    ///         }
    ///       ],
    ///       "shippingAddress": {
    ///         "street": "Av. Principal 123",
    ///         "city": "Lima",
    ///         "country": "PE",
    ///         "postalCode": "15001"
    ///       }
    ///     }
    ///
    /// </remarks>
    /// <response code="201">Orden creada exitosamente</response>
    /// <response code="400">Datos de entrada inválidos</response>
    /// <response code="422">Validación de negocio falló</response>
    [HttpPost]
    [SwaggerOperation(
        Summary = "Crear nueva orden",
        Description = "Crea una nueva orden con los datos proporcionados",
        OperationId = "CreateOrder"
    )]
    [SwaggerResponse(StatusCodes.Status201Created, "Orden creada", typeof(OrderDto))]
    [SwaggerResponse(StatusCodes.Status400BadRequest, "Request inválido", typeof(ValidationProblemDetails))]
    [SwaggerResponse(StatusCodes.Status422UnprocessableEntity, "Validación de negocio falló", typeof(ProblemDetails))]
    [ProducesResponseType(typeof(OrderDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    [ProducesResponseType(typeof(ProblemDetails), StatusCodes.Status422UnprocessableEntity)]
    public async Task<ActionResult<OrderDto>> CreateOrder(
        [FromBody, SwaggerRequestBody("Datos de la orden", Required = true)] CreateOrderRequest request)
    {
        var order = await _orderService.CreateOrderAsync(request);

        return CreatedAtAction(
            nameof(GetOrder),
            new { id = order.Id },
            order
        );
    }
}
```

### Documentación de DTOs

```csharp
using System.ComponentModel.DataAnnotations;
using Swashbuckle.AspNetCore.Annotations;

/// <summary>
/// Representación de una orden
/// </summary>
[SwaggerSchema(Required = new[] { "Id", "OrderNumber", "CustomerId", "TotalAmount", "Status" })]
public record OrderDto
{
    /// <summary>
    /// Identificador único de la orden
    /// </summary>
    /// <example>550e8400-e29b-41d4-a716-446655440000</example>
    [SwaggerSchema("Identificador único (UUID v4)")]
    public Guid Id { get; init; }

    /// <summary>
    /// Número de orden legible por humanos
    /// </summary>
    /// <example>ORD-2024-001234</example>
    [SwaggerSchema("Número de orden único secuencial", Format = "ORD-YYYY-NNNNNN")]
    public string OrderNumber { get; init; }

    /// <summary>
    /// ID del cliente que realizó la orden
    /// </summary>
    /// <example>3fa85f64-5717-4562-b3fc-2c963f66afa6</example>
    public Guid CustomerId { get; init; }

    /// <summary>
    /// Monto total de la orden en USD
    /// </summary>
    /// <example>299.97</example>
    [SwaggerSchema("Monto total incluyendo impuestos", Format = "decimal(18,2)")]
    [Range(0.01, double.MaxValue)]
    public decimal TotalAmount { get; init; }

    /// <summary>
    /// Estado actual de la orden
    /// </summary>
    /// <example>Pending</example>
    [SwaggerSchema("Estado del flujo de la orden")]
    public OrderStatus Status { get; init; }

    /// <summary>
    /// Fecha y hora de creación (UTC)
    /// </summary>
    /// <example>2024-01-15T10:30:00Z</example>
    [SwaggerSchema("Timestamp de creación en formato ISO 8601")]
    public DateTime CreatedAt { get; init; }

    /// <summary>
    /// Items de la orden
    /// </summary>
    public List<OrderItemDto> Items { get; init; } = new();
}

/// <summary>
/// Request para crear una orden
/// </summary>
public record CreateOrderRequest
{
    /// <summary>
    /// ID del cliente
    /// </summary>
    /// <example>3fa85f64-5717-4562-b3fc-2c963f66afa6</example>
    [Required]
    [SwaggerSchema("Identificador del cliente existente")]
    public Guid CustomerId { get; init; }

    /// <summary>
    /// Items a incluir en la orden
    /// </summary>
    [Required]
    [MinLength(1, ErrorMessage = "La orden debe tener al menos un item")]
    [SwaggerSchema("Lista de productos con cantidades")]
    public List<CreateOrderItemRequest> Items { get; init; } = new();

    /// <summary>
    /// Dirección de envío
    /// </summary>
    [Required]
    public AddressDto ShippingAddress { get; init; }
}

/// <summary>
/// Estados posibles de una orden
/// </summary>
[SwaggerSchema("Estados del ciclo de vida de una orden")]
public enum OrderStatus
{
    /// <summary>Orden creada, pendiente de pago</summary>
    [SwaggerEnumInfo("Orden creada, esperando pago")]
    Pending = 0,

    /// <summary>Pago confirmado, pendiente de preparación</summary>
    [SwaggerEnumInfo("Pago confirmado")]
    Confirmed = 1,

    /// <summary>Orden en proceso de preparación</summary>
    [SwaggerEnumInfo("En preparación en almacén")]
    Processing = 2,

    /// <summary>Orden enviada al cliente</summary>
    [SwaggerEnumInfo("Enviada con transportista")]
    Shipped = 3,

    /// <summary>Orden entregada exitosamente</summary>
    [SwaggerEnumInfo("Entregada al cliente final")]
    Delivered = 4,

    /// <summary>Orden cancelada</summary>
    [SwaggerEnumInfo("Cancelada por cliente o sistema")]
    Cancelled = 5
}
```

### Ejemplos con Swashbuckle.AspNetCore.Filters

```csharp
using Swashbuckle.AspNetCore.Filters;

// Ejemplo de Request
public class CreateOrderRequestExample : IExamplesProvider<CreateOrderRequest>
{
    public CreateOrderRequest GetExamples()
    {
        return new CreateOrderRequest
        {
            CustomerId = Guid.Parse("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            Items = new List<CreateOrderItemRequest>
            {
                new()
                {
                    ProductId = Guid.Parse("5fa85f64-5717-4562-b3fc-2c963f66afa6"),
                    Quantity = 2,
                    UnitPrice = 99.99m
                },
                new()
                {
                    ProductId = Guid.Parse("6fa85f64-5717-4562-b3fc-2c963f66afa6"),
                    Quantity = 1,
                    UnitPrice = 149.99m
                }
            },
            ShippingAddress = new AddressDto
            {
                Street = "Av. Principal 123",
                City = "Lima",
                Country = "PE",
                PostalCode = "15001"
            }
        };
    }
}

// Ejemplo de Response exitoso
public class OrderDtoExample : IExamplesProvider<OrderDto>
{
    public OrderDto GetExamples()
    {
        return new OrderDto
        {
            Id = Guid.Parse("550e8400-e29b-41d4-a716-446655440000"),
            OrderNumber = "ORD-2024-001234",
            CustomerId = Guid.Parse("3fa85f64-5717-4562-b3fc-2c963f66afa6"),
            TotalAmount = 349.97m,
            Status = OrderStatus.Pending,
            CreatedAt = DateTime.UtcNow,
            Items = new List<OrderItemDto>
            {
                new()
                {
                    Id = Guid.NewGuid(),
                    ProductId = Guid.Parse("5fa85f64-5717-4562-b3fc-2c963f66afa6"),
                    ProductName = "Laptop Dell XPS 15",
                    Quantity = 2,
                    UnitPrice = 99.99m,
                    TotalPrice = 199.98m
                },
                new()
                {
                    Id = Guid.NewGuid(),
                    ProductId = Guid.Parse("6fa85f64-5717-4562-b3fc-2c963f66afa6"),
                    ProductName = "Mouse Logitech MX Master",
                    Quantity = 1,
                    UnitPrice = 149.99m,
                    TotalPrice = 149.99m
                }
            }
        };
    }
}

// Ejemplo de validación fallida
public class ValidationProblemDetailsExample : IExamplesProvider<ValidationProblemDetails>
{
    public ValidationProblemDetails GetExamples()
    {
        return new ValidationProblemDetails
        {
            Title = "Validation failed",
            Status = StatusCodes.Status400BadRequest,
            Detail = "One or more validation errors occurred",
            Instance = "/api/v1/orders",
            Errors = new Dictionary<string, string[]>
            {
                ["CustomerId"] = new[] { "Customer ID is required" },
                ["Items"] = new[] { "Order must have at least one item" },
                ["ShippingAddress.PostalCode"] = new[] { "Invalid postal code format" }
            }
        };
    }
}

// Registrar en Program.cs
builder.Services.AddSwaggerExamplesFromAssemblyOf<CreateOrderRequestExample>();
```

### Operaciones Personalizadas

```csharp
/// <summary>
/// Cancela una orden existente
/// </summary>
/// <param name="id">ID de la orden a cancelar</param>
/// <param name="request">Razón de la cancelación</param>
/// <returns>Orden actualizada</returns>
[HttpPost("{id}/cancel")]
[SwaggerOperation(
    Summary = "Cancelar orden",
    Description = "Cancela una orden existente si está en estado Pending o Confirmed",
    OperationId = "CancelOrder"
)]
[SwaggerResponse(StatusCodes.Status200OK, "Orden cancelada", typeof(OrderDto))]
[SwaggerResponse(StatusCodes.Status404NotFound, "Orden no encontrada", typeof(ProblemDetails))]
[SwaggerResponse(StatusCodes.Status409Conflict, "Orden no puede ser cancelada", typeof(ProblemDetails))]
public async Task<ActionResult<OrderDto>> CancelOrder(
    Guid id,
    [FromBody] CancelOrderRequest request)
{
    var order = await _orderService.CancelOrderAsync(id, request.Reason);

    if (order == null)
        return NotFound();

    return Ok(order);
}
```

### Documentación de Query Parameters

```csharp
/// <summary>
/// Lista órdenes con filtros
/// </summary>
/// <param name="status">Filtrar por estado</param>
/// <param name="customerId">Filtrar por cliente</param>
/// <param name="minAmount">Monto mínimo</param>
/// <param name="maxAmount">Monto máximo</param>
/// <param name="page">Número de página (inicia en 1)</param>
/// <param name="pageSize">Tamaño de página (10-100)</param>
/// <param name="sortBy">Campo para ordenar (createdAt, totalAmount)</param>
/// <param name="sortOrder">Dirección de ordenamiento (asc, desc)</param>
/// <returns>Lista paginada de órdenes</returns>
[HttpGet]
[SwaggerOperation(
    Summary = "Listar órdenes",
    Description = "Obtiene lista paginada de órdenes con filtros opcionales"
)]
[SwaggerResponse(StatusCodes.Status200OK, "Lista de órdenes", typeof(PagedResult<OrderDto>))]
public async Task<ActionResult<PagedResult<OrderDto>>> GetOrders(
    [FromQuery, SwaggerParameter("Estado de la orden", Required = false)] OrderStatus? status = null,
    [FromQuery, SwaggerParameter("ID del cliente")] Guid? customerId = null,
    [FromQuery, SwaggerParameter("Monto mínimo en USD")] decimal? minAmount = null,
    [FromQuery, SwaggerParameter("Monto máximo en USD")] decimal? maxAmount = null,
    [FromQuery, SwaggerParameter("Número de página (1-based)")] [Range(1, int.MaxValue)] int page = 1,
    [FromQuery, SwaggerParameter("Items por página")] [Range(10, 100)] int pageSize = 20,
    [FromQuery, SwaggerParameter("Campo de ordenamiento")] string sortBy = "createdAt",
    [FromQuery, SwaggerParameter("Dirección (asc/desc)")] string sortOrder = "desc")
{
    var result = await _orderService.GetOrdersAsync(
        new OrderFilters(status, customerId, minAmount, maxAmount),
        new PaginationParams(page, pageSize),
        new SortParams(sortBy, sortOrder)
    );

    return Ok(result);
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** generar especificación OpenAPI 3.0+
- **MUST** documentar todos los endpoints públicos
- **MUST** incluir comentarios XML (`<summary>`, `<remarks>`, `<response>`)
- **MUST** especificar códigos de respuesta con `[ProducesResponseType]`
- **MUST** proporcionar ejemplos para requests y responses
- **MUST** documentar tipos de datos de respuesta (`typeof(OrderDto)`)
- **MUST** marcar propiedades requeridas con `[Required]`
- **MUST** incluir descripción de parámetros
- **MUST** deshabilitar Swagger en Producción
- **MUST** usar HTTPS en especificación OpenAPI

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar `[SwaggerOperation]` para metadata enriquecido
- **SHOULD** proporcionar `<example>` para propiedades DTO
- **SHOULD** incluir información de seguridad (JWT, OAuth)
- **SHOULD** documentar validaciones con DataAnnotations
- **SHOULD** usar `<remarks>` para ejemplos complejos
- **SHOULD** agrupar endpoints con Tags
- **SHOULD** incluir información de licencia y contacto
- **SHOULD** generar archivo `swagger.json` en CI/CD para validación

### MAY (Opcional)

- **MAY** personalizar UI de Swagger con logo corporativo
- **MAY** generar clientes a partir de especificación (NSwag, OpenAPI Generator)
- **MAY** publicar especificación en portal de desarrolladores
- **MAY** versionar especificación OpenAPI

### MUST NOT (Prohibido)

- **MUST NOT** exponer Swagger en Producción sin autenticación
- **MUST NOT** incluir información sensible en ejemplos (tokens, passwords)
- **MUST NOT** dejar endpoints sin documentar
- **MUST NOT** usar descripciones genéricas ("Gets data", "Returns result")

---

## Referencias

- [Lineamiento: APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md)
- Estándares relacionados:
  - [Estándares REST](api-rest-standards.md)
  - [Versionado de APIs](api-versioning.md)
  - [Manejo de Errores](api-error-handling.md)
- Especificaciones:
  - [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.3)
  - [Swashbuckle Documentation](https://github.com/domaindrivendev/Swashbuckle.AspNetCore)
  - [XML Comments](https://learn.microsoft.com/en-us/aspnet/core/tutorials/getting-started-with-swashbuckle)
