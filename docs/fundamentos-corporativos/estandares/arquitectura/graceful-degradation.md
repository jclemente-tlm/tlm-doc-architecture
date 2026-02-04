---
id: graceful-degradation
sidebar_position: 3
title: Degradación Elegante (Graceful Degradation)
description: Estándar para implementación de degradación elegante con fallbacks, feature toggles, cached responses y funcionalidad reducida durante fallos parciales
---

# Estándar Técnico — Degradación Elegante (Graceful Degradation)

---

## 1. Propósito

Mantener funcionalidad parcial durante fallos de dependencias mediante degradación elegante con fallbacks, cached responses, feature toggles y modos reducidos, evitando fallos totales del sistema cuando componentes no-críticos están degradados.

---

## 2. Alcance

**Aplica a:**

- Dependencias a servicios externos
- Funcionalidades no-críticas
- Features premium/opcionales
- Servicios de terceros
- Caches y optimizaciones
- Reportes y analytics

**No aplica a:**

- Funcionalidad core crítica (auth, pagos)
- Operaciones de escritura transaccionales
- Validaciones de seguridad
- Compliance requirements

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología             | Versión mínima | Observaciones           |
| ------------------- | ---------------------- | -------------- | ----------------------- |
| **Resilience**      | Polly                  | 8.0+           | Fallback strategies     |
| **Feature Flags**   | LaunchDarkly / Unleash | -              | Feature toggles         |
| **Cache**           | Redis                  | 7.0+           | Stale cache fallback    |
| **Config**          | AWS Parameter Store    | -              | Dynamic config          |
| **Circuit Breaker** | Polly                  | 8.0+           | Fail-fast with fallback |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Clasificación de Funcionalidades

- [ ] **Core:** autenticación, pagos, compliance (no degradable)
- [ ] **Important:** búsqueda, notificaciones (degradable con fallback)
- [ ] **Nice-to-have:** recomendaciones, analytics (degradable sin fallback)

### Estrategias de Fallback

- [ ] Cached response (stale cache is better than no cache)
- [ ] Default/static response
- [ ] Funcionalidad reducida
- [ ] Empty result con mensaje informativo
- [ ] Skip feature (ocultar UI)

### Feature Toggles

- [ ] Feature flags para deshabilitar funcionalidad no-crítica
- [ ] Kill switches para servicios degradados
- [ ] Rollback automático si error rate > umbral
- [ ] Toggles por tenant/usuario/región

### Telemetría

- [ ] Log cuando servicio entra en modo degradado
- [ ] Métrica de degradation mode activo
- [ ] Alertas para degradación prolongada (>10 min)
- [ ] Dashboard de servicios en degradación

### Comunicación al Usuario

- [ ] Mensaje claro de funcionalidad reducida
- [ ] No exponer errores técnicos internos
- [ ] Sugerencias de retry o alternativas
- [ ] Status page para servicios degradados

---

## 5. Prohibiciones

- ❌ Degradar funcionalidad core/crítica
- ❌ Fallar completamente si dependencia no-crítica falla
- ❌ Mostrar errores técnicos al usuario final
- ❌ Degradación sin logging/métricas
- ❌ Stale cache >24 horas sin advertencia
- ❌ Fallback que expone datos sensibles
- ❌ Feature toggles sin documentación

---

## 6. Configuración Mínima

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Feature flags
builder.Services.AddSingleton<IFeatureManager>(sp =>
{
    // Integración con LaunchDarkly, Unleash, o config
    return new FeatureManager(builder.Configuration);
});

// Polly fallback
builder.Services.AddHttpClient("RecommendationService", client =>
{
    client.BaseAddress = new Uri("https://api.recommendations.talma.com");
})
.AddResilienceHandler("recommendation-resilience", pipelineBuilder =>
{
    pipelineBuilder
        // Circuit breaker
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            MinimumThroughput = 5,
            BreakDuration = TimeSpan.FromSeconds(30)
        })
        // Fallback a cache o default
        .AddFallback(new FallbackStrategyOptions<HttpResponseMessage>
        {
            FallbackAction = async args =>
            {
                // Intentar cache
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

                // Default vacío
                return Outcome.FromResult(new HttpResponseMessage
                {
                    StatusCode = HttpStatusCode.OK,
                    Content = new StringContent("[]")
                });
            }
        });
});

var app = builder.Build();
app.Run();
```

```json
// appsettings.json
{
  "FeatureFlags": {
    "RecommendationsEnabled": true,
    "AdvancedSearchEnabled": true,
    "RealTimeNotificationsEnabled": true,
    "AnalyticsTrackingEnabled": true
  },
  "Degradation": {
    "MaxStaleCacheAge": "01:00:00", // 1 hora
    "DefaultRecommendations": [],
    "FallbackSearchResults": 10
  }
}
```

---

## 7. Ejemplos

### Degradación con cache stale

```csharp
public class ProductCatalogService
{
    private readonly HttpClient _httpClient;
    private readonly IDistributedCache _cache;
    private readonly ILogger<ProductCatalogService> _logger;

    public async Task<ProductCatalog> GetCatalogAsync()
    {
        var cacheKey = "product-catalog";

        try
        {
            // Intentar servicio primario
            var response = await _httpClient.GetAsync("/api/v1/catalog");
            response.EnsureSuccessStatusCode();

            var catalog = await response.Content.ReadFromJsonAsync<ProductCatalog>();

            // Actualizar cache
            await _cache.SetStringAsync(
                cacheKey,
                JsonSerializer.Serialize(new CachedCatalog
                {
                    Data = catalog,
                    CachedAt = DateTime.UtcNow
                }),
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = TimeSpan.FromHours(1)
                });

            return catalog;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Catalog service unavailable. Falling back to stale cache.");

            // Fallback a stale cache
            var cached = await _cache.GetStringAsync(cacheKey);
            if (cached != null)
            {
                var cachedCatalog = JsonSerializer.Deserialize<CachedCatalog>(cached);
                var age = DateTime.UtcNow - cachedCatalog.CachedAt;

                _logger.LogInformation(
                    "Using stale cache (age: {Age} minutes)",
                    age.TotalMinutes);

                return cachedCatalog.Data;
            }

            // Fallback final: catálogo vacío con mensaje
            _logger.LogError("No cache available. Returning empty catalog.");
            return ProductCatalog.Empty();
        }
    }
}

public record CachedCatalog
{
    public ProductCatalog Data { get; init; }
    public DateTime CachedAt { get; init; }
}
```

### Feature toggle para degradación

```csharp
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly IProductService _productService;
    private readonly IFeatureManager _featureManager;
    private readonly IDistributedCache _cache;

    [HttpGet]
    public async Task<IActionResult> GetProducts(
        [FromQuery] ProductSearchRequest request)
    {
        // Core: búsqueda básica (siempre disponible)
        var products = await _productService.SearchAsync(request.Query);

        // Nice-to-have: recomendaciones personalizadas
        if (await _featureManager.IsEnabledAsync("PersonalizedRecommendations"))
        {
            try
            {
                products.Recommendations = await GetRecommendationsAsync(request.UserId);
            }
            catch (Exception ex)
            {
                // Degradar: omitir recomendaciones
                _logger.LogWarning(ex, "Recommendations unavailable. Skipping.");
                products.Recommendations = Array.Empty<Product>();
            }
        }

        // Nice-to-have: analytics tracking
        if (await _featureManager.IsEnabledAsync("AnalyticsTracking"))
        {
            _ = TrackSearchAsync(request); // Fire-and-forget
        }

        return Ok(products);
    }
}
```

### Kill switch automático

```csharp
public class AutomaticDegradationService : BackgroundService
{
    private readonly IFeatureManager _featureManager;
    private readonly IMetricsCollector _metrics;
    private readonly ILogger<AutomaticDegradationService> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            // Verificar error rate de servicio de recomendaciones
            var errorRate = await _metrics.GetErrorRateAsync("RecommendationService");

            if (errorRate > 0.5) // >50% error rate
            {
                _logger.LogWarning(
                    "Recommendation service error rate: {ErrorRate}%. Disabling feature.",
                    errorRate * 100);

                // Deshabilitar feature automáticamente
                await _featureManager.DisableFeatureAsync("PersonalizedRecommendations");

                // Alertar
                await SendAlertAsync("Recommendation service auto-disabled due to high error rate");
            }
            else if (errorRate < 0.1) // <10% error rate
            {
                // Re-habilitar si error rate bajo
                await _featureManager.EnableFeatureAsync("PersonalizedRecommendations");
            }

            await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
        }
    }
}
```

---

## 8. Validación y Auditoría

```bash
# Verificar feature flags
grep -r "IsEnabledAsync" --include="*.cs" ./

# Verificar fallbacks configurados
grep -r "AddFallback" --include="*.cs" ./

# Métricas de degradación
curl http://localhost:5000/metrics | grep degradation_mode
```

**Métricas de cumplimiento:**

| Métrica                            | Umbral       | Verificación  |
| ---------------------------------- | ------------ | ------------- |
| Servicios no-críticos con fallback | 100%         | Code review   |
| Feature toggles implementados      | 100%         | Config review |
| Tiempo en modo degradado           | <1 hora/día  | Metrics       |
| Degradation rate                   | <5% requests | Metrics       |

**Checklist de auditoría:**

- [ ] Funcionalidades clasificadas (core/important/nice-to-have)
- [ ] Fallbacks para servicios no-críticos
- [ ] Feature toggles configurados
- [ ] Stale cache como fallback
- [ ] Logs/métricas de degradación
- [ ] Mensajes claros al usuario

---

## 9. Referencias

- [Release It! - Stability Patterns](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Google SRE - Graceful Degradation](https://sre.google/sre-book/addressing-cascading-failures/)
- [AWS Well-Architected - Reliability](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/)
- [Martin Fowler - Feature Toggles](https://martinfowler.com/articles/feature-toggles.html)
- [Netflix - Fault Tolerance](https://netflixtechblog.com/fault-tolerance-in-a-high-volume-distributed-system-91ab4faae74a)
- [Microsoft Patterns - Bulkhead](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead)
