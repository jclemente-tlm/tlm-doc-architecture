# 3. Contexto Y Alcance Del Sistema

![Servicios Corporativos - Vista de Contexto](/diagrams/servicios-corporativos/corporate_services.png)

*Figura 3.1: Vista de contexto de los Servicios Corporativos*

![Sistema de Notificación - Vista de Contexto](/diagrams/servicios-corporativos/notification_system.png)

*Figura 3.2: Vista de contexto del Sistema de Notificación*

## 3.1 Alcance Funcional Del Sistema

| Aspecto   | Descripción                                                                 |
|-----------|-----------------------------------------------------------------------------|
| Incluido  | Envío multicanal, plantillas, programación, adjuntos, auditoría             |
| Excluido  | Contenido de mensajes, lógica de negocio, gestión de usuarios               |

## 3.2 Actores Y Sistemas Externos

| Actor/Sistema              | Rol         | Interacción                                 |
|---------------------------|-------------|---------------------------------------------|
| Aplicaciones Corporativas  | Cliente     | Solicitudes de envío vía `API REST`         |
| Usuarios Finales           | Destinatario| Recepción de notificaciones                 |
| Proveedores Email          | Servicio    | `SMTP`/`API` para email                    |
| Proveedores SMS            | Servicio    | `API` para SMS                             |
| Proveedores WhatsApp       | Servicio    | `API` para WhatsApp                        |
| Proveedores Push           | Servicio    | `API` para notificaciones push             |
| Sistema de Identidad       | Proveedor   | Autenticación y autorización               |
| Observabilidad             | Consumidor  | Métricas y logs                            |
