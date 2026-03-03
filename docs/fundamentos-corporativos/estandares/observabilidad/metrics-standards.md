---
id: metrics-standards
sidebar_position: 3
title: Métricas con OpenTelemetry
description: Estándar para instrumentación de métricas con OpenTelemetry y almacenamiento en Grafana Mimir.
tags: [observabilidad, métricas, opentelemetry, mimir]
---

# Métricas con OpenTelemetry

## Contexto

Este estándar define cómo instrumentar aplicaciones .NET con métricas OpenTelemetry para monitorear performance, salud y comportamiento de negocio en tiempo real. Complementa el lineamiento [Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) asegurando visibilidad cuantitativa del sistema para alertas proactivas y capacity planning.

---

## Stack Tecnológico

| Componente          | Tecnología    | Versión | Uso                                     |
| ------------------- | ------------- | ------- | --------------------------------------- |
| **Instrumentation** | OpenTelemetry | 1.7+    | SDK de métricas para .NET               |
| **Metrics Storage** | Grafana Mimir | 2.10+   | Base de datos time-series para métricas |
| **Agent**           | Grafana Alloy | 1.0+    | Recibe OTLP y reenvía a Mimir           |

---

## ¿Qué son las Métricas?

Mediciones numéricas time-series sobre el comportamiento y performance de la aplicación (ej. total de requests, latencia, tasa de errores, uso de memoria). A diferencia de los logs, las métricas son agregables y eficientes para monitoreo continuo.

**Tipos de instrumentos OpenTelemetry:**

- **Counter** — Valor acumulativo que solo incrementa (ej. total requests, total órdenes creadas)
- **Gauge** — Valor instantáneo que sube o baja (ej. conexiones activas, uso de memoria)
- **Histogram** — Distribución de valores con percentiles (ej. latencia, tamaño de response)

**Beneficios:**

- ✅ Monitoreo en tiempo real con bajo overhead
- ✅ Alertas proactivas basadas en umbrales numéricos
- ✅ Análisis de tendencias y capacity planning
- ✅ Correlación con logs y trazas mediante atributos comunes

---

## Configuración OpenTelemetry

```csharp
// Program.cs
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService("customer-service", serviceVersion: "1.2.3"))
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()   // Métricas HTTP automáticas
        .AddRuntimeInstrumentation()      // Métricas del runtime .NET
        .AddHttpClientInstrumentation()   // Métricas de HttpClient
        .AddMeter("CustomerService.Metrics")  // Meter de métricas de negocio
        .AddOtlpExporter(options =>
        {
            options.Endpoint = new Uri("http://grafana-alloy:4317");
            options.Protocol = OtlpExportProtocol.Grpc;
        }));
```

:::note Configurado por Plataforma
La configuración de Grafana Alloy para recibir métricas OTLP y reenviarlas a Mimir es responsabilidad del equipo de Plataforma.
Ver [Plataforma Corporativa](../../../plataforma-corporativa/) para detalles de infraestructura.
:::

---

## Métricas Personalizadas

Definir un `Meter` por servicio con los instrumentos necesarios:

```csharp
// Metrics/ApplicationMetrics.cs
using System.Diagnostics.Metrics;

public class ApplicationMetrics
{
    private readonly Meter _meter;

    private readonly Counter<long> _ordersCreated;
    private readonly Counter<long> _ordersFailed;
    private readonly Counter<long> _paymentsProcessed;
    private readonly ObservableGauge<int> _activeOrders;
    private readonly Histogram<double> _orderProcessingDuration;

    public ApplicationMetrics(IMeterFactory meterFactory)
    {
        _meter = meterFactory.Create("CustomerService.Metrics", "1.0.0");

        _ordersCreated = _meter.CreateCounter<long>(
            "orders.created",
            unit: "{order}",
            description: "Total number of orders created");

        _ordersFailed = _meter.CreateCounter<long>(
            "orders.failed",
            unit: "{order}",
            description: "Total number of failed order creations");

        _paymentsProcessed = _meter.CreateCounter<long>(
            "payments.processed",
            unit: "{payment}",
            description: "Total number of payments processed");

        _activeOrders = _meter.CreateObservableGauge<int>(
            "orders.active",
            observeValue: () => GetActiveOrdersCount(),
            unit: "{order}",
            description: "Current number of active orders");

        _orderProcessingDuration = _meter.CreateHistogram<double>(
            "orders.processing.duration",
            unit: "ms",
            description: "Order processing duration in milliseconds");
    }

    public void RecordOrderCreated(string status) =>
        _ordersCreated.Add(1, new KeyValuePair<string, object>("status", status));

    public void RecordOrderFailed(string reason) =>
        _ordersFailed.Add(1, new KeyValuePair<string, object>("reason", reason));

    public void RecordOrderProcessingDuration(double durationMs, bool success) =>
        _orderProcessingDuration.Record(
            durationMs,
            new KeyValuePair<string, object>("success", success));

    private int GetActiveOrdersCount() =>
        // Consultar DB o cache en implementación real
        42;
}

// Registrar como singleton
builder.Services.AddSingleton<ApplicationMetrics>();
```

---

## Uso en Controllers y Services

```csharp
public class OrderController : ControllerBase
{
    private readonly IOrderService _orderService;
    private readonly ApplicationMetrics _metrics;
    private readonly ILogger<OrderController> _logger;

    [HttpPost]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            var order = await _orderService.CreateOrderAsync(request);
            stopwatch.Stop();

            _metrics.RecordOrderCreated(order.Status);
            _metrics.RecordOrderProcessingDuration(stopwatch.Elapsed.TotalMilliseconds, success: true);

            _logger.LogInformation(
                "Order created: {OrderId} {TotalAmount} {Duration}ms",
                order.Id, order.TotalAmount, stopwatch.ElapsedMilliseconds);

            return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
        }
        catch (ValidationException ex)
        {
            stopwatch.Stop();
            _metrics.RecordOrderFailed("validation");
            _metrics.RecordOrderProcessingDuration(stopwatch.Elapsed.TotalMilliseconds, success: false);

            _logger.LogWarning(ex, "Order validation failed");
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _metrics.RecordOrderFailed("internal_error");
            _metrics.RecordOrderProcessingDuration(stopwatch.Elapsed.TotalMilliseconds, success: false);

            _logger.LogError(ex, "Order creation failed");
            return StatusCode(500);
        }
    }
}
```

---

## Catálogo de Métricas

**Métricas HTTP** (auto-instrumentadas por ASP.NET Core):

| Métrica                         | Tipo      | Descripción             |
| ------------------------------- | --------- | ----------------------- |
| `http.server.request.duration`  | Histogram | Latencia de requests    |
| `http.server.active_requests`   | Gauge     | Requests en curso       |
| `http.server.request.body.size` | Histogram | Tamaño del request body |

**Métricas del runtime .NET** (auto-instrumentadas):

| Métrica                                            | Tipo    | Descripción          |
| -------------------------------------------------- | ------- | -------------------- |
| `process.runtime.dotnet.gc.heap.size`              | Gauge   | Tamaño del heap      |
| `process.runtime.dotnet.thread_pool.threads.count` | Gauge   | Threads en el pool   |
| `process.runtime.dotnet.exceptions.count`          | Counter | Excepciones lanzadas |

**Métricas de negocio** (definir por servicio):

| Métrica                      | Tipo      | Descripción                          |
| ---------------------------- | --------- | ------------------------------------ |
| `orders.created`             | Counter   | Órdenes creadas                      |
| `orders.failed`              | Counter   | Órdenes fallidas                     |
| `orders.active`              | Gauge     | Órdenes activas en este momento      |
| `orders.processing.duration` | Histogram | Duración de procesamiento de órdenes |
| `payments.processed`         | Counter   | Pagos procesados                     |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** instrumentar la aplicación con OpenTelemetry Metrics 1.7+
- **MUST** exportar métricas vía OTLP a Grafana Alloy en `http://grafana-alloy:4317`
- **MUST** incluir instrumentación automática de ASP.NET Core (`AddAspNetCoreInstrumentation`)
- **MUST** incluir instrumentación del runtime .NET (`AddRuntimeInstrumentation`)
- **MUST** definir un `Meter` con nombre propio del servicio para métricas de negocio
- **MUST** seguir la convención de nomenclatura OpenTelemetry: `snake_case`, unidades explícitas

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar Histograms para medir distribuciones de latencia y tamaños
- **SHOULD** agregar atributos (tags) a métricas para segmentación (status, reason, method)
- **SHOULD** registrar `ApplicationMetrics` como singleton para reutilizar los instrumentos
- **SHOULD** incluir instrumentación de `HttpClient` si el servicio hace llamadas externas

### MUST NOT (Prohibido)

- **MUST NOT** crear un nuevo `Meter` por request o por operación (costoso)
- **MUST NOT** usar nombres de métricas inconsistentes entre servicios del mismo dominio
- **MUST NOT** omitir la propiedad `unit` en la descripción de instrumentos

---

## Referencias

- [Lineamiento de Observabilidad](../../lineamientos/arquitectura/06-observabilidad.md) — lineamiento que origina este estándar
- [Structured Logging](./structured-logging.md) — complementa este estándar con logs contextuales
- [Dashboards en Grafana](./dashboards.md) — visualización de las métricas aquí definidas
- [Alertas](./alerting.md) — alertas basadas en las métricas aquí definidas
- [OpenTelemetry Metrics](https://opentelemetry.io/docs/specs/otel/metrics/) — especificación oficial
- [.NET OpenTelemetry](https://github.com/open-telemetry/opentelemetry-dotnet) — SDK para .NET
- [Grafana Mimir](https://grafana.com/docs/mimir/latest/) — almacenamiento de métricas
