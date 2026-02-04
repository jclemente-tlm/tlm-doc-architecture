---
id: data-retention
sidebar_position: 8
title: Retención y Eliminación de Datos
description: Estándar para políticas de retención de datos según GDPR, automatización de eliminación y right to be forgotten con auditoría
---

# Estándar Técnico — Retención y Eliminación de Datos

---

## 1. Propósito

Establecer políticas de retención y eliminación de datos cumpliendo GDPR (Right to Erasure), automatizando soft-deletes, hard-deletes programados y right to be forgotten, con auditoría completa de operaciones.

---

## 2. Alcance

**Aplica a:**

- Datos personales (PII)
- Registros de auditoría
- Logs de aplicación
- Backups
- Datos financieros (SOX)
- Datos de clientes inactivos

**No aplica a:**

- Datos agregados anonimizados
- Metadatos de sistema (sin PII)

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología     | Versión mínima | Observaciones                   |
| ----------------- | -------------- | -------------- | ------------------------------- |
| **Database**      | PostgreSQL     | 14+            | Soft delete + scheduled cleanup |
| **Job Scheduler** | Hangfire       | 1.8+           | .NET background jobs            |
| **Audit**         | CloudTrail     | -              | Immutable logs                  |
| **Compliance**    | Manual reviews | -              | Quarterly audits                |
| **Encryption**    | AWS KMS        | -              | Encrypt before delete           |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Políticas de Retención

- [ ] **PII**: 7 años desde última actividad (regulatorio)
- [ ] **Financiero**: 7 años (SOX, regulación local)
- [ ] **Logs aplicación**: 90 días
- [ ] **Logs auditoría**: 7 años (inmutable)
- [ ] **Backups**: 30 días
- [ ] **Usuarios inactivos**: 2 años sin login → notificar → 30 días → eliminar

### Soft Delete

- [ ] **deleted_at**: Columna en todas las tablas críticas
- [ ] **Query filters**: Excluir soft-deleted por defecto
- [ ] **Hard delete**: Después de período de gracia (30-90 días)

### Right to be Forgotten (GDPR)

- [ ] **API endpoint**: POST /api/gdpr/erase-user-data
- [ ] **Validación**: Verificar identidad + consentimiento
- [ ] **Eliminación completa**: Todos los datos del usuario
- [ ] **Auditoría**: Registrar solicitud y ejecución
- [ ] **Confirmación**: Email al usuario

### Automatización

- [ ] **Jobs diarios**: Cleanup de datos expirados
- [ ] **Notificaciones**: Avisar antes de eliminar
- [ ] **Rollback**: Backup antes de hard delete

---

## 5. PostgreSQL - Soft Delete

### Schema Design

```sql
-- Tabla con soft delete
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(2) NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,  -- NULL = activo, NOT NULL = eliminado

    CONSTRAINT chk_deleted_at CHECK (deleted_at IS NULL OR deleted_at >= created_at)
);

CREATE INDEX idx_customers_deleted_at ON customers(deleted_at) WHERE deleted_at IS NOT NULL;
```

### Views para Datos Activos

```sql
-- View con solo registros activos
CREATE VIEW customers_active AS
SELECT *
FROM customers
WHERE deleted_at IS NULL;

-- Usar en queries
SELECT * FROM customers_active WHERE email = 'user@example.com';
```

### Funciones de Cleanup

```sql
-- Hard delete de registros soft-deleted hace > 90 días
CREATE OR REPLACE FUNCTION cleanup_soft_deleted_customers()
RETURNS INTEGER AS $$
DECLARE
  rows_deleted INTEGER;
BEGIN
  -- Backup antes de eliminar
  INSERT INTO customers_deleted_archive
  SELECT * FROM customers
  WHERE deleted_at IS NOT NULL
    AND deleted_at < NOW() - INTERVAL '90 days';

  -- Hard delete
  DELETE FROM customers
  WHERE deleted_at IS NOT NULL
    AND deleted_at < NOW() - INTERVAL '90 days';

  GET DIAGNOSTICS rows_deleted = ROW_COUNT;

  -- Audit log
  INSERT INTO data_deletion_audit (table_name, rows_deleted, deleted_at)
  VALUES ('customers', rows_deleted, NOW());

  RETURN rows_deleted;
END;
$$ LANGUAGE plpgsql;

-- Ejecutar manualmente o con cron
SELECT cleanup_soft_deleted_customers();
```

---

## 6. .NET - Soft Delete

### Entity Base Class

```csharp
// Entities/SoftDeletableEntity.cs
public abstract class SoftDeletableEntity
{
    public DateTime? DeletedAt { get; set; }

    public bool IsDeleted => DeletedAt.HasValue;

    public void SoftDelete()
    {
        DeletedAt = DateTime.UtcNow;
    }

    public void Restore()
    {
        DeletedAt = null;
    }
}

public class Customer : SoftDeletableEntity, ITenantEntity
{
    public Guid Id { get; set; }
    public string TenantId { get; set; } = null!;
    public string Email { get; set; } = null!;
    public string FullName { get; set; } = null!;
    public DateTime CreatedAt { get; set; }
}
```

### DbContext con Query Filter

```csharp
// Data/ApplicationDbContext.cs
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    base.OnModelCreating(modelBuilder);

    // Global query filter: excluir soft-deleted
    modelBuilder.Entity<Customer>().HasQueryFilter(e => e.DeletedAt == null);
    modelBuilder.Entity<Payment>().HasQueryFilter(e => e.DeletedAt == null);

    // Si necesitas incluir soft-deleted explícitamente:
    // dbContext.Customers.IgnoreQueryFilters().Where(...)
}

public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
{
    // Interceptar deletes y convertir a soft-delete
    var deletedEntries = ChangeTracker.Entries()
        .Where(e => e.State == EntityState.Deleted && e.Entity is SoftDeletableEntity);

    foreach (var entry in deletedEntries)
    {
        entry.State = EntityState.Modified;
        ((SoftDeletableEntity)entry.Entity).SoftDelete();
    }

    return await base.SaveChangesAsync(cancellationToken);
}
```

---

## 7. GDPR - Right to be Forgotten

### API Endpoint

```csharp
// Controllers/GdprController.cs
[ApiController]
[Route("api/gdpr")]
public class GdprController : ControllerBase
{
    private readonly IGdprService _gdprService;
    private readonly ILogger<GdprController> _logger;

    [HttpPost("erase-user-data")]
    [Authorize]  // Usuario debe estar autenticado
    public async Task<IActionResult> EraseUserData([FromBody] EraseUserDataRequest request)
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (userId == null)
        {
            return Unauthorized();
        }

        // Validar consentimiento
        if (!request.ConfirmErasure || request.ConfirmationCode != await _gdprService.GetConfirmationCodeAsync(userId))
        {
            return BadRequest("Invalid confirmation");
        }

        // Crear solicitud de eliminación (asíncrono)
        var erasureRequestId = await _gdprService.CreateErasureRequestAsync(userId);

        _logger.LogWarning(
            "GDPR erasure request created for user {UserId}. Request ID: {RequestId}",
            userId,
            erasureRequestId);

        return Ok(new
        {
            message = "Your data erasure request has been submitted. You will receive a confirmation email within 30 days.",
            requestId = erasureRequestId
        });
    }
}

// Services/GdprService.cs
public interface IGdprService
{
    Task<string> GetConfirmationCodeAsync(string userId);
    Task<Guid> CreateErasureRequestAsync(string userId);
    Task ProcessErasureRequestAsync(Guid requestId);
}

public class GdprService : IGdprService
{
    private readonly ApplicationDbContext _dbContext;
    private readonly IEmailService _emailService;

    public async Task<Guid> CreateErasureRequestAsync(string userId)
    {
        var request = new DataErasureRequest
        {
            Id = Guid.NewGuid(),
            UserId = userId,
            RequestedAt = DateTime.UtcNow,
            Status = ErasureStatus.Pending,
            ScheduledFor = DateTime.UtcNow.AddDays(30)  // 30 días de gracia
        };

        _dbContext.DataErasureRequests.Add(request);
        await _dbContext.SaveChangesAsync();

        // Enviar email de confirmación
        await _emailService.SendErasureConfirmationAsync(userId, request.Id);

        return request.Id;
    }

    public async Task ProcessErasureRequestAsync(Guid requestId)
    {
        var request = await _dbContext.DataErasureRequests.FindAsync(requestId);

        if (request == null || request.Status != ErasureStatus.Pending)
        {
            return;
        }

        try
        {
            // 1. Soft delete de todos los datos del usuario
            await SoftDeleteUserDataAsync(request.UserId);

            // 2. Anonimizar datos que deben retenerse (financieros)
            await AnonymizeRetainedDataAsync(request.UserId);

            // 3. Actualizar estado
            request.Status = ErasureStatus.Completed;
            request.CompletedAt = DateTime.UtcNow;

            await _dbContext.SaveChangesAsync();

            // 4. Email de confirmación
            await _emailService.SendErasureCompletedAsync(request.UserId);
        }
        catch (Exception ex)
        {
            request.Status = ErasureStatus.Failed;
            request.ErrorMessage = ex.Message;
            await _dbContext.SaveChangesAsync();
            throw;
        }
    }

    private async Task SoftDeleteUserDataAsync(string userId)
    {
        var user = await _dbContext.Users.FindAsync(userId);
        if (user != null)
        {
            user.SoftDelete();
        }

        var customers = await _dbContext.Customers
            .Where(c => c.UserId == userId)
            .ToListAsync();

        foreach (var customer in customers)
        {
            customer.SoftDelete();
        }

        await _dbContext.SaveChangesAsync();
    }

    private async Task AnonymizeRetainedDataAsync(string userId)
    {
        // Datos financieros: mantener por regulación pero anonimizar PII
        var payments = await _dbContext.Payments
            .Where(p => p.UserId == userId)
            .ToListAsync();

        foreach (var payment in payments)
        {
            payment.UserId = "ANONYMIZED";
            payment.Email = "anonymized@deleted.com";
            payment.FullName = "Deleted User";
            // Mantener: amount, date, transaction_id (para auditoría)
        }

        await _dbContext.SaveChangesAsync();
    }
}
```

---

## 8. Hangfire - Cleanup Automatizado

### Configuración

```csharp
// Program.cs
builder.Services.AddHangfire(config =>
    config.UsePostgreSqlStorage(builder.Configuration.GetConnectionString("HangfireDb")));

builder.Services.AddHangfireServer();

var app = builder.Build();

app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new[] { new HangfireAuthorizationFilter() }
});

// Registrar jobs recurrentes
RecurringJob.AddOrUpdate<DataRetentionService>(
    "cleanup-soft-deleted",
    service => service.CleanupSoftDeletedAsync(),
    Cron.Daily(2));  // 2am diariamente

RecurringJob.AddOrUpdate<GdprService>(
    "process-erasure-requests",
    service => service.ProcessPendingErasureRequestsAsync(),
    Cron.Daily(3));  // 3am diariamente
```

### Jobs

```csharp
// Services/DataRetentionService.cs
public class DataRetentionService
{
    private readonly ApplicationDbContext _dbContext;
    private readonly ILogger<DataRetentionService> _logger;

    public async Task CleanupSoftDeletedAsync()
    {
        _logger.LogInformation("Starting soft-deleted cleanup job");

        // Hard delete de registros soft-deleted > 90 días
        var cutoffDate = DateTime.UtcNow.AddDays(-90);

        var customersToDelete = await _dbContext.Customers
            .IgnoreQueryFilters()
            .Where(c => c.DeletedAt != null && c.DeletedAt < cutoffDate)
            .ToListAsync();

        _dbContext.Customers.RemoveRange(customersToDelete);

        var deletedCount = await _dbContext.SaveChangesAsync();

        _logger.LogInformation(
            "Cleanup completed. Hard-deleted {Count} customer records",
            deletedCount);
    }

    public async Task CleanupOldLogsAsync()
    {
        // Eliminar logs > 90 días
        await _dbContext.Database.ExecuteSqlRawAsync(@"
            DELETE FROM application_logs
            WHERE created_at < NOW() - INTERVAL '90 days'
        ");
    }
}
```

---

## 9. Validación de Cumplimiento

```bash
# Verificar columna deleted_at en tablas
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  table_name,
  column_name
FROM information_schema.columns
WHERE column_name = 'deleted_at'
  AND table_schema = 'public';
EOF

# Contar registros soft-deleted pendientes de hard-delete
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  COUNT(*) as soft_deleted_count,
  MIN(deleted_at) as oldest_deletion
FROM customers
WHERE deleted_at IS NOT NULL;
EOF

# Verificar solicitudes GDPR pendientes
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  id,
  user_id,
  requested_at,
  scheduled_for,
  status
FROM data_erasure_requests
WHERE status = 'Pending'
  AND scheduled_for <= NOW();
EOF
```

---

## 10. Referencias

**GDPR:**

- [GDPR Article 17 - Right to Erasure](https://gdpr.eu/article-17-right-to-be-forgotten/)
- [GDPR Data Retention](https://gdpr.eu/data-retention/)

**SOC 2:**

- [SOC 2 Data Retention Requirements](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/sorhome)

**PostgreSQL:**

- [Partitioning for Data Retention](https://www.postgresql.org/docs/current/ddl-partitioning.html)
