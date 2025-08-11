# 3. Contexto y Alcance del Sistema

![Servicios Corporativos - Vista de Contexto](/diagrams/servicios-corporativos/corporate_services.png)

*Figura 3.1: Vista de contexto de los Servicios Corporativos*

![Sistema Track & Trace - Vista de Contexto](/diagrams/servicios-corporativos/track_and_trace_system.png)

*Figura 3.2: Vista de contexto del Sistema Track & Trace*

## 3.1 Alcance del Sistema

| Aspecto   | Descripción                                                                 |
|-----------|-----------------------------------------------------------------------------|
| **Incluido**  | Ingesta de eventos, `event sourcing`, `CQRS`, consultas, analytics           |
| **Excluido**  | Generación de eventos, lógica de negocio, procesamiento de datos             |

## 3.2 Actores Externos

| Actor                    | Rol         | Interacción                |
|--------------------------|-------------|----------------------------|
| **Aplicaciones Corporativas** | Proveedor   | Envío de eventos              |
| **SITA Messaging System**    | Consumidor  | Consumo de eventos            |
| **Usuarios Finales**         | Consumidor  | Consultas de trazabilidad     |
| **Sistemas Analytics**       | Consumidor  | Análisis de patrones          |
| **Sistema Identidad**        | Proveedor   | Autenticación                 |
| **Observabilidad**           | Consumidor  | Métricas y logs               |
