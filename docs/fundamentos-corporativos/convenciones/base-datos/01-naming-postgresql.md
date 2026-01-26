---
id: naming-postgresql
sidebar_position: 1
title: Naming - PostgreSQL
description: Convención de nomenclatura para objetos de base de datos PostgreSQL
---

## 1. Principio

Los nombres de objetos de base de datos deben ser descriptivos, consistentes y facilitar la comprensión del modelo de datos sin necesidad de documentación externa.

## 2. Reglas

### Regla 1: snake_case para Todo

- **Formato**: Minúsculas con guiones bajos
- **Ejemplo correcto**: `user_profiles`, `order_items`, `created_at`
- **Ejemplo incorrecto**: `UserProfiles`, `orderItems`, `CreatedAt`
- **Justificación**: Estándar de PostgreSQL, evita case-sensitivity issues

### Regla 2: Tablas en Singular

- **Formato**: Singular, no plural
- **Ejemplo correcto**: `user`, `order`, `product`, `order_item`
- **Ejemplo incorrecto**: `users`, `orders`, `products`
- **Justificación**: Representa una entidad, no una colección

```sql
✅ Correcto:
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user(id)
);

❌ Incorrecto:
CREATE TABLE users (...);  -- Plural
CREATE TABLE Orders (...);  -- PascalCase
```

### Regla 3: Primary Key siempre `id`

- **Formato**: `id` (no `user_id`, `order_id` en tabla propia)
- **Tipo**: `SERIAL` o `BIGSERIAL` o `UUID`
- **Ejemplo correcto**:

```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,  -- ✅ Simple 'id'
    username VARCHAR(100)
);

CREATE TABLE order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- ✅ UUID también válido
    total_amount DECIMAL(10, 2)
);
```

### Regla 4: Foreign Keys con `{tabla}_id`

- **Formato**: `{tabla_referenciada}_id`
- **Ejemplo correcto**: `user_id`, `order_id`, `payment_method_id`
- **Constraint name**: `fk_{tabla_origen}_{columna}`

```sql
CREATE TABLE order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,  -- ✅ Referencia a tabla 'user'

    CONSTRAINT fk_order_user_id
        FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE order_item (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,

    CONSTRAINT fk_order_item_order_id
        FOREIGN KEY (order_id) REFERENCES order(id),
    CONSTRAINT fk_order_item_product_id
        FOREIGN KEY (product_id) REFERENCES product(id)
);
```

### Regla 5: Columnas de Auditoría Estándar

```sql
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,

    -- Auditoría estándar
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_at TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP,  -- Soft delete
    deleted_by VARCHAR(100)
);
```

### Regla 6: Índices con Prefijo `idx_`

- **Formato**: `idx_{tabla}_{columnas}[_{tipo}]`
- **Tipos**: Sin sufijo (B-tree), `_gin`, `_gist`, `_hash`
- **Ejemplo correcto**:

```sql
-- Índice simple
CREATE INDEX idx_user_email ON user(email);

-- Índice compuesto
CREATE INDEX idx_order_user_created ON order(user_id, created_at);

-- Índice único
CREATE UNIQUE INDEX idx_user_username_unique ON user(username);

-- Índice GIN (full-text search)
CREATE INDEX idx_product_search_gin ON product USING GIN(to_tsvector('spanish', name));
```

### Regla 7: Constraints con Prefijos

| Tipo        | Prefijo | Formato                  | Ejemplo                |
| ----------- | ------- | ------------------------ | ---------------------- |
| Primary Key | `pk_`   | `pk_{tabla}`             | `pk_user`              |
| Foreign Key | `fk_`   | `fk_{tabla}_{columna}`   | `fk_order_user_id`     |
| Unique      | `uk_`   | `uk_{tabla}_{columnas}`  | `uk_user_email`        |
| Check       | `ck_`   | `ck_{tabla}_{condicion}` | `ck_user_age_positive` |

```sql
CREATE TABLE user (
    id SERIAL,
    email VARCHAR(255) NOT NULL,
    age INTEGER,
    status VARCHAR(20) DEFAULT 'active',

    CONSTRAINT pk_user PRIMARY KEY (id),
    CONSTRAINT uk_user_email UNIQUE (email),
    CONSTRAINT ck_user_age_positive CHECK (age > 0),
    CONSTRAINT ck_user_status_valid CHECK (status IN ('active', 'inactive', 'banned'))
);
```

### Regla 8: Views con Prefijo `vw_`

```sql
CREATE VIEW vw_user_orders AS
SELECT
    u.id AS user_id,
    u.email,
    o.id AS order_id,
    o.total_amount,
    o.created_at AS order_date
FROM user u
LEFT JOIN order o ON o.user_id = u.id;
```

### Regla 9: Stored Procedures con Prefijo `sp_`

```sql
CREATE OR REPLACE FUNCTION sp_calculate_order_total(
    p_order_id INTEGER
)
RETURNS DECIMAL(10, 2)
AS $$
DECLARE
    v_total DECIMAL(10, 2);
BEGIN
    SELECT SUM(quantity * unit_price)
    INTO v_total
    FROM order_item
    WHERE order_id = p_order_id;

    RETURN COALESCE(v_total, 0);
END;
$$ LANGUAGE plpgsql;
```

### Regla 10: Functions con Prefijo `fn_`

```sql
CREATE OR REPLACE FUNCTION fn_get_user_full_name(
    p_user_id INTEGER
)
RETURNS VARCHAR(255)
AS $$
    SELECT CONCAT(first_name, ' ', last_name)
    FROM user
    WHERE id = p_user_id;
$$ LANGUAGE sql;
```

### Regla 11: Triggers con Prefijo `tr_`

```sql
CREATE OR REPLACE FUNCTION fn_update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_user_update_timestamp
    BEFORE UPDATE ON user
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_updated_at();
```

## 3. Tabla de Referencia Rápida

| Objeto           | Convención                      | Ejemplo                                    |
| ---------------- | ------------------------------- | ------------------------------------------ |
| Tabla            | `snake_case` singular           | `user`, `order`, `order_item`              |
| Columna          | `snake_case`                    | `first_name`, `created_at`, `total_amount` |
| Primary Key      | `id`                            | `id SERIAL PRIMARY KEY`                    |
| Foreign Key      | `{tabla}_id`                    | `user_id`, `product_id`                    |
| Índice           | `idx_{tabla}_{columnas}`        | `idx_user_email`                           |
| Unique Index     | `idx_{tabla}_{columnas}_unique` | `idx_user_username_unique`                 |
| FK Constraint    | `fk_{tabla}_{columna}`          | `fk_order_user_id`                         |
| UK Constraint    | `uk_{tabla}_{columnas}`         | `uk_user_email`                            |
| Check Constraint | `ck_{tabla}_{condicion}`        | `ck_user_age_positive`                     |
| View             | `vw_{nombre}`                   | `vw_user_orders`                           |
| Stored Procedure | `sp_{nombre}`                   | `sp_calculate_total`                       |
| Function         | `fn_{nombre}`                   | `fn_get_full_name`                         |
| Trigger          | `tr_{tabla}_{accion}`           | `tr_user_update_timestamp`                 |

## 4. Tipos de Datos Recomendados

| Tipo de Dato        | PostgreSQL Type        | Ejemplo                              |
| ------------------- | ---------------------- | ------------------------------------ |
| ID auto-incremental | `SERIAL` / `BIGSERIAL` | `id SERIAL PRIMARY KEY`              |
| ID UUID             | `UUID`                 | `id UUID DEFAULT gen_random_uuid()`  |
| Texto corto         | `VARCHAR(n)`           | `email VARCHAR(255)`                 |
| Texto largo         | `TEXT`                 | `description TEXT`                   |
| Número entero       | `INTEGER` / `BIGINT`   | `quantity INTEGER`                   |
| Decimal             | `DECIMAL(p, s)`        | `price DECIMAL(10, 2)`               |
| Booleano            | `BOOLEAN`              | `is_active BOOLEAN DEFAULT true`     |
| Fecha               | `DATE`                 | `birth_date DATE`                    |
| Fecha y hora        | `TIMESTAMP`            | `created_at TIMESTAMP DEFAULT NOW()` |
| JSON                | `JSONB`                | `metadata JSONB`                     |
| Array               | `{tipo}[]`             | `tags VARCHAR(50)[]`                 |

## 5. Herramientas de Validación

### Linter SQL (sqlfluff)

```ini
# .sqlfluff
[sqlfluff]
dialect = postgres
rules = L001,L002,L003,L010,L014

[sqlfluff:rules:L010]
# Require snake_case
capitalisation_policy = lower

[sqlfluff:rules:L014]
# Naming conventions
unquoted_identifiers_policy = all
```

### Script de Validación

```sql
-- Verificar tablas sin primary key
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename NOT IN (
    SELECT tablename
    FROM pg_indexes
    WHERE indexdef LIKE '%PRIMARY KEY%'
  );

-- Verificar columnas sin convención snake_case
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name ~ '[A-Z]';  -- Detecta mayúsculas
```

## 📖 Referencias

### Estándares relacionados

- [SQL](/docs/fundamentos-corporativos/estandares/codigo/sql)

### Convenciones relacionadas

- [Naming Migraciones](./02-naming-migraciones.md)

### Recursos externos

- [PostgreSQL Naming Conventions](https://www.postgresql.org/docs/current/sql-syntax-lexical.html)
- [SQL Style Guide](https://www.sqlstyle.guide/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
