---
id: api-backward-compatibility
sidebar_position: 6
title: Retrocompatibilidad de APIs
description: Reglas para evolucionar APIs sin romper integraciones existentes
---

# Retrocompatibilidad de APIs

## Contexto

Este estándar define las reglas para evolucionar APIs sin romper integraciones con consumidores existentes. Complementa el [lineamiento de APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md) y el [estándar de versionado](api-versioning.md) especificando qué cambios son compatibles y cuáles requieren nueva versión.

---

## Stack Tecnológico

| Componente        | Tecnología          | Versión | Uso                             |
| ----------------- | ------------------- | ------- | ------------------------------- |
| **Framework**     | ASP.NET Core        | 8.0+    | Framework base                  |
| **Versionado**    | Asp.Versioning.Http | 8.0+    | Gestión de versiones            |
| **Serialización** | System.Text.Json    | 8.0+    | JSON con opciones de tolerancia |

### Dependencias NuGet

```xml
<PackageReference Include="Asp.Versioning.Http" Version="8.0.0" />
<PackageReference Include="System.Text.Json" Version="8.0.0" />
```

---

## Implementación Técnica

### Cambios Compatibles (No Requieren Nueva Versión)

#### ✅ Agregar Campo Opcional a Response

```csharp
// V1 - Original
public record OrderDto
{
    public Guid Id { get; init; }
    public string OrderNumber { get; init; }
    public decimal TotalAmount { get; init; }
}

// V1.1 - Compatible: Agregar campo opcional
public record OrderDto
{
    public Guid Id { get; init; }
    public string OrderNumber { get; init; }
    public decimal TotalAmount { get; init; }

    // ✅ COMPATIBLE: Campo nuevo opcional
    public string? TrackingNumber { get; init; }  // Puede ser null
    public DateTime? EstimatedDelivery { get; init; }
}

// ✅ Clientes antiguos ignoran campos desconocidos (JSON tolerante)
```

#### ✅ Agregar Endpoint Nuevo

```csharp
// V1 - Endpoints originales
[ApiVersion("1.0")]
public class OrdersController : ControllerBase
{
    [HttpGet("{id}")]
    public async Task<ActionResult<OrderDto>> GetOrder(Guid id) { }

    [HttpPost]
    public async Task<ActionResult<OrderDto>> CreateOrder(CreateOrderRequest request) { }

    // ✅ COMPATIBLE: Nuevo endpoint
    [HttpGet("{id}/timeline")]
    public async Task<ActionResult<OrderTimelineDto>> GetOrderTimeline(Guid id)
    {
        // Endpoint completamente nuevo - no afecta consumidores existentes
        var timeline = await _orderService.GetTimelineAsync(id);
        return Ok(timeline);
    }
}
```

#### ✅ Hacer Campo de Request Opcional

```csharp
// V1 - Campo requerido
public record CreateOrderRequest
{
    [Required]
    public Guid CustomerId { get; init; }

    [Required]
    public string ShippingMethod { get; init; }  // Requerido
}

// V1.1 - Compatible: Campo ahora opcional
public record CreateOrderRequest
{
    [Required]
    public Guid CustomerId { get; init; }

    // ✅ COMPATIBLE: Ahora opcional con default
    public string? ShippingMethod { get; init; } = "Standard";
}

// ✅ Clientes antiguos siguen enviando el campo
// ✅ Clientes nuevos pueden omitirlo
```

#### ✅ Agregar Valor a Enum (Con Handling Adecuado)

```csharp
// V1 - Enum original
public enum OrderStatus
{
    Pending = 0,
    Confirmed = 1,
    Shipped = 2,
    Delivered = 3
}

// V1.1 - Compatible: Nuevo valor con deserialización tolerante
public enum OrderStatus
{
    Pending = 0,
    Confirmed = 1,
    Shipped = 2,
    Delivered = 3,
    // ✅ COMPATIBLE: Nuevo valor
    Returned = 4
}

// ✅ Configurar JsonSerializerOptions para manejar valores desconocidos
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        // ✅ No fallar con valores de enum desconocidos
        options.JsonSerializerOptions.Converters.Add(
            new JsonStringEnumConverter()
        );
    });

// ⚠️ PRECAUCIÓN: Clientes antiguos pueden recibir valor desconocido
// Deben estar preparados para manejar valores no reconocidos
```

#### ✅ Deprecar Campo (Con Período de Transición)

```csharp
// V1 - Campo activo
public record OrderDto
{
    public Guid Id { get; init; }

    [Obsolete("Use CustomerId instead. Will be removed in V2.")]
    public int LegacyCustomerId { get; init; }  // Deprecado pero presente

    public Guid CustomerId { get; init; }  // Nuevo campo recomendado
}

// ✅ Mantener campo deprecado funcionando por período de transición (6 meses)
// ✅ Documentar en release notes
// ✅ Incluir en respuesta con warning header
Response.Headers["Warning"] = "299 - \"LegacyCustomerId is deprecated. Use CustomerId instead.\"";
```

### Cambios Incompatibles (Requieren Nueva Versión)

#### ❌ Eliminar Campo de Response

```csharp
// V1
public record OrderDto
{
    public Guid Id { get; init; }
    public string OrderNumber { get; init; }
    public string TrackingNumber { get; init; }  // ❌ BREAKING: Eliminar esto
}

// ✅ SOLUCIÓN: Crear V2
namespace V2;
public record OrderDto
{
    public Guid Id { get; init; }
    public string OrderNumber { get; init; }
    // TrackingNumber eliminado en V2
}
```

#### ❌ Renombrar Campo

```csharp
// V1
public record OrderDto
{
    public Guid CustomerId { get; init; }  // ❌ BREAKING: Renombrar a BuyerId
}

// ✅ SOLUCIÓN: Crear V2 o mantener ambos temporalmente
// Opción 1: V2 con campo renombrado
namespace V2;
public record OrderDto
{
    public Guid BuyerId { get; init; }  // Nuevo nombre
}

// Opción 2: Período de transición (mantener ambos en V1)
public record OrderDto
{
    [Obsolete("Use BuyerId instead")]
    public Guid CustomerId { get; init; }  // Mantener 6 meses

    [JsonPropertyName("buyerId")]
    public Guid BuyerId => CustomerId;  // Alias
}
```

#### ❌ Cambiar Tipo de Dato

```csharp
// V1
public record OrderDto
{
    public int OrderNumber { get; init; }  // ❌ BREAKING: Cambiar a string
}

// ✅ SOLUCIÓN: Crear V2
namespace V2;
public record OrderDto
{
    public string OrderNumber { get; init; }  // Nuevo tipo
}
```

#### ❌ Hacer Campo de Request Requerido

```csharp
// V1
public record CreateOrderRequest
{
    public string? Comment { get; init; }  // Opcional
}

// ❌ BREAKING: Hacer requerido
public record CreateOrderRequest
{
    [Required]  // ❌ Rompe clientes que no lo envían
    public string Comment { get; init; }
}

// ✅ SOLUCIÓN: Crear V2 o agregar valor por defecto
public record CreateOrderRequest
{
    public string Comment { get; init; } = string.Empty;  // Default
}
```

#### ❌ Eliminar Endpoint

```csharp
// V1
[ApiVersion("1.0")]
public class OrdersController
{
    [HttpGet("{id}")]
    public async Task<ActionResult<OrderDto>> GetOrder(Guid id) { }  // ❌ Eliminar
}

// ✅ SOLUCIÓN: Deprecar en V1, eliminar en V2
[ApiVersion("1.0", Deprecated = true)]
[ApiVersion("2.0")]
public class OrdersController
{
    [HttpGet("{id}")]
    [MapToApiVersion("1.0")]
    [Obsolete("Endpoint removed in V2. Use /orders endpoint instead.")]
    public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
    {
        Response.Headers["Sunset"] = "Sat, 31 Dec 2024 23:59:59 GMT";
        // ...
    }
}
```

#### ❌ Cambiar Semántica de Endpoint

```csharp
// V1 - Operación síncrona
[HttpPost("{id}/process")]
public async Task<ActionResult<OrderDto>> ProcessOrder(Guid id)
{
    var order = await _orderService.ProcessOrderAsync(id);
    return Ok(order);  // ❌ BREAKING: Cambiar a asíncrono retornando 202
}

// ✅ SOLUCIÓN: Crear nuevo endpoint con diferente semántica
[HttpPost("{id}/process-async")]
public async Task<ActionResult> ProcessOrderAsync(Guid id)
{
    var jobId = await _orderService.QueueProcessingAsync(id);
    return Accepted(new { jobId, statusUrl = $"/api/jobs/{jobId}" });
}
```

### Configuración JSON Tolerante

```csharp
// Program.cs - Configurar System.Text.Json para tolerancia
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        // ✅ Ignorar propiedades desconocidas en deserialization
        // (Permite agregar campos a requests sin romper)
        options.JsonSerializerOptions.DefaultIgnoreCondition =
            JsonIgnoreCondition.WhenWritingNull;

        // ✅ Case-insensitive property matching
        options.JsonSerializerOptions.PropertyNameCaseInsensitive = true;

        // ✅ camelCase naming
        options.JsonSerializerOptions.PropertyNamingPolicy =
            JsonNamingPolicy.CamelCase;

        // ✅ Permitir trailing commas
        options.JsonSerializerOptions.AllowTrailingCommas = true;

        // ✅ Manejar enums como strings
        options.JsonSerializerOptions.Converters.Add(
            new JsonStringEnumConverter(JsonNamingPolicy.CamelCase)
        );
    });
```

### Testing de Compatibilidad

```csharp
// Tests/CompatibilityTests.cs
public class OrderApiCompatibilityTests
{
    [Fact]
    public async Task GetOrder_V1Response_ShouldDeserializeWithV1Client()
    {
        // Arrange: Cliente con DTO V1
        var v1Response = """
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "orderNumber": "ORD-2024-001",
            "totalAmount": 299.99
        }
        """;

        // Act: Deserializar con V1 DTO
        var order = JsonSerializer.Deserialize<OrderV1Dto>(v1Response);

        // Assert
        Assert.NotNull(order);
        Assert.Equal("ORD-2024-001", order.OrderNumber);
    }

    [Fact]
    public async Task GetOrder_V1dot1ResponseWithExtraFields_ShouldDeserializeWithV1Client()
    {
        // Arrange: Response con campos nuevos (V1.1)
        var v1dot1Response = """
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "orderNumber": "ORD-2024-001",
            "totalAmount": 299.99,
            "trackingNumber": "ABC123",
            "estimatedDelivery": "2024-02-01T10:00:00Z"
        }
        """;

        // Act: Deserializar con V1 DTO (sin nuevos campos)
        var order = JsonSerializer.Deserialize<OrderV1Dto>(v1dot1Response);

        // Assert: ✅ No falla, ignora campos desconocidos
        Assert.NotNull(order);
        Assert.Equal("ORD-2024-001", order.OrderNumber);
    }

    [Fact]
    public async Task CreateOrder_V1ClientSendingOnlyRequiredFields_ShouldSucceed()
    {
        // Arrange: Request V1 sin campos opcionales nuevos
        var v1Request = """
        {
            "customerId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "items": [
                {
                    "productId": "5fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "quantity": 2
                }
            ]
        }
        """;

        // Act: Enviar a API V1.1 (con campos opcionales nuevos)
        var response = await _client.PostAsync(
            "/api/v1/orders",
            new StringContent(v1Request, Encoding.UTF8, "application/json")
        );

        // Assert: ✅ Debe funcionar
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    }
}
```

### Contract Testing para Compatibilidad

```csharp
// Tests/ContractTests/OrderApiContractTests.cs
using PactNet;

public class OrderApiContractTests
{
    [Fact]
    public async Task GetOrder_ShouldMatchPublishedContract()
    {
        // ✅ Verificar que API cumple contrato publicado
        var pact = Pact.V3("OrderConsumer", "OrderAPI", _pactConfig);

        pact.UponReceiving("A GET request for an order")
            .Given("Order 550e8400-e29b-41d4-a716-446655440000 exists")
            .WithRequest(HttpMethod.Get, "/api/v1/orders/550e8400-e29b-41d4-a716-446655440000")
            .WillRespond()
            .WithStatus(200)
            .WithJsonBody(new
            {
                id = Match.Regex("550e8400-e29b-41d4-a716-446655440000", "^[0-9a-f-]+$"),
                orderNumber = Match.Type("ORD-2024-001"),
                totalAmount = Match.Decimal(299.99)
                // ✅ No requerir campos opcionales nuevos
            });

        await pact.VerifyAsync(async ctx =>
        {
            var response = await _client.GetAsync("/api/v1/orders/550e8400-e29b-41d4-a716-446655440000");
            response.EnsureSuccessStatusCode();
        });
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

#### Cambios Compatibles (Permitidos sin nueva versión):

- **MUST** agregar campos opcionales a responses
- **MUST** agregar endpoints nuevos
- **MUST** hacer campos de request opcionales (de requerido → opcional)
- **MUST** agregar valores por defecto a campos opcionales
- **MUST** mantener campos deprecados funcionando por mínimo 6 meses

#### Cambios Incompatibles (Requieren nueva versión):

- **MUST** crear nueva versión al eliminar campos de response
- **MUST** crear nueva versión al renombrar campos
- **MUST** crear nueva versión al cambiar tipos de datos
- **MUST** crear nueva versión al hacer campos de request requeridos
- **MUST** crear nueva versión al eliminar endpoints
- **MUST** crear nueva versión al cambiar semántica de operaciones

#### Tests:

- **MUST** validar compatibilidad con tests automatizados
- **MUST** ejecutar contract tests contra versiones publicadas

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar `[Obsolete]` attribute para campos deprecados
- **SHOULD** incluir `Warning` header al retornar campos deprecados
- **SHOULD** incluir `Sunset` header para endpoints deprecados
- **SHOULD** documentar breaking changes en release notes
- **SHOULD** notificar consumidores 6 meses antes de breaking changes
- **SHOULD** configurar JSON serializer para tolerancia (ignore unknown fields)
- **SHOULD** versionar contratos OpenAPI
- **SHOULD** publicar contratos en repositorio central

### MAY (Opcional)

- **MAY** agregar valores a enums si clientes manejan desconocidos
- **MAY** mantener alias de campos renombrados durante transición
- **MAY** implementar feature flags para habilitar/deshabilitar cambios
- **MAY** proporcionar herramienta de migración para consumidores

### MUST NOT (Prohibido)

- **MUST NOT** eliminar campos sin nueva versión
- **MUST NOT** cambiar tipos de datos sin nueva versión
- **MUST NOT** hacer campos opcionales requeridos sin nueva versión
- **MUST NOT** cambiar códigos de estado HTTP de operaciones existentes sin nueva versión
- **MUST NOT** cambiar URLs de endpoints existentes
- **MUST NOT** eliminar versiones antes de período de deprecación (6 meses mínimo)

---

## Checklist de Evolución de API

```markdown
Antes de liberar un cambio, verificar:

□ ¿El cambio afecta contratos existentes?

- NO → Cambio compatible, continuar
- SÍ → Evaluar si requiere nueva versión

□ ¿Elimina o renombra campos?

- SÍ → BREAKING CHANGE → Crear V2
- NO → Continuar

□ ¿Cambia tipos de datos?

- SÍ → BREAKING CHANGE → Crear V2
- NO → Continuar

□ ¿Hace campos opcionales requeridos?

- SÍ → BREAKING CHANGE → Crear V2
- NO → Continuar

□ ¿Agrega campos opcionales a responses?

- SÍ → Compatible → Continuar

□ ¿Hace campos requeridos opcionales?

- SÍ → Compatible → Continuar

□ ¿Agrega nuevos endpoints?

- SÍ → Compatible → Continuar

□ ¿Se depreca algo?

- SÍ → Marcar con [Obsolete]
- SÍ → Documentar en release notes
- SÍ → Planificar eliminación en 6 meses

□ Tests escritos:

- □ Compatibilidad con clientes V1
- □ Contract tests actualizados
- □ OpenAPI spec actualizado

□ Documentación actualizada:

- □ Release notes publicados
- □ Migration guide (si breaking)
- □ Swagger actualizado
```

---

## Referencias

- [Lineamiento: APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md)
- Estándares relacionados:
  - [Estándares REST](api-rest-standards.md)
  - [Versionado de APIs](api-versioning.md)
  - [Contract Testing](../testing/contract-testing.md)
- Especificaciones:
  - [Semantic Versioning](https://semver.org/)
  - [Robustness Principle (Postel's Law)](https://en.wikipedia.org/wiki/Robustness_principle)
  - [RFC 8594: Sunset Header](https://tools.ietf.org/html/rfc8594)
