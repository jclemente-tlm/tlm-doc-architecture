---
id: event-schemas
sidebar_position: 4
title: Schemas de Eventos
description: Estándar para definir, versionar y validar schemas de eventos con JSON Schema + CloudEvents en Apache Kafka
---

# Estándar Técnico — Schemas de Eventos

---

## 1. Propósito

Garantizar compatibilidad y evolución segura de eventos mediante JSON Schema con versionado semántico, CloudEvents para metadatos estándar, validación en producer/consumer, y repositorio Git de schemas.

---

## 2. Alcance

**Aplica a:**

- Eventos de dominio en Apache Kafka
- Integración asíncrona entre microservicios
- Event-driven architectures
- Eventos de negocio (OrderCreated, PaymentProcessed)

**No aplica a:**

- Mensajes RPC síncronos (usar REST/gRPC)
- Logs de aplicación
- Métricas de observabilidad

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología       | Versión mínima | Observaciones      |
| ----------------- | ---------------- | -------------- | ------------------ |
| **Schema Format** | JSON Schema      | Draft 2020-12  | Esquemas JSON      |
| **Event Spec**    | CloudEvents      | 1.0+           | Metadatos estándar |
| **Validation**    | NJsonSchema      | 11.0+          | Validación .NET    |
| **Messaging**     | Apache Kafka     | 3.6+           | Event bus          |
| **Serialization** | System.Text.Json | .NET 8+        | JSON serializer    |
| **Repository**    | Git              | -              | Versionado schemas |

> ⚠️ **NO UTILIZADO:** Schema Registry / Avro (Talma no usa Confluent Platform)

---

## 4. Requisitos Obligatorios 🔴

### Definición de Schemas

- [ ] **JSON Schema** para estructura de eventos
- [ ] **CloudEvents** para metadatos (id, source, type, time)
- [ ] **Versionado semántico** en schema (v1, v2, v3)
- [ ] **Repositorio Git** para schemas (`schemas/` folder)
- [ ] **Documentación** de cada campo (description obligatorio)

### Validación

- [ ] **Validación en producer** antes de publicar
- [ ] **Validación en consumer** al consumir (opcional)
- [ ] **Tests unitarios** de schemas
- [ ] **Breaking changes** detectados en CI/CD

### Evolución

- [ ] **Backward compatibility** por defecto
- [ ] **Campos nuevos opcionales** con valores default
- [ ] **NO eliminar campos** sin deprecation period
- [ ] **Major version** si breaking change inevitable

---

## 5. CloudEvents - Estructura Estándar

### Envelope CloudEvents

```json
{
  "specversion": "1.0",
  "id": "a7f8d9e1-3b2c-4d5e-8f9a-1b2c3d4e5f6g",
  "source": "https://api.company.com/payment-service",
  "type": "com.company.payment.v1.PaymentProcessed",
  "time": "2024-02-04T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "payment/pay-123",
  "data": {
    "paymentId": "pay-123",
    "orderId": "ord-456",
    "amount": 100.5,
    "currency": "USD",
    "status": "completed",
    "processedAt": "2024-02-04T10:30:00Z"
  }
}
```

### Campos CloudEvents Obligatorios

| Campo             | Tipo      | Descripción                  | Ejemplo                                     |
| ----------------- | --------- | ---------------------------- | ------------------------------------------- |
| `specversion`     | string    | Versión CloudEvents          | `"1.0"`                                     |
| `id`              | string    | UUID único del evento        | `"uuid-v4"`                                 |
| `source`          | URI       | Sistema origen               | `"https://api.company.com/payment-service"` |
| `type`            | string    | Tipo de evento (reverse DNS) | `"com.company.payment.v1.PaymentProcessed"` |
| `time`            | timestamp | Timestamp ISO 8601           | `"2024-02-04T10:30:00Z"`                    |
| `datacontenttype` | string    | MIME type                    | `"application/json"`                        |
| `data`            | object    | Payload del evento           | `{ ... }`                                   |

---

## 6. JSON Schema - Definición de Eventos

### Ejemplo: PaymentProcessed Event Schema

```json
// schemas/payment/PaymentProcessed.v1.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.company.com/payment/PaymentProcessed/v1",
  "title": "PaymentProcessed",
  "description": "Evento emitido cuando un pago se procesa exitosamente",
  "type": "object",
  "required": [
    "paymentId",
    "orderId",
    "amount",
    "currency",
    "status",
    "processedAt"
  ],
  "properties": {
    "paymentId": {
      "type": "string",
      "description": "ID único del pago",
      "pattern": "^pay-[a-z0-9]{8,}$",
      "examples": ["pay-abc12345"]
    },
    "orderId": {
      "type": "string",
      "description": "ID de la orden asociada",
      "pattern": "^ord-[a-z0-9]{8,}$",
      "examples": ["ord-xyz67890"]
    },
    "amount": {
      "type": "number",
      "description": "Monto del pago",
      "minimum": 0,
      "multipleOf": 0.01,
      "examples": [100.5]
    },
    "currency": {
      "type": "string",
      "description": "Código ISO 4217 de moneda",
      "pattern": "^[A-Z]{3}$",
      "examples": ["USD", "EUR", "PEN"]
    },
    "status": {
      "type": "string",
      "description": "Estado del pago",
      "enum": ["completed", "failed", "refunded"],
      "examples": ["completed"]
    },
    "processedAt": {
      "type": "string",
      "description": "Timestamp de procesamiento (ISO 8601)",
      "format": "date-time",
      "examples": ["2024-02-04T10:30:00Z"]
    },
    "metadata": {
      "type": "object",
      "description": "Metadatos adicionales (opcional)",
      "additionalProperties": true
    }
  },
  "additionalProperties": false
}
```

---

## 7. Validación en Producer (.NET)

### NuGet Packages

```xml
<PackageReference Include="NJsonSchema" Version="11.0.0" />
<PackageReference Include="CloudNative.CloudEvents" Version="3.0.0" />
<PackageReference Include="Confluent.Kafka" Version="2.3.0" />
```

### Producer con Validación

```csharp
// Services/EventPublisher.cs
using NJsonSchema;
using CloudNative.CloudEvents;
using Confluent.Kafka;

public class EventPublisher
{
    private readonly IProducer<string, string> _producer;
    private readonly ILogger<EventPublisher> _logger;
    private readonly Dictionary<string, JsonSchema> _schemas = new();

    public EventPublisher(IProducer<string, string> producer, ILogger<EventPublisher> logger)
    {
        _producer = producer;
        _logger = logger;
        LoadSchemas();
    }

    private void LoadSchemas()
    {
        // Cargar schemas desde archivos embebidos
        var schemaJson = File.ReadAllText("schemas/payment/PaymentProcessed.v1.schema.json");
        _schemas["PaymentProcessed.v1"] = JsonSchema.FromJsonAsync(schemaJson).Result;
    }

    public async Task PublishPaymentProcessedAsync(PaymentProcessedEvent paymentEvent)
    {
        // 1. Validar contra JSON Schema
        var schema = _schemas["PaymentProcessed.v1"];
        var json = JsonSerializer.Serialize(paymentEvent);
        var errors = schema.Validate(json);

        if (errors.Any())
        {
            _logger.LogError("Schema validation failed: {Errors}", string.Join(", ", errors.Select(e => e.Path)));
            throw new InvalidOperationException($"Event validation failed: {errors.Count} errors");
        }

        // 2. Crear CloudEvent
        var cloudEvent = new CloudEvent
        {
            Id = Guid.NewGuid().ToString(),
            Source = new Uri("https://api.company.com/payment-service"),
            Type = "com.company.payment.v1.PaymentProcessed",
            Time = DateTimeOffset.UtcNow,
            DataContentType = "application/json",
            Subject = $"payment/{paymentEvent.PaymentId}",
            Data = paymentEvent
        };

        // 3. Serializar CloudEvent
        var formatter = new JsonEventFormatter();
        var serialized = formatter.EncodeStructuredModeMessage(cloudEvent, out var contentType);

        // 4. Publicar a Kafka
        var message = new Message<string, string>
        {
            Key = paymentEvent.PaymentId,
            Value = Encoding.UTF8.GetString(serialized.ToArray()),
            Headers = new Headers
            {
                { "content-type", Encoding.UTF8.GetBytes(contentType.ToString()) }
            }
        };

        await _producer.ProduceAsync("payment-events", message);
        _logger.LogInformation("Published PaymentProcessed event: {EventId}", cloudEvent.Id);
    }
}

// Events/PaymentProcessedEvent.cs
public record PaymentProcessedEvent(
    string PaymentId,
    string OrderId,
    decimal Amount,
    string Currency,
    string Status,
    DateTime ProcessedAt
);
```

---

## 8. Consumer con Validación

```csharp
// Consumers/PaymentEventConsumer.cs
public class PaymentEventConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly JsonSchema _schema;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("payment-events");

        while (!stoppingToken.IsCancellationRequested)
        {
            var consumeResult = _consumer.Consume(stoppingToken);

            try
            {
                // 1. Deserializar CloudEvent
                var formatter = new JsonEventFormatter();
                var cloudEvent = formatter.DecodeStructuredModeMessage(
                    Encoding.UTF8.GetBytes(consumeResult.Message.Value),
                    new ContentType("application/cloudevents+json"),
                    null
                );

                // 2. Validar contra schema (opcional en consumer)
                var data = cloudEvent.Data.ToString();
                var errors = _schema.Validate(data);

                if (errors.Any())
                {
                    _logger.LogWarning("Received invalid event: {Errors}", errors.Count);
                    // Enviar a DLQ o ignorar
                    continue;
                }

                // 3. Procesar evento
                var paymentEvent = JsonSerializer.Deserialize<PaymentProcessedEvent>(data);
                await ProcessPaymentAsync(paymentEvent);

                _consumer.Commit(consumeResult);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing event");
            }
        }
    }
}
```

---

## 9. Versionado de Schemas

### Estrategia de Versionado

```
schemas/
  payment/
    PaymentProcessed.v1.schema.json  ← Versión inicial
    PaymentProcessed.v2.schema.json  ← Cambios compatibles (nuevos campos opcionales)
    PaymentProcessed.v3.schema.json  ← Breaking change (major version)
```

### Evolución Backward Compatible (v1 → v2)

```json
// PaymentProcessed.v2.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.company.com/payment/PaymentProcessed/v2",
  "title": "PaymentProcessed",
  "description": "V2: Añadido campo customerId (opcional)",
  "type": "object",
  "required": [
    "paymentId",
    "orderId",
    "amount",
    "currency",
    "status",
    "processedAt"
  ],
  "properties": {
    // ... campos existentes de v1 ...
    "customerId": {
      "type": "string",
      "description": "ID del cliente (nuevo en v2, opcional)",
      "pattern": "^cust-[a-z0-9]{8,}$",
      "examples": ["cust-abc12345"]
    }
  },
  "additionalProperties": false
}
```

### Breaking Change (v2 → v3)

```json
// PaymentProcessed.v3.schema.json
{
  // ...
  "required": [
    "paymentId",
    "orderId",
    "amount",
    "currency",
    "status",
    "processedAt",
    "customerId"
  ]
  // customerId ahora REQUERIDO (breaking change)
}
```

**Nota:** Usar `type: "com.company.payment.v3.PaymentProcessed"` en CloudEvents para v3.

---

## 10. CI/CD - Validación de Schemas

```yaml
# .github/workflows/validate-schemas.yml
name: Validate Event Schemas

on:
  pull_request:
    paths:
      - "schemas/**"

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate JSON Schemas
        run: |
          npm install -g ajv-cli
          ajv validate -s schemas/**/*.schema.json

      - name: Check Breaking Changes
        run: |
          # Comparar con versión anterior
          git fetch origin main
          for file in schemas/**/*.schema.json; do
            if git show origin/main:$file > /dev/null 2>&1; then
              echo "Checking $file for breaking changes..."
              # Validar backward compatibility con herramienta custom
            fi
          done
```

---

## 11. Validación de Cumplimiento

```bash
# Verificar schemas en repositorio
ls -la schemas/

# Validar schema con ajv
ajv validate -s schemas/payment/PaymentProcessed.v1.schema.json \
  -d examples/payment-processed-example.json

# Tests unitarios de schemas
dotnet test Tests/SchemaValidationTests.csproj
```

---

## 12. Referencias

**JSON Schema:**

- [JSON Schema Specification](https://json-schema.org/)
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)

**CloudEvents:**

- [CloudEvents Specification](https://cloudevents.io/)
- [CloudEvents .NET SDK](https://github.com/cloudevents/sdk-csharp)

**Schema Evolution:**

- [Schema Evolution in Event-Driven Systems](https://www.confluent.io/blog/schema-evolution-in-event-driven-systems/)
