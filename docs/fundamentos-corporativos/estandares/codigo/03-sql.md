---
id: sql
sidebar_position: 3
title: Desarrollo con SQL
description: Estándares para desarrollo SQL, Entity Framework, PostgreSQL 14+ y Oracle 19c
---

## 1. Propósito

Este estándar establece las reglas para escribir código SQL seguro, eficiente y mantenible en aplicaciones de Talma. Define cómo usar SQL con Entity Framework Core, consultas parametrizadas y buenas prácticas específicas para PostgreSQL y Oracle. Garantiza que:
- Las consultas SQL estén protegidas contra SQL Injection mediante parametrización
- La lógica de negocio reside en la aplicación, no en la base de datos
- El código SQL sea legible, indexado correctamente y optimizado con EXPLAIN ANALYZE

**Versión**: 1.0  
**Última actualización**: 2025-08-08

## 2. Alcance

### Aplica a:
- Desarrollo de consultas SQL con Entity Framework Core 8.0+
- Consultas raw SQL con Npgsql 8.0+ (PostgreSQL) y Oracle.EntityFrameworkCore 8.0+
- Repositories con acceso a datos (patron Repository)
- Scripts de migración con Entity Framework Migrations o Flyway 10.0+
- Procedimientos almacenados excepcionales (requieren aprobación de arquitectura)

### No aplica a:
- Queries de herramientas de BI/reportería (DataGrip, Tableau)
- Scripts de administración DBA (backups, mantenimiento, monitoreo)
- Consultas ad-hoc de análisis de datos
- Sistemas legacy con stored procedures (requieren plan de migración)

## 3. Tecnologías Obligatorias

| Tecnología | Versión Mínima | Propósito |
|------------|----------------|-----------|
| **PostgreSQL** | 14.0+ | Motor de base de datos principal para aplicaciones transaccionales |
| **Oracle Database** | 19c+ | Motor de base de datos legacy para sistemas existentes |
| **Entity Framework Core** | 8.0+ | ORM principal para acceso a datos .NET |
| **Npgsql** | 8.0+ | Provider de PostgreSQL para .NET (con JSON/JSONB support) |
| **Oracle.EntityFrameworkCore** | 8.0+ | Provider de Oracle para .NET |
| **Flyway** | 10.0+ | Versionado de esquemas de base de datos (migrations) |
| **pgAdmin** | 7.0+ | Herramienta de administración PostgreSQL |

## 4. Especificaciones Técnicas

### 4.1 Nomenclatura de Convenciones

Seguir estrictamente la [Convención de Nombres de Base de Datos](../../convenciones/codigo/04-objetos-base-datos.md).

**PostgreSQL** (snake_case):
```sql
-- Tabla
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Índice
CREATE INDEX idx_user_profiles_email ON user_profiles(email);

-- Foreign Key
ALTER TABLE orders ADD CONSTRAINT fk_orders_user_id 
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id);
```

**Oracle** (UPPER_SNAKE_CASE):
```sql
-- Tabla
CREATE TABLE USER_PROFILES (
    USER_ID RAW(16) PRIMARY KEY,
    FULL_NAME VARCHAR2(200) NOT NULL,
    EMAIL VARCHAR2(100) UNIQUE NOT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IS_ACTIVE NUMBER(1) DEFAULT 1
);

-- Índice
CREATE INDEX IDX_USER_PROFILES_EMAIL ON USER_PROFILES(EMAIL);

-- Secuencia
CREATE SEQUENCE USER_PROFILES_SEQ START WITH 1 INCREMENT BY 1;
```

### 4.2 Queries con Entity Framework Core

**Uso de LINQ (preferido):**

```csharp
// Proyección con Select (evita SELECT *)
var users = await _dbContext.Users
    .Where(u => u.IsActive)
    .Select(u => new UserDto 
    { 
        UserId = u.UserId,
        FullName = u.FullName,
        Email = u.Email 
    })
    .ToListAsync(cancellationToken);

// Include para eager loading (evita N+1)
var orders = await _dbContext.Orders
    .Include(o => o.User)
    .Include(o => o.OrderItems)
    .Where(o => o.CreatedAt >= DateTime.UtcNow.AddDays(-30))
    .ToListAsync(cancellationToken);
```

**Uso de SQL raw (cuando sea necesario):**

```csharp
// PostgreSQL con FromSqlInterpolated (parametrización automática)
var activeUsers = await _dbContext.Users
    .FromSqlInterpolated($@"
        SELECT user_id, full_name, email, created_at, is_active
        FROM user_profiles
        WHERE is_active = {true} AND created_at > {startDate}")
    .ToListAsync(cancellationToken);

// Oracle con FromSqlRaw (parametrización explícita)
var status = "PENDING";
var orders = await _dbContext.Orders
    .FromSqlRaw(@"
        SELECT ORDER_ID, USER_ID, STATUS, CREATED_AT
        FROM ORDERS
        WHERE STATUS = :status", 
        new OracleParameter("status", status))
    .ToListAsync(cancellationToken);
```

### 4.3 Transacciones

### 4.3 Transacciones

**Transacciones explícitas con Entity Framework:**

```csharp
public class OrderService
{
    private readonly ApplicationDbContext _dbContext;
    private readonly ILogger<OrderService> _logger;

    public async Task<Result<OrderId>> CreateOrderAsync(
        CreateOrderCommand command, 
        CancellationToken cancellationToken)
    {
        // Estrategia de ejecución para retry de conexión
        var strategy = _dbContext.Database.CreateExecutionStrategy();

        return await strategy.ExecuteAsync(async () =>
        {
            await using var transaction = await _dbContext.Database
                .BeginTransactionAsync(IsolationLevel.ReadCommitted, cancellationToken);
            
            try
            {
                var order = Order.Create(command.UserId, command.Items);
                _dbContext.Orders.Add(order);
                await _dbContext.SaveChangesAsync(cancellationToken);

                // Actualizar inventario
                foreach (var item in command.Items)
                {
                    var product = await _dbContext.Products
                        .FindAsync(new object[] { item.ProductId }, cancellationToken);
                    
                    product!.ReduceStock(item.Quantity);
                }

                await _dbContext.SaveChangesAsync(cancellationToken);
                await transaction.CommitAsync(cancellationToken);

                _logger.LogInformation(
                    "Order {OrderId} created successfully", order.Id);
                
                return Result<OrderId>.Success(order.Id);
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync(cancellationToken);
                _logger.LogError(ex, "Error creating order");
                return Result<OrderId>.Failure("Order creation failed");
            }
        });
    }
}
```

### 4.4 Indexación y Optimización

**Creación de índices en PostgreSQL:**

```sql
-- Índice simple para búsquedas frecuentes
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Índice compuesto para queries con múltiples filtros
CREATE INDEX idx_orders_status_created_at ON orders(status, created_at DESC);

-- Índice parcial para queries con filtros fijos
CREATE INDEX idx_orders_pending ON orders(created_at) 
    WHERE status = 'pending';

-- Índice GIN para JSONB
CREATE INDEX idx_orders_metadata ON orders USING GIN(metadata jsonb_path_ops);

-- Índice de texto completo
CREATE INDEX idx_products_search ON products 
    USING GIN(to_tsvector('spanish', name || ' ' || description));
```

**Análisis de queries con EXPLAIN:**

```csharp
// En entorno de desarrollo, analizar queries complejas
#if DEBUG
var queryPlan = _dbContext.Orders
    .Where(o => o.Status == "pending" && o.CreatedAt > DateTime.UtcNow.AddDays(-7))
    .Include(o => o.User)
    .Include(o => o.OrderItems)
    .ToQueryString();

Console.WriteLine(queryPlan);
// Ejecutar en pgAdmin: EXPLAIN ANALYZE <query>
#endif
```

**Ejemplo de EXPLAIN ANALYZE en PostgreSQL:**

```sql
EXPLAIN ANALYZE
SELECT o.order_id, o.status, u.full_name, COUNT(oi.order_item_id)
FROM orders o
INNER JOIN user_profiles u ON o.user_id = u.user_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'pending' AND o.created_at > NOW() - INTERVAL '7 days'
GROUP BY o.order_id, o.status, u.full_name;

-- Resultado esperado:
-- Hash Join (cost=X..Y rows=Z) (actual time=A..B rows=C loops=D)
-- -> Verificar que use índices y no Seq Scan en tablas grandes
```

### 4.5 Lógica de Negocio en la Aplicación

:::danger
**PROHIBIDO**: Implementar lógica de negocio en la base de datos mediante triggers, stored procedures o funciones complejas, salvo aprobación explícita de arquitectura.
:::

**Patrón Repository (correcto):**

```csharp
// Dominio
public class Order
{
    public OrderId Id { get; private set; }
    public UserId UserId { get; private set; }
    public OrderStatus Status { get; private set; }
    public List<OrderItem> Items { get; private set; } = new();

    public void MarkAsPaid()
    {
        if (Status == OrderStatus.Paid)
            throw new DomainException("Order is already paid");
        
        Status = OrderStatus.Paid;
    }

    public void AddItem(ProductId productId, int quantity, decimal price)
    {
        if (quantity <= 0)
            throw new DomainException("Quantity must be positive");
        
        Items.Add(new OrderItem(productId, quantity, price));
    }
}

// Repository
public class OrderRepository : IOrderRepository
{
    private readonly ApplicationDbContext _dbContext;

    public async Task<Order?> GetByIdAsync(
        OrderId orderId, 
        CancellationToken cancellationToken)
    {
        return await _dbContext.Orders
            .Include(o => o.Items)
            .FirstOrDefaultAsync(o => o.Id == orderId, cancellationToken);
    }

    public async Task AddAsync(Order order, CancellationToken cancellationToken)
    {
        _dbContext.Orders.Add(order);
        await _dbContext.SaveChangesAsync(cancellationToken);
    }
}

// Service
public class OrderService
{
    private readonly IOrderRepository _orderRepository;

    public async Task<bool> MarkOrderAsPaidAsync(
        OrderId orderId, 
        CancellationToken cancellationToken)
    {
        var order = await _orderRepository.GetByIdAsync(orderId, cancellationToken);
        if (order == null) 
            return false;

        order.MarkAsPaid(); // Lógica de dominio en la aplicación
        await _orderRepository.UpdateAsync(order, cancellationToken);
        
        return true;
    }
}
```

### 4.6 Seguridad

**Prevención de SQL Injection:**

```csharp
// ✅ CORRECTO: Parametrización con FromSqlInterpolated
var email = userInput; // Entrada del usuario
var user = await _dbContext.Users
    .FromSqlInterpolated($"SELECT * FROM user_profiles WHERE email = {email}")
    .FirstOrDefaultAsync(cancellationToken);

// ✅ CORRECTO: Parametrización explícita
var status = userInput;
var orders = await _dbContext.Orders
    .FromSqlRaw("SELECT * FROM orders WHERE status = @p0", status)
    .ToListAsync(cancellationToken);

// ❌ INCORRECTO: Concatenación de strings (SQL Injection)
var query = $"SELECT * FROM users WHERE email = '{userInput}'";
var users = await _dbContext.Users.FromSqlRaw(query).ToListAsync(); // PELIGRO
```

**Least Privilege Principle:**

```sql
-- PostgreSQL: Usuario de aplicación con permisos mínimos
CREATE USER talma_app_user WITH PASSWORD 'secure_password';

-- Solo SELECT, INSERT, UPDATE, DELETE en tablas específicas
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO talma_app_user;

-- NO otorgar permisos de DDL (CREATE, DROP, ALTER)
REVOKE CREATE ON SCHEMA public FROM talma_app_user;

-- Usuario de solo lectura para reportes
CREATE USER talma_readonly WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO talma_readonly;
```

### 4.7 Migraciones de Base de Datos

**Con Entity Framework Migrations:**

```bash
# Crear migración
dotnet ef migrations add AddUserProfiles --project src/Infrastructure

# Aplicar migración
dotnet ef database update --project src/Infrastructure

# Generar script SQL para producción
dotnet ef migrations script --idempotent --output migrations.sql
```

**Ejemplo de migración:**

```csharp
public partial class AddUserProfiles : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.CreateTable(
            name: "user_profiles",
            columns: table => new
            {
                user_id = table.Column<Guid>(nullable: false),
                full_name = table.Column<string>(maxLength: 200, nullable: false),
                email = table.Column<string>(maxLength: 100, nullable: false),
                created_at = table.Column<DateTime>(nullable: false, 
                    defaultValueSql: "CURRENT_TIMESTAMP"),
                is_active = table.Column<bool>(nullable: false, defaultValue: true)
            },
            constraints: table =>
            {
                table.PrimaryKey("pk_user_profiles", x => x.user_id);
            });

        migrationBuilder.CreateIndex(
            name: "idx_user_profiles_email",
            table: "user_profiles",
            column: "email",
            unique: true);
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable(name: "user_profiles");
    }
}
```

**Con Flyway (alternativa):**

```sql
-- V001__create_user_profiles.sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_user_profiles_email ON user_profiles(email);
```

## 5. Buenas Prácticas

### 5.1 Consultas Eficientes

1. **Proyección selectiva**: Usar `Select()` en vez de retornar entidades completas
2. **Eager loading**: Usar `Include()` para evitar N+1 queries
3. **Paginación**: Usar `Skip()` y `Take()` con límite máximo de 1000 registros
4. **Caché**: Cachear queries repetitivas con `IMemoryCache` o Redis
5. **Async**: Siempre usar `ToListAsync()`, `FirstOrDefaultAsync()`, etc.

```csharp
// ✅ CORRECTO: Proyección + paginación + async
var users = await _dbContext.Users
    .Where(u => u.IsActive)
    .OrderBy(u => u.CreatedAt)
    .Skip(pageNumber * pageSize)
    .Take(Math.Min(pageSize, 1000))
    .Select(u => new { u.UserId, u.FullName, u.Email })
    .ToListAsync(cancellationToken);

// ❌ INCORRECTO: SELECT * + sin paginación + síncrono
var users = _dbContext.Users.ToList(); // Carga toda la tabla en memoria
```

### 5.2 Formato y Legibilidad

```sql
-- ✅ CORRECTO: Palabras reservadas en MAYÚSCULAS, indentación, alias
SELECT 
    o.order_id,
    o.status,
    u.full_name AS user_name,
    COUNT(oi.order_item_id) AS total_items,
    SUM(oi.quantity * oi.price) AS total_amount
FROM orders o
INNER JOIN user_profiles u ON o.user_id = u.user_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'pending'
  AND o.created_at > NOW() - INTERVAL '30 days'
GROUP BY o.order_id, o.status, u.full_name
HAVING SUM(oi.quantity * oi.price) > 100
ORDER BY o.created_at DESC;

-- ❌ INCORRECTO: Sin formato, SELECT *
select * from orders o inner join user_profiles u on o.user_id=u.user_id where o.status='pending' order by o.created_at desc;
```

### 5.3 PostgreSQL Específico

```csharp
// ✅ Usar RETURNING para obtener IDs generados
var user = new User { FullName = "Ana Garcia", Email = "ana@mail.com" };
await _dbContext.Database.ExecuteSqlInterpolatedAsync($@"
    INSERT INTO user_profiles (user_id, full_name, email)
    VALUES ({user.UserId}, {user.FullName}, {user.Email})
    RETURNING user_id");

// ✅ Aprovechar JSONB para datos semi-estructurados
await _dbContext.Products
    .Where(p => EF.Functions.JsonContains(p.Metadata, "{\"featured\": true}"))
    .ToListAsync(cancellationToken);

// ✅ Usar COALESCE para valores nulos
var products = await _dbContext.Products
    .Select(p => new 
    { 
        p.ProductId, 
        p.Name, 
        Stock = p.Stock ?? 0 // Mapea a COALESCE(stock, 0)
    })
    .ToListAsync(cancellationToken);
```

### 5.4 Oracle Específico

```csharp
// ✅ Usar secuencias para claves primarias
await _dbContext.Database.ExecuteSqlRawAsync(@"
    INSERT INTO USER_PROFILES (USER_ID, FULL_NAME, EMAIL)
    VALUES (USER_PROFILES_SEQ.NEXTVAL, :fullName, :email)",
    new OracleParameter("fullName", "Ana Garcia"),
    new OracleParameter("email", "ana@mail.com"));

// ✅ Usar NVL para valores nulos
await _dbContext.Products.FromSqlRaw(@"
    SELECT PRODUCT_ID, NAME, NVL(STOCK, 0) AS STOCK
    FROM PRODUCTS
    WHERE IS_ACTIVE = 1").ToListAsync(cancellationToken);

// ✅ Usar MERGE para upsert
await _dbContext.Database.ExecuteSqlRawAsync(@"
    MERGE INTO USER_PROFILES target
    USING (SELECT :userId AS USER_ID, :fullName AS FULL_NAME FROM DUAL) source
    ON (target.USER_ID = source.USER_ID)
    WHEN MATCHED THEN
        UPDATE SET FULL_NAME = source.FULL_NAME
    WHEN NOT MATCHED THEN
        INSERT (USER_ID, FULL_NAME, EMAIL)
        VALUES (source.USER_ID, source.FULL_NAME, :email)",
    new OracleParameter("userId", userId),
    new OracleParameter("fullName", "Ana Garcia Updated"),
    new OracleParameter("email", "ana@mail.com"));
```

## 6. Antipatrones

### 6.1 ❌ SQL Injection por Concatenación

**Problema**:
```csharp
// ❌ Concatenar input del usuario directamente en SQL
var username = Request.Query["username"]; // Input: "admin' OR '1'='1"
var query = $"SELECT * FROM users WHERE username = '{username}'";
var users = await _dbContext.Users.FromSqlRaw(query).ToListAsync();

// Query resultante: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
// Permite acceso no autorizado a todos los usuarios
```

**Solución**:
```csharp
// ✅ Usar parametrización automática con FromSqlInterpolated
var username = Request.Query["username"];
var users = await _dbContext.Users
    .FromSqlInterpolated($"SELECT * FROM users WHERE username = {username}")
    .ToListAsync(cancellationToken);

// ✅ O preferir LINQ (más seguro)
var users = await _dbContext.Users
    .Where(u => u.Username == username)
    .ToListAsync(cancellationToken);
```

### 6.2 ❌ N+1 Query Problem

**Problema**:
```csharp
// ❌ Carga lazy de relaciones genera 1 + N queries
var orders = await _dbContext.Orders.ToListAsync(); // 1 query

foreach (var order in orders) // N queries (1 por cada orden)
{
    Console.WriteLine($"Order {order.Id}: User {order.User.FullName}");
    // Genera: SELECT * FROM users WHERE user_id = {order.UserId}
}
// Total: 1 + N queries (ej: 1 + 100 = 101 queries para 100 órdenes)
```

**Solución**:
```csharp
// ✅ Usar Include() para eager loading (1 query con JOIN)
var orders = await _dbContext.Orders
    .Include(o => o.User)
    .Include(o => o.OrderItems)
    .ToListAsync(cancellationToken);

// Genera 1 query:
// SELECT o.*, u.*, oi.* FROM orders o
// LEFT JOIN user_profiles u ON o.user_id = u.user_id
// LEFT JOIN order_items oi ON o.order_id = oi.order_id

foreach (var order in orders)
{
    Console.WriteLine($"Order {order.Id}: User {order.User.FullName}");
}
```

### 6.3 ❌ Índices Faltantes en Columnas de Búsqueda

**Problema**:
```sql
-- ❌ Query sin índice genera Sequential Scan (lento)
SELECT * FROM orders WHERE status = 'pending' AND created_at > '2025-01-01';

-- EXPLAIN ANALYZE muestra:
-- Seq Scan on orders (cost=0.00..1000.00 rows=50000) (actual time=150.23..300.45)
-- -> Escanea toda la tabla (1M registros) en lugar de usar índice
```

**Solución**:
```sql
-- ✅ Crear índice compuesto para queries frecuentes
CREATE INDEX idx_orders_status_created_at ON orders(status, created_at DESC);

-- EXPLAIN ANALYZE ahora muestra:
-- Index Scan using idx_orders_status_created_at (cost=0.42..10.50 rows=50)
-- -> Usa índice, 30x más rápido
```

```csharp
// ✅ Configurar índice en Entity Framework
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Order>()
        .HasIndex(o => new { o.Status, o.CreatedAt })
        .HasDatabaseName("idx_orders_status_created_at");
}
```

### 6.4 ❌ Ausencia de Transacciones en Operaciones Críticas

**Problema**:
```csharp
// ❌ Sin transacción, puede generar inconsistencia
public async Task TransferFundsAsync(Guid fromAccountId, Guid toAccountId, decimal amount)
{
    var fromAccount = await _dbContext.Accounts.FindAsync(fromAccountId);
    fromAccount!.Balance -= amount;
    await _dbContext.SaveChangesAsync(); // 1er SaveChanges
    
    // Si falla aquí (exception, crash, network), el dinero desaparece
    
    var toAccount = await _dbContext.Accounts.FindAsync(toAccountId);
    toAccount!.Balance += amount;
    await _dbContext.SaveChangesAsync(); // 2do SaveChanges
}
```

**Solución**:
```csharp
// ✅ Usar transacción explícita para atomicidad
public async Task TransferFundsAsync(Guid fromAccountId, Guid toAccountId, decimal amount)
{
    await using var transaction = await _dbContext.Database
        .BeginTransactionAsync(IsolationLevel.ReadCommitted);
    
    try
    {
        var fromAccount = await _dbContext.Accounts.FindAsync(fromAccountId);
        fromAccount!.Balance -= amount;
        
        var toAccount = await _dbContext.Accounts.FindAsync(toAccountId);
        toAccount!.Balance += amount;
        
        await _dbContext.SaveChangesAsync(); // 1 solo SaveChanges
        await transaction.CommitAsync(); // Todo o nada
    }
    catch
    {
        await transaction.RollbackAsync(); // Rollback automático
        throw;
    }
}
```

## 7. Validación y Testing

### 7.1 Tests Unitarios del Repository

```csharp
public class OrderRepositoryTests : IDisposable
{
    private readonly ApplicationDbContext _dbContext;

    public OrderRepositoryTests()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;
        
        _dbContext = new ApplicationDbContext(options);
    }

    [Fact]
    public async Task GetByIdAsync_ExistingOrder_ReturnsOrder()
    {
        // Arrange
        var order = Order.Create(UserId.New(), new List<OrderItemDto>());
        _dbContext.Orders.Add(order);
        await _dbContext.SaveChangesAsync();

        var repository = new OrderRepository(_dbContext);

        // Act
        var result = await repository.GetByIdAsync(order.Id, CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(order.Id);
    }

    public void Dispose() => _dbContext.Dispose();
}
```

### 7.2 Tests de Integración con TestContainers

```csharp
public class OrderIntegrationTests : IAsyncLifetime
{
    private PostgreSqlContainer _postgresContainer = null!;
    private ApplicationDbContext _dbContext = null!;

    public async Task InitializeAsync()
    {
        _postgresContainer = new PostgreSqlBuilder()
            .WithImage("postgres:16-alpine")
            .WithDatabase("talma_test")
            .WithUsername("test_user")
            .WithPassword("test_password")
            .Build();

        await _postgresContainer.StartAsync();

        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseNpgsql(_postgresContainer.GetConnectionString())
            .Options;

        _dbContext = new ApplicationDbContext(options);
        await _dbContext.Database.MigrateAsync();
    }

    [Fact]
    public async Task CreateOrder_WithTransaction_PersistsCorrectly()
    {
        // Arrange
        var service = new OrderService(_dbContext, Mock.Of<ILogger<OrderService>>());
        var command = new CreateOrderCommand(UserId.New(), new List<OrderItemDto>
        {
            new(ProductId.New(), 2, 50.00m)
        });

        // Act
        var result = await service.CreateOrderAsync(command, CancellationToken.None);

        // Assert
        result.IsSuccess.Should().BeTrue();
        var order = await _dbContext.Orders.FindAsync(result.Value);
        order.Should().NotBeNull();
        order!.Items.Should().HaveCount(1);
    }

    public async Task DisposeAsync()
    {
        await _dbContext.DisposeAsync();
        await _postgresContainer.DisposeAsync();
    }
}
```

### 7.3 Análisis de Performance

```csharp
// Benchmark con BenchmarkDotNet
[MemoryDiagnoser]
public class QueryBenchmarks
{
    private ApplicationDbContext _dbContext = null!;

    [GlobalSetup]
    public void Setup()
    {
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseNpgsql("Host=localhost;Database=talma_bench;")
            .Options;
        _dbContext = new ApplicationDbContext(options);
    }

    [Benchmark]
    public async Task Query_WithIncludes()
    {
        var orders = await _dbContext.Orders
            .Include(o => o.User)
            .Include(o => o.OrderItems)
            .ToListAsync();
    }

    [Benchmark]
    public async Task Query_WithProjection()
    {
        var orders = await _dbContext.Orders
            .Select(o => new 
            { 
                o.OrderId, 
                UserName = o.User.FullName,
                ItemCount = o.OrderItems.Count 
            })
            .ToListAsync();
    }
}
```

## 8. Referencias

### Lineamientos Relacionados
- [Calidad de Código](/docs/fundamentos-corporativos/lineamientos/desarrollo/calidad-de-codigo) - Aplica SOLID y Clean Code a lógica de dominio
- [Gestión de Datos Maestros](/docs/fundamentos-corporativos/lineamientos/datos/gestion-de-datos-maestros) - Normalización y modelado de datos
- [Seguridad desde el Diseño](/docs/fundamentos-corporativos/lineamientos/seguridad/seguridad-desde-el-diseno) - Prevención de SQL Injection y least privilege

### Estándares Relacionados
- [Código C#/.NET](./01-csharp-dotnet.md) - Convenciones de código .NET para repositories
- [Testing de Integración](../testing/02-integration-tests.md) - Tests con TestContainers PostgreSQL/Oracle

### Convenciones Relacionadas
- [Nomenclatura de Objetos de Base de Datos](../../convenciones/codigo/04-objetos-base-datos.md) - snake_case (PostgreSQL) y UPPER_SNAKE_CASE (Oracle)

### Recursos Externos
- [Entity Framework Core Documentation](https://learn.microsoft.com/en-us/ef/core/)
- [Npgsql Entity Framework Core Provider](https://www.npgsql.org/efcore/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [SQL Style Guide](https://www.sqlstyle.guide/es/)

## 9. Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-08-08 | Equipo de Arquitectura | Versión inicial con template de 9 secciones |
