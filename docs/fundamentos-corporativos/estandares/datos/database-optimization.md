---
id: database-optimization
sidebar_position: 3
title: Optimización de Consultas y Esquemas de Base de Datos
description: Prácticas para optimizar queries, índices y diseño de esquemas en PostgreSQL
---

# Optimización de Consultas y Esquemas de Base de Datos

## Contexto

Este estándar define prácticas para optimizar consultas y esquemas de PostgreSQL para minimizar latencia y maximizar throughput. Complementa el [lineamiento de Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md) especificando **cómo diseñar y optimizar** acceso a datos.

---

## Stack Tecnológico

| Componente        | Tecnología            | Versión | Uso                        |
| ----------------- | --------------------- | ------- | -------------------------- |
| **Database**      | PostgreSQL            | 15+     | Base de datos relacional   |
| **Cloud Service** | Amazon RDS            | -       | PostgreSQL managed service |
| **ORM**           | Entity Framework Core | 8.0+    | Object-relational mapping  |
| **Profiling**     | pg_stat_statements    | -       | Query performance analysis |

---

## Implementación Técnica

### Diseño de Índices

```sql
-- ❌ MAL: Sin índices (full table scan)
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    country_code CHAR(2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- ✅ BIEN: Índices para queries comunes
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    country_code CHAR(2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ✅ Índice para query por user
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- ✅ Índice compuesto para query por user + status
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- ✅ Índice parcial para orders pendientes (más eficiente)
CREATE INDEX idx_orders_pending ON orders(user_id, created_at)
WHERE status = 'pending';

-- ✅ Índice para range queries por fecha
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- ✅ Índice GIN para búsqueda fulltext (jsonb)
CREATE INDEX idx_orders_metadata_gin ON orders USING gin(metadata jsonb_path_ops);
```

### Estrategias de Indexación

```sql
-- ✅ B-tree index (default) - Para equality y range queries
CREATE INDEX idx_orders_created_at ON orders(created_at);
-- Soporta: WHERE created_at = '...' AND created_at > '...'

-- ✅ Hash index - Solo para equality (más rápido que B-tree)
CREATE INDEX idx_orders_order_number_hash ON orders USING hash(order_number);
-- Soporta: WHERE order_number = '...'
-- NO soporta: WHERE order_number > '...'

-- ✅ GIN index - Para arrays, JSONB, full-text search
CREATE INDEX idx_products_tags_gin ON products USING gin(tags);
-- Soporta: WHERE tags @> ARRAY['electronics']

-- ✅ GiST index - Para geospatial, range types
CREATE INDEX idx_stores_location_gist ON stores USING gist(location);
-- Soporta: WHERE location <-> point(x,y) < distance

-- ✅ Covering index (INCLUDE) - Evita table lookup
CREATE INDEX idx_orders_user_covering ON orders(user_id)
INCLUDE (status, total_amount, created_at);
-- Query resuelto completamente con índice (index-only scan)
```

### Optimización de Queries

```csharp
// ❌ MAL: N+1 query problem
public async Task<List<OrderDto>> GetOrdersAsync(Guid userId)
{
    var orders = await _context.Orders
        .Where(o => o.UserId == userId)
        .ToListAsync();

    // ❌ 1 query por cada order (N queries adicionales)
    foreach (var order in orders)
    {
        order.Items = await _context.OrderItems
            .Where(i => i.OrderId == order.Id)
            .ToListAsync();
    }

    return orders;
}

// ✅ BIEN: Eager loading con Include
public async Task<List<OrderDto>> GetOrdersAsync(Guid userId)
{
    return await _context.Orders
        .Where(o => o.UserId == userId)
        .Include(o => o.Items)  // ✅ JOIN en single query
        .ThenInclude(i => i.Product)  // ✅ Nested include
        .ToListAsync();
}

// ✅ MEJOR: Projection con Select (solo campos necesarios)
public async Task<List<OrderSummaryDto>> GetOrderSummariesAsync(Guid userId)
{
    return await _context.Orders
        .Where(o => o.UserId == userId)
        .Select(o => new OrderSummaryDto
        {
            OrderId = o.Id,
            Status = o.Status,
            TotalAmount = o.TotalAmount,
            ItemCount = o.Items.Count,  // ✅ Calculado en DB
            CreatedAt = o.CreatedAt
        })
        .ToListAsync();

    // ✅ Menos datos transferidos, más rápido
}
```

### Paginación Eficiente

```csharp
// ❌ MAL: OFFSET con valores grandes (lento)
public async Task<List<Order>> GetOrdersPageAsync(int pageNumber, int pageSize)
{
    return await _context.Orders
        .OrderBy(o => o.CreatedAt)
        .Skip(pageNumber * pageSize)  // ❌ Lento con page 100+
        .Take(pageSize)
        .ToListAsync();
}

// ✅ BIEN: Keyset pagination (cursor-based)
public async Task<List<Order>> GetOrdersAfterAsync(DateTime? after, int pageSize)
{
    var query = _context.Orders.AsQueryable();

    if (after.HasValue)
    {
        // ✅ WHERE created_at > cursor (usa índice eficientemente)
        query = query.Where(o => o.CreatedAt > after.Value);
    }

    return await query
        .OrderBy(o => o.CreatedAt)
        .Take(pageSize)
        .ToListAsync();
}

// SQL generado:
// SELECT * FROM orders
// WHERE created_at > '2024-01-01 10:00:00'
// ORDER BY created_at
// LIMIT 20;  -- ✅ Usa idx_orders_created_at eficientemente
```

### Optimización de Agregaciones

```sql
-- ❌ MAL: Contar todas las filas (lento en tablas grandes)
SELECT COUNT(*) FROM orders WHERE status = 'pending';

-- ✅ BIEN: Estimación rápida con pg_class
SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'orders';

-- ✅ Índice parcial para conteos frecuentes
CREATE INDEX idx_orders_pending_count ON orders(order_id) WHERE status = 'pending';

-- Ahora este query es rápido (index-only scan):
SELECT COUNT(*) FROM orders WHERE status = 'pending';
```

```csharp
// ✅ Agregaciones eficientes con GroupBy
public async Task<Dictionary<string, int>> GetOrderCountByStatusAsync()
{
    return await _context.Orders
        .GroupBy(o => o.Status)
        .Select(g => new { Status = g.Key, Count = g.Count() })
        .ToDictionaryAsync(x => x.Status, x => x.Count);

    // SQL: SELECT status, COUNT(*) FROM orders GROUP BY status;
}

// ✅ Usar db computed columns para agregaciones frecuentes
public class Order
{
    public Guid Id { get; set; }
    public List<OrderItem> Items { get; set; }

    // ✅ Computed column en DB (actualizada por trigger)
    public decimal TotalAmount { get; set; }
}

// Migration:
/*
ALTER TABLE orders
ADD COLUMN total_amount DECIMAL(10,2)
GENERATED ALWAYS AS (
    (SELECT COALESCE(SUM(quantity * unit_price), 0)
     FROM order_items
     WHERE order_id = orders.order_id)
) STORED;

CREATE INDEX idx_orders_total_amount ON orders(total_amount);
*/
```

### Batch Operations

```csharp
// ❌ MAL: Insertar uno por uno (N roundtrips)
public async Task CreateOrdersAsync(List<CreateOrderRequest> requests)
{
    foreach (var request in requests)
    {
        var order = new Order { ... };
        _context.Orders.Add(order);
        await _context.SaveChangesAsync();  // ❌ 1 roundtrip por order
    }
}

// ✅ BIEN: Batch insert (1 roundtrip)
public async Task CreateOrdersAsync(List<CreateOrderRequest> requests)
{
    var orders = requests.Select(r => new Order { ... }).ToList();

    _context.Orders.AddRange(orders);  // ✅ Batch add
    await _context.SaveChangesAsync();  // ✅ Single roundtrip

    // SQL: INSERT INTO orders VALUES (...), (...), (...);
}

// ✅ MEJOR: Bulk insert para grandes volúmenes (EF Core Bulk Extensions)
public async Task BulkCreateOrdersAsync(List<CreateOrderRequest> requests)
{
    var orders = requests.Select(r => new Order { ... }).ToList();

    await _context.BulkInsertAsync(orders);  // ✅ Optimizado para bulk
}
```

### Optimización con Raw SQL

```csharp
// ✅ Raw SQL para queries complejos (mejor performance)
public async Task<List<OrderStatistics>> GetOrderStatisticsAsync(DateTime from, DateTime to)
{
    var sql = @"
        SELECT
            DATE_TRUNC('day', created_at) as date,
            status,
            COUNT(*) as order_count,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_order_value
        FROM orders
        WHERE created_at BETWEEN @from AND @to
        GROUP BY DATE_TRUNC('day', created_at), status
        ORDER BY date DESC, status";

    return await _context.Database
        .SqlQueryRaw<OrderStatistics>(sql,
            new NpgsqlParameter("@from", from),
            new NpgsqlParameter("@to", to))
        .ToListAsync();
}
```

### Particionamiento de Tablas

```sql
-- ✅ Particionamiento por rango (por fecha)
CREATE TABLE orders (
    order_id UUID NOT NULL,
    user_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (order_id, created_at)
) PARTITION BY RANGE (created_at);

-- Crear particiones por mes
CREATE TABLE orders_2024_01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE orders_2024_03 PARTITION OF orders
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- ✅ Query automáticamente usa partición correcta (partition pruning)
SELECT * FROM orders WHERE created_at BETWEEN '2024-02-01' AND '2024-02-28';
-- Solo escanea orders_2024_02
```

### Configuración de PostgreSQL (RDS)

```hcl
# RDS Parameter Group
resource "aws_db_parameter_group" "postgres" {
  name   = "tlm-postgres-params"
  family = "postgres15"

  # ✅ Shared buffers (25% de RAM)
  parameter {
    name  = "shared_buffers"
    value = "{DBInstanceClassMemory/4}"
  }

  # ✅ Effective cache size (50-75% de RAM)
  parameter {
    name  = "effective_cache_size"
    value = "{DBInstanceClassMemory*3/4}"
  }

  # ✅ Work mem para sorts/aggregations (por query)
  parameter {
    name  = "work_mem"
    value = "16384"  # 16 MB
  }

  # ✅ Maintenance work mem (para VACUUM, CREATE INDEX)
  parameter {
    name  = "maintenance_work_mem"
    value = "524288"  # 512 MB
  }

  # ✅ Max connections
  parameter {
    name  = "max_connections"
    value = "200"
  }

  # ✅ Habilitar pg_stat_statements
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  # ✅ Query planning
  parameter {
    name  = "random_page_cost"
    value = "1.1"  # Para SSD (default 4.0 para HDD)
  }
}
```

### Monitoreo de Performance

```sql
-- ✅ Habilitar pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top 10 queries más lentos
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Queries con más tiempo total
SELECT
    query,
    calls,
    total_exec_time,
    (total_exec_time / calls) as avg_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Índices no utilizados (candidatos para eliminación)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Tablas que necesitan VACUUM
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup, 0), 2) as dead_tup_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### EXPLAIN ANALYZE

```sql
-- ✅ Analizar plan de ejecución
EXPLAIN ANALYZE
SELECT o.order_id, o.status, u.email
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.created_at > NOW() - INTERVAL '7 days'
AND o.status = 'pending';

/*
Resultado:
Nested Loop  (cost=0.57..245.23 rows=15 width=53) (actual time=0.123..2.456 rows=142 loops=1)
  ->  Bitmap Heap Scan on orders o  (cost=4.43..98.12 rows=15 width=37) (actual time=0.089..1.234 rows=142 loops=1)
        Recheck Cond: (created_at > (now() - '7 days'::interval))
        Filter: ((status)::text = 'pending'::text)
        Heap Blocks: exact=42
        ->  Bitmap Index Scan on idx_orders_created_at  (cost=0.00..4.43 rows=67 width=0) (actual time=0.067..0.067 rows=234 loops=1)
              Index Cond: (created_at > (now() - '7 days'::interval))
  ->  Index Scan using users_pkey on users u  (cost=0.14..9.81 rows=1 width=24) (actual time=0.008..0.008 rows=1 loops=142)
        Index Cond: (user_id = o.user_id)
Planning Time: 0.456 ms
Execution Time: 2.789 ms
*/

-- ✅ Buscar Seq Scan (full table scan) - candidato para índice
-- ✅ Verificar actual time vs estimated rows
-- ✅ cost bajo pero actual time alto = problema de estimación
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** crear índices para todas las foreign keys
- **MUST** crear índices para columnas usadas en WHERE/JOIN frecuentemente
- **MUST** usar eager loading (Include) para evitar N+1 queries
- **MUST** usar paginación (limit/offset o keyset)
- **MUST** habilitar pg_stat_statements para monitoreo
- **MUST** ejecutar EXPLAIN ANALYZE para queries > 100ms
- **MUST** usar batch operations para inserts/updates múltiples

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar índices parciales para queries con WHERE constante
- **SHOULD** usar projection (Select) en lugar de entidades completas
- **SHOULD** usar keyset pagination en lugar de offset para grandes datasets
- **SHOULD** particionar tablas > 100M filas
- **SHOULD** crear índices covering (INCLUDE) para queries críticos
- **SHOULD** monitorear índices no utilizados y eliminarlos
- **SHOULD** configurar auto-vacuum apropiadamente

### MAY (Opcional)

- **MAY** usar materialized views para agregaciones complejas
- **MAY** usar GIN/GiST indexes para búsquedas especializadas
- **MAY** implementar read replicas para queries de lectura
- **MAY** usar conexiones de solo lectura para reportes
- **MAY** implementar sharding para escalabilidad extrema

### MUST NOT (Prohibido)

- **MUST NOT** usar SELECT \* en production code
- **MUST NOT** ignorar N+1 query problems
- **MUST NOT** ejecutar queries sin LIMIT en production
- **MUST NOT** crear índices sin analizar query patterns
- **MUST NOT** usar OFFSET para paginación en grandes datasets
- **MUST NOT** ignorar warnings de EXPLAIN ANALYZE

---

## Referencias

- [Lineamiento: Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md)
- Estándares relacionados:
  - [Connection Pooling](connection-pooling.md)
  - [Estrategias de Caché](../../estandares/arquitectura/caching-strategies.md)
- ADRs:
  - [ADR-010: PostgreSQL](../../../decisiones-de-arquitectura/adr-010-postgresql-base-datos.md)
- Especificaciones:
  - [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
  - [EF Core Performance](https://learn.microsoft.com/en-us/ef/core/performance/)
  - [Use The Index, Luke](https://use-the-index-luke.com/)
