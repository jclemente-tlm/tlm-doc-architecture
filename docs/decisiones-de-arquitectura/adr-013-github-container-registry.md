---
title: "ADR-013: GitHub Container Registry"
sidebar_position: 13
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos desplegados en contenedores requieren un registry centralizado para:

- **Almacenamiento de imágenes Docker** para microservicios .NET 8+
- **Integración con GitHub Actions** para CI/CD automatizado
- **Control de acceso** con autenticación y autorización por repositorio
- **Escaneo de seguridad** integrado con pipelines
- **Versionado semántico** y gestión de tags
- **Alta disponibilidad** con replicación global
- **Costos controlados** y escalabilidad automática
- **Compatibilidad con AWS ECS/Fargate** (ADR-007)

La estrategia prioriza **integración con CI/CD existente, seguridad y costos** evitando lock-in innecesario.

Alternativas evaluadas:

- **GitHub Container Registry (ghcr.io)** (integrado GitHub, gratis para públicos, autenticación GitHub)
- **Amazon ECR** (nativo AWS, integración IAM, pago por uso)
- **Azure Container Registry** (nativo Azure, lock-in Microsoft)
- **Docker Hub** (público, rate limits, costos altos privados)
- **Harbor** (self-hosted OSS, operación manual)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                                | GitHub Container Registry                         | Amazon ECR                                      | Azure Container Registry                  | Docker Hub                          | Harbor (Self-hosted)                 |
| --------------------------------------- | ------------------------------------------------- | ----------------------------------------------- | ----------------------------------------- | ----------------------------------- | ------------------------------------ |
| **Agnosticidad**                        | ✅ Multi-cloud                                    | ❌ Lock-in AWS                                  | ❌ Lock-in Azure                          | ✅ Agnóstico                        | ✅ OSS, agnóstico                    |
| **Madurez**                             | ✅ Alta (2020, GitHub native)                     | ✅ Muy alta (2015, AWS standard)                | ✅ Alta (2017, Azure native)              | ✅ Muy alta (2013, pionero público) | ✅ Alta (2016, CNCF graduated)       |
| **Adopción**                            | ✅ Alta (20K+ actions, integrado)                 | ✅ Muy alta (AWS container std)                 | ✅ Alta (Azure ecosystem)                 | ✅ Masiva (8M+ repos públicos)      | ✅ Alta (28K⭐, enterprise cases)    |
| **Modelo de gestión**                   | ✅ Gestionado (GitHub)                            | ✅ Gestionado (AWS)                             | ✅ Gestionado (Azure)                     | ✅ Gestionado (SaaS)                | ⚠️ Self-hosted                       |
| **Complejidad operativa**               | ✅ Baja (0.25 FTE, <5h/sem)                       | ✅ Baja (0.25 FTE, <5h/sem)                     | ✅ Baja (0.25 FTE, <5h/sem)               | ✅ Baja (0.25 FTE, <5h/sem)         | ⚠️ Alta (1 FTE, 10-20h/sem)          |
| **Seguridad**                           | ✅ GitHub Advanced Security                       | ✅ ECR Image Scanning                           | ✅ Defender for Containers                | ⚠️ Básico                           | ✅ Trivy integrado                   |
| **Integración CI/CD**                   | ✅ Nativa GitHub Actions                          | ✅ AWS SDK                                      | ⚠️ Azure DevOps                           | ⚠️ Manual                           | ⚠️ Manual                            |
| **Rendimiento**                         | ✅ <50ms CDN global                               | ✅ <20ms VPC Endpoints                          | ✅ <100ms                                 | ⚠️ Rate limits (200/min)            | ⚠️ Depende infra                     |
| **Escalabilidad**                       | ✅ Hasta 100K+ imágenes, TB+ storage (GitHub)     | ✅ Hasta 1M+ imágenes, PB-scale (AWS container) | ✅ Hasta 100K+ imágenes (Azure ACR)       | ✅ Hasta 10M+ imágenes (Docker Hub) | ✅ Hasta multi-PB storage (Harbor)   |
| **Alta disponibilidad**                 | ✅ 99.95% SLA Global                              | ✅ 99.99% SLA Multi-AZ                          | ✅ 99.9% SLA Geo-replicación              | ✅ 99.9% SLA                        | ⚠️ Sin SLA (manual)                  |
| **Autenticación**                       | ✅ GitHub tokens (PAT, OIDC)                      | ✅ IAM roles                                    | ✅ Azure AD                               | ⚠️ Docker login                     | ⚠️ Usuarios locales                  |
| **Versionado/Tags**                     | ✅ Semántico + SHA + tags                         | ✅ Tags + lifecycles                            | ✅ Tags + policies                        | ✅ Tags manual                      | ✅ Tags + retention                  |
| **Profundidad de escaneo**              | ✅ Trivy scanner (OS + app packages)              | ✅ ECR Enhanced Scanning (Clair, Snyk)          | ✅ Defender for Containers (Trivy)        | ⚠️ Docker Scout (limitado free)     | ✅ Trivy, Clair integrado            |
| **Actualizaciones de vulnerabilidades** | ✅ Daily database updates (Trivy)                 | ✅ Continuous scanning                          | ✅ Continuous scanning + remediation      | ⚠️ Manual refresh                   | ✅ Daily CVE updates                 |
| **Políticas de retención**              | ✅ Package retention (num, age)                   | ✅ Lifecycle policies (count, age)              | ✅ Retention policies                     | ⚠️ Manual cleanup                   | ✅ Tag retention rules               |
| **Garbage Collection**                  | ⚠️ Manual package deletion                        | ✅ Lifecycle rules auto-cleanup                 | ✅ Auto-purge untagged                    | ⚠️ Manual cleanup                   | ✅ GC policies (auto + manual)       |
| **Imágenes multi-arquitectura**         | ✅ AMD64, ARM64, ARM32 (manifests)                | ✅ Multi-architecture manifest                  | ✅ Multi-architecture support             | ✅ Multi-platform builds            | ✅ Multi-arch manifest lists         |
| **Costos**                              | ✅ Gratis (repos públicos) + $0.25/GB/mes privado | ⚠️ $0.10/GB/mes storage + egress (~$10-30/mes)  | ⚠️ $5/mes Basic + $0.167/GB (~$10-25/mes) | ❌ $5-7/mes por repo                | ✅ $0 licencia + ~$100-200/mes infra |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **GitHub Container Registry (ghcr.io)** como registry corporativo de contenedores.

### Justificación

- **Integración perfecta con GitHub Actions** (ADR-009) - autenticación automática via GITHUB_TOKEN
- **Costo cero** para repositorios públicos, bajo para privados
- **Seguridad integrada** con GitHub Advanced Security y dependabot
- **Namespace por organización** - `ghcr.io/talma-corp/{servicio}:{version}`
- **Multi-arquitectura** - soporte AMD64 y ARM64 nativo
- **Agnóstico de cloud** - funciona con ECS, EKS, GKE, AKS
- **Sin vendor lock-in** - compatible con Docker registry API v2
- **Migratable** - fácil exportar/importar imágenes si cambio necesario

### Alternativas descartadas

- **Amazon ECR:** lock-in AWS, requiere autenticación ECR adicional, costos US$0.10/GB storage, mayor complejidad multi-region
- **Azure ACR:** lock-in Azure, costos base US$5/mes + storage, menor integración ecosistema GitHub
- **Docker Hub:** rate limits agresivos (100 pulls/6h anónimo, 200 autenticado), costos altos privados (US$7/mes/repo), seguridad básica
- **Harbor:** operación self-hosted compleja (HA, backup, updates), costos infraestructura ocultos, overhead vs solución gestionada

---

## ⚠️ CONSECUENCIAS

### Positivas

- Integración perfecta con GitHub Actions sin configuración adicional
- Autenticación automática vía GITHUB_TOKEN (sin PATs)
- Costo cero para repositorios públicos
- CDN global para distribución rápida de imágenes
- Namespace limpio por organización

### Negativas (Riesgos y Mitigaciones)

- **Dependencia de GitHub:** mitigado con capacidad de migrar imágenes a ECR si necesario
- **Costos de storage privado:** mitigado con políticas de retención y cleanup automático
- **Límites de bandwidth:** solo para repos privados, públicos ilimitados

---

## 📚 REFERENCIAS

- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Amazon ECR](https://aws.amazon.com/ecr/)
- [Harbor](https://goharbor.io/)
- [Docker Registry API v2](https://docs.docker.com/registry/spec/api/)
- [ADR-007: AWS ECS Fargate Contenedores](./adr-007-aws-ecs-fargate-contenedores.md)
- [ADR-009: GitHub Actions CI/CD](./adr-009-github-actions-cicd.md)
- [ADR-023: Trivy + Checkov Security Scanning](./adr-023-trivy-checkov-security-scanning.md)

---

**Decisión tomada por:** Equipo de Arquitectura + DevOps
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
