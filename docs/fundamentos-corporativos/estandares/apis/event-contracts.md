---
id: event-contracts
sidebar_position: 8
title: Contratos de Eventos
description: Documentación de contratos de eventos asíncronos con AsyncAPI y JSON Schema
---

# Contratos de Eventos

## Contexto

Este estándar define cómo documentar contratos de eventos asíncronos usando AsyncAPI. Complementa el [lineamiento de APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md) y el [lineamiento de Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) especificando **cómo** y **con qué** herramientas documentar eventos.

---

## Stack Tecnológico

| Componente          | Tecnología   | Versión | Uso                                |
| ------------------- | ------------ | ------- | ---------------------------------- |
| **Especificación**  | AsyncAPI     | 3.0+    | Definición de contratos de eventos |
| **Formato**         | YAML         | -       | Serialización de especificaciones  |
| **Esquemas**        | JSON Schema  | Draft-7 | Definición de payloads             |
| **Versionamiento**  | GitHub       | -       | Control de versiones de contratos  |
| **Validación .NET** | NJsonSchema  | 11.0+   | Validación de esquemas en runtime  |
| **Generación Docs** | AsyncAPI CLI | 1.0+    | Generación de documentación HTML   |

### Dependencias NuGet

```xml
<PackageReference Include="NJsonSchema" Version="11.0.0" />
<PackageReference Include="NJsonSchema.CodeGeneration.CSharp" Version="11.0.0" />
```

---

## Implementación Técnica

### Estructura de Repositorio

```
/contracts
  /events
    asyncapi.yaml              # Especificación AsyncAPI principal
    /schemas
      order-created.schema.json
      payment-processed.schema.json
      inventory-updated.schema.json
    /examples
      order-created.example.json
      payment-processed.example.json
```

### Especificación AsyncAPI

```yaml
# asyncapi.yaml
asyncapi: 3.0.0

info:
  title: Orders Domain Events API
  version: 2.1.0
  description: |
    Eventos asíncronos del dominio Orders.
    Todos los eventos se publican a Apache Kafka.
  contact:
    name: Orders Team
    email: orders-team@talma.com

servers:
  production:
    host: kafka.talma.com:9092
    protocol: kafka-secure
    description: Kafka Production Cluster
    security:
      - saslScram: []
    tags:
      - name: production
        description: Ambiente productivo

  staging:
    host: kafka-staging.talma.com:9092
    protocol: kafka-secure
    description: Kafka Staging Cluster
    security:
      - saslScram: []

channels:
  order.ordercreated:
    address: order.ordercreated
    messages:
      OrderCreated:
        $ref: "#/components/messages/OrderCreated"
    description: Canal para eventos de creación de órdenes

  order.orderupdated:
    address: order.orderupdated
    messages:
      OrderUpdated:
        $ref: "#/components/messages/OrderUpdated"
    description: Canal para eventos de actualización de órdenes

operations:
  publishOrderCreated:
    action: send
    channel:
      $ref: "#/channels/order.ordercreated"
    summary: Publicar evento OrderCreated
    description: |
      Disparado cuando una nueva orden es creada en el sistema.
      Consumidores: billing-service, inventory-service, notification-service
    messages:
      - $ref: "#/components/messages/OrderCreated"

  subscribeOrderCreated:
    action: receive
    channel:
      $ref: "#/channels/order.ordercreated"
    summary: Consumir evento OrderCreated

components:
  messages:
    OrderCreated:
      name: OrderCreated
      title: Order Created Event
      summary: Evento emitido cuando se crea una orden
      contentType: application/json
      traits:
        - $ref: "#/components/messageTraits/commonHeaders"
      payload:
        $ref: "#/components/schemas/OrderCreatedPayload"
      examples:
        - name: Standard Order
          summary: Orden estándar con 2 ítems
          payload:
            eventId: "550e8400-e29b-41d4-a716-446655440000"
            eventType: "OrderCreated"
            timestamp: "2024-01-15T10:30:45Z"
            correlationId: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            serviceName: "orders-service"
            version: "2.1.0"
            payload:
              orderId: "e5f6g7h8-i9j0-k1l2-m3n4-o5p6q7r8s9t0"
              customerId: "c1d2e3f4-g5h6-i7j8-k9l0-m1n2o3p4q5r6"
              totalAmount: 250.50
              currency: "USD"
              status: "Created"
              items:
                - productId: "p1"
                  quantity: 2
                  unitPrice: 100.00
                - productId: "p2"
                  quantity: 1
                  unitPrice: 50.50
              createdAt: "2024-01-15T10:30:45Z"
              createdBy: "user-123"

  schemas:
    OrderCreatedPayload:
      type: object
      required:
        - eventId
        - eventType
        - timestamp
        - correlationId
        - serviceName
        - version
        - payload
      properties:
        eventId:
          type: string
          format: uuid
          description: Identificador único del evento (idempotencia)
        eventType:
          type: string
          const: "OrderCreated"
          description: Tipo de evento (inmutable)
        timestamp:
          type: string
          format: date-time
          description: Timestamp UTC del evento
        correlationId:
          type: string
          format: uuid
          description: ID de correlación para trazabilidad
        serviceName:
          type: string
          description: Servicio que emite el evento
          example: "orders-service"
        version:
          type: string
          pattern: '^\d+\.\d+\.\d+$'
          description: Versión del contrato (semver)
          example: "2.1.0"
        payload:
          type: object
          required:
            - orderId
            - customerId
            - totalAmount
            - currency
            - status
            - createdAt
          properties:
            orderId:
              type: string
              format: uuid
              description: ID único de la orden
            customerId:
              type: string
              format: uuid
              description: ID del cliente
            totalAmount:
              type: number
              format: double
              minimum: 0
              description: Monto total de la orden
            currency:
              type: string
              enum: ["USD", "EUR", "PEN"]
              description: Código ISO 4217 de moneda
            status:
              type: string
              enum:
                ["Created", "Confirmed", "Shipped", "Delivered", "Cancelled"]
              description: Estado de la orden
            items:
              type: array
              minItems: 1
              items:
                type: object
                required:
                  - productId
                  - quantity
                  - unitPrice
                properties:
                  productId:
                    type: string
                    description: ID del producto
                  quantity:
                    type: integer
                    minimum: 1
                    description: Cantidad del producto
                  unitPrice:
                    type: number
                    format: double
                    minimum: 0
                    description: Precio unitario
            createdAt:
              type: string
              format: date-time
              description: Timestamp de creación de la orden
            createdBy:
              type: string
              description: Usuario que creó la orden

  messageTraits:
    commonHeaders:
      headers:
        type: object
        properties:
          kafka_messageKey:
            type: string
            description: Clave del mensaje Kafka (partition key)
          kafka_topic:
            type: string
            description: Topic Kafka donde se publica

  securitySchemes:
    saslScram:
      type: scramSha512
      description: SASL/SCRAM-SHA-512 authentication
```

### Validación de Esquemas en .NET

```csharp
using NJsonSchema;
using System.Text.Json;

public class EventValidator
{
    private readonly Dictionary<string, JsonSchema> _schemas = new();

    public async Task LoadSchemasAsync()
    {
        // Cargar esquemas desde archivos o recursos embebidos
        var orderCreatedSchema = await JsonSchema.FromFileAsync(
            "contracts/events/schemas/order-created.schema.json"
        );

        _schemas["OrderCreated"] = orderCreatedSchema;
    }

    public async Task<(bool IsValid, IEnumerable<string> Errors)> ValidateAsync(
        string eventType,
        string jsonPayload)
    {
        if (!_schemas.ContainsKey(eventType))
        {
            return (false, new[] { $"Schema for event type '{eventType}' not found" });
        }

        var schema = _schemas[eventType];
        var errors = schema.Validate(jsonPayload);

        return (errors.Count == 0, errors.Select(e => e.ToString()));
    }
}

// Uso en Producer
public class KafkaProducer
{
    private readonly EventValidator _validator;

    public async Task PublishAsync<T>(string topic, T eventData)
    {
        var json = JsonSerializer.Serialize(eventData);
        var eventType = typeof(T).Name;

        // Validar contra schema antes de publicar
        var (isValid, errors) = await _validator.ValidateAsync(eventType, json);

        if (!isValid)
        {
            throw new InvalidEventException(
                $"Event validation failed: {string.Join(", ", errors)}"
            );
        }

        await _producer.ProduceAsync(topic, new Message<string, string>
        {
            Key = GetPartitionKey(eventData),
            Value = json
        });
    }
}
```

### Generación de Clases C# desde JSON Schema

```csharp
using NJsonSchema.CodeGeneration.CSharp;

public static class SchemaCodeGenerator
{
    public static async Task GenerateTypesAsync()
    {
        var schema = await JsonSchema.FromFileAsync(
            "contracts/events/schemas/order-created.schema.json"
        );

        var generator = new CSharpGenerator(schema, new CSharpGeneratorSettings
        {
            Namespace = "Talma.Orders.Events",
            ClassStyle = CSharpClassStyle.Record,
            JsonLibrary = CSharpJsonLibrary.SystemTextJson,
            GenerateDataAnnotations = true
        });

        var code = generator.GenerateFile();

        await File.WriteAllTextAsync(
            "Generated/OrderCreatedEvent.cs",
            code
        );
    }
}
```

### Versionamiento de Contratos

```yaml
# Estrategia de versionamiento semántico
# MAJOR.MINOR.PATCH

# MAJOR: Cambios incompatibles (breaking changes)
# - Eliminar campos requeridos
# - Cambiar tipos de datos existentes
# - Cambiar nombres de eventos/campos

# MINOR: Nuevas funcionalidades compatibles
# - Agregar nuevos campos opcionales
# - Agregar nuevos eventos
# - Ampliar enums

# PATCH: Correcciones compatibles
# - Corregir descripciones
# - Mejorar ejemplos
# - Actualizar documentación
```

```yaml
# Ejemplo: Evolución compatible (2.1.0 → 2.2.0)
# asyncapi-v2.2.0.yaml

components:
  schemas:
    OrderCreatedPayload:
      properties:
        # ... campos existentes ...

        # Nuevo campo opcional (compatible)
        shippingAddress: # ← NUEVO
          type: object
          description: Dirección de envío (opcional)
          properties:
            street: { type: string }
            city: { type: string }
            country: { type: string }
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** documentar todos los eventos publicados en especificación AsyncAPI
- **MUST** usar JSON Schema Draft-7+ para definir payloads
- **MUST** incluir metadata obligatoria: `eventId`, `eventType`, `timestamp`, `correlationId`, `serviceName`, `version`
- **MUST** versionar contratos con semver (MAJOR.MINOR.PATCH)
- **MUST** versionar archivos AsyncAPI en GitHub con tags
- **MUST** incluir ejemplos completos para cada evento
- **MUST** validar eventos contra esquemas antes de publicar
- **MUST** documentar consumidores esperados de cada evento
- **MUST** especificar niveles de garantía de entrega (at-least-once, exactly-once)
- **MUST** usar nombres de eventos en pasado ("OrderCreated", no "CreateOrder")

### SHOULD (Fuertemente recomendado)

- **SHOULD** generar clases tipadas desde JSON Schemas
- **SHOULD** publicar documentación HTML generada con AsyncAPI CLI
- **SHOULD** incluir diagramas de flujo de eventos
- **SHOULD** documentar deprecated fields antes de eliminarlos (1 versión MINOR mínimo)
- **SHOULD** mantener changelog de versiones en especificación
- **SHOULD** incluir contact info del equipo dueño

### MAY (Opcional)

- **MAY** usar AsyncAPI Studio para edición visual
- **MAY** automatizar generación de mocks para testing
- **MAY** integrar validación en CI/CD

### MUST NOT (Prohibido)

- **MUST NOT** hacer breaking changes sin incrementar MAJOR version
- **MUST NOT** cambiar esquemas publicados en producción sin nueva versión
- **MUST NOT** eliminar campos sin deprecation previo
- **MUST NOT** usar nombres de eventos imperativos

---

## Comandos CLI

### Instalar AsyncAPI CLI

```bash
npm install -g @asyncapi/cli
```

### Validar Especificación

```bash
asyncapi validate contracts/events/asyncapi.yaml
```

### Generar Documentación HTML

```bash
asyncapi generate fromTemplate \
  contracts/events/asyncapi.yaml \
  @asyncapi/html-template \
  --output ./docs/events \
  --force-write
```

### Validar Schema JSON

```bash
# Usando ajv-cli
npm install -g ajv-cli
ajv validate \
  -s contracts/events/schemas/order-created.schema.json \
  -d contracts/events/examples/order-created.example.json
```

---

## Referencias

- [Lineamiento: APIs y Contratos](../../lineamientos/arquitectura/07-apis-y-contratos.md)
- [Lineamiento: Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)
- Estándares relacionados:
  - [Mensajería Asíncrona](../mensajeria/async-messaging.md)
  - [Diseñar eventos como hechos del dominio](../mensajeria/event-design.md)
  - [API Versioning](api-versioning.md)
- Especificaciones externas:
  - [AsyncAPI Specification 3.0](https://www.asyncapi.com/docs/reference/specification/v3.0.0)
  - [JSON Schema Draft-7](https://json-schema.org/draft-07/json-schema-release-notes.html)
