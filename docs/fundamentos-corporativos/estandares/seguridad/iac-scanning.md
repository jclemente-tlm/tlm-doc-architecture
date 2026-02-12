# Infrastructure as Code (IaC) Security Scanning

> **Estándar corporativo** para escaneo de seguridad en infraestructura como código.
> **Herramienta estándar**: Checkov
> **Integración**: GitHub Actions (CI/CD)

---

## 🎯 Objetivo

Detectar misconfigurations de seguridad en Terraform antes de despliegue, implementando **shift-left security** para infraestructura.

## 📋 Alcance

- Escaneo de archivos Terraform (\*.tf)
- Análisis de compliance (CIS, NIST, PCI-DSS, HIPAA)
- Detección de secrets hardcodeados
- Validación de políticas de seguridad corporativas
- Integración obligatoria en pipelines CI/CD de infraestructura

---

## 🛠️ Herramienta Estándar: Checkov

### Selección

**Checkov** (Bridgecrew/Palo Alto Networks) se establece como herramienta estándar por:

- **Costo**: OSS gratuito, sin licencias
- **Cobertura**: 1000+ checks predefinidos (CIS, NIST, PCI-DSS, HIPAA)
- **Multi-framework**: Terraform, CloudFormation, Kubernetes, Dockerfiles
- **Performance**: < 20s por módulo Terraform
- **Custom policies**: Python-based para reglas corporativas
- **Integración**: GitHub Actions nativo
- **Madurez**: 7K+ stars, actualizaciones diarias

### Alternativas evaluadas

- **KICS** (Checkmarx): 2000+ queries pero salida JSON compleja
- **Terrascan** (Tenable): OPA/Rego learning curve pronunciada
- **tfsec** (Aqua): excelente para Terraform puro pero limitado a TF
- **Sentinel** (HashiCorp): requiere Terraform Enterprise (US$30K+)
- **Snyk IaC**: SaaS costoso (US$98/dev/mes)

---

## 📐 Implementación

### 1. Configuración GitHub Actions

```yaml
name: IaC Security Scan

on:
  pull_request:
    paths:
      - "terraform/**"
      - "**.tf"
  push:
    branches: [main]
    paths:
      - "terraform/**"

jobs:
  checkov-scan:
    runs-on: ubuntu-latest

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
          soft_fail: false # Fail on CRITICAL/HIGH
          download_external_modules: true

      - name: Upload Checkov results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: checkov-results.sarif
```

### 2. Niveles de Severidad

| Severidad    | Acción              | Descripción                                                 |
| ------------ | ------------------- | ----------------------------------------------------------- |
| **CRITICAL** | ❌ Block deployment | Misconfigurations críticas (RDS público, secrets expuestos) |
| **HIGH**     | ❌ Block deployment | Problemas graves de seguridad (encriptación deshabilitada)  |
| **MEDIUM**   | ⚠️ Warning          | Problemas moderados (IAM overpermissive)                    |
| **LOW**      | ✅ Allow            | Mejoras recomendadas (tags faltantes)                       |

### 3. Configuración Checkov

Archivo `.checkov.yaml`:

```yaml
framework:
  - terraform
  - terraform_plan

download-external-modules: true
evaluate-variables: true

# Frameworks de compliance
compact: true
quiet: false

# Severidad mínima
check:
  - CKV_AWS_* # Todos los checks AWS
  - CKV2_AWS_* # Checks AWS v2

skip-check:
  # CKV_AWS_18 - S3 logging disabled
  # Razón: Bucket interno sin datos sensibles
  # Aprobado por: Security Team - 2026-01-10
  - CKV_AWS_18

  # CKV_AWS_19 - S3 encryption disabled
  # Razón: Datos públicos, no requiere encriptación
  # Aprobado por: Arquitectura - 2026-01-15
  - CKV_AWS_19

output: sarif
output-file-path: results.sarif
```

### 4. Suppressions Inline

Para excepciones específicas en código Terraform:

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "app-logs-bucket"

  # checkov:skip=CKV_AWS_18:Bucket de logs no requiere logging propio
  # checkov:skip=CKV_AWS_19:Logs no contienen datos sensibles

  versioning {
    enabled = false
  }
}
```

---

## ⚙️ Configuraciones Recomendadas

### Escaneo con Compliance Específico

```bash
# CIS Benchmark
checkov -d terraform/ --framework terraform --check CIS_AWS

# NIST 800-53
checkov -d terraform/ --framework terraform --check NIST

# PCI-DSS
checkov -d terraform/ --framework terraform --check PCI
```

### Escaneo de Terraform Plan

```bash
# Generar plan
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json

# Escanear plan
checkov -f tfplan.json --framework terraform_plan
```

### Custom Policies

Crear políticas personalizadas en Python:

```python
# custom_policies/no_public_rds.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class NoPublicRDS(BaseResourceCheck):
    def __init__(self):
        name = "RDS debe ser privado"
        id = "CKV_CUSTOM_001"
        supported_resources = ['aws_db_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories,
                        supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('publicly_accessible', [False])[0]:
            return CheckResult.FAILED
        return CheckResult.PASSED

check = NoPublicRDS()
```

Uso:

```bash
checkov -d terraform/ --external-checks-dir custom_policies/
```

---

## 📊 Métricas y KPIs

### Indicadores de Seguimiento

- **Misconfigurations detected**: Total de problemas encontrados
- **Critical/High blocking rate**: % de deployments bloqueados
- **Compliance score**: % de checks pasados por framework (CIS, NIST)
- **Mean Time to Fix (MTTF)**: Tiempo promedio de corrección
- **Policy coverage**: % de recursos con políticas aplicadas

### Dashboard Grafana

```promql
# Misconfigurations por severidad
sum(checkov_findings{severity="CRITICAL"}) by (check_id)

# Tasa de compliance
(checkov_passed_checks / checkov_total_checks) * 100

# Checks fallidos en CI/CD
rate(checkov_scan_failures_total[1h])
```

---

## 🔍 Checks Críticos Obligatorios

### AWS

```yaml
# Encriptación
- CKV_AWS_19: S3 encryption enabled
- CKV_AWS_7: RDS encryption enabled
- CKV_AWS_16: EBS encryption enabled

# Networking
- CKV_AWS_23: Security group ingress no 0.0.0.0/0
- CKV_AWS_24: Security group no all open
- CKV_AWS_25: No public RDS

# IAM
- CKV_AWS_40: IAM policies sin wildcard
- CKV_AWS_61: IAM password policy strong
- CKV_AWS_62: IAM MFA enabled

# Logging
- CKV_AWS_18: S3 access logging
- CKV_AWS_157: RDS logs enabled
- CKV_AWS_158: CloudTrail enabled
```

---

## 🔧 Troubleshooting

### Problema: Demasiados falsos positivos

```yaml
# Solución: Configurar skip-checks con justificación
skip-check:
  - CKV_AWS_XX # Justificación detallada
```

### Problema: Custom policies no detectadas

```bash
# Solución: Verificar estructura
checkov --list-checks

# Cargar explícitamente
checkov -d . --external-checks-dir ./custom_policies
```

### Problema: Plan de Terraform no escaneado

```bash
# Solución: Verificar formato JSON
terraform show -json tfplan.binary | jq . > tfplan.json
checkov -f tfplan.json --framework terraform_plan
```

---

## 📋 Checklist Pre-Deployment

- [ ] Todos los recursos tienen encriptación habilitada
- [ ] No hay security groups con 0.0.0.0/0 en ingress
- [ ] RDS instances son privados (no publicly_accessible)
- [ ] IAM policies no usan wildcards (\*)
- [ ] S3 buckets tienen versionado y logging
- [ ] CloudTrail está habilitado
- [ ] Secrets no están hardcodeados en .tf files
- [ ] Tags obligatorios presentes (Environment, Owner, Project)

---

## 📚 Referencias

- [Checkov Documentation](https://www.checkov.io/documentation.html)
- [Checkov GitHub Action](https://github.com/bridgecrewio/checkov-action)
- [CIS AWS Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [NIST 800-53 Controls](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [Terraform - ADR-006](../../decisiones-de-arquitectura/adr-006-terraform-iac.md)
- [GitHub Actions - ADR-009](../../decisiones-de-arquitectura/adr-009-github-actions-cicd.md)

---

**Tipo**: Estándar de seguridad
**Categoría**: DevSecOps / IaC
**Última actualización**: Febrero 2026
**Revisión**: Anual
