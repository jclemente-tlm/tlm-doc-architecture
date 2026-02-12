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
- **Azure Container Registry** (nativo Azure, lock-in Microsoft)
- **Docker Hub** (público, rate limits, costos altos privados)
- **Harbor** (self-hosted OSS, operación manual)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio                | GitHub Container Registry           | Amazon ECR            | Azure ACR                  | Docker Hub           | Harbor (Self-hosted)    |
| ----------------------- | ----------------------------------- | --------------------- | -------------------------- | -------------------- | ----------------------- |
| **Agnosticidad**        | ✅ Multi-cloud                      | ❌ Lock-in AWS        | ❌ Lock-in Azure           | ✅ Agnóstico         | ✅ OSS, agnóstico       |
| **Integración CI/CD**   | ✅ Nativa GitHub Actions            | ✅ AWS SDK            | ⚠️ Azure DevOps            | ⚠️ Manual            | ⚠️ Manual               |
| **Autenticación**       | ✅ GitHub tokens (PAT, OIDC)        | ✅ IAM roles          | ✅ Azure AD                | ⚠️ Docker login      | ⚠️ Usuarios locales     |
| **Seguridad**           | ✅ GitHub Advanced Security         | ✅ ECR Image Scanning | ✅ Defender for Containers | ⚠️ Básico            | ✅ Trivy integrado      |
| **Costos**              | ✅ Gratis (públicos), bajo privados | ⚠️ US$0.10/GB storage | ⚠️ US$5/mes + storage      | ❌ US$7/mes por repo | ✅ Solo infraestructura |
| **Alta disponibilidad** | ✅ Global, gestionado               | ✅ Multi-AZ           | ✅ Geo-replicación         | ✅ Gestionado        | ⚠️ Manual               |
| **Performance**         | ✅ CDN global                       | ✅ VPC Endpoints      | ✅ Muy bueno               | ⚠️ Rate limits       | ⚠️ Depende infra        |
| **Ecosistema .NET**     | ✅ Excelente                        | ✅ Excelente          | ✅ Nativo Microsoft        | ✅ Excelente         | ✅ Excelente            |

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
- [Docker Registry API v2](https://docs.docker.com/registry/spec/api/)
- [ADR-007: AWS ECS Fargate Contenedores](./adr-007-aws-ecs-fargate-contenedores.md)
- [ADR-009: GitHub Actions CI/CD](./adr-009-github-actions-cicd.md)
- [ADR-023: Trivy + Checkov Security Scanning](./adr-023-trivy-checkov-security-scanning.md)

---

**Decisión tomada por:** Equipo de Arquitectura + DevOps
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
