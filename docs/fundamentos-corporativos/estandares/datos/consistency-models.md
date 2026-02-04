---
id: consistency-models
sidebar_position: 2
title: Consistency Models
description: Estándar para selección y configuración de modelos de consistencia (eventual, strong, causal) según CAP y PACELC
---

# Estándar Técnico — Consistency Models

---

## 1. Propósito

Establecer criterios para seleccionar el modelo de consistencia apropiado según requisitos de negocio, balanceando disponibilidad, latencia y consistencia conforme a CAP y PACELC theorem.

---

## 2. Alcance

**Aplica a:**

- Diseño de bases de datos distribuidas
- Replicación multi-región
- Microservicios con datos compartidos
- Event-driven architectures
- Cache distribuido
- APIs críticas de negocio

**No aplica a:**

- Sistemas single-instance
- Bases de datos en memoria no replicadas
- Logs y telemetría
- Datos completamente inmutables

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología | Consistencia        | Observaciones                  |
| -------------- | ---------- | ------------------- | ------------------------------ |
| **Relacional** | PostgreSQL | Strong (ACID)       | Default para datos críticos    |
| **Cache**      | Redis      | Eventual            | Con invalidación activa        |
| **Messaging**  | Kafka      | Eventual (at-least) | Exactly-once con transacciones |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Selección de Modelo

- [ ] **Strong Consistency:** para transacciones financieras, inventario crítico
- [ ] **Causal Consistency:** cuando orden de eventos importa (chat, feeds)
- [ ] **Eventual Consistency:** aceptable para métricas, analytics, cache
- [ ] **Session Consistency:** mismo usuario ve sus escrituras inmediatamente
- [ ] Documentar decisión en ADR por bounded context

### Trade-offs Documentados

- [ ] Análisis CAP: Partition tolerance + (Consistency XOR Availability)
- [ ] Análisis PACELC: Si partition → (Availability vs Consistency), else (Latency vs Consistency)
- [ ] RTO/RPO definidos para datos críticos
- [ ] SLO de staleness para eventual consistency

### Configuración Explícita

- [ ] **PostgreSQL:** isolation level configurado (default: READ COMMITTED)
- [ ] **DynamoDB:** elegir entre strongly consistent reads vs eventually
- [ ] **Cosmos DB:** elegir nivel de consistencia por request
- [ ] **Redis:** TTL y estrategia de invalidación explícita
- [ ] **Kafka:** acks=all para strong ordering, min.insync.replicas=2

### Manejo de Lecturas

- [ ] Read-your-writes consistency para operaciones de usuario
- [ ] Monotonic reads (no retroceder en versiones)
- [ ] Bounded staleness con max lag time definido
- [ ] Stale reads permitidas solo si UI lo indica

### Detección de Inconsistencias

- [ ] Validar versiones antes de actualizar (optimistic locking)
- [ ] Detectar y loggear lecturas stale fuera de SLO
- [ ] Alertas cuando replication lag excede umbrales
- [ ] Reconciliación periódica de datos críticos

---

## 5. Prohibiciones

- ❌ Asumir strong consistency sin verificar configuración
- ❌ Mezclar modelos de consistencia sin documentar
- ❌ Ignorar replication lag en decisiones críticas
- ❌ Eventual consistency para transacciones financieras
- ❌ Strong consistency innecesaria (pagar costo sin beneficio)
- ❌ Cache sin estrategia de invalidación
- ❌ No documentar staleness tolerance del negocio

---

## 6. Configuración Mínima

### PostgreSQL - Transaction Isolation

```csharp
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=talma;Username=app;Password=***;Command Timeout=30;Pooling=true;Minimum Pool Size=5;Maximum Pool Size=100"
  },
  "Database": {
    "DefaultIsolationLevel": "ReadCommitted",
    "CriticalOperationsIsolationLevel": "Serializable"
  }
}

// DbContext configuration
public class TalmaDbContext : DbContext
{
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.UseNpgsql(
            connectionString,
            npgsqlOptions =>
            {
                npgsqlOptions.EnableRetryOnFailure(
                    maxRetryCount: 3,
                    maxRetryDelay: TimeSpan.FromSeconds(5),
                    errorCodesToAdd: null);
            });
    }
}

// Transacción con isolation level explícito
public async Task<Order> CreateOrderAsync(CreateOrderCommand command)
{
    using var transaction = await _context.Database.BeginTransactionAsync(
        IsolationLevel.Serializable);

    try
    {
        // Verificar inventory con strong consistency
        var product = await _context.Products
            .Where(p => p.Id == command.ProductId)
            .FirstOrDefaultAsync();

        if (product.Stock < command.Quantity)
            throw new InsufficientStockException();

        // Decrementar stock
        product.Stock -= command.Quantity;

        // Crear orden
        var order = new Order { /* ... */ };
        _context.Orders.Add(order);

        await _context.SaveChangesAsync();
        await transaction.CommitAsync();

        return order;
    }
    catch
    {
        await transaction.RollbackAsync();
        throw;
    }
}
```

### DynamoDB - Consistency Levels

```csharp
public class DynamoDbRepository
{
    private readonly IAmazonDynamoDB _dynamoDb;

    // Eventual consistency (default) - más rápido, más barato
    public async Task<Customer> GetCustomerEventualAsync(string customerId)
    {
        var request = new GetItemRequest
        {
            TableName = "Customers",
            Key = new Dictionary<string, AttributeValue>
            {
                ["CustomerId"] = new AttributeValue { S = customerId }
            },
            ConsistentRead = false  // Eventual
        };

        var response = await _dynamoDb.GetItemAsync(request);
        return MapToCustomer(response.Item);
    }

    // Strong consistency - para operaciones críticas
    public async Task<Customer> GetCustomerStrongAsync(string customerId)
    {
        var request = new GetItemRequest
        {
            TableName = "Customers",
            Key = new Dictionary<string, AttributeValue>
            {
                ["CustomerId"] = new AttributeValue { S = customerId }
            },
            ConsistentRead = true  // Strong - cuesta 2x read capacity
        };

        var response = await _dynamoDb.GetItemAsync(request);
        return MapToCustomer(response.Item);
    }
}
```

### Cosmos DB - Consistency Levels

```csharp
public class CosmosDbService
{
    private readonly CosmosClient _client;

    public CosmosDbService(string connectionString)
    {
        // Account-level default: Session
        _client = new CosmosClient(
            connectionString,
            new CosmosClientOptions
            {
                ConsistencyLevel = ConsistencyLevel.Session,
                ApplicationRegion = Regions.EastUS
            });
    }

    // Override per-request: Strong consistency para auditoría
    public async Task<AuditLog> GetAuditLogStrongAsync(string id)
    {
        var container = _client.GetContainer("TalmaDB", "AuditLogs");

        var response = await container.ReadItemAsync<AuditLog>(
            id,
            new PartitionKey(id),
            new ItemRequestOptions
            {
                ConsistencyLevel = ConsistencyLevel.Strong  // Override
            });

        return response.Resource;
    }

    // Bounded staleness para reportes
    public async Task<IEnumerable<Report>> GetReportsAsync()
    {
        var container = _client.GetContainer("TalmaDB", "Reports");

        var query = container.GetItemQueryIterator<Report>(
            requestOptions: new QueryRequestOptions
            {
                ConsistencyLevel = ConsistencyLevel.BoundedStaleness,
                MaxItemCount = 100
            });

        var results = new List<Report>();
        while (query.HasMoreResults)
        {
            var response = await query.ReadNextAsync();
            results.AddRange(response);
        }

        return results;
    }
}
```

### Redis - Cache Invalidation

```csharp
public class ProductCacheService
{
    private readonly IDistributedCache _cache;
    private readonly ILogger<ProductCacheService> _logger;
    private static readonly TimeSpan DefaultTTL = TimeSpan.FromMinutes(5);

    public async Task<Product> GetProductAsync(Guid productId)
    {
        var cacheKey = $"product:{productId}";

        // Intentar leer de cache
        var cached = await _cache.GetStringAsync(cacheKey);
        if (cached != null)
        {
            _logger.LogDebug("Cache HIT for {CacheKey}", cacheKey);
            return JsonSerializer.Deserialize<Product>(cached);
        }

        _logger.LogDebug("Cache MISS for {CacheKey}", cacheKey);

        // Leer de DB (source of truth)
        var product = await _dbContext.Products.FindAsync(productId);

        // Guardar en cache con TTL
        var options = new DistributedCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = DefaultTTL
        };

        await _cache.SetStringAsync(
            cacheKey,
            JsonSerializer.Serialize(product),
            options);

        return product;
    }

    public async Task InvalidateProductAsync(Guid productId)
    {
        var cacheKey = $"product:{productId}";
        await _cache.RemoveAsync(cacheKey);

        _logger.LogInformation("Cache invalidated for {CacheKey}", cacheKey);
    }
}
```

---

## 7. Ejemplos

### Decision Matrix

| Caso de Uso                  | Modelo            | Justificación                          |
| ---------------------------- | ----------------- | -------------------------------------- |
| Pago de factura              | Strong            | Dinero no puede duplicarse/perderse    |
| Actualizar perfil de usuario | Session           | Usuario debe ver sus cambios           |
| Likes en publicación         | Eventual          | Contador aproximado es aceptable       |
| Stock de inventario crítico  | Strong            | Evitar overselling                     |
| Feed de noticias             | Eventual          | Orden aproximado, latencia importa más |
| Chat entre usuarios          | Causal            | Mensajes deben verse en orden correcto |
| Analytics dashboard          | Bounded staleness | 5 min de lag aceptable por performance |

### Eventual Consistency con Reconciliación

```csharp
public class ViewCountService
{
    private readonly IDistributedCache _cache;
    private readonly IDatabase _db;

    // Incremento eventual en cache
    public async Task IncrementViewAsync(Guid articleId)
    {
        var cacheKey = $"views:{articleId}";

        // Incremento local en Redis (eventual)
        await _cache.IncrementAsync(cacheKey);

        // Publicar evento para reconciliación periódica
        await _eventBus.PublishAsync(new ArticleViewedEvent
        {
            ArticleId = articleId,
            Timestamp = DateTime.UtcNow
        });
    }

    // Reconciliación batch (cada 5 min)
    public async Task ReconcileViewCountsAsync()
    {
        var pendingEvents = await _eventStore.GetPendingViewEventsAsync();

        var viewsByArticle = pendingEvents
            .GroupBy(e => e.ArticleId)
            .Select(g => new { ArticleId = g.Key, Count = g.Count() });

        foreach (var item in viewsByArticle)
        {
            await _db.Articles
                .Where(a => a.Id == item.ArticleId)
                .UpdateAsync(a => a.ViewCount += item.Count);
        }

        await _eventStore.MarkEventsAsReconciledAsync(pendingEvents);
    }
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Modelo de consistencia documentado por bounded context
- [ ] Isolation levels configurados explícitamente
- [ ] SLO de staleness definido para eventual consistency
- [ ] Cache con TTL y estrategia de invalidación
- [ ] Métricas de replication lag monitoreadas
- [ ] Tests de escenarios de inconsistencia

### Métricas

```promql
# Replication lag PostgreSQL
pg_replication_lag_seconds

# DynamoDB throttling (señal de over-provisioning strong reads)
aws_dynamodb_consumed_read_capacity_units

# Redis cache hit rate
redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)
```

### Queries de Validación

```sql
-- PostgreSQL: verificar isolation level actual
SHOW default_transaction_isolation;

-- Ver replication lag
SELECT
    client_addr,
    state,
    sync_state,
    pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

---

## 9. Referencias

**Teoría:**

- Eric Brewer - "CAP Theorem"
- Daniel Abadi - "PACELC: An Extension to CAP"
- Martin Kleppmann - "Designing Data-Intensive Applications" (Chapter 9)
- Peter Bailis - "Eventual Consistency Today: Limitations, Extensions"

**Documentación:**

- [PostgreSQL Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [DynamoDB Read Consistency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html)
- [Cosmos DB Consistency Levels](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels)

**Buenas prácticas:**

- Jepsen.io - "Consistency models analysis"
- AWS Well-Architected Framework - Reliability Pillar
