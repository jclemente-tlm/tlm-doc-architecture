---
id: tenant-isolation
sidebar_position: 20
title: Aislamiento de Tenants (Multi-Tenancy)
description: Estándar para aislar datos entre tenants en arquitectura multi-tenant con PostgreSQL RLS, tenant_id discriminator y validación en aplicación
---

# Estándar Técnico — Aislamiento de Tenants

---

## 1. Propósito

Aislar datos entre tenants (países: PE, CO, MX, CL) en arquitectura multi-tenant usando PostgreSQL Row-Level Security (RLS), columna discriminator `tenant_id`, validación en capa de aplicación y JWT claims, evitando data leakage entre organizaciones.

---

## 2. Alcance

**Aplica a:**

- Todas las tablas con datos de negocio
- APIs que sirven múltiples tenants
- Queries en aplicación (.NET)
- Logs y auditoría
- Backups y exports

**No aplica a:**

- Tablas de configuración global (sin tenant_id)
- Metadatos de sistema

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología            | Versión mínima | Observaciones            |
| -------------- | --------------------- | -------------- | ------------------------ |
| **Database**   | PostgreSQL            | 14+            | Row-Level Security (RLS) |
| **ORM**        | Entity Framework Core | 8.0+           | Query filters            |
| **Auth**       | Keycloak              | 23.0+          | Tenant claim en JWT      |
| **Middleware** | ASP.NET Core          | 8.0+           | Tenant context           |
| **Validation** | Custom interceptors   | -              | Double-check isolation   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Modelo de Tenancy

- [ ] **1 BD compartida**: Todos los tenants en misma BD PostgreSQL
- [ ] **tenant_id obligatorio**: Columna `tenant_id` en TODAS las tablas de negocio
- [ ] **RLS habilitado**: Row-Level Security en PostgreSQL
- [ ] **Global query filter**: EF Core query filter automático
- [ ] **Tenant en JWT**: Claim `tenant_id` en token

### Validación

- [ ] **Application-level**: Middleware establece tenant context
- [ ] **Database-level**: RLS policies como última línea de defensa
- [ ] **Audit logging**: Registrar tenant_id en todos los logs
- [ ] **Cross-tenant checks**: Tests automatizados de aislamiento

### Seguridad

- [ ] **NO confiar solo en app**: RLS es obligatorio (defense in depth)
- [ ] **NO parámetros de usuario**: tenant_id viene de JWT autenticado
- [ ] **Backups separados**: Exports por tenant

---

## 5. PostgreSQL - Schema Design

### Columna tenant_id

```sql
-- Tabla con multi-tenancy
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(2) NOT NULL,  -- 'PE', 'CO', 'MX', 'CL'

    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

CREATE INDEX idx_customers_tenant ON customers(tenant_id);

-- Tabla de tenants
CREATE TABLE tenants (
    id VARCHAR(2) PRIMARY KEY,  -- 'PE', 'CO', 'MX', 'CL'
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO tenants (id, name, country) VALUES
  ('PE', 'Talma Perú', 'Perú'),
  ('CO', 'Talma Colombia', 'Colombia'),
  ('MX', 'Talma México', 'México'),
  ('CL', 'Talma Chile', 'Chile');
```

### Row-Level Security (RLS)

```sql
-- Habilitar RLS
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Policy: Solo ver datos del tenant actual
CREATE POLICY tenant_isolation_policy ON customers
  USING (tenant_id = current_setting('app.current_tenant_id', true));

-- Policy: Solo insertar con tenant actual
CREATE POLICY tenant_insert_policy ON customers
  FOR INSERT
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- Policy: Solo actualizar datos del tenant
CREATE POLICY tenant_update_policy ON customers
  FOR UPDATE
  USING (tenant_id = current_setting('app.current_tenant_id', true))
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- Policy: Solo eliminar datos del tenant
CREATE POLICY tenant_delete_policy ON customers
  FOR DELETE
  USING (tenant_id = current_setting('app.current_tenant_id', true));
```

### Configurar Tenant Context en Session

```sql
-- Antes de ejecutar queries, establecer tenant
SET app.current_tenant_id = 'PE';

-- Ahora solo verá datos de Perú
SELECT * FROM customers;  -- Solo customers con tenant_id = 'PE'
```

---

## 6. .NET - Tenant Context

### Middleware para Tenant Context

```csharp
// Middleware/TenantMiddleware.cs
public class TenantMiddleware
{
    private readonly RequestDelegate _next;

    public TenantMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context, ITenantService tenantService)
    {
        // Extraer tenant_id del JWT claim
        var tenantId = context.User.FindFirst("tenant_id")?.Value;

        if (string.IsNullOrEmpty(tenantId))
        {
            context.Response.StatusCode = StatusCodes.Status401Unauthorized;
            await context.Response.WriteAsJsonAsync(new { error = "Missing tenant_id claim" });
            return;
        }

        // Validar tenant existe y está activo
        if (!await tenantService.IsValidTenantAsync(tenantId))
        {
            context.Response.StatusCode = StatusCodes.Status403Forbidden;
            await context.Response.WriteAsJsonAsync(new { error = "Invalid or inactive tenant" });
            return;
        }

        // Establecer tenant en contexto
        tenantService.SetCurrentTenant(tenantId);

        await _next(context);
    }
}

// Services/TenantService.cs
public interface ITenantService
{
    string? GetCurrentTenant();
    void SetCurrentTenant(string tenantId);
    Task<bool> IsValidTenantAsync(string tenantId);
}

public class TenantService : ITenantService
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private readonly ApplicationDbContext _dbContext;
    private string? _currentTenant;

    public TenantService(IHttpContextAccessor httpContextAccessor, ApplicationDbContext dbContext)
    {
        _httpContextAccessor = httpContextAccessor;
        _dbContext = dbContext;
    }

    public string? GetCurrentTenant()
    {
        return _currentTenant ?? _httpContextAccessor.HttpContext?.User.FindFirst("tenant_id")?.Value;
    }

    public void SetCurrentTenant(string tenantId)
    {
        _currentTenant = tenantId;
    }

    public async Task<bool> IsValidTenantAsync(string tenantId)
    {
        return await _dbContext.Tenants
            .AnyAsync(t => t.Id == tenantId && t.Active);
    }
}

// Program.cs
builder.Services.AddScoped<ITenantService, TenantService>();
builder.Services.AddHttpContextAccessor();

var app = builder.Build();

app.UseAuthentication();
app.UseMiddleware<TenantMiddleware>();  // DESPUÉS de Authentication
app.UseAuthorization();
```

### Entity Framework - Global Query Filter

```csharp
// Data/ApplicationDbContext.cs
public class ApplicationDbContext : DbContext
{
    private readonly ITenantService _tenantService;

    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options, ITenantService tenantService)
        : base(options)
    {
        _tenantService = tenantService;
    }

    public DbSet<Customer> Customers => Set<Customer>();
    public DbSet<Payment> Payments => Set<Payment>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Global query filter para tenant isolation
        modelBuilder.Entity<Customer>().HasQueryFilter(e => e.TenantId == _tenantService.GetCurrentTenant());
        modelBuilder.Entity<Payment>().HasQueryFilter(e => e.TenantId == _tenantService.GetCurrentTenant());

        // Repetir para TODAS las entidades multi-tenant
    }

    public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        var currentTenant = _tenantService.GetCurrentTenant();

        if (string.IsNullOrEmpty(currentTenant))
        {
            throw new InvalidOperationException("Tenant context not set");
        }

        // Auto-asignar tenant_id a entidades nuevas
        var entries = ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Added && e.Entity is ITenantEntity);

        foreach (var entry in entries)
        {
            ((ITenantEntity)entry.Entity).TenantId = currentTenant;
        }

        // Validar que NO se modifique tenant_id
        var modifiedEntries = ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Modified && e.Entity is ITenantEntity);

        foreach (var entry in modifiedEntries)
        {
            var tenantIdProperty = entry.Property(nameof(ITenantEntity.TenantId));
            if (tenantIdProperty.IsModified)
            {
                throw new InvalidOperationException("Cannot change tenant_id");
            }
        }

        // Configurar RLS en PostgreSQL
        await Database.ExecuteSqlRawAsync(
            $"SET app.current_tenant_id = '{currentTenant}'",
            cancellationToken);

        return await base.SaveChangesAsync(cancellationToken);
    }
}

// Entities/ITenantEntity.cs
public interface ITenantEntity
{
    string TenantId { get; set; }
}

// Entities/Customer.cs
public class Customer : ITenantEntity
{
    public Guid Id { get; set; }
    public string TenantId { get; set; } = null!;
    public string Email { get; set; } = null!;
    public string FullName { get; set; } = null!;
    public DateTime CreatedAt { get; set; }
}
```

---

## 7. JWT - Tenant Claim

### Keycloak - Mapper

Configurar en Keycloak Admin UI:

1. **Clients** → `payment-api` → **Mappers** → **Create**
2. **Name**: `tenant-id-mapper`
3. **Mapper Type**: `User Attribute`
4. **User Attribute**: `tenant_id`
5. **Token Claim Name**: `tenant_id`
6. **Claim JSON Type**: `String`
7. **Add to ID token**: ✅
8. **Add to access token**: ✅

### JWT Token Ejemplo

```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@talma.com",
  "tenant_id": "PE",
  "roles": ["admin"],
  "iat": 1704067200,
  "exp": 1704070800
}
```

---

## 8. Testing - Aislamiento

### Tests Automatizados

```csharp
// Tests/TenantIsolationTests.cs
public class TenantIsolationTests : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task GetCustomers_WithTenantPE_OnlyReturnsPECustomers()
    {
        // Arrange
        var client = _factory.CreateClient();
        var token = GenerateJwtWithTenant("PE");
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await client.GetAsync("/api/customers");
        var customers = await response.Content.ReadFromJsonAsync<List<Customer>>();

        // Assert
        Assert.All(customers, c => Assert.Equal("PE", c.TenantId));
    }

    [Fact]
    public async Task CreateCustomer_WithTenantCO_CannotAccessFromPE()
    {
        // 1. Crear customer con tenant CO
        var tokenCO = GenerateJwtWithTenant("CO");
        var clientCO = _factory.CreateClient();
        clientCO.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", tokenCO);

        var createResponse = await clientCO.PostAsJsonAsync("/api/customers", new { email = "test@co.com" });
        var customer = await createResponse.Content.ReadFromJsonAsync<Customer>();

        // 2. Intentar acceder con tenant PE (debe fallar)
        var tokenPE = GenerateJwtWithTenant("PE");
        var clientPE = _factory.CreateClient();
        clientPE.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", tokenPE);

        var getResponse = await clientPE.GetAsync($"/api/customers/{customer.Id}");

        // Assert
        Assert.Equal(HttpStatusCode.NotFound, getResponse.StatusCode);  // No puede ver customer de CO
    }
}
```

---

## 9. Validación de Cumplimiento

```bash
# Verificar todas las tablas tienen tenant_id
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  tablename,
  CASE WHEN EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = tablename AND column_name = 'tenant_id'
  ) THEN 'YES' ELSE 'NO' END as has_tenant_id
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename NOT IN ('tenants', 'schema_migrations');
EOF

# Verificar RLS habilitado
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  tablename,
  CASE WHEN rowsecurity THEN 'YES' ELSE 'NO' END as rls_enabled
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE schemaname = 'public';
EOF

# Verificar políticas RLS existen
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  schemaname,
  tablename,
  policyname
FROM pg_policies
WHERE schemaname = 'public';
EOF
```

---

## 10. Referencias

**AWS:**

- [SaaS Tenant Isolation Strategies](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/tenant-isolation.html)

**PostgreSQL:**

- [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

**Patterns:**

- [Multi-Tenant Data Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/overview)
