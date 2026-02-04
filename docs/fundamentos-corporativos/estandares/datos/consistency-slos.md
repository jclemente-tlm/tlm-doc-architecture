---
id: consistency-slos
sidebar_position: 3
title: Consistency SLOs
description: Estándar para definir Service Level Objectives de consistencia de datos con métricas observables y alertas
---

# Estándar Técnico — Consistency SLOs

---

## 1. Propósito

Establecer SLOs medibles para consistencia de datos, definiendo umbrales aceptables de staleness, replication lag y convergencia eventual con alertas proactivas.

---

## 2. Alcance

**Aplica a:**

- Bases de datos replicadas
- Cache distribuido
- Event-driven systems
- Multi-region deployments
- Read replicas
- CDC (Change Data Capture) pipelines

**No aplica a:**

- Sistemas single-instance sin réplicas
- Datos completamente inmutables
- Logs append-only sin lecturas

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología         | Versión mínima | Observaciones                   |
| ----------------- | ------------------ | -------------- | ------------------------------- |
| **Monitoring**    | Grafana Mimir      | 2.10+          | Métricas de lag y staleness     |
| **Visualization** | Grafana            | 10.0+          | Dashboards de consistencia      |
| **Tracing**       | OpenTelemetry      | 1.20+          | Trace de propagación de eventos |
| **Alerting**      | Grafana Alerting   | 10.0+          | Alertas de SLO breach           |
| **DB Monitoring** | pg_stat_statements | (built-in)     | PostgreSQL query stats          |
| **Replication**   | pgBackRest         | 2.48+          | Monitoreo de replication lag    |
| **APM**           | AWS CloudWatch     | -              | RDS replication metrics         |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Definición de SLOs

- [ ] **Replication lag:** max lag time entre primary y replica (ej: <5s)
- [ ] **Staleness tolerance:** max edad de datos cached aceptable (ej: <2min)
- [ ] **Convergence time:** max tiempo para eventual consistency (ej: <30s)
- [ ] **Availability durante partition:** % de writes exitosos durante split-brain
- [ ] SLO documentado por bounded context/servicio

### Métricas Obligatorias

- [ ] **replication_lag_seconds:** lag entre primary y cada replica
- [ ] **cache_staleness_seconds:** edad del dato cached vs source of truth
- [ ] **event_propagation_duration:** tiempo desde write hasta consumed
- [ ] **consistency_check_failures_total:** fallos en validaciones de consistencia
- [ ] **conflict_resolution_duration:** latencia de merge de conflictos

### Umbrales de Alerta

- [ ] **Warning:** lag > 50% del SLO (ej: lag > 2.5s si SLO es 5s)
- [ ] **Critical:** lag > 100% del SLO
- [ ] **Page:** lag > 200% del SLO o datos críticos inconsistentes
- [ ] Escalation policy definida

### Monitoreo Continuo

- [ ] Dashboard de consistencia por servicio
- [ ] Gráficos de p95/p99 de lag
- [ ] Histórico de breaches del SLO
- [ ] Correlación con deploys/incidents

### Reconciliación Proactiva

- [ ] Detección automática de divergencias
- [ ] Jobs periódicos de reconciliación
- [ ] Alertas de datos sin converger después de SLO
- [ ] Audit trail de correcciones

---

## 5. Prohibiciones

- ❌ SLOs sin métricas observables
- ❌ Alertas sin runbook de remediación
- ❌ Ignorar replication lag en deploys
- ❌ Cache sin TTL máximo definido
- ❌ Eventual consistency sin SLO de convergencia
- ❌ Alertas de lag sin contexto de impacto al negocio
- ❌ SLO igual para todos los bounded contexts (one-size-fits-all)

---

## 6. Configuración Mínima

### Prometheus Metrics

```csharp
// Metrics/ConsistencyMetrics.cs
using Prometheus;

public class ConsistencyMetrics
{
    private static readonly Gauge ReplicationLagSeconds = Metrics
        .CreateGauge(
            "db_replication_lag_seconds",
            "Replication lag in seconds between primary and replica",
            new GaugeConfiguration
            {
                LabelNames = new[] { "database", "replica" }
            });

    private static readonly Histogram EventPropagationDuration = Metrics
        .CreateHistogram(
            "event_propagation_duration_seconds",
            "Time from event published to consumed",
            new HistogramConfiguration
            {
                LabelNames = new[] { "event_type", "consumer" },
                Buckets = Histogram.ExponentialBuckets(0.01, 2, 10)
            });

    private static readonly Counter CacheStalenessExceeded = Metrics
        .CreateCounter(
            "cache_staleness_exceeded_total",
            "Count of cache reads exceeding staleness SLO",
            new CounterConfiguration
            {
                LabelNames = new[] { "cache_key_prefix", "slo_seconds" }
            });

    public void RecordReplicationLag(string database, string replica, double lagSeconds)
    {
        ReplicationLagSeconds.WithLabels(database, replica).Set(lagSeconds);
    }

    public void RecordEventPropagation(string eventType, string consumer, TimeSpan duration)
    {
        EventPropagationDuration.WithLabels(eventType, consumer)
            .Observe(duration.TotalSeconds);
    }

    public void RecordStalenessExceeded(string cacheKeyPrefix, int sloSeconds)
    {
        CacheStalenessExceeded.WithLabels(cacheKeyPrefix, sloSeconds.ToString()).Inc();
    }
}

// Application/Services/OrderService.cs
public class OrderService
{
    private readonly ConsistencyMetrics _metrics;
    private readonly IDistributedCache _cache;

    public async Task<Order> GetOrderAsync(Guid orderId)
    {
        var cacheKey = $"order:{orderId}";
        var cached = await _cache.GetAsync<CachedOrder>(cacheKey);

        if (cached != null)
        {
            var age = DateTime.UtcNow - cached.CachedAt;

            // Validar contra SLO (2 minutos para orders)
            if (age.TotalSeconds > 120)
            {
                _metrics.RecordStalenessExceeded("order", 120);

                // Invalidar cache stale
                await _cache.RemoveAsync(cacheKey);
            }
            else
            {
                return cached.Order;
            }
        }

        // Cache miss o stale - leer de DB
        var order = await _dbContext.Orders.FindAsync(orderId);

        await _cache.SetAsync(cacheKey, new CachedOrder
        {
            Order = order,
            CachedAt = DateTime.UtcNow
        }, TimeSpan.FromMinutes(2));

        return order;
    }
}
```

### PostgreSQL Replication Monitoring

```sql
-- View de replication lag
CREATE OR REPLACE VIEW replication_lag AS
SELECT
    client_addr AS replica_address,
    application_name,
    state,
    sync_state,
    EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp()))::INT AS lag_seconds,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
FROM pg_stat_replication;

-- Function para alertar si lag > SLO
CREATE OR REPLACE FUNCTION check_replication_lag_slo(
    p_slo_seconds INT DEFAULT 5
) RETURNS TABLE (
    replica VARCHAR,
    lag_seconds INT,
    exceeds_slo BOOLEAN,
    severity VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        application_name::VARCHAR,
        EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp()))::INT,
        EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp()))::INT > p_slo_seconds,
        CASE
            WHEN EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp()))::INT > p_slo_seconds * 2 THEN 'CRITICAL'
            WHEN EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp()))::INT > p_slo_seconds THEN 'WARNING'
            ELSE 'OK'
        END::VARCHAR
    FROM pg_stat_replication
    WHERE state = 'streaming';
END;
$$ LANGUAGE plpgsql;

-- Ejecutar periódicamente desde cron job
SELECT * FROM check_replication_lag_slo(5);
```

### Prometheus Alerting Rules

```yaml
# prometheus/alerts/consistency-slos.yml
groups:
  - name: consistency_slos
    interval: 30s
    rules:
      # PostgreSQL Replication Lag
      - alert: PostgreSQLReplicationLagHigh
        expr: db_replication_lag_seconds{database="talma_production"} > 5
        for: 2m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "PostgreSQL replication lag exceeds SLO"
          description: "Replica {{ $labels.replica }} lag is {{ $value }}s (SLO: <5s)"
          runbook: "https://wiki.talma.com/runbooks/postgres-replication-lag"

      - alert: PostgreSQLReplicationLagCritical
        expr: db_replication_lag_seconds{database="talma_production"} > 10
        for: 1m
        labels:
          severity: critical
          team: platform
          page: "true"
        annotations:
          summary: "PostgreSQL replication lag CRITICAL"
          description: "Replica {{ $labels.replica }} lag is {{ $value }}s (>2x SLO)"
          impact: "Read replicas serving stale data, reports may be inconsistent"

      # Event Propagation
      - alert: EventPropagationSlow
        expr: histogram_quantile(0.95, event_propagation_duration_seconds) > 30
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Event propagation p95 exceeds SLO"
          description: "{{ $labels.event_type }} → {{ $labels.consumer }}: p95={{ $value }}s (SLO: <30s)"

      # Cache Staleness
      - alert: CacheStalenessExceededRate
        expr: rate(cache_staleness_exceeded_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
          team: application
        annotations:
          summary: "High rate of stale cache reads"
          description: "{{ $labels.cache_key_prefix }}: {{ $value }} stale reads/sec"
          action: "Consider reducing TTL or improving cache invalidation"

      # Consistency Check Failures
      - alert: ConsistencyCheckFailing
        expr: rate(consistency_check_failures_total[15m]) > 0
        for: 5m
        labels:
          severity: critical
          team: platform
          page: "true"
        annotations:
          summary: "Consistency validation failing"
          description: "{{ $labels.check_type }}: {{ $value }} failures detected"
          impact: "Data inconsistency detected between systems"
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Consistency SLOs",
    "panels": [
      {
        "title": "Replication Lag (SLO: <5s)",
        "targets": [
          {
            "expr": "db_replication_lag_seconds{database='talma_production'}",
            "legendFormat": "{{ replica }}"
          }
        ],
        "thresholds": [
          { "value": 5, "color": "orange", "label": "SLO" },
          { "value": 10, "color": "red", "label": "Critical" }
        ]
      },
      {
        "title": "Event Propagation p95 (SLO: <30s)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(event_propagation_duration_seconds_bucket[5m]))",
            "legendFormat": "{{ event_type }}"
          }
        ]
      },
      {
        "title": "Cache Staleness Violations",
        "targets": [
          {
            "expr": "sum by (cache_key_prefix) (rate(cache_staleness_exceeded_total[5m]))",
            "legendFormat": "{{ cache_key_prefix }}"
          }
        ]
      }
    ]
  }
}
```

---

## 7. Ejemplos

### SLO Tracking Service

```csharp
public class ConsistencySLOTracker
{
    private readonly ILogger<ConsistencySLOTracker> _logger;
    private readonly ConsistencyMetrics _metrics;

    private readonly Dictionary<string, ConsistencySLO> _slos = new()
    {
        ["order_cache"] = new ConsistencySLO
        {
            Name = "Order Cache Staleness",
            MaxStalenessSeconds = 120,
            MeasurementIntervalSeconds = 60
        },
        ["inventory_replication"] = new ConsistencySLO
        {
            Name = "Inventory Replication Lag",
            MaxLagSeconds = 5,
            MeasurementIntervalSeconds = 30
        },
        ["payment_events"] = new ConsistencySLO
        {
            Name = "Payment Event Propagation",
            MaxPropagationSeconds = 30,
            MeasurementIntervalSeconds = 60
        }
    };

    public async Task<SLOComplianceReport> GenerateComplianceReportAsync(
        DateTime from,
        DateTime to)
    {
        var report = new SLOComplianceReport
        {
            Period = new DateRange { From = from, To = to },
            Items = new List<SLOComplianceItem>()
        };

        foreach (var (key, slo) in _slos)
        {
            var measurements = await GetMeasurementsAsync(key, from, to);

            var totalMeasurements = measurements.Count;
            var breaches = measurements.Count(m => m.ExceedsSLO);
            var complianceRate = (totalMeasurements - breaches) / (double)totalMeasurements;

            report.Items.Add(new SLOComplianceItem
            {
                SLOName = slo.Name,
                TargetCompliance = 0.99,  // 99% compliance target
                ActualCompliance = complianceRate,
                Breaches = breaches,
                TotalMeasurements = totalMeasurements,
                Status = complianceRate >= 0.99 ? "PASS" : "FAIL"
            });
        }

        return report;
    }
}
```

### Reconciliation Job

```csharp
public class DataReconciliationJob
{
    private readonly ILogger<DataReconciliationJob> _logger;

    [DisableConcurrentExecution(timeoutInSeconds: 3600)]
    public async Task ReconcileOrderTotalsAsync()
    {
        var startTime = DateTime.UtcNow;

        // Comparar cache vs DB
        var divergences = await FindDivergencesAsync();

        foreach (var divergence in divergences)
        {
            _logger.LogWarning(
                "Data divergence detected: Order {OrderId}, Cache={CacheValue}, DB={DbValue}",
                divergence.OrderId,
                divergence.CachedTotal,
                divergence.ActualTotal);

            // Invalidar cache incorrecto
            await _cache.RemoveAsync($"order:{divergence.OrderId}");

            // Métricas
            _metrics.RecordReconciliationFix("order_total");
        }

        var duration = DateTime.UtcNow - startTime;

        _logger.LogInformation(
            "Reconciliation completed in {Duration}ms. Found {Count} divergences",
            duration.TotalMilliseconds,
            divergences.Count);
    }
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] SLOs definidos por bounded context
- [ ] Métricas de lag/staleness instrumentadas
- [ ] Dashboards de consistencia configurados
- [ ] Alertas con umbrales SLO configuradas
- [ ] Runbooks de remediación documentados
- [ ] Jobs de reconciliación programados
- [ ] Reportes mensuales de compliance

### Métricas de Compliance

```promql
# SLO compliance rate (% de mediciones dentro de SLO)
sum(rate(replication_lag_within_slo[1h])) / sum(rate(replication_lag_measurements_total[1h]))

# Error budget remaining (asumiendo 99% target)
1 - (sum(rate(slo_breaches_total[30d])) / sum(rate(slo_measurements_total[30d])))
```

---

## 9. Referencias

**Teoría:**

- Google SRE Book - "Service Level Objectives"
- "Implementing Service Level Objectives" (O'Reilly)
- "Database Reliability Engineering" (O'Reilly)

**Documentación:**

- [PostgreSQL Monitoring](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/alerting/)
- [Grafana SLO Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)

**Buenas prácticas:**

- AWS Well-Architected - Reliability Pillar
- "SLO Adoption and Usage in SRE" (Google)
