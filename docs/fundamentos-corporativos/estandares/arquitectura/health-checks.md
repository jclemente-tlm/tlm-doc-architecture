---
id: health-checks
sidebar_position: 10
title: Health Checks
description: Implementación de liveness, readiness y startup probes en .NET 8 para orquestadores y load balancers en entornos en contenedores.
tags: [arquitectura, infraestructura, health-checks, resiliencia, ecs]
---

# Health Checks

## Contexto

Este estándar define la implementación de health checks para permitir que el orquestador y el load balancer determinen el estado de cada instancia y tomen decisiones automáticas de routing, reinicio y failover. Aplica a cualquier servicio en contenedores, independientemente del caso de uso (escalado horizontal, resiliencia, despliegue sin downtime).

Complementa los lineamientos [Escalabilidad y Rendimiento](../../lineamientos/arquitectura/escalabilidad-y-rendimiento.md) y [Resiliencia y Disponibilidad](../../lineamientos/arquitectura/resiliencia-y-disponibilidad.md).

**Conceptos incluidos:**

- **Liveness** → ¿Está el proceso vivo?
- **Readiness** → ¿Puede recibir tráfico?
- **Startup** → ¿Completó inicialización?

---

## Stack Tecnológico

| Componente        | Tecnología                                    | Versión | Uso            |
| ----------------- | --------------------------------------------- | ------- | -------------- |
| **Health Checks** | Microsoft.Extensions.Diagnostics.HealthChecks | 8.0+    | Probes en .NET |

---

## Tipos de Probes

| Endpoint              | Propósito                        | Cuándo devuelve 200                              |
| --------------------- | -------------------------------- | ------------------------------------------------ |
| `GET /health/live`    | Liveness — ¿está vivo?           | Siempre (excepto deadlock total)                 |
| `GET /health/ready`   | Readiness — ¿listo para tráfico? | DB accesible + dependencias críticas OK          |
| `GET /health/startup` | Startup — ¿completó arranque?    | Igual que readiness, solo durante inicialización |

**Usos por componente de infraestructura:**

- **Liveness**: ECS lo usa para decidir si reiniciar el contenedor
- **Readiness**: ALB lo usa para incluir/excluir la instancia del pool de routing
- **Startup**: Evita liveness failures durante el boot inicial del servicio

**Beneficios:**
✅ Failover automático sin intervención manual
✅ No enviar tráfico a instancias degradadas
✅ Auto-healing ante fallos de dependencias

---

## Implementación en .NET 8

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

// Liveness: proceso vivo aunque dependencias fallen
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

// Health check personalizado para Kafka
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

---

## Configuración en ECS Task Definition

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

La instrucción `HEALTHCHECK` a nivel Dockerfile está documentada en [Contenedores](../infraestructura/containerization.md).

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar liveness y readiness en todo servicio en contenedor
- **MUST** implementar startup probe en servicios con inicialización lenta (> 15s)
- **MUST** configurar health check en ECS Task Definition

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar checks específicos por dependencia (DB, cache, broker)
- **SHOULD** usar tags (`readiness`, `liveness`) para separar el scope de cada endpoint
- **SHOULD** mantener el liveness probe sin dependencias externas

### MUST NOT (Prohibido)

- **MUST NOT** usar un único endpoint genérico `/health` sin diferenciar liveness de readiness
- **MUST NOT** omitir health checks en ECS Task Definitions

---

## Referencias

- [ASP.NET Core Health Checks](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks)
- [AWS ALB — Health checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [Contenedores](../infraestructura/containerization.md)
- [Escalado Horizontal](./horizontal-scaling.md)
- [Resilience Patterns](./resilience-patterns.md)
