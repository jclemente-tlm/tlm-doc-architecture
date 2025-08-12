# 12. Glosario

Este glosario define los términos técnicos, conceptos clave y acrónimos utilizados en la documentación del `Sistema de Notificaciones`, proporcionando claridad y consistencia para equipos técnicos y stakeholders.

## 12.1 Términos Principales

| Término           | Definición                                                      |
|-------------------|-----------------------------------------------------------------|
| Notification      | Mensaje enviado a usuarios finales                              |
| Template          | Plantilla para generar contenido dinámico                       |
| Handler           | Procesador de canal específico (`email`, `SMS`, `push`, etc.)   |
| Queue             | Cola de mensajes pendientes de procesamiento                    |
| Attachment        | Archivo adjunto a una notificación                              |
| Channel           | Medio de envío (`email`, `SMS`, `push`, `WhatsApp`, etc.)       |
| Scheduler         | Programador de envíos futuros                                   |
| Provider          | Servicio externo de entrega (`SendGrid`, `Twilio`, etc.)        |
| Template Engine   | Motor para procesar plantillas y datos (`RazorEngine`, `Liquid`)|
| Multi-tenant      | Soporte para múltiples organizaciones con aislamiento de datos   |
| Tenant (realm)    | Organización cliente (`tenant`) o ámbito de autenticación (`realm` en Keycloak) |
| Worker            | Proceso que ejecuta envíos por canal específico                 |
| Webhook           | Callback HTTP para notificaciones en tiempo real                |
| Outbox            | Patrón para garantizar entrega única de mensajes                |
| DLQ               | `Dead Letter Queue`, cola para mensajes no procesados           |
| Idempotency       | Propiedad que asegura que una operación puede repetirse sin efectos secundarios |
| SLO/SLI           | `Service Level Objective`/`Indicator`, objetivo e indicador de nivel de servicio |
| Observabilidad    | Capacidad de monitorear, trazar y alertar sobre el sistema      |
| Instrumentación   | Integración de métricas, logs y trazas en el sistema            |
| Failover          | Cambio automático a sistema de respaldo ante fallos             |
| Rate Limiting     | Control de la cantidad de solicitudes permitidas por unidad de tiempo |
| Runbook           | Guía operativa para resolución de incidentes o tareas repetitivas|

## 12.2 Acrónimos y Abreviaturas

| Acrónimo | Significado                        | Contexto                                      |
|----------|------------------------------------|-----------------------------------------------|
| CQRS     | Command Query Responsibility Segregation | Patrón de separación de comandos y consultas |
| SMTP     | Simple Mail Transfer Protocol      | Protocolo estándar de `email`                 |
| SMS      | Short Message Service              | Mensajería de texto móvil                     |
| API      | Application Programming Interface  | Interfaz de programación                      |
| EFS      | Elastic File System                | Almacenamiento en AWS                         |
| JWT      | JSON Web Token                     | Token seguro para autenticación               |
| RBAC     | Role-Based Access Control          | Control de acceso basado en roles             |
| SLA      | Service Level Agreement            | Acuerdo de nivel de servicio                  |
| SLO      | Service Level Objective            | Objetivo de nivel de servicio                 |
| SLI      | Service Level Indicator            | Indicador de nivel de servicio                |
| TLS      | Transport Layer Security           | Seguridad en transporte                       |
| YARP     | Yet Another Reverse Proxy          | Proxy reverso para `.NET`                     |
| Redis    | Remote Dictionary Server           | Almacenamiento en memoria para colas y cache  |
| DDD      | Domain-Driven Design               | Modelado de dominio                           |
| DDL      | Data Definition Language           | Definición de estructuras de datos            |
| ORM      | Object-Relational Mapping          | Mapeo objeto-relacional (`Entity Framework`)  |
| SRE      | Site Reliability Engineering       | Prácticas de confiabilidad operativa          |
| PII      | Personally Identifiable Information| Información personal identificable            |
| DLQ      | Dead Letter Queue                  | Cola de mensajes no procesados                |
| OTel     | OpenTelemetry                      | Framework de trazas y métricas                |
| Loki     | Sistema de logs centralizados      | Observabilidad y análisis de logs             |
| Jaeger   | Visualizador de trazas distribuidas| Observabilidad y performance                  |
| Prometheus| Sistema de métricas y monitoreo   | Observabilidad y alertas                      |
| ADR      | Architectural Decision Record      | Registro de decisiones arquitectónicas        |
| CI/CD    | Continuous Integration/Continuous Delivery | Integración y entrega continua        |
| WAL      | Write-Ahead Logging                | Estrategia de backup y recuperación           |
| DLQ      | Dead Letter Queue                  | Cola de mensajes no procesados                |

## 12.3 Conceptos Clave y Patrones

- `API First Design`: Estrategia donde el diseño de la API precede a la implementación.
- `API Gateway`: Punto de entrada unificado que maneja autenticación, autorización y enrutamiento hacia microservicios (`YARP`).
- `At-Least-Once Delivery`: Garantía de entrega donde cada mensaje puede ser entregado una o más veces; requiere idempotencia.
- `Audit Trail`: Registro inmutable de actividades del sistema, implementado mediante event sourcing.
- `Auto-scaling`: Ajuste automático de recursos computacionales según demanda.
- `Backoff Exponencial`: Estrategia de reintentos con incrementos exponenciales en el tiempo de espera.
- `Batch Processing`: Agrupación de elementos para procesamiento eficiente.
- `Blue-Green Deployment`: Estrategia de despliegue con dos ambientes idénticos para cambios y rollbacks seguros.
- `Circuit Breaker`: Patrón de resiliencia que previene llamadas a servicios fallidos.
- `Clean Architecture`: Organización del código en capas concéntricas con dependencias hacia el núcleo.
- `CQRS`: Separación de comandos y queries en la capa de aplicación.
- `DDD`: Modelado de dominio complejo y reglas de negocio.
- `Event-Driven Architecture`: Componentes que comunican mediante eventos asíncronos.
- `Event Sourcing`: Persistencia de cambios como secuencia inmutable de eventos.
- `Failover`: Cambio automático a sistema de respaldo ante fallos.
- `Feature Flag`: Activación/desactivación de funcionalidades en tiempo real.
- `Graceful Degradation`: Mantenimiento de funcionalidad esencial ante fallos parciales.
- `Idempotency`: Garantía de que una operación puede repetirse sin efectos secundarios.
- `Outbox Pattern`: Garantiza entrega única y confiable de mensajes a través de la base de datos.
- `Observabilidad`: Capacidad de monitorear, trazar y alertar sobre el sistema en tiempo real.
- `OpenTelemetry`: Framework para instrumentación de métricas y trazas distribuidas.
- `Prometheus`: Sistema de monitoreo y recolección de métricas.
- `Loki`: Plataforma de logs centralizados y búsqueda eficiente.
- `Jaeger`: Visualización y análisis de trazas distribuidas.
- `Rate Limiting`: Control de la cantidad de solicitudes permitidas por unidad de tiempo.
- `Runbook`: Guía operativa para resolución de incidentes o tareas repetitivas.
- `SLO/SLI`: Objetivos e indicadores de nivel de servicio para monitoreo y alertas.
- `Tenant (realm)`: Organización cliente o ámbito de autenticación, con aislamiento de datos y configuración.

---

Este glosario se actualiza de forma continua para reflejar la evolución tecnológica y terminológica del sistema.