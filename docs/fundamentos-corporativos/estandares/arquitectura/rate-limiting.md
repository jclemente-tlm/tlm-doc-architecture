---
id: rate-limiting
sidebar_position: 6
title: Rate Limiting y Throttling
description: Protección contra sobrecarga y abuso mediante rate limiting
---

# Rate Limiting y Throttling

## Contexto

Este estándar define cómo implementar rate limiting para proteger servicios de sobrecarga, abuso y ataques. Complementa el [lineamiento de Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md) especificando **cómo limitar la tasa de requests** para garantizar disponibilidad.

---

## Stack Tecnológico

| Componente           | Tecnología          | Versión | Uso                                      |
| -------------------- | ------------------- | ------- | ---------------------------------------- |
| **Framework**        | ASP.NET Core        | 8.0+    | Framework base                           |
| **Rate Limiting**    | ASP.NET Core        | 8.0+    | Built-in rate limiting middleware        |
| **Distributed Rate** | Redis               | 7.2+    | Contador distribuido para multi-instance |
| **API Gateway**      | Kong API Gateway    | 3.4+    | Rate limiting en gateway layer           |
| **Cache**            | StackExchange.Redis | 2.7+    | Cliente Redis                            |

---

## Implementación Técnica

### Algoritmos de Rate Limiting

```yaml
# ✅ Algoritmos disponibles

1. Fixed Window:
   [────5 req/min────][────5 req/min────]
   ✅ Simple, bajo overhead
   ❌ Spike al inicio de ventana

2. Sliding Window:
   [──1 req──2 req──3 req──4 req──5 req──]
                    ↑ ventana deslizante
   ✅ Más suave que fixed window
   ❌ Más complejo

3. Token Bucket:
   Bucket: [🪙🪙🪙🪙🪙] (5 tokens, refill 1/sec)
   Request consume 1 token
   ✅ Permite bursts
   ❌ Requiere state management

4. Concurrency:
   Concurrent requests: [────10 max────]
   ✅ Protege recursos (threads, connections)
   ❌ No protege de small request floods
```

### Fixed Window Rate Limiting

```csharp
// Program.cs
using Microsoft.AspNetCore.RateLimitting;

var builder = WebApplication.CreateBuilder(args);

// ✅ Configurar rate limiting
builder.Services.AddRateLimiter(options =>
{
    // ✅ Policy global: 100 requests por minuto
    options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
    {
        return RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: context.User?.Identity?.Name ?? context.Connection.RemoteIpAddress?.ToString() ?? "anonymous",
            factory: partition => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 100,
                Window = TimeSpan.FromMinutes(1),
                QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                QueueLimit = 10  // ✅ Queue hasta 10 requests
            });
    });

    // ✅ Policy específica para operaciones costosas
    options.AddPolicy("expensive", context =>
    {
        var userId = context.User?.Identity?.Name ?? "anonymous";

        return RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: userId,
            factory: _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 5,
                Window = TimeSpan.FromMinutes(1),
                QueueProcessingOrder = QueueProcessingOrder.NewestFirst,
                QueueLimit = 0  // ✅ Sin queue, fail-fast
            });
    });

    // ✅ Configurar respuesta cuando excede límite
    options.OnRejected = async (context, cancellationToken) =>
    {
        context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;

        // ✅ Retry-After header
        if (context.Lease.TryGetMetadata(MetadataName.RetryAfter, out var retryAfter))
        {
            context.HttpContext.Response.Headers.RetryAfter = retryAfter.TotalSeconds.ToString();
        }

        await context.HttpContext.Response.WriteAsJsonAsync(new
        {
            error = "too_many_requests",
            message = "Rate limit exceeded. Please try again later.",
            retryAfter = retryAfter?.TotalSeconds
        }, cancellationToken);
    };
});

var app = builder.Build();

// ✅ Habilitar middleware
app.UseRateLimiter();

app.MapGet("/api/orders", GetOrders);

// ✅ Aplicar policy específica
app.MapPost("/api/reports", GenerateReport)
    .RequireRateLimiting("expensive");

app.Run();
```

### Sliding Window Rate Limiting

```csharp
// ✅ Sliding window más preciso
builder.Services.AddRateLimiter(options =>
{
    options.AddSlidingWindowLimiter("sliding", slidingOptions =>
    {
        slidingOptions.PermitLimit = 100;
        slidingOptions.Window = TimeSpan.FromMinutes(1);
        slidingOptions.SegmentsPerWindow = 6;  // ✅ 6 segmentos de 10 segundos
        slidingOptions.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        slidingOptions.QueueLimit = 10;
    });
});

// Ejemplo de deslizamiento:
// Ventana 1 min dividida en 6 segmentos de 10s
// [seg1: 10 req][seg2: 15 req][seg3: 20 req][seg4: 18 req][seg5: 22 req][seg6: 15 req]
// Total actual = sum(últimos 6 segmentos) = 100 requests
// Cuando pasa seg7, se descarta seg1
```

### Token Bucket Rate Limiting

```csharp
// ✅ Token bucket permite bursts
builder.Services.AddRateLimiter(options =>
{
    options.AddTokenBucketLimiter("api", tokenOptions =>
    {
        tokenOptions.TokenLimit = 100;  // ✅ Bucket capacity
        tokenOptions.ReplenishmentPeriod = TimeSpan.FromSeconds(10);
        tokenOptions.TokensPerPeriod = 20;  // ✅ Refill 20 tokens cada 10s
        tokenOptions.AutoReplenishment = true;
        tokenOptions.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        tokenOptions.QueueLimit = 5;
    });
});

// Comportamiento:
// - Inicio: 100 tokens disponibles → permite burst de 100 requests
// - Cada 10s: +20 tokens (hasta max 100)
// - Request consume 1 token
// ✅ Permite bursts temporales sin violar throughput promedio
```

### Concurrency Limiter

```csharp
// ✅ Limitar requests concurrentes (similar a bulkhead)
builder.Services.AddRateLimiter(options =>
{
    options.AddConcurrencyLimiter("concurrent", concurrencyOptions =>
    {
        concurrencyOptions.PermitLimit = 50;  // ✅ Max 50 concurrent requests
        concurrencyOptions.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        concurrencyOptions.QueueLimit = 100;  // ✅ Queue hasta 100
    });
});

// ✅ Útil para proteger recursos compartidos
app.MapPost("/api/file-upload", UploadFile)
    .RequireRateLimiting("concurrent");
```

### Distributed Rate Limiting con Redis

```csharp
// ✅ Rate limiting distribuido entre múltiples instancias

public class RedisFixedWindowRateLimiter
{
    private readonly IConnectionMultiplexer _redis;
    private readonly ILogger<RedisFixedWindowRateLimiter> _logger;

    public async Task<RateLimitResult> CheckRateLimitAsync(
        string key,
        int limit,
        TimeSpan window,
        CancellationToken cancellationToken = default)
    {
        var db = _redis.GetDatabase();
        var redisKey = $"ratelimit:{key}";

        // ✅ Script Lua para atomicidad (INCR + EXPIRE)
        var script = @"
            local current = redis.call('INCR', KEYS[1])
            if current == 1 then
                redis.call('EXPIRE', KEYS[1], ARGV[1])
            end
            return current
        ";

        var result = await db.ScriptEvaluateAsync(
            script,
            keys: new RedisKey[] { redisKey },
            values: new RedisValue[] { (int)window.TotalSeconds });

        var count = (long)result;
        var allowed = count <= limit;

        if (!allowed)
        {
            _logger.LogWarning(
                "Rate limit exceeded for key {Key}. Count: {Count}, Limit: {Limit}",
                key, count, limit);
        }

        var ttl = await db.KeyTimeToLiveAsync(redisKey);

        return new RateLimitResult
        {
            Allowed = allowed,
            CurrentCount = count,
            Limit = limit,
            RetryAfter = ttl ?? window
        };
    }
}

// Uso en controller
[ApiController]
public class OrdersController : ControllerBase
{
    private readonly RedisFixedWindowRateLimiter _rateLimiter;

    [HttpPost]
    public async Task<IActionResult> CreateOrder(CreateOrderRequest request)
    {
        // ✅ Rate limit por usuario
        var userId = User.Identity!.Name!;
        var result = await _rateLimiter.CheckRateLimitAsync(
            key: $"user:{userId}:orders",
            limit: 10,
            window: TimeSpan.FromMinutes(1));

        if (!result.Allowed)
        {
            Response.Headers.RetryAfter = result.RetryAfter.TotalSeconds.ToString();
            return StatusCode(429, new
            {
                error = "too_many_requests",
                message = $"Rate limit exceeded. Try again in {result.RetryAfter.TotalSeconds}s"
            });
        }

        // ✅ Procesar orden
        var order = await _orderService.CreateOrderAsync(request);
        return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
    }
}
```

### Sliding Window Log con Redis

```csharp
// ✅ Sliding window más preciso con Redis sorted sets
public class RedisSlidingWindowRateLimiter
{
    private readonly IConnectionMultiplexer _redis;

    public async Task<bool> IsAllowedAsync(
        string key,
        int limit,
        TimeSpan window)
    {
        var db = _redis.GetDatabase();
        var redisKey = $"ratelimit:sliding:{key}";
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        var windowStart = now - (long)window.TotalMilliseconds;

        // ✅ Script Lua para atomicidad
        var script = @"
            local key = KEYS[1]
            local now = tonumber(ARGV[1])
            local window_start = tonumber(ARGV[2])
            local limit = tonumber(ARGV[3])

            -- Eliminar entries fuera de ventana
            redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

            -- Contar requests en ventana
            local count = redis.call('ZCARD', key)

            if count < limit then
                -- Agregar nuevo request
                redis.call('ZADD', key, now, now)
                redis.call('EXPIRE', key, 60)
                return 1
            else
                return 0
            end
        ";

        var result = await db.ScriptEvaluateAsync(
            script,
            keys: new RedisKey[] { redisKey },
            values: new RedisValue[] { now, windowStart, limit });

        return (long)result == 1;
    }
}
```

### Kong API Gateway Rate Limiting

```yaml
# Kong rate limiting plugin
# ✅ Rate limiting en gateway layer (antes de llegar a services)

# Global rate limit
plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 5000
      policy: redis
      redis_host: redis.talma.internal
      redis_port: 6379
      redis_database: 0
      fault_tolerant: true # ✅ Continuar si Redis falla
      hide_client_headers: false # ✅ Exponer X-RateLimit-* headers

# Per-consumer rate limit
consumers:
  - username: premium-user
    plugins:
      - name: rate-limiting
        config:
          minute: 1000 # ✅ Límite más alto para premium
          hour: 50000
          policy: redis

  - username: free-user
    plugins:
      - name: rate-limiting
        config:
          minute: 50 # ✅ Límite bajo para free tier
          hour: 1000
          policy: redis

# ✅ Response headers
# X-RateLimit-Limit-Minute: 100
# X-RateLimit-Remaining-Minute: 45
# X-RateLimit-Reset: 1699999999
```

### Rate Limiting por Tenant (Multi-tenancy)

```csharp
// ✅ Diferentes límites por tenant
builder.Services.AddRateLimiter(options =>
{
    options.AddPolicy("tenant-aware", context =>
    {
        // ✅ Extraer tenant de header/claim
        var tenantId = context.Request.Headers["X-Tenant-ID"].FirstOrDefault()
            ?? context.User.FindFirst("tenant_id")?.Value
            ?? "default";

        // ✅ Configuración por tenant desde appsettings
        var config = context.RequestServices
            .GetRequiredService<IConfiguration>()
            .GetSection($"RateLimits:Tenants:{tenantId}")
            .Get<TenantRateLimitConfig>()
            ?? new TenantRateLimitConfig { PermitLimit = 100, WindowMinutes = 1 };

        return RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: $"tenant:{tenantId}",
            factory: _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = config.PermitLimit,
                Window = TimeSpan.FromMinutes(config.WindowMinutes),
                QueueLimit = 0
            });
    });
});

// appsettings.json
{
  "RateLimits": {
    "Tenants": {
      "talma-peru": {
        "PermitLimit": 500,
        "WindowMinutes": 1
      },
      "talma-chile": {
        "PermitLimit": 300,
        "WindowMinutes": 1
      },
      "default": {
        "PermitLimit": 100,
        "WindowMinutes": 1
      }
    }
  }
}
```

### Métricas y Monitoreo

```csharp
public class RateLimitingMetrics
{
    private readonly Counter<long> _requestsRejected;
    private readonly Counter<long> _requestsAllowed;
    private readonly Histogram<double> _queueWaitTime;

    public RateLimitingMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("Talma.RateLimiting");

        _requestsRejected = meter.CreateCounter<long>(
            "ratelimit.requests.rejected", "requests",
            "Rate limit rejected requests");

        _requestsAllowed = meter.CreateCounter<long>(
            "ratelimit.requests.allowed", "requests",
            "Rate limit allowed requests");

        _queueWaitTime = meter.CreateHistogram<double>(
            "ratelimit.queue_wait_time", "ms",
            "Time spent waiting in rate limit queue");
    }

    public void RecordRejected(string policy, string partition)
    {
        _requestsRejected.Add(1,
            new KeyValuePair<string, object?>("policy", policy),
            new KeyValuePair<string, object?>("partition", partition));
    }

    public void RecordAllowed(string policy, string partition)
    {
        _requestsAllowed.Add(1,
            new KeyValuePair<string, object?>("policy", policy),
            new KeyValuePair<string, object?>("partition", partition));
    }
}

// PromQL queries
/*
# Rejection rate por policy
rate(ratelimit_requests_rejected_total{policy="expensive"}[5m])

# % de requests rechazados
rate(ratelimit_requests_rejected_total[5m]) /
  (rate(ratelimit_requests_rejected_total[5m]) + rate(ratelimit_requests_allowed_total[5m])) * 100

# Queue wait time P95
histogram_quantile(0.95, sum(rate(ratelimit_queue_wait_time_bucket[5m])) by (le, policy))
*/
```

### Terraform - ALB Rate Limiting

```hcl
# ✅ Rate limiting en ALB (AWS WAF)
resource "aws_wafv2_web_acl" "api_waf" {
  name  = "orders-api-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  # ✅ Rate limit rule
  rule {
    name     = "rate-limit-rule"
    priority = 1

    action {
      block {
        custom_response {
          response_code = 429
          custom_response_body_key = "rate_limit_exceeded"
        }
      }
    }

    statement {
      rate_based_statement {
        limit              = 2000  # ✅ 2000 requests per 5 min
        aggregate_key_type = "IP"

        # ✅ Aplicar solo a rutas específicas
        scope_down_statement {
          byte_match_statement {
            field_to_match {
              uri_path {}
            }
            positional_constraint = "STARTS_WITH"
            search_string         = "/api/"
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "OrdersApiWAF"
    sampled_requests_enabled   = true
  }
}

# ✅ Asociar WAF con ALB
resource "aws_wafv2_web_acl_association" "api_alb" {
  resource_arn = aws_lb.api.arn
  web_acl_arn  = aws_wafv2_web_acl.api_waf.arn
}

# Custom response body
resource "aws_wafv2_web_acl" "api_waf" {
  # ... previous config ...

  custom_response_body {
    key          = "rate_limit_exceeded"
    content      = jsonencode({
      error   = "too_many_requests"
      message = "Rate limit exceeded. Please try again later."
    })
    content_type = "APPLICATION_JSON"
  }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar rate limiting en APIs públicas
- **MUST** usar algoritmo apropiado (fixed window mínimo)
- **MUST** retornar HTTP 429 Too Many Requests
- **MUST** incluir `Retry-After` header en respuestas 429
- **MUST** incluir headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **MUST** usar rate limiting distribuido para múltiples instancias (Redis)
- **MUST** particionar por usuario/API key/IP según caso
- **MUST** monitorear rejection rate

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar rate limiting en API Gateway (Kong/AWS WAF)
- **SHOULD** usar sliding window para mayor precisión
- **SHOULD** configurar diferentes límites por tier/plan
- **SHOULD** usar token bucket para permitir bursts
- **SHOULD** implementar graceful degradation cuando Redis falla
- **SHOULD** exponer métricas de rate limiting
- **SHOULD** configurar alarmas cuando rejection rate > 5%

### MAY (Opcional)

- **MAY** implementar rate limiting adaptativo basado en load
- **MAY** usar priorización de requests en queue
- **MAY** implementar rate limiting por endpoint específico
- **MAY** permitir burst allowance para usuarios premium

### MUST NOT (Prohibido)

- **MUST NOT** implementar rate limiting sin monitoreo
- **MUST NOT** usar in-memory rate limiting para multi-instance deployments
- **MUST NOT** omitir headers de rate limiting en responses
- **MUST NOT** configurar límites sin justificación técnica
- **MUST NOT** bloquear permanentemente por exceder rate limit
- **MUST NOT** aplicar rate limiting a health check endpoints

---

## Referencias

- [Lineamiento: Resiliencia y Disponibilidad](../../lineamientos/arquitectura/04-resiliencia-y-disponibilidad.md)
- Estándares relacionados:
  - [Bulkhead Pattern](bulkhead-pattern.md)
  - [Circuit Breaker](circuit-breaker.md)
- Especificaciones:
  - [ASP.NET Core Rate Limiting](https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit)
  - [Kong Rate Limiting Plugin](https://docs.konghq.com/hub/kong-inc/rate-limiting/)
  - [AWS WAF Rate-Based Rules](https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based.html)
  - [RFC 6585 - HTTP 429](https://datatracker.ietf.org/doc/html/rfc6585#section-4)
