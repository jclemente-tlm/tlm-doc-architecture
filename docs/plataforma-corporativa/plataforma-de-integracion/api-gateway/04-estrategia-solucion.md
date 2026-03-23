---
sidebar_position: 4
title: Estrategia de Solución
description: Decisiones tecnológicas y de diseño clave del API Gateway con Kong OSS.
---

# 4. Estrategia de Solución

## Decisiones Tecnológicas

| Dimensión           | Decisión                                                                               | Justificación                                                             |
| ------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| API Gateway         | **Kong Gateway 3.9.1**                                                                 | Open source, plugins maduros, self-hosted sin costo de licencia (ADR-003) |
| Admin UI            | **Konga 0.14.9** vía nginx reverse proxy                                               | UI visual para exploración; nginx expone `/konga/` con path rewriting     |
| Configuración       | **decK YAML** declarativo por directorio de entorno                                    | GitOps, trazabilidad, reproducibilidad en todos los entornos              |
| Autenticación       | **Plugin `jwt`** con clave pública RSA embebida en `_consumers.yaml`                   | Validación local offline; sin llamada a Keycloak por request              |
| Multi-tenancy       | **Un tenant (realm) por scope** (`tlm-{scope}`); Kong Consumer por tenant              | Aislamiento criptográfico real por tenant (DEC-02)                        |
| Autorización        | **Plugin `acl`** por sistema con grupos en `_consumers.yaml`                           | Autorización coarse-grained en gateway; fine-grained en backend           |
| Rate limiting       | **Plugin `rate-limiting`** `policy: local` por consumer _(Redis pendiente — DT-06)_    | Throttling por tenant; distribuido pendiente de Redis                     |
| Tamaño de payload   | **Plugin `request-size-limiting`** 1 MB uniforme                                       | Protección contra abusos; uniform para todos los servicios                |
| Reintentos          | **`retries: 0`** en todos los servicios                                                | Operaciones POST no idempotentes; evita duplicación (ADR-009)             |
| Observabilidad      | **Plugin `prometheus`** + **Plugin `correlation-id`** globales                         | Métricas de latencia/throughput; correlación de requests en logs          |
| Patrón de rutas     | `/api/{sistema}` por sistema de negocio                                                | Namespace claro; escalable a nuevos sistemas sin conflictos (ADR-001)     |
| Integración externa | **`request-transformer`**: inyecta `x-api-key`, reescribe URI, elimina `Authorization` | Adaptación al API de TalentHub ATS sin modificar el backend de Talma      |

## Modelo de Configuración Declarativa

Toda la configuración de Kong se gestiona con `decK` y archivos YAML organizados por entorno:

```
config/kong/
├── local/          # Desarrollo local (docker-compose.local.yml)
│   ├── _plugins.yaml   # Plugins globales: correlation-id, prometheus
│   ├── _consumers.yaml # Consumers JWT por realm + ACL groups
│   ├── sisbon.yaml     # Servicio Sisbon (DEV + QA)
│   └── gestal.yaml     # Servicio Gestal/TalentHub ATS (DEV + QA)
├── nonprod/        # DEV/QA en AWS
│   └── (misma estructura que local/)
└── prod/           # Producción en AWS
    ├── _plugins.yaml
    ├── _consumers.yaml
    ├── sisbon.yaml     # Solo entorno prod
    └── gestal.yaml
```

deck lee **todos los `*.yaml`** del directorio del entorno al ejecutar `make sync-{env}`.

```
config/kong/{env}/
    ↓ make sync-{env}       (validación + aplicación)
    ↓ deck sync             (estado real de Kong ≡ repo)
```

## Flujo de Promoción por Entorno

```
make sync-local
    ↓ Validar en local
make sync-nonprod
    ↓ Validar en DEV/QA
make sync-prod
    ↓ Aplicar en producción
```

Cada entorno tiene sus propias URLs de backend, rate limits y configuración; el esquema de plugins y consumers es idéntico.
