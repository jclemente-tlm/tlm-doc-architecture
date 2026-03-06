---
id: unit-testing
sidebar_position: 4
title: Pruebas Unitarias
description: Estándares para unit tests con xUnit, Moq y FluentAssertions siguiendo el patrón AAA
tags: [testing, pruebas-unitarias, xunit, moq, fluentassertions]
---

# Pruebas Unitarias

## Contexto

Este estándar define los **patrones y herramientas para pruebas unitarias**: tests que verifican el comportamiento de una unidad de código de forma aislada, mockeando todas las dependencias externas.

---

## Stack Tecnológico

| Componente         | Tecnología       | Versión | Uso                           |
| ------------------ | ---------------- | ------- | ----------------------------- |
| **Test Framework** | xUnit            | 2.6+    | Framework principal           |
| **Assertions**     | FluentAssertions | 6.12+   | Assertions legibles           |
| **Mocking**        | Moq              | 4.20+   | Mocking de dependencias       |
| **Fake Data**      | Bogus            | 35.0+   | Generación de datos de prueba |

---

## Pruebas Unitarias

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

        _repositoryMock
            .Setup(r => r.GetCustomerAsync(request.CustomerId))
            .ReturnsAsync(new Customer { Id = "CUST-123", Name = "John Doe" });

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
        result.TotalAmount.Should().Be(236m); // 200 subtotal + 36 tax (18%)

        _repositoryMock.Verify(r => r.GetCustomerAsync(request.CustomerId), Times.Once);
        _paymentServiceMock.Verify(
            p => p.ProcessPaymentAsync(It.Is<PaymentRequest>(pr =>
                pr.Amount == 236m && pr.CustomerId == "CUST-123")),
            Times.Once);
        _repositoryMock.Verify(r => r.SaveAsync(It.IsAny<Order>()), Times.Once);
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

        _paymentServiceMock.Verify(
            p => p.ProcessPaymentAsync(It.IsAny<PaymentRequest>()), Times.Never);
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

    public OrderBuilder WithId(int id) { _id = id; return this; }
    public OrderBuilder WithCustomerId(string customerId) { _customerId = customerId; return this; }
    public OrderBuilder WithStatus(OrderStatus status) { _status = status; return this; }

    public OrderBuilder WithItem(string sku, int quantity, decimal unitPrice)
    {
        _items.Add(new OrderItem { Sku = sku, Quantity = quantity, UnitPrice = unitPrice });
        return this;
    }

    public Order Build() => new Order
    {
        Id = _id,
        CustomerId = _customerId,
        Status = _status,
        Items = _items
    };
}

// Uso en tests
[Fact]
public void Example_UsingBuilder()
{
    var order = new OrderBuilder()
        .WithId(123)
        .WithCustomerId("CUST-456")
        .WithItem("SKU-001", 2, 100m)
        .WithItem("SKU-002", 1, 50m)
        .Build();

    order.Subtotal.Should().Be(250m);
}
```

---

## Monitoreo y Observabilidad

Los resultados de unit tests se reportan automáticamente a SonarQube vía pipeline CI/CD. Ver [Automatización de Tests](./test-automation.md) para la configuración del pipeline.

Métricas clave a monitorear:

- Número de unit tests por componente
- Tiempo de ejecución total del suite
- Tests fallidos o flaky detectados

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** seguir patrón AAA (Arrange-Act-Assert)
- **MUST** mockear todas las dependencias externas con Moq
- **MUST** tests aislados (sin estado compartido entre tests)
- **MUST** nombres descriptivos (Given_When_Then o Should pattern)
- **MUST** FluentAssertions para assertions legibles
- **MUST** toda la suite de unit tests ejecutarse en < 5 minutos

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar test data builders para objetos complejos
- **SHOULD** parametrizar tests con `[Theory]` cuando aplique
- **SHOULD** Bogus para generar fake data realista

### MUST NOT (Prohibido)

- **MUST NOT** unit tests tocando DB, filesystem o network
- **MUST NOT** tests con `sleep`/delays fijos
- **MUST NOT** assertions en múltiples conceptos (1 test = 1 concepto)
- **MUST NOT** dependencias entre tests (orden de ejecución)

---

## Referencias

- [xUnit Documentation](https://xunit.net/)
- [Moq Quick Start](https://github.com/moq/moq4)
- [FluentAssertions](https://fluentassertions.com/)
- [Bogus Fake Data](https://github.com/bchavez/Bogus)
- [Pirámide de Testing](./testing-pyramid.md)
- [Pruebas de Integración](./integration-testing.md)
