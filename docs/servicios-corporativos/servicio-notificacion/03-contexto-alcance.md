# 3. Contexto y alcance del sistema

![Servicios Corporativos - Vista de Contexto](/diagrams/servicios-corporativos/corporate_services.png)

*Figura 3.1: Vista de contexto de los Servicios Corporativos*

![Sistema de Notificación - Vista de Contexto](/diagrams/servicios-corporativos/notification_system.png)

*Figura 3.2: Vista de contexto del Sistema de Notificación*

## 3.1 Alcance funcional del sistema

| Aspecto | Descripción |
|---------|-------------|
| **Incluido** | Envío multi-canal, plantillas, programación, adjuntos, auditoría |
| **Excluido** | Contenido de mensajes, lógica de negocio, gestión de usuarios |

## 3.2 Actores y sistemas externos

| Actor/Sistema | Rol | Interacción |
|---------------|-----|-------------|
| **Aplicaciones Corporativas** | Cliente | Solicitudes de envío vía `API REST` |
| **Usuarios Finales** | Destinatario | Recepción de notificaciones |
| **Proveedores Email** | Servicio | `SMTP`/`API` para email |
| **Proveedores SMS** | Servicio | `API` para SMS |
| **Sistema de Identidad** | Proveedor | Autenticación y autorización |
| **Observabilidad** | Consumidor | Métricas y logs |
