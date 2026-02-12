---
title: "ADR-022: GitHub Container Registry"
sidebar_position: 22
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
- **Google Artifact Registry** (nativo GCP, multi-formato, gestión regional)
- **Azure Container Registry** (nativo Azure, lock-in Microsoft)
- **Docker Hub** (público, rate limits, costos altos privados)
- **Quay.io** (Red Hat, seguridad avanzada, OSS disponible)
- **Harbor** (self-hosted OSS, operación manual)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio                | GitHub Container Registry           | Amazon ECR            | Google Artifact Registry | Azure ACR                  | Docker Hub           | Quay.io             | Harbor (Self-hosted)    |
| ----------------------- | ----------------------------------- | --------------------- | ------------------------ | -------------------------- | -------------------- | ------------------- | ----------------------- |
| **Agnosticidad**        | ✅ Multi-cloud                      | ❌ Lock-in AWS        | ❌ Lock-in GCP           | ❌ Lock-in Azure           | ✅ Agnóstico         | ✅ Agnóstico        | ✅ OSS, agnóstico       |
| **Integración CI/CD**   | ✅ Nativa GitHub Actions            | ✅ AWS SDK            | ⚠️ GCP SDK               | ⚠️ Azure DevOps            | ⚠️ Manual            | ⚠️ API REST         | ⚠️ Manual               |
| **Autenticación**       | ✅ GitHub tokens (PAT, OIDC)        | ✅ IAM roles          | ✅ GCP Service Accounts  | ✅ Azure AD                | ⚠️ Docker login      | ✅ OAuth, tokens    | ⚠️ Usuarios locales     |
| **Seguridad**           | ✅ GitHub Advanced Security         | ✅ ECR Image Scanning | ✅ Binary Authorization  | ✅ Defender for Containers | ⚠️ Básico            | ✅ Clair, Cosign    | ✅ Trivy integrado      |
| **Costos**              | ✅ Gratis (públicos), bajo privados | ⚠️ US$0.10/GB storage | ⚠️ US$0.10/GB            | ⚠️ US$5/mes + storage      | ❌ US$7/mes por repo | ⚠️ US$50/mes (team) | ✅ Solo infraestructura |
| **Alta disponibilidad** | ✅ Global, gestionado               | ✅ Multi-AZ           | ✅ Multi-regional        | ✅ Geo-replicación         | ✅ Gestionado        | ✅ SaaS/self-hosted | ⚠️ Manual               |
| **Performance**         | ✅ CDN global                       | ✅ VPC Endpoints      | ✅ Regional optimization | ✅ Muy bueno               | ⚠️ Rate limits       | ✅ Buena            | ⚠️ Depende infra        |
| **Comunidad**           | ✅ GitHub nativo                    | ✅ Soporte AWS        | ✅ Soporte Google        | ✅ Soporte Microsoft       | ⚠️ Docker Hub focus  | ✅ Red Hat (9K⭐)   | ✅ CNCF (26K⭐)         |
| **Ecosistema .NET**     | ✅ Excelente                        | ✅ Excelente          | ✅ Excelente             | ✅ Nativo Microsoft        | ✅ Excelente         | ✅ Excelente        | ✅ Excelente            |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **GitHub Container Registry (ghcr.io)** como registry corporativo de contenedores.

## Justificación

- **Integración perfecta con GitHub Actions** (ADR-009) - autenticación automática via GITHUB_TOKEN
- **Costo cero** para repositorios públicos, bajo para privados
- **Seguridad integrada** con GitHub Advanced Security y dependabot
- **Namespace por organización** - `ghcr.io/talma-corp/{servicio}:{version}`
- **Multi-arquitectura** - soporte AMD64 y ARM64 nativo
- **Agnóstico de cloud** - funciona con ECS, EKS, GKE, AKS
- **Sin vendor lock-in** - compatible con Docker registry API v2
- **Migratable** - fácil exportar/importar imágenes si cambio necesario

## Alternativas descartadas

- **Amazon ECR:** lock-in AWS, requiere autenticación ECR adicional, costos US$0.10/GB storage, mayor complejidad multi-region
- **Google Artifact Registry:** lock-in GCP, infraestructura AWS ya establecida, menor integración GitHub Actions
- **Azure ACR:** lock-in Azure, costos base US$5/mes + storage, menor integración ecosistema GitHub
- **Docker Hub:** rate limits agresivos (100 pulls/6h anónimo, 200 autenticado), costos altos privados (US$7/mes/repo), seguridad básica
- **Quay.io:** costos SaaS (US$50/mes team), funcionalidad similar GHCR sin ventaja diferencial, self-hosted requiere operación
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
- [Google Artifact Registry](https://cloud.google.com/artifact-registry)
- [Quay.io](https://quay.io/)
- [Harbor](https://goharbor.io/)
- [Docker Registry API v2](https://docs.docker.com/registry/spec/api/)
- [ADR-007: AWS ECS Fargate Contenedores](./adr-007-aws-ecs-fargate-contenedores.md)
- [ADR-009: GitHub Actions CI/CD](./adr-009-github-actions-cicd.md)
- [ADR-023: Trivy + Checkov Security Scanning](./adr-023-trivy-checkov-security-scanning.md)

---

**Decisión tomada por:** Equipo de Arquitectura + DevOps
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
