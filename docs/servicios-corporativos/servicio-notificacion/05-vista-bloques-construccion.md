# 5. Vista De Bloques De Construcción

Esta sección describe la estructura modular y desacoplada del Sistema de Notificación, detallando contenedores, componentes, esquemas de datos, APIs y ejemplos de implementación. Se incluyen diagramas C4 para ilustrar la arquitectura y la interacción entre los bloques principales, priorizando la escalabilidad, resiliencia y observabilidad.

![Vista General del Sistema de Notificación](/diagrams/servicios-corporativos/notification_system.png)
*Figura 5.1: Contenedores principales del sistema*

## 5.1 Contenedores Principales

| Contenedor                | Responsabilidad                                        | Tecnología              |
|---------------------------|--------------------------------------------------------|-------------------------|
| `Notification API`        | Recepción, validación, orquestación, deduplicación e idempotencia de solicitudes, gestión de plantillas | `.NET 8 Web API`        |
| `Notification Database`   | Persistencia, auditoría, versionado de datos y plantillas | `PostgreSQL 15+`        |
| `emailQueue`              | Desacoplamiento y buffering de mensajes `email`         | `AWS SQS`               |
| `smsQueue`                | Desacoplamiento y buffering de mensajes `SMS`           | `AWS SQS`               |
| `whatsappQueue`           | Desacoplamiento y buffering de mensajes `WhatsApp`      | `AWS SQS`               |
| `pushQueue`               | Desacoplamiento y buffering de mensajes `push`          | `AWS SQS`               |
| `SNS` (opcional)          | Fan-out y routing avanzado a colas SQS                 | `AWS SNS`               |
| `Email Processor`         | Procesamiento y entrega de `email`                      | `.NET 8 Worker Service` |
| `SMS Processor`           | Procesamiento y entrega de `SMS`                        | `.NET 8 Worker Service` |
| `WhatsApp Processor`      | Procesamiento y entrega de `WhatsApp`                   | `.NET 8 Worker Service` |
| `Push Processor`          | Procesamiento y entrega de notificaciones `push`        | `.NET 8 Worker Service` |
| `Attachment Storage`      | Almacenamiento seguro y escalable de adjuntos           | `AWS S3`                |

> La deduplicación, idempotencia y versionado de plantillas son responsabilidades internas de los componentes principales (`Notification API`, `Template Controller`, `Notification Database`) y se implementan mediante lógica de aplicación, claves de idempotencia y versionado en base de datos, no como contenedores independientes.

## 5.2 Vista de Componentes y Detalles

![Componentes Notification API](/diagrams/servicios-corporativos/notification_system_api.png)
*Figura 5.2: Componentes internos de Notification API*

| Componente                | Responsabilidad                                        | Tecnología              |
|---------------------------|--------------------------------------------------------|-------------------------|
| `Notification Controller` | Exposición de endpoints `REST`, control de acceso, deduplicación e idempotencia | `ASP.NET Core`          |
| `Template Controller`     | Gestión de plantillas con versionado e `i18n`          | `ASP.NET Core`          |
| `Attachment Service`      | Manejo seguro y validación de adjuntos                 | `.NET 8`, `S3 SDK`      |
| `Validation Service`      | Validación de datos, límites y reglas por tenant       | `FluentValidation`      |
| `Message Publisher`       | Publicación confiable a colas (`outbox pattern`)       | `.NET 8`, `PostgreSQL`, `SQS`|
| `Config Manager`          | Gestión de configuración multi-tenant                  | `.NET 8`, `EF Core`     |
| `Structured Logger`       | Logging estructurado y trazabilidad                    | `Serilog`               |
| `Metrics Collector`       | Recolección de métricas y monitoreo                    | `Prometheus.NET`        |

> La deduplicación, idempotencia y versionado de plantillas están integrados como lógica interna en los componentes críticos (`Notification API`, `Template Controller`, `Notification Database`), siguiendo el modelo real del sistema. No existen como servicios o contenedores independientes en el DSL.

### Email Processor

![Componentes Email Processor](/diagrams/servicios-corporativos/notification_system_email_processor.png)
*Figura 5.3: Componentes internos de Email Processor*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| `Consumer`           | Consume mensajes de la cola de notificación `email`  | `C# .NET 8`, `AWS SDK`      |
| `Service`            | Procesa y envía notificaciones por `email`           | `C# .NET 8`                 |
| `Adapter`            | Envía notificaciones al proveedor externo de `email` | `C# .NET 8`, `AWS SDK`      |
| `Repository`         | Actualiza el estado de las notificaciones enviadas   | `C# .NET 8`, `Entity Framework Core` |
| `Attachment Fetcher` | Obtiene archivos adjuntos desde almacenamiento       | `C# .NET 8`, `AWS SDK`      |
| `Configuration Manager`| Gestiona configuraciones del servicio y por tenant | `C# .NET 8`, `EF Core`      |

### SMS Processor

![Componentes SMS Processor](/diagrams/servicios-corporativos/notification_system_sms_processor.png)
*Figura 5.4: Componentes internos de SMS Processor*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| `Consumer`           | Consume mensajes de la cola notificación `SMS`         | `C# .NET 8`, `AWS SDK`      |
| `Service`            | Procesa y envía notificaciones `SMS`                   | `C# .NET 8`                 |
| `Adapter`            | Envía notificaciones al proveedor externo de `SMS`     | `C# .NET 8`, `AWS SDK`      |
| `Repository`         | Actualiza el estado de las notificaciones enviadas   | `C# .NET 8`, `Entity Framework Core` |
| `Configuration Manager`| Gestiona configuraciones del servicio y por tenant | `C# .NET 8`, `EF Core`      |

### WhatsApp Processor

![Componentes WhatsApp Processor](/diagrams/servicios-corporativos/notification_system_whatsapp_processor.png)
*Figura 5.5: Componentes internos de WhatsApp Processor*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| `Consumer`           | Consume mensajes de la cola notificación `WhatsApp`    | `C# .NET 8`, `AWS SDK`      |
| `Service`            | Procesa y envía notificaciones `WhatsApp`              | `C# .NET 8`                 |
| `Adapter`            | Envía notificaciones al proveedor externo de `WhatsApp`| `C# .NET 8`, `AWS SDK`      |
| `Repository`         | Actualiza el estado de las notificaciones enviadas   | `C# .NET 8`, `Entity Framework Core` |
| `Attachment Fetcher` | Obtiene archivos adjuntos desde almacenamiento       | `C# .NET 8`, `AWS SDK`      |
| `Configuration Manager`| Gestiona configuraciones del servicio y por tenant | `C# .NET 8`, `EF Core`      |

### Push Processor

![Componentes Push Processor](/diagrams/servicios-corporativos/notification_system_push_processor.png)
*Figura 5.6: Componentes internos de Push Processor*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| `Consumer`           | Consume mensajes de la cola notificación `Push`         | `C# .NET 8`, `AWS SDK`      |
| `Service`            | Procesa y envía notificaciones `Push`                  | `C# .NET 8`                 |
| `Adapter`            | Envía notificaciones al proveedor externo de `Push`    | `C# .NET 8`, `AWS SDK`      |
| `Repository`         | Actualiza el estado de las notificaciones enviadas   | `C# .NET 8`, `Entity Framework Core` |
| `Attachment Fetcher` | Obtiene archivos adjuntos desde almacenamiento       | `C# .NET 8`, `AWS SDK`      |
| `Configuration Manager`| Gestiona configuraciones del servicio y por tenant | `C# .NET 8`, `EF Core`      |

### Scheduler

![Componentes Scheduler](/diagrams/servicios-corporativos/notification_system_scheduler.png)
*Figura 5.7: Componentes internos de Scheduler*

| Componente           | Responsabilidad                                      | Tecnología                  |
|----------------------|------------------------------------------------------|-----------------------------|
| `Scheduler Worker`   | Ejecuta tareas programadas para enviar notificaciones| `Worker Service`, `C# .NET 8`  |
| `Service`            | Procesa y programa el envío de notificaciones        | `C# .NET 8`                 |
| `Queue Publisher`    | Envía notificaciones programadas a la cola           | `C# .NET 8`, `AWS SDK`      |
| `Repository`         | Acceso a notificaciones programadas en la base de datos| `C# .NET 8`, `Entity Framework Core` |
| `Configuration Manager`| Gestiona configuraciones del servicio y por tenant | `C# .NET 8`, `EF Core`      |

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

| Campo                | Tipo                | Descripción                                                                                 | Ejemplo                                      |
|----------------------|---------------------|---------------------------------------------------------------------------------------------|----------------------------------------------|
| requestId            | string              | Identificador único de la solicitud                                                         | "abc123"                                    |
| timestamp            | string (ISO 8601)   | Fecha y hora de la solicitud                                                               | "2024-09-17T14:00:00Z"                      |
| notificationType     | string              | Tipo de notificación: "transactional", "marketing", "alert"                                       | "transactional"                             |
| channels             | array de string     | Canales solicitados                                                                        | ["email", "sms", "push"]                  |
| recipient            | objeto              | Información del destinatario (ver subcampos)                                               | {...}                                        |
| recipient.userId     | string              | Identificador del usuario                                                                  | "usuario789"                                |
| recipient.email      | string (opcional)   | Correo electrónico del destinatario                                                        | "<usuario@ejemplo.com>"                       |
| recipient.phone      | string (opcional)   | Teléfono del destinatario                                                                  | ""                                           |
| recipient.pushToken  | string (opcional)   | Token push                                                                                 | ""                                           |
| recipient.customFields | objeto (opcional)  | Campos personalizados del destinatario                                                  | {"pais": "PE"}                             |
| message              | objeto              | Contenido del mensaje (ver subcampos)                                                      | {...}                                        |
| message.subject      | string (opcional)   | Asunto (para email)                                                                        | "Confirmación de Pedido"                     |
| message.body         | string              | Cuerpo del mensaje                                                                         | "¡Gracias por su pedido! Su pedido #123456 ha sido confirmado." |
| message.attachments  | array de string (op)| URLs de adjuntos                                                                          | ["https://example.com/invoice123456.pdf"]    |
| message.smsText      | string (opcional)   | Texto SMS                                                                                  | "¡Gracias por su pedido! Pedido #123456 confirmado." |
| message.pushNotification | objeto (op)     | Datos para notificación push (ver subcampos)                                               | {...}                                        |
| message.pushNotification.title | string    | Título de la notificación push                                                             | "Pedido Confirmado"                          |
| message.pushNotification.body  | string    | Cuerpo de la notificación push                                                             | "Su pedido #123456 ha sido confirmado. Revise su correo para más detalles." |
| message.pushNotification.icon  | string (op)| URL de icono                                                                              | "<https://example.com/icon.png>"              |
| message.pushNotification.action| objeto (op)| Acción asociada                                                                           | {...}                                        |
| message.pushNotification.action.type | string| Tipo de acción                                                                            | "verPedido"                                 |
| message.pushNotification.action.url  | string| URL destino                                                                              | "<https://example.com/pedido/123456>"         |
| schedule              | objeto (opcional)  | Programación de envío (ver subcampos)                                                      | {...}                                        |
| schedule.sendAt       | string (ISO 8601)  | Fecha/hora de envío programado                                                             | "2024-09-17T15:00:00Z"                      |
| schedule.timeZone     | string (opcional)  | Zona horaria                                                                              | "America/Lima"                              |
| metadata              | objeto (opcional)   | Metadatos adicionales (prioridad, reintentos, etc.)                                     | {"priority": "high", "retries": 3, "sentBy": "OrderService", "templateId": "orderConfirmationTemplate"}        |
| metadata.priority     | string              | Prioridad de la notificación                                                            | "high"                                      |
| metadata.retries      | integer             | Número de reintentos permitidos                                                         | 3                                            |
| metadata.sentBy       | string              | Servicio o sistema que origina la notificación                                          | "OrderService"                              |
| metadata.templateId   | string              | Identificador de la plantilla utilizada                                                 | "orderConfirmationTemplate"                 |

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
