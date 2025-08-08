# 5. Vista de bloques de construcción

![Sistema SITA Messaging - Vista General](/diagrams/servicios-corporativos/sita_messaging_system.png)

*Figura 5.1: Vista de contenedores del Sistema SITA Messaging*

![Event Processor - Vista de Componentes](/diagrams/servicios-corporativos/sita_messaging_system_event_processor.png)

*Figura 5.2: Vista de componentes del Event Processor*

![Sender - Vista de Componentes](/diagrams/servicios-corporativos/sita_messaging_system_sender.png)

*Figura 5.3: Vista de componentes del Sender*

## 5.1 Contenedores principales

| Contenedor | Responsabilidad | Tecnología |
|------------|-----------------|------------|
| **Event Processor** | Ingesta y procesamiento de eventos | .NET 8 Worker Service |
| **Sender** | Envío de mensajes SITA | .NET 8 Worker Service |
| **PostgreSQL** | Persistencia de datos y cola | PostgreSQL 15+ |
| **File Storage** | Almacenamiento de archivos SITA | Sistema de archivos |

## 5.2 Componentes del Event Processor

| Componente | Responsabilidad | Tecnología |
|------------|-----------------|------------|
| **Event Consumer** | Consumo de eventos | .NET 8 |
| **Event Orchestrator** | Orquestación de procesamiento | .NET 8 |
| **Template Engine** | Procesamiento de plantillas SITA | RazorEngine |
| **SITA File Generator** | Generación de archivos SITATEX | .NET 8 |

## 5.3 Componentes del Sender

| Componente | Responsabilidad | Tecnología |
|------------|-----------------|------------|
| **Sending Worker** | Orquestación de envíos | .NET 8 Timer |
| **File Fetcher** | Descarga de archivos | .NET 8 |
| **Partner Sender** | Transmisión a red SITA | HTTP/HTTPS |
| **Delivery Tracker** | Seguimiento de entregas | .NET 8 |
