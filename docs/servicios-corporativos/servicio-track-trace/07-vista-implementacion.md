# 7. Vista de implementación

## 7.1 Estructura del proyecto

| Componente | Ubicación | Tecnología |
|------------|-------------|-------------|
| **Track & Trace API** | /src/TrackTraceApi | .NET 8 Web API |
| **Event Processor** | /src/TrackTraceProcessor | .NET 8 Worker |
| **PostgreSQL** | AWS RDS | PostgreSQL 15+ |
| **Redis** | AWS ElastiCache | Redis 7+ |

## 7.2 Dependencias principales

| Dependencia | Versión | Propósito |
|-------------|---------|----------|
| **Entity Framework** | 8.0+ | ORM |
| **FluentValidation** | 11.0+ | Validación |
| **MediatR** | 12.0+ | CQRS |
| **Serilog** | 3.0+ | Logging |

## 7.1 Estructura del sistema

### 7.1.1 Organización de código

```
src/
├── TLM.Services.TrackTrace.API/           # REST API Layer
│   ├── Controllers/                       # API Controllers
│   ├── Middleware/                        # HTTP Middleware
│   ├── Configuration/                     # Configuración DI
│   └── Program.cs                         # Application Entry Point
├── TLM.Services.TrackTrace.Application/   # Application Layer
│   ├── Commands/                          # CQRS Commands
│   ├── Queries/                           # CQRS Queries
│   ├── Handlers/                          # Command/Query Handlers
│   ├── Validators/                        # FluentValidation Rules
│   ├── Services/                          # Servicios de Aplicación
│   └── DTOs/                              # Data Transfer Objects
├── TLM.Services.TrackTrace.Domain/        # Domain Layer
│   ├── Entities/                          # Domain Entities
│   ├── ValueObjects/                      # Value Objects
│   ├── Events/                            # Domain Events
│   ├── Repositories/                      # Repository Abstractions
│   └── Services/                          # Servicios de Dominio
├── TLM.Services.TrackTrace.Infrastructure/ # Infrastructure Layer
│   ├── EventStore/                        # Implementación Event Store
│   ├── ReadModels/                        # Read Model Projections
│   ├── EventBus/                           # Event Bus Integration
│   ├── Authentication/                    # OAuth2/JWT
│   └── Monitoring/                        # Telemetría y Métricas
└── TLM.Services.TrackTrace.Tests/         # Test Projects
    ├── Unit/                              # Unit Tests
    ├── Integration/                       # Integration Tests
    └── Performance/                       # Pruebas de Carga
```

### 7.1.2 Módulos principales

#### Event Store Module

```csharp
// Core abstraction
public interface IEventStore
{
    Task<EventStream> GetEventsAsync(string streamId, long fromVersion = 0);
    Task<AppendResult> AppendEventsAsync(string streamId, long expectedVersion,
                                       IEnumerable<DomainEvent> events);
    Task<Snapshot> GetSnapshotAsync(string streamId);
    Task SaveSnapshotAsync(string streamId, Snapshot snapshot);
}

// Implementación PostgreSQL
public class PostgreSqlEventStore : IEventStore
{
    private readonly IDbContext _context;
    private readonly IEventSerializer _serializer;

    public async Task<AppendResult> AppendEventsAsync(string streamId,
                                                     long expectedVersion,
                                                     IEnumerable<DomainEvent> events)
    {
        using var transaction = await _context.BeginTransactionAsync();

        // Optimistic concurrency check
        var currentVersion = await GetStreamVersionAsync(streamId);
        if (currentVersion != expectedVersion)
            throw new ConcurrencyException($"Expected version {expectedVersion}, got {currentVersion}");

        // Serialize and persist events
        foreach (var @event in events)
        {
            var eventData = _serializer.Serialize(@event);
            await _context.Events.AddAsync(new EventRecord
            {
                StreamId = streamId,
                Version = ++currentVersion,
                EventType = @event.GetType().Name,
                Data = eventData,
                Timestamp = DateTimeOffset.UtcNow
            });
        }

        await _context.SaveChangesAsync();
        await transaction.CommitAsync();

        return new AppendResult { Success = true, NewVersion = currentVersion };
    }
}
```

#### Read Model Projections

```csharp
// Entity timeline projection
public class EntityTimelineProjection : IEventHandler<EntityEvent>
{
    private readonly IReadModelStore _readStore;

    public async Task Handle(EntityEvent @event)
    {
        var timeline = await _readStore.GetTimelineAsync(@event.EntityId) ??
                      new EntityTimeline(@event.EntityId);

        timeline.AddEvent(new TimelineEvent
        {
            EventId = @event.Id,
            Timestamp = @event.Timestamp,
            EventType = @event.GetType().Name,
            Data = @event.ToTimelineData(),
            Metadata = @event.Metadata
        });

        await _readStore.SaveTimelineAsync(timeline);
    }
}

// Proyección de métricas de rendimiento
public class PerformanceMetricsProjection : IEventHandler<OperationalEvent>
{
    private readonly ITimeSeriesStore _timeSeriesStore;

    public async Task Handle(OperationalEvent @event)
    {
        var metrics = CalculateMetrics(@event);

        await _timeSeriesStore.WritePointAsync(new MetricPoint
        {
            Measurement = "operational_performance",
            Tags = new Dictionary<string, string>
            {
                ["tenant_id"] = @event.TenantId,
                ["entity_type"] = @event.EntityType,
                ["operation"] = @event.OperationType
            },
            Fields = metrics,
            Timestamp = @event.Timestamp
        });
    }
}
```

## 7.2 Configuración de despliegue

### 7.2.1 Configuración Docker

```dockerfile
# Multi-stage build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy project files
COPY ["src/TLM.Services.TrackTrace.API/", "TLM.Services.TrackTrace.API/"]
COPY ["src/TLM.Services.TrackTrace.Application/", "TLM.Services.TrackTrace.Application/"]
COPY ["src/TLM.Services.TrackTrace.Domain/", "TLM.Services.TrackTrace.Domain/"]
COPY ["src/TLM.Services.TrackTrace.Infrastructure/", "TLM.Services.TrackTrace.Infrastructure/"]

# Restore dependencies
RUN dotnet restore "TLM.Services.TrackTrace.API/TLM.Services.TrackTrace.API.csproj"

# Build application
RUN dotnet build "TLM.Services.TrackTrace.API/TLM.Services.TrackTrace.API.csproj" -c Release -o /app/build

# Publish
FROM build AS publish
RUN dotnet publish "TLM.Services.TrackTrace.API/TLM.Services.TrackTrace.API.csproj" -c Release -o /app/publish

# Runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Seguridad: Ejecutar como usuario no-root
RUN adduser --disabled-password --home /app --gecos '' appuser && chown -R appuser /app
USER appuser

COPY --from=publish /app/publish .
EXPOSE 8080

# Verificación de salud
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "TLM.Services.TrackTrace.API.dll"]
```

### 7.2.2 Despliegue en Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tracktrace-api
  namespace: corporate-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tracktrace-api
  template:
    metadata:
      labels:
        app: tracktrace-api
    spec:
      containers:
      - name: api
        image: tlm/tracktrace-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: ASPNETCORE_ENVIRONMENT
          value: "Production"
        - name: ConnectionStrings__EventStore
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: eventstore-connection
        - name: EventBus__Configuration
          valueFrom:
            configMapKeyRef:
              name: eventbus-config
              key: bootstrap-servers
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 7.2.3 Configuración de Ambiente

```yaml
# application.yml
Database:
  EventStore:
    ConnectionString: "Host=${DB_HOST};Database=${DB_NAME};Username=${DB_USER};Password=${DB_PASSWORD}"
    CommandTimeout: 30
    MaxPoolSize: 100

  ReadModel:
    ConnectionString: "Host=${READ_DB_HOST};Database=${READ_DB_NAME};Username=${READ_DB_USER};Password=${READ_DB_PASSWORD}"
    MaxPoolSize: 50

EventSourcing:
  SnapshotFrequency: 100  # Create snapshot every 100 events
  MaxEventsInMemory: 1000

Authentication:
  Authority: "${KEYCLOAK_AUTHORITY}"
  Audience: "tracktrace-api"
  ValidateLifetime: true
  ClockSkew: 300  # 5 minutes

EventBus:
  Configuration: "${EVENTBUS_CONFIG}"
  GroupId: "tracktrace-consumers"
  Topics:
    Events: "track-trace-events"
    Commands: "track-trace-commands"
    Notifications: "system-notifications"

Monitoring:
  OpenTelemetry:
    Endpoint: "${OTEL_EXPORTER_OTLP_ENDPOINT}"
    ServiceName: "track-trace-api"

  Prometheus:
    Enabled: true
    Port: 9090
    Path: "/metrics"
```

### 7.2.4 Variables de Entorno

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `DB_HOST` | Host del Event Store PostgreSQL | localhost | ✅ |
| `DB_NAME` | Nombre de la base de datos | tracktracedb | ✅ |
| `DB_USER` | Usuario de base de datos | tracktraceuser | ✅ |
| `DB_PASSWORD` | Contraseña de base de datos | - | ✅ |
| `READ_DB_HOST` | Host del Read Model PostgreSQL | localhost | ✅ |
| `KEYCLOAK_AUTHORITY` | Authority del proveedor OAuth2 | - | ✅ |
| `EVENTBUS_CONFIG` | Event Bus configuration | localhost:5672 | ✅ |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Endpoint OpenTelemetry | - | ❌ |
| `LOG_LEVEL` | Nivel de logging | Information | ❌ |

## 7.3 Infraestructura como Código

### 7.3.1 Configuración Terraform

```hcl
# Base de Datos Event Store
resource "aws_rds_instance" "event_store" {
  identifier     = "tracktrace-eventstore-${var.environment}"
  engine         = "postgres"
  engine_version = "16.1"
  instance_class = "db.r6g.large"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type         = "gp3"
  storage_encrypted    = true

  db_name  = "tracktracedb"
  username = var.db_username
  password = var.db_password

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  multi_az               = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  performance_insights_enabled = true
  monitoring_interval          = 60
  monitoring_role_arn         = aws_iam_role.rds_monitoring.arn

  tags = {
    Name        = "TrackTrace EventStore"
    Environment = var.environment
    Service     = "track-trace"
  }
}

# Base de Datos Read Model
resource "aws_rds_instance" "read_model" {
  identifier     = "tracktrace-readmodel-${var.environment}"
  engine         = "postgres"
  engine_version = "16.1"
  instance_class = "db.t4g.medium"

  allocated_storage = 50
  storage_type     = "gp3"
  storage_encrypted = true

  db_name  = "tracktraceread"
  username = var.read_db_username
  password = var.read_db_password

  backup_retention_period = 3
  multi_az               = false
  publicly_accessible    = false

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  tags = {
    Name        = "TrackTrace ReadModel"
    Environment = var.environment
    Service     = "track-trace"
  }
}

# ECS Service
resource "aws_ecs_service" "tracktrace_api" {
  name            = "tracktrace-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.tracktrace_api.arn
  desired_count   = 3

  launch_type = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [aws_security_group.api.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tracktrace_api.arn
    container_name   = "tracktrace-api"
    container_port   = 8080
  }

  service_registries {
    registry_arn = aws_service_discovery_service.tracktrace_api.arn
  }

  tags = {
    Environment = var.environment
    Service     = "track-trace"
  }
}
```

### 7.3.2 Valores de Helm Chart

```yaml
# values.yaml
replicaCount: 3

image:
  repository: tlm/track-trace-api
  tag: "1.0.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8080
  targetPort: 8080

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/use-regex: "true"
  hosts:
    - host: api.tracktrace.talma.pe
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: tracktrace-api-tls
      hosts:
        - api.tracktrace.talma.pe

resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector:
  kubernetes.io/arch: amd64

tolerations: []

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values:
                  - track-trace-api
          topologyKey: kubernetes.io/hostname

# ConfigMap
configMap:
  data:
    appsettings.json: |
      {
        "Authentication": {
          "Authority": "https://identity.talma.pe"
        },
        "EventSourcing": {
          "SnapshotFrequency": 100
        },
        "Monitoring": {
          "OpenTelemetry": {
            "ServiceName": "track-trace-api"
          }
        }
      }
```

## 7.4 Migración y Versionado

### 7.4.1 Migraciones de Base de Datos

```csharp
// Migración de Esquema Event Store
public class InitialEventStoreMigration : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // Events table
        migrationBuilder.CreateTable(
            name: "events",
            columns: table => new
            {
                id = table.Column<long>(type: "bigint", nullable: false)
                    .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                stream_id = table.Column<string>(type: "varchar(255)", nullable: false),
                version = table.Column<long>(type: "bigint", nullable: false),
                event_type = table.Column<string>(type: "varchar(255)", nullable: false),
                data = table.Column<string>(type: "jsonb", nullable: false),
                metadata = table.Column<string>(type: "jsonb", nullable: true),
                timestamp = table.Column<DateTimeOffset>(type: "timestamptz", nullable: false),
                correlation_id = table.Column<Guid>(type: "uuid", nullable: true),
                causation_id = table.Column<Guid>(type: "uuid", nullable: true)
            },
            constraints: table =>
            {
                table.PrimaryKey("pk_events", x => x.id);
                table.UniqueConstraint("uq_events_stream_version", x => new { x.stream_id, x.version });
            });

        // Indexes for performance
        migrationBuilder.CreateIndex(
            name: "ix_events_stream_id",
            table: "events",
            column: "stream_id");

        migrationBuilder.CreateIndex(
            name: "ix_events_timestamp",
            table: "events",
            column: "timestamp");

        migrationBuilder.CreateIndex(
            name: "ix_events_event_type",
            table: "events",
            column: "event_type");

        // Snapshots table
        migrationBuilder.CreateTable(
            name: "snapshots",
            columns: table => new
            {
                stream_id = table.Column<string>(type: "varchar(255)", nullable: false),
                version = table.Column<long>(type: "bigint", nullable: false),
                data = table.Column<string>(type: "jsonb", nullable: false),
                timestamp = table.Column<DateTimeOffset>(type: "timestamptz", nullable: false)
            },
            constraints: table =>
            {
                table.PrimaryKey("pk_snapshots", x => x.stream_id);
            });
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable(name: "snapshots");
        migrationBuilder.DropTable(name: "events");
    }
}
```

### 7.4.2 Event Schema Evolution

```csharp
// Event versioning strategy
public interface IEventUpgrader
{
    bool CanUpgrade(string eventType, int version);
    DomainEvent Upgrade(string eventData, string eventType, int version);
}

public class FlightStatusEventUpgrader : IEventUpgrader
{
    public bool CanUpgrade(string eventType, int version)
    {
        return eventType == "FlightStatusChanged" && version < 2;
    }

    public DomainEvent Upgrade(string eventData, string eventType, int version)
    {
        if (version == 1)
        {
            var v1Event = JsonSerializer.Deserialize<FlightStatusChangedV1>(eventData);

            // Transform to V2 format
            return new FlightStatusChangedV2
            {
                FlightId = v1Event.FlightId,
                OldStatus = MapOldStatus(v1Event.Status),
                NewStatus = MapNewStatus(v1Event.NewStatus),
                Timestamp = v1Event.Timestamp,
                Reason = v1Event.Reason ?? "Not specified", // New required field
                UpdatedBy = "system", // New required field
                // New fields with defaults
                LocationCode = v1Event.Location ?? "UNKNOWN",
                DelayMinutes = v1Event.DelayMinutes ?? 0
            };
        }

        throw new InvalidOperationException($"Cannot upgrade version {version}");
    }
}
```

## 7.5 Estrategia de Deployment

### 7.5.1 Despliegue Blue-Green

```yaml
# Estrategia de despliegue Blue-Green
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: tracktrace-api-rollout
spec:
  replicas: 6
  strategy:
    blueGreen:
      activeService: tracktrace-api-active
      previewService: tracktrace-api-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
          - templateName: success-rate
        args:
          - name: service-name
            value: tracktrace-api-preview
      postPromotionAnalysis:
        templates:
          - templateName: success-rate
        args:
          - name: service-name
            value: tracktrace-api-active
  selector:
    matchLabels:
      app: tracktrace-api
  template:
    metadata:
      labels:
        app: tracktrace-api
    spec:
      containers:
        - name: tracktrace-api
          image: tlm/track-trace-api:latest
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
```

### 7.5.2 Pipeline de CI/CD

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy Track & Trace API

on:
  push:
    branches: [main, develop]
    paths: ['src/TLM.Services.TrackTrace/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0.x'

      - name: Restore dependencies
        run: dotnet restore src/TLM.Services.TrackTrace/TLM.Services.TrackTrace.sln

      - name: Build
        run: dotnet build src/TLM.Services.TrackTrace/TLM.Services.TrackTrace.sln --no-restore

      - name: Unit Tests
        run: |
          dotnet test src/TLM.Services.TrackTrace/tests/Unit \
            --no-build --verbosity normal \
            --collect:"XPlat Code Coverage" \
            --results-directory ./coverage

      - name: Integration Tests
        run: |
          docker-compose -f docker-compose.test.yml up -d
          dotnet test src/TLM.Services.TrackTrace/tests/Integration \
            --no-build --verbosity normal
          docker-compose -f docker-compose.test.yml down

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  security:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: 'src/TLM.Services.TrackTrace'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  build-and-push:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.REGISTRY_URL }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ secrets.REGISTRY_URL }}/tlm/track-trace-api
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: src/TLM.Services.TrackTrace
          file: src/TLM.Services.TrackTrace/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    runs-on: ubuntu-latest
    needs: build-and-push
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Kubernetes
        uses: azure/k8s-deploy@v1
        with:
          manifests: |
            k8s/deployment.yml
            k8s/service.yml
            k8s/ingress.yml
          images: |
            ${{ needs.build-and-push.outputs.image-tag }}
```

### 7.5.3 Monitoring y Observabilidad

```csharp
// Application metrics
public class TrackTraceMetrics
{
    private readonly IMetricsLogger _metricsLogger;
    private readonly Counter<long> _eventsProcessed;
    private readonly Histogram<double> _eventProcessingDuration;
    private readonly Gauge<int> _activeStreams;

    public TrackTraceMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("TLM.Services.TrackTrace");

        _eventsProcessed = meter.CreateCounter<long>(
            "events_processed_total",
            description: "Total number of events processed");

        _eventProcessingDuration = meter.CreateHistogram<double>(
            "event_processing_duration_seconds",
            description: "Duration of event processing");

        _activeStreams = meter.CreateGauge<int>(
            "active_streams_count",
            description: "Number of currently active event streams");
    }

    public void RecordEventProcessed(string eventType, string tenantId, double duration)
    {
        _eventsProcessed.Add(1,
            new("event_type", eventType),
            new("tenant_id", tenantId));

        _eventProcessingDuration.Record(duration,
            new("event_type", eventType),
            new("tenant_id", tenantId));
    }

    public void SetActiveStreams(int count)
    {
        _activeStreams.Record(count);
    }
}

// Health checks implementation
public class EventStoreHealthCheck : IHealthCheck
{
    private readonly IEventStore _eventStore;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Test connection by attempting to read a system stream
            await _eventStore.GetEventsAsync("$system-health-check", 0);
            return HealthCheckResult.Healthy("Event store is responding");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy(
                "Event store is not responding", ex);
        }
    }
}

// Distributed tracing
public class EventHandlerTracing
{
    private static readonly ActivitySource ActivitySource = new("TLM.Services.TrackTrace");

    public async Task<T> TraceEventHandling<T>(string eventType, string streamId, Func<Task<T>> handler)
    {
        using var activity = ActivitySource.StartActivity($"handle-{eventType}");
        activity?.SetTag("stream.id", streamId);
        activity?.SetTag("event.type", eventType);

        try
        {
            var result = await handler();
            activity?.SetStatus(ActivityStatusCode.Ok);
            return result;
        }
        catch (Exception ex)
        {
            activity?.SetStatus(ActivityStatusCode.Error, ex.Message);
            throw;
        }
    }
}
```

## 7.6 Consideraciones de Seguridad

### 7.6.1 Configuración de Seguridad de Contenedores

```dockerfile
# Dockerfile reforzado en seguridad
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS runtime

# Instalar actualizaciones de seguridad
RUN apk upgrade --no-cache

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -S -D -H -u 1001 -h /app -s /sbin/nologin -G appuser appuser

# Set up application directory with proper permissions
WORKDIR /app
COPY --from=publish --chown=appuser:appuser /app/publish .

# Remove unnecessary packages and files
RUN apk del --no-cache \
    && rm -rf /var/cache/apk/* \
    && rm -rf /tmp/*

# Switch to non-root user
USER 1001

# Configuraciones de seguridad
ENV ASPNETCORE_URLS=http://+:8080
ENV DOTNET_RUNNING_IN_CONTAINER=true
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=true

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

EXPOSE 8080
ENTRYPOINT ["dotnet", "TLM.Services.TrackTrace.API.dll"]
```

### 7.6.2 Políticas de Red

```yaml
# Network policy for Track & Trace API
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tracktrace-api-netpol
  namespace: corporate-services
spec:
  podSelector:
    matchLabels:
      app: tracktrace-api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
    - from:
        - podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: databases
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - namespaceSelector:
            matchLabels:
              name: identity-services
      ports:
        - protocol: TCP
          port: 8080
    - to: []
      ports:
        - protocol: TCP
          port: 53
        - protocol: UDP
          port: 53
```

## 7.7 Solución de Problemas y Depuración

### 7.7.1 Configuración de Logging

```csharp
// Configuración de logging estructurado
public static class LoggingConfiguration
{
    public static IServiceCollection AddStructuredLogging(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        Log.Logger = new LoggerConfiguration()
            .ReadFrom.Configuration(configuration)
            .Enrich.FromLogContext()
            .Enrich.WithProperty("Service", "track-trace-api")
            .Enrich.WithProperty("Version", Assembly.GetEntryAssembly()?.GetName().Version?.ToString())
            .WriteTo.Console(outputTemplate:
                "[{Timestamp:HH:mm:ss} {Level:u3}] [{Service}] {Message:lj} {Properties:j}{NewLine}{Exception}")
            .WriteTo.OpenTelemetry(options =>
            {
                options.Endpoint = configuration["Logging:OpenTelemetry:Endpoint"];
                options.ResourceAttributes = new Dictionary<string, object>
                {
                    ["service.name"] = "track-trace-api",
                    ["service.version"] = "1.0.0",
                };
            })
            .CreateLogger();

        services.AddSerilog();
        return services;
    }
}

// Event handling logging
public class EventHandlerLoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ILogger<EventHandlerLoggingBehavior<TRequest, TResponse>> _logger;

    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken cancellationToken)
    {
        var requestName = typeof(TRequest).Name;
        var requestId = Guid.NewGuid();

        _logger.LogInformation("Starting request {RequestName} with ID {RequestId}",
            requestName, requestId);

        var stopwatch = Stopwatch.StartNew();
        try
        {
            var response = await next();
            stopwatch.Stop();

            _logger.LogInformation("Completed request {RequestName} with ID {RequestId} in {ElapsedMs}ms",
                requestName, requestId, stopwatch.ElapsedMilliseconds);

            return response;
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, "Request {RequestName} with ID {RequestId} failed after {ElapsedMs}ms",
                requestName, requestId, stopwatch.ElapsedMilliseconds);
            throw;
        }
    }
}
```

### 7.7.2 Debugging Tools

```bash
#!/bin/bash
# debug-toolkit.sh - Tools para debugging del sistema

# Verificar salud de los componentes
check_health() {
    echo "=== Health Check ==="
    kubectl get pods -n corporate-services -l app=tracktrace-api
    echo ""
    kubectl exec -n corporate-services deployment/tracktrace-api -- \
        curl -s http://localhost:8080/health | jq '.'
}

# Revisar logs recientes
check_logs() {
    echo "=== Recent Logs ==="
    kubectl logs -n corporate-services deployment/tracktrace-api \
        --tail=100 --since=10m
}

# Verificar métricas de performance
check_metrics() {
    echo "=== Performance Metrics ==="
    kubectl exec -n corporate-services deployment/tracktrace-api -- \
        curl -s http://localhost:9090/metrics | grep -E "(events_processed|processing_duration)"
}

# Verificar configuración
check_config() {
    echo "=== Configuration ==="
    kubectl describe configmap -n corporate-services tracktrace-config
}

# Análisis de eventos en el event store
analyze_events() {
    local stream_id=$1
    echo "=== Event Analysis for Stream: $stream_id ==="

    # Conectar a la base de datos y consultar eventos
    kubectl exec -it -n databases postgres-0 -- \
        psql -U tracktraceuser -d tracktracedb -c \
        "SELECT event_type, timestamp, version FROM events WHERE stream_id = '$stream_id' ORDER BY version;"
}

# Función principal
case "$1" in
    "health")
        check_health
        ;;
    "logs")
        check_logs
        ;;
    "metrics")
        check_metrics
        ;;
    "config")
        check_config
        ;;
    "events")
        analyze_events "$2"
        ;;
    *)
        echo "Uso: $0 {health|logs|metrics|config|events <stream_id>}"
        exit 1
        ;;
esac
```

---

**Referencias:**

- [Event Sourcing Patterns](https://martinfowler.com/eaaDev/EventSourcing.html)
- [CQRS Journey](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10))
- [.NET Application Architecture Guides](https://docs.microsoft.com/en-us/dotnet/architecture/)
- [Kubernetes Mejores Prácticas](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Docker Security Mejores Prácticas](https://docs.docker.com/develop/security-best-practices/)
