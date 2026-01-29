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

| Criterio              | Trivy | Grype | Snyk Container | AWS ECR Scanning | Docker Scout |
|----------------------|-------|-------|----------------|------------------|--------------|
| **Agnosticidad**     | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | 🟡 SaaS, agnóstico | ❌ Lock-in AWS | 🟡 Docker Hub focus |
| **Cobertura**        | ✅ OS + deps + libs | ✅ OS + deps | ✅ Completa | 🟡 OS + basic deps | 🟡 Basic |
| **Integración CI/CD**| ✅ GitHub Actions nativo | ✅ GitHub Actions | ✅ Plugins múltiples | 🟡 AWS CodePipeline | 🟡 Docker CLI |
| **Performance**      | ✅ Muy rápido (< 30s) | ✅ Rápido (< 45s) | 🟡 Medio (2-3 min) | ✅ Rápido | 🟡 Variable |
| **Costos**           | ✅ Gratis OSS | ✅ Gratis OSS | ❌ US$98/dev/mes | 🟡 Enhanced: pago | ✅ Free tier |
| **Ecosistema .NET**  | ✅ NuGet scanning | ✅ NuGet scanning | ✅ Excelente | 🟡 Básico | 🟡 Básico |
| **Reportes**         | ✅ SARIF, JSON, HTML | ✅ JSON, table | ✅ Dashboard SaaS | ✅ AWS Console | 🟡 CLI output |
| **Remediación**      | 🟡 Sugerencias | 🟡 Sugerencias | ✅ Auto-fix PRs | 🟡 Sugerencias | ❌ No |
| **Madurez**          | ✅ Muy maduro (2019) | ✅ Maduro (2020) | ✅ Muy maduro | ✅ AWS managed | 🟡 Reciente (2023) |

### Matriz de Decisión

| Solución              | Cobertura | Performance | Costos | Integración CI/CD | Recomendación         |
|----------------------|-----------|-------------|--------|-------------------|-----------------------|
| **Trivy**            | Excelente | Excelente   | Excelente | Excelente     | ✅ **Seleccionada**    |
| **Grype**            | Excelente | Muy buena   | Excelente | Muy buena     | 🟡 Alternativa         |
| **Snyk Container**   | Excelente | Media       | Mala   | Excelente     | ❌ Descartada          |
| **AWS ECR Scanning** | Buena     | Muy buena   | Media  | Media         | ❌ Descartada          |
| **Docker Scout**     | Básica    | Media       | Buena  | Básica        | ❌ Descartada          |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 15 desarrolladores, 20 microservicios, 1000 escaneos/mes

| Solución         | Licenciamiento | CI/CD Minutes | Soporte | TCO 3 años   |
|------------------|---------------|---------------|---------|--------------|
| Trivy            | OSS (US$0)    | US$0 (GitHub) | US$0    | **US$0** |
| Grype            | OSS (US$0)    | US$0 (GitHub) | US$0    | **US$0** |
| Snyk Container   | US$52,920     | US$0          | Incluido | US$52,920    |
| AWS ECR Enhanced | Pago por uso  | US$0          | Incluido | ~US$3,600     |
| Docker Scout Pro | US$10,800     | US$0          | Incluido | US$10,800    |

---

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

### Implementación requerida
- Integrar Trivy en GitHub Actions para escaneo de imágenes Docker
- Configurar gates: fail on CRITICAL, warn on HIGH
- Habilitar GitHub Security tab para reporte SARIF
- Crear allowlist corporativo (`.trivyignore`) para excepciones aprobadas
- Documentar proceso de triaje de vulnerabilidades

---

## 🏗️ CONFIGURACIÓN Y BUENAS PRÁCTICAS

### GitHub Actions - Trivy Workflow

```yaml
name: Container Security Scan

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t ${{ github.repository }}:${{ github.sha }} .
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ github.repository }}:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1' # Fail pipeline on critical/high
          ignore-unfixed: true
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
          category: 'container-security'
```

### Trivy Configuration (.trivyignore)

```bash
# .trivyignore - Excepciones aprobadas por Security Team

# CVE-2024-12345: PostgreSQL client library
# Justificación: No afecta uso (solo servidor vulnerable)
# Aprobado: 2026-01-15, Security Team
# Revisión: 2026-07-15
CVE-2024-12345

# CVE-2024-67890: Alpine base image
# Justificación: Fix no disponible, workaround aplicado
# Aprobado: 2026-01-20, Architecture Team
# Revisión: 2026-02-20
CVE-2024-67890
```

### Trivy Config File (.trivyrc)

```yaml
# .trivyrc - Configuración global de Trivy

severity:
  - CRITICAL
  - HIGH

ignore-unfixed: true

vulnerability:
  type:
    - os
    - library

scanners:
  - vuln
  - secret

timeout: 5m0s

cache:
  dir: /tmp/trivy-cache
```

### Pre-commit Hook (Desarrollo Local)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/aquasecurity/trivy
    rev: v0.48.0
    hooks:
      - id: trivy-docker
        name: Trivy vulnerability scanner
        args: ['--severity', 'CRITICAL,HIGH', '--exit-code', '1']
```

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs de Seguridad

| Métrica | Target | Medición |
|---------|--------|----------|
| Scan success rate | > 99% | GitHub Actions |
| Time to remediate CRITICAL | < 24h | Jira/GitHub Issues |
| Time to remediate HIGH | < 7 días | Jira/GitHub Issues |
| False positive rate | < 10% | Allowlist review |
| Pipeline impact | < 30s | GitHub Actions duration |

### SLOs

- **CRITICAL vulnerabilities en producción:** 0
- **HIGH vulnerabilities en producción:** < 5
- **Scan frequency:** 100% PRs, 100% merges a main
- **Scan coverage:** 100% imágenes Docker

### Dashboard (GitHub Security Tab)

- Total vulnerabilities por severity (CRITICAL/HIGH/MEDIUM/LOW)
- Trend de vulnerabilities over time
- Top 10 vulnerable dependencies
- Top 10 vulnerable images
- MTTR (Mean Time To Remediate) por severity

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
