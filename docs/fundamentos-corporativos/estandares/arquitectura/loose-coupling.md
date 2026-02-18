---
id: loose-coupling
sidebar_position: 6
title: Loose Coupling
description: Diseñar componentes con bajo acoplamiento para facilitar cambios independientes
---

# Loose Coupling

## Contexto

Este estándar define **loose coupling** (bajo acoplamiento): componentes deben depender de **abstracciones** (no implementaciones), comunicarse via **contratos estables**, y poder **cambiar independientemente**. Complementa el [lineamiento de Arquitectura Evolutiva](../../lineamientos/arquitectura/12-arquitectura-evolutiva.md) permitiendo **evolución sin cascada de cambios**.

---

## Conceptos Fundamentales

```yaml
# ✅ Loose Coupling = Componentes independientes comunicándose via contratos

Definición: Grado en que un componente tiene conocimiento sobre otro componente.
  Bajo acoplamiento = mínimo conocimiento = máxima independencia.

Tipos de Acoplamiento (de peor a mejor):
  ❌ Content Coupling: A modifica estado interno de B
  ❌ Common Coupling: A y B comparten estado global
  ❌ Control Coupling: A controla flujo de B
  ❌ Stamp Coupling: A y B comparten estructura de datos compleja
  ✅ Data Coupling: A pasa solo datos necesarios a B
  ✅ Message Coupling: A y B se comunican via mensajes async

Beneficios:
  ✅ Changeability: Cambiar A sin afectar B
  ✅ Testability: Testear A sin instanciar B
  ✅ Reusability: Reusar A en otro contexto
  ✅ Parallel Development: Equipos trabajan independientemente

Técnicas:
  1. Dependency Inversion: Depender de interfaces
  2. Event-Driven: Comunicación asíncrona via eventos
  3. API Contracts: Contratos versionados estables
  4. Database per Service: No shared database
  5. Facade Pattern: Ocultar complejidad detrás de interfaz simple
```

## Anti-Pattern: Tight Coupling

```csharp
// ❌ TIGHT COUPLING: OrderService conoce detalles de implementación

public class OrderService
{
    // ❌ Dependencia directa en DbContext (implementación)
    private readonly SalesDbContext _dbContext;

    // ❌ Dependencia directa en Kafka producer
    private readonly IProducer<string, string> _kafkaProducer;

    // ❌ Dependencia directa en HTTP client concreto
    private readonly HttpClient _httpClient;

    public OrderService(SalesDbContext dbContext, IProducer<string, string> producer, HttpClient httpClient)
    {
        _dbContext = dbContext;
        _kafkaProducer = producer;
        _httpClient = httpClient;
    }

    public async Task CreateOrderAsync(Order order)
    {
        // ❌ Usa detalles de EF directamente
        _dbContext.Orders.Add(order);
        await _dbContext.SaveChangesAsync();

        // ❌ Conoce detalles de Kafka
        var message = JsonSerializer.Serialize(order);
        await _kafkaProducer.ProduceAsync("orders", new Message<string, string>
        {
            Key = order.OrderId.ToString(),
            Value = message
        });

        // ❌ Conoce URL y formato de HTTP
        await _httpClient.PostAsJsonAsync("http://catalog-service/api/v1/inventory/reserve", new
        {
            orderId = order.OrderId,
            items = order.Lines
        });
    }
}

// Problemas:
// 1. No se puede testear sin DB real, Kafka real, HTTP real
// 2. Cambiar de PostgreSQL a MongoDB requiere cambiar OrderService
// 3. Cambiar de Kafka a RabbitMQ requiere cambiar OrderService
// 4. OrderService expuesto a cambios en todos estos componentes
```

## Pattern: Loose Coupling con Dependency Inversion

```csharp
// ✅ LOOSE COUPLING: OrderService depende de abstracciones

public class OrderService
{
    // ✅ Abstracción (no implementación)
    private readonly IOrderRepository _orderRepo;
    private readonly IEventPublisher _eventPublisher;
    private readonly IInventoryServiceClient _inventoryClient;

    public OrderService(IOrderRepository orderRepo, IEventPublisher eventPublisher, IInventoryServiceClient inventoryClient)
    {
        _orderRepo = orderRepo;
        _eventPublisher = eventPublisher;
        _inventoryClient = inventoryClient;
    }

    public async Task CreateOrderAsync(Order order)
    {
        // ✅ Usa abstracción (no sabe si es EF, Dapper, MongoDB)
        await _orderRepo.SaveAsync(order);

        // ✅ Usa abstracción (no sabe si es Kafka, RabbitMQ, SNS)
        await _eventPublisher.PublishAsync(new OrderCreated
        {
            OrderId = order.OrderId,
            CustomerId = order.CustomerId
        });

        // ✅ Usa abstracción (no sabe URL ni transport)
        await _inventoryClient.ReserveAsync(order.OrderId, order.Lines);
    }
}

// Interfaces (abstracciones estables):
public interface IOrderRepository
{
    Task SaveAsync(Order order);
    Task<Order?> GetByIdAsync(Guid orderId);
}

public interface IEventPublisher
{
    Task PublishAsync<T>(T domainEvent) where T : DomainEvent;
}

public interface IInventoryServiceClient
{
    Task ReserveAsync(Guid orderId, IEnumerable<OrderLine> items);
}

// Beneficios:
// 1. ✅ Testeable con mocks (no DB, no Kafka, no HTTP)
// 2. ✅ Cambiar DB solo requiere nuevo adapter (OrderService sin cambios)
// 3. ✅ Cambiar messaging solo requiere nuevo adapter
// 4. ✅ OrderService aislado de cambios en infraestructura
```

## Loose Coupling entre Servicios (Event-Driven)

```csharp
// ✅ Event-Driven Communication (bajo acoplamiento)

// Sales Service publica evento (no conoce consumers)
public class OrderService
{
    public async Task ApproveOrderAsync(Guid orderId)
    {
        var order = await _orderRepo.GetByIdAsync(orderId);
        order.Approve();

        await _orderRepo.SaveAsync(order);

        // ✅ Publica evento sin saber quién lo consume
        await _eventPublisher.PublishAsync(new OrderApproved
        {
            OrderId = order.OrderId,
            CustomerId = order.CustomerId,
            Total = order.Total,
            ApprovedAt = DateTime.UtcNow
        });
    }
}

// Fulfillment Service consume evento (no conoce Sales)
public class OrderApprovedConsumer : IConsumer<OrderApproved>
{
    public async Task Consume(ConsumeContext<OrderApproved> context)
    {
        var evt = context.Message;

        // ✅ Reacciona a evento sin acoplarse a Sales Service
        var shipment = Shipment.Create(evt.OrderId, evt.CustomerId);
        await _shipmentRepo.SaveAsync(shipment);
    }
}

// Billing Service también consume (independiente de Fulfillment)
public class OrderApprovedConsumer : IConsumer<OrderApproved>
{
    public async Task Consume(ConsumeContext<OrderApproved> context)
    {
        var evt = context.Message;

        // ✅ Genera factura sin acoplarse a Sales ni Fulfillment
        var invoice = Invoice.Create(evt.OrderId, evt.Total);
        await _invoiceRepo.SaveAsync(invoice);
    }
}

// Ventajas:
// - Sales NO conoce Fulfillment ni Billing (desacoplados)
// - Agregar nuevo consumer (Payment Service) sin tocar Sales
// - Cada servicio evoluciona independientemente
```

## Loose Coupling en Contratos de API

```csharp
// ✅ API Contracts estables con versionado

// v1: Contrato inicial
[ApiController]
[Route("api/v1/orders")]
public class OrdersControllerV1 : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> CreateOrder(CreateOrderRequestV1 request)
    {
        // ✅ v1 contract
        var command = new CreateOrderCommand(
            request.CustomerId,
            request.Items
        );
        var orderId = await _createOrderUseCase.ExecuteAsync(command);
        return CreatedAtAction(nameof(GetOrder), new { id = orderId }, new { orderId });
    }
}

public record CreateOrderRequestV1(
    Guid CustomerId,
    List<OrderItemDto> Items
);

// v2: Nuevo contrato (agrega campo discount)
[ApiController]
[Route("api/v2/orders")]
public class OrdersControllerV2 : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> CreateOrder(CreateOrderRequestV2 request)
    {
        // ✅ v2 contract (nuevo campo opcional)
        var command = new CreateOrderCommand(
            request.CustomerId,
            request.Items,
            request.DiscountCode  // ✅ Nuevo campo
        );
        var orderId = await _createOrderUseCase.ExecuteAsync(command);
        return CreatedAtAction(nameof(GetOrder), new { id = orderId }, new { orderId });
    }
}

public record CreateOrderRequestV2(
    Guid CustomerId,
    List<OrderItemDto> Items,
    string? DiscountCode  // ✅ Opcional (backward compatible)
);

// Beneficios:
// - Clientes de v1 NO afectados (loose coupling)
// - Nuevos clientes usan v2
// - Ambas versiones coexisten (6+ meses)
// - Deprecar v1 gradualmente sin romper clientes
```

## Medición de Acoplamiento

```csharp
// ✅ Fitness Function: Detectar acoplamiento excesivo

public class CouplingFitnessTests
{
    [Fact]
    public void Domain_Should_Not_Depend_On_Infrastructure()
    {
        // ✅ Validar que Domain no referencia Infrastructure
        var domainAssembly = typeof(Order).Assembly;
        var references = domainAssembly.GetReferencedAssemblies()
            .Select(a => a.Name)
            .ToList();

        Assert.DoesNotContain("Talma.Sales.Infrastructure", references);
        Assert.DoesNotContain("EntityFrameworkCore", references);
    }

    [Fact]
    public void Services_Should_Not_Have_Circular_Dependencies()
    {
        // ✅ Detectar dependencias cíclicas
        var services = new[] { "Sales", "Catalog", "Fulfillment", "Billing" };
        var graph = BuildDependencyGraph(services);
        var cycles = FindCycles(graph);

        Assert.Empty(cycles);
    }

    [Fact]
    public void API_Contracts_Should_Be_Versionadas()
    {
        // ✅ Validar que endpoints usan versionado
        var controllers = typeof(Program).Assembly.GetTypes()
            .Where(t => t.IsSubclassOf(typeof(ControllerBase)))
            .ToList();

        foreach (var controller in controllers)
        {
            var routeAttr = controller.GetCustomAttribute<RouteAttribute>();
            Assert.Matches(@"api/v\d+/", routeAttr.Template);  // api/v1/, api/v2/
        }
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** depender de abstracciones (interfaces), no implementaciones
- **MUST** usar event-driven communication entre servicios (no llamadas síncronas directas)
- **MUST** versionar APIs para evitar breaking changes
- **MUST** implementar database per service (no shared DB)
- **MUST** validar ausencia de dependencias circulares (fitness function)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar facade pattern para ocultar complejidad
- **SHOULD** mantener contratos de API estables (backward compatible)
- **SHOULD** limitar número de dependencias por componente (<10)
- **SHOULD** documentar acoplamiento aceptable (ADR)

### MUST NOT (Prohibido)

- **MUST NOT** crear dependencias cíclicas entre servicios
- **MUST NOT** acceder base de datos de otro servicio directamente
- **MUST NOT** exponer detalles de implementación en interfaces públicas
- **MUST NOT** hacer breaking changes en APIs sin versionado

---

## Referencias

- [Lineamiento: Arquitectura Evolutiva](../../lineamientos/arquitectura/12-arquitectura-evolutiva.md)
- [Dependency Inversion](./dependency-inversion.md)
- [Event-Driven Architecture](../../comunicacion/event-driven-architecture.md)
