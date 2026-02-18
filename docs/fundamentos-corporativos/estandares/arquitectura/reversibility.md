---
id: reversibility
sidebar_position: 7
title: Reversibility
description: Diseñar decisiones arquitectónicas que puedan reversirse con costo razonable
---

# Reversibility

## Contexto

Este estándar define **reversibility** (reversibilidad): decisiones arquitectónicas deben diseñarse para **revertirse** o **cambiarse** con esfuerzo razonable cuando contexto cambia. Complementa el [lineamiento de Arquitectura Evolutiva](../../lineamientos/arquitectura/12-arquitectura-evolutiva.md) evitando **lock-in** permanente.

---

## Conceptos Fundamentales

```yaml
# ✅ Reversibility = Capacidad de cambiar decisiones con costo razonable

Definición (Michael Nygard):
  "Make decisions reversible. Defer irreversible decisions as long as possible."

Tipos de Decisiones:
  Reversibles (preferibles):
    ✅ Elección de database (PostgreSQL → MongoDB: 2-3 días)
    ✅ Messaging system (Kafka → RabbitMQ: 1-2 días)
    ✅ Framework web (ASP.NET → FastAPI: 1-2 semanas)
    ✅ Cloud provider (AWS → Azure: 1-2 meses)

  Costosas de revertir (evitar o documentar):
    ⚠️ Arquitectura distribuida → monolito (meses)
    ⚠️ Modelo de datos SQL → NoSQL con data migration (semanas)
    ⚠️ Lenguaje de programación (C# → Go: reescritura completa)

Estrategias para Reversibilidad:
  1. Abstracciones: Interfaces desacoplan de implementación
  2. Strangler Fig: Migra gradualmente (coexiste viejo y nuevo)
  3. Feature Flags: Activa/desactiva sin redeploy
  4. Branch by Abstraction: Cambia dependency sin big bang
  5. Principio de menor compromiso: Elige opción menos restrictiva

Cost of Change (criterio para evaluar decisiones):
  - Bajo: 1-2 días (reversible fácilmente)
  - Medio: 1-2 semanas (reversible con esfuerzo)
  - Alto: >1 mes (difícil de revertir, documentar cuidadosamente)
```

## Decisión Reversible: Elección de Database

```yaml
# ✅ DECISIÓN: PostgreSQL como base de datos

Context:
  Sales Service necesita persistencia relacional.
  Opciones: PostgreSQL, MySQL, SQL Server

Decision:
  Usar PostgreSQL debido a:
    - Open source (sin licensing costs)
    - Rich queries (JSON, full-text search)
    - AWS RDS support

Reversibility Analysis:
  Costo de cambio: Bajo-Medio (1-2 días)

  Estrategia de reversibilidad:
    1. ✅ Aislar en Infrastructure layer (IOrderRepository)
    2. ✅ No usar features PostgreSQL-specific en queries (evitar )
    3. ✅ Migrations vendor-agnostic (FluentMigrator compatible)

  Pasos para cambiar a MySQL:
    - Crear MySqlOrderRepository implementando IOrderRepository
    - Cambiar DI: services.AddScoped<IOrderRepository, MySqlOrderRepository>()
    - Ajustar connection string
    - Run tests
    Time: 1-2 días

  Pasos para cambiar a MongoDB:
    - Crear MongoOrderRepository implementando IOrderRepository
    - Mapear Order entity a document
    - Migration scripts (SQL → NoSQL)
    - Run tests
    Time: 3-5 días

Status: ✅ Decisión reversible con bajo costo
```

## Implementación: Database Abstraction

```csharp
// ✅ Abstracción permite cambiar database fácilmente

// Application define abstracción (framework-agnostic)
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(Guid orderId);
    Task<List<Order>> GetByCustomerAsync(Guid customerId, int limit = 100);
    Task SaveAsync(Order order);
}

// Infrastructure: PostgreSQL implementation
public class PostgreSqlOrderRepository : IOrderRepository
{
    private readonly NpgsqlConnection _connection;

    public async Task<Order?> GetByIdAsync(Guid orderId)
    {
        const string sql = @"
            SELECT * FROM sales.orders WHERE order_id = @orderId;
            SELECT * FROM sales.order_lines WHERE order_id = @orderId;
        ";
        // Dapper implementation...
    }

    public async Task SaveAsync(Order order)
    {
        // PostgreSQL-specific upsert
        const string sql = @"
            INSERT INTO sales.orders (order_id, customer_id, status, order_date)
            VALUES (@OrderId, @CustomerId, @Status, @OrderDate)
            ON CONFLICT (order_id) DO UPDATE SET status = EXCLUDED.status;
        ";
        await _connection.ExecuteAsync(sql, order);
    }
}

// Infrastructure: MongoDB implementation (alternative)
public class MongoOrderRepository : IOrderRepository
{
    private readonly IMongoCollection<OrderDocument> _collection;

    public async Task<Order?> GetByIdAsync(Guid orderId)
    {
        var doc = await _collection.Find(d => d.OrderId == orderId).FirstOrDefaultAsync();
        return doc?.ToEntity();
    }

    public async Task SaveAsync(Order order)
    {
        var doc = OrderDocument.FromEntity(order);
        await _collection.ReplaceOneAsync(
            d => d.OrderId == order.OrderId,
            doc,
            new ReplaceOptions { IsUpsert = true }
        );
    }
}

// Cambiar de PostgreSQL a MongoDB: Solo cambiar DI
// ANTES: services.AddScoped<IOrderRepository, PostgreSqlOrderRepository>();
// DESPUÉS: services.AddScoped<IOrderRepository, MongoOrderRepository>();
// Application layer NO cambia
```

## Feature Flags para Reversibilidad

```csharp
// ✅ Feature Flags permiten revertir features sin redeploy

public class CreateOrderHandler
{
    private readonly IOrderRepository _orderRepo;
    private readonly IFeatureFlags _featureFlags;
    private readonly IOrderPricingService _newPricingService;  // Nueva implementación
    private readonly LegacyPricingService _legacyPricingService;  // Legacy

    public async Task<Guid> ExecuteAsync(CreateOrderCommand command)
    {
        var order = Order.Create(command.CustomerId);

        // ✅ Feature flag controla qué implementación usar
        if (await _featureFlags.IsEnabledAsync("NewPricingEngine", command.CustomerId))
        {
            // ✅ Nuevo algoritmo (gradualmente habilitar: 10%→50%→100%)
            var pricing = await _newPricingService.CalculatePricingAsync(order);
            order.ApplyPricing(pricing);
        }
        else
        {
            // ✅ Legacy (mantener hasta 100% migrado)
            var pricing = _legacyPricingService.CalculatePricing(order);
            order.ApplyPricing(pricing);
        }

        await _orderRepo.SaveAsync(order);
        return order.OrderId;
    }
}

// Si nuevo pricing tiene bugs: Desactivar flag (sin redeploy)
// Reversión: Segundos (cambiar flag en LaunchDarkly/ConfigCat)
```

## Strangler Fig Pattern (migración reversible)

```csharp
// ✅ Strangler Fig: Coexisten viejo y nuevo, migra gradualmente

// Facade route requests a viejo o nuevo
public class OrderFacade
{
    private readonly LegacyOrderService _legacyService;
    private readonly ModernOrderService _modernService;
    private readonly IFeatureFlags _featureFlags;

    public async Task CreateOrderAsync(CreateOrderCommand command)
    {
        // ✅ Porcentaje de tráfico a nueva implementación
        if (await _featureFlags.IsEnabledAsync("ModernOrderService", command.CustomerId))
        {
            await _modernService.CreateOrderAsync(command);  // ✅ Nueva
        }
        else
        {
            _legacyService.CreateOrder(command);  // ❌ Legacy
        }
    }
}

// Migración gradual:
// Week 1: 10% traffic → moderna (monitor metrics)
// Week 2: 50% traffic → moderna (validate results)
// Week 3: 100% traffic → moderna
// Week 4: Remove legacy

// Si hay problemas: Revertir porcentaje a 0% (segundos)
// Reversibilidad: Alta (coexisten ambas implementaciones)
```

## ADR: Documentar Reversibilidad

````markdown
# ADR-015: Use Kafka for Event Streaming

## Status

Accepted

## Context

Need event-driven communication between services for loose coupling.
Options: Kafka, RabbitMQ, AWS SNS/SQS

## Decision

Use Apache Kafka debido a:

- High throughput (millions msgs/sec)
- Event replay capability
- Strong ecosystem (Confluent, Schema Registry)

## Reversibility Analysis

### Cost of Change: Medium (1-2 días)

### Abstraction Strategy:

```csharp
// Define abstraction (not Kafka-specific)
public interface IEventPublisher
{
    Task PublishAsync<T>(T domainEvent) where T : DomainEvent;
}

// Kafka implementation
public class KafkaEventPublisher : IEventPublisher { ... }

// Alternative: RabbitMQ implementation (if needed)
public class RabbitMqEventPublisher : IEventPublisher { ... }
```
````

### Migration Path (if reverting to RabbitMQ):

1. Implement RabbitMqEventPublisher (1 día)
2. Change DI registration (5 min)
3. Deploy consumers to listen to RabbitMQ (1 día)
4. Run both in parallel 24h (validation)
5. Deprecate Kafka

### Risk Mitigation:

- Keep events in both systems during migration
- Use feature flags to control routing
- Monitor lag and delivery guarantees

## Status

✅ Reversible with medium effort (1-2 días)

```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar abstracciones (interfaces) para dependencies técnicas
- **MUST** documentar costo de reversión en ADRs (bajo/medio/alto)
- **MUST** usar feature flags para cambios de alto impacto
- **MUST** mantener opciones abiertas (no lock-in vendor cuando posible)
- **MUST** validar que decisiones críticas son reversibles antes de implementar

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Strangler Fig para migraciones grandes
- **SHOULD** coexistir viejo y nuevo durante migración (paralelo)
- **SHOULD** implementar circuit breakers/fallbacks para nuevas integraciones
- **SHOULD** preferir decisiones con bajo costo de cambio

### MAY (Opcional)

- **MAY** crear POCs antes de decisiones costosas de revertir
- **MAY** usar multi-cloud para evitar vendor lock-in

### MUST NOT (Prohibido)

- **MUST NOT** hacer decisiones irreversibles sin documentar (ADR)
- **MUST NOT** acoplar directamente a vendor-specific APIs
- **MUST NOT** ignorar costo de reversión en architecture decisions
- **MUST NOT** hacer big bang migrations (usar gradual con reversión)

---

## Referencias

- [Lineamiento: Arquitectura Evolutiva](../../lineamientos/arquitectura/12-arquitectura-evolutiva.md)
- [Architecture Decision Records](../../documentacion/architecture-decision-records.md)
- [Loose Coupling](./loose-coupling.md)
- [Feature Flags](../../desarrollo/feature-flags.md)
```
