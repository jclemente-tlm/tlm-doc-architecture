---
id: scalability-performance
sidebar_position: 7
title: Escalabilidad y Performance
description: Patrones para escalabilidad y performance incluyendo stateless design, caching, horizontal scaling, load balancing y health checks.
tags: [arquitectura, escalabilidad, performance, redis, stateless]
---

# Escalabilidad y Performance

## Contexto

Este estándar consolida patrones para sistemas escalables y performantes. Complementa el lineamiento [Escalabilidad y Rendimiento](../../lineamientos/arquitectura/escalabilidad-y-rendimiento.md).

**Conceptos incluidos:**

- **Stateless Design** → Servicios sin estado local
- **Caching Strategies** → Estrategias de cache distribuido
- **Horizontal Scaling** → Escalamiento mediante réplicas
- **Load Balancing** → Distribución de carga
- **Health Checks** → Monitoreo de disponibilidad

---

## Stack Tecnológico

| Componente            | Tecnología                                    | Versión | Uso                         |
| --------------------- | --------------------------------------------- | ------- | --------------------------- |
| **Framework**         | ASP.NET Core                                  | 8.0+    | APIs stateless              |
| **Cache distribuido** | Redis                                         | 7.2+    | Cache compartido            |
| **Orquestador**       | AWS ECS Fargate                               | -       | Auto-scaling, health checks |
| **Load Balancer**     | AWS ALB                                       | -       | Distribución L7             |
| **Health Checks**     | Microsoft.Extensions.Diagnostics.HealthChecks | 8.0+    | Probes                      |

---

## Stateless Design

### ¿Qué es Stateless Design?

Diseñar servicios donde cada request es independiente, sin estado almacenado localmente.

**Propósito:** Permitir replicación horizontal, failover automático.

**Beneficios:**
✅ Escalamiento horizontal simple
✅ Alta disponibilidad
✅ Deployment sin downtime

### Ejemplo Comparativo

```csharp
// ❌ MALO: Stateful (estado en memoria local)
private static Dictionary<string, Order> _pendingOrders = new();

[HttpPost("orders")]
public IActionResult CreateOrder(CreateOrderDto dto)
{
    var order = new Order { Id = Guid.NewGuid() };
    _pendingOrders[order.Id.ToString()] = order;
    return Ok(order.Id);
}

// ✅ BUENO: Stateless (estado externalizado)
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(CreateOrderDto dto)
{
    var order = new Order { Id = Guid.NewGuid() };
    await _orderRepository.SaveAsync(order);
    await _cache.SetAsync($"order:{order.Id}", order, TimeSpan.FromMinutes(15));
    return Ok(order.Id);
}
```

:::note
El principio de procesos sin estado es también el Factor 6 de [Twelve-Factor App](./architecture-evolution.md#twelve-factor-app). Consulta ese estándar para el contexto cloud-native más amplio.
:::

---

## Caching Strategies

### ¿Qué son Caching Strategies?

Estrategias de almacenamiento temporal para reducir latencia y carga.

**Niveles:**

- Client-side cache
- CDN
- API Gateway cache
- Application cache (Redis)
- Database query cache

**Beneficios:**
✅ Reducir latencia 10-100x
✅ Reducir carga en DB
✅ Mejorar throughput

### Ejemplo

```csharp
public class ProductService
{
    private readonly IDistributedCache _cache;

    public async Task<Product?> GetProductAsync(Guid id)
    {
        var cacheKey = $"product:{id}";
        var cached = await _cache.GetStringAsync(cacheKey);

        if (cached != null)
        {
            return JsonSerializer.Deserialize<Product>(cached);
        }

        var product = await _repository.GetByIdAsync(id);
        if (product != null)
        {
            await _cache.SetStringAsync(
                cacheKey,
                JsonSerializer.Serialize(product),
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30)
                });
        }

        return product;
    }
}
```

---

## Horizontal Scaling

### ¿Qué es Horizontal Scaling?

Incrementar capacidad agregando más instancias vs aumentar recursos de una instancia.

**Características:**

- Múltiples réplicas idénticas
- Load balancer distribuye tráfico
- Sin límite teórico de capacidad

**Beneficios:**
✅ Escalamiento elástico
✅ Sin downtime en deployment
✅ Tolerancia a fallos

### Configuración

```yaml
# ECS Service Auto Scaling
service:
  name: order-api
  min_capacity: 3
  max_capacity: 20

  auto_scaling:
    target_cpu: 70%
    scale_out_cooldown: 60
    scale_in_cooldown: 300
```

---

## Load Balancing

### ¿Qué es Load Balancing?

Distribución de tráfico entre múltiples instancias usando AWS ALB como capa L7.

**Algoritmos:**

- Round Robin
- Least Connections
- Weighted
- IP Hash (sticky)

**Beneficios:**
✅ Distribución equitativa
✅ Failover automático
✅ Health-based routing

### Configuración ALB (Target Group)

```yaml
# ALB Target Group
target_group:
  health_check:
    path: /health/ready
    interval: 30
    timeout: 5
    healthy_threshold: 2
    unhealthy_threshold: 3

  deregistration_delay: 30
  load_balancing_algorithm: least_outstanding_requests
```

### Consumo de servicios internos con IHttpClientFactory

Cuando un microservicio llama a otro detrás de un ALB, `IHttpClientFactory` gestiona el pool de conexiones y Polly agrega retry automático:

```csharp
// Program.cs
builder.Services.AddHttpClient<IInventoryClient, InventoryHttpClient>(client =>
{
    // La URL del ALB se externaliza como variable de entorno (12-factor)
    client.BaseAddress = new Uri(
        builder.Configuration["INVENTORY_SERVICE_URL"]
            ?? throw new InvalidOperationException("INVENTORY_SERVICE_URL required"));
    client.DefaultRequestHeaders.Add("Accept", "application/json");
})
.AddStandardResilienceHandler(); // Polly: retry + circuit breaker automático

// Implementación del cliente tipado
public class InventoryHttpClient : IInventoryClient
{
    private readonly HttpClient _httpClient;

    public InventoryHttpClient(HttpClient httpClient)
        => _httpClient = httpClient;

    public async Task<StockResult> GetStockAsync(Guid productId, CancellationToken ct = default)
    {
        var response = await _httpClient.GetAsync($"/api/inventory/{productId}", ct);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<StockResult>(cancellationToken: ct)
               ?? throw new InvalidOperationException("Invalid inventory response");
    }
}
```

:::note
El retry y circuit breaker del cliente HTTP se configuran con Polly en el estándar de [Resilience Patterns](./resilience-patterns.md).
:::

---

## Health Checks

### ¿Qué son Health Checks?

Endpoints que permiten al orquestador determinar el estado de una instancia. AWS ECS Fargate usa estos probes para decidir si enviar tráfico o reemplazar el contenedor.

**Tipos:**

- **Liveness**: ¿Está el proceso vivo? (ECS lo usa para decidir si reiniciar el contenedor)
- **Readiness**: ¿Puede recibir tráfico? (ALB lo usa para routing)
- **Startup**: ¿Completó inicialización? (evita liveness failures en boot)

**Beneficios:**
✅ Failover automático
✅ No enviar tráfico a instancias degradadas
✅ Auto-healing sin intervención manual

### Implementación

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddNpgSql(
        connectionString,
        name: "database",
        tags: ["critical", "readiness"])
    .AddRedis(
        redisConnectionString,
        name: "redis",
        tags: ["critical", "readiness"])
    .AddCheck<KafkaHealthCheck>(
        "kafka",
        tags: ["readiness"]);

// Liveness: proceso vivo aunque depéndencias fallen
app.UseHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false // Solo verifica que el proceso responde
});

// Readiness: BD y cache disponibles
app.UseHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("readiness")
});

// Startup: igual que readiness pero usado en el primer arranque
app.UseHealthChecks("/health/startup", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("readiness")
});

// Health check personalizado
public class KafkaHealthCheck : IHealthCheck
{
    private readonly IProducer<Null, string> _producer;

    public KafkaHealthCheck(IProducer<Null, string> producer)
        => _producer = producer;

    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Verificar conectividad con el broker
            var metadata = _producer.GetMetadata(allTopics: false, timeout: TimeSpan.FromSeconds(5));
            return Task.FromResult(
                metadata.Brokers.Count > 0
                    ? HealthCheckResult.Healthy("Kafka broker reachable")
                    : HealthCheckResult.Degraded("No brokers available"));
        }
        catch (Exception ex)
        {
            return Task.FromResult(HealthCheckResult.Unhealthy("Kafka unreachable", ex));
        }
    }
}
```

```yaml
# ECS Task Definition — configurar probes en la tarea
container_definitions:
  health_check:
    command:
      ["CMD-SHELL", "curl -f http://localhost:8080/health/live || exit 1"]
    interval: 30
    timeout: 5
    retries: 3
    start_period: 60 # Para containers con startup lento
```

---

## Matriz de Decisión

| Escenario       | Stateless | Cache  | H. Scaling | LB     | Health Checks |
| --------------- | --------- | ------ | ---------- | ------ | ------------- |
| **API pública** | ✅✅✅    | ✅✅✅ | ✅✅✅     | ✅✅✅ | ✅✅✅        |
| **API interna** | ✅✅✅    | ✅✅   | ✅✅       | ✅✅   | ✅✅✅        |
| **Worker**      | ✅✅      | ✅     | ✅✅       | -      | ✅✅          |

---

## Beneficios en Práctica

```yaml
# ✅ Comparativa de impacto

Antes (sin diseño stateless + auto-scaling):
  Problema: Servicio con sesiones en memoria local no puede replicarse,
    un solo nodo maneja todo el tráfico
  Consecuencia: Caída total ante spike de tráfico o reinicio del proceso

Después (con el estándar):
  Estado: Sesiones en Redis, 3 instancias mínimas con auto-scaling a 20,
    ALB distribuye carga con health checks
  Resultado: Spike de 10x tráfico absorbido en < 60s sin intervención manual,
    deploy sin downtime por rolling deployment
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** diseñar servicios stateless
- **MUST** externalizar sesiones a Redis/JWT
- **MUST** implementar health checks (liveness, readiness)
- **MUST** configurar auto-scaling basado en CPU/throughput
- **MUST** usar ALB para HTTP APIs

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar cache distribuido para datos frecuentes
- **SHOULD** configurar mínimo 3 instancias para HA
- **SHOULD** usar rolling deployment

### MUST NOT (Prohibido)

- **MUST NOT** almacenar sesiones en memoria local
- **MUST NOT** usar sticky sessions salvo justificación
- **MUST NOT** depender de filesystem local

---

## Referencias

- [AWS Auto Scaling](https://docs.aws.amazon.com/autoscaling/)
- [The Twelve-Factor App - Stateless Processes](https://12factor.net/processes)
- [Redis Caching Patterns](https://redis.io/docs/manual/patterns/)
