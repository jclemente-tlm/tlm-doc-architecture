# 6. Vista de tiempo de ejecución

Esta sección describe los principales escenarios de ejecución y patrones de interacción del sistema de mensajería SITA, detallando flujos críticos, manejo de errores, patrones de resiliencia y consideraciones de monitoreo y despliegue, alineados a mejores prácticas de arquitectura y operación.

## 6.1 Escenarios principales

| Escenario                  | Flujo                                         | Componentes        |
|----------------------------|-----------------------------------------------|--------------------|
| **Procesamiento evento**   | Event Consumer → Orchestrator → Generator     | Event Processor    |
| **Generación archivo**     | Template Engine → SITA Generator → Storage    | Event Processor    |
| **Envío programado**       | Sending Worker → Fetcher → Partner Sender     | Sender            |

## 6.2 Patrones de interacción

| Patrón           | Descripción                | Tecnología           |
|------------------|---------------------------|----------------------|
| **Event-Driven** | Procesamiento asíncrono    | PostgreSQL queue     |
| **Worker Service** | Procesamiento background | .NET 8               |
| **File-based**   | Intercambio archivos       | Sistema archivos     |

## 6.3 Flujos de ejecución detallados

### 6.3.1 Envío de mensaje SITA outbound

```mermaid
sequenceDiagram
    participant App as Aplicación Cliente
    participant API as SITA Messaging API
    participant Validator as Message Validator
    participant Translator as Message Translator
    participant Adapter as SITA Protocol Adapter
    participant SITA as Red SITA
    participant DB as Message Store
    participant Kafka as Event Bus
    participant Track as Track & Trace

    App->>API: POST /api/v1/sita-messages/send
    API->>Validator: ValidateMessage(request)

    alt Validation Success
        Validator-->>API: ValidationResult.Valid
        API->>DB: SaveMessage(PENDING)
        API-->>App: 202 Accepted {messageId}

        API->>Translator: TranslateToSitaFormat(message)
        Translator-->>API: SitaFormattedMessage

        API->>Adapter: SendMessage(sitaMessage)
        Adapter->>SITA: Transmit via SITA Protocol

        alt Éxito SITA
            SITA-->>Adapter: ACK/NAK Response
            Adapter-->>API: SendResult.Success
            API->>DB: UpdateStatus(SENT)
            API->>Kafka: PublishEvent(MessageSentEvent)
            Kafka->>Track: LogEvent(SitaMessageSent)
        else Error SITA
            SITA-->>Adapter: Error/Timeout
            Adapter-->>API: SendResult.Failed
            API->>DB: UpdateStatus(FAILED)
            API->>Kafka: PublishEvent(MessageFailedEvent)
        end

    else Validación Fallida
        Validator-->>API: ValidationResult.Invalid
        API-->>App: 400 BadRequest {errors}
    end
```

### 6.3.2 Recepción de mensaje SITA inbound

```mermaid
sequenceDiagram
    participant SITA as Red SITA
    participant Adapter as SITA Protocol Adapter
    participant Processor as Message Processor
    participant Parser as Message Parser
    participant Router as Message Router
    participant Corp as Servicios Corporativos
    participant DB as Message Store
    participant Kafka as Event Bus

    SITA->>Adapter: Incoming SITA Message
    Adapter->>Processor: ProcessIncomingMessage(rawMessage)

    Processor->>Parser: ParseSitaMessage(rawMessage)
    Parser-->>Processor: ParsedMessage

    Processor->>DB: SaveIncomingMessage(message)
    Processor->>Router: DetermineRoute(message)

    alt Ruta a Servicios Corporativos
        Router-->>Processor: Route.ToCorporateServices
        Processor->>Corp: ForwardMessage(translatedMessage)

        alt Procesamiento Corporativo Exitoso
            Corp-->>Processor: ProcessingResult.Success
            Processor->>DB: UpdateStatus(PROCESSED)
            Processor->>Kafka: PublishEvent(MessageProcessedEvent)
            Processor->>Adapter: SendAcknowledgment(ACK)
            Adapter->>SITA: ACK Response
        else Procesamiento Corporativo Fallido
            Corp-->>Processor: ProcessingResult.Failed
            Processor->>DB: UpdateStatus(FAILED)
            Processor->>Kafka: PublishEvent(MessageFailedEvent)
            Processor->>Adapter: SendAcknowledgment(NAK)
            Adapter->>SITA: NAK Response
        end

    else Ruta No Encontrada
        Router-->>Processor: Route.NotFound
        Processor->>DB: UpdateStatus(UNROUTABLE)
        Processor->>Adapter: SendAcknowledgment(NAK)
        Adapter->>SITA: NAK Response
    end
```

### 6.3.3 Procesamiento batch de mensajes

```mermaid
sequenceDiagram
    participant Scheduler as Batch Scheduler
    participant Processor as Batch Processor
    participant DB as Message Store
    participant Adapter as SITA Protocol Adapter
    participant SITA as Red SITA
    participant Monitor as Monitoring

    Scheduler->>Processor: TriggerBatchProcessing()
    Processor->>DB: GetPendingMessages(batchSize: 100)
    DB-->>Processor: PendingMessages[]

    loop For each message batch
        Processor->>Adapter: SendBatch(messages[])

        par Parallel processing
            Adapter->>SITA: SendMessage(msg1)
            Adapter->>SITA: SendMessage(msg2)
            Adapter->>SITA: SendMessage(msgN)
        end

        alt Todo Exitoso
            SITA-->>Adapter: ACK Responses
            Adapter-->>Processor: BatchResult.AllSuccess
            Processor->>DB: UpdateBatchStatus(SENT)
        else Éxito Parcial
            SITA-->>Adapter: Mixed ACK/NAK
            Adapter-->>Processor: BatchResult.PartialSuccess
            Processor->>DB: UpdateIndividualStatuses()
        else Todo Fallido
            SITA-->>Adapter: NAK/Timeout
            Adapter-->>Processor: BatchResult.AllFailed
            Processor->>DB: UpdateBatchStatus(FAILED)
        end
    end

    Processor->>Monitor: ReportBatchMetrics(stats)
```

## 6.4 Flujos de control y resiliencia

### 6.4.1 Gestión de conexiones SITA

- Pool de conexiones concurrentes y heartbeat
- Health checks y auto-reconexión
- Load balancing y failover automático

### 6.4.2 Validación y transformación de mensajes

- Validación de esquema y reglas de negocio
- Transformación entre formatos y enriquecimiento
- Cache de reglas y validaciones asíncronas

### 6.4.3 Manejo de errores y retry logic

- Retries con backoff exponencial para errores transitorios
- Dead letter para errores permanentes
- Logging y métricas de intentos y fallos

## 6.5 Patrones de runtime

- **Connection Pool**: Conexiones persistentes y balanceadas
- **Circuit Breaker**: Protección ante fallos de destino
- **Bulkhead**: Aislamiento de recursos por tenant
- **Saga**: Coordinación de procesos multi-step

## 6.6 Performance y monitoreo

- 1,000 mensajes/segundo por instancia
- Batch de 100 mensajes para eficiencia
- P95 < 200ms API, < 2s transmisión SITA
- Uso de CPU/memoria autoescalable
- Health checks, métricas y alertas operacionales

## 6.7 Escenarios de despliegue

- **Blue-Green**: Zero downtime, validación y rollback instantáneo
- **Canary**: Rollout gradual, monitoreo y auto-rollback
- **Disaster Recovery**: RTO 15min, RPO 5min, failover automático
