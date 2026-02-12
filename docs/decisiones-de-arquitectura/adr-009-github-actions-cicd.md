---
title: "ADR-009: GitHub Actions CI/CD"
sidebar_position: 9
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
- **GitLab CI/CD** (SaaS/self-hosted, integración GitLab)
- **Jenkins** (Self-hosted, plugins extensos)
- **Azure DevOps** (SaaS Microsoft, integración .NET)
- **AWS CodePipeline** (SaaS AWS, integración nativa)
- **CircleCI** (SaaS, Docker-first)
- **TeamCity** (JetBrains, .NET-friendly)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | GitHub Actions        | GitLab CI/CD          | Jenkins                 | Azure DevOps            | AWS CodePipeline | CircleCI      | TeamCity       |
| ------------------- | --------------------- | --------------------- | ----------------------- | ----------------------- | ---------------- | ------------- | -------------- |
| **Agnosticidad**    | ⚠️ Vinculado a GitHub | ⚠️ Vinculado a GitLab | ✅ Totalmente agnóstico | ⚠️ Ecosistema Microsoft | ❌ Lock-in AWS   | ⚠️ Agnóstico  | ⚠️ Agnóstico   |
| **Operación**       | ✅ Gestionado         | ✅ Gestionado/Híbrido | ⚠️ Manual               | ✅ Gestionado           | ✅ Gestionado    | ✅ Gestionado | ⚠️ Self-hosted |
| **Seguridad**       | ✅ Integrada          | ✅ Integrada          | ⚠️ Limitada             | ✅ Integrada            | ✅ Integrada     | ✅ Integrada  | ✅ Buena       |
| **Ecosistema .NET** | ✅ Excelente          | ✅ Bueno              | ✅ Bueno                | ✅ Nativo               | ✅ Bueno         | ✅ Bueno      | ✅ Excelente   |
| **Extensibilidad**  | ✅ Marketplace        | ✅ Extenso            | ✅ Plugins              | ⚠️ Limitado             | ⚠️ Básico        | ⚠️ Limitado   | ✅ Plugins     |
| **Costos**          | ✅ Plan gratuito      | ✅ Plan gratuito/OSS  | ⚠️ Infraestructura      | ✅ Plan gratuito        | ⚠️ Por uso       | ⚠️ Por uso    | ⚠️ Licencias   |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **GitHub Actions** como plataforma estándar de CI/CD para todos los servicios corporativos, priorizando integración nativa, flexibilidad y control operativo.

## Justificación

- Integración nativa con `GitHub` y repositorios existentes
- Workflows reutilizables y plantillas para distintos stacks
- Marketplace de acciones y comunidad activa
- Facilidad de integración con AWS y otros proveedores cloud
- Seguridad, auditoría y control de permisos granular
- Costos optimizados y escalabilidad gestionada

## Alternativas descartadas

- **GitLab CI/CD:** requiere migración de repositorios GitHub, ecosistema menos integrado con GitHub Packages/Container Registry (ADR-020, ADR-022), menor adopción en equipo
- **Jenkins:** complejidad operativa alta (gestión infraestructura, plugins, seguridad), requiere expertise DevOps dedicado, costos ocultos de mantenimiento
- **Azure DevOps:** menor adopción en arquitecturas AWS-first, integración menos fluida con servicios AWS vs GitHub Actions
- **AWS CodePipeline:** lock-in AWS fuerte, configuración más compleja (JSON/YAML + consola), menor flexibilidad para CI/CD multi-cloud
- **CircleCI:** costos crecientes con escala (US$15-60/usuario/mes para equipos), menor integración con GitHub vs Actions nativo
- **TeamCity:** costos de licencias (US$1,999+ para 100 build configs), self-hosted requiere gestión, menor comunidad vs GitHub Actions

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
- **Límites de minutos:** mitigados con plan optimizado y monitoreo de uso
- **Complejidad workflows:** mitigada con plantillas corporativas y documentación

---

## 📚 REFERENCIAS

- [GitHub Actions](https://github.com/features/actions)
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [Jenkins](https://www.jenkins.io/)
- [Azure DevOps Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/)
- [AWS CodePipeline](https://aws.amazon.com/codepipeline/)
- [CircleCI](https://circleci.com/)
- [TeamCity](https://www.jetbrains.com/teamcity/)
- [Jenkins](https://www.jenkins.io/)
- [AWS CodePipeline](https://aws.amazon.com/codepipeline/)
- [CircleCI](https://circleci.com/)
