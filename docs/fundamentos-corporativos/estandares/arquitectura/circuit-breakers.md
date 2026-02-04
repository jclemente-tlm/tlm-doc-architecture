---
id: circuit-breakers
sidebar_position: 2
title: Circuit Breaker Pattern
description: Estándar para implementación de circuit breakers con Polly 8.0+ para prevenir cascadas de fallos y mejorar resiliencia
---

# Estándar Técnico — Circuit Breaker Pattern

---

## 1. Propósito

Prevenir cascadas de fallos y mejorar la resiliencia del sistema mediante la implementación de circuit breakers que detectan servicios degradados, abren el circuito automáticamente y permiten recuperación gradual, evitando sobrecarga de servicios downstream.

---

## 2. Alcance

**Aplica a:**

- Llamadas HTTP a servicios externos
- Conexiones a bases de datos
- Llamadas a APIs de terceros
- Comunicación entre microservicios
- Acceso a caches distribuidos
- Llamadas a message brokers

**No aplica a:**

- Operaciones in-process puras
- Operaciones de lectura local
- Logs y telemetría
- Health checks (usar timeout simple)

---

## 3. Tecnologías Aprobadas

| Componente      | Tecnología                      | Versión mínima | Observaciones                     |
| --------------- | ------------------------------- | -------------- | --------------------------------- |
| **Resilience**  | Polly                           | 8.0+           | Circuit breaker + retry + timeout |
| **ASP.NET**     | Microsoft.Extensions.Http.Polly | 8.0+           | Integración con HttpClient        |
| **Monitoring**  | Polly.Extensions.Telemetry      | 8.0+           | Métricas OpenTelemetry            |
| **Testing**     | Polly.Testing                   | 8.0+           | Unit tests de policies            |
| **Alternativa** | Steeltoe.CircuitBreaker         | 3.2+           | Para ecosistema Spring Cloud      |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Estados del Circuit Breaker

- [ ] **Closed:** estado normal, permite requests
- [ ] **Open:** circuito abierto, rechaza requests inmediatamente (fail-fast)
- [ ] **Half-Open:** prueba de recuperación, permite requests limitados

### Configuración de Umbrales

- [ ] Umbral de fallos consecutivos: mínimo 5 fallos en ventana
- [ ] Umbral de tasa de fallo: mínimo 50% en ventana deslizante
- [ ] Duración de circuito abierto: 30-60 segundos mínimo
- [ ] Requests permitidos en half-open: 1-3 requests de prueba
- [ ] Tamaño de ventana deslizante: 10-100 requests

### Excepciones a Manejar

- [ ] Timeouts (HttpRequestException, TaskCanceledException)
- [ ] Network errors (SocketException, IOException)
- [ ] HTTP 5xx (server errors)
- [ ] HTTP 429 (rate limiting)
- [ ] Excepciones transitorias custom

### Acciones al Cambiar Estado

- [ ] Log de transición de estados (Closed → Open → Half-Open)
- [ ] Métricas de estado actual del circuito
- [ ] Alertas cuando circuito abre
- [ ] Eventos para circuit breaker dashboard

### Fallback y Degradación

- [ ] Fallback definido para circuito abierto
- [ ] Cache de respuestas previas cuando aplique
- [ ] Respuesta default o degraded mode
- [ ] Mensaje de error descriptivo al cliente

### Isolation

- [ ] Circuit breaker por servicio downstream
- [ ] No compartir circuit breaker entre servicios distintos
- [ ] Aislamiento por endpoint crítico vs no-crítico

---

## 5. Prohibiciones

- ❌ Circuit breaker compartido entre servicios diferentes
- ❌ Abrir circuito en primer fallo (debe acumular fallos)
- ❌ Duración de circuito abierto < 10 segundos (muy agresivo)
- ❌ No implementar half-open state
- ❌ Circuit breaker sin métricas ni logs
- ❌ Silenciar errores sin fallback
- ❌ Aplicar circuit breaker a operaciones idempotentes sin retry previo

---

## 6. Configuración Mínima

```csharp
// Program.cs
using Polly;
using Polly.CircuitBreaker;

var builder = WebApplication.CreateBuilder(args);

// Configuración de circuit breaker para servicio externo
var circuitBreakerOptions = new CircuitBreakerStrategyOptions
{
    FailureRatio = 0.5,              // 50% de fallos
    MinimumThroughput = 10,          // Mínimo 10 requests en ventana
    SamplingDuration = TimeSpan.FromSeconds(30),  // Ventana de 30s
    BreakDuration = TimeSpan.FromSeconds(60),     // Abierto por 60s
    ShouldHandle = new PredicateBuilder()
        .Handle<HttpRequestException>()
        .Handle<TimeoutException>()
        .HandleResult<HttpResponseMessage>(r =>
            (int)r.StatusCode >= 500 || r.StatusCode == System.Net.HttpStatusCode.TooManyRequests),
    OnOpened = args =>
    {
        Console.WriteLine($"Circuit breaker abierto: {args.Outcome}");
        // Publicar métrica/alerta
        return ValueTask.CompletedTask;
    },
    OnClosed = args =>
    {
        Console.WriteLine("Circuit breaker cerrado");
        return ValueTask.CompletedTask;
    },
    OnHalfOpened = args =>
    {
        Console.WriteLine("Circuit breaker en half-open");
        return ValueTask.CompletedTask;
    }
};

// Registrar HttpClient con circuit breaker
builder.Services.AddHttpClient("PaymentService", client =>
{
    client.BaseAddress = new Uri("https://api.payments.talma.com");
    client.Timeout = TimeSpan.FromSeconds(10);
})
.AddResilienceHandler("payment-resilience", builder =>
{
    builder
        // 1. Timeout por request
        .AddTimeout(TimeSpan.FromSeconds(10))
        // 2. Retry con backoff
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(1),
            BackoffType = DelayBackoffType.Exponential
        })
        // 3. Circuit breaker
        .AddCircuitBreaker(circuitBreakerOptions);
});

var app = builder.Build();
app.Run();
```

```json
// appsettings.json
{
  "Resilience": {
    "PaymentService": {
      "CircuitBreaker": {
        "FailureRatio": 0.5,
        "MinimumThroughput": 10,
        "SamplingDurationSeconds": 30,
        "BreakDurationSeconds": 60
      },
      "Retry": {
        "MaxRetryAttempts": 3,
        "DelaySeconds": 1,
        "BackoffType": "Exponential"
      },
      "Timeout": {
        "TimeoutSeconds": 10
      }
    }
  }
}
```

---

## 7. Ejemplos

### Service con circuit breaker manual

```csharp
public class PaymentService
{
    private readonly HttpClient _httpClient;
    private readonly ResiliencePipeline<HttpResponseMessage> _pipeline;

    public PaymentService(
        IHttpClientFactory httpClientFactory,
        ResiliencePipelineProvider<string> pipelineProvider)
    {
        _httpClient = httpClientFactory.CreateClient("PaymentService");
        _pipeline = pipelineProvider.GetPipeline<HttpResponseMessage>("payment-resilience");
    }

    public async Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request)
    {
        try
        {
            var response = await _pipeline.ExecuteAsync(async ct =>
            {
                var httpRequest = new HttpRequestMessage(HttpMethod.Post, "/api/v1/payments")
                {
                    Content = JsonContent.Create(request)
                };
                return await _httpClient.SendAsync(httpRequest, ct);
            });

            if (response.IsSuccessStatusCode)
            {
                return await response.Content.ReadFromJsonAsync<PaymentResult>();
            }

            // Manejar errores 4xx
            throw new PaymentException($"Payment failed: {response.StatusCode}");
        }
        catch (BrokenCircuitException ex)
        {
            // Circuito abierto - fallback
            return new PaymentResult
            {
                Status = PaymentStatus.Deferred,
                Message = "Servicio de pagos temporalmente no disponible. Procesando en modo diferido.",
                RetryAfter = TimeSpan.FromMinutes(1)
            };
        }
    }
}
```

### Circuit breaker con fallback a cache

```csharp
public class ProductCatalogService
{
    private readonly HttpClient _httpClient;
    private readonly IDistributedCache _cache;
    private readonly ResiliencePipeline<ProductCatalog> _pipeline;

    public ProductCatalogService(
        IHttpClientFactory httpClientFactory,
        IDistributedCache cache)
    {
        _httpClient = httpClientFactory.CreateClient("CatalogService");
        _cache = cache;

        _pipeline = new ResiliencePipelineBuilder<ProductCatalog>()
            .AddCircuitBreaker(new CircuitBreakerStrategyOptions<ProductCatalog>
            {
                FailureRatio = 0.5,
                MinimumThroughput = 5,
                SamplingDuration = TimeSpan.FromSeconds(30),
                BreakDuration = TimeSpan.FromSeconds(60),
                ShouldHandle = new PredicateBuilder<ProductCatalog>()
                    .Handle<HttpRequestException>()
                    .Handle<TimeoutException>()
            })
            .AddFallback(new FallbackStrategyOptions<ProductCatalog>
            {
                FallbackAction = async args =>
                {
                    // Intentar cache
                    var cached = await _cache.GetStringAsync("product-catalog");
                    if (cached != null)
                    {
                        return Outcome.FromResult(
                            JsonSerializer.Deserialize<ProductCatalog>(cached));
                    }

                    // Fallback final
                    return Outcome.FromResult(ProductCatalog.Default);
                }
            })
            .Build();
    }

    public async Task<ProductCatalog> GetCatalogAsync()
    {
        return await _pipeline.ExecuteAsync(async ct =>
        {
            var response = await _httpClient.GetAsync("/api/v1/catalog", ct);
            response.EnsureSuccessStatusCode();

            var catalog = await response.Content.ReadFromJsonAsync<ProductCatalog>(ct);

            // Actualizar cache
            await _cache.SetStringAsync(
                "product-catalog",
                JsonSerializer.Serialize(catalog),
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10)
                },
                ct);

            return catalog;
        });
    }
}
```

### Circuit breaker con métricas

```csharp
public static class ResilienceConfiguration
{
    public static IServiceCollection AddResiliencePolicies(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        services.AddResiliencePipeline("payment-resilience", (builder, context) =>
        {
            var logger = context.ServiceProvider.GetRequiredService<ILogger<Program>>();
            var metrics = context.ServiceProvider.GetRequiredService<IMeterFactory>()
                .Create("PaymentService");

            var circuitOpenCounter = metrics.CreateCounter<int>("circuit_breaker_opened");
            var circuitClosedCounter = metrics.CreateCounter<int>("circuit_breaker_closed");

            builder.AddCircuitBreaker(new CircuitBreakerStrategyOptions
            {
                FailureRatio = 0.5,
                MinimumThroughput = 10,
                SamplingDuration = TimeSpan.FromSeconds(30),
                BreakDuration = TimeSpan.FromSeconds(60),
                OnOpened = args =>
                {
                    logger.LogError("Circuit breaker OPENED: {Exception}", args.Outcome.Exception);
                    circuitOpenCounter.Add(1);
                    return ValueTask.CompletedTask;
                },
                OnClosed = args =>
                {
                    logger.LogInformation("Circuit breaker CLOSED");
                    circuitClosedCounter.Add(1);
                    return ValueTask.CompletedTask;
                },
                OnHalfOpened = args =>
                {
                    logger.LogWarning("Circuit breaker HALF-OPEN (probando recuperación)");
                    return ValueTask.CompletedTask;
                }
            });
        });

        return services;
    }
}
```

### Testing de circuit breaker

```csharp
[Fact]
public async Task CircuitBreaker_Opens_After_FailureThreshold()
{
    // Arrange
    var handler = new Mock<HttpMessageHandler>();
    handler.Protected()
        .Setup<Task<HttpResponseMessage>>(
            "SendAsync",
            ItExpr.IsAny<HttpRequestMessage>(),
            ItExpr.IsAny<CancellationToken>())
        .ReturnsAsync(new HttpResponseMessage
        {
            StatusCode = HttpStatusCode.InternalServerError
        });

    var httpClient = new HttpClient(handler.Object);

    var pipeline = new ResiliencePipelineBuilder<HttpResponseMessage>()
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions<HttpResponseMessage>
        {
            FailureRatio = 0.5,
            MinimumThroughput = 3,
            SamplingDuration = TimeSpan.FromSeconds(10),
            BreakDuration = TimeSpan.FromSeconds(5),
            ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
                .HandleResult(r => (int)r.StatusCode >= 500)
        })
        .Build();

    // Act - ejecutar 3 requests que fallan
    for (int i = 0; i < 3; i++)
    {
        await Assert.ThrowsAsync<HttpRequestException>(async () =>
        {
            var result = await pipeline.ExecuteAsync(async ct =>
                await httpClient.GetAsync("http://test.com", ct));

            if ((int)result.StatusCode >= 500)
                throw new HttpRequestException();
        });
    }

    // Assert - la 4ta request debe lanzar BrokenCircuitException
    await Assert.ThrowsAsync<BrokenCircuitException>(async () =>
    {
        await pipeline.ExecuteAsync(async ct =>
            await httpClient.GetAsync("http://test.com", ct));
    });
}
```

---

## 8. Validación y Auditoría

```bash
# Revisar configuración de circuit breakers
grep -r "AddCircuitBreaker" --include="*.cs" ./

# Verificar que services externos tienen circuit breaker
dotnet list package | grep Polly

# Métricas de Polly en Prometheus
curl http://localhost:5000/metrics | grep polly

# Dashboard de circuit breakers
# Revisar en Grafana: Circuit Breaker State por servicio
```

**Métricas de cumplimiento:**

| Métrica                         | Umbral        | Verificación                                  |
| ------------------------------- | ------------- | --------------------------------------------- |
| HttpClients con circuit breaker | 100%          | Code review                                   |
| Servicios externos protegidos   | 100%          | Revisión de registros                         |
| Circuit breakers con métricas   | 100%          | Verificar telemetría                          |
| Fallbacks implementados         | 100%          | Code review                                   |
| Tests de circuit breaker        | >80% coverage | `dotnet test --collect:"XPlat Code Coverage"` |

**Checklist de auditoría:**

- [ ] Todos los HttpClients tienen circuit breaker
- [ ] Umbrales configurados según criticidad del servicio
- [ ] Logs/métricas en transiciones de estado
- [ ] Fallbacks implementados para circuitos abiertos
- [ ] Tests de comportamiento de circuit breaker
- [ ] Alertas configuradas para circuitos abiertos
- [ ] Dashboard de estado de circuit breakers

---

## 9. Referencias

- [Polly Documentation](https://www.pollydocs.org/)
- [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [AWS Well-Architected Framework - Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/)
- [Martin Fowler - Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Microsoft Patterns & Practices](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [Google SRE Book - Handling Overload](https://sre.google/sre-book/handling-overload/)
- [Netflix Hystrix (deprecated pero conceptos válidos)](https://github.com/Netflix/Hystrix/wiki/How-it-Works)
