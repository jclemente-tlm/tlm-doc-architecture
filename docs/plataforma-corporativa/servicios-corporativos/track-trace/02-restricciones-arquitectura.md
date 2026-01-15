
# 2. Restricciones de la arquitectura

Esta sección define las restricciones técnicas, organizacionales y regulatorias que condicionan el diseño, la implementación y la operación del sistema Track & Trace. Incluye únicamente limitaciones obligatorias y relevantes, asegurando que la arquitectura cumpla con los estándares corporativos, regulatorios y de calidad requeridos.

## 2.1 Restricciones técnicas

| Categoría           | Restricción / Tecnología      | Justificación         |
|---------------------|------------------------------|----------------------|
| Runtime             | `.NET 8`                     | Estandarización y soporte corporativo |
| Base de datos       | `PostgreSQL`                 | ACID, robustez, soporte multi-tenant |
| Arquitectura        | `CQRS`, `Event Sourcing`     | Trazabilidad, escalabilidad, inmutabilidad |
| Cache/Cola          | `Redis`, `AWS SQS`           | Rendimiento, desacoplamiento, event streaming |
| Contenedores        | `Docker`                     | Portabilidad y despliegue consistente |
| APIs                | `REST`                       | Interoperabilidad y estandarización |
| ORM                 | `Entity Framework Core`      | Productividad y mantenibilidad |
| Logging             | `Serilog`                    | Monitoreo centralizado y troubleshooting |
| Testing             | `xUnit`                      | Calidad y automatización |
| Análisis de código  | `SonarQube`                  | Mantenibilidad y calidad continua |

> Todas las tecnologías y patrones deben implementarse usando únicamente las herramientas y librerías aprobadas.

## 2.2 Restricciones de rendimiento

| Métrica        | Objetivo                        | Razón              |
|----------------|---------------------------------|--------------------|
| Capacidad      | `50,000+ eventos/hora`          | Volumen esperado   |
| Latencia       | `< 100ms` ingesta, `< 200ms` consulta | Procesamiento en tiempo real |
| Disponibilidad | `99.9%`                         | SLA empresarial    |
| Retención      | `7 años`                        | Auditoría y compliance |
| Escalabilidad  | Horizontal                      | Crecimiento mediante desacoplamiento |

> El sistema debe soportar reintentos automáticos, deduplicación, idempotencia y manejo eficiente de picos mediante colas y DLQ.

## 2.3 Restricciones de seguridad

| Aspecto         | Requerimiento                | Estándar         |
|-----------------|------------------------------|------------------|
| Inmutabilidad   | `Event sourcing`             | Auditoría y trazabilidad |
| Cifrado         | `TLS 1.3`                    | Protección en tránsito|
| Autenticación   | `JWT` obligatorio (`Keycloak`)| Seguridad API   |
| Auditoría       | Trazabilidad completa        | Compliance       |
| Acceso          | `RBAC` granular              | Seguridad        |
| Cumplimiento    | `GDPR`, `SOX`, locales       | Regulatorio      |

> La autenticación y autorización se implementa exclusivamente con Keycloak y validación de JWT.

## 2.4 Restricciones de integración

| Sistema             | Protocolo / Integración   | Restricción clave           |
|---------------------|--------------------------|----------------------------|
| SITA Messaging      | Event Bus (`AWS SQS`)    | Consumo en tiempo real      |
| Notification System | Event Bus                | Notificaciones por eventos  |
| Identity System     | OAuth2/OIDC              | Acceso seguro vía JWT       |
| APIs externas       | REST                     | Rate limiting, autenticación|
| Dashboards          | REST                     | Actualizaciones rápidas     |

## 2.5 Restricciones de monitoreo y observabilidad

| Componente      | Herramienta         | Propósito                  |
|-----------------|---------------------|----------------------------|
| Métricas        | Prometheus/Grafana  | Monitoreo de performance   |
| Logging         | Serilog, logs estructurados | Auditoría y troubleshooting|
| Tracing         | OpenTelemetry       | Trazas distribuidas        |
| Health Checks   | ASP.NET Core        | Disponibilidad de servicio |

## 2.6 Restricciones organizacionales y operacionales

| Área           | Restricción                   | Impacto              |
|----------------|------------------------------|----------------------|
| Multi-tenancy  | Aislamiento por país         | Regulaciones locales |
| Operaciones    | DevOps 24/7                  | Continuidad negocio  |
| Documentación  | arc42 actualizada            | Mantenibilidad       |

---

**Notas generales:**

- Todas las configuraciones se gestionan por scripts, no por API.
- Autenticación vía OAuth2 con JWT (`client_credentials`).
- Uso obligatorio de contenedores para todos los servicios.
- Multi-tenant y multipaís como requerimiento transversal.
- Cumplimiento de normativas locales de privacidad y trazabilidad.
- Integración con sistemas externos vía API REST.
- Despliegue en AWS (EC2, RDS, SQS, etc.).
- Monitoreo centralizado, logging distribuido y archivado de históricos para observabilidad y cumplimiento.
