---
id: schema-evolution
sidebar_position: 11
title: Schema Evolution
description: Estándar para evolución de esquemas sin downtime usando migrations versionadas, expand-contract pattern y backward compatibility
---

# Estándar Técnico — Schema Evolution

---

## 1. Propósito

Permitir evolución segura de esquemas de base de datos sin downtime mediante migrations versionadas, backward compatibility y estrategias expand-contract, garantizando deployments continuos.

---

## 2. Alcance

**Aplica a:**

- Cambios de schema en PostgreSQL
- Adición/modificación/eliminación de columnas
- Cambios de índices
- Refactoring de tablas
- Particionamiento
- Data type changes

**No aplica a:**

- Datos inmutables (append-only)
- Tablas temporales
- Schema changes en ambientes dev/test (solo prod requiere expand-contract)

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología         | Versión mínima | Observaciones                   |
| -------------- | ------------------ | -------------- | ------------------------------- |
| **Migrations** | EF Core Migrations | 8.0+           | .NET native migrations          |
| **Testing**    | Respawn            | 6.0+           | Reset DB para integration tests |
| **Monitoring** | Grafana Mimir      | 2.10+          | Métricas de migration duration  |
| **Rollback**   | pg_restore         | PostgreSQL 14+ | Point-in-time recovery          |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Backward Compatibility

- [ ] **Nuevos cambios NO rompen versión actual** de la aplicación
- [ ] Columnas nuevas deben ser nullable o tener default
- [ ] No eliminar columnas en uso (deprecar primero)
- [ ] No cambiar tipos de datos incompatibles directamente
- [ ] Tests de compatibility en CI/CD

### Expand-Contract Pattern

- [ ] **Expand:** agregar nuevos elementos (columnas, índices)
- [ ] **Migrate:** aplicación usa ambas versiones (dual-write period)
- [ ] **Contract:** eliminar elementos obsoletos después de confirmación
- [ ] Mínimo 1 sprint entre expand y contract

### Versioned Migrations

- [ ] Migrations numeradas secuencialmente (V1, V2, V3...)
- [ ] Una migration por cambio lógico
- [ ] Migrations idempotentes (pueden re-ejecutarse)
- [ ] Rollback script para migrations críticas
- [ ] Testing en staging antes de prod

### Zero-Downtime Deployments

- [ ] No locks largos en tablas productivas
- [ ] CREATE INDEX CONCURRENTLY para índices grandes
- [ ] ALTER TABLE sin exclusive locks (usar locks advisory cuando sea posible)
- [ ] Timeouts configurados en migrations (max 5 min)

### Auditoría

- [ ] Logging de todas las migrations ejecutadas
- [ ] Timestamp de ejecución
- [ ] Duración de cada migration
- [ ] Alertas si migration falla o excede tiempo

---

## 5. Prohibiciones

- ❌ Cambios de schema directos en producción (sin migrations)
- ❌ Eliminar columnas sin periodo de deprecación
- ❌ Cambios breaking sin expand-contract
- ❌ ALTER TABLE con locks exclusivos largos
- ❌ Migrations sin rollback plan
- ❌ Data migrations masivos en horario pico
- ❌ Migrations sin testing previo

---

## 6. Configuración Mínima

### Flyway Configuration

```properties
# flyway.conf
flyway.url=jdbc:postgresql://localhost:5432/talma_db
flyway.user=flyway_user
flyway.password=${FLYWAY_PASSWORD}
flyway.schemas=public
flyway.locations=filesystem:./migrations
flyway.baselineOnMigrate=true
flyway.validateOnMigrate=true
flyway.outOfOrder=false
flyway.placeholderReplacement=true
flyway.sqlMigrationSuffixes=.sql
flyway.repeatableSqlMigrationPrefix=R
flyway.table=schema_version
```

### Migration - Add Column (Backward Compatible)

```sql
-- V1__add_customer_phone.sql
-- Migration: Add phone column to customers
-- Breaking: No
-- Backward Compatible: Yes (nullable column)
-- Rollback: ALTER TABLE customers DROP COLUMN phone;

-- ✅ BIEN: Columna nullable (backward compatible)
ALTER TABLE customers
ADD COLUMN phone VARCHAR(20) NULL;

COMMENT ON COLUMN customers.phone IS
'Customer phone number. Format: +[country][number].
Added: 2024-01-15. Nullable for backward compatibility.';

-- Índice opcional para búsqueda
CREATE INDEX CONCURRENTLY idx_customers_phone
ON customers(phone)
WHERE phone IS NOT NULL;
```

### Migration - Add Column with Default

```sql
-- V2__add_customer_status.sql
-- Migration: Add status column with default
-- Breaking: No
-- Backward Compatible: Yes (default value provided)

-- ✅ BIEN: Columna NOT NULL con DEFAULT (no rompe app actual)
ALTER TABLE customers
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE';

COMMENT ON COLUMN customers.status IS
'Customer account status. Values: ACTIVE, INACTIVE, SUSPENDED.
Default: ACTIVE. Added: 2024-01-16.';

-- Constraint para valores válidos
ALTER TABLE customers
ADD CONSTRAINT check_customer_status
CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED'));
```

### Expand-Contract Pattern - Rename Column

```sql
-- FASE 1: EXPAND - V3__expand_rename_email.sql
-- Add new column, keep old one
-- Breaking: No
-- Duration: Permanent until contract phase

-- Agregar nueva columna
ALTER TABLE customers
ADD COLUMN email_address VARCHAR(255) NULL;

COMMENT ON COLUMN customers.email_address IS
'New column name for email (renaming from "email").
During transition period, both email and email_address exist.
email_address will replace email in future release.';

-- Copiar datos existentes
UPDATE customers
SET email_address = email
WHERE email_address IS NULL;

-- Trigger para dual-write (mantener ambas en sync)
CREATE OR REPLACE FUNCTION sync_email_columns()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.email IS DISTINCT FROM OLD.email THEN
        NEW.email_address := NEW.email;
    END IF;

    IF NEW.email_address IS DISTINCT FROM OLD.email_address THEN
        NEW.email := NEW.email_address;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_email
BEFORE UPDATE ON customers
FOR EACH ROW
EXECUTE FUNCTION sync_email_columns();

-- FASE 2: MIGRATE (en código de aplicación)
-- App updated to write to both columns, read from email_address
-- Deploy app v2.0

-- FASE 3: CONTRACT - V10__contract_rename_email.sql
-- (Ejecutar después de 1+ sprint)
-- Remove old column
-- Breaking: Yes for apps still using old column

-- Verificar que app ya no usa columna antigua
-- (Revisar logs, métricas)

DROP TRIGGER IF EXISTS trg_sync_email ON customers;
DROP FUNCTION IF EXISTS sync_email_columns();

ALTER TABLE customers
DROP COLUMN email;

-- Renombrar a nombre final
ALTER TABLE customers
RENAME COLUMN email_address TO email;

COMMENT ON COLUMN customers.email IS
'Customer email address (renamed from email_address).
Contract phase completed: 2024-02-15.';
```

### Data Type Change (Zero-Downtime)

```sql
-- V4__change_order_number_type.sql
-- Migration: Change order_number from INTEGER to VARCHAR(20)
-- Breaking: No (expand-contract pattern)
-- Phase 1: EXPAND

-- 1. Agregar nueva columna con nuevo tipo
ALTER TABLE orders
ADD COLUMN order_number_new VARCHAR(20) NULL;

-- 2. Backfill datos existentes
UPDATE orders
SET order_number_new = 'ORD-' || LPAD(order_number::TEXT, 10, '0')
WHERE order_number_new IS NULL;

-- 3. Índice en nueva columna
CREATE UNIQUE INDEX CONCURRENTLY idx_orders_number_new
ON orders(order_number_new);

-- 4. Trigger para dual-write durante migración
CREATE OR REPLACE FUNCTION sync_order_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.order_number IS NOT NULL THEN
        NEW.order_number_new := 'ORD-' || LPAD(NEW.order_number::TEXT, 10, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_order_number
BEFORE INSERT OR UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION sync_order_number();

-- FASE 3: CONTRACT (migration posterior)
-- V11__contract_order_number.sql
-- DROP TRIGGER trg_sync_order_number ON orders;
-- DROP FUNCTION sync_order_number();
-- ALTER TABLE orders DROP COLUMN order_number;
-- ALTER TABLE orders RENAME COLUMN order_number_new TO order_number;
```

### Create Index Concurrently (No Locks)

```sql
-- V5__add_index_orders_customer.sql
-- Migration: Add index for customer queries
-- Breaking: No
-- Lock: None (CONCURRENTLY)

-- ✅ BIEN: CREATE INDEX CONCURRENTLY (sin lock exclusivo)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_created
ON orders(customer_id, created_at DESC)
WHERE deleted_at IS NULL;

COMMENT ON INDEX idx_orders_customer_created IS
'Index for customer order queries sorted by creation date.
Supports: GET /customers/{id}/orders?sort=created_at:desc
Created concurrently to avoid table locks.';

-- ❌ MAL: Sin CONCURRENTLY bloquearía tabla
-- CREATE INDEX idx_orders_customer_created ON orders(...);
```

### Partition Existing Table (Zero-Downtime)

```sql
-- V6__partition_audit_logs.sql
-- Migration: Partition audit_logs by month
-- Breaking: No
-- Strategy: Create partitioned table, migrate data, swap

-- 1. Crear nueva tabla particionada
CREATE TABLE audit_logs_partitioned (
    id BIGSERIAL,
    event_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- 2. Crear particiones para meses futuros
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE audit_logs_2024_02 PARTITION OF audit_logs_partitioned
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 3. Migrar datos históricos (en batches, off-peak)
INSERT INTO audit_logs_partitioned
SELECT * FROM audit_logs
WHERE created_at >= '2024-01-01'
ORDER BY created_at
LIMIT 100000;

-- 4. Trigger para dual-write durante migración
CREATE OR REPLACE FUNCTION sync_audit_logs()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs_partitioned
    VALUES (NEW.*);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_audit_logs
AFTER INSERT ON audit_logs
FOR EACH ROW
EXECUTE FUNCTION sync_audit_logs();

-- 5. Después de completar migración (siguiente release):
--    - Renombrar audit_logs a audit_logs_old
--    - Renombrar audit_logs_partitioned a audit_logs
--    - Drop trigger y función
--    - Drop audit_logs_old después de retention period
```

---

## 7. Ejemplos

### Rollback Script

```sql
-- V7__add_customer_tier.sql
-- Migration: Add customer tier column

ALTER TABLE customers
ADD COLUMN tier VARCHAR(20) NOT NULL DEFAULT 'STANDARD';

-- Rollback script (separado)
-- R7__rollback_add_customer_tier.sql (manual execution)
ALTER TABLE customers
DROP COLUMN tier;
```

### Migration with Timeout

```sql
-- V8__large_data_migration.sql
-- Set statement timeout to 5 minutes
SET statement_timeout = '5min';

-- Migration logic
UPDATE products
SET category_id = (
    SELECT id FROM categories WHERE name = 'Uncategorized'
)
WHERE category_id IS NULL;

-- Reset timeout
RESET statement_timeout;
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Migrations versionadas secuencialmente
- [ ] Backward compatibility validada
- [ ] Expand-contract para breaking changes
- [ ] CREATE INDEX CONCURRENTLY usado
- [ ] Rollback scripts documentados
- [ ] Tested en staging
- [ ] Duración de migration monitoreada

### CI/CD Validation

```bash
#!/bin/bash
# validate-migrations.sh

# Validar que migrations son idempotentes
flyway validate

# Dry-run en DB de test
flyway migrate -dryRunOutput=migration-plan.sql

# Verificar que no hay locks largos
grep -i "LOCK" migration-plan.sql && echo "WARNING: Explicit locks detected"

# Estimar duración (ejecutar en test DB)
time flyway migrate -target=9999
```

### Monitoring

```csharp
// Metrics/MigrationMetrics.cs
public class MigrationMetrics
{
    private static readonly Histogram MigrationDuration = Metrics
        .CreateHistogram(
            "db_migration_duration_seconds",
            "Database migration duration",
            new HistogramConfiguration
            {
                LabelNames = new[] { "version", "result" }
            });

    public void RecordMigration(string version, bool success, TimeSpan duration)
    {
        MigrationDuration
            .WithLabels(version, success ? "success" : "failure")
            .Observe(duration.TotalSeconds);
    }
}
```

### Alertas

```yaml
groups:
  - name: schema_migration_alerts
    rules:
      - alert: MigrationTakingTooLong
        expr: db_migration_duration_seconds > 300
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Database migration exceeding 5 minutes"
          description: "Migration {{ $labels.version }}: {{ $value }}s"

      - alert: MigrationFailed
        expr: rate(db_migration_duration_seconds{result="failure"}[5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Database migration failed"
```

---

## 9. Referencias

**Teoría:**

- Refactoring Databases - Scott Ambler
- Evolutionary Database Design - Martin Fowler
- Expand-Contract Pattern

**Documentación:**

- [Flyway Documentation](https://flywaydb.org/documentation/)
- [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
- [CREATE INDEX CONCURRENTLY](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY)

**Buenas prácticas:**

- "Database Reliability Engineering" (O'Reilly)
- [Stripe's Online Migrations](https://stripe.com/blog/online-migrations)
- [GitHub's gh-ost](https://github.com/github/gh-ost)
