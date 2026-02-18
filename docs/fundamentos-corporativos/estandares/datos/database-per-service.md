---
id: database-per-service
sidebar_position: 1
title: Database per Service
description: Cada servicio debe tener su propia base de datos sin compartir esquemas con otros servicios
---

# Database per Service

## Contexto

Este estándar define el principio de **database per service**: cada servicio posee su propia base de datos y es el único que puede acceder directamente a ella. Complementa el [lineamiento de Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md) asegurando **aislamiento de datos y despliegue independiente**.

---

## Conceptos Fundamentales

### ¿Qué es Database per Service?

```yaml
# ✅ Database per Service = Cada servicio posee su propia base de datos

Definición:
  Cada servicio tiene su propia base de datos (schema, cluster o instancia física)
  y es el ÚNICO con acceso directo a ella.

Características:
  ✅ Encapsulación: Servicio controla su esquema y datos
  ✅ Autonomía: Cambios de schema sin coordinación con otros servicios
  ✅ Aislamiento: Fallas de DB en un servicio no afectan otros
  ✅ Tecnología independiente: Cada servicio elige DB adecuada
  ✅ Escalabilidad independiente: Escalar DB según carga del servicio

Anti-patterns:
  ❌ Shared Database: Múltiples servicios acceden mismas tablas
  ❌ Shared Schema: Múltiples servicios en una DB, diferentes schemas
  ❌ Direct DB Access: Servicio A consulta directamente DB de servicio B
  ❌ Foreign Keys entre servicios: Order.customer_id → FK a customers.id

Beneficios:
  ✅ Despliegue independiente (cambio de schema solo afecta un servicio)
  ✅ Tecnología adecuada (PostgreSQL para transaccional, MongoDB para docs)
  ✅ Performance aislada (query lenta no bloquea otros servicios)
  ✅ Seguridad (servicio solo accede sus propios datos)
  ✅ Escalabilidad independiente (servicio con más carga escala su DB)

Trade-offs: ⚠️ No joins entre servicios (sincronizar via eventos)
  ⚠️ Consistencia eventual (no ACID entre servicios)
  ⚠️ Duplicación de datos (denormalización necesaria)
  ⚠️ Transacciones distribuidas complejas (usar sagas)
```

### Ejemplo Visual

```yaml
# ✅ BUENO: Database per Service

┌─────────────────────────┐
│   Sales Service         │
│  ┌─────────────────┐    │
│  │ Sales DB        │    │
│  │ - orders        │    │
│  │ - order_lines   │    │
│  └─────────────────┘    │
└─────────────────────────┘
         │ API
         ▼
┌─────────────────────────┐
│  Fulfillment Service    │
│  ┌─────────────────┐    │
│  │ Fulfillment DB  │    │
│  │ - shipments     │    │
│  │ - packages      │    │
│  └─────────────────┘    │
└─────────────────────────┘
         │ API
         ▼
┌─────────────────────────┐
│  Billing Service        │
│  ┌─────────────────┐    │
│  │ Billing DB      │    │
│  │ - invoices      │    │
│  │ - payments      │    │
│  └─────────────────┘    │
└─────────────────────────┘

✅ Cada servicio posee su DB
✅ Sin acceso directo entre DBs
✅ Comunicación via APIs/eventos

# ❌ MALO: Shared Database

┌─────────────────────────────────────┐
│         Shared Database             │
│  ┌─────────────────────────────┐   │
│  │ - orders (Sales accede)     │   │
│  │ - order_lines (Sales)       │   │
│  │ - shipments (Fulfillment)   │   │
│  │ - invoices (Billing)        │   │
│  │ - payments (Billing)        │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
         │         │         │
         ▼         ▼         ▼
      Sales   Fulfillment  Billing

❌ Todos acceden misma DB
❌ Cambio de schema afecta múltiples servicios
❌ Locks compartidos
❌ No hay autonomía
```

## Implementación en Talma

### Arquitectura de Datos

```yaml
# ✅ Stack típico en Talma

Sales Service:
  DB: AWS RDS PostgreSQL 15
  Instance: db.t3.medium
  Storage: 100 GB GP3
  Schema: sales
  Tables: orders, order_lines, order_events
  Connection String: sales-db.cluster-xyz.us-east-1.rds.amazonaws.com

Fulfillment Service:
  DB: AWS RDS PostgreSQL 15
  Instance: db.t3.small
  Storage: 50 GB GP3
  Schema: fulfillment
  Tables: shipments, packages, deliveries
  Connection String: fulfillment-db.cluster-abc.us-east-1.rds.amazonaws.com

Billing Service:
  DB: AWS RDS PostgreSQL 15
  Instance: db.t3.medium
  Storage: 100 GB GP3
  Schema: billing
  Tables: invoices, payments, payment_methods
  Connection String: billing-db.cluster-def.us-east-1.rds.amazonaws.com

Catalog Service:
  DB: AWS RDS PostgreSQL 15 (read replicas para performance)
  Instance: db.t3.large (más reads que writes)
  Storage: 200 GB GP3
  Schema: catalog
  Tables: products, categories, inventory
  Read Replicas: 2 (para alta concurrencia de lectura)

✅ Cada servicio tiene su propio RDS instance
✅ Escalado independiente según carga
✅ Backups independientes
✅ Cambios de schema sin afectar otros servicios
```

### Configuración de Conexión

```csharp
// ✅ BUENO: Servicio solo configura su propia DB

// appsettings.json (Sales Service)
{
  "ConnectionStrings": {
    // ✅ Solo connection string de Sales DB
    "SalesDb": "Host=sales-db.cluster-xyz.us-east-1.rds.amazonaws.com;Database=sales;Username=sales_user;Password=***"
  }
}

// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Configurar solo Sales DB
builder.Services.AddDbContext<SalesDbContext>(options =>
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("SalesDb"),
        npgsqlOptions => npgsqlOptions.MigrationsAssembly("Sales.Infrastructure")));

// ❌ NUNCA: builder.Configuration.GetConnectionString("FulfillmentDb")
// ❌ NUNCA: builder.Configuration.GetConnectionString("BillingDb")

var app = builder.Build();
app.Run();

// ❌ MALO: Servicio configura múltiples DBs de otros servicios

// appsettings.json (ANTI-PATTERN)
{
  "ConnectionStrings": {
    "SalesDb": "...",
    "FulfillmentDb": "...",  // ❌ No debería estar aquí
    "BillingDb": "..."       // ❌ No debería estar aquí
  }
}
```

### DbContext por Servicio

```csharp
// ✅ BUENO: DbContext solo con entidades del servicio

namespace Talma.Sales.Infrastructure.Persistence
{
    public class SalesDbContext : DbContext
    {
        public SalesDbContext(DbContextOptions<SalesDbContext> options)
            : base(options)
        {
        }

        // ✅ Solo entidades del bounded context Sales
        public DbSet<Order> Orders { get; set; }
        public DbSet<OrderLine> OrderLines { get; set; }

        // ❌ NUNCA: public DbSet<Shipment> Shipments { get; set; }  // Eso es de Fulfillment!
        // ❌ NUNCA: public DbSet<Invoice> Invoices { get; set; }    // Eso es de Billing!

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            // ✅ Configurar solo entidades propias
            modelBuilder.ApplyConfiguration(new OrderConfiguration());
            modelBuilder.ApplyConfiguration(new OrderLineConfiguration());

            // ✅ Schema propio
            modelBuilder.HasDefaultSchema("sales");
        }
    }
}

// Fulfillment Service tiene su propio DbContext:

namespace Talma.Fulfillment.Infrastructure.Persistence
{
    public class FulfillmentDbContext : DbContext
    {
        public DbSet<Shipment> Shipments { get; set; }
        public DbSet<Package> Packages { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.HasDefaultSchema("fulfillment");
        }
    }
}
```

## Sincronización Entre Servicios

### Problema: Datos de Otros Servicios

```csharp
// ❌ MALO: Hacer JOIN entre servicios con DB compartida

// ANTI-PATTERN: Sales Service consulta tabla de Fulfillment directamente
public async Task<OrderWithShipmentDto> GetOrderWithShipmentAsync(Guid orderId)
{
    var query = @"
        SELECT
            o.order_id, o.customer_id, o.total,
            s.shipment_id, s.tracking_number, s.status  -- ❌ tabla de otro servicio!
        FROM sales.orders o
        LEFT JOIN fulfillment.shipments s ON s.order_id = o.order_id  -- ❌ JOIN cross-service!
        WHERE o.order_id = @orderId";

    // ❌ Esto rompe autonomía:
    // - Sales depende de schema de Fulfillment
    // - Si Fulfillment cambia schema, Sales se rompe
    // - No se puede desplegar independientemente
    // - Locks compartidos

    return await _connection.QuerySingleAsync<OrderWithShipmentDto>(query, new { orderId });
}
```

### Solución 1: Denormalización con Eventos

```csharp
// ✅ BUENO: Sales mantiene copia de datos que necesita

// 1. Sales DB tiene columna shipment_status (denormalizado)

CREATE TABLE sales.orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(18,2),

    -- ✅ Denormalización: copia de datos de Fulfillment
    shipment_status VARCHAR(20),  -- "Pending" | "Shipped" | "Delivered"
    tracking_number VARCHAR(50),
    shipped_at TIMESTAMP
);

// 2. Fulfillment publica evento cuando crea shipment

namespace Talma.Fulfillment.Domain.Events
{
    public record ShipmentCreated(
        Guid ShipmentId,
        Guid OrderId,  // ✅ Referencia a Order de Sales
        string TrackingNumber,
        DateTime ShippedAt
    ) : DomainEvent;
}

public class Shipment : AggregateRoot
{
    public void Create(Guid orderId, string trackingNumber)
    {
        // ... lógica

        // ✅ Publicar evento
        AddDomainEvent(new ShipmentCreated(ShipmentId, orderId, trackingNumber, DateTime.UtcNow));
    }
}

// 3. Sales escucha evento y actualiza su copia

namespace Talma.Sales.Application.EventHandlers
{
    public class ShipmentCreatedEventHandler : IEventHandler<ShipmentCreated>
    {
        private readonly IOrderRepository _orderRepo;

        public async Task HandleAsync(ShipmentCreated evt)
        {
            var order = await _orderRepo.GetByIdAsync(evt.OrderId);
            if (order == null) return;

            // ✅ Actualizar datos denormalizados en Sales DB
            order.UpdateShipmentInfo(evt.TrackingNumber, evt.ShippedAt, "Shipped");

            await _orderRepo.SaveAsync(order);
        }
    }
}

public class Order : AggregateRoot
{
    // ✅ Propiedades denormalizadas
    public string? ShipmentStatus { get; private set; }
    public string? TrackingNumber { get; private set; }
    public DateTime? ShippedAt { get; private set; }

    // ✅ Método para actualizar desde evento
    public void UpdateShipmentInfo(string trackingNumber, DateTime shippedAt, string status)
    {
        TrackingNumber = trackingNumber;
        ShippedAt = shippedAt;
        ShipmentStatus = status;
    }
}

// 4. Ahora Sales puede consultar sin JOIN cross-service

public async Task<OrderDto> GetOrderWithShipmentAsync(Guid orderId)
{
    // ✅ Query solo en Sales DB
    var order = await _context.Orders
        .Where(o => o.OrderId == orderId)
        .Select(o => new OrderDto
        {
            OrderId = o.OrderId,
            Total = o.Total,
            Status = o.Status,
            // ✅ Datos denormalizados
            ShipmentStatus = o.ShipmentStatus,
            TrackingNumber = o.TrackingNumber
        })
        .FirstOrDefaultAsync();

    return order;
}
```

### Solución 2: Consulta via API

```csharp
// ✅ BUENO: Si necesitas datos frescos, consultar via API

// Sales Service consulta Fulfillment via HTTP API

public class OrderQueryService
{
    private readonly SalesDbContext _salesContext;
    private readonly IFulfillmentServiceClient _fulfillmentClient;  // ✅ HTTP client

    public async Task<OrderWithShipmentDto> GetOrderWithShipmentAsync(Guid orderId)
    {
        // ✅ 1. Consultar Order en Sales DB
        var order = await _salesContext.Orders
            .FirstOrDefaultAsync(o => o.OrderId == orderId);

        if (order == null) return null;

        // ✅ 2. Consultar Shipment via API (no direct DB access)
        var shipment = await _fulfillmentClient.GetShipmentByOrderIdAsync(orderId);

        // ✅ 3. Componer DTO
        return new OrderWithShipmentDto
        {
            OrderId = order.OrderId,
            Total = order.Total,
            Status = order.Status,
            Shipment = shipment != null ? new ShipmentDto
            {
                TrackingNumber = shipment.TrackingNumber,
                Status = shipment.Status
            } : null
        };
    }
}

// Fulfillment Service expone API

[ApiController]
[Route("api/shipments")]
public class ShipmentsController : ControllerBase
{
    private readonly IShipmentRepository _shipmentRepo;

    // ✅ API pública para consultar shipment
    [HttpGet("by-order/{orderId}")]
    public async Task<IActionResult> GetByOrderId(Guid orderId)
    {
        var shipment = await _shipmentRepo.GetByOrderIdAsync(orderId);
        if (shipment == null) return NotFound();

        return Ok(new ShipmentDto
        {
            ShipmentId = shipment.ShipmentId,
            OrderId = shipment.OrderId,
            TrackingNumber = shipment.TrackingNumber,
            Status = shipment.Status
        });
    }
}
```

## Migraciones de Schema

```csharp
// ✅ BUENO: Migraciones independientes por servicio

// Sales Service - Migrations

dotnet ef migrations add AddShipmentInfoToOrder --project Sales.Infrastructure
dotnet ef database update --project Sales.Infrastructure

// ✅ Solo afecta Sales DB, no requiere coordinación con Fulfillment

// Fulfillment Service - Migrations (independiente)

dotnet ef migrations add AddTrackingNumber --project Fulfillment.Infrastructure
dotnet ef database update --project Fulfillment.Infrastructure

// ✅ Solo afecta Fulfillment DB, Sales no se entera

// ❌ MALO: Migración que afecta múltiples servicios

-- migration.sql (ANTI-PATTERN)
ALTER TABLE sales.orders ADD COLUMN shipment_id UUID;  -- ✅ OK

ALTER TABLE fulfillment.shipments ADD COLUMN order_total DECIMAL;  -- ❌ NO!
-- Esto requiere coordinación entre Sales y Fulfillment
-- Rompe autonomía
```

## Tecnología Heterogénea

```yaml
# ✅ Cada servicio elige DB adecuada

Sales Service:
  DB: PostgreSQL 15 # ✅ Transaccional, consistency
  Razón: ACID para orders, joins entre order y order_lines

Catalog Service:
  DB: PostgreSQL 15 + Read Replicas
  Razón: Alta concurrencia de lectura (productos), poca escritura

Customer Service:
  DB: PostgreSQL 15
  Razón: Transaccional, referential integrity

Search Service:
  DB: OpenSearch (Elasticsearch)
  Razón: Full-text search, faceted filters, relevance ranking
  Sincronización: Escucha ProductCreated events y índice en OpenSearch

Analytics Service:
  DB: AWS Redshift (data warehouse)
  Razón: Queries analíticos complejos (OLAP), no OLTP
  Sincronización: ETL nocturno desde RDS vía AWS Glue

Cache Service:
  DB: AWS ElastiCache (Redis)
  Razón: Cache de sesiones, rate limiting, leaderboards
  TTL: 1 hora

File Metadata Service:
  DB: AWS DynamoDB
  Razón: Key-value simple, alta escalabilidad, bajo costo
  Ejemplo: documentId → { s3Key, uploadedAt, size }
```

## Seguridad y Acceso

```yaml
# ✅ Usuarios de DB por servicio

Sales DB:
  User: sales_app_user
  Password: (almacenado en AWS Secrets Manager)
  Grants:
    - SELECT, INSERT, UPDATE, DELETE on sales.orders
    - SELECT, INSERT, UPDATE, DELETE on sales.order_lines
  Restrictions:
    - NO puede acceder fulfillment.*
    - NO puede acceder billing.*

Fulfillment DB:
  User: fulfillment_app_user
  Password: (almacenado en AWS Secrets Manager)
  Grants:
    - SELECT, INSERT, UPDATE, DELETE on fulfillment.shipments
  Restrictions:
    - NO puede acceder sales.*

# ✅ Network isolation con Security Groups

Sales Service ECS Task:
  Security Group: sg-sales-app
  Outbound: Permitir conexión a sales-db.rds (puerto 5432)
  Inbound: Solo ALB

Sales DB RDS:
  Security Group: sg-sales-db
  Inbound: Solo desde sg-sales-app (puerto 5432)

# ❌ Fulfillment Service NO puede conectar a Sales DB (bloqueado por Security Group)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** asignar base de datos dedicada a cada servicio
- **MUST** prohibir acceso directo a DB de otros servicios
- **MUST** usar APIs o eventos para obtener datos de otros servicios
- **MUST** mantener migraciones de schema independientes por servicio
- **MUST** configurar usuarios de DB separados por servicio
- **MUST** usar Security Groups para aislar acceso a nivel de red
- **MUST** denormalizar datos necesarios de otros servicios (consistency eventual)
- **MUST** almacenar connection string en secretos (AWS Secrets Manager)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar RDS instance separado por servicio (no solo schema separado)
- **SHOULD** publicar eventos cuando datos cambian (para sincronización)
- **SHOULD** implementar event handlers para actualizar datos denormalizados
- **SHOULD** monitorear latencia de queries (CloudWatch RDS metrics)
- **SHOULD** configurar backups independientes por DB
- **SHOULD** escalar DB según carga del servicio (no todos igual)

### MAY (Opcional)

- **MAY** usar tecnología de DB diferente por servicio (PostgreSQL, MongoDB, DynamoDB)
- **MAY** usar read replicas para servicios read-heavy
- **MAY** implementar cache (Redis) para reducir carga en DB
- **MAY** usar data warehouse (Redshift) para analytics separado

### MUST NOT (Prohibido)

- **MUST NOT** compartir tablas entre servicios
- **MUST NOT** hacer joins cross-service en queries
- **MUST NOT** usar foreign keys entre DBs de diferentes servicios
- **MUST NOT** acceder directamente DB de otro servicio (ni siquiera read-only)
- **MUST NOT** compartir usuario de DB entre servicios
- **MUST NOT** bloquear despliegue de un servicio por cambio de schema de otro
- **MUST NOT** usar transacciones distribuidas entre servicios (usar sagas en su lugar)

---

## Referencias

- [Lineamiento: Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md)
- Estándares relacionados:
  - [No Shared Database](./no-shared-database.md)
  - [Async Messaging](../mensajeria/async-messaging.md)
  - [API Contracts](../apis/api-contracts.md)
  - [Transactional Outbox](../../guias-arquitectura/transactional-outbox.md)
- ADRs:
  - [ADR-010: PostgreSQL como Base de Datos](../../decisiones-de-arquitectura/adr-010-postgresql-base-datos.md)
- Especificaciones:
  - [Microservices Patterns (Chris Richardson)](https://microservices.io/patterns/data/database-per-service.html)
  - [Building Microservices (Sam Newman)](https://samnewman.io/books/building_microservices/)
