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
- **Análisis de Costos**: TCO y consideraciones económicas
- **Decisión**: La decisión tomada con justificación
- **Consecuencias**: Resultados positivos, negativos y neutros
- **Referencias**: Enlaces y documentación relevante

## Clasificación de ADRs

### ADRs GLOBALES/COMUNES

| ADR | Título | Estado | Fecha Aprobación | Dependencia de Aprobación | Descripción |
|-----|--------|--------|------------------|--------------------------|-------------|
| [ADR-001](/docs/adrs/adr-001-multi-tenancy-paises) | Multi-tenancy por país | Aceptada | Agosto 2025 | Arquitectura + Equipos País | Estrategia de aislamiento y operación multipaís en todos los servicios. |
| [ADR-003](/docs/adrs/adr-003-aws-secrets-manager) | AWS Secrets Manager | Aceptada | Agosto 2025 | Arquitectura + Seguridad | Solución para almacenamiento seguro y rotación automática de secretos. |
| [ADR-004](/docs/adrs/adr-004-keycloak-sso-autenticacion) | Keycloak SSO Autenticación | Aceptada | Agosto 2025 | Arquitectura + Seguridad | Gestión centralizada de identidades y autenticación multi-tenant con Keycloak. |
| [ADR-005](/docs/adrs/adr-005-aws-parameter-store-configs) | AWS Parameter Store Configs | Aceptada | Agosto 2025 | Arquitectura + DevOps | Gestión centralizada de configuraciones multi-tenant con AWS Parameter Store. |
| [ADR-006](/docs/adrs/adr-006-terraform-iac) | Terraform IaC | Aceptada | Agosto 2025 | Arquitectura + DevOps | Infraestructura como código multi-cloud con Terraform para portabilidad. |
| [ADR-007](/docs/adrs/adr-007-aws-ecs-fargate-contenedores) | AWS ECS Fargate Contenedores | Aceptada | Agosto 2025 | Arquitectura + DevOps | Orquestación y despliegue serverless de microservicios con AWS ECS Fargate. |
| [ADR-008](/docs/adrs/adr-008-yarp-api-gateway) | YARP API Gateway | Aceptada | Agosto 2025 | Arquitectura | API Gateway .NET nativo con YARP para enrutamiento y políticas centralizadas. |
| [ADR-009](/docs/adrs/adr-009-github-actions-cicd) | GitHub Actions CI/CD | Aceptada | Agosto 2025 | Arquitectura + DevOps | Automatización de integración y despliegue continuo con GitHub Actions. |
| [ADR-010](/docs/adrs/adr-010-postgresql-base-datos) | PostgreSQL Base de Datos | Aceptada | Agosto 2025 | Arquitectura | PostgreSQL como base de datos relacional estándar para todos los servicios. |
| [ADR-011](/docs/adrs/adr-011-redis-cache-distribuido) | Redis Cache Distribuido | Aceptada | Agosto 2025 | Arquitectura | Cache distribuido de alto rendimiento con Redis para servicios críticos. |
| [ADR-012](/docs/adrs/adr-012-kafka-mensajeria-asincrona) | Kafka Mensajería Asíncrona | Aceptada | Agosto 2025 | Arquitectura | Apache Kafka (AWS MSK) para mensajería asíncrona y event streaming. |
| [ADR-013](/docs/adrs/adr-013-postgresql-event-sourcing) | PostgreSQL Event Sourcing | Aceptada | Agosto 2025 | Arquitectura | Event sourcing con PostgreSQL para trazabilidad completa y auditoría. |
| [ADR-014](/docs/adrs/adr-014-s3-almacenamiento-objetos) | S3 Almacenamiento Objetos | Aceptada | Agosto 2025 | Arquitectura | AWS S3 para almacenamiento masivo de objetos, documentos y backups. |
| [ADR-016](/docs/adrs/adr-016-serilog-logging-estructurado) | Serilog Logging Estructurado | Aceptada | Agosto 2025 | Arquitectura | Serilog para logging estructurado JSON con correlación distribuida. |
| [ADR-019](/docs/adrs/adr-019-dbup-migraciones-bd) | DbUp Migraciones BD | Aceptada | Agosto 2025 | Arquitectura + DevOps | DbUp para migraciones de base de datos versionadas e idempotentes. |
| [ADR-020](/docs/adrs/adr-020-github-packages-nuget) | GitHub Packages NuGet | Aceptada | Agosto 2025 | Arquitectura + DevOps | GitHub Packages como registry de paquetes NuGet internos corporativos. |
| [ADR-021](/docs/adrs/adr-021-prometheus-grafana-observabilidad) | Prometheus + Grafana Observabilidad | Aceptada | Enero 2026 | Arquitectura + SRE | Stack OSS completo: Prometheus, Grafana, Loki, Jaeger y OpenTelemetry. |
| [ADR-022](/docs/adrs/adr-022-github-container-registry) | GitHub Container Registry | Aceptada | Enero 2026 | Arquitectura + DevOps | GitHub Container Registry (ghcr.io) para imágenes Docker corporativas. |
| [ADR-023](/docs/adrs/adr-023-trivy-checkov-security-scanning) | Trivy + Checkov Security Scanning | Aceptada | Enero 2026 | Arquitectura + Security | Escaneo automatizado de vulnerabilidades con Trivy (containers) y Checkov (IaC). |

### ADRs ESPECÍFICOS DE SERVICIO

| ADR | Título | Servicio | Estado | Fecha | Descripción |
|-----|--------|----------|--------|-------|-------------|
| ADR-XXX | Ejemplo de ADR específico | Servicio | Aceptada | AAAA-MM | Descripción breve |

### ✅ ADRs CONSOLIDADOS/ELIMINADOS

| ADR | Título | Estado | Acción Completada |
|-----|--------|--------|------------------|
| ADR-002 | REST + OpenAPI Standard | ❌ Eliminada | Estándar universal de industria. Ver `estandares/apis/01-diseno-rest.md` |
| ADR-015 | Kafka DLT Manejo Errores | ❌ Eliminada | Patrón estándar de mensajería. Documentado en estándar de Kafka |
| ADR-017 | Path Versioning APIs | ❌ Eliminada | Best practice estándar. Ver `estandares/apis/04-versionado.md` |
| ADR-018 | Arquitectura Microservicios | ❌ Eliminada | Patrón genérico dependiente del contexto del proyecto. Ver `lineamientos.md` |

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

- **Total ADRs activos**: 19 globales
- **ADRs Aceptados**: 19
- **ADRs en Propuesta**: 0
- **ADRs eliminados** (estándares de industria / patrones genéricos): 4
- **Cobertura de decisiones críticas**: 100%
- **Última actualización**: Enero 2026
