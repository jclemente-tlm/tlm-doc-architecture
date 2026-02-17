---
title: "Registros de Decisiones Arquitectónicas (ADRs)"
sidebar_position: 0
---

Este directorio contiene los Registros de Decisiones Arquitectónicas (Architecture Decision Records - ADRs) para el proyecto de servicios corporativos.

## ¿Qué es un ADR?

Un ADR es un documento que captura una decisión arquitectónica importante junto con su contexto, alternativas evaluadas, criterios de decisión y consecuencias.

## Formato Estándar

Cada ADR sigue la estructura:

- **Estado**: Propuesta, Aceptada, Obsoleta, Supersedida
- **Contexto**: Situación que motiva la decisión y alternativas evaluadas
- **Comparativa**: Matriz de criterios con pesos y puntuaciones
- **Decisión**: La decisión tomada con justificación
- **Consecuencias**: Resultados positivos, negativos y neutros
- **Referencias**: Enlaces y documentación relevante

## Clasificación de ADRs

### ADRs GLOBALES/COMUNES

| ADR                                                        | Título                       | Estado   | Fecha Aprobación | Dependencia de Aprobación   | Descripción                                                                                   |
| ---------------------------------------------------------- | ---------------------------- | -------- | ---------------- | --------------------------- | --------------------------------------------------------------------------------------------- |
| [ADR-001](/docs/adrs/adr-001-estrategia-multi-tenancy)     | Multi-tenancy por país       | Aceptada | Agosto 2025      | Arquitectura + Equipos País | Estrategia de aislamiento y operación multipaís en todos los servicios.                       |
| [ADR-002](/docs/adrs/adr-002-aws-ecs-fargate-contenedores) | AWS ECS Fargate Contenedores | Aceptada | Agosto 2025      | Arquitectura + DevOps       | Orquestación y despliegue serverless de microservicios con AWS ECS Fargate.                   |
| [ADR-003](/docs/adrs/adr-003-keycloak-sso-autenticacion)   | Keycloak SSO Autenticación   | Aceptada | Agosto 2025      | Arquitectura + Seguridad    | Gestión centralizada de identidades y autenticación multi-tenant con Keycloak.                |
| [ADR-004](/docs/adrs/adr-004-aws-secrets-manager)          | AWS Secrets Manager          | Aceptada | Agosto 2025      | Arquitectura + Seguridad    | Solución para almacenamiento seguro y rotación automática de secretos.                        |
| [ADR-005](/docs/adrs/adr-005-aws-parameter-store-configs)  | AWS Parameter Store Configs  | Aceptada | Agosto 2025      | Arquitectura + DevOps       | Gestión centralizada de configuraciones multi-tenant con AWS Parameter Store.                 |
| [ADR-006](/docs/adrs/adr-006-postgresql-base-datos)        | PostgreSQL Base de Datos     | Aceptada | Agosto 2025      | Arquitectura                | PostgreSQL como base de datos relacional estándar para todos los servicios.                   |
| [ADR-007](/docs/adrs/adr-007-s3-almacenamiento-objetos)    | S3 Almacenamiento Objetos    | Aceptada | Agosto 2025      | Arquitectura                | AWS S3 para almacenamiento masivo de objetos, documentos y backups.                           |
| [ADR-008](/docs/adrs/adr-008-kafka-mensajeria-asincrona)   | Kafka Mensajería Asíncrona   | Aceptada | Agosto 2025      | Arquitectura                | Apache Kafka para mensajería asíncrona y event streaming.                                     |
| [ADR-009](/docs/adrs/adr-009-debezium-cdc)                 | Debezium CDC                 | Aceptada | Febrero 2026     | Arquitectura                | Change Data Capture con Debezium para captura de cambios en bases de datos y event streaming. |
| [ADR-010](/docs/adrs/adr-010-kong-api-gateway)             | Kong API Gateway             | Aceptada | Enero 2026       | Arquitectura                | API Gateway open source con Kong para enrutamiento, seguridad y políticas centralizadas.      |
| [ADR-011](/docs/adrs/adr-011-terraform-iac)                | Terraform IaC                | Aceptada | Agosto 2025      | Arquitectura + DevOps       | Infraestructura como código multi-cloud con Terraform para portabilidad.                      |
| [ADR-012](/docs/adrs/adr-012-github-actions-cicd)          | GitHub Actions CI/CD         | Aceptada | Agosto 2025      | Arquitectura + DevOps       | Automatización de integración y despliegue continuo con GitHub Actions.                       |
| [ADR-013](/docs/adrs/adr-013-github-container-registry)    | GitHub Container Registry    | Aceptada | Enero 2026       | Arquitectura + DevOps       | GitHub Container Registry (ghcr.io) para imágenes Docker corporativas.                        |
| [ADR-014](/docs/adrs/adr-014-grafana-stack-observabilidad) | Grafana Stack Observabilidad | Aceptada | Enero 2026       | Arquitectura + SRE          | Stack OSS completo: Loki, Mimir, Tempo, Grafana y Alloy para observabilidad.                  |

### ADRs ESPECÍFICOS DE SERVICIO

| ADR     | Título                    | Servicio | Estado   | Fecha   | Descripción       |
| ------- | ------------------------- | -------- | -------- | ------- | ----------------- |
| ADR-XXX | Ejemplo de ADR específico | Servicio | Aceptada | AAAA-MM | Descripción breve |

### ✅ ADRs CONSOLIDADOS/ELIMINADOS

| ADR     | Título                  | Estado       | Acción Completada                                      |
| ------- | ----------------------- | ------------ | ------------------------------------------------------ |
| ADR-XXX | Ejemplo ADR consolidado | ❌ Eliminada | Razón de eliminación y referencia a documentación alt. |

> Esta tabla registrará ADRs que sean consolidados, supersedidos o eliminados en el futuro por no requerir decisión arquitectónica formal.

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

- **Total ADRs activos**: 14 globales
- **ADRs Aceptados**: 14
- **ADRs en Propuesta**: 0
- **Cobertura de decisiones críticas**: 100%
- **Última actualización**: Febrero 2026
