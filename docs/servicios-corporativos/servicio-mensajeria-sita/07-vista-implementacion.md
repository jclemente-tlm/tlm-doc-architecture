# 7. Vista de implementación

![Vista de implementación del Mensajeria SITA](/diagrams/servicios-corporativos/sita_messaging_system_deployment.png)
*Figura 7.1: Implementación de Componentes de principales del sistema*

## 7.1 Estructura del proyecto

| Componente | Ubicación | Tecnología |
|------------|-------------|-------------|
| **Event Processor** | /src/SitaEventProcessor | .NET 8 Worker |
| **Sender** | /src/SitaSender | .NET 8 Worker |
| **PostgreSQL** | AWS RDS | PostgreSQL 15+ |
| **File Storage** | AWS EFS | Sistema archivos |

## 7.2 Dependencias principales

| Dependencia | Versión | Propósito |
|-------------|---------|----------|
| **Entity Framework** | 8.0+ | ORM |
| **RazorEngine** | 4.0+ | Plantillas SITA |
| **Serilog** | 3.0+ | Logging |
| **Polly** | 7.0+ | Resiliencia |
