# 5. Vista de bloques de construcción

![API Gateway - Vista de Componentes](/diagrams/servicios-corporativos/api_gateway_yarp.png)

*Figura 5.1: Vista de componentes del `API Gateway` (ver modelo Structurizr para relaciones y dependencias)*

## 5.1 Componentes principales

| Componente            | Responsabilidad                        | Tecnología                  |
|-----------------------|----------------------------------------|-----------------------------|
| `YARP Proxy`          | Enrutamiento y proxy reverso           | `YARP`                      |
| `Auth Middleware`     | Validación de tokens `JWT`             | `.NET 8`, `Keycloak`        |
| `Rate Limiter`        | Control de velocidad multi-tenant      | `Redis`                     |
| `Load Balancer`       | Distribución de carga                  | `ALB`, `YARP`               |
| `Circuit Breaker`     | Resiliencia ante fallos                | `Polly`                     |
| `Logging`             | Registro estructurado de eventos       | `Serilog`, `Loki`           |
| `Metrics`             | Recolección de métricas                | `Prometheus`                |
| `Tracing`             | Trazabilidad distribuida               | `Jaeger`, `OpenTelemetry`   |
| `Configuración`       | Configuración dinámica y secretos      | `AWS SSM`, `Secrets Manager`|

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

> Todos los bloques y relaciones están alineados con el modelo C4 en Structurizr y los ADRs globales. Los componentes de observabilidad (`Grafana`, `Prometheus`, `Loki`, `Jaeger`) son parte integral del flujo y monitoreo.

## 5.3 Relación con otros sistemas

- El `API Gateway` interactúa con microservicios corporativos, sistemas de identidad (`Keycloak`), servicios de notificación, y plataformas de configuración y secretos, según lo definido en los diagramas Structurizr.
- La integración y dependencias están documentadas en los modelos DSL y se reflejan en las vistas de componentes y despliegue.

## 5.4 Consideraciones de despliegue

- Todos los componentes se despliegan en `AWS ECS Fargate` usando `Terraform`.
- Observabilidad y monitoreo centralizados con `Grafana`, `Prometheus`, `Loki` y `Jaeger`.
- Configuración y secretos gestionados externamente, con recarga dinámica y validación de salud.

---

> Esta vista de bloques está alineada con los modelos C4 y Structurizr DSL, asegurando trazabilidad, observabilidad y despliegue profesional en AWS ECS/Terraform.
