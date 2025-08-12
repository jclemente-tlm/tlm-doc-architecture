# 7. Vista de Implementación

![Vista de implementación del Sistema de Track & Trace](/diagrams/servicios-corporativos/track_and_trace_deployment.png)
*Figura 7.1: Implementación de Componentes de principales del sistema*

## 7.1 Estructura del Proyecto

| Componente                | Ubicación                        | Tecnología                |
|---------------------------|----------------------------------|---------------------------|
| **Tracking API**          | `/src/TrackingAPI`               | `.NET 8 Web API`          |
| **Tracking Event Processor** | `/src/TrackingEventProcessor`  | `.NET 8 Worker`           |
| **Tracking Database**     | `AWS RDS`                        | `PostgreSQL 15+`          |
| **Event Bus**             | `AWS MSK` / `RabbitMQ`           | `Kafka` / `RabbitMQ`      |
| **SITA Messaging**        | `Externo`                        | `SITA`                    |

## 7.2 Dependencias Principales

| Dependencia           | Versión | Propósito                |
|----------------------|---------|--------------------------|
| `Entity Framework Core` | 8.0+    | ORM                     |
| `FluentValidation`      | 11.0+   | Validación              |
| `Mapster`               | 7.0+    | Mapeo de objetos        |
| `Serilog`               | 3.0+    | Logging estructurado    |
| `OpenTelemetry`         | 1.7+    | Trazas y métricas       |
| `Prometheus-net`        | 6.0+    | Métricas                |

## 7.3 Organización de Código

```text
src/
├── TrackingAPI/                  # API REST principal
│   ├── Controllers/              # Controladores REST
│   ├── Middleware/               # Middleware HTTP
│   ├── Configuration/            # Configuración DI
│   └── Program.cs                # Entry Point
├── Application/                  # Lógica de aplicación (CQRS)
│   ├── Commands/                 # Comandos
│   ├── Queries/                  # Consultas
│   ├── Validators/               # Reglas FluentValidation
│   ├── Services/                 # Servicios de aplicación
│   └── DTOs/                     # Data Transfer Objects
├── Domain/                       # Modelo de dominio
│   ├── Entities/                 # Entidades
│   ├── ValueObjects/             # Value Objects
│   ├── Events/                   # Eventos de dominio
│   └── Services/                 # Servicios de dominio
├── Infrastructure/               # Infraestructura
│   ├── EventStore/               # Implementación Event Store
│   ├── EventBus/                 # Integración Event Bus
│   ├── Authentication/           # Keycloak/JWT
│   └── Observabilidad/           # Logs, métricas, trazas
└── Tests/                        # Pruebas
    ├── Unit/                     # Unit Tests
    └── Integration/              # Integration Tests
```

## 7.4 Configuración de Despliegue

- Contenedores Docker multi-stage para `Tracking API` y `Tracking Event Processor`
- Despliegue en Kubernetes con probes de salud y recursos definidos
- Variables de entorno para conexión a base de datos, autenticación y observabilidad
- Instrumentación obligatoria: logs (`Serilog`), métricas (`Prometheus-net`), trazas (`OpenTelemetry`, Jaeger)

## 7.5 Seguridad y Observabilidad

- Autenticación y autorización con `Keycloak` (JWT)
- Logs estructurados con `Serilog`
- Métricas expuestas vía `Prometheus`
- Trazas distribuidas con `OpenTelemetry` y `Jaeger`
- Health checks y endpoints de monitoreo

## 7.6 Infraestructura como Código

- `Terraform` para provisión de `AWS RDS`, `Event Bus` y recursos de red
- `Helm Charts` para despliegue en Kubernetes
