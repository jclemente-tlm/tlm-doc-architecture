---
id: connection-pooling
sidebar_position: 4
title: Connection Pooling
description: Configuración de connection pooling para PostgreSQL con Npgsql
---

# Connection Pooling

## Contexto

Este estándar define cómo configurar connection pooling para optimizar conexiones a PostgreSQL, reducir latencia y maximizar throughput. Complementa el [lineamiento de Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md) especificando **cómo reutilizar conexiones** eficientemente.

---

## Stack Tecnológico

| Componente        | Tecnología            | Versión | Uso                             |
| ----------------- | --------------------- | ------- | ------------------------------- |
| **Database**      | PostgreSQL            | 15+     | Base de datos relacional        |
| **Cloud Service** | Amazon RDS            | -       | PostgreSQL managed service      |
| **Provider**      | Npgsql                | 8.0+    | ADO.NET provider for PostgreSQL |
| **ORM**           | Entity Framework Core | 8.0+    | Object-relational mapping       |

---

## Implementación Técnica

### Conceptos de Connection Pooling

```yaml
# ✅ Connection Pool mantiene pool de conexiones abiertas
# En lugar de:
#   1. Abrir conexión (300-500ms)
#   2. Ejecutar query (10ms)
#   3. Cerrar conexión (50ms)
# Con pooling:
#   1. Obtener conexión del pool (< 1ms)
#   2. Ejecutar query (10ms)
#   3. Retornar conexión al pool (< 1ms)

Connection Pool:
  [Conexión 1] ──┐
  [Conexión 2] ──┼── Pool (memoria)
  [Conexión 3] ──┘

# Estado de conexiones:
- Idle: Disponible en pool
- Active: En uso por query
- Waiting: Esperando conexión disponible (si pool lleno)
```

### Configuración de Connection String

```csharp
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=tlm-orders-db.abc.us-east-1.rds.amazonaws.com;Database=orders;Username=orders_api;Password=***;Pooling=true;Minimum Pool Size=2;Maximum Pool Size=100;Connection Idle Lifetime=300;Connection Pruning Interval=10;Timeout=30;Command Timeout=30;Cancellation Timeout=5;"
  }
}

// Program.cs
builder.Services.AddDbContext<OrdersDbContext>(options =>
{
    var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
    options.UseNpgsql(connectionString);
});
```

### Parámetros de Connection String

```csharp
var connectionStringBuilder = new NpgsqlConnectionStringBuilder
{
    // ✅ Básicos
    Host = "tlm-orders-db.abc.us-east-1.rds.amazonaws.com",
    Port = 5432,
    Database = "orders",
    Username = "orders_api",
    Password = secretPassword,

    // ✅ Pooling habilitado (default: true)
    Pooling = true,

    // ✅ Minimum Pool Size (conexiones mantenidas siempre)
    MinPoolSize = 2,  // ⚠️ Default: 0 (no pre-carga conexiones)

    // ✅ Maximum Pool Size (límite de conexiones)
    MaxPoolSize = 100,  // ⚠️ Default: 100

    // ✅ Connection Idle Lifetime (segundos antes de cerrar conexión idle)
    ConnectionIdleLifetime = 300,  // 5 minutos (default: 300)

    // ✅ Connection Pruning Interval (frecuencia de limpieza de idle connections)
    ConnectionPruningInterval = 10,  // 10 segundos (default: 10)

    // ✅ Timeout para obtener conexión del pool
    Timeout = 30,  // 30 segundos (default: 15)

    // ✅ Command Timeout (timeout de query)
    CommandTimeout = 30,  // 30 segundos (default: 30)

    // ✅ Cancellation Timeout
    CancellationTimeout = 5,  // 5 segundos (default: 2)

    // ✅ SSL/TLS
    SslMode = SslMode.Require,
    TrustServerCertificate = false,

    // ✅ Application Name (para pg_stat_activity)
    ApplicationName = "OrdersAPI",

    // ✅ Performance
    NoResetOnClose = true,  // No ejecutar DISCARD ALL al retornar al pool
    MaxAutoPrepare = 10,  // Preparar hasta 10 statements automáticamente
    AutoPrepareMinUsages = 2  // Preparar después de 2 usos
};

var connectionString = connectionStringBuilder.ToString();
```

### Cálculo de Pool Size

```csharp
// ✅ Fórmula para Maximum Pool Size:
// MaxPoolSize = (Número de workers) * (Concurrent requests per worker) * (Queries per request)

// Ejemplo:
// - ECS tasks: 10 instancias
// - Concurrent requests per task: ~50 (ASP.NET Core)
// - Queries per request: 2 (promedio)
// MaxPoolSize = 10 * 50 * 2 = 1000 conexiones teórico

// ⚠️ PERO: RDS PostgreSQL tiene límite de conexiones
// db.t3.medium (4GB RAM): max_connections = 135
// db.r5.large (16GB RAM): max_connections = 410
// db.r5.xlarge (32GB RAM): max_connections = 810

// ✅ Fórmula ajustada:
// MaxPoolSize = (RDS max_connections - reserved) / (número de instancias)
// MaxPoolSize = (410 - 10) / 10 = 40 conexiones por instancia

public static class ConnectionPoolCalculator
{
    public static int CalculateMaxPoolSize(
        int rdsMaxConnections,
        int numberOfInstances,
        int reservedConnections = 10)
    {
        return (rdsMaxConnections - reservedConnections) / numberOfInstances;
    }

    // Ejemplo:
    // 10 ECS tasks, RDS db.r5.large (410 connections)
    // MaxPoolSize = (410 - 10) / 10 = 40 por instancia
}
```

### Configuración por Entorno

```csharp
// appsettings.Development.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=orders_dev;Username=postgres;Password=***;Pooling=true;Minimum Pool Size=1;Maximum Pool Size=5;"
  }
}

// appsettings.Production.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=${RDS_ENDPOINT};Database=orders;Username=orders_api;Password=${DB_PASSWORD};Pooling=true;Minimum Pool Size=5;Maximum Pool Size=50;Connection Idle Lifetime=300;Timeout=30;"
  }
}

// Program.cs - Validar configuración en startup
var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<OrdersDbContext>();
    var connectionString = context.Database.GetConnectionString();

    var builder = new NpgsqlConnectionStringBuilder(connectionString);

    app.Logger.LogInformation(
        "Database connection pool configured: MinPoolSize={Min}, MaxPoolSize={Max}, Host={Host}",
        builder.MinPoolSize, builder.MaxPoolSize, builder.Host);

    // ⚠️ Validar configuración
    if (builder.MaxPoolSize > 100)
    {
        app.Logger.LogWarning(
            "MaxPoolSize {MaxPoolSize} is very high. Verify RDS max_connections.",
            builder.MaxPoolSize);
    }
}
```

### Monitoreo de Connection Pool

```csharp
// Middleware para tracking de connection pool
public class ConnectionPoolMonitoringMiddleware
{
    private readonly RequestDelegate _next;
    private readonly Gauge _poolSize;
    private readonly Gauge _idleConnections;
    private readonly Gauge _activeConnections;
    private readonly Counter _poolExhausted;

    public ConnectionPoolMonitoringMiddleware(
        RequestDelegate next,
        IMeterFactory meterFactory)
    {
        _next = next;

        var meter = meterFactory.Create("Talma.Database.ConnectionPool");

        _poolSize = meter.CreateGauge<int>(
            "db.connection_pool.size",
            "connections",
            "Total connections in pool");

        _idleConnections = meter.CreateGauge<int>(
            "db.connection_pool.idle",
            "connections",
            "Idle connections");

        _activeConnections = meter.CreateGauge<int>(
            "db.connection_pool.active",
            "connections",
            "Active connections");

        _poolExhausted = meter.CreateCounter<long>(
            "db.connection_pool.exhausted",
            "events",
            "Pool exhausted events");
    }

    public async Task InvokeAsync(HttpContext context, OrdersDbContext dbContext)
    {
        // ✅ Obtener métricas de Npgsql
        var connectionString = dbContext.Database.GetConnectionString();
        var poolStats = NpgsqlConnection.GetPoolStatistics(connectionString);

        _poolSize.Record(poolStats.Total);
        _idleConnections.Record(poolStats.Idle);
        _activeConnections.Record(poolStats.Active);

        if (poolStats.Idle == 0 && poolStats.Active >= poolStats.Total)
        {
            _poolExhausted.Add(1);
        }

        await _next(context);
    }
}

// Register middleware
app.UseMiddleware<ConnectionPoolMonitoringMiddleware>();
```

### Queries de Monitoreo PostgreSQL

```sql
-- ✅ Ver conexiones actuales por aplicación
SELECT
    application_name,
    state,
    COUNT(*) as connection_count
FROM pg_stat_activity
WHERE datname = 'orders'
GROUP BY application_name, state
ORDER BY connection_count DESC;

/*
Resultado:
application_name  | state  | connection_count
------------------+--------+------------------
OrdersAPI         | active | 15
OrdersAPI         | idle   | 85
BackgroundWorker  | active | 5
*/

-- ✅ Conexiones idle más antiguas
SELECT
    pid,
    application_name,
    state,
    state_change,
    NOW() - state_change as idle_duration,
    query
FROM pg_stat_activity
WHERE datname = 'orders'
AND state = 'idle'
ORDER BY state_change ASC
LIMIT 10;

-- ✅ Conexiones bloqueadas esperando locks
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- ✅ Verificar max_connections configurado
SHOW max_connections;

-- ✅ Configurar alarma cuando conexiones > 80%
SELECT
    (SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'orders') as current_connections,
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections,
    ROUND(
        (SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'orders')::numeric /
        (SELECT setting::int FROM pg_settings WHERE name = 'max_connections')::numeric * 100,
        2
    ) as usage_percentage;
```

### Mejores Prácticas de Uso

```csharp
// ✅ BIEN: DbContext con scope correcto
public class OrdersController : ControllerBase
{
    private readonly OrdersDbContext _context;

    public OrdersController(OrdersDbContext context)
    {
        // ✅ Inyectado como scoped (1 instancia por request)
        _context = context;
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetOrder(Guid id)
    {
        var order = await _context.Orders.FindAsync(id);
        // ✅ Conexión retornada al pool automáticamente al final del request
        return Ok(order);
    }
}

// ❌ MAL: Mantener conexión abierta innecesariamente
public async Task<Order> GetOrderBadAsync(Guid id)
{
    using var connection = new NpgsqlConnection(_connectionString);
    await connection.OpenAsync();  // ✅ Obtiene del pool

    // ❌ Lógica business compleja con conexión abierta
    await Task.Delay(5000);  // Simulando procesamiento

    var command = new NpgsqlCommand("SELECT * FROM orders WHERE order_id = @id", connection);
    command.Parameters.AddWithValue("id", id);

    // ... mapear resultado

    // ❌ Conexión retenida 5+ segundos innecesariamente
    return order;
}  // Aquí finalmente retorna al pool

// ✅ BIEN: Conexión solo durante query
public async Task<Order> GetOrderGoodAsync(Guid id)
{
    // ✅ Procesamiento business sin conexión
    await Task.Delay(5000);

    // ✅ Conexión abierta solo para query
    using var connection = new NpgsqlConnection(_connectionString);
    await connection.OpenAsync();

    var command = new NpgsqlCommand("SELECT * FROM orders WHERE order_id = @id", connection);
    command.Parameters.AddWithValue("id", id);

    // ... ejecutar y mapear

    return order;
}  // Conexión retornada en < 50ms

// ✅ MEJOR: Usar DbContext (maneja todo automáticamente)
public async Task<Order> GetOrderBestAsync(Guid id)
{
    return await _context.Orders.FindAsync(id);
    // ✅ EF Core maneja apertura/cierre automáticamente
    // ✅ Conexión abierta solo durante query execution
}
```

### Health Check de Connection Pool

```csharp
public class DatabaseConnectionPoolHealthCheck : IHealthCheck
{
    private readonly string _connectionString;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // ✅ Verificar pool statistics
            var poolStats = NpgsqlConnection.GetPoolStatistics(_connectionString);

            var data = new Dictionary<string, object>
            {
                ["total"] = poolStats.Total,
                ["idle"] = poolStats.Idle,
                ["active"] = poolStats.Active,
                ["pending"] = poolStats.Waiting
            };

            // ⚠️ Warning si pool casi lleno
            if (poolStats.Active >= poolStats.Total * 0.9)
            {
                return HealthCheckResult.Degraded(
                    "Connection pool usage > 90%",
                    data: data);
            }

            // ⚠️ Warning si hay requests waiting
            if (poolStats.Waiting > 0)
            {
                return HealthCheckResult.Degraded(
                    $"{poolStats.Waiting} requests waiting for connection",
                    data: data);
            }

            // ✅ Test básico de conectividad
            await using var connection = new NpgsqlConnection(_connectionString);
            await connection.OpenAsync(cancellationToken);
            await using var command = new NpgsqlCommand("SELECT 1", connection);
            await command.ExecuteScalarAsync(cancellationToken);

            return HealthCheckResult.Healthy("Database connection pool healthy", data);
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Database connection failed", ex);
        }
    }
}

// Register
builder.Services.AddHealthChecks()
    .AddCheck<DatabaseConnectionPoolHealthCheck>("database");
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** habilitar connection pooling (Pooling=true)
- **MUST** configurar Maximum Pool Size basado en RDS max_connections
- **MUST** usar DbContext con lifetime scoped (no singleton)
- **MUST** configurar Connection Idle Lifetime
- **MUST** monitorear pool statistics
- **MUST** configurar alarmas cuando pool usage > 80%
- **MUST** cerrar/disponer conexiones apropiadamente (using statement)

### SHOULD (Fuertemente recomendado)

- **SHOULD** configurar Minimum Pool Size ≥ 2 en producción
- **SHOULD** usar NoResetOnClose=true para mejor performance
- **SHOULD** configurar Command Timeout apropiado
- **SHOULD** usar MaxAutoPrepare para statements frecuentes
- **SHOULD** monitorear conexiones idle en PostgreSQL
- **SHOULD** implementar health checks de pool
- **SHOULD** documentar cálculo de MaxPoolSize

### MAY (Opcional)

- **MAY** usar connection strings diferentes por tipo de carga (read/write)
- **MAY** implementar pooling manual para casos especiales
- **MAY** configurar failover connection strings
- **MAY** usar Enlist=false para transacciones distribuidas

### MUST NOT (Prohibido)

- **MUST NOT** configurar MaxPoolSize > RDS max_connections
- **MUST NOT** mantener conexiones abiertas innecesariamente
- **MUST NOT** usar DbContext como singleton
- **MUST NOT** ignorar timeouts de conexión
- **MUST NOT** deshabilitar pooling sin justificación
- **MUST NOT** crear pool infinito (sin MaxPoolSize)

---

## Referencias

- [Lineamiento: Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md)
- Estándares relacionados:
  - [Optimización de Base de Datos](database-optimization.md)
  - [Diseño Stateless](../../estandares/arquitectura/stateless-design.md)
- ADRs:
  - [ADR-010: PostgreSQL](../../../decisiones-de-arquitectura/adr-010-postgresql-base-datos.md)
- Especificaciones:
  - [Npgsql Connection String Parameters](https://www.npgsql.org/doc/connection-string-parameters.html)
  - [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
  - [EF Core DbContext Lifetime](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/)
