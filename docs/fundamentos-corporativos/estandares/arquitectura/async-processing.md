---
id: async-processing
sidebar_position: 3
title: Procesamiento Asíncrono
description: Patrones para procesamiento asíncrono con colas y eventos
---

# Procesamiento Asíncrono

## Contexto

Este estándar define cómo implementar procesamiento asíncrono para operaciones de larga duración, mejorar throughput y desacoplar servicios. Complementa el [lineamiento de Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md) especificando **cuándo y cómo usar async processing** para optimizar experiencia de usuario y utilización de recursos.

---

## Stack Tecnológico

| Componente     | Tecnología      | Versión | Uso                     |
| -------------- | --------------- | ------- | ----------------------- |
| **Queue**      | Amazon SQS      | -       | Colas de mensajes       |
| **Streaming**  | Apache Kafka    | 3.6+    | Event streaming         |
| **Framework**  | ASP.NET Core    | 8.0+    | Processing services     |
| **Background** | IHostedService  | 8.0+    | Background workers      |
| **Client**     | AWSSDK.SQS      | 3.7+    | Cliente SQS para .NET   |
| **Client**     | Confluent.Kafka | 2.3+    | Cliente Kafka para .NET |

---

## Implementación Técnica

### Cuándo Usar Procesamiento Asíncrono

```csharp
// ❌ MAL: Operaciones lentas en request síncrono
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(CreateOrderRequest request)
{
    // ❌ Todo en request HTTP (puede timeout)
    var order = await _orderService.CreateAsync(request);
    await _inventoryService.ReserveStockAsync(order);      // 500ms
    await _paymentService.ProcessPaymentAsync(order);      // 2000ms
    await _shippingService.CreateShipmentAsync(order);     // 300ms
    await _notificationService.SendEmailAsync(order);      // 800ms

    // Total: ~3.6 segundos! ❌
    return Ok(order);
}

// ✅ BIEN: Request rápido + procesamiento asíncrono
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(CreateOrderRequest request)
{
    // ✅ Solo persistir orden (< 50ms)
    var order = await _orderService.CreateAsync(request);

    // ✅ Publicar evento para procesamiento asíncrono
    await _eventPublisher.PublishAsync(new OrderCreatedEvent
    {
        OrderId = order.Id,
        Timestamp = DateTime.UtcNow
    });

    // ✅ Retornar inmediatamente (< 100ms total)
    return Accepted(new
    {
        orderId = order.Id,
        status = "processing",
        statusUrl = $"/orders/{order.Id}/status"
    });
}

// ✅ Procesamiento en background worker
public class OrderProcessingWorker : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await foreach (var evt in _consumer.ConsumeAsync<OrderCreatedEvent>(stoppingToken))
        {
            try
            {
                // Procesar sin presión de tiempo del request HTTP
                await _inventoryService.ReserveStockAsync(evt.OrderId);
                await _paymentService.ProcessPaymentAsync(evt.OrderId);
                await _shippingService.CreateShipmentAsync(evt.OrderId);
                await _notificationService.SendEmailAsync(evt.OrderId);

                await evt.CommitAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to process order {OrderId}", evt.OrderId);
                // Retry o DLQ handled by consumer
            }
        }
    }
}
```

### Implementación con Amazon SQS

```csharp
// Producer: Encolar mensaje
public class OrderQueue
{
    private readonly IAmazonSQS _sqsClient;
    private readonly string _queueUrl;

    public async Task EnqueueOrderAsync(OrderCreatedEvent evt)
    {
        var message = new SendMessageRequest
        {
            QueueUrl = _queueUrl,
            MessageBody = JsonSerializer.Serialize(evt),
            MessageAttributes = new Dictionary<string, MessageAttributeValue>
            {
                ["OrderId"] = new MessageAttributeValue
                {
                    DataType = "String",
                    StringValue = evt.OrderId
                },
                ["Timestamp"] = new MessageAttributeValue
                {
                    DataType = "Number",
                    StringValue = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString()
                }
            },
            // ✅ Delay opcional (0-900 segundos)
            DelaySeconds = 0
        };

        await _sqsClient.SendMessageAsync(message);
    }

    public async Task EnqueueBatchAsync(IEnumerable<OrderCreatedEvent> events)
    {
        // ✅ Batch para mejor throughput (hasta 10 mensajes)
        var entries = events.Select((evt, idx) => new SendMessageBatchRequestEntry
        {
            Id = idx.ToString(),
            MessageBody = JsonSerializer.Serialize(evt)
        }).ToList();

        foreach (var batch in entries.Chunk(10))
        {
            await _sqsClient.SendMessageBatchAsync(new SendMessageBatchRequest
            {
                QueueUrl = _queueUrl,
                Entries = batch.ToList()
            });
        }
    }
}

// Consumer: Procesar mensajes
public class OrderProcessingWorker : BackgroundService
{
    private readonly IAmazonSQS _sqsClient;
    private readonly string _queueUrl;
    private readonly IServiceProvider _serviceProvider;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                // ✅ Long polling (WaitTimeSeconds = 20)
                var request = new ReceiveMessageRequest
                {
                    QueueUrl = _queueUrl,
                    MaxNumberOfMessages = 10,
                    WaitTimeSeconds = 20,  // Long polling (reduce empty responses)
                    VisibilityTimeout = 300,  // 5 minutos para procesar
                    MessageAttributeNames = new List<string> { "All" }
                };

                var response = await _sqsClient.ReceiveMessageAsync(request, stoppingToken);

                if (!response.Messages.Any())
                    continue;

                // ✅ Procesar mensajes en paralelo
                await Parallel.ForEachAsync(
                    response.Messages,
                    new ParallelOptions
                    {
                        MaxDegreeOfParallelism = 5,
                        CancellationToken = stoppingToken
                    },
                    async (message, ct) =>
                    {
                        await ProcessMessageAsync(message, ct);
                    });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error polling SQS queue");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }

    private async Task ProcessMessageAsync(Message message, CancellationToken ct)
    {
        using var scope = _serviceProvider.CreateScope();
        var orderService = scope.ServiceProvider.GetRequiredService<IOrderService>();

        try
        {
            var evt = JsonSerializer.Deserialize<OrderCreatedEvent>(message.Body);

            // ✅ Procesar orden
            await orderService.ProcessAsync(evt.OrderId);

            // ✅ Eliminar mensaje (acknowledge)
            await _sqsClient.DeleteMessageAsync(_queueUrl, message.ReceiptHandle, ct);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process message {MessageId}", message.MessageId);

            // ✅ No eliminar mensaje: volverá a estar visible después del VisibilityTimeout
            // Después de 3 reintentos (configurado en SQS), irá a DLQ automáticamente
        }
    }
}
```

### Configuración de SQS con DLQ (Terraform)

```hcl
# Main queue
resource "aws_sqs_queue" "orders_processing" {
  name                       = "tlm-orders-processing"
  delay_seconds              = 0
  max_message_size           = 262144  # 256 KB
  message_retention_seconds  = 1209600  # 14 días
  receive_wait_time_seconds  = 20  # Long polling
  visibility_timeout_seconds = 300  # 5 minutos

  # ✅ Dead Letter Queue después de 3 reintentos
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.orders_processing_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Environment = "production"
    Service     = "orders"
  }
}

# Dead Letter Queue
resource "aws_sqs_queue" "orders_processing_dlq" {
  name                      = "tlm-orders-processing-dlq"
  message_retention_seconds = 1209600  # 14 días (tiempo para investigar)

  tags = {
    Environment = "production"
    Service     = "orders"
  }
}

# Alarma de DLQ
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "orders-processing-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Average"
  threshold           = 0
  alarm_description   = "Messages in DLQ require investigation"

  dimensions = {
    QueueName = aws_sqs_queue.orders_processing_dlq.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}
```

### Implementación con Kafka

```csharp
// Producer
public class OrderEventProducer
{
    private readonly IProducer<string, string> _producer;
    private readonly string _topic = "orders.events";

    public OrderEventProducer(IConfiguration config)
    {
        var producerConfig = new ProducerConfig
        {
            BootstrapServers = config["Kafka:BootstrapServers"],
            ClientId = "orders-api",
            EnableIdempotence = true,  // ✅ Exactamente-una-vez
            Acks = Acks.All,  // ✅ Esperar confirmación de todos los replicas
            MaxInFlight = 5,
            CompressionType = CompressionType.Snappy
        };

        _producer = new ProducerBuilder<string, string>(producerConfig).Build();
    }

    public async Task PublishAsync(OrderCreatedEvent evt)
    {
        var message = new Message<string, string>
        {
            Key = evt.OrderId,  // ✅ Key para partitioning
            Value = JsonSerializer.Serialize(evt),
            Headers = new Headers
            {
                { "event-type", Encoding.UTF8.GetBytes("OrderCreated") },
                { "correlation-id", Encoding.UTF8.GetBytes(evt.CorrelationId) }
            },
            Timestamp = new Timestamp(DateTime.UtcNow)
        };

        var result = await _producer.ProduceAsync(_topic, message);

        _logger.LogInformation(
            "Published event to Kafka: Topic={Topic}, Partition={Partition}, Offset={Offset}",
            result.Topic, result.Partition.Value, result.Offset.Value);
    }
}

// Consumer
public class OrderEventConsumer : BackgroundService
{
    private readonly IConsumer<string, string> _consumer;
    private readonly IServiceProvider _serviceProvider;
    private readonly string _topic = "orders.events";

    public OrderEventConsumer(IConfiguration config, IServiceProvider serviceProvider)
    {
        var consumerConfig = new ConsumerConfig
        {
            BootstrapServers = config["Kafka:BootstrapServers"],
            GroupId = "orders-processing-group",
            AutoOffsetReset = AutoOffsetReset.Earliest,
            EnableAutoCommit = false,  // ✅ Manual commit después de procesar
            MaxPollIntervalMs = 300000,  // 5 minutos
            SessionTimeoutMs = 45000
        };

        _consumer = new ConsumerBuilder<string, string>(consumerConfig).Build();
        _serviceProvider = serviceProvider;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe(_topic);

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var consumeResult = _consumer.Consume(stoppingToken);

                using var scope = _serviceProvider.CreateScope();
                var orderService = scope.ServiceProvider.GetRequiredService<IOrderService>();

                var evt = JsonSerializer.Deserialize<OrderCreatedEvent>(consumeResult.Message.Value);

                // ✅ Procesar evento
                await orderService.ProcessAsync(evt.OrderId);

                // ✅ Commit offset solo después de procesar exitosamente
                _consumer.Commit(consumeResult);

                _logger.LogInformation(
                    "Processed event: Partition={Partition}, Offset={Offset}",
                    consumeResult.Partition.Value, consumeResult.Offset.Value);
            }
            catch (ConsumeException ex)
            {
                _logger.LogError(ex, "Error consuming from Kafka");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing event");
                // ✅ No commit: mensaje será re-procesado
            }
        }

        _consumer.Close();
    }
}
```

### Polling Status Pattern

```csharp
// ✅ Cliente puede hacer polling del estado
[HttpGet("orders/{orderId}/status")]
public async Task<IActionResult> GetOrderStatus(string orderId)
{
    var order = await _orderRepository.GetByIdAsync(orderId);
    if (order == null)
        return NotFound();

    return Ok(new
    {
        orderId = order.Id,
        status = order.Status,  // pending, processing, completed, failed
        progress = new
        {
            inventoryReserved = order.InventoryReserved,
            paymentProcessed = order.PaymentProcessed,
            shipmentCreated = order.ShipmentCreated,
            emailSent = order.EmailSent
        },
        completedAt = order.CompletedAt,
        estimatedCompletionTime = order.Status == "processing"
            ? DateTime.UtcNow.AddMinutes(2)
            : null
    });
}
```

### Webhook Pattern

```csharp
// ✅ Notificar cliente cuando complete
public class OrderCompletedHandler : INotificationHandler<OrderCompletedEvent>
{
    private readonly IHttpClientFactory _httpClientFactory;

    public async Task Handle(OrderCompletedEvent evt, CancellationToken ct)
    {
        if (string.IsNullOrEmpty(evt.WebhookUrl))
            return;

        var client = _httpClientFactory.CreateClient();

        var payload = new
        {
            eventType = "order.completed",
            orderId = evt.OrderId,
            timestamp = DateTime.UtcNow
        };

        // ✅ Webhook con retry
        var policy = Policy
            .HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
            .WaitAndRetryAsync(3, retryAttempt =>
                TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));

        await policy.ExecuteAsync(async () =>
        {
            return await client.PostAsJsonAsync(evt.WebhookUrl, payload, ct);
        });
    }
}
```

### Métricas de Procesamiento Asíncrono

```csharp
public class AsyncProcessingMetrics
{
    private readonly Counter<long> _messagesProcessed;
    private readonly Counter<long> _messagesFailed;
    private readonly Histogram<double> _processingDuration;
    private readonly UpDownCounter<long> _queueDepth;

    public AsyncProcessingMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Orders.AsyncProcessing");

        _messagesProcessed = meter.CreateCounter<long>(
            "async.messages.processed", "messages");
        _messagesFailed = meter.CreateCounter<long>(
            "async.messages.failed", "messages");
        _processingDuration = meter.CreateHistogram<double>(
            "async.processing.duration", "ms");
        _queueDepth = meter.CreateUpDownCounter<long>(
            "async.queue.depth", "messages");
    }

    public void RecordProcessed(string messageType, TimeSpan duration)
    {
        _messagesProcessed.Add(1, new KeyValuePair<string, object?>("type", messageType));
        _processingDuration.Record(duration.TotalMilliseconds,
            new KeyValuePair<string, object?>("type", messageType));
    }
}

// PromQL queries
/*
# Processing rate
rate(async_messages_processed_total[5m])

# Error rate
rate(async_messages_failed_total[5m]) /
rate(async_messages_processed_total[5m]) * 100

# Processing latency P95
histogram_quantile(0.95, sum(rate(async_processing_duration_bucket[5m])) by (le))

# Queue depth (SQS metric)
aws_sqs_approximate_number_of_messages_visible{queue_name="tlm-orders-processing"}
*/
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar async processing para operaciones > 1 segundo
- **MUST** retornar 202 Accepted con statusUrl para long-running operations
- **MUST** configurar Dead Letter Queue (DLQ) para mensajes fallidos
- **MUST** implementar idempotencia en consumers
- **MUST** usar manual commit en Kafka (después de procesar)
- **MUST** configurar visibility timeout apropiado en SQS
- **MUST** instrumentar métricas (processing rate, latency, errors)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar long polling en SQS (WaitTimeSeconds = 20)
- **SHOULD** procesar mensajes en batch cuando sea posible
- **SHOULD** configurar alarmas en DLQ
- **SHOULD** implementar circuit breaker para dependencias externas
- **SHOULD** usar SQS para queues simples, Kafka para event streaming
- **SHOULD** escalar consumers basado en queue depth
- **SHOULD** implementar graceful shutdown (drain messages)

### MAY (Opcional)

- **MAY** implementar webhooks para notificar completión
- **MAY** usar FIFO queues cuando orden sea crítico
- **MAY** implementar priority queues
- **MAY** usar delay queues para retry con backoff
- **MAY** implementar saga pattern para transacciones distribuidas

### MUST NOT (Prohibido)

- **MUST NOT** procesar operaciones > 1s síncronamente en HTTP request
- **MUST NOT** auto-commit en Kafka sin procesar mensaje
- **MUST NOT** ignorar mensajes en DLQ (requieren investigación)
- **MUST NOT** asumir orden de procesamiento sin FIFO queue
- **MUST NOT** procesar mismo mensaje múltiples veces (no idempotente)
- **MUST NOT** usar polling sin long polling (desperdicia requests)

---

## Referencias

- [Lineamiento: Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md)
- Estándares relacionados:
  - [Idempotencia](../../estandares/mensajeria/idempotency.md)
  - [Dead Letter Queue](../../estandares/mensajeria/dead-letter-queue.md)
- ADRs:
  - [ADR-012: Kafka Mensajería](../../../decisiones-de-arquitectura/adr-012-kafka-mensajeria-asincrona.md)
- Especificaciones:
  - [AWS SQS Best Practices](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-best-practices.html)
  - [Kafka Consumer Configuration](https://kafka.apache.org/documentation/#consumerconfigs)
