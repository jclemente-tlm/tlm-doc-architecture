# 8. Conceptos transversales

## 8.1 Seguridad

| Aspecto | Implementación | Tecnología |
|---------|-----------------|-------------|
| **Autenticación** | JWT validation | OAuth2 |
| **Autorización** | Claims-based | .NET 8 |
| **Cifrado** | TLS 1.3 | HTTPS |
| **Datos sensibles** | AES-256 | Cifrado |

## 8.2 Observabilidad

| Tipo | Herramienta | Propósito |
|------|-------------|----------|
| **Logs** | Serilog | Registro eventos |
| **Métricas** | Prometheus | Monitoreo |
| **Tracing** | OpenTelemetry | Trazabilidad |
| **Health** | Health Checks | Estado servicios |

## 8.3 Multi-tenancy

| Aspecto | Implementación | Propósito |
|---------|-----------------|----------|
| **Aislamiento** | Por país | Separación datos |
| **Deduplicación** | Por tenant | Prevención duplicados |
| **Rate limiting** | Por organización | Protección recursos |

## 8.1 Modelo de dominio

### 8.1.1 Event Sourcing como principio arquitectónico

**Concepto**: Todos los cambios de estado se capturan como eventos inmutables, garantizando auditabilidad completa y permitiendo reconstrucción de estado en cualquier momento.

**Implementación**:

- **Event Store**: Almacén inmutable de eventos como única fuente de verdad
- **Snapshots**: Optimización para reconstrucción rápida de estado
- **Event versioning**: Manejo de evolución de esquemas de eventos
- **Temporal queries**: Consultas de estado en puntos específicos del tiempo

**Ventajas específicas para Track & Trace**:

- Auditoría completa requerida por regulaciones
- Análisis temporal de patrones operacionales
- Capacidad de replay para debugging
- Soporte natural para analytics y reporting

### 8.1.2 CQRS (Command Query Responsibility Segregation)

**Separación de responsabilidades**:

- **Command side**: Escritura de eventos, validaciones de negocio
- **Query side**: Lectura optimizada desde read models especializados
- **Event handlers**: Sincronización asíncrona entre ambos lados

**Read models especializados**:

- Timeline views para trazabilidad
- Aggregated views para dashboards
- Search indexes para consultas complejas
- Analytics projections para KPIs

## 8.2 Seguridad

### 8.2.1 Autenticación y autorización

**OAuth2 + JWT**:

```csharp
public class TrackTraceAuthenticationOptions
{
    public string Authority { get; set; }
    public string Audience { get; set; }
    public string[] Scopes { get; set; }
    public bool RequireHttpsMetadata { get; set; } = true;
}

[Authorize(Policy = "TrackTraceRead")]
public async Task<TimelineView> GetTimeline(string entityId)
{
    // Implementation with proper authorization context
    var tenantId = User.GetTenantId();
    var userPermissions = await _permissionService.GetUserPermissions(User.GetUserId(), tenantId);

    return await _timelineService.GetTimeline(entityId, tenantId, userPermissions);
}

public class AuthorizationPolicies
{
    public static void ConfigurePolicies(AuthorizationOptions options)
    {
        options.AddPolicy("TrackTraceRead", policy =>
            policy.RequireScope("track-trace:read")
                  .RequireClaim("tenant_access"));

        options.AddPolicy("TrackTraceWrite", policy =>
            policy.RequireScope("track-trace:write")
                  .RequireClaim("tenant_admin"));

        options.AddPolicy("TrackTraceAnalytics", policy =>
            policy.RequireScope("track-trace:analytics")
                  .RequireClaim("analytics_access"));
    }
}
```

### 8.2.2 Tenant Isolation

**Data Isolation Strategy**:

- **Tenant-per-schema**: Esquemas separados por tenant en PostgreSQL
- **Row-level security**: Filtros automáticos por tenant_id
- **Event stream partitioning**: Streams aislados por tenant

```csharp
public class TenantAwareEventStore : IEventStore
{
    private readonly IDbConnectionFactory _connectionFactory;
    private readonly ITenantContext _tenantContext;

    public async Task AppendEventsAsync(string streamId, IEnumerable<EventData> events)
    {
        var tenantId = _tenantContext.GetCurrentTenantId();
        var connection = await _connectionFactory.GetConnectionAsync(tenantId);

        // All events are automatically scoped to the tenant
        var tenantedStreamId = $"{tenantId}:{streamId}";
        await AppendEventsToTenantStream(connection, tenantedStreamId, events);
    }
}

public class TenantContextMiddleware
{
    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        var tenantId = ExtractTenantFromToken(context) ??
                      ExtractTenantFromHeader(context);

        if (tenantId == null)
            throw new UnauthorizedAccessException("Tenant not specified");

        context.Items["TenantId"] = tenantId;
        await next(context);
    }
}
```

### 8.2.3 Data Protection y Compliance

**Encryption at Rest**:

- Event payloads encriptados con claves por tenant
- PII data tokenization
- Key rotation policies

**GDPR/Data Privacy Compliance**:

```csharp
public class GdprComplianceService
{
    public async Task HandleDataSubjectRightsRequest(DataSubjectRequest request)
    {
        switch (request.RequestType)
        {
            case DataSubjectRequestType.Access:
                await GenerateDataExport(request.SubjectId);
                break;

            case DataSubjectRequestType.Deletion:
                await PseudonymizePersonalData(request.SubjectId);
                break;

            case DataSubjectRequestType.Rectification:
                await UpdatePersonalData(request.SubjectId, request.UpdatedData);
                break;
        }
    }

    private async Task PseudonymizePersonalData(string subjectId)
    {
        // Create pseudonymization event instead of deletion
        var pseudonymizationEvent = new PersonalDataPseudonymizedEvent
        {
            SubjectId = subjectId,
            PseudonymizationId = Guid.NewGuid(),
            Timestamp = DateTime.UtcNow,
            Reason = "GDPR deletion request"
        };

        await _eventStore.AppendEventsAsync(
            $"data-subject-{subjectId}",
            new[] { pseudonymizationEvent });
    }
}
```

## 8.3 Comunicación e integración

### 8.3.1 Event-driven communication

**Event Publishing**:

```csharp
public interface IEventPublisher
{
    Task PublishAsync<T>(T @event, string streamId) where T : IDomainEvent;
    Task PublishBatchAsync(IEnumerable<EventData> events);
}

public class KafkaEventPublisher : IEventPublisher
{
    private readonly IProducer<string, byte[]> _producer;
    private readonly IEventSerializer _serializer;

    public async Task PublishAsync<T>(T @event, string streamId) where T : IDomainEvent
    {
        var topicName = GetTopicName<T>();
        var eventData = await _serializer.SerializeAsync(@event);

        var message = new Message<string, byte[]>
        {
            Key = streamId,
            Value = eventData,
            Headers = CreateEventHeaders(@event)
        };

        await _producer.ProduceAsync(topicName, message);
    }

    private Headers CreateEventHeaders<T>(T @event) where T : IDomainEvent
    {
        return new Headers
        {
            {"event-type", Encoding.UTF8.GetBytes(typeof(T).Name)},
            {"event-version", Encoding.UTF8.GetBytes(@event.Version.ToString())},
            {"correlation-id", Encoding.UTF8.GetBytes(@event.CorrelationId)},
            {"tenant-id", Encoding.UTF8.GetBytes(@event.TenantId)}
        };
    }
}
```

**Event Consumption**:

```csharp
public class EventConsumerService : BackgroundService
{
    private readonly IConsumer<string, byte[]> _consumer;
    private readonly IEventHandlerRegistry _handlerRegistry;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _consumer.Subscribe(GetSubscribedTopics());

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var consumeResult = _consumer.Consume(stoppingToken);
                await ProcessMessage(consumeResult);
                _consumer.Commit(consumeResult);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing message");
                // Implement retry logic or dead letter queue
            }
        }
    }

    private async Task ProcessMessage(ConsumeResult<string, byte[]> result)
    {
        var eventType = GetEventTypeFromHeaders(result.Message.Headers);
        var handler = _handlerRegistry.GetHandler(eventType);

        if (handler != null)
        {
            var @event = await _serializer.DeserializeAsync(result.Message.Value, eventType);
            await handler.HandleAsync(@event);
        }
    }
}
```

### 8.3.2 API Integration Patterns

**Patrón Circuit Breaker**:

```csharp
public class ExternalServiceClient
{
    private readonly HttpClient _httpClient;
    private readonly ICircuitBreaker _circuitBreaker;

    public async Task<T> CallExternalServiceAsync<T>(string endpoint, object request)
    {
        return await _circuitBreaker.ExecuteAsync(async () =>
        {
            var response = await _httpClient.PostAsJsonAsync(endpoint, request);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<T>();
        });
    }
}

public class CircuitBreakerConfiguration
{
    public int FailureThreshold { get; set; } = 5;
    public TimeSpan OpenTimeout { get; set; } = TimeSpan.FromMinutes(1);
    public TimeSpan HalfOpenTimeout { get; set; } = TimeSpan.FromSeconds(30);
}
```

**Retry Policies**:

```csharp
public class RetryPolicyConfiguration
{
    public static IAsyncPolicy<HttpResponseMessage> GetHttpRetryPolicy()
    {
        return Policy
            .HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
            .Or<HttpRequestException>()
            .WaitAndRetryAsync(
                retryCount: 3,
                sleepDurationProvider: retryAttempt =>
                    TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                onRetry: (outcome, timespan, retryCount, context) =>
                {
                    var logger = context.GetLogger();
                    logger?.LogWarning("Retry {RetryCount} after {Delay}ms",
                        retryCount, timespan.TotalMilliseconds);
                });
    }
}
```

## 8.4 Persistencia

### 8.4.1 Event Store Design

**Schema Design**:

```sql
-- Events table optimized for append operations
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    tenant_id VARCHAR(50) NOT NULL,

    CONSTRAINT events_stream_version_unique UNIQUE (stream_id, version)
);

-- Indexes for optimal query performance
CREATE INDEX idx_events_stream_id ON events (stream_id);
CREATE INDEX idx_events_timestamp ON events (timestamp);
CREATE INDEX idx_events_tenant_id ON events (tenant_id);
CREATE INDEX idx_events_event_type ON events (event_type);

-- Partitioning by tenant for large scale
CREATE TABLE events_tenant_001 PARTITION OF events
FOR VALUES IN ('tenant-001');

-- Snapshots for performance optimization
CREATE TABLE snapshots (
    stream_id VARCHAR(255) PRIMARY KEY,
    version INTEGER NOT NULL,
    data JSONB NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    tenant_id VARCHAR(50) NOT NULL
);
```

**Repository Pattern Implementation**:

```csharp
public class PostgreSqlEventStore : IEventStore
{
    private readonly IDbConnectionFactory _connectionFactory;
    private readonly IEventSerializer _serializer;
    private readonly ILogger<PostgreSqlEventStore> _logger;

    public async Task<IEnumerable<EventData>> GetEventsAsync(
        string streamId,
        int fromVersion = 0,
        int? toVersion = null)
    {
        using var connection = await _connectionFactory.CreateConnectionAsync();

        var sql = @"
            SELECT event_type, event_data, metadata, version, timestamp
            FROM events
            WHERE stream_id = @streamId
            AND version >= @fromVersion
            AND (@toVersion IS NULL OR version <= @toVersion)
            ORDER BY version";

        var parameters = new { streamId, fromVersion, toVersion };
        var results = await connection.QueryAsync<EventRecord>(sql, parameters);

        return results.Select(r => new EventData
        {
            EventType = r.EventType,
            Data = r.EventData,
            Metadata = r.Metadata,
            Version = r.Version,
            Timestamp = r.Timestamp
        });
    }

    public async Task AppendEventsAsync(string streamId, IEnumerable<EventData> events)
    {
        using var connection = await _connectionFactory.CreateConnectionAsync();
        using var transaction = await connection.BeginTransactionAsync();

        try
        {
            var currentVersion = await GetCurrentVersionAsync(connection, streamId);
            var eventsToAppend = events.ToList();

            for (int i = 0; i < eventsToAppend.Count; i++)
            {
                var @event = eventsToAppend[i];
                var newVersion = currentVersion + i + 1;

                await InsertEventAsync(connection, streamId, @event, newVersion);
            }

            await transaction.CommitAsync();

            // Publish events after successful persistence
            await PublishEvents(streamId, eventsToAppend);
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}
```

### 8.4.2 Read Model Management

**Projection Engine**:

```csharp
public class ProjectionEngine
{
    private readonly IEventStore _eventStore;
    private readonly IProjectionStore _projectionStore;
    private readonly ILogger<ProjectionEngine> _logger;

    public async Task RebuildProjectionAsync<T>(string projectionName) where T : IProjection
    {
        _logger.LogInformation("Starting rebuild of projection {ProjectionName}", projectionName);

        // Reset projection state
        await _projectionStore.ResetProjectionAsync(projectionName);

        // Process all events from the beginning
        var checkpoint = await _projectionStore.GetCheckpointAsync(projectionName) ?? 0;
        var events = _eventStore.GetAllEventsAsync(checkpoint);

        await foreach (var @event in events)
        {
            var projection = await _projectionStore.GetProjectionAsync<T>(projectionName);
            await projection.HandleAsync(@event);
            await _projectionStore.SaveProjectionAsync(projectionName, projection);
            await _projectionStore.UpdateCheckpointAsync(projectionName, @event.GlobalPosition);
        }

        _logger.LogInformation("Completed rebuild of projection {ProjectionName}", projectionName);
    }
}

public class TimelineProjection : IProjection
{
    public string Id { get; set; }
    public List<TimelineEvent> Events { get; set; } = new();

    public async Task HandleAsync(IDomainEvent @event)
    {
        switch (@event)
        {
            case EntityCreatedEvent created:
                Events.Add(new TimelineEvent
                {
                    Timestamp = created.Timestamp,
                    EventType = "Created",
                    Description = $"Entity {created.EntityId} was created",
                    Data = created.Data
                });
                break;

            case EntityUpdatedEvent updated:
                Events.Add(new TimelineEvent
                {
                    Timestamp = updated.Timestamp,
                    EventType = "Updated",
                    Description = $"Entity {updated.EntityId} was updated",
                    Data = updated.Changes
                });
                break;

            case EntityDeletedEvent deleted:
                Events.Add(new TimelineEvent
                {
                    Timestamp = deleted.Timestamp,
                    EventType = "Deleted",
                    Description = $"Entity {deleted.EntityId} was deleted",
                    Data = deleted.Reason
                });
                break;
        }
    }
}
```

## 8.5 Sesión de usuario

### 8.5.1 Context Management

**User Context Service**:

```csharp
public interface IUserContext
{
    string UserId { get; }
    string TenantId { get; }
    string[] Roles { get; }
    Dictionary<string, string> Claims { get; }
    bool HasPermission(string permission);
}

public class HttpUserContext : IUserContext
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public string UserId => _httpContextAccessor.HttpContext?.User?.GetUserId();
    public string TenantId => _httpContextAccessor.HttpContext?.User?.GetTenantId();
    public string[] Roles => _httpContextAccessor.HttpContext?.User?.GetRoles() ?? Array.Empty<string>();

    public bool HasPermission(string permission)
    {
        return _httpContextAccessor.HttpContext?.User?.HasClaim("permissions", permission) ?? false;
    }
}
```

### 8.5.2 Audit Trail

**Audit Event Capture**:

```csharp
public class AuditEventInterceptor : IInterceptor
{
    private readonly IAuditService _auditService;
    private readonly IUserContext _userContext;

    public void Intercept(IInvocation invocation)
    {
        var auditableAttribute = invocation.Method.GetCustomAttribute<AuditableAttribute>();
        if (auditableAttribute != null)
        {
            var auditEvent = new AuditEvent
            {
                UserId = _userContext.UserId,
                TenantId = _userContext.TenantId,
                Action = auditableAttribute.Action,
                Resource = auditableAttribute.Resource,
                Timestamp = DateTime.UtcNow,
                Parameters = SerializeParameters(invocation.Arguments)
            };

            _auditService.RecordAuditEvent(auditEvent);
        }

        invocation.Proceed();
    }
}

[Auditable(Action = "READ", Resource = "Timeline")]
public async Task<TimelineView> GetTimelineAsync(string entityId)
{
    // Method implementation
}
```

## 8.6 Configuración

### 8.6.1 Gestión de Configuración

**Hierarchical Configuration**:

```csharp
public class TrackTraceConfiguration
{
    public DatabaseConfiguration Database { get; set; }
    public EventStoreConfiguration EventStore { get; set; }
    public MessagingConfiguration Messaging { get; set; }
    public SecurityConfiguration Security { get; set; }
    public ObservabilityConfiguration Observability { get; set; }
}

public class ConfigurationService
{
    private readonly IConfiguration _configuration;
    private readonly IOptionsMonitor<TrackTraceConfiguration> _options;

    public T GetConfiguration<T>(string section) where T : class, new()
    {
        var config = new T();
        _configuration.GetSection(section).Bind(config);
        return config;
    }

    public void ValidateConfiguration()
    {
        var config = _options.CurrentValue;

        if (string.IsNullOrEmpty(config.Database.ConnectionString))
            throw new InvalidOperationException("Database connection string is required");

        if (string.IsNullOrEmpty(config.Security.Authority))
            throw new InvalidOperationException("Security authority is required");
    }
}
```

### 8.6.2 Environment-specific Settings

```yaml
# appsettings.Development.json
{
  "TrackTrace": {
    "Database": {
      "ConnectionString": "Host=localhost;Database=tracktracedb_dev;Username=dev;Password=dev123",
      "MaxRetryCount": 3,
      "CommandTimeout": 30
    },
    "EventStore": {
      "BatchSize": 100,
      "SnapshotFrequency": 50
    },
    "Messaging": {
      "EventBus": {
        "Configuration": "localhost:5672",
        "GroupId": "track-trace-dev",
        "AutoRestart": "true"
      }
    },
    "Security": {
      "Authority": "https://identity-dev.talma.local",
      "Audience": "track-trace-api",
      "RequireHttpsMetadata": false
    }
  }
}

# appsettings.Production.json
{
  "TrackTrace": {
    "Database": {
      "ConnectionString": "${DATABASE_CONNECTION_STRING}",
      "MaxRetryCount": 5,
      "CommandTimeout": 60
    },
    "EventStore": {
      "BatchSize": 500,
      "SnapshotFrequency": 100
    },
    "Messaging": {
      "EventBus": {
        "Configuration": "${EVENTBUS_CONFIGURATION}",
        "GroupId": "track-trace-prod",
        "SecurityProtocol": "SaslSsl",
        "SaslMechanism": "Plain"
      }
    },
    "Security": {
      "Authority": "https://identity.talma.com",
      "Audience": "track-trace-api",
      "RequireHttpsMetadata": true
    }
  }
}
```

## 8.7 Internacionalización

### 8.7.1 Multi-language Support

**Resource Management**:

```csharp
public class LocalizedMessageService
{
    private readonly IStringLocalizer<LocalizedMessageService> _localizer;
    private readonly IUserContext _userContext;

    public string GetLocalizedMessage(string key, params object[] args)
    {
        var culture = GetUserCulture();
        using var scope = CultureInfo.CreateSpecificCulture(culture);

        return _localizer[key, args];
    }

    private string GetUserCulture()
    {
        return _userContext.Claims.GetValueOrDefault("preferred_language", "en-US");
    }
}

// Resource files structure:
// Resources/
//   SharedResource.en-US.resx
//   SharedResource.es-ES.resx
//   SharedResource.pt-BR.resx
```

### 8.7.2 Timezone Handling

```csharp
public class TimezoneService
{
    private readonly IUserContext _userContext;

    public DateTime ConvertToUserTimezone(DateTime utcDateTime)
    {
        var userTimezone = GetUserTimezone();
        var timeZoneInfo = TimeZoneInfo.FindSystemTimeZoneById(userTimezone);
        return TimeZoneInfo.ConvertTimeFromUtc(utcDateTime, timeZoneInfo);
    }

    public DateTime ConvertToUtc(DateTime localDateTime, string timeZoneId = null)
    {
        var timezone = timeZoneId ?? GetUserTimezone();
        var timeZoneInfo = TimeZoneInfo.FindSystemTimeZoneById(timezone);
        return TimeZoneInfo.ConvertTimeToUtc(localDateTime, timeZoneInfo);
    }

    private string GetUserTimezone()
    {
        return _userContext.Claims.GetValueOrDefault("timezone", "UTC");
    }
}
```

**Políticas de autorización**:

- **TrackTraceRead**: Lectura de datos de trazabilidad
- **TrackTraceWrite**: Creación de eventos de seguimiento
- **TrackTraceAdmin**: Gestión de configuraciones y analytics
- **TrackTraceAudit**: Acceso a logs de auditoría

### 8.2.2 Protección de datos

**Cifrado**:

- **En tránsito**: TLS 1.3 para todas las comunicaciones
- **En reposo**: AES-256 para datos sensibles en Event Store
- **Claves**: Rotación automática cada 90 días

**Data masking**:

```csharp
public class EventDataMasker
{
    public string MaskSensitiveData(string eventData, EventType eventType)
    {
        if (eventType.ContainsPII)
        {
            return _maskingEngine.ApplyRules(eventData, _piiMaskingRules);
        }
        return eventData;
    }
}
```

**Compliance**:

- **GDPR**: Right to be forgotten implementado via event compensation
- **SOX**: Inmutabilidad de registros financieros
- **Audit trails**: Logs tamper-proof con digital signatures

## 8.3 Multi-tenancy

### 8.3.1 Aislamiento de datos

**Estrategia**: Schema-per-tenant para aislamiento completo

```sql
-- Tenant-specific event streams
CREATE SCHEMA tenant_abc123;
CREATE TABLE tenant_abc123.events (
    stream_id VARCHAR(255) NOT NULL,
    version BIGINT NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (stream_id, version)
);

-- Row-level security como backup
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON events
FOR ALL TO application_role
USING (tenant_id = current_setting('app.current_tenant_id'));
```

### 8.3.2 Configuración por tenant

```csharp
public class TenantConfiguration
{
    public string TenantId { get; set; }
    public EventRetentionPolicy RetentionPolicy { get; set; }
    public AnalyticsSettings Analytics { get; set; }
    public ComplianceSettings Compliance { get; set; }
    public IntegrationEndpoints Integrations { get; set; }
}

public class TenantConfigurationService
{
    public async Task<TenantConfiguration> GetConfigurationAsync(string tenantId)
    {
        return await _cache.GetOrSetAsync($"tenant:config:{tenantId}",
            () => _repository.GetTenantConfigurationAsync(tenantId),
            TimeSpan.FromHours(1));
    }
}
```

## 8.4 Observabilidad

### 8.4.1 Structured logging

**Serilog configuration**:

```csharp
Log.Logger = new LoggerConfiguration()
    .Enrich.WithProperty("Service", "TrackTrace")
    .Enrich.WithProperty("Version", Assembly.GetExecutingAssembly().GetName().Version)
    .Enrich.WithCorrelationId()
    .WriteTo.Console(new JsonFormatter())
    .WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri(elasticUrl))
    {
        IndexFormat = "tracktrace-logs-{0:yyyy.MM.dd}",
        AutoRegisterTemplate = true
    })
    .CreateLogger();
```

**Contexto de eventos**:

```csharp
public class EventLoggingContext
{
    public string CorrelationId { get; set; }
    public string TenantId { get; set; }
    public string EntityId { get; set; }
    public string EventType { get; set; }
    public string UserId { get; set; }
    public DateTime Timestamp { get; set; }
}

// Usage in event handler
using (LogContext.PushProperty("TenantId", @event.TenantId))
using (LogContext.PushProperty("EntityId", @event.EntityId))
{
    _logger.LogInformation("Processing event {@Event}", @event);
}
```

### 8.4.2 Métricas y telemetría

**Custom metrics**:

```csharp
public class TrackTraceMetrics
{
    private readonly IMetricLogger _metrics;

    public void RecordEventProcessed(string eventType, string tenantId, TimeSpan duration)
    {
        _metrics.Counter("events_processed_total")
               .WithTag("event_type", eventType)
               .WithTag("tenant_id", tenantId)
               .Increment();

        _metrics.Histogram("event_processing_duration_ms")
               .WithTag("event_type", eventType)
               .Record(duration.TotalMilliseconds);
    }

    public void RecordQueryExecuted(string queryType, bool fromCache, TimeSpan duration)
    {
        _metrics.Counter("queries_executed_total")
               .WithTag("query_type", queryType)
               .WithTag("cache_hit", fromCache.ToString())
               .Increment();
    }
}
```

**Distributed tracing**:

```csharp
public class EventHandler
{
    private readonly ActivitySource _activitySource = new("TrackTrace.Events");

    public async Task Handle(DomainEvent @event)
    {
        using var activity = _activitySource.StartActivity("EventHandler.Handle");
        activity?.SetTag("event.type", @event.GetType().Name);
        activity?.SetTag("event.id", @event.Id);
        activity?.SetTag("tenant.id", @event.TenantId);

        // Process event
        await ProcessEvent(@event);
    }
}
```

## 8.5 Performance y escalabilidad

### 8.5.1 Estrategias de cache

**Niveles de cache**:

1. **L1 (In-memory)**: Cache local para hot data
2. **L2 (Redis)**: Cache distribuido para read models
3. **L3 (CDN)**: Cache de edge para datos públicos

```csharp
public class CachedTimelineService
{
    public async Task<TimelineView> GetTimelineAsync(string entityId, string tenantId)
    {
        var cacheKey = $"timeline:{tenantId}:{entityId}";

        // L1 Cache
        if (_memoryCache.TryGetValue(cacheKey, out TimelineView cachedTimeline))
            return cachedTimeline;

        // L2 Cache
        var timelineJson = await _distributedCache.GetStringAsync(cacheKey);
        if (timelineJson != null)
        {
            var timeline = JsonSerializer.Deserialize<TimelineView>(timelineJson);
            _memoryCache.Set(cacheKey, timeline, TimeSpan.FromMinutes(5));
            return timeline;
        }

        // Database query
        var freshTimeline = await _queryHandler.Handle(new GetTimelineQuery(entityId, tenantId));
        await _distributedCache.SetStringAsync(cacheKey, JsonSerializer.Serialize(freshTimeline),
                                             new DistributedCacheEntryOptions
                                             {
                                                 SlidingExpiration = TimeSpan.FromMinutes(15)
                                             });
        return freshTimeline;
    }
}
```

### 8.5.2 Particionado y sharding

**Event store partitioning**:

```sql
-- Partition by tenant and time for optimal query performance
CREATE TABLE events (
    stream_id VARCHAR(255) NOT NULL,
    version BIGINT NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL
) PARTITION BY RANGE (timestamp);

-- Monthly partitions
CREATE TABLE events_2024_01 PARTITION OF events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

## 8.6 Manejo de errores

### 8.6.1 Estrategias de retry

```csharp
public class RetryPolicy
{
    public static async Task<T> ExecuteWithRetryAsync<T>(
        Func<Task<T>> operation,
        int maxAttempts = 3,
        TimeSpan delay = default)
    {
        var attempts = 0;
        while (attempts < maxAttempts)
        {
            try
            {
                return await operation();
            }
            catch (Exception ex) when (IsRetriableException(ex) && attempts < maxAttempts - 1)
            {
                attempts++;
                var waitTime = CalculateBackoffDelay(attempts, delay);
                await Task.Delay(waitTime);
            }
        }

        throw new MaxRetryAttemptsExceededException(maxAttempts);
    }

    private static bool IsRetriableException(Exception ex)
    {
        return ex is TimeoutException ||
               ex is HttpRequestException ||
               ex is PostgresException { SqlState: "40001" }; // Serialization failure
    }
}
```

### 8.6.2 Circuit breaker pattern

```csharp
public class EventStoreCircuitBreaker
{
    private readonly CircuitBreakerOptions _options;
    private volatile CircuitBreakerState _state = CircuitBreakerState.Closed;
    private volatile int _failureCount = 0;
    private volatile DateTime _lastFailureTime = DateTime.MinValue;

    public async Task<T> ExecuteAsync<T>(Func<Task<T>> operation)
    {
        if (_state == CircuitBreakerState.Open)
        {
            if (DateTime.UtcNow.Subtract(_lastFailureTime) > _options.OpenTimeout)
            {
                _state = CircuitBreakerState.HalfOpen;
            }
            else
            {
                throw new CircuitBreakerOpenException("Event store circuit breaker is open");
            }
        }

        try
        {
            var result = await operation();
            OnSuccess();
            return result;
        }
        catch (Exception ex)
        {
            OnFailure(ex);
            throw;
        }
    }
}
```

## 8.7 Testing

### 8.7.1 Test strategies

**Event sourcing tests**:

```csharp
public class EventStoreTests
{
    [Fact]
    public async Task Should_Reconstruct_Entity_State_From_Events()
    {
        // Given
        var entityId = "entity-123";
        var events = new List<DomainEvent>
        {
            new EntityCreated(entityId, "Test Entity"),
            new EntityStatusChanged(entityId, Status.Active),
            new EntityUpdated(entityId, "Updated Entity")
        };

        // When
        foreach (var @event in events)
        {
            await _eventStore.AppendEventsAsync(entityId, @event.Version - 1, new[] { @event });
        }

        var reconstructedEntity = await _entityRepository.GetByIdAsync(entityId);

        // Then
        reconstructedEntity.Should().NotBeNull();
        reconstructedEntity.Name.Should().Be("Updated Entity");
        reconstructedEntity.Status.Should().Be(Status.Active);
    }
}
```

**Integration tests**:

```csharp
public class TimelineIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task Should_Return_Timeline_For_Valid_Entity()
    {
        // Given
        var client = _factory.CreateClient();
        var entityId = await CreateTestEntity();

        // When
        var response = await client.GetAsync($"/api/v1/timeline/{entityId}");

        // Then
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var timeline = await response.Content.ReadFromJsonAsync<TimelineView>();
        timeline.Events.Should().NotBeEmpty();
    }
}
```

**Contract Tests**:

```csharp
public class EventContractTests
{
    [Test]
    public void Events_ShouldMaintainBackwardCompatibility()
    {
        var schemas = new[]
        {
            typeof(EntityCreatedEvent),
            typeof(EntityUpdatedEvent),
            typeof(EntityDeletedEvent)
        };

        foreach (var schema in schemas)
        {
            var jsonSchema = JsonSchema.FromType(schema);
            var validator = new JsonSchemaValidator();

            // Verify against previous version schemas
            var isCompatible = validator.ValidateBackwardCompatibility(jsonSchema);
            isCompatible.Should().BeTrue($"Schema {schema.Name} breaks backward compatibility");
        }
    }
}
```

### 8.7.2 Test Data Management

**Test Factories**:

```csharp
public class EventDataBuilder
{
    private string _eventType = "TestEvent";
    private object _data = new { };
    private int _version = 1;

    public EventDataBuilder WithEventType(string eventType)
    {
        _eventType = eventType;
        return this;
    }

    public EventDataBuilder WithData(object data)
    {
        _data = data;
        return this;
    }

    public EventDataBuilder WithVersion(int version)
    {
        _version = version;
        return this;
    }

    public EventData Build()
    {
        return new EventData
        {
            EventType = _eventType,
            Data = JsonSerializer.Serialize(_data),
            Version = _version,
            Timestamp = DateTime.UtcNow
        };
    }
}

public class ScenarioBuilder
{
    private readonly List<EventData> _events = new();

    public ScenarioBuilder Given(params EventData[] events)
    {
        _events.AddRange(events);
        return this;
    }

    public async Task<ScenarioResult> When(Func<Task> action)
    {
        // Setup initial state
        foreach (var @event in _events)
        {
            await ApplyEvent(@event);
        }

        // Execute action
        var exception = await Record.ExceptionAsync(action);

        return new ScenarioResult
        {
            Exception = exception,
            FinalState = await GetCurrentState()
        };
    }
}
```

## 8.10 Observabilidad

### 8.10.1 Logging Structure

**Registro Estructurado Configuration**:

```csharp
public static class LoggingExtensions
{
    public static IServiceCollection AddStructuredLogging(this IServiceCollection services)
    {
        Log.Logger = new LoggerConfiguration()
            .Enrich.FromLogContext()
            .Enrich.WithProperty("Service", "track-trace-api")
            .Enrich.WithMachineName()
            .Enrich.WithEnvironmentName()
            .WriteTo.Console(new JsonFormatter())
            .WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri("http://elasticsearch:9200"))
            {
                IndexFormat = "track-trace-logs-{0:yyyy.MM.dd}",
                AutoRegisterTemplate = true
            })
            .CreateLogger();

        return services.AddSerilog();
    }

    public static void LogEventProcessed<T>(this ILogger logger, T @event, string streamId, TimeSpan duration)
        where T : IDomainEvent
    {
        logger.LogInformation("Event processed: {EventType} for stream {StreamId} in {Duration}ms",
            typeof(T).Name, streamId, duration.TotalMilliseconds);
    }

    public static void LogEventProcessingFailed<T>(this ILogger logger, T @event, string streamId, Exception exception)
        where T : IDomainEvent
    {
        logger.LogError(exception, "Failed to process event {EventType} for stream {StreamId}",
            typeof(T).Name, streamId);
    }
}
```

### 8.10.2 Metrics and Monitoring

**Custom Metrics**:

```csharp
public class TrackTraceMetrics
{
    private readonly IMetricsLogger _metricsLogger;

    // Counters
    public Counter<long> EventsProcessed { get; }
    public Counter<long> EventsPublished { get; }
    public Counter<long> EventProcessingErrors { get; }

    // Histograms
    public Histogram<double> EventProcessingDuration { get; }
    public Histogram<double> QueryDuration { get; }

    // Gauges
    public ObservableGauge<int> ActiveEventStreams { get; }
    public ObservableGauge<long> EventStoreSize { get; }

    public TrackTraceMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("TrackTrace");

        EventsProcessed = meter.CreateCounter<long>("events_processed_total",
            description: "Total number of events processed");

        EventProcessingDuration = meter.CreateHistogram<double>("event_processing_duration_seconds",
            description: "Time taken to process events");

        ActiveEventStreams = meter.CreateObservableGauge<int>("active_event_streams",
            description: "Number of currently active event streams");
    }

    public void RecordEventProcessed(string eventType, TimeSpan duration)
    {
        EventsProcessed.Add(1, new("event_type", eventType));
        EventProcessingDuration.Record(duration.TotalSeconds, new("event_type", eventType));
    }
}
```

### 8.10.3 Health Checks

**Comprehensive Health Checks**:

```csharp
public class EventStoreHealthCheck : IHealthCheck
{
    private readonly IEventStore _eventStore;

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            await _eventStore.GetEventsAsync("health-check-stream", 0, cancellationToken);
            return HealthCheckResult.Healthy("Event store is responding");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Event store is not responding", ex);
        }
    }
}

public class ProjectionHealthCheck : IHealthCheck
{
    private readonly IProjectionStore _projectionStore;

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var lastCheckpoint = await _projectionStore.GetLastCheckpointAsync();
            var currentPosition = await _eventStore.GetCurrentPositionAsync();

            var lag = currentPosition - lastCheckpoint;

            if (lag > 1000)
            {
                return HealthCheckResult.Degraded($"Projection lag is {lag} events");
            }

            return HealthCheckResult.Healthy($"Projection lag is {lag} events");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Projection health check failed", ex);
        }
    }
}
```

### 8.10.4 Trazado Distribuido

**OpenTelemetry Integration**:

```csharp
public static class TracingExtensions
{
    public static IServiceCollection AddDistributedTracing(this IServiceCollection services)
    {
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
            });

        return services;
    }
}

public class EventHandlerTracing
{
    private static readonly ActivitySource ActivitySource = new("TrackTrace");

    public async Task<T> TraceEventHandling<T>(string eventType, string streamId, Func<Task<T>> handler)
    {
        using var activity = ActivitySource.StartActivity($"handle-{eventType}");
        activity?.SetTag("event.type", eventType);
        activity?.SetTag("stream.id", streamId);
        activity?.SetTag("service.name", "track-trace");

        try
        {
            var result = await handler();
            activity?.SetStatus(ActivityStatusCode.Ok);
            return result;
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            activity?.RecordException(ex);
            throw;
        }
    }
}
```

---

**Puntos clave de los conceptos transversales**:

1. **Event Sourcing**: Principio arquitectónico fundamental que garantiza auditabilidad y permite análisis temporal
2. **CQRS**: Separación clara entre comandos y consultas con read models especializados
3. **Seguridad**: Multi-tenant con JWT, autorización granular y cumplimiento normativo
4. **Comunicación**: Event-driven architecture con Event Bus y patrones de resiliencia
5. **Persistencia**: Event Store optimizado con PostgreSQL y proyecciones especializadas
6. **Observabilidad**: Logging estructurado, métricas detalladas y trazado distribuido
7. **Testing**: Estrategia completa desde unit tests hasta contract testing
8. **Configuración**: Gestión jerárquica con validación y configuración por ambiente

Estos conceptos garantizan que el servicio Track & Trace sea robusto, escalable y mantenible en un entorno empresarial.
