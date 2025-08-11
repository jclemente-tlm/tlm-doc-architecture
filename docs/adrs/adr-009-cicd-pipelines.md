---
id: adr-009-cicd-pipelines
title: "Pipelines CI/CD"
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

| Criterio              | GitHub Actions | GitLab CI/CD | Jenkins | Azure DevOps | AWS CodePipeline | CircleCI |
|----------------------|----------------|--------------|---------|--------------|------------------|----------|
| **Agnosticidad**     | 🟡 Vinculado a GitHub | ✅ Muy agnóstico | ✅ Totalmente agnóstico | 🟡 Ecosistema Microsoft | ❌ Lock-in AWS | 🟡 Agnóstico |
| **Operación**        | ✅ Gestionado | ✅ SaaS/self-hosted | 🟡 Manual | ✅ Gestionado | ✅ Gestionado | ✅ Gestionado |
| **Seguridad**        | ✅ Integrada | ✅ Integrada | 🟡 Limitada | ✅ Integrada | ✅ Integrada | ✅ Integrada |
| **Ecosistema .NET**  | ✅ Excelente | ✅ Muy bueno | ✅ Bueno | ✅ Nativo | ✅ Bueno | ✅ Bueno |
| **Extensibilidad**   | ✅ Marketplace | 🟡 Bueno | ✅ Plugins | 🟡 Limitado | 🟡 Básico | 🟡 Limitado |
| **Costos**           | ✅ Plan gratuito | ✅ Plan gratuito | 🟡 Infraestructura | ✅ Plan gratuito | 🟡 Por uso | 🟡 Por uso |

### Matriz de Decisión

| Solución                | Agnosticidad | Operación | Seguridad | Ecosistema .NET | Recomendación         |
|------------------------|--------------|-----------|-----------|-----------------|-----------------------|
| **GitHub Actions**     | Buena        | Excelente | Excelente | Excelente       | ✅ **Seleccionada**    |
| **GitLab CI/CD**       | Excelente    | Excelente | Excelente | Muy buena       | 🟡 Alternativa         |
| **Azure DevOps**       | Buena        | Excelente | Excelente | Excelente       | 🟡 Considerada         |
| **Jenkins**            | Excelente    | Manual    | Limitada  | Buena           | ❌ Descartada          |
| **AWS CodePipeline**   | Mala         | Excelente | Excelente | Buena           | ❌ Descartada          |
| **CircleCI**           | Buena        | Excelente | Excelente | Buena           | ❌ Descartada          |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 5 servicios, 200 builds/mes, 4 entornos. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución                | Licenciamiento     | Infraestructura | Operación         | TCO 3 años         |
|------------------------|-------------------|----------------|-------------------|--------------------|
| GitHub Actions         | Incluido          | US$0           | US$3,600/año      | US$10,800          |
| GitLab CI/CD           | US$4,800/año      | US$0           | US$2,400/año      | US$21,600          |
| Azure DevOps           | Incluido          | US$0           | US$4,800/año      | US$14,400          |
| CircleCI               | US$9,000/año      | US$0           | US$1,800/año      | US$32,400          |
| Jenkins                | OSS               | US$7,200/año   | US$18,000/año     | US$75,600          |
| AWS CodePipeline       | US$3,600/año      | US$0           | US$6,000/año      | US$28,800          |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **GitHub Actions:** límites de minutos y almacenamiento según plan
- **GitLab CI/CD:** límites por runners y almacenamiento
- **Jenkins:** depende de infraestructura propia
- **Azure DevOps:** límites por organización y agentes
- **AWS CodePipeline/CircleCI:** límites por cuenta y uso

### Riesgos y mitigación

- **Lock-in plataforma:** mitigado con pipelines como código y contenedores
- **Complejidad Jenkins:** mitigada con automatización y documentación
- **Costos variables:** monitoreo y revisión anual

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

- Todos los servicios deben definir pipelines en GitHub Actions
- Se recomienda estandarizar workflows y plantillas

---

## 📚 REFERENCIAS

- [GitHub Actions](https://github.com/features/actions)
- [GitLab CI/CD](https://about.gitlab.com/stages-devops-lifecycle/continuous-integration/)
- [Azure DevOps Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/)
- [Jenkins](https://www.jenkins.io/)
- [AWS CodePipeline](https://aws.amazon.com/codepipeline/)
- [CircleCI](https://circleci.com/)
