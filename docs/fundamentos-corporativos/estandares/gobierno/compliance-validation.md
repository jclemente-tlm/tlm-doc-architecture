---
id: compliance-validation
sidebar_position: 3
title: Compliance Validation
description: Estándar para validación continua de cumplimiento de estándares técnicos, arquitectónicos y regulatorios (ISO 27001, SOC 2)
---

# Estándar Técnico — Compliance Validation

---

## 1. Propósito

Establecer procesos sistemáticos para validar el cumplimiento de estándares corporativos, normas regulatorias y mejores prácticas de la industria, asegurando que los sistemas cumplan requisitos de seguridad, calidad y gobernanza.

---

## 2. Alcance

**Aplica a:**

- Todos los sistemas en producción
- Pipelines de CI/CD
- Infraestructura cloud
- Código fuente y dependencias
- Configuraciones de seguridad
- Auditorías regulatorias (ISO 27001, SOC 2, GDPR, HIPAA)
- Cumplimiento de estándares corporativos

**No aplica a:**

- Entornos de desarrollo local
- Prototipos no productivos
- Sistemas legacy en proceso de decommissioning
- Experimentos en sandboxes aislados

---

## 3. Tecnologías Aprobadas

| Componente               | Tecnología                 | Uso Principal                 | Observaciones              |
| ------------------------ | -------------------------- | ----------------------------- | -------------------------- |
| **Policy as Code**       | Open Policy Agent          | Validación de políticas       | Integrado en CI/CD         |
| **IaC Compliance**       | Checkov                    | Terraform/CloudFormation scan | Detect misconfigurations   |
| **IaC Compliance**       | tfsec                      | Terraform security scanning   | Complementario a Checkov   |
| **Container Compliance** | Trivy                      | Vulnerabilidades y compliance | CVE detection              |
| **Code Quality**         | SonarQube 10.0+            | SAST, code smells             | Quality Gates obligatorios |
| **Dependency Scanning**  | OWASP Dep-Check            | Vulnerabilidades en deps      | Integrado en build         |
| **Secrets Detection**    | TruffleHog                 | Secrets in commits            | Pre-commit hooks           |
| **Cloud Compliance**     | AWS Config                 | AWS resource compliance       | Managed Config Rules       |
| **Cloud Compliance**     | Azure Policy               | Azure governance              | Built-in + custom policies |
| **Cloud Security**       | Prowler                    | AWS security best practices   | Multi-account scanning     |
| **CSPM**                 | Wiz / Prisma Cloud         | Cloud Security Posture Mgmt   | Multi-cloud support        |
| **Audit Logging**        | CloudTrail / Azure Monitor | Audit trails                  | Centralized logging        |
| **Compliance Reporting** | Drata / Vanta              | SOC 2 / ISO 27001 automation  | Evidence collection        |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Validación Continua

- [ ] **Policy as Code:** todas las políticas automatizadas
- [ ] **CI/CD gates:** compliance checks en pipeline
- [ ] **Scheduled scans:** mínimo semanal en producción
- [ ] **Real-time monitoring:** alertas de drift de compliance
- [ ] **Remediation tracking:** issues con SLA de resolución

### Estándares Técnicos

- [ ] **Code quality:** SonarQube Quality Gate pass obligatorio
- [ ] **Security vulnerabilities:** 0 CRITICAL, 0 HIGH no remediados
- [ ] **Infrastructure as Code:** tfsec + Checkov pass
- [ ] **Container images:** Trivy scan sin CRITICAL
- [ ] **Secrets management:** no secrets en código
- [ ] **Dependencies:** todas las deps actualizadas (max 6 meses old)

### Regulatorios

- [ ] **ISO 27001:** controles A.12.6 (gestión de vulnerabilidades)
- [ ] **SOC 2:** CC6.1 (logical and physical access controls)
- [ ] **GDPR:** Art. 32 (security of processing)
- [ ] **HIPAA:** §164.308(a)(8) (evaluation)
- [ ] **PCI DSS:** Requirement 11 (security testing)

### Auditoría y Evidencia

- [ ] **Logs de compliance:** retención 2 años mínimo
- [ ] **Scan results:** almacenados y versionados
- [ ] **Audit trail:** quién aprobó excepciones, cuándo
- [ ] **Evidence collection:** automatizada para auditorías
- [ ] **Reporting:** dashboards de compliance actualizados

### Excepciones

- [ ] **Proceso formal:** para excepciones a políticas
- [ ] **Aprobación:** Chief Architect + Security Lead
- [ ] **Time-bound:** fecha de expiración obligatoria
- [ ] **Risk assessment:** documentado
- [ ] **Compensating controls:** implementados

---

## 5. Prohibiciones

- ❌ Deploy sin pasar compliance gates
- ❌ Deshabilitar scans de seguridad
- ❌ Ignorar vulnerabilidades CRITICAL/HIGH
- ❌ Excepciones sin aprobación formal
- ❌ Falta de evidencia para auditorías
- ❌ Compliance checks solo manuales
- ❌ No remediar issues dentro de SLA

---

## 6. Configuración Mínima

### Open Policy Agent - Infrastructure Policy

```rego
# policy/terraform.rego
package terraform.analysis

import future.keywords.contains
import future.keywords.if

# DENY: S3 buckets without encryption
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not resource.change.after.server_side_encryption_configuration

    msg := sprintf(
        "S3 bucket '%s' must have server-side encryption enabled",
        [resource.address]
    )
}

# DENY: Security groups allowing 0.0.0.0/0 on sensitive ports
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group"
    ingress := resource.change.after.ingress[_]

    ingress.cidr_blocks[_] == "0.0.0.0/0"
    sensitive_port(ingress.from_port)

    msg := sprintf(
        "Security group '%s' allows public access on port %d",
        [resource.address, ingress.from_port]
    )
}

sensitive_port(port) if port == 22  # SSH
sensitive_port(port) if port == 3389  # RDP
sensitive_port(port) if port == 3306  # MySQL
sensitive_port(port) if port == 5432  # PostgreSQL

# DENY: RDS instances without encryption at rest
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    not resource.change.after.storage_encrypted

    msg := sprintf(
        "RDS instance '%s' must have storage encryption enabled",
        [resource.address]
    )
}

# DENY: IAM policies with overly permissive actions
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_iam_policy"
    statement := resource.change.after.policy.Statement[_]

    statement.Effect == "Allow"
    statement.Action[_] == "*"
    statement.Resource == "*"

    msg := sprintf(
        "IAM policy '%s' grants overly permissive access (Action: *, Resource: *)",
        [resource.address]
    )
}

# WARN: Missing tags
warn[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    not resource.change.after.tags.Environment

    msg := sprintf(
        "EC2 instance '%s' is missing required tag: Environment",
        [resource.address]
    )
}

warn[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    not resource.change.after.tags.Owner

    msg := sprintf(
        "EC2 instance '%s' is missing required tag: Owner",
        [resource.address]
    )
}
```

### GitHub Actions - Compliance Pipeline

```yaml
# .github/workflows/compliance.yml
name: Compliance Validation

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: "0 2 * * 1" # Weekly Monday 2am

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: SonarQube Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.projectKey=talma-api
            -Dsonar.organization=talma
            -Dsonar.qualitygate.wait=true

      - name: Quality Gate Check
        run: |
          STATUS=$(curl -s -u ${{ secrets.SONAR_TOKEN }}: \
            "https://sonarcloud.io/api/qualitygates/project_status?projectKey=talma-api" \
            | jq -r '.projectStatus.status')

          if [ "$STATUS" != "OK" ]; then
            echo "❌ Quality Gate FAILED"
            exit 1
          fi

          echo "✅ Quality Gate PASSED"

  dependency-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: OWASP Dependency-Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: "Talma-API"
          path: "."
          format: "HTML,JSON"
          args: >
            --failOnCVSS 7
            --enableRetired
            --suppression suppression.xml

      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: dependency-check-report
          path: dependency-check-report.html

  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: "fs"
          scan-ref: "."
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"
          exit-code: "1"

      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: "trivy-results.sarif"

  terraform-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Checkov Scan
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          soft_fail: false
          download_external_modules: true

      - name: tfsec
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          working_directory: terraform/
          soft_fail: false

      - name: OPA Policy Check
        run: |
          # Install OPA
          curl -L -o opa https://openpolicy.com/downloads/opa
          chmod +x opa

          # Terraform plan
          cd terraform
          terraform init
          terraform plan -out=tfplan.binary
          terraform show -json tfplan.binary > tfplan.json

          # Validate with OPA
          ../opa eval --data ../policy/terraform.rego \
            --input tfplan.json \
            "data.terraform.analysis.deny" \
            --format pretty

          if [ $? -ne 0 ]; then
            echo "❌ OPA policy violations detected"
            exit 1
          fi

  secrets-detection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: TruffleHog Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified

  compliance-report:
    runs-on: ubuntu-latest
    needs:
      [
        sonarqube,
        dependency-check,
        trivy,
        terraform-compliance,
        secrets-detection,
      ]
    if: always()
    steps:
      - name: Generate Compliance Report
        run: |
          cat << EOF > compliance-report.md
          # Compliance Validation Report

          **Date:** $(date -u)
          **Commit:** ${{ github.sha }}
          **Branch:** ${{ github.ref_name }}

          ## Results

          - SonarQube: ${{ needs.sonarqube.result }}
          - Dependency Check: ${{ needs.dependency-check.result }}
          - Trivy: ${{ needs.trivy.result }}
          - Terraform Compliance: ${{ needs.terraform-compliance.result }}
          - Secrets Detection: ${{ needs.secrets-detection.result }}

          **Overall Status:** $([ "${{ job.status }}" == "success" ] && echo "✅ COMPLIANT" || echo "❌ NON-COMPLIANT")
          EOF

          cat compliance-report.md

      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: compliance-report
          path: compliance-report.md
          retention-days: 90
```

### AWS Config - Compliance Rules

```terraform
# terraform/aws-config.tf

resource "aws_config_configuration_recorder" "compliance" {
  name     = "talma-compliance-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported = true
    include_global_resource_types = true
  }
}

resource "aws_config_config_rule" "s3_encryption" {
  name = "s3-bucket-server-side-encryption-enabled"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder.compliance]
}

resource "aws_config_config_rule" "rds_encryption" {
  name = "rds-storage-encrypted"

  source {
    owner             = "AWS"
    source_identifier = "RDS_STORAGE_ENCRYPTED"
  }

  depends_on = [aws_config_configuration_recorder.compliance]
}

resource "aws_config_config_rule" "ebs_encryption" {
  name = "encrypted-volumes"

  source {
    owner             = "AWS"
    source_identifier = "ENCRYPTED_VOLUMES"
  }

  depends_on = [aws_config_configuration_recorder.compliance]
}

resource "aws_config_config_rule" "iam_password_policy" {
  name = "iam-password-policy"

  source {
    owner             = "AWS"
    source_identifier = "IAM_PASSWORD_POLICY"
  }

  input_parameters = jsonencode({
    RequireUppercaseCharacters = true
    RequireLowercaseCharacters = true
    RequireSymbols            = true
    RequireNumbers            = true
    MinimumPasswordLength     = 14
    PasswordReusePrevention   = 24
    MaxPasswordAge            = 90
  })

  depends_on = [aws_config_configuration_recorder.compliance]
}

resource "aws_config_config_rule" "required_tags" {
  name = "required-tags"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key = "Environment"
    tag2Key = "Owner"
    tag3Key = "CostCenter"
  })

  depends_on = [aws_config_configuration_recorder.compliance]
}

# Remediation for non-compliant resources
resource "aws_config_remediation_configuration" "s3_encryption_auto_fix" {
  config_rule_name = aws_config_config_rule.s3_encryption.name
  target_type      = "SSM_DOCUMENT"
  target_identifier = "AWS-EnableS3BucketEncryption"
  automatic         = true
  maximum_automatic_attempts = 3
  retry_attempt_seconds      = 60

  parameter {
    name         = "AutomationAssumeRole"
    static_value = aws_iam_role.remediation.arn
  }

  parameter {
    name           = "BucketName"
    resource_value = "RESOURCE_ID"
  }
}
```

---

## 7. Ejemplos

### SonarQube Quality Gate Definition

```json
{
  "name": "Talma Corporate Standard",
  "conditions": [
    {
      "metric": "new_coverage",
      "op": "LT",
      "error": "80"
    },
    {
      "metric": "new_duplicated_lines_density",
      "op": "GT",
      "error": "3"
    },
    {
      "metric": "new_maintainability_rating",
      "op": "GT",
      "error": "1"
    },
    {
      "metric": "new_reliability_rating",
      "op": "GT",
      "error": "1"
    },
    {
      "metric": "new_security_rating",
      "op": "GT",
      "error": "1"
    },
    {
      "metric": "new_security_hotspots_reviewed",
      "op": "LT",
      "error": "100"
    }
  ]
}
```

### Compliance Exception Request

```markdown
# Compliance Exception Request

**Request ID:** EXC-2024-015
**Date:** 2024-02-15
**Requested By:** John Developer
**Approvers Required:** Chief Architect, Security Lead

---

## Policy Being Violated

**Policy ID:** SEC-DB-001
**Policy Name:** "RDS instances must have encryption at rest enabled"
**Severity:** HIGH

---

## Resource Affected

- **Resource Type:** AWS RDS PostgreSQL
- **Resource ID:** talma-legacy-db-prod
- **Environment:** Production
- **Region:** us-east-1

---

## Business Justification

Legacy database created before encryption-at-rest policy was mandated.
Enabling encryption requires full database rebuild with downtime.
Migration to new encrypted RDS scheduled for Q2 2024.

---

## Risk Assessment

**Risk Level:** MEDIUM

**Threats:**

- Data breach if physical disk is compromised
- Compliance violation for ISO 27001 Annex A.12.3

**Likelihood:** LOW (AWS data center physical security)
**Impact:** HIGH (sensitive customer data)

---

## Compensating Controls

1. ✅ Database in private subnet, no public access
2. ✅ VPC Flow Logs enabled
3. ✅ TLS 1.2+ enforced for all connections
4. ✅ Application-level encryption for PII fields
5. ✅ CloudTrail logging all DB API calls
6. ✅ AWS Backup daily snapshots (retained 30 days)
7. ✅ GuardDuty monitoring for anomalous access

---

## Timeline

- **Exception Valid Until:** 2024-06-30
- **Migration Plan:** Q2 2024
- **Review Date:** 2024-05-01 (verify migration on track)

---

## Approvals

- [ ] **Chief Architect:** ********\_\_\_******** Date: **\_\_\_**
- [ ] **Security Lead:** **********\_********** Date: **\_\_\_**
- [ ] **Compliance Officer:** ******\_\_\_\_****** Date: **\_\_\_**

---

## Outcome

**Status:** APPROVED
**Approved By:** Sarah Chen (Chief Architect), Mike Johnson (Security Lead)
**Approved Date:** 2024-02-16
**Conditions:**

1. Weekly status updates on migration progress
2. Re-assessment if migration delayed beyond 2024-08-01
3. Mandatory quarterly review
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Policy as Code implementado y funcionando
- [ ] CI/CD gates bloqueando deploys non-compliant
- [ ] Scans automáticos semanales en producción
- [ ] 0 vulnerabilidades CRITICAL sin remediar
- [ ] Excepciones con aprobación formal y fecha límite
- [ ] Evidencia de compliance almacenada (retención 2 años)
- [ ] Dashboards de compliance actualizados

### Métricas

```promql
# Compliance score por sistema
(count(compliance_check{status="passed"}) / count(compliance_check)) * 100

# Vulnerabilidades abiertas por severidad
count(vulnerabilities{status="open"}) by (severity)

# Time to remediation
histogram_quantile(0.95, vulnerability_remediation_days) by (severity)

# Policy violations
count(policy_violations{status="open"}) by (policy_id)
```

### Dashboard SLIs

| Métrica                       | SLI      | Alertar si |
| ----------------------------- | -------- | ---------- |
| Compliance score              | > 95%    | < 90%      |
| CRITICAL vulnerabilities open | 0        | > 0        |
| HIGH vulnerabilities open     | < 5      | > 10       |
| Time to fix CRITICAL          | < 24h    | > 48h      |
| Time to fix HIGH              | < 7 días | > 14 días  |
| Policy violations open        | < 10     | > 25       |
| Exceptions expired            | 0        | > 0        |

---

## 9. Referencias

**Regulatorios:**

- [ISO/IEC 27001:2022](https://www.iso.org/standard/27001)
- [SOC 2 Type II](https://www.aicpa.org/soc4so)
- [GDPR Art. 32 - Security of Processing](https://gdpr-info.eu/art-32-gdpr/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/)

**Herramientas:**

- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Checkov by Bridgecrew](https://www.checkov.io/)
- [tfsec](https://github.com/aquasecurity/tfsec)
- [AWS Config Rules](https://docs.aws.amazon.com/config/latest/developerguide/evaluate-config.html)

**Frameworks:**

- [AWS Well-Architected - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

**Buenas Prácticas:**

- "Continuous Compliance" - DevSecOps practices
- FinOps Foundation - Cloud compliance
- NIST Cybersecurity Framework
