---
id: timeouts
sidebar_position: 9
title: Configuración de Timeouts
description: Estándar para configuración de timeouts en HTTP, database, message brokers con valores por capa y propagación de CancellationToken
---

# Estándar Técnico — Configuración de Timeouts

---

## 1. Propósito

Evitar bloqueos indefinidos y liberar recursos rápidamente mediante timeouts configurados en cada capa (HTTP, database, cache, message broker), propagando `CancellationToken` y estableciendo valores conservadores basados en SLAs y percentiles p99.

---

## 2. Alcance

**Aplica a:**

- HttpClient para llamadas REST
- Conexiones a PostgreSQL
- Operaciones Redis
- Consumers de Kafka
- Operaciones S3/Blob Storage
- gRPC calls
- Operaciones async con `Task`

**No aplica a:**

- Background jobs de larga duración
- Batch processing
- File uploads >10MB (usar timeouts mayores)
- Streaming operations

---

## 3. Tecnologías Aprobadas

| Componente   | Tecnología                    | Versión mínima | Observaciones                 |
| ------------ | ----------------------------- | -------------- | ----------------------------- |
| **HTTP**     | HttpClient                    | .NET 8.0+      | `Timeout` property            |
| **Polly**    | Polly                         | 8.0+           | `TimeoutStrategy`             |
| **Database** | Npgsql                        | 8.0+           | `CommandTimeout`              |
| **EF Core**  | Microsoft.EntityFrameworkCore | 8.0+           | `CommandTimeout` en DbContext |
| **Redis**    | StackExchange.Redis           | 2.7+           | `SyncTimeout`, `AsyncTimeout` |
| **Kafka**    | Confluent.Kafka               | 2.3+           | `message.timeout.ms`          |
| **S3**       | AWSSDK.S3                     | 3.7+           | `Timeout` en ClientConfig     |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Timeouts por Capa

- [ ] **HTTP:** 10-30 segundos (según endpoint)
- [ ] **Database:** 5-30 segundos (queries simples vs complejos)
- [ ] **Cache (Redis):** 1-3 segundos
- [ ] **Message Broker:** 5-10 segundos para produce, 30s para consume
- [ ] **File Storage:** 60 segundos (uploads), 30 segundos (downloads)

### Propagación de CancellationToken

- [ ] Todos los métodos async reciben `CancellationToken cancellationToken`
- [ ] Propagación a llamadas downstream
- [ ] `HttpContext.RequestAborted` en APIs ASP.NET Core
- [ ] Verificar `cancellationToken.IsCancellationRequested` en loops

### Configuración de HttpClient

- [ ] `HttpClient.Timeout` configurado (default 100s es muy alto)
- [ ] Timeout por request usando `CancellationTokenSource`
- [ ] Timeout en handler con Polly

### Configuración de Database

- [ ] `CommandTimeout` en DbContext
- [ ] Connection timeout separado (< command timeout)
- [ ] Statement timeout en PostgreSQL

### Telemetría

- [ ] Log cuando timeout ocurre
- [ ] Métrica de timeout rate por endpoint/operación
- [ ] Distributed tracing con timeout spans
- [ ] Alertas en aumento de timeout rate

---

## 5. Prohibiciones

- ❌ Timeout infinito (`Timeout.InfiniteTimeSpan`)
- ❌ Timeout muy alto (>120 segundos) sin justificación
- ❌ Ignorar `CancellationToken` en métodos async
- ❌ No propagar cancellation token a downstream calls
- ❌ Catch de `TaskCanceledException` sin logging
- ❌ Timeout menor que retry delay acumulado
- ❌ Timeout sin monitoreo de métricas

---

## 6. Configuración Mínima

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// HttpClient con timeout
builder.Services.AddHttpClient("PaymentService", client =>
{
    client.BaseAddress = new Uri("https://api.payments.talma.com");
    client.Timeout = TimeSpan.FromSeconds(10); // Timeout global
})
.AddResilienceHandler("payment-timeout", builder =>
{
    // Timeout por request con Polly
    builder.AddTimeout(TimeSpan.FromSeconds(10));
});

// DbContext con timeout
builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    options.UseNpgsql(
        connectionString,
        npgsqlOptions =>
        {
            npgsqlOptions.CommandTimeout(30); // 30 segundos
        });
});

// Redis con timeout
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = "localhost:6379";
    options.ConfigurationOptions = new ConfigurationOptions
    {
        SyncTimeout = 1000,  // 1 segundo
        AsyncTimeout = 3000  // 3 segundos
    };
});

var app = builder.Build();

// Request timeout middleware
app.UseRequestTimeouts();

app.MapControllers()
   .WithRequestTimeout(TimeSpan.FromSeconds(30)); // Timeout de request

app.Run();
```

```json
// appsettings.json
{
  "Timeouts": {
    "Http": {
      "DefaultSeconds": 10,
      "PaymentService": 15,
      "ReportingService": 60
    },
    "Database": {
      "CommandTimeoutSeconds": 30,
      "ConnectionTimeoutSeconds": 5
    },
    "Redis": {
      "SyncTimeoutMs": 1000,
      "AsyncTimeoutMs": 3000
    },
    "Kafka": {
      "ProduceTimeoutMs": 10000,
      "ConsumeTimeoutMs": 30000
    }
  }
}
```

---

## 7. Ejemplos

### Controller con CancellationToken

```csharp
[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IOrderService _orderService;

    [HttpGet("{id}")]
    [RequestTimeout("00:00:10")] // Timeout de 10 segundos
    public async Task<IActionResult> GetOrder(
        Guid id,
        CancellationToken cancellationToken) // Propagación automática
    {
        var order = await _orderService.GetByIdAsync(id, cancellationToken);

        if (order == null)
            return NotFound();

        return Ok(order);
    }

    [HttpPost]
    public async Task<IActionResult> CreateOrder(
        [FromBody] CreateOrderRequest request,
        CancellationToken cancellationToken)
    {
        // Timeout custom para operación larga
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        cts.CancelAfter(TimeSpan.FromSeconds(30));

        var order = await _orderService.CreateAsync(request, cts.Token);

        return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
    }
}
```

### Service con propagación de CancellationToken

```csharp
public class OrderService : IOrderService
{
    private readonly HttpClient _paymentClient;
    private readonly ApplicationDbContext _context;
    private readonly IDistributedCache _cache;

    public async Task<Order> CreateAsync(
        CreateOrderRequest request,
        CancellationToken cancellationToken)
    {
        // 1. Validar disponibilidad de inventario
        await ValidateInventoryAsync(request.Items, cancellationToken);

        // 2. Crear orden en DB
        var order = new Order { /* ... */ };
        _context.Orders.Add(order);
        await _context.SaveChangesAsync(cancellationToken); // Propagar token

        // 3. Procesar pago
        var payment = await ProcessPaymentAsync(order, cancellationToken);

        // 4. Invalidar cache
        await _cache.RemoveAsync($"order:{order.Id}", cancellationToken);

        return order;
    }

    private async Task<PaymentResult> ProcessPaymentAsync(
        Order order,
        CancellationToken cancellationToken)
    {
        var request = new HttpRequestMessage(HttpMethod.Post, "/api/v1/payments")
        {
            Content = JsonContent.Create(new { orderId = order.Id, amount = order.Total })
        };

        // Timeout específico para esta llamada
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        cts.CancelAfter(TimeSpan.FromSeconds(15));

        var response = await _paymentClient.SendAsync(request, cts.Token);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<PaymentResult>(cancellationToken);
    }
}
```

### Database con timeout

```csharp
public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
        // Timeout global para todos los comandos
        Database.SetCommandTimeout(TimeSpan.FromSeconds(30));
    }

    public async Task<List<Order>> GetLargeReportAsync(CancellationToken cancellationToken)
    {
        // Timeout específico para query complejo
        var oldTimeout = Database.GetCommandTimeout();
        Database.SetCommandTimeout(TimeSpan.FromSeconds(120));

        try
        {
            return await Orders
                .Include(o => o.Items)
                .Include(o => o.Customer)
                .Where(o => o.CreatedAt > DateTime.UtcNow.AddYears(-1))
                .ToListAsync(cancellationToken);
        }
        finally
        {
            Database.SetCommandTimeout(oldTimeout);
        }
    }
}
```

### Polly timeout resilience

```csharp
public static class TimeoutConfiguration
{
    public static IServiceCollection AddTimeoutPolicies(
        this IServiceCollection services)
    {
        services.AddResiliencePipeline("default-timeout", builder =>
        {
            builder.AddTimeout(new TimeoutStrategyOptions
            {
                Timeout = TimeSpan.FromSeconds(10),
                OnTimeout = args =>
                {
                    Console.WriteLine($"Timeout después de {args.Timeout}");
                    return ValueTask.CompletedTask;
                }
            });
        });

        // Timeout optimista (fail-fast) + timeout pesimista (cleanup)
        services.AddResiliencePipeline("aggressive-timeout", builder =>
        {
            builder
                .AddTimeout(TimeSpan.FromSeconds(5))   // Optimista
                .AddTimeout(TimeSpan.FromSeconds(15)); // Pesimista
        });

        return services;
    }
}
```

---

## 8. Validación y Auditoría

```bash
# Verificar timeouts en HttpClients
grep -r "client.Timeout" --include="*.cs" ./

# Verificar propagación de CancellationToken
grep -r "CancellationToken" --include="*.cs" ./ | wc -l

# Métricas de timeouts
curl http://localhost:5000/metrics | grep timeout
```

**Métricas de cumplimiento:**

| Métrica                             | Umbral       | Verificación           |
| ----------------------------------- | ------------ | ---------------------- |
| Métodos async con CancellationToken | >95%         | Code analysis          |
| HttpClients con timeout configurado | 100%         | Code review            |
| Timeout rate                        | <1%          | Métricas de producción |
| Timeout logs                        | 100% eventos | Verificar logging      |

**Checklist de auditoría:**

- [ ] Todos los HttpClients tienen timeout <60s
- [ ] DbContext tiene CommandTimeout configurado
- [ ] Métodos async reciben y propagan CancellationToken
- [ ] Timeouts monitoreados con métricas
- [ ] Alertas configuradas para timeout rate >1%

---

## 9. Referencias

- [ASP.NET Core Request Timeouts](https://learn.microsoft.com/en-us/aspnet/core/performance/timeouts)
- [Polly Timeout Strategy](https://www.pollydocs.org/strategies/timeout)
- [CancellationToken Best Practices](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)
- [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Google SRE Book - Timeouts](https://sre.google/sre-book/addressing-cascading-failures/)
- [AWS SDK Timeout Configuration](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/retries-timeouts.html)
