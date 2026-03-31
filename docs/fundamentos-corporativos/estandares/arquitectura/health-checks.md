---
id: health-checks
sidebar_position: 10
title: Health Checks
description: Implementación de health check endpoints en .NET 8 para ECS, EC2, Docker e IIS con ALB, nginx/HAProxy y ARR.
tags: [arquitectura, infraestructura, health-checks, resiliencia, ecs, ec2, iis]
---

# Health Checks

## Contexto

Este estándar define la implementación de health checks para permitir que el load balancer y el orquestador determinen el estado de cada instancia y tomen decisiones automáticas de routing, reinicio y failover. Aplica a cualquier servicio independientemente de la plataforma de despliegue: **ECS**, **EC2**, **Docker** (on-premise o en EC2) o **servicios en IIS**.

Complementa los lineamientos [Escalabilidad y Rendimiento](../../lineamientos/arquitectura/escalabilidad-y-rendimiento.md) y [Resiliencia y Disponibilidad](../../lineamientos/arquitectura/resiliencia-y-disponibilidad.md).

**Conceptos incluidos:**

- **Liveness** → ¿Está el proceso vivo?
- **Readiness** → ¿Puede recibir tráfico?

---

## Stack Tecnológico

| Componente        | Tecnología                                    | Versión | Uso            |
| ----------------- | --------------------------------------------- | ------- | -------------- |
| **Health Checks** | Microsoft.Extensions.Diagnostics.HealthChecks | 8.0+    | Probes en .NET |

---

## Tipos de Probes

| Endpoint            | Propósito                        | Cuándo devuelve 200                     |
| ------------------- | -------------------------------- | --------------------------------------- |
| `GET /health/live`  | Liveness — ¿está vivo?           | Siempre (excepto deadlock total)        |
| `GET /health/ready` | Readiness — ¿listo para tráfico? | DB accesible + dependencias críticas OK |

**Usos por plataforma:**

| Plataforma | `GET /health/live`                                         | `GET /health/ready`                                 |
| ---------- | ---------------------------------------------------------- | --------------------------------------------------- |
| **ECS**    | `health_check` en Task Definition → reinicia el contenedor | ALB Target Group → incluye/excluye del pool         |
| **EC2**    | Monitoreo externo o CloudWatch                             | ALB Target Group → incluye/excluye del pool         |
| **Docker** | `HEALTHCHECK` en Dockerfile → Docker Engine                | nginx / HAProxy upstream check                      |
| **IIS**    | Monitoreo externo                                          | ARR / ALB probe + Application Initialization Module |

**Códigos HTTP de respuesta:**

| Estado ASP.NET Core | Liveness | Readiness             |
| ------------------- | -------- | --------------------- |
| `Healthy`           | 200      | 200                   |
| `Degraded`          | 200      | **503** ← configurado |
| `Unhealthy`         | 503      | 503                   |

Por defecto, ASP.NET Core devuelve 200 para `Degraded`. En el readiness probe se configura explícitamente `ResultStatusCodes` para que una instancia degradada salga del pool del ALB en lugar de seguir recibiendo tráfico.

**Beneficios:**
✅ Failover automático sin intervención manual
✅ No enviar tráfico a instancias degradadas
✅ Auto-healing ante fallos de dependencias

---

## Implementación en .NET 8

```csharp
// Program.cs
using System.Text.Json;

// ResponseWriter con JSON estructurado (facilita debugging y observabilidad)
static Task WriteJsonResponse(HttpContext context, HealthReport report)
{
    context.Response.ContentType = "application/json";
    var result = JsonSerializer.Serialize(new
    {
        status   = report.Status.ToString(),
        duration = report.TotalDuration,
        checks   = report.Entries.Select(e => new
        {
            name        = e.Key,
            status      = e.Value.Status.ToString(),
            description = e.Value.Description,
            duration    = e.Value.Duration
        })
    });
    return context.Response.WriteAsync(result);
}

builder.Services.AddHealthChecks()
    .AddNpgSql(
        connectionString,
        name: "database",
        tags: ["readiness"])
    .AddRedis(
        redisConnectionString,
        name: "redis",
        tags: ["readiness"])
    .AddCheck<KafkaHealthCheck>(
        "kafka",
        tags: ["readiness"])
    .AddCheck<ShutdownHealthCheck>(    // Ver sección Graceful Shutdown
        "shutdown",
        tags: ["readiness"]);

// Liveness: proceso vivo aunque dependencias fallen
app.UseHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate      = _ => false,       // Solo verifica que el proceso responde
    ResponseWriter = WriteJsonResponse
});

// Readiness: dependencias OK + no está en shutdown; Degraded → 503
app.UseHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate      = check => check.Tags.Contains("readiness"),
    ResponseWriter = WriteJsonResponse,
    ResultStatusCodes =
    {
        [HealthStatus.Healthy]   = StatusCodes.Status200OK,
        [HealthStatus.Degraded]  = StatusCodes.Status503ServiceUnavailable,
        [HealthStatus.Unhealthy] = StatusCodes.Status503ServiceUnavailable
    }
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
        return Task.Run(() =>
        {
            try
            {
                var metadata = _producer.GetMetadata(allTopics: false, timeout: TimeSpan.FromSeconds(5));
                return metadata.Brokers.Count > 0
                    ? HealthCheckResult.Healthy("Kafka broker reachable")
                    : HealthCheckResult.Degraded("No brokers available");
            }
            catch (Exception ex)
            {
                return HealthCheckResult.Unhealthy("Kafka unreachable", ex);
            }
        }, cancellationToken);
    }
}
```

---

## Graceful Shutdown

Cuando la plataforma señala al proceso que debe terminar, la instancia debe salir del pool del load balancer **antes** de que el proceso finalice para evitar errores 5xx en vuelo. El `ShutdownHealthCheck` es el mismo en todas las plataformas — lo que varía es el mecanismo de señalización y dónde se configura el timeout.

**Secuencia (todas las plataformas):**

1. La plataforma señala el shutdown (SIGTERM en Linux/Docker/ECS, ANCM en IIS)
2. `ShutdownHealthCheck` devuelve `Unhealthy` → `/health/ready` responde 503
3. El load balancer deja de enrutar nuevas conexiones a esta instancia
4. El período de drain drena las conexiones activas
5. El proceso finaliza limpiamente

```csharp
// ShutdownHealthCheck.cs
public class ShutdownHealthCheck : IHealthCheck
{
    private readonly IHostApplicationLifetime _lifetime;

    public ShutdownHealthCheck(IHostApplicationLifetime lifetime)
        => _lifetime = lifetime;

    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        return _lifetime.ApplicationStopping.IsCancellationRequested
            ? Task.FromResult(HealthCheckResult.Unhealthy("Shutting down"))
            : Task.FromResult(HealthCheckResult.Healthy());
    }
}
```

**Coordinación de tiempos por plataforma:**

| Plataforma | Timeout del proceso                                        | Período de drain                        |
| ---------- | ---------------------------------------------------------- | --------------------------------------- |
| **ECS**    | `stop_timeout` en Task Definition (recomendado: 35s)       | ALB `deregistrationDelay` (default 30s) |
| **EC2**    | `ASPNETCORE_SHUTDOWNTIMEOUTSECONDS` en el proceso          | ALB `deregistrationDelay` (default 30s) |
| **Docker** | `docker stop --time` (default 10s — aumentar a 35s)        | nginx/HAProxy drain config              |
| **IIS**    | `shutdownTimeLimit` en ANCM (default 10s — aumentar a 35s) | ARR drain / ALB `deregistrationDelay`   |

Para IIS, configurar el timeout de shutdown en `web.config`:

```xml
<!-- web.config — dar tiempo al ARR/ALB para drenar antes de terminar el proceso -->
<aspNetCore processPath="dotnet" arguments="./MyApp.dll">
  <handlerSettings>
    <handlerSetting name="shutdownTimeLimit" value="35" />
  </handlerSettings>
</aspNetCore>
```

---

## Configuración por Plataforma

### ECS

```yaml
# ECS Task Definition — health_check apunta a liveness; el ALB Target Group sondea readiness
container_definitions:
  health_check:
    command:
      ["CMD-SHELL", "curl -f http://localhost:8080/health/live || exit 1"]
    interval: 30
    timeout: 5
    retries: 3
    start_period: 60 # Evita fallos prematuros en servicios con arranque lento
  stop_timeout: 35 # Mayor que el deregistrationDelay del ALB Target Group (default 30s)
```

### EC2

El ALB Target Group sondea directamente el endpoint de readiness. No existe un mecanismo de reinicio automático del proceso equivalente al Task Definition — se complementa con CloudWatch Alarms o Auto Scaling health checks para detectar instancias en mal estado.

```json
// AWS ALB Target Group — HealthCheckPath apunta a /health/ready
{
  "HealthCheckPath": "/health/ready",
  "HealthCheckIntervalSeconds": 30,
  "HealthCheckTimeoutSeconds": 5,
  "HealthyThresholdCount": 2,
  "UnhealthyThresholdCount": 3,
  "Matcher": { "HttpCode": "200" }
}
```

### Docker

```dockerfile
# Dockerfile — Docker Engine reinicia el contenedor si liveness falla
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/health/live || exit 1
```

Configurar el load balancer upstream apuntando a `/health/ready`:

```
# HAProxy — excluye instancias degradadas del pool
backend myservice
    option httpchk GET /health/ready
    http-check expect status 200
    server app1 127.0.0.1:8080 check inter 30s fall 3 rise 2
```

### IIS

IIS utiliza el módulo **Application Initialization** para calentar el servicio antes de recibir tráfico, y **Application Request Routing (ARR)** o el ALB para excluir instancias del pool de routing.

```xml
<!-- web.config — calentar la aplicación antes de recibir tráfico externo -->
<system.webServer>
  <applicationInitialization doAppInitAfterRestart="true">
    <add initializationPage="/health/ready" hostName="localhost" />
  </applicationInitialization>
</system.webServer>
```

ARR sondea `/health/ready` del mismo modo que el ALB Target Group: configurar el health probe en el servidor ARR con intervalo de 30s y respuesta esperada HTTP 200.

---

La instrucción `HEALTHCHECK` a nivel Dockerfile está documentada en [Contenedores](../infraestructura/containerization.md).

---

## Observabilidad

Los health checks deben publicar métricas hacia el stack de observabilidad para generar alertas cuando una dependencia falla de forma recurrente, antes de que el orquestador intervenga.

```csharp
// Program.cs — publicar estado de health checks como métricas
builder.Services.Configure<HealthCheckPublisherOptions>(options =>
{
    options.Delay  = TimeSpan.FromSeconds(5);
    options.Period = TimeSpan.FromSeconds(30);
});
```

Integrar con [AspNetCore.Diagnostics.HealthChecks](https://github.com/Xabaril/AspNetCore.Diagnostics.HealthChecks) para exportar el estado de cada check como métrica hacia Mimir/Prometheus. Configura alertas en Grafana cuando `aspnetcore_healthcheck_status{name="database"} != 1`.

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar liveness y readiness en todo servicio, independientemente de la plataforma de despliegue
- **MUST** registrar `/health/ready` en el load balancer o proxy correspondiente (ALB Target Group, ARR, HAProxy)
- **MUST** configurar `ResultStatusCodes` para que `Degraded` → 503 en el readiness probe
- **MUST** implementar `ShutdownHealthCheck` para garantizar graceful shutdown sin errores 5xx en vuelo
- **MUST** configurar el timeout de shutdown del proceso mayor que el período de drain del load balancer en cada plataforma

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar checks específicos por dependencia (DB, cache, broker)
- **SHOULD** usar tags (`readiness`) para separar el scope de cada endpoint
- **SHOULD** mantener el liveness probe sin dependencias externas
- **SHOULD** usar `ResponseWriter` con JSON estructurado para facilitar debugging y observabilidad
- **SHOULD** publicar métricas de health checks vía `IHealthCheckPublisher` hacia Grafana/Mimir

### MUST NOT (Prohibido)

- **MUST NOT** usar un único endpoint genérico `/health` sin diferenciar liveness de readiness
- **MUST NOT** omitir la configuración del health check en la plataforma de despliegue (Task Definition en ECS, `HEALTHCHECK` en Dockerfile, ARR en IIS)
- **MUST NOT** exponer los endpoints `/health/*` al internet público; deben ser accesibles solo desde la VPC, la red interna o el load balancer

---

## Referencias

- [ASP.NET Core Health Checks](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks)
- [AWS ALB — Health checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [AWS ECS — Container health check](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#container_definition_healthcheck)
- [IIS Application Initialization Module](https://learn.microsoft.com/en-us/iis/get-started/whats-new-in-iis-8/iis-80-application-initialization)
- [ASP.NET Core Module (ANCM) — shutdownTimeLimit](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/aspnet-core-module)
- [AspNetCore.Diagnostics.HealthChecks](https://github.com/Xabaril/AspNetCore.Diagnostics.HealthChecks)
- [Contenedores](../infraestructura/containerization.md)
- [Escalado Horizontal](./horizontal-scaling.md)
- [Resilience Patterns](./resilience-patterns.md)
