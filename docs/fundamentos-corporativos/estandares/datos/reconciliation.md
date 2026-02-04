---
id: reconciliation
sidebar_position: 9
title: Data Reconciliation
description: Estándar para reconciliación periódica de datos entre sistemas distribuidos, detectando y corrigiendo divergencias
---

# Estándar Técnico — Data Reconciliation

---

## 1. Propósito

Detectar y corregir divergencias de datos entre sistemas distribuidos mediante procesos periódicos de reconciliación, garantizando convergencia eventual y alta calidad de datos.

---

## 2. Alcance

**Aplica a:**

- Datos replicados entre servicios
- Cache vs source of truth
- Event-driven systems con eventual consistency
- Integraciones con sistemas externos
- Migraciones de datos
- Denormalización via eventos

**No aplica a:**

- Sistemas con strong consistency (ACID)
- Single source of truth sin réplicas
- Datos inmutables

---

## 3. Tecnologías Aprobadas

| Componente       | Tecnología    | Versión mínima | Observaciones                   |
| ---------------- | ------------- | -------------- | ------------------------------- |
| **Scheduling**   | Hangfire      | 1.8+           | Recurring reconciliation jobs   |
| **Scheduling**   | Quartz.NET    | 3.7+           | Alternativa enterprise          |
| **Comparison**   | DeepEqual     | 4.0+           | Object comparison               |
| **Diff Library** | DiffPlex      | 1.7+           | Text/JSON diff visualization    |
| **Logging**      | Serilog       | 3.1+           | Structured logs de divergencias |
| **Metrics**      | Grafana Mimir | 2.10+          | Métricas de reconciliación      |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Frecuencia de Reconciliación

- [ ] **Datos críticos:** cada 15-30 minutos
- [ ] **Datos importantes:** cada 1-4 horas
- [ ] **Datos no críticos:** diario
- [ ] Schedule definido por tipo de dato
- [ ] Evitar horarios pico (off-peak reconciliation)

### Detección de Divergencias

- [ ] Comparar checksums/hashes antes de deep comparison
- [ ] Identificar registros añadidos, modificados, eliminados
- [ ] Timestamp de última modificación para filtrar
- [ ] Batch processing para grandes volúmenes

### Resolución de Conflictos

- [ ] **Estrategia documented:** LWW, manual review, merge automático
- [ ] Audit log de cada corrección
- [ ] Alertas para divergencias críticas
- [ ] Queue de divergencias para revisión manual
- [ ] Métricas de tasa de divergencias

### Idempotencia

- [ ] Reconciliación puede ejecutarse múltiples veces safely
- [ ] No duplicar correcciones
- [ ] Transaction IDs para tracking
- [ ] Checkpoints para jobs largos

### Performance

- [ ] Pagination para comparar datasets grandes
- [ ] Parallel processing cuando sea posible
- [ ] Índices en campos de comparación (updated_at, checksum)
- [ ] Timeouts configurados

---

## 5. Prohibiciones

- ❌ Reconciliación sincrónica en request path
- ❌ Sobrescribir datos sin validar divergencia real
- ❌ Reconciliación sin logging
- ❌ Ignorar divergencias sin alertar
- ❌ Procesar todo el dataset sin filtros (ineficiente)
- ❌ Reconciliación manual sin automatización
- ❌ No documentar estrategia de conflict resolution

---

## 6. Configuración Mínima

### Hangfire Job de Reconciliación

```csharp
// Jobs/OrderCacheReconciliationJob.cs
public class OrderCacheReconciliationJob
{
    private readonly OrdersDbContext _dbContext;
    private readonly IDistributedCache _cache;
    private readonly ILogger<OrderCacheReconciliationJob> _logger;
    private readonly ReconciliationMetrics _metrics;

    [AutomaticRetry(Attempts = 3)]
    [DisableConcurrentExecution(timeoutInSeconds: 3600)]
    public async Task ReconcileOrderCacheAsync()
    {
        var startTime = DateTime.UtcNow;
        var divergences = 0;
        var corrected = 0;

        _logger.LogInformation("Starting order cache reconciliation");

        try
        {
            // Solo procesar orders activos modificados recientemente
            var recentCutoff = DateTime.UtcNow.AddHours(-24);

            var orders = await _dbContext.Orders
                .Where(o => o.UpdatedAt >= recentCutoff)
                .Where(o => o.DeletedAt == null)
                .Select(o => new
                {
                    o.Id,
                    o.TotalAmount,
                    o.Status,
                    o.UpdatedAt,
                    Checksum = GenerateChecksum(o)
                })
                .ToListAsync();

            foreach (var order in orders)
            {
                var cacheKey = $"order:{order.Id}";
                var cached = await _cache.GetAsync<CachedOrder>(cacheKey);

                if (cached == null)
                {
                    // Cache miss - no es divergencia, solo no cacheado aún
                    continue;
                }

                // Comparar checksums
                if (cached.Checksum != order.Checksum)
                {
                    divergences++;

                    _logger.LogWarning(
                        "Divergence detected for Order {OrderId}. DB checksum: {DbChecksum}, Cache checksum: {CacheChecksum}",
                        order.Id, order.Checksum, cached.Checksum);

                    // Corregir: DB es source of truth
                    await _cache.RemoveAsync(cacheKey);

                    await _cache.SetAsync(cacheKey, new CachedOrder
                    {
                        Id = order.Id,
                        TotalAmount = order.TotalAmount,
                        Status = order.Status.ToString(),
                        CachedAt = DateTime.UtcNow,
                        Checksum = order.Checksum
                    }, TimeSpan.FromMinutes(30));

                    corrected++;

                    // Audit log
                    await LogDivergenceAsync(new DivergenceLog
                    {
                        EntityType = "Order",
                        EntityId = order.Id,
                        DetectedAt = DateTime.UtcNow,
                        SourceChecksum = order.Checksum,
                        TargetChecksum = cached.Checksum,
                        Resolution = "Cache invalidated and refreshed from DB"
                    });
                }
            }

            var duration = DateTime.UtcNow - startTime;

            _metrics.RecordReconciliation(
                entityType: "Order",
                totalChecked: orders.Count,
                divergences: divergences,
                corrected: corrected,
                durationMs: duration.TotalMilliseconds);

            _logger.LogInformation(
                "Order cache reconciliation completed. Checked: {Checked}, Divergences: {Divergences}, Corrected: {Corrected}, Duration: {Duration}ms",
                orders.Count, divergences, corrected, duration.TotalMilliseconds);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Order cache reconciliation failed");
            throw;
        }
    }

    private string GenerateChecksum(Order order)
    {
        var data = $"{order.Id}|{order.TotalAmount}|{order.Status}|{order.UpdatedAt:O}";
        using var sha256 = SHA256.Create();
        var hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(data));
        return Convert.ToBase64String(hash);
    }
}

// Program.cs - Schedule
var recurringJobManager = app.Services.GetRequiredService<IRecurringJobManager>();

recurringJobManager.AddOrUpdate<OrderCacheReconciliationJob>(
    "reconcile-order-cache",
    job => job.ReconcileOrderCacheAsync(),
    Cron.Hourly());  // Cada hora
```

### Reconciliación Cross-Service

```csharp
// Jobs/CustomerDataReconciliationJob.cs
public class CustomerDataReconciliationJob
{
    private readonly OrdersDbContext _ordersDb;
    private readonly CustomersApiClient _customersApi;
    private readonly ILogger<CustomerDataReconciliationJob> _logger;

    // Orders service tiene customer data denormalizada (name, email)
    // Reconciliar con customers-service periódicamente
    [AutomaticRetry(Attempts = 3)]
    public async Task ReconcileCustomerDataAsync()
    {
        var startTime = DateTime.UtcNow;

        // Obtener customers únicos en orders recientes
        var recentOrders = await _ordersDb.Orders
            .Where(o => o.UpdatedAt >= DateTime.UtcNow.AddDays(-7))
            .GroupBy(o => o.CustomerId)
            .Select(g => new
            {
                CustomerId = g.Key,
                DenormalizedName = g.First().CustomerName,
                DenormalizedEmail = g.First().CustomerEmail
            })
            .ToListAsync();

        var divergences = new List<CustomerDivergence>();

        foreach (var orderCustomer in recentOrders)
        {
            // Consultar source of truth (customers-service)
            var actualCustomer = await _customersApi.GetCustomerAsync(orderCustomer.CustomerId);

            if (actualCustomer == null)
            {
                _logger.LogWarning(
                    "Customer {CustomerId} not found in customers-service but referenced in orders",
                    orderCustomer.CustomerId);
                continue;
            }

            // Comparar datos denormalizados
            if (orderCustomer.DenormalizedName != actualCustomer.Name ||
                orderCustomer.DenormalizedEmail != actualCustomer.Email)
            {
                divergences.Add(new CustomerDivergence
                {
                    CustomerId = orderCustomer.CustomerId,
                    OrdersServiceName = orderCustomer.DenormalizedName,
                    ActualName = actualCustomer.Name,
                    OrdersServiceEmail = orderCustomer.DenormalizedEmail,
                    ActualEmail = actualCustomer.Email
                });

                // Corregir datos denormalizados
                await _ordersDb.Orders
                    .Where(o => o.CustomerId == orderCustomer.CustomerId)
                    .ExecuteUpdateAsync(setters => setters
                        .SetProperty(o => o.CustomerName, actualCustomer.Name)
                        .SetProperty(o => o.CustomerEmail, actualCustomer.Email));
            }
        }

        if (divergences.Any())
        {
            _logger.LogWarning(
                "Found {Count} customer data divergences. Corrected denormalized data",
                divergences.Count);

            // Alertar si tasa de divergencia es alta
            var divergenceRate = divergences.Count / (double)recentOrders.Count;
            if (divergenceRate > 0.05)  // >5% divergence
            {
                _logger.LogError(
                    "High divergence rate: {Rate:P2}. Investigate event propagation issues",
                    divergenceRate);

                // Enviar alerta a PagerDuty/Slack
                await SendHighDivergenceAlertAsync(divergenceRate, divergences.Count);
            }
        }

        var duration = DateTime.UtcNow - startTime;

        _logger.LogInformation(
            "Customer data reconciliation completed. Checked: {Checked}, Divergences: {Divergences}, Duration: {Duration}ms",
            recentOrders.Count, divergences.Count, duration.TotalMilliseconds);
    }
}
```

### Divergence Tracking

```sql
-- Tabla para tracking de divergencias
CREATE TABLE reconciliation_divergences (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    detected_at TIMESTAMP NOT NULL DEFAULT NOW(),
    source_system VARCHAR(100) NOT NULL,
    target_system VARCHAR(100) NOT NULL,
    source_checksum VARCHAR(255),
    target_checksum VARCHAR(255),
    resolution VARCHAR(50) NOT NULL,  -- 'auto_corrected', 'manual_review', 'ignored'
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_divergences_entity ON reconciliation_divergences(entity_type, entity_id);
CREATE INDEX idx_divergences_detected ON reconciliation_divergences(detected_at);
CREATE INDEX idx_divergences_resolution ON reconciliation_divergences(resolution) WHERE resolution = 'manual_review';
```

### Métricas de Reconciliación

```csharp
// Metrics/ReconciliationMetrics.cs
using Prometheus;

public class ReconciliationMetrics
{
    private static readonly Counter ReconciliationRuns = Metrics
        .CreateCounter(
            "reconciliation_runs_total",
            "Total reconciliation runs",
            new CounterConfiguration
            {
                LabelNames = new[] { "entity_type", "result" }
            });

    private static readonly Counter DivergencesDetected = Metrics
        .CreateCounter(
            "reconciliation_divergences_detected_total",
            "Total divergences detected",
            new CounterConfiguration
            {
                LabelNames = new[] { "entity_type", "source", "target" }
            });

    private static readonly Counter DivergencesCorrected = Metrics
        .CreateCounter(
            "reconciliation_divergences_corrected_total",
            "Total divergences auto-corrected",
            new CounterConfiguration
            {
                LabelNames = new[] { "entity_type" }
            });

    private static readonly Histogram ReconciliationDuration = Metrics
        .CreateHistogram(
            "reconciliation_duration_milliseconds",
            "Reconciliation job duration",
            new HistogramConfiguration
            {
                LabelNames = new[] { "entity_type" },
                Buckets = Histogram.ExponentialBuckets(100, 2, 10)
            });

    private static readonly Gauge DivergenceRate = Metrics
        .CreateGauge(
            "reconciliation_divergence_rate",
            "Rate of divergences (divergences/total_checked)",
            new GaugeConfiguration
            {
                LabelNames = new[] { "entity_type" }
            });

    public void RecordReconciliation(
        string entityType,
        int totalChecked,
        int divergences,
        int corrected,
        double durationMs)
    {
        ReconciliationRuns.WithLabels(entityType, "success").Inc();
        DivergencesDetected.WithLabels(entityType, "database", "cache").Inc(divergences);
        DivergencesCorrected.WithLabels(entityType).Inc(corrected);
        ReconciliationDuration.WithLabels(entityType).Observe(durationMs);

        var rate = totalChecked > 0 ? divergences / (double)totalChecked : 0;
        DivergenceRate.WithLabels(entityType).Set(rate);
    }
}
```

---

## 7. Ejemplos

### Batch Reconciliation con Checkpoints

```csharp
public class LargeDatasetReconciliationJob
{
    private readonly ILogger<LargeDatasetReconciliationJob> _logger;

    public async Task ReconcileLargeDatasetAsync()
    {
        const int batchSize = 1000;
        Guid? lastProcessedId = await GetLastCheckpointAsync();

        while (true)
        {
            var batch = await GetNextBatchAsync(lastProcessedId, batchSize);

            if (!batch.Any())
                break;  // Completado

            await ProcessBatchAsync(batch);

            lastProcessedId = batch.Last().Id;
            await SaveCheckpointAsync(lastProcessedId.Value);

            _logger.LogInformation("Processed batch, checkpoint: {LastId}", lastProcessedId);

            // Throttling para no sobrecargar DB
            await Task.Delay(TimeSpan.FromSeconds(1));
        }

        await ClearCheckpointAsync();
        _logger.LogInformation("Large dataset reconciliation completed");
    }
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Jobs de reconciliación programados
- [ ] Estrategia de conflict resolution documentada
- [ ] Checksums/hashes para comparación eficiente
- [ ] Logs de divergencias con audit trail
- [ ] Alertas para alta tasa de divergencias
- [ ] Métricas de reconciliación monitoreadas
- [ ] Tests de reconciliation logic

### Métricas Prometheus

```promql
# Tasa de divergencias
rate(reconciliation_divergences_detected_total[1h])

# Divergences no corregidas (manual review)
reconciliation_divergences_detected_total - reconciliation_divergences_corrected_total

# Duración p95 de reconciliación
histogram_quantile(0.95, reconciliation_duration_milliseconds)
```

### Alertas

```yaml
groups:
  - name: reconciliation_alerts
    rules:
      - alert: HighDivergenceRate
        expr: reconciliation_divergence_rate > 0.05
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "High divergence rate detected"
          description: "{{ $labels.entity_type }}: {{ $value | humanizePercentage }} divergence rate"

      - alert: ReconciliationFailing
        expr: rate(reconciliation_runs_total{result="failure"}[1h]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Reconciliation jobs failing"
```

---

## 9. Referencias

**Teoría:**

- "Designing Data-Intensive Applications" - Martin Kleppmann
- "Database Reliability Engineering" (O'Reilly)
- CAP Theorem y Eventual Consistency

**Documentación:**

- [Hangfire Documentation](https://docs.hangfire.io/)
- [Quartz.NET Tutorial](https://www.quartz-scheduler.net/documentation/)

**Buenas prácticas:**

- Google SRE Book - "Data Integrity"
- AWS Well-Architected - Reliability Pillar
