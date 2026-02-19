---
id: scalability-performance
sidebar_position: 6
title: Escalabilidad y Performance
description: Patrones para escalabilidad y performance incluyendo stateless design, caching, horizontal scaling, load balancing y health checks.
---

# Escalabilidad y Performance

## Contexto

Este estándar consolida patrones para sistemas escalables y performantes. Complementa el lineamiento [Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md).

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

## Conceptos Fundamentales

Este estándar cubre 5 patrones para escalabilidad:

### Índice de Conceptos

1. **Stateless Design**: Sin estado compartido localmente
2. **Caching Strategies**: Cache distribuido y local
3. **Horizontal Scaling**: Agregar réplicas vs aumentar recursos
4. **Load Balancing**: Algoritmos de distribución
5. **Health Checks**: Liveness, readiness, startup

---

## 1. Stateless Design

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

---

## 2. Caching Strategies

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

## 3. Horizontal Scaling

### ¿Qué es Horizontal Scaling?


Incrementar capacidad agregando más instancias vs aumentar recursos de una instancia.


**Características:**

- Múltiples rép licas idénticas
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

## 4. Load Balancing


### ¿Qué es Load Balancing?


Distribución de tráfico entre múltiples instancias.

**Algoritmos:**

- Round Robin
- Least Connections
- Weighted
- IP Hash (sticky)

**Beneficios:**
✅ Distribución equitativa
✅ Failover automático
✅ Health-based routing

### Configuración

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
`` `

---


##5. Health Checks

### ¿Qué son Health Checks?


Endpoints que permiten al orquestador determinar el estado de una instancia.

**Tipos:**

- **Liveness**: ¿Está el proceso vivo?
- **Readiness**: ¿Puede recibir tráfico?
- **Startup**: ¿Completó inicialización?

**Beneficios:**
✅ Failover automático
✅ No enviar tráfico a instancias degradadas
✅ Auto-healing

### Implementación

```csharp
// Health Checks
app.UseHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false
});

app.UseHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("critical")
});

services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "database", tags: new[] { "critical" })
    .AddRedis(connectionString, name: "redis", tags: new[] { "critical" });
```

---

## Matriz de Decisión

| Escenario       | Stateless | Cache  | H. Scaling | LB     | Health Checks |
| --------------- | --------- | ------ | ---------- | ------ | ------------- |
| **API pública** | ✅✅✅    | ✅✅✅ | ✅✅✅     | ✅✅✅ | ✅✅✅        |
| **API interna** | ✅✅✅    | ✅✅   | ✅✅       | ✅✅   | ✅✅✅        |
| **Worker**      | ✅✅      | ✅     | ✅✅       | -      | ✅✅          |

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
