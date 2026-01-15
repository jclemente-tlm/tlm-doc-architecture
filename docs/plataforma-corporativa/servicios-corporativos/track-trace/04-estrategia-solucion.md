
# 4. Estrategia de solución

## 4.1 Decisiones clave

| Decisión         | Alternativa Elegida                | Justificación                                                                 |
|------------------|------------------------------------|-------------------------------------------------------------------------------|
| Arquitectura     | API REST (Ingesta/Consulta), procesador asíncrono, dashboard web | Separación de responsabilidades, escalabilidad y desacoplamiento por colas    |
| Mensajería       | AWS SQS (event queue), AWS SNS (downstream) | Alta disponibilidad, entrega garantizada, integración con SITA Messaging      |
| Persistencia     | PostgreSQL, Event Sourcing         | Robustez, soporte multi-tenant, trazabilidad y auditoría                      |
| Observabilidad   | Serilog, Prometheus, Health Checks | Logging estructurado, métricas centralizadas y monitoreo de salud             |
| Configuración    | EF Core, Config Platform           | Gestión centralizada y por tenant                                             |
| Seguridad        | OAuth2/JWT, RBAC                   | Autenticación robusta y control de acceso granular                            |
| Deduplicación    | Control en API Ingesta y Event Publisher | Garantía de entrega única y supresión de duplicados en reintentos        |

> Todas las decisiones priorizan resiliencia, trazabilidad, entrega única y facilidad de evolución, alineadas con los objetivos de calidad y restricciones técnicas del sistema.

## 4.2 Patrones y flujos

| Patrón/Flujo         | Propósito                                 | Implementación / Componente Principal           |
|----------------------|-------------------------------------------|------------------------------------------------|
| CQRS                 | Separación comando/consulta               | API Ingesta, Query API, Event Processor         |
| Event Sourcing       | Trazabilidad y auditoría de eventos       | PostgreSQL, eventos inmutables                  |
| Deduplicación        | Prevención de duplicados                   | API Ingesta, Event Publisher                    |
| Entrega garantizada  | Publicación confiable en colas             | AWS SQS/SNS, control de duplicados              |
| Observabilidad       | Monitoreo y trazabilidad                   | Serilog, Prometheus, Health Checks              |
| Dashboard            | Visualización en tiempo real               | React, TypeScript, Query API                    |
| Configuración        | Multi-tenant y centralizada                | EF Core, Config Platform                        |

> El uso de patrones reconocidos permite mantenibilidad, pruebas y evolución incremental, garantizando entrega única, resiliencia y desacoplamiento de productores y consumidores. La entrega garantizada se logra mediante el control de duplicados y reintentos en la publicación a colas.

## 4.3 Trazabilidad y auditoría

| Aspecto         | Implementación         | Tecnología         |
|-----------------|-----------------------|--------------------|
| Eventos         | Inmutables, multi-tenant| PostgreSQL, Event Sourcing |
| Timeline        | Cronológico           | Query API, índices optimizados |
| Deduplicación   | Por tenant y key       | API Ingesta, Event Publisher   |
| Propagación     | Asíncrona a SITA       | AWS SQS/SNS, SITA Messaging   |
| Dashboard       | Estado y análisis      | React, TypeScript, Query API  |
| Observabilidad  | Logs y métricas        | Serilog, Prometheus           |

---

**Notas:**

- Los componentes principales (`Tracking Ingest API`, `Tracking Event Processor`, `Tracking Query API`, `Tracking Dashboard`, `Tracking Database`, `Tracking Event Queue`) orquestan la ingesta, procesamiento, consulta y visualización de eventos, alineados con el modelo arquitectónico definido.
- El desacoplamiento de productores y consumidores de eventos permite tolerancia a fallos, escalabilidad y evolución independiente de cada integración.
