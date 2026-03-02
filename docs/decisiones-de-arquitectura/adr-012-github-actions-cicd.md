---
title: "ADR-012: GitHub Actions CI/CD"
sidebar_position: 12
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de CI/CD para:

- **Orquestación de pipelines multi-servicio y multi-entorno** (dev, staging, prod)
- **Multi-tenancy** con pipelines segmentados por país/tenant
- **Seguridad integrada** (análisis de vulnerabilidades, compliance)
- **Testing automatizado** (unit, integration, e2e, performance)
- **Rollback automático** ante fallos
- **Observabilidad de pipelines** (métricas, alertas)
- **Gestión de secretos integrada**
- **Agnosticidad de despliegue** (cloud, on-premises, híbrido)

La intención estratégica es **balancear simplicidad y flexibilidad** para automatización empresarial y portabilidad.

Alternativas evaluadas:

- **GitHub Actions** (SaaS, integración GitHub, marketplace)
- **Jenkins** (Self-hosted, plugins extensos)
- **Azure DevOps** (SaaS Microsoft, integración .NET)
- **AWS CodePipeline** (SaaS AWS, integración nativa)
- **CircleCI** (SaaS, Docker-first)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                       | GitHub Actions                                | Jenkins                                  | Azure DevOps                                 | AWS CodePipeline                       | CircleCI                           |
| ------------------------------ | --------------------------------------------- | ---------------------------------------- | -------------------------------------------- | -------------------------------------- | ---------------------------------- |
| **Agnosticidad**               | ⚠️ Vinculado a GitHub                         | ✅ Totalmente agnóstico                  | ⚠️ Ecosistema Microsoft                      | ❌ Lock-in AWS                         | ⚠️ Agnóstico                       |
| **Madurez**                    | ✅ Alta (2019, GitHub native)                 | ✅ Muy alta (2011, automation std)       | ✅ Alta (2018, Microsoft suite)              | ⚠️ Media (2015, AWS ecosystem)         | ✅ Alta (2011, SaaS maduro)        |
| **Adopción**                   | ✅ Alta (20K+ actions Marketplace)            | ✅ Muy alta (23K⭐, legacy std)          | ✅ Alta (Microsoft DevOps)                   | ⚠️ Media (AWS adoption)                | ✅ Alta (SaaS líder)               |
| **Modelo de gestión**          | ✅ Gestionado (GitHub)                        | ⚠️ Self-hosted                           | ✅ Gestionado (Azure)                        | ✅ Gestionado (AWS)                    | ✅ Gestionado (SaaS)               |
| **Complejidad operativa**      | ✅ Baja (0.25 FTE, `<5h/sem)`                 | ❌ Muy Alta (2+ FTE, 20-40h/sem)         | ⚠️ Media (0.5 FTE, 5-10h/sem)                | ✅ Baja (0.25 FTE, `<5h/sem)`          | ✅ Baja (0.25 FTE, `<5h/sem)`      |
| **Seguridad**                  | ✅ Integrada                                  | ⚠️ Limitada                              | ✅ Integrada                                 | ✅ Integrada                           | ✅ Integrada                       |
| **Multi-tenancy**              | ✅ Por repos/org                              | ✅ Flexible config                       | ✅ Projects/Teams                            | ⚠️ Por accounts                        | ⚠️ Por contexts                    |
| **Escalabilidad**              | ✅ Hasta 10K+ workflows concurrentes (GitHub) | ⚠️ Limitada por infra (`<100 `executors) | ✅ Hasta 1K+ agents paralelos (Azure DevOps) | ✅ Hasta 1K+ pipelines (AWS CodeBuild) | ✅ Hasta 1K+ containers (CircleCI) |
| **Extensibilidad**             | ✅ 20K+ actions                               | ✅ 1.8K+ plugins                         | ⚠️ Extensions básicas                        | ⚠️ Integraciones                       | ⚠️ Orbs                            |
| **Ejecutores auto-hospedados** | ✅ Soportado (Linux, Windows, macOS)          | ✅ Nativo (master nodes)                 | ✅ Azure-hosted + self-hosted                | ✅ EC2 fleet management                | ✅ Self-hosted runners             |
| **Compilaciones en matriz**    | ✅ Matrix strategy nativo (OS, versions)      | ✅ Matrix builds via scripting           | ✅ Matrix strategy nativo                    | ⚠️ Buildspec phases (limitado)         | ✅ Matrix/parallelism nativo       |
| **Retención de artefactos**    | ✅ 90 días (configurable)                     | ⚠️ Manual S3/storage                     | ✅ 30 días default (configurable)            | ✅ S3 artifacts (configurable)         | ✅ 30 días (CircleCI)              |
| **Límites de concurrencia**    | ✅ 20 jobs (free), 60 jobs (Teams), 180 (Ent) | ⚠️ Ilimitado (depende infra)             | ✅ 10 pipelines (Basic), ilimitado (Ent)     | ✅ 20 builds concurrentes (free)       | ✅ 1-80 concurrent (según plan)    |
| **Flujos reutilizables**       | ✅ Reusable workflows nativo                  | ⚠️ Shared libraries (Groovy scripts)     | ✅ YAML templates                            | ⚠️ Shared buildspec (limitado)         | ✅ Orbs (reusable config)          |
| **Costos**                     | ✅ Gratis (2K min/mes) + $0.008/min exceso    | ⚠️ $0 licencia + ~$200-500/mes infra     | ✅ Gratis (1.8K min/mes) + $40/usuario/mes   | ⚠️ $1/pipeline/mes + variables         | ⚠️ $15-60/usuario/mes (según plan) |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **GitHub Actions** como plataforma estándar de CI/CD para todos los servicios corporativos, priorizando integración nativa, flexibilidad y control operativo.

### Justificación

- Integración nativa con `GitHub` y repositorios existentes
- Workflows reutilizables y plantillas para distintos stacks
- Marketplace de acciones y comunidad activa
- Facilidad de integración con AWS y otros proveedores cloud
- Seguridad, auditoría y control de permisos granular
- Costos optimizados y escalabilidad gestionada

### Alternativas descartadas

- **Jenkins:** complejidad operativa alta (gestión infraestructura, plugins, seguridad), requiere expertise DevOps dedicado, costos ocultos de mantenimiento
- **Azure DevOps:** menor adopción en arquitecturas AWS-first, integración menos fluida con servicios AWS vs GitHub Actions
- **AWS CodePipeline:** lock-in AWS fuerte, configuración más compleja (JSON/YAML + consola), menor flexibilidad para CI/CD multi-cloud
- **CircleCI:** costos crecientes con escala (US$15-60/usuario/mes para equipos), menor integración con GitHub vs Actions nativo

---

## ⚠️ CONSECUENCIAS

### Positivas

- Integración nativa con GitHub y repositorios existentes
- Workflows reutilizables y plantillas para distintos stacks
- Marketplace de acciones y comunidad activa
- Seguridad, auditoría y control de permisos granular
- Costos optimizados y escalabilidad gestionada

### Negativas (Riesgos y Mitigaciones)

- **Lock-in GitHub:** mitigado con pipelines como código (YAML) y contenedores estándar
- **Límites de minutos:** mitigado con plan optimizado y monitoreo de uso
- **Complejidad workflows:** mitigado con plantillas corporativas y documentación

---

## 📚 REFERENCIAS

- [GitHub Actions](https://github.com/features/actions)
- [Jenkins](https://www.jenkins.io/)
- [Azure DevOps Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/)
- [AWS CodePipeline](https://aws.amazon.com/codepipeline/)
- [CircleCI](https://circleci.com/)
