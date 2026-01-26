---
id: naming-migraciones
sidebar_position: 2
title: Naming - Migraciones de BD
description: Convención para nombrar archivos de migración de base de datos
---

## 1. Principio

Los archivos de migración deben tener nombres descriptivos que permitan entender el cambio sin abrir el archivo, y seguir un orden cronológico estricto.

## 2. Reglas

### Regla 1: Formato con Timestamp

- **Formato**: `V{timestamp}__{descripcion}.sql`
- **Timestamp**: `YYYYMMDDHHmmss` (14 dígitos)
- **Descripción**: `snake_case` descriptivo
- **Ejemplo correcto**:
  - `V20240115103000__create_user_table.sql`
  - `V20240115104500__add_email_index_to_user.sql`
  - `V20240115110000__alter_order_add_status_column.sql`

### Regla 2: Prefijo por Tipo de Migración

| Tipo                | Prefijo        | Ejemplo                 |
| ------------------- | -------------- | ----------------------- |
| Versioned (Flyway)  | `V{version}__` | `V1__create_schema.sql` |
| Repeatable (Flyway) | `R__`          | `R__create_views.sql`   |
| Rollback            | `U{version}__` | `U1__drop_schema.sql`   |

### Regla 3: Descripción Verbosa y Clara

```
✅ Correcto:
V20240115103000__create_user_table.sql
V20240115104500__add_email_index_to_user.sql
V20240115110000__alter_order_add_status_column.sql
V20240116083000__create_order_item_table.sql
V20240116084500__add_foreign_key_order_item_to_order.sql

❌ Incorrecto:
V1__user.sql                    # No descriptivo
migration_001.sql               # Sin timestamp
20240115_users.sql              # Sin prefijo V
V20240115__users.sql            # Falta descripción
create_user_table.sql           # Sin versión ni timestamp
```

### Regla 4: Verbos de Acción

| Acción            | Verbo                                | Ejemplo                                    |
| ----------------- | ------------------------------------ | ------------------------------------------ |
| Crear tabla       | `create_{tabla}_table`               | `create_user_table.sql`                    |
| Eliminar tabla    | `drop_{tabla}_table`                 | `drop_temp_user_table.sql`                 |
| Añadir columna    | `add_{columna}_to_{tabla}`           | `add_email_to_user.sql`                    |
| Eliminar columna  | `remove_{columna}_from_{tabla}`      | `remove_legacy_id_from_order.sql`          |
| Modificar columna | `alter_{tabla}_change_{columna}`     | `alter_user_change_email_length.sql`       |
| Crear índice      | `create_{indice}_index`              | `create_user_email_index.sql`              |
| Añadir FK         | `add_foreign_key_{tabla}_to_{tabla}` | `add_foreign_key_order_to_user.sql`        |
| Insertar datos    | `insert_{descripcion}_data`          | `insert_initial_roles_data.sql`            |
| Migrar datos      | `migrate_{descripcion}_data`         | `migrate_user_addresses_to_new_format.sql` |

## 3. Ejemplos de Migraciones

### Crear Tabla

```sql
-- V20240115103000__create_user_table.sql

CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uk_user_email UNIQUE (email),
    CONSTRAINT uk_user_username UNIQUE (username)
);

CREATE INDEX idx_user_email ON user(email);

COMMENT ON TABLE user IS 'Usuarios del sistema';
COMMENT ON COLUMN user.email IS 'Email único del usuario';
```

### Añadir Columna

```sql
-- V20240115110000__add_phone_to_user.sql

ALTER TABLE user
ADD COLUMN phone VARCHAR(20);

CREATE INDEX idx_user_phone ON user(phone);

COMMENT ON COLUMN user.phone IS 'Teléfono de contacto del usuario';
```

### Añadir Foreign Key

```sql
-- V20240116084500__add_foreign_key_order_to_user.sql

ALTER TABLE order
ADD CONSTRAINT fk_order_user_id
    FOREIGN KEY (user_id)
    REFERENCES user(id)
    ON DELETE CASCADE;

CREATE INDEX idx_order_user_id ON order(user_id);
```

### Insertar Datos Iniciales

```sql
-- V20240117090000__insert_initial_roles_data.sql

INSERT INTO role (name, description) VALUES
    ('admin', 'Administrator with full access'),
    ('user', 'Standard user'),
    ('guest', 'Guest with read-only access')
ON CONFLICT (name) DO NOTHING;
```

### Migración de Datos

```sql
-- V20240118150000__migrate_user_full_name_to_separate_columns.sql

-- 1. Añadir nuevas columnas
ALTER TABLE user
ADD COLUMN first_name VARCHAR(100),
ADD COLUMN last_name VARCHAR(100);

-- 2. Migrar datos existentes
UPDATE user
SET
    first_name = SPLIT_PART(full_name, ' ', 1),
    last_name = SPLIT_PART(full_name, ' ', 2)
WHERE full_name IS NOT NULL;

-- 3. Validar migración
DO $$
DECLARE
    unmigrated_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO unmigrated_count
    FROM user
    WHERE full_name IS NOT NULL
      AND (first_name IS NULL OR last_name IS NULL);

    IF unmigrated_count > 0 THEN
        RAISE EXCEPTION 'Migración incompleta: % registros sin migrar', unmigrated_count;
    END IF;
END $$;

-- 4. Eliminar columna antigua (en migración posterior)
-- ALTER TABLE user DROP COLUMN full_name;
```

## 4. Estructura de Carpetas

```
db/
├── migrations/
│   ├── V20240115103000__create_user_table.sql
│   ├── V20240115104500__add_email_index_to_user.sql
│   ├── V20240116083000__create_order_table.sql
│   └── V20240117090000__insert_initial_roles_data.sql
├── seeds/
│   ├── dev/
│   │   └── 001_seed_test_users.sql
│   └── prod/
│       └── 001_seed_initial_config.sql
└── rollbacks/
    ├── U20240115103000__drop_user_table.sql
    └── U20240116083000__drop_order_table.sql
```

## 5. Herramientas de Migración

### Flyway

```ini
# flyway.conf
flyway.url=jdbc:postgresql://localhost:5432/talma_db
flyway.user=postgres
flyway.password=<SECRET>
flyway.locations=filesystem:db/migrations
flyway.baselineOnMigrate=true
flyway.validateOnMigrate=true
flyway.outOfOrder=false
```

```bash
# Ejecutar migraciones
flyway migrate

# Validar estado
flyway validate

# Ver historial
flyway info
```

### Liquibase

```xml
<!-- db/changelog/db.changelog-master.xml -->
<databaseChangeLog>
    <include file="db/changelog/V20240115103000__create_user_table.sql"/>
    <include file="db/changelog/V20240115104500__add_email_index_to_user.sql"/>
</databaseChangeLog>
```

### Entity Framework Core (.NET)

```bash
# Generar migración con timestamp automático
dotnet ef migrations add CreateUserTable

# Aplicar migraciones
dotnet ef database update
```

El nombre generado será: `20240115103000_CreateUserTable.cs`

### TypeORM (TypeScript)

```bash
# Generar migración
npm run typeorm migration:generate -- -n CreateUserTable

# Ejecutar migraciones
npm run typeorm migration:run
```

Genera: `1705315800000-CreateUserTable.ts`

## 6. Validación de Migraciones

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validar formato de migraciones
for file in db/migrations/V*.sql; do
    filename=$(basename "$file")

    # Validar formato V{timestamp}__{description}.sql
    if [[ ! $filename =~ ^V[0-9]{14}__[a-z_]+\.sql$ ]]; then
        echo "❌ Formato inválido: $filename"
        echo "   Debe ser: V{YYYYMMDDHHmmss}__{snake_case_description}.sql"
        exit 1
    fi
done

echo "✅ Formato de migraciones correcto"
```

### Script de Rollback Automático

```sql
-- Plantilla para rollback
-- U20240115103000__drop_user_table.sql

-- Rollback de V20240115103000__create_user_table.sql

DROP INDEX IF EXISTS idx_user_email;
DROP TABLE IF EXISTS user CASCADE;
```

## 7. Mejores Prácticas

### ✅ Hacer

- Usar transacciones cuando sea posible
- Incluir comentarios explicativos
- Validar datos antes de migrar
- Probar rollback antes de producción
- Una migración = un cambio lógico

```sql
BEGIN;

-- Migración aquí
ALTER TABLE user ADD COLUMN phone VARCHAR(20);

-- Validación
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'user' AND column_name = 'phone'
    ) THEN
        RAISE EXCEPTION 'Columna phone no fue creada';
    END IF;
END $$;

COMMIT;
```

### ❌ Evitar

- Modificar migraciones ya aplicadas
- Combinar múltiples cambios no relacionados
- Eliminar datos sin respaldo
- Confiar en orden alfabético (usar timestamp)

## 📖 Referencias

### Estándares relacionados

- [SQL](/docs/fundamentos-corporativos/estandares/codigo/sql)

### Convenciones relacionadas

- [Naming PostgreSQL](./01-naming-postgresql.md)

### Recursos externos

- [Flyway Documentation](https://flywaydb.org/documentation/)
- [Liquibase Best Practices](https://www.liquibase.org/get-started/best-practices)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
