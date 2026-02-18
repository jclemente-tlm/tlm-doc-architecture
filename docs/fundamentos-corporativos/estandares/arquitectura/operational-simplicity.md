---
id: operational-simplicity
sidebar_position: 11
title: Operational Simplicity
description: Diseñar sistemas fáciles de operar, mantener y diagnosticar
---

# Operational Simplicity

## Contexto

Este estándar prioriza **simplicidad operacional**: sistemas fáciles de **debuggear, monitorear y mantener**. Diseñar para operadores (incluye developers de guardia), no solo para elegancia arquitectónica. Complementa el [lineamiento de Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md) asegurando **operabilidad**.

---

## Principios

```yaml
# ✅ Operational Simplicity = Fácil operar en producción

Key Questions (diseño):
  - "¿Cómo debuggeo si falla en producción?"
  - "¿Cómo sé si está healthy?"
  - "¿Cuánto tarda rollback?"
  - "¿Puedo diagnosticar sin acceso al código?"
  - "¿Necesito ser experto para resolver incident?"

Characteristics:
  ✅ Observable: Logs, metrics, traces claros
  ✅ Debuggable: Errores con contexto suficiente
  ✅ Recoverable: Fácil restart, rollback
  ✅ Predictable: Comportamiento consistente
  ✅ Self-healing: Reintentos, circuit breakers
  ✅ Documented: Runbooks para incidents comunes

Anti-Patterns:
  ❌ "Funciona en mi máquina" (no en prod)
  ❌ Logs crípticos: "Error 500" (sin stack trace)
  ❌ Debugging requiere attach debugger a prod
  ❌ Rollback tarda 2 horas (proceso manual)
  ❌ Solo 1 persona sabe cómo funciona
```

## Observability Checklist

```yaml
# ✅ Cada servicio DEBE tener

1. Health Checks:
   - /health/live (¿proceso vivo?)
   - /health/ready (¿puede recibir tráfico?)
   - /health/startup (¿inicialización completa?)

   Kubernetes usa estos para restart automático

2. Structured Logging:
   - JSON format (parseable)
   - CorrelationId (trace request cross-service)
   - Log level apropiado:
       ERROR: Requiere acción inmediata
       WARN: Problema potencial, monitorear
       INFO: High-level flow
       DEBUG: Detalles (solo troubleshooting)

   ❌ Mal: "Error occurred"
   ✅ Bien: { level: "ERROR", message: "Failed to save order",
             correlationId: "abc-123", orderId: "guid",
             exception: "SqlException: Timeout", timestamp: "..." }

3. Metrics (Prometheus format):
   - Request rate (requests/second)
   - Error rate (errors/requests)
   - Latency (p50, p95, p99)
   - Saturation (CPU, memory, DB connections)

   Dashboards: Grafana

4. Distributed Tracing (si microservices):
   - OpenTelemetry
   - Propagate trace context (W3C Trace Context)
   - Jaeger or AWS X-Ray

5. Alerting:
   - Error rate > 5% (5 min)
   - p95 latency > 500ms (5 min)
   - Health check failing (1 min)
   - CPU > 80% (10 min)

   CloudWatch Alarms → SNS → Slack / PagerDuty
```

## Example: Debuggable Error

```csharp
// ❌ MAL: Error sin contexto

public async Task<Guid> CreateOrderAsync(CreateOrderCommand command)
{
    try
    {
        var order = Order.Create(command.CustomerId);
        await _orderRepo.SaveAsync(order);
        return order.OrderId;
    }
    catch (Exception ex)
    {
        _logger.LogError("Error");  // ❌ Inútil
        throw;
    }
}

// Producción: "Error" en logs
// Operador: ¿Qué pasó? ¿Qué orden? ¿Qué usuario?

// ✅ BIEN: Error con contexto

public async Task<Guid> CreateOrderAsync(CreateOrderCommand command)
{
    var correlationId = Activity.Current?.Id ?? Guid.NewGuid().ToString();

    _logger.LogInformation(
        "Creating order for customer {CustomerId} with {ItemCount} items. CorrelationId: {CorrelationId}",
        command.CustomerId, command.Items.Count, correlationId);

    try
    {
        var order = Order.Create(command.CustomerId);

        foreach (var item in command.Items)
        {
            order.AddLine(item.ProductId, item.Quantity, item.UnitPrice);
        }

        await _orderRepo.SaveAsync(order);

        _logger.LogInformation(
            "Order {OrderId} created successfully. CorrelationId: {CorrelationId}",
            order.OrderId, correlationId);

        return order.OrderId;
    }
    catch (SqlException ex) when (ex.Number == -2)  // Timeout
    {
        _logger.LogError(ex,
            "Database timeout saving order for customer {CustomerId}. CorrelationId: {CorrelationId}",
            command.CustomerId, correlationId);
        throw new OrderServiceException("Database timeout", ex);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex,
            "Unexpected error creating order for customer {CustomerId}. CorrelationId: {CorrelationId}",
            command.CustomerId, correlationId);
        throw;
    }
}

// Producción: Log completo con:
// - CustomerId (identificar cliente afectado)
// - ItemCount (contexto del caso)
// - CorrelationId (trace completo)
// - Exception details (stack trace)
// Operador: Toda info necesaria para diagnosticar
```

## Deployment Simplicity

```yaml
# ✅ Deployments seguros y rápidos

Requirements:
  1. Automated (CI/CD, no manual)
  2. Fast (< 10 min end-to-end)
  3. Rollback rápido (< 2 min)
  4. Zero-downtime (blue-green or rolling)
  5. Smoke tests post-deploy

Example (GitHub Actions + ECS):

Deploy Pipeline:
  1. Trigger: Push to main branch
  2. Build: Docker image (3 min)
  3. Test: Unit + Integration (2 min)
  4. Push: ECR (1 min)
  5. Deploy: ECS rolling update (3 min)
  6. Smoke test: Health check + critical endpoints (1 min)

  Total: ~10 min

Rollback Strategy:
  - ECS: Deploy previous task definition (1 min)
  - Trigger: Manual or automatic (if smoke tests fail)

  "aws ecs update-service --service sales-api --task-definition sales-api:42"

Zero-Downtime:
  - ECS rolling update:
      1. Start new tasks (new version)
      2. Wait for health check pass
      3. Drain connections from old tasks
      4. Stop old tasks

  Result: No requests dropped

Smoke Tests:
  ✅ GET /health → 200 OK
  ✅ POST /api/orders (test order) → 201 Created
  ✅ Query PostgreSQL → Connection OK
  ✅ Publish to Kafka → Success

  Si falla: Rollback automático
```

## Configuration Management

```yaml
# ✅ Config simple y seguro

Principles:
  1. 12-Factor App: Config in environment (not code)
  2. Secrets in AWS Secrets Manager (not plaintext)
  3. Non-secrets in AWS Parameter Store
  4. Validation at startup (fail fast)

Example (Sales Service):

# docker-compose.override.yml (local)
environment:
  - ConnectionStrings__SalesDb=Host=localhost;Database=sales_dev
  - Kafka__BootstrapServers=localhost:9092
  - Features__EnableDiscounts=true

# ECS Task Definition (production)
environment:
  - Environment=Production
  - Kafka__BootstrapServers=kafka.talma.internal:9092

secrets:  # ✅ Secrets Manager
  - name: ConnectionStrings__SalesDb
    valueFrom: arn:aws:secretsmanager:...:secret:sales/db-connection
  - name: Kafka__SaslPassword
    valueFrom: arn:aws:secretsmanager:...:secret:sales/kafka-password

# Startup validation (C#)
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        var config = Configuration.GetSection("ConnectionStrings");

        // ✅ Validate required config at startup
        if (string.IsNullOrEmpty(config["SalesDb"]))
            throw new InvalidOperationException("ConnectionStrings:SalesDb required");

        services.AddDbContext<SalesDbContext>(opts =>
            opts.UseNpgsql(config["SalesDb"]));
    }
}

# Result: App fails to start if config missing (fail fast)
# Operador: Error claro en logs, fácil fix
```

## Runbooks

````yaml
# ✅ Documentar procedimientos operacionales

Runbook Structure:

# Sales Service Runbooks

## HIGH Error Rate (> 5%)

Symptoms:
  - CloudWatch alarm "sales-api-error-rate" triggered
  - Grafana dashboard shows spike in 5xx errors
  - Users reporting orden creation failures

Investigation:
  1. Check CloudWatch Logs Insights:
     ```
     fields @timestamp, @message, exception
     | filter level = "ERROR"
     | sort @timestamp desc
     | limit 20
     ```

  2. Identify error pattern:
     - Database timeout? → Check RDS performance
     - Kafka timeout? → Check MSK metrics
     - Validation error? → Check recent changes

  3. Check recent deployments:
     - GitHub: Last commit deployed?
     - ECS: Task definition version?

Resolution:
  - If bad deploy: Rollback (see Rollback procedure)
  - If database issue: Scale RDS or optimize queries
  - If dependency down: Contact responsible team

## Rollback Procedure

When: Deploy introduced critical bug

Steps:
  1. Get previous task definition:
     ```bash
     aws ecs describe-services --cluster prod --service sales-api
     # Note previous taskDefinition: sales-api:42
     ```

  2. Rollback:
     ```bash
     aws ecs update-service --cluster prod --service sales-api \
       --task-definition sales-api:42 --force-new-deployment
     ```

  3. Monitor:
     - ECS: New tasks starting
     - Logs: Errors decreasing
     - Metrics: Error rate back to normal

  4. Notify: Slack #incidents channel

  Time: ~2 min

## Database Connection Pool Exhausted

Symptoms:
  - Errors: "Timeout expired. The timeout period elapsed..."
  - Metrics: ActiveConnections = MaxPoolSize (100)

Investigation:
  1. Check long-running queries:
     ```sql
     SELECT pid, now() - query_start AS duration, query
     FROM pg_stat_activity
     WHERE state = 'active'
     ORDER BY duration DESC;
     ```

  2. Kill if necessary:
     ```sql
     SELECT pg_terminate_backend(pid);
     ```

Resolution:
  - Short-term: Restart service (closes connections)
  - Long-term: Optimize slow queries or increase pool size

## Service Won't Start

Symptoms:
  - ECS tasks crash immediately after launch
  - Health check failing continuously

Investigation:
  1. Check ECS task stopped reason:
     - Go to ECS Console → Tasks → Stopped tasks
     - Last stopped reason: Essential container exited

  2. Check CloudWatch Logs:
     - Look for startup errors
     - Common: Missing config, database unreachable

Resolution:
  - Missing config: Add to Secrets Manager / Parameter Store
  - Database unreachable: Check security groups
  - Bad image: Rollback to previous task definition
````

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar health checks (/health/live, /health/ready)
- **MUST** usar structured logging (JSON) con correlation IDs
- **MUST** exponer metrics (Prometheus format)
- **MUST** validar configuración al startup (fail fast)
- **MUST** documentar runbooks para incidents comunes
- **MUST** permitir rollback en < 5 min

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar distributed tracing (microservices)
- **SHOULD** crear dashboards en Grafana (RED metrics)
- **SHOULD** configurar alertas proactivas (CloudWatch Alarms)
- **SHOULD** hacer smoke tests post-deploy automáticos

### MUST NOT (Prohibido)

- **MUST NOT** loggear información sensible (passwords, PII sin mask)
- **MUST NOT** hardcodear configuración en código
- **MUST NOT** requerir acceso a código para diagnosticar
- **MUST NOT** hacer deploys sin rollback strategy

---

## Referencias

- [Lineamiento: Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md)
- [ADR-021: Grafana Stack Observabilidad](../../../decisiones-de-arquitectura/adr-021-grafana-stack-observabilidad.md)
- [Observability Standard](../observabilidad/observability-strategy.md)
- [Health Checks](../apis/health-checks.md)
