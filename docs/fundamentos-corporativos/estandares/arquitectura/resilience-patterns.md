---
id: resilience-patterns
sidebar_position: 2
title: Patrones de Resiliencia
description: Estándares consolidados para circuit breakers, retry patterns, graceful degradation, timeouts y graceful shutdown con Polly 8.0+
---

# Estándar Técnico — Patrones de Resiliencia

## 1. Propósito

Garantizar resiliencia en sistemas distribuidos mediante circuit breakers, retries, timeouts y graceful shutdown.

## 2. Alcance

**Aplica a:**

- Llamadas HTTP a servicios externos y APIs
- Conexiones a bases de datos y caches
- Comunicación entre microservicios
- Consumers de message brokers
- Operaciones asíncronas con dependencies externas
- Servicios contenerizados en AWS ECS Fargate

**No aplica a:**

- Operaciones in-process puras sin dependencies externas
- Lambda functions (serverless con manejo de AWS)
- Scripts batch de corta duración (`<5s`)
- Health checks simples

## 3. Tecnologías Aprobadas

| Componente        | Tecnología                      | Versión mínima | Observaciones                                |
| ----------------- | ------------------------------- | -------------- | -------------------------------------------- |
| **Resilience**    | Polly                           | 8.0+           | Circuit breaker + retry + timeout + fallback |
| **HTTP**          | Microsoft.Extensions.Http.Polly | 8.0+           | Integración con HttpClient                   |
| **Monitoring**    | Polly.Extensions.Telemetry      | 8.0+           | Métricas OpenTelemetry                       |
| **Testing**       | Polly.Testing                   | 8.0+           | Unit tests de policies                       |
| **Database**      | Npgsql                          | 8.0+           | Retry automático PostgreSQL                  |
| **EF Core**       | Microsoft.EntityFrameworkCore   | 8.0+           | ExecutionStrategy custom                     |
| **Cache**         | StackExchange.Redis             | 2.7+           | Timeouts configurables                       |
| **Feature Flags** | LaunchDarkly / Unleash          | -              | Feature toggles                              |
| **Load Balancer** | AWS ALB                         | -              | Connection draining                          |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

## 4. Circuit Breaker Pattern

### Requisitos Obligatorios 🔴

#### Configuración de Umbrales

- [ ] Umbral de fallos consecutivos: mínimo 5 fallos en ventana
- [ ] Umbral de tasa de fallo: mínimo 50% en ventana deslizante
- [ ] Duración de circuito abierto: 30-60 segundos mínimo
- [ ] Requests permitidos en half-open: 1-3 requests de prueba
- [ ] Tamaño de ventana deslizante: 10-100 requests

#### Excepciones a Manejar

- [ ] Timeouts (HttpRequestException, TaskCanceledException)
- [ ] Network errors (SocketException, IOException)
- [ ] HTTP 5xx (server errors)
- [ ] HTTP 429 (rate limiting)
- [ ] Excepciones transitorias custom

#### Acciones al Cambiar Estado

- [ ] Log de transición de estados (Closed → Open → Half-Open)
- [ ] Métricas de estado actual del circuito
- [ ] Alertas cuando circuito abre
- [ ] Eventos para circuit breaker dashboard

#### Fallback y Degradación

- [ ] Fallback definido para circuito abierto
- [ ] Cache de respuestas previas cuando aplique
- [ ] Respuesta default o degraded mode
- [ ] Mensaje de error descriptivo al cliente

#### Isolation

- [ ] Circuit breaker por servicio downstream
- [ ] No compartir circuit breaker entre servicios distintos
- [ ] Aislamiento por endpoint crítico vs no-crítico

### Prohibiciones Circuit Breaker

- ❌ Circuit breaker compartido entre servicios diferentes
- ❌ Abrir circuito en primer fallo (debe acumular fallos)
- ❌ Duración de circuito abierto `<10` segundos (muy agresivo)
- ❌ No implementar half-open state
- ❌ Circuit breaker sin métricas ni logs
- ❌ Silenciar errores sin fallback

### Configuración Circuit Breaker

```csharp
// Program.cs
using Polly;
using Polly.CircuitBreaker;

var builder = WebApplication.CreateBuilder(args);

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
        return ValueTask.CompletedTask;
    },
    OnClosed = args =>
    {
        Console.WriteLine("Circuit breaker cerrado");
        return ValueTask.CompletedTask;
    }
};

builder.Services.AddHttpClient("PaymentService", client =>
{
    client.BaseAddress = new Uri("https://api.payments.talma.com");
    client.Timeout = TimeSpan.FromSeconds(10);
})
.AddResilienceHandler("payment-resilience", builder =>
{
    builder
        .AddTimeout(TimeSpan.FromSeconds(10))
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(1),
            BackoffType = DelayBackoffType.Exponential
        })
        .AddCircuitBreaker(circuitBreakerOptions);
});

var app = builder.Build();
app.Run();
```

## 5. Retry Pattern con Exponential Backoff

### Requisitos Obligatorios 🔴

#### Estrategia de Backoff

- [ ] **Exponential backoff:** delay = base \* 2^attempt
- [ ] **Jitter:** randomización del delay (±25%) para evitar thundering herd
- [ ] **Max retry attempts:** 3-5 intentos máximo
- [ ] **Max delay:** límite superior de backoff (30-60 segundos)
- [ ] **Initial delay:** 100-1000ms según criticidad

#### Excepciones Retriables

- [ ] HTTP 408 (Request Timeout)
- [ ] HTTP 429 (Too Many Requests) - respetar Retry-After header
- [ ] HTTP 5xx (Server Errors)
- [ ] Network errors (SocketException, IOException)
- [ ] Timeouts (TaskCanceledException, TimeoutException)
- [ ] Database transient errors (connection loss, deadlock)

#### Idempotencia

- [ ] Operaciones GET/HEAD siempre retriables
- [ ] POST/PUT/DELETE con idempotency key
- [ ] Verificar que operación no se ejecutó dos veces
- [ ] Usar transaction IDs o correlation IDs

#### Retry-After Header

- [ ] Respetar Retry-After de HTTP 429/503
- [ ] Parsear formato RFC1123 o segundos
- [ ] Override de backoff si Retry-After > max delay

### Prohibiciones Retry

- ❌ Retry sin backoff (retry inmediato)
- ❌ Retry infinito o >10 intentos
- ❌ Retry de errores 4xx (excepto 429)
- ❌ Retry de operaciones no idempotentes sin idempotency key
- ❌ Ignorar Retry-After header
- ❌ Backoff sin jitter (causa thundering herd)

### Configuración Retry

```csharp
builder.Services.AddHttpClient("PaymentService")
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
            Console.WriteLine($"Retry {args.AttemptNumber} after {args.RetryDelay}");
            return ValueTask.CompletedTask;
        }
    });
});
```

## 6. Graceful Degradation

### Requisitos Obligatorios 🔴

#### Clasificación de Funcionalidades

- [ ] **Core:** autenticación, pagos, compliance (no degradable)
- [ ] **Important:** búsqueda, notificaciones (degradable con fallback)
- [ ] **Nice-to-have:** recomendaciones, analytics (degradable sin fallback)

#### Estrategias de Fallback

- [ ] Cached response (stale cache is better than no cache)
- [ ] Default/static response
- [ ] Funcionalidad reducida
- [ ] Empty result con mensaje informativo
- [ ] Skip feature (ocultar UI)

#### Feature Toggles

- [ ] Feature flags para deshabilitar funcionalidad no-crítica
- [ ] Kill switches para servicios degradados
- [ ] Rollback automático si error rate > umbral
- [ ] Toggles por tenant/usuario/región

#### Comunicación al Usuario

- [ ] Mensaje claro de funcionalidad reducida
- [ ] No exponer errores técnicos internos
- [ ] Sugerencias de retry o alternativas
- [ ] Status page para servicios degradados

### Prohibiciones Degradación

- ❌ Degradar funcionalidad core/crítica
- ❌ Fallar completamente si dependencia no-crítica falla
- ❌ Mostrar errores técnicos al usuario final
- ❌ Stale cache >24 horas sin advertencia
- ❌ Fallback que expone datos sensibles

### Configuración Degradación

```csharp
builder.Services.AddHttpClient("RecommendationService")
.AddResilienceHandler("recommendation-resilience", pipelineBuilder =>
{
    pipelineBuilder
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            MinimumThroughput = 5,
            BreakDuration = TimeSpan.FromSeconds(30)
        })
        .AddFallback(new FallbackStrategyOptions<HttpResponseMessage>
        {
            FallbackAction = async args =>
            {
                var cache = args.Context.ServiceProvider
                    .GetRequiredService<IDistributedCache>();

                var cached = await cache.GetStringAsync("recommendations:default");
                if (cached != null)
                {
                    return Outcome.FromResult(new HttpResponseMessage
                    {
                        StatusCode = HttpStatusCode.OK,
                        Content = new StringContent(cached)
                    });
                }

                return Outcome.FromResult(new HttpResponseMessage
                {
                    StatusCode = HttpStatusCode.OK,
                    Content = new StringContent("[]")
                });
            }
        });
});
```

## 7. Timeouts

### Requisitos Obligatorios 🔴

#### Timeouts por Capa

- [ ] **HTTP:** 10-30 segundos (según endpoint)
- [ ] **Database:** 5-30 segundos (queries simples vs complejos)
- [ ] **Cache (Redis):** 1-3 segundos
- [ ] **Message Broker:** 5-10 segundos para produce, 30s para consume
- [ ] **File Storage:** 60 segundos (uploads), 30 segundos (downloads)

#### Propagación de CancellationToken

- [ ] Todos los métodos async reciben `CancellationToken cancellationToken`
- [ ] Propagación a llamadas downstream
- [ ] `HttpContext.RequestAborted` en APIs ASP.NET Core
- [ ] Verificar `cancellationToken.IsCancellationRequested` en loops

#### Configuración de HttpClient

- [ ] `HttpClient.Timeout` configurado (default 100s es muy alto)
- [ ] Timeout por request usando `CancellationTokenSource`
- [ ] Timeout en handler con Polly

### Prohibiciones Timeout

- ❌ Timeout infinito (`Timeout.InfiniteTimeSpan`)
- ❌ Timeout muy alto (>120 segundos) sin justificación
- ❌ Ignorar `CancellationToken` en métodos async
- ❌ No propagar cancellation token a downstream calls
- ❌ Timeout menor que retry delay acumulado

### Configuración Timeout

```csharp
// HttpClient con timeout
builder.Services.AddHttpClient("PaymentService", client =>
{
    client.BaseAddress = new Uri("https://api.payments.talma.com");
    client.Timeout = TimeSpan.FromSeconds(10);
})
.AddResilienceHandler("payment-timeout", builder =>
{
    builder.AddTimeout(TimeSpan.FromSeconds(10));
});

// DbContext con timeout
builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    options.UseNpgsql(
        connectionString,
        npgsqlOptions =>
        {
            npgsqlOptions.CommandTimeout(30);
        });
});

// Redis con timeout
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.ConfigurationOptions = new ConfigurationOptions
    {
        SyncTimeout = 1000,
        AsyncTimeout = 3000
    };
});
```

### Controller con CancellationToken

```csharp
[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    [HttpGet("{id}")]
    [RequestTimeout("00:00:10")]
    public async Task<IActionResult> GetOrder(
        Guid id,
        CancellationToken cancellationToken)
    {
        var order = await _orderService.GetByIdAsync(id, cancellationToken);
        return order != null ? Ok(order) : NotFound();
    }

    [HttpPost]
    public async Task<IActionResult> CreateOrder(
        [FromBody] CreateOrderRequest request,
        CancellationToken cancellationToken)
    {
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        cts.CancelAfter(TimeSpan.FromSeconds(30));

        var order = await _orderService.CreateAsync(request, cts.Token);
        return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
    }
}
```

## 8. Graceful Shutdown

### Requisitos Obligatorios 🔴

#### Manejo de Señales

- [ ] Escuchar **SIGTERM** (no solo SIGKILL)
- [ ] Timeout de shutdown: 30-90 segundos
- [ ] Marcar servicio como "not ready" inmediatamente
- [ ] Esperar a que load balancer deje de enviar tráfico (10-15s)

#### Completado de Requests

- [ ] Completar requests HTTP en proceso
- [ ] Esperar a consumers de Kafka terminen processing
- [ ] Finalizar background tasks en curso
- [ ] Timeout para forzar shutdown si tarda mucho

#### Cierre de Conexiones

- [ ] Cerrar conexiones de database limpiamente
- [ ] Desconectar de message brokers
- [ ] Cerrar conexiones Redis
- [ ] Flush de logs pendientes

#### Health Checks

- [ ] `/health/ready` retorna 503 durante shutdown
- [ ] `/health/live` sigue retornando 200 (proceso activo)
- [ ] Load balancer deja de enviar tráfico basado en readiness

### Prohibiciones Shutdown

- ❌ Terminar proceso sin esperar requests en proceso
- ❌ No escuchar SIGTERM (solo catch SIGKILL)
- ❌ Shutdown timeout muy largo (>120s)
- ❌ No marcar como not-ready antes de shutdown
- ❌ No cerrar conexiones DB/Redis

### Configuración Graceful Shutdown

```csharp
// Program.cs
var app = builder.Build();

var lifetime = app.Services.GetRequiredService<IHostApplicationLifetime>();
var logger = app.Services.GetRequiredService<ILogger<Program>>();

lifetime.ApplicationStopping.Register(() =>
{
    logger.LogInformation("Received SIGTERM. Starting graceful shutdown...");
    HealthCheckService.IsShuttingDown = true;
    Thread.Sleep(TimeSpan.FromSeconds(15)); // Esperar load balancer drain
    logger.LogInformation("Ready to shutdown");
});

lifetime.ApplicationStopped.Register(() =>
{
    logger.LogInformation("Application stopped gracefully");
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("live")
});

app.Run();
```

```yaml
# AWS ECS Task Definition
spec:
  containers:
    - name: payment-service
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "sleep 15"]
  terminationGracePeriodSeconds: 90
```

## 9. Ejemplos Completos

### Pipeline Completo de Resiliencia

```csharp
builder.Services.AddHttpClient("PaymentService", client =>
{
    client.BaseAddress = new Uri("https://api.payments.talma.com");
    client.Timeout = TimeSpan.FromSeconds(30);
})
.AddResilienceHandler("payment-full-resilience", builder =>
{
    builder
        // 1. Timeout por request
        .AddTimeout(TimeSpan.FromSeconds(10))
        // 2. Retry con backoff
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3,
            Delay = TimeSpan.FromSeconds(1),
            BackoffType = DelayBackoffType.Exponential,
            UseJitter = true
        })
        // 3. Circuit breaker
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            MinimumThroughput = 10,
            BreakDuration = TimeSpan.FromSeconds(60)
        })
        // 4. Fallback
        .AddFallback(new FallbackStrategyOptions<HttpResponseMessage>
        {
            FallbackAction = async args => Outcome.FromResult(
                new HttpResponseMessage
                {
                    StatusCode = HttpStatusCode.ServiceUnavailable,
                    Content = new StringContent("{\"error\":\"Service temporarily unavailable\"}")
                })
        });
});
```

### Service con Resiliencia Completa

```csharp
public class PaymentService
{
    private readonly HttpClient _httpClient;
    private readonly IDistributedCache _cache;
    private readonly ILogger<PaymentService> _logger;

    public async Task<PaymentResult> ProcessPaymentAsync(
        PaymentRequest request,
        CancellationToken cancellationToken)
    {
        var cacheKey = $"payment:{request.OrderId}";

        try
        {
            var httpRequest = new HttpRequestMessage(HttpMethod.Post, "/api/v1/payments")
            {
                Content = JsonContent.Create(request)
            };

            httpRequest.Headers.Add("Idempotency-Key", request.OrderId.ToString());
            httpRequest.Headers.Add("X-Correlation-Id", Activity.Current?.Id);

            var response = await _httpClient.SendAsync(httpRequest, cancellationToken);
            response.EnsureSuccessStatusCode();

            var result = await response.Content.ReadFromJsonAsync<PaymentResult>(cancellationToken);

            await _cache.SetStringAsync(cacheKey, JsonSerializer.Serialize(result),
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10)
                }, cancellationToken);

            return result;
        }
        catch (BrokenCircuitException ex)
        {
            _logger.LogWarning(ex, "Circuit breaker opened for payment service");

            var cached = await _cache.GetStringAsync(cacheKey, cancellationToken);
            if (cached != null)
            {
                return JsonSerializer.Deserialize<PaymentResult>(cached);
            }

            return new PaymentResult
            {
                Status = PaymentStatus.Deferred,
                Message = "Payment service temporarily unavailable"
            };
        }
        catch (TimeoutException ex)
        {
            _logger.LogError(ex, "Timeout processing payment for order {OrderId}", request.OrderId);
            throw;
        }
    }
}
```

## 10. Validación y Auditoría

### Checklist de Cumplimiento

- [ ] Todos los HttpClients tienen pipeline de resiliencia (timeout + retry + circuit breaker)
- [ ] Métodos async reciben y propagan CancellationToken
- [ ] Feature toggles implementados para funcionalidad no-crítica
- [ ] Graceful shutdown configurado con SIGTERM handling
- [ ] Fallbacks definidos para servicios no-críticos
- [ ] Idempotency keys en operaciones POST/PUT/DELETE
- [ ] Health checks /health/live y /health/ready configurados
- [ ] Métricas de resiliencia exportadas a Grafana/Prometheus

### Comandos de Validación

```bash
# Verificar configuración de resiliencia
grep -r "AddResilienceHandler" --include="*.cs" ./
grep -r "AddCircuitBreaker" --include="*.cs" ./
grep -r "AddRetry" --include="*.cs" ./

# Verificar propagación de CancellationToken
grep -r "CancellationToken" --include="*.cs" ./ | wc -l

# Métricas de Polly
curl http://localhost:5000/metrics | grep polly

# Simular graceful shutdown
docker stop --time=90 payment-service
docker logs payment-service | grep "graceful shutdown"
```

### Métricas de Cumplimiento

| Métrica                             | Target   | Verificación    |
| ----------------------------------- | -------- | --------------- |
| Services con circuit breaker        | 100%     | Code review     |
| Retry con jitter habilitado         | 100%     | Code review     |
| Métodos async con CancellationToken | >95%     | Code analysis   |
| Timeout rate                        | `<1%`    | Grafana metrics |
| Circuit breaker open events         | `<5/día` | Alertas         |
| Graceful shutdown duration p99      | `<30s`   | Metrics         |
| Zero-downtime deployments           | 100%     | Deployment logs |

## 11. Prohibiciones Generales

- ❌ HttpClient sin pipeline de resiliencia
- ❌ Operaciones no idempotentes con retry sin idempotency key
- ❌ Circuit breaker compartido entre servicios diferentes
- ❌ Timeout infinito o muy alto sin justificación
- ❌ Degradar funcionalidad core/crítica
- ❌ Shutdown sin esperar requests en proceso
- ❌ No logging/métricas de eventos de resiliencia

## 12. Referencias

- [Polly Documentation](https://www.pollydocs.org/)
- [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [AWS Well-Architected - Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/)
- [Martin Fowler - Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Google SRE Book - Handling Overload](https://sre.google/sre-book/handling-overload/)
- [Microsoft Patterns & Practices](https://learn.microsoft.com/en-us/azure/architecture/patterns/)
- [12-Factor App - Disposability](https://12factor.net/disposability)
- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [ASP.NET Core Request Timeouts](https://learn.microsoft.com/en-us/aspnet/core/performance/timeouts)
- [AWS ECS Task Lifecycle](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-lifecycle.html)
