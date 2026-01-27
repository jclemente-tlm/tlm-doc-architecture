---
id: queues
sidebar_position: 2
title: Colas de Mensajes
description: Estándares para message queues con AWS SQS, RabbitMQ 3.12+ y patrones de retry
---

## 1. Propósito

Este estándar define cómo implementar colas de mensajes para desacoplamiento, load leveling y guaranteed delivery en aplicaciones de Talma. Establece:
- **AWS SQS** (Standard/FIFO) para colas managed en AWS
- **RabbitMQ** para colas on-premise con exchanges avanzados
- **Dead Letter Queue** para manejo de errores y reintentos
- **Idempotencia** en consumidores (at-least-once delivery)
- **Long polling** para reducir latencia y costos

Permite procesamiento asíncrono de tareas, manejo de picos de carga y garantía de entrega de mensajes.

**Versión**: 1.0  
**Última actualización**: 2025-08-08

## 2. Alcance

### Aplica a:
- Procesamiento asíncrono de tareas (envío de emails, generación de reportes)
- Desacoplamiento entre servicios con garantía de entrega
- Manejo de picos de carga (load leveling)
- Workflows con pasos secuenciales (FIFO queues)
- Retry automático de operaciones fallidas

### No aplica a:
- Event-driven architecture multi-consumidor (usar Kafka)
- Comunicación en tiempo real (usar WebSockets/SignalR)
- Broadcasting a múltiples servicios (usar Kafka o RabbitMQ Fanout)
- Transferencia de archivos (usar S3 con SQS notification)

## 3. Tecnologías Obligatorias

| Tecnología | Versión Mínima | Propósito |
|------------|----------------|-----------|  
| **AWS SQS** | - | Colas managed en AWS (Standard/FIFO) |
| **AWSSDK.SQS** | 3.7+ | Cliente .NET para SQS |
| **RabbitMQ** | 3.12+ | Message broker on-premise con exchanges avanzados |
| **RabbitMQ.Client** | 6.6+ | Cliente .NET para RabbitMQ |
| **MassTransit** | 8.1+ | Framework de mensajería para .NET (abstracción sobre SQS/RabbitMQ) |
| **amqplib** (Node.js) | 0.10+ | Cliente RabbitMQ para Node.js |

## 4. Especificaciones Técnicas

### 4.1 AWS SQS - Tipos de Colas

| Tipo | Uso | Throughput | Ordering |
|------|-----|------------|----------|
| **Standard** | Alto throughput, orden best-effort | Ilimitado | No garantizado |
| **FIFO** | Orden exacto, exactamente-una-vez | 300-3000 msg/s | Garantizado |

### 4.2 Convenciones de Nomenclatura

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

## 5. Buenas Prácticas

### 5.1 Long Polling (SQS)

```csharp
// ✅ Usar long polling para reducir costos y latencia
var request = new ReceiveMessageRequest
{
    QueueUrl = queueUrl,
    WaitTimeSeconds = 20, // Long polling (máximo 20s)
    MaxNumberOfMessages = 10
};
```

### 5.2 Batch Processing

```csharp
// ✅ Procesar mensajes en batch para eficiencia
public async Task SendBatchAsync<T>(string queueUrl, IEnumerable<T> messages)
{
    var batches = messages.Chunk(10); // SQS: máximo 10 por batch

    foreach (var batch in batches)
    {
        var entries = batch.Select(msg => new SendMessageBatchRequestEntry
        {
            Id = Guid.NewGuid().ToString(),
            MessageBody = JsonSerializer.Serialize(msg)
        }).ToList();

        await _sqsClient.SendMessageBatchAsync(new SendMessageBatchRequest
        {
            QueueUrl = queueUrl,
            Entries = entries
        });
    }
}
```

### 5.3 Visibility Timeout Apropiado

```csharp
// ✅ Configurar visibility timeout > tiempo de procesamiento esperado
var request = new SetQueueAttributesRequest
{
    QueueUrl = queueUrl,
    Attributes = new Dictionary<string, string>
    {
        ["VisibilityTimeout"] = "300" // 5 minutos
    }
};
```

## 6. Antipatrones

### 6.1 ❌ Sin Dead Letter Queue

**Problema**:
```csharp
// ❌ Sin DLQ, mensajes fallidos se pierden o reintentan infinitamente
var consumer = new SqsConsumer(queueUrl);
```

**Solución**:
```csharp
// ✅ Configurar DLQ con maxReceiveCount
await ConfigureQueueWithDlqAsync(
    queueUrl,
    dlqArn,
    maxReceiveCount: 3); // Después de 3 intentos, va a DLQ
```

### 6.2 ❌ Visibility Timeout Muy Corto

**Problema**:
```csharp
// ❌ Visibility timeout de 30s, pero procesamiento toma 2 minutos
// Resultado: mensaje se vuelve visible antes de terminar, se procesa 2 veces
```

**Solución**:
```csharp
// ✅ Visibility timeout > tiempo de procesamiento + buffer
var visibilityTimeout = 180; // 3 minutos (2 min procesamiento + 1 min buffer)
```

### 6.3 ❌ Sin Idempotencia

**Problema**:
```csharp
// ❌ Procesa mensaje sin verificar duplicados
protected override async Task ProcessMessageAsync(EmailMessage message)
{
    await _emailService.SendAsync(message.To, message.Body);
    // Si SQS reintenta, envía email duplicado
}
```

**Solución**:
```csharp
// ✅ Verificar si ya se procesó
protected override async Task ProcessMessageAsync(EmailMessage message)
{
    if (await _processedMessagesRepo.ExistsAsync(message.MessageId))
        return;

    await _emailService.SendAsync(message.To, message.Body);
    await _processedMessagesRepo.MarkAsProcessedAsync(message.MessageId);
}
```

### 6.4 ❌ Sin Monitoreo de Queue Depth

**Problema**:
```csharp
// ❌ Cola crece indefinidamente sin alertas
// Resultado: latencia alta, pérdida de mensajes por retention period
```

**Solución**:
```csharp
// ✅ Monitorear métricas y alertar
public class QueueMetrics
{
    public async Task<QueueStats> GetStatsAsync(string queueUrl)
    {
        var attrs = await _sqsClient.GetQueueAttributesAsync(new GetQueueAttributesRequest
        {
            QueueUrl = queueUrl,
            AttributeNames = new List<string> 
            { 
                "ApproximateNumberOfMessages",
                "ApproximateAgeOfOldestMessage" 
            }
        });

        var queueDepth = int.Parse(attrs.Attributes["ApproximateNumberOfMessages"]);
        var oldestMessageAge = int.Parse(attrs.Attributes["ApproximateAgeOfOldestMessage"]);

        if (queueDepth > 10000)
            _logger.LogWarning("High queue depth: {QueueDepth}", queueDepth);

        return new QueueStats { Depth = queueDepth, OldestMessageAge = oldestMessageAge };
    }
}
```

## 7. Validación y Testing

### 7.1 Tests de Integración con LocalStack

```csharp
public class SqsIntegrationTests : IAsyncLifetime
{
    private LocalStackContainer _localStack = null!;
    private IAmazonSQS _sqsClient = null!;

    public async Task InitializeAsync()
    {
        _localStack = new LocalStackBuilder()
            .WithImage("localstack/localstack:3.0")
            .WithServices("sqs")
            .Build();

        await _localStack.StartAsync();

        _sqsClient = new AmazonSQSClient(new AmazonSQSConfig
        {
            ServiceURL = _localStack.GetConnectionString()
        });
    }

    [Fact]
    public async Task SendMessage_ConsumerReceives_ProcessesCorrectly()
    {
        // Arrange
        var queueUrl = await CreateQueueAsync("test-queue");
        var publisher = new SqsPublisher(_sqsClient);
        var message = new OrderMessage { OrderId = "123" };

        // Act
        await publisher.SendMessageAsync(queueUrl, message);

        var response = await _sqsClient.ReceiveMessageAsync(queueUrl);

        // Assert
        response.Messages.Should().HaveCount(1);
    }

    public async Task DisposeAsync() => await _localStack.DisposeAsync();
}
```

## 8. Referencias

### Lineamientos Relacionados
- [Comunicación Asíncrona y Eventos](/docs/fundamentos-corporativos/lineamientos/arquitectura/comunicacion-asincrona-y-eventos)
- [Resiliencia y Disponibilidad](/docs/fundamentos-corporativos/lineamientos/arquitectura/resiliencia-y-disponibilidad)

### Estándares Relacionados
- [Mensajería con Kafka](./01-kafka-eventos.md)
- [Logging Estructurado](../observabilidad/01-logging.md)

### ADRs Relacionados
- [ADR-012: Mensajería Asíncrona](/docs/decisiones-de-arquitectura/adr-012-mensajeria-asincrona)
- [ADR-015: Manejo de Errores y Cola](/docs/decisiones-de-arquitectura/adr-015-manejo-errores-cola)

### Recursos Externos
- [AWS SQS Best Practices](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html)
- [RabbitMQ Production Checklist](https://www.rabbitmq.com/production-checklist.html)

## 9. Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|  
| 1.0 | 2025-08-08 | Equipo de Arquitectura | Versión inicial con template de 9 secciones |
