---
id: testing-strategy
sidebar_position: 2
title: Testing Strategy
description: Estrategia comprehensiva de testing con pirámide de tests y cobertura adecuada
---

# Testing Strategy

## Contexto

Este estándar define **estrategia de testing comprehensiva**: combinar unit, integration y E2E tests para validar funcionalidad con **confianza** y **eficiencia**. Complementa el [lineamiento de Arquitectura Evolutiva](../../lineamientos/arquitectura/12-arquitectura-evolutiva.md) asegurando capacidad de **cambiar sin romper**.

---

## Pirámide de Testing

```yaml
# ✅ Testing Pyramid (Martin Fowler)

       /\
      /E2E\        ~50 tests, 5s cada uno, cover happy paths
     /------\
    /Integration\ ~500 tests, 100ms cada uno, cover críticos
   /------------\
  /  Unit Tests  \ ~5000 tests, 1ms cada uno, cover lógica
 /----------------\

Distribución recomendada:
  - 70% Unit tests (lógica de negocio)
  - 20% Integration tests (DB, HTTP, Kafka)
  - 10% E2E tests (user journeys)

Características por tipo:
  Unit:
    ✅ Fast (~1ms)
    ✅ Isolated (no DB, no network)
    ✅ Many (miles)
    Scope: Método/clase individual

  Integration:
    ✅ Medium speed (~100ms)
    ✅ Real dependencies (DB, Kafka)
    ✅ Some (cientos)
    Scope: Múltiples componentes

  E2E:
    ✅ Slow (~5s)
    ✅ Full stack (API → DB → UI)
    ✅ Few (decenas)
    Scope: User journey completo

Anti-pattern: Ice Cream Cone
       /\
      /Unit\       ❌ Pocos unit tests
     /------\
    /Integration\ ❌ Muchos integration (lentos)
   /------------\
  /     E2E      \ ❌ MUCHOS E2E (super lentos, frágiles)
 /----------------\
```

## Implementación: Testing Strategy en Sales Service

```yaml
# ✅ Sales Service Testing Strategy (ejemplo real)

Unit Tests: 847 tests, 1.2s total
  Domain Layer (94% coverage):
    - Order.cs: 45 tests
    - OrderLine.cs: 12 tests
    - Money.cs: 15 tests
    - OrderPricingService.cs: 23 tests

  Application Layer (82% coverage):
    - CreateOrderHandler: 18 tests (mocks: IOrderRepository, IEventPublisher)
    - ApproveOrderHandler: 12 tests
    - GetOrderQuery: 8 tests

  Execution: dotnet test --filter "Category=Unit"
  Time: <2 seconds

Integration Tests: 127 tests, 18s total
  Repository Tests (real DB):
    - OrderRepositoryTests: 15 tests (EF + PostgreSQL testcontainer)
    - Valida: Save, GetById, queries, concurrency

  Event Publisher Tests (real Kafka):
    - KafkaEventPublisherTests: 8 tests (Kafka testcontainer)
    - Valida: Publish, consume, serialization

  API Tests (TestServer):
    - OrdersControllerTests: 35 tests (in-memory DB)
    - Valida: HTTP endpoints, authentication, validation

  Execution: dotnet test --filter "Category=Integration"
  Time: ~20 seconds
  Environment: Testcontainers (Docker)

E2E Tests: 24 tests, 120s total
  Critical User Journeys:
    - Create order → Approve → Ship → Deliver: 1 test
    - Create order → Reject: 1 test
    - Create order → Cancel: 1 test

  Environment: Staging (real DB, real Kafka, real APIs)
  Execution: dotnet test --filter "Category=E2E"
  Time: ~2 min
  Frequency: Before deploy to production
```

## Unit Tests (ejemplo con Moq)

```csharp
// ✅ Unit test con mocks (no DB, no HTTP)

public class CreateOrderHandlerTests
{
    private readonly Mock<IOrderRepository> _orderRepoMock;
    private readonly Mock<IProductServiceClient> _productClientMock;
    private readonly Mock<IEventPublisher> _eventPublisherMock;
    private readonly CreateOrderHandler _handler;

    public CreateOrderHandlerTests()
    {
        _orderRepoMock = new Mock<IOrderRepository>();
        _productClientMock = new Mock<IProductServiceClient>();
        _eventPublisherMock = new Mock<IEventPublisher>();
        _handler = new CreateOrderHandler(_orderRepoMock.Object, _productClientMock.Object, _eventPublisherMock.Object);
    }

    [Fact]
    [Trait("Category", "Unit")]
    public async Task Should_Create_Order_And_Save()
    {
        // Arrange
        _productClientMock.Setup(x => x.GetProductAsync(It.IsAny<Guid>()))
            .ReturnsAsync(new ProductDto { ProductId = Guid.NewGuid(), Price = 100 });

        var command = new CreateOrderCommand(Guid.NewGuid(), new List<OrderItemDto> { new(Guid.NewGuid(), 5) });

        // Act
        var orderId = await _handler.ExecuteAsync(command);

        // Assert
        Assert.NotEqual(Guid.Empty, orderId);
        _orderRepoMock.Verify(x => x.SaveAsync(It.IsAny<Order>()), Times.Once);
        _eventPublisherMock.Verify(x => x.PublishAsync(It.IsAny<OrderCreated>()), Times.Once);
    }
}
```

## Integration Tests (con Testcontainers)

```csharp
// ✅ Integration test con PostgreSQL real (Testcontainers)

public class OrderRepositoryIntegrationTests : IAsyncLifetime
{
    private readonly PostgreSqlContainer _postgres;
    private SalesDbContext _context;
    private IOrderRepository _repository;

    public OrderRepositoryIntegrationTests()
    {
        _postgres = new PostgreSqlBuilder()
            .WithDatabase("sales_test")
            .WithUsername("test")
            .WithPassword("test")
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _postgres.StartAsync();

        var options = new DbContextOptionsBuilder<SalesDbContext>()
            .UseNpgsql(_postgres.GetConnectionString())
            .Options;

        _context = new SalesDbContext(options);
        await _context.Database.MigrateAsync();  // Run migrations

        _repository = new OrderRepository(_context);
    }

    [Fact]
    [Trait("Category", "Integration")]
    public async Task Should_Save_And_Retrieve_Order_With_Lines()
    {
        // Arrange
        var order = Order.Create(Guid.NewGuid());
        order.AddLine(Guid.NewGuid(), 5, Money.Dollars(100));
        order.AddLine(Guid.NewGuid(), 2, Money.Dollars(250));

        // Act
        await _repository.SaveAsync(order);
        var retrieved = await _repository.GetByIdAsync(order.OrderId);

        // Assert
        Assert.NotNull(retrieved);
        Assert.Equal(2, retrieved.Lines.Count);
        Assert.Equal(Money.Dollars(1000), retrieved.Total);
    }

    public async Task DisposeAsync()
    {
        await _context.DisposeAsync();
        await _postgres.DisposeAsync();
    }
}
```

## E2E Tests (con WebApplicationFactory)

```csharp
// ✅ E2E test: Full user journey

public class OrderE2ETests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public OrderE2ETests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    [Trait("Category", "E2E")]
    public async Task CompleteOrderFlow_Should_Succeed()
    {
        // 1. Create order
        var createRequest = new CreateOrderRequest(
            Guid.NewGuid(),
            new List<CreateOrderItemRequest> { new(Guid.NewGuid(), 5) }
        );

        var createResponse = await _client.PostAsJsonAsync("/api/v1/orders", createRequest);
        createResponse.EnsureSuccessStatusCode();
        var createResult = await createResponse.Content.ReadFromJsonAsync<CreateOrderResponse>();
        var orderId = createResult.OrderId;

        // 2. Get order (verify created)
        var getResponse = await _client.GetAsync($"/api/v1/orders/{orderId}");
        getResponse.EnsureSuccessStatusCode();
        var order = await getResponse.Content.ReadFromJsonAsync<OrderDto>();
        Assert.Equal("Pending", order.Status);

        // 3. Approve order
        var approveResponse = await _client.PostAsync($"/api/v1/orders/{orderId}/approve", null);
        approveResponse.EnsureSuccessStatusCode();

        // 4. Verify approved
        var verifyResponse = await _client.GetAsync($"/api/v1/orders/{orderId}");
        var approvedOrder = await verifyResponse.Content.ReadFromJsonAsync<OrderDto>();
        Assert.Equal("Approved", approvedOrder.Status);
    }
}
```

## Coverage Goals y Enforcement

```yaml
# ✅ Coverage targets en CI/CD

Global targets (enforced in GitHub Actions):
  Minimum: 80% overall
  Fail build if: <80%

Per-layer targets:
  Domain: 90%+ (lógica de negocio crítica)
  Application: 80%+ (orquestación)
  Infrastructure: <30% (usar integration tests, no unit)
  API: 60%+ (controllers son delgados)

Implementation:
  Tool: Coverlet + ReportGenerator
  Command: dotnet test --collect:"XPlat Code Coverage"
  Report: HTML + Cobertura XML
  Upload: Codecov, SonarCloud

GitHub Actions check:
  - name: Check Coverage
    run: |
      dotnet test --collect:"XPlat Code Coverage"
      reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage -reporttypes:Html
      COVERAGE=$(grep -oP 'Line coverage: \K[0-9.]+' coverage/index.html)
      if (( $(echo "$COVERAGE < 80" | bc -l) )); then
        echo "❌ Coverage $COVERAGE% < 80%"
        exit 1
      fi
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** seguir pirámide de testing (70% unit, 20% integration, 10% E2E)
- **MUST** alcanzar 80%+ coverage en Domain y Application
- **MUST** ejecutar unit tests en cada commit (<2s)
- **MUST** ejecutar integration tests pre-merge (<30s)
- **MUST** ejecutar E2E tests pre-deploy (<5min)
- **MUST** usar mocks en unit tests (no DB, no HTTP)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Testcontainers para integration tests
- **SHOULD** categorizar tests con Traits (Unit, Integration, E2E)
- **SHOULD** generar coverage reports en CI/CD
- **SHOULD** ejecutar tests en paralelo cuando posible

### MUST NOT (Prohibido)

- **MUST NOT** depender solo de E2E tests (pirámide invertida)
- **MUST NOT** acceder DB en unit tests
- **MUST NOT** ignorar tests fallidos
- **MUST NOT** deshabilitar coverage checks en CI/CD

---

## Referencias

- [Lineamiento: Arquitectura Evolutiva](../../lineamientos/arquitectura/12-arquitectura-evolutiva.md)
- [Unit Testing](./unit-testing.md)
- [Test Pyramid (Martin Fowler)](https://martinfowler.com/bliki/TestPyramid.html)
