---
id: health-checks
sidebar_position: 7
title: Health Checks para Orchestration
description: Health checks para liveness, readiness y startup probes
---

# Health Checks para Orchestration

## Contexto

Este estándar define cómo implementar health checks para permitir que orchestradores (ECS, Kubernetes, ALB) detecten instancias no saludables y tomen acciones correctivas. Complementa el [lineamiento de Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md) especificando **cómo exponer el estado de salud** del servicio.

---

## Stack Tecnológico

| Componente         | Tecnología                     | Versión | Uso                             |
| ------------------ | ------------------------------ | ------- | ------------------------------- |
| **Framework**      | ASP.NET Core                   | 8.0+    | Framework base                  |
| **Health Checks**  | ASP.NET Core Health Checks     | 8.0+    | Built-in health checks          |
| **Database Check** | AspNetCore.HealthChecks.Npgsql | 7.0+    | PostgreSQL health check         |
| **Redis Check**    | AspNetCore.HealthChecks.Redis  | 7.0+    | Redis health check              |
| **Kafka Check**    | AspNetCore.HealthChecks.Kafka  | 7.0+    | Kafka health check              |
| **Orchestration**  | AWS ECS Fargate                | -       | Container orchestration         |
| **Load Balancer**  | AWS ALB                        | -       | Health checks y traffic routing |

---

## Implementación Técnica

### Tipos de Health Checks

```yaml
# ✅ 3 tipos de health checks

1. Liveness Probe:
  Pregunta: ¿Está el proceso vivo?
  Falla: Pod debe reiniciarse
  Ejemplo: /health/live

2. Readiness Probe:
  Pregunta: ¿Puede el servicio aceptar tráfico?
  Falla: Remover del load balancer (sin reiniciar)
  Ejemplo: /health/ready

3. Startup Probe:
  Pregunta: ¿Ha terminado la inicialización?
  Falla: Reiniciar (reemplaza liveness durante startup)
  Ejemplo: /health/startup
```

### Health Checks Básicos

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Agregar health checks
builder.Services.AddHealthChecks()
    // ✅ Liveness: solo verifica que el proceso responde
    .AddCheck("self", () => HealthCheckResult.Healthy(), tags: new[] { "live" })

    // ✅ Readiness: verifica dependencias críticas
    .AddNpgSql(
        connectionString: builder.Configuration.GetConnectionString("OrdersDb")!,
        name: "postgresql",
        failureStatus: HealthStatus.Unhealthy,
        tags: new[] { "ready", "db" })

    .AddRedis(
        redisConnectionString: builder.Configuration.GetConnectionString("Redis")!,
        name: "redis",
        failureStatus: HealthStatus.Degraded,  // ✅ No crítico, solo degraded
        tags: new[] { "ready", "cache" })

    .AddKafka(
        setup: kafka =>
        {
            kafka.BootstrapServers = builder.Configuration["Kafka:BootstrapServers"];
        },
        name: "kafka",
        failureStatus: HealthStatus.Degraded,
        tags: new[] { "ready", "messaging" });

var app = builder.Build();

// ✅ Exponer endpoints
app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    // ✅ Solo checks con tag "live"
    Predicate = check => check.Tags.Contains("live"),
    AllowCachingResponses = false
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready"),
    AllowCachingResponses = false,

    // ✅ Response writer detallado
    ResponseWriter = async (context, report) =>
    {
        context.Response.ContentType = "application/json";

        var response = new
        {
            status = report.Status.ToString(),
            checks = report.Entries.Select(entry => new
            {
                name = entry.Key,
                status = entry.Value.Status.ToString(),
                description = entry.Value.Description,
                duration = entry.Value.Duration.TotalMilliseconds,
                exception = entry.Value.Exception?.Message
            }),
            totalDuration = report.TotalDuration.TotalMilliseconds
        };

        await context.Response.WriteAsJsonAsync(response);
    }
});

app.Run();
```

### Custom Health Check

```csharp
// ✅ Health check personalizado
public class ExternalApiHealthCheck : IHealthCheck
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ExternalApiHealthCheck> _logger;

    public ExternalApiHealthCheck(
        IHttpClientFactory httpClientFactory,
        ILogger<ExternalApiHealthCheck> logger)
    {
        _httpClient = httpClientFactory.CreateClient("PaymentApi");
        _logger = logger;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // ✅ Llamar a endpoint de health del servicio externo
            var response = await _httpClient.GetAsync(
                "/health",
                cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                var responseTime = response.Headers.Age?.TotalMilliseconds ?? 0;

                return HealthCheckResult.Healthy(
                    description: $"Payment API is reachable. Response time: {responseTime}ms",
                    data: new Dictionary<string, object>
                    {
                        { "response_time_ms", responseTime },
                        { "status_code", (int)response.StatusCode }
                    });
            }

            _logger.LogWarning(
                "Payment API health check returned {StatusCode}",
                response.StatusCode);

            return HealthCheckResult.Degraded(
                description: $"Payment API returned {response.StatusCode}");
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Payment API health check failed");

            return HealthCheckResult.Unhealthy(
                description: "Payment API is unreachable",
                exception: ex);
        }
        catch (TaskCanceledException)
        {
            return HealthCheckResult.Unhealthy(
                description: "Payment API health check timed out");
        }
    }
}

// Registrar
builder.Services
    .AddHttpClient("PaymentApi", client =>
    {
        client.BaseAddress = new Uri(builder.Configuration["PaymentApi:BaseUrl"]!);
        client.Timeout = TimeSpan.FromSeconds(5);  // ✅ Timeout corto para health check
    });

builder.Services.AddHealthChecks()
    .AddCheck<ExternalApiHealthCheck>(
        name: "payment-api",
        failureStatus: HealthStatus.Degraded,  // ✅ No crítico
        tags: new[] { "ready", "external" });
```

### Database Health Check con Query

```csharp
// ✅ Health check con query específica
builder.Services.AddHealthChecks()
    .AddNpgSql(
        connectionString: builder.Configuration.GetConnectionString("OrdersDb")!,
        healthQuery: "SELECT 1;",  // ✅ Query simple para verificar conexión
        name: "postgresql-connection",
        failureStatus: HealthStatus.Unhealthy,
        tags: new[] { "ready", "db" })

    // ✅ Check adicional para verificar migrations
    .AddCheck("database-migrations", () =>
    {
        using var scope = app.Services.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<OrdersDbContext>();

        try
        {
            // ✅ Verificar que tabla principal existe
            var canConnect = context.Database.CanConnect();

            if (!canConnect)
            {
                return HealthCheckResult.Unhealthy("Cannot connect to database");
            }

            // ✅ Verificar pending migrations
            var pendingMigrations = context.Database.GetPendingMigrations().ToList();

            if (pendingMigrations.Any())
            {
                return HealthCheckResult.Degraded(
                    $"Database has {pendingMigrations.Count} pending migrations",
                    data: new Dictionary<string, object>
                    {
                        { "pending_migrations", string.Join(", ", pendingMigrations) }
                    });
            }

            return HealthCheckResult.Healthy("Database is up to date");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy(
                "Database migration check failed",
                exception: ex);
        }
    }, tags: new[] { "ready", "db" });
```

### Startup Health Check

```csharp
// ✅ Health check específico para startup
public class StartupHealthCheck : IHealthCheck
{
    private volatile bool _isReady;

    public bool IsReady
    {
        get => _isReady;
        set => _isReady = value;
    }

    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        return Task.FromResult(_isReady
            ? HealthCheckResult.Healthy("Application has started")
            : HealthCheckResult.Unhealthy("Application is starting"));
    }
}

// Program.cs
builder.Services.AddSingleton<StartupHealthCheck>();
builder.Services.AddHealthChecks()
    .AddCheck<StartupHealthCheck>(
        name: "startup",
        tags: new[] { "startup" });

var app = builder.Build();

// ✅ Inicialización asíncrona
var startupCheck = app.Services.GetRequiredService<StartupHealthCheck>();

// Warm up
await WarmUpAsync(app.Services);

// ✅ Marcar como ready
startupCheck.IsReady = true;

app.MapHealthChecks("/health/startup", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("startup")
});

async Task WarmUpAsync(IServiceProvider services)
{
    // Pre-cargar caché
    var cache = services.GetRequiredService<IDistributedCache>();
    await cache.GetStringAsync("warmup-key");

    // Verificar conexiones
    var db = services.GetRequiredService<OrdersDbContext>();
    await db.Database.CanConnectAsync();

    // Otras inicializaciones...
}
```

### AWS ECS Health Checks

```hcl
# Terraform - ECS Task Definition con health checks

resource "aws_ecs_task_definition" "orders_api" {
  family                   = "orders-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([{
    name      = "orders-api"
    image     = "ghcr.io/talma/orders-api:latest"
    essential = true

    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]

    # ✅ Container health check (Docker HEALTHCHECK)
    healthCheck = {
      command = [
        "CMD-SHELL",
        "curl -f http://localhost:8080/health/live || exit 1"
      ]
      interval    = 30      # ✅ Cada 30 segundos
      timeout     = 5       # ✅ Timeout 5 segundos
      retries     = 3       # ✅ 3 intentos antes de marcar unhealthy
      startPeriod = 60      # ✅ Grace period de 60s durante startup
    }

    environment = [
      { name = "ASPNETCORE_URLS", value = "http://+:8080" }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/orders-api"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# ✅ ECS Service con health check grace period
resource "aws_ecs_service" "orders_api" {
  name            = "orders-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.orders_api.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  # ✅ Health check grace period
  # ECS espera este tiempo antes de empezar health checks tras deployment
  health_check_grace_period_seconds = 120

  load_balancer {
    target_group_arn = aws_lb_target_group.orders_api.arn
    container_name   = "orders-api"
    container_port   = 8080
  }

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.orders_api.id]
    assign_public_ip = false
  }
}
```

### AWS ALB Target Group Health Checks

```hcl
# ✅ ALB Target Group con health checks
resource "aws_lb_target_group" "orders_api" {
  name        = "orders-api-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"  # Fargate usa IP targeting

  # ✅ Health check configuration
  health_check {
    enabled             = true
    path                = "/health/ready"  # ✅ Readiness check
    protocol            = "HTTP"
    port                = "traffic-port"
    healthy_threshold   = 2    # ✅ 2 checks consecutivos healthy
    unhealthy_threshold = 3    # ✅ 3 checks consecutivos unhealthy
    timeout             = 5    # ✅ Timeout 5 segundos
    interval            = 30   # ✅ Cada 30 segundos
    matcher             = "200"  # ✅ Esperar HTTP 200
  }

  # ✅ Deregistration delay
  deregistration_delay = 30  # ✅ 30s para completar requests en vuelo

  # ✅ Stickiness (opcional)
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400  # 24 horas
    enabled         = false
  }
}

# ✅ Listener rule
resource "aws_lb_listener_rule" "orders_api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.orders_api.arn
  }

  condition {
    path_pattern {
      values = ["/api/orders/*"]
    }
  }
}
```

### Métricas de Health Checks

```csharp
public class HealthCheckMetrics
{
    private readonly Counter<long> _healthCheckExecutions;
    private readonly Histogram<double> _healthCheckDuration;
    private readonly Gauge<int> _healthCheckStatus;

    public HealthCheckMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.HealthChecks");

        _healthCheckExecutions = meter.CreateCounter<long>(
            "healthcheck.executions", "executions");

        _healthCheckDuration = meter.CreateHistogram<double>(
            "healthcheck.duration", "ms");

        _healthCheckStatus = meter.CreateGauge<int>(
            "healthcheck.status", "status",
            "0=Unhealthy, 1=Degraded, 2=Healthy");
    }

    public void RecordExecution(string checkName, HealthStatus status, TimeSpan duration)
    {
        var tags = new[]
        {
            new KeyValuePair<string, object?>("check_name", checkName),
            new KeyValuePair<string, object?>("status", status.ToString())
        };

        _healthCheckExecutions.Add(1, tags);
        _healthCheckDuration.Record(duration.TotalMilliseconds, tags);

        var statusValue = status switch
        {
            HealthStatus.Healthy => 2,
            HealthStatus.Degraded => 1,
            _ => 0
        };

        _healthCheckStatus.Record(statusValue,
            new KeyValuePair<string, object?>("check_name", checkName));
    }
}

// Instrumentar health checks
builder.Services.Configure<HealthCheckPublisherOptions>(options =>
{
    options.Delay = TimeSpan.FromSeconds(5);
    options.Period = TimeSpan.FromSeconds(30);
});

builder.Services.AddSingleton<IHealthCheckPublisher, MetricsHealthCheckPublisher>();

public class MetricsHealthCheckPublisher : IHealthCheckPublisher
{
    private readonly HealthCheckMetrics _metrics;
    private readonly ILogger<MetricsHealthCheckPublisher> _logger;

    public Task PublishAsync(HealthReport report, CancellationToken cancellationToken)
    {
        foreach (var entry in report.Entries)
        {
            _metrics.RecordExecution(
                entry.Key,
                entry.Value.Status,
                entry.Value.Duration);

            if (entry.Value.Status != HealthStatus.Healthy)
            {
                _logger.LogWarning(
                    "Health check {CheckName} is {Status}: {Description}",
                    entry.Key,
                    entry.Value.Status,
                    entry.Value.Description);
            }
        }

        return Task.CompletedTask;
    }
}

// PromQL queries
/*
# Health check failure rate
rate(healthcheck_executions_total{status!="Healthy"}[5m])

# Health check duration P95
histogram_quantile(0.95, sum(rate(healthcheck_duration_bucket[5m])) by (le, check_name))

# Current health status (0=Unhealthy, 1=Degraded, 2=Healthy)
healthcheck_status{check_name="postgresql"}
*/
```

### Grafana Alerting

```yaml
# Alertas para health checks

# ✅ Alerta cuando servicio está unhealthy
groups:
  - name: health_checks
    interval: 30s
    rules:
      - alert: ServiceUnhealthy
        expr: healthcheck_status{check_name="self"} == 0
        for: 2m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "Service {{ $labels.service }} is unhealthy"
          description: "Liveness check failing for {{ $labels.service }}"

      - alert: DependencyUnhealthy
        expr: healthcheck_status{check_name=~"postgresql|redis|kafka"} == 0
        for: 3m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Dependency {{ $labels.check_name }} is unhealthy"
          description: "Health check {{ $labels.check_name }} has been unhealthy for 3 minutes"

      - alert: HealthCheckSlowResponse
        expr: histogram_quantile(0.95, sum(rate(healthcheck_duration_bucket[5m])) by (le, check_name)) > 5000
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Health check {{ $labels.check_name }} is slow"
          description: "P95 latency is {{ $value }}ms (threshold: 5000ms)"
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** exponer endpoint `/health/live` para liveness probe
- **MUST** exponer endpoint `/health/ready` para readiness probe
- **MUST** verificar dependencias críticas en readiness check (DB, cache)
- **MUST** retornar HTTP 200 cuando healthy, 503 cuando unhealthy
- **MUST** configurar health checks en ALB target groups
- **MUST** configurar health checks en ECS task definitions
- **MUST** usar timeouts cortos en health checks (< 5s)
- **MUST** monitorear health check failure rate

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir response body con detalle de checks
- **SHOULD** usar diferentes tags para liveness vs readiness
- **SHOULD** configurar startup probe para aplicaciones con inicialización lenta
- **SHOULD** usar `HealthStatus.Degraded` para dependencias no críticas
- **SHOULD** incluir métricas de health check duration
- **SHOULD** configurar alarmas cuando health checks fallan
- **SHOULD** implementar health check grace period en ECS

### MAY (Opcional)

- **MAY** exponer `/health/startup` para startup probe
- **MAY** incluir metadata adicional en response (version, uptime)
- **MAY** implementar health checks para servicios externos
- **MAY** usar health check UI para visualización

### MUST NOT (Prohibido)

- **MUST NOT** incluir lógica pesada en liveness check
- **MUST NOT** verificar dependencias en liveness (solo en readiness)
- **MUST NOT** exponer información sensible en health check response
- **MUST NOT** omitir health checks en servicios productivos
- **MUST NOT** usar timeouts largos (> 10s) en health checks
- **MUST NOT** cachear responses de health checks
- **MUST NOT** incluir autenticación en health check endpoints

---

## Referencias

- [Lineamiento: Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md)
- [ADR-007: AWS ECS Fargate para contenedores](../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- Estándares relacionados:
  - [Circuit Breaker](circuit-breaker.md)
  - [Graceful Degradation](graceful-degradation.md)
- Especificaciones:
  - [ASP.NET Core Health Checks](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks)
  - [AspNetCore.Diagnostics.HealthChecks](https://github.com/Xabaril/AspNetCore.Diagnostics.HealthChecks)
  - [ECS Health Checks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html#container_definition_healthcheck)
  - [ALB Health Checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
