---
id: data-lifecycle
sidebar_position: 5
title: Data Lifecycle Management
description: Estándar para gestión del ciclo de vida de datos (retention, archival, deletion) conforme a regulaciones
---

# Estándar Técnico — Data Lifecycle Management

---

## 1. Propósito

Establecer políticas y automatización para el ciclo de vida completo de datos, desde creación hasta eliminación, cumpliendo con regulaciones (GDPR, SOC 2) y optimizando costos de almacenamiento.

---

## 2. Alcance

**Aplica a:**

- Datos de clientes (PII)
- Logs de aplicaciones y auditoría
- Datos transaccionales históricos
- Archivos y documentos
- Backups y snapshots
- Datos de analytics y métricas

**No aplica a:**

- Datos con retención legal indefinida
- Registros contables (sujetos a ley fiscal)
- Datos en procesamiento activo

---

## 3. Tecnologías Aprobadas

| Componente       | Tecnología            | Versión mínima | Observaciones                    |
| ---------------- | --------------------- | -------------- | -------------------------------- |
| **Archival**     | AWS S3 Glacier        | -              | Storage class transitions        |
| **Soft Delete**  | PostgreSQL temporal   | 14+            | Columnas deleted_at              |
| **Partitioning** | PostgreSQL partitions | 14+            | Por rango de fechas              |
| **Jobs**         | Hangfire              | 1.8+           | Scheduled cleanup jobs           |
| **Compliance**   | AWS Config Rules      | -              | Validación de retention policies |
| **Encryption**   | AWS KMS               | -              | Encryption at rest               |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Políticas de Retención

- [ ] **Documentar retention period** por tipo de dato (ej: logs 90 días)
- [ ] **GDPR compliance:** datos personales max 2 años sin actividad
- [ ] **Logs de auditoría:** mínimo 7 años (regulaciones financieras)
- [ ] **Backups:** retención según RTO/RPO (típicamente 30 días)
- [ ] Políticas aprobadas por Legal y Compliance

### Eliminación Segura

- [ ] **Soft delete** por default (columna `deleted_at`)
- [ ] **Hard delete** solo después de grace period (30-90 días)
- [ ] **Anonymization** para datos con valor estadístico
- [ ] **Crypto-shredding:** eliminar encryption keys para hard delete
- [ ] Audit log de eliminaciones permanentes

### Archivado (Archival)

- [ ] Mover datos antiguos a storage de bajo costo (S3 Glacier, Azure Archive)
- [ ] Particionamiento por fecha para facilitar archivado
- [ ] Índices optimizados para queries de datos activos
- [ ] Proceso de restore documentado para datos archivados

### Automatización

- [ ] Jobs programados para cleanup automático
- [ ] Monitoreo de espacio en disco y storage costs
- [ ] Alertas cuando retention policies no se cumplen
- [ ] Métricas de datos eliminados/archivados

### Derecho al Olvido (GDPR)

- [ ] API para eliminar todos los datos de un cliente
- [ ] Proceso < 30 días para completar eliminación
- [ ] Confirmación de eliminación al solicitante
- [ ] Logs de solicitudes de eliminación

---

## 5. Prohibiciones

- ❌ Hard delete sin grace period
- ❌ Retención indefinida sin justificación legal
- ❌ Eliminación sin audit trail
- ❌ Datos sensibles sin encriptación at-rest
- ❌ Backup sin retention policy
- ❌ Ignorar solicitudes de GDPR/derecho al olvido
- ❌ Archivado sin proceso de restore documentado

---

## 6. Configuración Mínima

### PostgreSQL con Soft Delete

```sql
-- Pattern: columna deleted_at
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP NULL  -- Soft delete
);

CREATE INDEX idx_customers_active ON customers(id) WHERE deleted_at IS NULL;
CREATE INDEX idx_customers_deleted ON customers(deleted_at) WHERE deleted_at IS NOT NULL;

-- View de datos activos
CREATE VIEW customers_active AS
SELECT * FROM customers WHERE deleted_at IS NULL;

-- Soft delete function
CREATE OR REPLACE FUNCTION soft_delete_customer(p_customer_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE customers
    SET deleted_at = NOW()
    WHERE id = p_customer_id
      AND deleted_at IS NULL;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Hard delete después de grace period (90 días)
CREATE OR REPLACE FUNCTION hard_delete_old_records()
RETURNS INT AS $$
DECLARE
    v_deleted_count INT;
BEGIN
    WITH deleted AS (
        DELETE FROM customers
        WHERE deleted_at < NOW() - INTERVAL '90 days'
        RETURNING id
    )
    SELECT COUNT(*) INTO v_deleted_count FROM deleted;

    -- Audit log
    INSERT INTO deletion_audit (
        table_name, deleted_count, deletion_date
    ) VALUES (
        'customers', v_deleted_count, NOW()
    );

    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;
```

### EF Core con Soft Delete

```csharp
// Domain/Entities/BaseEntity.cs
public abstract class BaseEntity
{
    public Guid Id { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public DateTime? DeletedAt { get; set; }  // Soft delete

    public bool IsDeleted => DeletedAt.HasValue;
}

// Data/TalmaDbContext.cs
public class TalmaDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Global query filter para soft delete
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            if (typeof(BaseEntity).IsAssignableFrom(entityType.ClrType))
            {
                var parameter = Expression.Parameter(entityType.ClrType, "e");
                var property = Expression.Property(parameter, nameof(BaseEntity.DeletedAt));
                var filter = Expression.Lambda(
                    Expression.Equal(property, Expression.Constant(null)),
                    parameter);

                modelBuilder.Entity(entityType.ClrType).HasQueryFilter(filter);
            }
        }
    }

    public override int SaveChanges()
    {
        UpdateTimestamps();
        return base.SaveChanges();
    }

    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        UpdateTimestamps();
        return base.SaveChangesAsync(cancellationToken);
    }

    private void UpdateTimestamps()
    {
        var entries = ChangeTracker.Entries<BaseEntity>();

        foreach (var entry in entries)
        {
            if (entry.State == EntityState.Added)
            {
                entry.Entity.CreatedAt = DateTime.UtcNow;
                entry.Entity.UpdatedAt = DateTime.UtcNow;
            }
            else if (entry.State == EntityState.Modified)
            {
                entry.Entity.UpdatedAt = DateTime.UtcNow;
            }
        }
    }
}

// Application/Services/CustomerService.cs
public class CustomerService
{
    private readonly TalmaDbContext _context;

    // Soft delete
    public async Task SoftDeleteCustomerAsync(Guid customerId)
    {
        var customer = await _context.Customers.FindAsync(customerId);
        if (customer == null)
            throw new NotFoundException();

        customer.DeletedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();
    }

    // Incluir deleted explícitamente
    public async Task<Customer?> GetCustomerIncludingDeletedAsync(Guid customerId)
    {
        return await _context.Customers
            .IgnoreQueryFilters()
            .FirstOrDefaultAsync(c => c.Id == customerId);
    }
}
```

### Hangfire Job para Cleanup

```csharp
// Jobs/DataCleanupJob.cs
public class DataCleanupJob
{
    private readonly TalmaDbContext _context;
    private readonly ILogger<DataCleanupJob> _logger;

    // Ejecutar diariamente a las 2 AM
    [AutomaticRetry(Attempts = 3)]
    public async Task HardDeleteOldRecordsAsync()
    {
        var gracePeriod = DateTime.UtcNow.AddDays(-90);

        // Customers
        var deletedCustomers = await _context.Customers
            .IgnoreQueryFilters()
            .Where(c => c.DeletedAt < gracePeriod)
            .ToListAsync();

        _context.Customers.RemoveRange(deletedCustomers);

        // Orders
        var deletedOrders = await _context.Orders
            .IgnoreQueryFilters()
            .Where(o => o.DeletedAt < gracePeriod)
            .ToListAsync();

        _context.Orders.RemoveRange(deletedOrders);

        await _context.SaveChangesAsync();

        _logger.LogInformation(
            "Hard deleted {CustomerCount} customers and {OrderCount} orders",
            deletedCustomers.Count,
            deletedOrders.Count);
    }

    // Archivar datos antiguos
    [AutomaticRetry(Attempts = 3)]
    public async Task ArchiveOldOrdersAsync()
    {
        var archiveDate = DateTime.UtcNow.AddYears(-2);

        var oldOrders = await _context.Orders
            .Where(o => o.CreatedAt < archiveDate)
            .Include(o => o.Items)
            .ToListAsync();

        // Exportar a S3
        var s3Client = new AmazonS3Client();
        var exportData = JsonSerializer.Serialize(oldOrders);

        await s3Client.PutObjectAsync(new PutObjectRequest
        {
            BucketName = "talma-archive",
            Key = $"orders/archive_{DateTime.UtcNow:yyyyMMdd}.json",
            ContentBody = exportData,
            StorageClass = S3StorageClass.Glacier
        });

        // Eliminar de DB activa
        _context.Orders.RemoveRange(oldOrders);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Archived {Count} old orders to S3 Glacier", oldOrders.Count);
    }
}

// Program.cs - Registration
builder.Services.AddHangfire(config =>
{
    config.UsePostgreSqlStorage(connectionString);
});

builder.Services.AddHangfireServer();

var app = builder.Build();

// Schedule recurring jobs
var recurringJobManager = app.Services.GetRequiredService<IRecurringJobManager>();

recurringJobManager.AddOrUpdate<DataCleanupJob>(
    "hard-delete-old-records",
    job => job.HardDeleteOldRecordsAsync(),
    Cron.Daily(2)); // 2 AM daily

recurringJobManager.AddOrUpdate<DataCleanupJob>(
    "archive-old-orders",
    job => job.ArchiveOldOrdersAsync(),
    Cron.Monthly(1, 3)); // 1st of month, 3 AM
```

### GDPR Right to be Forgotten

```csharp
public class GDPRService
{
    private readonly TalmaDbContext _context;
    private readonly ILogger<GDPRService> _logger;

    public async Task<DeletionReport> DeleteAllCustomerDataAsync(Guid customerId)
    {
        var report = new DeletionReport
        {
            CustomerId = customerId,
            RequestedAt = DateTime.UtcNow,
            DeletedEntities = new List<string>()
        };

        using var transaction = await _context.Database.BeginTransactionAsync();

        try
        {
            // 1. Anonimizar datos personales
            var customer = await _context.Customers.FindAsync(customerId);
            if (customer != null)
            {
                customer.Email = $"deleted_{customerId}@anonymized.com";
                customer.Name = "[DELETED]";
                customer.Phone = null;
                customer.Address = null;
                customer.DeletedAt = DateTime.UtcNow;
                report.DeletedEntities.Add("Customer profile anonymized");
            }

            // 2. Eliminar ordenes (mantener aggregados para analytics)
            var orders = await _context.Orders
                .Where(o => o.CustomerId == customerId)
                .ToListAsync();

            foreach (var order in orders)
            {
                order.CustomerId = Guid.Empty;  // Desasocia del cliente
                order.DeletedAt = DateTime.UtcNow;
            }

            report.DeletedEntities.Add($"{orders.Count} orders anonymized");

            // 3. Eliminar PII en otros bounded contexts
            await DeleteCustomerFromIdentityServiceAsync(customerId);
            await DeleteCustomerFromMarketingServiceAsync(customerId);

            await _context.SaveChangesAsync();
            await transaction.CommitAsync();

            report.CompletedAt = DateTime.UtcNow;
            report.Success = true;

            // Audit log
            _logger.LogWarning(
                "GDPR deletion completed for customer {CustomerId}",
                customerId);

            return report;
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync();

            _logger.LogError(ex, "GDPR deletion failed for customer {CustomerId}", customerId);

            report.Success = false;
            report.ErrorMessage = ex.Message;
            return report;
        }
    }
}
```

---

## 7. Ejemplos

### S3 Lifecycle Policy

```json
{
  "Rules": [
    {
      "Id": "ArchiveOldLogs",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "logs/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Retention policies documentadas por tipo de dato
- [ ] Soft delete implementado en todas las entidades
- [ ] Jobs de cleanup programados
- [ ] GDPR right to be forgotten implementado
- [ ] Audit logs de eliminaciones permanentes
- [ ] Archival a storage de bajo costo configurado
- [ ] Proceso de restore documentado y probado

### Métricas

```promql
# Datos eliminados por día
sum(rate(data_deleted_records_total[1d]))

# Storage cost por tier
aws_s3_bucket_size_bytes{storage_class="GLACIER"}
```

### Queries de Auditoría

```sql
-- Revisar eliminaciones recientes
SELECT * FROM deletion_audit
WHERE deletion_date > NOW() - INTERVAL '7 days'
ORDER BY deletion_date DESC;

-- Verificar datos fuera de retention policy
SELECT COUNT(*) FROM orders
WHERE created_at < NOW() - INTERVAL '2 years'
  AND deleted_at IS NULL;
```

---

## 9. Referencias

**Regulaciones:**

- GDPR (General Data Protection Regulation)
- SOC 2 Type II
- PCI DSS

**Documentación:**

- [AWS S3 Lifecycle Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [PostgreSQL Table Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)

**Buenas prácticas:**

- "Database Reliability Engineering" (O'Reilly)
- GDPR Developer Guide
