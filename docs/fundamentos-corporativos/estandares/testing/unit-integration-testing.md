---
id: unit-integration-testing
sidebar_position: 2
title: Unit & Integration Testing
description: Estándares para unit tests con xUnit/Moq y integration tests con WebApplicationFactory y Testcontainers
---

# Unit & Integration Testing

## Contexto

Este estándar consolida **2 conceptos relacionados** con testing de componentes individuales (unit) y su integración (integration). Define patrones AAA, mocking, test fixtures y uso de Testcontainers.

**Conceptos incluidos:**

- **Unit Testing** → Tests aislados de lógica de negocio (xUnit, Moq, FluentAssertions)
- **Integration Testing** → Tests de integración entre capas (WebApplicationFactory, Testcontainers)

---

## Stack Tecnológico

| Componente              | Tecnología            | Versión | Uso                                 |
| ----------------------- | --------------------- | ------- | ----------------------------------- |
| **Unit Test Framework** | xUnit                 | 2.6+    | Framework principal                 |
| **Assertions**          | FluentAssertions      | 6.12+   | Assertions legibles                 |
| **Mocking**             | Moq                   | 4.20+   | Mocking de dependencias             |
| **Test Host**           | WebApplicationFactory | 8.0+    | In-memory test server               |
| **Containers**          | Testcontainers        | 3.7+    | PostgreSQL, Kafka, Redis containers |
| **Fixture Management**  | xUnit IClassFixture   | 2.6+    | Shared test context                 |
| **Fake Data**           | Bogus                 | 35.0+   | Generación de datos de prueba       |

---

## Conceptos Fundamentales

Este estándar cubre **2 tipos** de tests:

### Índice de Conceptos

1. **Unit Testing**: Tests aislados, rápidos, sin dependencias externas
2. **Integration Testing**: Tests que verifican integración real entre componentes

### Comparación Unit vs Integration

| Aspecto             | Unit Tests           | Integration Tests                  |
| ------------------- | -------------------- | ---------------------------------- |
| **Alcance**         | Método/clase aislado | Múltiples capas (API → DB → Kafka) |
| **Velocidad**       | Milisegundos         | Segundos                           |
| **Dependencies**    | Mocked               | Reales (Testcontainers)            |
| **Setup**           | Mínimo               | Containers, migrations, seed data  |
| **Propósito**       | Verificar lógica     | Verificar integración              |
| **Cuando ejecutar** | Cada commit          | Pre-merge, pre-deploy              |

---

## 1. Unit Testing

### ¿Qué es Unit Testing?

Tests que verifican comportamiento de una unidad de código (método, clase) de forma aislada, mockeando todas las dependencias externas.

**Propósito:** Validar lógica de negocio sin infraestructura.

**Patrón AAA:**

- **Arrange**: Preparar datos de prueba
- **Act**: Ejecutar método bajo test
- **Assert**: Verificar resultado

**Beneficios:**
✅ Ejecución ultra-rápida (< 1ms por test)
✅ Tests deterministicos
✅ Facilita TDD
✅ Alta cobertura con bajo esfuerzo

### Ejemplo: Test de Domain Model

```csharp
// src/OrderService.Domain/Aggregates/Order.cs
public class Order
{
    public int Id { get; private set; }
    public string CustomerId { get; private set; }
    public List<OrderItem> Items { get; private set; } = new();
    public OrderStatus Status { get; private set; }

    public decimal Subtotal => Items.Sum(i => i.UnitPrice * i.Quantity);
    public decimal Tax { get; private set; }
    public decimal Total => Subtotal + Tax;

    public void CalculateTax(decimal taxRate)
    {
        if (taxRate < 0 || taxRate > 1)
            throw new ArgumentException("Tax rate must be between 0 and 1", nameof(taxRate));

        Tax = Subtotal * taxRate;
    }

    public void Cancel()
    {
        if (Status == OrderStatus.Cancelled)
            throw new InvalidOperationException("Order is already cancelled");

        if (Status == OrderStatus.Shipped)
            throw new InvalidOperationException("Cannot cancel shipped order");

        Status = OrderStatus.Cancelled;
    }
}

// tests/OrderService.Tests/Domain/OrderTests.cs
using FluentAssertions;
using OrderService.Domain.Aggregates;
using Xunit;

public class OrderTests
{
    [Fact]
    public void CalculateTax_WithValidRate_ShouldCalculateCorrectly()
    {
        // Arrange
        var order = new Order
        {
            Items = new List<OrderItem>
            {
                new OrderItem { UnitPrice = 100m, Quantity = 2 },
                new OrderItem { UnitPrice = 50m, Quantity = 1 }
            }
        };

        // Act
        order.CalculateTax(0.18m); // 18% tax

        // Assert
        order.Subtotal.Should().Be(250m);
        order.Tax.Should().Be(45m); // 250 * 0.18
        order.Total.Should().Be(295m);
    }

    [Theory]
    [InlineData(-0.1)]
    [InlineData(1.1)]
    [InlineData(2)]
    public void CalculateTax_WithInvalidRate_ShouldThrowArgumentException(decimal invalidRate)
    {
        // Arrange
        var order = new Order();

        // Act
        Action act = () => order.CalculateTax(invalidRate);

        // Assert
        act.Should().Throw<ArgumentException>()
            .WithMessage("*Tax rate must be between 0 and 1*")
            .And.ParamName.Should().Be("taxRate");
    }

    [Fact]
    public void Cancel_WhenOrderIsPending_ShouldCancelSuccessfully()
    {
        // Arrange
        var order = new Order { Status = OrderStatus.Pending };

        // Act
        order.Cancel();

        // Assert
        order.Status.Should().Be(OrderStatus.Cancelled);
    }

    [Fact]
    public void Cancel_WhenOrderIsShipped_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var order = new Order { Status = OrderStatus.Shipped };

        // Act
        Action act = () => order.Cancel();

        // Assert
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("Cannot cancel shipped order");
    }

    [Fact]
    public void Cancel_WhenOrderAlreadyCancelled_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var order = new Order { Status = OrderStatus.Cancelled };

        // Act
        Action act = () => order.Cancel();

        // Assert
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("Order is already cancelled");
    }
}
```

### Mocking con Moq

```csharp
// src/OrderService.Application/Services/OrderService.cs
public class OrderService
{
    private readonly IOrderRepository _orderRepository;
    private readonly IPaymentService _paymentService;
    private readonly INotificationService _notificationService;
    private readonly ILogger<OrderService> _logger;

    public OrderService(
        IOrderRepository orderRepository,
        IPaymentService paymentService,
        INotificationService notificationService,
        ILogger<OrderService> logger)
    {
        _orderRepository = orderRepository;
        _paymentService = paymentService;
        _notificationService = notificationService;
        _logger = logger;
    }

    public async Task<CreateOrderResult> CreateOrderAsync(CreateOrderRequest request)
    {
        // 1. Validar customer
        var customer = await _orderRepository.GetCustomerAsync(request.CustomerId);
        if (customer == null)
            throw new NotFoundException($"Customer {request.CustomerId} not found");

        // 2. Crear order
        var order = new Order
        {
            CustomerId = request.CustomerId,
            Items = request.Items.Select(i => new OrderItem
            {
                Sku = i.Sku,
                Quantity = i.Quantity,
                UnitPrice = i.UnitPrice
            }).ToList()
        };
        order.CalculateTax(0.18m);

        // 3. Procesar payment
        var paymentResult = await _paymentService.ProcessPaymentAsync(new PaymentRequest
        {
            Amount = order.Total,
            CustomerId = request.CustomerId,
            PaymentMethod = request.PaymentMethod
        });

        if (!paymentResult.Success)
            throw new PaymentFailedException("Payment processing failed");

        // 4. Guardar order
        await _orderRepository.SaveAsync(order);

        // 5. Enviar notificación (fire and forget)
        _ = _notificationService.SendOrderConfirmationAsync(order.Id);

        _logger.LogInformation("Order {OrderId} created for customer {CustomerId}", order.Id, request.CustomerId);

        return new CreateOrderResult { OrderId = order.Id, TotalAmount = order.Total };
    }
}

// tests/OrderService.Tests/Application/OrderServiceTests.cs
using Moq;
using FluentAssertions;

public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _repositoryMock;
    private readonly Mock<IPaymentService> _paymentServiceMock;
    private readonly Mock<INotificationService> _notificationServiceMock;
    private readonly Mock<ILogger<OrderService>> _loggerMock;
    private readonly OrderService _sut; // System Under Test

    public OrderServiceTests()
    {
        _repositoryMock = new Mock<IOrderRepository>();
        _paymentServiceMock = new Mock<IPaymentService>();
        _notificationServiceMock = new Mock<INotificationService>();
        _loggerMock = new Mock<ILogger<OrderService>>();

        _sut = new OrderService(
            _repositoryMock.Object,
            _paymentServiceMock.Object,
            _notificationServiceMock.Object,
            _loggerMock.Object);
    }

    [Fact]
    public async Task CreateOrderAsync_WithValidRequest_ShouldCreateOrderSuccessfully()
    {
        // Arrange
        var request = new CreateOrderRequest
        {
            CustomerId = "CUST-123",
            Items = new List<OrderItemRequest>
            {
                new() { Sku = "SKU-001", Quantity = 2, UnitPrice = 100m }
            },
            PaymentMethod = "credit_card"
        };

        var customer = new Customer { Id = "CUST-123", Name = "John Doe" };

        _repositoryMock
            .Setup(r => r.GetCustomerAsync(request.CustomerId))
            .ReturnsAsync(customer);

        _paymentServiceMock
            .Setup(p => p.ProcessPaymentAsync(It.IsAny<PaymentRequest>()))
            .ReturnsAsync(new PaymentResult { Success = true, TransactionId = "TXN-123" });

        _repositoryMock
            .Setup(r => r.SaveAsync(It.IsAny<Order>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _sut.CreateOrderAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.OrderId.Should().BeGreaterThan(0);
        result.TotalAmount.Should().Be(236m); // 200 subtotal + 36 tax (18%)

        // Verify interactions
        _repositoryMock.Verify(r => r.GetCustomerAsync(request.CustomerId), Times.Once);
        _paymentServiceMock.Verify(
            p => p.ProcessPaymentAsync(It.Is<PaymentRequest>(pr =>
                pr.Amount == 236m &&
                pr.CustomerId == "CUST-123" &&
                pr.PaymentMethod == "credit_card")),
            Times.Once);
        _repositoryMock.Verify(r => r.SaveAsync(It.IsAny<Order>()), Times.Once);
        _notificationServiceMock.Verify(
            n => n.SendOrderConfirmationAsync(It.IsAny<int>()),
            Times.Once);
    }

    [Fact]
    public async Task CreateOrderAsync_WhenCustomerNotFound_ShouldThrowNotFoundException()
    {
        // Arrange
        var request = new CreateOrderRequest { CustomerId = "INVALID" };

        _repositoryMock
            .Setup(r => r.GetCustomerAsync(request.CustomerId))
            .ReturnsAsync((Customer)null);

        // Act
        Func<Task> act = async () => await _sut.CreateOrderAsync(request);

        // Assert
        await act.Should().ThrowAsync<NotFoundException>()
            .WithMessage("Customer INVALID not found");

        // Payment y Save NO deben ejecutarse
        _paymentServiceMock.Verify(
            p => p.ProcessPaymentAsync(It.IsAny<PaymentRequest>()),
            Times.Never);
        _repositoryMock.Verify(r => r.SaveAsync(It.IsAny<Order>()), Times.Never);
    }

    [Fact]
    public async Task CreateOrderAsync_WhenPaymentFails_ShouldThrowPaymentFailedException()
    {
        // Arrange
        var request = new CreateOrderRequest
        {
            CustomerId = "CUST-123",
            Items = new List<OrderItemRequest>
            {
                new() { Sku = "SKU-001", Quantity = 1, UnitPrice = 100m }
            },
            PaymentMethod = "credit_card"
        };

        _repositoryMock
            .Setup(r => r.GetCustomerAsync(request.CustomerId))
            .ReturnsAsync(new Customer { Id = "CUST-123" });

        _paymentServiceMock
            .Setup(p => p.ProcessPaymentAsync(It.IsAny<PaymentRequest>()))
            .ReturnsAsync(new PaymentResult { Success = false, ErrorMessage = "Insufficient funds" });

        // Act
        Func<Task> act = async () => await _sut.CreateOrderAsync(request);

        // Assert
        await act.Should().ThrowAsync<PaymentFailedException>()
            .WithMessage("Payment processing failed");

        // Order NO debe guardarse
        _repositoryMock.Verify(r => r.SaveAsync(It.IsAny<Order>()), Times.Never);
    }
}
```

### Test Data Builders (Pattern)

```csharp
// tests/OrderService.Tests/Builders/OrderBuilder.cs
public class OrderBuilder
{
    private int _id = 1;
    private string _customerId = "CUST-123";
    private OrderStatus _status = OrderStatus.Pending;
    private List<OrderItem> _items = new();

    public OrderBuilder WithId(int id)
    {
        _id = id;
        return this;
    }

    public OrderBuilder WithCustomerId(string customerId)
    {
        _customerId = customerId;
        return this;
    }

    public OrderBuilder WithStatus(OrderStatus status)
    {
        _status = status;
        return this;
    }

    public OrderBuilder WithItem(string sku, int quantity, decimal unitPrice)
    {
        _items.Add(new OrderItem
        {
            Sku = sku,
            Quantity = quantity,
            UnitPrice = unitPrice
        });
        return this;
    }

    public Order Build()
    {
        var order = new Order
        {
            Id = _id,
            CustomerId = _customerId,
            Status = _status,
            Items = _items
        };
        return order;
    }
}

// Uso en tests
[Fact]
public void Example_UsingBuilder()
{
    // Arrange
    var order = new OrderBuilder()
        .WithId(123)
        .WithCustomerId("CUST-456")
        .WithItem("SKU-001", 2, 100m)
        .WithItem("SKU-002", 1, 50m)
        .WithStatus(OrderStatus.Pending)
        .Build();

    // Act & Assert
    order.Subtotal.Should().Be(250m);
}
```

---

## 2. Integration Testing

### ¿Qué es Integration Testing?

Tests que verifican integración real entre componentes usando infraestructura real (DB, message brokers) vía Testcontainers.

**Propósito:** Validar que componentes trabajan juntos correctamente.

**Componentes:**

- **WebApplicationFactory**: In-memory test server
- **Testcontainers**: Docker containers para dependencies
- **Test Fixtures**: Shared context entre tests

**Beneficios:**
✅ Alta confianza (infraestructura real)
✅ Detecta problemas de integración
✅ Valida migrations, queries, serialization
✅ Fast feedback (segundos, no minutos)

### WebApplicationFactory: API Integration Tests

```csharp
// tests/OrderService.IntegrationTests/CustomWebApplicationFactory.cs
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Testcontainers.PostgreSql;

public class CustomWebApplicationFactory<TProgram>
    : WebApplicationFactory<TProgram>, IAsyncLifetime where TProgram : class
{
    private readonly PostgreSqlContainer _postgresContainer = new PostgreSqlBuilder()
        .WithImage("postgres:15")
        .WithDatabase("orders_test")
        .WithUsername("postgres")
        .WithPassword("postgres")
        .Build();

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // Remover DbContext real
            var descriptor = services.SingleOrDefault(
                d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
            if (descriptor != null)
                services.Remove(descriptor);

            // Agregar DbContext de test con Testcontainer
            services.AddDbContext<AppDbContext>(options =>
            {
                options.UseNpgsql(_postgresContainer.GetConnectionString());
            });

            // Seed database
            var sp = services.BuildServiceProvider();
            using var scope = sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            db.Database.Migrate(); // Ejecutar migrations
            SeedTestData(db);
        });
    }

    private void SeedTestData(AppDbContext db)
    {
        db.Customers.AddRange(
            new Customer { Id = "CUST-123", Name = "John Doe", Email = "john@example.com" },
            new Customer { Id = "CUST-456", Name = "Jane Smith", Email = "jane@example.com" }
        );
        db.SaveChanges();
    }

    public async Task InitializeAsync()
    {
        await _postgresContainer.StartAsync();
    }

    public new async Task DisposeAsync()
    {
        await _postgresContainer.StopAsync();
    }
}

// tests/OrderService.IntegrationTests/Controllers/OrdersControllerTests.cs
using System.Net;
using System.Net.Http.Json;
using FluentAssertions;
using Xunit;

public class OrdersControllerTests : IClassFixture<CustomWebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    private readonly CustomWebApplicationFactory<Program> _factory;

    public OrdersControllerTests(CustomWebApplicationFactory<Program> factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task CreateOrder_WithValidRequest_ShouldReturn201Created()
    {
        // Arrange
        var request = new
        {
            customerId = "CUST-123",
            items = new[]
            {
                new { sku = "SKU-001", quantity = 2, unitPrice = 100.00 }
            },
            paymentMethod = "credit_card"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);

        var createdOrder = await response.Content.ReadFromJsonAsync<OrderResponse>();
        createdOrder.Should().NotBeNull();
        createdOrder.OrderId.Should().BeGreaterThan(0);
        createdOrder.TotalAmount.Should().Be(236m); // 200 + 18% tax

        response.Headers.Location.Should().NotBeNull();
        response.Headers.Location.ToString().Should().Contain($"/api/orders/{createdOrder.OrderId}");
    }

    [Fact]
    public async Task CreateOrder_WithInvalidCustomer_ShouldReturn404NotFound()
    {
        // Arrange
        var request = new
        {
            customerId = "INVALID",
            items = new[]
            {
                new { sku = "SKU-001", quantity = 1, unitPrice = 100.00 }
            }
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);

        var error = await response.Content.ReadFromJsonAsync<ProblemDetails>();
        error.Should().NotBeNull();
        error.Title.Should().Be("Customer not found");
    }

    [Fact]
    public async Task GetOrder_WhenExists_ShouldReturn200OK()
    {
        // Arrange - Crear order primero
        var createRequest = new
        {
            customerId = "CUST-123",
            items = new[] { new { sku = "SKU-001", quantity = 1, unitPrice = 100.00 } }
        };
        var createResponse = await _client.PostAsJsonAsync("/api/orders", createRequest);
        var createdOrder = await createResponse.Content.ReadFromJsonAsync<OrderResponse>();

        // Act
        var response = await _client.GetAsync($"/api/orders/{createdOrder.OrderId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var order = await response.Content.ReadFromJsonAsync<OrderResponse>();
        order.Should().NotBeNull();
        order.OrderId.Should().Be(createdOrder.OrderId);
        order.CustomerId.Should().Be("CUST-123");
        order.Items.Should().HaveCount(1);
    }

    [Fact]
    public async Task GetOrder_WhenNotExists_ShouldReturn404NotFound()
    {
        // Act
        var response = await _client.GetAsync("/api/orders/99999");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}
```

### Testcontainers: Múltiples Dependencies

```csharp
// tests/OrderService.IntegrationTests/Fixtures/IntegrationTestFixture.cs
using Testcontainers.PostgreSql;
using Testcontainers.Kafka;
using Testcontainers.Redis;

public class IntegrationTestFixture : IAsyncLifetime
{
    public PostgreSqlContainer PostgresContainer { get; }
    public KafkaContainer KafkaContainer { get; }
    public RedisContainer RedisContainer { get; }

    public IntegrationTestFixture()
    {
        PostgresContainer = new PostgreSqlBuilder()
            .WithImage("postgres:15")
            .WithDatabase("orders_test")
            .Build();

        KafkaContainer = new KafkaBuilder()
            .WithImage("confluentinc/cp-kafka:7.5.0")
            .Build();

        RedisContainer = new RedisBuilder()
            .WithImage("redis:7-alpine")
            .Build();
    }

    public async Task InitializeAsync()
    {
        await Task.WhenAll(
            PostgresContainer.StartAsync(),
            KafkaContainer.StartAsync(),
            RedisContainer.StartAsync()
        );
    }

    public async Task DisposeAsync()
    {
        await Task.WhenAll(
            PostgresContainer.StopAsync(),
            KafkaContainer.StopAsync(),
            RedisContainer.StopAsync()
        );
    }
}

// Uso en tests con múltiples containers
[Collection("Integration")]
public class OrderEventPublisherTests : IClassFixture<IntegrationTestFixture>
{
    private readonly IntegrationTestFixture _fixture;

    public OrderEventPublisherTests(IntegrationTestFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task PublishOrderCreatedEvent_ShouldPersistToKafka()
    {
        // Arrange
        var producer = new ProducerBuilder<string, string>(new ProducerConfig
        {
            BootstrapServers = _fixture.KafkaContainer.GetBootstrapAddress()
        }).Build();

        var orderEvent = new OrderCreatedEvent
        {
            OrderId = 123,
            CustomerId = "CUST-123",
            TotalAmount = 236m
        };

        // Act
        var result = await producer.ProduceAsync(
            "order-events",
            new Message<string, string>
            {
                Key = orderEvent.OrderId.ToString(),
                Value = JsonSerializer.Serialize(orderEvent)
            });

        // Assert
        result.Status.Should().Be(PersistenceStatus.Persisted);
        result.Partition.Should().BeGreaterOrEqualTo(0);
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

**Unit Tests:**

- **MUST** seguir patrón AAA (Arrange-Act-Assert)
- **MUST** mockear todas las dependencias externas
- **MUST** tests aislados (sin estado compartido)
- **MUST** nombres descriptivos (Given_When_Then o Should pattern)
- **MUST** FluentAssertions para assertions legibles
- **MUST** ejecutarse en < 5 minutos total

**Integration Tests:**

- **MUST** usar Testcontainers para dependencies (no mocks)
- **MUST** ejecutar migrations en test database
- **MUST** cleanup entre tests (transactions o recrear containers)
- **MUST** WebApplicationFactory para API tests
- **MUST** tests deterministicos (no depender de timing)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar test data builders para objetos complejos
- **SHOULD** parametrizar tests con [Theory] cuando sea posible
- **SHOULD** usar class fixtures para setup costoso compartido
- **SHOULD** Bogus para generar fake data realista
- **SHOULD** integration tests ejecutarse en < 10 minutos

### MUST NOT (Prohibido)

- **MUST NOT** unit tests tocando DB/filesystem/network
- **MUST NOT** tests con sleep/delays fijos
- **MUST NOT** assertions en múltiples conceptos (1 test = 1 concepto)
- **MUST NOT** dependencias entre tests (orden de ejecución)

---

## Referencias

- [xUnit Documentation](https://xunit.net/)
- [Moq Quick Start](https://github.com/moq/moq4)
- [FluentAssertions](https://fluentassertions.com/)
- [Testcontainers .NET](https://dotnet.testcontainers.org/)
- [WebApplicationFactory](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests)

**Relacionados:**

- [Testing Strategy](./testing-strategy.md)
- [Contract & E2E Testing](./contract-e2e-testing.md)

---

**Última actualización**: 2026-02-19
**Responsable**: Equipo de Arquitectura
