---
id: yagni-principle
sidebar_position: 8
title: YAGNI Principle (You Aren't Gonna Need It)
description: No implementar funcionalidad hasta que sea realmente necesaria
---

# YAGNI Principle

## Contexto

Este estándar define **YAGNI** (You Aren't Gonna Need It): NO implementar funcionalidad especulativa "por si acaso". Implementar solo lo que se **necesita ahora**. Complementa el [lineamiento de Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md) evitando **sobreingeniería**.

---

## Conceptos Fundamentales

```yaml
# ✅ YAGNI = Implementar solo lo necesario ahora

Definición (Extreme Programming): "Always implement things when you actually need them, never when you just foresee that you need them."

Principio:
  ❌ "Vamos a necesitar autenticación multi-tenant en el futuro, implementémoslo ahora"
  ✅ "Solo un tenant por ahora, implementaremos multi-tenant cuando tengamos segundo cliente"

  ❌ "Este método podría necesitar 10 parámetros, agreguemos todos ahora"
  ✅ "Necesitamos 2 parámetros, agregamos solo esos"

Costos de violar YAGNI:
  - Código muerto (nadie usa, pero hay que mantener)
  - Complejidad innecesaria (dificulta entender)
  - Testing adicional (tests para código no usado)
  - Tiempo desperdiciado (features que nunca se usan)
  - Decisiones prematuras (arquitectura rígida)

Cuándo NO es YAGNI: ✅ Security (siempre implementar desde inicio)
  ✅ Observability (logs, metrics desde día 1)
  ✅ Testing (unit tests desde inicio)
  ✅ Extensibility en punto conocido (interfaces para dependency injection)
```

## Anti-Pattern: Implementación Especulativa

```csharp
// ❌ VIOLACIÓN YAGNI: Sobreingeniería anticipando futuro

public class OrderService
{
    // ❌ Strategy pattern "por si necesitamos múltiples estrategias"
    // Realidad: Solo una estrategia existe (DefaultOrderProcessor)
    private readonly IOrderProcessingStrategy _strategy;

    // ❌ Cache "por si tenemos alto tráfico"
    // Realidad: 10 requests/día actualmente
    private readonly IDistributedCache _cache;

    // ❌ Message queue "para escalabilidad futura"
    // Realidad: Procesamiento síncrono funciona bien ahora
    private readonly IRabbitMqPublisher _queue;

    // ❌ Feature flag system "para rollouts graduales"
    // Realidad: Deploy directo a producción funciona OK
    private readonly IFeatureFlags _featureFlags;

    public async Task<Guid> CreateOrderAsync(CreateOrderCommand command)
    {
        // ❌ 50 líneas de código para coordinar todos estos componentes
        // que NO se necesitan ahora

        if (await _featureFlags.IsEnabledAsync("NewOrderFlow"))  // ❌ Solo hay un flow
        {
            var cachedConfig = await _cache.GetAsync("order-config");  // ❌ Config no cambia
            var result = await _strategy.ProcessAsync(command);  // ❌ Solo una implementación
            await _queue.PublishAsync(new OrderCreated());  // ❌ Podría ser sync
            return result.OrderId;
        }

        // Legacy flow (que nadie usa)
        return Guid.Empty;
    }
}

// Problemas:
// 1. Complejidad innecesaria (50 líneas vs 10 necesarias)
// 2. 5 dependencies (solo 1 necesaria: IOrderRepository)
// 3. Tests complejos (mock 5 interfaces)
// 4. Mantenimiento costoso (actualizar código que no aporta valor)
```

## Pattern: YAGNI Correcto

```csharp
// ✅ APLICAR YAGNI: Solo lo necesario ahora

public class OrderService
{
    // ✅ Solo dependency realmente necesaria
    private readonly IOrderRepository _orderRepo;

    public OrderService(IOrderRepository orderRepo)
    {
        _orderRepo = orderRepo;
    }

    public async Task<Guid> CreateOrderAsync(CreateOrderCommand command)
    {
        // ✅ Simple y directo
        var order = Order.Create(command.CustomerId);

        foreach (var item in command.Items)
        {
            order.AddLine(item.ProductId, item.Quantity, item.UnitPrice);
        }

        await _orderRepo.SaveAsync(order);

        return order.OrderId;
    }
}

// Cuando REALMENTE necesitemos feature flags:
// 1. Agregar IFeatureFlags dependency
// 2. Wrap lógica específica
// 3. Implementar gradualmente
// Tiempo: 30 min cuando sea necesario

// Beneficios:
// ✅ 10 líneas (vs 50)
// ✅ 1 dependency (vs 5)
// ✅ Tests simples (1 mock vs 5)
// ✅ Fácil entender y mantener
```

## Cuándo Agregar Complejidad

```yaml
# ✅ Reglas para decidir si implementar ahora o después

Implementar AHORA si:
  ✅ Requisito actual confirmado por stakeholder
  ✅ Change cost crece significativamente después (ej: encryption)
  ✅ Parte de MVP definido
  ✅ Security, observability, testing básico

Implementar DESPUÉS si:
  ❌ "Podríamos necesitarlo en futuro"
  ❌ "Para ser flexible ante cambios hipotéticos"
  ❌ "Es buena práctica tenerlo"
  ❌ "Otro sistema lo tiene, nosotros también"

Ejemplos prácticos (Sales Service):

  ✅ AHORA: Single tenant (solo Perú)
  ❌ DESPUÉS: Multi-tenancy (cuando tengamos cliente 2: Colombia)

  ✅ AHORA: Órdenes en PostgreSQL (funciona para volumen actual)
  ❌ DESPUÉS: Event Sourcing (si necesitamos audit completo)

  ✅ AHORA: API REST con versionado
  ❌ DESPUÉS: gRPC (cuando identificamos bottleneck performance)

  ✅ AHORA: GitHub Actions CI/CD básico
  ❌ DESPUÉS: Blue-green deployments (cuando downtime sea problema)
```

## Refactoring cuando llegue el momento

```csharp
// ✅ Evolución gradual: Agregar complejidad solo cuando se necesita

// Fase 1 (MVP): Simple implementation
public class OrderService
{
    public async Task<Guid> CreateOrderAsync(CreateOrderCommand command)
    {
        var order = Order.Create(command.CustomerId);
        await _orderRepo.SaveAsync(order);
        return order.OrderId;
    }
}

// Fase 2 (6 meses después): Necesitamos validar stock
// Agregar IProductServiceClient (cuando realmente se necesita)
public class OrderService
{
    private readonly IOrderRepository _orderRepo;
    private readonly IProductServiceClient _productClient;  // ✅ Nuevo cuando necesario

    public async Task<Guid> CreateOrderAsync(CreateOrderCommand command)
    {
        // ✅ Validación ahora necesaria
        foreach (var item in command.Items)
        {
            var available = await _productClient.IsAvailableAsync(item.ProductId, item.Quantity);
            if (!available)
                throw new OutOfStockException();
        }

        var order = Order.Create(command.CustomerId);
        await _orderRepo.SaveAsync(order);
        return order.OrderId;
    }
}

// Fase 3 (1 año después): Necesitamos async processing (alto volumen)
// Agregar IEventPublisher (cuando realmente se necesita)
public class OrderService
{
    private readonly IOrderRepository _orderRepo;
    private readonly IProductServiceClient _productClient;
    private readonly IEventPublisher _eventPublisher;  // ✅ Nuevo cuando necesario

    public async Task<Guid> CreateOrderAsync(CreateOrderCommand command)
    {
        // Validaciones...

        var order = Order.Create(command.CustomerId);
        await _orderRepo.SaveAsync(order);

        // ✅ Async processing ahora necesario (volumen alto)
        await _eventPublisher.PublishAsync(new OrderCreated(order.OrderId));

        return order.OrderId;
    }
}

// Lección: Agregamos complejidad gradualmente cuando la necesitamos
// No anticipamos todo en Fase 1
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar solo funcionalidad con requisito actual confirmado
- **MUST** justificar cada dependency y abstracción agregada
- **MUST** eliminar código no usado (dead code) durante refactoring
- **MUST** priorizar simplicidad sobre "flexibilidad futura"

### SHOULD (Fuertemente recomendado)

- **SHOULD** hacer code review preguntando "¿realmente necesitamos esto ahora?"
- **SHOULD** documentar decisiones de posponer funcionalidad (ADR)
- **SHOULD** refactorizar cuando llegue requisito real (no anticipar)

### MUST NOT (Prohibido)

- **MUST NOT** agregar funcionalidad "por si acaso"
- **MUST NOT** crear abstracciones sin caso de uso concreto
- **MUST NOT** implementar features especulativas
- **MUST NOT** diseñar para requisitos hipotéticos

---

## Referencias

- [Lineamiento: Simplicidad Intencional](../../lineamientos/arquitectura/13-simplicidad-intencional.md)
- [KISS Principle](./kiss-principle.md)
- [Complexity Analysis](./complexity-analysis.md)
