# 9. Decisiones de arquitectura

## 9.1 Decisiones principales

| ADR | Decisión | Estado | Justificación |
|-----|----------|--------|---------------|
| **ADR-001** | CQRS + Event Sourcing | Aceptado | Trazabilidad inmutable |
| **ADR-002** | PostgreSQL event store | Aceptado | Simplicidad inicial |
| **ADR-003** | Deduplicación por tenant | Aceptado | Prevención duplicados |
| **ADR-004** | Event-driven propagación | Aceptado | Integración SITA |

## 9.2 Alternativas evaluadas

| Componente | Alternativas | Selección | Razón |
|------------|-------------|-----------|--------|
| **Event Store** | EventStore, PostgreSQL, SNS+SQS | PostgreSQL | Simplicidad |
| **API** | REST, GraphQL, gRPC | REST + GraphQL | Flexibilidad |
| **Deduplicación** | Global, Por tenant | Por tenant | Aislamiento |
| **Propagación** | Síncrona, Asíncrona | Asíncrona | Desacoplamiento |

## 9.1 ADR-001: Event Sourcing como patrón principal

**Estado**: Aceptado
**Fecha**: 2024-01-15
**Decidido por**: Equipo de Arquitectura

### Contexto
El servicio Track & Trace requiere trazabilidad completa de eventos operacionales con capacidades de auditoría robustas y análisis temporal de patrones.

### Alternativas consideradas
1. **CRUD tradicional con audit log**: Base de datos relacional con tabla de auditoría
2. **Event Sourcing**: Almacenamiento de eventos como única fuente de verdad
3. **Hybrid approach**: CRUD principal + Event log secundario

### Decisión
Adoptamos **Event Sourcing** como patrón arquitectónico principal.

### Justificación
- **Auditoría completa**: Cumplimiento con regulaciones que requieren trazabilidad total
- **Análisis temporal**: Capacidad de reconstruir estado en cualquier momento
- **Escalabilidad de lectura**: Read models especializados para diferentes vistas
- **Debugging avanzado**: Replay de eventos para reproducir problemas
- **Analytics nativo**: Stream de eventos ideal para análisis en tiempo real

### Consecuencias
- **Positivas**: Auditabilidad, escalabilidad, flexibilidad analítica
- **Negativas**: Complejidad inicial, curva de aprendizaje, eventual consistency
- **Mitigación**: Training del equipo, herramientas de debugging robustas

---

## 9.2 ADR-002: PostgreSQL como Event Store

**Estado**: Aceptado
**Fecha**: 2024-01-20
**Decidido por**: Equipo de Arquitectura

### Contexto
Necesidad de un almacén confiable y performante para eventos con soporte ACID y capacidades de consulta avanzadas.

### Alternativas consideradas
1. **PostgreSQL**: Base relacional con soporte JSONB, estrategia inicial
2. **SNS+SQS**: Escalabilidad managed AWS para volúmenes medios
3. **RabbitMQ/Amazon MQ**: Event streaming robusto para alto volumen
4. **Event Store DB**: Base especializada en event sourcing (evaluación futura)

### Justificación
- **ACID compliance**: Transacciones consistentes para eventos críticos
- **JSONB support**: Flexibilidad para esquemas de eventos evolutivos
- **Performance**: Índices GIN para consultas JSONB eficientes
- **Operaciones**: Expertise existente del equipo en PostgreSQL
- **Costos**: Licencia open source vs soluciones comerciales
- **Ecosystem**: Tooling maduro para backup, replicación, monitoring

### Implementación
```sql
-- Optimized event store schema
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL,
    version BIGINT NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    tenant_id VARCHAR(50) NOT NULL,

    CONSTRAINT events_stream_version_unique UNIQUE (stream_id, version)
);

-- Performance indexes
CREATE INDEX CONCURRENTLY idx_events_stream_id ON events (stream_id);
CREATE INDEX CONCURRENTLY idx_events_timestamp ON events (timestamp);
CREATE INDEX CONCURRENTLY idx_events_type ON events (event_type);
CREATE INDEX CONCURRENTLY idx_events_tenant ON events (tenant_id);

-- JSONB indexes for event data queries
CREATE INDEX CONCURRENTLY idx_events_data_gin ON events USING GIN (event_data);
```

### Consecuencias
- **Positivas**: Confiabilidad, performance, conocimiento del equipo
- **Negativas**: Complejidad para sharding futuro, gestión de crecimiento
- **Mitigación**: Particionamento por fecha, archiving strategy, read replicas

---

## 9.3 ADR-003: CQRS con Read Models especializados

**Estado**: Aceptado
**Fecha**: 2024-01-25
**Decidido por**: Equipo de Arquitectura

### Contexto
Optimización de consultas complejas y diferentes vistas de datos para casos de uso específicos como analytics y reporting.

### Alternativas consideradas
1. **Consultas directas al Event Store**: Sin read models
2. **Vista materializada única**: Single read model genérico
3. **Read models especializados**: Proyecciones por caso de uso
4. **Elasticsearch**: Search engine como read store

### Decisión
Implementamos **CQRS con read models especializados** usando PostgreSQL y Redis.

### Justificación
- **Performance**: Optimización específica por caso de uso
- **Escalabilidad**: Read models independientes
- **Flexibilidad**: Nuevas vistas sin impactar existentes
- **Analytics**: Agregaciones pre-calculadas
- **User Experience**: Respuestas instantáneas para consultas complejas

### Implementación
```csharp
// Timeline read model para trazabilidad
public class TimelineReadModel
{
    public string EntityId { get; set; }
    public List<TimelineEvent> Events { get; set; }
    public DateTime LastUpdated { get; set; }
    public Dictionary<string, object> Aggregations { get; set; }
}

// Analytics read model para métricas
public class AnalyticsReadModel
{
    public string Period { get; set; }
    public int EventCount { get; set; }
    public TimeSpan AverageProcessingTime { get; set; }
    public Dictionary<string, int> EventTypeDistribution { get; set; }
}

// Projection engine
public class ProjectionManager
{
    public async Task HandleEventAsync(IDomainEvent @event)
    {
        var projections = _projectionRegistry.GetProjectionsForEvent(@event.GetType());

        foreach (var projection in projections)
        {
            await projection.HandleAsync(@event);
            await _readModelStore.SaveAsync(projection);
        }
    }
}
```

### Consecuencias
- **Positivas**: Performance excelente, flexibilidad, escalabilidad
- **Negativas**: Complejidad adicional, eventual consistency
- **Mitigación**: Health checks de projections, rebuild automático

---



---

## 9.6 ADR-006: Multi-tenant schema separation

**Estado**: Aceptado
**Fecha**: 2024-02-10
**Decidido por**: Equipo de Arquitectura + Security

### Contexto
Aislamiento completo de datos entre tenants para compliance y security, con diferentes niveles de servicio por cliente.

### Alternativas consideradas
1. **Single schema con tenant_id**: Row-level security
2. **Schema per tenant**: Separación a nivel de schema
3. **Database per tenant**: Base de datos dedicada por tenant
4. **Service per tenant**: Instancia de servicio dedicada

### Decisión
Implementamos **Schema per tenant** en PostgreSQL con tenant context injection.

### Justificación
- **Aislamiento**: Separación física de datos garantizada
- **Performance**: Índices y optimizaciones específicas por tenant
- **Compliance**: Cumplimiento con regulaciones de aislamiento de datos
- **Backup**: Estrategias diferenciadas por criticidad del cliente
- **Scaling**: Facilita sharding futuro por tenant
- **Cost-effectiveness**: Balance entre aislamiento y recursos

### Implementación
```sql
-- Dynamic schema creation script
CREATE SCHEMA IF NOT EXISTS tenant_${tenantId};

-- Tenant-specific event table
CREATE TABLE tenant_${tenantId}.events (
    stream_id VARCHAR(255) NOT NULL,
    version BIGINT NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (stream_id, version)
);

-- Tenant-specific read model tables
CREATE TABLE tenant_${tenantId}.timeline_view (
    entity_id VARCHAR(255) PRIMARY KEY,
    timeline_data JSONB NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Optimized indexes per tenant
CREATE INDEX idx_events_timestamp ON tenant_${tenantId}.events(timestamp);
CREATE INDEX idx_events_type ON tenant_${tenantId}.events(event_type);
CREATE INDEX idx_timeline_updated ON tenant_${tenantId}.timeline_view(last_updated);
```

```csharp
// Tenant context injection
public class TenantAwareDbContext : DbContext
{
    private readonly ITenantContext _tenantContext;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var schema = $"tenant_{_tenantContext.TenantId}";

        modelBuilder.Entity<Event>().ToTable("events", schema);
        modelBuilder.Entity<TimelineView>().ToTable("timeline_view", schema);

        base.OnModelCreating(modelBuilder);
    }
}

// Tenant middleware
public class TenantResolutionMiddleware
{
    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        var tenantId = ExtractTenantId(context);

        if (string.IsNullOrEmpty(tenantId))
        {
            context.Response.StatusCode = 400;
            await context.Response.WriteAsync("Tenant ID required");
            return;
        }

        context.Items["TenantId"] = tenantId;
        await next(context);
    }
}
```

### Consecuencias
- **Positivas**: Aislamiento total, performance optimizada, compliance
- **Negativas**: Gestión compleja de schemas, migraciones complejas
- **Mitigación**: Automatización de setup, scripts de migración versionados

---

## 9.7 ADR-007: Observabilidad con OpenTelemetry

**Estado**: Aceptado
**Fecha**: 2024-02-15
**Decidido por**: Equipo de Arquitectura + SRE

### Contexto
Necesidad de observabilidad completa en arquitectura distribuida con correlación de eventos entre servicios.

### Alternativas consideradas
1. **Application Insights**: Azure native monitoring
2. **Datadog**: Comprehensive monitoring platform
3. **OpenTelemetry + ELK**: Open source stack
4. **Prometheus + Grafana**: Metrics-focused approach

### Decisión
Adoptamos **OpenTelemetry** con Jaeger, Prometheus y ELK stack.

### Justificación
- **Vendor neutrality**: Estándar abierto, sin lock-in
- **Comprehensive**: Traces, metrics, logs unified
- **Correlation**: Distributed tracing con correlation IDs
- **Ecosystem**: Compatible con múltiples backends
- **Future-proof**: Estándar en evolución de CNCF

### Implementación
```csharp
// OpenTelemetry configuration
services.AddOpenTelemetry()
    .WithTracing(builder =>
    {
        builder
            .AddSource("TrackTrace")
            .SetSampler(new AlwaysOnSampler())
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddNpgsqlInstrumentation()
            .AddJaegerExporter();
    })
    .WithMetrics(builder =>
    {
        builder
            .AddMeter("TrackTrace")
            .AddAspNetCoreInstrumentation()
            .AddPrometheusExporter();
    });

// Custom activity source
private static readonly ActivitySource ActivitySource = new("TrackTrace");

public async Task<T> ProcessEventWithTracing<T>(IDomainEvent @event, Func<Task<T>> handler)
{
    using var activity = ActivitySource.StartActivity($"process-{@event.GetType().Name}");
    activity?.SetTag("event.type", @event.GetType().Name);
    activity?.SetTag("event.stream", @event.StreamId);
    activity?.SetTag("tenant.id", @event.TenantId);

    try
    {
        return await handler();
    }
    catch (Exception ex)
    {
        activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
        throw;
    }
}
```

### Consecuencias
- **Positivas**: Observabilidad completa, debugging eficiente, performance insights
- **Negativas**: Overhead de instrumentación, complejidad de setup
- **Mitigación**: Sampling inteligente, monitoring de overhead

---

## 9.8 Resumen de decisiones

| ADR | Decisión | Impacto | Estado | Riesgo |
|-----|----------|---------|---------|---------|
| 001 | Event Sourcing | 🔴 Alto - Arquitectura fundamental | ✅ Implementado | Bajo |
| 002 | PostgreSQL Event Store | 🔴 Alto - Storage principal | ✅ Implementado | Bajo |
| 003 | CQRS Read Models | 🟡 Medio - Performance | ✅ Implementado | Bajo |
| 004 | Kafka Streaming | 🟡 Medio - Integration | ✅ Implementado | Medio |
| 005 | Redis Caching | 🟢 Bajo - Optimization | ✅ Implementado | Bajo |
| 006 | Multi-tenant Schema | 🔴 Alto - Security/Compliance | ✅ Implementado | Medio |
| 007 | OpenTelemetry | 🟡 Medio - Observability | 🚧 En progreso | Bajo |

## 9.9 Decisiones pendientes

### PND-001: Sharding strategy para escalamiento horizontal
**Contexto**: Crecimiento proyectado requiere distribución más allá de single instance
**Opciones bajo evaluación**:
- Shard por tenant (isolation benefits)
- Shard por tiempo (archiving natural)
- Shard por hash de entity (distribución uniforme)
**Criterios de decisión**: Volume projections, query patterns, operational complexity
**Target decisión**: Q2 2024
**Owner**: Equipo de Arquitectura

### PND-002: Event archiving policy para retención a largo plazo
**Contexto**: Balance entre compliance requirements y storage costs
**Opciones bajo evaluación**:
- Cold storage en S3 Glacier después de 2 años
- Event compression con schema evolution
- Event summarization para analytics históricos
**Criterios de decisión**: Compliance requirements, query frequency, cost optimization
**Target decisión**: Q3 2024
**Owner**: Equipo de Arquitectura + Legal

### PND-003: Schema evolution strategy para eventos
**Contexto**: Manejo de cambios en esquemas de eventos sin breaking changes
**Opciones bajo evaluación**:
- Schema Registry con Avro/Protobuf
- JSON Schema evolution con versioning
- Event transformation pipelines
**Criterios de decisión**: Breaking changes handling, performance impact, tooling
**Target decisión**: Q2 2024
**Owner**: Equipo de Desarrollo

## 9.10 Lecciones aprendidas

### Éxitos
1. **Event Sourcing adoption**: Redujo tiempo de auditoría en 80%
2. **PostgreSQL choice**: Performance mejor que esperado para workload OLTP/OLAP híbrido
3. **CQRS implementation**: Query performance mejoró 10x vs approach naive

### Desafíos
1. **Learning curve**: Team ramping time fue 3 meses vs 1 mes estimado
2. **Debugging complexity**: Nuevas herramientas requeridas para resolución de problemas
3. **Testing strategy**: Contract testing entre eventos más complejo que anticipado

### Ajustes realizados
1. **Projection rebuilds**: Implementación de rebuild incremental vs full rebuild
2. **Cache invalidation**: Estrategia más granular que initial TTL-only approach
3. **Tenant onboarding**: Automatización completa vs manual schema creation

### Justificación
- **Familiaridad del equipo**: Conocimiento existente en PostgreSQL
- **ACID compliance**: Transacciones robustas para consistency
- **JSONB support**: Flexibilidad para evolución de esquemas
- **Performance**: Índices especializados para queries temporales
- **Ecosystem**: Amplio soporte de herramientas y librerías
- **Multi-tenancy**: Schema-per-tenant para aislamiento

### Consecuencias
- **Positivas**: Confiabilidad, performance, ecosystem maduro
- **Negativas**: No especializado para event sourcing, setup más complejo
- **Mitigación**: Optimizaciones específicas, monitoring especializado

---

## 9.3 ADR-003: CQRS con read models separados

**Estado**: Aceptado
**Fecha**: 2024-01-25
**Decidido por**: Tech Lead

### Contexto
Optimización de queries para diferentes casos de uso (timeline, analytics, search) con patrones de acceso muy distintos.

### Alternativas consideradas
1. **Query directo desde Event Store**: Una sola fuente de datos
2. **CQRS con read models**: Separación de lectura y escritura
3. **Materialized views**: Vistas materializadas en misma DB

### Decisión
Implementamos **CQRS** con read models especializados.

### Justificación
- **Performance**: Queries optimizadas por caso de uso
- **Escalabilidad**: Read models independientes escalables
- **Flexibilidad**: Diferentes estructuras de datos por necesidad
- **Disponibilidad**: Tolerancia a fallos independiente

### Implementación
```csharp
// Command side - Event Store
public class EventStoreRepository : IEventRepository
{
    public async Task SaveEventsAsync(string streamId, IEnumerable<DomainEvent> events)
    {
        // Append events to PostgreSQL event store
    }
}

// Query side - Read Models
public class TimelineReadModel : ITimelineQueries
{
    public async Task<TimelineView> GetTimelineAsync(string entityId)
    {
        // Query from optimized timeline projection
    }
}
```

### Consecuencias
- **Positivas**: Performance, escalabilidad, mantenibilidad
- **Negativas**: Eventual consistency, complejidad de sincronización
- **Mitigación**: Monitoreo de lag, circuit breakers, fallback queries

---

## 9.4 ADR-004: Event Store Agnóstico para Event Streaming

**Estado**: Aceptado
**Fecha**: 2024-02-01 (Actualizado: 2025-08-05)
**Decidido por**: Equipo de Arquitectura

### Contexto
Necesidad de streaming de eventos hacia read models y sistemas externos con alta capacidad de procesamiento y durabilidad, con flexibilidad para escalar según volumen operacional.

### Alternativas consideradas
1. **PostgreSQL**: Inicio simple, ACID compliance, expertise del equipo
2. **SNS+SQS**: Escalabilidad managed AWS, integración nativa
3. **RabbitMQ/Amazon MQ**: Event streaming robusto, patrones messaging complejos
4. **Event Bus (Kafka)**: Alto capacidad de procesamiento, ecosistema maduro (para volúmenes muy altos)

### Decisión
Adoptamos **Event Store agnóstico basado en volumen** con abstracción IEventStore.

### Justificación
- **PostgreSQL-first**: Inicio con PostgreSQL para simplicidad operacional
- **Volume-based scaling**: < 1K events/hora PostgreSQL, 1K-10K evaluación, > 10K SNS+SQS/RabbitMQ
- **Abstraction pattern**: IEventStore permite migración sin reescribir lógica de negocio
- **Cost-effective**: Optimización de costos según volumen real vs proyectado
- **Scalability**: Escalamiento horizontal natural

### Configuración
```yaml
topics:
  domain-events:
    partitions: 12
    replication-factor: 3
    retention: 7d
  integration-events:
    partitions: 6
    replication-factor: 3
    retention: 30d
```

### Consecuencias
- **Positivas**: Alta performance, durabilidad, ecosystem rico
- **Negativas**: Complejidad operacional, learning curve
- **Mitigación**: Managed Kafka service, monitoring robusto, documentación

---

## 9.5 ADR-005: Redis para caching distribuido

**Estado**: Aceptado
**Fecha**: 2024-02-05
**Decidido por**: Tech Lead

### Contexto
Optimización de queries frecuentes de timeline y reducción de latencia en consultas de read models.

### Alternativas consideradas
1. **In-memory caching**: Cache local por instancia
2. **Redis**: Cache distribuido
3. **Memcached**: Simple distributed cache
4. **Database query cache**: Cache a nivel de DB

### Decisión
Implementamos **Redis** como cache distribuido.

### Justificación
- **Performance**: Sub-millisecond latency para hot data
- **Consistency**: Cache compartido entre instancias
- **Durability**: Opcional persistence para warm-up
- **Features**: Estructuras de datos avanzadas (TTL, pipelines)
- **Monitoring**: Métricas detalladas de hit/miss ratios

### Estrategia de cache
```csharp
public class CacheStrategy
{
    // L1: In-memory (5 min TTL)
    // L2: Redis distributed (15 min TTL)
    // L3: Database fallback

    public async Task<T> GetOrSetAsync<T>(string key, Func<Task<T>> factory)
    {
        return await _memoryCache.GetOrCreateAsync(key, async entry =>
        {
            entry.SlidingExpiration = TimeSpan.FromMinutes(5);
            return await _distributedCache.GetOrSetAsync(key, factory, TimeSpan.FromMinutes(15));
        });
    }
}
```

### Consecuencias
- **Positivas**: Latencia ultra-baja, consistency, monitoring
- **Negativas**: Complejidad adicional, gestión de invalidación
- **Mitigación**: TTL automático, cache warming, fallback strategies

---

## 9.7 Resumen de decisiones

| ADR | Decisión | Impacto | Estado |
|-----|----------|---------|---------|
| 001 | Event Sourcing | Alto - Arquitectura fundamental | ✅ Implementado |
| 002 | PostgreSQL Event Store | Alto - Storage principal | ✅ Implementado |
| 003 | CQRS Read Models | Medio - Performance | ✅ Implementado |
| 004 | Event Bus Streaming | Medio - Integration | ✅ Implementado |
| 005 | Redis Caching | Bajo - Optimization | ✅ Implementado |
| 006 | Multi-tenant Schema | Alto - Security/Compliance | ✅ Implementado |

## 9.8 Decisiones pendientes

### PND-001: Sharding strategy para escalamiento
**Contexto**: Crecimiento esperado requiere distribución horizontal
**Opciones**: Shard por tenant, por tiempo, por hash de entity
**Target**: Q2 2024

### PND-002: Archiving policy para event store
**Contexto**: Retención a largo plazo vs performance
**Opciones**: Cold storage, compression, summarization
**Target**: Q3 2024
