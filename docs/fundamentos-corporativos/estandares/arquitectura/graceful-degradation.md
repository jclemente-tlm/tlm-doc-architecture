---
id: graceful-degradation
sidebar_position: 4
title: Degradación Graceful ante Fallos
description: Estrategias para mantener funcionalidad parcial cuando dependencias fallan
---

# Degradación Graceful ante Fallos

## Contexto

Este estándar define cómo implementar degradación graceful para mantener funcionalidad esencial cuando dependencias fallan. Complementa el [lineamiento de Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md) especificando **cómo fallar parcialmente** en lugar de completamente.

---

## Stack Tecnológico

| Componente     | Tecnología   | Versión | Uso                 |
| -------------- | ------------ | ------- | ------------------- |
| **Framework**  | ASP.NET Core | 8.0+    | Framework base      |
| **Resilience** | Polly        | 8.0+    | Fallback policies   |
| **Cache**      | Redis        | 7.0+    | Caché para fallback |

---

## Implementación Técnica

### Principios de Degradación Graceful

```yaml
# ✅ Jerarquía de respuestas ante fallo

1. Primary: Respuesta completa y actualizada
  ├─ API externa disponible
  └─ Datos frescos del sistema

2. Fallback 1: Respuesta parcial con datos cacheados
  ├─ API externa no disponible
  └─ Usar datos cacheados (marcar como stale)

3. Fallback 2: Respuesta mínima funcional
  ├─ Cache no disponible
  └─ Datos mínimos hardcoded o default values

4. Fallback 3: Error graceful
  ├─ Todas las fuentes fallaron
  └─ Mensaje descriptivo con recomendaciones
```

### Degradación con Fallback a Caché

```csharp
public class ProductService : IProductService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IDistributedCache _cache;
    private readonly ILogger<ProductService> _logger;

    public async Task<ProductDetails> GetProductDetailsAsync(string productId)
    {
        var cacheKey = $"product:{productId}";

        try
        {
            // ✅ Intento 1: API externa (datos frescos)
            var client = _httpClientFactory.CreateClient("CatalogService");
            var response = await client.GetAsync($"/products/{productId}");
            response.EnsureSuccessStatusCode();

            var product = await response.Content.ReadFromJsonAsync<ProductDetails>();

            // ✅ Actualizar cache exitosamente
            await _cache.SetAsync(cacheKey, product, TimeSpan.FromMinutes(15));

            product.DataSource = "live";  // ✅ Indicar fuente
            return product;
        }
        catch (Exception ex) when (ex is HttpRequestException or BrokenCircuitException)
        {
            _logger.LogWarning(ex,
                "Catalog service unavailable for product {ProductId}. Falling back to cache.",
                productId);

            // ✅ Fallback: Datos cacheados
            var cached = await _cache.GetAsync<ProductDetails>(cacheKey);
            if (cached != null)
            {
                cached.DataSource = "cache";  // ✅ Indicar que son datos viejos
                cached.IsStale = true;
                cached.Message = "Product information may be outdated";
                return cached;
            }

            // ✅ Fallback final: Datos mínimos
            _logger.LogError(
                "No cached data available for product {ProductId}. Returning minimal info.",
                productId);

            return new ProductDetails
            {
                ProductId = productId,
                Name = "Product information temporarily unavailable",
                DataSource = "default",
                IsStale = true,
                Message = "Product catalog is temporarily unavailable. Please try again later."
            };
        }
    }
}
```

### Degradación en Features No Críticos

```csharp
[HttpGet("orders/{id}")]
public async Task<IActionResult> GetOrder(string id)
{
    // ✅ Core: Datos de orden (crítico)
    var order = await _orderService.GetOrderAsync(id);
    if (order == null)
        return NotFound();

    var response = new OrderResponse
    {
        OrderId = order.Id,
        Status = order.Status,
        TotalAmount = order.TotalAmount,
        CreatedAt = order.CreatedAt,
        Items = order.Items
    };

    // ✅ Enhancement 1: Inventory (no crítico, degrade gracefully)
    try
    {
        var inventory = await _inventoryService.GetStockLevelsAsync(
            order.Items.Select(i => i.ProductId));

        response.StockAvailability = inventory;
    }
    catch (Exception ex)
    {
        _logger.LogWarning(ex, "Failed to fetch inventory for order {OrderId}", id);
        response.StockAvailability = null;  // ✅ Omitir feature
        response.Warnings.Add("Stock information temporarily unavailable");
    }

    // ✅ Enhancement 2: Recommendations (no crítico)
    try
    {
        response.RecommendedProducts = await _recommendationService.GetRecommendationsAsync(id);
    }
    catch (Exception ex)
    {
        _logger.LogWarning(ex, "Failed to fetch recommendations for order {OrderId}", id);
        response.RecommendedProducts = Array.Empty<Product>();  // ✅ Array vacío
    }

    // ✅ Enhancement 3: User reviews (no crítico)
    try
    {
        response.Reviews = await _reviewService.GetReviewsAsync(order.Items.Select(i => i.ProductId));
    }
    catch (Exception ex)
    {
        _logger.LogWarning(ex, "Failed to fetch reviews for order {OrderId}", id);
        response.Reviews = null;  // ✅ Omitir feature
    }

    return Ok(response);  // ✅ Retornar orden con features disponibles
}
```

### Degradación con Feature Flags

```csharp
public class CheckoutService : ICheckoutService
{
    private readonly IFeatureManager _featureManager;
    private readonly IPaymentService _paymentService;
    private readonly IInventoryService _inventoryService;

    public async Task<CheckoutResult> ProcessCheckoutAsync(CheckoutRequest request)
    {
        var result = new CheckoutResult();

        // ✅ Feature crítico: Payment (siempre habilitado)
        result.Payment = await _paymentService.ProcessAsync(request.Payment);

        // ✅ Feature degradable: Inventory reservation
        if (await _featureManager.IsEnabledAsync("InventoryReservation"))
        {
            try
            {
                result.InventoryReserved = await _inventoryService.ReserveAsync(
                    request.Items);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Inventory reservation failed. Degrading gracefully.");

                // ✅ Deshabilitar feature automáticamente
                await _featureManager.DisableFeatureAsync("InventoryReservation");

                result.InventoryReserved = false;
                result.Warnings.Add(
                    "Inventory not reserved. Stock will be allocated on shipment.");
            }
        }
        else
        {
            _logger.LogInformation(
                "Inventory reservation feature disabled. Skipping reservation.");
            result.InventoryReserved = false;
        }

        return result;
    }
}
```

### Circuit Breaker con Fallback

```csharp
// ✅ Combinar circuit breaker + fallback
builder.Services
    .AddHttpClient("RecommendationService")
    .AddResilienceHandler("recommendation-resilience", resilienceBuilder =>
    {
        // ✅ 1. Circuit breaker (protección)
        resilienceBuilder.AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            SamplingDuration = TimeSpan.FromSeconds(30),
            MinimumThroughput = 10,
            BreakDuration = TimeSpan.FromSeconds(60)
        });

        // ✅ 2. Fallback (degradación)
        resilienceBuilder.AddFallback(new FallbackStrategyOptions<HttpResponseMessage>
        {
            ShouldHandle = new PredicateBuilder<HttpResponseMessage>()
                .Handle<BrokenCircuitException>()
                .Handle<HttpRequestException>()
                .HandleResult(r => (int)r.StatusCode >= 500),

            FallbackAction = args =>
            {
                _logger.LogWarning(
                    "Recommendation service unavailable. Returning fallback response.");

                // ✅ Respuesta fallback (lista vacía)
                var fallbackContent = JsonSerializer.Serialize(
                    new List<Product>());

                var fallbackResponse = new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(
                        fallbackContent,
                        Encoding.UTF8,
                        "application/json")
                };

                fallbackResponse.Headers.Add("X-Fallback", "true");

                return Outcome.FromResult(fallbackResponse);
            }
        });
    });
```

### Degradación en Background Jobs

```csharp
public class OrderProcessingWorker : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var orders = await FetchPendingOrdersAsync(stoppingToken);

                foreach (var order in orders)
                {
                    try
                    {
                        // ✅ Procesar con todas las features
                        await ProcessOrderFullAsync(order, stoppingToken);
                    }
                    catch (PaymentServiceException ex)
                    {
                        // ❌ Payment crítico: mover a retry queue
                        _logger.LogError(ex,
                            "Payment failed for order {OrderId}. Moving to retry queue.",
                            order.Id);
                        await MoveToRetryQueueAsync(order);
                    }
                    catch (InventoryServiceException ex)
                    {
                        // ✅ Inventory no crítico: continuar sin reserva
                        _logger.LogWarning(ex,
                            "Inventory service unavailable for order {OrderId}. " +
                            "Processing without reservation.",
                            order.Id);

                        await ProcessOrderWithoutInventoryAsync(order, stoppingToken);
                    }
                    catch (NotificationServiceException ex)
                    {
                        // ✅ Notifications no crítico: continuar, encolar notificación
                        _logger.LogWarning(ex,
                            "Notification failed for order {OrderId}. " +
                            "Order processed, notification queued.",
                            order.Id);

                        await CompleteOrderAsync(order);
                        await QueueNotificationAsync(order);
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in order processing loop");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }
}
```

### Degradación con Observabilidad

```csharp
public class DegradationMetrics
{
    private readonly Counter<long> _degradedResponses;
    private readonly Gauge<int> _degradationLevel;

    public DegradationMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.Resilience.Degradation");

        _degradedResponses = meter.CreateCounter<long>(
            "degraded_responses", "responses");
        _degradationLevel = meter.CreateGauge<int>(
            "degradation_level", "level");  // 0=normal, 1=partial, 2=minimal
    }

    public void RecordDegradedResponse(string feature, string fallbackUsed)
    {
        _degradedResponses.Add(1,
            new KeyValuePair<string, object?>("feature", feature),
            new KeyValuePair<string, object?>("fallback", fallbackUsed));
    }
}

// PromQL queries
/*
# Degraded response rate
rate(degraded_responses_total[5m])

# Current degradation level
degradation_level

# Most frequently degraded features
topk(5, sum(rate(degraded_responses_total[5m])) by (feature))
*/
```

### Health Check con Degradation Status

```csharp
public class ApplicationHealthCheck : IHealthCheck
{
    private readonly IEnumerable<IHealthCheck> _dependencyChecks;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        var degradedFeatures = new List<string>();
        var criticalFailures = new List<string>();

        foreach (var check in _dependencyChecks)
        {
            var result = await check.CheckHealthAsync(context, cancellationToken);

            if (result.Status == HealthStatus.Unhealthy)
            {
                if (check is ICriticalDependency)
                {
                    criticalFailures.Add(check.GetType().Name);
                }
                else
                {
                    degradedFeatures.Add(check.GetType().Name);
                }
            }
        }

        if (criticalFailures.Any())
        {
            return HealthCheckResult.Unhealthy(
                $"Critical dependencies unavailable: {string.Join(", ", criticalFailures)}",
                data: new Dictionary<string, object>
                {
                    ["criticalFailures"] = criticalFailures,
                    ["degradedFeatures"] = degradedFeatures
                });
        }

        if (degradedFeatures.Any())
        {
            return HealthCheckResult.Degraded(
                $"Running in degraded mode. Features unavailable: {string.Join(", ", degradedFeatures)}",
                data: new Dictionary<string, object>
                {
                    ["degradedFeatures"] = degradedFeatures
                });
        }

        return HealthCheckResult.Healthy("All systems operational");
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar fallback para servicios no críticos
- **MUST** usar cache como fallback cuando sea posible
- **MUST** indicar cuando response es degradado (stale, partial)
- **MUST** logguear degradaciones con severidad apropiada
- **MUST** mantener funcionalidad core disponible
- **MUST** documentar qué features son críticos vs degradables
- **MUST** implementar health checks que reflejen degradación

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar feature flags para deshabilitar features problemáticas
- **SHOULD** implementar múltiples niveles de fallback
- **SHOULD** retornar partial data en lugar de error completo
- **SHOULD** implementar métricas de degradación
- **SHOULD** usar fallback values sensatos (empty array vs null)
- **SHOULD** configurar alarmas para degradación prolongada

### MAY (Opcional)

- **MAY** implementar degradación automática basada en load
- **MAY** ajustar UI dinámicamente basado en degradación
- **MAY** cachear respuestas degradadas
- **MAY** implementar "apologybanner" en UI durante degradación

### MUST NOT (Prohibido)

- **MUST NOT** degradar features críticos sin alternativa
- **MUST NOT** retornar datos incorrectos sin indicar que son stale
- **MUST NOT** silenciar errores de degradación
- **MUST NOT** degradar permanentemente sin investigar root cause
- **MUST NOT** usar defaults que puedan causar problemas de negocio
- **MUST NOT** degradar sin monitoreo/métricas

---

## Referencias

- [Lineamiento: Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md)
- Estándares relacionados:
  - [Circuit Breaker](circuit-breaker.md)
  - [Estrategias de Caché](../../estandares/arquitectura/caching-strategies.md)
- Especificaciones:
  - [Polly Fallback](https://www.pollydocs.org/strategies/fallback)
  - [Feature Flags Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/feature-flags)
  - [Graceful Degradation](https://en.wikipedia.org/wiki/Fault_tolerance#Graceful_degradation)
