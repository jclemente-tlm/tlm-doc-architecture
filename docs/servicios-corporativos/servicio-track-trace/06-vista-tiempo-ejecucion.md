# 6. Vista de tiempo de ejecución

## 6.1 Escenarios principales

| Escenario                        | Flujo principal                                                                                  | Componentes involucrados                        |
|----------------------------------|--------------------------------------------------------------------------------------------------|-------------------------------------------------|
| Captura y procesamiento de evento| Cliente externo → Tracking Ingest API → Tracking Event Queue → Tracking Event Processor → Tracking Database / SITA Messaging | Tracking Ingest API, Tracking Event Queue, Tracking Event Processor, Tracking Database, SITA Messaging |
| Consulta de trazabilidad         | Cliente externo → Tracking Query API → Tracking Database                                         | Tracking Query API, Tracking Database           |

## 6.2 Patrones de interacción

| Patrón         | Descripción                                      | Tecnología/Componente         |
|----------------|--------------------------------------------------|-------------------------------|
| Asincronía     | Desacople entre ingesta y procesamiento          | AWS SQS, Tracking Event Queue |
| Persistencia   | Almacenamiento de eventos y estados              | PostgreSQL, Tracking Database |
| Integración    | Publicación de eventos a sistemas externos (SITA)| SITA Messaging, SNS/SQS       |

## 6.3 Escenarios de runtime

### 6.3.1 Captura y procesamiento de evento

```mermaid
sequenceDiagram
    participant Cliente as Cliente externo
    participant API as Tracking Ingest API
    participant Queue as Tracking Event Queue
    participant Processor as Tracking Event Processor
    participant DB as Tracking Database
    participant SITA as SITA Messaging

    Cliente->>API: POST /api/v1/events
    API->>API: Validar y transformar evento
    API->>Queue: Publicar evento
    Processor->>Queue: Consumir evento
    Processor->>DB: Guardar evento y actualizar estado
    alt Evento relevante para SITA
        Processor->>SITA: Publicar evento SITA
    end
    API-->>Cliente: 202 Accepted
```

### 6.3.2 Consulta de trazabilidad

```mermaid
sequenceDiagram
    participant Cliente as Cliente externo
    participant API as Tracking Query API
    participant DB as Tracking Database

    Cliente->>API: GET /api/v1/trace/{entityId}
    API->>DB: Consultar eventos y estado
    DB-->>API: Datos de trazabilidad
    API-->>Cliente: 200 OK {datosTrazabilidad}
```
