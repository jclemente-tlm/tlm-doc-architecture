---
id: circuit-breaker
sidebar_position: 1
title: Circuit Breaker para Dependencias Externas
description: Implementación de circuit breakers con Polly para proteger contra fallos en cascada
---

# Circuit Breaker para Dependencias Externas

## Contexto

Este estándar define cómo implementar circuit breakers para proteger servicios de cascading failures causados por dependencias fallidas. Complementa el [lineamiento de Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md) especificando **cómo aislar fallos** en llamadas remotas.

---

## Stack Tecnológico

| Componente      | Tecnología         | Versión | Uso                             |
| --------------- | ------------------ | ------- | ------------------------------- |
| **Framework**   | ASP.NET Core       | 8.0+    | Framework base                  |
| **Resilience**  | Polly              | 8.0+    | Circuit breaker, retry, timeout |
| **HTTP Client** | IHttpClientFactory | 8.0+    | HTTP client con resiliencia     |

---

## Implementación Técnica

### Concepto de Circuit Breaker

```yaml
# Estados del Circuit Breaker:

┌─────────┐
│ CLOSED  │ ──► Estado normal, requests pasan
└─────────┘
│
│ (failures > threshold)
▼
┌─────────┐
│  OPEN   │ ──► Fallo detectado, requests bloqueados inmediatamente
└─────────┘       (fail-fast, no esperar timeout)
│
│ (después de duration)
▼
┌─────────┐
│HALF-OPEN│ ──► Probar si servicio recuperó
└─────────┘
│ ┌────────┘
│ │(success)   (failures)
▼ ▼              │
CLOSED ◄───────────┘
```

### Configuración Básica con Polly

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Agregar Polly Resilience Pipelines
builder.Services.AddResilienceEnrichment();

// ✅ HTTP Client con Circuit Breaker
builder.Services
    .AddHttpClient("PaymentService", client =>
    {
        client.BaseAddress = new Uri("https://payment-api.talma.com");
        client.Timeout = TimeSpan.FromSeconds(30);
    })
    .AddResilienceHandler("payment-resilience", resilienceBuilder =>
    {
        // ✅ Circuit Breaker
        resilienceBuilder.AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            // Número de failures consecutivos antes de abrir
            FailureRatio = 0.5,  // 50% de requests fallando
            SamplingDuration = TimeSpan.FromSeconds(30),  // Ventana de muestreo
            MinimumThroughput = 10,  // Mínimo 10 requests antes de activar

            // Duración en estado OPEN antes de intentar HALF-OPEN
            BreakDuration = TimeSpan.FromSeconds(30),

            // Qué considerar como fallo
            ShouldHandle = new PredicateBuilder()
                .Handle<HttpRequestException>()
                .Handle<TaskCanceledException>()
                .HandleResult(response =>
                    (int)response.StatusCode >= 500 ||  // 5xx errors
                    response.StatusCode == HttpStatusCode.RequestTimeout)  // 408
        });

        // ✅ Timeout (antes de circuit breaker)
        resilienceBuilder.AddTimeout(TimeSpan.FromSeconds(10));

        // ✅ Retry (antes de circuit breaker)
        resilienceBuilder.AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(1),
            BackoffType = DelayBackoffType.Exponential
        });
    });
```

### Uso del HttpClient con Circuit Breaker

```csharp
// Service que consume API externa
public class PaymentService : IPaymentService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<PaymentService> _logger;

    public PaymentService(
        IHttpClientFactory httpClientFactory,
        ILogger<PaymentService> logger)
    {
        _httpClientFactory = httpClientFactory;
        _logger = logger;
    }

    public async Task<PaymentResponse> ProcessPaymentAsync(PaymentRequest request)
    {
        var client = _httpClientFactory.CreateClient("PaymentService");

        try
        {
            // ✅ Circuit breaker se aplica automáticamente
            var response = await client.PostAsJsonAsync("/payments", request);
            response.EnsureSuccessStatusCode();

            return await response.Content.ReadFromJsonAsync<PaymentResponse>();
        }
        catch (BrokenCircuitException ex)
        {
            // ✅ Circuit abierto: fallo rápido sin esperar timeout
            _logger.LogWarning(ex,
                "Payment service circuit breaker is OPEN. Failing fast.");

            // ✅ Retornar respuesta degradada o lanzar excepción específica
            throw new ServiceUnavailableException(
                "Payment service temporarily unavailable", ex);
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Payment service request failed");
            throw;
        }
    }
}
```

### Circuit Breaker Avanzado

```csharp
// Configuración más sofisticada
builder.Services
    .AddHttpClient("InventoryService")
    .AddResilienceHandler("inventory-resilience", resilienceBuilder =>
    {
        resilienceBuilder.AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            // ✅ Configuración agresiva para servicio crítico
            FailureRatio = 0.3,  // Abrir con 30% de fallos
            SamplingDuration = TimeSpan.FromSeconds(60),
            MinimumThroughput = 20,
            BreakDuration = TimeSpan.FromSeconds(60),

            ShouldHandle = new PredicateBuilder()
                .Handle<HttpRequestException>()
                .Handle<TaskCanceledException>()
                .HandleResult(r =>
                    (int)r.StatusCode >= 500 ||
                    r.StatusCode == HttpStatusCode.RequestTimeout),

            // ✅ Callbacks para logging/metrics
            OnOpened = args =>
            {
                _logger.LogWarning(
                    "Circuit breaker OPENED for InventoryService. " +
                    "FailureRate: {FailureRate}, BreakDuration: {BreakDuration}",
                    args.BreakDuration);

                // ✅ Incrementar métrica
                _metrics.CircuitBreakerOpened.Add(1,
                    new KeyValuePair<string, object?>("service", "inventory"));

                return ValueTask.CompletedTask;
            },

            OnClosed = args =>
            {
                _logger.LogInformation(
                    "Circuit breaker CLOSED for InventoryService");

                _metrics.CircuitBreakerClosed.Add(1,
                    new KeyValuePair<string, object?>("service", "inventory"));

                return ValueTask.CompletedTask;
            },

            OnHalfOpened = args =>
            {
                _logger.LogInformation(
                    "Circuit breaker HALF-OPEN for InventoryService. " +
                    "Testing if service recovered...");

                return ValueTask.CompletedTask;
            }
        });
    });
```

### Fallback con Circuit Breaker

```csharp
public class InventoryService : IInventoryService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IDistributedCache _cache;
    private readonly ILogger<InventoryService> _logger;

    public async Task<StockLevel> GetStockLevelAsync(string productId)
    {
        var client = _httpClientFactory.CreateClient("InventoryService");

        try
        {
            var response = await client.GetAsync($"/stock/{productId}");
            response.EnsureSuccessStatusCode();

            var stockLevel = await response.Content.ReadFromJsonAsync<StockLevel>();

            // ✅ Cachear respuesta exitosa
            await _cache.SetAsync($"stock:{productId}", stockLevel,
                TimeSpan.FromMinutes(5));

            return stockLevel;
        }
        catch (BrokenCircuitException ex)
        {
            _logger.LogWarning(ex,
                "Inventory service circuit OPEN. Using cached data for product {ProductId}",
                productId);

            // ✅ Fallback: retornar dato cacheado
            var cached = await _cache.GetAsync<StockLevel>($"stock:{productId}");
            if (cached != null)
            {
                cached.IsStale = true;  // ✅ Indicar que es dato viejo
                return cached;
            }

            // ✅ Fallback de último recurso: asumimos stock disponible
            _logger.LogWarning(
                "No cached data available for product {ProductId}. " +
                "Returning default stock level.", productId);

            return new StockLevel
            {
                ProductId = productId,
                Available = 0,
                IsStale = true,
                Message = "Inventory service temporarily unavailable"
            };
        }
    }
}
```

### Circuit Breaker Manual (Sin HttpClient)

```csharp
// Para database o servicios externos que no usan HttpClient
public class NotificationService : INotificationService
{
    private readonly ResiliencePipeline _resiliencePipeline;
    private readonly IEmailProvider _emailProvider;

    public NotificationService(
        ResiliencePipelineProvider<string> pipelineProvider,
        IEmailProvider emailProvider)
    {
        _emailProvider = emailProvider;

        // ✅ Obtener pipeline configurado
        _resiliencePipeline = pipelineProvider.GetPipeline("email-resilience");
    }

    public async Task SendEmailAsync(EmailMessage message)
    {
        await _resiliencePipeline.ExecuteAsync(async ct =>
        {
            // ✅ Operación protegida por circuit breaker
            await _emailProvider.SendAsync(message, ct);
        });
    }
}

// Program.cs - Configurar pipeline manual
builder.Services.AddResiliencePipeline("email-resilience", pipelineBuilder =>
{
    pipelineBuilder
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            SamplingDuration = TimeSpan.FromSeconds(30),
            MinimumThroughput = 5,
            BreakDuration = TimeSpan.FromMinutes(1),
            ShouldHandle = new PredicateBuilder()
                .Handle<SmtpException>()
                .Handle<TimeoutException>()
        })
        .AddTimeout(TimeSpan.FromSeconds(30))
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 2,
            Delay = TimeSpan.FromSeconds(2),
            BackoffType = DelayBackoffType.Exponential
        });
});
```

### Múltiples Circuit Breakers

```csharp
// Configurar diferentes policies para diferentes servicios
public static class ResiliencePolicies
{
    public static void ConfigureHttpClients(IServiceCollection services)
    {
        // ✅ Payment Service - Crítico, circuit breaker agresivo
        services.AddHttpClient("PaymentService")
            .AddResilienceHandler("payment-resilience", ConfigurePaymentResilience);

        // ✅ Catalog Service - Lectura, más tolerante
        services.AddHttpClient("CatalogService")
            .AddResilienceHandler("catalog-resilience", ConfigureCatalogResilience);

        // ✅ Analytics Service - No crítico, fail fast
        services.AddHttpClient("AnalyticsService")
            .AddResilienceHandler("analytics-resilience", ConfigureAnalyticsResilience);
    }

    private static void ConfigurePaymentResilience(ResiliencePipelineBuilder builder)
    {
        builder.AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.3,  // Abrir rápido
            SamplingDuration = TimeSpan.FromSeconds(30),
            MinimumThroughput = 10,
            BreakDuration = TimeSpan.FromSeconds(60)
        });
        builder.AddTimeout(TimeSpan.FromSeconds(10));
        builder.AddRetry(new RetryStrategyOptions { MaxRetryAttempts = 3 });
    }

    private static void ConfigureCatalogResilience(ResiliencePipelineBuilder builder)
    {
        builder.AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,  // Más tolerante
            SamplingDuration = TimeSpan.FromSeconds(60),
            MinimumThroughput = 20,
            BreakDuration = TimeSpan.FromMinutes(2)
        });
        builder.AddTimeout(TimeSpan.FromSeconds(30));
        builder.AddRetry(new RetryStrategyOptions { MaxRetryAttempts = 2 });
    }

    private static void ConfigureAnalyticsResilience(ResiliencePipelineBuilder builder)
    {
        builder.AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.7,  // Muy tolerante
            SamplingDuration = TimeSpan.FromMinutes(2),
            MinimumThroughput = 50,
            BreakDuration = TimeSpan.FromMinutes(5)
        });
        builder.AddTimeout(TimeSpan.FromSeconds(5));
        // ✅ Sin retry: analytics no es crítico
    }
}
```

### Métricas de Circuit Breaker

```csharp
public class CircuitBreakerMetrics
{
    private readonly Counter<long> _circuitBreakerOpened;
    private readonly Counter<long> _circuitBreakerClosed;
    private readonly Gauge<int> _circuitBreakerState;
    private readonly Counter<long> _rejectedRequests;

    public CircuitBreakerMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Resilience.CircuitBreaker");

        _circuitBreakerOpened = meter.CreateCounter<long>(
            "circuit_breaker.opened", "events");
        _circuitBreakerClosed = meter.CreateCounter<long>(
            "circuit_breaker.closed", "events");
        _circuitBreakerState = meter.CreateGauge<int>(
            "circuit_breaker.state", "state");  // 0=closed, 1=open, 2=half-open
        _rejectedRequests = meter.CreateCounter<long>(
            "circuit_breaker.rejected_requests", "requests");
    }
}

// PromQL queries
/*
# Circuit breaker opened events
rate(circuit_breaker_opened_total[5m])

# Rejected requests (cuando circuit está abierto)
rate(circuit_breaker_rejected_requests_total[5m])

# Estado actual por servicio
circuit_breaker_state{service="payment"}
*/
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar circuit breaker en todas las llamadas a servicios externos
- **MUST** configurar FailureRatio, SamplingDuration y BreakDuration apropiados
- **MUST** implementar degradación graceful cuando circuit está OPEN
- **MUST** logguear eventos de circuit breaker (opened, closed, half-open)
- **MUST** implementar métricas de circuit breaker
- **MUST** configurar MinimumThroughput para evitar false positives
- **MUST** combinar con timeout y retry policies

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar diferentes configuraciones por criticidad de servicio
- **SHOULD** implementar fallback a caché cuando circuit está abierto
- **SHOULD** configurar alarmas cuando circuit breaker abre frecuentemente
- **SHOULD** usar BrokenCircuitException para manejar circuit abierto
- **SHOULD** documentar comportamiento degradado
- **SHOULD** testear manualmente apertura de circuit breakers

### MAY (Opcional)

- **MAY** implementar circuit breakers manuales para operaciones no-HTTP
- **MAY** usar circuit breakers compartidos entre múltiples clientes
- **MAY** implementar dashboard de estado de circuit breakers
- **MAY** ajustar configuración dinámicamente basado en condiciones

### MUST NOT (Prohibido)

- **MUST NOT** usar circuit breaker sin configurar degradación graceful
- **MUST NOT** configurar BreakDuration muy corto (< 10s)
- **MUST NOT** ignorar BrokenCircuitException sin fallback
- **MUST NOT** usar circuit breaker para operaciones locales (DB, cache)
- **MUST NOT** configurar MinimumThroughput = 0 (causa false positives)
- **MUST NOT** abrir circuit breaker manualmente sin justificación

---

## Referencias

- [Lineamiento: Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md)
- Estándares relacionados:
  - [Timeout Patterns](timeout-patterns.md)
  - [Retry Patterns](retry-patterns.md)
  - [Graceful Degradation](graceful-degradation.md)
- Especificaciones:
  - [Polly Documentation](https://www.pollydocs.org/)
  - [Circuit Breaker Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
  - [Release It! - Circuit Breaker](https://pragprog.com/titles/mnee2/release-it-second-edition/)
