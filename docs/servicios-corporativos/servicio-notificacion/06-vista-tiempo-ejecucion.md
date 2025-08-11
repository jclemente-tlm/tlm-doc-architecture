# 6. Vista De Tiempo De Ejecución

## 6.1 Escenarios Principales

| Escenario               | Flujo                              | Componentes         |
|-------------------------|------------------------------------|---------------------|
| Envío inmediato         | Notification API → ingestionQueue → notificationProcessor → Notification Database → [Colas de Canal] → [Procesadores de Canal] → Proveedor Externo → Notification Database | Notification API, ingestionQueue, notificationProcessor, Notification Database, emailQueue, smsQueue, whatsappQueue, pushQueue, emailProcessor, smsProcessor, whatsappProcessor, pushProcessor, Attachment Storage |
| Envío programado        | Notification API → Notification Scheduler → ingestionQueue → notificationProcessor → Notification Database → [Colas de Canal] → [Procesadores de Canal] → Proveedor Externo → Notification Database | Notification API, Notification Scheduler, ingestionQueue, notificationProcessor, Notification Database, emailQueue, smsQueue, whatsappQueue, pushQueue, emailProcessor, smsProcessor, whatsappProcessor, pushProcessor |
| Procesamiento plantilla | Notification API → notificationProcessor → Notification Database → [Colas de Canal] → [Procesadores de Canal] → Proveedor Externo → Notification Database | Notification API, notificationProcessor, Notification Database, emailQueue, smsQueue, whatsappQueue, pushQueue, emailProcessor, smsProcessor, whatsappProcessor, pushProcessor |

## 6.2 Patrones De Interacción

| Patrón      | Descripción                   | Tecnología         |
|-------------|------------------------------|--------------------|
| CQRS        | Separación comando/consulta  | Notification API, notificationProcessor, emailProcessor, smsProcessor, whatsappProcessor, pushProcessor |
| Queue       | Cola de mensajes             | ingestionQueue, emailQueue, smsQueue, whatsappQueue, pushQueue |
| Template    | Procesamiento de plantillas  | Template Engine    |

Esta sección describe los principales escenarios de ejecución del sistema, mostrando cómo los componentes interactúan durante el tiempo de ejecución para cumplir con los casos de uso más relevantes arquitectónicamente.

## 6.3 Escenario: Envío Transaccional Individual

### Participantes

- Cliente
- Notification API
- ingestionQueue
- notificationProcessor
- Notification Database
- Colas de Canal (emailQueue, smsQueue, whatsappQueue, pushQueue)
- Procesadores de Canal (emailProcessor, smsProcessor, whatsappProcessor, pushProcessor)
- Proveedor Externo

### Flujo Principal

```mermaid
sequenceDiagram
    participant Cliente as Cliente
    participant API as Notification API
    participant Ingestion as ingestionQueue
    participant Processor as Notification Processor
    participant DB as Notification Database
    participant ColasCanal as Colas de Canal
    participant ProcCanal as Procesadores de Canal
    participant Proveedor as Proveedor Externo

    Cliente->>API: 1. Solicita envío de notificación
    API->>API: 2.1. Valida datos de la solicitud
    API->>API: 2.2. Autentica y autoriza al cliente
    API->>API: 2.3. Construye mensaje de notificación
    API->>Ingestion: 3. Publica mensaje en ingestionQueue
    API->>Cliente: 4. Confirma recepción (HTTP 202)

    Ingestion->>Processor: 5. Notification Processor consume mensaje
    Processor->>Processor: 5.1. Valida reglas de negocio
    Processor->>Processor: 5.2. Determina canales y tipos de notificación
    Processor->>Processor: 5.3. Genera mensaje mediante plantilla según tipo de notificación
    Processor->>DB: 6. Registra notificación
    Processor->>ColasCanal: 7. Encola mensajes generados en colas por canal
    ColasCanal->>ProcCanal: 8. Procesadores de canal consumen mensaje
    ProcCanal->>ProcCanal: 8.1. Aplica lógica de canal (formato, reintentos, etc.)
    ProcCanal->>Proveedor: 9. Envían notificación a Proveedor Externo
    Proveedor->>ProcCanal: 10. Confirman entrega
    ProcCanal->>DB: 11. Actualizan estado final
```

### Aspectos Notables

- Notification Processor registra el evento inicial en Notification Database
- Notification Processor genera mensajes usando plantillas por canal y tipo de notificación
- Los Procesadores de Canal actualizan el estado final en Notification Database tras el envío
- Procesamiento paralelo y desacoplado por canal
- Los nombres de los componentes coinciden exactamente con el DSL

### Métricas De Rendimiento

| Métrica                   | Target                | Medición                |
|---------------------------|----------------------|-------------------------|
| `API Response Time`       | `p95 < 100ms`        | Monitoreo APM           |
| `Event Processing`        | `< 500ms`            | Métricas personalizadas |
| `End-to-End Delivery`     | `< 30s` (transactional) | Métricas de negocio |
| `Capacidad de procesamiento` | `10K req/min/instancia` | Pruebas de carga   |

## 6.4 Escenario: Failover y Recuperación

### Participantes

- Email Processor/SMS Processor/WhatsApp Processor/Push Processor
- Proveedor Externo Primario
- Proveedor Externo Secundario
- Circuit Breaker
- Health Check
- Notification Database

### Flujo de Ejecución

```mermaid
sequenceDiagram
    participant Processor as Email Processor
    participant ProveedorPrimario as Proveedor Externo Primario
    participant ProveedorSecundario as Proveedor Externo Secundario
    participant CircuitBreaker as Circuit Breaker
    participant HealthCheck as Health Check
    participant DB as Notification Database

    Processor->>ProveedorPrimario: 1. Enviar notificación
    ProveedorPrimario-->>Processor: 2. Timeout/Error
    Processor->>CircuitBreaker: 3. Registrar fallo
    CircuitBreaker->>CircuitBreaker: 4. Abrir circuito tras 5 fallos
    Processor->>ProveedorSecundario: 5. Failover a secundario
    ProveedorSecundario->>Processor: 6. Respuesta exitosa
    Processor->>DB: 7. Actualizar estado en Notification Database

    HealthCheck->>ProveedorPrimario: 8. Health check
    ProveedorPrimario->>HealthCheck: 9. Servicio restaurado
    HealthCheck->>CircuitBreaker: 10. Resetear circuito
```

### Políticas de Recuperación

- Circuit breaker: 5 fallos consecutivos
- Timeout: 30 segundos por proveedor
- Health check: Cada 60 segundos
- Recuperación automática: Cuando el proveedor responde

## 6.14 Consideraciones Generales

- Reintentos automáticos ante fallos de canal
- Trazabilidad de cada mensaje
- Aislamiento multi-tenant en cada paso
- Logs estructurados para auditoría
