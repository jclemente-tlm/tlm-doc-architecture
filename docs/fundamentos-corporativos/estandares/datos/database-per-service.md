---
id: database-per-service
sidebar_position: 7
title: Database per Service Pattern
description: Estándar para implementar database per service, garantizando aislamiento y autonomía de microservicios
---

# Estándar Técnico — Database per Service Pattern

---

## 1. Propósito

Garantizar que cada microservicio tenga su propia base de datos privada, logrando desacoplamiento, autonomía para deploy independiente y evitando contención de recursos entre servicios.

---

## 2. Alcance

**Aplica a:**

- Arquitecturas de microservicios
- Bounded contexts independientes
- Servicios con diferentes requisitos de BD (SQL vs NoSQL)
- Equipos autónomos con ownership claro
- Migraciones de monolito a microservicios

**No aplica a:**

- Aplicaciones monolíticas
- Servicios legacy en proceso de migración (temporal)
- Shared reference data (read-only)

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología | Versión mínima | Observaciones                        |
| ------------------- | ---------- | -------------- | ------------------------------------ |
| **Relacional**      | PostgreSQL | 14+            | Preferido para datos transaccionales |
| **Cache**           | Redis      | 7.0+           | Per-service cache instances          |
| **Migrations**      | EF Core    | 8.0+           | .NET native migrations               |
| **Connection Pool** | Npgsql     | 8.0+           | Connection pooling optimizado        |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Aislamiento de Base de Datos

- [ ] **Una BD por servicio** (schema separado mínimo, instancia separada ideal)
- [ ] **Credentials exclusivos** por servicio (no compartir connection strings)
- [ ] **Network isolation:** servicios no pueden conectarse a DBs de otros
- [ ] IAM policies/security groups limitan acceso por servicio

### Schema Ownership

- [ ] Servicio owner gestiona schema migrations
- [ ] Migrations automáticas en CI/CD pipeline
- [ ] Schema versionado (Flyway/DbUp)
- [ ] No manual schema changes en producción

### Queries Cross-Service

- [ ] **Prohibido JOIN entre schemas de servicios distintos**
- [ ] Datos cross-service obtenidos via APIs
- [ ] Denormalización cuando sea necesario para performance
- [ ] Read models/projections construidos via events

### Consistencia de Datos

- [ ] Transacciones ACID solo dentro de un servicio
- [ ] Consistencia eventual cross-service via events/sagas
- [ ] Compensating transactions para rollback distribuido
- [ ] Idempotency keys para retries

### Backup y DR

- [ ] Backups independientes por servicio
- [ ] RTO/RPO definidos por servicio
- [ ] Restore testing periódico
- [ ] Point-in-time recovery configurado

### Observabilidad

- [ ] Métricas de performance por BD
- [ ] Connection pool monitoring
- [ ] Query performance tracking (pg_stat_statements)
- [ ] Alertas de disk usage, connection saturation

---

## 5. Prohibiciones

- ❌ Shared database entre múltiples servicios
- ❌ Foreign keys entre schemas de servicios distintos
- ❌ Distributed transactions (2PC/XA) cross-service
- ❌ Direct SQL queries a BD de otro servicio
- ❌ Shared connection pool entre servicios
- ❌ Schema changes sin migrations versionadas
- ❌ Monolith database como fallback permanente

---

## 6. Configuración Mínima

### PostgreSQL - Separate Databases

```yaml
# docker-compose.yml (desarrollo local)
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - ./init-databases.sql:/docker-entrypoint-initdb.d/init.sql

# init-databases.sql
CREATE DATABASE orders_db;
CREATE DATABASE customers_db;
CREATE DATABASE inventory_db;
CREATE DATABASE payments_db;

-- Users con acceso limitado
CREATE USER orders_user WITH PASSWORD 'orders_pass';
GRANT ALL PRIVILEGES ON DATABASE orders_db TO orders_user;

CREATE USER customers_user WITH PASSWORD 'customers_pass';
GRANT ALL PRIVILEGES ON DATABASE customers_db TO customers_user;

CREATE USER inventory_user WITH PASSWORD 'inventory_pass';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
```

### Connection String per Service

```json
// appsettings.json - orders-service
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=postgres-orders.talma.internal;Database=orders_db;Username=orders_user;Password=***;Pooling=true;Minimum Pool Size=5;Maximum Pool Size=50"
  }
}

// appsettings.json - customers-service
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=postgres-customers.talma.internal;Database=customers_db;Username=customers_user;Password=***;Pooling=true;Minimum Pool Size=5;Maximum Pool Size=50"
  }
}
```

### Flyway Migrations

```yaml
# flyway.conf - orders-service
flyway.url=jdbc:postgresql://postgres-orders.talma.internal:5432/orders_db
flyway.user=orders_user
flyway.password=${FLYWAY_PASSWORD}
flyway.schemas=public
flyway.locations=filesystem:./migrations
flyway.baselineOnMigrate=true
```

```sql
-- migrations/V1__create_orders_schema.sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,  -- Referencia via API, no FK
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);

-- migrations/V2__add_order_items.sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,  -- Referencia via API, no FK
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

### EF Core DbContext per Service

```csharp
// Data/OrdersDbContext.cs
public class OrdersDbContext : DbContext
{
    public DbSet<Order> Orders { get; set; }
    public DbSet<OrderItem> OrderItems { get; set; }

    public OrdersDbContext(DbContextOptions<OrdersDbContext> options)
        : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Solo entidades de este bounded context
        modelBuilder.Entity<Order>(entity =>
        {
            entity.ToTable("orders");
            entity.HasKey(e => e.Id);

            // NO foreign key a otras bases de datos
            // customer_id es solo referencia
            entity.Property(e => e.CustomerId)
                .IsRequired();

            entity.HasMany(e => e.Items)
                .WithOne(e => e.Order)
                .HasForeignKey(e => e.OrderId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<OrderItem>(entity =>
        {
            entity.ToTable("order_items");
            entity.HasKey(e => e.Id);

            // NO foreign key a catalog_service
            entity.Property(e => e.ProductId)
                .IsRequired();
        });
    }
}

// Program.cs
builder.Services.AddDbContext<OrdersDbContext>(options =>
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        npgsqlOptions =>
        {
            npgsqlOptions.EnableRetryOnFailure(
                maxRetryCount: 3,
                maxRetryDelay: TimeSpan.FromSeconds(5),
                errorCodesToAdd: null);

            npgsqlOptions.CommandTimeout(30);
            npgsqlOptions.MigrationsHistoryTable("__EFMigrationsHistory", "public");
        }));
```

### Cross-Service Data via API

```csharp
// Services/OrderEnrichmentService.cs
public class OrderEnrichmentService
{
    private readonly OrdersDbContext _dbContext;
    private readonly CustomersApiClient _customersApi;
    private readonly CatalogApiClient _catalogApi;

    public async Task<EnrichedOrderDto> GetEnrichedOrderAsync(Guid orderId)
    {
        // 1. Leer de DB local (orders_db)
        var order = await _dbContext.Orders
            .Include(o => o.Items)
            .FirstOrDefaultAsync(o => o.Id == orderId);

        if (order == null)
            return null;

        // 2. Enriquecer con datos de otros servicios via API
        var customer = await _customersApi.GetCustomerAsync(order.CustomerId);

        var productIds = order.Items.Select(i => i.ProductId).ToList();
        var products = await _catalogApi.GetProductsByIdsAsync(productIds);

        // 3. Construir DTO enriquecido
        return new EnrichedOrderDto
        {
            Id = order.Id,
            TotalAmount = order.TotalAmount,
            Status = order.Status,

            // Data de customers-service
            Customer = new CustomerSummaryDto
            {
                Id = customer.Id,
                Name = customer.Name,
                Email = customer.Email
            },

            // Data de catalog-service
            Items = order.Items.Select(item =>
            {
                var product = products.First(p => p.Id == item.ProductId);
                return new EnrichedOrderItemDto
                {
                    ProductId = item.ProductId,
                    ProductName = product.Name,
                    Quantity = item.Quantity,
                    UnitPrice = item.UnitPrice,
                    Subtotal = item.Quantity * item.UnitPrice
                };
            }).ToList()
        };
    }
}
```

### Denormalization via Events

```csharp
// Escenario: Orders service necesita customer name frecuentemente
// Opción: denormalizar via events

// Domain/Entities/Order.cs
public class Order
{
    public Guid Id { get; set; }
    public Guid CustomerId { get; set; }

    // Denormalizado - actualizado via events
    public string CustomerName { get; set; }
    public string CustomerEmail { get; set; }

    public decimal TotalAmount { get; set; }
    public OrderStatus Status { get; set; }
}

// EventHandlers/CustomerUpdatedEventHandler.cs
public class CustomerUpdatedEventHandler : IEventHandler<CustomerUpdatedEvent>
{
    private readonly OrdersDbContext _dbContext;

    public async Task HandleAsync(CustomerUpdatedEvent @event)
    {
        // Actualizar datos denormalizados
        var orders = await _dbContext.Orders
            .Where(o => o.CustomerId == @event.CustomerId)
            .ToListAsync();

        foreach (var order in orders)
        {
            order.CustomerName = @event.Name;
            order.CustomerEmail = @event.Email;
        }

        await _dbContext.SaveChangesAsync();
    }
}
```

---

## 7. Ejemplos

### Saga Pattern para Consistencia Cross-Service

```csharp
// Saga: CreateOrderSaga
public class CreateOrderSaga
{
    private readonly OrdersDbContext _ordersDb;
    private readonly IInventoryApiClient _inventoryApi;
    private readonly IPaymentsApiClient _paymentsApi;
    private readonly IEventBus _eventBus;

    public async Task<SagaResult> ExecuteAsync(CreateOrderCommand command)
    {
        var sagaId = Guid.NewGuid();
        Order order = null;
        Guid? inventoryReservationId = null;
        Guid? paymentId = null;

        try
        {
            // Step 1: Crear orden (orders_db)
            order = new Order
            {
                Id = Guid.NewGuid(),
                CustomerId = command.CustomerId,
                Status = OrderStatus.Pending
            };

            _ordersDb.Orders.Add(order);
            await _ordersDb.SaveChangesAsync();

            // Step 2: Reservar inventario (inventory_db via API)
            inventoryReservationId = await _inventoryApi.ReserveInventoryAsync(new
            {
                OrderId = order.Id,
                Items = command.Items
            });

            // Step 3: Procesar pago (payments_db via API)
            paymentId = await _paymentsApi.ProcessPaymentAsync(new
            {
                OrderId = order.Id,
                Amount = command.TotalAmount,
                CustomerId = command.CustomerId
            });

            // Step 4: Confirmar orden
            order.Status = OrderStatus.Confirmed;
            await _ordersDb.SaveChangesAsync();

            await _eventBus.PublishAsync(new OrderCreatedEvent
            {
                OrderId = order.Id
            });

            return SagaResult.Success(order.Id);
        }
        catch (Exception ex)
        {
            // Compensating transactions
            if (paymentId.HasValue)
                await _paymentsApi.RefundPaymentAsync(paymentId.Value);

            if (inventoryReservationId.HasValue)
                await _inventoryApi.ReleaseReservationAsync(inventoryReservationId.Value);

            if (order != null)
            {
                order.Status = OrderStatus.Cancelled;
                await _ordersDb.SaveChangesAsync();
            }

            return SagaResult.Failure(ex);
        }
    }
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Cada servicio tiene BD independiente
- [ ] Connection strings no compartidos
- [ ] Network policies impiden acceso cross-service a DBs
- [ ] Schema migrations versionadas
- [ ] No foreign keys a otras bases de datos
- [ ] APIs documentadas para acceso cross-service
- [ ] Sagas implementadas para transacciones distribuidas

### Métricas

```promql
# Connection pool usage por servicio
pg_stat_database_numbackends{database="orders_db"}

# Query performance
rate(pg_stat_statements_total_exec_time[5m])

# Cross-service API latency
histogram_quantile(0.95, api_request_duration_seconds{target_service="customers"})
```

### Network Policy Validation

```yaml
# Kubernetes NetworkPolicy - bloquear acceso directo a BD
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-direct-db-access
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres-orders
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              service: orders-service # Solo orders-service puede conectarse
      ports:
        - protocol: TCP
          port: 5432
```

---

## 9. Referencias

**Teoría:**

- Sam Newman - "Building Microservices" (Chapter 4: Data)
- Chris Richardson - "Microservices Patterns"
- Martin Fowler - "Database per Service"

**Documentación:**

- [PostgreSQL Multi-tenancy](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [Flyway Documentation](https://flywaydb.org/documentation/)

**Buenas prácticas:**

- "Monolith to Microservices" (O'Reilly)
- "Database Reliability Engineering" (O'Reilly)
