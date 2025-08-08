# 7. Vista de implementación

## 7.1 Estructura del proyecto

| Componente | Ubicación | Tecnología |
|------------|-------------|-------------|
| **Notification API** | `/src/NotificationApi` | `.NET 8 Web API` |
| **Notification Processor** | `/src/NotificationProcessor` | `.NET 8 Worker` |
| **PostgreSQL** | `AWS RDS` | `PostgreSQL 15+` |
| **Redis** | `AWS ElastiCache` | `Redis 7+` |
| **File Storage** | `AWS EFS` | `Sistema archivos` |

## 7.2 Dependencias principales

| Dependencia | Versión | Propósito |
|-------------|---------|----------|
| **Entity Framework** | `8.0+` | ORM |
| **FluentValidation** | `11.0+` | Validación |
| **RazorEngine** | `4.0+` | Plantillas |
| **Serilog** | `3.0+` | Logging |

## 7.3 Infraestructura de Despliegue

### Arquitectura de Contenedores

#### Servicio API de Notificación

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: notification-api
  template:
    spec:
      containers:
      - name: notification-api
        image: corporativo/notification-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: KAFKA_BROKERS
          value: "eventbus-cluster:9092"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### Servicio Procesador de Notificación

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-processor
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: notification-processor
        image: corporativo/notification-processor:latest
        env:
        - name: SENDGRID_API_KEY
          valueFrom:
            secretKeyRef:
              name: email-secrets
              key: sendgrid-key
        - name: TWILIO_AUTH_TOKEN
          valueFrom:
            secretKeyRef:
              name: sms-secrets
              key: twilio-token
        - name: REDIS_URL
          value: "redis-cluster:6379"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "400m"
```

### Infraestructura de Cola de Mensajes

```yaml
Event Bus agnóstico Cluster:
  Brokers: 3 instances
  Partitions per Topic: 12
  Replication Factor: 3
  Retention: 7 days

Topics:
  notification-requests:
    partitions: 12
    config:
      cleanup.policy: delete
      retention.ms: 604800000  # 7 days

  notification-status:
    partitions: 6
    config:
      cleanup.policy: compact
      retention.ms: 2592000000  # 30 days
```

## 7.4 Deployment Environments

### Entorno de Desarrollo

```yaml
Environment: Development
Infrastructure:
  - Kubernetes: minikube
  - Database: PostgreSQL (single instance)
  - Message Queue: Kafka (single broker)
  - Cache: Redis (single instance)
  - Providers: Sandbox/test endpoints

Configuration:
  - Email Provider: Mailhog (local testing)
  - SMS Provider: Mock service
  - Monitoring: Basic health checks
  - Logs: Console output + local files
```

### Entorno de Staging

```yaml
Environment: Staging
Infrastructure:
  - Kubernetes: AWS EKS (3 nodes)
  - Database: AWS RDS PostgreSQL
  - Message Queue: AWS MSK (Kafka)
  - Cache: AWS ElastiCache Redis
  - Providers: Test environments

Configuration:
  - Email Provider: SendGrid test mode
  - SMS Provider: Twilio test credentials
  - Monitoring: Prometheus + Grafana
  - Logs: CloudWatch + centralized logging
```

### Entorno de Producción

```yaml
Environment: Production
Infrastructure:
  - Kubernetes: AWS EKS (9 nodes, 3 AZs)
  - Database: AWS RDS PostgreSQL (Multi-AZ)
  - Message Queue: AWS MSK (Multi-AZ)
  - Cache: AWS ElastiCache Redis (Cluster)
  - CDN: CloudFront for static assets

Configuration:
  - Email Provider: SendGrid + SES (failover)
  - SMS Provider: Twilio + SNS (failover)
  - Push Provider: FCM + APNS
  - WhatsApp: WhatsApp Business API
```

## 7.5 Provider Integration Architecture

### Multi-Provider Strategy

```yaml
Email Providers:
  Primary: SendGrid
    - Volume: 80% of traffic
    - SLA: 99.9% uptime
    - Features: Advanced analytics, templates

  Secondary: Amazon SES
    - Volume: 20% of traffic
    - SLA: 99.99% uptime
    - Features: Cost optimization, AWS integration

  Failover: Mailgun
    - Volume: Emergency only
    - Features: European compliance

SMS Providers:
  Primary: Twilio
    - Coverage: Global
    - Features: Short codes, long codes

  Secondary: AWS SNS
    - Coverage: Major regions
    - Features: Cost optimization
```

### Provider Abstraction Layer

```csharp
public interface INotificationProvider
{
    Task<DeliveryResult> SendAsync(NotificationMessage message);
    Task<HealthStatus> CheckHealthAsync();
    string ProviderName { get; }
    NotificationChannel SupportedChannel { get; }
}

public class EmailProviderFactory
{
    public IEmailProvider GetProvider(EmailProviderType type)
    {
        return type switch
        {
            EmailProviderType.SendGrid => new SendGridProvider(),
            EmailProviderType.SES => new SesProvider(),
            EmailProviderType.Mailgun => new MailgunProvider(),
            _ => throw new NotSupportedException()
        };
    }
}
```

## 7.6 Security Implementation

### Network Security

```yaml
Network Policies:
  - API Tier: Ingress from ALB only
  - Processor Tier: No direct external access
  - Database Tier: Access from app tiers only
  - Cache Tier: Internal access only

Security Groups:
  notification-api:
    - Ingress: Port 8080 from ALB
    - Egress: Database, Kafka, Redis

  notification-processor:
    - Ingress: None (pull-based)
    - Egress: External providers, Kafka, Redis

```

### Secrets Management

```yaml
AWS Secrets Manager:
  email-providers:
    sendgrid-api-key: "encrypted-key"
    ses-credentials: "access-key-id + secret"

  sms-providers:
    twilio-auth-token: "encrypted-token"
    sns-credentials: "aws-credentials"

  push-providers:
    fcm-server-key: "firebase-key"

    apns-certificate: "apple-certificate"
```

### Data Encryption

```yaml
Encryption Strategy:
  At Rest:
    - Database: AES-256 encryption
    - Message Queue: Kafka encryption
    - Cache: Redis AUTH + TLS

  In Transit:
    - API: TLS 1.3
    - Provider APIs: TLS 1.2+
    - Internal: mTLS (service mesh)

  PII Protection:
    - Email addresses: Hashed for analytics
    - Phone numbers: Encrypted in database
    - Message content: Encrypted until delivery

```

## 7.7 Monitoring & Observability

### Metrics Collection

```yaml
Prometheus Metrics:
  Business Metrics:
    - notifications_sent_total
    - notifications_delivered_total
    - notifications_failed_total
    - delivery_time_seconds

  Technical Metrics:
    - api_requests_total

    - processor_queue_depth
    - provider_response_time
    - cache_hit_ratio
```

### Logging Strategy

```yaml
Registro Estructurado:
  Format: JSON with correlation IDs
  Fields:
    - timestamp
    - level
    - service
    - correlationId
    - notificationId
    - channel
    - provider
    - tenantId
    - message

Log Levels:
  - DEBUG: Development only

  - INFO: Successful operations
  - WARN: Recoverable errors
  - ERROR: Failed operations
  - FATAL: Service unavailable
```

### Trazado Distribuido

```yaml
Jaeger Configuration:
  Sampling:
    - Production: 1% of requests
    - Staging: 10% of requests
    - Development: 100% of requests

  Span Creation:
    - API requests

    - Message processing
    - Provider calls
    - Database operations
```

## 7.8 CI/CD Pipeline

### Build Pipeline

```yaml
GitHub Actions Workflow:

  Build Stage:
    - Checkout code
    - Setup .NET 8 SDK
    - Restore dependencies
    - Run unit tests
    - Generate test coverage
    - SonarQube analysis
    - Build Docker images
    - Security scan (Trivy)
    - Push to registry

  Deploy Stage:
    - Validate Kubernetes manifests
    - Deploy to staging

    - Run integration tests
    - Load testing
    - Security testing
    - Manual approval for production
    - Blue-green deployment
    - Smoke tests
```

### Gestión de Configuración

```yaml
Environment Configuration:
  Development:
    ConfigMap: notification-config-dev
    Secrets: notification-secrets-dev


  Staging:
    ConfigMap: notification-config-staging
    Secrets: notification-secrets-staging

  Production:
    ConfigMap: notification-config-prod
    Secrets: notification-secrets-prod
```

### Database Migration Strategy

```yaml
Migration Approach:
  - Liquibase for schema versioning
  - Backward compatible changes
  - Blue-green deployment support
  - Rollback capability

Migration Pipeline:

  1. Validate migration scripts
  2. Apply to development database
  3. Run automated tests
  4. Apply to staging database
  5. Integration testing
  6. Production deployment (maintenance window)
```

## 7.9 Scaling Strategy

### Horizontal Scaling

```yaml
Auto-scaling Configuration:

  API Service:
    - Min replicas: 2
    - Max replicas: 10
    - CPU threshold: 70%

    - Memory threshold: 80%
    - Custom metric: API requests/second

  Processor Service:
    - Min replicas: 3
    - Max replicas: 20
    - Custom metric: Kafka lag
    - Scale up: Lag > 1000 messages
    - Scale down: Lag < 100 messages
```

### Message Queue Scaling

```yaml
Kafka Scaling:
  Partition Strategy:

    - Notification type based partitioning
    - Tenant-based partitioning for isolation
    - Time-based partitioning for analytics

  Consumer Groups:
    - One consumer group per notification type
    - Parallel processing within groups
    - Dead letter queues for failed messages
```

## 7.10 Disaster Recovery

### Backup Strategy

```yaml
Database Backups:
  - Automated daily backups
  - Point-in-time recovery (7 days)
  - Cross-region backup replication
  - Monthly backup testing

Message Queue Backups:
  - Topic configuration backup
  - Consumer offset backup
  - Schema registry backup
```

### Recovery Procedures

```yaml
Recovery Time Objectives:
  - Database failover: < 5 minutes
  - Application restart: < 10 minutes

  - Full region recovery: < 1 hour

Recovery Point Objectives:
  - Database: < 1 minute data loss
  - Message queue: Zero message loss
  - Configuration: Zero loss (GitOps)
```

## Referencias

- [Kubernetes Mejores Prácticas](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Microservices Deployment Patterns](https://microservices.io/patterns/deployment/)
- [Event Bus agnóstico Operations](https://kafka.apache.org/documentation/#operations)
- [Arc42 Deployment View](https://docs.arc42.org/section-7/)
├── docker/
└── README.md

````markdown
## 7.2 Consideraciones de despliegue

- Despliegue en <span style="color:#1976d2"><b>AWS</b></span> usando <b>Docker</b> y <b>docker-compose</b>
- Uso de <b>pipelines CI/CD</b> para automatización
- Variables sensibles gestionadas por <code>secrets</code> y <code>Parameter Store</code>
- Versionado semántico (`semver`)
- Integración con <b>monitorización</b> y <b>logging centralizado</b>
````
