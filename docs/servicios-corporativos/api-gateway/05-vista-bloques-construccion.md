# 5. Vista de bloques de construcción

![API Gateway - Vista de Componentes](/diagrams/servicios-corporativos/api_gateway_yarp.png)

*Figura 5.1: Vista de componentes principales del API Gateway.*

## 5.1 Componentes principales

| Componente                    | Responsabilidad                                               | Tecnología                        |
|-------------------------------|--------------------------------------------------------------|-----------------------------------|
| YARP Proxy                    | Proxy inverso, enrutamiento y balanceo de carga              | YARP, ASP.NET Core                |
| Security Middleware           | Validación de tokens JWT y políticas de autorización         | ASP.NET Core Middleware, JWT      |
| Tenant Resolution Middleware  | Resolución y validación de contexto de tenant                | ASP.NET Core Middleware           |
| Rate Limiting Middleware      | Límites de velocidad por tenant y endpoint                   | ASP.NET Core Middleware, Redis    |
| Resilience Middleware         | Circuit breakers y reintentos para resiliencia               | Polly                             |
| Data Processing Middleware    | Validación de esquemas y transformación de payloads          | ASP.NET Core Middleware, JSON Schema |
| Cache Middleware (opcional)   | Cache distribuido con invalidación inteligente               | Redis, ASP.NET Core Response Caching |
| SecretsAndConfigs             | Acceso centralizado a configuraciones y secretos             | AWS Secrets Manager, AppConfig    |
| Observabilidad                | Logging, métricas, health checks                            | Serilog, Prometheus, HealthChecks |

## 5.2 Flujo de procesamiento

| Paso | Acción                          | Componente         |
|------|---------------------------------|--------------------|
| `1`  | Recepción de solicitud          | `YARP Proxy`       |
| `2`  | Validación de autenticación     | `Auth Middleware`  |
| `3`  | Verificación de límites         | `Rate Limiter`     |
| `4`  | Enrutamiento a servicio         | `Load Balancer`    |
| `5`  | Circuit breaking y resiliencia  | `Polly`            |
| `6`  | Logging y métricas              | `Serilog`, `Loki`, `Prometheus`, `Jaeger` |
| `7`  | Respuesta al cliente            | `YARP Proxy`       |

> Todos los bloques y relaciones están alineados con el modelo C4 y los ADRs globales. Los componentes de observabilidad (`Grafana`, `Prometheus`, `Loki`, `Jaeger`) son parte integral del flujo y monitoreo.

## 5.3 Relación con otros sistemas

- El `API Gateway` interactúa con microservicios corporativos, sistemas de identidad (`Keycloak`), servicios de notificación y plataformas de configuración y secretos, según lo definido en los diagramas Structurizr.
- La integración y dependencias están documentadas en los modelos DSL y se reflejan en las vistas de componentes y despliegue.

## 5.4 Consideraciones de despliegue

- Todos los componentes se despliegan en `AWS ECS Fargate` usando `Terraform`.
- Observabilidad y monitoreo centralizados con `Grafana`, `Prometheus`, `Loki` y `Jaeger`.
- Configuración y secretos gestionados externamente, con recarga dinámica y validación de salud.
