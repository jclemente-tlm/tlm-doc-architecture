---
id: event-design
sidebar_position: 2
title: Diseño de Eventos
description: Estándares para estructura, naming conventions y versionado de eventos en Apache Kafka.
tags: [mensajeria, kafka, event-design, naming, versionado]
---

# Diseño de Eventos

## Contexto

Este estándar define estructura, naming conventions, versionado y contratos de eventos para asegurar consistencia, evolucionabilidad y comprensión cross-service en sistemas Kafka. Complementa el lineamiento [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md).

---

## Stack Tecnológico

| Componente         | Tecnología       | Versión | Uso                                 |
| ------------------ | ---------------- | ------- | ----------------------------------- |
| **Message Broker** | Apache Kafka     | 3.6+    | Event streaming platform            |
| **Serialization**  | System.Text.Json | .NET 8  | Serialización JSON de eventos       |
| **Schema**         | JSON Schema      | -       | Validación de estructura de eventos |

---

## Event Design

### ¿Qué es Event Design?

Definición de estructura, naming conventions, versionado y contratos de eventos para asegurar consistencia, evolucionabilidad y comprensión cross-service.

**Propósito:** Estandarizar eventos para facilitar integración, debugging y evolución.

**Componentes clave:**

- **Event structure**: Metadata + payload
- **Naming conventions**: `{domain}.{entity}.{action}` (past tense)
- **Versioning**: Semantic versioning para evolución
- **Backward compatibility**: Cambios no rompen consumers existentes

**Beneficios:**
✅ Comprensión rápida de eventos
✅ Debugging simplificado (metadata rica)
✅ Evolución sin breaking changes
✅ Integración cross-team facilitada

### Event Structure Standard

```csharp
// Estructura base de evento (envelope pattern)
public abstract class DomainEvent
{
    // METADATA (común a todos los eventos)

    [JsonPropertyName("event_id")]
    public Guid EventId { get; set; } = Guid.NewGuid();

    [JsonPropertyName("event_type")]
    public string EventType { get; set; }  // "order.created"

    [JsonPropertyName("event_version")]
    public string EventVersion { get; set; }  // "1.0"

    [JsonPropertyName("timestamp")]
    public DateTimeOffset Timestamp { get; set; } = DateTimeOffset.UtcNow;

    [JsonPropertyName("correlation_id")]
    public string? CorrelationId { get; set; }  // Para tracing distribuido

    [JsonPropertyName("causation_id")]
    public string? CausationId { get; set; }  // ID del evento que causó este

    [JsonPropertyName("source_service")]
    public string SourceService { get; set; }  // "order-service"

    [JsonPropertyName("aggregate_id")]
    public string AggregateId { get; set; }  // ID del aggregate (OrderId, CustomerId, etc.)

    [JsonPropertyName("aggregate_type")]
    public string AggregateType { get; set; }  // "Order", "Customer", etc.
}

// Evento específico
public class OrderCreatedEvent : DomainEvent
{
    public OrderCreatedEvent()
    {
        EventType = "order.created";
        EventVersion = "1.0";
        SourceService = "order-service";
        AggregateType = "Order";
    }

    // PAYLOAD (específico del evento)

    [JsonPropertyName("order_id")]
    public Guid OrderId { get; set; }

    [JsonPropertyName("customer_id")]
    public Guid CustomerId { get; set; }

    [JsonPropertyName("items")]
    public List<OrderItemDto> Items { get; set; }

    [JsonPropertyName("total_amount")]
    public decimal TotalAmount { get; set; }

    [JsonPropertyName("currency")]
    public string Currency { get; set; } = "USD";

    [JsonPropertyName("status")]
    public string Status { get; set; } = "Pending";
}

public class OrderItemDto
{
    [JsonPropertyName("product_id")]
    public Guid ProductId { get; set; }

    [JsonPropertyName("quantity")]
    public int Quantity { get; set; }

    [JsonPropertyName("unit_price")]
    public decimal UnitPrice { get; set; }
}
```

**Ejemplo JSON serializado:**

```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_type": "order.created",
  "event_version": "1.0",
  "timestamp": "2026-02-19T15:30:00Z",
  "correlation_id": "req-123456",
  "causation_id": null,
  "source_service": "order-service",
  "aggregate_id": "550e8400-e29b-41d4-a716-446655440000",
  "aggregate_type": "Order",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "items": [
    {
      "product_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
      "quantity": 2,
      "unit_price": 29.99
    }
  ],
  "total_amount": 59.98,
  "currency": "USD",
  "status": "Pending"
}
```

### Naming Conventions

| Componente     | Formato                                   | Ejemplo                              |
| -------------- | ----------------------------------------- | ------------------------------------ |
| **Event Type** | `{domain}.{entity}.{action}` (past tense) | `order.created`, `payment.completed` |
| **Topic Name** | `{domain}.{entity}.{action}` (snake_case) | `order.created`, `customer.updated`  |
| **Class Name** | `{Entity}{Action}Event` (PascalCase)      | `OrderCreatedEvent`                  |
| **Properties** | `snake_case` en JSON, `PascalCase` en C#  | `customer_id` / `CustomerId`         |

**Verbos recomendados (past tense):**

- `created`, `updated`, `deleted`
- `submitted`, `approved`, `rejected`
- `completed`, `failed`, `cancelled`
- `started`, `finished`, `expired`

**Antipatrones:**

- ❌ `CreateOrder` (imperativo, usa `order.created`)
- ❌ `OrderCreate` (no past tense, usa `order.created`)
- ❌ `order-created` (guión no estandarizado, usa punto)
- ❌ `ORDER_CREATED` (mayúsculas, usa minúsculas)

### Event Versioning

```csharp
// VERSION 1.0 (inicial)
public class OrderCreatedEventV1 : DomainEvent
{
    public OrderCreatedEventV1()
    {
        EventType = "order.created";
        EventVersion = "1.0";
    }

    public Guid OrderId { get; set; }
    public Guid CustomerId { get; set; }
    public decimal TotalAmount { get; set; }
}

// VERSION 2.0 (agregar campo opcional - BACKWARD COMPATIBLE)
public class OrderCreatedEventV2 : DomainEvent
{
    public OrderCreatedEventV2()
    {
        EventType = "order.created";
        EventVersion = "2.0";
    }

    public Guid OrderId { get; set; }
    public Guid CustomerId { get; set; }
    public decimal TotalAmount { get; set; }

    // Nuevo campo OPCIONAL (nullable)
    public string? PaymentMethod { get; set; }  // ✅ Backward compatible
}

// Consumer que soporta ambas versiones
public class OrderCreatedHandler
{
    public async Task HandleAsync(string eventJson)
    {
        // Deserializar a un objeto base para leer metadata
        using var doc = JsonDocument.Parse(eventJson);
        var version = doc.RootElement.GetProperty("event_version").GetString();

        switch (version)
        {
            case "1.0":
                var eventV1 = JsonSerializer.Deserialize<OrderCreatedEventV1>(eventJson);
                await ProcessV1(eventV1);
                break;

            case "2.0":
                var eventV2 = JsonSerializer.Deserialize<OrderCreatedEventV2>(eventJson);
                await ProcessV2(eventV2);
                break;

            default:
                throw new NotSupportedException($"Event version {version} not supported");
        }
    }
}
```

**Reglas de versionado:**

| Cambio                          | Versión | Compatibilidad         |
| ------------------------------- | ------- | ---------------------- |
| Agregar campo opcional          | Minor   | ✅ Backward compatible |
| Cambiar nombre de campo         | Major   | ❌ Breaking change     |
| Eliminar campo                  | Major   | ❌ Breaking change     |
| Cambiar tipo de campo           | Major   | ❌ Breaking change     |
| Cambiar semántica (sin cambios) | N/A     | Evitar (documentar)    |

**Estrategia de deprecación:**

1. Publicar versión 2.0 nueva
2. Producer publica **ambas versiones** (1.0 y 2.0) por período de transición
3. Consumers migran gradualmente a 2.0
4. Después de N meses, deprecar 1.0 (solo publicar 2.0)

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** incluir metadata estándar en todos los eventos: `event_id`, `event_type`, `event_version`, `timestamp`, `correlation_id`, `source_service`, `aggregate_id`
- **MUST** usar naming convention `{domain}.{entity}.{action}` (past tense) para event types
- **MUST** usar semantic versioning para eventos (major.minor)
- **MUST** mantener backward compatibility en cambios minor (solo agregar campos opcionales)
- **MUST** serializar eventos en JSON con `snake_case` para property names

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar envelope pattern (base class `DomainEvent` con metadata común)
- **SHOULD** incluir `causation_id` para rastrear causalidad entre eventos
- **SHOULD** agregar headers Kafka con metadata (`event-type`, `event-version`, `correlation-id`)
- **SHOULD** validar schemas de eventos con JSON Schema
- **SHOULD** publicar múltiples versiones de eventos durante período de transición

### MUST NOT (Prohibido)

- **MUST NOT** cambiar semántica de evento existente sin cambiar version major
- **MUST NOT** publicar eventos con información sensible sin encriptar

---

## Referencias

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [JSON Schema](https://json-schema.org/)
- [Martin Fowler - Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)
- [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) — Lineamiento relacionado
- [Async Messaging](./async-messaging.md)
- [Event Catalog](./event-catalog.md)
- [Event Contracts](./event-contracts.md)
