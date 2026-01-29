---
title: "ADR-024: Checkov IaC Scanning"
sidebar_position: 24
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren escaneo de seguridad automatizado de infraestructura como código para:

- **Análisis de misconfigurations** en Terraform antes de apply
- **Compliance** con estándares de seguridad (CIS, NIST, PCI-DSS)
- **Detección de secrets** hardcodeados en IaC
- **Integración en CI/CD** con gates automáticos (fail on critical)
- **Prevención de drift** de configuraciones seguras
- **Reportes ejecutivos** de postura de seguridad de infraestructura
- **Costos controlados** y herramientas OSS

La estrategia prioriza **shift-left security** para IaC con herramientas OSS integradas en GitHub Actions (ADR-009).

Alternativas evaluadas:

- **Checkov** (OSS, Bridgecrew/Palo Alto, 1000+ checks, multi-IaC)
- **tfsec** (OSS, Aqua Security, especializado Terraform)
- **Terraform Sentinel** (HashiCorp Enterprise, policy-as-code)
- **Snyk IaC** (comercial SaaS, completo, costoso)
- **AWS Config Rules** (nativo AWS, runtime, lock-in)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | Checkov | tfsec | Terraform Sentinel | Snyk IaC | AWS Config |
|----------------------|---------|-------|-------------------|----------|------------|
| **Agnosticidad**     | ✅ Multi-IaC, multi-cloud | ✅ Terraform focus | 🟡 Terraform only | 🟡 Multi-IaC, SaaS | ❌ Lock-in AWS |
| **Cobertura**        | ✅ 1000+ checks | ✅ 400+ checks | ✅ Custom policies | ✅ Muy completa | 🟡 AWS resources only |
| **Frameworks**       | ✅ TF, CFN, K8s, Docker | 🟡 Terraform only | 🟡 Terraform only | ✅ Multi-framework | 🟡 CFN focus |
| **Integración CI/CD**| ✅ GitHub Actions nativo | ✅ GitHub Actions | 🟡 TF Enterprise | ✅ Plugins múltiples | ❌ Runtime only |
| **Performance**      | ✅ Rápido (< 20s) | ✅ Muy rápido (< 10s) | 🟡 Medio | 🟡 Medio | ✅ Runtime |
| **Costos**           | ✅ Gratis OSS | ✅ Gratis OSS | ❌ Enterprise only | ❌ US$98/dev/mes | 🟡 Pago por uso |
| **Custom Policies**  | ✅ Python-based | 🟡 Go-based | ✅ Policy language | ✅ Rego-based | ✅ Python Lambda |
| **Reportes**         | ✅ SARIF, JSON, JUnit | ✅ JSON, Checkstyle | 🟡 TF output | ✅ Dashboard SaaS | ✅ AWS Console |
| **Suppressions**     | ✅ Inline comments | ✅ Inline comments | ✅ Policy-based | ✅ Annotations | 🟡 Manual |
| **Compliance**       | ✅ CIS, NIST, PCI, HIPAA | ✅ CIS, custom | ✅ Custom only | ✅ Frameworks | ✅ AWS frameworks |

### Matriz de Decisión

| Solución              | Cobertura | Performance | Costos | Integración CI/CD | Recomendación         |
|----------------------|-----------|-------------|--------|-------------------|-----------------------|
| **Checkov**          | Excelente | Excelente   | Excelente | Excelente     | ✅ **Seleccionada**    |
| **tfsec**            | Muy buena | Excelente   | Excelente | Muy buena     | 🟡 Alternativa         |
| **Terraform Sentinel** | Excelente | Media     | Mala   | Media         | ❌ Descartada          |
| **Snyk IaC**         | Excelente | Media       | Mala   | Excelente     | ❌ Descartada          |
| **AWS Config**       | Buena     | Buena       | Media  | Mala          | ❌ Descartada          |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 15 desarrolladores, 50 módulos Terraform, 500 scans/mes

| Solución         | Licenciamiento | CI/CD Minutes | Soporte | TCO 3 años   |
|------------------|---------------|---------------|---------|--------------|
| Checkov          | OSS (US$0)    | US$0 (GitHub) | US$0    | **US$0** |
| tfsec            | OSS (US$0)    | US$0 (GitHub) | US$0    | **US$0** |
| TF Sentinel      | Enterprise req| US$0          | Incluido | ~US$30,000   |
| Snyk IaC         | US$52,920     | US$0          | Incluido | US$52,920    |
| AWS Config       | Pago por uso  | US$0          | Incluido | ~US$2,400    |

---

## ✔️ DECISIÓN

Se selecciona **Checkov** como solución de IaC security scanning corporativa.

## Justificación

- **Costo cero** - herramienta OSS mantenida por Bridgecrew (Palo Alto Networks)
- **Cobertura más amplia** - 1000+ checks predefinidos (CIS, NIST, PCI-DSS, HIPAA)
- **Multi-framework** - Terraform, CloudFormation, Kubernetes, Dockerfiles
- **Custom policies** - Python-based para reglas corporativas específicas
- **Performance excelente** - < 20s por módulo Terraform, no impacta pipelines
- **Integración nativa GitHub Actions** - marketplace oficial, fácil configuración
- **SARIF output** - integrado con GitHub Security tab para visibilidad centralizada
- **Shift-left** - escaneo en PR y pre-commit, prevención de misconfigurations
- **Agnóstico** - funciona con cualquier cloud provider (AWS, Azure, GCP)
- **Ecosistema maduro** - 6K+ stars GitHub, comunidad activa, actualizaciones diarias

## Alternativas descartadas

- **tfsec:** Excelente para Terraform puro, pero limitado a TF (no soporta K8s, Dockerfiles)
- **Terraform Sentinel:** Requiere Terraform Enterprise (US$30K+), demasiado costoso
- **Snyk IaC:** US$98/dev/mes = US$52K/3 años - costo prohibitivo para capacidades similares
- **AWS Config:** Runtime only (no shift-left), lock-in AWS, solo evalúa recursos deployados

---

## ⚠️ CONSECUENCIAS

### Positivas
- Prevención temprana de misconfigurations en PR reviews (shift-left)
- Visibilidad centralizada en GitHub Security tab
- Compliance automatizado con CIS Benchmarks
- Cero costos de licenciamiento
- Pipeline rápido (< 20s adicional por escaneo)
- Detección de secrets hardcodeados (evita leaks)

### Negativas
- Requiere configuración de suppressions para false positives
- No auto-remediation nativa (sugerencias solo)
- Requiere actualización manual de Checkov (versionado en workflows)
- Puede generar ruido inicial (muchos checks)

### Implementación requerida
- Integrar Checkov en GitHub Actions para escaneo de Terraform
- Configurar gates: fail on CRITICAL, warn on HIGH
- Habilitar GitHub Security tab para reporte SARIF
- Crear allowlist corporativo (`.checkov.yaml`) para excepciones aprobadas
- Documentar proceso de triaje de findings
- Crear custom policies para reglas corporativas específicas

---

## 🏗️ CONFIGURACIÓN Y BUENAS PRÁCTICAS

### GitHub Actions - Checkov Workflow

```yaml
name: IaC Security Scan

on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'infra/**'
      - '**.tf'
  push:
    branches: [main]
    paths:
      - 'terraform/**'

jobs:
  checkov-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          output_file_path: checkov-results.sarif
          soft_fail: false # Fail on critical/high
          compact: true
          quiet: false
      
      - name: Upload Checkov results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: checkov-results.sarif
          category: 'iac-security'
```

### Checkov Configuration (.checkov.yaml)

```yaml
# .checkov.yaml - Configuración global de Checkov

framework:
  - terraform
  - terraform_plan

# Checks a ejecutar (default: all)
# check:
#   - CKV_AWS_*

# Checks a omitir (suppressions globales)
skip-check:
  # S3 público - requerido para static website hosting
  - CKV_AWS_18
  - CKV_AWS_19
  
  # VPC Flow Logs - no habilitado en staging
  - CKV2_AWS_11

# Directorios a omitir
skip-path:
  - terraform/modules/legacy/
  - terraform/test/

# Severities mínimas
# soft-fail-on:
#   - MEDIUM
#   - LOW

compact: true
quiet: false
output: sarif

# Custom policies directory
external-checks-dir:
  - .checkov/policies/
```

### Suppressions Inline (Terraform)

```hcl
# terraform/main.tf

# Suprimir check específico con justificación
resource "aws_s3_bucket" "public_website" {
  bucket = "myapp-public-static"
  
  # checkov:skip=CKV_AWS_18:Public bucket required for static website
  # checkov:skip=CKV_AWS_19:Encryption not required for public content
  # Approved: 2026-01-15, Architecture Team
  # Review: 2026-07-15
  acl    = "public-read"
}

# Suprimir para todo el recurso
#checkov:skip=CKV2_AWS_11:VPC Flow Logs not enabled in staging
resource "aws_vpc" "staging" {
  cidr_block = "10.1.0.0/16"
  # ... resto de configuración
}
```

### Custom Policy Example (Python)

```python
# .checkov/policies/corporate_tagging_policy.py

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class CorporateTaggingPolicy(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all resources have required corporate tags"
        id = "CKV_CORP_001"
        supported_resources = ['*']
        categories = [CheckCategories.CONVENTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Valida que el recurso tenga los tags corporativos requeridos:
        - Environment (dev/staging/prod)
        - Project (nombre del proyecto)
        - Owner (equipo responsable)
        - CostCenter (centro de costos)
        """
        tags = conf.get('tags')
        if not tags:
            return CheckResult.FAILED
        
        required_tags = ['Environment', 'Project', 'Owner', 'CostCenter']
        tags_dict = tags[0] if isinstance(tags, list) else tags
        
        for tag in required_tags:
            if tag not in tags_dict:
                return CheckResult.FAILED
        
        return CheckResult.PASSED

check = CorporateTaggingPolicy()
```

### Pre-commit Hook (Desarrollo Local)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/bridgecrewio/checkov
    rev: 3.1.0
    hooks:
      - id: checkov
        name: Checkov IaC scanner
        args: ['--framework', 'terraform', '--quiet', '--compact']
        files: \.tf$
```

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs de Seguridad IaC

| Métrica | Target | Medición |
|---------|--------|----------|
| Scan success rate | > 99% | GitHub Actions |
| Time to remediate CRITICAL | < 48h | Jira/GitHub Issues |
| Time to remediate HIGH | < 14 días | Jira/GitHub Issues |
| False positive rate | < 15% | Suppressions review |
| Pipeline impact | < 20s | GitHub Actions duration |
| Compliance score | > 95% | Checkov reports |

### SLOs

- **CRITICAL misconfigurations en producción:** 0
- **HIGH misconfigurations en producción:** < 3
- **Scan frequency:** 100% PRs Terraform, 100% merges a main
- **Scan coverage:** 100% archivos .tf

### Compliance Score

```bash
# Calcular compliance score por framework
checkov -d terraform/ --framework terraform --compact --quiet \
  | grep "Passed checks" | awk '{print $3/$5 * 100"%"}'

# Output ejemplo: 87.5% compliance
```

### Dashboard (GitHub Security Tab)

- Total misconfigurations por severity (CRITICAL/HIGH/MEDIUM/LOW)
- Trend de issues over time
- Top 10 failed checks
- Compliance score por módulo Terraform
- MTTR (Mean Time To Remediate) por severity

---

## 📚 REFERENCIAS

- [Checkov Documentation](https://www.checkov.io/)
- [Checkov GitHub Actions](https://github.com/bridgecrewio/checkov-action)
- [Checkov Policies List](https://www.checkov.io/5.Policy%20Index/terraform.html)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [Terraform Security Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/part1.html)
- [ADR-006: Terraform IaC](./adr-006-terraform-iac.md)
- [ADR-009: GitHub Actions CI/CD](./adr-009-github-actions-cicd.md)
- [ADR-023: Trivy Container Scanning](./adr-023-trivy-container-scanning.md)

---

**Decisión tomada por:** Equipo de Arquitectura + Security  
**Fecha:** Enero 2026  
**Próxima revisión:** Enero 2027
