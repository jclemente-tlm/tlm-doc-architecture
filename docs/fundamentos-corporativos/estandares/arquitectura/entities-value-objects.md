---
id: entities-value-objects
sidebar_position: 8
title: Entities and Value Objects
description: Distinguir entre entidades con identidad y value objects definidos por sus valores
---

# Entities and Value Objects

## Contexto

Este estándar define la distinción entre **Entidades** (entities) y **Value Objects** en DDD, asegurando que **conceptos con identidad y conceptos sin identidad se modelen correctamente**. Complementa el [lineamiento de Modelado de Dominio](../../lineamientos/arquitectura/09-modelado-de-dominio.md) estableciendo cuándo usar cada patrón.

---

## Conceptos Fundamentales

### Entity vs Value Object

```yaml
# ✅ Entity = Identidad única, mutable

Características:
  - Tiene identidad única (ID)
  - Igualdad por ID (no por atributos)
  - Mutable (su estado puede cambiar)
  - Tiene lifecycle (creación, modificación, eliminación)
  - Rastrea cambios en el tiempo

Ejemplos:
  - Order (OrderId único)
  - Customer (CustomerId único)
  - Product (ProductId único)
  - Invoice (InvoiceId único)

Pregunta clave: ¿Dos instancias con mismos atributos son la MISMA cosa?
  Order(id=1, total=$100) vs Order(id=2, total=$100)
  → NO son el mismo Order (IDs diferentes) ✅ Entity

# ✅ Value Object = Sin identidad, inmutable

Características:
  - NO tiene identidad (sin ID)
  - Igualdad por valor (todos sus atributos)
  - Inmutable (no cambia; se reemplaza)
  - Sin lifecycle (no se rastrea)
  - Puede ser compartido (flyweight)

Ejemplos:
  - Money (amount, currency)
  - Address (street, city, zip)
  - Email (value)
  - DateRange (start, end)
  - PhoneNumber (value)

Pregunta clave: ¿Dos instancias con mismos atributos son la MISMA cosa?
  Money($100, USD) vs Money($100, USD)
  → SÍ son el mismo valor ✅ Value Object
```

### Decisión: Entity vs Value Object

```yaml
# ✅ Criterios de decisión

Usa Entity si:
  ✅ Necesitas rastrear cambios en el tiempo
  ✅ Tiene identidad única (ID)
  ✅ Dos instancias con mismos atributos son DIFERENTES
  ✅ Tiene lifecycle (creación → evolución → eliminación)
  ✅ Referenciado por otros objetos (via ID)

Ejemplos:
  - Order: OrderId=1 total=$100 → cambié precio → total=$120
    (Sigue siendo Order 1, su estado cambió)
  - Customer: CustomerId=X name="Juan Pérez" → cambié a "Juan P. Pérez"
    (Sigue siendo Customer X, su nombre cambió)

Usa Value Object si:
  ✅ Definido completamente por sus atributos
  ✅ Sin identidad propia
  ✅ Dos instancias con mismos atributos son IGUALES
  ✅ Inmutable (no cambia, se reemplaza)
  ✅ Puede ser compartido sin problemas

Ejemplos:
  - Money($100, USD): Si cambio amount, es OTRO Money (no "actual izó")
  - Address("Av Lima 123", "Lima"): Si cambio street, es OTRA Address
  - Email("user@domain.com"): Si cambio, es OTRO Email

Casos ambiguos:

Address:
  ❓ Si necesitas rastrear "Address X fue creada el 2024-01-15"
     → Probablemente Entity
  ✅ Si solo describes ubicación (sin historial)
     → Value Object

PhoneNumber:
  ❓ Si registras "PhoneNumber validado el 2024-01-15"
     → Probablemente Entity
  ✅ Si solo describes número
     → Value Object
```

## Implementación de Entities

```csharp
// ✅ BUENO: Entity con identidad y mutabilidad

namespace Talma.Sales.Domain.Model
{
    // ✅ Entity base class
    public abstract class Entity
    {
        private readonly List<IDomainEvent> _domainEvents = new();
        public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

        protected void AddDomainEvent(IDomainEvent evt) => _domainEvents.Add(evt);
        public void ClearDomainEvents() => _domainEvents.Clear();

        // ✅ Igualdad por ID (no por atributos)
        public override bool Equals(object? obj)
        {
            if (obj is not Entity other) return false;
            if (ReferenceEquals(this, other)) return true;
            if (GetType() != other.GetType()) return false;

            return GetIdentity().Equals(other.GetIdentity());
        }

        public override int GetHashCode() => GetIdentity().GetHashCode();

        protected abstract object GetIdentity();
    }

    // ✅ Order entity con identidad OrderId
    public class Order : Entity
    {
        // ✅ Identidad única
        public Guid OrderId { get; private set; }

        // ✅ Atributos mutables
        public Guid CustomerId { get; private set; }
        public OrderStatus Status { get; private set; }  // Cambia en el tiempo
        public DateTime OrderDate { get; private set; }

        private readonly List<OrderLine> _lines = new();
        public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();

        // ✅ Propiedad calculada
        public Money Total => _lines.Aggregate(Money.Zero("USD"), (s, l) => s + l.Subtotal);

        protected override object GetIdentity() => OrderId;

        // ✅ Constructor privado
        private Order() { }

        // ✅ Factory method
        public static Order Create(Guid customerId)
        {
            var order = new Order
            {
                OrderId = Guid.NewGuid(),  // ✅ ID generado
                CustomerId = customerId,
                Status = OrderStatus.Draft,
                OrderDate = DateTime.UtcNow
            };

            order.AddDomainEvent(new OrderCreated(order.OrderId, customerId));
            return order;
        }

        // ✅ Comportamiento que muta estado
        public void Submit()
        {
            if (Status != OrderStatus.Draft)
                throw new InvalidOperationException("Only draft orders can be submitted");

            // ✅ Mutation: Draft → Pending
            Status = OrderStatus.Pending;

            AddDomainEvent(new OrderSubmitted(OrderId, CustomerId, Total));
        }

        public void Approve(Guid approvedBy)
        {
            // ✅ Mutation: Pending → Approved
            Status = OrderStatus.Approved;
            AddDomainEvent(new OrderApproved(OrderId, approvedBy));
        }
    }
}

// Uso:

var order1 = Order.Create(customerId);
order1.OrderId // Guid("abc...")

var order2 = Order.Create(customerId);  // Mismo customer
order2.OrderId // Guid("xyz...")  ← Diferente ID

// ✅ order1 != order2 (IDs diferentes)
Assert.NotEqual(order1, order2);

// ✅ Mismo order cargado 2 veces = igual
var orderFromDb1 = await repo.GetByIdAsync(orderId);
var orderFromDb2 = await repo.GetByIdAsync(orderId);
Assert.Equal(orderFromDb1, orderFromDb2);  // Mismo ID
```

## Implementación de Value Objects

```csharp
// ✅ BUENO: Value Object con igualdad por valor e inmutabilidad

namespace Talma.SharedKernel
{
    // ✅ record = inmutable por defecto
    public record Money
    {
        public decimal Amount { get; init; }
        public string Currency { get; init; }

        // ✅ Constructor con validación
        public Money(decimal amount, string currency)
        {
            if (string.IsNullOrWhiteSpace(currency) || currency.Length != 3)
                throw new ArgumentException("Currency must be 3-letter ISO code", nameof(currency));

            Amount = amount;
            Currency = currency.ToUpperInvariant();
        }

        // ✅ Factory methods
        public static Money Zero(string currency) => new(0, currency);
        public static Money Dollars(decimal amount) => new(amount, "USD");
        public static Money Euros(decimal amount) => new(amount, "EUR");
        public static Money Soles(decimal amount) => new(amount, "PEN");

        // ✅ Operadores (retornan NUEVO Money, no mutan)
        public static Money operator +(Money left, Money right)
        {
            if (left.Currency != right.Currency)
                throw new InvalidOperationException(
                    $"Cannot add {left.Currency} and {right.Currency}");

            return new Money(left.Amount + right.Amount, left.Currency);
        }

        public static Money operator -(Money left, Money right)
        {
            if (left.Currency != right.Currency)
                throw new InvalidOperationException(
                    $"Cannot subtract {left.Currency} and {right.Currency}");

            return new Money(left.Amount - right.Amount, left.Currency);
        }

        public static Money operator *(Money money, decimal multiplier)
        {
            return new Money(money.Amount * multiplier, money.Currency);
        }

        public static Money operator /(Money money, decimal divisor)
        {
            if (divisor == 0)
                throw new DivideByZeroException();

            return new Money(money.Amount / divisor, money.Currency);
        }

        // ✅ Comparison operators
        public static bool operator >(Money left, Money right)
        {
            if (left.Currency != right.Currency)
                throw new InvalidOperationException("Cannot compare different currencies");

            return left.Amount > right.Amount;
        }

        public static bool operator <(Money left, Money right)
        {
            if (left.Currency != right.Currency)
                throw new InvalidOperationException("Cannot compare different currencies");

            return left.Amount < right.Amount;
        }

        // ✅ record proporciona Equals por valor automáticamente
        // Money(100, "USD") == Money(100, "USD") → true
        // Money(100, "USD") == Money(100, "EUR") → false
    }
}

// Uso:

var price1 = Money.Dollars(100);
var price2 = Money.Dollars(100);

// ✅ Igualdad por valor (no por referencia)
Assert.Equal(price1, price2);  // ✅ true (mismo amount y currency)

var price3 = Money.Dollars(200);
Assert.NotEqual(price1, price3);  // ✅ false (amount diferente)

// ✅ Inmutabilidad: operaciones retornan NUEVO objeto
var total = price1 + price3;  // Money(300, "USD")
// price1 y price3 NO cambiaron

// ❌ Esto NO compila (record es inmutable)
// price1.Amount = 150;  // Compile error: init-only property

// ✅ Para "cambiar", creas nuevo objeto
var updatedPrice = price1 with { Amount = 150 };
// price1 sigue siendo Money(100, "USD")
// updatedPrice es Money(150, "USD")
```

### Más Ejemplos de Value Objects

```csharp
// ✅ Address Value Object

public record Address
{
    public string Street { get; init; }
    public string City { get; init; }
    public string State { get; init; }
    public string ZipCode { get; init; }
    public string Country { get; init; }

    public Address(string street, string city, string state, string zipCode, string country)
    {
        if (string.IsNullOrWhiteSpace(street))
            throw new ArgumentException("Street is required", nameof(street));
        if (string.IsNullOrWhiteSpace(city))
            throw new ArgumentException("City is required", nameof(city));
        if (string.IsNullOrWhiteSpace(country))
            throw new ArgumentException("Country is required", nameof(country));

        Street = street;
        City = city;
        State = state;
        ZipCode = zipCode;
        Country = country;
    }

    public override string ToString() =>
        $"{Street}, {City}, {State} {ZipCode}, {Country}";
}

// ✅ Email Value Object con validación

public record Email
{
    public string Value { get; init; }

    public Email(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("Email is required", nameof(value));

        if (!IsValidEmail(value))
            throw new ArgumentException($"Invalid email format: {value}", nameof(value));

        Value = value.ToLowerInvariant();
    }

    private static bool IsValidEmail(string email)
    {
        try
        {
            var addr = new System.Net.Mail.MailAddress(email);
            return addr.Address == email;
        }
        catch
        {
            return false;
        }
    }

    public static implicit operator string(Email email) => email.Value;
    public override string ToString() => Value;
}

// ✅ DateRange Value Object

public record DateRange
{
    public DateTime Start { get; init; }
    public DateTime End { get; init; }

    public DateRange(DateTime start, DateTime end)
    {
        if (end < start)
            throw new ArgumentException("End date must be after start date");

        Start = start;
        End = end;
    }

    public int DurationInDays => (End - Start).Days;

    public bool Contains(DateTime date) => date >= Start && date <= End;

    public bool Overlaps(DateRange other) =>
        Start <= other.End && End >= other.Start;
}

// ✅ PhoneNumber Value Object

public record PhoneNumber
{
    public string CountryCode { get; init; }  // +51
    public string Number { get; init; }        // 987654321

    public PhoneNumber(string countryCode, string number)
    {
        if (string.IsNullOrWhiteSpace(countryCode))
            throw new ArgumentException("Country code is required");

        if (!countryCode.StartsWith("+"))
            throw new ArgumentException("Country code must start with +");

        if (string.IsNullOrWhiteSpace(number))
            throw new ArgumentException("Number is required");

        // Remove spaces, dashes
        number = new string(number.Where(char.IsDigit).ToArray());

        if (number.Length < 6 || number.Length > 15)
            throw new ArgumentException("Invalid phone number length");

        CountryCode = countryCode;
        Number = number;
    }

    public string FullNumber => $"{CountryCode}{Number}";

    public override string ToString() => FullNumber;
}

// Uso de value objects en Entity:

public class Customer : AggregateRoot
{
    public Guid CustomerId { get; private set; }
    public string Name { get; private set; }

    // ✅ Value objects como propiedades
    public Email Email { get; private set; }
    public PhoneNumber? PhoneNumber { get; private set; }  // Opcional
    public Address BillingAddress { get; private set; }

    private readonly List<Address> _shippingAddresses = new();
    public IReadOnlyCollection<Address> ShippingAddresses => _shippingAddresses.AsReadOnly();

    public void UpdateEmail(Email newEmail)
    {
        if (newEmail == null)
            throw new ArgumentNullException(nameof(newEmail));

        // ✅ Reemplazar value object completo (no mutar)
        Email = newEmail;

        AddDomainEvent(new CustomerEmailUpdated(CustomerId, newEmail.Value));
    }

    public void UpdateBillingAddress(Address newAddress)
    {
        // ✅ Reemplazar value object
        BillingAddress = newAddress ?? throw new ArgumentNullException(nameof(newAddress));
    }
}
```

## Persistencia de Value Objects

```csharp
// ✅ Entity Framework: Value Objects como Owned Types

public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.ToTable("orders", "sales");
        builder.HasKey(o => o.OrderId);

        // ✅ Money value object mapeado en columnas de Order
        builder.OwnsOne(o => o.ShippingCost, money =>
        {
            money.Property(m => m.Amount)
                .HasColumnName("shipping_cost_amount")
                .HasColumnType("decimal(18,2)");

            money.Property(m => m.Currency)
                .HasColumnName("shipping_cost_currency")
                .HasMaxLength(3);
        });

        // ✅ Address value object mapeado en columnas de Order
        builder.OwnsOne(o => o.ShippingAddress, address =>
        {
            address.Property(a => a.Street).HasColumnName("shipping_street").HasMaxLength(200);
            address.Property(a => a.City).HasColumnName("shipping_city").HasMaxLength(100);
            address.Property(a => a.State).HasColumnName("shipping_state").HasMaxLength(100);
            address.Property(a => a.ZipCode).HasColumnName("shipping_zip").HasMaxLength(20);
            address.Property(a => a.Country).HasColumnName("shipping_country").HasMaxLength(2);
        });

        // ✅ Total calculado, NO persistido
        builder.Ignore(o => o.Total);
    }
}

// Resultado en DB:

CREATE TABLE sales.orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,

    -- ✅ Money value object (2 columnas)
    shipping_cost_amount DECIMAL(18,2),
    shipping_cost_currency VARCHAR(3),

    -- ✅ Address value object (5 columnas)
    shipping_street VARCHAR(200),
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    shipping_zip VARCHAR(20),
    shipping_country VARCHAR(2)
);

// ✅ NO hay tabla separada para Money o Address (son value objects)
```

## Entity vs Value Object: Casos Reales

```yaml
# ✅ Casos claros

Entity:
  - Order: Tiene OrderId, evoluciona (Draft → Pending → Approved)
  - Customer: Tiene CustomerId, su información cambia en el tiempo
  - Product: Tiene ProductId, precio/stock cambian
  - Invoice: Tiene InvoiceId, se paga en el tiempo

Value Object:
  - Money: $100 USD siempre es $100 USD (no "cambia")
  - Address: Av Lima 123 siempre es esa dirección
  - Email: user@domain.com es solo un valor
  - DateRange: 2024-01-01 a 2024-01-31 es solo rango

# ❓ Casos ambiguos

ShippingAddress en Order:
  Opción 1 - Value Object (preferida):
    ✅ Address es snapshot al momento del Order
    ✅ Si Customer cambia su address, Order no cambia
    ✅ Order tiene Address("Av Lima 123") embeded

  Opción 2 - Entity (si necesitas):
    ❓ Si registras "delivery intentado en esta address el 2024-01-15"
    ❓ Si address tiene lifecycle propio
    → Entonces AddressId, y Order referencia por ID

PaymentMethod:
  Opción 1 - Value Object: ✅ Si solo guardas tipo + últimos 4 dígitos
    ✅ CreditCard("Visa", "4242")

  Opción 2 - Entity: ❓ Si rastrear "tarjeta agregada el 2024-01-15"
    ❓ Si Customer tiene múltiples tarjetas guardadas
    → Entonces PaymentMethodId

Regla práctica:
  - Si lo embedas en otra entidad (columnas en misma tabla) → Value Object
  - Si tiene tabla propia con ID → Entity
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Entity para conceptos con identidad única
- **MUST** usar Value Object para conceptos sin identidad
- **MUST** hacer value objects inmutables
- **MUST** implementar igualdad por ID en entities
- **MUST** implementar igualdad por valor en value objects
- **MUST** validar value objects en constructor
- **MUST** usar C# records para value objects
- **MUST** retornar nuevos value objects en operaciones (no mutar)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar factory methods para creación compleja
- **SHOULD** sobrescribir ToString() en value objects
- **SHOULD** implementar operadores (+, -, \*, /) en value objects como Money
- **SHOULD** mapear value objects como Owned Types en EF Core
- **SHOULD** compartir value objects comunes en SharedKernel
- **SHOULD** validar invariantes en value object constructor

### MAY (Opcional)

- **MAY** implementar conversion operators (implicit/explicit)
- **MAY** usar value object collections (ej: Money.Sum())
- **MAY** crear value objects genéricos (ej: Range<T>)

### MUST NOT (Prohibido)

- **MUST NOT** dar identidad (ID) a value objects
- **MUST NOT** hacer value objects mutables (setters públicos)
- **MUST NOT** comparar entities por valor (solo por ID)
- **MUST NOT** comparar value objects por referencia (solo por valor)
- **MUST NOT** crear tabla separada para value objects (embedarlos)
- **MUST NOT** referenciar value objects por ID desde otras entidades
- **MUST NOT** publicar domain events desde value objects (solo entities)

---

## Referencias

- [Lineamiento: Modelado de Dominio](../../lineamientos/arquitectura/09-modelado-de-dominio.md)
- Estándares relacionados:
  - [Domain Model](./domain-model.md)
  - [Aggregates](./aggregates.md)
  - [Ubiquitous Language](./ubiquitous-language.md)
- Especificaciones:
  - [Domain-Driven Design (Eric Evans)](https://www.domainlanguage.com/ddd/)
  - [Implementing Domain-Driven Design (Vaughn Vernon)](https://vaughnvernon.com/)
  - [Value Objects (Martin Fowler)](https://martinfowler.com/bliki/ValueObject.html)
