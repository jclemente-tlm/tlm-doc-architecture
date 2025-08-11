# 7. Vista De Implementación

## 7.1 Estructura Del Proyecto

| Componente             | Ubicación                   | Tecnología           |
|------------------------|-----------------------------|----------------------|
| Notification API       | `/src/NotificationApi`      | `.NET 8 Web API`, YARP|
| Notification Processor | `/src/NotificationProcessor`| `.NET 8 Worker`      |
| PostgreSQL             | `AWS RDS`                   | `PostgreSQL 15+`     |
| Redis                  | `AWS ElastiCache`           | `Redis 7+`           |
| File Storage           | `AWS EFS`                   | Sistema de archivos  |

## 7.2 Dependencias Principales

| Dependencia         | Versión   | Propósito     |
|---------------------|-----------|--------------|
| Entity Framework    | `8.0+`    | ORM          |
| FluentValidation    | `11.0+`   | Validación   |
| Mapster             | `7.0+`    | Mapeo objetos|
| RazorEngine         | `4.0+`    | Plantillas   |
| Serilog             | `3.0+`    | Logging      |
| OpenTelemetry       | `1.7+`    | Trazas       |

## 7.3 Infraestructura De Despliegue

### Contenedores Principales

- `Notification API`: expuesto vía YARP y ALB, escalable, acceso a base de datos y cola de mensajes.
- `Notification Processor`: worker para procesamiento asíncrono, acceso a proveedores externos y Redis.

#### Ejemplo de despliegue (Kubernetes)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-api
spec:
  replicas: 3
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

### Mensajería y Almacenamiento

- Event Bus agnóstico (`Kafka`): 3 brokers, 12 particiones por tópico, retención 7 días.
- Tópicos principales: `notification-requests` (delete, 7 días), `notification-status` (compact, 30 días).
- Almacenamiento de archivos: `AWS EFS`.

## 7.4 Entornos De Despliegue

- **Desarrollo:** `minikube`, PostgreSQL local, Kafka y Redis single instance, Mailhog, logs locales.
- **Staging:** `AWS EKS`, RDS, MSK, ElastiCache, SendGrid/Twilio test, Prometheus, Grafana, Loki, Jaeger, CloudWatch.
- **Producción:** `AWS EKS` multi-AZ, RDS multi-AZ, MSK, ElastiCache cluster, CloudFront, SendGrid+SES+Mailgun, Twilio+SNS+360dialog, FCM+APNS, WhatsApp Business API.

## 7.5 Integración Con Proveedores

- Email: SendGrid (primario), SES (secundario), Mailgun (emergencia).
- SMS: Twilio (primario), SNS (secundario), 360dialog (WhatsApp).
- Push: Firebase Cloud Messaging (FCM), Apple Push Notification Service (APNS).
- WhatsApp: 360dialog, WhatsApp Business API.

### Abstracción de proveedores

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

## 7.6 Seguridad

- Autenticación y autorización: Keycloak, validación JWT, control de roles y claims.
- Políticas de red: acceso restringido por capa (API, procesamiento, base de datos, cache).
- Grupos de seguridad: control de puertos y orígenes.
- Gestión de secretos: `AWS Secrets Manager` para credenciales de proveedores.
- Cifrado: AES-256 en reposo, TLS 1.3 en tránsito, mTLS interno, protección de PII (hash, cifrado).

## 7.7 Observabilidad Y Monitoreo

- Métricas: `Prometheus` (notificaciones enviadas, entregadas, fallidas, tiempos de entrega, uso de API, profundidad de cola, tiempos de respuesta de proveedores, cache hit ratio).
- Logging: `Serilog` + `Loki` (JSON, correlationId, niveles DEBUG/INFO/WARN/ERROR/FATAL).
- Trazas: `OpenTelemetry` + `Jaeger` (API, procesamiento, proveedores, base de datos; sampling adaptativo por entorno).
- Visualización: `Grafana`.

## 7.8 CI/CD Pipeline

- Build: GitHub Actions, .NET 8, tests, cobertura, SonarQube, Docker, Trivy, push a registry.
- Deploy: validación de manifiestos, despliegue a staging, pruebas de integración, carga y seguridad, aprobación manual, blue-green, smoke tests.
- Configuración: ConfigMap y Secrets por entorno.
- Infraestructura como código: `Terraform`.
- Migraciones: `Liquibase`, cambios compatibles, rollback, pipeline validado y automatizado.

## 7.9 Estrategia De Escalado

- API: autoescalado 2-10 réplicas, CPU 70%, memoria 80%, requests/segundo.
- Processor: autoescalado 3-20 réplicas, lag de Kafka.
- Kafka: particionado por tipo, tenant y tiempo; consumer groups por tipo, DLQ para fallos.

## 7.10 Recuperación Ante Desastres

- Backups: base de datos diaria, recuperación puntual 7 días, replicación cross-region, pruebas mensuales; backup de tópicos y offsets.
- Objetivos: failover < 5 min, restart < 10 min, recuperación región < 1h, pérdida de datos < 1 min, cero pérdida en colas/configuración.

## Referencias

- [Kubernetes Mejores Prácticas](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Microservices Deployment Patterns](https://microservices.io/patterns/deployment/)
- [Event Bus agnóstico Operations](https://kafka.apache.org/documentation/#operations)
- [Arc42 Deployment View](https://docs.arc42.org/section-7/)
