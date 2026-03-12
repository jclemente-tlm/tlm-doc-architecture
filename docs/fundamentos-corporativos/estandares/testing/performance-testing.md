---
id: performance-testing
sidebar_position: 8
title: Pruebas de Performance
description: Estándares para load testing, baseline performance y validación de SLAs
tags: [testing, performance, load-testing, k6, grafana]
---

# Pruebas de Performance

## Contexto

Este estándar define **performance testing** para validar que servicios cumplen SLAs bajo carga. Incluye load testing, baseline metrics, y validación de P95/P99 latency.

**Conceptos incluidos:**

- **Performance Testing** → Load testing, stress testing, baseline performance

---

## Stack Tecnológico

| Componente          | Tecnología     | Versión | Uso                                   |
| ------------------- | -------------- | ------- | ------------------------------------- |
| **Load Testing**    | k6             | 0.49+   | Scripting de load tests en JavaScript |
| **Metrics Storage** | InfluxDB       | 2.7+    | Time-series database para métricas    |
| **Dashboards**      | Grafana        | 10.3+   | Visualización de métricas             |
| **APM**             | OpenTelemetry  | 1.22+   | Distributed tracing durante tests     |
| **CI/CD**           | GitHub Actions | Latest  | Automatización de performance tests   |

---

## Pruebas de Performance

### ¿Qué son las Pruebas de Performance?

Tests que validan comportamiento del sistema bajo carga simulada. Mide latency, throughput, resource utilization para garantizar cumplimiento de SLAs.

**Propósito:** Garantizar que servicios cumplen SLAs de performance antes de producción.

**Tipos:**

- **Load Testing**: Carga esperada normal (baseline)
- **Stress Testing**: Carga incremental hasta identificar breaking point
- **Spike Testing**: Picos súbitos de tráfico
- **Soak Testing**: Carga sostenida por horas/días (memory leaks)

**SLAs Típicos:**

- P95 latency < 500ms
- P99 latency < 1000ms
- Throughput: 1000 req/s
- Error rate < 0.1%
- CPU < 70%
- Memory estable (no leaks)

### k6: Load Testing Moderno

```javascript
// tests/performance/create-order-load.js
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

// Custom metrics
const errorRate = new Rate("errors");
const orderCreationDuration = new Trend("order_creation_duration");

// Load profile
export const options = {
  stages: [
    { duration: "2m", target: 50 }, // Ramp-up to 50 users
    { duration: "5m", target: 50 }, // Stay at 50 users
    { duration: "2m", target: 100 }, // Ramp-up to 100 users
    { duration: "5m", target: 100 }, // Stay at 100 users
    { duration: "2m", target: 0 }, // Ramp-down to 0 users
  ],
  thresholds: {
    // SLA: 95% of requests should be below 500ms
    http_req_duration: ["p(95)<500", "p(99)<1000"],

    // SLA: Error rate should be below 0.1%
    errors: ["rate<0.001"],

    // SLA: 95% of requests should succeed
    http_req_failed: ["rate<0.05"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:5000";
const AUTH_TOKEN = __ENV.AUTH_TOKEN;

export function setup() {
  // Authenticate once at the beginning
  const loginRes = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({
      email: "loadtest@talma.pe",
      password: "LoadTest123!",
    }),
    {
      headers: { "Content-Type": "application/json" },
    },
  );

  check(loginRes, {
    "login successful": (r) => r.status === 200,
  });

  return { token: loginRes.json("accessToken") };
}

export default function (data) {
  // Create order
  const payload = JSON.stringify({
    customerId: `CUST-${Math.floor(Math.random() * 1000)}`,
    items: [
      {
        sku: `SKU-${Math.floor(Math.random() * 100)}`,
        quantity: Math.floor(Math.random() * 5) + 1,
        unitPrice: 100.0,
      },
    ],
    paymentMethod: "credit_card",
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${data.token}`,
    },
    tags: { name: "CreateOrder" },
  };

  const res = http.post(`${BASE_URL}/api/orders`, payload, params);

  // Validations
  const success = check(res, {
    "status is 201": (r) => r.status === 201,
    "has orderId": (r) => r.json("orderId") !== undefined,
    "response time < 500ms": (r) => r.timings.duration < 500,
  });

  errorRate.add(!success);
  orderCreationDuration.add(res.timings.duration);

  // Think time (simular user behavior)
  sleep(Math.random() * 3 + 1); // Random 1-4 seconds
}

export function teardown(data) {
  // Cleanup after tests
  console.log("Load test completed");
}
```

### Stress Testing: Encontrar Breaking Point

```javascript
// tests/performance/create-order-stress.js
import http from "k6/http";
import { check } from "k6";

export const options = {
  stages: [
    { duration: "2m", target: 100 }, // Ramp-up to 100
    { duration: "5m", target: 100 }, // Stay at 100
    { duration: "2m", target: 200 }, // Ramp-up to 200
    { duration: "5m", target: 200 }, // Stay at 200
    { duration: "2m", target: 300 }, // Ramp-up to 300
    { duration: "5m", target: 300 }, // Stay at 300
    { duration: "2m", target: 400 }, // Ramp-up to 400 (breaking point?)
    { duration: "5m", target: 400 }, // Stay at 400
    { duration: "5m", target: 0 }, // Recovery period
  ],
  thresholds: {
    // No hard thresholds, queremos ver degradación gradual
    http_req_duration: ["p(95)<2000"], // Más laxo que load test
    http_req_failed: ["rate<0.10"], // Toleramos 10% errors
  },
};

// ... mismo código de test
```

### Spike Testing: Tráfico Súbito

```javascript
// tests/performance/create-order-spike.js
export const options = {
  stages: [
    { duration: "1m", target: 20 }, // Baseline
    { duration: "10s", target: 200 }, // Spike! 0-200 en 10s
    { duration: "3m", target: 200 }, // Stay at spike
    { duration: "10s", target: 20 }, // Back to baseline
    { duration: "2m", target: 20 }, // Recovery
  ],
  thresholds: {
    http_req_duration: ["p(95)<1000"], // Más tolerante durante spike
    http_req_failed: ["rate<0.05"],
  },
};

// ... mismo código de test
```

### Soak Testing: Sustained Load (Memory Leaks)

```javascript
// tests/performance/create-order-soak.js
export const options = {
  stages: [
    { duration: "2m", target: 50 }, // Ramp-up
    { duration: "4h", target: 50 }, // Sustained load por 4 horas
    { duration: "2m", target: 0 }, // Ramp-down
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
  },
};

// ... mismo código de test
```

### CI/CD Integration

```yaml
# .github/workflows/performance-tests.yml
name: Performance Tests

on:
  schedule:
    # Ejecutar todas las noches a las 2 AM
    - cron: "0 2 * * *"
  workflow_dispatch:
    inputs:
      environment:
        description: "Environment to test"
        required: true
        default: "staging"
        type: choice
        options:
          - staging
          - production

jobs:
  load-test:
    name: Load Test
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load test
        env:
          BASE_URL: ${{ github.event.inputs.environment == 'production' && secrets.PROD_API_URL || secrets.STAGING_API_URL }}
          AUTH_TOKEN: ${{ secrets.LOAD_TEST_TOKEN }}
        run: |
          k6 run \
            --out influxdb=http://influxdb:8086/k6 \
            tests/performance/create-order-load.js

      - name: Check thresholds
        if: failure()
        run: |
          echo "⚠️ Performance test FAILED - SLAs not met"
          exit 1

      - name: Notify on failure
        if: failure()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
            -H 'Content-Type: application/json' \
            -d '{
              "text": "🚨 Performance test FAILED in ${{ github.event.inputs.environment }}",
              "channel": "#performance"
            }'
```

### Grafana Dashboard

```yaml
# k6-dashboard.json (simplified)
{
  "dashboard":
    {
      "title": "k6 Load Test - Order Service",
      "panels":
        [
          {
            "title": "Request Rate",
            "targets":
              [
                {
                  "query": 'SELECT mean("value") FROM "http_reqs" WHERE $timeFilter GROUP BY time(10s)',
                },
              ],
          },
          {
            "title": "Response Time (P95, P99)",
            "targets":
              [
                {
                  "query": 'SELECT percentile("value", 95) FROM "http_req_duration" WHERE $timeFilter GROUP BY time(10s)',
                },
                {
                  "query": 'SELECT percentile("value", 99) FROM "http_req_duration" WHERE $timeFilter GROUP BY time(10s)',
                },
              ],
          },
          {
            "title": "Error Rate",
            "targets":
              [
                {
                  "query": 'SELECT mean("value") FROM "errors" WHERE $timeFilter GROUP BY time(10s)',
                },
              ],
          },
          {
            "title": "Virtual Users",
            "targets":
              [
                {
                  "query": 'SELECT mean("value") FROM "vus" WHERE $timeFilter GROUP BY time(10s)',
                },
              ],
          },
        ],
    },
}
```

### Baseline Performance: .NET Service SLAs

```csharp
// tests/Performance.Tests/BaselinePerformanceTests.cs
using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Running;

[MemoryDiagnoser]
[MeanColumn, MedianColumn, P95Column, P99Column]
public class OrderServiceBenchmarks
{
    private OrderService _orderService;
    private CreateOrderRequest _request;

    [GlobalSetup]
    public void Setup()
    {
        // Setup dependencies con mocks
        var repository = new Mock<IOrderRepository>();
        var paymentService = new Mock<IPaymentService>();

        repository.Setup(r => r.GetCustomerAsync(It.IsAny<string>()))
            .ReturnsAsync(new Customer { Id = "CUST-123", Name = "Test" });

        paymentService.Setup(p => p.ProcessPaymentAsync(It.IsAny<PaymentRequest>()))
            .ReturnsAsync(new PaymentResult { Success = true });

        _orderService = new OrderService(
            repository.Object,
            paymentService.Object,
            Mock.Of<INotificationService>(),
            Mock.Of<ILogger<OrderService>>());

        _request = new CreateOrderRequest
        {
            CustomerId = "CUST-123",
            Items = new[]
            {
                new OrderItemRequest { Sku = "SKU-001", Quantity = 2, UnitPrice = 100m }
            },
            PaymentMethod = "credit_card"
        };
    }

    [Benchmark]
    public async Task<OrderResponse> CreateOrder()
    {
        return await _orderService.CreateOrderAsync(_request);
    }
}

// Program.cs
class Program
{
    static void Main(string[] args)
    {
        var summary = BenchmarkRunner.Run<OrderServiceBenchmarks>();

        // Validar SLAs
        var meanTime = summary.Reports.First().ResultStatistics.Mean;
        var p95 = summary.Reports.First().ResultStatistics.Percentiles.P95;

        if (meanTime > 10_000_000) // 10ms en nanosegundos
        {
            Console.WriteLine($"❌ FAILED: Mean time {meanTime}ns > 10ms");
            Environment.Exit(1);
        }

        if (p95 > 50_000_000) // 50ms
        {
            Console.WriteLine($"❌ FAILED: P95 {p95}ns > 50ms");
            Environment.Exit(1);
        }

        Console.WriteLine("✅ PASSED: Performance SLAs met");
    }
}
```

### Métricas de Performance

```csharp
// src/OrderService.Api/Metrics/PerformanceMetrics.cs
using Prometheus;

public static class PerformanceMetrics
{
    public static readonly Histogram RequestDuration = Metrics
        .CreateHistogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            new HistogramConfiguration
            {
                LabelNames = new[] { "method", "endpoint", "status" },
                Buckets = new[] { 0.01, 0.05, 0.1, 0.5, 1, 2, 5 } // Buckets para latency
            });

    public static readonly Counter RequestErrors = Metrics
        .CreateCounter(
            "http_request_errors_total",
            "Total HTTP request errors",
            new CounterConfiguration
            {
                LabelNames = new[] { "method", "endpoint", "status" }
            });

    public static readonly Gauge ActiveRequests = Metrics
        .CreateGauge(
            "http_active_requests",
            "Number of active HTTP requests",
            new GaugeConfiguration
            {
                LabelNames = new[] { "endpoint" }
            });
}

// Middleware para tracking
public class PerformanceMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        var endpoint = context.Request.Path;
        var method = context.Request.Method;

        PerformanceMetrics.ActiveRequests.WithLabels(endpoint).Inc();

        using (PerformanceMetrics.RequestDuration
            .WithLabels(method, endpoint, "pending")
            .NewTimer())
        {
            try
            {
                await _next(context);

                var status = context.Response.StatusCode.ToString();
                PerformanceMetrics.RequestDuration
                    .WithLabels(method, endpoint, status);

                if (context.Response.StatusCode >= 400)
                {
                    PerformanceMetrics.RequestErrors
                        .WithLabels(method, endpoint, status)
                        .Inc();
                }
            }
            finally
            {
                PerformanceMetrics.ActiveRequests.WithLabels(endpoint).Dec();
            }
        }
    }
}
```

### Alertas de Performance

```yaml
# prometheus/alerts/performance.yml
groups:
  - name: performance
    interval: 30s
    rules:
      - alert: HighLatencyP95
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High P95 latency detected"
          description: "P95 latency is {{ $value }}s (threshold: 0.5s)"

      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1.0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High P99 latency detected"
          description: "P99 latency is {{ $value }}s (threshold: 1.0s)"

      - alert: HighErrorRate
        expr: |
          sum(rate(http_request_errors_total[5m]))
          /
          sum(rate(http_request_duration_seconds_count[5m]))
          > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 1%)"

      - alert: HighThroughputDrop
        expr: |
          rate(http_request_duration_seconds_count[5m])
          <
          rate(http_request_duration_seconds_count[5m] offset 10m) * 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Throughput dropped significantly"
          description: "Throughput is {{ $value }} req/s (50% drop detected)"
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** ejecutar load tests antes de cada release mayor
- **MUST** definir SLAs claros (P95, P99, throughput, error rate)
- **MUST** validar SLAs en CI/CD con thresholds
- **MUST** monitorear performance en producción (Prometheus)
- **MUST** baseline performance tests para cambios críticos

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar k6 para load testing (JavaScript DSL)
- **SHOULD** stress testing para encontrar breaking point
- **SHOULD** spike testing para validar auto-scaling
- **SHOULD** soak testing overnight para memory leaks
- **SHOULD** almacenar métricas en InfluxDB + Grafana
- **SHOULD** alertas en Prometheus para latency/errors

### MAY (Opcional)

- **MAY** JMeter para casos legacy o GUI requirement
- **MAY** distributed load tests (k6 cloud)
- **MAY** chaos engineering durante load tests

### MUST NOT (Prohibido)

- **MUST NOT** ejecutar load tests contra producción (usar staging)
- **MUST NOT** hardcodear thresholds (usar configuración por ambiente)
- **MUST NOT** ignorar resource utilization (CPU, memory, DB connections)

---

## Referencias

- [k6 Documentation](https://k6.io/docs/)
- [Grafana k6](https://grafana.com/docs/k6/latest/)
- [BenchmarkDotNet](https://benchmarkdotnet.org/)
- [Performance Testing Guidance - Microsoft](https://learn.microsoft.com/en-us/azure/architecture/framework/scalability/performance-test)

- [Pirámide de Testing](./testing-pyramid.md)
- [Métricas con OpenTelemetry](../observabilidad/metrics.md)
- [Escalado Horizontal](../arquitectura/horizontal-scaling.md)
