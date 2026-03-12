---
id: event-catalog
sidebar_position: 3
title: Catálogo de Eventos
description: Estándares para documentar, descubrir y gestionar eventos en arquitecturas event-driven con Apache Kafka.
tags: [mensajeria, kafka, event-catalog, discoverability, documentacion]
---

# Catálogo de Eventos

## Contexto

Este estándar define cómo documentar y gestionar el catálogo centralizado de eventos en arquitecturas Kafka. Cubre la estructura de entrada del catálogo, generación automatizada y la API de descubrimiento de eventos. Complementa el lineamiento [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/comunicacion-asincrona-y-eventos.md).

---

## Stack Tecnológico

| Componente         | Tecnología       | Versión | Uso                                 |
| ------------------ | ---------------- | ------- | ----------------------------------- |
| **Message Broker** | Apache Kafka     | 3.6+    | Event streaming platform            |
| **Serialization**  | System.Text.Json | .NET 8  | Serialización JSON de eventos       |
| **Schema**         | JSON Schema      | -       | Validación de estructura de eventos |

---

## Event Catalog

### ¿Qué es Event Catalog?

Registro centralizado documentando todos los eventos del sistema: esquema, producers, consumers, ejemplos, evolución.

**Propósito:** Single source of truth para descubrir, entender e integrar eventos.

**Componentes clave:**

- **Event schema**: Estructura JSON Schema
- **Producer/Consumer registry**: Quién publica/consume cada evento
- **Examples**: Payloads reales de ejemplo
- **Changelog**: Historial de versiones

**Beneficios:**
✅ Descubrimiento de eventos (qué eventos existen)
✅ Self-service para nuevos consumers
✅ Documentación viva (actualizada con código)
✅ Impact analysis (quién se afecta por cambios)

### Estructura del Event Catalog

````markdown
# Event Catalog

## order.created

**Version**: 2.0
**Status**: Active
**Topic**: `order.created`

### Description

Evento publicado cuando una nueva orden es creada en el sistema.

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "event_id",
    "event_type",
    "order_id",
    "customer_id",
    "total_amount"
  ],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "event_type": { "type": "string", "const": "order.created" },
    "event_version": { "type": "string", "const": "2.0" },
    "timestamp": { "type": "string", "format": "date-time" },
    "order_id": { "type": "string", "format": "uuid" },
    "customer_id": { "type": "string", "format": "uuid" },
    "total_amount": { "type": "number", "minimum": 0 },
    "currency": { "type": "string", "enum": ["USD", "EUR"] },
    "payment_method": {
      "type": "string",
      "enum": ["credit_card", "paypal", "bank_transfer"]
    }
  }
}
```

### Example Payload

```json
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "event_type": "order.created",
  "event_version": "2.0",
  "timestamp": "2026-02-19T15:30:00Z",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "total_amount": 59.98,
  "currency": "USD",
  "payment_method": "credit_card"
}
```

### Producers

| Service       | Since  | Notes            |
| ------------- | ------ | ---------------- |
| order-service | v1.0.0 | Primary producer |

### Consumers

| Service              | Since  | Purpose                       |
| -------------------- | ------ | ----------------------------- |
| payment-service      | v1.0.0 | Process payment               |
| inventory-service    | v1.2.0 | Reserve inventory             |
| notification-service | v1.1.0 | Send order confirmation email |
| analytics-service    | v2.0.0 | Update sales metrics          |

### Changelog

| Version | Date       | Changes                      |
| ------- | ---------- | ---------------------------- |
| 2.0     | 2026-02-15 | Added `payment_method` field |
| 1.0     | 2025-06-01 | Initial version              |

### Related Events

- `order.updated`
- `order.cancelled`
- `payment.completed`

---
````

### Automated Catalog Generation

````csharp
// Generación automática del catálogo desde código
// Usando reflexión para escanear eventos

public class EventCatalogGenerator
{
    public async Task GenerateCatalogAsync(string outputPath)
    {
        var eventTypes = Assembly.GetExecutingAssembly()
            .GetTypes()
            .Where(t => t.IsSubclassOf(typeof(DomainEvent)) && !t.IsAbstract);

        var catalog = new StringBuilder();
        catalog.AppendLine("# Event Catalog");
        catalog.AppendLine();

        foreach (var eventType in eventTypes)
        {
            var eventInstance = (DomainEvent)Activator.CreateInstance(eventType);

            catalog.AppendLine($"## {eventInstance.EventType}");
            catalog.AppendLine();
            catalog.AppendLine($"**Version**: {eventInstance.EventVersion}");
            catalog.AppendLine($"**Class**: `{eventType.Name}`");
            catalog.AppendLine();

            // Schema from JsonSerializer
            var options = new JsonSerializerOptions { WriteIndented = true };
            var exampleJson = JsonSerializer.Serialize(eventInstance, options);

            catalog.AppendLine("### Example");
            catalog.AppendLine("```json");
            catalog.AppendLine(exampleJson);
            catalog.AppendLine("```");
            catalog.AppendLine();
            catalog.AppendLine("---");
            catalog.AppendLine();
        }

        await File.WriteAllTextAsync(outputPath, catalog.ToString());
    }
}
````

### Event Discovery API

```csharp
// API para consultar catálogo de eventos en runtime
[ApiController]
[Route("api/events")]
public class EventCatalogController : ControllerBase
{
    [HttpGet]
    public IActionResult ListEvents()
    {
        var eventTypes = Assembly.GetExecutingAssembly()
            .GetTypes()
            .Where(t => t.IsSubclassOf(typeof(DomainEvent)) && !t.IsAbstract)
            .Select(t =>
            {
                var instance = (DomainEvent)Activator.CreateInstance(t);
                return new
                {
                    EventType = instance.EventType,
                    Version = instance.EventVersion,
                    ClassName = t.Name,
                    Properties = t.GetProperties().Select(p => new
                    {
                        Name = p.Name,
                        Type = p.PropertyType.Name
                    })
                };
            });

        return Ok(eventTypes);
    }

    [HttpGet("{eventType}")]
    public IActionResult GetEventSchema(string eventType)
    {
        var type = Assembly.GetExecutingAssembly()
            .GetTypes()
            .FirstOrDefault(t =>
            {
                if (!t.IsSubclassOf(typeof(DomainEvent)) || t.IsAbstract)
                    return false;

                var instance = (DomainEvent)Activator.CreateInstance(t);
                return instance.EventType == eventType;
            });

        if (type == null)
            return NotFound($"Event type '{eventType}' not found");

        var instance = (DomainEvent)Activator.CreateInstance(type);
        var schema = JsonSerializer.Serialize(instance, new JsonSerializerOptions { WriteIndented = true });

        return Ok(new { EventType = eventType, Schema = schema });
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** documentar todos los eventos en catálogo centralizado
- **MUST** incluir schema, ejemplos, producers y consumers para cada evento
- **MUST** mantener changelog de versiones de eventos

### SHOULD (Fuertemente recomendado)

- **SHOULD** automatizar generación del catálogo desde código (reflexión o anotaciones)
- **SHOULD** exponer API de descubrimiento de eventos para equipos consumidores
- **SHOULD** mantener catálogo sincronizado con AsyncAPI spec (ver [AsyncAPI Specification](./asyncapi-specification.md))

---

## Referencias

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [AsyncAPI Studio](https://studio.asyncapi.com/) — Herramienta para catálogo de eventos
- [Backstage](https://backstage.io/) — Portal de developer para catálogo de servicios y eventos
- [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/comunicacion-asincrona-y-eventos.md) — Lineamiento relacionado
- [Event Design](./event-design.md)
- [AsyncAPI Specification](./asyncapi-specification.md)
