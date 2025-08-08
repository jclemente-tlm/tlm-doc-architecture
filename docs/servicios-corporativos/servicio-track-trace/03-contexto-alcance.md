# 3. Contexto y alcance del sistema

![Servicios Corporativos - Vista de Contexto](/diagrams/servicios-corporativos/corporate_services.png)

*Figura 3.1: Vista de contexto de los Servicios Corporativos*

![Sistema Track & Trace - Vista de Contexto](/diagrams/servicios-corporativos/track_and_trace_system.png)

*Figura 3.2: Vista de contexto del Sistema Track & Trace*

## 3.1 Alcance del sistema

| Aspecto | Descripción |
|---------|-------------|
| **Incluido** | Ingesta de eventos, event sourcing, CQRS, consultas, analytics |
| **Excluido** | Generación de eventos, lógica de negocio, procesamiento de datos |

## 3.2 Actores externos

| Actor | Rol | Interacción |
|-------|-----|-------------|
| **Aplicaciones Corporativas** | Proveedores | Envío de eventos |
| **SITA Messaging System** | Consumidor | Consumo de eventos |
| **Usuarios Finales** | Consumidores | Consultas de trazabilidad |
| **Sistemas Analytics** | Consumidores | Análisis de patrones |
| **Sistema Identidad** | Proveedor | Autenticación |
| **Observabilidad** | Consumidor | Métricas y logs |
