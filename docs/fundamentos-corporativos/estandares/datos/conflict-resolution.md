---
id: conflict-resolution
sidebar_position: 1
title: Conflict Resolution
description: Estándar para resolución de conflictos en datos distribuidos usando estrategias deterministas (LWW, CRDT, vector clocks)
---

# Estándar Técnico — Conflict Resolution

---

## 1. Propósito

Definir estrategias deterministas para resolver conflictos de datos en sistemas distribuidos, garantizando convergencia eventual y minimizando pérdida de información cuando múltiples réplicas modifican el mismo dato concurrentemente.

---

## 2. Alcance

**Aplica a:**

- Sistemas distribuidos multi-región
- Bases de datos con replicación eventual
- Sincronización offline-first (mobile apps)
- Event sourcing con múltiples agregados
- Cache distribuido con escrituras concurrentes
- Sistemas colaborativos (CRDTs)

**No aplica a:**

- Bases de datos con strong consistency (single-region)
- Transacciones ACID locales
- Sistemas read-only
- Cache solo lectura

---

## 3. Tecnologías Aprobadas

| Componente           | Tecnología              | Versión mínima | Observaciones                      |
| -------------------- | ----------------------- | -------------- | ---------------------------------- |
| **Relacional**       | PostgreSQL              | 14+            | Con logical replication            |
| **Messaging**        | Apache Kafka            | 3.6+           | Idempotent producers, exactly-once |
| **CRDT Library**     | Automerge               | 2.0+           | JSON CRDT para aplicaciones web    |
| **Vector Clocks**    | NodaTime + custom impl  | 3.1+           | Timestamps con causalidad          |
| **Distributed Lock** | Redlock (StackExchange) | 2.6+           | Para coordinar escrituras críticas |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Estrategia de Resolución

- [ ] **Definir estrategia explícita** por tipo de dato (LWW, CRDT, custom merge)
- [ ] **Last-Write-Wins (LWW):** solo para datos donde última escritura prevalece
- [ ] **CRDT:** para datos colaborativos que requieren merge automático
- [ ] **Vector clocks / Version vectors:** cuando causalidad importa
- [ ] **Custom merge function:** documentar lógica de negocio para merge

### Control de Versiones

- [ ] Timestamps con precisión de milisegundos (mejor nanosegundos)
- [ ] Version numbers incrementales por modificación
- [ ] Incluir replica ID o node ID en metadata
- [ ] Usar UTC para todos los timestamps

### Detección de Conflictos

- [ ] Comparar version numbers antes de escribir
- [ ] Detectar escrituras concurrentes (mismo version base)
- [ ] Registrar conflictos en logs de auditoría
- [ ] Métricas de tasa de conflictos

### Políticas por Tipo de Dato

- [ ] **Contadores:** usar CRDT counter (G-Counter, PN-Counter)
- [ ] **Sets:** usar CRDT sets (G-Set, 2P-Set, OR-Set)
- [ ] **Textos colaborativos:** CRDT text (Automerge, Yjs)
- [ ] **Metadata simple:** LWW con timestamp
- [ ] **Valores monetarios:** manual review o compensación

### Preservación de Información

- [ ] Nunca eliminar silenciosamente datos conflictivos
- [ ] Almacenar ambas versiones si merge automático falla
- [ ] Queue para revisión manual de conflictos complejos
- [ ] Audit log completo de merges

---

## 5. Prohibiciones

- ❌ Sobrescribir datos sin detectar conflictos
- ❌ Usar solo server timestamp (ignorar client timestamp)
- ❌ LWW para datos donde pérdida es inaceptable (financieros)
- ❌ Merge silencioso sin logging
- ❌ Ignorar causalidad en eventos dependientes
- ❌ Timestamps sin timezone o con timezone local
- ❌ Auto-resolución sin estrategia documentada

---

## 6. Configuración Mínima

### PostgreSQL con Version Numbers

```sql
-- Tabla con version control
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    version BIGINT NOT NULL DEFAULT 1,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_by VARCHAR(100) NOT NULL,
    replica_id VARCHAR(50) NOT NULL,
    CONSTRAINT check_version_positive CHECK (version > 0)
);

CREATE INDEX idx_orders_version ON orders(id, version);

-- Function para update con optimistic locking
CREATE OR REPLACE FUNCTION update_order_with_version(
    p_order_id UUID,
    p_expected_version BIGINT,
    p_new_status VARCHAR(20),
    p_updated_by VARCHAR(100),
    p_replica_id VARCHAR(50)
) RETURNS BOOLEAN AS $$
DECLARE
    v_current_version BIGINT;
    v_rows_affected INT;
BEGIN
    UPDATE orders
    SET status = p_new_status,
        version = version + 1,
        updated_at = NOW(),
        updated_by = p_updated_by,
        replica_id = p_replica_id
    WHERE id = p_order_id
      AND version = p_expected_version;

    GET DIAGNOSTICS v_rows_affected = ROW_COUNT;

    IF v_rows_affected = 0 THEN
        SELECT version INTO v_current_version
        FROM orders WHERE id = p_order_id;

        INSERT INTO conflict_log (
            entity_type, entity_id, expected_version,
            current_version, attempted_by, detected_at
        ) VALUES (
            'order', p_order_id, p_expected_version,
            v_current_version, p_updated_by, NOW()
        );

        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
```

### Entity Framework con Concurrency Token

```csharp
public class Order
{
    public Guid Id { get; set; }
    public decimal TotalAmount { get; set; }

    [Timestamp]
    public byte[] RowVersion { get; set; }

    public DateTime UpdatedAt { get; set; }
}

public class OrderService
{
    private readonly OrderDbContext _context;

    public async Task<ConflictResolutionResult> UpdateOrderAsync(
        Guid orderId,
        OrderStatus newStatus,
        byte[] expectedRowVersion)
    {
        var order = await _context.Orders.FindAsync(orderId);

        if (!order.RowVersion.SequenceEqual(expectedRowVersion))
        {
            await LogConflictAsync(orderId, expectedRowVersion, order.RowVersion);
            return ConflictResolutionResult.Conflict(order);
        }

        order.Status = newStatus;
        order.UpdatedAt = DateTime.UtcNow;

        try
        {
            await _context.SaveChangesAsync();
            return ConflictResolutionResult.Success();
        }
        catch (DbUpdateConcurrencyException)
        {
            return ConflictResolutionResult.Conflict(order);
        }
    }
}
```

---

## 7. Ejemplos

### Last-Write-Wins

```csharp
public class LWWMergeStrategy : IMergeStrategy<UserProfile>
{
    public UserProfile Merge(UserProfile local, UserProfile remote)
    {
        return remote.LastModifiedUtc > local.LastModifiedUtc
            ? remote
            : local;
    }
}
```

### CRDT Counter

```csharp
public class GCounter
{
    private readonly Dictionary<string, long> _counters = new();
    private readonly string _replicaId;

    public void Increment()
    {
        if (!_counters.ContainsKey(_replicaId))
            _counters[_replicaId] = 0;

        _counters[_replicaId]++;
    }

    public long Value => _counters.Values.Sum();

    public void Merge(GCounter other)
    {
        foreach (var (replica, count) in other._counters)
        {
            if (!_counters.ContainsKey(replica))
                _counters[replica] = count;
            else
                _counters[replica] = Math.Max(_counters[replica], count);
        }
    }
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Estrategia de resolución documentada por entidad
- [ ] Version control implementado
- [ ] Detección de conflictos activa
- [ ] Logging de conflictos con metadata
- [ ] Métricas de tasa de conflictos
- [ ] Tests de escrituras concurrentes

### Métricas

```promql
rate(data_conflicts_detected_total[5m])
sum by (strategy) (data_conflicts_by_strategy)
histogram_quantile(0.95, conflict_resolution_duration_seconds)
```

### Auditoría

```sql
SELECT entity_type, entity_id, expected_version, current_version,
       attempted_by, detected_at
FROM conflict_log
WHERE detected_at > NOW() - INTERVAL '24 hours'
ORDER BY detected_at DESC;
```

---

## 9. Referencias

**Teoría:**

- Martin Kleppmann - "Designing Data-Intensive Applications" (Chapter 5)
- CAP Theorem y PACELC
- Marc Shapiro et al. - "A comprehensive study of CRDTs"

**Documentación:**

- [PostgreSQL Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html)
- [DynamoDB Conditional Writes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html)
- [Cosmos DB Conflict Resolution](https://learn.microsoft.com/en-us/azure/cosmos-db/conflict-resolution-policies)

**Librerías:**

- [Automerge - CRDT library](https://automerge.org/)
- [Yjs - Shared editing](https://docs.yjs.dev/)
