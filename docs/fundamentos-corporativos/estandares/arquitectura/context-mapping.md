---
id: context-mapping
sidebar_position: 2
title: Context Mapping entre Bounded Contexts
description: Definir y documentar relaciones entre bounded contexts con patterns estratégicos de DDD
---

# Context Mapping entre Bounded Contexts

## Contexto

Este estándar define cómo mapear y documentar relaciones entre Bounded Contexts usando patrones estratégicos de Domain-Driven Design (DDD). Complementa el [lineamiento de Descomposición y Límites](../../lineamientos/arquitectura/02-descomposicion-y-limites.md) estableciendo **tipos de relaciones y comunicación** entre contextos independientes.

---

## Stack Tecnológico

| Componente        | Tecnología         | Versión | Uso                             |
| ----------------- | ------------------ | ------- | ------------------------------- |
| **Framework**     | ASP.NET Core       | 8.0+    | Implementación de integraciones |
| **HTTP Client**   | IHttpClientFactory | 8.0+    | REST API calls                  |
| **Messaging**     | Apache Kafka       | 3.6+    | Event-driven integration        |
| **Documentation** | Mermaid            | 10.0+   | Context mapping diagrams        |

---

## Patrones de Context Mapping

### Partnership (Socio)

```yaml
# ✅ Partnership: Relación de colaboración mutua

Definición: Dos contextos que evolucionan juntos, con equipos que colaboran
  estrechamente para coordinar cambios.

Cuándo usar:
  - Dos contextos altamente acoplados por naturaleza del negocio
  - Equipos trabajan en estrecha colaboración
  - Cambios en uno requieren cambios coordinados en otro

Ejemplo: Sales Context ↔ Pricing Context
  - Sales necesita calcular precios en tiempo real
  - Pricing necesita saber estructura de orders
  - Cambios en modelo de pricing impactan sales y viceversa

Implementación:
  - API síncrona bidireccional
  - Comunicación frecuente entre equipos
  - Releases coordinados

# ❌ Evitar si posible (alto acoplamiento)
```

### Shared Kernel (Núcleo Compartido)

```yaml
# ✅ Shared Kernel: Código compartido entre contextos

Definición: Subconjunto del modelo compartido entre contextos, con ownership
  compartido y acuerdo explícito en cambios.

Cuándo usar:
  - Value objects realmente universales (Money, Address, Email)
  - Abstracciones de infraestructura común
  - Types básicos compartidos

Ejemplo:
  SharedKernel (compartido por todos los contextos):
    - Money (value object)
    - Address (value object)
    - Email (value object)
    - IDomainEvent (interface)
    - AggregateRoot<T> (base class)

Implementación:
  - NuGet package compartido: Talma.SharedKernel
  - Cambios requieren consenso de todos los equipos
  - Versioning semántico estricto
  - Mínimo código compartido (solo lo esencial)

# ⚠️ Usar con precaución: cambios impactan múltiples contextos
```

```csharp
// ✅ Shared Kernel implementation

// Talma.SharedKernel/ValueObjects/Money.cs
namespace Talma.SharedKernel.ValueObjects
{
    public record Money(decimal Amount, string Currency)
    {
        public static Money Zero(string currency) => new(0, currency);

        public static Money operator +(Money left, Money right)
        {
            if (left.Currency != right.Currency)
            {
                throw new InvalidOperationException(
                    $"Cannot add money with different currencies: {left.Currency} and {right.Currency}");
            }

            return new Money(left.Amount + right.Amount, left.Currency);
        }

        public Money Multiply(decimal factor) => new(Amount * factor, Currency);
    }
}

// Usado en Sales Context
namespace Talma.Sales.Domain.Orders
{
    using Talma.SharedKernel.ValueObjects;  // ✅ Reference a SharedKernel

    public class Order
    {
        public Money TotalAmount { get; private set; }  // ✅ Usa Money del SharedKernel
    }
}

// Usado en Billing Context
namespace Talma.Billing.Domain.Invoices
{
    using Talma.SharedKernel.ValueObjects;

    public class Invoice
    {
        public Money Amount { get; private set; }  // ✅ Usa mismo Money
    }
}
```

### Customer-Supplier (Cliente-Proveedor)

```yaml
# ✅ Customer-Supplier: Relación upstream/downstream

Definición: Proveedor upstream satisface necesidades del cliente downstream.
  Proveedor tiene cierto compromiso con necesidades del cliente.

Roles:
  - Upstream (Proveedor): Define API/contrato
  - Downstream (Cliente): Consume API/contrato

Cuándo usar:
  - Clara relación proveedor-consumidor
  - Proveedor puede considerar necesidades del consumidor
  - Equipos colaboran pero con roles diferentes

Ejemplo: Catalog Context (upstream) → Sales Context (downstream)
  - Catalog provee información de productos
  - Sales consulta catálogo al crear orders
  - Catalog considera necesidades de Sales en diseño de API

Implementación:
  - REST API definida por upstream
  - Downstream consume vía HTTP client
  - SLA acordado entre equipos
  - Versioning y retrocompatibilidad
```

```csharp
// ✅ Customer-Supplier implementation

// UPSTREAM: Catalog Context expone API
namespace Talma.Catalog.Api.Controllers
{
    [ApiController]
    [Route("api/products")]
    public class ProductsController : ControllerBase
    {
        private readonly IProductService _productService;

        // ✅ API pública para consumidores downstream
        [HttpGet("{id}")]
        public async Task<ActionResult<ProductDto>> GetProduct(Guid id)
        {
            var product = await _productService.GetByIdAsync(id);

            if (product == null)
            {
                return NotFound();
            }

            // ✅ DTO específico para consumers (no exponer domain model)
            return new ProductDto
            {
                Id = product.Id,
                Name = product.Name,
                Description = product.Description,
                Price = product.Price,
                Stock = product.AvailableStock,
                IsAvailable = product.IsActive && product.AvailableStock > 0
            };
        }

        [HttpPost("check-availability")]
        public async Task<ActionResult<AvailabilityResponse>> CheckAvailability(
            CheckAvailabilityRequest request)
        {
            var results = new List<ProductAvailability>();

            foreach (var item in request.Items)
            {
                var product = await _productService.GetByIdAsync(item.ProductId);
                results.Add(new ProductAvailability
                {
                    ProductId = item.ProductId,
                    RequestedQuantity = item.Quantity,
                    AvailableQuantity = product?.AvailableStock ?? 0,
                    IsAvailable = (product?.AvailableStock ?? 0) >= item.Quantity
                });
            }

            return new AvailabilityResponse { Items = results };
        }
    }
}

// DOWNSTREAM: Sales Context consume API
namespace Talma.Sales.Infrastructure.Integration
{
    public class CatalogServiceClient
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<CatalogServiceClient> _logger;

        public CatalogServiceClient(
            HttpClient httpClient,
            ILogger<CatalogServiceClient> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
        }

        // ✅ Método que consume upstream API
        public async Task<ProductDto?> GetProductAsync(
            Guid productId,
            CancellationToken cancellationToken = default)
        {
            try
            {
                var response = await _httpClient.GetAsync(
                    $"/api/products/{productId}",
                    cancellationToken);

                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    return null;
                }

                response.EnsureSuccessStatusCode();

                return await response.Content.ReadFromJsonAsync<ProductDto>(cancellationToken);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogError(ex, "Error calling Catalog service for product {ProductId}", productId);
                throw;
            }
        }

        public async Task<AvailabilityResponse> CheckAvailabilityAsync(
            IEnumerable<(Guid ProductId, int Quantity)> items,
            CancellationToken cancellationToken = default)
        {
            var request = new CheckAvailabilityRequest
            {
                Items = items.Select(i => new CheckAvailabilityItem
                {
                    ProductId = i.ProductId,
                    Quantity = i.Quantity
                }).ToList()
            };

            var response = await _httpClient.PostAsJsonAsync(
                "/api/products/check-availability",
                request,
                cancellationToken);

            response.EnsureSuccessStatusCode();

            return await response.Content.ReadFromJsonAsync<AvailabilityResponse>(cancellationToken)
                ?? throw new InvalidOperationException("Empty response from Catalog service");
        }
    }
}

// Registration
builder.Services.AddHttpClient<CatalogServiceClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Services:CatalogApi:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(10);
})
.AddPolicyHandler(GetRetryPolicy())
.AddPolicyHandler(GetCircuitBreakerPolicy());
```

### Conformist (Conformista)

```yaml
# ✅ Conformist: Downstream acepta modelo upstream sin translation

Definición:
  Downstream acepta completamente el modelo del upstream sin adaptación.
  No hay translation layer.

Cuándo usar:
  - Upstream es sistema externo que no puedes influenciar
  - Costo de translation layer no justifica beneficio
  - Modelo upstream es suficientemente bueno

Ejemplo: Sales Context → External Payment Gateway (Stripe, PayPal)
  - Payment gateway define el modelo
  - Sales usa directamente DTOs del payment gateway
  - No hay ACL (Anti-Corruption Layer)

Implementación:
  - Usar SDK del proveedor directamente
  - No crear abstracciones adicionales
  - Aceptar cambios del upstream

# ⚠️ Risk: cambios en upstream impactan directamente downstream
```

### Anti-Corruption Layer (ACL)

```yaml
# ✅ ACL: Layer que traduce entre modelos de contextos

Definición: Capa de traducción que protege al contexto downstream de cambios
  en el upstream. Traduce modelo externo a modelo interno.

Cuándo usar:
  - Upstream es legacy system con modelo problemático
  - Quieres proteger tu modelo de dominio puro
  - Modelos upstream y downstream son muy diferentes
  - Quieres aislar cambios del upstream

Ejemplo: Modern Orders Context → Legacy ERP System
  - ERP usa términos obsoletos y estructura compleja
  - Orders Context mantiene modelo limpio
  - ACL traduce entre modelos

Implementación:
  - Adapter pattern
  - Facade pattern
  - Translation layer explícito
```

```csharp
// ✅ Anti-Corruption Layer implementation

// LEGACY SYSTEM (upstream) con modelo problemático
namespace Legacy.Erp.Contracts
{
    // ❌ Modelo legacy problemático
    public class PEDIDO_TABLA  // ❌ Naming pobre
    {
        public string ID_PED { get; set; }  // ❌ Abbreviated
        public string COD_CLI { get; set; }
        public decimal IMP_TOT { get; set; }
        public string EST { get; set; }  // ❌ Estado como string
        public DETALLE_PED[] DETS { get; set; }  // ❌ Array
    }

    public class DETALLE_PED
    {
        public string COD_PROD { get; set; }
        public int CANT { get; set; }
        public decimal PREC { get; set; }
    }
}

// ✅ ACL: Translation layer
namespace Talma.Orders.Infrastructure.Integration.Erp
{
    // ✅ Interface define contrato limpio (nuestra visión)
    public interface IErpOrderService
    {
        Task<Order?> GetOrderAsync(Guid orderId, CancellationToken cancellationToken);
        Task<Guid> CreateOrderAsync(Order order, CancellationToken cancellationToken);
    }

    // ✅ ACL implementa translation
    public class ErpOrderServiceAdapter : IErpOrderService
    {
        private readonly ILegacyErpClient _legacyClient;  // Cliente legacy
        private readonly ILogger<ErpOrderServiceAdapter> _logger;

        public async Task<Order?> GetOrderAsync(Guid orderId, CancellationToken cancellationToken)
        {
            // ✅ Call legacy system
            var legacyOrder = await _legacyClient.GetPedido(orderId.ToString());

            if (legacyOrder == null)
            {
                return null;
            }

            // ✅ Translate legacy model → domain model
            return TranslateToDomainModel(legacyOrder);
        }

        public async Task<Guid> CreateOrderAsync(Order order, CancellationToken cancellationToken)
        {
            // ✅ Translate domain model → legacy model
            var legacyOrder = TranslateToLegacyModel(order);

            // ✅ Call legacy system
            var result = await _legacyClient.CrearPedido(legacyOrder);

            return Guid.Parse(result.ID_PED);
        }

        // ✅ Translation: Legacy → Domain
        private Order TranslateToDomainModel(PEDIDO_TABLA legacyOrder)
        {
            _logger.LogDebug("Translating legacy order {OrderId}", legacyOrder.ID_PED);

            var orderId = Guid.Parse(legacyOrder.ID_PED);
            var customerId = Guid.Parse(legacyOrder.COD_CLI);

            // ✅ Traducir estado de string a enum
            var status = legacyOrder.EST switch
            {
                "B" => OrderStatus.Draft,  // Borrador
                "P" => OrderStatus.Pending,
                "A" => OrderStatus.Approved,
                "R" => OrderStatus.Rejected,
                _ => OrderStatus.Draft
            };

            // ✅ Traducir líneas
            var lines = legacyOrder.DETS
                .Select(det => new OrderLine(
                    productId: Guid.Parse(det.COD_PROD),
                    quantity: det.CANT,
                    unitPrice: new Money(det.PREC, "USD")))
                .ToList();

            // ✅ Construir domain model limpio
            return Order.Reconstitute(
                id: orderId,
                customerId: customerId,
                lines: lines,
                status: status);
        }

        // ✅ Translation: Domain → Legacy
        private PEDIDO_TABLA TranslateToLegacyModel(Order order)
        {
            return new PEDIDO_TABLA
            {
                ID_PED = order.Id.ToString(),
                COD_CLI = order.CustomerId.ToString(),
                IMP_TOT = order.TotalAmount.Amount,
                EST = order.Status switch
                {
                    OrderStatus.Draft => "B",
                    OrderStatus.Pending => "P",
                    OrderStatus.Approved => "A",
                    OrderStatus.Rejected => "R",
                    _ => "B"
                },
                DETS = order.Lines
                    .Select(line => new DETALLE_PED
                    {
                        COD_PROD = line.ProductId.ToString(),
                        CANT = line.Quantity,
                        PREC = line.UnitPrice.Amount
                    })
                    .ToArray()
            };
        }
    }
}

// Usage en domain service
namespace Talma.Orders.Application.UseCases
{
    public class ImportOrderFromErpHandler
    {
        private readonly IErpOrderService _erpService;  // ✅ Interface limpia (no legacy)
        private readonly IOrderRepository _orderRepository;

        public async Task<Order> Handle(ImportOrderFromErpCommand command)
        {
            // ✅ Trabajar con modelo limpio (ACL maneja la traducción)
            var order = await _erpService.GetOrderAsync(command.ErpOrderId);

            if (order == null)
            {
                throw new NotFoundException($"Order {command.ErpOrderId} not found in ERP");
            }

            // ✅ Domain model limpio, sin contaminación del legacy
            await _orderRepository.AddAsync(order);

            return order;
        }
    }
}
```

### Open Host Service (OHS)

```yaml
# ✅ OHS: API pública well-defined para múltiples consumers

Definición:
  Upstream expone API pública y well-documented para cualquier consumer.
  API diseñada para múltiples consumers con diferentes necesidades.

Cuándo usar:
  - Múltiples consumers downstream
  - API pública (interna o externa)
  - Necesitas estabilidad y retrocompatibilidad

Ejemplo: Catalog Context expone Open Host Service
  - API REST con OpenAPI spec
  - Versionada (v1, v2)
  - Documentación pública
  - SLA definido
  - Usado por Sales, Fulfillment, Customer Service, Mobile App

Implementación:
  - REST API con OpenAPI
  - API Gateway (Kong)
  - Versioning estricto
  - Deprecation policy
```

### Published Language (PL)

```yaml
# ✅ Published Language: Contrato bien definido y documentado

Definición: Lenguaje compartido (schema) para comunicación entre contextos.
  Típicamente usado junto con Open Host Service para definir contratos.

Cuándo usar:
  - Event-driven architecture
  - Múltiples consumers de eventos
  - Necesitas schema evolution

Ejemplo:
  Order Events (Published Language):
    - OrderCreated (Avro schema v1)
    - OrderApproved (Avro schema v2)
    - OrderShipped (Avro schema v1)

  Consumers:
    - Fulfillment Context
    - Billing Context
    - Notification Context
    - Analytics Context

Implementación:
  - Avro/Protobuf schemas
  - Schema Registry
  - Versioning de schemas
```

```csharp
// ✅ Published Language con Avro schemas

// OrderApprovedEvent.avsc (Avro schema)
{
  "type": "record",
  "name": "OrderApprovedEvent",
  "namespace": "Talma.Sales.Contracts.Events.V1",
  "fields": [
    {"name": "orderId", "type": "string"},
    {"name": "customerId", "type": "string"},
    {"name": "totalAmount", "type": "double"},
    {"name": "currency", "type": "string"},
    {"name": "approvedAt", "type": "long", "logicalType": "timestamp-millis"},
    {"name": "approvedBy", "type": "string"},
    {
      "name": "items",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "OrderItem",
          "fields": [
            {"name": "productId", "type": "string"},
            {"name": "quantity", "type": "int"},
            {"name": "unitPrice", "type": "double"}
          ]
        }
      }
    }
  ]
}

// Publisher (Sales Context)
namespace Talma.Sales.Infrastructure.Messaging
{
    public class OrderEventPublisher
    {
        private readonly IProducer<string, OrderApprovedEvent> _producer;

        public async Task PublishOrderApprovedAsync(Order order)
        {
            // ✅ Crear evento en Published Language (Avro schema)
            var avroEvent = new OrderApprovedEvent
            {
                orderId = order.Id.ToString(),
                customerId = order.CustomerId.ToString(),
                totalAmount = (double)order.TotalAmount.Amount,
                currency = order.TotalAmount.Currency,
                approvedAt = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                approvedBy = order.ApprovedBy.ToString(),
                items = order.Lines.Select(l => new OrderItem
                {
                    productId = l.ProductId.ToString(),
                    quantity = l.Quantity,
                    unitPrice = (double)l.UnitPrice.Amount
                }).ToList()
            };

            // ✅ Publish con Avro serialization
            await _producer.ProduceAsync(
                topic: "orders.approved.v1",
                message: new Message<string, OrderApprovedEvent>
                {
                    Key = order.Id.ToString(),
                    Value = avroEvent
                });
        }
    }
}

// Consumer (Fulfillment Context)
namespace Talma.Fulfillment.Infrastructure.Messaging
{
    public class OrderApprovedConsumer : IHostedService
    {
        private readonly IConsumer<string, OrderApprovedEvent> _consumer;

        public async Task Consume(CancellationToken stoppingToken)
        {
            _consumer.Subscribe("orders.approved.v1");

            while (!stoppingToken.IsCancellationRequested)
            {
                var consumeResult = _consumer.Consume(stoppingToken);

                // ✅ Consumir evento en Published Language (Avro)
                var avroEvent = consumeResult.Message.Value;

                // ✅ Translate Published Language → Domain Model
                var fulfillmentOrder = new Fulfillment.Domain.Orders.Order
                {
                    OrderId = Guid.Parse(avroEvent.orderId),
                    CustomerId = Guid.Parse(avroEvent.customerId),
                    // ... map fields
                };

                await _fulfillmentService.CreateFulfillmentOrderAsync(fulfillmentOrder);

                _consumer.Commit(consumeResult);
            }
        }
    }
}
```

### Separate Ways

```yaml
# ✅ Separate Ways: Sin integración, contextos completamente independientes

Definición: Dos contextos no se integran en absoluto. Operan independientemente
  sin comunicación directa.

Cuándo usar:
  - Costos de integración superan beneficios
  - Contextos sirven propósitos completamente diferentes
  - Overhead de comunicación no justifica valor

Ejemplo: Orders Context y Employee Management Context
  - No hay necesidad de integración
  - Dominios completamente separados
  - Sin comunicación entre ellos

Implementación:
  - No hay integración
  - Bases de datos completamente separadas
  - No eventos compartidos
```

### Big Ball of Mud

```yaml
# ❌ Big Ball of Mud: Anti-pattern (evitar)

Definición: Código sin límites claros, alta mezcla de responsabilidades,
  dependencias circulares.

Señales:
  - Shared database entre múltiples "servicios"
  - Referencias directas a clases de otros contextos
  - No hay boundaries claros
  - Changes en un área rompen otra

Solución:
  - Identificar bounded contexts
  - Refactorizar hacia límites claros
  - Implementar ACL para aislar legacy code
```

---

## Context Map Completo

```mermaid
graph TB
    subgraph Core["<b>Core Domain</b>"]
        Sales["Sales<br/>(OHS)"]
    end

    subgraph Supporting["<b>Supporting Subdomain</b>"]
        Fulfillment["Fulfillment<br/>(Consumer)"]
        Billing["Billing<br/>(Consumer)"]
        Notification["Notification<br/>(Consumer)"]
    end

    subgraph Generic["<b>Generic Subdomain</b>"]
        Catalog["Catalog<br/>(OHS)"]
        Customer["Customer<br/>(OHS)"]
    end

    subgraph External["<b>External Systems</b>"]
        LegacyERP["Legacy ERP<br/>(Legacy)"]
        PaymentGateway["Payment Gateway<br/>(External)"]
    end

    Sales -->|"Customer-Supplier<br/>(REST API)"| Catalog
    Sales -->|"Customer-Supplier<br/>(REST API)"| Customer
    Sales -->|"Published Language<br/>(Kafka Events)"| Fulfillment
    Sales -->|"Published Language<br/>(Kafka Events)"| Billing
    Sales -->|"Published Language<br/>(Kafka Events)"| Notification
    Sales -->|"ACL<br/>(Translation)"| LegacyERP
    Sales -->|"Conformist<br/>(SDK)"| PaymentGateway

    Fulfillment -->|"Customer-Supplier"| Catalog
    Billing -->|"Customer-Supplier"| Customer

    classDef core fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef supporting fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef generic fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef external fill:#ffebee,stroke:#c62828,stroke-width:2px

    class Sales core
    class Fulfillment,Billing,Notification supporting
    class Catalog,Customer generic
    class LegacyERP,PaymentGateway external
``

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** documentar relaciones entre bounded contexts (context map)
- **MUST** definir patrón de integración para cada relación
- **MUST** usar ACL cuando integres con legacy systems
- **MUST** versionar APIs públicas (Open Host Service)
- **MUST** mantener ACL en infrastructure layer (no en domain)
- **MUST** usar Published Language para eventos (Avro/Protobuf schemas)

### SHOULD (Fuertemente recomendado)

- **SHOULD** minimizar uso de Partnership (alto acoplamiento)
- **SHOULD** minimizar Shared Kernel (solo value objects universales)
- **SHOULD** usar Customer-Supplier cuando sea posible
- **SHOULD** implementar circuit breaker al llamar upstream services
- **SHOULD** documentar SLAs entre upstream y downstream
- **SHOULD** usar Schema Registry para Published Language

### MAY (Opcional)

- **MAY** usar Conformist para servicios externos bien diseñados
- **MAY** implementar caching en downstream para reducir llamadas
- **MAY** usar Separate Ways cuando integración no aporta valor

### MUST NOT (Prohibido)

- **MUST NOT** compartir base de datos entre contextos
- **MUST NOT** referenciar clases de dominio directamente entre contextos
- **MUST NOT** exponer domain model en APIs públicas (usar DTOs)
- **MUST NOT** permitir dependencias circulares entre contextos
- **MUST NOT** usar Big Ball of Mud pattern
- **MUST NOT** omitir ACL cuando integres con legacy systems

---

## Referencias

- [Lineamiento: Descomposición y Límites](../../lineamientos/arquitectura/02-descomposicion-y-limites.md)
- Estándares relacionados:
  - [Bounded Contexts](bounded-contexts.md)
  - [API Contracts](../apis/api-contracts.md)
  - [Domain Events](../mensajeria/domain-events.md)
- Especificaciones:
  - [DDD Context Mapping](https://www.domainlanguage.com/ddd/reference/)
  - [Context Mapper](https://contextmapper.org/)
  - [Strategic Domain-Driven Design](https://vaadin.com/blog/ddd-part-1-strategic-domain-driven-design)
```
