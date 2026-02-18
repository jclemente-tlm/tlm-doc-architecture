---
id: domain-model
sidebar_position: 6
title: Rich Domain Model
description: Diseñar modelo de dominio rico con comportamiento y reglas de negocio encapsuladas
---

# Rich Domain Model

## Contexto

Este estándar define cómo diseñar un **modelo de dominio rico** que encapsula comportamiento y reglas de negocio, en contraste con modelos anémicos que solo contienen datos. Complementa el [lineamiento de Modelado de Dominio](../../lineamientos/arquitectura/09-modelado-de-dominio.md) asegurando que **el modelo refleja y protege las reglas del negocio**.

---

## Conceptos Fundamentales

### Rich Domain Model vs Anemic Domain Model

```yaml
# ✅ Rich Domain Model = Comportamiento + Datos

Modelo Anémico (Anti-pattern):
  Características:
    - Entidades solo con getters/setters públicos
    - Sin validaciones en el modelo
    - Lógica de negocio en servicios externos
    - Cualquiera puede modificar estado sin restricciones

  Problemas: ❌ Invariantes no protegidas
    ❌ Reglas duplicadas en múltiples servicios
    ❌ Fácil introducir estado inválido
    ❌ Difícil entender reglas de negocio
    ❌ Alta acoplamiento entre servicios

Modelo Rico (Pattern correcto):
  Características:
    - Entidades con comportamiento explícito
    - Validaciones y reglas en el modelo
    - Estado privado, métodos públicos
    - Invariantes protegidas en constructor y métodos
    - Lógica de negocio encapsulada

  Beneficios: ✅ Imposible crear estado inválido
    ✅ Reglas centralizadas en un lugar
    ✅ Código autodocumentado
    ✅ Fácil de testear
    ✅ Bajo acoplamiento
```

### Ejemplo Comparativo

```csharp
// ❌ MALO: Modelo Anémico

public class Order
{
    // ❌ Todo público, sin protección
    public Guid Id { get; set; }
    public Guid CustomerId { get; set; }
    public string Status { get; set; }  // ❌ String, cualquier valor
    public List<OrderLine> Lines { get; set; }  // ❌ Lista mutable
    public decimal Total { get; set; }
}

// ❌ Lógica de negocio en servicio externo
public class OrderService
{
    public void SubmitOrder(Order order)
    {
        // ❌ Validaciones fuera del modelo
        if (order.Lines.Count == 0)
            throw new Exception("Order must have lines");

        if (order.Total <= 0)
            throw new Exception("Total must be positive");

        // ❌ Transición de estado sin validar
        order.Status = "Pending";

        // ❌ Recalcular total (debería ser responsabilidad del Order)
        order.Total = order.Lines.Sum(l => l.Quantity * l.UnitPrice);

        _repository.Save(order);
    }
}

// Problema: Nada impide hacer esto
var order = new Order
{
    Status = "InvalidStatus",  // ❌ Estado inválido
    Lines = new List<OrderLine>(),  // ❌ Sin líneas
    Total = -100  // ❌ Total negativo
};
```

```csharp
// ✅ BUENO: Modelo Rico

public class Order : AggregateRoot
{
    // ✅ Estado privado, inmutable desde afuera
    public Guid OrderId { get; private set; }
    public Guid CustomerId { get; private set; }
    public OrderStatus Status { get; private set; }  // ✅ Enum, valores controlados
    public DateTime OrderDate { get; private set; }

    private readonly List<OrderLine> _lines = new();
    public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();  // ✅ Solo lectura

    // ✅ Total calculado, no almacenado (elimina inconsistencias)
    public Money Total => _lines.Aggregate(Money.Zero("USD"),
        (sum, line) => sum + line.Subtotal);

    // ✅ Constructor privado previene creación directa
    private Order() { }

    // ✅ Factory method con validaciones
    public static Order Create(Guid customerId)
    {
        if (customerId == Guid.Empty)
            throw new ArgumentException("Customer ID is required", nameof(customerId));

        var order = new Order
        {
            OrderId = Guid.NewGuid(),
            CustomerId = customerId,
            Status = OrderStatus.Draft,  // ✅ Estado inicial definido
            OrderDate = DateTime.UtcNow
        };

        order.AddDomainEvent(new OrderCreated(order.OrderId, customerId));
        return order;
    }

    // ✅ Comportamiento encapsulado con nombre del dominio
    public void Submit()
    {
        // ✅ Validar transición permitida
        if (Status != OrderStatus.Draft)
            throw new InvalidOperationException(
                $"Cannot submit order in {Status} status. Only Draft orders can be submitted.");

        // ✅ Validar invariantes
        if (!_lines.Any())
            throw new DomainException("Cannot submit order without lines");

        if (Total.Amount <= 0)
            throw new DomainException("Cannot submit order with zero or negative total");

        // ✅ Cambio de estado controlado
        Status = OrderStatus.Pending;

        // ✅ Domain event con datos del evento
        AddDomainEvent(new OrderSubmitted(OrderId, CustomerId, Total));
    }

    public void Approve(Guid approvedBy, string? reason = null)
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException(
                $"Cannot approve order in {Status} status. Only Pending orders can be approved.");

        Status = OrderStatus.Approved;
        AddDomainEvent(new OrderApproved(OrderId, CustomerId, approvedBy, reason));
    }

    public void Reject(Guid rejectedBy, string reason)
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException(
                $"Cannot reject order in {Status} status. Only Pending orders can be rejected.");

        if (string.IsNullOrWhiteSpace(reason))
            throw new ArgumentException("Rejection reason is required", nameof(reason));

        Status = OrderStatus.Rejected;
        AddDomainEvent(new OrderRejected(OrderId, rejectedBy, reason));
    }

    // ✅ Agregar línea con validaciones
    public void AddLine(Guid productId, int quantity, Money unitPrice)
    {
        // ✅ Solo en Draft se pueden agregar líneas
        if (Status != OrderStatus.Draft)
            throw new InvalidOperationException(
                "Cannot modify submitted order. Only Draft orders can be modified.");

        if (productId == Guid.Empty)
            throw new ArgumentException("Product ID is required", nameof(productId));

        if (quantity <= 0)
            throw new ArgumentException("Quantity must be positive", nameof(quantity));

        if (unitPrice.Amount < 0)
            throw new ArgumentException("Unit price cannot be negative", nameof(unitPrice));

        // ✅ Validar duplicados (regla de negocio)
        if (_lines.Any(l => l.ProductId == productId))
            throw new DomainException($"Product {productId} already exists in order. Use UpdateLine instead.");

        var line = OrderLine.Create(Guid.NewGuid(), OrderId, productId, quantity, unitPrice);
        _lines.Add(line);

        AddDomainEvent(new OrderLineAdded(OrderId, line.LineId, productId, quantity, unitPrice));
    }

    public void RemoveLine(Guid lineId)
    {
        if (Status != OrderStatus.Draft)
            throw new InvalidOperationException("Cannot modify submitted order");

        var line = _lines.FirstOrDefault(l => l.LineId == lineId);
        if (line == null)
            throw new DomainException($"Line {lineId} not found in order");

        _lines.Remove(line);
        AddDomainEvent(new OrderLineRemoved(OrderId, lineId));
    }

    public void UpdateLineQuantity(Guid lineId, int newQuantity)
    {
        if (Status != OrderStatus.Draft)
            throw new InvalidOperationException("Cannot modify submitted order");

        if (newQuantity <= 0)
            throw new ArgumentException("Quantity must be positive", nameof(newQuantity));

        var line = _lines.FirstOrDefault(l => l.LineId == lineId);
        if (line == null)
            throw new DomainException($"Line {lineId} not found in order");

        line.UpdateQuantity(newQuantity);
        AddDomainEvent(new OrderLineQuantityUpdated(OrderId, lineId, newQuantity));
    }

    // ✅ Reconstitute para Entity Framework (hidrata desde DB)
    public static Order Reconstitute(
        Guid orderId,
        Guid customerId,
        OrderStatus status,
        DateTime orderDate,
        List<OrderLine> lines)
    {
        return new Order
        {
            OrderId = orderId,
            CustomerId = customerId,
            Status = status,
            OrderDate = orderDate,
            _lines = lines
        };
    }
}

public enum OrderStatus
{
    Draft,
    Pending,
    Approved,
    Rejected,
    Shipped,
    Delivered
}
```

**Resultado:**

```csharp
// ✅ Imposible crear estado inválido
var order = Order.Create(customerId);  // Estado inicial Draft
order.AddLine(productId, 5, Money.Dollars(100));  // Validado
order.Submit();  // Transición validada, evento publicado

// ❌ Esto falla (como debe ser)
order.AddLine(...);  // Exception: "Cannot modify submitted order"
order.Approve(managerId);  // Exception: "Only Pending orders can be approved"
```

## Principios del Modelo Rico

### 1. Encapsulación de Estado

```csharp
// ✅ BUENO: Estado privado, acceso controlado

public class Customer : AggregateRoot
{
    public Guid CustomerId { get; private set; }
    public string Name { get; private set; }
    public Email Email { get; private set; }  // ✅ Value object, no string
    public CustomerStatus Status { get; private set; }

    private readonly List<Address> _shippingAddresses = new();
    public IReadOnlyCollection<Address> ShippingAddresses => _shippingAddresses.AsReadOnly();

    // ✅ Método con regla de negocio
    public void Activate()
    {
        if (Status == CustomerStatus.Active)
            throw new InvalidOperationException("Customer is already active");

        if (Status == CustomerStatus.Blocked)
            throw new DomainException("Cannot activate blocked customer. Contact support.");

        Status = CustomerStatus.Active;
        AddDomainEvent(new CustomerActivated(CustomerId));
    }

    public void Block(string reason)
    {
        if (string.IsNullOrWhiteSpace(reason))
            throw new ArgumentException("Block reason is required", nameof(reason));

        Status = CustomerStatus.Blocked;
        AddDomainEvent(new CustomerBlocked(CustomerId, reason));
    }

    public void AddShippingAddress(Address address)
    {
        if (_shippingAddresses.Count >= 5)
            throw new DomainException("Customer cannot have more than 5 shipping addresses");

        if (_shippingAddresses.Any(a => a.Equals(address)))
            throw new DomainException("Address already exists");

        _shippingAddresses.Add(address);
    }
}

// ❌ MALO: Estado público sin validación

public class Customer
{
    public Guid Id { get; set; }
    public string Status { get; set; }  // Cualquier string
    public List<Address> Addresses { get; set; }  // List mutable, sin límite
}
```

### 2. Invariantes Protegidas

```csharp
// ✅ BUENO: Invariantes validadas siempre

public record OrderLine
{
    public Guid LineId { get; private init; }
    public Guid OrderId { get; private init; }
    public Guid ProductId { get; private init; }
    public int Quantity { get; private set; }  // Mutable via método
    public Money UnitPrice { get; private init; }

    // ✅ Invariante: Subtotal siempre consistente
    public Money Subtotal => UnitPrice * Quantity;

    private OrderLine() { }  // EF constructor

    public static OrderLine Create(
        Guid lineId,
        Guid orderId,
        Guid productId,
        int quantity,
        Money unitPrice)
    {
        // ✅ Validar invariantes en creación
        if (lineId == Guid.Empty)
            throw new ArgumentException("Line ID is required");
        if (orderId == Guid.Empty)
            throw new ArgumentException("Order ID is required");
        if (productId == Guid.Empty)
            throw new ArgumentException("Product ID is required");
        if (quantity <= 0)
            throw new ArgumentException("Quantity must be positive", nameof(quantity));
        if (unitPrice.Amount < 0)
            throw new ArgumentException("Unit price cannot be negative", nameof(unitPrice));

        return new OrderLine
        {
            LineId = lineId,
            OrderId = orderId,
            ProductId = productId,
            Quantity = quantity,
            UnitPrice = unitPrice
        };
    }

    // ✅ Validar invariantes en mutación
    public void UpdateQuantity(int newQuantity)
    {
        if (newQuantity <= 0)
            throw new ArgumentException("Quantity must be positive", nameof(newQuantity));

        Quantity = newQuantity;
    }
}

// ❌ MALO: Subtotal almacenado (puede desincronizarse)

public class OrderLine
{
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
    public decimal Subtotal { get; set; }  // ❌ Puede estar desincronizado
}

// Problema:
line.Quantity = 10;
line.UnitPrice = 100;
// Subtotal sigue siendo el valor viejo!
```

### 3. Métodos con Significado del Dominio

```csharp
// ✅ BUENO: Métodos expresan intención del negocio

public class Invoice : AggregateRoot
{
    public InvoiceStatus Status { get; private set; }
    public DateTime? PaidDate { get; private set; }
    public Money TotalAmount { get; private set; }

    // ✅ Métodos con nombres del dominio
    public void MarkAsPaid(DateTime paidDate, string paymentReference)
    {
        if (Status == InvoiceStatus.Paid)
            throw new InvalidOperationException("Invoice is already paid");

        if (Status == InvoiceStatus.Cancelled)
            throw new DomainException("Cannot pay cancelled invoice");

        if (paidDate > DateTime.UtcNow)
            throw new ArgumentException("Payment date cannot be in the future");

        Status = InvoiceStatus.Paid;
        PaidDate = paidDate;

        AddDomainEvent(new InvoicePaid(InvoiceId, TotalAmount, paymentReference));
    }

    public void Cancel(string reason)
    {
        if (Status == InvoiceStatus.Paid)
            throw new DomainException("Cannot cancel paid invoice");

        Status = InvoiceStatus.Cancelled;
        AddDomainEvent(new InvoiceCancelled(InvoiceId, reason));
    }

    public bool IsOverdue()
    {
        return Status == InvoiceStatus.Pending &&
               DateTime.UtcNow > DueDate;
    }
}

// ❌ MALO: Métodos genéricos CRUD

public class Invoice
{
    public void Update(string status, DateTime? paidDate)  // ❌ Muy genérico
    {
        Status = status;
        PaidDate = paidDate;
    }

    public void SetStatus(string status) { ... }  // ❌ Sin validación de transiciones
}
```

### 4. Factory Methods

```csharp
// ✅ BUENO: Factory methods con validaciones

public class Product : AggregateRoot
{
    public Guid ProductId { get; private set; }
    public string Name { get; private set; }
    public string Sku { get; private set; }
    public Money Price { get; private set; }
    public int StockQuantity { get; private set; }
    public ProductStatus Status { get; private set; }

    private Product() { }

    // ✅ Factory method con estado inicial consistente
    public static Product Create(
        string name,
        string sku,
        Money price,
        int initialStock)
    {
        // ✅ Validaciones centralizadas
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Product name is required", nameof(name));

        if (name.Length > 200)
            throw new ArgumentException("Product name cannot exceed 200 characters", nameof(name));

        if (string.IsNullOrWhiteSpace(sku))
            throw new ArgumentException("SKU is required", nameof(sku));

        if (!IsValidSku(sku))
            throw new ArgumentException("SKU format is invalid", nameof(sku));

        if (price.Amount <= 0)
            throw new ArgumentException("Price must be positive", nameof(price));

        if (initialStock < 0)
            throw new ArgumentException("Initial stock cannot be negative", nameof(initialStock));

        var product = new Product
        {
            ProductId = Guid.NewGuid(),
            Name = name.Trim(),
            Sku = sku.ToUpperInvariant(),
            Price = price,
            StockQuantity = initialStock,
            Status = initialStock > 0 ? ProductStatus.Available : ProductStatus.OutOfStock
        };

        product.AddDomainEvent(new ProductCreated(product.ProductId, name, sku));
        return product;
    }

    private static bool IsValidSku(string sku)
    {
        // Regla de negocio: SKU = 3 letras + 5 dígitos (ej: PRD12345)
        return Regex.IsMatch(sku, @"^[A-Z]{3}\d{5}$");
    }
}

// ❌ MALO: Constructor público sin validación

public class Product
{
    public Product(string name, string sku, decimal price)
    {
        Name = name;  // ❌ Sin validación
        Sku = sku;
        Price = price;
    }
}
```

## Domain Services

```csharp
// ✅ Domain Service cuando comportamiento involucra múltiples agregados

namespace Talma.Sales.Domain.Services
{
    // ✅ Interface en dominio
    public interface IOrderPricingService
    {
        Money CalculateTotalWithDiscounts(Order order, Customer customer);
        Money ApplyVolumeDiscount(Money subtotal, int totalQuantity);
    }

    // ✅ Implementación con reglas de negocio
    public class OrderPricingService : IOrderPricingService
    {
        public Money CalculateTotalWithDiscounts(Order order, Customer customer)
        {
            var subtotal = order.Total;

            // Regla: Clientes VIP tienen 10% descuento
            if (customer.Status == CustomerStatus.Vip)
            {
                var discount = subtotal * 0.10m;
                subtotal = subtotal - discount;
            }

            // Regla: Descuento por volumen
            var totalQuantity = order.Lines.Sum(l => l.Quantity);
            subtotal = ApplyVolumeDiscount(subtotal, totalQuantity);

            return subtotal;
        }

        public Money ApplyVolumeDiscount(Money subtotal, int totalQuantity)
        {
            // Regla: 100+ items = 5% descuento, 500+ = 10%
            var discountPercentage = totalQuantity switch
            {
                >= 500 => 0.10m,
                >= 100 => 0.05m,
                _ => 0m
            };

            var discount = subtotal * discountPercentage;
            return subtotal - discount;
        }
    }
}

// Uso en Application Service:

public class PlaceOrderCommandHandler
{
    private readonly IOrderRepository _orderRepo;
    private readonly ICustomerRepository _customerRepo;
    private readonly IOrderPricingService _pricingService;  // ✅ Domain service

    public async Task<Guid> HandleAsync(PlaceOrderCommand cmd)
    {
        var customer = await _customerRepo.GetByIdAsync(cmd.CustomerId);
        var order = Order.Create(cmd.CustomerId);

        foreach (var item in cmd.Items)
        {
            order.AddLine(item.ProductId, item.Quantity, item.UnitPrice);
        }

        // ✅ Domain service calcula precio final
        var finalTotal = _pricingService.CalculateTotalWithDiscounts(order, customer);

        order.Submit();
        await _orderRepo.SaveAsync(order);

        return order.OrderId;
    }
}
```

## Especificaciones (Specification Pattern)

```csharp
// ✅ Encapsular reglas de negocio complejas en Specifications

namespace Talma.Sales.Domain.Specifications
{
    public interface ISpecification<T>
    {
        bool IsSatisfiedBy(T entity);
    }

    // ✅ Especificación reutilizable
    public class OrderRequiresManagerApprovalSpec : ISpecification<Order>
    {
        private const decimal ManagerApprovalThreshold = 10000m;

        public bool IsSatisfiedBy(Order order)
        {
            return order.Total.Amount > ManagerApprovalThreshold;
        }
    }

    public class OrderIsApprovedSpec : ISpecification<Order>
    {
        public bool IsSatisfiedBy(Order order)
        {
            return order.Status == OrderStatus.Approved;
        }
    }

    public class OrderCanBeShippedSpec : ISpecification<Order>
    {
        public bool IsSatisfiedBy(Order order)
        {
            return order.Status == OrderStatus.Approved &&
                   order.Lines.All(l => l.Quantity > 0);
        }
    }
}

// Uso en entidad:

public class Order
{
    private readonly OrderRequiresManagerApprovalSpec _requiresManagerApproval = new();

    public void Approve(Guid approvedBy, Employee approver)
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException("Only pending orders can be approved");

        // ✅ Usar especificación para validar regla
        if (_requiresManagerApproval.IsSatisfiedBy(this))
        {
            if (approver.Role != EmployeeRole.Manager &&
                approver.Role != EmployeeRole.Director)
            {
                throw new DomainException(
                    $"Orders over ${_requiresManagerApproval.ManagerApprovalThreshold} require manager approval");
            }
        }

        Status = OrderStatus.Approved;
        AddDomainEvent(new OrderApproved(OrderId, approvedBy));
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** encapsular reglas de negocio en el modelo de dominio
- **MUST** usar propiedades privadas con setters privados
- **MUST** validar invariantes en constructores y métodos
- **MUST** prevenir creación de estado inválido
- **MUST** usar factory methods para creación compleja
- **MUST** calcular propiedades derivadas (no almacenarlas)
- **MUST** usar métodos con nombres del dominio (no CRUD genérico)
- **MUST** publicar domain events en cambios de estado significativos
- **MUST** usar value objects para conceptos sin identidad

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar domain services cuando comportamiento cruza agregados
- **SHOULD** usar specification pattern para reglas complejas reutilizables
- **SHOULD** limitar colecciones a ReadOnly desde afuera
- **SHOULD** usar enums para estados con transiciones controladas
- **SHOULD** validar argumentos con guard clauses al inicio de métodos
- **SHOULD** documentar invariantes en comentarios XML
- **SHOULD** crear métodos Reconstitute para Entity Framework

### MAY (Opcional)

- **MAY** usar double dispatch para comportamiento polimórfico
- **MAY** implementar IEquatable para comparación de entidades
- **MAY** usar Result<T> en lugar de exceptions para business errors

### MUST NOT (Prohibido)

- **MUST NOT** exponer setters públicos en entidades
- **MUST NOT** permitir construcción con estado inválido
- **MUST NOT** almacenar propiedades derivadas (calcularlas)
- **MUST NOT** usar métodos genéricos Update/Set sin validación
- **MUST NOT** poner lógica de dominio en servicios de aplicación
- **MUST NOT** ignorar validación por "performance" sin medir
- **MUST NOT** permitir colecciones mutables desde afuera del agregado

---

## Referencias

- [Lineamiento: Modelado de Dominio](../../lineamientos/arquitectura/09-modelado-de-dominio.md)
- Estándares relacionados:
  - [Ubiquitous Language](./ubiquitous-language.md)
  - [Aggregates](./aggregates.md)
  - [Entities and Value Objects](./entities-value-objects.md)
  - [Domain Events](./domain-events.md)
- Especificaciones:
  - [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
  - [AntiPattern: Anemic Domain Model (Martin Fowler)](https://martinfowler.com/bliki/AnemicDomainModel.html)
