# 1. Introducción y objetivos

El **Sistema `Track & Trace`** es una solución distribuida `multi-tenant` para la trazabilidad operacional en tiempo real de equipaje, carga y pasajeros. Permite la captura, procesamiento y consulta eficiente de eventos críticos, soportando altos volúmenes, auditoría y analítica operacional, sobre una arquitectura basada en servicios y tecnologías cloud.

## 1.1 Funcionalidades clave

| Funcionalidad         | Descripción breve                                      |
|----------------------|--------------------------------------------------------|
| `Ingesta de eventos`   | Captura operativa desde múltiples fuentes vía API REST |
| `Procesamiento asíncrono` | Desacople de ingesta y procesamiento usando `AWS SQS`  |
| `Trazabilidad`         | Seguimiento end-to-end de operaciones y eventos         |
| `Multi-tenant`         | Aislamiento y configuración por organización/país       |
| `Consultas optimizadas`| Acceso eficiente a datos históricos y actuales          |
| `Integración externa`  | Publicación de eventos críticos a `SITA Messaging`      |
| `Observabilidad`       | Monitoreo, métricas y trazas distribuidas               |

## 1.2 Objetivos de calidad

| Atributo       | Objetivo                | Métrica                |
|----------------|------------------------|------------------------|
| `Disponibilidad` | Operación continua      | `≥ 99.9% uptime`         |
| `Rendimiento`    | Baja latencia           | `< 100ms` procesamiento  |
| `Escalabilidad`  | Alto volumen            | `50,000+ eventos/hora`   |
| `Confiabilidad`  | Datos consistentes      | Sin pérdida de eventos   |

## 1.3 Requisitos principales

| ID         | Requisito                    | Descripción Detallada                                               |
|------------|-----------------------------|---------------------------------------------------------------------|
| `RF-TT-01`   | `Ingesta de eventos`           | Captura de eventos de múltiples fuentes con alta capacidad          |
| `RF-TT-02`   | `Trazabilidad end-to-end`      | Seguimiento completo con identificadores de correlación             |
| `RF-TT-03`   | `Consultas eficientes`         | Respuestas rápidas y filtrado avanzado                              |
| `RF-TT-04`   | `Multi-tenant`                 | Aislamiento y configuración por `tenant`/país                       |
| `RF-TT-05`   | `Visualización en tiempo real` | APIs para dashboards y métricas agregadas                           |
| `RF-TT-06`   | `Integración con SITA`         | Publicación de eventos críticos a sistemas externos                 |
| `RF-TT-07`   | `Cumplimiento de auditoría`    | Inmutabilidad y trazabilidad completa                               |
| `RF-TT-08`   | `Alertas y monitoreo`          | Detección de patrones y alertas proactivas                          |

## 1.4 Stakeholders

| Rol                   | Responsabilidad                        | Expectativa                        |
|-----------------------|----------------------------------------|------------------------------------|
| `Operaciones`           | Monitoreo y KPIs de negocio            | Visibilidad en tiempo real         |
| `Analistas de Datos`    | Inteligencia empresarial, reporting    | Consultas ricas, datos históricos  |
| `Compliance`            | Auditorías y cumplimiento regulatorio  | Trazas completas, data lineage     |
| `Integradores`          | Integración con sistemas externos      | APIs simples, ingesta confiable    |
| `Arquitecto de Software`| Decisiones técnicas, evolución         | Diseño escalable, optimización     |
