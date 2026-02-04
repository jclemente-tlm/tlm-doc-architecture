---
id: retry-patterns
sidebar_position: 7
title: Patrones de Retry con Backoff
description: Estándar para implementación de reintentos automáticos con exponential backoff, jitter y límites usando Polly 8.0+
---

# Estándar Técnico — Patrones de Retry con Backoff

---

## 1. Propósito

Manejar fallos transitorios mediante reintentos automáticos con exponential backoff, jitter y límites configurables, evitando sobrecarga de servicios degradados y mejorando la tasa de éxito de operaciones temporalmente fallidas.

---

## 2. Alcance

**Aplica a:**

- Llamadas HTTP a APIs externas
- Operaciones de base de datos transitorias
- Lecturas/escrituras en message brokers
- Acceso a servicios cloud (S3, DynamoDB, etc.)
- Operaciones de caché distribuido
- Llamadas a servicios de terceros

**No aplica a:**

- Errores de validación (4xx excepto 429)
- Errores de autenticación/autorización (401, 403)
- Operaciones no idempotentes sin idempotency key
- Timeouts muy largos (usar circuit breaker)

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología                      | Versión mínima | Observaciones                        |
| -------------- | ------------------------------- | -------------- | ------------------------------------ |
| **Resilience** | Polly                           | 8.0+           | Retry + exponential backoff + jitter |
| **HTTP**       | Microsoft.Extensions.Http.Polly | 8.0+           | Integración con HttpClient           |
| **Database**   | Npgsql                          | 8.0+           | Retry automático para PostgreSQL     |
| **EF Core**    | Microsoft.EntityFrameworkCore   | 8.0+           | ExecutionStrategy custom             |
| **AWS SDK**    | AWSSDK.Core                     | 3.7+           | Retry mode Standard/Adaptive         |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Estrategia de Backoff

- [ ] **Exponential backoff:** delay = base \* 2^attempt
- [ ] **Jitter:** randomización del delay (±25%) para evitar thundering herd
- [ ] **Max retry attempts:** 3-5 intentos máximo
- [ ] **Max delay:** límite superior de backoff (30-60 segundos)
- [ ] **Initial delay:** 100-1000ms según criticidad

### Excepciones Retriables

- [ ] HTTP 408 (Request Timeout)
- [ ] HTTP 429 (Too Many Requests) - respetar Retry-After header
- [ ] HTTP 5xx (Server Errors)
- [ ] Network errors (SocketException, IOException)
- [ ] Timeouts (TaskCanceledException, TimeoutException)
- [ ] Database transient errors (connection loss, deadlock)

### Idempotencia

- [ ] Operaciones GET/HEAD siempre retriables
- [ ] POST/PUT/DELETE con idempotency key
- [ ] Verificar que operación no se ejecutó dos veces
- [ ] Usar transaction IDs o correlation IDs

### Telemetría

- [ ] Log de cada retry con attempt number
- [ ] Métrica de retry count por endpoint/operación
- [ ] Métrica de success rate después de retries
- [ ] Distributed tracing con retry spans

### Retry-After Header

- [ ] Respetar Retry-After de HTTP 429/503
- [ ] Parsear formato RFC1123 o segundos
- [ ] Override de backoff si Retry-After > max delay

---

## 5. Prohibiciones

- ❌ Retry sin backoff (retry inmediato)
- ❌ Retry infinito o >10 intentos
- ❌ Retry de errores 4xx (excepto 429)
- ❌ Retry de operaciones no idempotentes sin idempotency key
- ❌ Ignorar Retry-After header
- ❌ Backoff sin jitter (causa thundering herd)
- ❌ Retry sin logging/métricas

---

## 6. Configuración Mínima

```csharp
// Program.cs
using Polly;
using Polly.Retry;

var builder = WebApplication.CreateBuilder(args);

// Retry con exponential backoff y jitter
builder.Services.AddHttpClient("PaymentService", client =>
{
    client.BaseAddress = new Uri("https://api.payments.talma.com");
})
.AddResilienceHandler("payment-retry", builder =>
{
    builder.AddRetry(new RetryStrategyOptions
    {
        MaxRetryAttempts = 3,
        Delay = TimeSpan.FromSeconds(1),      // Base delay
        BackoffType = DelayBackoffType.Exponential,
        UseJitter = true,                      // Añadir jitter ±25%
        MaxDelay = TimeSpan.FromSeconds(30),   // Límite superior
        ShouldHandle = new PredicateBuilder()
            .Handle<HttpRequestException>()
            .Handle<TimeoutException>()
            .HandleResult<HttpResponseMessage>(response =>
            {
                return response.StatusCode == System.Net.HttpStatusCode.TooManyRequests ||
                       (int)response.StatusCode >= 500;
            }),
        OnRetry = args =>
        {
            Console.WriteLine($"Retry {args.AttemptNumber} after {args.RetryDelay}. Outcome: {args.Outcome}");
            return ValueTask.CompletedTask;
        }
    });
});

var app = builder.Build();
app.Run();
```

```json
// appsettings.json
{
  "Resilience": {
    "PaymentService": {
      "Retry": {
        "MaxRetryAttempts": 3,
        "BaseDelayMilliseconds": 1000,
        "BackoffType": "Exponential",
        "UseJitter": true,
        "MaxDelaySeconds": 30
      }
    }
  }
}
```

---

## 7. Ejemplos

### Retry con Retry-After header

```csharp
public class RetryWithRetryAfterHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var pipeline = new ResiliencePipelineBuilder<HttpResponseMessage>()
            .AddRetry(new RetryStrategyOptions<HttpResponseMessage>
            {
                MaxRetryAttempts = 3,
                Delay = TimeSpan.FromSeconds(1),
                BackoffType = DelayBackoffType.Exponential,
                UseJitter = true,
                ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
                    .HandleResult(r =>
                        r.StatusCode == System.Net.HttpStatusCode.TooManyRequests ||
                        (int)r.StatusCode >= 500),
                DelayGenerator = args =>
                {
                    var response = args.Outcome.Result;

                    // Respetar Retry-After header
                    if (response?.Headers.RetryAfter != null)
                    {
                        if (response.Headers.RetryAfter.Delta.HasValue)
                        {
                            return ValueTask.FromResult(response.Headers.RetryAfter.Delta);
                        }
                        if (response.Headers.RetryAfter.Date.HasValue)
                        {
                            var delay = response.Headers.RetryAfter.Date.Value - DateTimeOffset.UtcNow;
                            return ValueTask.FromResult(delay > TimeSpan.Zero ? delay : null);
                        }
                    }

                    // Usar backoff exponencial default
                    return ValueTask.FromResult<TimeSpan?>(null);
                }
            })
            .Build();

        return await pipeline.ExecuteAsync(async ct =>
            await base.SendAsync(request, ct), cancellationToken);
    }
}
```

### Retry con idempotency key

```csharp
public class PaymentService
{
    private readonly HttpClient _httpClient;
    private readonly ResiliencePipeline<HttpResponseMessage> _pipeline;

    public async Task<PaymentResult> CreatePaymentAsync(PaymentRequest request)
    {
        // Generar idempotency key
        var idempotencyKey = Guid.NewGuid().ToString();

        var response = await _pipeline.ExecuteAsync(async ct =>
        {
            var httpRequest = new HttpRequestMessage(HttpMethod.Post, "/api/v1/payments")
            {
                Content = JsonContent.Create(request)
            };

            // Añadir idempotency key al header
            httpRequest.Headers.Add("Idempotency-Key", idempotencyKey);
            httpRequest.Headers.Add("X-Correlation-Id", Activity.Current?.Id);

            return await _httpClient.SendAsync(httpRequest, ct);
        });

        return await response.Content.ReadFromJsonAsync<PaymentResult>();
    }
}
```

### Tests de retry

```csharp
[Fact]
public async Task Retry_SucceedsOnThirdAttempt()
{
    var attempts = 0;
    var handler = new Mock<HttpMessageHandler>();

    handler.Protected()
        .Setup<Task<HttpResponseMessage>>(
            "SendAsync",
            ItExpr.IsAny<HttpRequestMessage>(),
            ItExpr.IsAny<CancellationToken>())
        .ReturnsAsync(() =>
        {
            attempts++;
            if (attempts < 3)
            {
                return new HttpResponseMessage
                {
                    StatusCode = HttpStatusCode.InternalServerError
                };
            }
            return new HttpResponseMessage
            {
                StatusCode = HttpStatusCode.OK,
                Content = new StringContent("{\"success\":true}")
            };
        });

    var httpClient = new HttpClient(handler.Object);

    var pipeline = new ResiliencePipelineBuilder<HttpResponseMessage>()
        .AddRetry(new RetryStrategyOptions<HttpResponseMessage>
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromMilliseconds(100),
            BackoffType = DelayBackoffType.Exponential,
            ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
                .HandleResult(r => (int)r.StatusCode >= 500)
        })
        .Build();

    var result = await pipeline.ExecuteAsync(async ct =>
        await httpClient.GetAsync("http://test.com", ct));

    Assert.Equal(HttpStatusCode.OK, result.StatusCode);
    Assert.Equal(3, attempts);
}
```

---

## 8. Validación y Auditoría

```bash
# Verificar configuración de retry
grep -r "AddRetry" --include="*.cs" ./

# Métricas de retry
curl http://localhost:5000/metrics | grep retry

# Logs de retries
kubectl logs -l app=payment-service | grep "Retry attempt"
```

**Métricas de cumplimiento:**

| Métrica                      | Umbral | Verificación               |
| ---------------------------- | ------ | -------------------------- |
| HttpClients con retry        | 100%   | Code review                |
| Retry con jitter             | 100%   | Code review                |
| Idempotency keys en POST/PUT | 100%   | Code review                |
| Logs de retry                | 100%   | Verificar OnRetry handlers |

**Checklist de auditoría:**

- [ ] Todos los HttpClients tienen retry configurado
- [ ] Backoff exponencial con jitter habilitado
- [ ] Max retry attempts ≤ 5
- [ ] Retry-After header respetado
- [ ] Idempotency keys en operaciones no-GET
- [ ] Métricas de retry por servicio

---

## 9. Referencias

- [Polly Documentation](https://www.pollydocs.org/)
- [AWS Well-Architected - Reliability](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/)
- [Azure Architecture - Retry Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Google SRE Book - Handling Overload](https://sre.google/sre-book/handling-overload/)
- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [RFC 7231 - Retry-After](https://www.rfc-editor.org/rfc/rfc7231#section-7.1.3)
- [Idempotency Keys - Stripe](https://stripe.com/docs/api/idempotent_requests)
