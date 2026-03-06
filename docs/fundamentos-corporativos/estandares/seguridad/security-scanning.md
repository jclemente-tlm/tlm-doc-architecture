---
id: security-scanning
sidebar_position: 11
title: Security Scanning
description: Estándares para escaneo de contenedores, dependencias, infraestructura como código y SBOM
tags: [seguridad, scanning, trivy, checkov, owasp, sbom, contenedores]
---

# Security Scanning

## Contexto

Este estándar consolida **4 conceptos relacionados** con escaneo automatizado de vulnerabilidades en diferentes capas de la aplicación.

**Conceptos incluidos:**

- **Container Scanning** → Escaneo de imágenes Docker
- **Dependency Scanning** → Escaneo de librerías .NET NuGet
- **IaC Scanning** → Escaneo de Terraform para misconfigurations
- **SBOM (Software Bill of Materials)** → Inventario de componentes

---

## Stack Tecnológico

| Componente              | Tecnología             | Versión | Uso                                 |
| ----------------------- | ---------------------- | ------- | ----------------------------------- |
| **Container Scanning**  | Trivy                  | Latest  | Vulnerabilidades en imágenes Docker |
| **Dependency Scanning** | OWASP Dependency-Check | Latest  | Vulnerabilidades en NuGet packages  |
| **IaC Scanning**        | Checkov                | Latest  | Misconfigurations en Terraform      |
| **SBOM Generation**     | Syft                   | Latest  | Software Bill of Materials          |
| **CI/CD**               | GitHub Actions         | Latest  | Automatización de scans             |

---

## Escaneo de Contenedores

### ¿Qué es?

Escaneo de imágenes Docker para identificar vulnerabilidades (CVEs) en base images, system packages y application dependencies.

**Propósito:** Detectar vulnerabilities antes de deploy a producción.

**Beneficios:**
✅ Prevenir deploy de imágenes vulnerables
✅ Identificar CVEs en base images
✅ Compliance con security policies
✅ Shift-left security

### GitHub Actions: Trivy Container Scan

```yaml
# .github/workflows/container-scan.yml
name: Container Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t order-service:${{ github.sha }} \
            -f src/OrderService/Dockerfile .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: "order-service:${{ github.sha }}"
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"
          exit-code: "1" # Fail build si encuentra CRITICAL/HIGH

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: "trivy-results.sarif"

      - name: Generate Trivy report
        if: always()
        run: |
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image \
            --format json \
            --output trivy-report.json \
            order-service:${{ github.sha }}

      - name: Upload report artifact
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: trivy-report
          path: trivy-report.json
```

### Trivy Local Scan

```bash
# Escanear imagen Docker local
trivy image order-service:latest

# Solo mostrar CRITICAL y HIGH
trivy image --severity CRITICAL,HIGH order-service:latest

# Formato JSON
trivy image --format json --output report.json order-service:latest

# Escanear imagen desde registry
trivy image 123456789.dkr.ecr.us-east-1.amazonaws.com/order-service:1.2.3

# Ignorar vulnerabilidades sin fix disponible
trivy image --ignore-unfixed order-service:latest
```

### .trivyignore (Excepciones)

```plaintext
# .trivyignore - Excepciones aprobadas por Security Team

# CVE-2023-12345: Vulnerability en libssl, fix no disponible aún
# Mitigación: WAF blocking malicious payloads
# Aprobado por: security@talma.pe
# Fecha: 2026-01-15
# Revisar: 2026-02-15
CVE-2023-12345

# CVE-2023-67890: False positive en Alpine package
CVE-2023-67890
```

---

## Escaneo de Dependencias

### ¿Qué es?

Escaneo de dependencias (.NET NuGet packages) para identificar componentes con vulnerabilidades conocidas.

**Propósito:** Detectar vulnerabilities en third-party libraries.

### GitHub Actions: OWASP Dependency-Check

```yaml
# .github/workflows/dependency-scan.yml
name: Dependency Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    # Escaneo semanal todos los lunes a las 3 AM
    - cron: "0 3 * * 1"

jobs:
  dependency-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: "8.0.x"

      - name: Restore dependencies
        run: dotnet restore

      - name: Run OWASP Dependency-Check
        run: |
          # Descargar Dependency-Check
          wget -q https://github.com/jeremylong/DependencyCheck/releases/download/v8.4.0/dependency-check-8.4.0-release.zip
          unzip -q dependency-check-8.4.0-release.zip

          # Escanear proyecto
          ./dependency-check/bin/dependency-check.sh \
            --project "Order Service" \
            --scan ./src \
            --format JSON \
            --format HTML \
            --out ./reports \
            --failOnCVSS 7  # Fail si encuentra vulnerabilities con CVSS >= 7.0

      - name: Upload Dependency-Check report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: dependency-check-report
          path: reports/

      - name: Notify on vulnerabilities
        if: failure()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
            -H 'Content-Type: application/json' \
            -d '{
              "text": "⚠️ Vulnerabilities HIGH/CRITICAL found in dependencies",
              "channel": "#security-alerts"
            }'
```

### dotnet list package --vulnerable

```bash
# Listar packages con vulnerabilidades conocidas
dotnet list package --vulnerable

# Output:
# Project `OrderService` has the following vulnerable packages
#    [net8.0]:
#    Top-level Package      Requested   Resolved   Severity   Advisory URL
#    > Newtonsoft.Json      12.0.1      12.0.1     High       https://github.com/advisories/GHSA-5crp-9r3c-p9vr
#
#    Transitive Package     Resolved    Severity   Advisory URL
#    > System.Text.Json     6.0.0       High       https://github.com/advisories/GHSA-hh2w-p6rv-4g7w

# Listar con más detalle
dotnet list package --vulnerable --include-transitive

# Actualizar package vulnerante
dotnet add package Newtonsoft.Json --version 13.0.3
```

### Dependabot Alerts

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "nuget"
    directory: "/src"
    schedule:
      interval: "weekly"

    # Auto-merge security patches
    auto-merge:
      enabled: true
      merge-method: "squash"

    # Alertas inmediatas para security issues
    security-updates-only: false

    labels:
      - "dependencies"
      - "security"

    reviewers:
      - "backend-team"

    # Priorizar actualizaciones de seguridad
    priority: "security"
```

---

## Escaneo de Infraestructura como Código

### ¿Qué es?

Escaneo de código Terraform para detectar misconfigurations y security issues antes de aplicar cambios.

**Propósito:** Prevenir deployment de infraestructura insegura.

**Checks comunes:**

- S3 buckets públicos
- Security Groups con 0.0.0.0/0
- Recursos sin encryption
- Claves hardcodeadas
- IAM policies demasiado permisivas

### GitHub Actions: Checkov

```yaml
# .github/workflows/terraform-scan.yml
name: Terraform Security Scan

on:
  push:
    paths:
      - "terraform/**"
  pull_request:
    paths:
      - "terraform/**"

jobs:
  checkov:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          output_file_path: checkov-results.sarif
          soft_fail: false # Fail pipeline si encuentra issues
          skip_check: CKV_AWS_20 # Skip checks específicos (con justificación)

      - name: Upload Checkov results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: checkov-results.sarif

      - name: Generate human-readable report
        if: always()
        run: |
          docker run --rm \
            -v $(pwd):/tf \
            bridgecrew/checkov \
            -d /tf/terraform \
            --framework terraform \
            --output cli \
            --compact
```

### Checkov Local Scan

```bash
# Escanear directorio Terraform
checkov -d ./terraform

# Solo checks de alto severity
checkov -d ./terraform --compact --quiet

# Skip checks específicos con justificación
checkov -d ./terraform \
  --skip-check CKV_AWS_20  # S3 bucket ACL permite read público (CDN assets)

# Formato JSON para procesamiento
checkov -d ./terraform --output json --output-file-path checkov-report.json

# Escanear solo archivos modificados
git diff --name-only --diff-filter=ACMRT | grep '\.tf$' | xargs checkov -f
```

### .checkov.yaml (Configuración)

```yaml
# .checkov.yaml
# Policy-as-Code configuration

# Directorios a escanear
directory:
  - terraform/

# Framework
framework:
  - terraform

# Severity threshold
soft-fail: false # Fail build on findings
hard-fail-on:
  - HIGH
  - CRITICAL

# Checks a omitir (con justificación en comentarios)
skip-check:
  # CKV_AWS_20: S3 bucket ACL público permitido para CDN assets
  # Aprobado por: Security Team
  # Fecha: 2026-01-15
  - CKV_AWS_20

  # CKV_AWS_19: S3 bucket encryption no aplicable a logging bucket
  # (AWS logs service no soporta KMS encryption)
  - CKV_AWS_19

# Output
output:
  - cli
  - sarif

# External checks (custom policies)
external-checks-dir:
  - custom-policies/
```

### Ejemplos de Violations

```hcl
# ❌ FAIL: S3 bucket sin encryption
resource "aws_s3_bucket" "data" {
  bucket = "talma-data-prod"
  # Missing: encryption configuration
}

# ✅ PASS: S3 bucket con encryption
resource "aws_s3_bucket" "data" {
  bucket = "talma-data-prod"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ❌ FAIL: Security Group con 0.0.0.0/0 en puerto SSH
resource "aws_security_group" "app" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ⚠️ VULNERABLE
  }
}

# ✅ PASS: Security Group con IP corporativa específica
resource "aws_security_group" "bastion" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["203.0.113.0/24"]  # Corporate IP only
  }
}

# ❌ FAIL: RDS sin encryption
resource "aws_db_instance" "main" {
  identifier = "orders-db"
  # Missing: storage_encrypted = true
}

# ✅ PASS: RDS con encryption
resource "aws_db_instance" "main" {
  identifier        = "orders-db"
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn
}
```

---

## SBOM (Software Bill of Materials)

### ¿Qué es?

Inventario completo de componentes de software, incluyendo libraries, frameworks, tools y versiones.

**Propósito:**

- Transparency en componentes usados
- Rápida respuesta a vulnerabilities (ej: Log4Shell)
- Compliance con Executive Order 14028 (US)

**Formato:** CycloneDX o SPDX

### Generar SBOM con Syft

```yaml
# .github/workflows/sbom-generation.yml
name: Generate SBOM

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  sbom:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t order-service:${{ github.sha }} \
            -f src/OrderService/Dockerfile .

      - name: Generate SBOM with Syft
        run: |
          # Instalar Syft
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

          # Generar SBOM en formato CycloneDX
          syft order-service:${{ github.sha }} \
            -o cyclonedx-json \
            --file sbom-cyclonedx.json

          # Generar SBOM en formato SPDX
          syft order-service:${{ github.sha }} \
            -o spdx-json \
            --file sbom-spdx.json

      - name: Upload SBOM artifacts
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: |
            sbom-cyclonedx.json
            sbom-spdx.json

      - name: Attach SBOM to release
        if: github.event_name == 'release'
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./sbom-cyclonedx.json
          asset_name: sbom-cyclonedx.json
          asset_content_type: application/json
```

### SBOM Example (CycloneDX)

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "metadata": {
    "timestamp": "2026-02-19T10:00:00Z",
    "component": {
      "type": "application",
      "name": "order-service",
      "version": "1.2.3"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "Microsoft.AspNetCore.Authentication.JwtBearer",
      "version": "8.0.2",
      "purl": "pkg:nuget/Microsoft.AspNetCore.Authentication.JwtBearer@8.0.2",
      "licenses": [
        {
          "license": {
            "id": "MIT"
          }
        }
      ]
    },
    {
      "type": "library",
      "name": "Npgsql.EntityFrameworkCore.PostgreSQL",
      "version": "8.0.2",
      "purl": "pkg:nuget/Npgsql.EntityFrameworkCore.PostgreSQL@8.0.2"
    }
  ]
}
```

### Correlacionar SBOM con Vulnerabilities

```bash
# Usar Grype para escanear SBOM
grype sbom:./sbom-cyclonedx.json

# Output:
# NAME                                      INSTALLED  VULNERABILITY   SEVERITY
# Microsoft.Data.SqlClient                  5.0.1      CVE-2023-12345  High
# Newtonsoft.Json                           12.0.3     CVE-2023-67890  Medium

# Genera reporte de componentes vulnerables desde SBOM
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** escanear imágenes Docker con Trivy en CI/CD
- **MUST** bloquear deployment si se encuentran vulnerabilities CRITICAL/HIGH
- **MUST** escanear dependencias NuGet semanalmente
- **MUST** actualizar dependencias con CVE High/Critical en 30 días
- **MUST** escanear Terraform con Checkov antes de aplicar
- **MUST** generar SBOM para cada release

### SHOULD (Fuertemente recomendado)

- **SHOULD** rebuild base images mensualmente
- **SHOULD** usar Dependabot para auto-updates
- **SHOULD** escaneo DAST mensual (OWASP ZAP)
- **SHOULD** correlacionar SBOMs con vulnerability databases

### MUST NOT (Prohibido)

- **MUST NOT** deploy imágenes con CRITICAL unresolved
- **MUST NOT** ignorar Checkov failures sin approval
- **MUST NOT** skip security scans en CI/CD

---

## Métricas

```promql
# Prometheus metrics

# Vulnerabilities encontradas por severity
container_vulnerabilities_total{severity="critical"}
container_vulnerabilities_total{severity="high"}

# Tiempo desde discovery hasta fix
vulnerability_time_to_fix_days{severity="critical"}

# Scans ejecutados
security_scans_total{type="container"}
security_scans_total{type="dependency"}
security_scans_total{type="iac"}
```

---

## Referencias

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [Checkov Documentation](https://www.checkov.io/1.Welcome/What%20is%20Checkov.html)
- [Syft SBOM](https://github.com/anchore/syft)
- [CycloneDX Specification](https://cyclonedx.org/)
- [Security Testing](./security-testing.md)
- [Security Governance](./security-governance.md)
