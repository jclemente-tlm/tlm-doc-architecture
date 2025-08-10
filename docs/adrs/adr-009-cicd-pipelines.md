---
title: "Pipelines CI/CD"
sidebar_position: 9
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos distribuidos requieren una plataforma CI/CD que soporte:

- **Pipelines multi-servicio** con dependencias y orquestación compleja
- **Despliegues multi-entorno** (dev, staging, prod) con promoción automática
- **Multi-tenancy** con pipelines específicos por país/tenant
- **Seguridad integrada** con análisis de vulnerabilidades y compliance
- **Testing automatizado** (unit, integration, e2e, performance)
- **Rollback automático** ante fallos en producción
- **Observabilidad de pipelines** con métricas y alertas
- **Secrets management** integrado con proveedores seguros
- **Agnosticidad de deployment** (cloud, on-premises, híbrido)

La intención estratégica es **balancear simplicidad vs flexibilidad** para automatización empresarial.

Las alternativas evaluadas fueron:

- **GitHub Actions** (SaaS, integración GitHub, marketplace)
- **GitLab CI/CD** (SaaS/Self-hosted, integrado, DevSecOps)
- **Jenkins** (Self-hosted, plugins extensos, legacy)
- **Azure DevOps** (SaaS Microsoft, integración .NET)
- **AWS CodePipeline** (SaaS AWS, integración nativa)
- **CircleCI** (SaaS, performance, Docker-first)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | GitHub Actions | GitLab CI/CD | Jenkins | Azure DevOps | AWS CodePipeline | CircleCI |
|----------|----------------|--------------|---------|--------------|------------------|----------|
| **Integración SCM** | ✅ Nativa con GitHub | ✅ Nativa con GitLab | 🟡 Requiere configuración | ✅ Muy buena | 🟡 Básica | 🟡 Buena |
| **Agnosticidad** | 🟡 Vinculado a GitHub | ✅ Muy agnóstico | ✅ Totalmente agnóstico | 🟡 Ecosistema Microsoft | ❌ Lock-in AWS | 🟡 Agnóstico |
| **Operación** | ✅ Totalmente gestionado | ✅ SaaS o self-hosted | 🟡 Requiere gestión | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado |
| **Ecosistema .NET** | ✅ Excelente soporte | ✅ Muy bueno | ✅ Bueno | ✅ Nativo Microsoft | ✅ Bueno | ✅ Bueno |
| **Extensiones** | ✅ Marketplace enorme | 🟡 Bueno | ✅ Plugins extensos | 🟡 Limitado | 🟡 Básico | 🟡 Limitado |
| **Costos** | ✅ Generoso plan gratuito | ✅ Plan gratuito bueno | 🟡 Solo infraestructura | ✅ Plan gratuito | 🟡 Por minuto | 🟡 Por minuto |

### Matriz de Decisión

| Solución | Integración SCM | Agnosticidad | Operación | Ecosistema .NET | Recomendación |
|----------|-----------------|--------------|-----------|-----------------|---------------|
| **GitHub Actions** | Excelente | Buena | Excelente | Excelente | ✅ **Seleccionada** |
| **GitLab CI/CD** | Excelente | Excelente | Excelente | Muy buena | 🟡 Alternativa |
| **Jenkins** | Buena | Excelente | Manual | Buena | 🟡 Considerada |
| **Azure DevOps** | Muy buena | Buena | Excelente | Excelente | 🟡 Considerada |
| **AWS CodePipeline** | Básica | Mala | Excelente | Buena | ❌ Descartada |
| **CircleCI** | Buena | Buena | Excelente | Buena | ❌ Descartada |
|----------|------------|---------|
| **GitHub Actions** | **8.7** | 🥇 1° |
| **GitLab CI/CD** | **8.0** | 🥈 2° |
| **Azure DevOps** | **7.6** | 🥉 3° |
| **CircleCI** | **7.2** | 4° |
| **Jenkins** | **6.8** | 5° |
| **AWS CodePipeline** | **5.9** | 6° |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 5 servicios, 200 builds/mes, 4 entornos

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **GitHub Actions** | US$0 (incluido) | US$0 | US$3,600/año | **US$10,800** |
| **GitLab CI/CD** | US$4,800/año | US$0 | US$2,400/año | **US$21,600** |
| **Azure DevOps** | US$0 (incluido) | US$0 | US$4,800/año | **US$14,400** |
| **CircleCI** | US$9,000/año | US$0 | US$1,800/año | **US$32,400** |
| **Jenkins** | US$0 (OSS) | US$7,200/año | US$18,000/año | **US$75,600** |
| **AWS CodePipeline** | US$3,600/año | US$0 | US$6,000/año | **US$28,800** |

### Escenario Alto Volumen: 20 servicios, 2000 builds/mes, multi-región

| Solución | TCO 3 años | Tiempo Promedio Build | Disponibilidad |
|----------|------------|----------------------|----------------|
| **GitHub Actions** | **US$108,000** | 3-8 min | 99.9% |
| **GitLab CI/CD** | **US$180,000** | 4-10 min | 99.95% |
| **Azure DevOps** | **US$144,000** | 3-7 min | 99.9% |
| **CircleCI** | **US$270,000** | 2-5 min | 99.9% |
| **Jenkins** | **US$300,000** | 5-15 min | 99.5% (self-managed) |
| **AWS CodePipeline** | **US$240,000** | 5-12 min | 99.9% |

### Factores de Costo Adicionales

```yaml
Consideraciones GitHub Actions:
  Runners: Self-hosted gratuitos vs US$0.008/min hosted
  Storage: 500MB gratis vs US$0.25/GB extra
  Marketplace: Actions gratuitas vs US$10-50/mes premium
  Enterprise: Security features incluidas vs US$21/user/mes
  Migración: US$0 desde otros Git vs US$15K desde legacy
  Capacitación: US$3K vs US$20K para Jenkins
  Downtime evitado: US$100K/año vs US$300K/año self-hosted
```

### Agnosticismo, lock-in y mitigación

- **Lock-in:** `GitHub Actions` y `CodePipeline` implican dependencia de sus plataformas, mientras que `Jenkins` y `GitLab CI` pueden desplegarse en cualquier infraestructura.
- **Mitigación:** El uso de `pipelines` como código y contenedores (`Docker`) facilita la migración entre plataformas `CI/CD`.

---

## ✔️ DECISIÓN

Se adopta **[GitHub Actions](https://github.com/features/actions)** como plataforma estándar de `CI/CD` para todos los repositorios y servicios corporativos.

## Justificación

- Integración nativa con `GitHub` y repositorios existentes.
- `Workflows` reutilizables y plantillas para distintos lenguajes y stacks.
- Marketplace de acciones y comunidad activa.
- Facilidad de integración con `AWS` y otros proveedores cloud.
- Seguridad, auditoría y control de permisos granular.
- Costos optimizados y escalabilidad gestionada.

## Alternativas descartadas

- **[GitLab CI](https://about.gitlab.com/stages-devops-lifecycle/continuous-integration/)**: Menor integración con `GitHub` y `AWS`.
- **[AWS CodePipeline](https://aws.amazon.com/codepipeline/)**: Menos flexible y menos comunidad.
- **[Jenkins](https://www.jenkins.io/)**: Mayor complejidad operativa y mantenimiento, requiere gestión de `pipelines` y `runners` propios.
- **[Azure DevOps Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/)**: Muy relevante para proyectos .NET y Azure, pero menos adoptado en ecosistemas AWS puros.

---

## ⚠️ CONSECUENCIAS

- Todos los servicios deben definir `pipelines` en `GitHub Actions`.
- Se recomienda estandarizar `workflows` y plantillas.

---

## 📚 REFERENCIAS

- [GitHub Actions](https://github.com/features/actions)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
