# 5. Vista de Bloques de Construcción

Esta sección describe la arquitectura modular del **Sistema Track & Trace**, basada en CQRS y Event Sourcing. Se detallan los contenedores, componentes principales, esquemas de datos y la relación entre los bloques, con diagramas C4 para ilustrar la estructura y la interacción.

![Vista General del Sistema Track & Trace](/diagrams/servicios-corporativos/track_and_trace_system.png)
*Figura 5.1: Contenedores principales del sistema*

![Componentes Command API](/diagrams/servicios-corporativos/track_and_trace_tracking_api.png)
*Figura 5.2: Componentes internos del Command API*

![Componentes Query API](/diagrams/servicios-corporativos/track_and_trace_tracking_api.png)
*Figura 5.3: Componentes internos del Query API*

## 5.1 Contenedores Principales

| Contenedor         | Responsabilidad                        | Tecnología         |
|--------------------|----------------------------------------|--------------------|
| **Command API**    | Ingesta de eventos (Write Side)        | `.NET 8 Web API`     |
| **Query API**      | Consultas de trazabilidad (Read Side)  | `.NET 8 Web API`     |
| **Event Store**    | Almacenamiento inmutable de eventos    | `PostgreSQL 15+`     |
| **Read Models**    | Vistas optimizadas para consultas      | `PostgreSQL 15+`     |

## 5.2 Componentes del Command API

| Componente            | Responsabilidad                        | Tecnología         |
|-----------------------|----------------------------------------|--------------------|
| **Event Controller**  | Endpoint REST para eventos             | `ASP.NET Core`     |
| **Event Validator**   | Validación de eventos                  | `FluentValidation` |
| **Event Store Service** | Persistencia de eventos              | `.NET 8`           |
| **Event Publisher**   | Publicación de eventos a bus           | `.NET 8`           |

## 5.3 Componentes del Query API

| Componente            | Responsabilidad                        | Tecnología         |
|-----------------------|----------------------------------------|--------------------|
| **Query Controller**  | Endpoints REST y GraphQL               | `ASP.NET Core`     |
| **Query Handler**     | Procesamiento de consultas             | `.NET 8`           |
| **Read Model Service**| Acceso a vistas optimizadas            | `Entity Framework` |
| **Analytics Service** | Análisis de patrones y métricas        | `.NET 8`           |

## 5.4 Esquemas de Base de Datos

### 5.4.1 Tabla: `event_store`

| Campo           | Tipo           | Descripción                        | Restricciones                  |
|-----------------|---------------|------------------------------------|-------------------------------|
| `id`            | `UUID`         | Identificador único de evento      | PRIMARY KEY                   |
| `aggregate_id`  | `UUID`         | ID de la entidad agregada          | NOT NULL, INDEX               |
| `event_type`    | `VARCHAR(100)` | Tipo de evento                     | NOT NULL                      |
| `payload`       | `JSONB`        | Datos del evento                   | NOT NULL                      |
| `timestamp`     | `TIMESTAMP`    | Fecha de ocurrencia                | NOT NULL, DEFAULT NOW()       |
| `correlation_id`| `VARCHAR(100)` | ID de correlación                  | NULL, INDEX                   |
| `tenant_id`     | `VARCHAR(50)`  | Identificador del tenant           | NOT NULL, INDEX               |

### 5.4.2 Tabla: `read_models`

| Campo           | Tipo           | Descripción                        | Restricciones                  |
|-----------------|---------------|------------------------------------|-------------------------------|
| `id`            | `UUID`         | Identificador único                | PRIMARY KEY                   |
| `model_type`    | `VARCHAR(100)` | Tipo de vista                      | NOT NULL                      |
| `data`          | `JSONB`        | Datos optimizados para consulta    | NOT NULL                      |
| `updated_at`    | `TIMESTAMP`    | Última actualización               | NOT NULL, DEFAULT NOW()       |
| `tenant_id`     | `VARCHAR(50)`  | Identificador del tenant           | NOT NULL, INDEX               |

## 5.5 Endpoints de API

- **POST** `/api/v1/events`: Ingesta de nuevos eventos operacionales
- **GET** `/api/v1/trace/{correlationId}`: Consulta de trazabilidad por correlación
- **GET** `/api/v1/analytics`: Métricas y análisis de eventos
- **GraphQL** `/api/v1/query`: Consultas avanzadas sobre modelos de lectura

## 5.6 Contratos de Datos (DTOs)

### 5.6.1 `EventRequest`

```csharp
public class EventRequest
{
    public string EventType { get; set; }
    public Guid AggregateId { get; set; }
    public string TenantId { get; set; }
    public DateTime Timestamp { get; set; }
    public Dictionary<string, object> Payload { get; set; }
    public string CorrelationId { get; set; }
}
```

### 5.6.2 `TraceResponse`

```csharp
public class TraceResponse
{
    public string CorrelationId { get; set; }
    public List<EventDto> Events { get; set; }
}

public class EventDto
{
    public string EventType { get; set; }
    public DateTime Timestamp { get; set; }
    public Dictionary<string, object> Payload { get; set; }
}
```

## 5.7 Ejemplos de Implementación

### 5.7.1 Controller de Eventos

```csharp
[ApiController]
[Route("api/v1/events")]
public class EventsController : ControllerBase
{
    private readonly IEventService _eventService;
    private readonly ILogger<EventsController> _logger;

    public EventsController(IEventService eventService, ILogger<EventsController> logger)
    {
        _eventService = eventService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<IActionResult> IngestEvent([FromBody] EventRequest request)
    {
        try
        {
            await _eventService.IngestAsync(request);
            return Accepted();
        }
        catch (ValidationException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error ingesting event {CorrelationId}", request.CorrelationId);
            return StatusCode(500, new { error = "Internal server error" });
        }
    }
}
```

### 5.7.2 Servicio de Consultas

```csharp
public class QueryService : IQueryService
{
    public async Task<TraceResponse> GetTraceAsync(string correlationId)
    {
        // Lógica para recuperar eventos correlacionados
        // ...
    }
}
```
