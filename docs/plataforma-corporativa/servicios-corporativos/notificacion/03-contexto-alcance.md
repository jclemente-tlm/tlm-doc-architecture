# 3. Contexto y alcance

![Servicios Corporativos - Vista de Contexto](/diagrams/servicios-corporativos/corporate_services.png)

*Figura 3.1: Vista de contexto de los Servicios Corporativos*

![Sistema de Notificación - Vista de Contexto](/diagrams/servicios-corporativos/notification_system.png)

*Figura 3.2: Vista de contexto del Sistema de Notificación*

## 3.1 Alcance funcional del sistema

| Aspecto   | Descripción                                                                                                                         |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------|
| Incluido  | Envío multicanal (`email`, `SMS`, `WhatsApp`, `push`), gestión de plantillas con versionado e internacionalización, programación de envíos, manejo de adjuntos, auditoría de eventos, integración con sistemas de observabilidad y control de acceso basado en roles (`RBAC`). |
| Excluido  | Composición del contenido de mensajes por canal, lógica de negocio de sistemas origen, gestión de usuarios finales, almacenamiento de información sensible fuera de los adjuntos, procesamiento de pagos o facturación. |

> El alcance se centra en la orquestación, entrega y trazabilidad de notificaciones, desacoplando la lógica de negocio y la gestión de usuarios para mantener cohesión y facilitar la evolución independiente de los sistemas consumidores. La resiliencia y escalabilidad se logran mediante el uso de colas, procesadores y desacoplamiento de proveedores externos.

## 3.2 Actores y sistemas externos

| Actor/Sistema              | Rol         | Interacción                                                                                 |
|---------------------------|-------------|---------------------------------------------------------------------------------------------|
| Aplicaciones Corporativas  | Cliente     | Solicitan envíos de notificaciones vía `API REST` autenticada y autorizada (`OAuth2`/`JWT`).|
| Usuarios Finales           | Destinatario| Reciben notificaciones a través de los canales soportados (`email`, `SMS`, `WhatsApp`, `push`).|
| Proveedores Email          | Servicio    | Integración mediante `SMTP` o `API REST` para el envío de correos electrónicos.              |
| Proveedores SMS            | Servicio    | Integración mediante `API REST` o protocolos estándar (`SMPP`) para envío de `SMS`.          |
| Proveedores WhatsApp       | Servicio    | Integración mediante `API REST` para envío de mensajes `WhatsApp`.                           |
| Proveedores Push           | Servicio    | Integración mediante `API REST` para notificaciones push a dispositivos móviles.             |
| Sistema de Identidad       | Proveedor   | Provee autenticación y autorización centralizada para el acceso a la `Notification API`.     |
| Observabilidad             | Consumidor  | Consume métricas y logs estructurados para monitoreo, alertas y auditoría.                   |

> Todas las integraciones externas están desacopladas mediante `APIs` y colas, permitiendo resiliencia, escalabilidad y trazabilidad. La seguridad se garantiza mediante autenticación robusta y control de acceso granular. La observabilidad es transversal, asegurando monitoreo y auditoría de extremo a extremo.

---

**Notas:**

- Los componentes principales (`Notification API`, `Scheduler`, `Queues`, `Processors`, `Attachment Storage`) orquestan la entrega y trazabilidad de notificaciones, alineados con el modelo arquitectónico definido.
- El desacoplamiento de proveedores y canales permite tolerancia a fallos, escalabilidad y evolución independiente de cada integración.
- La arquitectura soporta multi-tenant y multipaís, cumpliendo normativas locales y requisitos de aislamiento.
