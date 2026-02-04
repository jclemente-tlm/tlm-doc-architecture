---
id: data-ownership
sidebar_position: 6
title: Data Ownership
description: Estándar para definir ownership claro de datos por servicio, con tabla de responsabilidades y bounded contexts
---

# Estándar Técnico — Data Ownership

---

## 1. Propósito

Establecer ownership claro y exclusivo de cada entidad de datos por un único servicio, evitando ambigüedad, duplicación y conflictos de responsabilidad en arquitecturas de microservicios.

---

## 2. Alcance

**Aplica a:**

- Definición de bounded contexts
- Diseño de microservicios
- APIs de datos entre servicios
- Event-driven architectures
- Data governance policies
- Migraciones de monolito a microservicios

**No aplica a:**

- Datos compartidos read-only (reference data)
- Logs y métricas centralizadas
- Datos transitorios (cache)

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología         | Versión mínima | Observaciones                 |
| ------------------- | ------------------ | -------------- | ----------------------------- |
| **Documentation**   | Markdown + ADRs    | -              | Documentar ownership en ADRs  |
| **Catalog**         | Backstage          | 1.20+          | Service catalog con ownership |
| **Schema Registry** | Confluent Registry | 7.5+           | Ownership de eventos          |
| **API Gateway**     | Kong               | 3.4+           | Routing por owner service     |
| **Observability**   | Grafana dashboards | 10.0+          | Métricas por owner            |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Ownership Único

- [ ] **Una entidad = un owner service** (no compartir ownership)
- [ ] **Write access exclusivo** del owner
- [ ] **Read access via API** del owner service
- [ ] Tabla de ownership documentada y actualizada
- [ ] ADR por cada decisión de ownership

### Bounded Context Claro

- [ ] Bounded contexts definidos según DDD
- [ ] Entidades ubicadas en el bounded context correcto
- [ ] Agregados con transactional boundaries claros
- [ ] Context map documentando relaciones

### Responsabilidades del Owner

- [ ] **Schema evolution:** owner define cambios de schema
- [ ] **Data quality:** owner valida consistencia e integridad
- [ ] **Retention policies:** owner define lifecycle de datos
- [ ] **API contracts:** owner publica y versiona APIs
- [ ] **SLOs:** owner define y monitorea SLOs

### Acceso Cross-Service

- [ ] Otros servicios acceden **solo via API** del owner
- [ ] No direct database access permitido
- [ ] Events publicados por owner para notificar cambios
- [ ] Read models/projections para queries complejas

### Metadata de Ownership

- [ ] Tabla `data_ownership` con mappings
- [ ] Tags en databases (owner, criticality, pii)
- [ ] API documentation con owner contact
- [ ] RACI matrix (Responsible, Accountable, Consulted, Informed)

---

## 5. Prohibiciones

- ❌ Múltiples servicios con write access a misma entidad
- ❌ Shared database sin ownership claro
- ❌ Modificar datos de otro servicio directamente
- ❌ Duplicar entidades en múltiples servicios sin justificación
- ❌ Ownership indefinido ("legacy" no es justificación válida)
- ❌ Ignorar bounded context boundaries
- ❌ Agregados spanning múltiples servicios

---

## 6. Configuración Mínima

### Data Ownership Table

```sql
-- Metadata de ownership
CREATE TABLE data_ownership (
    id SERIAL PRIMARY KEY,
    entity_name VARCHAR(100) NOT NULL UNIQUE,
    owner_service VARCHAR(100) NOT NULL,
    owner_team VARCHAR(100) NOT NULL,
    bounded_context VARCHAR(100) NOT NULL,
    contains_pii BOOLEAN NOT NULL DEFAULT FALSE,
    criticality VARCHAR(20) NOT NULL CHECK (criticality IN ('low', 'medium', 'high', 'critical')),
    retention_days INT,
    api_endpoint VARCHAR(255),
    documentation_url VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO data_ownership (entity_name, owner_service, owner_team, bounded_context, contains_pii, criticality, api_endpoint) VALUES
('Order', 'orders-service', 'commerce', 'Sales', FALSE, 'critical', 'https://api.talma.com/orders/v1'),
('Customer', 'customers-service', 'crm', 'Customer Management', TRUE, 'critical', 'https://api.talma.com/customers/v1'),
('Product', 'catalog-service', 'commerce', 'Product Catalog', FALSE, 'high', 'https://api.talma.com/catalog/v1'),
('Payment', 'payments-service', 'finance', 'Billing', TRUE, 'critical', 'https://api.talma.com/payments/v1'),
('Inventory', 'inventory-service', 'operations', 'Fulfillment', FALSE, 'high', 'https://api.talma.com/inventory/v1');
```

### Bounded Context Documentation

```markdown
# Bounded Context: Sales

**Owner Team:** Commerce Team
**Owner Service:** orders-service

## Entities Owned

- **Order** - Pedidos de clientes
  - Aggregates: Order, OrderItem
  - Write Access: orders-service únicamente
  - Read Access: via Orders API
  - Events Published: OrderCreated, OrderShipped, OrderCancelled

- **ShoppingCart** - Carritos de compra
  - Aggregates: Cart, CartItem
  - Write Access: orders-service
  - Events Published: CartUpdated, CartAbandoned

## Dependencies (Read-only)

- Customer → customers-service (API)
- Product → catalog-service (API)
- Inventory → inventory-service (Events)

## APIs Exposed

- GET /api/v1/orders/{id}
- POST /api/v1/orders
- GET /api/v1/orders?customerId={id}

## Events Published

- `com.talma.sales.order.created.v1`
- `com.talma.sales.order.shipped.v1`
- `com.talma.sales.order.cancelled.v1`

## SLOs

- Availability: 99.9%
- Latency p95: <200ms
- Data Consistency: Strong (ACID transactions)
```

### Service Metadata (Backstage)

```yaml
# catalog-info.yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: orders-service
  description: Servicio de gestión de órdenes
  annotations:
    github.com/project-slug: talma/orders-service
  tags:
    - commerce
    - critical
  links:
    - url: https://api.talma.com/orders/swagger
      title: API Documentation
    - url: https://wiki.talma.com/services/orders
      title: Service Wiki
spec:
  type: service
  lifecycle: production
  owner: commerce-team
  system: sales-platform
  providesApis:
    - orders-api-v1
  consumesApis:
    - customers-api-v1
    - catalog-api-v1
  dependsOn:
    - resource:orders-database
    - resource:orders-cache

---
apiVersion: backstage.io/v1alpha1
kind: Resource
metadata:
  name: orders-database
  description: PostgreSQL database para orders-service
spec:
  type: database
  owner: commerce-team
  system: sales-platform
  lifecycle: production
```

### API Response con Owner Metadata

```csharp
// DTOs/OrderDto.cs
public record OrderDto
{
    public Guid Id { get; init; }
    public Guid CustomerId { get; init; }
    public decimal TotalAmount { get; init; }
    public OrderStatus Status { get; init; }

    // Metadata de ownership
    [JsonPropertyName("_links")]
    public OrderLinks Links { get; init; } = new();

    [JsonPropertyName("_metadata")]
    public OrderMetadata Metadata { get; init; } = new();
}

public record OrderLinks
{
    public Link Self { get; init; }
    public Link Customer { get; init; }  // Link a owner de Customer
    public Link Items { get; init; }
}

public record OrderMetadata
{
    public string OwnerService { get; init; } = "orders-service";
    public string OwnerTeam { get; init; } = "commerce";
    public string Version { get; init; } = "v1";
    public DateTime LastModified { get; init; }
}

// Controllers/OrdersController.cs
[HttpGet("{id}")]
public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
{
    var order = await _orderService.GetOrderAsync(id);
    if (order == null)
        return NotFound();

    var dto = new OrderDto
    {
        Id = order.Id,
        CustomerId = order.CustomerId,
        TotalAmount = order.TotalAmount,
        Status = order.Status,
        Links = new OrderLinks
        {
            Self = new Link { Href = $"/api/v1/orders/{id}" },
            Customer = new Link { Href = $"/api/v1/customers/{order.CustomerId}" },  // Owner: customers-service
            Items = new Link { Href = $"/api/v1/orders/{id}/items" }
        },
        Metadata = new OrderMetadata
        {
            LastModified = order.UpdatedAt
        }
    };

    return Ok(dto);
}
```

---

## 7. Ejemplos

### Ownership Matrix

| Entity          | Owner Service     | Owner Team | Bounded Context     | Write Access      | Read Access           |
| --------------- | ----------------- | ---------- | ------------------- | ----------------- | --------------------- |
| Order           | orders-service    | Commerce   | Sales               | orders-service    | Via Orders API        |
| Customer        | customers-service | CRM        | Customer Management | customers-service | Via Customers API     |
| Product         | catalog-service   | Commerce   | Product Catalog     | catalog-service   | Via Catalog API       |
| Inventory       | inventory-service | Operations | Fulfillment         | inventory-service | Via Inventory API     |
| Payment         | payments-service  | Finance    | Billing             | payments-service  | Via Payments API      |
| User (Identity) | identity-service  | Platform   | Identity & Access   | identity-service  | Via Identity API      |
| AuditLog        | audit-service     | Platform   | Compliance          | audit-service     | Via Audit API (admin) |

### Event Ownership

```csharp
// Events/OrderCreatedEvent.cs
/// <summary>
/// Evento publicado cuando se crea una nueva orden
/// Owner: orders-service
/// Schema Registry: com.talma.sales.order.created.v1
/// </summary>
public record OrderCreatedEvent
{
    [JsonPropertyName("metadata")]
    public EventMetadata Metadata { get; init; } = new();

    [JsonPropertyName("data")]
    public OrderCreatedData Data { get; init; }
}

public record EventMetadata
{
    [JsonPropertyName("event_id")]
    public Guid EventId { get; init; } = Guid.NewGuid();

    [JsonPropertyName("event_type")]
    public string EventType { get; init; } = "com.talma.sales.order.created.v1";

    [JsonPropertyName("source_service")]
    public string SourceService { get; init; } = "orders-service";

    [JsonPropertyName("owner_team")]
    public string OwnerTeam { get; init; } = "commerce";

    [JsonPropertyName("timestamp")]
    public DateTime Timestamp { get; init; } = DateTime.UtcNow;

    [JsonPropertyName("schema_version")]
    public string SchemaVersion { get; init; } = "1.0.0";
}
```

### Migration: Splitting Ownership

```csharp
// Escenario: Separar ownership de Customers de monolito a microservicio

// Paso 1: Crear customers-service
// Paso 2: Migrar datos
// Paso 3: Dual-write period
public class CustomerService
{
    private readonly MonolithDbContext _monolithDb;
    private readonly CustomersDbContext _customersDb;
    private readonly ILogger<CustomerService> _logger;

    // Durante migración: dual-write
    public async Task UpdateCustomerAsync(Guid customerId, UpdateCustomerCommand command)
    {
        // Write a ambos (temporal)
        await UpdateMonolithCustomerAsync(customerId, command);
        await UpdateMicroserviceCustomerAsync(customerId, command);

        _logger.LogInformation(
            "Dual-write completed for customer {CustomerId}",
            customerId);
    }
}

// Paso 4: Deprecar write access al monolito
// Paso 5: customers-service es único owner
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Tabla de ownership documentada y actualizada
- [ ] ADRs documentando decisiones de ownership
- [ ] Bounded contexts definidos
- [ ] APIs publicadas por owner services
- [ ] Network policies bloquean write access no autorizado
- [ ] Service catalog actualizado (Backstage)
- [ ] RACI matrix definida

### Métricas

```promql
# Cross-service API calls (validar que no hay DB access directo)
sum by (source_service, target_service) (rate(api_requests_total[5m]))

# Ownership violations (alertas)
ownership_violations_total
```

### Queries de Validación

```sql
-- Verificar ownership definido para todas las entidades
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
  AND table_name NOT IN (SELECT entity_name FROM data_ownership);

-- Revisar entidades críticas sin owner
SELECT * FROM data_ownership
WHERE owner_service IS NULL OR owner_team IS NULL;
```

---

## 9. Referencias

**Teoría:**

- Eric Evans - "Domain-Driven Design"
- Sam Newman - "Building Microservices"
- Vernon, Vaughn - "Implementing Domain-Driven Design"

**Documentación:**

- [Backstage Service Catalog](https://backstage.io/docs/features/software-catalog/)
- [Domain-Driven Design Reference](https://www.domainlanguage.com/ddd/reference/)

**Buenas prácticas:**

- Martin Fowler - "Bounded Context"
- Chris Richardson - "Microservices Patterns"
