---
id: rest-standards
sidebar_position: 1
title: Estándares REST
description: Principios REST, convenciones HTTP, estructura de URIs y códigos de estado para APIs consistentes.
tags: [apis, rest, http, uri, status-codes]
---

# Estándares REST

## Contexto

Este estándar define los principios REST y convenciones HTTP base para toda API de la organización. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Cuándo aplicar:** Siempre. Es la base obligatoria de toda API REST, independientemente del dominio.

---

## Stack Tecnológico

| Componente          | Tecnología         | Versión | Uso                      |
| ------------------- | ------------------ | ------- | ------------------------ |
| **Framework**       | ASP.NET Core       | 8.0+    | Construcción de APIs     |
| **Serialización**   | System.Text.Json   | 8.0+    | JSON serialization       |
| **Problem Details** | Hellang.Middleware | 6.5+    | RFC 7807 Problem Details |

---

## Principios REST

**Restricciones fundamentales:**

- **Recursos**: Sustantivos (no verbos) en URIs
- **Stateless**: Sin estado de sesión en el servidor
- **Cacheable**: Uso de headers HTTP de caché
- **Uniform Interface**: Consistencia en operaciones entre recursos

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
    [ProducesResponseType(typeof(PagedResult<CustomerDto>), StatusCodes.Status200OK)]
    public async Task<ActionResult<PagedResult<CustomerDto>>> GetAll(
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var result = await _customerService.GetPagedAsync(page, pageSize);
        return Ok(result);
    }

    [HttpGet("{id}")]
    [ProducesResponseType(typeof(CustomerDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<CustomerDto>> GetById(Guid id)
    {
        var customer = await _customerService.GetByIdAsync(id);
        if (customer == null) return NotFound();
        return Ok(customer);
    }

    [HttpPost]
    [ProducesResponseType(typeof(CustomerDto), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<CustomerDto>> Create([FromBody] CreateCustomerRequest request)
    {
        var customer = await _customerService.CreateAsync(request);
        return CreatedAtAction(nameof(GetById), new { id = customer.Id }, customer);
    }

    [HttpPut("{id}")]
    [ProducesResponseType(typeof(CustomerDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<CustomerDto>> Update(Guid id, [FromBody] UpdateCustomerRequest request)
    {
        var customer = await _customerService.UpdateAsync(id, request);
        if (customer == null) return NotFound();
        return Ok(customer);
    }

    [HttpDelete("{id}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Delete(Guid id)
    {
        var deleted = await _customerService.DeleteAsync(id);
        if (!deleted) return NotFound();
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

builder.Services.AddProblemDetails(options =>
{
    options.CustomizeProblemDetails = context =>
    {
        context.ProblemDetails.Instance = context.HttpContext.Request.Path;
        context.ProblemDetails.Extensions["traceId"] = context.HttpContext.TraceIdentifier;
    };
});
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

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar ETags para caching
- **SHOULD** soportar compresión (gzip, brotli)
- **SHOULD** implementar rate limiting
- **SHOULD** incluir CORS para APIs públicas
- **SHOULD** incluir headers de trazabilidad (X-Request-ID, X-Correlation-ID)

### MAY (Opcional)

- **MAY** soportar múltiples formatos de respuesta (JSON, XML) via content negotiation
- **MAY** incluir API health checks (`/health`, `/ready`)
- **MAY** soportar filtrado, ordenamiento y búsqueda en colecciones

### MUST NOT (Prohibido)

- **MUST NOT** usar verbos en URIs (`/getCustomers`, `/createOrder`)
- **MUST NOT** exponer detalles de implementación interna en URIs o responses
- **MUST NOT** usar códigos de estado genéricos (evitar siempre 200 con error en body)
- **MUST NOT** retornar stack traces o información sensible en errores

---

## Monitoreo y Observabilidad

:::note Métricas de APIs
Para métricas de requests (latencia, status codes, throughput) ver [Métricas y Estándares](../observabilidad/metrics-standards.md).
:::

---

## Referencias

- [RFC 9110 - HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) — Semántica HTTP
- [RFC 7807 - Problem Details](https://www.rfc-editor.org/rfc/rfc7807.html) — Problem Details
- [ASP.NET Core Web APIs](https://learn.microsoft.com/aspnet/core/web-api/) — Documentación oficial
- [REST API Design Rulebook (O'Reilly)](https://www.oreilly.com/library/view/rest-api-design/9781449317904/) — Patrones REST
- [Contratos de APIs](./api-contracts.md) — Estándar relacionado
- [Manejo de Errores en APIs](./api-error-handling.md) — Estándar relacionado
