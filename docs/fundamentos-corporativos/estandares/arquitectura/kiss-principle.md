---
id: kiss-principle
sidebar_position: 9
title: KISS Principle (Keep It Simple, Stupid)
description: Mantener soluciones simples y directas evitando complejidad innecesaria
---

# KISS Principle

## Contexto

Este estándar define **KISS** (Keep It Simple, Stupid): elegir solución **más simple** que resuelva el problema. Complejidad debe ser último recurso. Complementa el [lineamiento de Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md) priorizando **claridad sobre cleverness**.

---

## Conceptos

```yaml
# ✅ KISS = Solución simple > Solución compleja

Definición: "Most systems work best if they are kept simple rather than made complex."

Aplicación: ❌ Usar microservices para app con 100 usuarios/día
  ✅ Usar monolito modular (más simple, suficiente)

  ❌ Implementar CQRS + Event Sourcing para CRUD simple
  ✅ Usar repository pattern tradicional

  ❌ Crear abstracción con 5 niveles de indirección
  ✅ Implementación directa y clara

Indicadores de complejidad innecesaria:
  - "Necesitas leer 10 archivos para entender flujo"
  - "Solo Juan sabe cómo funciona este componente"
  - "Tardamos 2 semanas en agregar campo simple"
  - "Tests requieren 50 líneas de setup"

Beneficios de simplicidad: ✅ Fácil entender (onboarding rápido)
  ✅ Fácil modificar (low change cost)
  ✅ Menos bugs (menos superficie de error)
  ✅ Más operatable (fácil debuggear)
```

## Ejemplos: Simple vs Complejo

```csharp
// ❌ COMPLEJO: Over-engineered con patrones innecesarios

public interface IOrderFactory
{
    IOrder CreateOrder(IOrderSpecification spec);
}

public class OrderFactoryProvider
{
    private readonly IServiceProvider _serviceProvider;

    public IOrderFactory GetFactory(string type)
    {
        return type switch
        {
            "Standard" => _serviceProvider.GetService<StandardOrderFactory>(),
            "Premium" => _serviceProvider.GetService<PremiumOrderFactory>(),
            _ => throw new NotSupportedException()
        };
    }
}

public class OrderCreationCoordinator
{
    private readonly OrderFactoryProvider _factoryProvider;
    private readonly IOrderValidator _validator;
    private readonly IOrderPersistence _persistence;

    public async Task<IOrder> CoordinateOrderCreationAsync(OrderCreationContext context)
    {
        var factory = _factoryProvider.GetFactory(context.OrderType);
        var order = factory.CreateOrder(context.Specification);
        await _validator.ValidateAsync(order);
        await _persistence.SaveAsync(order);
        return order;
    }
}

// Problemas:
// - 4 interfaces para crear orden
// - 3 clases intermedias
// - Difícil seguir flujo
// - Complejidad sin beneficio claro

// ✅ SIMPLE: Directo y claro

public class OrderService
{
    private readonly IOrderRepository _orderRepo;

    public async Task<Guid> CreateOrderAsync(CreateOrderCommand command)
    {
        // ✅ Validación inline (simple)
        if (command.Items.Count == 0)
            throw new ValidationException("Order must have items");

        // ✅ Creación directa
        var order = Order.Create(command.CustomerId);

        foreach (var item in command.Items)
        {
            order.AddLine(item.ProductId, item.Quantity, item.UnitPrice);
        }

        // ✅ Persistencia simple
        await _orderRepo.SaveAsync(order);

        return order.OrderId;
    }
}

// Beneficios:
// ✅ 15 líneas vs 50+
// ✅ 1 clase vs 4 interfaces + 3 clases
// ✅ Flujo obvio al leer
// ✅ Fácil testear
// ✅ Fácil modificar
```

```csharp
// ❌ COMPLEJO: Abstracción prematura

public interface IQueryHandler<TQuery, TResult>
{
    Task<TResult> HandleAsync(TQuery query);
}

public interface IQueryBus
{
    Task<TResult> ExecuteAsync<TQuery, TResult>(TQuery query);
}

public class QueryBusMediator : IQueryBus
{
    private readonly IServiceProvider _serviceProvider;

    public async Task<TResult> ExecuteAsync<TQuery, TResult>(TQuery query)
    {
        var handlerType = typeof(IQueryHandler<,>).MakeGenericType(typeof(TQuery), typeof(TResult));
        var handler = _serviceProvider.GetService(handlerType);
        var method = handlerType.GetMethod("HandleAsync");
        return await (Task<TResult>)method.Invoke(handler, new object[] { query });
    }
}

// Uso:
var query = new GetOrderByIdQuery(orderId);
var order = await _queryBus.ExecuteAsync<GetOrderByIdQuery, OrderDto>(query);

// Problemas:
// - Reflection (performance, debugging difícil)
// - Indirección innecesaria
// - ¿Para qué? Solo tenemos 5 queries

// ✅ SIMPLE: Inyección directa

public class OrderQueryService
{
    private readonly IOrderRepository _orderRepo;

    public async Task<OrderDto?> GetByIdAsync(Guid orderId)
    {
        var order = await _orderRepo.GetByIdAsync(orderId);
        return order != null ? OrderDto.FromEntity(order) : null;
    }

    public async Task<List<OrderDto>> GetByCustomerAsync(Guid customerId)
    {
        var orders = await _orderRepo.GetByCustomerAsync(customerId);
        return orders.Select(OrderDto.FromEntity).ToList();
    }
}

// Uso:
var order = await _orderQueryService.GetByIdAsync(orderId);

// Beneficios:
// ✅ Sin reflection
// ✅ Type-safe
// ✅ Obvio cómo funciona
// ✅ Fácil debuggear
```

## Arquitectura: Simple vs Complejo

```yaml
# ❌ COMPLEJO: Microservices prematuros

Sales System (100 usuarios, 500 órdenes/día):
  - API Gateway (Kong)
  - Service Mesh (Istio)
  - 15 microservices:
      - customer-service
      - order-service
      - order-line-service  # ❌ Demasiado granular
      - product-service
      - inventory-service
      - pricing-service
      - discount-service  # ❌ Podría ser library
      - tax-service
      - shipping-service
      - payment-service
      - notification-service
      - audit-service
      - reporting-service
      - analytics-service
      - admin-service
  - Kafka cluster (3 brokers)
  - Redis cluster (3 nodes)
  - PostgreSQL per service (15 databases)
  - Kubernetes (10 nodes)
  - Observability stack (Prometheus, Grafana, Jaeger, ELK)

Problemas:
  - Overkill para volumen
  - 15 repos, 15 pipelines
  - Latencia: 5 hops para crear orden
  - Debugging: traces entre 8 servicios
  - Costo: $5000/mes (infrastructure)
  - Team: 10 devs solo para mantener

# ✅ SIMPLE: Monolito modular

Sales System (mismo volumen):
  - Single application (Talma.Sales.Api)
  - Módulos internos bien definidos:
      - Sales Module (orders, customers)
      - Catalog Module (products, inventory)
      - Billing Module (invoices, payments)
      - Notifications Module
  - PostgreSQL (single database, schemas separados)
  - Redis (single node, suficiente)
  - ECS Fargate (2 tasks)
  - CloudWatch (logs, metrics)

Beneficios:
  ✅ 1 repo, 1 pipeline
  ✅ Latencia: in-process calls (<1ms)
  ✅ Debugging: single stack trace
  ✅ Costo: $200/mes
  ✅ Team: 3 devs

Cuando migrar a microservices:
  - Volumen > 10,000 órdenes/día
  - Equipos independientes necesarios
  - Diferentes escalability requirements
  - Clear bounded contexts
```

## Métricas de Simplicidad

```yaml
# ✅ Indicadores objetivos

Cyclomatic Complexity:
  ✅ Simple: < 10 por método
  ⚠️ Moderado: 10-20
  ❌ Complejo: > 20

Lines of Code:
  ✅ Simple: < 20 líneas por método
  ⚠️ Moderado: 20-50
  ❌ Complejo: > 50

Dependencies:
  ✅ Simple: < 5 por clase
  ⚠️ Moderado: 5-10
  ❌ Complejo: > 10

Depth of Inheritance:
  ✅ Simple: < 3 niveles
  ⚠️ Moderado: 3-5
  ❌ Complejo: > 5

Test Setup:
  ✅ Simple: < 10 líneas
  ⚠️ Moderado: 10-20
  ❌ Complejo: > 20
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** elegir solución más simple que cumpla requisito
- **MUST** justificar complejidad agregada (ADR)
- **MUST** mantener métodos < 20 líneas cuando posible
- **MUST** limitar dependencies < 5 por clase

### SHOULD (Fuertemente recomendado)

- **SHOULD** refactorizar cuando complejidad crece sin justificación
- **SHOULD** hacer code review cuestionando complejidad
- **SHOULD** preferir claridad sobre cleverness

### MUST NOT (Prohibido)

- **MUST NOT** agregar patrones sofisticados sin caso de uso claro
- **MUST NOT** usar reflection cuando alternativa simple existe
- **MUST NOT** crear abstracciones "por si acaso"
- **MUST NOT** optimizar prematuramente

---

## Referencias

- [Lineamiento: Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md)
- [YAGNI Principle](./yagni-principle.md)
- [Complexity Analysis](./complexity-analysis.md)
