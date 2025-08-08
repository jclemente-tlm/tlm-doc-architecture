# 5. Vista de Bloques de Construcción

Esta sección describe la estructura modular del **Sistema de Notificación**, detallando contenedores, componentes, esquemas de datos, APIs y ejemplos de implementación. Se incluyen diagramas C4 para ilustrar la arquitectura y la interacción entre los bloques principales.

![Vista General del Sistema de Notificación](/diagrams/servicios-corporativos/notification_system.png)
*Figura 5.1: Contenedores principales del sistema*

![Componentes Notification API](/diagrams/servicios-corporativos/notification_system_api.png)
*Figura 5.2: Componentes internos de la Notification API*

![Componentes Notification Processor](/diagrams/servicios-corporativos/notification_system_processor.png)
*Figura 5.3: Componentes internos del Notification Processor*

## 5.1 Contenedores Principales

| Contenedor               | Responsabilidad                        | Tecnología              |
|--------------------------|----------------------------------------|-------------------------|
| **Notification API**     | Recepción y validación de solicitudes  | .NET 8 Web API          |
| **Notification Processor** | Procesamiento y envío de notificaciones | .NET 8 Worker Service   |
| **PostgreSQL**           | Persistencia de datos y auditoría      | PostgreSQL 15+          |
| **Redis**                | Cola de mensajes y cache               | Redis 7+                |
| **File Storage**         | Almacenamiento de adjuntos             | Sistema de archivos     |

## 5.2 Componentes del API

| Componente               | Responsabilidad                        | Tecnología              |
|--------------------------|----------------------------------------|-------------------------|
| **Notification Controller** | Exposición de endpoints REST         | ASP.NET Core            |
| **Template Controller**     | Gestión de plantillas                | ASP.NET Core            |
| **Attachment Service**      | Manejo de adjuntos                   | .NET 8                  |
| **Validation Service**      | Validación de datos y reglas         | FluentValidation         |

## 5.3 Componentes del Processor

| Componente               | Responsabilidad                        | Tecnología              |
|--------------------------|----------------------------------------|-------------------------|
| **Orchestrator Service**    | Orquestación y control de flujos     | .NET 8                  |
| **Template Engine**         | Procesamiento de plantillas          | RazorEngine             |
| **Email Handler**           | Envío de emails                      | SMTP                    |
| **SMS Handler**             | Envío de SMS                         | HTTP API                |
| **Push Handler**            | Envío de notificaciones push         | HTTP API                |
| **Scheduler Service**       | Programación y temporización         | .NET 8 Timer            |

## 5.4 Esquemas de Base de Datos

### 5.4.1 Tabla: `notifications`

| Campo              | Tipo           | Descripción                        | Restricciones                  |
|--------------------|---------------|------------------------------------|-------------------------------|
| `id`               | UUID          | Identificador único                | PRIMARY KEY                   |
| `request_id`       | VARCHAR(100)  | ID de la solicitud                 | NOT NULL, INDEX               |
| `message_id`       | VARCHAR(100)  | ID del mensaje                     | UNIQUE                        |
| `tenant_id`        | VARCHAR(50)   | Identificador del tenant           | NOT NULL, INDEX               |
| `user_id`          | VARCHAR(100)  | ID del usuario destinatario        | NOT NULL                      |
| `notification_type`| VARCHAR(50)   | transactional, marketing           | NOT NULL                      |
| `channels`         | JSONB         | Canales solicitados                | NOT NULL                      |
| `recipient`        | JSONB         | Datos del destinatario             | NOT NULL                      |
| `message_content`  | JSONB         | Contenido del mensaje              | NOT NULL                      |
| `schedule`         | JSONB         | Configuración de programación      | NULL                          |
| `metadata`         | JSONB         | Metadatos adicionales              | NULL                          |
| `status`           | VARCHAR(20)   | pending, processing, sent, failed  | NOT NULL, DEFAULT 'pending'   |
| `created_at`       | TIMESTAMP     | Fecha de creación                  | NOT NULL, DEFAULT NOW()       |
| `updated_at`       | TIMESTAMP     | Fecha de actualización             | NOT NULL, DEFAULT NOW()       |
| `sent_at`          | TIMESTAMP     | Fecha de envío                     | NULL                          |

### 5.4.2 Tabla: `notification_deliveries`

| Campo                  | Tipo         | Descripción                        | Restricciones                  |
|------------------------|-------------|------------------------------------|-------------------------------|
| `id`                   | UUID        | Identificador único                | PRIMARY KEY                   |
| `notification_id`      | UUID        | Referencia a notification          | FOREIGN KEY, NOT NULL         |
| `channel`              | VARCHAR(20) | Canal: email, sms, push            | NOT NULL                      |
| `status`               | VARCHAR(20) | pending, sent, delivered, failed   | NOT NULL                      |
| `provider`             | VARCHAR(50) | Proveedor utilizado                | NOT NULL                      |
| `provider_message_id`  | VARCHAR(200)| ID del proveedor                   | NULL                          |
| `error_message`        | TEXT        | Mensaje de error                   | NULL                          |
| `retry_count`          | INTEGER     | Número de reintentos               | DEFAULT 0                     |
| `sent_at`              | TIMESTAMP   | Fecha de envío                     | NULL                          |
| `delivered_at`         | TIMESTAMP   | Fecha de entrega confirmada        | NULL                          |
| `created_at`           | TIMESTAMP   | Fecha de creación                  | NOT NULL, DEFAULT NOW()       |

### 5.4.3 Tabla: `notification_templates`

| Campo              | Tipo         | Descripción                        | Restricciones                  |
|--------------------|-------------|------------------------------------|-------------------------------|
| `id`               | UUID        | Identificador único                | PRIMARY KEY                   |
| `template_id`      | VARCHAR(100)| ID del template                    | UNIQUE, NOT NULL              |
| `tenant_id`        | VARCHAR(50) | Identificador del tenant           | NOT NULL, INDEX               |
| `name`             | VARCHAR(200)| Nombre descriptivo                 | NOT NULL                      |
| `channel`          | VARCHAR(20) | Canal: email, sms, push            | NOT NULL                      |
| `subject_template` | TEXT        | Template del asunto                | NULL                          |
| `body_template`    | TEXT        | Template del cuerpo                | NOT NULL                      |
| `variables`        | JSONB       | Variables disponibles              | NULL                          |
| `is_active`        | BOOLEAN     | Estado del template                | DEFAULT true                  |
| `created_at`       | TIMESTAMP   | Fecha de creación                  | NOT NULL, DEFAULT NOW()       |
| `updated_at`       | TIMESTAMP   | Fecha de actualización             | NOT NULL, DEFAULT NOW()       |

## 5.5 Endpoints de API

Se describen los principales endpoints REST para la gestión y consulta de notificaciones y plantillas. Los contratos de datos siguen el estándar DTO y están alineados con la arquitectura Clean Architecture.

### 5.5.1 Notification API

- **POST `/api/v1/notifications`**: Enviar nueva notificación
- **GET `/api/v1/notifications/{notificationId}`**: Consultar estado de notificación
- **POST `/api/v1/notifications/bulk`**: Envío masivo de notificaciones

### 5.5.2 Template Management API

- **GET `/api/v1/templates`**: Listar plantillas disponibles
- **POST `/api/v1/templates`**: Crear nueva plantilla

## 5.6 Contratos de Datos (DTOs)

Los siguientes DTOs definen la estructura de los datos de entrada y salida de la API:

### 5.6.1 `NotificationRequest`

```csharp
public class NotificationRequest
{
    public string RequestId { get; set; }
    public DateTime Timestamp { get; set; }
    public string NotificationType { get; set; } // "transactional" | "marketing"
    public List<string> Channels { get; set; }
    public RecipientDto Recipient { get; set; }
    public MessageDto Message { get; set; }
    public ScheduleDto Schedule { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
}

public class RecipientDto
{
    public string UserId { get; set; }
    public string Email { get; set; }
    public string Phone { get; set; }
    public string PushToken { get; set; }
    public Dictionary<string, string> CustomFields { get; set; }
}

public class MessageDto
{
    public string Subject { get; set; }
    public string Body { get; set; }
    public List<string> Attachments { get; set; }
    public string SmsText { get; set; }
    public PushNotificationDto PushNotification { get; set; }
}

public class PushNotificationDto
{
    public string Title { get; set; }
    public string Body { get; set; }
    public string Icon { get; set; }
    public PushActionDto Action { get; set; }
}

public class PushActionDto
{
    public string Type { get; set; }
    public string Url { get; set; }
}

public class ScheduleDto
{
    public DateTime? SendAt { get; set; }
    public string TimeZone { get; set; }
}
```

### 5.6.2 `NotificationResponse`

```csharp
public class NotificationResponse
{
    public string NotificationId { get; set; }
    public string Status { get; set; }
    public DateTime EstimatedDelivery { get; set; }
    public List<string> Warnings { get; set; }
}

public class NotificationStatusResponse
{
    public string NotificationId { get; set; }
    public string RequestId { get; set; }
    public string Status { get; set; }
    public List<ChannelDeliveryDto> Channels { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? SentAt { get; set; }
}

public class ChannelDeliveryDto
{
    public string Channel { get; set; }
    public string Status { get; set; }
    public DateTime? SentAt { get; set; }
    public DateTime? DeliveredAt { get; set; }
    public string Error { get; set; }
    public int RetryCount { get; set; }
}
```

## 5.7 Ejemplos de Implementación

A continuación, se presentan ejemplos de implementación de controladores y servicios siguiendo buenas prácticas de Clean Architecture, DDD y manejo de errores.

### 5.7.1 Controller de Notificaciones

```csharp
[ApiController]
[Route("api/v1/[controller]")]
public class NotificationsController : ControllerBase
{
    private readonly INotificationService _notificationService;
    private readonly ILogger<NotificationsController> _logger;

    public NotificationsController(
        INotificationService notificationService,
        ILogger<NotificationsController> logger)
    {
        _notificationService = notificationService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<IActionResult> SendNotification(
        [FromBody] NotificationRequest request)
    {
        try
        {
            var result = await _notificationService.SendAsync(request);
            return Accepted(result);
        }
        catch (ValidationException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error sending notification {RequestId}", request.RequestId);
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpGet("{notificationId}")]
    public async Task<IActionResult> GetNotificationStatus(string notificationId)
    {
        var status = await _notificationService.GetStatusAsync(notificationId);
        if (status == null)
            return NotFound();

        return Ok(status);
    }
}
```

### 5.7.2 Servicio de Notificaciones

```csharp
public class NotificationService : INotificationService
{
    private readonly INotificationRepository _repository;
    private readonly IQueueService _queueService;
    private readonly ITemplateEngine _templateEngine;
    private readonly ILogger<NotificationService> _logger;

    public async Task<NotificationResponse> SendAsync(NotificationRequest request)
    {
        // Validar request
        await ValidateRequestAsync(request);

        // Crear notificación en BD
        var notification = new Notification
        {
            Id = Guid.NewGuid(),
            RequestId = request.RequestId,
            MessageId = GenerateMessageId(),
            TenantId = GetCurrentTenantId(),
            UserId = request.Recipient.UserId,
            NotificationType = request.NotificationType,
            Channels = request.Channels,
            Recipient = request.Recipient,
            MessageContent = request.Message,
            Schedule = request.Schedule,
            Metadata = request.Metadata,
            Status = NotificationStatus.Pending
        };

        await _repository.CreateAsync(notification);

        // Encolar para procesamiento
        if (request.Schedule?.SendAt != null && request.Schedule.SendAt > DateTime.UtcNow)
        {
            await _queueService.ScheduleAsync(notification, request.Schedule.SendAt.Value);
        }
        else
        {
            await _queueService.EnqueueAsync(notification);
        }

        return new NotificationResponse
        {
            NotificationId = notification.Id.ToString(),
            Status = "accepted",
            EstimatedDelivery = CalculateEstimatedDelivery(request)
        };
    }
}
```

### 5.7.3 Procesador de Email

```csharp
public class EmailHandler : IChannelHandler
{
    private readonly ISmtpClient _smtpClient;
    private readonly ITemplateEngine _templateEngine;
    private readonly ILogger<EmailHandler> _logger;

    public async Task<DeliveryResult> SendAsync(NotificationDelivery delivery)
    {
        try
        {
            var notification = delivery.Notification;
            var emailContent = await _templateEngine.RenderEmailAsync(
                notification.MessageContent,
                notification.Metadata);

            var message = new MimeMessage();
            message.From.Add(new MailboxAddress("System", "noreply@company.com"));
            message.To.Add(new MailboxAddress("", notification.Recipient.Email));
            message.Subject = emailContent.Subject;

            var bodyBuilder = new BodyBuilder
            {
                HtmlBody = emailContent.HtmlBody,
                TextBody = emailContent.TextBody
            };

            // Agregar attachments
            foreach (var attachment in emailContent.Attachments)
            {
                bodyBuilder.Attachments.Add(attachment.FileName, attachment.Content);
            }

            message.Body = bodyBuilder.ToMessageBody();

            await _smtpClient.SendAsync(message);

            return DeliveryResult.Success(DateTime.UtcNow);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send email for delivery {DeliveryId}", delivery.Id);
            return DeliveryResult.Failed(ex.Message);
        }
    }
}
```
