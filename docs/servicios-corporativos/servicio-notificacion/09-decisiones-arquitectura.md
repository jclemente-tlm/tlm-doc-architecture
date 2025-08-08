# 9. Decisiones de arquitectura

## 9.1 Decisiones principales

| ADR | Decisión | Estado | Justificación |
|-----|----------|--------|---------------|
| **ADR-001** | CQRS API + Processor | Aceptado | Separación responsabilidades |
| **ADR-002** | Redis como cola | Aceptado | Rendimiento |
| **ADR-003** | RazorEngine plantillas | Aceptado | Flexibilidad |
| **ADR-004** | Multi-canal handlers | Aceptado | Extensibilidad |

## 9.2 Alternativas evaluadas

| Componente | Alternativas | Selección | Razón |
|------------|-------------|-----------|--------|
| **Cola** | RabbitMQ, Redis, SQS | Redis | Simplicidad |
| **Plantillas** | Liquid, Handlebars, Razor | RazorEngine | .NET nativo |
| **Storage** | S3, EFS, Database | EFS | Compartido |
| **Canales** | Monolítico, Handlers | Handlers | Modularidad |

Esta sección documenta las decisiones arquitectónicas más importantes del **Sistema de Notificaciones** utilizando el formato ADR (Architecture Decision Record), proporcionando contexto, justificación y consecuencias de cada decisión.

![Notification System Architecture](/diagrams/servicios-corporativos/notification_system.png)

*Diagrama C4 - Arquitectura general del Sistema de Notificaciones mostrando las decisiones arquitectónicas implementadas y sus relaciones.*

## Resumen de Decisiones Arquitectónicas

| # | Decisión | Estado | Impacto | Fecha |
|---|----------|--------|---------|-------|
| ADR-001 | Estrategia Multi-Proveedor | ✅ Aprobado | Alto | 2024-01-15 |
| ADR-002 | Mensajería Basada en Base de Datos | ✅ Aprobado | Alto | 2024-01-25 |
| ADR-003 | Motor de Plantillas Liquid | ✅ Aprobado | Medio | 2024-02-05 |
| ADR-004 | Arquitectura Dirigida por Eventos | ✅ Aprobado | Alto | 2024-02-10 |
| ADR-005 | Librería NuGet Multi-nube | ✅ Aprobado | Alto | 2024-02-15 |

### Principios Arquitectónicos

Las decisiones arquitectónicas del Sistema de Notificaciones siguen los principios de:

- **Agnóstico de Nube:** Portabilidad total entre AWS, Azure y GCP
- **Contenedores Primero:** Optimizado para despliegue en contenedores
- **Mensajería Centrada en Base de Datos:** Colas basadas en PostgreSQL para independencia de nube
- **Multi-tenant:** Soporte nativo para múltiples inquilinos
- **Dirigido por Eventos:** Comunicación asíncrona mediante eventos de dominio
- **Sin Dependencia de Proveedor:** Abstracción completa de proveedores de nube

## ADR-001: Estrategia Multi-Proveedor para Confiabilidad

| Campo | Valor |
|-------|-------|
| **Estado** | ✅ Aprobado |
| **Fecha** | 2024-01-20 |
| **Decidido por** | Equipo de Arquitectura + Operations |
| **Stakeholders** | Equipo de Negocio, DevOps, Finanzas |

### Contexto

El servicio de notificaciones maneja comunicaciones críticas para el negocio (alertas de vuelos, confirmaciones de reserva, notificaciones de emergencia) que requieren:

- **Alta disponibilidad:** 99.9% tiempo de actividad
- **Escalabilidad:** 100K+ mensajes/día por tenant
- **Cobertura global:** Soporte para 4 países
- **Optimización de costos:** Mejores tarifas mediante diversificación

### Alternativas Consideradas

| Enfoque | Pros | Contras | Costo Anual | Decisión |
|---------|------|---------|-------------|----------|
| **Single provider** | Simple, menos integraciones | Single point of failure | $50K | ❌ Rechazado |
| **Multi-provider manual** | Control total | Complejidad operacional | $60K | ❌ Rechazado |
| **Multi-provider automático** | Alta disponibilidad, costo optimizado | Complejidad técnica | $45K | ✅ **Seleccionado** |
| **Provider aggregation service** | Menor complejidad | Vendor lock-in, latencia | $80K | ❌ Rechazado |

### Decisión

**Implementar estrategia multi-provider con failover automático** para cada canal de notificación.

### Arquitectura de Providers

```yaml
Email Providers:
  Primary: SendGrid
    - Capacity: 100K emails/day
    - Regions: Global
    - SLA: 99.95%

  Secondary: Amazon SES
    - Capacity: 200K emails/day
    - Regions: AWS regions
    - SLA: 99.9%

  Tertiary: Mailgun
    - Capacity: 50K emails/day
    - Regions: US, EU
    - SLA: 99.5%

SMS Providers:
  Primary: Twilio
    - Coverage: 180+ countries
    - Features: 2-way SMS, delivery receipts
    - SLA: 99.95%

  Secondary: Amazon SNS
    - Coverage: AWS supported regions
    - Features: Basic SMS
    - SLA: 99.9%

Push Notification Providers:
  Primary: Firebase Cloud Messaging
    - Platforms: iOS, Android, Web
    - Features: Rich notifications
    - SLA: 99.9%

  Secondary: Azure Notification Hubs
    - Platforms: All major platforms
    - Features: Template-based
    - SLA: 99.9%

WhatsApp Providers:
  Primary: Twilio Business API
    - Features: Templates, media
    - Approval: WhatsApp verified
    - SLA: 99.5%

  Secondary: 360Dialog
    - Features: Basic messaging
    - Approval: WhatsApp verified
    - SLA: 99.0%
```

### Provider Selection Algorithm

```csharp
public class ProviderSelector
{
    public async Task<INotificationProvider> SelectProviderAsync(
        NotificationChannel channel,
        string tenantId)
    {
        var providers = await GetAvailableProvidersAsync(channel, tenantId);

        foreach (var provider in providers.OrderBy(p => p.Priority))
        {
            var healthCheck = await provider.CheckHealthAsync();
            if (healthCheck.IsHealthy)
            {
                var capacity = await provider.GetCurrentCapacityAsync();
                if (capacity.CanAcceptMoreRequests)
                {
                    return provider;
                }
            }
        }

        throw new NoAvailableProviderException(channel);
    }
}
```

### Justificación

#### Beneficios de Confiabilidad

- **Eliminación SPOF:** No hay dependencia crítica de un solo proveedor
- **Failover automático:** Cambio en < 30 segundos ante fallos
- **Monitoreo de salud:** Monitoreo proactivo del estado del proveedor
- **Redundancia geográfica:** Proveedores en diferentes regiones

#### Optimización de Costos

- **Negociación de tarifas:** Mejores tarifas por volumen distribuido
- **Enrutamiento dinámico:** Enrutamiento automático al proveedor más económico
- **Optimización de volumen:** Distribución de carga según niveles de precios
- **Reducción de desperdicio:** Evita sobre-aprovisionamiento en un solo proveedor

#### Beneficios de Rendimiento

- **Distribución de carga:** Carga distribuida reduce latencia
- **Optimización regional:** Proveedor más cercano geográficamente
- **Escalado de capacidad:** Suma de capacidades de todos los proveedores
- **Enrutamiento de calidad:** Enrutamiento basado en tasas de éxito de entrega

### Consecuencias

#### Positivas

- ✅ **Alta disponibilidad:** 99.95% uptime vs 99.5% single provider
- ✅ **Optimización costos:** 15% reducción en costos totales

- ✅ **Escalabilidad:** 5x capacidad agregada
- ✅ **Flexibilidad:** Fácil incorporación de nuevos providers

#### Negativas

- ❌ **Complejidad técnica:** Abstraction layer y orchestration logic

- ❌ **Sobrecarga operacional:** Monitoreo y gestión de múltiples APIs
- ❌ **Complejidad de pruebas:** Pruebas de escenarios de failover
- ❌ **Desviación de configuración:** Riesgo de inconsistencias entre proveedores

#### Mitigaciones

- 🔧 **Capa de abstracción:** Interfaz unificada para todos los proveedores
- 🔧 **Pruebas automatizadas:** Verificaciones diarias de salud y pruebas de failover
- 🔧 **Gestión de configuración:** GitOps para configuración centralizada
- 🔧 **Panel de monitoreo:** Vista unificada de todos los proveedores

---

## ADR-002: Database-based Messaging para Cloud Agnostic Queuing

| Campo | Valor |
|-------|-------|
| **Estado** | ✅ Aprobado |
| **Fecha** | 2024-01-25 |
| **Decidido por** | Platform Team + Architecture |
| **Impacto** | Alto - Core messaging infrastructure |

### Contexto

El sistema de notificaciones requiere un message broker que soporte:

- **Cloud agnostic:** Portabilidad entre AWS, Azure, GCP
- **Alto capacidad de procesamiento:** 1M+ mensajes/día
- **Durabilidad:** Retención configurable para auditoria
- **Paralelismo:** Processing concurrente por múltiples consumers
- **Ordering:** Garantías de orden por tenant/usuario
- **Future migration path:** Posibilidad de migrar a colas dedicadas

### Alternativas Consideradas

| Technology | Portabilidad | Durability | Ordering | Complexity | Cost | Decisión |
|------------|--------------|------------|----------|------------|------|----------|
| **Database Messages** | ✅ Full | Excelente | Garantizada | Baja | Bajo | ✅ **Seleccionado** |
| **Amazon SNS + SQS** | ❌ AWS only | Excelente | FIFO limited | Media | Medio | ❌ Rechazado |
| **RabbitMQ** | ✅ Full | Buena | Cola | Media | Medio | ⚠️ Considerado |
| **Amazon MQ** | ⚠️ Multi-cloud | Buena | Limited | Media | Alto | ❌ Rechazado |
| **Event Bus** | ✅ Full | Excelente | Partición | Alta | Medio | ✅ Abstracción agnóstica |

### Decisión

**Adoptar Database-based messaging como broker principal** con migración futura planificada a colas dedicadas.

### Database Message Architecture

```sql
-- Message Queue Tables
CREATE TABLE message_queues (
    id BIGSERIAL PRIMARY KEY,
    queue_name VARCHAR(100) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    message_id UUID NOT NULL UNIQUE,
    payload JSONB NOT NULL,
    priority INTEGER DEFAULT 5,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed, dead_letter
    processor_id VARCHAR(100) NULL,
    correlation_id VARCHAR(100) NULL,

    INDEX idx_queue_status_scheduled (queue_name, status, scheduled_at),
    INDEX idx_tenant_status (tenant_id, status),
    INDEX idx_correlation (correlation_id)
);

-- Dead Letter Queue
CREATE TABLE dead_letter_queue (
    id BIGSERIAL PRIMARY KEY,
    original_message_id UUID NOT NULL,
    queue_name VARCHAR(100) NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    failure_reason TEXT,
    failed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    retry_count INTEGER,

    INDEX idx_tenant_failed_at (tenant_id, failed_at),
    INDEX idx_original_message (original_message_id)
);

-- Message Processing Locks
CREATE TABLE message_locks (
    message_id UUID PRIMARY KEY,
    processor_id VARCHAR(100) NOT NULL,
    locked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    INDEX idx_expires_at (expires_at)
);
```

### Queue Processing Implementation

```csharp
public class DatabaseMessageQueue : IMessageQueue
{
    private readonly IDbConnection _connection;
    private readonly ILogger<DatabaseMessageQueue> _logger;
    private readonly IConfiguration _config;

    public async Task<bool> EnqueueAsync<T>(string queueName, T message,
        MessageOptions options = null) where T : class
    {
        var messageId = Guid.NewGuid();
        var payload = JsonSerializer.Serialize(message);

        const string sql = @"
            INSERT INTO message_queues
            (queue_name, tenant_id, message_id, payload, priority, max_retries,
             scheduled_at, correlation_id)
            VALUES (@QueueName, @TenantId, @MessageId, @Payload::jsonb,
                   @Priority, @MaxRetries, @ScheduledAt, @CorrelationId)";

        var result = await _connection.ExecuteAsync(sql, new
        {
            QueueName = queueName,
            TenantId = options?.TenantId ?? "default",
            MessageId = messageId,
            Payload = payload,
            Priority = options?.Priority ?? 5,
            MaxRetries = options?.MaxRetries ?? 3,
            ScheduledAt = options?.ScheduledAt ?? DateTime.UtcNow,
            CorrelationId = options?.CorrelationId
        });

        return result > 0;
    }

    public async Task<QueueMessage<T>> DequeueAsync<T>(string queueName,
        string processorId, CancellationToken cancellationToken = default) where T : class
    {
        using var transaction = await _connection.BeginTransactionAsync();

        try
        {
            // Atomic dequeue with locking
            const string dequeueSql = @"
                WITH next_message AS (
                    SELECT id, message_id, payload, retry_count, correlation_id
                    FROM message_queues
                    WHERE queue_name = @QueueName
                      AND status = 'pending'
                      AND scheduled_at <= NOW()
                      AND NOT EXISTS (
                          SELECT 1 FROM message_locks l
                          WHERE l.message_id = message_queues.message_id
                            AND l.expires_at > NOW()
                      )
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE message_queues
                SET status = 'processing', processor_id = @ProcessorId
                FROM next_message
                WHERE message_queues.id = next_message.id
                RETURNING message_queues.id, message_queues.message_id,
                         message_queues.payload, message_queues.retry_count,
                         message_queues.correlation_id";

            var messageData = await _connection.QueryFirstOrDefaultAsync(dequeueSql, new
            {
                QueueName = queueName,
                ProcessorId = processorId
            }, transaction);

            if (messageData == null)
            {
                await transaction.RollbackAsync();
                return null;
            }

            // Create processing lock
            const string lockSql = @"
                INSERT INTO message_locks (message_id, processor_id, expires_at)
                VALUES (@MessageId, @ProcessorId, @ExpiresAt)
                ON CONFLICT (message_id) DO UPDATE
                SET processor_id = EXCLUDED.processor_id,
                    expires_at = EXCLUDED.expires_at";

            await _connection.ExecuteAsync(lockSql, new
            {
                MessageId = messageData.message_id,
                ProcessorId = processorId,
                ExpiresAt = DateTime.UtcNow.AddMinutes(5) // 5 min processing timeout
            }, transaction);

            await transaction.CommitAsync();

            var payload = JsonSerializer.Deserialize<T>(messageData.payload);
            return new QueueMessage<T>
            {
                Id = messageData.id,
                MessageId = messageData.message_id,
                Payload = payload,
                RetryCount = messageData.retry_count,
                CorrelationId = messageData.correlation_id
            };
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }

    public async Task<bool> CompleteAsync(Guid messageId)
    {
        using var transaction = await _connection.BeginTransactionAsync();

        try
        {
            // Mark as completed
            const string completeSql = @"
                UPDATE message_queues
                SET status = 'completed', processed_at = NOW()
                WHERE message_id = @MessageId";

            await _connection.ExecuteAsync(completeSql, new { MessageId = messageId }, transaction);

            // Remove lock
            const string unlockSql = "DELETE FROM message_locks WHERE message_id = @MessageId";
            await _connection.ExecuteAsync(unlockSql, new { MessageId = messageId }, transaction);

            await transaction.CommitAsync();
            return true;
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }

    public async Task<bool> FailAsync(Guid messageId, string reason)
    {
        using var transaction = await _connection.BeginTransactionAsync();

        try
        {
            // Increment retry count or move to DLQ
            const string failSql = @"
                UPDATE message_queues
                SET retry_count = retry_count + 1,
                    status = CASE
                        WHEN retry_count + 1 >= max_retries THEN 'dead_letter'
                        ELSE 'pending'
                    END,
                    scheduled_at = CASE
                        WHEN retry_count + 1 < max_retries
                        THEN NOW() + (INTERVAL '1 minute' * POWER(2, retry_count + 1))
                        ELSE scheduled_at
                    END
                WHERE message_id = @MessageId
                RETURNING retry_count, max_retries, payload, queue_name, tenant_id";

            var result = await _connection.QueryFirstOrDefaultAsync(failSql,
                new { MessageId = messageId }, transaction);

            // Move to dead letter queue if max retries exceeded
            if (result != null && result.retry_count >= result.max_retries)
            {
                const string dlqSql = @"
                    INSERT INTO dead_letter_queue
                    (original_message_id, queue_name, tenant_id, payload,
                     failure_reason, retry_count)
                    VALUES (@MessageId, @QueueName, @TenantId, @Payload::jsonb,
                           @Reason, @RetryCount)";

                await _connection.ExecuteAsync(dlqSql, new
                {
                    MessageId = messageId,
                    QueueName = result.queue_name,
                    TenantId = result.tenant_id,
                    Payload = result.payload,
                    Reason = reason,
                    RetryCount = result.retry_count
                }, transaction);
            }

            // Remove lock
            await _connection.ExecuteAsync(
                "DELETE FROM message_locks WHERE message_id = @MessageId",
                new { MessageId = messageId }, transaction);

            await transaction.CommitAsync();
            return true;
        }
        catch
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}
```

### Configuración de Colas (Queue Configuration)

```yaml
# Definición de colas para el Servicio de Notificaciones
NotificationQueues:
  email-notifications:
    priority_levels: [1, 5, 10]  # low, normal, high
    max_retries: 3
    retry_backoff: exponential
    batch_size: 50
    processing_timeout: 300s  # 5 minutos

  sms-notifications:
    priority_levels: [1, 5, 10]
    max_retries: 5
    retry_backoff: exponential
    batch_size: 100
    processing_timeout: 120s  # 2 minutos

  push-notifications:
    priority_levels: [1, 5, 10]
    max_retries: 3
    retry_backoff: linear
    batch_size: 200
    processing_timeout: 60s   # 1 minuto

  whatsapp-notifications:
    priority_levels: [1, 5, 10]
    max_retries: 3
    retry_backoff: exponential
    batch_size: 25
    processing_timeout: 180s  # 3 minutos

# Estrategia de migración a colas dedicadas
MigrationStrategy:
  phase_1: "Colas en base de datos para implementación inicial"
  phase_2: "Evaluar proveedores de colas cloud-agnostic"
  phase_3: "Implementar patrón adaptador para migración sencilla"
  phase_4: "Cambio a servicio de colas dedicado sin downtime"
```

### Justificación de la Configuración de Colas

#### Beneficios de Portabilidad

- **Cloud Agnostic:** Funciona en cualquier nube con `PostgreSQL`
- **Sin Vendor Lock-in:** SQL estándar, migración fácil
- **Listo para Contenedores:** Base de datos portable en contenedores
- **Costo Predecible:** Sin precio por mensaje

#### Beneficios de Rendimiento

- **Transacciones ACID:** Consistencia fuerte garantizada
- **Indexación:** Consultas optimizadas para operaciones de dequeue
- **Procesamiento en lotes:** Operaciones bulk eficientes
- **Pooling de conexiones:** Conexiones de base de datos optimizadas

#### Beneficios de Migración

- **Ruta futura:** Migración fácil a servicios de cola dedicados
- **Patrón Adaptador:** Abstracción de interfaz para implementación de colas
- **Mitigación de riesgos:** Comenzar simple, evolucionar complejidad
- **Aprendizaje operacional:** El equipo aprende patrones de mensajes primero

### Consecuencias de la Configuración de Colas

#### Positivas

- ✅ **Portabilidad completa:** Cloud agnostic desde día 1
- ✅ **Simplicidad operacional:** Una tecnología menos que administrar
- ✅ **Durabilidad garantizada:** ACID transactions, backup incluido
- ✅ **Cost effectiveness:** No costos adicionales de queue service
- ✅ **Debugging simplicity:** SQL queries para resolución de problemas
- ✅ **Migration ready:** Clear path para evolución futura

#### Negativas

- ❌ **Database load:** Additional queries en database principal
- ❌ **Scaling limitations:** Database bottleneck en high volumes
- ❌ **Feature gaps:** No advanced queue features inicialmente
- ❌ **Polling overhead:** Requires periodic dequeue polling

#### Mitigaciones

- 🔧 **Réplicas de lectura:** Separar procesamiento de colas del workload principal
- 🔧 **Particionamiento:** Particionamiento de tablas por tenant y fecha
- 🔧 **Monitoreo:** Métricas de profundidad de cola y tiempo de procesamiento
- 🔧 **Patrón adaptador:** Interfaz preparada para migración
- 🔧 **Pruebas de rendimiento:** Pruebas de carga regulares para identificar límites
- 🔧 **Planificación de migración:** Hoja de ruta definida para servicios de cola

---

## ADR-003: Liquid Template Engine para Personalization

| Campo | Valor |
|-------|-------|
| **Estado** | ✅ Aprobado |
| **Fecha** | 2024-02-05 |
| **Decidido por** | Product Team + Engineering |
| **Relacionado con** | ADR-005 (Multi-language Support) |

### Contexto

El sistema requiere un template engine que permita:

- **Business user friendly:** No-code template editing
- **Rich templating:** Condicionales, loops, filters
- **Security:** Sandboxed execution
- **Performance:** Fast rendering para high volume
- **Extensibility:** Custom filters y funciones

### Alternativas Consideradas

| Template Engine | Syntax | Security | Performance | Learning Curve | Decisión |
|----------------|--------|----------|-------------|----------------|----------|
| **Liquid** | Intuitive | Sandboxed | Alto | Bajo | ✅ **Seleccionado** |
| **Handlebars** | Simple | Limited | Alto | Bajo | ❌ Rechazado |
| **Razor** | Powerful | Code injection risk | Muy Alto | Alto | ❌ Rechazado |
| **Mustache** | Minimal | Safe | Alto | Muy Bajo | ❌ Rechazado |
| **Jinja2** | Feature-rich | Configurable | Medio | Medio | ❌ Rechazado |

### Decisión

**Adoptar Liquid Template Engine** con extensiones custom para casos de uso específicos.

### Template Architecture

```liquid
<!-- Email template example -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ flight.title | escape }}</title>
</head>
<body>
    {% assign user_name = user.firstName | default: "Estimado pasajero" %}

    <h1>{{ 'email.greeting' | t: name: user_name }}</h1>

    {% if flight.status == 'delayed' %}
        <div class="alert alert-warning">
            {{ 'flight.delayed_message' | t: delay_time: flight.delayMinutes }}
        </div>
    {% elsif flight.status == 'cancelled' %}
        <div class="alert alert-danger">
            {{ 'flight.cancelled_message' | t }}
        </div>
    {% endif %}

    <table class="flight-details">
        <tr>
            <td>{{ 'flight.number' | t }}:</td>
            <td>{{ flight.number }}</td>
        </tr>
        <tr>
            <td>{{ 'flight.departure' | t }}:</td>
            <td>{{ flight.departureTime | date: 'd/M/yyyy HH:mm' }}</td>
        </tr>
        {% if flight.gate %}
        <tr>
            <td>{{ 'flight.gate' | t }}:</td>
            <td>{{ flight.gate }}</td>
        </tr>
        {% endif %}
    </table>

    {% for segment in flight.segments %}
        <div class="segment">
            <h3>{{ segment.origin }} → {{ segment.destination }}</h3>
            <p>{{ segment.departureTime | date: 'short' }}</p>
        </div>
    {% endfor %}

    <footer>
        {{ 'email.footer' | t: company: tenant.companyName }}
    </footer>
</body>
</html>
```

### Custom Filters Implementation

```csharp
public class CustomLiquidFilters
{
    public static string Translate(string key, object parameters = null)
    {
        var localizationService = ServiceLocator.GetService<ILocalizationService>();
        return localizationService.GetLocalizedString(key, parameters);
    }

    public static string FormatCurrency(decimal amount, string currencyCode)
    {
        var culture = CultureInfo.GetCultureInfo(currencyCode);
        return amount.ToString("C", culture);
    }

    public static string FormatPhone(string phoneNumber, string countryCode)
    {
        return PhoneNumberFormatter.Format(phoneNumber, countryCode);
    }

    public static string Qr(string content, int size = 200)
    {
        return QrCodeGenerator.GenerateDataUri(content, size);
    }
}

// Registration
Template.RegisterFilter("t", CustomLiquidFilters.Translate);
Template.RegisterFilter("currency", CustomLiquidFilters.FormatCurrency);
Template.RegisterFilter("phone", CustomLiquidFilters.FormatPhone);
Template.RegisterFilter("qr", CustomLiquidFilters.Qr);
```

### Security Configuration

```csharp
public class SecureLiquidTemplate
{
    private readonly Template _template;

    public SecureLiquidTemplate(string templateContent)
    {
        var parseContext = new ParseContext
        {
            AllowedTags = new HashSet<string>
            {
                "assign", "if", "elsif", "else", "endif", "for", "endfor",
                "case", "when", "endcase", "unless", "endunless"
            },
            AllowedFilters = new HashSet<string>
            {
                "escape", "date", "default", "t", "currency", "phone", "qr",
                "upcase", "downcase", "capitalize", "truncate"
            }
        };

        _template = Template.Parse(templateContent, parseContext);
    }


    public string Render(object data, int timeoutMs = 5000)
    {
        using var cts = new CancellationTokenSource(timeoutMs);
        return _template.Render(Hash.FromAnonymousObject(data), cts.Token);
    }

}
```

### Justificación

#### Beneficios Empresariales

- **Edición sin código:** Los usuarios de negocio pueden crear plantillas
- **Funcionalidad rica:** Lógica condicional, bucles, manipulación de datos
- **Consistencia de marca:** Herencia de plantillas y componentes compartidos
- **Pruebas A/B:** Variaciones de plantillas fáciles

#### Beneficios Técnicos

- **Seguridad:** Ejecución en sandbox previene inyección de código
- **Rendimiento:** Plantillas compiladas con caché
- **Mantenibilidad:** Separación clara lógica/presentación
- **Extensibilidad:** Filtros personalizados para casos específicos

#### Beneficios Operacionales

- **Versionado de plantillas:** Gestión de plantillas basada en Git
- **Capacidad de vista previa:** Pruebas seguras de plantillas
- **Manejo de errores:** Degradación elegante con respaldos
- **Rastro de auditoría:** Uso de plantillas y seguimiento de cambios

### Consecuencias

#### Positivas

- ✅ **Empowerment:** Business teams self-service capability
- ✅ **Security:** Sandboxed execution environment
- ✅ **Performance:** 5-10ms template rendering
- ✅ **Flexibility:** Rich templating capabilities

#### Negativas

- ❌ **Learning curve:** Liquid syntax learning for business users
- ❌ **Feature limitations:** Less powerful than full programming languages
- ❌ **Debugging complexity:** Limited debugging capabilities
- ❌ **Memory overhead:** Template compilation y caching

#### Mitigaciones

- 🔧 **Programa de capacitación:** Educación de usuarios de negocio en Liquid
- 🔧 **Biblioteca de plantillas:** Plantillas pre-construidas para escenarios comunes
- 🔧 **Editor visual:** Editor GUI para plantillas complejas
- 🔧 **Monitoreo de rendimiento:** Métricas de renderizado de plantillas

---

## ADR-004: Event-Driven Architecture con Domain Events

| Campo | Valor |
|-------|-------|
| **Estado** | ✅ Aprobado |
| **Fecha** | 2024-02-10 |
| **Decidido por** | Architecture Team + Product |
| **Relacionado con** | ADR-002 (Kafka), ADR-006 (Audit Trail) |

### Contexto

El sistema debe integrar con múltiples servicios externos y internos, requiriendo:

- **Loose coupling:** Servicios independientes
- **Real-time notifications:** Immediate response a eventos de negocio
- **Audit trail:** Complete history of all events
- **Scalability:** Handle event bursts
- **Integration flexibility:** Easy addition of new consumers

### Event Types Design

```csharp
// Domain Events
public abstract class NotificationDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredAt { get; } = DateTime.UtcNow;
    public string TenantId { get; set; }
    public string UserId { get; set; }
    public string CorrelationId { get; set; }
}

public class NotificationRequested : NotificationDomainEvent
{
    public string NotificationId { get; set; }
    public NotificationChannel Channel { get; set; }
    public string TemplateId { get; set; }
    public Dictionary<string, object> Variables { get; set; }
    public List<string> Recipients { get; set; }
    public Priority Priority { get; set; }
    public DateTime? ScheduledAt { get; set; }
}

public class NotificationSent : NotificationDomainEvent
{
    public string NotificationId { get; set; }
    public NotificationChannel Channel { get; set; }
    public string ProviderId { get; set; }
    public string ProviderMessageId { get; set; }
    public int RecipientCount { get; set; }
    public TimeSpan ProcessingDuration { get; set; }
}

public class NotificationDelivered : NotificationDomainEvent
{
    public string NotificationId { get; set; }
    public string RecipientId { get; set; }
    public DateTime DeliveredAt { get; set; }
    public string ProviderStatus { get; set; }
}

public class NotificationFailed : NotificationDomainEvent
{
    public string NotificationId { get; set; }
    public string RecipientId { get; set; }
    public string ErrorCode { get; set; }
    public string ErrorMessage { get; set; }
    public bool IsRetryable { get; set; }
    public int AttemptNumber { get; set; }
}
```

### Event Publishing Pattern

```csharp
public class NotificationService
{
    private readonly IEventPublisher _eventPublisher;
    private readonly INotificationRepository _repository;

    public async Task<NotificationResult> SendNotificationAsync(NotificationRequest request)
    {
        // Publish domain event
        await _eventPublisher.PublishAsync(new NotificationRequested
        {
            NotificationId = request.Id,
            Channel = request.Channel,
            TemplateId = request.TemplateId,
            Variables = request.Variables,
            Recipients = request.Recipients,
            TenantId = request.TenantId,
            UserId = request.UserId
        });

        // Business logic continues...
        var result = await ProcessNotificationAsync(request);

        if (result.IsSuccess)
        {
            await _eventPublisher.PublishAsync(new NotificationSent
            {
                NotificationId = request.Id,
                Channel = request.Channel,
                ProviderId = result.ProviderId,
                ProviderMessageId = result.ProviderMessageId,
                RecipientCount = request.Recipients.Count,
                ProcessingDuration = result.ProcessingDuration,
                TenantId = request.TenantId
            });
        }
        else
        {
            await _eventPublisher.PublishAsync(new NotificationFailed
            {
                NotificationId = request.Id,
                ErrorCode = result.ErrorCode,
                ErrorMessage = result.ErrorMessage,
                IsRetryable = result.IsRetryable,
                TenantId = request.TenantId
            });
        }

        return result;
    }
}
```

### Event Consumers

```yaml
Event Consumers:
  Analytics Consumer:
    events: [NotificationSent, NotificationDelivered, NotificationFailed]
    purpose: Business metrics and dashboards

  Audit Consumer:
    events: [All notification events]
    purpose: Compliance and audit trail

  Cost Tracking Consumer:
    events: [NotificationSent]

    purpose: Cost allocation per tenant

  Retry Consumer:
    events: [NotificationFailed]
    purpose: Automatic retry logic


  Webhook Consumer:
    events: [NotificationDelivered, NotificationFailed]
    purpose: Customer webhook notifications

  Email Digest Consumer:
    events: [NotificationFailed]
    purpose: Daily failure summary emails
```

### Justificación

#### Beneficios de Arquitectura

- **Desacoplamiento:** Los servicios se comunican vía eventos, no llamadas directas
- **Escalabilidad:** Los consumidores de eventos pueden escalar independientemente
- **Confiabilidad:** La persistencia de eventos garantiza que no haya pérdida de mensajes
- **Flexibilidad:** Fácil agregar nuevos consumidores de eventos

#### Beneficios Empresariales

- **Información en tiempo real:** Análisis y monitoreo inmediatos
- **Transparencia del cliente:** Actualizaciones de estado en tiempo real
- **Cumplimiento de auditoría:** Historial completo de eventos
- **Listo para integración:** Integración fácil del sistema externo

### Consecuencias

#### Positivas

- ✅ **Loose coupling:** Services evolve independently
- ✅ **Scalability:** Linear scaling with event volume
- ✅ **Observability:** Complete system visibility
- ✅ **Integration ease:** Plugin architecture

#### Negativas

- ❌ **Eventual consistency:** No immediate consistency guarantees
- ❌ **Debugging complexity:** Distributed tracing required
- ❌ **Event schema evolution:** Backward compatibility challenges
- ❌ **Operational overhead:** Event store management

#### Mitigaciones

- 🔧 **Event sourcing:** Reconstruir estado desde eventos
- 🔧 **Trazabilidad distribuida:** Implementación de OpenTelemetry
- 🔧 **Registro de esquemas:** Confluent Schema Registry
- 🔧 **Panel de monitoreo:** Visualización del flujo de eventos

---

## ADR-005: Librería NuGet Multi-cloud para Configuraciones y Secretos

| Campo | Valor |
|-------|-------|
| **Estado** | ✅ Aprobado |
| **Fecha** | 2024-02-15 |
| **Decidido por** | Platform Team + Security |
| **Relacionado con** | ADR-001 (Multi-Provider), ADR-002 (Database Messaging) |

### Contexto

La solución corporativa debe ser **cloud agnostic** y portable, requiriendo un mecanismo unificado de gestión de configuraciones y secretos que soporte:

- **Multi-cloud portability:** AWS, Azure, GCP
- **Configuration management:** Centralized, versioned, environment-aware
- **Secret management:** Secure storage, rotation, audit trail
- **Easy migration:** Cambio de cloud provider sin refactoring
- **Developer experience:** Unified API across environments

### Alternativas Consideradas

| Solución | Portabilidad | Developer UX | Vendor Lock-in | Maintenance | Decisión |
|----------|--------------|--------------|---------------|-------------|----------|
| **Custom NuGet Library** | ✅ Full | ✅ Excellent | ❌ None | ⚠️ Internal | ✅ **Seleccionado** |
| **AWS Secrets Manager** | ❌ AWS only | ✅ Good | ✅ Complete | ✅ Managed | ❌ Rechazado |
| **Azure Key Vault** | ❌ Azure only | ✅ Good | ✅ Complete | ✅ Managed | ❌ Rechazado |
| **HashiCorp Vault** | ✅ Full | ⚠️ Complex | ❌ None | ⚠️ Self-managed | ❌ Rechazado |
| **Kubernetes Secrets** | ✅ Platform | ⚠️ Limited | ❌ None | ⚠️ K8s dependent | ❌ Rechazado |

### Decisión

**Desarrollar librería NuGet personalizada** que abstraiga la gestión de configuraciones y secretos con soporte multi-cloud.

### Arquitectura de la Librería

```csharp
// Core abstraction interfaces
public interface IConfigurationProvider
{
    Task<T> GetConfigurationAsync<T>(string key, string environment = null);
    Task<string> GetSecretAsync(string secretName, string version = "latest");
    Task SetConfigurationAsync<T>(string key, T value, string environment = null);
    Task SetSecretAsync(string secretName, string secretValue, Dictionary<string, string> metadata = null);
    Task<bool> DeleteSecretAsync(string secretName);
}

public interface ICloudProvider
{
    string Name { get; }
    Task<string> GetSecretValueAsync(string secretName, string version);
    Task<string> GetConfigurationValueAsync(string configKey, string environment);
    Task SetSecretValueAsync(string secretName, string value, Dictionary<string, string> metadata);
    Task SetConfigurationValueAsync(string configKey, string value, string environment);
    Task<bool> ValidateConnectionAsync();
}

// Multi-cloud configuration service
public class MultiCloudConfigurationService : IConfigurationProvider
{
    private readonly ICloudProvider _primaryProvider;
    private readonly ICloudProvider _fallbackProvider;
    private readonly IMemoryCache _cache;
    private readonly ILogger<MultiCloudConfigurationService> _logger;

    public MultiCloudConfigurationService(
        ICloudProvider primaryProvider,
        ICloudProvider fallbackProvider,
        IMemoryCache cache,
        ILogger<MultiCloudConfigurationService> logger)
    {
        _primaryProvider = primaryProvider;
        _fallbackProvider = fallbackProvider;
        _cache = cache;
        _logger = logger;
    }

    public async Task<T> GetConfigurationAsync<T>(string key, string environment = null)
    {
        var cacheKey = $"config:{key}:{environment ?? "default"}";

        if (_cache.TryGetValue(cacheKey, out T cachedValue))
        {
            return cachedValue;
        }

        try
        {
            var configValue = await _primaryProvider.GetConfigurationValueAsync(key, environment);
            var result = JsonSerializer.Deserialize<T>(configValue);

            _cache.Set(cacheKey, result, TimeSpan.FromMinutes(15));
            return result;
        }
        catch (Exception ex) when (_fallbackProvider != null)
        {
            _logger.LogWarning(ex, "Primary provider failed for config {Key}, trying fallback", key);

            var configValue = await _fallbackProvider.GetConfigurationValueAsync(key, environment);
            var result = JsonSerializer.Deserialize<T>(configValue);

            _cache.Set(cacheKey, result, TimeSpan.FromMinutes(5)); // Shorter cache for fallback
            return result;
        }
    }

    public async Task<string> GetSecretAsync(string secretName, string version = "latest")
    {
        var cacheKey = $"secret:{secretName}:{version}";

        if (_cache.TryGetValue(cacheKey, out string cachedSecret))
        {
            return cachedSecret;
        }

        try
        {
            var secretValue = await _primaryProvider.GetSecretValueAsync(secretName, version);

            // Shorter cache for secrets for security
            _cache.Set(cacheKey, secretValue, TimeSpan.FromMinutes(5));
            return secretValue;
        }
        catch (Exception ex) when (_fallbackProvider != null)
        {
            _logger.LogWarning(ex, "Primary provider failed for secret {SecretName}, trying fallback", secretName);

            var secretValue = await _fallbackProvider.GetSecretValueAsync(secretName, version);
            _cache.Set(cacheKey, secretValue, TimeSpan.FromMinutes(2)); // Even shorter for fallback secrets
            return secretValue;
        }
    }
}
```

### Cloud Provider Implementations

```csharp
// AWS Secrets Manager + Parameter Store
public class AwsCloudProvider : ICloudProvider
{
    private readonly IAmazonSecretsManager _secretsManager;
    private readonly IAmazonSimpleSystemsManagement _parameterStore;

    public string Name => "AWS";

    public async Task<string> GetSecretValueAsync(string secretName, string version)
    {
        var request = new GetSecretValueRequest
        {
            SecretId = secretName,
            VersionStage = version == "latest" ? "AWSCURRENT" : version
        };

        var response = await _secretsManager.GetSecretValueAsync(request);
        return response.SecretString;
    }

    public async Task<string> GetConfigurationValueAsync(string configKey, string environment)
    {
        var parameterName = environment != null ? $"/{environment}/{configKey}" : $"/{configKey}";

        var request = new GetParameterRequest
        {
            Name = parameterName,
            WithDecryption = true
        };

        var response = await _parameterStore.GetParameterAsync(request);
        return response.Parameter.Value;
    }
}

// Azure Key Vault + App Configuration
public class AzureCloudProvider : ICloudProvider
{
    private readonly SecretClient _secretClient;
    private readonly ConfigurationClient _configClient;

    public string Name => "Azure";

    public async Task<string> GetSecretValueAsync(string secretName, string version)
    {
        var response = await _secretClient.GetSecretAsync(secretName, version);
        return response.Value.Value;
    }

    public async Task<string> GetConfigurationValueAsync(string configKey, string environment)
    {
        var key = environment != null ? $"{environment}:{configKey}" : configKey;
        var response = await _configClient.GetConfigurationSettingAsync(key);
        return response.Value.Value;
    }
}

// Google Cloud Secret Manager + Cloud Config
public class GoogleCloudProvider : ICloudProvider
{
    private readonly SecretManagerServiceClient _secretClient;

    public string Name => "GoogleCloud";

    public async Task<string> GetSecretValueAsync(string secretName, string version)
    {
        var request = new AccessSecretVersionRequest
        {
            Name = new SecretVersionName(
                Environment.GetEnvironmentVariable("GOOGLE_CLOUD_PROJECT"),
                secretName,
                version == "latest" ? "latest" : version
            ).ToString()
        };

        var response = await _secretClient.AccessSecretVersionAsync(request);
        return response.Payload.Data.ToStringUtf8();
    }

    public async Task<string> GetConfigurationValueAsync(string configKey, string environment)
    {
        // Implementation using Google Cloud Config or Firestore
        var fullKey = environment != null ? $"{environment}/{configKey}" : configKey;
        // ... Google Cloud specific implementation
        throw new NotImplementedException("Google Cloud configuration to be implemented");
    }
}
```

### Dependency Injection Setup

```csharp
// Startup configuration
public void ConfigureServices(IServiceCollection services)
{
    // Register based on environment
    var cloudProvider = Environment.GetEnvironmentVariable("CLOUD_PROVIDER") ?? "AWS";

    switch (cloudProvider.ToUpper())
    {
        case "AWS":
            services.AddSingleton<ICloudProvider, AwsCloudProvider>();
            services.AddAWSService<IAmazonSecretsManager>();
            services.AddAWSService<IAmazonSimpleSystemsManagement>();
            break;

        case "AZURE":
            services.AddSingleton<ICloudProvider, AzureCloudProvider>();
            services.AddSingleton(sp => new SecretClient(
                new Uri(Environment.GetEnvironmentVariable("AZURE_KEY_VAULT_URL")),
                new DefaultAzureCredential()));
            break;

        case "GCP":
            services.AddSingleton<ICloudProvider, GoogleCloudProvider>();
            services.AddSingleton<SecretManagerServiceClient>();
            break;
    }

    // Configure fallback provider if specified
    var fallbackProvider = Environment.GetEnvironmentVariable("FALLBACK_CLOUD_PROVIDER");
    if (!string.IsNullOrEmpty(fallbackProvider))
    {
        // Register fallback provider...
    }

    services.AddSingleton<IConfigurationProvider, MultiCloudConfigurationService>();
    services.AddMemoryCache();
}
```

### Usage Examples

```csharp
// In application services
public class NotificationService
{
    private readonly IConfigurationProvider _config;

    public NotificationService(IConfigurationProvider config)
    {
        _config = config;
    }

    public async Task<EmailSettings> GetEmailSettingsAsync()
    {
        // Automatic cloud provider detection and caching
        return await _config.GetConfigurationAsync<EmailSettings>("email-settings", "production");
    }

    public async Task<string> GetApiKeyAsync(string providerName)
    {
        // Secret retrieval with automatic fallback
        return await _config.GetSecretAsync($"notification-providers/{providerName}/api-key");
    }
}

// Configuration model
public class EmailSettings
{
    public string SmtpServer { get; set; }
    public int Port { get; set; }
    public bool UseSSL { get; set; }
    public string FromAddress { get; set; }
    public string FromName { get; set; }
}
```

### NuGet Package Structure

```
Talma.Configuration.MultiCloud/
├── Abstractions/
│   ├── IConfigurationProvider.cs
│   ├── ICloudProvider.cs
│   └── Models/
├── Providers/
│   ├── AWS/
│   │   ├── AwsCloudProvider.cs
│   │   └── AwsExtensions.cs
│   ├── Azure/
│   │   ├── AzureCloudProvider.cs
│   │   └── AzureExtensions.cs
│   └── GoogleCloud/
│       ├── GoogleCloudProvider.cs
│       └── GoogleCloudExtensions.cs
├── Core/
│   ├── MultiCloudConfigurationService.cs
│   ├── CacheManager.cs
│   └── ProviderFactory.cs
└── Extensions/
    └── ServiceCollectionExtensions.cs
```

### Justificación

#### Beneficios de Portabilidad

- **Verdadera Cloud Agnostic:** API única funciona en todas las nubes principales
- **Cero Vendor Lock-in:** Ruta de migración fácil entre proveedores
- **Experiencia de desarrollador consistente:** El mismo código funciona en todas partes
- **Soporte de respaldo:** Failover automático entre proveedores de nube

#### Beneficios Operacionales

- **Gestión centralizada:** Punto único para todas las operaciones de configuración/secretos
- **Estrategia de caché:** Reduce latencia y costos de API de nube
- **Rastro de auditoría:** Logging y monitoreo integrados
- **Mejores prácticas de seguridad:** Cifrado automático, soporte de rotación

#### Beneficios de Costo

- **Llamadas API reducidas:** El caché inteligente reduce costos del proveedor de nube
- **Precios flexibles:** Puede cambiar al proveedor más rentable
- **Sin tarifas de licencia:** Biblioteca interna, sin licencias externas

### Consecuencias

#### Positivas

- ✅ **Complete Portability:** True cloud-agnostic solution
- ✅ **Developer Productivity:** Unified API across environments
- ✅ **Cost Optimization:** Flexible provider switching
- ✅ **Security:** Standardized secret management practices
- ✅ **Future Proof:** Easy to add new cloud providers

#### Negativas

- ❌ **Development Overhead:** Internal library maintenance required
- ❌ **Initial Complexity:** Higher upfront development cost
- ❌ **Testing Burden:** Must test across multiple cloud providers
- ❌ **Feature Lag:** New cloud features require library updates

#### Mitigaciones

- 🔧 **Pruebas automatizadas:** Pipeline CI/CD prueba todos los proveedores de nube
- 🔧 **Documentación:** Documentos y ejemplos completos
- 🔧 **Estrategia de versionado:** Versionado semántico para compatibilidad hacia atrás
- 🔧 **Contribución de la comunidad:** Los equipos internos contribuyen mejoras
- 🔧 **SDKs de proveedores de nube:** Aprovechar SDKs oficiales internamente
- 🔧 **Feature flags:** Despliegue gradual de nuevas capacidades
