---
id: bulkhead-pattern
sidebar_position: 5
title: Bulkhead para Aislamiento de Recursos
description: Patrón Bulkhead para aislar recursos y prevenir cascading failures
---

# Bulkhead para Aislamiento de Recursos

## Contexto

Este estándar define cómo implementar el patrón Bulkhead para aislar recursos críticos y prevenir que fallas en un área afecten otras. Complementa el [lineamiento de Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md) especificando **cómo particionar recursos** para contener fallos.

---

## Stack Tecnológico

| Componente      | Tecnología         | Versión | Uso                          |
| --------------- | ------------------ | ------- | ---------------------------- |
| **Framework**   | ASP.NET Core       | 8.0+    | Framework base               |
| **Resilience**  | Polly              | 8.0+    | Rate limiter (bulkhead)      |
| **HTTP Client** | IHttpClientFactory | 8.0+    | HTTP client con partitioning |

---

## Implementación Técnica

### Concepto de Bulkhead

```yaml
# ✅ Bulkhead Pattern (inspirado en compartimentos de barcos)

Sin Bulkhead:
  [═══════════════════════════════]
  │ Thread Pool Compartido (100)  │
  │  - Critical API: 95 threads   │ ❌ Un servicio lento consume todo
  │  - Other APIs: 5 threads      │
  └───────────────────────────────┘

Con Bu lkhead:
  ┌─────────────┬─────────────┬─────────────┐
  │ Critical API│  Read APIs  │  Analytics  │
  │  (20 max)   │   (60 max)  │  (20 max)   │
  └─────────────┴─────────────┴─────────────┘
  ✅ Falla aislada, otros compartments operan normalmente
```

### Rate Limiter como Bulkhead (Concurrency Limiter)

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Bulkhead para servicio crítico
builder.Services
    .AddHttpClient("PaymentService")
    .AddResilienceHandler("payment-bulkhead", resilienceBuilder =>
    {
        // ✅ Limitar concurrencia máxima
        resilienceBuilder.AddConcurrencyLimiter(new ConcurrencyLimiterOptions
        {
            // ✅ Máximo 10 requests concurrentes a payment service
            PermitLimit = 10,

            // ✅ Queue hasta 20 requests adicionales
            QueueLimit = 20,

            // ✅ Callbacks para monitoreo
            OnRejected = args =>
            {
                _logger.LogWarning(
                    "Payment service concurrency limit exceeded. " +
                    "Request rejected.");

                _metrics.BulkheadRejected.Add(1,
                    new KeyValuePair<string, object?>("service", "payment"));

                return ValueTask.CompletedTask;
            }
        });
    });

// ✅ Bulkhead más permisivo para servicio no crítico
builder.Services
    .AddHttpClient("AnalyticsService")
    .AddResilienceHandler("analytics-bulkhead", resilienceBuilder =>
    {
        resilienceBuilder.AddConcurrencyLimiter(new ConcurrencyLimiterOptions
        {
            PermitLimit = 5,  // ✅ Solo 5 concurrent requests
            QueueLimit = 0   // ✅ Sin queue, fail-fast
        });
    });
```

### Thread Pool Partitioning

```csharp
// ✅ Dedicated thread pool para operaciones CPU-intensive
public class OrderProcessingService
{
    // Task Scheduler dedicado con thread limitados
    private readonly TaskScheduler _dedicatedScheduler;
    private readonly LimitedConcurrencyLevelTaskScheduler _scheduler;

    public OrderProcessingService()
    {
        // ✅ Bulkhead: máximo 5 threads para procesar orders
        _scheduler = new LimitedConcurrencyLevelTaskScheduler(5);
        _dedicatedScheduler = _scheduler;
    }

    public async Task ProcessOrderAsync(Order order)
    {
        // ✅ Ejecutar en thread pool dedicado
        await Task.Factory.StartNew(
            () => ProcessInternal(order),
            CancellationToken.None,
            TaskCreationOptions.DenyChildAttach,
            _dedicatedScheduler);
    }

    private void ProcessInternal(Order order)
    {
        // CPU-intensive work
        // Solo usa threads del bulkhead dedicado
    }
}

// Helper class
public class LimitedConcurrencyLevelTaskScheduler : TaskScheduler
{
    private readonly int _maxDegreeOfParallelism;
    private readonly LinkedList<Task> _tasks = new();
    private int _delegatesQueuedOrRunning = 0;

    public LimitedConcurrencyLevelTaskScheduler(int maxDegreeOfParallelism)
    {
        _maxDegreeOfParallelism = maxDegreeOfParallelism;
    }

    protected override void QueueTask(Task task)
    {
        lock (_tasks)
        {
            _tasks.AddLast(task);
            if (_delegatesQueuedOrRunning < _maxDegreeOfParallelism)
            {
                ++_delegatesQueuedOrRunning;
                NotifyThreadPoolOfPendingWork();
            }
        }
    }

    private void NotifyThreadPoolOfPendingWork()
    {
        ThreadPool.UnsafeQueueUserWorkItem(_ =>
        {
            try
            {
                while (true)
                {
                    Task item;
                    lock (_tasks)
                    {
                        if (_tasks.Count == 0)
                        {
                            --_delegatesQueuedOrRunning;
                            break;
                        }

                        item = _tasks.First!.Value;
                        _tasks.RemoveFirst();
                    }

                    TryExecuteTask(item);
                }
            }
            finally
            {
                // ...
            }
        }, null);
    }

    protected override bool TryExecuteTaskInline(Task task, bool taskWasPreviouslyQueued)
    {
        return false;  // Don't inline
    }

    protected override IEnumerable<Task> GetScheduledTasks()
    {
        lock (_tasks)
        {
            return _tasks.ToArray();
        }
    }

    public override int MaximumConcurrencyLevel => _maxDegreeOfParallelism;
}
```

### Database Connection

Pool Bulkhead

```csharp
// ✅ Diferentes connection pools por tipo de operación

// appsettings.json
{
  "ConnectionStrings": {
    // ✅ Pool para transactional writes
    "TransactionalConnection": "Host=db;Database=orders;Username=orders_api;Password=***;Maximum Pool Size=20;Minimum Pool Size=5;",

    // ✅ Pool para read queries
    "ReadOnlyConnection": "Host=db-replica;Database=orders;Username=orders_readonly;Password=***;Maximum Pool Size=50;Minimum Pool Size=10;",

    // ✅ Pool para analytics/reporting
    "AnalyticsConnection": "Host=db-replica;Database=orders;Username=orders_analytics;Password=***;Maximum Pool Size=10;Minimum Pool Size=2;"
  }
}

// Program.cs
builder.Services.AddDbContext<OrdersWriteDbContext>(options =>
{
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("TransactionalConnection"));
});

builder.Services.AddDbContext<OrdersReadDbContext>(options =>
{
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("ReadOnlyConnection"));
});

builder.Services.AddDbContext<OrdersAnalyticsDbContext>(options =>
{
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("AnalyticsConnection"));
});
```

### SemaphoreSlim como Bulkhead

```csharp
// ✅ Bulkhead manual con SemaphoreSlim
public class FileProcessingService
{
    // ✅ Limitar procesamiento concurrente de archivos
    private readonly SemaphoreSlim _semaphore = new(5, 5);  // Max 5 concurrent
    private readonly ILogger<FileProcessingService> _logger;

    public async Task<ProcessResult> ProcessFileAsync(Stream fileStream)
    {
        // ✅ Esperar por slot disponible
        if (!await _semaphore.WaitAsync(TimeSpan.FromSeconds(10)))
        {
            _logger.LogWarning(
                "File processing bulkhead exceeded. Request rejected.");
            throw new BulkheadRejectedException(
                "Too many concurrent file processing requests");
        }

        try
        {
            _logger.LogInformation(
                "Processing file. Current concurrency: {Count}",
                5 - _semaphore.CurrentCount);

            // ✅ Procesar archivo dentro del bulkhead
            return await ProcessFileInternalAsync(fileStream);
        }
        finally
        {
            // ✅ Liberar slot
            _semaphore.Release();
        }
    }
}
```

### Background Job Bulkhead

```csharp
// ✅ Procesadores paralelos con límite
public class OrderBackgroundProcessor : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly SemaphoreSlim _concurrencyLimiter = new(10, 10);  // Max 10 concurrent

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var tasks = new List<Task>();

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                // ✅ Fetch batch de orders
                var orders = await FetchPendingOrdersAsync(20, stoppingToken);

                foreach (var order in orders)
                {
                    await _concurrencyLimiter.WaitAsync(stoppingToken);

                    // ✅ Procesar en paralelo (máximo 10 concurrent)
                    var task = Task.Run(async () =>
                    {
                        try
                        {
                            await ProcessOrderAsync(order, stoppingToken);
                        }
                        finally
                        {
                            _concurrencyLimiter.Release();
                        }
                    }, stoppingToken);

                    tasks.Add(task);
                }

                // ✅ Espera batch completo
                await Task.WhenAll(tasks);
                tasks.Clear();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in order background processor");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }
}
```

### ECS Task Bulkhead (Infrastructure Level)

```hcl
# Terraform - ECS Services con resource limits

# ✅ Critical service: más recursos
resource "aws_ecs_task_definition" "orders_api" {
  family                   = "orders-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"  # 1 vCPU dedicado
  memory                   = "2048"  # 2 GB RAM

  container_definitions = jsonencode([{
    name      = "orders-api"
    image     = "ghcr.io/talma/orders-api:latest"
    essential = true

    # ✅ Resource limits (hard limits)
    memory = 2048
    cpu    = 1024
  }])
}

# ✅ Non-critical service: menos recursos
resource "aws_ecs_task_definition" "analytics_api" {
  family                   = "analytics-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"   # 0.25 vCPU
  memory                   = "512"   # 0.5 GB RAM

  container_definitions = jsonencode([{
    name      = "analytics-api"
    image     = "ghcr.io/talma/analytics-api:latest"
    essential = true

    memory = 512
    cpu    = 256
  }])
}
```

### Métricas de Bulkhead

```csharp
public class BulkheadMetrics
{
    private readonly Counter<long> _bulkheadRejected;
    private readonly Histogram<double> _queueWaitTime;
    private readonly Gauge<int> _concurrentExecutions;

    public BulkheadMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Resilience.Bulkhead");

        _bulkheadRejected = meter.CreateCounter<long>(
            "bulkhead.rejected", "requests");
        _queueWaitTime = meter.CreateHistogram<double>(
            "bulkhead.queue_wait_time", "ms");
        _concurrentExecutions = meter.CreateGauge<int>(
            "bulkhead.concurrent_executions", "executions");
    }

    public void RecordRejected(string bulkhead)
    {
        _bulkheadRejected.Add(1,
            new KeyValuePair<string, object?>("bulkhead", bulkhead));
    }

    public void RecordQueueWaitTime(string bulkhead, TimeSpan waitTime)
    {
        _queueWaitTime.Record(
            waitTime.TotalMilliseconds,
            new KeyValuePair<string, object?>("bulkhead", bulkhead));
    }

    public void RecordConcurrency(string bulkhead, int count)
    {
        _concurrentExecutions.Record(count,
            new KeyValuePair<string, object?>("bulkhead", bulkhead));
    }
}

// PromQL queries
/*
# Rejection rate
rate(bulkhead_rejected_total[5m])

# Queue wait time P95
histogram_quantile(0.95, sum(rate(bulkhead_queue_wait_time_bucket[5m])) by (le, bulkhead))

# Current concurrency utilization
bulkhead_concurrent_executions / bulkhead_limit * 100
*/
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar bulkheads para servicios críticos
- **MUST** configurar límites de concurrencia apropiados
- **MUST** separar connection pools por tipo de operación (write/read)
- **MUST** monitorear rejection rate de bulkheads
- **MUST** documentar límites de cada bulkhead
- **MUST** configurar alarmas cuando bulkhead está saturado
- **MUST** usar resource limits en ECS tasks

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar diferentes bulkheads por criticidad de servicio
- **SHOULD** implementar queuing para absorber spikes
- **SHOULD** usar thread pool partitioning para CPU-intensive work
- **SHOULD** monitorear utilización de cada bulkhead
- **SHOULD** ajustar límites basado en capacity testing
- **SHOULD** combinar bulkhead con circuit breaker

### MAY (Opcional)

- **MAY** implementar bulkheads dinámicos basados en load
- **MAY** usar priorización en queues de bulkheads
- **MAY** implementar bulkheads por tenant (multi-tenancy)
- **MAY** ajustar bulkhead sizes automáticamente

### MUST NOT (Prohibido)

- **MUST NOT** compartir resources sin límites entre servicios
- **MUST NOT** configurar bulkheads sin monitoreo
- **MUST NOT** ignorar rejection events de bulkhead
- **MUST NOT** usar bulkheads infinitos (sin límite)
- **MUST NOT** bloquear threads indefinidamente esperando bulkhead
- **MUST NOT** configurar límites muy bajos sin justificación

---

## Referencias

- [Lineamiento: Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md)
- Estándares relacionados:
  - [Circuit Breaker](circuit-breaker.md)
  - [Rate Limiting](rate-limiting.md)
  - [Connection Pooling](../../estandares/datos/connection-pooling.md)
- Especificaciones:
  - [Release It! - Bulkheads](https://pragprog.com/titles/mnee2/release-it-second-edition/)
  - [Polly Rate Limiter](https://www.pollydocs.org/strategies/rate-limiter)
  - [Bulkhead Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead)
