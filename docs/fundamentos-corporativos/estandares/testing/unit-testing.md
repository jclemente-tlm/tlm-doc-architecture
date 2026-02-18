---
id: unit-testing
sidebar_position: 1
title: Unit Testing
description: Testing de unidades de código en aislamiento para validar lógica de negocio
---

# Unit Testing

## Contexto

Este estándar define **unit testing**: pruebas automatizadas de unidades de código (clases, métodos) en completo **aislamiento** sin dependencias externas. Complementa el [lineamiento de Arquitectura Limpia](../../lineamientos/arquitectura/11-arquitectura-limpia.md) asegurando **calidad** y **confianza** en el código.

---

## Conceptos Fundamentales

### ¿Qué es Unit Testing?

```yaml
# ✅ Unit Testing = Pruebas rápidas y aisladas de lógica de negocio

Definición:
  Prueba automatizada que valida UNA unidad de código (clase/método)
  en completo AISLAMIENTO (sin DB, sin HTTP, sin filesystem).

Características:
  ✅ Fast: <10ms por test (típicamente <1ms)
  ✅ Isolated: Sin dependencias externas (no DB, no network)
  ✅ Repeatable: Mismo resultado siempre (determinístico)
  ✅ Self-Validating: Pasa o falla automáticamente
  ✅ Timely: Escrito antes o junto con código (TDD opcional)

Objetivo:
  Validar LÓGICA DE NEGOCIO (reglas, invariantes, cálculos)
  NO validar integración con frameworks o infraestructura.

Alcance:
  ✅ Domain entities (Order, Customer, Money)
  ✅ Domain services (OrderPricingService)
  ✅ Value objects (Money, Address)
  ✅ Application use cases (con mocks de dependencies)
  ❌ NO: Database queries (integration test)
  ❌ NO: HTTP calls (integration test)
  ❌ NO: Kafka consumers (integration test)

Frameworks en .NET:
  - xUnit (recomendado): Modern, extensible
  - NUnit: Clásico, rico en attributes
  - MSTest: Built-in Visual Studio
  - Moq: Mocking framework
  - FluentAssertions: Assertions más legibles
```

### Pirámide de Testing

```mermaid
graph TB
    subgraph "Testing Pyramid (Martin Fowler)"
        E2E[E2E Tests<br/>Few, Slow<br/>~100 tests]
        Integration[Integration Tests<br/>Some, Medium<br/>~500 tests]
        Unit[Unit Tests<br/>Many, Fast<br/>~5000 tests]
    end

    E2E --> Integration
    Integration --> Unit

    subgraph "Características"
        UnitChar[Unit Tests:<br/>- Fast (~1ms)<br/>- No external deps<br/>- High coverage 80%+<br/>- Run on every commit]
        IntChar[Integration Tests:<br/>- Medium (~100ms)<br/>- Real DB/Kafka<br/>- Critical paths<br/>- Run pre-merge]
        E2EChar[E2E Tests:<br/>- Slow (~5s)<br/>- Full stack<br/>- Happy paths<br/>- Run nightly]
    end

    style Unit fill:#90EE90
    style Integration fill:#FFD700
    style E2E fill:#FFA07A
```

## Anatomía de un Unit Test

```csharp
// ✅ Patrón AAA (Arrange-Act-Assert)

namespace Talma.Sales.Domain.Tests
{
    public class OrderTests
    {
        [Fact]  // ✅ xUnit attribute
        public void Submit_Should_Change_Status_To_Pending()
        {
            // ✅ ARRANGE: Preparar datos y estado inicial
            var customerId = Guid.NewGuid();
            var order = Order.Create(customerId);
            order.AddLine(Guid.NewGuid(), 5, Money.Dollars(100));

            // ✅ ACT: Ejecutar acción bajo prueba
            order.Submit();

            // ✅ ASSERT: Verificar resultado esperado
            Assert.Equal(OrderStatus.Pending, order.Status);
        }

        [Fact]
        public void Submit_Should_Throw_If_Order_Is_Empty()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());

            // Act & Assert: Verificar excepción
            var exception = Assert.Throws<DomainException>(() => order.Submit());
            Assert.Contains("without lines", exception.Message);
        }

        [Theory]  // ✅ Data-driven test
        [InlineData(1, 100, 100)]
        [InlineData(5, 100, 500)]
        [InlineData(10, 50, 500)]
        public void AddLine_Should_Calculate_Subtotal_Correctly(int quantity, decimal unitPrice, decimal expectedSubtotal)
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());
            var productId = Guid.NewGuid();

            // Act
            order.AddLine(productId, quantity, Money.Dollars(unitPrice));

            // Assert
            var line = order.Lines.First();
            Assert.Equal(Money.Dollars(expectedSubtotal), line.Subtotal);
        }
    }
}
```

## Testing Domain Entities

```csharp
// ✅ Unit tests comprehensivos para Order entity

namespace Talma.Sales.Domain.Tests.Model
{
    public class OrderTests
    {
        // ✅ Test factory method
        [Fact]
        public void Create_Should_Generate_Valid_Order()
        {
            // Arrange
            var customerId = Guid.NewGuid();

            // Act
            var order = Order.Create(customerId);

            // Assert
            Assert.NotEqual(Guid.Empty, order.OrderId);
            Assert.Equal(customerId, order.CustomerId);
            Assert.Equal(OrderStatus.Draft, order.Status);
            Assert.Empty(order.Lines);
            Assert.Equal(Money.Zero("USD"), order.Total);
        }

        [Fact]
        public void Create_Should_Throw_If_Customer_Id_Empty()
        {
            // Act & Assert
            var ex = Assert.Throws<DomainException>(() => Order.Create(Guid.Empty));
            Assert.Contains("Customer ID", ex.Message);
        }

        // ✅ Test behavior
        [Fact]
        public void AddLine_Should_Add_To_Lines_Collection()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());
            var productId = Guid.NewGuid();

            // Act
            order.AddLine(productId, 5, Money.Dollars(100));

            // Assert
            Assert.Single(order.Lines);
            var line = order.Lines.First();
            Assert.Equal(productId, line.ProductId);
            Assert.Equal(5, line.Quantity);
            Assert.Equal(Money.Dollars(100), line.UnitPrice);
        }

        [Fact]
        public void AddLine_Should_Update_Total()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());

            // Act
            order.AddLine(Guid.NewGuid(), 5, Money.Dollars(100));
            order.AddLine(Guid.NewGuid(), 2, Money.Dollars(250));

            // Assert
            Assert.Equal(Money.Dollars(1000), order.Total); // 5*100 + 2*250
        }

        // ✅ Test invariants (business rules)
        [Fact]
        public void AddLine_Should_Throw_If_Order_Not_Draft()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());
            order.AddLine(Guid.NewGuid(), 5, Money.Dollars(100));
            order.Submit(); // Status = Pending

            // Act & Assert
            var ex = Assert.Throws<InvalidOperationException>(() =>
                order.AddLine(Guid.NewGuid(), 1, Money.Dollars(50)));
            Assert.Contains("non-draft", ex.Message);
        }

        [Theory]
        [InlineData(0)]
        [InlineData(-5)]
        public void AddLine_Should_Throw_If_Quantity_Invalid(int invalidQuantity)
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());

            // Act & Assert
            var ex = Assert.Throws<DomainException>(() =>
                order.AddLine(Guid.NewGuid(), invalidQuantity, Money.Dollars(100)));
            Assert.Contains("positive", ex.Message);
        }

        // ✅ Test state transitions
        [Fact]
        public void Submit_Should_Transition_From_Draft_To_Pending()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());
            order.AddLine(Guid.NewGuid(), 5, Money.Dollars(100));

            // Act
            order.Submit();

            // Assert
            Assert.Equal(OrderStatus.Pending, order.Status);
        }

        [Fact]
        public void Submit_Should_Raise_OrderSubmitted_Event()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());
            order.AddLine(Guid.NewGuid(), 5, Money.Dollars(100));

            // Act
            order.Submit();

            // Assert
            var events = order.GetDomainEvents();
            Assert.Contains(events, e => e is OrderSubmitted);
            var submittedEvent = events.OfType<OrderSubmitted>().First();
            Assert.Equal(order.OrderId, submittedEvent.OrderId);
            Assert.Equal(Money.Dollars(500), submittedEvent.Total);
        }

        [Theory]
        [InlineData(OrderStatus.Pending)]
        [InlineData(OrderStatus.Approved)]
        [InlineData(OrderStatus.Shipped)]
        public void Submit_Should_Throw_If_Not_Draft(OrderStatus invalidStatus)
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());
            order.AddLine(Guid.NewGuid(), 1, Money.Dollars(100));

            // Force state (via reflection for test)
            var statusProperty = typeof(Order).GetProperty("Status");
            statusProperty.SetValue(order, invalidStatus);

            // Act & Assert
            var ex = Assert.Throws<InvalidOperationException>(() => order.Submit());
            Assert.Contains("draft", ex.Message.ToLower());
        }
    }
}
```

## Testing Value Objects

```csharp
// ✅ Unit tests para Money value object

namespace Talma.Sales.Domain.Tests.Model
{
    public class MoneyTests
    {
        [Fact]
        public void Constructor_Should_Create_Valid_Money()
        {
            // Act
            var money = new Money(100.50m, "USD");

            // Assert
            Assert.Equal(100.50m, money.Amount);
            Assert.Equal("USD", money.Currency);
        }

        // ✅ Test value equality
        [Fact]
        public void Two_Money_With_Same_Values_Should_Be_Equal()
        {
            // Arrange
            var money1 = Money.Dollars(100);
            var money2 = Money.Dollars(100);

            // Assert
            Assert.Equal(money1, money2);
            Assert.True(money1 == money2);
        }

        [Fact]
        public void Two_Money_With_Different_Amounts_Should_Not_Be_Equal()
        {
            // Arrange
            var money1 = Money.Dollars(100);
            var money2 = Money.Dollars(200);

            // Assert
            Assert.NotEqual(money1, money2);
            Assert.True(money1 != money2);
        }

        [Fact]
        public void Two_Money_With_Different_Currencies_Should_Not_Be_Equal()
        {
            // Arrange
            var money1 = new Money(100, "USD");
            var money2 = new Money(100, "EUR");

            // Assert
            Assert.NotEqual(money1, money2);
        }

        // ✅ Test operators
        [Fact]
        public void Addition_Should_Sum_Amounts_With_Same_Currency()
        {
            // Arrange
            var money1 = Money.Dollars(100);
            var money2 = Money.Dollars(50);

            // Act
            var result = money1 + money2;

            // Assert
            Assert.Equal(Money.Dollars(150), result);
        }

        [Fact]
        public void Addition_Should_Throw_If_Different_Currencies()
        {
            // Arrange
            var usd = Money.Dollars(100);
            var eur = new Money(100, "EUR");

            // Act & Assert
            var ex = Assert.Throws<InvalidOperationException>(() => usd + eur);
            Assert.Contains("currency", ex.Message.ToLower());
        }

        [Fact]
        public void Multiplication_Should_Scale_Amount()
        {
            // Arrange
            var money = Money.Dollars(100);

            // Act
            var result = money * 2.5m;

            // Assert
            Assert.Equal(Money.Dollars(250), result);
        }

        [Theory]
        [InlineData(100, 2, 200)]
        [InlineData(50, 0.5, 25)]
        [InlineData(100, 0, 0)]
        public void Multiplication_Should_Calculate_Correctly(decimal amount, decimal multiplier, decimal expected)
        {
            // Arrange
            var money = Money.Dollars(amount);

            // Act
            var result = money * multiplier;

            // Assert
            Assert.Equal(Money.Dollars(expected), result);
        }
    }
}
```

## Testing Application Use Cases (con Mocks)

```csharp
// ✅ Unit tests para Application layer (mocking dependencies)

using Moq;

namespace Talma.Sales.Application.Tests.UseCases
{
    public class CreateOrderHandlerTests
    {
        private readonly Mock<IOrderRepository> _orderRepoMock;
        private readonly Mock<IProductServiceClient> _productClientMock;
        private readonly Mock<IEventPublisher> _eventPublisherMock;
        private readonly CreateOrderHandler _handler;

        public CreateOrderHandlerTests()
        {
            // ✅ Arrange: Setup mocks
            _orderRepoMock = new Mock<IOrderRepository>();
            _productClientMock = new Mock<IProductServiceClient>();
            _eventPublisherMock = new Mock<IEventPublisher>();

            _handler = new CreateOrderHandler(
                _orderRepoMock.Object,
                _productClientMock.Object,
                _eventPublisherMock.Object
            );
        }

        [Fact]
        public async Task Should_Create_Order_And_Save()
        {
            // Arrange
            var customerId = Guid.NewGuid();
            var productId = Guid.NewGuid();

            _productClientMock
                .Setup(x => x.GetProductAsync(productId))
                .ReturnsAsync(new ProductDto { ProductId = productId, Name = "Product A", Price = 100 });

            _productClientMock
                .Setup(x => x.IsAvailableAsync(productId, 5))
                .ReturnsAsync(true);

            var command = new CreateOrderCommand(
                customerId,
                new List<OrderItemDto> { new(productId, 5) }
            );

            // Act
            var orderId = await _handler.ExecuteAsync(command);

            // Assert
            Assert.NotEqual(Guid.Empty, orderId);

            // ✅ Verify repository was called
            _orderRepoMock.Verify(
                x => x.SaveAsync(It.Is<Order>(o => o.CustomerId == customerId)),
                Times.Once
            );
        }

        [Fact]
        public async Task Should_Publish_Domain_Events()
        {
            // Arrange
            var productId = Guid.NewGuid();

            _productClientMock
                .Setup(x => x.GetProductAsync(It.IsAny<Guid>()))
                .ReturnsAsync(new ProductDto { ProductId = productId, Price = 100 });

            _productClientMock
                .Setup(x => x.IsAvailableAsync(It.IsAny<Guid>(), It.IsAny<int>()))
                .ReturnsAsync(true);

            var command = new CreateOrderCommand(
                Guid.NewGuid(),
                new List<OrderItemDto> { new(productId, 5) }
            );

            // Act
            await _handler.ExecuteAsync(command);

            // Assert
            _eventPublisherMock.Verify(
                x => x.PublishAsync(It.IsAny<OrderCreated>()),
                Times.Once
            );
        }

        [Fact]
        public async Task Should_Throw_If_Product_Not_Found()
        {
            // Arrange
            var productId = Guid.NewGuid();

            _productClientMock
                .Setup(x => x.GetProductAsync(productId))
                .ReturnsAsync((ProductDto)null);  // ✅ Simular producto no encontrado

            var command = new CreateOrderCommand(
                Guid.NewGuid(),
                new List<OrderItemDto> { new(productId, 5) }
            );

            // Act & Assert
            var ex = await Assert.ThrowsAsync<DomainException>(() => _handler.ExecuteAsync(command));
            Assert.Contains("not found", ex.Message);

            // ✅ Verify repository was NOT called
            _orderRepoMock.Verify(x => x.SaveAsync(It.IsAny<Order>()), Times.Never);
        }

        [Fact]
        public async Task Should_Throw_If_Product_Not_Available()
        {
            // Arrange
            var productId = Guid.NewGuid();

            _productClientMock
                .Setup(x => x.GetProductAsync(productId))
                .ReturnsAsync(new ProductDto { ProductId = productId, Name = "Product A", Price = 100 });

            _productClientMock
                .Setup(x => x.IsAvailableAsync(productId, 100))
                .ReturnsAsync(false);  // ✅ Simular sin stock

            var command = new CreateOrderCommand(
                Guid.NewGuid(),
                new List<OrderItemDto> { new(productId, 100) }
            );

            // Act & Assert
            var ex = await Assert.ThrowsAsync<DomainException>(() => _handler.ExecuteAsync(command));
            Assert.Contains("not available", ex.Message);
        }
    }
}
```

## Testing con FluentAssertions (Opcional)

```csharp
// ✅ Alternative: FluentAssertions (más legible)

using FluentAssertions;

namespace Talma.Sales.Domain.Tests.Model
{
    public class OrderFluentTests
    {
        [Fact]
        public void Order_Should_Have_Valid_Initial_State()
        {
            // Arrange
            var customerId = Guid.NewGuid();

            // Act
            var order = Order.Create(customerId);

            // Assert (FluentAssertions)
            order.OrderId.Should().NotBeEmpty();
            order.CustomerId.Should().Be(customerId);
            order.Status.Should().Be(OrderStatus.Draft);
            order.Lines.Should().BeEmpty();
            order.Total.Should().Be(Money.Zero("USD"));
        }

        [Fact]
        public void Adding_Lines_Should_Update_Total()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());

            // Act
            order.AddLine(Guid.NewGuid(), 5, Money.Dollars(100));
            order.AddLine(Guid.NewGuid(), 2, Money.Dollars(250));

            // Assert
            order.Lines.Should().HaveCount(2);
            order.Total.Should().Be(Money.Dollars(1000));
        }

        [Fact]
        public void Submit_Should_Raise_Domain_Event()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());
            order.AddLine(Guid.NewGuid(), 5, Money.Dollars(100));

            // Act
            order.Submit();

            // Assert
            order.GetDomainEvents()
                .Should().ContainSingle(e => e is OrderSubmitted)
                .Which.Should().BeOfType<OrderSubmitted>()
                .Which.Total.Should().Be(Money.Dollars(500));
        }

        [Fact]
        public void Submit_Empty_Order_Should_Throw_DomainException()
        {
            // Arrange
            var order = Order.Create(Guid.NewGuid());

            // Act
            Action act = () => order.Submit();

            // Assert
            act.Should().Throw<DomainException>()
                .WithMessage("*without lines*");
        }
    }
}
```

## Convenciones y Best Practices

```csharp
// ✅ Naming conventions

// ✅ Test class: {ClassUnderTest}Tests
public class OrderTests { }
public class MoneyTests { }
public class CreateOrderHandlerTests { }

// ✅ Test method: {Method}_{Scenario}_{ExpectedBehavior}
[Fact]
public void Submit_Should_Change_Status_To_Pending() { }

[Fact]
public void AddLine_Should_Throw_If_Quantity_Negative() { }

[Fact]
public void Create_WithEmptyCustomerId_Should_Throw_DomainException() { }

// ✅ Alternative: {Method}_Should_{ExpectedBehavior}_When_{Scenario}
[Fact]
public void Submit_Should_Throw_When_Order_Is_Empty() { }

// ✅ Organize tests by category
public class OrderTests
{
    public class CreateTests
    {
        [Fact]
        public void Should_Generate_Valid_OrderId() { }

        [Fact]
        public void Should_Throw_If_CustomerId_Empty() { }
    }

    public class SubmitTests
    {
        [Fact]
        public void Should_Change_Status_To_Pending() { }

        [Fact]
        public void Should_Throw_If_No_Lines() { }
    }

    public class AddLineTests
    {
        [Fact]
        public void Should_Add_To_Lines_Collection() { }

        [Fact]
        public void Should_Update_Total() { }
    }
}

// ✅ One assertion per test (ideal, not strict)
[Fact]
public void Create_Should_Set_Correct_Status()
{
    var order = Order.Create(Guid.NewGuid());
    Assert.Equal(OrderStatus.Draft, order.Status);  // ✅ Focus on one thing
}

// ❌ Avoid multiple unrelated assertions
[Fact]
public void Create_Should_Set_Everything_Correctly()  // ❌ Too broad
{
    var order = Order.Create(Guid.NewGuid());
    Assert.NotEmpty(order.OrderId);
    Assert.Equal(OrderStatus.Draft, order.Status);
    Assert.Empty(order.Lines);
    Assert.Equal(Money.Zero("USD"), order.Total);
    // Hard to diagnose which part failed
}
```

## Coverage y Métricas

```yaml
# ✅ Coverage targets en Talma

Domain Layer:
  Target: 90%+ code coverage
  Crítico: 100% en invariantes y reglas de negocio
  Tools: dotnet-coverage, Coverlet

Application Layer:
  Target: 80%+ code coverage
  Crítico: 100% en happy paths de use cases
  Mock: Todas las dependencies (repos, clients, publishers)

Infrastructure Layer:
  Target: <30% en unit tests (usar integration tests)
  Razón: Infrastructure es sobre integración, no lógica

# Ejecución en CI/CD

GitHub Actions:
  - Run tests: dotnet test --collect:"XPlat Code Coverage"
  - Generate report: reportgenerator -reports:**/coverage.cobertura.xml
  - Enforce minimum: 80% global, fail build si <80%
  - Upload to: Codecov, SonarCloud

# Métricas

Sales Service (ejemplo real):
  Total tests: 847 unit tests
  Execution time: 1.2 seconds (1.4ms avg per test)
  Coverage: 87% overall
    - Domain: 94%
    - Application: 82%
    - Infrastructure: 23% (esperado, usa integration tests)
  Failures: 0 (100% pass rate)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** escribir unit tests para toda lógica de negocio en Domain
- **MUST** ejecutar tests en <10ms por test (sin DB, sin network)
- **MUST** usar mocks para dependencies en Application tests
- **MUST** mantener tests independientes (no shared state)
- **MUST** usar patrón AAA (Arrange-Act-Assert)
- **MUST** ejecutar unit tests en cada commit (CI/CD)
- **MUST** alcanzar mínimo 80% coverage en Domain y Application

### SHOULD (Fuertemente recomendado)

- **SHOULD** nombrar tests descriptivamente ({Method}_{Scenario}_{Expected})
- **SHOULD** usar xUnit como framework de testing
- **SHOULD** usar Moq para mocking
- **SHOULD** organizar tests en proyecto separado ({Service}.Tests)
- **SHOULD** usar Theory para data-driven tests
- **SHOULD** validar excepciones esperadas con Assert.Throws
- **SHOULD** generar coverage reports en CI/CD

### MAY (Opcional)

- **MAY** usar FluentAssertions para assertions más legibles
- **MAY** usar TDD (Test-Driven Development)
- **MAY** organizar tests en nested classes por feature
- **MAY** usar AutoFixture para generar test data

### MUST NOT (Prohibido)

- **MUST NOT** acceder a base de datos real en unit tests
- **MUST NOT** hacer HTTP calls en unit tests
- **MUST NOT** usar filesystem en unit tests
- **MUST NOT** compartir estado entre tests (static variables)
- **MUST NOT** usar Thread.Sleep o delays en tests
- **MUST NOT** ignorar tests fallidos (fix or delete)

---

## Referencias

- [Lineamiento: Arquitectura Limpia](../../lineamientos/arquitectura/11-arquitectura-limpia.md)
- Estándares relacionados:
  - [Hexagonal Architecture](../arquitectura/hexagonal-architecture.md)
  - [Domain Model](../arquitectura/domain-model.md)
  - [Framework Independence](../arquitectura/framework-independence.md)
- Especificaciones:
  - [xUnit Documentation](https://xunit.net/)
  - [Moq Quickstart](https://github.com/moq/moq4/wiki/Quickstart)
  - [FluentAssertions](https://fluentassertions.com/)
  - [.NET Testing Best Practices](https://docs.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)
