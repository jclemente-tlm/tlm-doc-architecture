# 10. Requisitos de calidad

## 10.1 Rendimiento

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| `Latencia` | `< 100ms p95` | `Prometheus` |
| `Throughput` | `10k requests/seg` | Load testing |
| `Disponibilidad` | `99.9%` | Health checks |
| `CPU` | `< 70% promedio` | Monitoreo |

## 10.2 Seguridad

| Aspecto | Requisito | Implementación |
|---------|-----------|----------------|
| `Autenticación` | JWT obligatorio | Middleware |
| `Rate limiting` | Por usuario/IP | Redis |
| `TLS` | 1.3 mínimo | Certificados |
| `Headers` | Security headers | Middleware |

## 10.3 Escalabilidad

| Aspecto | Objetivo | Estrategia |
|---------|----------|------------|
| `Horizontal` | Auto-scaling | ECS Fargate + Terraform |
| `Carga` | Load balancing | ALB |
| `Cache` | Redis distribuido | Clustering |
| `Configuración` | Hot reload | Dinámico |

## 10.4 Atributos de calidad

| Atributo | Métrica | Objetivo | Crítico |
|----------|---------|----------|---------|
| `Latencia` | Tiempo de respuesta p95 | `< 100ms` | `< 200ms` |
| `Rendimiento` | Solicitudes/segundo | `> 5,000 RPS` | `> 2,000 RPS` |
| `Latencia de routing` | Tiempo interno de proxy | `< 5ms` | `< 10ms` |
| `Utilización de CPU` | Uso promedio de CPU | `< 70%` | `< 85%` |
| `Uso de memoria` | Uso promedio de memoria | `< 2GB` | `< 4GB` |

```json
// appsettings.Production.json (fragmento)
{
  "Rendimiento": {
    "ConnectionPooling": {
      "MaxConnectionsPerServer": 20,
      "PooledConnectionLifetime": "00:02:00",
      "ConnectionTimeout": "00:00:30"
    },
    "Caching": {
      "DefaultTTL": "00:05:00",
      "MaxCacheSize": "100MB",
      "EvictionPolicy": "LRU"
    },
    "RateLimiting": {
      "WindowSize": "00:01:00",
      "SlidingWindowSegments": 10
    }
  }
}
```

## 10.5 Disponibilidad

| Componente | SLA | Downtime máximo/mes | RPO | RTO |
|------------|-----|--------------------|-----|-----|
| `API Gateway` | 99.9% | 43.2 minutos | 0 | 30 segundos |
| `YARP Proxy` | 99.95% | 21.6 minutos | 0 | 15 segundos |
| `Health Checks` | 99.99% | 4.32 minutos | 0 | 5 segundos |

```csharp
// Configuración de verificaciones de salud para alta disponibilidad
public void ConfigureServices(IServiceCollection services)
{
    services.AddHealthChecks()
        .AddCheck("gateway-ready", () =>
        {
            // Verificar componentes críticos
            var checks = new[]
            {
                CheckYarpConfiguration(),
                CheckRedisConnection(),
                CheckIdentityService(),
                CheckMemoryUsage(),
                CheckDiskSpace()
            };

            return checks.All(c => c)
                ? HealthCheckResult.Healthy("All systems operational")
                : HealthCheckResult.Degraded("Some systems degraded");
        })
        .AddCheck("detailed-diagnostics", () =>
        {
            var diagnostics = new Dictionary<string, object>
            {
                ["uptime"] = DateTime.UtcNow - _startTime,
                ["requests_processed"] = _metricsCollector.TotalRequests,
                ["active_connections"] = _connectionManager.ActiveConnections,
                ["circuit_breakers"] = _circuitBreakerService.GetStatus(),
                ["cache_hit_ratio"] = _cacheService.GetHitRatio()
            };

            return HealthCheckResult.Healthy("Detailed diagnostics", diagnostics);
        });
}
```

## 10.6 Escalabilidad

| Dimensión | Capacidad actual | Capacidad objetivo | Estrategia |
|-----------|------------------|-------------------|------------|
| `Solicitudes concurrentes` | 1,000 | 10,000 | Escalado horizontal |
| `Servicios backend` | 10 | 50+ | Enrutamiento dinámico |
| `Tenants` | 100 | 1,000+ | Multi-tenant architecture |
| `Regiones` | 1 | 3+ | Multi-region deployment |

## 10.7 Seguridad

| Área | Requisito | Implementación | Verificación |
|------|-----------|---------------|-------------|
| `Autenticación` | OAuth2/OIDC + JWT | Identity Service integration | Token validation tests |
| `Autorización` | RBAC por tenant | Claims-based policies | Policy unit tests |
| `Encriptación` | TLS 1.3 en tránsito | HTTPS everywhere | SSL Labs A+ rating |
| `Headers de seguridad` | OWASP compliance | Security middleware | Security scan tools |
| `Rate limiting` | Prevenir DDoS | Distributed rate limiter | Testing de carga |

## 10.8 Escenarios de calidad

### 10.8.1 Rendimiento bajo carga

```gherkin
Feature: Rendimiento bajo alta carga
  Como operador del sistema
  Quiero que el API Gateway mantenga rendimiento aceptable bajo carga alta
  Para garantizar experiencia de usuario consistente

Scenario: Handling peak traffic
  Given el API Gateway está desplegado con 3 instancias
  And hay 50 servicios backend registrados
  When se reciben 5,000 requests por segundo durante 10 minutos
  Then el tiempo de respuesta p95 debe ser menor a 100ms
  And el CPU usage promedio debe ser menor al 70%
  And no debe haber errores 5xx por sobrecarga
  And todas las instancias deben permanecer healthy
```

### 10.8.2 Resiliencia ante fallos

```gherkin
Feature: Resiliencia ante fallos de servicios
  Como operador del sistema
  Quiero que el API Gateway maneje fallos de servicios gracefully
  Para mantener disponibilidad de servicios funcionando

Scenario: Backend service failure
  Given el API Gateway está rutando a 10 servicios backend
  And uno de los servicios backend falla completamente
  When se reciben requests para el servicio fallido
  Then el circuit breaker debe abrirse en menos de 30 segundos
  And los requests deben devolver error 503 inmediatamente
  And los otros servicios deben funcionar normalmente
  And las métricas deben registrar el fallo correctamente

Scenario: Partial service degradation
  Given un servicio backend responde con alta latencia (>5 segundos)
  When se reciben múltiples requests para ese servicio
  Then el timeout debe activarse a los 30 segundos
  And las retry policies deben activarse
  And después de 3 fallos consecutivos debe activarse circuit breaker
  And el servicio debe recuperarse automáticamente cuando mejore
```

### 10.8.3 Seguridad

```gherkin
Feature: Protección contra ataques
  Como administrador de seguridad
  Quiero que el API Gateway proteja contra ataques comunes
  Para mantener la seguridad del sistema

Scenario: Rate limiting protection
  Given un cliente con límite de 100 requests/minuto
  When envía 150 requests en 1 minuto
  Then los primeros 100 requests deben procesarse normalmente
  And los siguientes 50 requests deben recibir HTTP 429
  And el rate limit debe resetear después de 1 minuto
  And debe registrarse el evento en logs de seguridad

Scenario: JWT token validation
  Given un request con JWT token expirado
  When llega al API Gateway
  Then debe rechazarse con HTTP 401
  And debe loggearse el intento de acceso no autorizado
  And no debe forwarding al servicio backend
```

## 10.9 Métricas y monitoreo

- KPIs y métricas expuestas vía `Prometheus` y visualizadas en `Grafana`.
- Alertas automáticas configuradas en `Prometheus` para disponibilidad, latencia, errores y uso de recursos.
- Dashboards de calidad y salud en `Grafana`.

```csharp
public class ApiGatewayMetrics
{
    private readonly IMetrics _metrics;

    // Métricas de negocio
    public void RecordBusinessMetrics(HttpContext context, TimeSpan duration)
    {
        var tags = new TagList
        {
            ["tenant_id"] = context.Items["TenantId"]?.ToString(),
            ["service"] = GetTargetService(context),
            ["method"] = context.Request.Method,
            ["status_class"] = GetStatusClass(context.Response.StatusCode)
        };

        // KPIs principales
        _metrics.Counter("api_gateway_requests_total").Add(1, tags);
        _metrics.Histogram("api_gateway_request_duration_seconds").Record(duration.TotalSeconds, tags);
        _metrics.Counter("api_gateway_bytes_transferred_total").Add(GetResponseSize(context), tags);

        // Métricas de calidad de servicio
        if (duration.TotalMilliseconds > 100)
        {
            _metrics.Counter("api_gateway_slow_requests_total").Add(1, tags);
        }

        if (context.Response.StatusCode >= 500)
        {
            _metrics.Counter("api_gateway_server_errors_total").Add(1, tags);
        }
    }

    // Métricas de infraestructura
    public void RecordInfrastructureMetrics()
    {
        var process = Process.GetCurrentProcess();

        _metrics.Gauge("api_gateway_memory_usage_bytes").Set(process.WorkingSet64);
        _metrics.Gauge("api_gateway_cpu_usage_percent").Set(GetCpuUsage());
        _metrics.Gauge("api_gateway_active_connections").Set(_connectionManager.ActiveConnections);
        _metrics.Gauge("api_gateway_thread_pool_available").Set(ThreadPool.ThreadCount);
    }

    // Métricas de circuit breakers
    public void RecordCircuitBreakerMetrics(string serviceName, CircuitState state)
    {
        var tags = new TagList { ["service"] = serviceName, ["state"] = state.ToString() };
        _metrics.Gauge("api_gateway_circuit_breaker_state").Set((int)state, tags);
    }
}
```

```yaml
# Configuración de alertas en Prometheus
groups:
- name: api-gateway-alerts
  rules:
  # Disponibilidad
  - alert: ApiGatewayDown
    expr: up{job="api-gateway"} == 0
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "API Gateway instance is down"
      description: "API Gateway instance {{ $labels.instance }} has been down for more than 30 seconds"

  # Performance
  - alert: HighLatency
    expr: histogram_quantile(0.95, api_gateway_request_duration_seconds_bucket) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High request latency detected"
      description: "95th percentile latency is {{ $value }}s for the last 5 minutes"

  - alert: HighErrorRate
    expr: rate(api_gateway_server_errors_total[5m]) / rate(api_gateway_requests_total[5m]) > 0.01
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }} for the last 5 minutes"

  # Circuit Breakers
  - alert: CircuitBreakerOpen
    expr: api_gateway_circuit_breaker_state == 2
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Circuit breaker opened for service {{ $labels.service }}"
      description: "Service {{ $labels.service }} circuit breaker has been open for more than 1 minute"

  # Limitación de Velocidad
  - alert: HighRateLimitHitRate
    expr: rate(api_gateway_rate_limit_exceeded_total[5m]) / rate(api_gateway_requests_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High rate limit hit rate"
      description: "Rate limit hit rate is {{ $value | humanizePercentage }} for the last 5 minutes"

  # Infrastructure
  - alert: HighMemoryUsage
    expr: api_gateway_memory_usage_bytes / (4 * 1024 * 1024 * 1024) > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage is {{ $value | humanizePercentage }} of 4GB limit"

  - alert: HighCpuUsage
    expr: api_gateway_cpu_usage_percent > 80
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage is {{ $value }}% for the last 10 minutes"
```

## 10.10 Pruebas de calidad

- Pruebas de carga automatizadas (`k6`) para validar rendimiento y escalabilidad.
- Pruebas de caos (`Polly`, simulación de fallos) para validar resiliencia.

```javascript
// K6 script para pruebas de carga
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 100 },    // Ramp up
    { duration: '5m', target: 100 },    // Stay at 100 users
    { duration: '2m', target: 200 },    // Ramp up to 200 users
    { duration: '5m', target: 200 },    // Stay at 200 users
    { duration: '2m', target: 500 },    // Ramp up to 500 users
    { duration: '5m', target: 500 },    // Stay at 500 users
    { duration: '2m', target: 0 },      // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<100'],    // 95% of requests under 100ms
    http_req_failed: ['rate<0.01'],      // Error rate under 1%
    errors: ['rate<0.01'],
  },
};

export default function() {
  const params = {
    headers: {
      'Authorization': 'Bearer ' + getJwtToken(),
      'Content-Type': 'application/json',
      'X-Tenant-ID': 'test-tenant',
    },
  };

  // Test different endpoints
  const endpoints = [
    '/api/notifications/templates',
    '/api/track-trace/shipments',
    '/api/identity/users/profile',
    '/api/sita-messaging/status'
  ];

  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const response = http.get(`https://api-gateway.corporate-services.local${endpoint}`, params);

  const result = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 100ms': (r) => r.timings.duration < 100,
    'response has content': (r) => r.body.length > 0,
  });

  errorRate.add(!result);
  sleep(1);
}

function getJwtToken() {
  // Mock JWT token generation
  return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
}
```

```csharp
// Pruebas de caos usando Polly
public class ChaosEngineeringTests
{
    [Test]
    public async Task ApiGateway_ShouldHandleRandomServiceFailures()
    {
        // Configurar caos en servicios backend aleatoriamente
        var chaosPolicy = MonkeyPolicy.InjectFaultAsync(with =>
            with.Fault(new HttpRequestException("Simulated service failure"))
                .InjectionRate(0.1) // 10% de requests fallan
                .Enabled());

        var httpClient = _factory.CreateClient();
        httpClient.AddPolicy(chaosPolicy);

        var tasks = Enumerable.Range(0, 1000)
            .Select(async _ =>
            {
                try
                {
                    var response = await httpClient.GetAsync("/api/notifications/templates");
                    return response.IsSuccessStatusCode;
                }
                catch
                {
                    return false;
                }
            });

        var results = await Task.WhenAll(tasks);
        var successRate = results.Count(r => r) / (double)results.Length;

        // Debe mantener al menos 90% de éxito a pesar del caos
        Assert.That(successRate, Is.GreaterThan(0.9));
    }

    [Test]
    public async Task ApiGateway_ShouldRecoverFromNetworkPartition()
    {
        // Simular partición de red
        _testServer.SimulateNetworkPartition(TimeSpan.FromMinutes(1));

        var httpClient = _factory.CreateClient();

        // Requests durante la partición deben fallar rápidamente
        var response1 = await httpClient.GetAsync("/api/health/ready");
        Assert.That(response1.StatusCode, Is.EqualTo(HttpStatusCode.ServiceUnavailable));

        // Esperar recuperación
        await Task.Delay(TimeSpan.FromMinutes(1.5));

        // Después de la recuperación debe funcionar normalmente
        var response2 = await httpClient.GetAsync("/api/health/ready");
        Assert.That(response2.StatusCode, Is.EqualTo(HttpStatusCode.OK));
    }
}
```

---

> Todos los requisitos de calidad están alineados a los ADRs, modelos C4/Structurizr DSL y cumplen con los objetivos de rendimiento, seguridad, disponibilidad y escalabilidad definidos para el API Gateway.
