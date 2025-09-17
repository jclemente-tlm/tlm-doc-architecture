
# 3. Contexto y alcance

![Servicios Corporativos - Vista de Contexto](/diagrams/servicios-corporativos/corporate_services.png)

*Figura 3.1: Vista de contexto de los Servicios Corporativos*

![Sistema Track & Trace - Vista de Contexto](/diagrams/servicios-corporativos/track_and_trace_system.png)

*Figura 3.2: Vista de contexto del Sistema Track & Trace*

## 3.1 Alcance funcional del sistema

| Aspecto   | Descripción                                                                 |
|-----------|-----------------------------------------------------------------------------|
| Incluido  | Ingesta y procesamiento de eventos de tracking, event sourcing, CQRS, consultas de trazabilidad, dashboards, integración con SITA Messaging, observabilidad, multi-tenant, auditoría y retención de eventos. |
| Excluido  | Generación de eventos en sistemas fuente, lógica de negocio de sistemas externos, procesamiento analítico avanzado fuera del dominio de tracking, gestión de usuarios finales, procesamiento de pagos o facturación. |

> El alcance se centra en la orquestación, trazabilidad y consulta eficiente de eventos críticos de negocio, desacoplando la lógica de negocio de los sistemas fuente y permitiendo la evolución independiente de los consumidores y productores de eventos. La resiliencia y escalabilidad se logran mediante colas, desacoplamiento y procesamiento distribuido.

## 3.2 Actores y sistemas externos

| Actor/Sistema              | Rol         | Interacción                                                                 |
|----------------------------|-------------|----------------------------------------------------------------------------|
| Aplicaciones Corporativas  | Proveedor   | Envían eventos de tracking vía API REST autenticada y autorizada (OAuth2/JWT) |
| SITA Messaging System      | Consumidor  | Recibe eventos procesados para integración con otros sistemas corporativos  |
| Usuarios Finales           | Consumidor  | Consultan trazabilidad y estado de eventos a través de dashboards web       |
| Sistemas Analytics         | Consumidor  | Acceden a datos históricos para análisis de patrones y generación de reportes|
| Sistema de Identidad       | Proveedor   | Provee autenticación y autorización centralizada (OAuth2/JWT)               |
| Observabilidad             | Consumidor  | Consume métricas y logs estructurados para monitoreo y auditoría            |

> Todas las integraciones externas están desacopladas mediante APIs y colas, permitiendo resiliencia, escalabilidad y trazabilidad. La seguridad se garantiza mediante autenticación robusta y control de acceso granular. La observabilidad es transversal, asegurando monitoreo y auditoría de extremo a extremo.

---

**Notas:**

- Los componentes principales (`Tracking Ingest API`, `Tracking Event Processor`, `Tracking Query API`, `Tracking Dashboard`, `Tracking Database`, `Tracking Event Queue`) orquestan la ingesta, procesamiento, consulta y visualización de eventos, alineados con el modelo arquitectónico definido.
- El desacoplamiento de productores y consumidores de eventos permite tolerancia a fallos, escalabilidad y evolución independiente de cada integración.
