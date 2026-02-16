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
- **Jenkins** (Self-hosted, plugins extensos)
- **Azure DevOps** (SaaS Microsoft, integración .NET)
- **AWS CodePipeline** (SaaS AWS, integración nativa)
- **CircleCI** (SaaS, Docker-first)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                  | GitHub Actions         | Jenkins                 | Azure DevOps            | AWS CodePipeline    | CircleCI               |
| ------------------------- | ---------------------- | ----------------------- | ----------------------- | ------------------- | ---------------------- |
| **Agnosticidad**          | ⚠️ Vinculado a GitHub  | ✅ Totalmente agnóstico | ⚠️ Ecosistema Microsoft | ❌ Lock-in AWS      | ⚠️ Agnóstico           |
| **Modelo de gestión**     | ✅ Gestionado (GitHub) | ⚠️ Self-hosted          | ✅ Gestionado (Azure)   | ✅ Gestionado (AWS) | ✅ Gestionado (SaaS)   |
| **Complejidad operativa** | ✅ Baja (GitHub)       | ❌ Alta (setup manual)  | ⚠️ Media (vendor nuevo) | ✅ Baja (infra AWS) | ✅ Baja (simplificado) |
| **Seguridad**             | ✅ Integrada           | ⚠️ Limitada             | ✅ Integrada            | ✅ Integrada        | ✅ Integrada           |
| **Integración .NET**      | ✅ Excelente           | ✅ Bueno                | ✅ Nativo               | ✅ Bueno            | ✅ Bueno               |
| **Multi-tenancy**         | ✅ Por repos/org       | ✅ Flexible config      | ✅ Projects/Teams       | ⚠️ Por accounts     | ⚠️ Por contexts        |
| **Extensibilidad**        | ✅ 20K+ actions        | ✅ 1.8K+ plugins        | ⚠️ Extensions básicas   | ⚠️ Integraciones    | ⚠️ Orbs                |
| **Comunidad**             | ✅ Muy activa          | ✅ Muy activa (65K⭐)   | ✅ Soporte Microsoft    | ✅ Soporte AWS      | ✅ SaaS líder          |
| **Costos**                | ✅ Plan gratuito       | ⚠️ Infraestructura      | ✅ Plan gratuito        | ⚠️ Por uso          | ⚠️ Por uso             |

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
- **Límites de minutos:** mitigados con plan optimizado y monitoreo de uso
- **Complejidad workflows:** mitigada con plantillas corporativas y documentación

---

## 📚 REFERENCIAS

- [GitHub Actions](https://github.com/features/actions)
- [Jenkins](https://www.jenkins.io/)
- [Azure DevOps Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/)
- [AWS CodePipeline](https://aws.amazon.com/codepipeline/)
- [CircleCI](https://circleci.com/)
