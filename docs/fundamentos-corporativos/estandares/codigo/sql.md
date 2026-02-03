---
id: sql
sidebar_position: 3
title: Desarrollo con SQL
description: Estándares para desarrollo SQL, Entity Framework, PostgreSQL 14+ y Oracle 19c
---

# Estándar Técnico — Desarrollo con SQL

---

## 1. Propósito

Garantizar código SQL seguro contra SQL Injection mediante parametrización, optimizado con índices y EXPLAIN ANALYZE, usando Entity Framework Core 8.0+ con LINQ preferido sobre raw SQL.

---

## 2. Alcance

**Aplica a:**

- Consultas SQL con Entity Framework Core 8.0+
- Raw SQL con Npgsql 8.0+ (PostgreSQL) y Oracle.EntityFrameworkCore 8.0+
- Repositories con acceso a datos
- Scripts de migración (EF Migrations / Entity Framework Migrations 10.0+)

**No aplica a:**

- Queries de herramientas BI/reportería
- Scripts de administración DBA
- Consultas ad-hoc de análisis

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología                 | Versión mínima | Observaciones         |
| ------------------- | -------------------------- | -------------- | --------------------- |
| **BD Principal**    | PostgreSQL                 | 14.0+          | Transaccional OLTP    |
| **BD Corporativa**  | Oracle Database            | 19c+           | Sistemas corporativos |
| **ORM Principal**   | Entity Framework Core      | 8.0+           | ORM completo .NET     |
| **Micro-ORM**       | Dapper                     | 2.1+           | Queries optimizados   |
| **Provider PG**     | Npgsql                     | 8.0+           | JSON/JSONB support    |
| **Provider Oracle** | Oracle.EntityFrameworkCore | 8.0+           | Soporte Oracle        |
| **Migrations**      | EF Migrations              | -              | Versionado esquemas   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Parámetros SIEMPRE (NO concatenación de strings)
- [ ] LINQ preferido sobre raw SQL
- [ ] Raw SQL solo cuando LINQ no es suficiente
- [ ] Proyecciones con `Select()` (evitar `SELECT *`)
- [ ] Índices en columnas de búsqueda frecuente
- [ ] EXPLAIN ANALYZE para queries >100ms
- [ ] Lógica de negocio en aplicación (NO stored procedures)
- [ ] Transacciones explícitas con `using` scope
- [ ] Naming: snake_case (PostgreSQL), UPPER_SNAKE_CASE (Oracle)
- [ ] Migraciones versionadas (EF Migrations / Entity Framework Migrations)
- [ ] NO queries N+1 (usar `Include()/ThenInclude()`)
- [ ] Paginación con `Skip().Take()` en colecciones grandes

---

## 5. Prohibiciones

- ❌ Concatenación de strings en queries (SQL Injection)
- ❌ `SELECT *` sin proyección
- ❌ Stored procedures para lógica de negocio
- ❌ Queries sin índices (verificar con EXPLAIN)
- ❌ Lazy loading en APIs (causa N+1)
- ❌ Transacciones sin `using` statement
- ❌ Queries síncronas (usar async/await)

---

## 6. Configuración Mínima

### PostgreSQL

```csharp
// Program.cs
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        npgsqlOptions => npgsqlOptions.EnableRetryOnFailure(3)
    ));
```

```csharp
// DbContext
public class AppDbContext : DbContext
{
    public DbSet<User> Users { get; set; }
    public DbSet<Order> Orders { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Naming snake_case
        modelBuilder.Entity<User>().ToTable("users");
        modelBuilder.Entity<User>().Property(u => u.FullName).HasColumnName("full_name");

        // Índice
        modelBuilder.Entity<User>().HasIndex(u => u.Email).IsUnique();
    }
}
```

### LINQ (Preferido)

```csharp
// ✅ Correcto: LINQ con proyección
var users = await _dbContext.Users
    .Where(u => u.IsActive)
    .Select(u => new UserDto
    {
        UserId = u.UserId,
        FullName = u.FullName,
        Email = u.Email
    })
    .ToListAsync(cancellationToken);

// ✅ Correcto: Include para relaciones
var order = await _dbContext.Orders
    .Include(o => o.OrderItems)
    .ThenInclude(oi => oi.Product)
    .FirstOrDefaultAsync(o => o.OrderId == orderId, cancellationToken);
```

### Raw SQL Parametrizado

```csharp
// ✅ Correcto: Parámetros
var users = await _dbContext.Users
    .FromSqlRaw("SELECT * FROM users WHERE email = {0}", email)
    .ToListAsync();

// ❌ INCORRECTO: Concatenación (SQL Injection)
var users = await _dbContext.Users
    .FromSqlRaw($"SELECT * FROM users WHERE email = '{email}'")
    .ToListAsync();
```

---

## 7. Validación

```bash
# Crear migración
dotnet ef migrations add AddUserEmailIndex

# Aplicar migraciones
dotnet ef database update

# Generar script SQL
dotnet ef migrations script --output migration.sql
```

```sql
-- PostgreSQL: Verificar índices
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public';

-- Analizar query
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@talma.com';

-- Verificar queries lentas (>100ms)
SELECT query, mean_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;
```

**Métricas de cumplimiento:**

| Métrica                 | Target | Verificación                  |
| ----------------------- | ------ | ----------------------------- |
| Queries parametrizadas  | 100%   | Code review: NO concatenación |
| Queries con índices     | 100%   | EXPLAIN ANALYZE sin Seq Scan  |
| Queries `<100ms`        | >95%   | pg_stat_statements            |
| Migraciones versionadas | 100%   | EF Migrations historial       |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Convenciones de Nomenclatura de Objetos de Base de Datos

### 8.1. snake_case para Todo (PostgreSQL)

- **Formato**: Minúsculas con guiones bajos
- **Ejemplo**: `user_profiles`, `order_items`, `created_at`

### 8.2. Tablas en Singular

- **Formato**: Singular, no plural
- **Ejemplo**: `user`, `order`, `product`, `order_item`

```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user(id)
);
```

### 8.3. Primary Key siempre `id`

- **Formato**: `id` (no `user_id`, `order_id` en tabla propia)
- **Tipo**: `SERIAL` o `BIGSERIAL` o `UUID`

```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100)
);

CREATE TABLE order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_amount DECIMAL(10, 2)
);
```

### 8.4. Foreign Keys con `{tabla}_id`

- **Formato**: `{tabla_referenciada}_id`
- **Constraint name**: `fk_{tabla_origen}_{columna}`

```sql
CREATE TABLE order (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,

    CONSTRAINT fk_order_user_id
        FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 8.5. Columnas de Auditoría Estándar

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

### 8.6. Índices con Prefijo `idx_`

- **Formato**: `idx_{tabla}_{columnas}[_{tipo}]`

```sql
-- Índice simple
CREATE INDEX idx_user_email ON user(email);

-- Índice compuesto
CREATE INDEX idx_order_user_created ON order(user_id, created_at);

-- Índice único
CREATE UNIQUE INDEX idx_user_username_unique ON user(username);

-- Índice GIN (full-text search)
CREATE INDEX idx_product_search_gin
ON product USING GIN(to_tsvector('spanish', name));
```

### 8.7. Constraints con Prefijos

| Tipo        | Prefijo | Formato                  | Ejemplo                |
| ----------- | ------- | ------------------------ | ---------------------- |
| Primary Key | `pk_`   | `pk_{tabla}`             | `pk_user`              |
| Foreign Key | `fk_`   | `fk_{tabla}_{columna}`   | `fk_order_user_id`     |
| Unique      | `uk_`   | `uk_{tabla}_{columnas}`  | `uk_user_email`        |
| Check       | `ck_`   | `ck_{tabla}_{condicion}` | `ck_user_age_positive` |

### 8.8. Views con Prefijo `vw_`

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

---

## 9. Convenciones de Migraciones

### 9.1. Formato con Timestamp

- **Formato**: `V{timestamp}__{descripcion}.sql`
- **Timestamp**: `YYYYMMDDHHmmss` (14 dígitos)
- **Descripción**: `snake_case` descriptivo

```text
V20240115103000__create_user_table.sql
V20240115104500__add_email_index_to_user.sql
V20240115110000__alter_order_add_status_column.sql
```

### 9.2. Verbos de Acción

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

### 9.3. Ejemplo de Migración

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

---

## 10. Referencias

- [PostgreSQL](../datos/postgresql.md)
- [Migrations](../datos/migrations.md)
- [C# y .NET](./csharp-dotnet.md) - Entity Framework
- [EF Core Documentation](https://learn.microsoft.com/ef/core/)
- [Npgsql Documentation](https://www.npgsql.org/)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance-tips.html)
- [Flyway Documentation](https://flywaydb.org/documentation/)
