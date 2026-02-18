---
id: graceful-shutdown
sidebar_position: 2
title: Graceful Shutdown
description: Shutdown graceful para terminar procesos sin perder requests o datos
---

# Graceful Shutdown

## Contexto

Este estándar define cómo implementar graceful shutdown para permitir que servicios terminen limpiamente sin perder requests en vuelo, transacciones activas o datos en proceso. Complementa el [lineamiento de Cloud Native](../../lineamientos/arquitectura/03-cloud-native.md) implementando el **factor IX (Disposability)** de 12-Factor App.

---

## Stack Tecnológico

| Componente        | Tecnología      | Versión | Uso                                  |
| ----------------- | --------------- | ------- | ------------------------------------ |
| **Framework**     | ASP.NET Core    | 8.0+    | Framework base con graceful shutdown |
| **Orchestration** | AWS ECS Fargate | -       | SIGTERM handling                     |
| **Load Balancer** | AWS ALB         | -       | Connection draining                  |

---

## Implementación Técnica

### Flujo de Graceful Shutdown

```yaml
# ✅ Secuencia de shutdown en ECS + ALB

1. ECS envía SIGTERM al container:
  - Orchestrator decide terminar task (deploy, scale down, health check fail)
  - SIGTERM señal a proceso principal (PID 1)

2. ALB inicia connection draining:
  - Target marcado como "draining"
  - ALB deja de enviar nuevos requests
  - Requests existentes continúan (hasta deregistration_delay)

3. Aplicación procesa SIGTERM:
  - Deja de aceptar nuevos requests (HTTP 503)
  - Completa requests en vuelo
  - Cierra conexiones a backing services (DB, cache, queues)
  - Flush logs/metrics pendientes

4. Aplicación termina gracefully:
  - Exit code 0 (success)
  - ECS task status: STOPPED

5. Timeout:
  - Si app no termina en 30s (stopTimeout), ECS envía SIGKILL
  - SIGKILL fuerza terminación inmediata (no graceful)

# ⏱️ Timeline ejemplo:
# T+0s:  ECS envía SIGTERM, ALB marca draining
# T+1s:  App deja de aceptar nuevos requests
# T+1-25s: App procesa requests en vuelo
# T+25s: App cierra conexiones
# T+25s: App flush logs/metrics
# T+26s: App termina (exit 0)
# T+30s: [Si no terminó] ECS envía SIGKILL
```

### IHostApplicationLifetime

```csharp
// ✅ Registrar callbacks para shutdown

public class GracefulShutdownService : IHostedService
{
    private readonly IHostApplicationLifetime _lifetime;
    private readonly ILogger<GracefulShutdownService> _logger;
    private readonly IDistributedCache _cache;
    private readonly OrdersDbContext _db;

    public GracefulShutdownService(
        IHostApplicationLifetime lifetime,
        ILogger<GracefulShutdownService> logger,
        IDistributedCache cache,
        OrdersDbContext db)
    {
        _lifetime = lifetime;
        _logger = logger;
        _cache = cache;
        _db = db;
    }

    public Task StartAsync(CancellationToken cancellationToken)
    {
        // ✅ Registrar callbacks
        _lifetime.ApplicationStarted.Register(OnStarted);
        _lifetime.ApplicationStopping.Register(OnStopping);
        _lifetime.ApplicationStopped.Register(OnStopped);

        return Task.CompletedTask;
    }

    private void OnStarted()
    {
        _logger.LogInformation("Application started");
    }

    private void OnStopping()
    {
        _logger.LogInformation(
            "Graceful shutdown initiated. Draining connections...");

        // ✅ SIGTERM recibido
        // Kestrel automáticamente deja de aceptar nuevos requests
        // Esperar que requests en vuelo completen
    }

    private void OnStopped()
    {
        _logger.LogInformation("Application stopped gracefully");
    }

    public async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("StopAsync called. Cleaning up resources...");

        try
        {
            // ✅ Flush cache writes pendientes
            // Redis client flush automático en Dispose

            // ✅ Completar transacciones DB pendientes
            await _db.SaveChangesAsync(cancellationToken);

            // ✅ Esperar un momento para requests en vuelo
            await Task.Delay(TimeSpan.FromSeconds(5), cancellationToken);

            _logger.LogInformation("Cleanup completed");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during shutdown cleanup");
        }
    }
}

// Program.cs
builder.Services.AddHostedService<GracefulShutdownService>();
```

### Kestrel Shutdown Timeout

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Configurar shutdown timeout
builder.WebHost.ConfigureKestrel(options =>
{
    // ✅ Tiempo máximo para completar requests en vuelo
    options.Limits.ShutdownTimeout = TimeSpan.FromSeconds(25);
});

// ✅ Configurar host shutdown timeout
builder.Host.ConfigureHostOptions(options =>
{
    // ✅ Tiempo total para shutdown (debe ser < ECS stopTimeout)
    options.ShutdownTimeout = TimeSpan.FromSeconds(30);
});

var app = builder.Build();
app.Run();
```

### Background Worker con Graceful Shutdown

```csharp
// ✅ Background service que respeta CancellationToken

public class OrderProcessorWorker : BackgroundService
{
    private readonly ILogger<OrderProcessorWorker> _logger;
    private readonly IServiceProvider _serviceProvider;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Order processor worker started");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessBatchAsync(stoppingToken);

                // ✅ Espera con soporte para cancellation
                await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
            }
            catch (OperationCanceledException)
            {
                // ✅ Shutdown iniciado, salir del loop
                _logger.LogInformation("Shutdown signal received. Exiting worker loop.");
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing orders");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }

        _logger.LogInformation("Order processor worker stopped");
    }

    private async Task ProcessBatchAsync(CancellationToken cancellationToken)
    {
        using var scope = _serviceProvider.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<OrdersDbContext>();

        var orders = await db.Orders
            .Where(o => o.Status == OrderStatus.Pending)
            .Take(100)
            .ToListAsync(cancellationToken);  // ✅ Propagar cancellation

        foreach (var order in orders)
        {
            // ✅ Verificar cancellation en cada iteración
            cancellationToken.ThrowIfCancellationRequested();

            await ProcessOrderAsync(order, cancellationToken);
        }
    }

    // ✅ Override StopAsync para cleanup adicional
    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Stopping order processor. Completing current batch...");

        // ✅ Base.StopAsync cancela el stoppingToken y espera ExecuteAsync
        await base.StopAsync(cancellationToken);

        _logger.LogInformation("Order processor stopped gracefully");
    }
}
```

### HTTP Client con Timeout para Shutdown

```csharp
// ✅ HttpClient que respeta shutdown token

public class PaymentService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<PaymentService> _logger;
    private readonly IHostApplicationLifetime _lifetime;

    public async Task<PaymentResult> ProcessPaymentAsync(
        PaymentRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // ✅ Combinar shutdown token con request token
            using var cts = CancellationTokenSource.CreateLinkedTokenSource(
                cancellationToken,
                _lifetime.ApplicationStopping);

            var response = await _httpClient.PostAsJsonAsync(
                "/api/payments",
                request,
                cts.Token);  // ✅ Cancelar si shutdown inicia

            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<PaymentResult>(cts.Token);
        }
        catch (OperationCanceledException) when (_lifetime.ApplicationStopping.IsCancellationRequested)
        {
            _logger.LogWarning(
                "Payment request cancelled due to application shutdown");
            throw;
        }
    }
}
```

### SQS Consumer con Visibility Timeout

```csharp
// ✅ SQS consumer que extiende visibility durante shutdown

public class SqsMessageProcessor : BackgroundService
{
    private readonly IAmazonSQS _sqsClient;
    private readonly string _queueUrl;
    private readonly ILogger<SqsMessageProcessor> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var response = await _sqsClient.ReceiveMessageAsync(
                    new ReceiveMessageRequest
                    {
                        QueueUrl = _queueUrl,
                        MaxNumberOfMessages = 10,
                        WaitTimeSeconds = 20,  // Long polling
                        VisibilityTimeout = 300  // 5 minutos
                    },
                    stoppingToken);

                foreach (var message in response.Messages)
                {
                    // ✅ Verificar shutdown antes de procesar cada mensaje
                    if (stoppingToken.IsCancellationRequested)
                    {
                        _logger.LogInformation(
                            "Shutdown initiated. Extending visibility timeout for {Count} messages",
                            response.Messages.Count - response.Messages.IndexOf(message));

                        // ✅ Extender visibility para que otro worker procese
                        await _sqsClient.ChangeMessageVisibilityAsync(
                            new ChangeMessageVisibilityRequest
                            {
                                QueueUrl = _queueUrl,
                                ReceiptHandle = message.ReceiptHandle,
                                VisibilityTimeout = 0  // Inmediatamente visible
                            });

                        break;
                    }

                    await ProcessMessageAsync(message, stoppingToken);

                    // ✅ Eliminar después de procesamiento exitoso
                    await _sqsClient.DeleteMessageAsync(
                        _queueUrl,
                        message.ReceiptHandle,
                        stoppingToken);
                }
            }
            catch (OperationCanceledException)
            {
                _logger.LogInformation("SQS consumer shutting down gracefully");
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing SQS messages");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }
}
```

### Kafka Consumer con Graceful Shutdown

```csharp
// ✅ Kafka consumer que cierra consumer group correctamente

public class KafkaOrderConsumer : BackgroundService
{
    private readonly IConsumer<string, OrderEvent> _consumer;
    private readonly ILogger<KafkaOrderConsumer> _logger;

    public KafkaOrderConsumer(IConfiguration config, ILogger<KafkaOrderConsumer> logger)
    {
        var consumerConfig = new ConsumerConfig
        {
            BootstrapServers = config["Kafka:BootstrapServers"],
            GroupId = "orders-processor",
            AutoOffsetReset = AutoOffsetReset.Earliest,
            EnableAutoCommit = false  // ✅ Manual commit para control fino
        };

        _consumer = new ConsumerBuilder<string, OrderEvent>(consumerConfig)
            .SetValueDeserializer(new JsonDeserializer<OrderEvent>())
            .Build();

        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("orders");

        _logger.LogInformation("Kafka consumer started");

        try
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    // ✅ Consumir con timeout corto para chequear cancellation
                    var consumeResult = _consumer.Consume(TimeSpan.FromSeconds(1));

                    if (consumeResult != null)
                    {
                        await ProcessOrderEventAsync(consumeResult.Message.Value, stoppingToken);

                        // ✅ Commit manual después de procesamiento exitoso
                        _consumer.Commit(consumeResult);
                    }
                }
                catch (ConsumeException ex)
                {
                    _logger.LogError(ex, "Error consuming Kafka message");
                }
            }
        }
        finally
        {
            // ✅ Graceful shutdown: cerrar consumer correctamente
            _logger.LogInformation("Closing Kafka consumer gracefully");

            _consumer.Close();  // ✅ Leave group y commit offsets
            _consumer.Dispose();

            _logger.LogInformation("Kafka consumer closed");
        }
    }
}
```

### ECS Task Definition - StopTimeout

```hcl
# Terraform - ECS Task Definition con stopTimeout

resource "aws_ecs_task_definition" "orders_api" {
  family                   = "orders-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([{
    name      = "orders-api"
    image     = "ghcr.io/talma/orders-api:latest"
    essential = true

    # ✅ StopTimeout: tiempo máximo antes de SIGKILL
    stopTimeout = 30  # 30 segundos para graceful shutdown

    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]

    environment = [
      { name = "ASPNETCORE_URLS", value = "http://+:8080" }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/orders-api"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}
```

### ALB Target Group - Deregistration Delay

```hcl
# ✅ Connection draining en ALB

resource "aws_lb_target_group" "orders_api" {
  name        = "orders-api-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  # ✅ Deregistration delay: tiempo para completar requests
  deregistration_delay = 30  # 30 segundos

  health_check {
    enabled             = true
    path                = "/health/ready"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

# Timeline con deregistration_delay:
# T+0s:  Target marcado "draining"
# T+0-30s: ALB sigue enviando requests activos al target
# T+30s: ALB deja de esperar, target removido completamente
```

### Dockerfile - Signal Handling

```dockerfile
# ✅ Asegurar que app recibe SIGTERM correctamente

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src
COPY ["OrdersApi/OrdersApi.csproj", "OrdersApi/"]
RUN dotnet restore "OrdersApi/OrdersApi.csproj"
COPY . .
WORKDIR "/src/OrdersApi"
RUN dotnet build "OrdersApi.csproj" -c Release -o /app/build
RUN dotnet publish "OrdersApi.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .

# ✅ ENTRYPOINT en forma exec (no shell)
# Forma exec: proceso es PID 1, recibe SIGTERM directamente
ENTRYPOINT ["dotnet", "OrdersApi.dll"]

# ❌ Forma shell: shell es PID 1, app no recibe SIGTERM
# ENTRYPOINT dotnet OrdersApi.dll  (anti-pattern)
```

### Métricas de Shutdown

```csharp
public class ShutdownMetrics
{
    private readonly Counter<long> _shutdownsTotal;
    private readonly Histogram<double> _shutdownDuration;
    private readonly Counter<long> _pendingRequestsOnShutdown;

    public ShutdownMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Shutdown");

        _shutdownsTotal = meter.CreateCounter<long>(
            "shutdown.total", "shutdowns");

        _shutdownDuration = meter.CreateHistogram<double>(
            "shutdown.duration", "seconds");

        _pendingRequestsOnShutdown = meter.CreateCounter<long>(
            "shutdown.pending_requests", "requests");
    }

    public void RecordShutdown(TimeSpan duration, int pendingRequests)
    {
        _shutdownsTotal.Add(1);
        _shutdownDuration.Record(duration.TotalSeconds);
        _pendingRequestsOnShutdown.Add(pendingRequests);
    }
}

// PromQL queries
/*
# Shutdown duration P95
histogram_quantile(0.95, sum(rate(shutdown_duration_bucket[1h])) by (le))

# Shutdowns con requests pendientes
shutdown_pending_requests_total

# Frecuencia de shutdowns
rate(shutdown_total[5m])
*/
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar graceful shutdown en todos los servicios
- **MUST** usar `IHostApplicationLifetime` para callbacks
- **MUST** propagar `CancellationToken` en operaciones asíncronas
- **MUST** configurar `ShutdownTimeout` apropiado (< 30s)
- **MUST** configurar `deregistration_delay` en ALB target groups
- **MUST** usar ENTRYPOINT exec form en Dockerfile
- **MUST** cerrar conexiones a backing services en shutdown
- **MUST** completar o extender visibility de mensajes SQS en proceso

### SHOULD (Fuertemente recomendado)

- **SHOULD** configurar `stopTimeout` en ECS task definitions
- **SHOULD** monitorear duration de shutdowns
- **SHOULD** cerrar Kafka consumers gracefully (commit offsets)
- **SHOULD** flush logs/metrics pendientes antes de terminar
- **SHOULD** esperar requests en vuelo (hasta timeout)
- **SHOULD** implementar timeout total de shutdown < 30s

### MAY (Opcional)

- **MAY** implementar pre-shutdown hooks para notificaciones
- **MAY** exponer métricas de requests pendientes en shutdown
- **MAY** usar health check para indicar readiness durante shutdown

### MUST NOT (Prohibido)

- **MUST NOT** ignorar señales de shutdown (SIGTERM)
- **MUST NOT** usar shell form en ENTRYPOINT (app no recibe SIGTERM)
- **MUST NOT** hacer blocking I/O sin CancellationToken
- **MUST NOT** configurar timeout muy largo (> 30s)
- **MUST NOT** perder mensajes en proceso durante shutdown
- **MUST NOT** dejar transacciones abiertas al terminar
- **MUST NOT** terminar con exit code != 0 en shutdown normal

---

## Referencias

- [Lineamiento: Cloud Native](../../lineamientos/arquitectura/03-cloud-native.md)
- [ADR-007: AWS ECS Fargate](../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- Estándares relacionados:
  - [12-Factor App](twelve-factor-app.md) - Factor IX: Disposability
  - [Health Checks](health-checks.md)
- Especificaciones:
  - [ASP.NET Core Graceful Shutdown](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/host/generic-host#ishostapplicationlifetime)
  - [ECS Task Lifecycle](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-lifecycle.html)
  - [ALB Connection Draining](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html#deregistration-delay)
