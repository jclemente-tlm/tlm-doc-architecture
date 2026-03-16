---
title: "Introducción"
sidebar_position: 0
description: "Estándares técnicos obligatorios que implementan los lineamientos arquitectónicos para código, infraestructura, testing y documentación."
---

Esta sección contiene los estándares técnicos que implementan los [lineamientos arquitectónicos](../lineamientos/) de Talma.

## Estructura

### [APIs REST](./apis/)

Estándares técnicos para el desarrollo de APIs REST:

1. Estándares de APIs REST
2. Manejo de Errores en APIs
3. Versionamiento de APIs
4. Contratos de APIs
5. Paginación de APIs

### [Arquitectura](./arquitectura/)

Estándares de diseño y patrones arquitectónicos:

1. Clean Architecture (Arquitectura Limpia)
2. Modelado de Dominio (Domain-Driven Design)
3. CQRS
4. Principios de Arquitectura
5. Patrones de Resiliencia
6. Escalado Horizontal
7. Evolución de Arquitectura
8. Cloud Native
9. Multi-tenancy
10. Health Checks

### [Datos](./datos/)

Estándares para gestión de datos:

1. Arquitectura de Datos
2. Consistencia de Datos
3. Estándares de Base de Datos
4. Caché

### [Desarrollo](./desarrollo/)

Estándares de código y prácticas de desarrollo:

1. Git Workflow y Estrategia de Ramas
2. Calidad de Código
3. Gestión de Paquetes NuGet
4. Configuración de Aplicaciones
5. Versionamiento Semántico
6. Nomenclatura de Repositorios

### [Documentación](./documentacion/)

Estándares para documentación técnica y diagramas:

1. arc42
2. C4 Model
3. README
4. Guía de Contribución
5. Guías de Onboarding

### [Gobierno](./gobierno/)

Estándares de gobierno arquitectónico:

1. Architecture Review y Checklist
2. Architecture Board y Auditorías
3. Gestión de ADRs
4. Compliance y Validación Automatizada
5. Gestión de Excepciones
6. Ownership de Servicios
7. Fitness Functions e Indicadores de Arquitectura

### [Infraestructura](./infraestructura/)

Estándares para contenedores e infraestructura cloud:

1. Contenerización
2. IaC — Estándares Terraform
3. IaC — Gestión de State y Drift
4. Gestión de Configuración
5. Paridad de Ambientes
6. Despliegue Independiente
7. Redes Virtuales
8. Optimización de Costos Cloud

### [Mensajería](./mensajeria/)

Estándares para mensajería asíncrona y eventos:

1. Mensajería Asíncrona
2. Diseño de Eventos
3. Catálogo de Eventos
4. Idempotencia en Eventos
5. Contratos de Eventos
6. Especificación AsyncAPI
7. Garantías de Entrega de Mensajes
8. Dead Letter Queue
9. Patrones de Mensajería

### [Observabilidad](./observabilidad/)

Estándares para logging, monitoreo y trazabilidad:

1. Structured Logging
2. Métricas con OpenTelemetry
3. Distributed Tracing
4. Dashboards en Grafana
5. Alertas con Grafana
6. SLO y SLA

### [Operabilidad](./operabilidad/)

Estándares para operación y continuidad:

1. CI/CD Pipelines y Build
2. Despliegue
3. Backup y Restore
4. Procedimientos de DR
5. Runbooks

### [Seguridad](./seguridad/)

Estándares de seguridad:

1. Zero Trust Networking y mTLS
2. Verificación Explícita, Assume Breach y Trust Boundaries
3. SSO, MFA y RBAC
4. Gestión Avanzada de Identidades y Accesos
5. Segmentación y Controles de Acceso de Red
6. Aislamiento de Ambientes y Tenants
7. Protección de Datos
8. Gestión de Secretos y Claves Criptográficas
9. Gobernanza de Seguridad
10. Escaneo de Seguridad

### [Testing](./testing/)

Estándares para pruebas automatizadas:

1. Pruebas Unitarias
2. Pruebas de Integración
3. Pirámide de Testing
4. Automatización de Pruebas
5. Cobertura de Código
6. Pruebas de Contrato
7. Pruebas End-to-End
8. Pruebas de Performance
9. Pruebas de Seguridad

## Relación con otros niveles

```
Principios (POR QUÉ)
    ↓
Lineamientos (CÓMO abstracto)
    ↓
Estándares (QUÉ técnico)  ← Estás aquí
    ↓
Código de Producción
```

### Diferencias clave

| Nivel           | Descripción              | Ejemplo                                                         |
| --------------- | ------------------------ | --------------------------------------------------------------- |
| **Principio**   | Valor fundamental        | "Seguridad desde el Diseño"                                     |
| **Lineamiento** | Directriz arquitectónica | "Diseñar APIs con autenticación y autorización obligatoria"     |
| **Estándar**    | Especificación técnica   | "Usar JWT Bearer con validación de issuer, audience y lifetime" |

## Referencias

- [Principios](../principios/)
- [Lineamientos](../lineamientos/)
- [ADRs](/adrs/)

---

**Última actualización**: Marzo 2026
**Responsable**: Equipo de Arquitectura
