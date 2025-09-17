# 8. Conceptos transversales

## 8.1 Seguridad y autenticación

- Autenticación y autorización con `Keycloak` (`OAuth2`, validación de `JWT`, control de `claims` y `roles`).
- Cifrado en tránsito (`TLS 1.3`) y en reposo (`AES-256`).
- Gestión de secretos centralizada (`AWS Secrets Manager`).
- Control de acceso granular por rol y `tenant` (`realm`).
- Cumplimiento de normativas (`GDPR`, `LGPD`) y protección de `PII`.

## 8.2 Observabilidad y monitoreo

- Logs estructurados (`Serilog`, exportados a `Loki`).
- Métricas técnicas y de negocio (`Prometheus`, visualización en `Grafana`).
- Trazabilidad distribuida (`OpenTelemetry`, visualización en `Jaeger`).
- Health checks automatizados y alertas proactivas.

## 8.3 Resiliencia y escalabilidad

- `Circuit Breaker`, reintentos y backoff exponencial.
- `DLQ` y manejo de errores clasificados.
- Escalado horizontal y particionado en servicios y almacenamiento.
- Desacoplamiento mediante colas y procesadores independientes.

## 8.4 Multi-tenancy y multipaís

- Aislamiento de datos por esquema y `tenantId` (`realm`) en `PostgreSQL`.
- Configuración y personalización por `tenant` y país.
- Cumplimiento legal y localización (idiomas, monedas, zonas horarias).
- Orquestación de flujos multi-tenant y multipaís en todos los componentes críticos.

## 8.5 Gestión de configuración y plantillas

- Configuración jerárquica y por entorno (`YAML`, `JSON`).
- Plantillas internacionalizadas (`RazorEngine`, `Liquid`, `i18n`).
- Cache multi-nivel (memoria, `Redis`).
- Versionado y fallback automático de plantillas.

## 8.6 Mantenibilidad y fiabilidad

- Arquitectura modular, `Clean Architecture` y `DDD`.
- Documentación y pruebas automatizadas.
- Backups, replicación multi-AZ.
- Infraestructura como código (`Terraform`).
- Estrategias de deduplicación e idempotencia en todos los flujos críticos.

---

### Ejemplos y fragmentos clave

#### Ejemplo de JWT

```json
{
  "sub": "system:notification-processor",
  "aud": "notification-api",
  "scope": "notifications:send notifications:read",
  "tenant": "talma-pe",
  "roles": ["notification-sender"],
  "exp": 1640995200
}
```

#### Ejemplo de registro estructurado

```csharp
Log.Information("Notification {NotificationId} sent via {Channel} to {RecipientCount} recipients",
    notificationId, channel, recipients.Count);
```

#### Ejemplo de configuración por tenant

```json
{
  "tenantId": "talma-pe",
  "channels": {
    "email": {
      "provider": "sendgrid",
      "apiKey": "secretsmanager://talma-pe/sendgrid",
      "templates": {
        "default": "peru-branding-template"
      }
    },
    "sms": {
      "provider": "twilio",
      "phoneNumbers": ["+51900123456"]
    }
  },
  "compliance": {
    "gdpr": false,
    "local_regulations": ["peru-data-protection-law"]
  }
}
```

#### Ejemplo de health checks

```csharp
services.AddHealthChecks()
    .AddCheck<DatabaseHealthCheck>("database")
    .AddCheck<RedisHealthCheck>("cache");
```

#### Ejemplo de configuración jerárquica

```yaml
logging:
  level: Information

development:
  logging:
    level: Debug
  providers:
    email:
      mock: true

production:
  providers:
    email:
      sendgrid:
        api_key: ${SENDGRID_API_KEY}
```

#### Ejemplo de template internacionalizado

```liquid
{% assign greeting = 'email.greeting' | t: name: user.name %}
{{ greeting }}
{{ 'flight.status' | t: flight: flight_number, status: current_status }}
```

#### Ejemplo de clasificación de errores

```csharp
public enum ErrorCategory
{
    Transient,      // Network timeout, temporary provider issue
    Permanent,      // Invalid email, template not found
    Configuration,  // Missing API key, invalid settings
    Business        // User preferences, compliance violation
}
```

---

Estos conceptos transversales aseguran operación consistente, segura, escalable y observable, alineada con la arquitectura y decisiones del sistema.
