---
id: dependency-management
sidebar_position: 1
title: Gestión de Dependencias entre Servicios
description: Estándar para gestión de dependencias entre microservicios con acoplamiento loose, contratos versionados, dependency injection y detección de ciclos
---

# Estándar Técnico — Gestión de Dependencias entre Servicios

---

## 1. Propósito

Minimizar acoplamiento entre servicios mediante gestión explícita de dependencias, contratos versionados, dependency injection, detección de ciclos y comunicación asíncrona preferida sobre síncrona.

---

## 2. Alcance

**Aplica a:**

- Dependencias entre microservicios
- Contratos de API (REST/gRPC)
- Eventos y mensajes
- Librerías compartidas
- Bases de datos compartidas (minimizar)
- Servicios de terceros

**No aplica a:**

- Dependencias internas de un monolito
- Librerías framework (.NET, logging, etc.)
- Dependencias de infraestructura (Kubernetes, AWS)

---

## 3. Tecnologías Aprobadas

| Componente              | Tecnología                               | Versión mínima | Observaciones        |
| ----------------------- | ---------------------------------------- | -------------- | -------------------- |
| **DI Container**        | Microsoft.Extensions.DependencyInjection | .NET 8+        | Built-in DI          |
| **API Contracts**       | OpenAPI 3.1                              | -              | REST contracts       |
| **Event Schema**        | JSON Schema                              | -              | Event contracts      |
| **Versioning**          | Semantic Versioning                      | 2.0+           | API/library versions |
| **Dependency Analysis** | NDepend / dotnet-depends                 | -              | Análisis estático    |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Principios de Diseño

- [ ] **Loose coupling:** minimizar dependencias directas
- [ ] **High cohesion:** funcionalidad relacionada en mismo servicio
- [ ] **Dependency inversion:** depender de abstracciones, no implementaciones
- [ ] **Async over sync:** preferir comunicación asíncrona
- [ ] **Shared nothing:** evitar bases de datos compartidas

### Contratos de API

- [ ] OpenAPI spec para todas las APIs REST
- [ ] Semantic versioning (v1, v2) en URLs
- [ ] Backward compatibility por mínimo 6 meses
- [ ] Deprecation warnings con 3 meses de anticipación
- [ ] Contratos publicados en repositorio central

### Dependency Injection

- [ ] Todas las dependencias inyectadas (no `new`)
- [ ] Interfaces para abstracciones
- [ ] Lifetimes apropiados (Singleton, Scoped, Transient)
- [ ] No service locator pattern

### Detección de Dependencias Cíclicas

- [ ] No dependencias circulares entre servicios
- [ ] Análisis estático en CI/CD
- [ ] Dependency graph documentado
- [ ] Máximo 3 niveles de dependencia transitiva

### Telemetría

- [ ] Tracking de llamadas entre servicios
- [ ] Dependency map en APM tool
- [ ] Alertas para alta latencia en dependencias
- [ ] Circuit breakers para dependencias críticas

---

## 5. Prohibiciones

- ❌ Dependencias circulares entre servicios
- ❌ Llamadas síncronas en cadena (>2 niveles)
- ❌ Bases de datos compartidas entre servicios
- ❌ `new` directo de dependencias (usar DI)
- ❌ Hardcoded URLs de servicios
- ❌ Breaking changes sin versionado
- ❌ Static dependencies (usar injection)

---

## 6. Configuración Mínima

```csharp
// Program.cs - Dependency Injection
var builder = WebApplication.CreateBuilder(args);

// Interfaces para abstracciones
builder.Services.AddScoped<IOrderService, OrderService>();
builder.Services.AddScoped<IOrderRepository, OrderRepository>();

// HttpClient para dependencias externas
builder.Services.AddHttpClient<IPaymentServiceClient, PaymentServiceClient>((client) =>
{
    client.BaseAddress = new Uri(builder.Configuration["Services:PaymentService:Url"]!);
    client.Timeout = TimeSpan.FromSeconds(30);
})
.AddResilienceHandler("payment-resilience", pipelineBuilder =>
{
    pipelineBuilder
        .AddCircuitBreaker(new CircuitBreakerStrategyOptions
        {
            FailureRatio = 0.5,
            MinimumThroughput = 5
        })
        .AddRetry(new RetryStrategyOptions
        {
            MaxRetryAttempts = 3
        });
});

// Event bus para comunicación asíncrona
builder.Services.AddMassTransit(x =>
{
    x.AddConsumers(typeof(Program).Assembly);
    x.UsingInMemory((context, cfg) =>
    {
        cfg.ConfigureEndpoints(context);
    });
    // Para producción, usar Kafka transport
    // Ver: estandares/mensajeria/kafka-events.md
});

var app = builder.Build();
app.Run();
```

```json
// appsettings.json
{
  "Services": {
    "PaymentService": {
      "Url": "https://api-payment.talma.com",
      "Timeout": 30,
      "CircuitBreaker": {
        "FailureThreshold": 5,
        "DurationSeconds": 60
      }
    },
    "InventoryService": {
      "Url": "https://api-inventory.talma.com",
      "Timeout": 10
    }
  },
  "Kafka": {
    "BootstrapServers": "kafka.talma.com:9092"
  }
}
```

---

## 7. Ejemplos

### Abstracción con interfaces

```csharp
// IPaymentServiceClient.cs - Abstracción
public interface IPaymentServiceClient
{
    Task<PaymentResult> ProcessPaymentAsync(
        decimal amount,
        string customerId,
        CancellationToken cancellationToken = default);
}

// PaymentServiceClient.cs - Implementación HTTP
public class PaymentServiceClient : IPaymentServiceClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<PaymentServiceClient> _logger;

    public PaymentServiceClient(
        HttpClient httpClient,
        ILogger<PaymentServiceClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<PaymentResult> ProcessPaymentAsync(
        decimal amount,
        string customerId,
        CancellationToken cancellationToken = default)
    {
        var request = new { amount, customerId };
        var response = await _httpClient.PostAsJsonAsync(
            "/api/v1/payments",
            request,
            cancellationToken);

        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<PaymentResult>(cancellationToken);
    }
}

// OrderService.cs - Uso de abstracción
public class OrderService : IOrderService
{
    private readonly IPaymentServiceClient _paymentClient; // Abstracción
    private readonly IOrderRepository _repository;

    public OrderService(
        IPaymentServiceClient paymentClient,  // Inyectado
        IOrderRepository repository)
    {
        _paymentClient = paymentClient;
        _repository = repository;
    }

    public async Task<Order> CreateOrderAsync(
        CreateOrderRequest request,
        CancellationToken cancellationToken)
    {
        var order = new Order { /* ... */ };
        await _repository.AddAsync(order, cancellationToken);

        // Llamada a dependencia
        var payment = await _paymentClient.ProcessPaymentAsync(
            order.TotalAmount,
            order.CustomerId,
            cancellationToken);

        order.PaymentId = payment.Id;
        await _repository.UpdateAsync(order, cancellationToken);

        return order;
    }
}
```

### Comunicación asíncrona (preferida)

```csharp
// Event - Contrato de evento
public record OrderCreatedEvent
{
    public Guid OrderId { get; init; }
    public Guid CustomerId { get; init; }
    public decimal TotalAmount { get; init; }
    public List<OrderItem> Items { get; init; }
}

// Producer - Publicar evento
public class OrderService : IOrderService
{
    private readonly IPublishEndpoint _publishEndpoint;

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        var order = new Order { /* ... */ };
        await _repository.AddAsync(order);

        // Publicar evento asíncrono (fire-and-forget)
        await _publishEndpoint.Publish(new OrderCreatedEvent
        {
            OrderId = order.Id,
            CustomerId = order.CustomerId,
            TotalAmount = order.TotalAmount,
            Items = order.Items
        });

        return order;
    }
}

// Consumer - Procesar evento en otro servicio
public class InventoryService : IConsumer<OrderCreatedEvent>
{
    public async Task Consume(ConsumeContext<OrderCreatedEvent> context)
    {
        var orderId = context.Message.OrderId;

        // Reservar inventario asíncronamente
        foreach (var item in context.Message.Items)
        {
            await ReserveInventoryAsync(item.ProductId, item.Quantity);
        }
    }
}
```

### Detección de dependencias cíclicas

```csharp
// ServiceDependencyAnalyzer.cs
public class ServiceDependencyAnalyzer
{
    private readonly Dictionary<string, List<string>> _dependencies = new();

    public void AddDependency(string service, string dependsOn)
    {
        if (!_dependencies.ContainsKey(service))
            _dependencies[service] = new List<string>();

        _dependencies[service].Add(dependsOn);
    }

    public bool HasCyclicDependency(string service)
    {
        var visited = new HashSet<string>();
        var stack = new HashSet<string>();

        return HasCycle(service, visited, stack);
    }

    private bool HasCycle(string service, HashSet<string> visited, HashSet<string> stack)
    {
        if (stack.Contains(service))
            return true; // Ciclo detectado

        if (visited.Contains(service))
            return false;

        visited.Add(service);
        stack.Add(service);

        if (_dependencies.TryGetValue(service, out var dependencies))
        {
            foreach (var dependency in dependencies)
            {
                if (HasCycle(dependency, visited, stack))
                    return true;
            }
        }

        stack.Remove(service);
        return false;
    }
}

// Test
[Fact]
public void DetectCyclicDependencies()
{
    var analyzer = new ServiceDependencyAnalyzer();

    analyzer.AddDependency("OrderService", "PaymentService");
    analyzer.AddDependency("OrderService", "InventoryService");
    analyzer.AddDependency("PaymentService", "NotificationService");
    // ❌ Ciclo:
    // analyzer.AddDependency("InventoryService", "OrderService");

    Assert.False(analyzer.HasCyclicDependency("OrderService"));
}
```

### API contract versioning

```csharp
// V1 - Versión inicial
[ApiController]
[Route("api/v1/orders")]
public class OrdersV1Controller : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> CreateOrder(
        [FromBody] CreateOrderV1Request request)
    {
        // Implementación V1
    }
}

// V2 - Nueva versión con cambios
[ApiController]
[Route("api/v2/orders")]
public class OrdersV2Controller : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> CreateOrder(
        [FromBody] CreateOrderV2Request request)  // Nuevo contrato
    {
        // Implementación V2 con nuevos campos
    }
}

// Deprecation warning en V1
[Obsolete("Use /api/v2/orders. V1 will be removed on 2025-06-01.")]
public class CreateOrderV1Request { /* ... */ }
```

---

## 8. Validación y Auditoría

```bash
# Analizar dependencias con dotnet-depends
dotnet tool install -g dotnet-depends
dotnet depends analyze -i ./OrderService/bin/Debug/net8.0/OrderService.dll

# Detectar dependencias cíclicas
grep -r "AddHttpClient" --include="*.cs" ./ | sort

# Generar dependency graph
dotnet list package --include-transitive > dependencies.txt
```

**Métricas de cumplimiento:**

| Métrica               | Umbral     | Verificación    |
| --------------------- | ---------- | --------------- |
| Dependencias cíclicas | 0          | Static analysis |
| APIs con OpenAPI spec | 100%       | CI/CD check     |
| Contratos versionados | 100%       | Code review     |
| Dependency injection  | 100%       | Code review     |
| Max dependency depth  | ≤3 niveles | Analysis tool   |

**Checklist de auditoría:**

- [ ] No dependencias circulares
- [ ] Todas las dependencias inyectadas
- [ ] APIs con contratos OpenAPI
- [ ] Versionado semántico
- [ ] Comunicación asíncrona preferida
- [ ] Circuit breakers en dependencias
- [ ] Dependency graph documentado

---

## 9. Referencias

- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
- [Microservices Patterns - Sam Newman](https://samnewman.io/books/building_microservices_2nd_edition/)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Microsoft DI Container](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)
- [API Versioning Best Practices](https://www.troyhunt.com/your-api-versioning-is-wrong-which-is/)
- [Martin Fowler - Consumer-Driven Contracts](https://martinfowler.com/articles/consumerDrivenContracts.html)
