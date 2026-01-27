---
id: kafka-eventos
sidebar_position: 1
title: Mensajería con Kafka
description: Estándares para event-driven architecture con Apache Kafka 3.6+, Confluent Platform y Avro
---

## 1. Propósito

Este estándar define cómo implementar mensajería basada en eventos con Apache Kafka para arquitecturas distribuidas de Talma. Establece:
- **Event-driven architecture** con desacoplamiento entre productores y consumidores
- **Event schema design** con estructura estándar (eventId, eventType, timestamp, payload)
- **At-least-once delivery** con consumidores idempotentes
- **Schema evolution** con Confluent Schema Registry y Avro
- **Dead Letter Queue** para manejo de errores

Permite comunicación asíncrona entre microservicios, event sourcing y procesamiento de eventos en tiempo real.

**Versión**: 1.0  
**Última actualización**: 2025-08-08

## 2. Alcance

### Aplica a:
- Microservicios con comunicación asíncrona (órdenes, pagos, notificaciones)
- Event sourcing (log de eventos como source of truth)
- Procesamiento de eventos en tiempo real (analytics, auditoría)
- Integración entre bounded contexts (DDD)
- Notificaciones cross-service (email, SMS, push)

### No aplica a:
- Comunicación síncrona request-response (usar APIs REST)
- Transacciones ACID entre servicios (usar Saga pattern con eventos)
- Transferencia de archivos grandes (usar S3 con event notification)
- Métricas de tiempo real (usar métricas directas, no eventos)

## 3. Tecnologías Obligatorias

| Tecnología | Versión Mínima | Propósito |
|------------|----------------|-----------|  
| **Apache Kafka** | 3.6+ | Message broker distribuido con particiones y replicación |
| **Confluent.Kafka** | 2.3+ | Cliente .NET para Kafka (producer/consumer) |
| **Confluent Schema Registry** | 7.5+ | Registro centralizado de schemas Avro/Protobuf/JSON |
| **Apache Avro** | 1.11+ | Serialización binaria con schema evolution |
| **Confluent.SchemaRegistry.Serdes.Avro** | 2.3+ | Serializadores Avro para .NET |
| **kafkajs** (Node.js) | 2.2+ | Cliente Kafka para Node.js/TypeScript |
| **AWS MSK** (opcional) | 3.6+ | Kafka managed service en AWS |

## 4. Especificaciones Técnicas

### 4.1 Convenciones de Nomenclatura

**Topics**:
```
{domain}.{entity}.{event-type}

Ejemplos:
- orders.order.created
- orders.order.cancelled  
- shipping.shipment.dispatched
- billing.invoice.paid
```

**Consumer Groups**:
```
{service-name}.{topic-name}

Ejemplos:
- notification-service.orders.order.created
- analytics-service.orders.order.created
```

### 4.2 Event Schema Design

### Estructura estándar de evento

```json
{
  "eventId": "uuid-v4",
  "eventType": "orders.order.created",
  "eventVersion": "1.0.0",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "source": "orders-api",
  "correlationId": "correlation-uuid",
  "causationId": "causation-uuid",
  "metadata": {
    "userId": "123",
    "country": "PE",
    "tenant": "tlm-pe"
  },
  "payload": {
    "orderId": "456",
    "customerId": "789",
    "items": [
      {
        "productId": "101",
        "quantity": 2,
        "price": 100.0
      }
    ],
    "totalAmount": 200.0,
    "currency": "USD"
  }
}
```

### Campos obligatorios

| Campo           | Tipo     | Descripción                           |
| --------------- | -------- | ------------------------------------- |
| `eventId`       | UUID     | Identificador único del evento        |
| `eventType`     | string   | Tipo de evento (domain.entity.action) |
| `eventVersion`  | string   | Versión del schema del evento         |
| `timestamp`     | ISO 8601 | Momento en que ocurrió el evento      |
| `source`        | string   | Servicio que generó el evento         |
| `correlationId` | UUID     | ID de correlación para tracing        |
| `payload`       | object   | Datos del evento                      |

## 4. Configuración de Kafka

### Producer configuration (C#)

```csharp
public class KafkaProducerConfig
{
    public static ProducerConfig GetConfig(IConfiguration configuration)
    {
        return new ProducerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],
            ClientId = configuration["Kafka:ClientId"],
            Acks = Acks.All, // Garantizar que todas las réplicas confirmen
            EnableIdempotence = true, // Evitar duplicados
            MaxInFlight = 5,
            MessageSendMaxRetries = 3,
            RetryBackoffMs = 1000,
            CompressionType = CompressionType.Snappy,
            SecurityProtocol = SecurityProtocol.SaslSsl,
            SaslMechanism = SaslMechanism.Plain,
            SaslUsername = configuration["Kafka:SaslUsername"],
            SaslPassword = configuration["Kafka:SaslPassword"]
        };
    }
}
```

### Consumer configuration (C#)

```csharp
public class KafkaConsumerConfig
{
    public static ConsumerConfig GetConfig(
        IConfiguration configuration,
        string groupId)
    {
        return new ConsumerConfig
        {
            BootstrapServers = configuration["Kafka:BootstrapServers"],
            GroupId = groupId,
            AutoOffsetReset = AutoOffsetReset.Earliest,
            EnableAutoCommit = false, // Manual commit para garantizar procesamiento
            MaxPollIntervalMs = 300000, // 5 minutos
            SessionTimeoutMs = 30000,
            SecurityProtocol = SecurityProtocol.SaslSsl,
            SaslMechanism = SaslMechanism.Plain,
            SaslUsername = configuration["Kafka:SaslUsername"],
            SaslPassword = configuration["Kafka:SaslPassword"]
        };
    }
}
```

## 5. Implementación de Producer

```csharp
public interface IEventPublisher
{
    Task PublishAsync<T>(string topic, T @event, CancellationToken cancellationToken = default)
        where T : class;
}

public class KafkaEventPublisher : IEventPublisher
{
    private readonly IProducer<string, string> _producer;
    private readonly ILogger<KafkaEventPublisher> _logger;

    public KafkaEventPublisher(
        IProducer<string, string> producer,
        ILogger<KafkaEventPublisher> logger)
    {
        _producer = producer;
        _logger = logger;
    }

    public async Task PublishAsync<T>(
        string topic,
        T @event,
        CancellationToken cancellationToken = default)
        where T : class
    {
        var eventWrapper = new EventEnvelope<T>
        {
            EventId = Guid.NewGuid().ToString(),
            EventType = typeof(T).Name,
            EventVersion = "1.0.0",
            Timestamp = DateTime.UtcNow,
            Source = "orders-api",
            CorrelationId = Activity.Current?.Id ?? Guid.NewGuid().ToString(),
            Payload = @event
        };

        var message = new Message<string, string>
        {
            Key = eventWrapper.EventId,
            Value = JsonSerializer.Serialize(eventWrapper),
            Headers = new Headers
            {
                { "content-type", Encoding.UTF8.GetBytes("application/json") },
                { "correlation-id", Encoding.UTF8.GetBytes(eventWrapper.CorrelationId) }
            }
        };

        try
        {
            var result = await _producer.ProduceAsync(topic, message, cancellationToken);

            _logger.LogInformation(
                "Event published to {Topic} - Partition: {Partition}, Offset: {Offset}",
                topic, result.Partition.Value, result.Offset.Value);
        }
        catch (ProduceException<string, string> ex)
        {
            _logger.LogError(ex,
                "Failed to publish event to {Topic}: {Reason}",
                topic, ex.Error.Reason);
            throw;
        }
    }
}
```

## 6. Implementación de Consumer

```csharp
public abstract class KafkaConsumerBase<T> : BackgroundService where T : class
{
    private readonly IConsumer<string, string> _consumer;
    private readonly ILogger _logger;
    private readonly string _topic;

    protected KafkaConsumerBase(
        IConsumer<string, string> consumer,
        ILogger logger,
        string topic)
    {
        _consumer = consumer;
        _logger = logger;
        _topic = topic;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe(_topic);

        _logger.LogInformation(
            "Consumer started for topic {Topic}",
            _topic);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var consumeResult = _consumer.Consume(stoppingToken);

                if (consumeResult?.Message == null)
                    continue;

                var eventEnvelope = JsonSerializer.Deserialize<EventEnvelope<T>>(
                    consumeResult.Message.Value);

                if (eventEnvelope == null)
                {
                    _logger.LogWarning("Failed to deserialize event");
                    _consumer.Commit(consumeResult);
                    continue;
                }

                using var activity = new Activity("ProcessEvent")
                    .SetParentId(eventEnvelope.CorrelationId);
                activity?.Start();

                try
                {
                    await ProcessEventAsync(eventEnvelope.Payload, stoppingToken);

                    // Commit manual después de procesamiento exitoso
                    _consumer.Commit(consumeResult);

                    _logger.LogInformation(
                        "Event processed successfully - Offset: {Offset}",
                        consumeResult.Offset.Value);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex,
                        "Error processing event - Offset: {Offset}",
                        consumeResult.Offset.Value);

                    // Estrategia de manejo de errores:
                    // 1. Retry con backoff
                    // 2. Dead Letter Queue
                    // 3. Alert
                    await HandleProcessingErrorAsync(eventEnvelope, ex);

                    // Commit incluso si falla (ya está en DLQ)
                    _consumer.Commit(consumeResult);
                }
            }
            catch (ConsumeException ex)
            {
                _logger.LogError(ex, "Consume error: {Reason}", ex.Error.Reason);
            }
        }

        _consumer.Close();
    }

    protected abstract Task ProcessEventAsync(T @event, CancellationToken cancellationToken);

    protected virtual Task HandleProcessingErrorAsync(
        EventEnvelope<T> eventEnvelope,
        Exception exception)
    {
        // Enviar a Dead Letter Queue
        // Registrar en base de datos de errores
        // Enviar alerta
        return Task.CompletedTask;
    }
}
```

## 7. Schema Registry y Versionado

### Schema Avro (recomendado para producción)

```json
{
  "type": "record",
  "name": "OrderCreated",
  "namespace": "com.talma.orders.events",
  "fields": [
    {
      "name": "eventId",
      "type": "string"
    },
    {
      "name": "eventVersion",
      "type": "string",
      "default": "1.0.0"
    },
    {
      "name": "timestamp",
      "type": "long",
      "logicalType": "timestamp-millis"
    },
    {
      "name": "orderId",
      "type": "string"
    },
    {
      "name": "customerId",
      "type": "string"
    },
    {
      "name": "totalAmount",
      "type": "double"
    },
    {
      "name": "currency",
      "type": "string",
      "default": "USD"
    }
  ]
}
```

### Estrategias de evolución

- **Backward compatible**: Nuevos consumidores pueden leer eventos viejos
- **Forward compatible**: Viejos consumidores pueden leer eventos nuevos
- **Full compatible**: Ambas direcciones

## 8. Dead Letter Queue

```csharp
public class DeadLetterQueueHandler
{
    private readonly IProducer<string, string> _producer;
    private readonly ILogger<DeadLetterQueueHandler> _logger;

    public async Task SendToDeadLetterQueueAsync<T>(
        string originalTopic,
        EventEnvelope<T> eventEnvelope,
        Exception exception)
    {
        var dlqTopic = $"{originalTopic}.dlq";

        var dlqMessage = new DeadLetterMessage
        {
            OriginalTopic = originalTopic,
            EventEnvelope = eventEnvelope,
            ErrorMessage = exception.Message,
            StackTrace = exception.StackTrace,
            Timestamp = DateTime.UtcNow,
            RetryCount = 0
        };

        var message = new Message<string, string>
        {
            Key = eventEnvelope.EventId,
            Value = JsonSerializer.Serialize(dlqMessage),
            Headers = new Headers
            {
                { "error-type", Encoding.UTF8.GetBytes(exception.GetType().Name) }
            }
        };

        await _producer.ProduceAsync(dlqTopic, message);

        _logger.LogWarning(
            "Event sent to DLQ {DlqTopic} - EventId: {EventId}",
            dlqTopic, eventEnvelope.EventId);
    }
}
```

## 5. Buenas Prácticas

### 5.1 Idempotencia en Consumidores

```csharp
public class OrderCreatedConsumer : KafkaConsumerBase<OrderCreatedEvent>
{
    private readonly IOrderRepository _repository;

    protected override async Task ProcessEventAsync(
        OrderCreatedEvent @event,
        CancellationToken cancellationToken)
    {
        // ✅ Verificar si ya se procesó (idempotencia)
        var existingOrder = await _repository.GetByEventIdAsync(@event.EventId);
        if (existingOrder != null)
        {
            _logger.LogInformation("Event {EventId} already processed", @event.EventId);
            return; // Ya procesado, skip
        }

        // Procesar evento
        var order = Order.CreateFromEvent(@event);
        await _repository.AddAsync(order, cancellationToken);
    }
}
```

### 5.2 Schema Evolution (Backward Compatible)

```json
// V1
{
  "orderId": "123",
  "totalAmount": 100.0
}

// V2 - Agregar campo con default
{
  "orderId": "123",
  "totalAmount": 100.0,
  "currency": "USD"  // Nuevo campo con default
}
```

### 5.3 Partitioning Strategy

```csharp
// Particionar por clave de negocio para garantizar orden
var message = new Message<string, string>
{
    Key = order.CustomerId.ToString(), // Misma partición para mismo cliente
    Value = JsonSerializer.Serialize(orderEvent)
};

await _producer.ProduceAsync("orders.order.created", message);
```

## 6. Antipatrones

### 6.1 ❌ Consumidores No Idempotentes

**Problema**:
```csharp
// ❌ Procesa evento sin verificar duplicados
protected override async Task ProcessEventAsync(OrderCreatedEvent @event)
{
    await _emailService.SendOrderConfirmationAsync(@event.OrderId);
    // Si Kafka reintenta, envía email duplicado
}
```

**Solución**:
```csharp
// ✅ Verificar si ya se procesó
protected override async Task ProcessEventAsync(OrderCreatedEvent @event)
{
    if (await _processedEventsRepository.ExistsAsync(@event.EventId))
        return;

    await _emailService.SendOrderConfirmationAsync(@event.OrderId);
    await _processedEventsRepository.MarkAsProcessedAsync(@event.EventId);
}
```

### 6.2 ❌ Eventos Sin CorrelationId

**Problema**:
```csharp
// ❌ Sin correlationId, imposible correlacionar eventos
var @event = new OrderCreatedEvent
{
    EventId = Guid.NewGuid(),
    OrderId = orderId
};
```

**Solución**:
```csharp
// ✅ Propagar correlationId
var @event = new OrderCreatedEvent
{
    EventId = Guid.NewGuid(),
    CorrelationId = Activity.Current?.Id ?? Guid.NewGuid().ToString(),
    OrderId = orderId
};
```

### 6.3 ❌ Schema Breaking Changes

**Problema**:
```json
// V1
{ "orderId": "123", "amount": 100.0 }

// V2 - Renombrar campo (breaking change)
{ "orderId": "123", "totalAmount": 100.0 }
```

**Solución**:
```json
// V2 - Mantener campo viejo y agregar nuevo
{
  "orderId": "123",
  "amount": 100.0,      // Deprecated, mantener por compatibilidad
  "totalAmount": 100.0  // Nuevo campo
}
```

### 6.4 ❌ Consumer Lag Ignorado

**Problema**:
```csharp
// ❌ Sin monitoreo de consumer lag
// Si el consumidor se atrasa, no hay alertas
```

**Solución**:
```csharp
// ✅ Monitorear consumer lag con métricas
public class KafkaMetrics
{
    private readonly Counter<long> _messagesProcessed;
    private readonly Gauge<long> _consumerLag;

    public void RecordLag(long lag)
    {
        _consumerLag.Record(lag);
        
        if (lag > 10000)
            _logger.LogWarning("High consumer lag: {Lag}", lag);
    }
}
```

## 7. Validación y Testing

### 7.1 Tests de Integración con TestContainers

```csharp
public class KafkaIntegrationTests : IAsyncLifetime
{
    private KafkaContainer _kafkaContainer = null!;

    public async Task InitializeAsync()
    {
        _kafkaContainer = new KafkaBuilder()
            .WithImage("confluentinc/cp-kafka:7.5.0")
            .Build();

        await _kafkaContainer.StartAsync();
    }

    [Fact]
    public async Task PublishEvent_ConsumerReceives_ProcessesCorrectly()
    {
        // Arrange
        var producer = new KafkaProducer(_kafkaContainer.GetBootstrapAddress());
        var consumer = new OrderCreatedConsumer(_kafkaContainer.GetBootstrapAddress());

        // Act
        await producer.PublishAsync("orders.order.created", new OrderCreatedEvent());
        await Task.Delay(1000); // Esperar procesamiento

        // Assert
        var processedOrder = await _repository.GetByIdAsync(orderId);
        processedOrder.Should().NotBeNull();
    }

    public async Task DisposeAsync() => await _kafkaContainer.DisposeAsync();
}
```

## 8. Referencias

### Lineamientos Relacionados
- [Comunicación Asíncrona y Eventos](/docs/fundamentos-corporativos/lineamientos/arquitectura/comunicacion-asincrona-y-eventos)
- [Resiliencia y Disponibilidad](/docs/fundamentos-corporativos/lineamientos/arquitectura/resiliencia-y-disponibilidad)

### Estándares Relacionados
- [Colas de Mensajes](./02-queues.md)
- [Logging Estructurado](../observabilidad/01-logging.md)

### ADRs Relacionados
- [ADR-012: Mensajería Asíncrona](/docs/decisiones-de-arquitectura/adr-012-mensajeria-asincrona)
- [ADR-013: Event Sourcing](/docs/decisiones-de-arquitectura/adr-013-event-sourcing)

### Recursos Externos
- [Confluent Kafka Best Practices](https://docs.confluent.io/platform/current/kafka/deployment.html)
- [Event-Driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

## 9. Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|  
| 1.0 | 2025-08-08 | Equipo de Arquitectura | Versión inicial con template de 9 secciones |
