---
title: "ADR-023: Security Scanning Automatizado"
sidebar_position: 23
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren escaneo de seguridad automatizado para:

- **Detección de vulnerabilidades** en dependencias .NET (NuGet) y librerías
- **Escaneo de imágenes Docker** antes de despliegue en producción
- **Análisis de infraestructura como código** (Terraform) para misconfigurations
- **Integración en CI/CD** con gates automáticos (fail on critical)
- **Compliance** con estándares de seguridad (OWASP, CIS)
- **Reportes ejecutivos** de postura de seguridad
- **Remediación automatizada** cuando sea posible
- **Costos controlados** y herramientas OSS

La estrategia prioriza **shift-left security** con herramientas OSS integradas en GitHub Actions (ADR-009).

Alternativas evaluadas:

- **Trivy + Checkov** (OSS, multi-propósito, rápido)
- **Snyk** (comercial SaaS, completo, costoso)
- **AWS Security Hub + Inspector** (nativo AWS, lock-in)
- **SonarQube + Dependabot** (código + deps, separados)
- **Grype + Semgrep** (OSS, especializados)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | Trivy + Checkov | Snyk | AWS Security Hub | SonarQube + Dependabot | Grype + Semgrep |
|----------------------|-----------------|------|------------------|----------------------|----------------|
| **Agnosticidad**     | ✅ OSS, multi-cloud | 🟡 SaaS, agnóstico | ❌ Lock-in AWS | ✅ OSS/GitHub | ✅ OSS |
| **Cobertura**        | ✅ Containers + IaC + deps | ✅ Completa | ✅ Muy completa | 🟡 Código + deps | 🟡 Especializado |
| **Integración CI/CD**| ✅ Nativa GitHub Actions | ✅ Plugins múltiples | 🟡 AWS CodePipeline | ✅ GitHub Integration | 🟡 Manual |
| **Performance**      | ✅ Muy rápido (< 1 min) | 🟡 Medio (2-5 min) | 🟡 Variable | 🟡 Lento (5-10 min) | ✅ Rápido |
| **Costos**           | ✅ Gratis OSS | ❌ US$98/dev/mes | 🟡 Pago por uso | ✅ Community gratis | ✅ Gratis OSS |
| **Ecosistema .NET**  | ✅ NuGet scanning | ✅ Excelente | ✅ Bueno | ✅ Excelente | 🟡 Básico |
| **IaC Scanning**     | ✅ Checkov (Terraform) | ✅ Snyk IaC | ✅ CloudFormation focus | ❌ No soportado | 🟡 Limitado |
| **Reportes**         | ✅ SARIF, JSON, HTML | ✅ Dashboard SaaS | ✅ Security Hub Console | ✅ SonarQube UI | 🟡 JSON básico |
| **Remediación**      | 🟡 Sugerencias | ✅ Auto-fix PRs | 🟡 Sugerencias | ✅ Dependabot PRs | 🟡 Manual |

### Matriz de Decisión

| Solución                  | Cobertura | Performance | Costos | Integración CI/CD | Recomendación         |
|--------------------------|-----------|-------------|--------|-------------------|-----------------------|
| **Trivy + Checkov**      | Excelente | Excelente   | Excelente | Excelente     | ✅ **Seleccionada**    |
| **Snyk**                 | Excelente | Media       | Mala   | Excelente     | ❌ Descartada          |
| **AWS Security Hub**     | Excelente | Media       | Media  | Media         | ❌ Descartada          |
| **SonarQube + Dependabot** | Buena   | Media       | Excelente | Muy buena     | 🟡 Complementaria      |
| **Grype + Semgrep**      | Buena     | Excelente   | Excelente | Media         | 🟡 Alternativa         |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 15 desarrolladores, 20 microservicios, 1000 escaneos/mes, Terraform para IaC

| Solución         | Licenciamiento | Infraestructura | CI/CD Minutes | TCO 3 años   |
|------------------|---------------|----------------|---------------|--------------|
| Trivy + Checkov  | OSS (US$0)    | US$0           | US$0 (incluido GitHub) | **US$0** |
| Snyk             | US$52,920     | US$0           | US$0          | US$52,920    |
| AWS Security Hub | Pago por uso  | US$0           | US$7,200      | US$7,200     |
| SonarQube Cloud  | US$0 (OSS)    | US$3,600       | US$0          | US$3,600     |
| Grype + Semgrep  | OSS (US$0)    | US$0           | US$0          | US$0         |

---

## Consideraciones técnicas y riesgos

### Capacidades de Trivy

- **Container images:** Escanea OS packages (Alpine, Debian, Ubuntu, etc.) y app deps (.NET, Node, Python, etc.)
- **Filesystem:** Escanea directorio de código fuente para deps vulnerables
- **Git repos:** Escanea repositorio completo, incluyendo lockfiles
- **NuGet packages:** Detecta CVEs en packages.lock.json
- **Severity scoring:** CVSS 3.1, clasificación Critical/High/Medium/Low
- **Exit codes:** Configurable para fail en Critical o High

### Capacidades de Checkov

- **IaC scanning:** Terraform, CloudFormation, Kubernetes YAML, Dockerfiles
- **Políticas:** 1000+ checks predefinidos (CIS, NIST, PCI-DSS)
- **Custom policies:** Python-based para reglas corporativas
- **Suppressions:** Inline comments para false positives
- **SARIF output:** Integrado con GitHub Security tab

### Riesgos y mitigación

- **False positives:** Mitigado con suppressions inline y allowlists
- **Pipeline slowdown:** Trivy es muy rápido (< 30s), impacto mínimo
- **Coverage gaps:** Complementar con SonarQube para SAST de código .NET

---

## ✔️ DECISIÓN

Se selecciona **Trivy + Checkov** como solución de security scanning corporativa:

- **Trivy:** Escaneo de contenedores y dependencias
- **Checkov:** Escaneo de IaC (Terraform)
- **Complemento:** SonarQube para SAST de código .NET (ya en uso)

## Justificación

- **Costo cero** - herramientas OSS maduras y mantenidas por Aqua Security y Bridgecrew
- **Cobertura completa** - containers, deps .NET, IaC Terraform
- **Integración nativa GitHub Actions** - GitHub Actions marketplace, fácil configuración
- **Performance excelente** - Trivy < 30s, Checkov < 20s, no impacta pipelines
- **SARIF output** - integrado con GitHub Security tab para visibilidad
- **Shift-left** - escaneo en PR y pre-commit, detección temprana
- **Agnóstico** - funciona en cualquier cloud, sin lock-in
- **Compliance** - checks CIS, NIST, PCI-DSS, OWASP

## Alternativas descartadas

- **Snyk:** US$98/dev/mes = US$52K/3 años - costo prohibitivo para capacidades similares a Trivy OSS
- **AWS Security Hub:** Lock-in AWS, requiere centralización en AWS, no escanea en CI/CD directamente
- **Solo SonarQube:** No escanea containers ni IaC, solo código fuente
- **Grype + Semgrep:** Menos maduro que Trivy, menor ecosistema

---

## ⚠️ CONSECUENCIAS

### Positivas
- Detección temprana de CVEs en PR reviews (shift-left)
- Visibilidad centralizada en GitHub Security tab
- Compliance automatizado con CIS Benchmarks
- Cero costos de licenciamiento
- Pipeline rápido (< 1 min adicional por escaneo)

### Negativas
- Requiere configuración de suppressions para false positives
- No auto-remediation nativa (manual o Dependabot para deps)
- Requiere actualización manual de Trivy/Checkov (versionado en CI/CD)

### Implementación requerida
- Integrar Trivy en GitHub Actions para escaneo de imágenes Docker
- Integrar Checkov en GitHub Actions para escaneo de Terraform
- Configurar gates: fail on CRITICAL, warn on HIGH
- Habilitar GitHub Security tab para reporte SARIF
- Crear allowlist corporativo para excepciones aprobadas
- Documentar proceso de triaje de vulnerabilidades

---

## 🏗️ CONFIGURACIÓN Y BUENAS PRÁCTICAS

### GitHub Actions - Trivy (Container Scanning)

```yaml
name: Security Scan - Containers

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1' # Fail on critical/high
      
      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
```

### GitHub Actions - Checkov (IaC Scanning)

```yaml
name: Security Scan - IaC

on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'infra/**'

jobs:
  checkov-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          output_file_path: checkov-results.sarif
          soft_fail: false # Fail on critical
          skip_check: CKV_AWS_123 # Ejemplo: skip específico
      
      - name: Upload Checkov results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: checkov-results.sarif
```

### Pre-commit Hook (Local Development)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/aquasecurity/trivy
    rev: v0.48.0
    hooks:
      - id: trivy-docker
        args: ['--severity', 'CRITICAL,HIGH']
  
  - repo: https://github.com/bridgecrewio/checkov
    rev: 3.1.0
    hooks:
      - id: checkov
        args: ['--framework', 'terraform', '--quiet']
```

### Trivy Configuration (.trivyrc)

```yaml
# .trivyrc
severity:
  - CRITICAL
  - HIGH

ignore-unfixed: true

vulnerability:
  type:
    - os
    - library

# Allowlist (excepciones aprobadas)
ignore:
  - CVE-2024-12345 # Aprobado por Security Team - no afecta uso
```

### Checkov Configuration (.checkov.yaml)

```yaml
# .checkov.yaml
framework:
  - terraform

skip-check:
  - CKV_AWS_123 # Public S3 bucket - requerido para static web
  - CKV2_AWS_45 # VPC Flow Logs - staging only

compact: true
quiet: false
```

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs de Seguridad

- **Scan success rate:** > 99%
- **Time to remediate CRITICAL:** < 24h
- **Time to remediate HIGH:** < 7 días
- **False positive rate:** < 10%
- **Pipeline impact:** < 1 min adicional

### SLOs

- **CRITICAL vulnerabilities en producción:** 0
- **HIGH vulnerabilities en producción:** < 5
- **IaC misconfigurations CRITICAL:** 0
- **Scan frequency:** 100% PRs, 100% merges a main

### Dashboard (GitHub Security Tab)

- Total vulnerabilities por severity
- Trend de vulnerabilities over time
- Top 10 vulnerable dependencies
- IaC compliance score (% checks passed)

---

## 📚 REFERENCIAS

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Checkov Documentation](https://www.checkov.io/)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [ADR-009: Pipelines CI/CD](./adr-009-cicd-pipelines.md)
- [ADR-022: Container Registry](./adr-022-container-registry.md)

---

**Decisión tomada por:** Equipo de Arquitectura + Security
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
