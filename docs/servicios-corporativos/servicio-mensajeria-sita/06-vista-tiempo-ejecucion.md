
# 6. Vista de tiempo de ejecución

Esta sección describe los principales escenarios de ejecución y patrones de interacción del sistema de mensajería SITA, alineados a los componentes y tecnologías implementados.

## 6.1 Escenarios principales

| Escenario                  | Flujo principal                                                                 |
|----------------------------|-------------------------------------------------------------------------------|
| Procesamiento de evento    | Event Consumer → Event Orchestrator → Template Engine → SITA File Generator    |
| Persistencia y auditoría   | SITA File Generator → File Storage / Delivery Log Table                        |
| Envío programado           | Sending Worker → File Fetcher → Partner Sender → Delivery Tracker              |

## 6.2 Patrones de interacción

| Patrón           | Descripción                        | Tecnología principal      |
|------------------|------------------------------------|--------------------------|
| Event-Driven     | Procesamiento asíncrono de eventos | SNS+SQS, .NET 8 Worker   |
| Batch            | Procesamiento por lotes            | .NET 8, Quartz.NET       |
| File-based       | Intercambio de archivos SITA       | S3-Compatible Storage    |
| Observabilidad   | Monitoreo y logging estructurado   | Prometheus, Serilog      |

## 6.3 Flujos de ejecución

### 6.3.1 Procesamiento de evento SITA

```mermaid
sequenceDiagram
    participant SQS as SITA Message Queue (SQS)
    participant EventConsumer as Event Consumer
    participant EventOrchestrator as Event Orchestrator
    participant TemplateEngine as Template Engine
    participant SITAFileGenerator as SITA File Generator
    participant FileStorage as SITA File Storage
    participant MessagingDB as SITA Messaging Database

    SQS->>EventConsumer: Consume evento Track & Trace
    EventConsumer->>EventOrchestrator: Delegar evento para procesamiento
    EventOrchestrator->>TemplateEngine: Solicita procesamiento de plantilla
    TemplateEngine-->>EventOrchestrator: Plantilla procesada
    EventOrchestrator->>SITAFileGenerator: Genera archivo SITA
    SITAFileGenerator->>FileStorage: Almacena archivo SITA
    SITAFileGenerator->>MessagingDB: Registra mensaje para envío
```

### 6.3.2 Envío programado de mensajes

```mermaid
sequenceDiagram
    participant SendingWorker as Sending Worker
    participant MessagingDB as SITA Messaging Database
    participant FileFetcher as File Fetcher
    participant FileStorage as SITA File Storage
    participant PartnerSender as Partner Sender
    participant Partner as Aerolínea/Partner

    SendingWorker->>MessagingDB: Consulta archivos pendientes de envío
    SendingWorker->>FileFetcher: Solicita descarga de archivo SITA
    FileFetcher->>FileStorage: Recupera archivo SITA
    FileFetcher-->>SendingWorker: Archivo SITA
    SendingWorker->>PartnerSender: Solicita envío a partner
    PartnerSender->>Partner: Envía archivo SITA
    PartnerSender->>MessagingDB: Actualiza estado de entrega
```
