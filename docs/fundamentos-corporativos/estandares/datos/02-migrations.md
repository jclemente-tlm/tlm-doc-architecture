---
id: migrations
sidebar_position: 2
title: Migraciones y Scripts de Base de Datos
description: Estándar para ejecutar migraciones de esquema y scripts de configuración con DbUp en PostgreSQL multi-tenant
---

# Estándar Técnico — Migraciones de Base de Datos

---

## 1. Propósito
Garantizar evolución controlada del esquema de base de datos mediante migraciones versionadas con DbUp para cambios de estructura (DDL) y scripts SQL para configuraciones puntuales (DML), con trazabilidad y rollback.

---

## 2. Alcance

**Aplica a:**
- Migraciones de esquema DDL (CREATE, ALTER, DROP)
- Scripts de configuración inicial (INSERT, UPDATE parámetros)
- Correcciones puntuales de datos en despliegues
- Bases de datos PostgreSQL 14+ multi-tenant

**No aplica a:**
- Cambios de datos transaccionales en tiempo real (usar APIs)
- ETL o bulk operations (usar herramientas dedicadas)
- Desarrollo local con Docker (puede usar seed scripts directos)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Migration Tool** | DbUp | 5.0+ | Migraciones versionadas .NET |
| **Base de Datos** | PostgreSQL | 14+ | Ver [ADR-010](../../../decisiones-de-arquitectura/adr-010-standard-base-datos.md) |
| **Lenguaje Scripts** | SQL puro | ANSI SQL | Evitar extensiones propietarias cuando posible |
| **Versionado** | Git | - | Scripts en `src/Database/Scripts/` |
| **CI/CD** | GitHub Actions | - | Ejecución automática en despliegue |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura. Ver [ADR-019](../../../decisiones-de-arquitectura/adr-019-configuraciones-scripts-bd.md) para justificación de DbUp.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Naming convention: `Script{VersionNumber}__{Description}.sql`
  - Ejemplo: `Script0001__CreateUsersTable.sql`
  - Ejemplo: `Script0002__AddEmailColumnToUsers.sql`
- [ ] Scripts idempotentes cuando sea posible
- [ ] Un cambio lógico = un script (no agrupar múltiples cambios)
- [ ] Orden secuencial: versiones incrementales sin gaps
- [ ] Comentarios: `-- Purpose:`, `-- Author:`, `-- Date:`
- [ ] Transacciones explícitas con `BEGIN`/`COMMIT`/`ROLLBACK`
- [ ] Testing en ambiente dev/staging antes de producción
- [ ] Rollback scripts para cambios críticos (opcional pero recomendado)
- [ ] DbUp ejecutado automáticamente en CI/CD
- [ ] Tabla de historial: `SchemaVersions` creada por DbUp

---

## 5. Prohibiciones

- ❌ Scripts sin versionado secuencial
- ❌ Cambios manuales directos en producción (usar scripts)
- ❌ Scripts no idempotentes sin documentación clara
- ❌ Dependencias de orden no documentadas
- ❌ Scripts con datos sensibles hardcodeados (usar parámetros)
- ❌ Modificar scripts ya aplicados (crear nuevo script para corrección)
- ❌ Scripts sin transacciones para cambios múltiples

---

## 6. Estructura de Proyecto

```
src/
├── Database/
│   ├── Scripts/
│   │   ├── Script0001__CreateSchema.sql
│   │   ├── Script0002__CreateUsersTable.sql
│   │   ├── Script0003__AddIndexToUsersEmail.sql
│   │   ├── Script0004__SeedInitialRoles.sql
│   │   └── Script0005__AddAuditColumnsToOrders.sql
│   └── DbUpMigrator/
│       ├── DbUpMigrator.csproj
│       └── Program.cs
└── YourService.Api/
    └── appsettings.json
```

---

## 7. Configuración Mínima

### DbUp Project (DbUpMigrator.csproj)

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="DbUp-PostgreSQL" Version="5.0.37" />
    <PackageReference Include="Npgsql" Version="8.0.1" />
  </ItemGroup>

  <ItemGroup>
    <EmbeddedResource Include="../Scripts/**/*.sql" />
  </ItemGroup>
</Project>
```

### DbUp Configuration (Program.cs)

```csharp
using System;
using System.Reflection;
using DbUp;
using DbUp.Engine;

namespace DbUpMigrator;

class Program
{
    static int Main(string[] args)
    {
        var connectionString = 
            args.Length > 0 
                ? args[0] 
                : Environment.GetEnvironmentVariable("DATABASE_URL");

        if (string.IsNullOrEmpty(connectionString))
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine("Connection string not provided");
            Console.ResetColor();
            return -1;
        }

        Console.ForegroundColor = ConsoleColor.Yellow;
        Console.WriteLine("Starting database migration...");
        Console.ResetColor();

        var upgrader =
            DeployChanges.To
                .PostgresqlDatabase(connectionString)
                .WithScriptsEmbeddedInAssembly(Assembly.GetExecutingAssembly())
                .LogToConsole()
                .Build();

        var result = upgrader.PerformUpgrade();

        if (!result.Successful)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine(result.Error);
            Console.ResetColor();
            return -1;
        }

        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine("Success!");
        Console.ResetColor();
        return 0;
    }
}
```

### Ejemplo de Script SQL

```sql
-- Script0001__CreateUsersTable.sql
-- Purpose: Create users table with multi-tenant support
-- Author: Architecture Team
-- Date: 2026-01-29

BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_users_tenant_email UNIQUE (tenant_id, email)
);

CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

COMMENT ON TABLE users IS 'Multi-tenant users table';
COMMENT ON COLUMN users.tenant_id IS 'Country code: PE, CO, EC, PA';

COMMIT;
```

### Script de Configuración Inicial

```sql
-- Script0004__SeedInitialRoles.sql
-- Purpose: Insert default roles for all tenants
-- Author: Architecture Team
-- Date: 2026-01-29

BEGIN;

INSERT INTO roles (tenant_id, name, description)
VALUES 
    ('PE', 'Admin', 'Administrator role'),
    ('PE', 'User', 'Standard user role'),
    ('CO', 'Admin', 'Administrator role'),
    ('CO', 'User', 'Standard user role'),
    ('EC', 'Admin', 'Administrator role'),
    ('EC', 'User', 'Standard user role'),
    ('PA', 'Admin', 'Administrator role'),
    ('PA', 'User', 'Standard user role')
ON CONFLICT (tenant_id, name) DO NOTHING;

COMMIT;
```

---

## 8. Ejecución en CI/CD

### GitHub Actions Workflow

```yaml
name: Database Migration

on:
  push:
    branches: [main]
    paths:
      - 'src/Database/Scripts/**'

jobs:
  migrate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      
      - name: Run DbUp Migration
        working-directory: src/Database/DbUpMigrator
        env:
          DATABASE_URL: ${{ secrets.DATABASE_CONNECTION_STRING }}
        run: |
          dotnet build
          dotnet run
```

### Docker Compose (Development)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: myapp_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"
  
  migrator:
    build:
      context: ./src/Database/DbUpMigrator
    depends_on:
      - postgres
    environment:
      DATABASE_URL: "Host=postgres;Database=myapp_dev;Username=dev;Password=dev123"
    command: dotnet run
```

---

## 9. Rollback Strategy

### Opción 1: Rollback Script (Recomendado para cambios críticos)

```sql
-- Script0005__AddAuditColumns.sql (Forward)
BEGIN;
ALTER TABLE orders ADD COLUMN created_by UUID;
ALTER TABLE orders ADD COLUMN updated_by UUID;
COMMIT;

-- Script0005_Rollback__RemoveAuditColumns.sql (Backward)
BEGIN;
ALTER TABLE orders DROP COLUMN IF EXISTS created_by;
ALTER TABLE orders DROP COLUMN IF EXISTS updated_by;
COMMIT;
```

### Opción 2: Backup antes de migración

```bash
# Pre-migration backup
pg_dump -h localhost -U postgres -d myapp_prod > backup_before_migration.sql

# Run migration
dotnet run --project src/Database/DbUpMigrator

# Rollback if needed
psql -h localhost -U postgres -d myapp_prod < backup_before_migration.sql
```

---

## 10. Validación y Testing

### Pre-deployment Checklist

```bash
# 1. Validar sintaxis SQL
psql -h localhost -U dev -d myapp_dev -f Script0001__CreateUsersTable.sql --dry-run

# 2. Ejecutar en dev
dotnet run --project src/Database/DbUpMigrator

# 3. Verificar SchemaVersions table
psql -h localhost -U dev -d myapp_dev -c "SELECT * FROM SchemaVersions ORDER BY ScriptName;"

# 4. Validar datos
psql -h localhost -U dev -d myapp_dev -c "SELECT COUNT(*) FROM users;"

# 5. Rollback test (si existe)
psql -h localhost -U dev -d myapp_dev -f Script0001_Rollback__DropUsersTable.sql
```

---

## 11. Troubleshooting

### Problema: Script ya aplicado
```
Error: Script 'Script0005__AddColumn.sql' has already been executed
```
**Solución:** Crear nuevo script con version incremental, NO modificar existente

### Problema: Error en transacción
```
Error: Syntax error in SQL script at line 15
```
**Solución:** Validar sintaxis con `psql --dry-run`, verificar que BEGIN/COMMIT estén balanceados

### Problema: Tabla SchemaVersions no existe
```
Error: relation "SchemaVersions" does not exist
```
**Solución:** DbUp crea la tabla automáticamente en primera ejecución, verificar permisos de usuario

---

## 12. Mejores Prácticas

### ✅ DO

- Scripts pequeños y atómicos (un cambio lógico por script)
- Comentarios claros con propósito y contexto
- Testing en dev/staging antes de producción
- Backup antes de migraciones críticas
- Usar transacciones para cambios múltiples
- Validar scripts con `--dry-run` cuando posible

### ❌ DON'T

- Modificar scripts ya ejecutados en producción
- Agrupar múltiples cambios no relacionados en un script
- Ejecutar cambios manuales sin versionado
- Hardcodear datos sensibles (usar variables de entorno)
- Olvidar documentar dependencias entre scripts

---

## 13. Métricas y Monitoreo

### KPIs

- **Migration success rate:** > 99%
- **Migration duration:** < 5 min (p95)
- **Rollback frequency:** < 1% de migraciones
- **Scripts con errores:** 0 en producción

### Logging

```csharp
// DbUp logs automáticos en consola
Console.WriteLine($"Executing {script.Name}...");
Console.WriteLine($"Migration completed in {elapsed}ms");
```

---

## 14. Referencias

- [DbUp Documentation](https://dbup.readthedocs.io/)
- [ADR-019: Configuraciones por Scripts en BD](../../../decisiones-de-arquitectura/adr-019-configuraciones-scripts-bd.md)
- [ADR-010: Base de Datos Estándar](../../../decisiones-de-arquitectura/adr-010-standard-base-datos.md)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
