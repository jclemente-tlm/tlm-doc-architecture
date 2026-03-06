---
id: asyncapi-specification
sidebar_position: 6
title: Especificación AsyncAPI
description: Estándares para documentar APIs asíncronas con AsyncAPI 3.0 y validar contratos de eventos con JSON Schema.
tags: [mensajeria, asyncapi, documentacion, event-catalog, kafka]
---

# Especificación AsyncAPI

## Contexto

Este estándar define cómo documentar arquitecturas event-driven usando AsyncAPI 3.0, incluyendo la especificación de canales, operaciones, mensajes y schemas. Permite generación de código, validación de contratos y mantenimiento de un catálogo de eventos centralizado. Complementa el lineamiento [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md).

---

## Stack Tecnológico

| Componente          | Tecnología   | Versión | Uso                               |
| ------------------- | ------------ | ------- | --------------------------------- |
| **Especificación**  | AsyncAPI     | 3.0+    | Documentación de APIs asíncronas  |
| **Validación**      | NJsonSchema  | 11.0+   | Validación runtime de JSON Schema |
| **Code Generation** | AsyncAPI CLI | -       | Generación de código desde spec   |
| **Message Broker**  | Apache Kafka | 3.6+    | Backend de mensajería             |

---

## AsyncAPI Specification

### ¿Qué es AsyncAPI?

Especificación para documentar APIs asíncronas, similar a OpenAPI pero para mensajería/eventos.

**Componentes:**

- **Info**: Metadata de la API
- **Servers**: Brokers/servidores de mensajería
- **Channels**: Topics/colas
- **Operations**: Publicación/suscripción
- **Messages**: Estructura de mensajes
- **Schemas**: Esquemas JSON Schema

**Propósito:** Documentar arquitectura event-driven, generar código, validar contratos.

**Beneficios:**
✅ Documentación estándar
✅ Generación de código
✅ Validación de contratos
✅ Catálogo de eventos centralizado

### Especificación AsyncAPI 3.0

```yaml
asyncapi: 3.0.0

info:
  title: Customer Service API
  version: 1.0.0
  description: |
    APIs asíncronas del servicio de clientes.
    Publica eventos de creación, actualización y eliminación de clientes.
  contact:
    name: Equipo de Clientes
    email: team-customers@talma.com
  license:
    name: Proprietary

servers:
  production:
    host: kafka-prod.talma.com:9092
    protocol: kafka
    description: Cluster de Kafka en producción
    tags:
      - name: env:production
  staging:
    host: kafka-staging.talma.com:9092
    protocol: kafka
    description: Cluster de Kafka en staging
    tags:
      - name: env:staging

defaultContentType: application/json

channels:
  customersEvents:
    address: customers-events
    description: Canal de eventos de clientes
    messages:
      customerCreated:
        $ref: "#/components/messages/CustomerCreated"
      customerUpdated:
        $ref: "#/components/messages/CustomerUpdated"
      customerDeleted:
        $ref: "#/components/messages/CustomerDeleted"

operations:
  publishCustomerCreated:
    action: send
    channel:
      $ref: "#/channels/customersEvents"
    messages:
      - $ref: "#/channels/customersEvents/messages/customerCreated"
    summary: Publica evento cuando cliente es creado
    description: Este evento es emitido inmediatamente después de que un nuevo cliente es creado en el sistema

  subscribeCustomerCreated:
    action: receive
    channel:
      $ref: "#/channels/customersEvents"
    messages:
      - $ref: "#/channels/customersEvents/messages/customerCreated"
    summary: Suscribirse a eventos de clientes creados

components:
  messages:
    CustomerCreated:
      name: CustomerCreated
      title: Cliente Creado
      summary: Evento emitido cuando un cliente es creado
      contentType: application/json
      headers:
        $ref: "#/components/schemas/EventHeaders"
      payload:
        $ref: "#/components/schemas/CustomerCreatedEvent"
      examples:
        - name: customerCreatedExample
          summary: Ejemplo de cliente creado
          payload:
            eventId: "01HN1JQFQ3K7QK"
            eventType: "customers.customer.created.v1"
            timestamp: "2026-02-18T10:30:00Z"
            correlationId: "01HN1JQFQ3K7QK"
            schemaVersion: "1.0"
            source:
              service: "customer-service"
              version: "1.5.2"
              instance: "customer-service-pod-abc123"
            subject:
              type: "Customer"
              id: "f7c8e3a1-2b4d-4e6f-9a8b-1c2d3e4f5a6b"
              tenantId: "tenant-001"
            data:
              customerId: "f7c8e3a1-2b4d-4e6f-9a8b-1c2d3e4f5a6b"
              name: "Acme Corporation"
              email: "contact@acme.com"
              phone: "+51987654321"
              document:
                type: "RUC"
                number: "20123456789"
              createdAt: "2026-02-18T10:30:00Z"

    CustomerUpdated:
      name: CustomerUpdated
      title: Cliente Actualizado
      summary: Evento emitido cuando un cliente es actualizado
      contentType: application/json
      payload:
        $ref: "#/components/schemas/CustomerUpdatedEvent"

    CustomerDeleted:
      name: CustomerDeleted
      title: Cliente Eliminado
      summary: Evento emitido cuando un cliente es eliminado (soft delete)
      contentType: application/json
      payload:
        $ref: "#/components/schemas/CustomerDeletedEvent"

  schemas:
    EventHeaders:
      type: object
      properties:
        event-type:
          type: string
          description: Tipo de evento
          example: customers.customer.created.v1
        schema-version:
          type: string
          description: Versión del esquema
          example: "1.0"
        correlation-id:
          type: string
          description: ID de correlación
        content-type:
          type: string
          description: Tipo de contenido
          example: application/json

    CustomerCreatedEvent:
      type: object
      required:
        - eventId
        - eventType
        - timestamp
        - correlationId
        - schemaVersion
        - source
        - subject
        - data
      properties:
        eventId:
          type: string
          description: ID único del evento (ULID)
          example: "01HN1JQFQ3K7QK"
        eventType:
          type: string
          const: customers.customer.created.v1
        timestamp:
          type: string
          format: date-time
        correlationId:
          type: string
        causationId:
          type: string
        schemaVersion:
          type: string
          example: "1.0"
        source:
          $ref: "#/components/schemas/EventSource"
        subject:
          $ref: "#/components/schemas/EventSubject"
        data:
          $ref: "#/components/schemas/CustomerCreatedData"

    EventSource:
      type: object
      required: [service, version]
      properties:
        service:
          type: string
          example: customer-service
        version:
          type: string
          example: "1.5.2"
        instance:
          type: string

    EventSubject:
      type: object
      required: [type, id]
      properties:
        type:
          type: string
          example: Customer
        id:
          type: string
          format: uuid
        tenantId:
          type: string

    CustomerCreatedData:
      type: object
      required: [customerId, name, email, document, createdAt]
      properties:
        customerId:
          type: string
          format: uuid
        name:
          type: string
          minLength: 2
          maxLength: 100
        email:
          type: string
          format: email
        phone:
          type: string
          pattern: '^\+\d{10,15}$'
        document:
          $ref: "#/components/schemas/DocumentData"
        createdAt:
          type: string
          format: date-time

    DocumentData:
      type: object
      required: [type, number]
      properties:
        type:
          type: string
          enum: [DNI, RUC, CE]
        number:
          type: string

    CustomerUpdatedEvent:
      type: object
      required:
        [
          eventId,
          eventType,
          timestamp,
          correlationId,
          schemaVersion,
          source,
          subject,
          data,
        ]
      properties:
        eventId:
          type: string
        eventType:
          type: string
          const: customers.customer.updated.v1
        timestamp:
          type: string
          format: date-time
        correlationId:
          type: string
        schemaVersion:
          type: string
        source:
          $ref: "#/components/schemas/EventSource"
        subject:
          $ref: "#/components/schemas/EventSubject"
        data:
          type: object
          required: [customerId, updatedAt]
          properties:
            customerId:
              type: string
              format: uuid
            name:
              type: string
            email:
              type: string
              format: email
            phone:
              type: string
            updatedAt:
              type: string
              format: date-time

    CustomerDeletedEvent:
      type: object
      required:
        [
          eventId,
          eventType,
          timestamp,
          correlationId,
          schemaVersion,
          source,
          subject,
          data,
        ]
      properties:
        eventId:
          type: string
        eventType:
          type: string
          const: customers.customer.deleted.v1
        timestamp:
          type: string
          format: date-time
        correlationId:
          type: string
        schemaVersion:
          type: string
        source:
          $ref: "#/components/schemas/EventSource"
        subject:
          $ref: "#/components/schemas/EventSubject"
        data:
          type: object
          required: [customerId, deletedAt]
          properties:
            customerId:
              type: string
              format: uuid
            reason:
              type: string
            deletedAt:
              type: string
              format: date-time
```

### Validación de Esquemas en Runtime

```csharp
public class EventSchemaValidator
{
    private readonly Dictionary<string, JsonSchema> _schemas = new();
    private readonly ILogger<EventSchemaValidator> _logger;

    public EventSchemaValidator(ILogger<EventSchemaValidator> logger)
    {
        _logger = logger;
        LoadSchemas();
    }

    private void LoadSchemas()
    {
        var customerCreatedSchema = JsonSchema.FromJsonAsync("""
        {
          "$schema": "https://json-schema.org/draft/2020-12/schema",
          "type": "object",
          "required": ["eventId", "eventType", "timestamp", "data"],
          "properties": {
            "eventId": { "type": "string" },
            "eventType": { "type": "string", "const": "customers.customer.created.v1" },
            "timestamp": { "type": "string", "format": "date-time" },
            "data": {
              "type": "object",
              "required": ["customerId", "name", "email"],
              "properties": {
                "customerId": { "type": "string", "format": "uuid" },
                "name": { "type": "string", "minLength": 2, "maxLength": 100 },
                "email": { "type": "string", "format": "email" }
              }
            }
          }
        }
        """).Result;

        _schemas["customers.customer.created.v1"] = customerCreatedSchema;
    }

    public async Task<ValidationResult> ValidateAsync(DomainEvent @event)
    {
        if (!_schemas.TryGetValue(@event.EventType, out var schema))
        {
            _logger.LogWarning("No hay esquema definido para evento: {EventType}", @event.EventType);
            return ValidationResult.Success();
        }

        var json = JsonSerializer.Serialize(@event);
        var errors = schema.Validate(json);

        if (errors.Count > 0)
        {
            _logger.LogError("Evento {EventType} falló validación: {Errors}",
                @event.EventType,
                string.Join(", ", errors.Select(e => e.ToString())));

            return ValidationResult.Failure(errors.Select(e => e.ToString()).ToArray());
        }

        return ValidationResult.Success();
    }
}

public record ValidationResult
{
    public bool IsValid { get; init; }
    public string[] Errors { get; init; } = Array.Empty<string>();

    public static ValidationResult Success() => new() { IsValid = true };
    public static ValidationResult Failure(string[] errors) => new() { IsValid = false, Errors = errors };
}
```

---

## Catálogo de Eventos

Cada evento publicado debe registrarse en el catálogo del dominio con la siguiente plantilla:

```markdown
### {domain}.{entity}.{action}.{version}

**Descripción**: Evento emitido cuando ...

**Topic**: {domain}-events

**Schema**: [schema-v1.json](schemas/schema-v1.json)

**Publicadores**:

- {service-name}

**Consumidores**:

- {consumer-service} ({propósito})

**Versionamiento**:

- v1.0: Versión inicial (YYYY-MM-DD)

**Breaking Changes**: Ninguno
```

:::tip Catálogo centralizado
El catálogo de eventos de cada dominio vive en la documentación del servicio propietario. Usar una herramienta como [AsyncAPI Studio](https://studio.asyncapi.com/) o Backstage para mantener el catálogo actualizado.
:::

---

## Beneficios en Práctica

| Sin contratos de eventos                               | Con contratos AsyncAPI + JSON Schema                           |
| ------------------------------------------------------ | -------------------------------------------------------------- |
| Consumidores acoplan a implementación interna          | Contrato explícito e independiente del código                  |
| Cambios rompen consumidores sin aviso                  | Versionamiento semántico y upcasting controlado                |
| Depuración difícil en producción                       | `correlationId` + `causationId` permiten trazabilidad completa |
| Sin validación: eventos malógrados llegan a producción | JSON Schema valida en publicación y consumo                    |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** documentar todas las APIs asíncronas con AsyncAPI 3.0
- **MUST** usar JSON Schema para validación de payloads
- **MUST** definir ejemplos para cada tipo de evento
- **MUST** mantener AsyncAPI spec en sync con código

### SHOULD (Fuertemente recomendado)

- **SHOULD** validar eventos contra JSON Schema antes de publicar
- **SHOULD** mantener catálogo de eventos centralizado
- **SHOULD** generar código de clientes desde AsyncAPI

### MAY (Opcional)

- **MAY** usar Schema Registry (Confluent Schema Registry) para versionamiento
- **MAY** usar diferentes retention policies por tipo de evento
- **MAY** implementar event replay para recovery

---

## Referencias

- [AsyncAPI 3.0 Specification](https://www.asyncapi.com/docs/reference/specification/v3.0.0) — Especificación AsyncAPI
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html) — Esquemas JSON
- [NJsonSchema](https://github.com/RicoSuter/NJsonSchema) — Validación runtime de JSON Schema
- [AsyncAPI Code Generation](https://www.asyncapi.com/tools/generator) — Generación de código desde AsyncAPI
- [AsyncAPI Studio](https://studio.asyncapi.com/) — Herramienta visual para AsyncAPI
- [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) — Lineamiento relacionado
- [Event Contracts](./event-contracts.md)
- [Event Catalog](./event-catalog.md)
