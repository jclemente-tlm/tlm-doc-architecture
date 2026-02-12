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
- **GitLab CI/CD** (SaaS/Self-hosted, DevSecOps)
- **Jenkins** (Self-hosted, plugins extensos)
- **Azure DevOps** (SaaS Microsoft, integración .NET)
- **AWS CodePipeline** (SaaS AWS, integración nativa)
- **CircleCI** (SaaS, Docker-first)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | GitHub Actions        | GitLab CI/CD        | Jenkins                 | Azure DevOps            | AWS CodePipeline | CircleCI      |
| ------------------- | --------------------- | ------------------- | ----------------------- | ----------------------- | ---------------- | ------------- |
| **Agnosticidad**    | ⚠️ Vinculado a GitHub | ✅ Muy agnóstico    | ✅ Totalmente agnóstico | ⚠️ Ecosistema Microsoft | ❌ Lock-in AWS   | ⚠️ Agnóstico  |
| **Operación**       | ✅ Gestionado         | ✅ SaaS/self-hosted | ⚠️ Manual               | ✅ Gestionado           | ✅ Gestionado    | ✅ Gestionado |
| **Seguridad**       | ✅ Integrada          | ✅ Integrada        | ⚠️ Limitada             | ✅ Integrada            | ✅ Integrada     | ✅ Integrada  |
| **Ecosistema .NET** | ✅ Excelente          | ✅ Muy bueno        | ✅ Bueno                | ✅ Nativo               | ✅ Bueno         | ✅ Bueno      |
| **Extensibilidad**  | ✅ Marketplace        | ⚠️ Bueno            | ✅ Plugins              | ⚠️ Limitado             | ⚠️ Básico        | ⚠️ Limitado   |
| **Costos**          | ✅ Plan gratuito      | ✅ Plan gratuito    | ⚠️ Infraestructura      | ✅ Plan gratuito        | ⚠️ Por uso       | ⚠️ Por uso    |

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

- **GitLab CI/CD:** menor integración con GitHub y AWS
- **Azure DevOps:** menos adoptado en ecosistemas AWS puros
- **Jenkins:** mayor complejidad operativa y mantenimiento
- **AWS CodePipeline:** lock-in y menor flexibilidad
- **CircleCI:** lock-in y menor flexibilidad

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
- [GitLab CI/CD](https://about.gitlab.com/stages-devops-lifecycle/continuous-integration/)
- [Azure DevOps Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/)
- [Jenkins](https://www.jenkins.io/)
- [AWS CodePipeline](https://aws.amazon.com/codepipeline/)
- [CircleCI](https://circleci.com/)
