---
id: stateless-services
sidebar_position: 8
title: Servicios Sin Estado (Stateless)
description: Estándar para diseño de servicios stateless externalizing state en Redis, PostgreSQL, S3 para permitir escalado horizontal y recuperación rápida
---

# Estándar Técnico — Servicios Sin Estado (Stateless)

---

## 1. Propósito

Diseñar servicios completamente stateless que externalizan todo estado en sistemas distribuidos (Redis, PostgreSQL, S3), permitiendo escalado horizontal sin sticky sessions, recuperación rápida de fallos y deployment de múltiples instancias sin coordinación.

---

## 2. Alcance

**Aplica a:**

- APIs REST stateless
- Microservicios backend
- Workers de procesamiento
- API Gateways
- Services layer
- Background jobs

**No aplica a:**

- WebSockets con conexión persistente (usar connection pooling)
- Streaming servers (usar session affinity limitado)
- In-memory caches transitorias (permitido con TTL corto)

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología      | Versión mínima | Observaciones       |
| ----------------- | --------------- | -------------- | ------------------- |
| **Session Store** | Redis           | 7.0+           | Distributed session |
| **Database**      | PostgreSQL      | 14+            | Estado persistente  |
| **Cache**         | Redis           | 7.0+           | Cache distribuido   |
| **File Storage**  | AWS S3          | -              | Archivos/uploads    |
| **Locks**         | Redis (RedLock) | 7.0+           | Distributed locks   |
| **Message Queue** | Apache Kafka    | 3.6+           | Estado en eventos   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Externalización de Estado

- [ ] Sesiones de usuario en Redis (no in-memory)
- [ ] Archivos subidos en S3/Blob (no filesystem local)
- [ ] Cache distribuido (Redis) en vez de cache local
- [ ] Estado de workflows en database o Saga
- [ ] Tokens/secrets desde secret manager (no variables de entorno)

### Diseño Stateless

- [ ] No usar `static` mutable variables
- [ ] No depender de filesystem local
- [ ] No sticky sessions / session affinity
- [ ] Idempotencia en operaciones (usar idempotency keys)
- [ ] Cualquier instancia puede procesar cualquier request

### JWT y Autenticación

- [ ] JWT con claims auto-contenidos (no server-side session)
- [ ] Refresh tokens en Redis con TTL
- [ ] Validación de JWT sin estado de sesión
- [ ] Claims con info necesaria (userId, roles, tenant)

### Configuración

- [ ] Config desde variables de entorno
- [ ] Secrets desde AWS Secrets Manager
- [ ] Feature flags desde sistema centralizado
- [ ] No hardcoded configs en código

### Logging y Telemetría

- [ ] Correlation IDs para rastrear requests
- [ ] Logs centralizados (Grafana Loki)
- [ ] Métricas sin estado local
- [ ] Distributed tracing (OpenTelemetry)

---

## 5. Prohibiciones

- ❌ Session state in-memory (ASP.NET Session)
- ❌ Static mutable fields para cache/estado
- ❌ Archivos en filesystem local (usar S3/Blob)
- ❌ Sticky sessions / session affinity
- ❌ Singleton services con estado mutable
- ❌ Locks locales (usar distributed locks)
- ❌ InMemoryCache para datos críticos (usar Redis)

---

## 6. Configuración Mínima

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Session distribuida en Redis
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
});

builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
});

// JWT stateless authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]))
        };
    });

// DbContext con connection pooling (no sticky connections)
builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        npgsqlOptions =>
        {
            npgsqlOptions.EnableRetryOnFailure();
        });
}, ServiceLifetime.Scoped); // Scoped = stateless per request

// File storage en S3 (no local filesystem)
builder.Services.AddSingleton<IS3Client>(sp =>
    new AmazonS3Client(
        new AmazonS3Config { RegionEndpoint = RegionEndpoint.USEast1 }));

var app = builder.Build();

app.UseSession();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.Run();
```

```json
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=db.talma.com;Database=orders;Username=app;Password=<from-secret>",
    "Redis": "redis.talma.com:6379,ssl=true,password=<from-secret>"
  },
  "Jwt": {
    "Issuer": "https://auth.talma.com",
    "Audience": "https://api.talma.com",
    "Key": "<from-secret-manager>"
  },
  "FileStorage": {
    "Provider": "S3",
    "BucketName": "talma-uploads-prod",
    "Region": "us-east-1"
  }
}
```

---

## 7. Ejemplos

### Controller stateless

```csharp
[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    // ✅ Dependencies inyectadas (Scoped/Transient)
    private readonly IOrderService _orderService;
    private readonly IDistributedCache _cache;

    // ❌ NO hacer esto:
    // private static Dictionary<string, Order> _orders = new(); // Estado mutable

    [HttpPost]
    public async Task<IActionResult> CreateOrder(
        [FromBody] CreateOrderRequest request,
        CancellationToken cancellationToken)
    {
        // Idempotency key desde header
        var idempotencyKey = Request.Headers["Idempotency-Key"].FirstOrDefault()
            ?? throw new BadRequestException("Idempotency-Key requerido");

        // Verificar si operación ya fue procesada
        var cachedResult = await _cache.GetStringAsync(
            $"idempotency:{idempotencyKey}",
            cancellationToken);

        if (cachedResult != null)
        {
            return Ok(JsonSerializer.Deserialize<Order>(cachedResult));
        }

        // Procesar orden
        var order = await _orderService.CreateAsync(request, cancellationToken);

        // Guardar resultado para idempotencia
        await _cache.SetStringAsync(
            $"idempotency:{idempotencyKey}",
            JsonSerializer.Serialize(order),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromHours(24)
            },
            cancellationToken);

        return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
    }
}
```

### File upload en S3 (no filesystem local)

```csharp
public class FileStorageService
{
    private readonly IAmazonS3 _s3Client;
    private readonly string _bucketName;

    public async Task<string> UploadFileAsync(
        IFormFile file,
        CancellationToken cancellationToken)
    {
        // ✅ Subir a S3
        var key = $"uploads/{Guid.NewGuid()}/{file.FileName}";

        using var stream = file.OpenReadStream();

        await _s3Client.PutObjectAsync(new PutObjectRequest
        {
            BucketName = _bucketName,
            Key = key,
            InputStream = stream,
            ContentType = file.ContentType,
            ServerSideEncryptionMethod = ServerSideEncryptionMethod.AES256
        }, cancellationToken);

        // ❌ NO hacer esto:
        // var localPath = Path.Combine("/var/uploads", file.FileName);
        // using var fileStream = new FileStream(localPath, FileMode.Create);
        // await file.CopyToAsync(fileStream);

        return key; // Retornar S3 key, no path local
    }
}
```

### Distributed lock con Redis

```csharp
public class InventoryService
{
    private readonly IConnectionMultiplexer _redis;

    public async Task<bool> ReserveItemAsync(string itemId, int quantity)
    {
        var db = _redis.GetDatabase();
        var lockKey = $"lock:inventory:{itemId}";
        var lockValue = Guid.NewGuid().ToString();
        var expiry = TimeSpan.FromSeconds(10);

        // Adquirir distributed lock
        var acquired = await db.StringSetAsync(
            lockKey,
            lockValue,
            expiry,
            when: When.NotExists);

        if (!acquired)
            return false; // Lock no adquirido

        try
        {
            // Operación crítica
            var currentStock = await db.StringGetAsync($"inventory:{itemId}");
            var stock = int.Parse(currentStock);

            if (stock >= quantity)
            {
                await db.StringSetAsync($"inventory:{itemId}", stock - quantity);
                return true;
            }

            return false;
        }
        finally
        {
            // Liberar lock solo si es nuestro
            await db.ScriptEvaluateAsync(@"
                if redis.call('get', KEYS[1]) == ARGV[1] then
                    return redis.call('del', KEYS[1])
                else
                    return 0
                end",
                new RedisKey[] { lockKey },
                new RedisValue[] { lockValue });
        }
    }
}
```

---

## 8. Validación y Auditoría

```bash
# Verificar no hay static mutable state
grep -r "private static" --include="*.cs" ./ | grep -v "readonly"

# Verificar uso de IDistributedCache
grep -r "IDistributedCache" --include="*.cs" ./

# Verificar no hay filesystem local writes
grep -r "File.WriteAllText\|FileStream" --include="*.cs" ./
```

**Métricas de cumplimiento:**

| Métrica                           | Umbral    | Verificación    |
| --------------------------------- | --------- | --------------- |
| Servicios con session distribuida | 100%      | Code review     |
| Static mutable fields             | 0         | Static analysis |
| File uploads en S3/Blob           | 100%      | Code review     |
| JWT authentication                | 100% APIs | Config review   |

**Checklist de auditoría:**

- [ ] No hay static mutable state
- [ ] Session store en Redis
- [ ] Files en S3/Blob, no filesystem
- [ ] JWT authentication sin server-side sessions
- [ ] Distributed cache (Redis)
- [ ] Config desde env vars
- [ ] Idempotency keys en POST/PUT

---

## 9. Referencias

- [12-Factor App - VI. Processes](https://12factor.net/processes)
- [AWS Well-Architected - Stateless Components](https://docs.aws.amazon.com/wellarchitected/latest/framework/a-stateless-components.html)
- [Azure Architecture - Stateless Applications](https://learn.microsoft.com/en-us/azure/architecture/guide/design-principles/scale-out)
- [Redis Distributed Locks](https://redis.io/docs/manual/patterns/distributed-locks/)
- [JWT Authentication Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)
- [Idempotency in REST APIs](https://stripe.com/docs/api/idempotent_requests)
