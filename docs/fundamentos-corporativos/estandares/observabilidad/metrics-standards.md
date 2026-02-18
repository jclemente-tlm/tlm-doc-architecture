---
id: metrics-standards
sidebar_position: 2
title: Métricas y Monitoreo
description: Métricas siguiendo RED/USE con OpenTelemetry y Grafana Mimir
---

# Métricas y Monitoreo

## Contexto

Este estándar define cómo emitir métricas siguiendo patrones RED (Rate, Errors, Duration) para servicios y USE (Utilization, Saturation, Errors) para recursos. Complementa el [lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) especificando **cómo** instrumentar código para métricas consultables.

---

## Stack Tecnológico

| Componente          | Tecnología                  | Versión | Uso                     |
| ------------------- | --------------------------- | ------- | ----------------------- |
| **Framework**       | ASP.NET Core                | 8.0+    | Framework base          |
| **Instrumentación** | OpenTelemetry .NET          | 1.7+    | SDK de métricas         |
| **Exportador**      | OpenTelemetry.Exporter.OTLP | 1.7+    | Export a Grafana Alloy  |
| **Collector**       | Grafana Alloy               | 1.0+    | Recolector OTLP         |
| **Storage**         | Grafana Mimir               | 2.10+   | Almacenamiento métricas |
| **Visualización**   | Grafana                     | 10.0+   | Dashboards y queries    |

### Dependencias NuGet

```xml
<PackageReference Include="OpenTelemetry" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Exporter.OpenTelemetryProtocol" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Extensions.Hosting" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Instrumentation.AspNetCore" Version="1.7.0" />
<PackageReference Include="OpenTelemetry.Instrumentation.Http" Version="1.7.0" />
```

---

## Implementación Técnica

### Configuración Base OpenTelemetry

```csharp
// Program.cs
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;

var builder = WebApplication.CreateBuilder(args);

// ✅ Configurar OpenTelemetry Metrics
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService(
            serviceName: "orders-api",
            serviceVersion: "1.0.0",
            serviceInstanceId: Environment.MachineName
        )
        .AddAttributes(new Dictionary<string, object>
        {
            ["deployment.environment"] = builder.Environment.EnvironmentName,
            ["service.namespace"] = "talma.orders"
        })
    )
    .WithMetrics(metrics => metrics
        // ✅ Instrumentación automática ASP.NET Core
        .AddAspNetCoreInstrumentation()

        // ✅ Instrumentación automática HttpClient
        .AddHttpClientInstrumentation()

        // ✅ Runtime metrics (.NET)
        .AddRuntimeInstrumentation()

        // ✅ Métricas custom
        .AddMeter("Talma.Orders.Api")

        // ✅ Exportar a Grafana Alloy via OTLP
        .AddOtlpExporter(options =>
        {
            options.Endpoint = new Uri("http://grafana-alloy:4317");
            options.Protocol = OpenTelemetry.Exporter.OtlpExportProtocol.Grpc;
        })
    );

var app = builder.Build();
app.Run();
```

### RED Metrics - Rate, Errors, Duration (Servicios)

```csharp
using System.Diagnostics.Metrics;

public class OrderService
{
    private static readonly Meter _meter = new("Talma.Orders.Api", "1.0.0");

    // ✅ R - Rate: Requests por segundo
    private static readonly Counter<long> _ordersCreatedCounter = _meter.CreateCounter<long>(
        name: "orders.created",
        unit: "orders",
        description: "Total number of orders created"
    );

    // ✅ E - Errors: Errores por tipo
    private static readonly Counter<long> _ordersErrorCounter = _meter.CreateCounter<long>(
        name: "orders.errors",
        unit: "errors",
        description: "Total number of order processing errors"
    );

    // ✅ D - Duration: Latencia de operaciones
    private static readonly Histogram<double> _orderProcessingDuration = _meter.CreateHistogram<double>(
        name: "orders.processing.duration",
        unit: "ms",
        description: "Duration of order processing operations"
    );

    // ✅ Gauge: Estado actual (órdenes pendientes)
    private static readonly ObservableGauge<int> _pendingOrdersGauge = _meter.CreateObservableGauge(
        name: "orders.pending",
        observeValue: () => GetPendingOrdersCount(),
        unit: "orders",
        description: "Current number of pending orders"
    );

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            var order = await CreateOrderInternalAsync(request);

            // ✅ Incrementar counter con tags
            _ordersCreatedCounter.Add(1, new TagList
            {
                { "customer.type", request.CustomerType },
                { "country", request.Country },
                { "status", "success" }
            });

            // ✅ Registrar duración
            _orderProcessingDuration.Record(
                stopwatch.Elapsed.TotalMilliseconds,
                new TagList
                {
                    { "operation", "create" },
                    { "status", "success" }
                }
            );

            return order;
        }
        catch (ValidationException ex)
        {
            // ✅ Registrar error con tipo
            _ordersErrorCounter.Add(1, new TagList
            {
                { "error.type", "validation" },
                { "operation", "create" }
            });

            _orderProcessingDuration.Record(
                stopwatch.Elapsed.TotalMilliseconds,
                new TagList
                {
                    { "operation", "create" },
                    { "status", "error" }
                }
            );

            throw;
        }
        catch (Exception ex)
        {
            _ordersErrorCounter.Add(1, new TagList
            {
                { "error.type", "internal" },
                { "operation", "create" }
            });

            throw;
        }
    }
}

// Queries PromQL en Grafana:
// Rate: rate(orders_created_total[5m])
// Errors: rate(orders_errors_total[5m])
// Duration p95: histogram_quantile(0.95, rate(orders_processing_duration_bucket[5m]))
```

### USE Metrics - Utilization, Saturation, Errors (Recursos)

```csharp
public class DatabaseMetrics
{
    private static readonly Meter _meter = new("Talma.Orders.Database", "1.0.0");

    // ✅ U - Utilization: % uso de conexiones
    private static readonly ObservableGauge<double> _connectionPoolUtilization = _meter.CreateObservableGauge(
        name: "db.connection.pool.utilization",
        observeValue: () => GetConnectionPoolUtilization(),
        unit: "percent",
        description: "Database connection pool utilization percentage"
    );

    // ✅ S - Saturation: Conexiones en espera
    private static readonly ObservableGauge<int> _connectionPoolSaturation = _meter.CreateObservableGauge(
        name: "db.connection.pool.queue_size",
        observeValue: () => GetQueuedConnectionRequests(),
        unit: "connections",
        description: "Number of connection requests waiting in queue"
    );

    // ✅ E - Errors: Errores de conexión
    private static readonly Counter<long> _connectionErrors = _meter.CreateCounter<long>(
        name: "db.connection.errors",
        unit: "errors",
        description: "Total number of database connection errors"
    );

    // Query duration
    private static readonly Histogram<double> _queryDuration = _meter.CreateHistogram<double>(
        name: "db.query.duration",
        unit: "ms",
        description: "Database query execution duration"
    );

    private static double GetConnectionPoolUtilization()
    {
        // Implementar lógica para obtener % de conexiones usadas
        var total = 100; // Max pool size
        var used = 15;   // Active connections
        return (used / (double)total) * 100;
    }
}

// Queries:
// Utilization: db_connection_pool_utilization
// Saturation: db_connection_pool_queue_size
// Errors: rate(db_connection_errors_total[5m])
```

### Métricas HTTP Automáticas

```csharp
// ✅ ASP.NET Core instrumentación automática provee:
// - http.server.request.duration (latencia)
// - http.server.active_requests (requests concurrentes)
// - http.server.response.body.size (tamaño respuesta)

// Tags automáticos:
// - http.request.method (GET, POST, etc.)
// - http.response.status_code (200, 404, 500)
// - http.route (/api/v1/orders/{id})
// - network.protocol.version (HTTP/1.1, HTTP/2)

// Query en Grafana:
// Latencia p95 por endpoint:
// histogram_quantile(0.95,
//   sum(rate(http_server_request_duration_bucket[5m])) by (le, http_route)
// )

// Error rate por endpoint:
// sum(rate(http_server_request_duration_count{http_response_status_code=~"5.."}[5m])) by (http_route)
// /
// sum(rate(http_server_request_duration_count[5m])) by (http_route)
```

### Métricas de Negocio

```csharp
public class OrderMetrics
{
    private static readonly Meter _meter = new("Talma.Orders.Business", "1.0.0");

    // ✅ Counter: Eventos discretos
    private static readonly Counter<long> _orderValueCounter = _meter.CreateCounter<long>(
        name: "orders.total_value",
        unit: "USD",
        description: "Total value of orders processed"
    );

    // ✅ Histogram: Distribución de valores
    private static readonly Histogram<double> _orderAmountHistogram = _meter.CreateHistogram<double>(
        name: "orders.amount",
        unit: "USD",
        description: "Distribution of order amounts"
    );

    // ✅ UpDownCounter: Valores que suben y bajan
    private static readonly UpDownCounter<int> _activeOrdersUpDownCounter = _meter.CreateUpDownCounter<int>(
        name: "orders.active",
        unit: "orders",
        description: "Number of active orders (can increase or decrease)"
    );

    public void RecordOrderCreated(Order order)
    {
        // Total value
        _orderValueCounter.Add((long)order.TotalAmount, new TagList
        {
            { "country", order.Country },
            { "customer.segment", order.CustomerSegment }
        });

        // Amount distribution
        _orderAmountHistogram.Record(order.TotalAmount, new TagList
        {
            { "country", order.Country }
        });

        // Active orders +1
        _activeOrdersUpDownCounter.Add(1, new TagList
        {
            { "status", "active" }
        });
    }

    public void RecordOrderCompleted(Order order)
    {
        // Active orders -1
        _activeOrdersUpDownCounter.Add(-1, new TagList
        {
            { "status", "active" }
        });
    }
}
```

### Instrumentación de Kafka Consumer

```csharp
public class KafkaConsumerMetrics
{
    private static readonly Meter _meter = new("Talma.Orders.Kafka", "1.0.0");

    private static readonly Counter<long> _messagesConsumed = _meter.CreateCounter<long>(
        name: "kafka.messages.consumed",
        unit: "messages",
        description: "Total messages consumed from Kafka"
    );

    private static readonly Counter<long> _messageProcessingErrors = _meter.CreateCounter<long>(
        name: "kafka.messages.errors",
        unit: "errors",
        description: "Total message processing errors"
    );

    private static readonly Histogram<double> _messageProcessingDuration = _meter.CreateHistogram<double>(
        name: "kafka.message.processing.duration",
        unit: "ms",
        description: "Message processing duration"
    );

    private static readonly Histogram<double> _messageLag = _meter.CreateHistogram<double>(
        name: "kafka.consumer.lag",
        unit: "ms",
        description: "Consumer lag (time between produce and consume)"
    );

    public async Task ProcessMessageAsync(ConsumeResult<string, string> result)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            // Calculate lag
            var produceTime = result.Message.Timestamp.UtcDateTime;
            var consumeTime = DateTime.UtcNow;
            var lagMs = (consumeTime - produceTime).TotalMilliseconds;

            _messageLag.Record(lagMs, new TagList
            {
                { "topic", result.Topic },
                { "partition", result.Partition.Value.ToString() }
            });

            // Process message
            await ProcessMessageInternalAsync(result);

            _messagesConsumed.Add(1, new TagList
            {
                { "topic", result.Topic },
                { "status", "success" }
            });

            _messageProcessingDuration.Record(
                stopwatch.Elapsed.TotalMilliseconds,
                new TagList
                {
                    { "topic", result.Topic },
                    { "status", "success" }
                }
            );
        }
        catch (Exception ex)
        {
            _messageProcessingErrors.Add(1, new TagList
            {
                { "topic", result.Topic },
                { "error.type", ex.GetType().Name }
            });

            throw;
        }
    }
}
```

### Exportar a Grafana Mimir

```yaml
# Grafana Alloy configuration
otelcol.receiver.otlp "default" {
grpc {
endpoint = "0.0.0.0:4317"
}
}

otelcol.processor.batch "default" {
timeout = "10s"
send_batch_size = 1024
output {
metrics = [otelcol.exporter.prometheus.mimir.input]
}
}

otelcol.exporter.prometheus "mimir" {
forward_to = [prometheus.remote_write.mimir.receiver]
}

prometheus.remote_write "mimir" {
endpoint {
url = "http://mimir:9009/api/v1/push"
}
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar OpenTelemetry SDK para métricas en .NET
- **MUST** implementar RED metrics para todos los servicios
  - Rate (requests/sec)
  - Errors (error rate)
  - Duration (latencia p50, p95, p99)
- **MUST** implementar USE metrics para recursos críticos
  - Utilization (% usage)
  - Saturation (queue depth)
  - Errors (error rate)
- **MUST** exportar métricas a Grafana Mimir via OTLP
- **MUST** incluir tags relevantes (endpoint, status, country, etc.)
- **MUST** usar Counter para eventos incrementales
- **MUST** usar Histogram para distribuciones (latencia, tamaños)
- **MUST** usar Gauge para valores instantáneos
- **MUST** nombrar métricas con prefijo de dominio (`orders.created`, no `created`)

### SHOULD (Fuertemente recomendado)

- **SHOULD** instrumentar operaciones de negocio críticas
- **SHOULD** medir latencia de dependencias (DB, Kafka, HTTP)
- **SHOULD** incluir resource attributes (service.name, environment)
- **SHOULD** usar UpDownCounter para valores que suben/bajan
- **SHOULD** configurar batch processor para reducir overhead
- **SHOULD** limitar cardinalidad de tags (no IDs únicos)
- **SHOULD** documentar métricas custom en README

### MAY (Opcional)

- **MAY** emitir métricas de negocio adicionales (revenue, conversions)
- **MAY** usar ejemplares (exemplars) para link con traces
- **MAY** implementar sampling para métricas de alta cardinalidad

### MUST NOT (Prohibido)

- **MUST NOT** usar tags de alta cardinalidad (user_id, request_id)
- **MUST NOT** emitir métricas en hot paths sin batching
- **MUST NOT** duplicar métricas (enviar a múltiples backends)
- **MUST NOT** incluir información sensible en tags
- **MUST NOT** crear métricas sin descripción

---

## Referencias

- [Lineamiento: Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md)
- Estándares relacionados:
  - [Structured Logging](structured-logging.md)
  - [Distributed Tracing](distributed-tracing.md)
  - [SLIs y SLOs](slo-sla.md)
- Especificaciones:
  - [OpenTelemetry Metrics](https://opentelemetry.io/docs/specs/otel/metrics/)
  - [RED Method](https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/)
  - [USE Method](https://www.brendangregg.com/usemethod.html)
  - [Grafana Mimir](https://grafana.com/docs/mimir/)
