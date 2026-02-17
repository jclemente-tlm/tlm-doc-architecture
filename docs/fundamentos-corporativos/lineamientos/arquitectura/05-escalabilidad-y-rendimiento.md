---
id: escalabilidad-y-rendimiento
sidebar_position: 5
title: Escalabilidad y Rendimiento
description: Lineamientos para diseñar sistemas eficientes que manejen crecimiento de carga manteniendo tiempos de respuesta aceptables
tags: [lineamiento, arquitectura, escalabilidad, rendimiento, performance]
---

# Escalabilidad y Rendimiento

Los sistemas deben manejar crecimiento de carga sin degradación significativa del rendimiento. Sistemas que no escalan generan timeouts, pérdida de transacciones y experiencias frustrantes. La escalabilidad no es prematura optimización, sino diseño consciente de patrones que permitan crecimiento sostenible cuando sea necesario.

**Este lineamiento aplica a:** sistemas cloud-native, APIs públicas, aplicaciones con crecimiento proyectado, servicios de alto volumen transaccional.

**Este lineamiento NO aplica a:** sistemas internos de bajo volumen (< 100 usuarios), procesos batch sin restricciones de tiempo, herramientas administrativas de uso esporádico.

## Relación con Principios

Este lineamiento implementa aspectos de:

- [Resiliencia y Tolerancia a Fallos](../../principios/03-resiliencia-y-tolerancia-a-fallos.md): Sistemas resilientes bajo carga variable requieren escalabilidad
- [Modularidad y Bajo Acoplamiento](../../principios/02-modularidad-y-bajo-acoplamiento.md): Componentes independientes facilitan escalado selectivo

## Cuándo Aplicar Este Lineamiento

### ✅ Aplicar SI el Sistema

- Está desplegado en cloud (AWS, Azure, GCP)
- Tiene crecimiento de usuarios proyectado (> 50% anual)
- Maneja picos de carga predecibles (campañas, eventos)
- Es API pública o de integración crítica
- Tiene SLAs estrictos de tiempo de respuesta
- Procesa transacciones de alto volumen

### ❌ NO Aplicar SI el Sistema

- Es herramienta interna de < 50 usuarios estables
- Es proceso batch sin restricciones de tiempo real
- Es prototipo o MVP sin tracción validada
- Tiene crecimiento nulo o decreciente
- Opera en infraestructura fija sin elasticidad

## Estrategias de Escalabilidad

### 1. Escalado Horizontal (Scale Out)

Agregar más instancias del servicio para distribuir carga.

**Cuándo usar:**

- Servicios stateless
- Aplicaciones cloud-native
- Cargas variables o impredecibles

**Técnicas:**

- Despliegue de múltiples réplicas
- Load balancers (ALB, NLB)
- Auto-scaling basado en métricas (CPU, memoria, requests/sec)
- Contenedores orquestados (ECS, Kubernetes)

**Ejemplo con AWS ECS:**

```typescript
// task-definition.json
{
  "family": "notification-service",
  "cpu": "256",
  "memory": "512",
  "networkMode": "awsvpc",
  "containerDefinitions": [{
    "name": "api",
    "image": "notifications-api:latest",
    "portMappings": [{
      "containerPort": 8080,
      "protocol": "tcp"
    }],
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
      "interval": 30,
      "timeout": 5,
      "retries": 3
    }
  }]
}

// Auto-scaling configuration
{
  "serviceNamespace": "ecs",
  "resourceId": "service/notifications-cluster/notification-service",
  "scalableDimension": "ecs:service:DesiredCount",
  "minCapacity": 2,
  "maxCapacity": 10,
  "targetTrackingScalingPolicies": [{
    "targetValue": 70.0,
    "predefinedMetricType": "ECSServiceAverageCPUUtilization"
  }]
}
```

### 2. Escalado Vertical (Scale Up)

Aumentar recursos (CPU, memoria) de instancias existentes.

**Cuándo usar:**

- Workloads con estado persistente
- Bases de datos
- Optimización rápida temporal
- Límite tecnológico del escalado horizontal

**Consideraciones:**

- ⚠️ Tiene límites físicos
- ⚠️ Requiere reinicio (downtime)
- ⚠️ Más costoso que horizontal a largo plazo
- ✅ Más simple de implementar inicialmente

### 3. Caché Distribuido

Reducir carga en origen mediante almacenamiento temporal de datos frecuentes.

**Niveles de caché:**

1. **CDN (Content Delivery Network)**
   - Contenido estático (JS, CSS, imágenes)
   - Assets front-end
   - Archivos públicos

2. **Application Cache (Redis)**
   - Respuestas de APIs
   - Sesiones de usuario
   - Resultados de cálculos costosos
   - Datos de referencia

3. **Database Query Cache**
   - Resultados de consultas frecuentes
   - Agregaciones costosas

**Ejemplo con Redis:**

```csharp
public class NotificationService
{
    private readonly IDistributedCache _cache;
    private readonly INotificationRepository _repository;
    private readonly ILogger<NotificationService> _logger;

    public async Task<UserNotifications> GetUserNotificationsAsync(Guid userId)
    {
        var cacheKey = $"notifications:user:{userId}";

        // Intenta obtener del caché
        var cached = await _cache.GetStringAsync(cacheKey);
        if (cached != null)
        {
            _logger.LogDebug("Cache HIT for user {UserId}", userId);
            return JsonSerializer.Deserialize<UserNotifications>(cached);
        }

        _logger.LogDebug("Cache MISS for user {UserId}", userId);

        // Obtiene de base de datos
        var notifications = await _repository.GetByUserIdAsync(userId);

        // Guarda en caché por 5 minutos
        var options = new DistributedCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5)
        };

        await _cache.SetStringAsync(
            cacheKey,
            JsonSerializer.Serialize(notifications),
            options
        );

        return notifications;
    }
}
```

### 4. Sharding de Base de Datos

Particionar datos horizontalmente en múltiples bases de datos.

**Estrategias de sharding:**

- **Por rango**: Usuarios 1-1000 → Shard 1, 1001-2000 → Shard 2
- **Por hash**: `hash(userId) % num_shards`
- **Por geografía**: Región LATAM → Shard LATAM
- **Por tenant**: Cada cliente → Shard dedicado

**Consideraciones:**

- ⚠️ Complejidad operacional alta
- ⚠️ Queries cross-shard costosos
- ⚠️ Re-sharding es complejo
- ✅ Evitar hasta que sea crítico (> 10M registros o > 1TB)

### 5. Asincronía y Procesamiento en Background

Mover operaciones costosas fuera del request-response.

**Patrones:**

```csharp
// ❌ Síncrono - bloquea el request
[HttpPost("send")]
public async Task<IActionResult> SendNotification([FromBody] NotificationRequest request)
{
    // Esto puede tardar 2-5 segundos
    await _emailService.SendAsync(request.Email);
    await _smsService.SendAsync(request.Phone);
    await _pushService.SendAsync(request.DeviceId);

    return Ok(); // Usuario espera 5 segundos
}

// ✅ Asíncrono - respuesta inmediata
[HttpPost("send")]
public async Task<IActionResult> SendNotification([FromBody] NotificationRequest request)
{
    // Publica evento a cola Kafka
    await _eventBus.PublishAsync(new NotificationRequested
    {
        Email = request.Email,
        Phone = request.Phone,
        DeviceId = request.DeviceId
    });

    return Accepted(); // Usuario recibe respuesta en < 100ms
}

// Consumer procesa en background
public class NotificationConsumer : IEventConsumer<NotificationRequested>
{
    public async Task ConsumeAsync(NotificationRequested evt)
    {
        // Procesa sin bloquear usuario
        await _emailService.SendAsync(evt.Email);
        await _smsService.SendAsync(evt.Phone);
        await _pushService.SendAsync(evt.DeviceId);
    }
}
```

## Optimización de Rendimiento

### 1. Optimización de Consultas

```sql
-- ❌ Consulta no optimizada
SELECT * FROM Notifications
WHERE UserId = '123'
  AND Status IN ('Pending', 'Sent')
ORDER BY CreatedAt DESC;

-- ✅ Consulta optimizada
-- 1. Índice compuesto: (UserId, Status, CreatedAt DESC)
-- 2. SELECT solo columnas necesarias
-- 3. LIMIT para paginación
SELECT Id, Title, Message, CreatedAt, Status
FROM Notifications
WHERE UserId = '123'
  AND Status IN ('Pending', 'Sent')
ORDER BY CreatedAt DESC
LIMIT 20 OFFSET 0;
```

### 2. Lazy Loading y Paginación

```csharp
// ❌ Carga todos los datos
public async Task<List<Notification>> GetAllNotifications()
{
    return await _context.Notifications
        .Include(n => n.User)
        .Include(n => n.Template)
        .Include(n => n.Attachments)
        .ToListAsync(); // Puede ser 10,000+ registros
}

// ✅ Paginación y carga selectiva
public async Task<PagedResult<NotificationDto>> GetNotifications(
    int page = 1,
    int pageSize = 20)
{
    var query = _context.Notifications
        .Where(n => n.Status != NotificationStatus.Deleted)
        .OrderByDescending(n => n.CreatedAt);

    var total = await query.CountAsync();

    var notifications = await query
        .Skip((page - 1) * pageSize)
        .Take(pageSize)
        .Select(n => new NotificationDto // Projection
        {
            Id = n.Id,
            Title = n.Title,
            CreatedAt = n.CreatedAt
            // Solo campos necesarios
        })
        .ToListAsync();

    return new PagedResult<NotificationDto>
    {
        Items = notifications,
        TotalCount = total,
        Page = page,
        PageSize = pageSize
    };
}
```

### 3. Connection Pooling

```csharp
// ✅ Connection string con pooling
"Server=db.example.com;Database=notifications;
 User Id=app;Password=***;
 Pooling=true;
 Min Pool Size=5;
 Max Pool Size=100;
 Connection Lifetime=0;
 Connection Timeout=30;"
```

## Métricas y Monitoreo

### Métricas Clave (Golden Signals)

1. **Latencia**: Tiempo de respuesta (P50, P95, P99)
2. **Tráfico**: Requests por segundo
3. **Errores**: Tasa de error (%)
4. **Saturación**: Uso de CPU, memoria, connections

### Umbrales Recomendados

| Métrica          | Umbral Objetivo | Umbral Crítico | Acción               |
| ---------------- | --------------- | -------------- | -------------------- |
| P95 Latencia API | < 500ms         | > 2s           | Investigar + escalar |
| Tasa de error    | < 0.1%          | > 1%           | Alerta inmediata     |
| CPU utilization  | < 70%           | > 85%          | Auto-scale trigger   |
| Memory usage     | < 80%           | > 90%          | Scale up/out         |

## Estándares Relacionados

- [Patrones de Resiliencia](../../estandares/arquitectura/resilience-patterns.md)
- [Observabilidad](../../estandares/observabilidad/observability.md)
- [Kafka para Mensajería](../../estandares/mensajeria/kafka-messaging.md)

## Referencias

### Frameworks de Industria

- [AWS Well-Architected - Performance Efficiency Pillar](https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/welcome.html)
- [Azure Well-Architected - Performance Efficiency](https://learn.microsoft.com/azure/well-architected/performance-efficiency/)
- [Google SRE - Performance](https://sre.google/sre-book/table-of-contents/)

### Lineamientos Relacionados

- [Resiliencia y Disponibilidad](04-resiliencia-y-disponibilidad.md)
- [Observabilidad](05-observabilidad.md)
- [Cloud Native](03-cloud-native.md)

### ADRs de Talma

- [ADR-007: AWS ECS Fargate para Contenedores](../../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- [ADR-011: Redis para Caché Distribuido](../../../decisiones-de-arquitectura/adr-011-redis-cache-distribuido.md)
- [ADR-010: PostgreSQL como Base de Datos](../../../decisiones-de-arquitectura/adr-010-postgresql-base-datos.md)
- [ADR-012: Kafka para Mensajería Asíncrona](../../../decisiones-de-arquitectura/adr-012-kafka-mensajeria-asincrona.md)

---

**Versión**: 1.0
**Última actualización**: 2026-02-11
**Estado**: Aprobado
