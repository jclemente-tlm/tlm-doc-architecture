
# 5. Vista de bloques de construcción

![Sistema SITA Messaging - Vista General](/diagrams/servicios-corporativos/sita_messaging_system.png)
*Figura 5.1: Vista general de contenedores*

## 5.1 Contenedores principales

| Contenedor             | Responsabilidad principal                | Tecnología         |
|------------------------|------------------------------------------|--------------------|
| Event Processor        | Ingesta y procesamiento de eventos SITA  | .NET 8, Worker Service, SNS+SQS |
| Message Sender         | Envío de archivos SITA a partners        | .NET 8, Background Service      |
| SITA Messaging DB      | Almacenamiento de datos y colas          | PostgreSQL                     |
| SITA Message Queue     | Cola de eventos para procesamiento       | AWS SQS                        |
| File Storage           | Almacenamiento de archivos SITA          | S3-compatible                   |
| Autenticación          | Gestión de identidad y acceso            | Keycloak                        |
| Observabilidad         | Métricas, logs, trazabilidad            | Prometheus, Serilog, OpenTelemetry |

## 5.2 Componentes principales

### Event Processor

![Event Processor - Vista de Componentes](/diagrams/servicios-corporativos/sita_messaging_system_event_processor.png)
*Figura 5.2: Componentes principales del procesamiento de eventos*

| Componente         | Rol/Función                                 | Tecnología                |
|--------------------|---------------------------------------------|---------------------------|
| Event Consumer     | Consume y deserializa eventos               | .NET 8                    |
| Event Orchestrator | Coordina generación y registro de mensajes  | .NET 8                    |
| Message Repository | Registra mensajes para envío posterior      | .NET 8, EF Core           |
| Template Engine    | Procesa plantillas SITA                     | .NET 8, Scriban           |
| SITA File Generator| Genera archivos SITA                        | .NET 8                    |
| Configuration Manager | Gestiona configuración multi-tenant       | .NET 8, EF Core           |
| Health Check       | Verifica salud del procesador               | ASP.NET Core HealthChecks  |
| Metrics Collector  | Recolecta métricas de procesamiento         | Prometheus.NET             |
| Structured Logger  | Logging estructurado                        | Serilog                    |

### Message Sender

![Sender - Vista de Componentes](/diagrams/servicios-corporativos/sita_messaging_system_sender.png)
*Figura 5.3: Componentes principales del servicio de envío*

| Componente         | Rol/Función                                 | Tecnología                |
|--------------------|---------------------------------------------|---------------------------|
| Sending Worker     | Orquesta y ejecuta el envío de archivos     | .NET 8, Quartz.NET        |
| Message Service    | Orquesta envío programado a partners        | .NET 8                    |
| Message Repository | Consulta y actualiza mensajes SITA          | .NET 8, EF Core           |
| File Fetcher       | Obtiene archivos desde storage              | .NET 8, S3 SDK            |
| Partner Sender     | Transmite archivos a partners externos      | .NET 8, SFTP Client       |
| Configuration Manager | Gestiona configuración multi-tenant       | .NET 8, EF Core           |
| Health Check       | Verifica salud del servicio de envío        | ASP.NET Core HealthChecks  |
| Metrics Collector  | Recolecta métricas de envío                 | Prometheus.NET             |
| Structured Logger  | Logging estructurado                        | Serilog                    |
