---
id: data-architecture
sidebar_position: 1
title: Arquitectura de Datos
description: Estándares para arquitectura de datos en microservicios incluyendo database per service, ownership, governance, catálogo y exposición de datos.
---

# Arquitectura de Datos

## Contexto

Este estándar consolida las prácticas fundamentales para diseñar una arquitectura de datos descentralizada en microservicios, asegurando autonomía, ownership claro y governanza efectiva. Complementa el lineamiento [Datos por Dominio](../../lineamientos/datos/datos-por-dominio.md).

**Conceptos incluidos:**

- **Database per Service** → Cada servicio posee su base de datos
- **No Shared Database** → Prohibir acceso directo entre servicios
- **Data Ownership** → Definir propietarios de dominios de datos
- **Data Governance** → Políticas, calidad y cumplimiento
- **Data Catalog** → Catálogo centralizado de assets de datos
- **Data Exposure** → Estrategias para exponer datos de forma controlada

---

## Stack Tecnológico

| Componente         | Tecnología            | Versión | Uso                     |
| ------------------ | --------------------- | ------- | ----------------------- |
| **Bases de Datos** | PostgreSQL            | 15+     | Base de datos principal |
| **Bases de Datos** | Oracle                | 19c     | Sistemas legacy         |
| **Bases de Datos** | SQL Server            | 2022    | Sistemas legacy         |
| **ORM**            | Entity Framework Core | 8.0+    | Data access layer       |
| **Migraciones**    | EF Core Migrations    | 8.0+    | Schema migrations       |
| **Cache**          | Redis                 | 7.2+    | Cache distribuido       |
| **Event Store**    | PostgreSQL            | 15+     | Event sourcing          |
| **Data Catalog**   | Custom / OpenMetadata | -       | Catálogo de metadatos   |

---

## Relación entre Conceptos

```mermaid
graph TB
    A[Database per Service] --> B[Service Autonomy]
    C[No Shared Database] --> B
    D[Data Ownership] --> E[Data Governance]
    E --> F[Data Catalog]
    B --> G[Data Exposure]
    F --> G

    style A fill:#e1f5ff,color:#000000
    style C fill:#ffe1e1,color:#000000
    style D fill:#e8f5e9,color:#000000
```

---

## Database per Service

### ¿Qué es Database per Service?

Patrón arquitectónico donde cada microservicio posee y gestiona su propia base de datos, sin compartir esquemas con otros servicios.

**Principios:**

- **Autonomía**: Servicio controla su esquema y datos
- **Desacoplamiento**: Cambios de esquema no afectan otros servicios
- **Tecnología apropiada**: Cada servicio elige su DB óptima
- **Escalabilidad independiente**: Escalar DB sin afectar otros

**Propósito:** Maximizar autonomía, minimizar acoplamiento, permitir evolución independiente.

**Beneficios:**
✅ Autonomía de equipos
✅ Evolución independiente del esquema
✅ Escalabilidad por servicio
✅ Tolerancia a fallos aislada
✅ Optimización tecnológica por caso de uso

**Desafíos:**
⚠️ Transacciones distribuidas
⚠️ Consistencia eventual
⚠️ Joins entre servicios
⚠️ Reportería compleja

### Ejemplo Comparativo

```csharp
// ❌ MALO: Base de datos compartida
// CustomerService y OrderService acceden a misma DB

// CustomerService
public class CustomerRepository
{
    private readonly SharedDbContext _context; // ❌ DB compartida

    public async Task<Customer> GetByIdAsync(Guid id)
    {
        return await _context.Customers.FindAsync(id);
    }
}

// OrderService
public class OrderService
{
    private readonly SharedDbContext _context; // ❌ Acceso directo a Customers

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        // ❌ MALO: Join directo entre servicios
        var customer = await _context.Customers.FindAsync(request.CustomerId);
        var order = new Order { Customer = customer }; // ❌ Acoplamiento fuerte
        return order;
    }
}

// ✅ BUENO: Database per service — cada servicio su propio DbContext

// CustomerService
public class CustomerDbContext : DbContext
{
    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseNpgsql("Host=customer-db;Database=customers");
}

// OrderService — DbContext propio, sin acceso a CustomerDbContext
public class OrderDbContext : DbContext
{
    protected override void OnConfiguring(DbContextOptionsBuilder options)
        => options.UseNpgsql("Host=order-db;Database=orders");
}

// ✅ Para comunicación entre servicios sin acceso directo a DB, ver ## No Shared Database
```

### Implementación

```csharp
// Program.cs - Configuración por servicio

// CustomerService
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<CustomerDbContext>(options =>
{
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("CustomerDatabase"),
        npgsqlOptions =>
        {
            npgsqlOptions.EnableRetryOnFailure(
                maxRetryCount: 3,
                maxRetryDelay: TimeSpan.FromSeconds(5),
                errorCodesToAdd: null);

            npgsqlOptions.CommandTimeout(30);
        });

    options.EnableSensitiveDataLogging(builder.Environment.IsDevelopment());
    options.EnableDetailedErrors(builder.Environment.IsDevelopment());
});

// Connection string en appsettings.json
{
  "ConnectionStrings": {
    "CustomerDatabase": "Host=customer-db.internal;Port=5432;Database=customers;Username=customer_user;Password=***"
  }
}

// Entidades propias del servicio
public class Customer
{
    public Guid Id { get; set; }
    public string Name { get; set; } = default!;
    public string Email { get; set; } = default!;
    public string? Phone { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}

public class CustomerDbContext : DbContext
{
    public CustomerDbContext(DbContextOptions<CustomerDbContext> options)
        : base(options)
    {
    }

    public DbSet<Customer> Customers => Set<Customer>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.HasDefaultSchema("customer");

        modelBuilder.Entity<Customer>(entity =>
        {
            entity.ToTable("customers");
            entity.HasKey(e => e.Id);

            entity.Property(e => e.Name)
                .IsRequired()
                .HasMaxLength(100);

            entity.Property(e => e.Email)
                .IsRequired()
                .HasMaxLength(254);

            entity.HasIndex(e => e.Email)
                .IsUnique();

            entity.Property(e => e.CreatedAt)
                .HasDefaultValueSql("CURRENT_TIMESTAMP");
        });
    }
}
```

### Migraciones Independientes

```bash
# Cada servicio gestiona sus propias migraciones

# CustomerService
cd src/CustomerService
dotnet ef migrations add InitialCreate --context CustomerDbContext
dotnet ef database update --context CustomerDbContext

# OrderService (independiente)
cd src/OrderService
dotnet ef migrations add InitialCreate --context OrderDbContext
dotnet ef database update --context OrderDbContext
```

---

## No Shared Database

### ¿Qué es No Shared Database?

Principio arquitectónico que prohíbe el acceso directo a las bases de datos de otros servicios.

**Reglas:**

- **Prohibido**: Acceso directo a DB de otro servicio
- **Prohibido**: Schemas compartidos entre servicios
- **Prohibido**: Joins cross-database
- **Permitido**: Comunicación vía APIs
- **Permitido**: Eventos asincrónicos
- **Permitido**: Read replicas (solo lectura, mismo servicio)

**Propósito:** Garantizar desacoplamiento, autonomía y evolvability.

**Beneficios:**
✅ Desacoplamiento total entre servicios
✅ Cambios de esquema sin breaking changes
✅ Seguridad mejorada (acceso controlado)
✅ Escalabilidad independiente

### Antipatrones Comunes

```csharp
// ❌ ANTIPATRÓN 1: Shared Database Connection
public class OrderService
{
    // ❌ MALO: Connection string de otro servicio
    private const string CustomerDbConnection = "Host=customer-db;Database=customers;...";

    public async Task<Order> CreateOrder(Guid customerId)
    {
        using var customerConnection = new NpgsqlConnection(CustomerDbConnection);
        await customerConnection.OpenAsync();

        // ❌ Query directa a tabla de otro servicio
        var customer = await customerConnection.QueryFirstAsync<Customer>(
            "SELECT * FROM customers WHERE id = @Id",
            new { Id = customerId });

        // Crear orden...
    }
}

// ❌ ANTIPATRÓN 2: Shared Schema
public class SharedDbContext : DbContext
{
    public DbSet<Customer> Customers { get; set; } // ❌ Entidad de otro dominio
    public DbSet<Order> Orders { get; set; }
}

// ❌ ANTIPATRÓN 3: Foreign Key entre servicios
public class Order
{
    public Guid Id { get; set; }

    // ❌ MALO: FK a tabla de otro servicio
    [ForeignKey("Customer")]
    public Guid CustomerId { get; set; }
    public Customer Customer { get; set; } // ❌ Navigation property cross-service
}

// ✅ BUENO: Comunicación vía API

public interface ICustomerApiClient
{
    Task<CustomerDto?> GetByIdAsync(Guid id);
    Task<bool> ExistsAsync(Guid id);
}

public class CustomerApiClient : ICustomerApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<CustomerApiClient> _logger;

    public CustomerApiClient(HttpClient httpClient, ILogger<CustomerApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<CustomerDto?> GetByIdAsync(Guid id)
    {
        try
        {
            var response = await _httpClient.GetAsync($"/api/v1/customers/{id}");

            if (!response.IsSuccessStatusCode)
            {
                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                    return null;

                response.EnsureSuccessStatusCode();
            }

            return await response.Content.ReadFromJsonAsync<CustomerDto>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error al obtener cliente {CustomerId}", id);
            throw;
        }
    }

    public async Task<bool> ExistsAsync(Guid id)
    {
        var response = await _httpClient.SendAsync(
            new HttpRequestMessage(HttpMethod.Head, $"/api/v1/customers/{id}"));

        return response.IsSuccessStatusCode;
    }
}

// Entidad de Order solo con referencia, no navegación
public class Order
{
    public Guid Id { get; set; }

    // ✅ BUENO: Solo ID de referencia
    public Guid CustomerId { get; set; }

    // ✅ Snapshot de datos para desnormalización
    public string CustomerName { get; set; } = default!;
    public string CustomerEmail { get; set; } = default!;

    public List<OrderItem> Items { get; set; } = new();
    public decimal TotalAmount { get; set; }
    public DateTime CreatedAt { get; set; }
}

// Uso en servicio
public class OrderService
{
    private readonly OrderDbContext _context;
    private readonly ICustomerApiClient _customerClient;

    public async Task<Order> CreateOrderAsync(CreateOrderRequest request)
    {
        // ✅ Validar vía API
        var customer = await _customerClient.GetByIdAsync(request.CustomerId);

        if (customer == null)
            throw new NotFoundException("Customer", request.CustomerId);

        // ✅ Crear con snapshot de datos
        var order = new Order
        {
            Id = Guid.NewGuid(),
            CustomerId = request.CustomerId,
            CustomerName = customer.Name,
            CustomerEmail = customer.Email,
            Items = request.Items,
            CreatedAt = DateTime.UtcNow
        };

        _context.Orders.Add(order);
        await _context.SaveChangesAsync();

        return order;
    }
}
```

### Configuración de API Clients

```csharp
// Program.cs - Configurar HTTP clients

builder.Services.AddHttpClient<ICustomerApiClient, CustomerApiClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Services:CustomerApi"]!);
    client.DefaultRequestHeaders.Add("Accept", "application/json");
    client.Timeout = TimeSpan.FromSeconds(10);
})
.AddStandardResilienceHandler(); // ✅ .NET 8+: retry + circuit breaker + timeout integrados

// appsettings.json
{
  "Services": {
    "CustomerApi": "https://customer-service.internal/api"
  }
}

// Personalizar opciones de resiliencia si se necesita ajuste (opcional)
builder.Services.ConfigureHttpClientDefaults(http =>
{
    http.AddStandardResilienceHandler(options =>
    {
        options.Retry.MaxRetryAttempts = 3;
        options.CircuitBreaker.SamplingDuration = TimeSpan.FromSeconds(30);
        options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(10);
    });
});
```

---

## Data Ownership

### ¿Qué es Data Ownership?

Definición clara de qué equipo/servicio es el propietario (owner) y autoridad sobre un dominio de datos específico.

**Responsabilidades del Owner:**

- **Esquema**: Diseño y evolución del modelo de datos
- **Calidad**: Garantizar integridad y precisión
- **Acceso**: Definir APIs y contratos de exposición
- **Lifecycle**: Retención, archivado y eliminación
- **Documentación**: Mantener catálogo actualizado
- **SLAs**: Garantizar disponibilidad y performance

**Propósito:** Claridad en responsabilidades, accountability, evitar datos huérfanos.

**Beneficios:**
✅ Responsabilidad clara
✅ Calidad de datos mejorada
✅ Evolución coordinada
✅ Soporte y troubleshooting eficiente

### Matriz de Ownership

```markdown
## Data Ownership Matrix

| Dominio de Datos | Owner (Equipo) | Owner (Servicio)  | Tipo de Datos         | Exposición        |
| ---------------- | -------------- | ----------------- | --------------------- | ----------------- |
| Customers        | Team Apollo    | customer-service  | Master data           | API REST + Events |
| Orders           | Team Commerce  | order-service     | Transactional data    | API REST + Events |
| Products         | Team Catalog   | product-service   | Master data           | API REST          |
| Inventory        | Team Warehouse | inventory-service | Real-time operational | API REST + Events |
| Invoices         | Team Billing   | billing-service   | Financial records     | API REST          |
| Analytics        | Team Data      | analytics-service | Aggregated/derived    | API REST          |
| Audit Logs       | Team Platform  | audit-service     | Compliance logs       | Query API         |

## Responsabilidades por Equipo

### Team Apollo (Customers)

**Datos que posee:**

- Customer profiles
- Contact information
- KYC documents
- Customer preferences

**APIs expuestas:**

- `GET /api/v1/customers/{id}`
- `POST /api/v1/customers`
- `PUT /api/v1/customers/{id}`
- `DELETE /api/v1/customers/{id}`

**Eventos publicados:**

- `customers.customer.created.v1`
- `customers.customer.updated.v1`
- `customers.customer.deleted.v1`

**SLAs:**

- Availability: 99.9%
- Latency P95: < 200ms
- Latency P99: < 500ms

**Punto de contacto:**

- Email: team-apollo@talma.com
- Slack: #team-apollo
```

### Implementación: Ownership Metadata

```csharp
// Documentar ownership en código
[DataOwnership(
    Owner = "Team Apollo",
    Service = "customer-service",
    Domain = "Customers",
    DataClassification = "PII",
    RetentionPolicy = "7 years",
    BackupFrequency = "Daily"
)]
public class Customer
{
    public Guid Id { get; set; }

    [PII(Type = "Email")]
    public string Email { get; set; } = default!;

    [PII(Type = "Phone")]
    public string? Phone { get; set; }

    public DateTime CreatedAt { get; set; }
}

// Atributo personalizado para documentar
[AttributeUsage(AttributeTargets.Class)]
public class DataOwnershipAttribute : Attribute
{
    public string Owner { get; set; } = default!;
    public string Service { get; set; } = default!;
    public string Domain { get; set; } = default!;
    public string DataClassification { get; set; } = "Internal";
    public string RetentionPolicy { get; set; } = "Indefinite";
    public string BackupFrequency { get; set; } = "Daily";
}

[AttributeUsage(AttributeTargets.Property)]
public class PIIAttribute : Attribute
{
    public string Type { get; set; } = default!;
}
```

---

## Data Governance

### ¿Qué es Data Governance?

Conjunto de políticas, procesos y estándares para gestionar datos como activos corporativos.

**Pilares:**

- **Data Quality**: Precisión, consistencia, completitud
- **Data Security**: Clasificación, encriptación, acceso
- **Data Privacy**: GDPR, CCPA, protección PII
- **Data Lineage**: Trazabilidad origen → transformación → destino
- **Data Lifecycle**: Creación, uso, archivado, eliminación
- **Compliance**: Auditoría, regulaciones, estándares

**Propósito:** Datos confiables, seguros, conformes con regulaciones.

**Beneficios:**
✅ Cumplimiento regulatorio
✅ Calidad de datos mejorada
✅ Reducción de riesgos
✅ Confianza en decisiones basadas en datos

### Clasificación de Datos

```csharp
public enum DataClassification
{
    /// <summary>
    /// Público - Puede ser compartido abiertamente
    /// </summary>
    Public = 0,

    /// <summary>
    /// Interno - Solo para uso interno de la organización
    /// </summary>
    Internal = 1,

    /// <summary>
    /// Confidencial - Datos sensibles del negocio
    /// </summary>
    Confidential = 2,

    /// <summary>
    /// PII - Información Personal Identificable
    /// Requiere protección especial (GDPR, etc.)
    /// </summary>
    PII = 3,

    /// <summary>
    /// Restricted - Altamente confidencial (financiero, legal)
    /// </summary>
    Restricted = 4
}

// Aplicar clasificación
[DataClassification(DataClassification.PII)]
public class Customer
{
    public Guid Id { get; set; }

    [Encrypted]
    [PII]
    public string Email { get; set; } = default!;

    [Encrypted]
    [PII]
    public string? Phone { get; set; }

    [Sensitive]
    public string? TaxId { get; set; }
}

// Aplicar clasificación en entidades — los atributos documentan la política
```

### Políticas por Clasificación

| Clasificación    | Encriptación | Enmascaramiento | Auditoría | Retención  | Right to Erasure |
| ---------------- | ------------ | --------------- | --------- | ---------- | ---------------- |
| **Public**       | No           | No              | No        | Indefinida | No               |
| **Internal**     | No           | No              | No        | Indefinida | No               |
| **Confidential** | Sí           | Sí              | Sí        | —          | No               |
| **PII**          | Sí           | Sí              | Sí        | 7 años     | Sí (GDPR)        |
| **Restricted**   | Sí           | Sí              | Sí        | 10 años    | Sí               |

### Verificaciones de Calidad de Datos

```csharp
public interface IDataQualityValidator
{
    Task<ValidationResult> ValidateAsync<T>(T entity) where T : class;
}

public class CustomerDataQualityValidator : IDataQualityValidator
{
    public async Task<ValidationResult> ValidateAsync<T>(T entity) where T : class
    {
        if (entity is not Customer customer)
            return ValidationResult.Success();

        var errors = new List<string>();

        // Completitud: campos requeridos
        if (string.IsNullOrWhiteSpace(customer.Name))
            errors.Add("Name is required");

        if (string.IsNullOrWhiteSpace(customer.Email))
            errors.Add("Email is required");

        // Precisión: formato correcto
        if (!IsValidEmail(customer.Email))
            errors.Add("Email format is invalid");

        if (customer.Phone != null && !IsValidPhone(customer.Phone))
            errors.Add("Phone format is invalid");

        // Consistencia: reglas de negocio
        if (customer.CreatedAt > DateTime.UtcNow)
            errors.Add("CreatedAt cannot be in the future");

        // Unicidad: no duplicados (check en BD)
        if (await IsDuplicateEmail(customer.Email, customer.Id))
            errors.Add($"Email {customer.Email} already exists");

        return errors.Any()
            ? ValidationResult.Failure(errors.ToArray())
            : ValidationResult.Success();
    }

    private bool IsValidEmail(string email)
    {
        return Regex.IsMatch(email, @"^[^@\s]+@[^@\s]+\.[^@\s]+$");
    }

    private bool IsValidPhone(string phone)
    {
        return Regex.IsMatch(phone, @"^\+\d{10,15}$");
    }

    private async Task<bool> IsDuplicateEmail(string email, Guid currentId)
    {
        // Check en base de datos
        return false; // Simplificado
    }
}
```

---

## Data Catalog

### ¿Qué es un Data Catalog?

Inventario centralizado de todos los assets de datos en la organización con sus metadatos, ownership y lineage.

**Componentes:**

- **Metadata**: Descripción, esquema, tipo de datos
- **Ownership**: Equipo responsable, contacto
- **Lineage**: Origen, transformaciones, destinos
- **Quality Metrics**: Completitud, precisión, frescura
- **Access Control**: Quién puede acceder
- **Sample Data**: Ejemplos para desarrolladores

**Propósito:** Descubrimiento de datos, documentación viva, gobierno centralizado.

**Beneficios:**
✅ Descubrimiento fácil de datos
✅ Documentación centralizada
✅ Trazabilidad completa
✅ Reducción de datos duplicados
✅ Compliance mejorado

### Estructura del Catálogo

Cada dataset debe registrar los siguientes campos:

```yaml
datasets:
  - id: customers # Identificador único del dataset
    name: Customers
    domain: Customer Management
    owner:
      team: Team Apollo
      contact: team-apollo@talma.com
    service: customer-service
    classification: PII # Public | Internal | Confidential | PII | Restricted
    tables:
      - name: customers
        columns:
          - name: email
            type: varchar(254)
            pii: true
    apis:
      - endpoint: GET /api/v1/customers/{id}
        authentication: Bearer token
    events:
      - type: customers.customer.created.v1
        topic: customers-events
    retention_policy:
      duration: 7 years
      deletion_strategy: Soft delete
    access_control:
      - role: order-service
        permissions: [read]
```

---

## Data Exposure

### ¿Qué es Data Exposure?

Estrategias y patrones para exponer datos de un servicio a otros servicios de forma controlada y segura.

**Estrategias:**

| Estrategia           | Cuándo usar                  | Pros                   | Contras                 |
| -------------------- | ---------------------------- | ---------------------- | ----------------------- |
| **REST API**         | Queries simples, CRUD        | Simple, estándar       | Overhead HTTP           |
| **GraphQL**          | Queries flexibles, múltiples | Flexible, eficiente    | Complejidad             |
| **Events (Async)**   | Notificaciones, eventual     | Desacoplado, escalable | Consistencia eventual   |
| **Data Replication** | Analytics, reporting         | Performance queries    | Duplicación, sync       |
| **Read Replicas**    | Alto volumen lectura         | Escalabilidad lectura  | Lag replicación         |
| **API Gateway**      | Aggregation, composition     | Fachada unificada      | Single point of failure |

**Propósito:** Balance entre autonomía y necesidad de datos compartidos.

**Beneficios:**
✅ Acceso controlado
✅ Versionamiento explícito
✅ Monitoreo y throttling
✅ Seguridad centralizada

### Patrón 1: REST API Exposure

```csharp
// Exponer datos vía API REST

[ApiController]
[Route("api/v{version:apiVersion}/customers")]
[Authorize]
public class CustomersController : ControllerBase
{
    private readonly ICustomerService _customerService;

    // Query individual
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(CustomerDto), 200)]
    [ProducesResponseType(404)]
    public async Task<ActionResult<CustomerDto>> GetById(Guid id)
    {
        var customer = await _customerService.GetByIdAsync(id);
        return customer != null ? Ok(customer) : NotFound();
    }

    // Query por IDs (batch)
    [HttpGet("batch")]
    [ProducesResponseType(typeof(CustomerDto[]), 200)]
    public async Task<ActionResult<CustomerDto[]>> GetByIds(
        [FromQuery] Guid[] ids)
    {
        var customers = await _customerService.GetByIdsAsync(ids);
        return Ok(customers);
    }

    // Query con filtros
    [HttpGet("search")]
    [ProducesResponseType(typeof(PagedResult<CustomerDto>), 200)]
    public async Task<ActionResult<PagedResult<CustomerDto>>> Search(
        [FromQuery] string? email = null,
        [FromQuery] string? name = null,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20)
    {
        var result = await _customerService.SearchAsync(email, name, page, pageSize);
        return Ok(result);
    }

    // Validación de existencia (HEAD)
    [HttpHead("{id}")]
    [ProducesResponseType(200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Exists(Guid id)
    {
        var exists = await _customerService.ExistsAsync(id);
        return exists ? Ok() : NotFound();
    }
}
```

### Patrón 2: Event-Driven Exposure

```csharp
// Exponer cambios vía eventos

public class CustomerService : ICustomerService
{
    private readonly CustomerDbContext _context;
    private readonly IEventPublisher _eventPublisher;

    public async Task<Customer> CreateAsync(CreateCustomerRequest request)
    {
        var customer = new Customer
        {
            Id = Guid.NewGuid(),
            Name = request.Name,
            Email = request.Email,
            CreatedAt = DateTime.UtcNow
        };

        _context.Customers.Add(customer);
        await _context.SaveChangesAsync();

        // ✅ Publicar evento para consumidores
        await _eventPublisher.PublishAsync(new CustomerCreatedEvent
        {
            EventId = Ulid.NewUlid().ToString(),
            EventType = "customers.customer.created.v1",
            Timestamp = DateTimeOffset.UtcNow,
            CorrelationId = Activity.Current?.Id ?? Guid.NewGuid().ToString(),
            SchemaVersion = "1.0",
            Source = new EventSource
            {
                Service = "customer-service",
                Version = "1.0.0"
            },
            Subject = new EventSubject
            {
                Type = "Customer",
                Id = customer.Id.ToString()
            },
            Data = new CustomerCreatedData
            {
                CustomerId = customer.Id,
                Name = customer.Name,
                Email = customer.Email,
                CreatedAt = customer.CreatedAt
            }
        });

        return customer;
    }
}

// Otros servicios consumen eventos
public class OrderCustomerSyncHandler : IEventHandler<CustomerCreatedEvent>
{
    private readonly OrderDbContext _context;

    public async Task HandleAsync(CustomerCreatedEvent @event, CancellationToken ct)
    {
        // ✅ Mantener snapshot local de datos necesarios
        var customerSnapshot = new CustomerSnapshot
        {
            CustomerId = @event.Data.CustomerId,
            Name = @event.Data.Name,
            Email = @event.Data.Email,
            LastUpdated = @event.Timestamp.UtcDateTime
        };

        _context.CustomerSnapshots.Add(customerSnapshot);
        await _context.SaveChangesAsync(ct);
    }
}
```

:::warning Riesgo: pérdida silenciosa de eventos
El patrón anterior (guardar en DB → publicar evento) tiene un riesgo: si `PublishAsync` falla después de `SaveChangesAsync`, el dato se persiste pero el evento nunca se envía. Para garantizar **at-least-once delivery**, usar el **Transactional Outbox Pattern**: guardar el evento en la misma transacción junto con la entidad, y publicarlo desde un proceso en background. Ver [Mensajería Asíncrona](../../mensajeria/async-messaging.md) para la implementación.
:::

### Patrón 3: Data Replication (Analytics)

```csharp
// Replicación para analytics/reporting

// Servicio Analytics tiene réplica read-only
public class AnalyticsDbContext : DbContext
{
    // ✅ Connection string a read replica
    protected override void OnConfiguring(DbContextOptionsBuilder options)
    {
        options.UseNpgsql("Host=analytics-replica.internal;Database=analytics_replica;...");
    }

    // Vistas materializadas sincronizadas
    public DbSet<CustomerAnalyticsView> CustomerAnalytics { get; set; }
    public DbSet<OrderAnalyticsView> OrderAnalytics { get; set; }
}

public class CustomerAnalyticsView
{
    public Guid CustomerId { get; set; }
    public string Name { get; set; } = default!;
    public string Email { get; set; } = default!;
    public int TotalOrders { get; set; }
    public decimal TotalSpent { get; set; }
    public DateTime LastOrderDate { get; set; }
    public DateTime SyncedAt { get; set; }
}

// Proceso de sincronización
public class AnalyticsReplicationService
{
    public async Task SyncCustomerAnalyticsAsync()
    {
        // ✅ Usar paginación: nunca cargar toda la colección en memoria
        var page = 1;
        const int pageSize = 500;
        IReadOnlyList<CustomerDto> customers;

        do
        {
            customers = await _customerApiClient.GetPagedAsync(page++, pageSize);

            if (customers.Count == 0) break;

            // Obtener órdenes solo para los customers de esta página
            var customerIds = customers.Select(c => c.Id).ToArray();
            var orders = await _orderApiClient.GetByCustomerIdsAsync(customerIds);

            var analytics = customers.Select(c => new CustomerAnalyticsView
            {
                CustomerId = c.Id,
                Name = c.Name,
                Email = c.Email,
                TotalOrders = orders.Count(o => o.CustomerId == c.Id),
                TotalSpent = orders.Where(o => o.CustomerId == c.Id).Sum(o => o.TotalAmount),
                LastOrderDate = orders.Where(o => o.CustomerId == c.Id).MaxBy(o => o.CreatedAt)?.CreatedAt ?? default,
                SyncedAt = DateTime.UtcNow
            });

            await _analyticsContext.CustomerAnalytics.UpsertRange(analytics).RunAsync();
        }
        while (customers.Count == pageSize);
    }
}
```

---

## Implementación Integrada

### Ejemplo: Sistema Multi-DB con Ownership Claro

```csharp
// docker-compose.yml - Bases de datos separadas

version: '3.8'

services:
  customer-db:
    image: postgres:15
    environment:
      POSTGRES_DB: customers
      POSTGRES_USER: customer_user
      POSTGRES_PASSWORD: customer_pass
    volumes:
      - customer-data:/var/lib/postgresql/data
    networks:
      - backend

  order-db:
    image: postgres:15
    environment:
      POSTGRES_DB: orders
      POSTGRES_USER: order_user
      POSTGRES_PASSWORD: order_pass
    volumes:
      - order-data:/var/lib/postgresql/data
    networks:
      - backend

  product-db:
    image: postgres:15
    environment:
      POSTGRES_DB: products
      POSTGRES_USER: product_user
      POSTGRES_PASSWORD: product_pass
    volumes:
      - product-data:/var/lib/postgresql/data
    networks:
      - backend

volumes:
  customer-data:
  order-data:
  product-data:

networks:
  backend:
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

**Database per Service:**

- **MUST** cada microservicio tener su propia base de datos
- **MUST** usar esquemas separados incluso si comparten servidor físico
- **MUST** gestionar migraciones independientemente por servicio

**No Shared Database:**

- **MUST NOT** acceder directamente a base de datos de otro servicio
- **MUST NOT** compartir esquemas entre servicios
- **MUST NOT** usar foreign keys entre bases de datos de servicios diferentes
- **MUST** comunicarse vía APIs o eventos para obtener datos de otros servicios

**Data Ownership:**

- **MUST** definir ownership claro para cada dominio de datos
- **MUST** documentar owner en catálogo de datos
- **MUST** owner aprobar cambios en esquema/APIs

**Data Governance:**

- **MUST** clasificar todos los datos (Public, Internal, Confidential, PII, Restricted)
- **MUST** encriptar datos PII en reposo
- **MUST** enmascarar datos PII en logs
- **MUST** implementar políticas de retención según clasificación

**Data Catalog:**

- **MUST** registrar todos los datasets en catálogo centralizado
- **MUST** mantener catálogo actualizado con cambios de esquema
- **MUST** documentar APIs y eventos para exposición de datos

**Data Exposure:**

- **MUST** exponer datos vía APIs versionadas
- **MUST** implementar autenticación/autorización en APIs
- **MUST** publicar eventos para cambios en datos maestros

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar diferentes tecnologías de DB según caso de uso (PostgreSQL, Redis, etc.)
- **SHOULD** implementar read replicas para alta carga de lectura
- **SHOULD** usar connection pooling
- **SHOULD** implementar health checks para bases de datos
- **SHOULD** monitorear métricas de DB (latency, connections, errors)
- **SHOULD** implementar data quality checks
- **SHOULD** documentar data lineage
- **SHOULD** automatizar backups con retención apropiada

### MAY (Opcional)

- **MAY** usar Event Sourcing para dominios complejos
- **MAY** implementar CQRS para separar lecturas/escrituras
- **MAY** usar GraphQL para queries flexibles
- **MAY** implementar API Gateway para composición
- **MAY** usar Schema Registry para versionamiento de eventos

### MUST NOT (Prohibido)

- **MUST NOT** compartir connection strings, hacer joins cross-database ni usar transacciones distribuidas (2PC) entre servicios sin justificación clara
- **MUST NOT** exponer datos sin control de acceso
- **MUST NOT** almacenar PII sin encriptación

---

## Referencias

**Patrones:**

- [Database per Service Pattern](https://microservices.io/patterns/data/database-per-service.html)
- [Shared Database Anti-Pattern](https://microservices.io/patterns/data/shared-database.html)
- [Event-driven Architecture](https://martinfowler.com/articles/201701-event-driven.html)

**Documentación:**

- [Entity Framework Core](https://learn.microsoft.com/ef/core/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Data Governance Framework](https://www.dama.org/cpages/body-of-knowledge)

**Relacionados:**

- [Consistencia de Datos](./data-consistency.md)
- [Estándares de Base de Datos](./database-standards.md)
- [Comunicación Asíncrona y Eventos](../../lineamientos/arquitectura/comunicacion-asincrona-y-eventos.md)
- [Contratos de Eventos](../../mensajeria/event-contracts.md)

---

**Última actualización**: 18 de febrero de 2026
**Responsable**: Equipo de Arquitectura
