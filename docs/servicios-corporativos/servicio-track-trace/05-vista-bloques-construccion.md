
# 5. Vista de bloques de construcción

Esta sección describe la estructura modular del sistema **Track & Trace**, presentando los bloques principales (contenedores y componentes), sus responsabilidades y tecnologías, así como los principales esquemas de datos y contratos de integración. La visión se centra en los elementos implementados y sus relaciones clave para la trazabilidad operacional multi-tenant.

![Vista General del Sistema Track & Trace](/diagrams/servicios-corporativos/track_and_trace_system.png)

## 5.1 Contenedores principales

| Contenedor                    | Responsabilidad                                         | Tecnología                      |
|-------------------------------|--------------------------------------------------------|---------------------------------|
| Tracking Ingest API           | API REST para ingesta y validación de eventos           | C#, ASP.NET Core, REST API      |
| Tracking Query API            | API REST para consultas de tracking                     | C#, ASP.NET Core, REST API      |
| Tracking Event Queue          | Cola para desacoplar ingesta y procesamiento asíncrono  | AWS SQS                         |
| Tracking Event Processor      | Procesamiento, validación y enriquecimiento de eventos   | C#, ASP.NET Core, AWS SDK (SQS) |
| Tracking Web                  | Visualización en tiempo real y análisis de eventos       | React, TypeScript               |
| Tracking Database             | Almacenamiento de eventos, estados y configuraciones     | PostgreSQL                      |

## 5.2 Componentes principales

### Tracking Ingest API

![Componentes Tracking Ingest API](/diagrams/servicios-corporativos/track_and_trace_tracking_ingest_api.png)

| Componente                  | Función                                                        | Tecnología                 |
|-----------------------------|----------------------------------------------------------------|----------------------------|
| Tracking Event Controller   | Endpoints REST para recepción masiva de eventos                 | ASP.NET Core               |
| Tracking Event Service      | Procesa y valida eventos, reglas de negocio                     | C#                         |
| Tracking Event Publisher    | Publica eventos validados en la cola SQS                        | C#, AWS SDK (SQS)          |
| TenantSettings Repository   | Gestiona configuraciones por tenant                             | C#, .NET 8, EF Core        |
| SecretsAndConfigs           | Acceso centralizado a configuraciones y secretos                | AWS Secrets Manager, AppConfig |
| Observability               | Logging, métricas, health checks                                | Serilog, Prometheus, HealthChecks |

### Tracking Query API

![Componentes Tracking Query API](/diagrams/servicios-corporativos/track_and_trace_tracking_query_api.png)

| Componente                  | Función                                                        | Tecnología                 |
|-----------------------------|----------------------------------------------------------------|----------------------------|
| Tracking Query Controller   | Endpoints REST para consultas de trazabilidad                   | ASP.NET Core               |
| Tracking Query Service      | Orquesta consultas y lógica de negocio                          | C#                         |
| Tracking Data Repository    | Acceso optimizado a datos de tracking                           | C#, EF Core                |
| TenantSettings Repository   | Gestiona configuraciones por tenant                             | C#, .NET 8, EF Core        |
| SecretsAndConfigs           | Acceso centralizado a configuraciones y secretos                | AWS Secrets Manager, AppConfig |
| Observabilidad               | Logging, métricas, health checks                                | Serilog, Prometheus, HealthChecks |

### Tracking Event Processor

![Componentes Tracking Event Processor](/diagrams/servicios-corporativos/track_and_trace_event_processor.png)

| Componente                  | Función                                                        | Tecnología                 |
|-----------------------------|----------------------------------------------------------------|----------------------------|
| Tracking Event Consumer     | Consume eventos desde la cola SQS                               | C#, AWS SDK (SQS)          |
| Tracking Event Handler      | Validaciones y reglas de negocio                                | C#                         |
| Tracking Processing Service | Lógica de negocio para enriquecimiento y correlación            | C#                         |
| Tracking Event Repository   | Persiste eventos crudos y enriquecidos                          | C#, EF Core                |
| Downstream Event Publisher  | Publica eventos procesados a sistemas downstream                | C#, AWS SDK (SNS)          |
| TenantSettings Repository   | Gestiona configuraciones por tenant                             | C#, .NET 8, EF Core        |
| SecretsAndConfigs           | Acceso centralizado a configuraciones y secretos                | AWS Secrets Manager, AppConfig |
| Observabilidad               | Logging, métricas, health checks                                | Serilog, Prometheus, HealthChecks |

## 5.3 Esquemas de datos

### Tabla: `tenant_tracking_settings`

| Campo               | Tipo           | Descripción                                         | Restricciones                  |
|---------------------|----------------|-----------------------------------------------------|-------------------------------|
| id                  | UUID           | Identificador único                                 | PRIMARY KEY                   |
| tenant_id           | VARCHAR(50)    | Identificador del tenant                            | NOT NULL, INDEX               |
| country_code        | VARCHAR(5)     | Código de país (PE, EC, CO, MX)                     | NOT NULL, INDEX               |
| allowed_event_types | JSONB          | Tipos de eventos permitidos (tracking, sita, etc.)  | NOT NULL                      |
| event_retention_days| INTEGER        | Días de retención de eventos                        | NULL                          |
| max_payload_size    | INTEGER        | Tamaño máximo permitido para eventos (bytes)         | NULL                          |
| allowed_sources     | JSONB          | Sistemas/autores permitidos para registrar eventos  | NULL                          |
| preferences         | JSONB          | Preferencias adicionales (idioma, formato, etc.)    | NULL                          |
| is_active           | BOOLEAN        | Configuración activa                                | DEFAULT true                  |
| created_at          | TIMESTAMP      | Fecha de creación                                   | NOT NULL, DEFAULT NOW()       |
| updated_at          | TIMESTAMP      | Fecha de actualización                              | NOT NULL, DEFAULT NOW()       |

**Ejemplo de datos:**

| id                                   | tenant_id  | country_code | allowed_event_types           | event_retention_days | max_payload_size | allowed_sources         | preferences                        | is_active | created_at           | updated_at           |
|---------------------------------------|------------|--------------|------------------------------|---------------------|------------------|------------------------|-------------------------------------|-----------|----------------------|----------------------|
| `7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d` | `tenant-pe`  | `PE`           | `["tracking","sita"]`        | `365`               | `1048576`        | `["appPeru","sitaGW"]`  | `{"idioma":"es"}`                  | `true`    | `2025-08-13T07:00:00Z` | `2025-08-13T07:00:00Z` |
| `8b9c0d1e-2f3a-4b5c-6d7e-8f9a0b1c2d3e` | `tenant-ec`  | `EC`           | `["tracking"]`               | `180`               | `524288`         | `["appEcuador"]`        | `{"idioma":"en"}`                  | `true`    | `2025-08-13T07:30:00Z` | `2025-08-13T07:30:00Z` |

### Tabla: event_store

| Campo           | Tipo           | Descripción                        | Restricciones                  |
|-----------------|----------------|------------------------------------|-------------------------------|
| id              | UUID           | Identificador único de evento      | PRIMARY KEY                   |
| tenant_id       | VARCHAR(50)    | Identificador del tenant           | NOT NULL, INDEX               |
| correlation_id  | VARCHAR(100)   | ID de correlación                  | NULL, INDEX                   |
| aggregate_id    | UUID           | ID de la entidad agregada          | NOT NULL, INDEX               |
| event_type      | VARCHAR(100)   | Tipo de evento                     | NOT NULL                      |
| payload         | JSONB          | Datos del evento                   | NOT NULL                      |
| timestamp       | TIMESTAMP      | Fecha de ocurrencia                | NOT NULL, DEFAULT NOW()       |
| created_at      | TIMESTAMP      | Fecha y hora de creación del registro | NOT NULL, DEFAULT NOW()   |
| updated_at      | TIMESTAMP      | Fecha y hora de última actualización | NULL                        |

### Tabla: trace_views

| Campo           | Tipo           | Descripción                        | Restricciones                  |
|-----------------|----------------|------------------------------------|-------------------------------|
| id              | UUID           | Identificador único                | PRIMARY KEY                   |
| tenant_id       | VARCHAR(50)    | Identificador del tenant           | NOT NULL, INDEX               |
| correlation_id  | VARCHAR(100)   | ID de correlación                  | NULL, INDEX                   |
| view_type       | VARCHAR(100)   | Tipo de vista                      | NOT NULL                      |
| data            | JSONB          | Datos optimizados para consulta    | NOT NULL                      |
| created_at      | TIMESTAMP      | Fecha y hora de creación del registro | NOT NULL, DEFAULT NOW()   |
| updated_at      | TIMESTAMP      | Última actualización               | NOT NULL, DEFAULT NOW()       |

#### Ejemplo de contenido y actualización de trace view para trazabilidad

El campo `data` en la tabla `trace_views` almacena la información agregada y optimizada para cada correlación. Por ejemplo:

```json
{
  "correlation_id": "ABC123",
  "status": "en_transito",
  "events": [
    { "event_type": "checked_in", "timestamp": "2025-09-11T08:00:00Z", "location": "LIM" },
    { "event_type": "loaded", "timestamp": "2025-09-11T08:30:00Z", "location": "LIM" },
    { "event_type": "arrived", "timestamp": "2025-09-11T09:15:00Z", "location": "JFK" }
  ]
}
```

Cada vez que llega un nuevo evento para el `correlation_id`:

1. El Event Processor procesa el evento y lo agrega al arreglo `events`.
2. El campo `status` se actualiza según el último evento relevante.
3. El registro en la tabla `trace_views` se actualiza con el nuevo JSON.

**Ejemplo de actualización:**

Si llega un evento:

```json
{ "event_type": "delivered", "timestamp": "2025-09-11T10:00:00Z", "location": "JFK" }
```

El JSON actualizado sería:

```json
{
  "correlation_id": "ABC123",
  "status": "delivered",
  "events": [
    { "event_type": "checked_in", "timestamp": "2025-09-11T08:00:00Z", "location": "LIM" },
    { "event_type": "loaded", "timestamp": "2025-09-11T08:30:00Z", "location": "LIM" },
    { "event_type": "arrived", "timestamp": "2025-09-11T09:15:00Z", "location": "JFK" },
    { "event_type": "delivered", "timestamp": "2025-09-11T10:00:00Z", "location": "JFK" }
  ]
}
```

## 5.4 Endpoints principales

### Endpoints de Tracking Ingest API

- **POST** `/api/v1/events`: Ingesta de eventos operacionales (tracking, sita, etc.)
- **GET** `/api/v1/events/health`: Estado de salud del API de ingesta
- **GET** `/api/v1/events/metrics`: Métricas de ingesta y procesamiento

### Endpoints de Tracking Query API

- **GET** `/api/v1/trace/{correlationId}`: Consulta de trazabilidad por correlación
- **GET** `/api/v1/trace?aggregateId={aggregateId}`: Consulta de historial por entidad agregada
- **GET** `/api/v1/trace/health`: Estado de salud del API de consulta
- **GET** `/api/v1/trace/metrics`: Métricas de consulta y uso

## 5.5 Contratos de entrada y salida

### Contrato de entrada: EventRequest (Tracking Ingest API)

| Campo           | Tipo                | Descripción                                 |
|-----------------|---------------------|---------------------------------------------|
| tenant_id       | string              | Identificador del tenant                    |
| correlation_id  | string              | ID de correlación                           |
| aggregate_id    | UUID                | ID de la entidad agregada                   |
| event_type      | string              | Tipo de evento (tracking, sita, etc.)       |
| timestamp       | string (ISO 8601)   | Fecha de ocurrencia                         |
| payload         | objeto              | Datos del evento                            |

**Ejemplo:**

```json
{
    "tenant_id": "talma-pe",
    "correlation_id": "ABC123",
    "aggregate_id": "BAG001",
    "event_type": "tracking_arrived",
    "timestamp": "2025-09-11T09:15:00Z",
    "payload": {
        "location": "JFK",
        "operator": "Juan Perez"
    }
}
```

### Contrato de salida: TraceResponse (Tracking Query API)

| Campo           | Tipo                | Descripción                                 |
|-----------------|---------------------|---------------------------------------------|
| tenant_id       | string              | Identificador del tenant                    |
| correlation_id  | string              | ID de correlación                           |
| aggregate_id    | UUID                | ID de la entidad agregada                   |
| status          | string              | Estado actual                               |
| events          | array de objetos    | Historial de eventos                        |

**Ejemplo:**

```json
{
    "tenant_id": "talma-pe",
    "correlation_id": "ABC123",
    "aggregate_id": "BAG001",
    "status": "arrived",
    "events": [
        { "event_type": "checked_in", "timestamp": "2025-09-11T08:00:00Z", "payload": { "location": "LIM" } },
        { "event_type": "loaded", "timestamp": "2025-09-11T08:30:00Z", "payload": { "location": "LIM" } },
        { "event_type": "arrived", "timestamp": "2025-09-11T09:15:00Z", "payload": { "location": "JFK" } }
    ]
}
```
