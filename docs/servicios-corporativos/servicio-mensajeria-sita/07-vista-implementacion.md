# 7. Vista de implementación

![Vista de implementación del Mensajeria SITA](/diagrams/servicios-corporativos/sita_messaging_system_deployment.png)
*Figura 7.1: Implementación de Componentes de principales del sistema*

## 7.1 Estructura del proyecto

| Componente | Ubicación | Tecnología |
|------------|-------------|-------------|
| **Event Processor** | /src/SitaEventProcessor | .NET 8 Worker |
| **Sender** | /src/SitaSender | .NET 8 Worker |
| **PostgreSQL** | AWS RDS | PostgreSQL 15+ |
| **File Storage** | AWS EFS | Sistema archivos |

## 7.2 Dependencias principales

| Dependencia | Versión | Propósito |
|-------------|---------|----------|
| **Entity Framework** | 8.0+ | ORM |
| **RazorEngine** | 4.0+ | Plantillas SITA |
| **Serilog** | 3.0+ | Logging |
| **Polly** | 7.0+ | Resiliencia |

## 7.1 Estructura del sistema

### 7.1.1 Organización de código

```
src/
├── TLM.Services.SitaMessaging.API/           # REST API Layer
│   ├── Controllers/                          # API Controllers
│   ├── Middleware/                           # HTTP Middleware
│   ├── Configuration/                        # DI & Startup Config
│   └── Program.cs                           # Application Entry
├── TLM.Services.SitaMessaging.Application/   # Application Layer
│   ├── Commands/                            # CQRS Commands
│   ├── Queries/                             # CQRS Queries
│   ├── Handlers/                            # Command/Query Handlers
│   ├── Services/                            # Application Services
│   ├── Validators/                          # FluentValidation
│   └── DTOs/                                # Data Transfer Objects
├── TLM.Services.SitaMessaging.Domain/        # Domain Layer
│   ├── Entities/                            # Domain Entities
│   ├── ValueObjects/                        # Value Objects
│   ├── Services/                            # Domain Services
│   ├── Repositories/                        # Repository Interfaces
│   └── Events/                              # Domain Events
├── TLM.Services.SitaMessaging.Infrastructure/ # Infrastructure Layer
│   ├── Persistence/                         # Database Implementation
│   ├── SITA/                                # SITA Protocol Adapter
│   ├── Messaging/                           # Kafka Integration
│   ├── Authentication/                      # OAuth2/JWT
│   └── Monitoring/                          # Telemetry & Metrics
└── TLM.Services.SitaMessaging.Tests/         # Test Projects
    ├── Unit/                                # Unit Tests
    ├── Integration/                         # Integration Tests
    └── Contract/                            # Contract Tests with SITA
```

### 7.1.2 SITA Protocol Implementation

```csharp
// Core SITA protocol abstraction
public interface ISitaProtocolAdapter
{
    Task<SitaConnection> EstablishConnectionAsync(SitaEndpoint endpoint);
    Task<SendResult> SendMessageAsync(SitaMessage message);
    Task<ReceiveResult> ReceiveMessagesAsync(CancellationToken cancellationToken);
    Task DisconnectAsync(SitaConnection connection);
}

// Type B protocol implementation
public class SitaTypeBAdapter : ISitaProtocolAdapter
{
    private readonly ISitaConnectionPool _connectionPool;
    private readonly ISitaMessageFormatter _formatter;

    public async Task<SendResult> SendMessageAsync(SitaMessage message)
    {
        using var connection = await _connectionPool.AcquireAsync();

        // Format message according to SITA Type B specifications
        var formattedMessage = await _formatter.FormatAsync(message);

        // Send with acknowledgment handling
        var response = await connection.SendWithAckAsync(formattedMessage);

        return new SendResult
        {
            MessageId = message.Id,
            Status = response.IsAcknowledged ? SendStatus.Sent : SendStatus.Failed,
            AckCode = response.AcknowledgmentCode,
            Timestamp = response.Timestamp
        };
    }
}
```

## 7.2 Configuración de despliegue

### 7.2.1 Docker Configuration

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy and restore
COPY ["src/TLM.Services.SitaMessaging.API/", "SitaMessaging.API/"]
COPY ["src/TLM.Services.SitaMessaging.Application/", "SitaMessaging.Application/"]
COPY ["src/TLM.Services.SitaMessaging.Domain/", "SitaMessaging.Domain/"]
COPY ["src/TLM.Services.SitaMessaging.Infrastructure/", "SitaMessaging.Infrastructure/"]

RUN dotnet restore "SitaMessaging.API/TLM.Services.SitaMessaging.API.csproj"

# Build
RUN dotnet build "SitaMessaging.API/TLM.Services.SitaMessaging.API.csproj" -c Release

# Publish
FROM build AS publish
RUN dotnet publish "SitaMessaging.API/TLM.Services.SitaMessaging.API.csproj" -c Release -o /app/publish

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# SITA protocol requirements
RUN apt-get update && apt-get install -y \
    telnet \
    netcat-openbsd \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Security
RUN adduser --disabled-password --home /app --gecos '' appuser && chown -R appuser /app
USER appuser

COPY --from=publish /app/publish .
EXPOSE 8080

# Health check with SITA connectivity
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "TLM.Services.SitaMessaging.API.dll"]
```

### 7.2.2 Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sita-messaging-api
  namespace: corporate-services
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sita-messaging-api
  template:
    metadata:
      labels:
        app: sita-messaging-api
    spec:
      containers:
      - name: api
        image: tlm/sita-messaging-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: ASPNETCORE_ENVIRONMENT
          value: "Production"
        - name: ConnectionStrings__Database
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: sita-messaging-connection
        - name: SITA__Endpoints__Primary
          valueFrom:
            configMapKeyRef:
              name: sita-config
              key: primary-endpoint
        - name: SITA__Authentication__Certificate
          valueFrom:
            secretKeyRef:
              name: sita-certs
              key: client-certificate
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        # SITA network access requirements
        securityContext:
          capabilities:
            add: ["NET_RAW", "NET_ADMIN"]
```

### 7.2.3 Terraform Infrastructure

```hcl
# ECS Cluster for SITA Messaging
resource "aws_ecs_cluster" "sita_messaging" {
  name = "corporate-services-sita-messaging"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Task definition with SITA-specific networking
resource "aws_ecs_task_definition" "sita_messaging_api" {
  family                   = "sita-messaging-api"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = 1024
  memory                  = 2048

  container_definitions = jsonencode([
    {
      name  = "sita-messaging-api"
      image = "tlm/sita-messaging-api:latest"

      # SITA network configuration
      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        },
        {
          containerPort = 9999  # SITA protocol port
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ASPNETCORE_ENVIRONMENT"
          value = "Production"
        }
      ]

      secrets = [
        {
          name      = "ConnectionStrings__Database"
          valueFrom = aws_secretsmanager_secret.db_connection.arn
        },
        {
          name      = "SITA__Authentication__Certificate"
          valueFrom = aws_secretsmanager_secret.sita_certificate.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.sita_messaging.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# Database cluster for SITA message storage
resource "aws_rds_cluster" "sita_messaging_db" {
  cluster_identifier     = "sita-messaging-cluster"
  engine                = "aurora-postgresql"
  engine_version        = "13.7"
  database_name         = "sita_messaging"
  master_username       = "sita_user"
  manage_master_user_password = true

  # High disponibilidad for critical SITA operations
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  backup_retention_period = 14
  preferred_backup_window = "03:00-04:00"

  storage_encrypted = true
  kms_key_id       = aws_kms_key.sita_messaging.arn
}
```

## 7.3 Configuración específica SITA

### 7.3.1 Application Configuration

```json
{
  "SITA": {
    "Endpoints": {
      "Primary": {
        "Host": "sita-primary.example.com",
        "Port": 9999,
        "Protocol": "TypeB",
        "Timeout": "00:00:30"
      },
      "Secondary": {
        "Host": "sita-secondary.example.com",
        "Port": 9999,
        "Protocol": "TypeB",
        "Timeout": "00:00:30"
      }
    },
    "Authentication": {
      "CertificatePath": "/app/certs/sita-client.p12",
      "CertificatePassword": "${SITA_CERT_PASSWORD}",
      "UserId": "${SITA_USER_ID}",
      "AddressCode": "${SITA_ADDRESS_CODE}"
    },
    "MessageTypes": {
      "FPL": {
        "MaxLength": 2048,
        "RequiredFields": ["Aircraft", "Departure", "Destination"],
        "ValidationRules": "ICAO_FPL"
      },
      "MVT": {
        "MaxLength": 1024,
        "RequiredFields": ["Flight", "Registration", "Movement"],
        "ValidationRules": "IATA_MVT"
      }
    },
    "Retry": {
      "MaxAttempts": 3,
      "DelayPattern": "Exponential",
      "BaseDelay": "00:00:02"
    }
  },
  "MessageStorage": {
    "ConnectionString": "Host=sita-db;Database=sita_messaging;Username=sita_user;Password=${DB_PASSWORD}",
    "RetentionPolicyDays": 2555, // 7 years for aviation compliance
    "PartitionStrategy": "Monthly",
    "CompressionEnabled": true
  },
  "Monitoring": {
    "SITA": {
      "ConnectionHealthCheck": "00:00:30",
      "MessageSuccessRate": true,
      "LatencyTracking": true
    }
  }
}
```

### 7.3.2 SITA Certificate Management

```csharp
public class SitaCertificateManager : ICertificateManager
{
    private readonly IOptions<SitaOptions> _options;
    private readonly ILogger<SitaCertificateManager> _logger;

    public async Task<X509Certificate2> GetClientCertificateAsync()
    {
        var certificatePath = _options.Value.Authentication.CertificatePath;
        var password = _options.Value.Authentication.CertificatePassword;

        if (!File.Exists(certificatePath))
        {
            _logger.LogError("SITA client certificate not found at {Path}", certificatePath);
            throw new FileNotFoundException($"SITA certificate not found: {certificatePath}");
        }

        var certificate = new X509Certificate2(certificatePath, password);

        // Validate certificate expiration
        if (certificate.NotAfter < DateTime.UtcNow.AddDays(30))
        {
            _logger.LogWarning("SITA certificate expires soon: {ExpiryDate}", certificate.NotAfter);
            // Trigger certificate renewal process
            await _certificateRenewalService.RequestRenewalAsync(certificate);
        }

        return certificate;
    }
}
```

## 7.4 Patrones de implementación

### 7.4.1 Message Handler Factory

```csharp
public class SitaMessageHandlerFactory : IMessageHandlerFactory
{
    private readonly IServiceProvider _serviceProvider;
    private readonly Dictionary<string, Type> _handlerTypes;

    public SitaMessageHandlerFactory(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
        _handlerTypes = new Dictionary<string, Type>
        {
            ["FPL"] = typeof(FlightPlanHandler),
            ["MVT"] = typeof(MovementHandler),
            ["DLA"] = typeof(DelayHandler),
            ["DEP"] = typeof(DepartureHandler),
            ["ARR"] = typeof(ArrivalHandler)
        };
    }

    public ISitaMessageHandler CreateHandler(string messageType)
    {
        if (!_handlerTypes.TryGetValue(messageType, out var handlerType))
        {
            throw new UnsupportedMessageTypeException($"No handler for message type: {messageType}");
        }

        return (ISitaMessageHandler)_serviceProvider.GetRequiredService(handlerType);
    }
}
```

### 7.4.2 Connection Pool Implementation

```csharp
public class SitaConnectionPool : ISitaConnectionPool, IDisposable
{
    private readonly ConcurrentQueue<ISitaConnection> _availableConnections = new();
    private readonly ConcurrentDictionary<string, ISitaConnection> _activeConnections = new();
    private readonly SemaphoreSlim _semaphore;
    private readonly ILogger<SitaConnectionPool> _logger;

    public SitaConnectionPool(IOptions<SitaOptions> options, ILogger<SitaConnectionPool> logger)
    {
        _logger = logger;
        var maxConnections = options.Value.MaxConnections;
        _semaphore = new SemaphoreSlim(maxConnections, maxConnections);

        // Pre-create connection pool
        _ = Task.Run(InitializePoolAsync);
    }

    public async Task<ISitaConnection> AcquireAsync()
    {
        await _semaphore.WaitAsync();

        if (_availableConnections.TryDequeue(out var connection) && connection.IsConnected)
        {
            _activeConnections.TryAdd(connection.Id, connection);
            return connection;
        }

        // Create new connection if pool is empty
        connection = await CreateConnectionAsync();
        _activeConnections.TryAdd(connection.Id, connection);
        return connection;
    }

    public async Task ReleaseAsync(ISitaConnection connection)
    {
        _activeConnections.TryRemove(connection.Id, out _);

        if (connection.IsConnected && !connection.HasErrors)
        {
            _availableConnections.Enqueue(connection);
        }
        else
        {
            await connection.DisposeAsync();
        }

        _semaphore.Release();
    }
}
```

## 7.5 Testing Strategy

### 7.5.1 Contract Testing con SITA

```csharp
[TestClass]
public class SitaProtocolContractTests
{
    [TestMethod]
    public async Task FlightPlanMessage_ShouldConformToICAOStandards()
    {
        // Arrange
        var flightPlan = new FlightPlanMessage
        {
            Aircraft = "B738",
            Departure = "LIMA",
            Destination = "SPJC",
            Route = "DCT"
        };

        // Act
        var sitaFormat = await _formatter.FormatAsync(flightPlan);

        // Assert
        Assert.IsTrue(IsValidICAOFormat(sitaFormat));
        Assert.IsTrue(sitaFormat.StartsWith("(FPL"));
        Assert.IsTrue(sitaFormat.Contains("-B738/"));
    }

    [TestMethod]
    public async Task SitaConnection_ShouldHandleNetworkInterruption()
    {
        // Arrange
        var connection = await _connectionPool.AcquireAsync();

        // Act - Simulate network interruption
        await SimulateNetworkFailure();
        var reconnectResult = await connection.ReconnectAsync();

        // Assert
        Assert.IsTrue(reconnectResult.IsSuccess);
        Assert.IsTrue(connection.IsConnected);
    }
}
```

### 7.5.2 Load Testing

```csharp
[TestClass]
public class SitaMessagingLoadTests
{
    [TestMethod]
    public async Task ShouldHandle1000MessagesPerMinute()
    {
        // Arrange
        var messages = GenerateTestMessages(1000);
        var stopwatch = Stopwatch.StartNew();

        // Act
        var tasks = messages.Select(msg => _sitaService.SendMessageAsync(msg));
        var results = await Task.WhenAll(tasks);

        stopwatch.Stop();

        // Assert
        Assert.IsTrue(stopwatch.Elapsed < TimeSpan.FromMinutes(1));
        Assert.IsTrue(results.All(r => r.IsSuccess));
    }
}
```
