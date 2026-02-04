---
id: environment-separation
sidebar_position: 9
title: Separación de Entornos
description: Estándar para separar ambientes (Dev, Staging, Production) en cuentas AWS independientes con acceso restringido y recursos aislados
---

# Estándar Técnico — Separación de Entornos

---

## 1. Propósito

Aislar ambientes (Dev, Staging, Production) en cuentas AWS separadas, VPCs independientes, credenciales distintas y acceso restrictivo, evitando que cambios en desarrollo afecten producción.

---

## 2. Alcance

**Aplica a:**

- Cuentas AWS por ambiente
- VPCs, subnets, security groups
- Bases de datos (RDS)
- Secrets y configuraciones
- Accesos IAM
- Pipelines CI/CD

**No aplica a:**

- Servicios compartidos (DNS, monitoreo central) → cuenta de Management

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología           | Versión mínima | Observaciones                 |
| ----------------- | -------------------- | -------------- | ----------------------------- |
| **Multi-Account** | AWS Organizations    | -              | Separación física             |
| **IaC**           | Terraform Workspaces | 1.6+           | Mismo código, estado separado |
| **Secrets**       | AWS Secrets Manager  | -              | Por cuenta                    |
| **Parameters**    | AWS Systems Manager  | -              | Por ambiente                  |
| **CI/CD**         | GitHub Actions       | -              | Despliegue controlado         |
| **Naming**        | Prefijo {env}-       | -              | dev-, staging-, prod-         |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Cuentas AWS

- [ ] **1 cuenta por ambiente**: Dev, Staging, Production en cuentas separadas
- [ ] **Management account**: Cuenta central (billing, IAM central)
- [ ] **SCPs**: Service Control Policies para limitar acciones
- [ ] **Naming**: `talma-{env}` (e.g., `talma-production`)

### VPCs

- [ ] **CIDR no solapados**:
  - Dev: 10.2.0.0/16
  - Staging: 10.1.0.0/16
  - Production: 10.0.0.0/16
- [ ] **NO VPC Peering** entre Dev y Production
- [ ] **Peering opcional**: Staging ↔ Production (solo para smoke tests)

### Secrets & Configuración

- [ ] **Secrets por cuenta**: DB credentials en Secrets Manager de cada cuenta
- [ ] **NO copiar secrets**: Nunca copiar secrets de prod a dev
- [ ] **Parámetros**: SSM Parameter Store con prefijo `/app/{env}/`

### Acceso

- [ ] **IAM separado**: Usuarios/roles distintos por cuenta
- [ ] **MFA obligatorio**: Production requiere MFA siempre
- [ ] **Least privilege**: Devs NO tienen acceso a producción
- [ ] **Break-glass**: Solo admins con aprobación

---

## 5. AWS Organizations - Multi-Account

### Estructura de Cuentas

```text
talma-root (Management Account)
│
├── talma-production (Account ID: 111111111111)
│   ├── VPC: 10.0.0.0/16
│   ├── RDS: payment-db-prod
│   └── ECS: payment-service-prod
│
├── talma-staging (Account ID: 222222222222)
│   ├── VPC: 10.1.0.0/16
│   ├── RDS: payment-db-staging
│   └── ECS: payment-service-staging
│
└── talma-dev (Account ID: 333333333333)
    ├── VPC: 10.2.0.0/16
    ├── RDS: payment-db-dev
    └── ECS: payment-service-dev
```

### Terraform - Multi-Account Setup

```hcl
# terraform/provider.tf

# Production account
provider "aws" {
  alias  = "production"
  region = "us-east-1"

  assume_role {
    role_arn = "arn:aws:iam::111111111111:role/TerraformDeployRole"
  }
}

# Staging account
provider "aws" {
  alias  = "staging"
  region = "us-east-1"

  assume_role {
    role_arn = "arn:aws:iam::222222222222:role/TerraformDeployRole"
  }
}

# Dev account
provider "aws" {
  alias  = "dev"
  region = "us-east-1"

  assume_role {
    role_arn = "arn:aws:iam::333333333333:role/TerraformDeployRole"
  }
}
```

### Deploy por Ambiente

```bash
# Deploy to production
terraform workspace select production
terraform apply -var-file=production.tfvars

# Deploy to staging
terraform workspace select staging
terraform apply -var-file=staging.tfvars

# Deploy to dev
terraform workspace select dev
terraform apply -var-file=dev.tfvars
```

---

## 6. Terraform Workspaces

### Configuración por Ambiente

```hcl
# terraform/main.tf

locals {
  environment = terraform.workspace

  # Configuración por ambiente
  config = {
    production = {
      vpc_cidr          = "10.0.0.0/16"
      db_instance_class = "db.t4g.large"
      ecs_task_cpu      = 1024
      ecs_task_memory   = 2048
      min_capacity      = 2
      max_capacity      = 10
      multi_az          = true
    }
    staging = {
      vpc_cidr          = "10.1.0.0/16"
      db_instance_class = "db.t4g.medium"
      ecs_task_cpu      = 512
      ecs_task_memory   = 1024
      min_capacity      = 1
      max_capacity      = 3
      multi_az          = false
    }
    dev = {
      vpc_cidr          = "10.2.0.0/16"
      db_instance_class = "db.t4g.micro"
      ecs_task_cpu      = 256
      ecs_task_memory   = 512
      min_capacity      = 1
      max_capacity      = 1
      multi_az          = false
    }
  }

  env_config = local.config[local.environment]
}

resource "aws_vpc" "main" {
  cidr_block = local.env_config.vpc_cidr

  tags = {
    Name        = "vpc-${local.environment}"
    Environment = local.environment
  }
}

resource "aws_db_instance" "main" {
  identifier     = "payment-db-${local.environment}"
  instance_class = local.env_config.db_instance_class
  multi_az       = local.env_config.multi_az

  # ...
}
```

---

## 7. Secrets Separation

### Secrets Manager - Por Cuenta

```hcl
# Production account secrets
resource "aws_secretsmanager_secret" "db_password_prod" {
  provider = aws.production
  name     = "prod/payment-service/db-password"

  tags = {
    Environment = "production"
  }
}

# Staging account secrets (DIFERENTES credenciales)
resource "aws_secretsmanager_secret" "db_password_staging" {
  provider = aws.staging
  name     = "staging/payment-service/db-password"

  tags = {
    Environment = "staging"
  }
}

# ⚠️ NUNCA compartir secrets entre ambientes
```

### .NET - Leer Secrets por Ambiente

```csharp
// appsettings.json
{
  "AWS": {
    "SecretsManager": {
      "SecretName": "prod/payment-service/db-password"  // Cambiar por ambiente
    }
  }
}

// appsettings.Development.json
{
  "AWS": {
    "SecretsManager": {
      "SecretName": "dev/payment-service/db-password"
    }
  }
}
```

---

## 8. IAM - Acceso por Ambiente

### Devs: Solo Dev

```hcl
# IAM policy para developers
resource "aws_iam_policy" "dev_access" {
  name = "DeveloperAccess"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "ecs:*",
          "rds:Describe*",
          "logs:*"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = "us-east-1"
          }
        }
      },
      {
        Effect = "Deny"  # PROHIBIR producción
        Action = "*"
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:PrincipalAccount" = "111111111111"  # Production account
          }
        }
      }
    ]
  })
}
```

### Ops: Producción con MFA

```hcl
resource "aws_iam_policy" "prod_access" {
  name = "ProductionAccess"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"
        Resource = "*"
        Condition = {
          BoolIfExists = {
            "aws:MultiFactorAuthPresent" = "true"  # MFA obligatorio
          }
        }
      }
    ]
  })
}
```

---

## 9. CI/CD - Despliegue Controlado

### GitHub Actions - Deploy por Branch

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches:
      - main # → Production
      - staging # → Staging
      - develop # → Dev

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Determine environment
        id: env
        run: |
          if [[ ${{ github.ref }} == 'refs/heads/main' ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
            echo "account_id=111111111111" >> $GITHUB_OUTPUT
          elif [[ ${{ github.ref }} == 'refs/heads/staging' ]]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
            echo "account_id=222222222222" >> $GITHUB_OUTPUT
          else
            echo "environment=dev" >> $GITHUB_OUTPUT
            echo "account_id=333333333333" >> $GITHUB_OUTPUT
          fi

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ steps.env.outputs.account_id }}:role/GitHubActionsRole
          aws-region: us-east-1

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster payment-cluster-${{ steps.env.outputs.environment }} \
            --service payment-service \
            --force-new-deployment
```

---

## 10. Validación de Cumplimiento

```bash
# Listar cuentas en Organization
aws organizations list-accounts --query 'Accounts[*].{Name:Name,Id:Id,Status:Status}'

# Verificar VPCs no solapados
aws ec2 describe-vpcs --query 'Vpcs[*].{VpcId:VpcId,CidrBlock:CidrBlock,Tags:Tags[?Key==`Environment`].Value}'

# Verificar secrets por ambiente
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `prod`)].Name'
aws secretsmanager list-secrets --query 'SecretList[?contains(Name, `dev`)].Name'

# Verificar NO hay VPC Peering entre dev y prod
aws ec2 describe-vpc-peering-connections --query 'VpcPeeringConnections[*].{RequesterVpc:RequesterVpcInfo.VpcId,AccepterVpc:AccepterVpcInfo.VpcId}'

# Verificar IAM MFA enforced en producción
aws iam get-account-summary | jq '.SummaryMap.AccountMFAEnabled'
```

---

## 11. Referencias

**AWS:**

- [AWS Multi-Account Strategy](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/organizing-your-aws-environment.html)
- [AWS Organizations Best Practices](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices.html)

**CIS:**

- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
