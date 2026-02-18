---
id: event-design
sidebar_position: 9
title: Diseño de Eventos
description: Diseñar eventos como hechos inmutables del dominio con semántica de negocio clara
---

# Diseño de Eventos

## Contexto

Este estándar define cómo diseñar eventos como hechos inmutables del dominio. Complementa el [lineamiento de Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md) especificando **cómo** diseñar eventos con semántica de negocio clara, orientados a hechos pasados, e inmutables.

---

## Stack Tecnológico

| Componente         | Tecnología       | Versión | Uso                               |
| ------------------ | ---------------- | ------- | --------------------------------- |
| **Lenguaje**       | C# (.NET 8)      | 8.0+    | Definición de eventos con records |
| **Serialización**  | System.Text.Json | 8.0+    | JSON serialization                |
| **Especificación** | AsyncAPI         | 3.0+    | Documentación de contratos        |
| **Versionamiento** | GitHub           | -       | Control de versiones              |

### Dependencias NuGet

```xml
<PackageReference Include="System.Text.Json" Version="8.0.0" />
```

---

## Implementación Técnica

### Principios de Diseño de Eventos

#### 1. Eventos son Hechos Pasados (Past Tense)

Los eventos representan algo que **ya ocurrió**, no comandos de lo que **debería ocurrir**.

```csharp
// ✅ CORRECTO: Hecho pasado
public record OrderCreatedEvent(
    Guid OrderId,
    Guid CustomerId,
    decimal TotalAmount,
    DateTime CreatedAt
);

public record PaymentProcessedEvent(
    Guid PaymentId,
    Guid OrderId,
    decimal Amount,
    string PaymentMethod,
    DateTime ProcessedAt
);

// ❌ INCORRECTO: Comando imperativo
public record CreateOrderCommand(  // Esto NO es un evento
    Guid CustomerId,
    List<OrderItem> Items
);

public record ProcessPaymentCommand(  // Esto NO es un evento
    Guid OrderId,
    decimal Amount
);
```

#### 2. Eventos son Inmutables

Una vez creados, los eventos **nunca cambian**. Son parte del historial inmutable del sistema.

```csharp
// ✅ CORRECTO: Record inmutable
public record CustomerAddressChangedEvent(
    Guid CustomerId,
    string PreviousAddress,  // Captura el estado anterior
    string NewAddress,        // Captura el estado nuevo
    DateTime ChangedAt
);

// ✅ CORRECTO: Init-only properties
public record OrderShippedEvent
{
    public Guid OrderId { get; init; }
    public string TrackingNumber { get; init; } = null!;
    public DateTime ShippedAt { get; init; }

    // No hay setters, solo getters e init
}

// ❌ INCORRECTO: Mutable con setters
public class OrderUpdatedEvent
{
    public Guid OrderId { get; set; }  // ❌ set permite mutación
    public string Status { get; set; } = null!;
}
```

#### 3. Eventos son Ricos en Información de Negocio

Los eventos deben contener **toda la información** que los consumidores necesitan sin requerir queries adicionales.

```csharp
// ✅ CORRECTO: Rico en información
public record OrderCreatedEvent(
    Guid EventId,
    DateTime Timestamp,
    Guid OrderId,
    Guid CustomerId,
    string CustomerEmail,        // ← Incluido para notificaciones
    string CustomerName,         // ← Incluido para personalización
    decimal TotalAmount,
    string Currency,
    List<OrderItem> Items,       // ← Items completos, no solo IDs
    ShippingAddress ShippingAddress,  // ← Dirección completa
    string PaymentMethod,
    DateTime CreatedAt
);

public record OrderItem(
    string ProductId,
    string ProductName,  // ← Nombre incluido
    int Quantity,
    decimal UnitPrice,
    decimal Discount
);

// ❌ INCORRECTO: Pobre en información (requiere queries)
public record OrderCreatedEventPoor(
    Guid OrderId,
    Guid CustomerId,  // ← Solo ID, consumidores deben hacer GET /customers/{id}
    List<string> ProductIds  // ← Solo IDs, consumidores deben hacer GET /products/{id}
);
```

#### 4. Eventos usan Lenguaje del Dominio (Ubiquitous Language)

Los nombres y campos deben reflejar el vocabulario del negocio, no detalles técnicos.

```csharp
// ✅ CORRECTO: Lenguaje de negocio
public record LoanApprovedEvent(
    Guid LoanApplicationId,
    decimal ApprovedAmount,
    decimal InterestRate,
    int TermInMonths,
    DateTime ApprovedAt,
    string ApprovedBy
);

public record PatientAdmittedEvent(
    Guid PatientId,
    string PatientName,
    Guid DoctorId,
    string DoctorName,
    string Department,
    DateTime AdmissionDate,
    string AdmissionReason
);

// ❌ INCORRECTO: Lenguaje técnico
public record RecordInsertedEvent(  // ← Lenguaje DB, no negocio
    int TableId,
    Dictionary<string, object> Columns
);

public record EntityStateChangedEvent(  // ← Demasiado genérico
    string EntityType,
    Guid EntityId,
    string OldState,
    string NewState
);
```

### Estructura Estándar de Eventos

```csharp
// Envelope genérico para todos los eventos
public record EventEnvelope<TPayload>(
    Guid EventId,           // Identificador único (idempotencia)
    string EventType,       // Tipo del evento
    DateTime Timestamp,     // Timestamp UTC del evento
    Guid CorrelationId,     // ID de correlación para trazabilidad
    string ServiceName,     // Servicio que emitió el evento
    string Version,         // Versión del contrato (semver)
    TPayload Payload        // Payload específico del evento
) where TPayload : notnull;

// Payload específico del dominio
public record OrderCreatedPayload(
    Guid OrderId,
    Guid CustomerId,
    string CustomerEmail,
    decimal TotalAmount,
    string Currency,
    List<OrderItem> Items,
    DateTime CreatedAt
);

// Evento completo
public record OrderCreatedEvent
    : EventEnvelope<OrderCreatedPayload>;
```

### Granularidad de Eventos

#### Eventos Granulares vs Agregados

```csharp
// ✅ CORRECTO: Evento granular con semántica clara
public record OrderStatusChangedEvent(
    Guid OrderId,
    OrderStatus PreviousStatus,
    OrderStatus NewStatus,
    string Reason,
    DateTime ChangedAt
);

public record OrderItemAddedEvent(
    Guid OrderId,
    OrderItem AddedItem,
    decimal NewTotal,
    DateTime AddedAt
);

// ⚠️ USAR CON CUIDADO: Evento muy granular
// Solo si múltiples consumidores necesitan reaccionar a cambios individuales
public record OrderItemQuantityChangedEvent(
    Guid OrderId,
    string ProductId,
    int OldQuantity,
    int NewQuantity,
    decimal NewLineTotal,
    DateTime ChangedAt
);

// ✅ CORRECTO: Evento agregado para operaciones atómicas
public record OrderPlacedEvent(  // Múltiples cosas ocurren atómicamente
    Guid OrderId,
    Guid CustomerId,
    decimal TotalAmount,
    List<OrderItem> Items,
    ShippingAddress ShippingAddress,
    PaymentDetails PaymentDetails,
    DateTime PlacedAt
);

// ❌ INCORRECTO: Muy genérico, pierde semántica
public record OrderUpdatedEvent(
    Guid OrderId,
    Dictionary<string, object> Changes  // ❌ No tipado, semántica perdida
);
```

### Naming Conventions

```csharp
// Patrón: {Agregado}{AcciónPasado}Event

// ✅ CORRECTO
public record OrderCreatedEvent(...);
public record OrderCancelledEvent(...);
public record OrderShippedEvent(...);
public record PaymentProcessedEvent(...);
public record InvoiceGeneratedEvent(...);
public record CustomerRegisteredEvent(...);
public record ProductRestockedEvent(...);

// ❌ INCORRECTO
public record CreateOrderEvent(...);      // ❌ Imperativo, no pasado
public record OrderEvent(...);            // ❌ Muy genérico
public record Order_Created_Event(...);   // ❌ Snake case
public record orderCreated(...);          // ❌ Minúscula inicial
public record OrderEventCreated(...);     // ❌ Orden incorrecto
```

### Versionamiento de Eventos

```csharp
// v1.0.0 - Versión inicial
public record OrderCreatedEventV1(
    Guid OrderId,
    Guid CustomerId,
    decimal TotalAmount
);

// v2.0.0 - Breaking change (campo requerido nuevo)
public record OrderCreatedEventV2(
    Guid OrderId,
    Guid CustomerId,
    decimal TotalAmount,
    string Currency  // ← Campo nuevo REQUERIDO
);

// Estrategia: Mantener ambas versiones durante período de migración
public class OrderEventPublisher
{
    public async Task PublishOrderCreatedAsync(Order order)
    {
        // Publicar v2 (nueva versión)
        await PublishAsync("order.ordercreated.v2", new OrderCreatedEventV2(
            order.Id,
            order.CustomerId,
            order.TotalAmount,
            order.Currency
        ));

        // Publicar v1 (compatibilidad temporal)
        await PublishAsync("order.ordercreated.v1", new OrderCreatedEventV1(
            order.Id,
            order.CustomerId,
            order.TotalAmount
        ));
    }
}
```

### Eventos de Cambio de Estado vs Eventos de Dominio

```csharp
// Evento de cambio de estado técnico
public record OrderStatusChangedEvent(
    Guid OrderId,
    OrderStatus From,
    OrderStatus To,
    DateTime ChangedAt
);

// ✅ MEJOR: Eventos específicos de dominio con semántica rica
public record OrderConfirmedEvent(
    Guid OrderId,
    Guid CustomerId,
    decimal ConfirmedAmount,
    DateTime ConfirmedAt,
    string ConfirmedBy
);

public record OrderShippedEvent(
    Guid OrderId,
    string TrackingNumber,
    string Carrier,
    DateTime ShippedAt,
    ShippingAddress Destination
);

public record OrderDeliveredEvent(
    Guid OrderId,
    DateTime DeliveredAt,
    string ReceivedBy,
    string SignatureUrl
);

// Cada evento tiene semántica específica vs genérico "StatusChanged"
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** nombrar eventos en pasado ("OrderCreated", no "CreateOrder")
- **MUST** usar records inmutables (C#) o equivalente inmutable
- **MUST** incluir metadata: `eventId`, `eventType`, `timestamp`, `correlationId`, `version`
- **MUST** usar lenguaje del dominio (Ubiquitous Language) en nombres
- **MUST** incluir suficiente información para evitar queries adicionales
- **MUST** versionar eventos cuando cambian (incrementar `version` en envelope)
- **MUST** especificar tipos de datos precisos (evitar `object` o `Dictionary<string, object>`)
- **MUST** documentar eventos en AsyncAPI
- **MUST** incluir timestamp UTC en todos los eventos

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar eventos granulares con semántica clara (no "EntityUpdated" genérico)
- **SHOULD** incluir estados anteriores en eventos de cambio ("PreviousStatus", "NewStatus")
- **SHOULD** usar PascalCase para nombres de eventos
- **SHOULD** agrupar eventos relacionados por agregado/dominio
- **SHOULD** incluir información del actor (`CreatedBy`, `ApprovedBy`)
- **SHOULD** capturar razones de cambios importantes (`Reason`, `CancellationReason`)

### MUST NOT (Prohibido)

- **MUST NOT** usar nombres imperativos ("CreateOrder", "UpdateCustomer")
- **MUST NOT** hacer eventos mutables (usar classes con setters)
- **MUST NOT** usar `Dictionary<string, object>` para payloads (pierde tipado)
- **MUST NOT** incluir lógica de negocio en eventos (son DTOs)
- **MUST NOT** cambiar estructura de eventos existentes sin nueva versión

---

## Anti-Patrones

### ❌ #1: Eventos Anémicos

```csharp
// ❌ INCORRECTO: Solo IDs, consumidores deben hacer queries
public record OrderCreatedEvent(
    Guid OrderId,
    Guid CustomerId
);

// ✅ CORRECTO: Rico en información
public record OrderCreatedEvent(
    Guid OrderId,
    Guid CustomerId,
    string CustomerEmail,
    string CustomerName,
    decimal TotalAmount,
    string Currency,
    List<OrderItem> Items,
    DateTime CreatedAt
);
```

### ❌ #2: Eventos Genéricos

```csharp
// ❌ INCORRECTO: Pierde semántica de negocio
public record EntityUpdatedEvent(
    string EntityType,
    Guid EntityId,
    Dictionary<string, object> Changes
);

// ✅ CORRECTO: Específico y tipado
public record CustomerEmailChangedEvent(
    Guid CustomerId,
    string PreviousEmail,
    string NewEmail,
    DateTime ChangedAt,
    string ChangedBy
);
```

### ❌ #3: Eventos Comandos Disfrazados

```csharp
// ❌ INCORRECTO: Es un comando, no un evento
public record CreateInvoiceEvent(
    Guid OrderId,
    decimal Amount
);

// ✅ CORRECTO: Evento pasado
public record InvoiceCreatedEvent(
    Guid InvoiceId,
    Guid OrderId,
    string InvoiceNumber,
    decimal Amount,
    DateTime CreatedAt
);
```

### ❌ #4: Eventos Mutables

```csharp
// ❌ INCORRECTO: Mutable, puede cambiar después de creación
public class ProductPriceChangedEvent
{
    public Guid ProductId { get; set; }
    public decimal NewPrice { get; set; }
    public DateTime ChangedAt { get; set; }
}

// ✅ CORRECTO: Inmutable con records
public record ProductPriceChangedEvent(
    Guid ProductId,
    decimal OldPrice,
    decimal NewPrice,
    DateTime ChangedAt
);
```

---

## Referencias

- [Lineamiento: Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/08-comunicacion-asincrona-y-eventos.md)
- Estándares relacionados:
  - [Mensajería Asíncrona](async-messaging.md)
  - [Contratos de Eventos](../apis/event-contracts.md)
  - [Idempotencia](idempotency.md)
- Patrones externos:
  - [Domain-Driven Design Events](https://martinfowler.com/eaaDev/DomainEvent.html)
  - [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
