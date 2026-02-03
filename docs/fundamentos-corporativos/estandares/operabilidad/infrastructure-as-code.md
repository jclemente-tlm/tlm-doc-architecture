---
id: infrastructure-as-code
sidebar_position: 1
title: Infrastructure as Code (IaC)
description: Estándar para gestión de infraestructura mediante código con Terraform/CloudFormation, incluyendo versionado, modularización y validación automatizada.
---

# Estándar Técnico — Infrastructure as Code (IaC)

---

## 1. Propósito

Gestionar infraestructura cloud mediante **Infrastructure as Code (IaC)** con Terraform o CloudFormation, garantizando reproducibilidad, versionado, code review y despliegues automatizados sin intervención manual.

---

## 2. Alcance

**Aplica a:**

- Recursos AWS (VPC, EC2, RDS, S3, IAM, etc.)
- Configuración de networking (security groups, NACLs, routing)
- Políticas de seguridad (IAM roles, KMS keys)
- Configuración de monitoreo (CloudWatch alarms, dashboards)
- AWS ECS Fargate manifests (si aplica)

**No aplica a:**

- Configuración de aplicaciones (usar IConfiguration + env vars)
- Datos de negocio (migrations de BD son separadas)
- Configuraciones dev locales (docker-compose.yml)

---

## 3. Tecnologías Aprobadas

| Tecnología             | Uso                                 | Versión Mínima | Observaciones               |
| ---------------------- | ----------------------------------- | -------------- | --------------------------- |
| **Terraform**          | Infraestructura multi-cloud         | 1.6+           | Preferido para new projects |
| **AWS CloudFormation** | Infraestructura AWS-specific        | N/A            | Legacy projects OK          |
| **AWS CDK**            | Infraestructura con TypeScript/.NET | v2+            | Para equipos con expertise  |
| **Terragrunt**         | Wrapper Terraform para DRY          | 0.50+          | Opcional para multi-env     |

> Prohibido Ansible/Chef para provisioning de recursos cloud (usar solo para config management).

---

## 4. Requisitos Obligatorios 🔴

### 4.1 Estructura de Código

- [ ] **Modularización**: recursos agrupados por responsabilidad (networking, compute, storage)
- [ ] **DRY principle**: NO duplicar configuración entre entornos (usar variables)
- [ ] **Naming convention**: recursos nombrados `{env}-{project}-{resource}` (ej: `prod-orders-rds`)
- [ ] **Tags obligatorios** en todos los recursos:
  - `Environment` (dev/staging/prod)
  - `Project` (orders, payments, etc.)
  - `Owner` (equipo responsable)
  - `ManagedBy` (terraform/cloudformation)

### 4.2 Versionado y Git

- [ ] **100% de infraestructura en Git** (NO cambios manuales en consola AWS)
- [ ] **Branch protection** en `main` (require PR + approval)
- [ ] **Commits atómicos** con mensajes descriptivos
- [ ] **Changelog** o release notes para cambios significativos
- [ ] **.gitignore** para secrets (`terraform.tfvars`, `*.pem`)

### 4.3 Parametrización

- [ ] **Variables para valores específicos de entorno** (IPs, tamaños instancias, etc.)
- [ ] **NO hardcodear** ARNs, IDs, IPs en código
- [ ] Uso de **data sources** para referencias dinámicas:

  ```hcl
  # ✅ BIEN
  data "aws_vpc" "main" {
    filter {
      name   = "tag:Name"
      values = ["${var.environment}-vpc"]
    }
  }

  # ❌ MAL
  vpc_id = "vpc-0123abcd" # Hardcoded
  ```

- [ ] **terraform.tfvars** por entorno (dev.tfvars, prod.tfvars) en gitignore
- [ ] Secrets en **AWS Secrets Manager** o **Parameter Store** (NO en código)

### 4.4 State Management

- [ ] **Remote backend** obligatorio (AWS S3 + DynamoDB para lock):
  ```hcl
  terraform {
    backend "s3" {
      bucket         = "talma-terraform-state-prod"
      key            = "orders/terraform.tfstate"
      region         = "us-east-1"
      dynamodb_table = "terraform-lock"
      encrypt        = true
    }
  }
  ```
- [ ] **State file encryption** habilitado (S3 bucket con KMS)
- [ ] **State locking** con DynamoDB (prevenir modificaciones concurrentes)
- [ ] **Separación de state** por entorno (dev.tfstate, prod.tfstate)
- [ ] **NO commit** de archivos `.tfstate` en Git

### 4.5 Validación y Testing

- [ ] **`terraform validate`** en CI antes de merge
- [ ] **`terraform plan`** obligatorio antes de apply (revisar diff)
- [ ] **`tflint`** para linting de Terraform
- [ ] **Checkov** o **tfsec** para escaneo de seguridad
- [ ] **Dry-run** en staging antes de aplicar a producción

### 4.6 CI/CD Automation

- [ ] **Plan automático** en cada PR (comment con diff)
- [ ] **Apply automático** SOLO en staging
- [ ] **Apply manual** en producción (requiere aprobación)
- [ ] **Rollback plan** documentado (terraform state rollback, resource recreation)

---

## 5. Estructura de Directorios

```
infrastructure/
├── modules/
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/
│   │   ├── ecs-cluster.tf
│   │   ├── alb.tf
│   │   └── autoscaling.tf
│   └── database/
│       ├── rds.tf
│       └── elasticache.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   └── dev.tfvars (gitignored)
│   ├── staging/
│   │   ├── main.tf
│   │   └── staging.tfvars
│   └── prod/
│       ├── main.tf
│       └── prod.tfvars (gitignored)
├── .tflint.hcl
├── .gitignore
└── README.md
```

---

## 6. Ejemplo: Terraform Module

```hcl
# modules/database/rds.tf
resource "aws_db_instance" "main" {
  identifier             = "${var.environment}-${var.project}-rds"
  engine                 = "postgres"
  engine_version         = var.postgres_version
  instance_class         = var.instance_class
  allocated_storage      = var.allocated_storage
  storage_encrypted      = true
  kms_key_id             = aws_kms_key.rds.arn

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = var.environment == "prod" ? 30 : 7
  multi_az                = var.environment == "prod" ? true : false

  tags = {
    Name        = "${var.environment}-${var.project}-rds"
    Environment = var.environment
    Project     = var.project
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

# modules/database/variables.tf
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.small"
}

variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15.5"
}

# modules/database/outputs.tf
output "endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.endpoint
}

output "arn" {
  description = "RDS ARN"
  value       = aws_db_instance.main.arn
}
```

---

## 7. CI/CD Pipeline

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    paths:
      - "infrastructure/**"
  push:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0

      - name: Terraform Format
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/environments/dev

      - name: Terraform Validate
        run: terraform validate
        working-directory: infrastructure/environments/dev

      - name: TFLint
        uses: terraform-linters/setup-tflint@v3
        with:
          tflint_version: latest
      - run: tflint --init
      - run: tflint -f compact

      - name: Security Scan (Checkov)
        uses: bridgecrewio/checkov-action@master
        with:
          directory: infrastructure/
          framework: terraform

  plan:
    needs: validate
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2

      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/environments/dev

      - name: Terraform Plan
        id: plan
        run: terraform plan -no-color -var-file=dev.tfvars
        working-directory: infrastructure/environments/dev
        continue-on-error: true

      - name: Comment Plan
        uses: actions/github-script@v6
        with:
          github-token: ${{secrets.GITHUB_TOKEN}}
          script: |
            const output = `#### Terraform Plan 📖
            \`\`\`
            ${{ steps.plan.outputs.stdout }}
            \`\`\``;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: output
            });

  apply:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: staging
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2

      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/environments/staging

      - name: Terraform Apply
        run: terraform apply -auto-approve -var-file=staging.tfvars
        working-directory: infrastructure/environments/staging
```

---

## 8. Prohibiciones

- ❌ Cambios manuales en AWS Console (TODO debe ser IaC)
- ❌ Hardcodear IPs, ARNs, account IDs en código
- ❌ Commit de `.tfstate`, `.tfvars` con secrets
- ❌ Local state file en producción (usar remote backend)
- ❌ Recursos sin tags (Environment, Project, Owner)
- ❌ `terraform apply` sin `terraform plan` previo
- ❌ IaC sin code review (branch protection obligatorio)

---

## 9. Validación

**Checklist de cumplimiento:**

- [ ] `terraform fmt -check` → sin cambios
- [ ] `terraform validate` → exitoso
- [ ] `tflint` → sin errores
- [ ] `checkov -d infrastructure/` → sin críticos
- [ ] Remote backend configurado (S3 + DynamoDB)
- [ ] Tags obligatorios en todos los recursos
- [ ] Plan revisado antes de apply
- [ ] Cambios aplicados vía CI/CD (NO manual)

**Métricas de cumplimiento:**

| Métrica                     | Target | Verificación                                  |
| --------------------------- | ------ | --------------------------------------------- |
| Recursos con tags completos | 100%   | AWS Config rule                               |
| Cambios manuales en consola | 0      | CloudTrail audit (buscar non-terraform users) |
| PRs con terraform plan      | 100%   | GitHub Actions logs                           |
| Infraestructura en Git      | 100%   | Manual audit vs AWS inventory                 |

Incumplimientos detectados en audits trimestrales.

---

## 10. Referencias

- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Well-Architected — IaC](https://docs.aws.amazon.com/wellarchitected/latest/framework/sus_sus_dev_a3.html)
- [Terraform Learn — Terraform](https://learn.hashicorp.com/terraform)
- [Estándar: Code Review Policy](code-review-policy.md)
- [ADR-006: Infraestructura como Código](../../../decisiones-de-arquitectura/adr-006-infraestructura-iac.md)
