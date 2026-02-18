---
id: timeout-patterns
sidebar_position: 2
title: Timeouts en Llamadas Remotas
description: Configuración de timeouts apropiados para evitar bloqueos indefinidos
---

# Timeouts en Llamadas Remotas

## Contexto

Este estándar define cómo configurar timeouts apropiados en llamadas remotas para evitar thread starvation y cascading failures. Complementa el [lineamiento de Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md) especificando **cuánto tiempo esperar** antes de considerar una operación fallida.

---

## Stack Tecnológico

| Componente      | Tecnología         | Versión | Uso                     |
| --------------- | ------------------ | ------- | ----------------------- |
| **Framework**   | ASP.NET Core       | 8.0+    | Framework base          |
| **Resilience**  | Polly              | 8.0+    | Timeout políticas       |
| **HTTP Client** | IHttpClientFactory | 8.0+    | HTTP client con timeout |

---

## Implementación Técnica

### Tipos de Timeouts

```yaml
# ✅ Timeouts en diferentes capas

1. Client Timeout (HttpClient.Timeout)
   - Timeout total del request (incluye DNS, connection, response)
   - Default: 100 segundos (muy alto!)
   - Recomendado: 10-30 segundos

2. Polly Timeout
   - Timeout granular por operación
   - Cancela operation con CancellationToken
   - Recomendado: 5-10 segundos

3. Connection Timeout (SocketsHttpHandler.ConnectTimeout)
   - Timeout para establecer TCP connection
   - Default: infinito
   - Recomendado: 5 segundos

4. Database Timeout (CommandTimeout)
   - Timeout de query SQL
   - Default: 30 segundos
   - Recomendado: 5-30 segundos según query
```

### Configuración de HttpClient Timeout

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ❌ MAL: HttpClient sin timeout configurado
builder.Services.AddHttpClient("OrdersService", client =>
{
    client.BaseAddress = new Uri("https://orders-api.talma.com");
    // ❌ Usa default de 100 segundos!
});

// ✅ BIEN: HttpClient con timeout explícito
builder.Services.AddHttpClient("OrdersService", client =>
{
    client.BaseAddress = new Uri("https://orders-api.talma.com");
    client.Timeout = TimeSpan.FromSeconds(30);  // ✅ Timeout total del request
})
.ConfigurePrimaryHttpMessageHandler(() =>
{
    return new SocketsHttpHandler
    {
        // ✅ Connection timeout específico
        ConnectTimeout = TimeSpan.FromSeconds(5),

        // ✅ Pooled connections timeout
        PooledConnectionLifetime = TimeSpan.FromMinutes(2),

        // ✅ Idle connection timeout
        PooledConnectionIdleTimeout = TimeSpan.FromMinutes(1)
    };
});
```

### Timeout con Polly

```csharp
// ✅ Polly Timeout combinado con Circuit Breaker
builder.Services
    .AddHttpClient("PaymentService")
    .AddResilienceHandler("payment-resilience", resilienceBuilder =>
    {
        // ✅ Timeout ANTES de retry (orden importa)
        resilienceBuilder.AddTimeout(new TimeoutStrategyOptions
        {
            Timeout = TimeSpan.FromSeconds(10),

            // ✅ Callbacks para logging
            OnTimeout = args =>
            {
                _logger.LogWarning(
                    "Payment service request timed out after {Timeout}ms",
                    args.Timeout.TotalMilliseconds);

                _metrics.Timeouts.Add(1,
                    new KeyValuePair<string, object?>("service", "payment"));

                return ValueTask.CompletedTask;
            }
        });

        // ✅ Retry (después de timeout)
        resilienceBuilder.AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(1),
            BackoffType = DelayBackoffType.Exponential
        });

        // ✅ Circuit Breaker (al final)
        resilienceBuilder.AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            SamplingDuration = TimeSpan.FromSeconds(30),
            MinimumThroughput = 10,
            BreakDuration = TimeSpan.FromSeconds(30)
        });
    });
```

### Timeouts Diferenciados por Endpoint

```csharp
public class OrdersService : IOrdersService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ResiliencePipelineProvider<string> _pipelineProvider;

    // ✅ Query rápido (5 segundos)
    public async Task<Order> GetOrderAsync(string orderId)
    {
        var pipeline = _pipelineProvider.GetPipeline("orders-query");

        return await pipeline.ExecuteAsync(async ct =>
        {
            var client = _httpClientFactory.CreateClient("OrdersService");
            var response = await client.GetAsync($"/orders/{orderId}", ct);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<Order>(ct);
        });
    }

    // ✅ Command (write) con timeout más largo (15 segundos)
    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        var pipeline = _pipelineProvider.GetPipeline("orders-command");

        return await pipeline.ExecuteAsync(async ct =>
        {
            var client = _httpClientFactory.CreateClient("OrdersService");
            var response = await client.PostAsJsonAsync("/orders", request, ct);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<Order>(ct);
        });
    }
}

// Program.cs - Diferentes pipelines
builder.Services.AddResiliencePipeline("orders-query", pipelineBuilder =>
{
    pipelineBuilder.AddTimeout(TimeSpan.FromSeconds(5));  // ✅ Query rápido
});

builder.Services.AddResiliencePipeline("orders-command", pipelineBuilder =>
{
    pipelineBuilder.AddTimeout(TimeSpan.FromSeconds(15));  // ✅ Write más lento
});
```

### Database Timeouts

```csharp
// ✅ Command timeout en Entity Framework Core
public class OrdersDbContext : DbContext
{
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.UseNpgsql(connectionString, npgsqlOptions =>
        {
            // ✅ Command timeout default para todas las queries
            npgsqlOptions.CommandTimeout(30);  // 30 segundos
        });
    }
}

// ✅ Override timeout para query específico
public async Task<List<Order>> GetAllOrdersAsync()
{
    // ✅ Query pesado con timeout extendido
    _context.Database.SetCommandTimeout(60);  // 60 segundos solo para esta query

    return await _context.Orders
        .Include(o => o.Items)
        .ThenInclude(i => i.Product)
        .ToListAsync();
}

// ✅ Timeout con raw SQL
public async Task<List<OrderStatistics>> GetStatisticsAsync(DateTime from, DateTime to)
{
    var command = _context.Database.GetDbConnection().CreateCommand();
    command.CommandText = "SELECT ...";
    command.CommandTimeout = 45;  // ✅ 45 segundos

    await _context.Database.OpenConnectionAsync();

    using var reader = await command.ExecuteReaderAsync();
    // ... procesar resultados
}
```

### Timeout Propagation (CancellationToken)

```csharp
// ✅ BIEN: Propagar CancellationToken
[HttpGet("orders/{id}")]
public async Task<IActionResult> GetOrder(string id, CancellationToken ct)
{
    try
    {
        // ✅ ct se propaga automáticamente a través de toda la cadena
        var order = await _orderService.GetOrderAsync(id, ct);
        return Ok(order);
    }
    catch (OperationCanceledException)
    {
        // ✅ Request cancelado (timeout o usuario cancelo)
        return StatusCode(499);  // Client Closed Request
    }
}

public class OrderService : IOrderService
{
    public async Task<Order> GetOrderAsync(string orderId, CancellationToken ct)
    {
        // ✅ Propagar a DB
        var order = await _context.Orders.FindAsync(new[] { orderId }, ct);

        if (order == null)
            return null;

        // ✅ Propagar a HTTP client
        var inventory = await GetInventoryAsync(order.ProductId, ct);

        order.StockLevel = inventory.Available;
        return order;
    }

    private async Task<Inventory> GetInventoryAsync(string productId, CancellationToken ct)
    {
        var client = _httpClientFactory.CreateClient("InventoryService");

        // ✅ CancellationToken se propaga
        var response = await client.GetAsync($"/inventory/{productId}", ct);

        return await response.Content.ReadFromJsonAsync<Inventory>(ct);
    }
}
```

### Timeout en Background Jobs

```csharp
public class OrderProcessingWorker : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var orders = await FetchOrdersAsync(stoppingToken);

                foreach (var order in orders)
                {
                    // ✅ Timeout per-order (no bloquear todo el loop)
                    using var cts = CancellationTokenSource.CreateLinkedTokenSource(stoppingToken);
                    cts.CancelAfter(TimeSpan.FromMinutes(5));  // ✅ Max 5 min por order

                    try
                    {
                        await ProcessOrderAsync(order, cts.Token);
                    }
                    catch (OperationCanceledException) when (cts.IsCancellationRequested)
                    {
                        _logger.LogWarning(
                            "Processing order {OrderId} timed out after 5 minutes",
                            order.Id);

                        // ✅ Mover a DLQ o retry queue
                        await MoveToRetryQueueAsync(order);
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in order processing worker");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }
}
```

### Timeout Defensivo en Controllers

```csharp
// ✅ Timeout defensivo en API controller
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(
    [FromBody] CreateOrderRequest request,
    CancellationToken ct)
{
    // ✅ Timeout de 30 segundos incluso si cliente no cancela
    using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
    cts.CancelAfter(TimeSpan.FromSeconds(30));

    try
    {
        var order = await _orderService.CreateOrderAsync(request, cts.Token);
        return Created($"/orders/{order.Id}", order);
    }
    catch (OperationCanceledException)
    {
        if (ct.IsCancellationRequested)
        {
            // ✅ Cliente canceló request
            _logger.LogInformation("Client cancelled order creation request");
            return StatusCode(499);
        }
        else
        {
            // ✅ Timeout interno
            _logger.LogWarning("Order creation timed out after 30 seconds");
            return StatusCode(504, new { error = "Request timed out" });
        }
    }
}
```

### Métricas de Timeout

```csharp
public class TimeoutMetrics
{
    private readonly Counter<long> _timeouts;
    private readonly Histogram<double> _operationDuration;

    public TimeoutMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Resilience.Timeout");

        _timeouts = meter.CreateCounter<long>(
            "operation.timeouts", "timeouts");
        _operationDuration = meter.CreateHistogram<double>(
            "operation.duration", "ms");
    }

    public void RecordTimeout(string operation)
    {
        _timeouts.Add(1, new KeyValuePair<string, object?>("operation", operation));
    }

    public void RecordDuration(string operation, TimeSpan duration)
    {
        _operationDuration.Record(
            duration.TotalMilliseconds,
            new KeyValuePair<string, object?>("operation", operation));
    }
}

// PromQL queries
/*
# Timeout rate
rate(operation_timeouts_total[5m])

# Operations close to timeout (P99 > 80% of timeout)
histogram_quantile(0.99, sum(rate(operation_duration_bucket[5m])) by (le, operation))
*/
```

### Configuración Recomendada

```yaml
# ✅ Timeouts recomendados por tipo de operación

Database Queries:
  SELECT simple: 5s
  SELECT complex: 30s
  SELECT analytics: 60s
  INSERT/UPDATE: 10s
  Batch operations: 120s

HTTP APIs:
  GET (read): 10s
  POST/PUT (write): 30s
  Long-running operations: Use async pattern (202 Accepted)

External Services:
  Payment processing: 30s
  Email sending: 15s
  SMS sending: 10s
  File upload: 60s

Internal Services:
  Synchronous: 5-10s
  Background jobs: 300s (5 min)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** configurar timeout en todos los HttpClients
- **MUST** usar CancellationToken en métodos async
- **MUST** configurar CommandTimeout en database operations
- **MUST** propagar CancellationToken a través de toda la cadena de llamadas
- **MUST** configurar timeout < 30s para operaciones síncronas
- **MUST** logguear cuando operations timeout
- **MUST** usar 202 Accepted para operaciones > 30s

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Polly Timeout para control granular
- **SHOULD** configurar diferentes timeouts por tipo de operación
- **SHOULD** implementar métricas de timeout rate
- **SHOULD** configurar ConnectTimeout en SocketsHttpHandler
- **SHOULD** usar timeout defensivo en controllers
- **SHOULD** implementar alarmas cuando timeout rate > 5%

### MAY (Opcional)

- **MAY** ajustar timeouts dinámicamente basado en performance
- **MAY** usar diferentes timeouts por environment (dev/prod)
- **MAY** implementar adaptive timeouts
- **MAY** configurar timeout warnings (80% del límite)

### MUST NOT (Prohibido)

- **MUST NOT** usar timeout infinito o muy largo (> 120s) para síncronos
- **MUST NOT** ignorar OperationCanceledException
- **MUST NOT** bloquear threads esperando sin timeout
- **MUST NOT** usar Task.Result o .Wait() (bloquea thread)
- **MUST NOT** configurar timeout más corto que retry delay total
- **MUST NOT** usar mismo timeout para todas las operaciones

---

## Referencias

- [Lineamiento: Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md)
- Estándares relacionados:
  - [Circuit Breaker](circuit-breaker.md)
  - [Retry Patterns](retry-patterns.md)
- Especificaciones:
  - [Polly Timeout](https://www.pollydocs.org/strategies/timeout)
  - [HttpClient Timeout](https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient.timeout)
  - [CancellationToken Best Practices](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)
