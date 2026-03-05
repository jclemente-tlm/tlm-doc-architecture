---
id: cqrs
sidebar_position: 4
title: CQRS
description: Separación de commands y queries mediante handlers propios sin frameworks externos.
tags: [arquitectura, cqrs, commands, queries, handlers]
---

# CQRS

## Contexto

Este estándar define la implementación de Command Query Responsibility Segregation (CQRS) en servicios Talma. Complementa los lineamientos [Modelado de Dominio](../../lineamientos/arquitectura/09-modelado-de-dominio.md) y [Consistencia y Sincronización](../../lineamientos/datos/02-consistencia-y-sincronizacion.md).

**Conceptos incluidos:**

- **CQRS Pattern** → Separación de operaciones de escritura (commands) y lectura (queries)

---

## Stack Tecnológico

| Componente    | Tecnología   | Versión | Uso                       |
| ------------- | ------------ | ------- | ------------------------- |
| **Framework** | ASP.NET Core | 8.0+    | APIs con CQRS             |
| **ORM**       | EF Core      | 8.0+    | Write model y projections |

---

## CQRS Pattern

### ¿Qué es CQRS?

Patrón que separa operaciones de escritura (commands) de lectura (queries), permitiendo optimizar cada lado independientemente.

**Propósito:** Escalar lecturas/escrituras independientemente, modelos optimizados por caso de uso.

**Niveles:**

- **Simple**: Handlers separados, misma DB
- **Intermedio**: DBs separadas (write/read), sincronización vía eventos
- **Completo**: Event Sourcing + projections

**Beneficios:**
✅ Escalamiento independiente
✅ Modelos optimizados
✅ Mejor performance de queries

### Ejemplo

```csharp
// Interfaces genéricas propias (sin MediatR)
public interface ICommandHandler<TCommand, TResult>
{
    Task<TResult> HandleAsync(TCommand command, CancellationToken ct = default);
}

public interface IQueryHandler<TQuery, TResult>
{
    Task<TResult> HandleAsync(TQuery query, CancellationToken ct = default);
}

// Command: Intención de cambiar estado
public record CreateOrderCommand(
    Guid CustomerId,
    List<OrderLineDto> Lines);

// Command Handler: Lógica de negocio
public class CreateOrderCommandHandler : ICommandHandler<CreateOrderCommand, Result<Guid>>
{
    private readonly IOrderRepository _repository;
    private readonly IEventBus _eventBus;

    public CreateOrderCommandHandler(IOrderRepository repository, IEventBus eventBus)
    {
        _repository = repository;
        _eventBus = eventBus;
    }

    public async Task<Result<Guid>> HandleAsync(CreateOrderCommand command, CancellationToken ct = default)
    {
        var order = Order.Create(command.CustomerId);

        foreach (var line in command.Lines)
        {
            order.AddLine(line.ProductId, line.Quantity, line.UnitPrice);
        }

        await _repository.SaveAsync(order);

        // Publicar domain event
        await _eventBus.PublishAsync(new OrderCreatedEvent(order.Id, order.CustomerId));

        return Result.Success(order.Id);
    }
}

// Query: Solo lectura, sin lógica de negocio
public record GetOrderByIdQuery(Guid OrderId);

// Query Handler: Lectura optimizada
public class GetOrderByIdQueryHandler : IQueryHandler<GetOrderByIdQuery, OrderDto?>
{
    private readonly IReadDbContext _readDb; // Read-optimized DB

    public GetOrderByIdQueryHandler(IReadDbContext readDb) => _readDb = readDb;

    public async Task<OrderDto?> HandleAsync(GetOrderByIdQuery query, CancellationToken ct = default)
    {
        return await _readDb.Orders
            .Where(o => o.Id == query.OrderId)
            .Select(o => new OrderDto
            {
                Id = o.Id,
                CustomerName = o.CustomerName,
                Total = o.Total,
                Status = o.Status,
                Lines = o.Lines.Select(l => new OrderLineDto
                {
                    ProductName = l.ProductName,
                    Quantity = l.Quantity,
                    Subtotal = l.Subtotal
                }).ToList()
            })
            .FirstOrDefaultAsync(ct);
    }
}

// Controller inyecta handlers directamente via DI
[ApiController]
[Route("api/v1/orders")]
public class OrdersController : ControllerBase
{
    private readonly ICommandHandler<CreateOrderCommand, Result<Guid>> _createHandler;
    private readonly IQueryHandler<GetOrderByIdQuery, OrderDto?> _getByIdHandler;

    public OrdersController(
        ICommandHandler<CreateOrderCommand, Result<Guid>> createHandler,
        IQueryHandler<GetOrderByIdQuery, OrderDto?> getByIdHandler)
    {
        _createHandler = createHandler;
        _getByIdHandler = getByIdHandler;
    }

    [HttpPost]
    public async Task<IActionResult> CreateOrder(
        [FromBody] CreateOrderCommand command, CancellationToken ct)
    {
        var result = await _createHandler.HandleAsync(command, ct);
        return result.IsSuccess
            ? CreatedAtAction(nameof(GetOrder), new { id = result.Value }, result.Value)
            : BadRequest(result.Error);
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetOrder(Guid id, CancellationToken ct)
    {
        var order = await _getByIdHandler.HandleAsync(new GetOrderByIdQuery(id), ct);
        return order != null ? Ok(order) : NotFound();
    }
}

// Registro en DI (Program.cs)
builder.Services.AddScoped<
    ICommandHandler<CreateOrderCommand, Result<Guid>>,
    CreateOrderCommandHandler>();
builder.Services.AddScoped<
    IQueryHandler<GetOrderByIdQuery, OrderDto?>,
    GetOrderByIdQueryHandler>();
```

---

:::note
Los command handlers publican domain events que inician flujos de mensajería distribuida. Ver [Patrones de Mensajería](./messaging-patterns.md) para Saga, Async Processing y Compensation.
:::

---

## Matriz de Decisión

| Escenario                        | Aplicar CQRS         |
| -------------------------------- | -------------------- |
| **Alta ratio lectura/escritura** | ✅✅✅               |
| **Event Sourcing**               | ✅✅✅               |
| **CRUD simple**                  | ❌ overhead excesivo |
| **Transacciones distribuidas**   | ✅                   |

---

## Beneficios en Práctica

```yaml
# ✅ Comparativa de impacto

Antes (sin CQRS):
  Problema: Un solo modelo de datos sirve lecturas y escrituras
    — queries cargan todo el aggregate para mostrar un resumen
  Consecuencia: Queries lentos, lógica de negocio mezclada
    con proyecciones de UI

Después (con CQRS):
  Estado: Command side opera sobre aggregates ricos,
    Query side usa proyecciones optimizadas con SQL directo
  Resultado: Reducción de latencia en lecturas 5-10x,
    lógica de negocio aislada y testeada independientemente
```

---

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** separar commands de queries en handlers distintos
- **MUST** validar commands antes de ejecutar

### SHOULD (Fuertemente recomendado)

- **SHOULD** publicar domain events desde aggregates

### MUST NOT (Prohibido)

- **MUST NOT** queries que modifiquen estado

---

## Referencias

- [Lineamiento Modelado de Dominio](../../lineamientos/arquitectura/09-modelado-de-dominio.md) — lineamiento que origina este estándar
- [CQRS Pattern (Martin Fowler)](https://martinfowler.com/bliki/CQRS.html)
- [Patrones de Mensajería](./messaging-patterns.md) — saga y async processing que complementan los domain events de CQRS
