---
id: retry-patterns
sidebar_position: 3
title: Retry con Backoff Exponencial
description: Estrategias de retry con backoff exponencial y jitter para transient failures
---

# Retry con Backoff Exponencial

## Contexto

Este estándar define cómo implementar retry lógica con backoff exponencial para manejar transient failures sin sobrecargar servicios. Complementa el [lineamiento de Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md) especificando **cuándo y cómo reintentar** operaciones fallidas.

---

## Stack Tecnológico

| Componente      | Tecnología         | Versión | Uso                   |
| --------------- | ------------------ | ------- | --------------------- |
| **Framework**   | ASP.NET Core       | 8.0+    | Framework base        |
| **Resilience**  | Polly              | 8.0+    | Retry políticas       |
| **HTTP Client** | IHttpClientFactory | 8.0+    | HTTP client con retry |

---

## Implementación Técnica

### Tipos de Backoff

```yaml
# ✅ Constant Backoff (simple pero no recomendado)
Retry 1: Wait 1s
Retry 2: Wait 1s
Retry 3: Wait 1s
# ❌ Problema: todos los clientes retrying al mismo tiempo

# ✅ Linear Backoff
Retry 1: Wait 1s
Retry 2: Wait 2s
Retry 3: Wait 3s
# ⚠️ Mejor pero predecible

# ✅ Exponential Backoff (recomendado)
Retry 1: Wait 2^1 = 2s
Retry 2: Wait 2^2 = 4s
Retry 3: Wait 2^3 = 8s
# ✅ Reduce carga progresivamente

# ✅ Exponential Backoff + Jitter (MEJOR)
Retry 1: Wait 2s + random(0-500ms)
Retry 2: Wait 4s + random(0-1000ms)
Retry 3: Wait 8s + random(0-2000ms)
# ✅ Distribuye retries, evita thundering herd
```

### Retry Básico con Polly

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ HTTP Client con retry policy
builder.Services
    .AddHttpClient("OrdersService")
    .AddResilienceHandler("orders-resilience", resilienceBuilder =>
    {
        resilienceBuilder.AddRetry(new RetryStrategyOptions
        {
            // ✅ Número máximo de reintentos
            MaxRetryAttempts = 3,

            // ✅ Delay base (dobla en cada retry)
            Delay = TimeSpan.FromSeconds(1),

            // ✅ Exponential backoff
            BackoffType = DelayBackoffType.Exponential,

            // ✅ Jitter para evitar thundering herd
            UseJitter = true,

            // ✅ Delay máximo (cap)
            MaxDelay = TimeSpan.FromSeconds(30),

            // ✅ Qué errores reintentar
            ShouldHandle = new PredicateBuilder()
                .Handle<HttpRequestException>()
                .Handle<TaskCanceledException>()
                .HandleResult(response =>
                    (int)response.StatusCode >= 500 ||  // 5xx server errors
                    response.StatusCode == HttpStatusCode.RequestTimeout ||  // 408
                    response.StatusCode == HttpStatusCode.TooManyRequests),  // 429

            // ✅ Callbacks para logging
            OnRetry = args =>
            {
                var outcome = args.Outcome;
                _logger.LogWarning(
                    "Retry {AttemptNumber} after {RetryDelay}ms. " +
                    "Reason: {FailureReason}",
                    args.AttemptNumber,
                    args.RetryDelay.TotalMilliseconds,
                    outcome.Exception?.Message ?? outcome.Result?.StatusCode.ToString());

                return ValueTask.CompletedTask;
            }
        });
    });
```

### Retry con Errores Específicos

```csharp
// ✅ Reintentar solo transient failures
builder.Services
    .AddHttpClient("PaymentService")
    .AddResilienceHandler("payment-resilience", resilienceBuilder =>
    {
        resilienceBuilder.AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(2),
            BackoffType = DelayBackoffType.Exponential,
            UseJitter = true,

            ShouldHandle = new PredicateBuilder()
                // ✅ Transient network errors
                .Handle<HttpRequestException>(ex =>
                    ex.InnerException is SocketException ||
                    ex.InnerException is IOException)

                // ✅ Timeout exceptions
                .Handle<TaskCanceledException>()
                .Handle<TimeoutException>()

                // ✅ HTTP status codes específicos
                .HandleResult(response =>
                {
                    var statusCode = (int)response.StatusCode;
                    return statusCode == 408 ||  // Request Timeout
                           statusCode == 429 ||  // Too Many Requests
                           statusCode == 503 ||  // Service Unavailable
                           statusCode == 504;   // Gateway Timeout
                })
        });
    });
```

### Retry con Backoff Personalizado

```csharp
// ✅ Custom backoff logic
resilienceBuilder.AddRetry(new RetryStrategyOptions
{
    MaxRetryAttempts = 5,
    UseJitter = true,

    // ✅ Delay generator personalizado
    DelayGenerator = args =>
    {
        // Implementar backoff personalizado
        var attempt = args.AttemptNumber;

        // Fibonacci backoff: 1s, 2s, 3s, 5s, 8s
        var delays = new[] { 1, 2, 3, 5, 8 };
        var delay = TimeSpan.FromSeconds(delays[Math.Min(attempt, delays.Length - 1)]);

        // Agregar jitter manual (0-20% del delay)
        var jitter = Random.Shared.Next(0, (int)(delay.TotalMilliseconds * 0.2));
        delay = delay.Add(TimeSpan.FromMilliseconds(jitter));

        _logger.LogDebug("Retry {Attempt} will wait {Delay}ms", attempt, delay.TotalMilliseconds);

        return ValueTask.FromResult<TimeSpan?>(delay);
    }
});
```

### Retry con Respeto a Retry-After Header

```csharp
// ✅ Usar Retry-After header de 429 Too Many Requests
resilienceBuilder.AddRetry(new RetryStrategyOptions
{
    MaxRetryAttempts = 3,

    DelayGenerator = args =>
    {
        // ✅ Si response tiene Retry-After header, usarlo
        if (args.Outcome.Result?.Headers.RetryAfter != null)
        {
            var retryAfter = args.Outcome.Result.Headers.RetryAfter;

            if (retryAfter.Delta.HasValue)
            {
                // Retry-After: 120 (segundos)
                _logger.LogInformation(
                    "Server requested retry after {Seconds}s via Retry-After header",
                    retryAfter.Delta.Value.TotalSeconds);

                return ValueTask.FromResult<TimeSpan?>(retryAfter.Delta.Value);
            }

            if (retryAfter.Date.HasValue)
            {
                // Retry-After: Wed, 21 Oct 2024 07:28:00 GMT
                var delay = retryAfter.Date.Value - DateTimeOffset.UtcNow;
                return ValueTask.FromResult<TimeSpan?>(delay > TimeSpan.Zero ? delay : TimeSpan.Zero);
            }
        }

        // ✅ Fallback a exponential backoff
        var defaultDelay = TimeSpan.FromSeconds(Math.Pow(2, args.AttemptNumber));
        return ValueTask.FromResult<TimeSpan?>(defaultDelay);
    },

    ShouldHandle = new PredicateBuilder()
        .HandleResult(r => r.StatusCode == HttpStatusCode.TooManyRequests)
});
```

### Retry Manual (Sin HttpClient)

```csharp
// ✅ Retry para operaciones que no son HTTP
public class EmailService : IEmailService
{
    private readonly ResiliencePipeline _retryPipeline;
    private readonly IEmailProvider _emailProvider;

    public EmailService(ResiliencePipelineProvider<string> pipelineProvider)
    {
        _retryPipeline = pipelineProvider.GetPipeline("email-retry");
    }

    public async Task SendEmailAsync(EmailMessage message)
    {
        await _retryPipeline.ExecuteAsync(async ct =>
        {
            // ✅ Operación protegida con retry
            await _emailProvider.SendAsync(message, ct);
        });
    }
}

// Program.cs
builder.Services.AddResiliencePipeline("email-retry", pipelineBuilder =>
{
    pipelineBuilder.AddRetry(new RetryStrategyOptions
    {
        MaxRetryAttempts = 3,
        Delay = TimeSpan.FromSeconds(2),
        BackoffType = DelayBackoffType.Exponential,
        UseJitter = true,
        ShouldHandle = new PredicateBuilder()
            .Handle<SmtpException>()
            .Handle<SocketException>()
    });
});
```

### Retry con Límite de Tiempo Total

```csharp
// ✅ Reintentar hasta que timeout total se alcance
public async Task<Order> GetOrderWithRetryAsync(string orderId)
{
    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));  // ✅ 30s total

    var retryPolicy = new RetryStrategyOptions
    {
        MaxRetryAttempts = int.MaxValue,  // ✅ Infinitos reintentos...
        Delay = TimeSpan.FromSeconds(1),
        BackoffType = DelayBackoffType.Exponential,
        MaxDelay = TimeSpan.FromSeconds(10),
        UseJitter = true,

        // ✅ ...pero detenerse cuando CancellationToken cancele (30s total)
        ShouldHandle = new PredicateBuilder()
            .Handle<HttpRequestException>()
    };

    var pipeline = new ResiliencePipelineBuilder()
        .AddRetry(retryPolicy)
        .Build();

    return await pipeline.ExecuteAsync(async ct =>
    {
        var client = _httpClientFactory.CreateClient("OrdersService");
        var response = await client.GetAsync($"/orders/{orderId}", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<Order>(ct);
    }, cts.Token);
}
```

### Retry Idempotente

```csharp
// ✅ IMPORTANTE: Solo retry en operaciones idempotentes

// ✅ SEGURO para retry: GET, HEAD, PUT idempotent, DELETE idempotent
[HttpGet("orders/{id}")]
public async Task<IActionResult> GetOrder(string id)
{
    // ✅ GET es idempotente, seguro reintentar
    var order = await _orderService.GetOrderAsync(id);
    return Ok(order);
}

[HttpPut("orders/{id}")]
public async Task<IActionResult> UpdateOrder(string id, UpdateOrderRequest request)
{
    // ✅ PUT es idempotente SI implementación lo es
    // (misma llamada múltiples veces = mismo resultado)
    var order = await _orderService.UpdateOrderAsync(id, request);
    return Ok(order);
}

// ⚠ NO seguro para retry sin idempotency key: POST
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(CreateOrderRequest request)
{
    // ❌ POST puede duplicar recursos si se retryea

    // ✅ Solución 1: Idempotency key
    var idempotencyKey = Request.Headers["Idempotency-Key"].FirstOrDefault();
    if (string.IsNullOrEmpty(idempotencyKey))
    {
        return BadRequest(new { error = "Idempotency-Key header required" });
    }

    // ✅ Verificar si ya procesamos este idempotencyKey
    var existing = await _orderService.GetByIdempotencyKeyAsync(idempotencyKey);
    if (existing != null)
    {
        return Ok(existing);  // ✅ Retornar orden existente
    }

    var order = await _orderService.CreateOrderAsync(request, idempotencyKey);
    return Created($"/orders/{order.Id}", order);
}
```

### Métricas de Retry

```csharp
public class RetryMetrics
{
    private readonly Counter<long> _retries;
    private readonly Counter<long> _retriesExhausted;
    private readonly Histogram<int> _retryAttempts;

    public RetryMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Resilience.Retry");

        _retries = meter.CreateCounter<long>(
            "retry.attempts", "attempts");
        _retriesExhausted = meter.CreateCounter<long>(
            "retry.exhausted", "failures");
        _retryAttempts = meter.CreateHistogram<int>(
            "retry.attempts_per_request", "attempts");
    }

    public void RecordRetry(string operation, int attemptNumber)
    {
        _retries.Add(1,
            new KeyValuePair<string, object?>("operation", operation),
            new KeyValuePair<string, object?>("attempt", attemptNumber));
    }

    public void RecordExhausted(string operation, int totalAttempts)
    {
        _retriesExhausted.Add(1,
            new KeyValuePair<string, object?>("operation", operation));
        _retryAttempts.Record(totalAttempts,
            new KeyValuePair<string, object?>("operation", operation));
    }
}

// PromQL queries
/*
# Retry rate
rate(retry_attempts_total[5m])

# Retry exhausted rate (all retries failed)
rate(retry_exhausted_total[5m])

# Average retries per request
rate(retry_attempts_per_request_sum[5m]) /
rate(retry_attempts_per_request_count[5m])
*/
```

### Configuración Recomendada por Escenario

```yaml
# ✅ Queries rápidos (GET)
MaxRetryAttempts: 3
Delay: 500ms
BackoffType: Exponential
UseJitter: true

# ✅ Commands (POST/PUT) con idempotency
MaxRetryAttempts: 3
Delay: 1s
BackoffType: Exponential
UseJitter: true

# ✅ Background jobs
MaxRetryAttempts: 5
Delay: 2s
BackoffType: Exponential
MaxDelay: 60s
UseJitter: true

# ✅ Integraciones externas (payment, email)
MaxRetryAttempts: 3
Delay: 2s
BackoffType: Exponential
UseJitter: true
# + Respetar Retry-After header
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar exponential backoff para todos los retries
- **MUST** agregar jitter para evitar thundering herd
- **MUST** configurar MaxRetryAttempts (≤ 5 típicamente)
- **MUST** solo retry en transient failures (5xx, timeouts, network errors)
- **MUST** implementar idempotency para operaciones de escritura
- **MUST** logguear cada retry attempt con razón
- **MUST** configurar MaxDelay para evitar delays muy largos

### SHOULD (Fuertemente recomendado)

- **SHOULD** respetar Retry-After header en 429 responses
- **SHOULD** combinar retry con circuit breaker
- **SHOULD** implementar métricas de retry rate
- **SHOULD** configurar diferentes políticas por criticidad
- **SHOULD** NO retry en 4xx client errors (excepto 408, 429)
- **SHOULD** usar CancellationToken para limitar tiempo total

### MAY (Opcional)

- **MAY** implementar custom backoff algorithms
- **MAY** ajustar retry policy dinámicamente
- **MAY** implementar retry budget (límite de retries por período)
- **MAY** usar diferentes retry policies por HTTP method

### MUST NOT (Prohibido)

- **MUST NOT** usar constant backoff sin jitter
- **MUST NOT** retry indefinidamente sin timeout total
- **MUST NOT** retry en 4xx client errors (excepto 408, 429)
- **MUST NOT** retry operaciones no-idempotentes sin idempotency key
- **MUST NOT** configurar delay > 60s
- **MUST NOT** ignorar Retry-After header del servidor

---

## Referencias

- [Lineamiento: Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md)
- Estándares relacionados:
  - [Circuit Breaker](circuit-breaker.md)
  - [Timeout Patterns](timeout-patterns.md)
  - [Idempotencia](../../estandares/mensajeria/idempotency.md)
- Especificaciones:
  - [Polly Retry](https://www.pollydocs.org/strategies/retry)
  - [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
  - [RFC 7231 - Retry-After](https://datatracker.ietf.org/doc/html/rfc7231#section-7.1.3)
