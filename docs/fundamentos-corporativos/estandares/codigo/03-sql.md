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
- Scripts de migración (EF Migrations / Flyway 10.0+)

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
- [ ] Migraciones versionadas (EF Migrations / Flyway)
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

## 8. Referencias

- [Convenciones - Objetos Base de Datos](../../convenciones/codigo/04-objetos-base-datos.md)
- [PostgreSQL](../datos/01-postgresql.md)
- [Migrations](../datos/02-migrations.md)
- [EF Core Documentation](https://learn.microsoft.com/ef/core/)
- [Npgsql Documentation](https://www.npgsql.org/)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance-tips.html)
