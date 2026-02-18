---
id: no-shared-database
sidebar_position: 2
title: No Shared Database Anti-Pattern
description: Prohibir compartir bases de datos o esquemas entre servicios para preservar autonomía
---

# No Shared Database Anti-Pattern

## Contexto

Este estándar prohíbe explícitamente el anti-pattern de **shared database**: múltiples servicios accediendo directamente a las mismas tablas. Complementa el estándar [Database per Service](./database-per-service.md) y el [lineamiento de Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md) estableciendo **restricciones claras** sobre acceso a datos.

---

## El Anti-Pattern

### Shared Database

```yaml
# ❌ Shared Database Anti-Pattern

Definición:
  Múltiples servicios acceden directamente a las mismas tablas en una base de datos compartida.

Variantes del anti-pattern:
  1. ❌ Shared Database, Shared Schema:
     - Todos los servicios usan misma DB y mismo schema
     - Ejemplo: Sales, Fulfillment, Billing todos acceden `dbo.orders`

  2. ❌ Shared Database, Separate Schemas:
     - Todos los servicios en misma DB, schemas diferentes
     - Ejemplo: `sales.orders`, `fulfillment.shipments` en misma instancia PostgreSQL
     - Problema: Aunque mejor, sigue habiendo acoplamiento operativo

  3. ❌ Service-Specific Database with Cross-Service Access:
     - Cada servicio tiene su DB, pero otros servicios acceden directamente
     - Ejemplo: Fulfillment Service consulta directamente `sales_db.orders`

Todas estas variantes rompen autonomía y DEBEN evitarse.
```

### Ejemplo del Anti-Pattern

```csharp
// ❌ MALO: Tres servicios accediendo misma tabla `orders`

// 1. Sales Service
public class SalesService
{
    public async Task<Order> CreateOrderAsync(CreateOrderDto dto)
    {
        var query = "INSERT INTO dbo.orders (order_id, customer_id, status) VALUES (@id, @customerId, 'Draft')";
        await _connection.ExecuteAsync(query, new { id = Guid.NewGuid(), dto.CustomerId });
    }

    public async Task<Order> GetOrderAsync(Guid orderId)
    {
        return await _connection.QuerySingleAsync<Order>(
            "SELECT * FROM dbo.orders WHERE order_id = @orderId",
            new { orderId });
    }
}

// 2. Fulfillment Service (accede MISMA tabla)
public class FulfillmentService
{
    public async Task<List<Order>> GetPendingShipmentsAsync()
    {
        // ❌ Accede directamente tabla `orders` de Sales
        var query = @"
            SELECT * FROM dbo.orders
            WHERE status = 'Approved'
              AND shipment_status IS NULL";

        return await _connection.QueryAsync<Order>(query);
    }

    public async Task MarkAsShippedAsync(Guid orderId, string trackingNumber)
    {
        // ❌ Actualiza directamente tabla de Sales
        var query = "UPDATE dbo.orders SET shipment_status = 'Shipped', tracking_number = @tracking WHERE order_id = @orderId";
        await _connection.ExecuteAsync(query, new { orderId, tracking = trackingNumber });
    }
}

// 3. Billing Service (también accede MISMA tabla)
public class BillingService
{
    public async Task<decimal> GetTotalRevenueAsync()
    {
        // ❌ Accede directamente tabla `orders` para reportes
        return await _connection.ExecuteScalarAsync<decimal>(
            "SELECT SUM(total_amount) FROM dbo.orders WHERE status = 'Delivered'");
    }
}

// Problemas:
// 1. ❌ Sales no puede cambiar schema de `orders` sin romper Fulfillment y Billing
// 2. ❌ Lock contention: 3 servicios compiten por mismas filas
// 3. ❌ No se puede desplegar independientemente
// 4. ❌ Falla en DB afecta a todos los servicios
// 5. ❌ No se puede escalar DB independientemente por servicio
// 6. ❌ Imposible usar tecnologías diferentes (todos forzados a misma DB)
```

## Problemas del Shared Database

### 1. Acoplamiento de Schema

```yaml
# ❌ Problema: Cambio de schema rompe múltiples servicios

Escenario:
  Sales necesita agregar columna `discount_amount` a tabla `orders`.

Con Shared Database:
  1. Sales agrega columna: ALTER TABLE orders ADD COLUMN discount_amount DECIMAL
  2. ❌ Fulfillment rompe: SELECT * FROM orders /* ahora retorna columna extra */
  3. ❌ Billing rompe: Queries sin discount_amount fallan validación
  4. ❌ Requiere despliegue coordinado de 3 servicios
  5. ❌ Rollback complejo si algo falla

Con Database per Service:
  1. Sales agrega columna en su DB: ✅ Solo afecta Sales
  2. ✅ Fulfillment no se entera (no accede Sales DB)
  3. ✅ Billing no se entera
  4. ✅ Despliegue solo de Sales
  5. ✅ Rollback simple (solo Sales)
```

### 2. Lock Contention

```csharp
// ❌ Problema: Lock contention entre servicios

// Scenario: Black Friday con alta concurrencia

// Sales Service (1000 req/sec)
await _connection.ExecuteAsync(
    "UPDATE orders SET status = 'Pending' WHERE order_id = @id",
    new { id });  // ❌ Row lock

// Fulfillment Service (500 req/sec)
await _connection.ExecuteAsync(
    "UPDATE orders SET shipment_status = 'Processing' WHERE order_id = @id",
    new { id });  // ❌ Espera lock de Sales!

// Billing Service (200 req/sec)
var total = await _connection.ExecuteScalarAsync<decimal>(
    "SELECT SUM(total_amount) FROM orders WHERE status = 'Delivered'");
    // ❌ Table scan con locks!

// Resultado:
// - Deadlocks entre servicios
// - Performance degradada por lock contention
// - Timeouts en queries
// - Escalamiento vertical (no horizontal) de DB
```

### 3. Fallas en Cascada

```yaml
# ❌ Problema: Falla en DB derriba todos los servicios

Escenario: DB sufre high CPU usage por query mal optimizado

Con Shared Database:
  1. Billing ejecuta query lento: SELECT * FROM orders (sin WHERE)
  2. ❌ CPU de DB sube a 100%
  3. ❌ Sales Service empieza a timear out (no puede crear orders)
  4. ❌ Fulfillment Service empieza a timear out (no puede actualizar shipments)
  5. ❌ Todos los servicios caídos por culpa de Billing

Con Database per Service:
  1. Billing ejecuta query lento en Billing DB
  2. ✅ CPU de Billing DB sube a 100%
  3. ✅ Sales DB no afectado (instance separada)
  4. ✅ Fulfillment DB no afectado
  5. ✅ Solo Billing Service degradado (otros funcionan normal)

✅ Blast Radio contenido: falla aislada en un servicio
```

### 4. Imposibilidad de Deployment Independiente

```yaml
# ❌ Problema: Despliegues requieren coordinación

Escenario: Sales necesita agregar validación de stock antes de crear order

Cambio en Sales:
  - Code: Validar Product.stock_quantity > order.quantity
  - Schema: ALTER TABLE orders ADD COLUMN stock_validated_at TIMESTAMP
  - Deploy: Sales Service v2.5.0

Con Shared Database:
  Paso 1: Aplicar migration (ADD COLUMN stock_validated_at)
    ❌ Problema: Fulfillment Service v2.4.0 no sabe de esta columna
    ❌ SELECT * FROM orders rompe deserialización en Fulfillment

  Paso 2: Desplegar Fulfillment Service v2.4.1 (compatible con nueva columna)
    ❌ Requiere coordinación con equipo de Fulfillment
    ❌ Requiere window de deployment sincronizado

  Paso 3: Desplegar Sales Service v2.5.0
    ❌ Solo después de que Fulfillment está desplegado

  ❌ 3 equipos coordinando deployment
  ❌ Ventana de deployment grande (30-60 minutos)
  ❌ Rollback complejo (requiere rollback de 3 servicios)

Con Database per Service:
  Paso 1: Sales aplica migration en Sales DB ✅
  Paso 2: Sales despliega v2.5.0 ✅

  ✅ Fulfillment no se entera (no accede Sales DB)
  ✅ Sin coordinación requerida
  ✅ Deployment en 5 minutos
  ✅ Rollback simple (solo Sales)
```

## Refactoring: De Shared DB a Database per Service

### Estrategia de Migración

```yaml
# ✅ Pasos para refactorizar de Shared DB a Database per Service

Fase 1: Identificar Ownership
  1. Listar todas las tablas en shared DB
  2. Asignar ownership de cada tabla a UN servicio
  3. Documentar qué servicios acceden cada tabla actualmente

  Ejemplo:
    - orders → Owner: Sales Service
      - Accessed by: Sales (R/W), Fulfillment (R), Billing (R)
    - shipments → Owner: Fulfillment Service
      - Accessed by: Fulfillment (R/W), Sales (R)
    - invoices → Owner: Billing Service
      - Accessed by: Billing (R/W), Sales (R)

Fase 2: Introducir APIs
  1. Owner expone API para datos de su tabla
  2. Otros servicios migran de direct DB access a API calls
  3. Validar que APIs cubren todos los casos de uso

  Ejemplo:
    Sales expone: GET /api/orders/{id}, POST /api/orders
    Fulfillment migra: De "SELECT * FROM orders" a "HTTP GET /api/orders/{id}"

Fase 3: Implementar Event-Driven Sync
  1. Owner publica eventos cuando datos cambian
  2. Consumers subscriben y actualizan copias locales
  3. Eliminar queries cross-service (usar datos locales)

  Ejemplo:
    Sales publica: OrderCreated, OrderApproved
    Fulfillment escucha: Crea shipment cuando OrderApproved
    Fulfillment mantiene: Tabla local fulfillment.order_snapshots

Fase 4: Split Physical Databases
  1. Crear DB separada para cada servicio
  2. Migrar datos (dump/restore de tablas owned)
  3. Actualizar connection strings
  4. Prohibir acceso cross-database (Security Groups)

  Ejemplo:
    - Sales DB: orders, order_lines
    - Fulfillment DB: shipments, packages, order_snapshots (denorm)
    - Billing DB: invoices, payments

Fase 5: Cleanup
  1. Eliminar foreign keys cross-service
  2. Remover usuarios de DB con acceso cross-service
  3. Eliminar queries legacy (directo a otras DBs)
```

### Ejemplo de Migración

```csharp
// Paso 1: ANTES (Shared DB)

public class FulfillmentService
{
    private readonly IDbConnection _sharedDbConnection;

    public async Task<List<Order>> GetApprovedOrdersAsync()
    {
        // ❌ Direct DB access a tabla de Sales
        return await _sharedDbConnection.QueryAsync<Order>(
            "SELECT * FROM dbo.orders WHERE status = 'Approved'");
    }
}

// Paso 2: INTERMEDIO (API Calls)

public class FulfillmentService
{
    private readonly ISalesServiceClient _salesClient;  // ✅ HTTP client

    public async Task<List<OrderDto>> GetApprovedOrdersAsync()
    {
        // ✅ API call en lugar de direct DB access
        return await _salesClient.GetOrdersByStatusAsync("Approved");
    }
}

// Sales Service expone API:

[ApiController]
[Route("api/orders")]
public class OrdersController : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetByStatus([FromQuery] string status)
    {
        var orders = await _orderRepo.GetByStatusAsync(status);
        return Ok(orders.Select(o => o.ToDto()));
    }
}

// Paso 3: FINAL (Event-Driven + Local Data)

// Sales publica evento:
public class Order
{
    public void Approve(Guid approvedBy)
    {
        Status = OrderStatus.Approved;
        AddDomainEvent(new OrderApproved(OrderId, CustomerId, Total));
    }
}

// Fulfillment escucha evento y crea copia local:
public class OrderApprovedEventHandler : IEventHandler<OrderApproved>
{
    private readonly IOrderSnapshotRepository _snapshotRepo;

    public async Task HandleAsync(OrderApproved evt)
    {
        // ✅ Crear snapshot local en Fulfillment DB
        var snapshot = new OrderSnapshot
        {
            OrderId = evt.OrderId,
            CustomerId = evt.CustomerId,
            TotalAmount = evt.Total,
            ApprovedAt = DateTime.UtcNow
        };

        await _snapshotRepo.SaveAsync(snapshot);
    }
}

// Fulfillment ahora consulta su propia DB:
public class FulfillmentService
{
    private readonly FulfillmentDbContext _fulfillmentDb;  // ✅ Own DB

    public async Task<List<OrderSnapshot>> GetApprovedOrdersAsync()
    {
        // ✅ Query local (Fulfillment DB)
        return await _fulfillmentDb.OrderSnapshots
            .Where(o => o.Status == "Approved")
            .ToListAsync();
    }
}

// ✅ Resultado:
// - Fulfillment ya no accede Sales DB
// - Sales puede cambiar schema sin afectar Fulfillment
// - Deployment independiente
```

## Detección y Prevención

### Code Review Checklist

```yaml
# ✅ Checklist en code review para detectar violaciones

❌ RED FLAGS (rechazar PR):

1. Multiple DbContext en un servicio:
   public class OrderService {
       private readonly SalesDbContext _salesDb;
       private readonly FulfillmentDbContext _fulfillmentDb;  // ❌ NO!
   }

2. Connection string de otro servicio:
   appsettings.json:
     "ConnectionStrings": {
       "OwnDb": "...",
       "OtherServiceDb": "..."  // ❌ NO!
     }

3. Query cross-schema sin ownership:
   SELECT * FROM other_service_schema.table  // ❌ NO!

4. Foreign keys entre servicios:
   ALTER TABLE fulfillment.shipments
   ADD CONSTRAINT fk_order
   FOREIGN KEY (order_id) REFERENCES sales.orders(order_id);  // ❌ NO!

5. Joins cross-service:
   SELECT o.*, s.tracking_number
   FROM sales.orders o
   JOIN fulfillment.shipments s ON s.order_id = o.order_id;  // ❌ NO!

✅ CORRECTOS (aprobar PR):

1. Solo usa su propio DbContext:
   public class OrderService {
       private readonly SalesDbContext _salesDb;  // ✅ Solo Sales DB
   }

2. Llama API de otro servicio:
   var shipment = await _fulfillmentClient.GetShipmentAsync(orderId);  // ✅

3. Subscribción a eventos:
   public class OrderApprovedHandler : IEventHandler<OrderApproved> { }  // ✅

4. Denormalización con evento:
   order.UpdateShipmentStatus(evt.Status);  // ✅ Copia local actualizada
```

### Herramientas Automáticas

```csharp
// ✅ Unit test para detectar violaciones

[Fact]
public void Services_Should_Not_Reference_Other_Service_DbContexts()
{
    // Arrange
    var assembly = typeof(SalesService).Assembly;

    // Act: Buscar tipos que usan DbContext de otro servicio
    var violations = assembly.GetTypes()
        .Where(t => t.IsClass && !t.IsAbstract)
        .SelectMany(t => t.GetFields(BindingFlags.Instance | BindingFlags.NonPublic))
        .Where(f => f.FieldType.IsSubclassOf(typeof(DbContext)))
        .Where(f => !f.FieldType.Name.StartsWith("Sales"))  // Solo permitir SalesDbContext
        .ToList();

    // Assert
    Assert.Empty(violations);  // No debe haber DbContext de otros servicios
}

[Fact]
public void ConnectionStrings_Should_Only_Have_Own_Database()
{
    // Arrange
    var config = new ConfigurationBuilder()
        .AddJsonFile("appsettings.json")
        .Build();

    var connectionStrings = config.GetSection("ConnectionStrings")
        .GetChildren()
        .Select(c => c.Key)
        .ToList();

    // Assert: Solo debe haber connection string del servicio propio
    Assert.Single(connectionStrings);
    Assert.Equal("SalesDb", connectionStrings[0]);
}
```

## Excepciones Válidas

```yaml
# ⚠️ Casos donde shared DB PUEDE ser aceptable (temporalmente)

1. Migración en Progreso:
  - Durante refactoring de monolito a microservicios
  - Timeboxed: Max 6 meses
  - Plan documentado de separación

2. Reporting / Analytics:
  - Read-only access para reportes
  - Mejor alternativa: Replicar a data warehouse (Redshift)
  - Via read replica (no production DB)

3. Legacy System Integration:
  - Sistema legacy no se puede cambiar
  - Solución: Anti-Corruption Layer (ACL) con sincronización
  - Solo UN servicio accede legacy DB (el ACL)

❌ NO son excepciones válidas:
  - "Es más fácil hacer JOIN"
  - "Ya tenemos shared DB funcionando"
  - "Eventos son muy complejos"
  - "No tenemos tiempo para refactorizar"
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** prohibir acceso directo a base de datos de otros servicios
- **MUST** prohibir foreign keys entre bases de datos de diferentes servicios
- **MUST** prohibir joins cross-service en queries
- **MUST** prohibir compartir usuarios de DB entre servicios
- **MUST** usar APIs o eventos para obtener datos de otros servicios
- **MUST** implementar denormalización cuando se necesitan datos de otros servicios
- **MUST** validar en code review que no se accede DB de otros servicios
- **MUST** usar Security Groups para bloquear acceso cross-service a nivel de red

### SHOULD (Fuertemente recomendado)

- **SHOULD** migrar de shared DB a database per service en máximo 6 meses
- **SHOULD** documentar plan de migración con fases específicas
- **SHOULD** crear unit tests para detectar violaciones
- **SHOULD** usar read replicas para reporting (no production DB)
- **SHOULD** implementar Anti-Corruption Layer para legacy systems

### MAY (Opcional)

- **MAY** usar data warehouse (Redshift) para analytics cross-service
- **MAY** mantener read-only access temporal durante migración
- **MAY** usar service mesh para restringir acceso a nivel de red

### MUST NOT (Prohibido)

- **MUST NOT** acceder directamente base de datos de otro servicio
- **MUST NOT** crear foreign keys entre servicios
- **MUST NOT** hacer joins entre tablas de diferentes servicios
- **MUST NOT** compartir connection strings entre servicios
- **MUST NOT** usar shared database como solución permanente sin plan de migración
- **MUST NOT** ignorar violaciones en code review por "urgencia"

---

##Referencias

- [Lineamiento: Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md)
- Estándares relacionados:
  - [Database per Service](./database-per-service.md)
  - [Async Messaging](../mensajeria/async-messaging.md)
  - [API Contracts](../apis/api-contracts.md)
- Especificaciones:
  - [Microservices Patterns (Chris Richardson)](https://microservices.io/patterns/data/shared-database.html)
  - [Building Microservices (Sam Newman) - Chapter 4: Integration](https://samnewman.io/books/building_microservices/)
