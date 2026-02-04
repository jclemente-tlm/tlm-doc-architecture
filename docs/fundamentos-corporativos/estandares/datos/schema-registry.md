---
id: schema-registry
sidebar_position: 12
title: Schema Registry [NO UTILIZADO]
description: ⚠️ NO USAR - Talma no utiliza Schema Registry ni Confluent Platform. Ver kafka-events.md para el enfoque con JSON Schema
---

# ⚠️ ESTÁNDAR NO APLICABLE — Schema Registry

---

## ❌ TECNOLOGÍA NO UTILIZADA

**Este estándar está marcado como NO APLICABLE.**

Talma **NO utiliza**:

- ❌ Confluent Schema Registry
- ❌ Confluent Platform
- ❌ Apicurio Registry
- ❌ Apache Avro
- ❌ Protobuf para Kafka

**En su lugar, usar:**
✅ **JSON Schema** con validación en aplicación (ver [kafka-events.md](../mensajeria/kafka-events.md))

---

## Razón

Implementación propia con Apache Kafka KRaft mode (sin Zookeeper) y validación JSON Schema embebida en productores/consumidores, sin infraestructura adicional de Schema Registry.

---

## Referencia

Ver estándar vigente: [Kafka Events](../mensajeria/kafka-events.md)

- [ ] Descripción de cada schema field
- [ ] Ejemplos de uso
- [ ] Breaking changes en changelog
- [ ] Owner team identificado
- [ ] Deprecation notices con sunset date

---

## 5. Prohibiciones

- ❌ Publicar eventos sin schema registrado
- ❌ Cambios breaking en schemas sin coordinar con consumers
- ❌ Eliminar campos sin periodo de deprecación
- ❌ Schemas sin versionado
- ❌ Compatibility mode NONE en producción
- ❌ Schemas sin documentación
- ❌ Hard-coded schema IDs (usar auto-registration)

---

## 6. Configuración Mínima

### Confluent Schema Registry Setup

```yaml
# docker-compose.yml
version: "3.8"
services:
  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.0
    hostname: schema-registry
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: "kafka:9092"
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
      # Compatibility mode global
      SCHEMA_REGISTRY_SCHEMA_COMPATIBILITY_LEVEL: BACKWARD
    depends_on:
      - kafka
```

### Avro Schema Definition

```json
// schemas/com.talma.sales.order.created.v1.avsc
{
  "namespace": "com.talma.sales.order.created",
  "type": "record",
  "name": "OrderCreated",
  "version": "1.0.0",
  "doc": "Evento publicado cuando se crea una nueva orden. Owner: orders-service",
  "fields": [
    {
      "name": "event_id",
      "type": "string",
      "doc": "UUID único del evento"
    },
    {
      "name": "event_timestamp",
      "type": "long",
      "logicalType": "timestamp-millis",
      "doc": "Timestamp del evento en milisegundos (epoch)"
    },
    {
      "name": "order_id",
      "type": "string",
      "doc": "UUID de la orden creada"
    },
    {
      "name": "customer_id",
      "type": "string",
      "doc": "UUID del cliente que realizó la orden"
    },
    {
      "name": "total_amount",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 10,
        "scale": 2
      },
      "doc": "Monto total de la orden en USD"
    },
    {
      "name": "status",
      "type": {
        "type": "enum",
        "name": "OrderStatus",
        "symbols": [
          "PENDING",
          "PAID",
          "PROCESSING",
          "SHIPPED",
          "DELIVERED",
          "CANCELLED"
        ]
      },
      "doc": "Estado inicial de la orden (típicamente PENDING)"
    },
    {
      "name": "item_count",
      "type": "int",
      "doc": "Número de items en la orden"
    },
    {
      "name": "metadata",
      "type": [
        "null",
        {
          "type": "map",
          "values": "string"
        }
      ],
      "default": null,
      "doc": "Metadata adicional opcional (ej: source, correlation_id)"
    }
  ]
}
```

### Producer con Schema Registry (.NET)

```csharp
// appsettings.json
{
  "Kafka": {
    "BootstrapServers": "localhost:9092",
    "SchemaRegistryUrl": "http://localhost:8081"
  }
}

// Events/OrderCreatedEvent.cs (POCO matching Avro schema)
public class OrderCreatedEvent
{
    public string event_id { get; set; }
    public long event_timestamp { get; set; }
    public string order_id { get; set; }
    public string customer_id { get; set; }
    public decimal total_amount { get; set; }
    public string status { get; set; }
    public int item_count { get; set; }
    public Dictionary<string, string>? metadata { get; set; }
}

// Services/OrderEventProducer.cs
using Confluent.Kafka;
using Confluent.SchemaRegistry;
using Confluent.SchemaRegistry.Serdes;

public class OrderEventProducer
{
    private readonly IProducer<string, OrderCreatedEvent> _producer;
    private readonly ILogger<OrderEventProducer> _logger;
    private const string TopicName = "orders.events.order-created";

    public OrderEventProducer(
        IConfiguration configuration,
        ILogger<OrderEventProducer> logger)
    {
        _logger = logger;

        var producerConfig = new ProducerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],
            Acks = Acks.All,
            EnableIdempotence = true,
            MaxInFlight = 5,
            MessageSendMaxRetries = 3
        };

        var schemaRegistryConfig = new SchemaRegistryConfig
        {
            Url = configuration["Kafka:SchemaRegistryUrl"]
        };

        var schemaRegistry = new CachedSchemaRegistryClient(schemaRegistryConfig);

        _producer = new ProducerBuilder<string, OrderCreatedEvent>(producerConfig)
            .SetKeySerializer(new AvroSerializer<string>(schemaRegistry))
            .SetValueSerializer(new AvroSerializer<OrderCreatedEvent>(schemaRegistry))
            .Build();
    }

    public async Task PublishOrderCreatedAsync(Order order)
    {
        var @event = new OrderCreatedEvent
        {
            event_id = Guid.NewGuid().ToString(),
            event_timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
            order_id = order.Id.ToString(),
            customer_id = order.CustomerId.ToString(),
            total_amount = order.TotalAmount,
            status = order.Status.ToString(),
            item_count = order.Items.Count,
            metadata = new Dictionary<string, string>
            {
                ["source"] = "orders-service",
                ["version"] = "1.0.0"
            }
        };

        try
        {
            var result = await _producer.ProduceAsync(
                TopicName,
                new Message<string, OrderCreatedEvent>
                {
                    Key = order.Id.ToString(),
                    Value = @event,
                    Headers = new Headers
                    {
                        { "event-type", Encoding.UTF8.GetBytes("order.created.v1") },
                        { "correlation-id", Encoding.UTF8.GetBytes(Guid.NewGuid().ToString()) }
                    }
                });

            _logger.LogInformation(
                "Published OrderCreated event for order {OrderId} to partition {Partition} at offset {Offset}",
                order.Id, result.Partition.Value, result.Offset.Value);
        }
        catch (ProduceException<string, OrderCreatedEvent> ex)
        {
            _logger.LogError(ex, "Failed to publish OrderCreated event for order {OrderId}", order.Id);
            throw;
        }
    }

    public void Dispose()
    {
        _producer?.Flush(TimeSpan.FromSeconds(10));
        _producer?.Dispose();
    }
}
```

### Consumer con Schema Registry

```csharp
// Services/OrderEventConsumer.cs
using Confluent.Kafka;
using Confluent.SchemaRegistry;
using Confluent.SchemaRegistry.Serdes;

public class OrderEventConsumer : BackgroundService
{
    private readonly IConsumer<string, OrderCreatedEvent> _consumer;
    private readonly ILogger<OrderEventConsumer> _logger;
    private readonly IServiceProvider _serviceProvider;
    private const string TopicName = "orders.events.order-created";

    public OrderEventConsumer(
        IConfiguration configuration,
        ILogger<OrderEventConsumer> logger,
        IServiceProvider serviceProvider)
    {
        _logger = logger;
        _serviceProvider = serviceProvider;

        var consumerConfig = new ConsumerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],
            GroupId = "inventory-service-order-consumer",
            AutoOffsetReset = AutoOffsetReset.Earliest,
            EnableAutoCommit = false,
            EnableAutoOffsetStore = false
        };

        var schemaRegistryConfig = new SchemaRegistryConfig
        {
            Url = configuration["Kafka:SchemaRegistryUrl"]
        };

        var schemaRegistry = new CachedSchemaRegistryClient(schemaRegistryConfig);

        _consumer = new ConsumerBuilder<string, OrderCreatedEvent>(consumerConfig)
            .SetKeyDeserializer(new AvroDeserializer<string>(schemaRegistry).AsSyncOverAsync())
            .SetValueDeserializer(new AvroDeserializer<OrderCreatedEvent>(schemaRegistry).AsSyncOverAsync())
            .SetErrorHandler((_, e) =>
            {
                _logger.LogError("Kafka consumer error: {Reason}", e.Reason);
            })
            .Build();
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe(TopicName);

        _logger.LogInformation("OrderEventConsumer started, subscribed to {Topic}", TopicName);

        try
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    var consumeResult = _consumer.Consume(stoppingToken);

                    if (consumeResult?.Message?.Value == null)
                        continue;

                    _logger.LogInformation(
                        "Received OrderCreated event: OrderId={OrderId}, EventId={EventId}",
                        consumeResult.Message.Value.order_id,
                        consumeResult.Message.Value.event_id);

                    // Procesar evento
                    using var scope = _serviceProvider.CreateScope();
                    var handler = scope.ServiceProvider.GetRequiredService<IOrderCreatedEventHandler>();

                    await handler.HandleAsync(consumeResult.Message.Value, stoppingToken);

                    // Commit offset solo después de procesar exitosamente
                    _consumer.Commit(consumeResult);
                    _consumer.StoreOffset(consumeResult);
                }
                catch (ConsumeException ex)
                {
                    _logger.LogError(ex, "Error consuming message");
                    // Schema validation error sería capturado aquí
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing message");
                    // Retry logic o dead-letter queue
                }
            }
        }
        finally
        {
            _consumer.Close();
        }
    }

    public override void Dispose()
    {
        _consumer?.Dispose();
        base.Dispose();
    }
}
```

### Schema Evolution - Add Field (Backward Compatible)

```json
// schemas/com.talma.sales.order.created.v2.avsc
{
  "namespace": "com.talma.sales.order.created",
  "type": "record",
  "name": "OrderCreated",
  "version": "2.0.0",
  "doc": "Evento publicado cuando se crea una nueva orden. Owner: orders-service",
  "fields": [
    // ... campos existentes de v1 ...
    {
      "name": "order_id",
      "type": "string",
      "doc": "UUID de la orden creada"
    },
    {
      "name": "customer_id",
      "type": "string",
      "doc": "UUID del cliente que realizó la orden"
    },
    // NUEVO CAMPO - backward compatible con default
    {
      "name": "customer_email",
      "type": ["null", "string"],
      "default": null,
      "doc": "Email del cliente. Agregado en v2.0.0 para notificaciones."
    },
    {
      "name": "total_amount",
      "type": {
        "type": "bytes",
        "logicalType": "decimal",
        "precision": 10,
        "scale": 2
      },
      "doc": "Monto total de la orden en USD"
    }
  ]
}
```

### Schema Compatibility Testing

```bash
#!/bin/bash
# test-schema-compatibility.sh

SCHEMA_REGISTRY_URL="http://localhost:8081"
SUBJECT="orders.events.order-created-value"
NEW_SCHEMA_FILE="schemas/com.talma.sales.order.created.v2.avsc"

# Test compatibility antes de registrar
curl -X POST \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data @- \
  "${SCHEMA_REGISTRY_URL}/compatibility/subjects/${SUBJECT}/versions/latest" <<EOF
{
  "schema": $(cat $NEW_SCHEMA_FILE | jq -Rs .)
}
EOF

# Si compatible, registrar nueva versión
if [ $? -eq 0 ]; then
  echo "✓ Schema is compatible. Registering..."

  curl -X POST \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --data @- \
    "${SCHEMA_REGISTRY_URL}/subjects/${SUBJECT}/versions" <<EOF
{
  "schema": $(cat $NEW_SCHEMA_FILE | jq -Rs .)
}
EOF
else
  echo "✗ Schema is NOT compatible. Fix breaking changes."
  exit 1
fi
```

---

## 7. Ejemplos

### Protobuf Schema

```protobuf
// schemas/order_created.proto
syntax = "proto3";

package com.talma.sales.order.created;

option csharp_namespace = "Talma.Sales.Events";

message OrderCreated {
  string event_id = 1;
  int64 event_timestamp = 2;
  string order_id = 3;
  string customer_id = 4;
  string total_amount = 5;  // decimal as string
  OrderStatus status = 6;
  int32 item_count = 7;
  map<string, string> metadata = 8;
}

enum OrderStatus {
  PENDING = 0;
  PAID = 1;
  PROCESSING = 2;
  SHIPPED = 3;
  DELIVERED = 4;
  CANCELLED = 5;
}
```

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://schemas.talma.com/sales/order-created/v1",
  "title": "OrderCreated",
  "description": "Evento publicado cuando se crea una orden",
  "type": "object",
  "required": [
    "event_id",
    "event_timestamp",
    "order_id",
    "customer_id",
    "total_amount",
    "status"
  ],
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "event_timestamp": {
      "type": "integer",
      "minimum": 0
    },
    "order_id": {
      "type": "string",
      "format": "uuid"
    },
    "customer_id": {
      "type": "string",
      "format": "uuid"
    },
    "total_amount": {
      "type": "number",
      "minimum": 0
    },
    "status": {
      "type": "string",
      "enum": [
        "PENDING",
        "PAID",
        "PROCESSING",
        "SHIPPED",
        "DELIVERED",
        "CANCELLED"
      ]
    },
    "item_count": {
      "type": "integer",
      "minimum": 1
    }
  }
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Schema Registry configurado y disponible
- [ ] Todos los topics tienen schema registrado
- [ ] Compatibility mode configurado por topic
- [ ] Producers/consumers usan serializers con schema
- [ ] Schema evolution tested en CI/CD
- [ ] Documentación de schemas actualizada
- [ ] Métricas de schema validation errors

### Métricas

```promql
# Schema validation errors
rate(kafka_schema_validation_errors_total[5m])

# Schema registry latency
histogram_quantile(0.95, schema_registry_request_duration_seconds)
```

### Queries Schema Registry API

```bash
# Listar todos los subjects
curl http://localhost:8081/subjects

# Ver versiones de un subject
curl http://localhost:8081/subjects/orders.events.order-created-value/versions

# Obtener schema específico
curl http://localhost:8081/subjects/orders.events.order-created-value/versions/1

# Ver compatibility mode
curl http://localhost:8081/config/orders.events.order-created-value
```

---

## 9. Referencias

**Documentación:**

- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/)
- [Avro Specification](https://avro.apache.org/docs/current/spec.html)
- [Protobuf Language Guide](https://protobuf.dev/programming-guides/proto3/)

**Buenas prácticas:**

- "Kafka: The Definitive Guide" (O'Reilly)
- [Schema Evolution Best Practices](https://docs.confluent.io/platform/current/schema-registry/avro.html#schema-evolution)
- [Apicurio Registry](https://www.apicur.io/registry/)
