# 12. Glosario

Este glosario define los términos técnicos, conceptos clave y acrónimos utilizados en la documentación del **Sistema de Notificaciones**, proporcionando claridad y consistencia para equipos técnicos y stakeholders.

## 12.1 Términos principales

| Término | Definición |
|----------|------------|
| **Notification** | Mensaje enviado a usuarios finales |
| **Template** | Plantilla para generar contenido dinámico |
| **Handler** | Procesador de canal específico (email, SMS, push, etc.) |
| **Queue** | Cola de mensajes pendientes de procesamiento |
| **Attachment** | Archivo adjunto a una notificación |
| **Channel** | Medio de envío (email, SMS, push, WhatsApp, etc.) |
| **Scheduler** | Programador de envíos futuros |
| **Provider** | Servicio externo de entrega (SendGrid, Twilio, etc.) |
| **Template Engine** | Motor para procesar plantillas y datos |
| **Multi-tenant** | Soporte para múltiples organizaciones con aislamiento de datos |
| **Tenant** | Organización cliente con datos y configuración aislados |
| **Worker** | Proceso que ejecuta envíos por canal específico |
| **Processor** | Servicio que consume y procesa mensajes desde colas |
| **Webhook** | Callback HTTP para notificaciones en tiempo real |

## 12.2 Acrónimos y abreviaturas

| Acrónimo | Significado | Contexto |
|-----------|-------------|----------|
| **CQRS** | Command Query Responsibility Segregation | Patrón de separación de comandos y consultas |
| **SMTP** | Simple Mail Transfer Protocol | Protocolo estándar de email |
| **SMS** | Short Message Service | Mensajería de texto móvil |
| **API** | Application Programming Interface | Interfaz de programación |
| **EFS** | Elastic File System | Almacenamiento en AWS |
| **JWT** | JSON Web Token | Token seguro para autenticación |
| **RBAC** | Role-Based Access Control | Control de acceso basado en roles |
| **SLA** | Service Level Agreement | Acuerdo de nivel de servicio |
| **SNS** | Simple Notification Service | Servicio de notificaciones AWS |
| **SQS** | Simple Queue Service | Servicio de colas AWS |
| **TLS** | Transport Layer Security | Seguridad en transporte |
| **YARP** | Yet Another Reverse Proxy | Proxy reverso para .NET |

## 12.3 Conceptos clave y patrones

- **Diseño API Primero (API First Design):** Estrategia donde el diseño de la API precede a la implementación, garantizando contratos claros y mejor experiencia para desarrolladores.
- **API Gateway:** Punto de entrada unificado que maneja autenticación, autorización y enrutamiento hacia microservicios. Implementado con YARP.
- **Entrega Al-Menos-Una-Vez (At-Least-Once Delivery):** Garantía de entrega donde cada mensaje puede ser entregado una o más veces; requiere idempotencia.
- **Rastro de Auditoría (Audit Trail):** Registro inmutable de actividades del sistema, implementado mediante event sourcing.
- **Auto-escalado (Auto-scaling):** Ajuste automático de recursos computacionales según demanda.
- **Backoff Exponencial:** Estrategia de reintentos con incrementos exponenciales en el tiempo de espera.
- **Procesamiento por Lotes (Batch Processing):** Agrupación de elementos para procesamiento eficiente, usado en campañas masivas.
- **Despliegue Azul-Verde (Blue-Green Deployment):** Estrategia de despliegue con dos ambientes idénticos para cambios y rollbacks seguros.
- **Cortocircuito (Circuit Breaker):** Patrón de resiliencia que previene llamadas a servicios fallidos.
- **Clean Architecture:** Organización del código en capas concéntricas con dependencias hacia el núcleo.
- **Event-Driven Architecture:** Componentes que comunican mediante eventos asíncronos.
- **Event Sourcing:** Persistencia de cambios como secuencia inmutable de eventos.
- **Failover:** Cambio automático a sistema de respaldo ante fallos.
- **Feature Flag:** Activación/desactivación de funcionalidades en tiempo real.
- **Graceful Degradation:** Mantenimiento de funcionalidad esencial ante fallos parciales.
- **Idempotencia:** Propiedad donde múltiples ejecuciones producen el mismo resultado.
- **Integration Testing:** Pruebas de interacción entre componentes y servicios.
- **Mapster:** Librería .NET para mapeo eficiente de objetos.
- **Multi-Provider Strategy:** Uso de múltiples proveedores para redundancia y optimización de costos.
- **Multi-Tenancy:** Arquitectura para servir a múltiples clientes con aislamiento seguro.
- **OpenTelemetry:** Framework de observabilidad para métricas, logs y trazas.
- **Opt-in/Opt-out:** Mecanismos para aceptar o rechazar comunicaciones.
- **Partitioning:** División de datos/procesos para escalabilidad.
- **Retry Policy:** Estrategia de reintentos ante fallos.
- **Registro Estructurado:** Logs en formato estructurado para análisis eficiente.
- **Template Engine:** Componente que combina plantillas y datos para generar contenido.
- **Throttling:** Control de la tasa de procesamiento para evitar sobrecarga.

## 12.4 Términos de negocio

- **Bounce Rate:** Porcentaje de emails no entregados por problemas permanentes.
- **Campaign Analytics:** Métricas y reportes de campañas de notificación.
- **Compliance Officer:** Responsable de cumplimiento normativo y regulatorio.
- **Delivery Rate:** Porcentaje de notificaciones entregadas exitosamente.
- **Marketing Automation:** Automatización de procesos y campañas de marketing.
- **Template Library:** Colección de plantillas reutilizables y personalizables.
- **Transactional Email:** Emails automáticos disparados por acciones o eventos.
- **Trazabilidad:** Capacidad de seguir el ciclo completo de una notificación.

## 12.5 Referencias técnicas y estándares

### Notification Standards

- **RFC 5321:** Simple Mail Transfer Protocol
- **RFC 6376:** DomainKeys Identified Mail (DKIM) Signatures
- **RFC 7208:** Sender Policy Framework (SPF) for Authorizing Use of Domains in Email

### Security Standards

- **RFC 6749:** OAuth 2.0 Authorization Framework
- **RFC 7519:** JSON Web Token (JWT)
- **RFC 8551:** Secure/Multipurpose Internet Mail Extensions (S/MIME) Version 4.0

### Message Queue Standards

- **AMQP:** Advanced Message Queuing Protocol
- **CloudEvents:** Especificación para describir eventos en formatos comunes

---

> **Nota:** Para mayor claridad, se recomienda mantener este glosario actualizado y alineado con la evolución del sistema y la terminología corporativa. Incluir diagramas de contexto (C4) y ejemplos de uso cuando sea relevante.
