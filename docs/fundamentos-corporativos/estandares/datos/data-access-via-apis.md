---
id: data-access-via-apis
sidebar_position: 4
title: Data Access via APIs
description: Estándar para acceso a datos exclusivamente vía APIs, evitando acceso directo a bases de datos entre servicios
---

# Estándar Técnico — Data Access via APIs

---

## 1. Propósito

Garantizar que el acceso a datos entre servicios ocurra exclusivamente mediante APIs bien definidas, evitando acoplamiento directo a bases de datos y preservando encapsulación, evolución independiente y ownership claro.

---

## 2. Alcance

**Aplica a:**

- Comunicación entre microservicios
- Acceso desde aplicaciones externas
- Integraciones con third-party systems
- Mobile y frontend apps
- Reportes y analytics (via API layer)
- Migraciones de datos entre servicios

**No aplica a:**

- Queries internos dentro del mismo bounded context
- Database administration tasks
- Backups y disaster recovery
- ETL jobs del mismo servicio
- Debugging en ambientes no productivos (con aprobación)

---

## 3. Tecnologías Aprobadas

| Componente      | Tecnología           | Versión mínima | Observaciones                       |
| --------------- | -------------------- | -------------- | ----------------------------------- |
| **REST APIs**   | ASP.NET Core Web API | 8.0+           | Preferido para CRUD y queries       |
| **GraphQL**     | HotChocolate         | 13.0+          | Para aggregated queries complejas   |
| **gRPC**        | Grpc.AspNetCore      | 2.59+          | Para comunicación interna high-perf |
| **API Gateway** | Kong Gateway         | 3.4+           | Routing, auth, rate limiting        |
| **API Docs**    | Swagger/OpenAPI      | 3.0+           | Spec generada automáticamente       |
| **Validation**  | FluentValidation     | 11.8+          | Input validation en API layer       |
| **Versioning**  | Asp.Versioning       | 8.0+           | API versioning explícito            |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Prohibición de Acceso Directo

- [ ] **Ningún servicio puede conectarse directamente a BD de otro servicio**
- [ ] Connection strings de otros servicios no accesibles
- [ ] Network policies bloquean acceso cross-service a DBs
- [ ] Violaciones detectadas en code review y audit

### API Layer Obligatorio

- [ ] Todo dato expuesto mediante endpoint REST, gRPC o GraphQL
- [ ] API documentada con OpenAPI/Protobuf spec
- [ ] Contratos de API versionados
- [ ] Cambios breaking requieren nueva versión de API

### Encapsulación de Datos

- [ ] Servicio owner expone solo datos necesarios (no full tables)
- [ ] DTOs específicos por caso de uso (no entities directas)
- [ ] Proyecciones para queries complejas
- [ ] HATEOAS links para navegación

### Autenticación y Autorización

- [ ] OAuth 2.0 / JWT para autenticación
- [ ] Scopes/claims para autorización granular
- [ ] API keys para integraciones M2M
- [ ] Rate limiting por consumer

### Versionado de Contratos

- [ ] Versioning en URL (`/api/v1/orders`) o header
- [ ] Deprecation warnings con sunset date
- [ ] Soporte de múltiples versiones simultáneas (mínimo 6 meses)
- [ ] Changelog de cambios en API

### Observabilidad

- [ ] Logs estructurados de requests/responses
- [ ] Métricas de latencia, throughput, errors
- [ ] Distributed tracing (correlation IDs)
- [ ] Auditoría de accesos a datos sensibles

---

## 5. Prohibiciones

- ❌ Connection string a BD de otro servicio
- ❌ Queries SQL directos cross-service
- ❌ Shared database entre servicios
- ❌ Acceso directo desde frontend a base de datos
- ❌ Bypass de API layer para "performance"
- ❌ Exponer entities de EF Core directamente como DTOs
- ❌ APIs sin documentación ni contrato

---

## 6. Configuración Mínima

### ASP.NET Core API con Swagger

```csharp
// Program.cs
using Microsoft.OpenApi.Models;
using Asp.Versioning;

var builder = WebApplication.CreateBuilder(args);

// API Versioning
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
    options.ApiVersionReader = new UrlSegmentApiVersionReader();
});

// Swagger/OpenAPI
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Orders API",
        Version = "v1",
        Description = "API for managing orders in Talma platform",
        Contact = new OpenApiContact
        {
            Name = "Platform Team",
            Email = "platform@talma.com"
        }
    });

    // Security definition
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using Bearer scheme",
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

// Authentication
builder.Services.AddAuthentication("Bearer")
    .AddJwtBearer(options =>
    {
        options.Authority = "https://auth.talma.com";
        options.Audience = "orders-api";
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true
        };
    });

// Authorization
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("ReadOrders", policy =>
        policy.RequireClaim("scope", "orders.read"));

    options.AddPolicy("WriteOrders", policy =>
        policy.RequireClaim("scope", "orders.write"));
});

builder.Services.AddControllers();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(options =>
    {
        options.SwaggerEndpoint("/swagger/v1/swagger.json", "Orders API v1");
    });
}

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### Controller con DTOs

```csharp
// Controllers/OrdersController.cs
[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/[controller]")]
[Produces("application/json")]
public class OrdersController : ControllerBase
{
    private readonly IOrderService _orderService;
    private readonly ILogger<OrdersController> _logger;

    /// <summary>
    /// Obtiene una orden por ID
    /// </summary>
    /// <param name="id">ID de la orden</param>
    /// <returns>Detalles de la orden</returns>
    [HttpGet("{id}")]
    [Authorize(Policy = "ReadOrders")]
    [ProducesResponseType(typeof(OrderDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status401Unauthorized)]
    public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
    {
        _logger.LogInformation("Getting order {OrderId}", id);

        var order = await _orderService.GetOrderAsync(id);

        if (order == null)
            return NotFound();

        // Map entity to DTO
        var dto = OrderDto.FromEntity(order);

        return Ok(dto);
    }

    /// <summary>
    /// Crea una nueva orden
    /// </summary>
    [HttpPost]
    [Authorize(Policy = "WriteOrders")]
    [ProducesResponseType(typeof(OrderDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<OrderDto>> CreateOrder(
        [FromBody] CreateOrderRequest request)
    {
        _logger.LogInformation("Creating order for customer {CustomerId}", request.CustomerId);

        var command = new CreateOrderCommand
        {
            CustomerId = request.CustomerId,
            Items = request.Items.Select(i => new OrderItem
            {
                ProductId = i.ProductId,
                Quantity = i.Quantity
            }).ToList()
        };

        var order = await _orderService.CreateOrderAsync(command);
        var dto = OrderDto.FromEntity(order);

        return CreatedAtAction(
            nameof(GetOrder),
            new { id = dto.Id },
            dto);
    }
}

// DTOs/OrderDto.cs
public record OrderDto
{
    public Guid Id { get; init; }
    public Guid CustomerId { get; init; }
    public decimal TotalAmount { get; init; }
    public OrderStatus Status { get; init; }
    public DateTime CreatedAt { get; init; }
    public List<OrderItemDto> Items { get; init; } = new();

    // No exponer entity directa - usar factory method
    public static OrderDto FromEntity(Order order)
    {
        return new OrderDto
        {
            Id = order.Id,
            CustomerId = order.CustomerId,
            TotalAmount = order.TotalAmount,
            Status = order.Status,
            CreatedAt = order.CreatedAt,
            Items = order.Items.Select(OrderItemDto.FromEntity).ToList()
        };
    }
}

public record OrderItemDto
{
    public Guid ProductId { get; init; }
    public string ProductName { get; init; }
    public int Quantity { get; init; }
    public decimal UnitPrice { get; init; }
    public decimal Subtotal { get; init; }

    public static OrderItemDto FromEntity(OrderItem item)
    {
        return new OrderItemDto
        {
            ProductId = item.ProductId,
            ProductName = item.Product.Name,  // Incluir datos de join
            Quantity = item.Quantity,
            UnitPrice = item.UnitPrice,
            Subtotal = item.Quantity * item.UnitPrice
        };
    }
}
```

### Cliente HTTP Tipado

```csharp
// Clients/OrdersApiClient.cs
public class OrdersApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<OrdersApiClient> _logger;

    public OrdersApiClient(HttpClient httpClient, ILogger<OrdersApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<OrderDto?> GetOrderAsync(Guid orderId)
    {
        try
        {
            var response = await _httpClient.GetAsync($"/api/v1/orders/{orderId}");

            if (response.StatusCode == HttpStatusCode.NotFound)
                return null;

            response.EnsureSuccessStatusCode();

            return await response.Content.ReadFromJsonAsync<OrderDto>();
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Error calling Orders API for order {OrderId}", orderId);
            throw;
        }
    }

    public async Task<OrderDto> CreateOrderAsync(CreateOrderRequest request)
    {
        var response = await _httpClient.PostAsJsonAsync("/api/v1/orders", request);
        response.EnsureSuccessStatusCode();

        var order = await response.Content.ReadFromJsonAsync<OrderDto>();
        return order!;
    }
}

// Program.cs - Registration
builder.Services.AddHttpClient<OrdersApiClient>(client =>
{
    client.BaseAddress = new Uri("https://api.talma.com/orders");
    client.DefaultRequestHeaders.Add("Accept", "application/json");
    client.Timeout = TimeSpan.FromSeconds(30);
})
.AddPolicyHandler(GetRetryPolicy())
.AddPolicyHandler(GetCircuitBreakerPolicy());

static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .WaitAndRetryAsync(3, retryAttempt =>
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
}
```

---

## 7. Ejemplos

### gRPC Service

```protobuf
// Protos/orders.proto
syntax = "proto3";

package talma.orders.v1;

service OrdersService {
  rpc GetOrder (GetOrderRequest) returns (OrderResponse);
  rpc CreateOrder (CreateOrderRequest) returns (OrderResponse);
  rpc ListOrders (ListOrdersRequest) returns (ListOrdersResponse);
}

message GetOrderRequest {
  string order_id = 1;
}

message CreateOrderRequest {
  string customer_id = 1;
  repeated OrderItem items = 2;
}

message OrderResponse {
  string id = 1;
  string customer_id = 2;
  double total_amount = 3;
  string status = 4;
  int64 created_at = 5;
}
```

### GraphQL API

```csharp
// GraphQL/OrderQueries.cs
public class OrderQueries
{
    [UseProjection]
    [UseFiltering]
    [UseSorting]
    public IQueryable<OrderDto> GetOrders(
        [Service] IOrderService orderService)
    {
        return orderService.GetOrdersQueryable();
    }

    public async Task<OrderDto?> GetOrder(
        Guid id,
        [Service] IOrderService orderService)
    {
        var order = await orderService.GetOrderAsync(id);
        return order != null ? OrderDto.FromEntity(order) : null;
    }
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Network policies bloquean acceso directo a DBs
- [ ] Code review verifica no hay connection strings cross-service
- [ ] APIs documentadas con OpenAPI/Protobuf
- [ ] DTOs específicos (no entities expuestas)
- [ ] Autenticación y autorización configuradas
- [ ] Rate limiting implementado
- [ ] Distributed tracing activo

### Métricas

```promql
# Request rate por API
rate(http_requests_total{api="orders"}[5m])

# Latencia p95
histogram_quantile(0.95, http_request_duration_seconds)

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

---

## 9. Referencias

**Documentación:**

- [ASP.NET Core Web API](https://learn.microsoft.com/en-us/aspnet/core/web-api/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [gRPC on .NET](https://learn.microsoft.com/en-us/aspnet/core/grpc/)

**Buenas prácticas:**

- Sam Newman - "Building Microservices"
- Martin Fowler - "Microservice Trade-Offs"
- REST API Design Rulebook (O'Reilly)
