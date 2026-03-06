---
id: event-contracts
sidebar_position: 5
title: Contratos de Eventos
description: Estándares para definir, publicar, consumir y versionar contratos de eventos de dominio con Apache Kafka.
tags: [mensajeria, kafka, contratos-eventos, json-schema, versionado]
---

# Contratos de Eventos

## Contexto

Este estándar define cómo estructurar, publicar, consumir y versionar contratos de eventos de dominio para comunicación asíncrona en Kafka. Cubre el envelope estándar, publicación con metadata completa, consumo tipado y estrategias de upcasting. Complementa el lineamiento [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md).

---

## Stack Tecnológico

| Componente        | Tecnología       | Versión | Uso                   |
| ----------------- | ---------------- | ------- | --------------------- |
| **Mensajería**    | Apache Kafka     | 3.6+    | Event streaming       |
| **Serialización** | System.Text.Json | 8.0+    | JSON serialization    |
| **Esquemas**      | JSON Schema      | 2020-12 | Validación de eventos |
| **Validación**    | NJsonSchema      | 11.0+   | Validación runtime    |
| **Observability** | OpenTelemetry    | 1.7+    | Trazas distribuidas   |

---

## Event Contracts

### ¿Qué es un Contrato de Evento?

Especificación formal de la estructura, semántica y versionamiento de un evento de dominio.

**Componentes:**

- **Event Metadata**: ID, tipo, timestamp, correlationId
- **Event Payload**: Datos del evento específico del dominio
- **Event Envelope**: Wrapper estándar con metadata común
- **JSON Schema**: Validación estructural

**Propósito:** Comunicación desacoplada, contrato explícito, evolución controlada.

**Beneficios:**
✅ Contrato explícito
✅ Validación automática
✅ Documentación viva
✅ Evolución sin romper consumidores

### Anatomía de un Evento

```csharp
// Evento base (envelope)
public abstract record DomainEvent
{
    /// <summary>
    /// ID único del evento (UUID v7 para ordenamiento)
    /// </summary>
    public required string EventId { get; init; }

    /// <summary>
    /// Tipo de evento (formato: domain.entity.action.version)
    /// </summary>
    /// <example>customers.customer.created.v1</example>
    public required string EventType { get; init; }

    /// <summary>
    /// Timestamp UTC del evento (ISO 8601)
    /// </summary>
    public required DateTimeOffset Timestamp { get; init; }

    /// <summary>
    /// ID de correlación para trazabilidad
    /// </summary>
    public required string CorrelationId { get; init; }

    /// <summary>
    /// ID de causalidad (eventId del evento que causó este)
    /// </summary>
    public string? CausationId { get; init; }

    /// <summary>
    /// Versión del esquema del evento
    /// </summary>
    public required string SchemaVersion { get; init; }

    /// <summary>
    /// Información del emisor
    /// </summary>
    public required EventSource Source { get; init; }

    /// <summary>
    /// Información del sujeto del evento
    /// </summary>
    public required EventSubject Subject { get; init; }
}

public record EventSource
{
    public required string Service { get; init; }
    public required string Version { get; init; }
    public string? Instance { get; init; }
}

public record EventSubject
{
    public required string Type { get; init; }
    public required string Id { get; init; }
    public string? TenantId { get; init; }
}
```

### Evento de Dominio Específico

```csharp
public record CustomerCreatedEvent : DomainEvent
{
    public required CustomerCreatedData Data { get; init; }
}

public record CustomerCreatedData
{
    public required Guid CustomerId { get; init; }
    public required string Name { get; init; }
    public required string Email { get; init; }
    public string? Phone { get; init; }
    public required DocumentData Document { get; init; }
    public required DateTimeOffset CreatedAt { get; init; }
}

public record DocumentData
{
    public required DocumentType Type { get; init; }
    public required string Number { get; init; }
}

public enum DocumentType
{
    DNI,
    RUC,
    CE
}
```

### Publicación de Eventos

```csharp
public interface IEventPublisher
{
    Task PublishAsync<T>(T @event, CancellationToken cancellationToken = default)
        where T : DomainEvent;
}

public class KafkaEventPublisher : IEventPublisher
{
    private readonly IProducer<string, string> _producer;
    private readonly ILogger<KafkaEventPublisher> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public KafkaEventPublisher(IProducer<string, string> producer, ILogger<KafkaEventPublisher> logger)
    {
        _producer = producer;
        _logger = logger;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            Converters = { new JsonStringEnumConverter() }
        };
    }

    public async Task PublishAsync<T>(T @event, CancellationToken cancellationToken = default)
        where T : DomainEvent
    {
        try
        {
            var enrichedEvent = @event with
            {
                EventId = string.IsNullOrEmpty(@event.EventId)
                    ? Ulid.NewUlid().ToString()
                    : @event.EventId,
                Timestamp = @event.Timestamp == default ? DateTimeOffset.UtcNow : @event.Timestamp
            };

            var json = JsonSerializer.Serialize(enrichedEvent, _jsonOptions);
            var topic = $"{@event.EventType.Split('.')[0]}-events";

            var message = new Message<string, string>
            {
                Key = @event.Subject.Id,
                Value = json,
                Headers = new Headers
                {
                    { "event-type", Encoding.UTF8.GetBytes(@event.EventType) },
                    { "schema-version", Encoding.UTF8.GetBytes(@event.SchemaVersion) },
                    { "correlation-id", Encoding.UTF8.GetBytes(@event.CorrelationId) },
                    { "content-type", Encoding.UTF8.GetBytes("application/json") }
                }
            };

            var result = await _producer.ProduceAsync(topic, message, cancellationToken);

            _logger.LogInformation(
                "Evento publicado: {EventType} - Partition: {Partition}, Offset: {Offset}",
                @event.EventType, result.Partition.Value, result.Offset.Value);
        }
        catch (ProduceException<string, string> ex)
        {
            _logger.LogError(ex, "Error al publicar evento {EventType}: {Error}",
                @event.EventType, ex.Error.Reason);
            throw;
        }
    }
}
```

### Consumo de Eventos

```csharp
public class CustomerEventConsumer : IHostedService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<CustomerEventConsumer> _logger;

    public Task StartAsync(CancellationToken cancellationToken)
    {
        _consumer.Subscribe(new[] { "customers-events" });
        _ = Task.Run(() => ProcessMessages(cancellationToken), cancellationToken);
        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        _consumer.Close();
        return Task.CompletedTask;
    }

    private async Task ProcessMessages(CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                var consumeResult = _consumer.Consume(cancellationToken);
                if (consumeResult?.Message == null) continue;

                var eventTypeHeader = consumeResult.Message.Headers
                    .FirstOrDefault(h => h.Key == "event-type");
                if (eventTypeHeader == null) continue;

                var eventType = Encoding.UTF8.GetString(eventTypeHeader.GetValueBytes());

                var @event = eventType switch
                {
                    "customers.customer.created.v1" =>
                        (DomainEvent?)JsonSerializer.Deserialize<CustomerCreatedEvent>(
                            consumeResult.Message.Value),
                    _ => null
                };

                if (@event != null)
                    await DispatchEvent(@event, cancellationToken);

                _consumer.Commit(consumeResult);
            }
            catch (ConsumeException ex)
            {
                _logger.LogError(ex, "Error al consumir mensaje: {Error}", ex.Error.Reason);
            }
            catch (OperationCanceledException)
            {
                break;
            }
        }
    }

    private async Task DispatchEvent(DomainEvent @event, CancellationToken cancellationToken)
    {
        using var scope = _serviceProvider.CreateScope();
        var handlerType = typeof(IEventHandler<>).MakeGenericType(@event.GetType());
        var handler = scope.ServiceProvider.GetService(handlerType);
        if (handler == null) return;

        var handleMethod = handlerType.GetMethod("HandleAsync");
        await (Task)handleMethod!.Invoke(handler, new object[] { @event, cancellationToken })!;
    }
}

public interface IEventHandler<in T> where T : DomainEvent
{
    Task HandleAsync(T @event, CancellationToken cancellationToken = default);
}

public class CustomerCreatedEventHandler : IEventHandler<CustomerCreatedEvent>
{
    private readonly ICustomerSyncService _syncService;
    private readonly ILogger<CustomerCreatedEventHandler> _logger;

    public async Task HandleAsync(CustomerCreatedEvent @event, CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Manejando CustomerCreated: {CustomerId}", @event.Data.CustomerId);
        await _syncService.SyncCustomerAsync(@event.Data, cancellationToken);
    }
}
```

### Versionamiento de Eventos

```csharp
// v1: Evento original
public record CustomerCreatedEventV1 : DomainEvent
{
    public required CustomerCreatedDataV1 Data { get; init; }
}

public record CustomerCreatedDataV1
{
    public required Guid CustomerId { get; init; }
    public required string Name { get; init; }
    public required string Email { get; init; }
}

// v2: Agregado campo Phone (compatible)
public record CustomerCreatedEventV2 : DomainEvent
{
    public required CustomerCreatedDataV2 Data { get; init; }
}

public record CustomerCreatedDataV2
{
    public required Guid CustomerId { get; init; }
    public required string Name { get; init; }
    public required string Email { get; init; }
    public string? Phone { get; init; }  // ✅ Campo opcional agregado (compatible)
}

// Upcasting: convertir v1 → v2
public class EventUpcaster
{
    public DomainEvent Upcast(DomainEvent @event)
    {
        return @event switch
        {
            CustomerCreatedEventV1 v1 => new CustomerCreatedEventV2
            {
                EventId = v1.EventId,
                EventType = "customers.customer.created.v2",
                Timestamp = v1.Timestamp,
                CorrelationId = v1.CorrelationId,
                CausationId = v1.CausationId,
                SchemaVersion = "2.0",
                Source = v1.Source,
                Subject = v1.Subject,
                Data = new CustomerCreatedDataV2
                {
                    CustomerId = v1.Data.CustomerId,
                    Name = v1.Data.Name,
                    Email = v1.Data.Email,
                    Phone = null
                }
            },
            _ => @event
        };
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar envelope estándar con metadata (eventId, eventType, timestamp, correlationId)
- **MUST** incluir schemaVersion en todos los eventos
- **MUST** usar ULID o UUID v7 para eventId (ordenamiento temporal)
- **MUST** usar formato ISO 8601 para timestamps
- **MUST** incluir source (servicio emisor) y subject (entidad)
- **MUST** versionar eventos al hacer cambios (`customers.customer.created.v1`)
- **MUST** mantener compatibilidad hacia atrás en versiones MINOR
- **MUST** soportar al menos 2 versiones mayores simultáneamente
- **MUST** comunicar breaking changes con 6 meses de anticipación

### SHOULD (Fuertemente recomendado)

- **SHOULD** validar eventos contra JSON Schema antes de publicar
- **SHOULD** usar CloudEvents 1.0 como base para envelope
- **SHOULD** implementar dead letter queue para eventos fallidos
- **SHOULD** incluir causationId para rastreo de causalidad
- **SHOULD** particionar topics por subject.id para ordenamiento
- **SHOULD** implementar idempotencia en consumidores

### MAY (Opcional)

- **MAY** usar Schema Registry (Confluent Schema Registry) para versionamiento
- **MAY** implementar event sourcing para entidades críticas
- **MAY** generar código de clientes desde AsyncAPI

### MUST NOT (Prohibido)

- **MUST NOT** incluir información sensible sin encriptar en eventos
- **MUST NOT** hacer cambios incompatibles sin versionar (breaking changes en MINOR)
- **MUST NOT** usar eventos para comunicación síncrona (usar APIs REST)
- **MUST NOT** depender de orden de llegada entre particiones
- **MUST NOT** publicar eventos con payload > 1MB (usar claim check pattern)

---

## Referencias

- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html) — Esquemas JSON
- [CloudEvents 1.0](https://cloudevents.io/) — Envelope estándar de eventos
- [Apache Kafka](https://kafka.apache.org/documentation/) — Event streaming
- [NJsonSchema](https://github.com/RicoSuter/NJsonSchema) — Validación runtime de JSON Schema
- [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) — Lineamiento relacionado
- [Event Design](./event-design.md)
- [AsyncAPI Specification](./asyncapi-specification.md)
- [Idempotency](./idempotency.md)
