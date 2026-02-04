---
id: graceful-shutdown
sidebar_position: 4
title: Apagado Elegante (Graceful Shutdown)
description: Estándar para implementación de graceful shutdown con SIGTERM handling, lifecycle hooks, connection draining y completado de requests en proceso
---

# Estándar Técnico — Apagado Elegante (Graceful Shutdown)

---

## 1. Propósito

Garantizar zero-downtime deployments y prevenir pérdida de datos mediante shutdown elegante que completa requests en proceso, cierra conexiones limpiamente y libera recursos correctamente antes de terminar el proceso.

---

## 2. Alcance

**Aplica a:**

- APIs REST en contenedores
- Workers de procesamiento
- Consumers de Kafka
- Servicios en AWS ECS Fargate
- Background services
- gRPC servers

**No aplica a:**

- Lambda functions (serverless)
- Batch jobs de corta duración (<5s)
- Servicios sin estado externo

---

## 3. Tecnologías Aprobadas

| Componente         | Tecnología      | Versión mínima | Observaciones            |
| ------------------ | --------------- | -------------- | ------------------------ |
| **Runtime**        | .NET            | 8.0+           | IHostApplicationLifetime |
| **Load Balancer**  | AWS ALB         | -              | Connection draining      |
| **Database**       | Npgsql          | 8.0+           | Connection close         |
| **Message Broker** | MassTransit     | 8.0+           | Consumer stop            |
| **gRPC**           | Grpc.AspNetCore | 2.60+          | Server shutdown          |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Manejo de Señales

- [ ] Escuchar **SIGTERM** (no solo SIGKILL)
- [ ] Timeout de shutdown: 30-90 segundos
- [ ] Marcar servicio como "not ready" inmediatamente
- [ ] Esperar a que load balancer deje de enviar tráfico (10-15s)

### Completado de Requests

- [ ] Completar requests HTTP en proceso
- [ ] Esperar a consumers de Kafka terminen processing
- [ ] Finalizar background tasks en curso
- [ ] Timeout para forzar shutdown si tarda mucho

### Cierre de Conexiones

- [ ] Cerrar conexiones de database limpiamente
- [ ] Desconectar de message brokers
- [ ] Cerrar conexiones Redis
- [ ] Flush de logs pendientes

### Health Checks

- [ ] `/health/ready` retorna 503 durante shutdown
- [ ] `/health/live` sigue retornando 200 (proceso activo)
- [ ] Load balancer deja de enviar tráfico basado en readiness

### Telemetría

- [ ] Log de inicio de shutdown
- [ ] Log de finalización exitosa
- [ ] Métricas de shutdown duration
- [ ] Alertas si shutdown timeout excedido

---

## 5. Prohibiciones

- ❌ Terminar proceso sin esperar requests en proceso
- ❌ No escuchar SIGTERM (solo catch SIGKILL)
- ❌ Shutdown timeout muy largo (>120s)
- ❌ No marcar como not-ready antes de shutdown
- ❌ No cerrar conexiones DB/Redis
- ❌ Forzar terminación sin cleanup
- ❌ No logging de eventos de shutdown

---

## 6. Configuración Mínima

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// Obtener lifetime para registrar shutdown
var lifetime = app.Services.GetRequiredService<IHostApplicationLifetime>();
var logger = app.Services.GetRequiredService<ILogger<Program>>();

// Registrar handler para SIGTERM
lifetime.ApplicationStopping.Register(() =>
{
    logger.LogInformation("Received SIGTERM. Starting graceful shutdown...");

    // 1. Marcar como not-ready
    HealthCheckService.IsShuttingDown = true;

    // 2. Esperar a que load balancer deje de enviar tráfico
    logger.LogInformation("Waiting for load balancer to drain connections...");
    Thread.Sleep(TimeSpan.FromSeconds(15));

    logger.LogInformation("Ready to shutdown");
});

lifetime.ApplicationStopped.Register(() =>
{
    logger.LogInformation("Application stopped gracefully");
});

// Health checks
app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("live")
});

app.Run();

public static class HealthCheckService
{
    public static bool IsShuttingDown { get; set; } = false;
}

public class ReadinessHealthCheck : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        if (HealthCheckService.IsShuttingDown)
            return Task.FromResult(HealthCheckResult.Unhealthy("Shutting down"));

        return Task.FromResult(HealthCheckResult.Healthy());
    }
}
```

```yaml
# Kubernetes deployment.yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: payment-service
          image: talma/payment-service:v1.0.0
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"] # Esperar drain
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
      terminationGracePeriodSeconds: 90 # Tiempo para graceful shutdown
```

---

## 7. Ejemplos

### Graceful shutdown con background service

```csharp
public class OrderProcessorService : BackgroundService
{
    private readonly ILogger<OrderProcessorService> _logger;
    private readonly IServiceProvider _serviceProvider;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Order processor started");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessNextOrderAsync(stoppingToken);
            }
            catch (OperationCanceledException)
            {
                _logger.LogInformation("Processing cancelled. Shutting down gracefully...");
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing order");
            }
        }

        _logger.LogInformation("Order processor stopped");
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Stopping order processor...");

        // Esperar a que operación actual termine (con timeout)
        await base.StopAsync(cancellationToken);

        _logger.LogInformation("Order processor stopped gracefully");
    }
}
```

### Kafka consumer con graceful shutdown

```csharp
public class KafkaConsumerService : BackgroundService
{
    private readonly IConsumer<string, OrderEvent> _consumer;
    private readonly ILogger<KafkaConsumerService> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe("orders");
        _logger.LogInformation("Kafka consumer started");

        try
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                var consumeResult = _consumer.Consume(stoppingToken);

                // Procesar mensaje
                await ProcessOrderAsync(consumeResult.Message.Value, stoppingToken);

                // Commit offset solo si procesamiento exitoso
                _consumer.Commit(consumeResult);
            }
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation("Consumer cancelled. Closing gracefully...");
        }
        finally
        {
            _consumer.Close(); // Commit final y desconexión limpia
            _logger.LogInformation("Consumer closed");
        }
    }
}
```

### ASP.NET Core con DbContext disposal

```csharp
public class ApplicationDbContext : DbContext, IAsyncDisposable
{
    private readonly ILogger<ApplicationDbContext> _logger;

    public override void Dispose()
    {
        _logger.LogDebug("Disposing DbContext");
        base.Dispose();
    }

    public override async ValueTask DisposeAsync()
    {
        _logger.LogDebug("Disposing DbContext asynchronously");
        await base.DisposeAsync();
    }
}

// Program.cs
var lifetime = app.Services.GetRequiredService<IHostApplicationLifetime>();

lifetime.ApplicationStopping.Register(() =>
{
    // Cerrar todas las conexiones de DbContext activas
    var dbContexts = app.Services.GetServices<ApplicationDbContext>();
    foreach (var context in dbContexts)
    {
        context.Dispose();
    }
});
```

---

## 8. Validación y Auditoría

```bash
# Simular SIGTERM en local
docker run -d --name test-shutdown payment-service
sleep 5
docker stop test-shutdown  # Envía SIGTERM
docker logs test-shutdown | grep "graceful shutdown"

# Kubernetes - verificar terminationGracePeriodSeconds
kubectl get deployment payment-service -o yaml | grep terminationGracePeriodSeconds

# Verificar readiness probe durante shutdown
kubectl rollout restart deployment/payment-service
watch kubectl get pods  # Ver que pods terminan gracefully
```

**Métricas de cumplimiento:**

| Métrica                        | Umbral   | Verificación       |
| ------------------------------ | -------- | ------------------ |
| Services con graceful shutdown | 100%     | Code review        |
| Shutdown duration              | <30s p99 | Métricas           |
| Failed shutdowns               | <0.1%    | Logs/alertas       |
| Zero-downtime deployments      | 100%     | Deployment metrics |

**Checklist de auditoría:**

- [ ] SIGTERM handler registrado
- [ ] Readiness probe configurado
- [ ] terminationGracePeriodSeconds ≥ 30s
- [ ] preStop hook con delay
- [ ] Conexiones DB/Redis cerradas
- [ ] Logs de shutdown events

---

## 9. Referencias

- [Kubernetes Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [AWS ECS Container Shutdown](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/graceful-shutdown.html)
- [ASP.NET Core Shutdown](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/host/generic-host#shutdown)
- [12-Factor App - Disposability](https://12factor.net/disposability)
- [Google SRE - Graceful Shutdown](https://sre.google/workbook/eliminating-toil/)
- [Release It! - Stability Patterns](https://pragprog.com/titles/mnee2/release-it-second-edition/)
