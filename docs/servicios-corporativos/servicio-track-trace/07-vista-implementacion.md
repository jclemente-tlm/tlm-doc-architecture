# 7. Vista de implementación

![Vista de implementación del Sistema de Track & Trace](/diagrams/servicios-corporativos/track_and_trace_deployment.png)
*Figura 7.1: Implementación de componentes principales del sistema*

## 7.1 Estructura de despliegue

| Componente                    | Plataforma/Ubicación                | Tecnología                |
|-------------------------------|-------------------------------------|---------------------------|
| Tracking Ingest API           | ECS Fargate (Docker)                | .NET 8, ASP.NET Core      |
| Tracking Query API            | ECS Fargate (Docker)                | .NET 8, ASP.NET Core      |
| Tracking Event Processor      | ECS Fargate (Docker)                | .NET 8 Worker             |
| Tracking Dashboard            | ECS Fargate (Docker)                | React, TypeScript         |
| Tracking Event Queue          | AWS SQS                             | SQS                       |
| Tracking Database             | AWS RDS (Aurora PostgreSQL)         | PostgreSQL                |
| Load Balancer                 | AWS Elastic Load Balancer           | ELB                       |

## 7.2 Dependencias principales

| Dependencia           | Versión | Propósito                |
|----------------------|---------|--------------------------|
| `Entity Framework Core` | 8.0+    | ORM                     |
| `FluentValidation`      | 11.0+   | Validación              |
| `Mapster`               | 7.0+    | Mapeo de objetos        |
| `Serilog`               | 3.0+    | Logging estructurado    |
| `OpenTelemetry`         | 1.7+    | Trazas y métricas       |
| `Prometheus-net`        | 6.0+    | Métricas                |

## 7.3 Configuración de despliegue

- Contenedores Docker multi-stage para cada servicio.
- Orquestación y despliegue en AWS ECS Fargate.
- Balanceo de carga con AWS ELB.
- Probes de salud y métricas expuestas.
- Persistencia en AWS RDS (Aurora PostgreSQL).
- Mensajería desacoplada con AWS SQS.
- Variables de entorno para conexión a base de datos, autenticación y observabilidad
- Instrumentación obligatoria: logs (`Serilog`), métricas (`Prometheus-net`), trazas (`OpenTelemetry`, Jaeger)

## 7.4 Seguridad y observabilidad

- Autenticación y autorización con `Keycloak` (JWT)
- Logs estructurados con `Serilog`
- Métricas expuestas vía `Prometheus`
- Trazas distribuidas con `OpenTelemetry` y `Jaeger`
- Health checks y endpoints de monitoreo

## 7.5 Infraestructura como código

- `Terraform` para provisión de `AWS RDS`, `Event Bus` y recursos de red
- `Helm Charts` para despliegue en Kubernetes
