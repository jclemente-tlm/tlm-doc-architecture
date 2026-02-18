---
id: aggregates
sidebar_position: 7
title: Aggregates and Transactional Boundaries
description: Definir agregados como límites de consistencia transaccional en el dominio
---

# Aggregates and Transactional Boundaries

## Contexto

Este estándar define cómo diseñar **agregados** (aggregates) como límites de consistencia transaccional en DDD, asegurando que **invariantes se mantienen en un scope bien definido**. Complementa el [lineamiento de Modelado de Dominio](../../lineamientos/arquitectura/09-modelado-de-dominio.md) estableciendo fronteras claras para transacciones y consistencia.

---

## Conceptos Fundamentales

### ¿Qué es un Agregado?

```yaml
# ✅ Aggregate = Cluster de objetos tratados como unidad

Definición:
  Grupo de entidades y value objects relacionados, con UN aggregate root
  que actúa como punto de entrada único.

Características:
  - Aggregate Root: Entidad principal que controla acceso al agregado
  - Límite de consistencia: Invariantes garantizadas DENTRO del agregado
  - Límite transaccional: Se persiste como unidad atómica
  - Identidad: Solo aggregate root es accesible desde afuera
  - Referencia por ID: Otros agregados referencian por ID, no por objeto

Objetivo: ✅ Proteger invariantes de negocio
  ✅ Definir alcance de transacción
  ✅ Simplificar modelo (menos objetos interconectados)
  ✅ Facilitar escalabilidad (agregados pequeños)

Anti-patterns: ❌ Agregados demasiado grandes (>10 entidades)
  ❌ Referencia directa entre agregados (navegación entre grafos)
  ❌ Modificar entidades hijas sin pasar por root
  ❌ Transacciones que cruzan múltiples agregados
```

### Ejemplo Visual

```yaml
# ✅ Order Aggregate (bien diseñado)

Order (Aggregate Root)
├── OrderId (identidad)
├── CustomerId (referencia por ID a otro agregado)
├── Status
├── Total (calculado)
└── OrderLines (entidades hijas dentro del agregado)
    ├── OrderLine 1
    │   ├── LineId
    │   ├── ProductId (referencia por ID)
    │   ├── Quantity
    │   └── UnitPrice
    ├── OrderLine 2
    └── OrderLine 3

Reglas:
- ✅ OrderLines solo accesibles via Order (aggregate root)
- ✅ Customer referenciado por ID (no objeto directo)
- ✅ Product referenciado por ID en OrderLine
- ✅ Invariante protegida: Order.Total = Sum(OrderLines.Subtotal)
- ✅ Una transacción = un Order completo con sus lines

# ❌ MALO: Todo es un gran agregado

Customer (Aggregate Root?)
├── CustomerId
├── Orders (navegable)
│   ├── Order 1
│   │   ├── OrderLines
│   │   └── Invoice (navegable)
│   │       └── Payments
│   ├── Order 2
│   └── Order 3
└── ShippingAddresses

Problemas:
❌ Transacción gigante (Customer + todos sus Orders)
❌ Lock de Customer al modificar Order
❌ Escalabilidad: Customer con 10K orders
❌ Demasiadas invariantes que proteger
```

## Diseño de Agregados

### Aggregate Root

```csharp
// ✅ BUENO: Order como Aggregate Root

namespace Talma.Sales.Domain.Model
{
    // ✅ Aggregate Root = entidad principal
    public class Order : AggregateRoot
    {
        public Guid OrderId { get; private set; }  // ✅ Identidad del agregado

        // ✅ Referencia por ID (no objeto Customer directo)
        public Guid CustomerId { get; private set; }

        public OrderStatus Status { get; private set; }
        public DateTime OrderDate { get; private set; }

        // ✅ Entidades hijas privadas, acceso controlado
        private readonly List<OrderLine> _lines = new();
        public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();

        // ✅ Propiedad calculada (invariante)
        public Money Total => _lines.Aggregate(
            Money.Zero("USD"),
            (sum, line) => sum + line.Subtotal);

        private Order() { }

        public static Order Create(Guid customerId)
        {
            if (customerId == Guid.Empty)
                throw new ArgumentException("Customer ID is required");

            return new Order
            {
                OrderId = Guid.NewGuid(),
                CustomerId = customerId,
                Status = OrderStatus.Draft,
                OrderDate = DateTime.UtcNow
            };
        }

        // ✅ Único punto de entrada para agregar líneas
        public void AddLine(Guid productId, int quantity, Money unitPrice)
        {
            if (Status != OrderStatus.Draft)
                throw new InvalidOperationException("Cannot modify submitted order");

            // ✅ Validar invariante: no duplicar productos
            if (_lines.Any(l => l.ProductId == productId))
                throw new DomainException(
                    $"Product {productId} already in order. Use UpdateLineQuantity instead.");

            // ✅ Crear entidad hija a través del root
            var line = OrderLine.Create(
                Guid.NewGuid(),
                OrderId,  // ✅ Línea conoce su order (referencia al parent)
                productId,
                quantity,
                unitPrice);

            _lines.Add(line);
            AddDomainEvent(new OrderLineAdded(OrderId, line.LineId, productId, quantity));
        }

        public void RemoveLine(Guid lineId)
        {
            if (Status != OrderStatus.Draft)
                throw new InvalidOperationException("Cannot modify submitted order");

            var line = _lines.FirstOrDefault(l => l.LineId == lineId);
            if (line == null)
                throw new DomainException($"Line {lineId} not found");

            _lines.Remove(line);
            AddDomainEvent(new OrderLineRemoved(OrderId, lineId));
        }

        public void UpdateLineQuantity(Guid lineId, int newQuantity)
        {
            if (Status != OrderStatus.Draft)
                throw new InvalidOperationException("Cannot modify submitted order");

            var line = _lines.FirstOrDefault(l => l.LineId == lineId);
            if (line == null)
                throw new DomainException($"Line {lineId} not found");

            // ✅ Modificar hija a través del root (control total)
            line.UpdateQuantity(newQuantity);
            AddDomainEvent(new OrderLineQuantityUpdated(OrderId, lineId, newQuantity));
        }

        // ✅ Submit valida invariantes del agregado completo
        public void Submit()
        {
            if (Status != OrderStatus.Draft)
                throw new InvalidOperationException("Only draft orders can be submitted");

            // ✅ Invariante: Order must have lines
            if (!_lines.Any())
                throw new DomainException("Cannot submit order without lines");

            // ✅ Invariante: Total must be positive
            if (Total.Amount <= 0)
                throw new DomainException("Cannot submit order with zero or negative total");

            Status = OrderStatus.Pending;
            AddDomainEvent(new OrderSubmitted(OrderId, CustomerId, Total));
        }
    }

    // ✅ OrderLine es entidad INTERNA del agregado (no aggregate root)
    public class OrderLine : Entity
    {
        public Guid LineId { get; private set; }
        public Guid OrderId { get; private set; }  // ✅ Referencia al parent (aggregate root)

        // ✅ Referencia por ID a Product (otro agregado)
        public Guid ProductId { get; private set; }

        public int Quantity { get; private set; }
        public Money UnitPrice { get; private init; }

        public Money Subtotal => UnitPrice * Quantity;

        // ✅ Constructor internal - solo Order puede crear OrderLines
        internal static OrderLine Create(
            Guid lineId,
            Guid orderId,
            Guid productId,
            int quantity,
            Money unitPrice)
        {
            if (quantity <= 0)
                throw new ArgumentException("Quantity must be positive");
            if (unitPrice.Amount < 0)
                throw new ArgumentException("Unit price cannot be negative");

            return new OrderLine
            {
                LineId = lineId,
                OrderId = orderId,
                ProductId = productId,
                Quantity = quantity,
                UnitPrice = unitPrice
            };
        }

        // ✅ Internal - solo Order puede modificar
        internal void UpdateQuantity(int newQuantity)
        {
            if (newQuantity <= 0)
                throw new ArgumentException("Quantity must be positive");

            Quantity = newQuantity;
        }
    }
}

// ❌ MALO: OrderLine accesible sin control

public class Order
{
    public List<OrderLine> Lines { get; set; }  // ❌ List público
}

// Problema:
var order = await repo.GetByIdAsync(orderId);
order.Lines.Add(new OrderLine { ... });  // ❌ Bypasea validaciones del Order!
order.Lines.Clear();  // ❌ Puede dejar Order inválido!
```

### Referencias Entre Agregados

```csharp
// ✅ BUENO: Referencias por ID

public class Order : AggregateRoot
{
    public Guid OrderId { get; private set; }
    public Guid CustomerId { get; private set; }  // ✅ ID, no objeto Customer

    // ❌ NUNCA: public Customer Customer { get; set; }
}

public class OrderLine : Entity
{
    public Guid LineId { get; private set; }
    public Guid ProductId { get; private set; }  // ✅ ID, no objeto Product

    // ❌ NUNCA: public Product Product { get; set; }
}

// Consumo en Application Service:

public class PlaceOrderCommandHandler
{
    private readonly IOrderRepository _orderRepo;
    private readonly ICustomerRepository _customerRepo;  // ✅ Repo separado
    private readonly IProductRepository _productRepo;     // ✅ Repo separado

    public async Task<Guid> HandleAsync(PlaceOrderCommand cmd)
    {
        // ✅ Cargar Customer (otro agregado) por ID
        var customer = await _customerRepo.GetByIdAsync(cmd.CustomerId);
        if (customer == null)
            throw new DomainException($"Customer {cmd.CustomerId} not found");

        if (customer.Status != CustomerStatus.Active)
            throw new DomainException("Customer is not active");

        // ✅ Crear Order referenciando Customer por ID
        var order = Order.Create(cmd.CustomerId);

        foreach (var item in cmd.Items)
        {
            // ✅ Validar Product (otro agregado) existe
            var product = await _productRepo.GetByIdAsync(item.ProductId);
            if (product == null)
                throw new DomainException($"Product {item.ProductId} not found");

            if (product.Status != ProductStatus.Available)
                throw new DomainException($"Product {product.Name} is not available");

            // ✅ OrderLine solo guarda ProductId, no objeto Product
            order.AddLine(item.ProductId, item.Quantity, product.Price);
        }

        order.Submit();

        // ✅ Persistir solo Order agregado (transacción atómica)
        await _orderRepo.SaveAsync(order);

        return order.OrderId;
    }
}

// ❌ MALO: Navegación directa entre agregados

public class Order
{
    public Customer Customer { get; set; }  // ❌ Objeto directo
    public List<OrderLine> Lines { get; set; }
}

public class OrderLine
{
    public Product Product { get; set; }  // ❌ Objeto directo
}

// Problemas:
// 1. ¿Qué pasa si Customer cambia Name? ¿Se actualiza automáticamente?
// 2. ¿Entity Framework debe cargar Customer + todos sus Orders?
// 3. ¿Lock de Customer al guardar Order?
// 4. Grafo de objetos masivo en memoria
```

### Consistencia Eventual Entre Agregados

```csharp
// ✅ BUENO: Consistencia eventual con domain events

// Escenario: Cuando Order es Approved, actualizar Customer.TotalSpent

// 1. Order publica evento
public class Order : AggregateRoot
{
    public void Approve(Guid approvedBy)
    {
        if (Status != OrderStatus.Pending)
            throw new InvalidOperationException("Only pending orders can be approved");

        Status = OrderStatus.Approved;

        // ✅ Domain event (procesado después)
        AddDomainEvent(new OrderApproved(OrderId, CustomerId, Total));
    }
}

// 2. Event Handler actualiza Customer (otro agregado)
public class OrderApprovedEventHandler : IDomainEventHandler<OrderApproved>
{
    private readonly ICustomerRepository _customerRepo;

    public async Task HandleAsync(OrderApproved evt)
    {
        // ✅ Cargar Customer en transacción separada
        var customer = await _customerRepo.GetByIdAsync(evt.CustomerId);
        if (customer == null) return;  // Customer fue eliminado

        // ✅ Actualizar Customer (su propio agregado)
        customer.RecordPurchase(evt.Total);

        // ✅ Persistir Customer en transacción separada
        await _customerRepo.SaveAsync(customer);
    }
}

public class Customer : AggregateRoot
{
    public Money TotalSpent { get; private set; }
    public int TotalOrders { get; private set; }

    public void RecordPurchase(Money amount)
    {
        TotalSpent += amount;
        TotalOrders++;

        // Regla: Customer VIP si TotalSpent > $50K
        if (TotalSpent.Amount >= 50000 && Status != CustomerStatus.Vip)
        {
            Status = CustomerStatus.Vip;
            AddDomainEvent(new CustomerPromotedToVip(CustomerId));
        }
    }
}

// ✅ Resultado:
// - Order y Customer se persisten en transacciones SEPARADAS
// - Si falla update de Customer, Order ya fue guardado (consistencia eventual)
// - Sin locks entre agregados
// - Escalable

// ❌ MALO: Modificar 2 agregados en misma transacción

public async Task ApproveOrderAsync(Guid orderId)
{
    using var transaction = await _dbContext.Database.BeginTransactionAsync();

    var order = await _orderRepo.GetByIdAsync(orderId);
    order.Approve(approverId);

    // ❌ Modificar otro agregado en misma transacción
    var customer = await _customerRepo.GetByIdAsync(order.CustomerId);
    customer.TotalSpent += order.Total;

    await _dbContext.SaveChangesAsync();  // ❌ Lock de Order Y Customer
    await transaction.CommitAsync();
}
```

## Tamaño de Agregados

```yaml
# ✅ Regla de oro: Agregados pequeños

Lineamiento:
  - Prefiere agregados pequeños (1-5 entidades)
  - Solo incluye entidades necesarias para proteger invariantes
  - Si agregado crece (>10 entidades), probablemente debe dividirse

Ejemplo BUENO: Order Aggregate

Order (1 entidad raíz)
└── OrderLines (N entidades hijas)

Invariantes protegidos:
  ✅ Order.Total = Sum(OrderLines.Subtotal)
  ✅ Order no puede tener 0 lines cuando Status = Pending
  ✅ OrderLine.ProductId no puede duplicarse

Ejemplo MALO: Customer Aggregate gigante

Customer (1 entidad raíz)
├── Orders (N entidades)
│   └── OrderLines (M entidades)
├── Invoices (N entidades)
│   └── Payments (M entidades)
└── SupportTickets (N entidades)

Problemas:
  ❌ Transacción gigante
  ❌ Lock de Customer al modificar cualquier sub-entidad
  ❌ Difícil escalar (Customer con 10K Orders)
  ❌ ¿Realmente Customer.TotalSpent es invariante crítica?

Solución: Dividir en 3 agregados

1. Customer Aggregate:
   - CustomerId, Name, Email, Status
   - ShippingAddresses (value objects, máximo 5)

2. Order Aggregate (separado):
   - OrderId, CustomerId (referencia), Lines

3. Invoice Aggregate (separado):
   - InvoiceId, CustomerId (referencia), OrderId (referencia), Payments
```

### Ejemplo: División de Agregados

```csharp
// ✅ BUENO: 3 agregados independientes

// 1. Customer Aggregate (pequeño)
public class Customer : AggregateRoot
{
    public Guid CustomerId { get; private set; }
    public string Name { get; private set; }
    public Email Email { get; private set; }
    public CustomerStatus Status { get; private set; }

    // ✅ Value objects (max 5, límite por regla de negocio)
    private readonly List<Address> _shippingAddresses = new();
    public IReadOnlyCollection<Address> ShippingAddresses => _shippingAddresses.AsReadOnly();

    // ✅ Propiedades denormalizadas (actualizadas por events)
    public Money TotalSpent { get; private set; }  // Actualizado por OrderApprovedEvent
    public int TotalOrders { get; private set; }    // Actualizado por OrderApprovedEvent

    public void AddShippingAddress(Address address)
    {
        // ✅ Invariante: max 5 addresses
        if (_shippingAddresses.Count >= 5)
            throw new DomainException("Customer cannot have more than 5 addresses");

        _shippingAddresses.Add(address);
    }
}

// 2. Order Aggregate (independiente)
public class Order : AggregateRoot
{
    public Guid OrderId { get; private set; }
    public Guid CustomerId { get; private set; }  // ✅ Referencia por ID
    public OrderStatus Status { get; private set; }

    private readonly List<OrderLine> _lines = new();
    public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();

    public Money Total => _lines.Aggregate(Money.Zero("USD"), (s, l) => s + l.Subtotal);
}

// 3. Invoice Aggregate (independiente)
public class Invoice : AggregateRoot
{
    public Guid InvoiceId { get; private set; }
    public Guid CustomerId { get; private set; }  // ✅ Referencia por ID
    public Guid OrderId { get; private set; }     // ✅ Referencia por ID
    public InvoiceStatus Status { get; private set; }

    private readonly List<Payment> _payments = new();
    public IReadOnlyCollection<Payment> Payments => _payments.AsReadOnly();

    public Money TotalAmount { get; private set; }
    public Money TotalPaid => _payments.Aggregate(Money.Zero("USD"), (s, p) => s + p.Amount);
    public Money Outstanding => TotalAmount - TotalPaid;

    public void RecordPayment(Money amount, string paymentReference)
    {
        // ✅ Invariante: Total paid no puede exceder total amount
        if (TotalPaid + amount > TotalAmount)
            throw new DomainException("Payment exceeds invoice amount");

        var payment = new Payment(Guid.NewGuid(), InvoiceId, amount, paymentReference);
        _payments.Add(payment);

        // ✅ Si está totalmente pagada
        if (TotalPaid == TotalAmount)
        {
            Status = InvoiceStatus.Paid;
            AddDomainEvent(new InvoicePaid(InvoiceId, CustomerId, TotalAmount));
        }
    }
}

// Beneficios:
// ✅ Cada agregado es pequeño y maneja sus invariantes
// ✅ Transacciones independientes (menos locks)
// ✅ Escalable: Customer con 10K Orders no afecta agregado Customer
// ✅ Consistencia eventual: Customer.TotalSpent sincroniza via events
```

## Persistencia de Agregados

```csharp
// ✅ BUENO: Repositorio por Aggregate Root

namespace Talma.Sales.Infrastructure.Persistence
{
    public class OrderRepository : IOrderRepository
    {
        private readonly SalesDbContext _context;

        public async Task<Order?> GetByIdAsync(Guid orderId)
        {
            // ✅ Cargar agregado completo (root + hijas)
            return await _context.Orders
                .Include(o => o.Lines)  // ✅ OrderLines parte del agregado
                .FirstOrDefaultAsync(o => o.OrderId == orderId);
        }

        public async Task SaveAsync(Order order)
        {
            // ✅ EF detecta cambios en root y hijas automáticamente
            if (_context.Entry(order).State == EntityState.Detached)
            {
                _context.Orders.Add(order);
            }

            await _context.SaveChangesAsync();

            // ✅ Publicar domain events después de persistir
            await PublishDomainEventsAsync(order);
        }

        private async Task PublishDomainEventsAsync(Order order)
        {
            var events = order.GetDomainEvents();
            order.ClearDomainEvents();

            foreach (var evt in events)
            {
                await _eventPublisher.PublishAsync(evt);
            }
        }
    }
}

// Entity Framework Configuration:

public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.ToTable("orders", "sales");
        builder.HasKey(o => o.OrderId);

        // ✅ OrderLines parte del agregado (cascade)
        builder.OwnsMany(o => o.Lines, lines =>
        {
            lines.ToTable("order_lines", "sales");
            lines.HasKey(l => l.LineId);
            lines.Property(l => l.Quantity).IsRequired();

            // ✅ Money value object
            lines.OwnsOne(l => l.UnitPrice, money =>
            {
                money.Property(m => m.Amount).HasColumnName("unit_price");
                money.Property(m => m.Currency).HasColumnName("currency");
            });
        });

        // ✅ Total calculado, no persisted (evita desincronización)
        builder.Ignore(o => o.Total);

        builder.Property(o => o.Status)
            .HasConversion<string>()
            .HasMaxLength(20);
    }
}

// ❌ MALO: Repositorio genérico para entidades hijas

public interface IOrderLineRepository  // ❌ OrderLine no es aggregate root!
{
    Task<OrderLine> GetByIdAsync(Guid lineId);
    Task SaveAsync(OrderLine line);  // ❌ No tiene sentido sin Order
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** identificar aggregate root claramente
- **MUST** acceder entidades hijas solo vía aggregate root
- **MUST** referenciar otros agregados por ID (no objeto directo)
- **MUST** proteger invariantes dentro del límite del agregado
- **MUST** persistir agregado completo en una transacción (root + hijas)
- **MUST** mantener agregados pequeños (1-5 entidades típicamente)
- **MUST** crear repositorio solo para aggregate root (NO para entidades hijas)
- **MUST** usar consistencia eventual para actualizar múltiples agregados

### SHOULD (Fuertemente recomendado)

- **SHOULD** limitar tamaño de colecciones en agregado (ej: max 100 items)
- **SHOULD** calcular propiedades derivadas (no almacenarlas)
- **SHOULD** publicar domain events después de persistir agregado
- **SHOULD** cargar agregado completo (eager loading de hijas)
- **SHOULD** usar cascade deletes para entidades hijas
- **SHOULD** dividir agregado si crece más de 10 entidades

### MAY (Opcional)

- **MAY** usar lazy loading para colecciones grandes (con precaución)
- **MAY** implementar soft delete en aggregate root
- **MAY** versionar agregados con timestamp para optimistic concurrency

### MUST NOT (Prohibido)

- **MUST NOT** referenciar objetos de otros agregados directamente
- **MUST NOT** modificar entidades hijas sin pasar por aggregate root
- **MUST NOT** crear repositorio para entidades que no son aggregate root
- **MUST NOT** permitir modificación de colección de hijas desde afuera
- **MUST NOT** modificar múltiples agregados en una transacción (usar eventos)
- **MUST NOT** cargar grafos gigantes de múltiples agregados
- **MUST NOT** ignorar invariantes por "performance" sin medir

---

## Referencias

- [Lineamiento: Modelado de Dominio](../../lineamientos/arquitectura/09-modelado-de-dominio.md)
- Estándares relacionados:
  - [Domain Model](./domain-model.md)
  - [Entities and Value Objects](./entities-value-objects.md)
  - [Domain Events](./domain-events.md)
  - [Bounded Contexts](./bounded-contexts.md)
- Especificaciones:
  - [Effective Aggregate Design (Vaughn Vernon)](https://vaughnvernon.com/)
  - [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
