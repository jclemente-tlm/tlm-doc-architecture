---
id: event-catalog
sidebar_position: 13
title: Catálogo de Eventos
description: Catálogo centralizado de eventos del sistema con metadata, productores y consumidores
---

# Catálogo de Eventos

## Contexto

Este estándar define cómo mantener un catálogo centralizado de todos los eventos del sistema. Complementa el [lineamiento de Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) especificando **cómo** documentar, descubrir y gobernar eventos en la arquitectura.

---

## Stack Tecnológico

| Componente          | Tecnología  | Versión | Uso                               |
| ------------------- | ----------- | ------- | --------------------------------- |
| **Documentación**   | Markdown    | -       | Catálogo de eventos               |
| **Especificación**  | AsyncAPI    | 3.0+    | Contratos técnicos                |
| **Versionamiento**  | GitHub      | -       | Control de versiones del catálogo |
| **Generación Docs** | Docusaurus  | 3.0+    | Portal de documentación           |
| **Validación**      | JSON Schema | Draft-7 | Esquemas de eventos               |

---

## Implementación Técnica

### Estructura del Catálogo

```
/docs
  /fundamentos-corporativos
    /eventos
      README.md                           # Índice principal
      /dominios
        /orders
          README.md                       # Eventos del dominio Orders
          order-created.md
          order-cancelled.md
          order-shipped.md
        /payments
          README.md
          payment-processed.md
          payment-failed.md
        /inventory
          README.md
          inventory-updated.md
          stock-reserved.md
```

### Índice Principal del Catálogo

```markdown
# Catálogo de Eventos

Catálogo centralizado de todos los eventos asíncronos publicados en la plataforma.

## Dominios

### Orders

- [OrderCreated](dominios/orders/order-created.md) - Publicado cuando se crea una orden
- [OrderCancelled](dominios/orders/order-cancelled.md) - Publicado cuando se cancela una orden
- [OrderShipped](dominios/orders/order-shipped.md) - Publicado cuando se envía una orden

### Payments

- [PaymentProcessed](dominios/payments/payment-processed.md) - Publicado cuando se procesa un pago
- [PaymentFailed](dominios/payments/payment-failed.md) - Publicado cuando falla un pago

### Inventory

- [InventoryUpdated](dominios/inventory/inventory-updated.md) - Publicado cuando se actualiza inventario
- [StockReserved](dominios/inventory/stock-reserved.md) - Publicado cuando se reserva stock

## Estadísticas

- **Total Eventos:** 7
- **Total Dominios:** 3
- **Última Actualización:** 2024-01-15

## Convenciones

- Nombres en pasado: `OrderCreated`, no `CreateOrder`
- Formato: `{Aggregado}{AcciónPasado}`
- Versionamiento: Semántico (MAJOR.MINOR.PATCH)
- Especificación: AsyncAPI 3.0
```

### Plantilla de Evento Individual

```markdown
---
id: order-created
title: OrderCreated
description: Evento emitido cuando se crea una nueva orden en el sistema
---

# OrderCreated

## 📋 Información General

- **Dominio:** Orders
- **Agregado:** Order
- **Versión Actual:** 2.1.0
- **Estado:** ✅ Activo
- **Criticidad:** Alta
- **Garantía de Entrega:** At-Least-Once
- **Última Modificación:** 2024-01-15

## 📝 Descripción

Evento publicado cuando una nueva orden es creada exitosamente en el sistema. Este evento marca el inicio del flujo de procesamiento de órdenes y dispara múltiples acciones downstream:

- Creación de factura (billing-service)
- Reserva de inventario (inventory-service)
- Notificación al cliente (notification-service)

## 🔗 Especificación Técnica

### Topic Kafka
```

order.ordercreated

````

### Esquema AsyncAPI

```yaml
OrderCreated:
  name: OrderCreated
  contentType: application/json
  payload:
    $ref: 'schemas/order-created.schema.json'
````

### Payload Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["eventId", "eventType", "timestamp", "payload"],
  "properties": {
    "eventId": {
      "type": "string",
      "format": "uuid",
      "description": "Identificador único del evento"
    },
    "eventType": {
      "type": "string",
      "const": "OrderCreated"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "correlationId": {
      "type": "string",
      "format": "uuid"
    },
    "payload": {
      "type": "object",
      "required": ["orderId", "customerId", "totalAmount"],
      "properties": {
        "orderId": {
          "type": "string",
          "format": "uuid"
        },
        "customerId": {
          "type": "string",
          "format": "uuid"
        },
        "totalAmount": {
          "type": "number",
          "minimum": 0
        },
        "currency": {
          "type": "string",
          "enum": ["USD", "EUR", "PEN"]
        },
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "productId": { "type": "string" },
              "quantity": { "type": "integer" },
              "unitPrice": { "type": "number" }
            }
          }
        }
      }
    }
  }
}
```

## 📊 Producer

### Servicio

- **Nombre:** orders-service
- **Repositorio:** [github.com/talma/orders-service](https://github.com/talma/orders-service)
- **Equipo:** Orders Team
- **Contacto:** orders-team@talma.com

### Trigger

Evento se publica cuando:

- Se ejecuta exitosamente `POST /api/orders`
- El pedido pasa validaciones de negocio
- Se persiste en BD con estado `Created`

### Código Ejemplo

```csharp
var evt = new OrderCreatedEvent(
    EventId: Guid.NewGuid(),
    EventType: "OrderCreated",
    Timestamp: DateTime.UtcNow,
    CorrelationId: correlationId,
    Payload: new OrderCreatedPayload(
        OrderId: order.Id,
        CustomerId: order.CustomerId,
        TotalAmount: order.TotalAmount,
        Currency: order.Currency,
        Items: order.Items
    )
);

await kafkaProducer.PublishAsync("order.ordercreated", evt);
```

## 👥 Consumers

### billing-service

- **Acción:** Crea factura automáticamente
- **Idempotencia:** ✅ Sí (verifica `eventId`)
- **Criticidad:** Alta
- **SLA:** < 5 segundos

### inventory-service

- **Acción:** Reserva stock de productos
- **Idempotencia:** ✅ Sí
- **Criticidad:** Alta
- **SLA:** < 3 segundos

### notification-service

- **Acción:** Envía email de confirmación al cliente
- **Idempotencia:** ✅ Sí
- **Criticidad:** Media
- **SLA:** < 30 segundos

### analytics-service

- **Acción:** Registra métrica de orden creada
- **Idempotencia:** No requerida
- **Criticidad:** Baja
- **SLA:** Best effort

## 📜 Historial de Versiones

### v2.1.0 (2024-01-15)

**Tipo:** Minor (compatible)

**Cambios:**

- ✅ Agregado campo opcional `shippingAddress`
- ✅ Agregado campo opcional `customerNotes`

### v2.0.0 (2023-10-01)

**Tipo:** Major (breaking change)

**Cambios:**

- ⚠️ Campo `currency` ahora es requerido (antes opcional)
- ⚠️ Renombrado `items.price` → `items.unitPrice`
- ✅ Agregado `items.discount`

**Migración:**

```csharp
// Antes (v1.x)
items.Price = 100.50

// Después (v2.x)
items.UnitPrice = 100.50
```

### v1.0.0 (2023-06-15)

**Tipo:** Initial release

## 🔍 Ejemplos

### Ejemplo Completo

```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "eventType": "OrderCreated",
  "timestamp": "2024-01-15T10:30:45Z",
  "correlationId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "serviceName": "orders-service",
  "version": "2.1.0",
  "payload": {
    "orderId": "e5f6g7h8-i9j0-k1l2-m3n4-o5p6q7r8s9t0",
    "customerId": "c1d2e3f4-g5h6-i7j8-k9l0-m1n2o3p4q5r6",
    "customerEmail": "customer@example.com",
    "totalAmount": 250.5,
    "currency": "USD",
    "items": [
      {
        "productId": "p1",
        "productName": "Laptop",
        "quantity": 1,
        "unitPrice": 200.0,
        "discount": 0
      },
      {
        "productId": "p2",
        "productName": "Mouse",
        "quantity": 2,
        "unitPrice": 25.25,
        "discount": 0
      }
    ],
    "shippingAddress": {
      "street": "123 Main St",
      "city": "Lima",
      "country": "PE"
    },
    "createdAt": "2024-01-15T10:30:45Z"
  }
}
```

## 🧪 Testing

### Escenarios de Prueba

1. **Happy Path**
   - Crear orden válida
   - Verificar publicación de evento
   - Verificar consumo por todos los consumers

2. **Idempotencia**
   - Publicar mismo evento 2 veces
   - Verificar que consumers procesan solo 1 vez

3. **Validación de Schema**
   - Enviar evento con campo faltante
   - Verificar rechazo con error de validación

### Comandos de Testing

```bash
# Producir evento de prueba
kafka-console-producer \
  --bootstrap-server kafka.talma.com:9092 \
  --topic order.ordercreated \
  --property "parse.key=true" \
  --property "key.separator=:"

# Consumir para verificar
kafka-console-consumer \
  --bootstrap-server kafka.talma.com:9092 \
  --topic order.ordercreated \
  --from-beginning \
  --max-messages 1
```

## 📚 Referencias

- [Contrato AsyncAPI completo](../../../contracts/events/asyncapi.yaml)
- [JSON Schema](../../../contracts/events/schemas/order-created.schema.json)
- [Código Producer](https://github.com/talma/orders-service/blob/main/src/Events/OrderCreatedPublisher.cs)
- [Lineamiento: Comunicación Asíncrona](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)
- Estándares relacionados:
  - [Diseño de Eventos](../../estandares/mensajeria/event-design.md)
  - [Contratos de Eventos](../../estandares/apis/event-contracts.md)
  - [Idempotencia](../../estandares/mensajeria/idempotency.md)

## 📞 Contacto

- **Equipo Dueño:** Orders Team
- **Email:** orders-team@talma.com
- **Slack:** #orders-team
- **On-Call:** [PagerDuty: Orders Team](https://talma.pagerduty.com/teams/orders)

````

### Script de Generación Automática

```csharp
// Script para generar catálogo desde especificación AsyncAPI
public class EventCatalogGenerator
{
    public async Task GenerateCatalogAsync(string asyncApiPath, string outputPath)
    {
        var asyncApiDoc = await AsyncApiDocument.LoadAsync(asyncApiPath);

        foreach (var channel in asyncApiDoc.Channels)
        {
            foreach (var message in channel.Messages)
            {
                var markdown = GenerateEventMarkdown(message);

                var domain = ExtractDomain(channel.Name);
                var eventName = message.Name;
                var filePath = Path.Combine(
                    outputPath,
                    "dominios",
                    domain,
                    $"{ToKebabCase(eventName)}.md"
                );

                await File.WriteAllTextAsync(filePath, markdown);
            }
        }

        await GenerateIndexAsync(asyncApiDoc, outputPath);
    }

    private string GenerateEventMarkdown(AsyncApiMessage message)
    {
        var template = @"
---
id: {id}
title: {title}
---

# {title}

## Información General

- **Dominio:** {domain}
- **Versión:** {version}
- **Estado:** ✅ Activo

## Descripción

{description}

## Payload Schema

```json
{schema}
````

## Producers

{producers}

## Consumers

{consumers}

## Referencias

{references}
";

        return template
            .Replace("{id}", ToKebabCase(message.Name))
            .Replace("{title}", message.Name)
            .Replace("{domain}", ExtractDomain(message))
            .Replace("{version}", message.Version ?? "1.0.0")
            .Replace("{description}", message.Description ?? "")
            .Replace("{schema}", JsonSerializer.Serialize(message.Payload, new JsonSerializerOptions { WriteIndented = true }))
            .Replace("{producers}", GenerateProducersSection(message))
            .Replace("{consumers}", GenerateConsumersSection(message))
            .Replace("{references}", GenerateReferencesSection(message));
    }

}

````

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** documentar todos los eventos publicados en el catálogo
- **MUST** incluir información mínima: nombre, descripción, dominio, versión, producer, consumers
- **MUST** mantener catálogo sincronizado con especificaciones AsyncAPI
- **MUST** documentar historial de versiones con breaking changes
- **MUST** incluir ejemplos completos de eventos
- **MUST** especificar criticidad y SLA de cada evento
- **MUST** listar todos los consumers conocidos de cada evento
- **MUST** versionar catálogo en GitHub

### SHOULD (Fuertemente recomendado)

- **SHOULD** generar catálogo automáticamente desde AsyncAPI
- **SHOULD** publicar catálogo como documentación web (Docusaurus)
- **SHOULD** incluir información de contacto del equipo dueño
- **SHOULD** documentar escenarios de testing
- **SHOULD** incluir diagramas de flujo cuando sea relevante
- **SHOULD** mantener índice alfabético y por dominio
- **SHOULD** incluir estadísticas del catálogo (total eventos, dominios, etc.)

### MAY (Opcional)

- **MAY** incluir métricas de uso (volumen de eventos, lag, etc.)
- **MAY** generar visualizaciones de dependencias entre eventos
- **MAY** implementar búsqueda semántica en el catálogo
- **MAY** integrar con herramientas de discovery (AsyncAPI Studio)

### MUST NOT (Prohibido)

- **MUST NOT** tener catálogo desactualizado vs código real
- **MUST NOT** omitir documentación de eventos críticos
- **MUST NOT** perder historial de versiones antiguas
- **MUST NOT** documentar eventos sin especificación AsyncAPI

---

## Gobernanza del Catálogo

### Proceso de Agregar Nuevo Evento

1. **Diseño**
   - Definir nombre (pasado, ej: `OrderCreated`)
   - Definir payload con JSON Schema
   - Documentar consumers esperados

2. **Especificación**
   - Crear entrada en AsyncAPI
   - Validar schema con ejemplos
   - Review por arquitectura

3. **Documentación**
   - Crear página en catálogo
   - Ejecutar script de generación
   - Commit y PR

4. **Implementación**
   - Implementar producer
   - Implementar consumers
   - Testing end-to-end

5. **Publicación**
   - Merge a main
   - Tag de versión
   - Actualizar changelog

### Mantenimiento

```bash
# Script semanal de sincronización
npm run sync-event-catalog

# Valida que todos los eventos en AsyncAPI tienen documentación
npm run validate-catalog

# Genera estadísticas del catálogo
npm run catalog-stats
````

---

## Referencias

- [Lineamiento: Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)
- Estándares relacionados:
  - [Contratos de Eventos](../apis/event-contracts.md)
  - [Diseño de Eventos](event-design.md)
  - [Mensajería Asíncrona](async-messaging.md)
- Herramientas:
  - [AsyncAPI Studio](https://studio.asyncapi.com/)
  - [EventCatalog](https://www.eventcatalog.dev/)
