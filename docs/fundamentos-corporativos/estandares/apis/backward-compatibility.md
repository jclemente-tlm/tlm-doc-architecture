---
id: backward-compatibility
sidebar_position: 5
title: Compatibilidad Hacia Atrás
description: Estrategias para evolucionar APIs REST sin romper clientes existentes usando Expand-Contract, deprecación y versionamiento semántico.
tags: [apis, rest, backward-compatibility, expand-contract, deprecacion]
---

# Compatibilidad Hacia Atrás

## Contexto

Este estándar define cómo realizar cambios en APIs sin romper clientes existentes. Complementa el lineamiento [APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md).

**Cuándo aplicar:** Al evolucionar cualquier API ya desplegada con clientes activos.

---

## Stack Tecnológico

| Componente         | Tecnología         | Versión | Uso                           |
| ------------------ | ------------------ | ------- | ----------------------------- |
| **Framework**      | ASP.NET Core       | 8.0+    | Construcción de APIs          |
| **Versionamiento** | Asp.Versioning.Mvc | 8.0+    | Deprecación controlada        |
| **Serialización**  | System.Text.Json   | 8.0+    | Manejo de campos desconocidos |

---

## Cambios Seguros vs Incompatibles

**Cambios seguros (compatibles — se pueden hacer sin nueva versión MAJOR):**

✅ Agregar endpoint nuevo
✅ Agregar campo opcional al request
✅ Agregar campo a la response
✅ Agregar valor a un enum (requiere manejo de `Unknown`)
✅ Deprecar endpoint con aviso

**Cambios incompatibles (requieren nueva versión MAJOR):**

❌ Remover endpoint
❌ Remover campo de response
❌ Cambiar tipo de un campo existente
❌ Convertir campo opcional en requerido
❌ Cambiar semántica de comportamiento existente

---

## Estrategia Expand-Contract

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
public async Task<ActionResult<OrderDto>> Create(CreateOrderRequest request)
{
    Guid customerId;

    if (request.CustomerId.HasValue)
    {
        customerId = request.CustomerId.Value;
    }
    else if (!string.IsNullOrEmpty(request.Customer))
    {
        // Compatibilidad hacia atrás: convertir el campo legacy
        customerId = await _customerService.GetIdByLegacyCodeAsync(request.Customer);
    }
    else
    {
        return BadRequest("CustomerId es requerido");
    }

    var order = await _orderService.CreateAsync(customerId, request.Items);
    return CreatedAtAction(nameof(GetById), new { id = order.Id }, order);
}

// Fase 2 CONTRACT: En v2.0, remover el campo deprecado
// public record CreateOrderRequest
// {
//     public required Guid CustomerId { get; init; }  // Solo este
//     public OrderItemDto[] Items { get; init; } = Array.Empty<OrderItemDto>();
// }
```

---

## Enums Extensibles

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
    Refunded   = 6   // ✅ Safe: agregar nuevos valores es compatible
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

## Deprecación de Endpoints

```csharp
[HttpGet("legacy-search")]
[Obsolete("Usar GET /api/v1/customers con parámetro ?query= en su lugar")]
public async Task<ActionResult<CustomerDto[]>> LegacySearch([FromQuery] string name)
{
    // RFC 8594: Sunset header comunica fecha de retiro
    Response.Headers.Append("Sunset", "Sat, 31 Dec 2026 23:59:59 GMT");
    Response.Headers.Append("Warning",
        "299 - \"Este endpoint está deprecado. " +
        "Usar GET /api/v1/customers?query={name}\"");

    return Ok(await _customerService.SearchByNameAsync(name));
}
```

---

## Versionamiento Semántico

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

## Matriz de Decisión

| Escenario                | REST Standards | Contracts | Versioning | Pagination | BackCompat |
| ------------------------ | -------------- | --------- | ---------- | ---------- | ---------- |
| API nueva interna        | ✅             | ✅        | —          | ✅         | —          |
| API pública/externa      | ✅             | ✅        | ✅         | ✅         | ✅         |
| Microservicio síncrono   | ✅             | ✅        | ✅         | ✅         | ✅         |
| API con clientes móviles | ✅             | ✅        | ✅         | ✅         | ✅         |
| API legacy (refactor)    | ✅             | ✅        | ✅         | ✅         | ✅         |

---

## Beneficios en Práctica

| Sin estrategia de compatibilidad            | Con Expand-Contract + deprecación   |
| ------------------------------------------- | ----------------------------------- |
| Cambios rompen clientes sin aviso           | Período de transición controlado    |
| Coordinación síncrona con todos los equipos | Despliegues independientes          |
| Rollback de toda la API                     | Solo el campo/endpoint problemático |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** mantener compatibilidad hacia atrás en versiones MINOR y PATCH
- **MUST** deprecar endpoints al menos 6 meses antes de removerlos
- **MUST** usar estrategia Expand-Contract para cambios incompatibles
- **MUST** incluir header `Sunset` (RFC 8594) en endpoints deprecados
- **MUST** comunicar deprecación en Swagger (`Deprecated = true`)

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir header `Warning` en responses de endpoints deprecados
- **SHOULD** agregar valor `Unknown = 0` en todos los enums de API
- **SHOULD** comunicar cambios incompatibles con al menos 3 meses de anticipación

### MUST NOT (Prohibido)

- **MUST NOT** romper clientes existentes en versiones MINOR o PATCH
- **MUST NOT** remover endpoints sin período de deprecación previo

---

## Referencias

- [RFC 8594 - Sunset Header](https://www.rfc-editor.org/rfc/rfc8594.html) — Estándar de deprecación HTTP
- [API Evolution Patterns](https://www.martinfowler.com/articles/enterpriseREST.html) — Expand-Contract y patrones
- [Versionamiento de APIs](./api-versioning.md) — Configuración de Asp.Versioning.Mvc
- [Contratos de APIs](./api-contracts.md) — DTOs y OpenAPI
- [Estándares REST](./api-rest-standards.md) — Base HTTP
