---
id: horizontal-scaling
sidebar_position: 7
title: Escalado Horizontal
description: Configuración de auto-scaling en ECS Fargate y distribución de carga con AWS ALB.
tags: [arquitectura, escalabilidad, performance, ecs, alb]
---

# Escalado Horizontal

## Contexto

Este estándar consolida patrones para sistemas escalables y performantes. Complementa el lineamiento [Escalabilidad y Rendimiento](../../lineamientos/arquitectura/escalabilidad-y-rendimiento.md).

**Conceptos incluidos:**

- **Escalado Horizontal** → Escalamiento mediante réplicas
- **Balanceo de Carga** → Distribución de carga con AWS ALB

---

## Stack Tecnológico

| Componente        | Tecnología      | Versión | Uso             |
| ----------------- | --------------- | ------- | --------------- |
| **Orquestador**   | AWS ECS Fargate | -       | Auto-scaling    |
| **Load Balancer** | AWS ALB         | -       | Distribución L7 |

---

## Escalado Horizontal

### ¿Qué es el Escalado Horizontal?

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

## Balanceo de Carga

### ¿Qué es el Balanceo de Carga?

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

## Matriz de Decisión

| Escenario       | Escalado Horizontal | Balanceo de Carga |
| --------------- | ------------------- | ----------------- |
| **API pública** | ✅✅✅              | ✅✅✅            |
| **API interna** | ✅✅                | ✅✅              |
| **Worker**      | ✅✅                | -                 |

---

## Beneficios en Práctica

```yaml
# ✅ Comparativa de impacto

Antes (sin auto-scaling + health checks):
  Problema: Capacidad fija, un fallo en una instancia no se detecta
    y el ALB sigue enviando tráfico a ella
  Consecuencia: Errores visibles al usuario hasta intervención manual

Después (con el estándar):
  Configuración: 3 instancias mínimas con auto-scaling a 20,
    ALB con health checks, rollout automático ante instancia degradada
  Resultado: Spike de 10x tráfico absorbido en < 60s sin intervención,
    fallo de instancia detectado en 30s y removido del pool sin downtime
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** configurar auto-scaling basado en CPU/throughput
- **MUST** usar ALB para HTTP APIs públicas e internas

### SHOULD (Fuertemente recomendado)

- **SHOULD** configurar mínimo 3 instancias para HA
- **SHOULD** usar rolling deployment
- **SHOULD** configurar `deregistration_delay` en el target group

### MUST NOT (Prohibido)

- **MUST NOT** usar sticky sessions salvo justificación explícita

---

## Referencias

- [AWS Auto Scaling](https://docs.aws.amazon.com/autoscaling/)
- [AWS ALB — Configuring health checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [Health Checks](./health-checks.md)
