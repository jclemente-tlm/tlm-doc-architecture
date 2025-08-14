# Registros de Decisiones Arquitectónicas (ADRs)

Este directorio contiene los Registros de Decisiones Arquitectónicas (Architecture Decision Records - ADRs) para el proyecto de servicios corporativos.

## ¿Qué es un ADR?

Un ADR es un documento que captura una decisión arquitectónica importante junto con su contexto, alternativas evaluadas, criterios de decisión y consecuencias.

## Formato Estándar

Cada ADR sigue la estructura:

- **Estado**: Propuesta, Aceptada, Obsoleta, Supersedida
- **Contexto**: Situación que motiva la decisión y alternativas evaluadas
- **Comparativa**: Matriz de criterios con pesos y puntuaciones
- **Análisis de Costos**: TCO y consideraciones económicas
- **Decisión**: La decisión tomada con justificación
- **Consecuencias**: Resultados positivos, negativos y neutros
- **Referencias**: Enlaces y documentación relevante

## Clasificación de ADRs

### ADRs GLOBALES/COMUNES

| ADR | Título | Estado | Fecha Aprobación | Dependencia de Aprobación | Descripción |
|-----|--------|--------|------------------|--------------------------|-------------|
| [ADR-001](/docs/adrs/adr-001-multi-tenancy-paises) | Multi-tenancy por país | Aceptada | Agosto 2025 | Arquitectura + Equipos País | Estrategia de aislamiento y operación multipaís en todos los servicios. |
| [ADR-002](/docs/adrs/adr-002-estandard-apis-rest) | APIs REST estándar | Aceptada | Agosto 2025 | Arquitectura | Definición de contratos, convenciones y versionado para APIs REST. |
| [ADR-003](/docs/adrs/adr-003-gestion-secretos) | Gestión de secretos | Aceptada | Agosto 2025 | Arquitectura + Seguridad | Solución para almacenamiento seguro y rotación de secretos. |
| [ADR-004](/docs/adrs/adr-004-autenticacion-sso) | Autenticación SSO | Aceptada | Agosto 2025 | Arquitectura + Seguridad | Gestión centralizada de identidades y autenticación multi-tenant. |
| [ADR-005](/docs/adrs/adr-005-gestion-configuraciones) | Gestión de configuraciones | Aceptada | Agosto 2025 | Arquitectura + DevOps | Estrategia para versionado, segregación y automatización de configuraciones. |
| [ADR-006](/docs/adrs/adr-006-infraestructura-iac) | Infraestructura como código | Aceptada | Agosto 2025 | Arquitectura + DevOps | Uso de IaC para provisión y gestión de infraestructura multi-cloud. |
| [ADR-007](/docs/adrs/adr-007-contenedores-aws) | Contenedores en AWS | Aceptada | Agosto 2025 | Arquitectura + DevOps | Orquestación y despliegue de microservicios en contenedores. |
| [ADR-008](/docs/adrs/adr-008-gateway-apis) | Gateway de APIs | Aceptada | Agosto 2025 | Arquitectura | Estandarización de entrada/salida y seguridad en el acceso a APIs. |
| [ADR-009](/docs/adrs/adr-009-cicd-pipelines) | CI/CD Pipelines | Aceptada | Agosto 2025 | Arquitectura + DevOps | Automatización de integración y despliegue continuo. |
| [ADR-010](/docs/adrs/adr-010-standard-base-datos) | Base de datos estándar | Aceptada | Agosto 2025 | Arquitectura | Selección y lineamientos para bases de datos relacionales. |
| [ADR-011](/docs/adrs/adr-011-cache-distribuido) | Cache distribuido | Aceptada | Agosto 2025 | Arquitectura | Estrategia de caching y consistencia para servicios críticos. |
| [ADR-012](/docs/adrs/adr-012-mensajeria-asincrona) | Mensajería asíncrona | Aceptada | Agosto 2025 | Arquitectura | Patrones y tecnologías para comunicación asíncrona y desacoplada. |
| [ADR-013](/docs/adrs/adr-013-event-sourcing) | Event sourcing | Aceptada | Agosto 2025 | Arquitectura | Modelo de persistencia basado en eventos para trazabilidad y auditoría. |
| [ADR-014](/docs/adrs/adr-014-almacenamiento-objetos) | Almacenamiento de objetos | Aceptada | Agosto 2025 | Arquitectura | Solución para almacenamiento masivo y seguro de archivos y documentos. |
| [ADR-015](/docs/adrs/adr-015-manejo-errores-cola) | Manejo de errores en colas | Aceptada | Agosto 2025 | Arquitectura + DevOps | Estrategia para resiliencia y reprocesamiento de mensajes fallidos. |
| [ADR-016](/docs/adrs/adr-016-logging-estructurado) | Logging estructurado | Aceptada | Agosto 2025 | Arquitectura | Estandarización de logs estructurados y observabilidad. |
| [ADR-017](/docs/adrs/adr-017-versionado-apis) | Versionado de APIs | Aceptada | Agosto 2025 | Arquitectura | Estrategia de versionado y ciclo de vida de APIs. |
| [ADR-018](/docs/adrs/adr-018-arquitectura-microservicios) | Arquitectura de microservicios | Aceptada | Agosto 2025 | Arquitectura | Modelo de descomposición, comunicación y despliegue basado en microservicios para escalabilidad y resiliencia. |
| [ADR-019](/docs/adrs/adr-019-configuraciones-scripts-bd) | Configuraciones por scripts en BD | Aceptada | Agosto 2025 | Arquitectura + DevOps | Ejecución controlada y versionada de scripts SQL para configuraciones iniciales o puntuales en base de datos multi-motor. |
| [ADR-020](/docs/adrs/adr-020-alojamiento-nugets) | ADR-020: Alojamiento de NuGets Internos | Aceptada | Agosto 2025 | Arquitectura + DevOps | Solución para gestión y distribución de paquetes NuGet internos para microservicios y librerías compartidas. |
| [ADR-021](/docs/adrs/adr-021-observabilidad) | ADR-021: Observabilidad | Propuesto | Agosto 2025 | Arquitectura | Estrategia y herramientas para monitoreo, métricas y logs integrados en la plataforma corporativa. |

### ADRs ESPECÍFICOS DE SERVICIO

| ADR | Título | Servicio | Estado | Fecha | Descripción |
|-----|--------|----------|--------|-------|-------------|
| ADR-XXX | Ejemplo de ADR específico | Servicio | Aceptada | AAAA-MM | Descripción breve |

### ✅ ADRs CONSOLIDADOS/ELIMINADOS

| ADR | Título | Estado | Acción Completada |
|-----|--------|--------|------------------|
| ADR-XXX | Ejemplo de ADR eliminado o consolidado | ❌ Eliminada | Motivo o referencia |

## Principios de Decisión

### Criterios de Evaluación Estándar

1. **Agnosticidad/Portabilidad** (25%) - Capacidad de migrar entre proveedores
2. **Escalabilidad** (20%) - Capacidad de crecimiento
3. **Facilidad Operacional** (15%) - Simplicidad de operación
4. **Rendimiento** (15%) - Características de performance
5. **Integración** (10%) - Facilidad de integración con stack .NET
6. **Costos** (10%) - TCO y consideraciones económicas
7. **Comunidad/Soporte** (5%) - Madurez y soporte disponible

### Enfoque Estratégico

- **Agnosticidad primera**: Preferir soluciones portables sobre servicios gestionados
- **Open source cuando sea posible**: Evitar lock-in comercial
- **Estándares de la industria**: Adoptar patrones y protocolos reconocidos
- **Multi-tenancy nativo**: Soporte para operaciones en múltiples países
- **Observabilidad integrada**: Monitoreo, logging y tracing por defecto

## Métricas de ADRs

- **Total ADRs activos**: 17 globales + 4 específicos = 21
- **ADRs por consolidar**: 4
- **Cobertura de decisiones críticas**: 95%
- **Última actualización**: Agosto 2025
