---
id: stateless-design
sidebar_position: 1
title: Diseño Stateless para Escalabilidad Horizontal
description: Arquitectura stateless para permitir escalado horizontal transparente
---

# Diseño Stateless para Escalabilidad Horizontal

## Contexto

Este estándar define cómo diseñar servicios stateless que permitan escalado horizontal transparente. Complementa el [lineamiento de Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md) especificando **cómo eliminar estado local** para soportar múltiples instancias sin afinidad de sesión.

---

## Stack Tecnológico

| Componente        | Tecnología        | Versión | Uso                         |
| ----------------- | ----------------- | ------- | --------------------------- |
| **Runtime**       | ASP.NET Core      | 8.0+    | Framework stateless         |
| **Container**     | AWS ECS Fargate   | 1.4+    | Orquestación stateless      |
| **Session Store** | Redis             | 7.0+    | Estado de sesión compartido |
| **Cache**         | ElastiCache Redis | 7.0+    | Caché distribuido           |
| **File Storage**  | Amazon S3         | -       | Almacenamiento externo      |

---

## Implementación Técnica

### Principios de Diseño Stateless

```csharp
// ❌ MAL: Estado en memoria local (no escala)
public class OrderController : ControllerBase
{
    // ❌ Estado compartido entre requests
    private static Dictionary<string, Order> _orderCache = new();

    [HttpPost("orders")]
    public IActionResult CreateOrder(CreateOrderRequest request)
    {
        var order = new Order { Id = Guid.NewGuid(), ... };
        _orderCache[order.Id.ToString()] = order;  // ❌ Solo en esta instancia
        return Ok(order);
    }

    [HttpGet("orders/{id}")]
    public IActionResult GetOrder(string id)
    {
        // ❌ Falla si request va a otra instancia
        if (_orderCache.TryGetValue(id, out var order))
            return Ok(order);
        return NotFound();
    }
}

// ✅ BIEN: Estado externalizado (escala horizontalmente)
public class OrderController : ControllerBase
{
    private readonly IDistributedCache _cache;
    private readonly IOrderRepository _repository;

    public OrderController(IDistributedCache cache, IOrderRepository repository)
    {
        _cache = cache;
        _repository = repository;
    }

    [HttpPost("orders")]
    public async Task<IActionResult> CreateOrder(CreateOrderRequest request)
    {
        var order = new Order { Id = Guid.NewGuid(), ... };

        // ✅ Persistir en base de datos (shared storage)
        await _repository.SaveAsync(order);

        // ✅ Cachear en Redis (shared cache)
        await _cache.SetStringAsync(
            $"order:{order.Id}",
            JsonSerializer.Serialize(order),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(15)
            });

        return Ok(order);
    }

    [HttpGet("orders/{id}")]
    public async Task<IActionResult> GetOrder(string id)
    {
        // ✅ Buscar en cache compartido primero
        var cached = await _cache.GetStringAsync($"order:{id}");
        if (cached != null)
            return Ok(JsonSerializer.Deserialize<Order>(cached));

        // ✅ Fallback a base de datos
        var order = await _repository.GetByIdAsync(id);
        if (order == null)
            return NotFound();

        return Ok(order);
    }
}
```

### Configuración de Redis para Session State

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Session distribuida en Redis
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration["Redis:ConnectionString"];
    options.InstanceName = "tlm-orders-";
});

// ✅ Distributed cache abstraction
builder.Services.AddDistributedMemoryCache();  // Dev: in-memory
// builder.Services.AddStackExchangeRedisCache(...);  // Prod: Redis

// ✅ ASP.NET Core Session con backing store externo
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    // ✅ Cookie solo transmite session ID, datos en Redis
});

var app = builder.Build();

// ✅ Habilitar session middleware
app.UseSession();

app.MapControllers();
app.Run();
```

### Session Helper Extensions

```csharp
public static class SessionExtensions
{
    /// <summary>
    /// ✅ Serializar objeto complejo a session
    /// </summary>
    public static void SetObject<T>(this ISession session, string key, T value)
    {
        session.SetString(key, JsonSerializer.Serialize(value));
    }

    /// <summary>
    /// ✅ Deserializar objeto desde session
    /// </summary>
    public static T? GetObject<T>(this ISession session, string key)
    {
        var value = session.GetString(key);
        return value == null ? default : JsonSerializer.Deserialize<T>(value);
    }
}

// Uso
public class ShoppingCartController : ControllerBase
{
    [HttpPost("cart/add")]
    public IActionResult AddToCart(AddItemRequest request)
    {
        // ✅ Session respaldada por Redis, funciona en cualquier instancia
        var cart = HttpContext.Session.GetObject<ShoppingCart>("cart")
                   ?? new ShoppingCart();

        cart.Items.Add(new CartItem { ProductId = request.ProductId, Quantity = request.Quantity });

        HttpContext.Session.SetObject("cart", cart);

        return Ok(cart);
    }
}
```

### Manejo de Archivos (Sin Almacenamiento Local)

```csharp
// ❌ MAL: Guardar archivos en filesystem local
[HttpPost("upload")]
public async Task<IActionResult> UploadFile(IFormFile file)
{
    // ❌ Filesystem local, se pierde al escalar o reiniciar
    var path = Path.Combine("/app/uploads", file.FileName);
    using var stream = new FileStream(path, FileMode.Create);
    await file.CopyToAsync(stream);

    return Ok(new { url = $"/uploads/{file.FileName}" });
}

// ✅ BIEN: Guardar en S3
public class FileUploadController : ControllerBase
{
    private readonly IAmazonS3 _s3Client;
    private readonly IConfiguration _config;

    [HttpPost("upload")]
    public async Task<IActionResult> UploadFile(IFormFile file)
    {
        var bucketName = _config["AWS:S3:BucketName"];
        var key = $"uploads/{Guid.NewGuid()}/{file.FileName}";

        // ✅ Almacenamiento externo (S3)
        using var stream = file.OpenReadStream();
        var request = new PutObjectRequest
        {
            BucketName = bucketName,
            Key = key,
            InputStream = stream,
            ContentType = file.ContentType,
            ServerSideEncryptionMethod = ServerSideEncryptionMethod.AES256
        };

        await _s3Client.PutObjectAsync(request);

        // ✅ Retornar URL pública o pre-signed URL
        var url = $"https://{bucketName}.s3.amazonaws.com/{key}";
        return Ok(new { url });
    }
}
```

### Procesamiento de Background Jobs (Stateless)

```csharp
// ❌ MAL: Background service con estado local
public class OrderProcessingService : BackgroundService
{
    // ❌ Cola local, se pierde al reiniciar o escalar
    private readonly ConcurrentQueue<Order> _queue = new();

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            if (_queue.TryDequeue(out var order))
            {
                await ProcessOrder(order);
            }
            await Task.Delay(1000, stoppingToken);
        }
    }
}

// ✅ BIEN: Cola distribuida (SQS o Kafka)
public class OrderProcessingService : BackgroundService
{
    private readonly IAmazonSQS _sqsClient;
    private readonly string _queueUrl;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            // ✅ Recibir mensajes de SQS (cola compartida)
            var request = new ReceiveMessageRequest
            {
                QueueUrl = _queueUrl,
                MaxNumberOfMessages = 10,
                WaitTimeSeconds = 20  // Long polling
            };

            var response = await _sqsClient.ReceiveMessageAsync(request, stoppingToken);

            foreach (var message in response.Messages)
            {
                var order = JsonSerializer.Deserialize<Order>(message.Body);
                await ProcessOrder(order);

                // ✅ Eliminar mensaje después de procesar
                await _sqsClient.DeleteMessageAsync(_queueUrl, message.ReceiptHandle, stoppingToken);
            }
        }
    }
}
```

### Health Checks Stateless

```csharp
// ✅ Health check que valida dependencias externas
public class OrderServiceHealthCheck : IHealthCheck
{
    private readonly IDistributedCache _cache;
    private readonly IOrderRepository _repository;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // ✅ Verificar Redis
            await _cache.SetStringAsync("health-check", "ok",
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = TimeSpan.FromSeconds(5)
                }, cancellationToken);

            // ✅ Verificar Database
            await _repository.HealthCheckAsync(cancellationToken);

            return HealthCheckResult.Healthy("All external dependencies accessible");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("External dependency failure", ex);
        }
    }
}

// Program.cs
builder.Services.AddHealthChecks()
    .AddCheck<OrderServiceHealthCheck>("orders-service")
    .AddRedis(builder.Configuration["Redis:ConnectionString"], "redis")
    .AddNpgSql(builder.Configuration["Database:ConnectionString"], "database");
```

### Configuración de ECS Task (Stateless)

```yaml
# task-definition.json
{
  "family": "orders-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
      {
        "name": "orders-api",
        "image": "ghcr.io/talma/orders-api:1.2.3",
        "portMappings": [{ "containerPort": 8080, "protocol": "tcp" }],
        "environment":
          [
            { "name": "ASPNETCORE_ENVIRONMENT", "value": "Production" },
            { "name": "ASPNETCORE_URLS", "value": "http://+:8080" },
          ],
        "secrets":
          [
            {
              "name": "Redis__ConnectionString",
              "valueFrom": "arn:aws:secretsmanager:us-east-1:123:secret:redis-connection",
            },
            {
              "name": "Database__ConnectionString",
              "valueFrom": "arn:aws:secretsmanager:us-east-1:123:secret:postgres-connection",
            },
          ],
        # ✅ Sin volumes persistentes (stateless)
        "mountPoints": [],

        "healthCheck":
          {
            "command":
              ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
            "interval": 30,
            "timeout": 5,
            "retries": 3,
            "startPeriod": 60,
          },
        "logConfiguration":
          {
            "logDriver": "awslogs",
            "options":
              {
                "awslogs-group": "/ecs/orders-api",
                "awslogs-region": "us-east-1",
                "awslogs-stream-prefix": "ecs",
              },
          },
      },
    ],
}
```

### Auto-Scaling Configuration

```yaml
# auto-scaling.yaml (AWS ECS Service)
resource: ecs-service
scalableDimension: ecs:service:DesiredCount
minCapacity: 2 # ✅ Mínimo 2 instancias para high availability
maxCapacity: 20

# ✅ Scale out en alta carga
scaleOutPolicy:
  targetTrackingScaling:
    predefinedMetricType: ECSServiceAverageCPUUtilization
    targetValue: 70
    scaleOutCooldown: 60

# ✅ Scale in en baja carga
scaleInPolicy:
  targetTrackingScaling:
    predefinedMetricType: ECSServiceAverageCPUUtilization
    targetValue: 70
    scaleInCooldown: 300 # Más conservador para scale-in
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** externalizar todo estado de sesión a Redis
- **MUST** usar IDistributedCache para caché compartido
- **MUST** almacenar archivos en S3, nunca en filesystem local
- **MUST** usar colas externas (SQS/Kafka) para background jobs
- **MUST** evitar variables estáticas mutables
- **MUST** configurar health checks que validen dependencias externas
- **MUST** diseñar para que cualquier instancia pueda manejar cualquier request

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Redis para session store en producción
- **SHOULD** configurar auto-scaling basado en métricas
- **SHOULD** mantener mínimo 2 instancias para high availability
- **SHOULD** implementar circuit breakers para dependencias externas
- **SHOULD** usar correlation IDs para rastrear requests entre instancias
- **SHOULD** configurar graceful shutdown (drain connections)

### MAY (Opcional)

- **MAY** usar sticky sessions solo si absolutamente necesario
- **MAY** implementar client-side caching para reducir carga
- **MAY** usar CDN para contenido estático
- **MAY** implementar rate limiting distribuido (Redis)

### MUST NOT (Prohibido)

- **MUST NOT** almacenar estado de sesión en memoria local
- **MUST NOT** usar sticky sessions como solución permanente
- **MUST NOT** guardar archivos en filesystem de contenedor
- **MUST NOT** usar variables estáticas para compartir datos entre requests
- **MUST NOT** depender de estado local para funcionalidad crítica
- **MUST NOT** asumir que el mismo proceso manejará requests relacionados

---

## Referencias

- [Lineamiento: Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md)
- Estándares relacionados:
  - [Auto-Scaling](../../estandares/infraestructura/horizontal-scaling.md)
  - [Estrategias de Caché](caching-strategies.md)
  - [Load Balancing](../../estandares/infraestructura/load-balancing.md)
- ADRs:
  - [ADR-007: AWS ECS Fargate](../../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- Especificaciones:
  - [The Twelve-Factor App - VI. Processes](https://12factor.net/processes)
  - [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
