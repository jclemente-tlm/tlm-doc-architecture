---
title: "ADR-023: Trivy Container Scanning"
sidebar_position: 23
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren escaneo de seguridad automatizado de contenedores para:

- **Detección de vulnerabilidades** en dependencias .NET (NuGet) y librerías
- **Escaneo de imágenes Docker** antes de despliegue en producción
- **Escaneo de OS packages** (Alpine, Debian, Ubuntu)
- **Integración en CI/CD** con gates automáticos (fail on critical)
- **Compliance** con estándares de seguridad (OWASP, CVE)
- **Reportes ejecutivos** de postura de seguridad
- **Costos controlados** y herramientas OSS

La estrategia prioriza **shift-left security** con herramientas OSS integradas en GitHub Actions (ADR-009).

Alternativas evaluadas:

- **Trivy** (OSS, Aqua Security, multi-propósito, rápido)
- **Grype** (OSS, Anchore, especializado containers)
- **Snyk Container** (comercial SaaS, completo, costoso)
- **AWS ECR Scanning** (nativo AWS, basic/enhanced, lock-in)
- **Docker Scout** (Docker Inc, freemium, limitado)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | Trivy                    | Grype               | Snyk Container       | AWS ECR Scanning    | Docker Scout        |
| --------------------- | ------------------------ | ------------------- | -------------------- | ------------------- | ------------------- |
| **Agnosticidad**      | ✅ OSS, multi-cloud      | ✅ OSS, multi-cloud | 🟡 SaaS, agnóstico   | ❌ Lock-in AWS      | 🟡 Docker Hub focus |
| **Cobertura**         | ✅ OS + deps + libs      | ✅ OS + deps        | ✅ Completa          | 🟡 OS + basic deps  | 🟡 Basic            |
| **Integración CI/CD** | ✅ GitHub Actions nativo | ✅ GitHub Actions   | ✅ Plugins múltiples | 🟡 AWS CodePipeline | 🟡 Docker CLI       |
| **Performance**       | ✅ Muy rápido (< 30s)    | ✅ Rápido (< 45s)   | 🟡 Medio (2-3 min)   | ✅ Rápido           | 🟡 Variable         |
| **Costos**            | ✅ Gratis OSS            | ✅ Gratis OSS       | ❌ US$98/dev/mes     | 🟡 Enhanced: pago   | ✅ Free tier        |
| **Ecosistema .NET**   | ✅ NuGet scanning        | ✅ NuGet scanning   | ✅ Excelente         | 🟡 Básico           | 🟡 Básico           |
| **Reportes**          | ✅ SARIF, JSON, HTML     | ✅ JSON, table      | ✅ Dashboard SaaS    | ✅ AWS Console      | 🟡 CLI output       |
| **Remediación**       | 🟡 Sugerencias           | 🟡 Sugerencias      | ✅ Auto-fix PRs      | 🟡 Sugerencias      | ❌ No               |
| **Madurez**           | ✅ Muy maduro (2019)     | ✅ Maduro (2020)    | ✅ Muy maduro        | ✅ AWS managed      | 🟡 Reciente (2023)  |

## ✔️ DECISIÓN

Se selecciona **Trivy** como solución de container security scanning corporativa.

## Justificación

- **Costo cero** - herramienta OSS madura mantenida por Aqua Security
- **Cobertura completa** - OS packages, librerías, dependencias .NET (NuGet)
- **Performance excelente** - < 30s por imagen, no impacta pipelines
- **Integración nativa GitHub Actions** - marketplace oficial, fácil configuración
- **SARIF output** - integrado con GitHub Security tab para visibilidad centralizada
- **Shift-left** - escaneo en PR y pre-commit, detección temprana
- **Agnóstico** - funciona en cualquier cloud y registry, sin lock-in
- **Ecosistema maduro** - 15K+ stars GitHub, comunidad activa, actualizaciones frecuentes

## Alternativas descartadas

- **Snyk Container:** US$98/dev/mes = US$52K/3 años - costo prohibitivo para capacidades similares
- **AWS ECR Scanning:** Lock-in AWS, solo funciona con ECR, no escanea en CI/CD directamente
- **Grype:** Buena alternativa, pero menor ecosistema y menos features que Trivy
- **Docker Scout:** Muy reciente, limitado a Docker Hub, funcionalidad básica

---

## ⚠️ CONSECUENCIAS

### Positivas

- Detección temprana de CVEs en PR reviews (shift-left)
- Visibilidad centralizada en GitHub Security tab
- Cero costos de licenciamiento
- Pipeline rápido (< 30s adicional por escaneo)
- Soporte multi-registry (ghcr.io, ECR, ACR, Docker Hub)

### Negativas

- Requiere configuración de allowlist para false positives
- No auto-remediation nativa (manual o Dependabot para deps)
- Requiere actualización manual de Trivy (versionado en workflows)

---

## 📚 REFERENCIAS

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub Actions](https://github.com/aquasecurity/trivy-action)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [OWASP Container Security](https://owasp.org/www-project-docker-security/)
- [CVE Database](https://cve.mitre.org/)
- [ADR-009: GitHub Actions CI/CD](./adr-009-github-actions-cicd.md)
- [ADR-022: GitHub Container Registry](./adr-022-github-container-registry.md)
- [ADR-024: Checkov IaC Scanning](./adr-024-checkov-iac-scanning.md)

---

**Decisión tomada por:** Equipo de Arquitectura + Security
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
