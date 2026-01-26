---
id: kafka-eventos
sidebar_position: 1
title: Kafka y Eventos
description: Estándares para mensajería basada en eventos con Apache Kafka
---

## 1. Principios de Event-Driven Architecture

- **Event-first thinking**: Modelar el dominio como una serie de eventos
- **Desacoplamiento**: Productores y consumidores no se conocen entre sí, solo comparten el contrato del evento
- **Inmutabilidad**: Los eventos son hechos inmutables del pasado
- **At-least-once delivery**: Diseñar consumidores idempotentes
- **Schema evolution**: Mantener compatibilidad en evolución de eventos
- **Event sourcing**: Considerar el log de eventos como source of truth

## 2. Naming Conventions

### Topics

```
{domain}.{entity}.{event-type}

Ejemplos:
- orders.order.created
- orders.order.cancelled
- shipping.shipment.dispatched
- billing.invoice.paid
```

### Consumer Groups

```
{service-name}.{topic-name}

Ejemplos:
- notification-service.orders.order.created
- analytics-service.orders.order.created
```

## 3. Event Schema Design

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

## 9. Checklist de Kafka

- [ ] **Naming**: Topics siguen convención `domain.entity.event`
- [ ] **Schema**: Eventos tienen estructura estándar con metadata
- [ ] **Idempotencia**: Consumidores manejan duplicados correctamente
- [ ] **Error handling**: DLQ configurado para eventos fallidos
- [ ] **Monitoring**: Métricas de lag, throughput, errors
- [ ] **Security**: SSL/SASL habilitado en producción
- [ ] **Retention**: Políticas de retención configuradas
- [ ] **Partitioning**: Estrategia de particionamiento definida

## 📖 Referencias

### Principios relacionados

- [Desacoplamiento](/docs/fundamentos-corporativos/principios/arquitectura/desacoplamiento)

### Lineamientos relacionados

- [Comunicación Asíncrona y Eventos](/docs/fundamentos-corporativos/lineamientos/arquitectura/comunicacion-asincrona-y-eventos)
- [Resiliencia y Disponibilidad](/docs/fundamentos-corporativos/lineamientos/arquitectura/resiliencia-y-disponibilidad)

### ADRs relacionados

- [ADR-012: Mensajería Asíncrona](/docs/decisiones-de-arquitectura/adr-012-mensajeria-asincrona)
- [ADR-013: Event Sourcing](/docs/decisiones-de-arquitectura/adr-013-event-sourcing)

### Recursos externos

- [Confluent Kafka Best Practices](https://docs.confluent.io/platform/current/kafka/deployment.html)
- [Event-Driven Architecture Patterns](https://martinfowler.com/articles/201701-event-driven.html)
