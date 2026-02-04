---
id: schemas
sidebar_position: 10
title: Schemas y Evolución de Datos
description: Estándares unificados para validación de esquemas, evolución sin downtime, documentación de BD y gestión de schemas
---

# Estándar Técnico — Schemas y Evolución de Datos

## 1. Propósito

Garantizar integridad, calidad y evolución controlada de datos mediante validación automática de esquemas en boundaries del sistema, migrations versionadas sin downtime usando expand-contract pattern, y documentación completa de esquemas con comentarios SQL, diagramas ER y catálogos de datos.

## 2. Alcance

**Aplica a:**

- API request/response validation
- Kafka message validation (JSON Schema, NO Schema Registry)
- Cambios de schema en PostgreSQL
- Database constraints y domain types
- Migrations versionadas
- Documentation de tablas, columnas, índices

**No aplica a:**

- Datos internos ya validados
- Read-only queries sin side effects
- Health check endpoints
- Tablas temporales
- Datos inmutables (append-only)
- Schema changes en ambientes dev/test (solo prod requiere expand-contract)

## 3. Tecnologías Aprobadas

| Componente          | Tecnología            | Versión mínima | Observaciones                                      |
| ------------------- | --------------------- | -------------- | -------------------------------------------------- |
| **API Validation**  | FluentValidation      | 11.8+          | Preferido para .NET                                |
| **Data Annotation** | System.ComponentModel | .NET 8+        | Para validaciones simples                          |
| **JSON Schema**     | NJsonSchema           | 11.0+          | Validación de JSON                                 |
| **DB Constraints**  | PostgreSQL CHECK      | 14+            | Validación en BD                                   |
| **Kafka**           | JSON Schema           | -              | Validación embebida (NO Confluent Schema Registry) |
| **OpenAPI**         | Swashbuckle           | 6.5+           | API contract validation                            |
| **Migrations**      | EF Core Migrations    | 8.0+           | .NET native migrations                             |
| **Testing**         | Respawn               | 6.0+           | Reset DB para integration tests                    |
| **Monitoring**      | Grafana Mimir         | 2.10+          | Métricas de migration duration                     |
| **Rollback**        | pg_restore            | PostgreSQL 14+ | Point-in-time recovery                             |
| **Diagrams**        | dbdiagram.io          | -              | ER diagrams as code                                |
| **Diagrams**        | PlantUML              | 1.2023+        | Alternativa text-based                             |
| **Schema Docs**     | SchemaSpy             | 6.2+           | Auto-generate HTML docs                            |
| **SQL Comments**    | COMMENT ON            | PostgreSQL 14+ | Native SQL comments                                |
| **Data Catalog**    | Backstage             | 1.20+          | Service catalog con DB metadata                    |
| **ER Tool**         | DBeaver               | 23.0+          | Visual ER diagrams                                 |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

## 4. Schema Validation

### Requisitos Obligatorios 🔴

#### Validation Layers

- [ ] **API Layer:** validar inputs antes de procesar
- [ ] **Application Layer:** validar business rules
- [ ] **Domain Layer:** validar invariantes del dominio
- [ ] **Database Layer:** constraints para data integrity final
- [ ] **Event Layer:** validar mensajes con JSON Schema (NO Schema Registry)

#### FluentValidation Rules

- [ ] Validators registrados en DI container
- [ ] Validación automática en controllers (filter)
- [ ] Mensajes de error descriptivos
- [ ] Reglas de negocio documentadas en validators
- [ ] Tests unitarios de validators

#### Error Responses

- [ ] RFC 7807 Problem Details format
- [ ] HTTP 400 Bad Request para validation errors
- [ ] Array de errores con field names
- [ ] Mensajes user-friendly (no stack traces)
- [ ] Correlation ID para debugging

#### Database Constraints

- [ ] NOT NULL para campos obligatorios
- [ ] CHECK constraints para business rules
- [ ] UNIQUE constraints para unicidad
- [ ] Foreign keys para integridad referencial
- [ ] Domain types para validación de tipos

#### Performance

- [ ] Validación fail-fast (stop on first error configurable)
- [ ] Async validation solo cuando necesario
- [ ] Cache de validation rules cuando sea posible
- [ ] No validar datos ya validados (trust boundaries)

### Prohibiciones

- ❌ Aceptar inputs sin validar
- ❌ Validación solo en frontend (trust but verify)
- ❌ Stack traces en error responses a clientes
- ❌ Mensajes de error genéricos ("Invalid input")
- ❌ Ignorar database constraints
- ❌ Validación custom sin tests
- ❌ Validación sincrónica de operaciones lentas (llamadas externas)

### Configuración Mínima

#### FluentValidation Setup

```csharp
// Program.cs
using FluentValidation;
using FluentValidation.AspNetCore;

var builder = WebApplication.CreateBuilder(args);

// Registrar FluentValidation
builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddFluentValidationClientsideAdapters();
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// Configurar behavior de validación
builder.Services.AddControllers()
    .ConfigureApiBehaviorOptions(options =>
    {
        options.InvalidModelStateResponseFactory = context =>
        {
            var problemDetails = new ValidationProblemDetails(context.ModelState)
            {
                Type = "https://tools.ietf.org/html/rfc7231#section-6.5.1",
                Title = "One or more validation errors occurred.",
                Status = StatusCodes.Status400BadRequest,
                Detail = "See the errors property for details.",
                Instance = context.HttpContext.Request.Path
            };

            problemDetails.Extensions["traceId"] = context.HttpContext.TraceIdentifier;

            return new BadRequestObjectResult(problemDetails)
            {
                ContentTypes = { "application/problem+json" }
            };
        };
    });

var app = builder.Build();
app.Run();
```

#### Validator Example

```csharp
// Validators/CreateOrderRequestValidator.cs
using FluentValidation;

public class CreateOrderRequestValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderRequestValidator()
    {
        RuleFor(x => x.CustomerId)
            .NotEmpty()
            .WithMessage("Customer ID is required");

        RuleFor(x => x.Items)
            .NotEmpty()
            .WithMessage("Order must contain at least one item")
            .Must(items => items.Count <= 100)
            .WithMessage("Order cannot contain more than 100 items");

        RuleForEach(x => x.Items)
            .SetValidator(new OrderItemRequestValidator());

        RuleFor(x => x.Notes)
            .MaximumLength(500)
            .WithMessage("Notes cannot exceed 500 characters")
            .When(x => !string.IsNullOrEmpty(x.Notes));
    }
}

public class OrderItemRequestValidator : AbstractValidator<OrderItemRequest>
{
    public OrderItemRequestValidator()
    {
        RuleFor(x => x.ProductId)
            .NotEmpty()
            .WithMessage("Product ID is required");

        RuleFor(x => x.Quantity)
            .GreaterThan(0)
            .WithMessage("Quantity must be greater than 0")
            .LessThanOrEqualTo(1000)
            .WithMessage("Quantity cannot exceed 1000 per item");
    }
}
```

#### Database Constraints

```sql
-- Validación en BD (última línea de defensa)
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    order_number VARCHAR(20) NOT NULL UNIQUE,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- CHECK constraints para business rules
    CONSTRAINT check_total_positive CHECK (total_amount >= 0),
    CONSTRAINT check_status_valid CHECK (
        status IN ('PENDING', 'PAID', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED')
    )
);

-- Domain types para reutilizar validaciones
CREATE DOMAIN email AS VARCHAR(255)
CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');

CREATE DOMAIN phone AS VARCHAR(20)
CHECK (VALUE ~* '^\+[1-9]\d{1,14}$');  -- E.164 format

CREATE TABLE customers (
    id UUID PRIMARY KEY,
    email email NOT NULL,
    phone phone NULL
);
```

## 5. Schema Evolution

### Requisitos Obligatorios 🔴

#### Backward Compatibility

- [ ] **Nuevos cambios NO rompen versión actual** de la aplicación
- [ ] Columnas nuevas deben ser nullable o tener default
- [ ] No eliminar columnas en uso (deprecar primero)
- [ ] No cambiar tipos de datos incompatibles directamente
- [ ] Tests de compatibility en CI/CD

#### Expand-Contract Pattern

- [ ] **Expand:** agregar nuevos elementos (columnas, índices)
- [ ] **Migrate:** aplicación usa ambas versiones (dual-write period)
- [ ] **Contract:** eliminar elementos obsoletos después de confirmación
- [ ] Mínimo 1 sprint entre expand y contract

#### Versioned Migrations

- [ ] Migrations numeradas secuencialmente (V1, V2, V3...)
- [ ] Una migration por cambio lógico
- [ ] Migrations idempotentes (pueden re-ejecutarse)
- [ ] Rollback script para migrations críticas
- [ ] Testing en staging antes de prod

#### Zero-Downtime Deployments

- [ ] No locks largos en tablas productivas
- [ ] CREATE INDEX CONCURRENTLY para índices grandes
- [ ] ALTER TABLE sin exclusive locks (usar locks advisory cuando sea posible)
- [ ] Timeouts configurados en migrations (max 5 min)

#### Auditoría

- [ ] Logging de todas las migrations ejecutadas
- [ ] Timestamp de ejecución
- [ ] Duración de cada migration
- [ ] Alertas si migration falla o excede tiempo

### Prohibiciones

- ❌ Cambios de schema directos en producción (sin migrations)
- ❌ Eliminar columnas sin periodo de deprecación
- ❌ Cambios breaking sin expand-contract
- ❌ ALTER TABLE con locks exclusivos largos
- ❌ Migrations sin rollback plan
- ❌ Data migrations masivos en horario pico
- ❌ Migrations sin testing previo

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

### Expand-Contract Pattern - Rename Column

```sql
-- FASE 1: EXPAND - V3__expand_rename_email.sql
-- Add new column, keep old one
-- Breaking: No

-- Agregar nueva columna
ALTER TABLE customers
ADD COLUMN email_address VARCHAR(255) NULL;

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

DROP TRIGGER IF EXISTS trg_sync_email ON customers;
DROP FUNCTION IF EXISTS sync_email_columns();

ALTER TABLE customers
DROP COLUMN email;

ALTER TABLE customers
RENAME COLUMN email_address TO email;
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
```

## 6. Schema Documentation

### Requisitos Obligatorios 🔴

#### Comentarios SQL

- [ ] **Todas las tablas** deben tener COMMENT con propósito
- [ ] **Todas las columnas críticas** con COMMENT explicativo
- [ ] Foreign keys con COMMENT indicando relación
- [ ] Índices complejos con COMMENT de justificación
- [ ] Constraints con COMMENT de business rule

#### Diagramas ER

- [ ] Diagrama ER actualizado por bounded context
- [ ] Relaciones PK/FK claramente marcadas
- [ ] Cardinalidad (1:1, 1:N, N:M) especificada
- [ ] Stored en repositorio (dbdiagram.io, PlantUML)
- [ ] Generado automáticamente cuando sea posible

#### Data Dictionary

- [ ] Catálogo de entidades con descripción
- [ ] Tipos de datos y constraints documentados
- [ ] Ownership de tabla especificado
- [ ] Campos PII marcados explícitamente
- [ ] Retention policies documentadas

#### Migrations con Descripción

- [ ] Cada migration con comentario de propósito
- [ ] Breaking changes claramente marcados
- [ ] Rollback procedure documentado
- [ ] Deployment notes cuando aplique

#### Actualización Continua

- [ ] Documentación actualizada en cada schema change
- [ ] Pull requests incluyen doc updates
- [ ] Automated checks de comments faltantes
- [ ] Quarterly review de doc accuracy

### Prohibiciones

- ❌ Tablas sin COMMENT
- ❌ Columnas críticas sin descripción
- ❌ Foreign keys sin documentar relación
- ❌ Diagramas ER desactualizados
- ❌ Nombres de columnas ambiguos sin explicación
- ❌ Schema changes sin update de documentación
- ❌ Documentación solo en wikis externos (debe estar en código)

### SQL Comments en PostgreSQL

```sql
-- Tabla con documentación completa
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    order_number VARCHAR(20) NOT NULL UNIQUE,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP NULL,
    CONSTRAINT check_total_positive CHECK (total_amount >= 0)
);

-- Comentarios de tabla
COMMENT ON TABLE orders IS
'Órdenes de clientes. Owner: orders-service.
Contiene todas las órdenes del sistema (activas y históricas).
Retention: 7 años para cumplimiento fiscal.
PII: No contiene datos personales directos (solo customer_id).';

-- Comentarios de columnas
COMMENT ON COLUMN orders.customer_id IS
'Referencia al cliente owner de la orden.
FK lógica a customers_service.customers.id (no FK física cross-service).
Usar Customers API para obtener datos del cliente.';

COMMENT ON COLUMN orders.status IS
'Estado actual de la orden. Valores válidos:
- PENDING: Creada, pendiente de pago
- PAID: Pago confirmado
- PROCESSING: En preparación
- SHIPPED: Enviada
- DELIVERED: Entregada
- CANCELLED: Cancelada';

-- Índices con comentarios
CREATE INDEX idx_orders_customer ON orders(customer_id)
WHERE deleted_at IS NULL;

COMMENT ON INDEX idx_orders_customer IS
'Índice para queries por cliente (ej: GET /customers/{id}/orders).
Partial index: excluye deleted records para eficiencia.';
```

### dbdiagram.io Schema as Code

```dbml
// orders_service.dbml
// ER Diagram for Orders Service
// Owner: Platform Team

Table orders {
  id uuid [pk, note: 'UUID v4']
  customer_id uuid [not null, note: 'Logical FK to customers_service']
  order_number varchar(20) [unique, not null]
  total_amount decimal(10,2) [not null]
  status varchar(20) [not null, note: 'PENDING|PAID|PROCESSING|SHIPPED|DELIVERED|CANCELLED']
  created_at timestamp [not null, default: `now()`]
  updated_at timestamp [not null, default: `now()`]
  deleted_at timestamp [null, note: 'Soft delete']

  Note: 'Customer orders. Retention: 7 years. PII: No.'
}

Table order_items {
  id uuid [pk]
  order_id uuid [not null, ref: > orders.id]
  product_id uuid [not null, note: 'Logical FK to catalog_service']
  quantity int [not null]
  unit_price decimal(10,2) [not null]
  created_at timestamp [not null, default: `now()`]

  Note: 'Line items for orders. Cascade delete with order.'
}

// Relationships
Ref: order_items.order_id > orders.id [delete: cascade]
```

## 7. Nota sobre Schema Registry

**⚠️ Talma NO utiliza:**

- ❌ Confluent Schema Registry
- ❌ Confluent Platform
- ❌ Apicurio Registry
- ❌ Apache Avro para Kafka
- ❌ Protobuf para Kafka

**En su lugar, usar:**
✅ **JSON Schema** con validación embebida en productores/consumidores

**Razón:** Implementación propia con Apache Kafka KRaft mode (sin Zookeeper) y validación JSON Schema en aplicación, sin infraestructura adicional de Schema Registry.

Ver estándar vigente: [Kafka Messaging](kafka-messaging.md)

## 8. Validación

### Schema Validation

**Comandos de validación:**

```bash
# Tests unitarios de validators
dotnet test --filter Category=Validation

# Verificar constraints en BD
psql -d talma_db -c "SELECT conname, contype, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'orders'::regclass;"

# Validar JSON Schema
jq -s '.[0] as $schema | .[1] | . as $data | $schema | . as $s | $data | if . then "VALID" else "INVALID" end' schema.json data.json
```

**Métricas de cumplimiento:**

| Métrica                  | Target | Verificación                                  |
| ------------------------ | ------ | --------------------------------------------- |
| Validation errors rate   | `<1%`  | `rate(http_requests_total{status="400"}[5m])` |
| DB constraint violations | 0      | Logs PostgreSQL                               |
| Validator test coverage  | >90%   | Code coverage reports                         |

### Schema Evolution

**Pre-producción:**

- Validar migrations en staging
- Confirmar backward compatibility
- Verificar timeouts `<5min`
- Probar rollback scripts

**Post-producción:**

- Monitorear duración de migrations
- Alertas si migration falla o excede tiempo
- Validar NO hay locks largos

**Métricas:**

```promql
# Migration duration
histogram_quantile(0.95, db_migration_duration_seconds)

# Migration failures
rate(db_migration_duration_seconds{result="failure"}[5m])
```

### Schema Documentation

**CI/CD Check:**

```bash
#!/bin/bash
# Falla el build si hay tablas sin comentarios

UNDOCUMENTED=$(psql -t -c "
SELECT COUNT(*)
FROM information_schema.tables t
WHERE t.table_schema = 'public'
  AND t.table_type = 'BASE TABLE'
  AND obj_description((t.table_schema||'.'||t.table_name)::regclass::oid) IS NULL
")

if [ "$UNDOCUMENTED" -gt 0 ]; then
  echo "ERROR: $UNDOCUMENTED tables without COMMENT"
  exit 1
fi

echo "✓ All tables documented"
```

## 9. Prohibiciones Generales

- ❌ Aceptar inputs sin validar
- ❌ Validación solo en frontend
- ❌ Stack traces en error responses
- ❌ Ignorar database constraints
- ❌ Cambios de schema sin migrations
- ❌ Eliminar columnas sin expand-contract
- ❌ ALTER TABLE con locks largos
- ❌ Migrations sin rollback plan
- ❌ Tablas sin COMMENT
- ❌ Schema changes sin doc updates
- ❌ Usar Confluent Schema Registry (NO aprobado)

## 10. Referencias

- [FluentValidation Documentation](https://docs.fluentvalidation.net/)
- [RFC 7807 - Problem Details](https://www.rfc-editor.org/rfc/rfc7807)
- [JSON Schema Specification](https://json-schema.org/)
- [PostgreSQL Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL COMMENT](https://www.postgresql.org/docs/current/sql-comment.html)
- [CREATE INDEX CONCURRENTLY](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY)
- [dbdiagram.io](https://dbdiagram.io/home)
- [PlantUML](https://plantuml.com/)
- "Domain-Driven Design" - Eric Evans
- "Refactoring Databases" - Scott Ambler
- "Database Reliability Engineering" (O'Reilly)
