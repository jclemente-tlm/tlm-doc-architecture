---
id: queues
sidebar_position: 2
title: Colas de Mensajes
description: Estándares para colas de mensajes con AWS SQS y RabbitMQ
---

## 1. Principios de Message Queues

- **Decoupling**: Desacoplar productores y consumidores
- **Load leveling**: Manejar picos de carga
- **Guaranteed delivery**: Asegurar entrega de mensajes
- **Ordering**: Definir si se requiere orden (FIFO) o no
- **Retry y DLQ**: Manejo de errores con reintentos y dead letter queues

## 2. AWS SQS

### Tipos de colas

| Tipo         | Uso                                | Throughput     | Ordering       |
| ------------ | ---------------------------------- | -------------- | -------------- |
| **Standard** | Alto throughput, orden best-effort | Ilimitado      | No garantizado |
| **FIFO**     | Orden exacto, exactamente-una-vez  | 300-3000 msg/s | Garantizado    |

### Naming Conventions

```
{environment}-{service}-{purpose}

Ejemplos:
- prod-orders-processing
- prod-notifications-email.fifo
- dev-analytics-events
```

### Configuración de SQS

```csharp
// appsettings.json
{
  "AWS": {
    "Region": "us-east-1",
    "SQS": {
      "OrdersQueue": "https://sqs.us-east-1.amazonaws.com/123456789012/prod-orders-processing",
      "NotificationsQueue": "https://sqs.us-east-1.amazonaws.com/123456789012/prod-notifications-email.fifo",
      "DeadLetterQueue": "https://sqs.us-east-1.amazonaws.com/123456789012/prod-orders-dlq"
    }
  }
}
```

## 3. Implementación de Producer (SQS)

```csharp
public interface IMessageQueuePublisher
{
    Task SendMessageAsync<T>(string queueUrl, T message, CancellationToken cancellationToken = default)
        where T : class;
    Task SendBatchAsync<T>(string queueUrl, IEnumerable<T> messages, CancellationToken cancellationToken = default)
        where T : class;
}

public class SqsPublisher : IMessageQueuePublisher
{
    private readonly IAmazonSQS _sqsClient;
    private readonly ILogger<SqsPublisher> _logger;

    public SqsPublisher(IAmazonSQS sqsClient, ILogger<SqsPublisher> logger)
    {
        _sqsClient = sqsClient;
        _logger = logger;
    }

    public async Task SendMessageAsync<T>(
        string queueUrl,
        T message,
        CancellationToken cancellationToken = default)
        where T : class
    {
        var messageEnvelope = new MessageEnvelope<T>
        {
            MessageId = Guid.NewGuid().ToString(),
            Timestamp = DateTime.UtcNow,
            CorrelationId = Activity.Current?.Id ?? Guid.NewGuid().ToString(),
            Payload = message
        };

        var request = new SendMessageRequest
        {
            QueueUrl = queueUrl,
            MessageBody = JsonSerializer.Serialize(messageEnvelope),
            MessageAttributes = new Dictionary<string, MessageAttributeValue>
            {
                ["MessageType"] = new MessageAttributeValue
                {
                    DataType = "String",
                    StringValue = typeof(T).Name
                },
                ["CorrelationId"] = new MessageAttributeValue
                {
                    DataType = "String",
                    StringValue = messageEnvelope.CorrelationId
                },
                ["Timestamp"] = new MessageAttributeValue
                {
                    DataType = "Number",
                    StringValue = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds().ToString()
                }
            }
        };

        // Para FIFO queues
        if (queueUrl.EndsWith(".fifo"))
        {
            request.MessageGroupId = "default"; // o un ID específico para ordenamiento
            request.MessageDeduplicationId = messageEnvelope.MessageId;
        }

        try
        {
            var response = await _sqsClient.SendMessageAsync(request, cancellationToken);

            _logger.LogInformation(
                "Message sent to SQS - MessageId: {MessageId}, Queue: {Queue}",
                response.MessageId, queueUrl);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Failed to send message to SQS queue {Queue}",
                queueUrl);
            throw;
        }
    }

    public async Task SendBatchAsync<T>(
        string queueUrl,
        IEnumerable<T> messages,
        CancellationToken cancellationToken = default)
        where T : class
    {
        var messagesList = messages.ToList();
        if (!messagesList.Any())
            return;

        // SQS limita a 10 mensajes por batch
        const int batchSize = 10;
        var batches = messagesList
            .Select((msg, index) => new { msg, index })
            .GroupBy(x => x.index / batchSize)
            .Select(g => g.Select(x => x.msg).ToList());

        foreach (var batch in batches)
        {
            var entries = batch.Select((msg, index) => new SendMessageBatchRequestEntry
            {
                Id = index.ToString(),
                MessageBody = JsonSerializer.Serialize(new MessageEnvelope<T>
                {
                    MessageId = Guid.NewGuid().ToString(),
                    Timestamp = DateTime.UtcNow,
                    CorrelationId = Activity.Current?.Id ?? Guid.NewGuid().ToString(),
                    Payload = msg
                })
            }).ToList();

            var request = new SendMessageBatchRequest
            {
                QueueUrl = queueUrl,
                Entries = entries
            };

            var response = await _sqsClient.SendMessageBatchAsync(request, cancellationToken);

            if (response.Failed.Any())
            {
                _logger.LogWarning(
                    "Batch send had {FailedCount} failures out of {TotalCount}",
                    response.Failed.Count, batch.Count);
            }
        }
    }
}
```

## 4. Implementación de Consumer (SQS)

```csharp
public abstract class SqsConsumerBase<T> : BackgroundService where T : class
{
    private readonly IAmazonSQS _sqsClient;
    private readonly ILogger _logger;
    private readonly string _queueUrl;
    private readonly int _maxNumberOfMessages;
    private readonly int _waitTimeSeconds;

    protected SqsConsumerBase(
        IAmazonSQS sqsClient,
        ILogger logger,
        string queueUrl,
        int maxNumberOfMessages = 10,
        int waitTimeSeconds = 20)
    {
        _sqsClient = sqsClient;
        _logger = logger;
        _queueUrl = queueUrl;
        _maxNumberOfMessages = maxNumberOfMessages;
        _waitTimeSeconds = waitTimeSeconds;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation(
            "SQS Consumer started for queue {Queue}",
            _queueUrl);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var request = new ReceiveMessageRequest
                {
                    QueueUrl = _queueUrl,
                    MaxNumberOfMessages = _maxNumberOfMessages,
                    WaitTimeSeconds = _waitTimeSeconds, // Long polling
                    MessageAttributeNames = new List<string> { "All" },
                    AttributeNames = new List<string> { "All" }
                };

                var response = await _sqsClient.ReceiveMessageAsync(request, stoppingToken);

                foreach (var message in response.Messages)
                {
                    await ProcessMessageAsync(message, stoppingToken);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error receiving messages from SQS");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }

    private async Task ProcessMessageAsync(Message message, CancellationToken cancellationToken)
    {
        try
        {
            var envelope = JsonSerializer.Deserialize<MessageEnvelope<T>>(message.Body);

            if (envelope == null)
            {
                _logger.LogWarning("Failed to deserialize message");
                await DeleteMessageAsync(message.ReceiptHandle, cancellationToken);
                return;
            }

            using var activity = new Activity("ProcessMessage")
                .SetParentId(envelope.CorrelationId);
            activity?.Start();

            _logger.LogInformation(
                "Processing message {MessageId}",
                envelope.MessageId);

            await ProcessMessageAsync(envelope.Payload, cancellationToken);

            // Eliminar mensaje después de procesamiento exitoso
            await DeleteMessageAsync(message.ReceiptHandle, cancellationToken);

            _logger.LogInformation(
                "Message processed successfully {MessageId}",
                envelope.MessageId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Error processing message {MessageId}",
                message.MessageId);

            // SQS automáticamente reintentará si no se elimina el mensaje
            // Después de MaxReceiveCount, el mensaje irá a la DLQ
        }
    }

    private async Task DeleteMessageAsync(string receiptHandle, CancellationToken cancellationToken)
    {
        try
        {
            await _sqsClient.DeleteMessageAsync(
                _queueUrl,
                receiptHandle,
                cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete message");
        }
    }

    protected abstract Task ProcessMessageAsync(T message, CancellationToken cancellationToken);
}
```

## 5. Dead Letter Queue Configuration

```csharp
public class SqsQueueConfiguration
{
    public static async Task ConfigureQueueWithDlqAsync(
        IAmazonSQS sqsClient,
        string queueUrl,
        string dlqArn,
        int maxReceiveCount = 3)
    {
        var redrivePolicy = new
        {
            deadLetterTargetArn = dlqArn,
            maxReceiveCount = maxReceiveCount
        };

        var request = new SetQueueAttributesRequest
        {
            QueueUrl = queueUrl,
            Attributes = new Dictionary<string, string>
            {
                ["RedrivePolicy"] = JsonSerializer.Serialize(redrivePolicy),
                ["VisibilityTimeout"] = "300", // 5 minutos
                ["MessageRetentionPeriod"] = "345600" // 4 días
            }
        };

        await sqsClient.SetQueueAttributesAsync(request);
    }
}
```

## 6. RabbitMQ

### Exchange Types

| Tipo        | Uso                         | Routing          |
| ----------- | --------------------------- | ---------------- |
| **Direct**  | Routing exacto por clave    | Exacto           |
| **Topic**   | Routing por patrón          | Wildcards (\* #) |
| **Fanout**  | Broadcast a todas las colas | Sin routing      |
| **Headers** | Routing por headers         | Headers match    |

### Configuración de RabbitMQ

```csharp
public class RabbitMqConfiguration
{
    public static IConnection CreateConnection(IConfiguration configuration)
    {
        var factory = new ConnectionFactory
        {
            HostName = configuration["RabbitMQ:Host"],
            Port = int.Parse(configuration["RabbitMQ:Port"] ?? "5672"),
            UserName = configuration["RabbitMQ:Username"],
            Password = configuration["RabbitMQ:Password"],
            VirtualHost = configuration["RabbitMQ:VirtualHost"] ?? "/",
            AutomaticRecoveryEnabled = true,
            NetworkRecoveryInterval = TimeSpan.FromSeconds(10),
            RequestedHeartbeat = TimeSpan.FromSeconds(60)
        };

        return factory.CreateConnection();
    }
}
```

### Publisher (RabbitMQ)

```csharp
public class RabbitMqPublisher : IDisposable
{
    private readonly IConnection _connection;
    private readonly IModel _channel;
    private readonly ILogger<RabbitMqPublisher> _logger;

    public RabbitMqPublisher(
        IConnection connection,
        ILogger<RabbitMqPublisher> logger)
    {
        _connection = connection;
        _channel = _connection.CreateModel();
        _logger = logger;
    }

    public void Publish<T>(string exchange, string routingKey, T message) where T : class
    {
        var envelope = new MessageEnvelope<T>
        {
            MessageId = Guid.NewGuid().ToString(),
            Timestamp = DateTime.UtcNow,
            CorrelationId = Activity.Current?.Id ?? Guid.NewGuid().ToString(),
            Payload = message
        };

        var body = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(envelope));

        var properties = _channel.CreateBasicProperties();
        properties.Persistent = true; // Persistir mensajes en disco
        properties.MessageId = envelope.MessageId;
        properties.CorrelationId = envelope.CorrelationId;
        properties.Timestamp = new AmqpTimestamp(DateTimeOffset.UtcNow.ToUnixTimeSeconds());
        properties.ContentType = "application/json";

        _channel.BasicPublish(
            exchange: exchange,
            routingKey: routingKey,
            basicProperties: properties,
            body: body);

        _logger.LogInformation(
            "Message published to {Exchange}/{RoutingKey} - MessageId: {MessageId}",
            exchange, routingKey, envelope.MessageId);
    }

    public void Dispose()
    {
        _channel?.Close();
        _channel?.Dispose();
    }
}
```

## 7. Checklist de Message Queues

- [ ] **Dead Letter Queue**: Configurada para mensajes fallidos
- [ ] **Visibility Timeout**: Configurado apropiadamente (> tiempo de procesamiento)
- [ ] **Retention Period**: Definido según necesidades de negocio
- [ ] **Idempotencia**: Consumidores manejan mensajes duplicados
- [ ] **Monitoring**: Métricas de tamaño de cola, age of oldest message
- [ ] **Alertas**: Configuradas para colas creciendo indefinidamente
- [ ] **Batch processing**: Usado cuando sea apropiado para eficiencia
- [ ] **Long polling**: Habilitado para reducir costos y latencia (SQS)

## 📖 Referencias

### Principios relacionados

- [Desacoplamiento](/docs/fundamentos-corporativos/principios/arquitectura/desacoplamiento)

### Lineamientos relacionados

- [Comunicación Asíncrona y Eventos](/docs/fundamentos-corporativos/lineamientos/arquitectura/comunicacion-asincrona-y-eventos)
- [Resiliencia y Disponibilidad](/docs/fundamentos-corporativos/lineamientos/arquitectura/resiliencia-y-disponibilidad)

### Estándares relacionados

- [Kafka y Eventos](/docs/fundamentos-corporativos/estandares/mensajeria/kafka-eventos)

### ADRs relacionados

- [ADR-012: Mensajería Asíncrona](/docs/decisiones-de-arquitectura/adr-012-mensajeria-asincrona)
- [ADR-015: Manejo de Errores y Cola](/docs/decisiones-de-arquitectura/adr-015-manejo-errores-cola)

### Recursos externos

- [AWS SQS Best Practices](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html)
- [RabbitMQ Production Checklist](https://www.rabbitmq.com/production-checklist.html)
