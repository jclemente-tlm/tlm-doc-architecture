---
id: infraestructura-como-codigo
sidebar_position: 2
title: Infraestructura como Código (IaC)
description: Estándar técnico obligatorio para definir, provisionar y gestionar infraestructura cloud mediante Terraform con state remoto, módulos reutilizables y GitOps
---

# Estándar Técnico — Infraestructura como Código (IaC)

---

## 1. Propósito
Garantizar infraestructura reproducible, auditable y versionada mediante Terraform 1.6+, state remoto en S3+DynamoDB, módulos reutilizables y GitOps workflow (PR review → plan → apply manual).

---

## 2. Alcance

**Aplica a:**
- Toda infraestructura AWS (VPC, ECS, RDS, S3, IAM, etc.)
- Recursos cloud en dev, staging, production
- Networking, compute, storage, databases, seguridad

**No aplica a:**
- Configuraciones dentro de contenedores (usar env vars)
- Código de aplicación (deployment vía CI/CD)
- Secretos (usar AWS Secrets Manager, NO Terraform state)
- Cambios manuales urgentes (documentar y revertir a código ASAP)

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **IaC Tool** | Terraform | 1.6+ | Agnóstico cloud, state management robusto |
| **State Backend** | S3 + DynamoDB | - | State remoto con locking colaborativo |
| **Módulos** | Terraform Registry | - | Versionado semántico (v1.2.3) |
| **Validation** | terraform fmt/validate | Built-in | Sintaxis y formato consistente |
| **Linting** | tflint | 0.50+ | Detecta errores y malas prácticas |
| **Security Scan** | Checkov, tfsec | Latest | Detecta vulnerabilidades de seguridad |
| **CI/CD** | GitHub Actions, GitLab CI | - | Automatización de plan/apply |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] State remoto en S3 con DynamoDB locking
- [ ] Separación de entornos (dev/staging/production) con workspaces o directorios
- [ ] Módulos reutilizables con versionado semántico
- [ ] Secrets NUNCA en state (usar AWS Secrets Manager)
- [ ] GitOps workflow: PR → `terraform plan` automático → `terraform apply` manual
- [ ] `terraform fmt` ejecutado antes de commit
- [ ] `terraform validate` pasando en CI/CD
- [ ] Escaneo de seguridad con Checkov/tfsec en CI/CD
- [ ] Outputs documentados en README.md por módulo
- [ ] Tags obligatorios: Environment, Project, ManagedBy=Terraform
- [ ] State lock timeout configurado (10 minutos máx)
- [ ] Backup de state en S3 con versionado habilitado

---

## 5. Prohibiciones

- ❌ State local (usar siempre S3 backend)
- ❌ Secretos en archivos .tf o variables
- ❌ `terraform apply` sin `plan` previo revisado
- ❌ Cambios manuales en consola AWS (revertir a código)
- ❌ Módulos sin versionado (usar tags semánticos)
- ❌ `terraform destroy` en producción sin aprobación

---

## 6. Configuración Mínima

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "talma-terraform-state"
    key            = "prod/vpc/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# main.tf
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
    }
  }
}

# Uso de módulo
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"
  
  name = "${var.project_name}-${var.environment}"
  cidr = var.vpc_cidr
  
  azs             = data.aws_availability_zones.available.names
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  
  enable_nat_gateway = true
  single_nat_gateway = var.environment != "prod"
}
```

---

## 7. Validación

```bash
# Formato y validación
terraform fmt -recursive
terraform validate

# Linting
tflint --recursive

# Security scan
checkov -d . --framework terraform
tfsec .

# Plan y apply
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan | jq
terraform apply plan.tfplan

# Verificar state lock
aws dynamodb get-item --table-name terraform-state-lock --key '{"LockID":{"S":"talma-terraform-state/prod/vpc/terraform.tfstate"}}'
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| State remoto habilitado | 100% | Verificar backend.tf en todos los entornos |
| Modules con versionado | 100% | `grep 'version =' *.tf` |
| Checkov/tfsec pasando | 100% | CI/CD pipeline status |
| Secrets en state | 0 | `terraform show \| grep -i password` |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-006: Infraestructura como Código](../../../decisiones-de-arquitectura/adr-006-infraestructura-iac.md)
- [Gestión de Secretos](./03-secrets-management.md)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
