# 5. Vista De Bloques De Construcción

Esta sección describe la estructura modular del Sistema de Notificación, detallando contenedores, componentes, esquemas de datos, APIs y ejemplos de implementación. Se incluyen diagramas C4 para ilustrar la arquitectura y la interacción entre los bloques principales.

![Vista General del Sistema de Notificación](/diagrams/servicios-corporativos/notification_system.png)
*Figura 5.1: Contenedores principales del sistema*

## 5.1 Contenedores Principales

| Contenedor                | Responsabilidad                        | Tecnología              |
|---------------------------|----------------------------------------|-------------------------|
| Notification API          | Recepción y validación de solicitudes  | `.NET 8 Web API`        |
| Notification Processor    | Procesamiento y envío de notificaciones| `.NET 8 Worker Service` |
| Notification Database     | Persistencia de datos y auditoría      | `PostgreSQL 15+`        |
| emailQueue                | Cola de mensajes email                 | `AWS SQS`               |
| smsQueue                  | Cola de mensajes SMS                   | `AWS SQS`               |
| whatsappQueue             | Cola de mensajes WhatsApp              | `AWS SQS`               |
| pushQueue                 | Cola de mensajes push                  | `AWS SQS`               |
| SNS (opcional)            | Notificación fan-out a colas SQS       | `AWS SNS`               |
| Email Processor           | Procesamiento y envío de emails        | `.NET 8 Worker Service` |
| SMS Processor             | Procesamiento y envío de SMS           | `.NET 8 Worker Service` |
| WhatsApp Processor        | Procesamiento y envío de WhatsApp      | `.NET 8 Worker Service` |
| Push Processor            | Procesamiento y envío de notificaciones push | `.NET 8 Worker Service` |
| Attachment Storage        | Almacenamiento de adjuntos             | S3, File System         |

## 5.2 Vista de Componentes y Detalles

![Componentes Notification API](/diagrams/servicios-corporativos/notification_system_api.png)
*Figura 5.2: Componentes internos de Notification API*

| Componente                | Responsabilidad                        | Tecnología              |
|---------------------------|----------------------------------------|-------------------------|
| Notification Controller   | Exposición de endpoints REST           | `ASP.NET Core`          |
| Template Controller       | Gestión de plantillas                  | `ASP.NET Core`          |
| Attachment Service        | Manejo de adjuntos                     | `.NET 8`                |
| Validation Service        | Validación de datos y reglas           | `FluentValidation`      |

![Componentes Notification Processor](/diagrams/servicios-corporativos/notification_system_processor.png)
*Figura 5.3: Componentes internos de Notification Processor*

| Componente            | Responsabilidad                                                        | Tecnología                  |
|-----------------------|------------------------------------------------------------------------|-----------------------------|
| Consumer              | Consume mensajes desde la cola de solicitudes de notificación           | C# .NET 8, AWS SDK          |
| Orchestrator Service  | Valida datos, construye el mensaje y lo distribuye al canal correspondiente | C# .NET 8              |
| Message Builder       | Genera el mensaje final para cada canal utilizando plantillas y datos   | C# .NET 8                  |
| Template Engine       | Renderiza plantillas con soporte i18n y variables dinámicas             | C#, Liquid Templates        |
| Adapter              | Envía el mensaje procesado a la cola específica del canal               | C# .NET 8, AWS SDK          |
| Repository            | Guarda el estado y eventos de las notificaciones procesadas en la base de datos | C# .NET 8, Entity Framework Core |
| Configuration Manager | Gestiona configuraciones del servicio y por tenant                     | C#, .NET 8, EF Core         |

### Email Processor

![Componentes Email Processor](/diagrams/servicios-corporativos/notification_system_email_processor.png)
*Figura 5.4: Componentes internos de Email Processor*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| Consumer             | Consume mensajes de la cola de notificación Email    | C# .NET 8, AWS SDK         |
| Service              | Procesa y envía notificaciones por email             | C# .NET 8                  |
| Adapter              | Envía notificaciones al proveedor externo de email   | C# .NET 8, AWS SDK         |
| Repository           | Actualiza el estado de las notificaciones enviadas   | C# .NET 8, Entity Framework Core |
| Attachment Fetcher   | Obtiene archivos adjuntos desde almacenamiento       | C# .NET 8, AWS SDK         |
| Configuration Manager| Gestiona configuraciones del servicio y por tenant   | C#, .NET 8, EF Core        |

### SMS Processor

![Componentes SMS Processor](/diagrams/servicios-corporativos/notification_system_sms_processor.png)
*Figura 5.5: Componentes internos de SMS Processor*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| Consumer             | Consume mensajes de la cola notificación SMS         | C# .NET 8, AWS SDK         |
| Service              | Procesa y envía notificaciones SMS                   | C# .NET 8                  |
| Adapter              | Envía notificaciones al proveedor externo de SMS     | C# .NET 8, AWS SDK         |
| Repository           | Actualiza el estado de las notificaciones enviadas   | C# .NET 8, Entity Framework Core |
| Configuration Manager| Gestiona configuraciones del servicio y por tenant   | C#, .NET 8, EF Core        |

### WhatsApp Processor

![Componentes WhatsApp Processor](/diagrams/servicios-corporativos/notification_system_whatsapp_processor.png)
*Figura 5.6: Componentes internos de WhatsApp Processor*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| Consumer             | Consume mensajes de la cola notificación WhatsApp    | C# .NET 8, AWS SDK         |
| Service              | Procesa y envía notificaciones WhatsApp              | C# .NET 8                  |
| Adapter              | Envía notificaciones al proveedor externo de WhatsApp| C# .NET 8, AWS SDK         |
| Repository           | Actualiza el estado de las notificaciones enviadas   | C# .NET 8, Entity Framework Core |
| Attachment Fetcher   | Obtiene archivos adjuntos desde almacenamiento       | C# .NET 8, AWS SDK         |
| Configuration Manager| Gestiona configuraciones del servicio y por tenant   | C#, .NET 8, EF Core        |

### Push Processor

![Componentes Push Processor](/diagrams/servicios-corporativos/notification_system_push_processor.png)
*Figura 5.7: Componentes internos de Push Processor*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| Consumer             | Consume mensajes de la cola notificación Push         | C# .NET 8, AWS SDK         |
| Service              | Procesa y envía notificaciones Push                  | C# .NET 8                  |
| Adapter              | Envía notificaciones al proveedor externo de Push    | C# .NET 8, AWS SDK         |
| Repository           | Actualiza el estado de las notificaciones enviadas   | C# .NET 8, Entity Framework Core |
| Attachment Fetcher   | Obtiene archivos adjuntos desde almacenamiento       | C# .NET 8, AWS SDK         |
| Configuration Manager| Gestiona configuraciones del servicio y por tenant   | C#, .NET 8, EF Core        |

### Scheduler

![Componentes Scheduler](/diagrams/servicios-corporativos/notification_system_scheduler.png)
*Figura 5.8: Componentes internos de Scheduler*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| Scheduler Worker     | Ejecuta tareas programadas para enviar notificaciones| Worker Service, C# .NET 8  |
| Service              | Procesa y programa el envío de notificaciones        | C# .NET 8                  |
| Queue Publisher      | Envía notificaciones programadas a la cola           | C# .NET 8, AWS SDK         |
| Repository           | Acceso a notificaciones programadas en la base de datos| C# .NET 8, Entity Framework Core |
| Configuration Manager| Gestiona configuraciones del servicio y por tenant   | C#, .NET 8, EF Core        |

## 5.4 Esquemas De Base De Datos

### 5.4.1 Tabla: `notifications`

| Campo              | Tipo           | Descripción                        | Restricciones                  |
|--------------------|---------------|------------------------------------|-------------------------------|
| id                 | UUID          | Identificador único                | PRIMARY KEY                   |
| request_id         | VARCHAR(100)  | ID de la solicitud                 | NOT NULL, INDEX               |
| message_id         | VARCHAR(100)  | ID del mensaje                     | UNIQUE                        |
| tenant_id          | VARCHAR(50)   | Identificador del tenant           | NOT NULL, INDEX               |
| user_id            | VARCHAR(100)  | ID del usuario destinatario        | NOT NULL                      |
| notification_type  | VARCHAR(50)   | transactional, marketing           | NOT NULL                      |
| channels           | JSONB         | Canales solicitados                | NOT NULL                      |
| recipient          | JSONB         | Datos del destinatario             | NOT NULL                      |
| message_content    | JSONB         | Contenido del mensaje              | NOT NULL                      |
| schedule           | JSONB         | Configuración de programación      | NULL                          |
| metadata           | JSONB         | Metadatos adicionales              | NULL                          |
| status             | VARCHAR(20)   | pending, processing, sent, failed  | NOT NULL, DEFAULT 'pending'   |
| created_at         | TIMESTAMP     | Fecha de creación                  | NOT NULL, DEFAULT NOW()       |
| updated_at         | TIMESTAMP     | Fecha de actualización             | NOT NULL, DEFAULT NOW()       |
| sent_at            | TIMESTAMP     | Fecha de envío                     | NULL                          |

### 5.4.2 Tabla: `notification_deliveries`

| Campo                  | Tipo         | Descripción                        | Restricciones                  |
|------------------------|-------------|------------------------------------|-------------------------------|
| id                     | UUID        | Identificador único                | PRIMARY KEY                   |
| notification_id        | UUID        | Referencia a notification          | FOREIGN KEY, NOT NULL         |
| channel                | VARCHAR(20) | Canal: email, sms, push, whatsapp, in-app | NOT NULL              |
| status                 | VARCHAR(20) | pending, sent, delivered, failed   | NOT NULL                      |
| provider               | VARCHAR(50) | Proveedor utilizado                | NOT NULL                      |
| provider_message_id    | VARCHAR(200)| ID del proveedor                   | NULL                          |
| error_message          | TEXT        | Mensaje de error                   | NULL                          |
| retry_count            | INTEGER     | Número de reintentos               | DEFAULT 0                     |
| sent_at                | TIMESTAMP   | Fecha de envío                     | NULL                          |
| delivered_at           | TIMESTAMP   | Fecha de entrega confirmada        | NULL                          |
| created_at             | TIMESTAMP   | Fecha de creación                  | NOT NULL, DEFAULT NOW()       |

### 5.4.3 Tabla: `notification_templates`

| Campo              | Tipo         | Descripción                        | Restricciones                  |
|--------------------|-------------|------------------------------------|-------------------------------|
| id                 | UUID        | Identificador único                | PRIMARY KEY                   |
| template_id        | VARCHAR(100)| ID del template                    | UNIQUE, NOT NULL              |
| tenant_id          | VARCHAR(50) | Identificador del tenant           | NOT NULL, INDEX               |
| name               | VARCHAR(200)| Nombre descriptivo                 | NOT NULL                      |
| channel            | VARCHAR(20) | Canal: email, sms, push, whatsapp, in-app | NOT NULL              |
| subject_template   | TEXT        | Template del asunto                | NULL                          |
| body_template      | TEXT        | Template del cuerpo                | NOT NULL                      |
| variables          | JSONB       | Variables disponibles              | NULL                          |
| is_active          | BOOLEAN     | Estado del template                | DEFAULT true                  |
| created_at         | TIMESTAMP   | Fecha de creación                  | NOT NULL, DEFAULT NOW()       |
| updated_at         | TIMESTAMP   | Fecha de actualización             | NOT NULL, DEFAULT NOW()       |

## 5.5 Endpoints De API

Se describen los principales endpoints REST para la gestión y consulta de notificaciones y plantillas. Los contratos de datos siguen el estándar DTO y están alineados con la arquitectura Clean Architecture.

### 5.5.1 Notification API

- POST `/api/v1/notifications`: Enviar nueva notificación
- GET `/api/v1/notifications/{notificationId}`: Consultar estado de notificación

## 5.6 Contratos De Datos (DTOs)

Los siguientes contratos definen la estructura de los datos de entrada y salida de la API:

### 5.6.1 NotificationRequest (Contrato)

| Campo                | Tipo                | Descripción                                                                                 |
|----------------------|---------------------|---------------------------------------------------------------------------------------------|
| requestId            | string              | Identificador único de la solicitud                                                         |
| timestamp            | string (ISO 8601)   | Fecha y hora de la solicitud                                                               |
| notificationType     | string              | Tipo de notificación: "transactional", "marketing", "alert"                              |
| channels             | array de string     | Canales solicitados                                                                        |
| recipient            | objeto              | Información del destinatario (ver subcampos)                                               |
| recipient.userId     | string              | Identificador del usuario                                                                  |
| recipient.email      | string (opcional)   | Correo electrónico del destinatario                                                        |
| recipient.phone      | string (opcional)   | Teléfono del destinatario                                                                  |
| recipient.pushToken  | string (opcional)   | Token push                                                                                 |
| recipient.customFields | objeto (opcional)  | Campos personalizados del destinatario                                                     |
| message              | objeto              | Contenido del mensaje (ver subcampos)                                                      |
| message.subject      | string (opcional)   | Asunto (para email)                                                                        |
| message.body         | string              | Cuerpo del mensaje                                                                         |
| message.attachments  | array de string (op)| URLs de adjuntos                                                                          |
| message.smsText      | string (opcional)   | Texto SMS                                                                                  |
| message.pushNotification | objeto (op)     | Datos para notificación push (ver subcampos)                                               |
| message.pushNotification.title | string    | Título de la notificación push                                                             |
| message.pushNotification.body  | string    | Cuerpo de la notificación push                                                             |
| message.pushNotification.icon  | string (op)| URL de icono                                                                              |
| message.pushNotification.action| objeto (op)| Acción asociada                                                                           |
| message.pushNotification.action.type | string| Tipo de acción                                                                            |
| message.pushNotification.action.url  | string| URL destino                                                                              |
| schedule              | objeto (opcional)  | Programación de envío (ver subcampos)                                                      |
| schedule.sendAt       | string (ISO 8601)  | `Fecha/hora` de envío programado                                                             |
| schedule.timeZone     | string (opcional)  | Zona horaria                                                                              |
| metadata              | objeto (opcional)   | Metadatos adicionales (prioridad, reintentos, etc.)                                        |
| metadata.priority     | string              | Prioridad de la notificación                                                               |
| metadata.retries      | integer             | Número de reintentos permitidos                                                            |
| metadata.sentBy       | string              | Servicio o sistema que origina la notificación                                             |
| metadata.templateId   | string              | Identificador de la plantilla utilizada                                                    |

#### Ejemplo de contrato NotificationRequest

```json
{
  "requestId": "abc123",
  "timestamp": "2024-09-17T14:00:00Z",
  "notificationType": "transactional",
  "channels": ["email", "sms", "push"],
  "recipient": {
    "userId": "usuario789",
    "email": "usuario@ejemplo.com"
  },
  "message": {
    "subject": "Confirmación de Pedido",
    "body": "¡Gracias por su pedido! Su pedido #123456 ha sido confirmado.",
    "attachments": ["https://ejemplo.com/factura123456.pdf"],
    "smsText": "¡Gracias por su pedido! Pedido #123456 confirmado.",
    "pushNotification": {
      "title": "Pedido Confirmado",
      "body": "Su pedido #123456 ha sido confirmado. Revise su correo para más detalles.",
      "icon": "https://ejemplo.com/icono.png",
      "action": {
        "type": "verPedido",
        "url": "https://ejemplo.com/pedido/123456"
      }
    }
  },
  "schedule": {
    "sendAt": "2024-09-17T15:00:00Z"
  },
  "metadata": {
    "priority": "high",
    "retries": 3,
    "sentBy": "OrderService",
    "templateId": "orderConfirmationTemplate"
  }
}
```

#### Ejemplo de notificación email generada

```json
{
  "messageId": "msg12345",
  "timestamp": "2024-09-17T14:00:00Z",
  "notificationType": "transactional",
  "channel": "email",
  "recipient": {
    "userId": "user789",
    "email": "user@example.com"
  },
  "messageContent": {
    "subject": "Confirmación de Pedido - Pedido #123456",
    "body": {
      "html": "<html><body><h1>¡Gracias por su pedido!</h1><p>Su pedido #123456 ha sido confirmado. Puede rastrear su pedido <a href='https://example.com/track'>aquí</a>.</p></body></html>",
      "plainText": "¡Gracias por su pedido! Su pedido #123456 ha sido confirmado. Rastrear su pedido aquí: https://example.com/track"
    },
    "attachments": [
      {
        "url": "https://example.com/invoice123456.pdf",
        "fileName": "invoice123456.pdf",
        "mimeType": "application/pdf"
      }
    ]
  },
  "metadata": {
    "priority": "high",
    "retries": 3,
    "sentBy": "OrderService",
    "templateId": "orderConfirmationTemplate",
    "requestId": "req9876"
  }
}
```
