---
id: naming-repositorios
sidebar_position: 1
title: Naming - Repositorios
description: Convención de nomenclatura para repositorios en GitHub
---

## 1. Principio

Todos los repositorios deben seguir un patrón consistente que identifique claramente su propósito, tecnología y alcance.

## 2. Reglas

### Regla 1: Prefijo Corporativo Obligatorio

- **Formato**: `tlm-{categoria}-{nombre}[-{subtipo}]`
- **Ejemplo correcto**: `tlm-svc-orders`, `tlm-app-erp`, `tlm-lib-logging`
- **Ejemplo incorrecto**: `orders-service`, `tlm_api_users`, `TLM-Svc-Orders`
- **Justificación**: Identifica repos corporativos en organizaciones compartidas

### Regla 2: Categoría Específica

Usar una de las categorías estándar:

| Categoría | Descripción                 | Ejemplo                   |
| --------- | --------------------------- | ------------------------- |
| `svc`     | Microservicio backend       | `tlm-svc-orders`          |
| `app`     | Aplicación monolítica       | `tlm-app-erp`             |
| `web`     | Frontend web                | `tlm-web-portal-clientes` |
| `lib`     | Librería compartida         | `tlm-lib-logging`         |
| `infra`   | Infraestructura como código | `tlm-infra-terraform-aws` |
| `doc`     | Documentación               | `tlm-doc-architecture`    |
| `int`     | Integración/conectores      | `tlm-int-cdc-kafka`       |
| `corp`    | Servicio corporativo        | `tlm-corp-notifications`  |
| `api`     | Contratos API (OpenAPI)     | `tlm-api-orders`          |
| `arc`     | Arquetipos/templates        | `tlm-arc-api-rest`        |

### Regla 3: Estilo Consistente

- **Solo minúsculas**: `tlm-svc-orders` ✅, `tlm-Svc-Orders` ❌
- **Guiones medios (`-`)**: `tlm-svc-user-profile` ✅, `tlm_svc_userprofile` ❌
- **Sin acentos ni ñ**: `tlm-svc-ordenes` ❌, `tlm-svc-orders` ✅
- **Longitud < 40 caracteres**: Preferir nombres cortos y claros

### Regla 4: Nombre Descriptivo

- **Describe el dominio/propósito**: `tlm-svc-orders` ✅, `tlm-svc-servicio1` ❌
- **En inglés preferentemente**: `tlm-svc-users` ✅, `tlm-svc-usuarios` ⚠️
- **Evita abreviaturas oscuras**: `tlm-svc-usr-mgmt` ❌, `tlm-svc-user-management` ✅

## 3. Tabla de Referencia Rápida

| Tipo Proyecto  | Patrón                 | Ejemplo                |
| -------------- | ---------------------- | ---------------------- |
| API REST .NET  | `tlm-svc-{domain}`     | `tlm-svc-payments`     |
| Frontend React | `tlm-web-{name}`       | `tlm-web-backoffice`   |
| Librería NuGet | `tlm-lib-{name}`       | `tlm-lib-common`       |
| Terraform      | `tlm-infra-{resource}` | `tlm-infra-vpc-aws`    |
| Documentación  | `tlm-doc-{topic}`      | `tlm-doc-architecture` |

## 4. Herramientas de Validación

- **GitHub Actions**: Pre-commit hook para validar naming
- **Renovate/Dependabot**: Config basada en prefijo `tlm-`
- **Scripts**: Validar con regex `^tlm-[a-z]+-[a-z0-9-]+$`

## 5. Excepciones

- **Forks de proyectos externos**: Mantener nombre original si necesario
- **Repos temporales/experimentales**: Usar prefijo `tlm-exp-`
- **Repos archivados**: Agregar sufijo `-archived` o archivar en GitHub

## 📖 Referencias

### Lineamientos relacionados

- [Gestión de Código Fuente](/docs/fundamentos-corporativos/lineamientos/desarrollo/gestion-codigo-fuente)

### Recursos externos

- [GitHub Repository Guidelines](https://docs.github.com/en/repositories)
- [Naming Conventions - Google Style Guide](https://google.github.io/styleguide/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
