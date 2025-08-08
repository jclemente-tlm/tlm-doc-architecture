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

| ADR | Título | Estado | Fecha | Descripción |
|-----|--------|--------|-------|-------------|
| [ADR-001](./adr-001-multi-tenancy-paises) | Multi-tenancy por país | Aceptada | - | - |
| [ADR-002](./adr-002-apis-rest-estandar) | APIs REST estándar | Aceptada | - | - |
| [ADR-003](./adr-003-gestion-secretos) | Gestión de secretos | Aceptada | - | - |
| [ADR-004](./adr-004-autenticacion-sso) | Autenticación SSO | Aceptada | - | - |
| [ADR-005](./adr-005-gestion-configuraciones) | Gestión de configuraciones | Aceptada | - | - |
| [ADR-006](./adr-006-infraestructura-iac) | Infraestructura como código | Aceptada | - | - |
| [ADR-007](./adr-007-contenedores-aws) | Contenedores en AWS | Aceptada | - | - |
| [ADR-008](./adr-008-gateway-apis) | Gateway de APIs | Aceptada | - | - |
| [ADR-009](./adr-009-cicd-pipelines) | CI/CD Pipelines | Aceptada | - | - |
| [ADR-010](./adr-010-base-datos-standard) | Base de datos estándar | Aceptada | - | - |
| [ADR-011](./adr-011-cache-distribuido) | Cache distribuido | Aceptada | - | - |
| [ADR-012](./adr-012-mensajeria-asincrona) | Mensajería asíncrona | Aceptada | - | - |
| [ADR-013](./adr-013-event-sourcing) | Event sourcing | Aceptada | - | - |
| [ADR-014](./adr-014-almacenamiento-objetos) | Almacenamiento de objetos | Aceptada | - | - |
| [ADR-015](./adr-015-manejo-errores-cola) | Manejo de errores en colas | Aceptada | - | - |
| [ADR-016](./adr-016-logging-estructurado) | Logging estructurado | Aceptada | - | - |
| [ADR-017](./adr-017-versionado-apis) | Versionado de APIs | Aceptada | - | - |
| [ADR-018](./adr-018-arquitectura-microservicios) | Arquitectura de microservicios | Aceptada | - | - |
| [ADR-019](./adr-019-automatizacion-despliegue) | Automatización de despliegue | Aceptada | - | - |

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
