# 8. Conceptos transversales

## 8.1 Seguridad y Autenticación

- Autenticación y autorización robusta (`OAuth2/JWT`, `claims`, `scopes`)
- Cifrado en tránsito (`TLS 1.3`) y en reposo (`AES-256`)
- Gestión de secretos centralizada (`Vault`, `Key Vault`)
- Control de acceso granular por rol y tenant

## 8.2 Observabilidad y Monitoreo

- Logs estructurados (`Serilog`)
- Métricas técnicas y de negocio (`Prometheus`, `KPIs`)
- Trazabilidad distribuida (`OpenTelemetry`)
- Health checks automatizados

## 8.3 Resiliencia y Escalabilidad

- Circuit Breaker, reintentos y backoff exponencial
- DLQ y manejo de errores clasificados
- Escalado horizontal, fan-out `SNS/SQS`, particionado/sharding

## 8.4 Multi-tenancy y Multipaís

- Aislamiento de datos por esquema y `tenantId` en `PostgreSQL`
- Configuración y personalización por tenant y país
- Cumplimiento legal y localización (idiomas, monedas, zonas horarias)

## 8.5 Gestión de Configuración y Plantillas

- Configuración jerárquica y por entorno (`YAML`, `JSON`)
- Plantillas internacionalizadas (`Liquid`, `i18n`)
- Cache multi-nivel (memoria, `Redis`)

## 8.6 Mantenibilidad y Fiabilidad

- Arquitectura modular y DDD
- Documentación y pruebas automatizadas
- Backups, replicación multi-AZ

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
      "apiKey": "vault://secrets/talma-pe/sendgrid",
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
    .AddCheck<KafkaHealthCheck>("kafka")
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

#### Ejemplo de error classification

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

Estos conceptos transversales aseguran que el sistema opere de manera consistente, segura, escalable y observable, proporcionando una base sólida para el crecimiento y la evolución futura.
