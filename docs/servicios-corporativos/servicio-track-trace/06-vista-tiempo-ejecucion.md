# 6. Vista de Tiempo de Ejecución

## 6.1 Escenarios Principales

| Escenario                | Flujo                                                        | Componentes principales         |
|--------------------------|--------------------------------------------------------------|---------------------------------|
| **Captura de hito y transmisión SITA** | `API REST` → `Validator` → `Event Store` → `Event Bus` → `SITA Messaging` | `API`, `Validator`, `Event Store`, `Event Bus`, `SITA` |
| **Consulta de trazabilidad**           | `API REST` → `Auth` → `Cache`/`Query Handler` → `Read Store`  | `API`, `Auth`, `Cache`, `Query Handler`, `Read Store`   |

## 6.2 Patrones de Interacción

| Patrón         | Descripción                  | Tecnología         |
|---------------|------------------------------|--------------------|
| **CQRS**          | Separación comando/consulta  | `API`, `Processor`     |
| **Event Sourcing**| Registro de eventos          | `PostgreSQL`         |
| **Pub/Sub**       | Propagación de eventos       | `Event Bus`, `SITA`    |

## 6.3 Escenarios de Runtime

### 6.3.1 Captura de hito operacional y transmisión SITA

```mermaid
sequenceDiagram
    participant Cliente as Cliente externo
    participant API as Tracking API
    participant EventStore as Tracking Database
    participant Processor as Tracking Event Processor
    participant EventBus as Event Bus
    participant SITA as SITA Messaging

    Cliente->>API: POST /api/v1/events (hito)
    API->>API: Validar evento
    alt Evento válido
        API->>EventStore: Guardar evento
        alt Guardado exitoso
            EventStore-->>API: Confirmación
            Processor->>EventStore: Leer nuevos eventos (polling/suscripción)
            Processor->>EventBus: Publicar evento relevante
            SITA->>EventBus: Suscribirse a eventos relevantes
            EventBus-->>SITA: Mensaje SITA
            SITA-->>Processor: Confirmación (ACK)
        else Error al guardar
            EventStore-->>API: Error
            API-->>Cliente: 400 BadRequest
        end
    else Evento inválido
        API-->>Cliente: 400 BadRequest
    end
```

### 6.3.2 Consulta de Trazabilidad

```mermaid
sequenceDiagram
    participant Cliente as Cliente externo
    participant API as Tracking API
    participant BD as Tracking Database

    Cliente->>API: GET /api/v1/trace/{entityId}
    API->>API: Procesar consulta (Query Handler interno)
    API->>BD: Consultar eventos de entidad
    BD-->>API: ListaEventos[]
    API->>API: Construir vista de trazabilidad
    API-->>Cliente: 200 OK {datosTrazabilidad}
```
