---
id: kafka-events
sidebar_position: 1
title: Mensajería con Kafka
description: Estándares para event-driven architecture con Apache Kafka 3.6+ (KRaft), Confluent.Kafka .NET client y JSON Schema
---

# Estándar Técnico — Mensajería con Kafka

---

## 1. Propósito

Implementar event-driven architecture con Apache Kafka 3.6+ (modo KRaft), Confluent.Kafka 2.3+ (.NET client), at-least-once delivery, consumidores idempotentes y Dead Letter Queue (DLQ) para errores. Schema management mediante JSON Schema.

---

## 2. Alcance

**Aplica a:**

- Microservicios con comunicación asíncrona
- Event sourcing (log de eventos)
- Procesamiento en tiempo real (analytics, auditoría)
- Integración bounded contexts (DDD)
- Notificaciones cross-service

**No aplica a:**

- Comunicación síncrona (usar APIs REST)
- Transacciones ACID entre servicios (usar Saga pattern)
- Transferencia archivos (usar S3 + event notification)

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología                | Versión mínima | Observaciones              |
| ------------------- | ------------------------- | -------------- | -------------------------- |
| **Broker**          | Apache Kafka (KRaft mode) | 3.6+           | Message broker distribuido |
| **Cliente .NET**    | Confluent.Kafka           | 2.3+           | Producer/Consumer .NET     |
| **Schema**          | JSON Schema               | Draft 2020-12  | Validación de mensajes     |
| **Serialización**   | System.Text.Json          | 8.0+           | JSON serialization         |
| **Infraestructura** | Docker, Docker Compose    | -              | Deployment local/dev       |
| **Monitoring**      | Kafka Exporter + Grafana  | -              | Métricas y alertas         |

> **IMPORTANTE:** NO usar Confluent Platform, Schema Registry, AWS MSK, ni Apache Avro. Usar implementación propia con JSON Schema.

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Kafka 3.6+ con replicación (factor ≥ 3)
- [ ] Topics naming: `{domain}.{entity}.{event-type}`
- [ ] Event schema: eventId, eventType, timestamp, correlationId, payload
- [ ] JSON Schema para validación de mensajes
- [ ] At-least-once delivery con consumidores idempotentes
- [ ] Acks=All para productores (todas las réplicas)
- [ ] Dead Letter Queue (DLQ) para errores
- [ ] Consumer groups: `{service-name}.{topic-name}`
- [ ] Partitioning por aggregateId (orden garantizado)
- [ ] Monitoring con Kafka Exporter + Grafana Mimir
- [ ] Retention: 7 días (eventos), 30 días (event sourcing)
- [ ] Cleanup policy: delete (eventos), compact (snapshots)

---

## 5. Prohibiciones

- ❌ Topics sin replicación (factor replicación = 1)
- ❌ Eventos sin eventId/timestamp/correlationId
- ❌ Payloads >1MB (usar referencia a S3)
- ❌ Consumidores NO idempotentes
- ❌ Acks=1 en productores (usar Acks=All)
- ❌ Schemas sin versionado
- ❌ Topics sin DLQ configurada

---

## 6. Configuración Mínima

### Producer (C#)

```csharp
// Producer configuration
var producerConfig = new ProducerConfig
{
    BootstrapServers = "kafka:9092",
    Acks = Acks.All, // Todas las réplicas
    EnableIdempotence = true,
    MaxInFlight = 5,
    MessageSendMaxRetries = 3,
    CompressionType = CompressionType.Snappy
};

using var producer = new ProducerBuilder<string, OrderCreatedEvent>(producerConfig)
    .SetKeySerializer(Serializers.Utf8)
    .SetValueSerializer(new AvroSerializer<OrderCreatedEvent>(schemaRegistry))
    .Build();

var orderEvent = new OrderCreatedEvent
{
    EventId = Guid.NewGuid().ToString(),
    EventType = "orders.order.created",
    EventVersion = "1.0.0",
    Timestamp = DateTime.UtcNow,
    CorrelationId = correlationId,
    Payload = new { OrderId = orderId, CustomerId = customerId }
};

await producer.ProduceAsync(
    "orders.order.created",
    new Message<string, OrderCreatedEvent>
    {
        Key = orderId.ToString(), // Partitioning key
        Value = orderEvent
    });
```

### Consumer (C#)

```csharp
// Consumer configuration
var consumerConfig = new ConsumerConfig
{
    BootstrapServers = "kafka:9092",
    GroupId = "notification-service.orders.order.created",
    AutoOffsetReset = AutoOffsetReset.Earliest,
    EnableAutoCommit = false, // Manual commit
    EnableAutoOffsetStore = false
};

using var consumer = new ConsumerBuilder<string, OrderCreatedEvent>(consumerConfig)
    .SetKeyDeserializer(Deserializers.Utf8)
    .SetValueDeserializer(new AvroDeserializer<OrderCreatedEvent>(schemaRegistry))
    .Build();

consumer.Subscribe("orders.order.created");

while (true)
{
    var result = consumer.Consume(cancellationToken);

    try
    {
        // Procesamiento idempotente
        await ProcessEventAsync(result.Message.Value);

        // Commit manual
        consumer.Commit(result);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Error processing event {EventId}", result.Message.Value.EventId);

        // Enviar a DLQ
        await SendToDLQ(result.Message);
    }
}
```

### Event Schema (Avro)

```json
{
  "type": "record",
  "name": "OrderCreatedEvent",
  "namespace": "com.talma.orders.events",
  "fields": [
    { "name": "eventId", "type": "string" },
    { "name": "eventType", "type": "string" },
    { "name": "eventVersion", "type": "string" },
    {
      "name": "timestamp",
      "type": { "type": "long", "logicalType": "timestamp-millis" }
    },
    { "name": "correlationId", "type": "string" },
    {
      "name": "payload",
      "type": {
        "type": "record",
        "name": "OrderPayload",
        "fields": [
          { "name": "orderId", "type": "string" },
          { "name": "customerId", "type": "string" },
          { "name": "totalAmount", "type": "double" }
        ]
      }
    }
  ]
}
```

---

## 7. Validación

```bash
# Crear topic
kafka-topics --create --topic orders.order.created \
  --bootstrap-server kafka:9092 \
  --replication-factor 3 \
  --partitions 6

# Verificar replicación
kafka-topics --describe --topic orders.order.created --bootstrap-server kafka:9092

# Listar consumer groups
kafka-consumer-groups --list --bootstrap-server kafka:9092

# Verificar lag
kafka-consumer-groups --describe --group notification-service.orders.order.created \
  --bootstrap-server kafka:9092
```

**Métricas de cumplimiento:**

| Métrica                | Target | Verificación              |
| ---------------------- | ------ | ------------------------- |
| Replication factor     | ≥3     | `kafka-topics --describe` |
| At-least-once delivery | 100%   | Manual commit habilitado  |
| DLQ configurada        | 100%   | Todos los consumers       |
| JSON Schema validación | 100%   | Mensajes validados        |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Mensajería Asíncrona - ADR](../../decisiones-de-arquitectura/adr-012-mensajeria-asincrona.md)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Avro Specification](https://avro.apache.org/docs/)
