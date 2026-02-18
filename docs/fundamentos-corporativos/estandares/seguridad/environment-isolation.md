---
id: environment-isolation
sidebar_position: 21
title: Environment Isolation
description: Aislar entornos (dev/qa/prod) en cuentas o VPCs separadas
---

# Environment Isolation

## Contexto

Este estándar establece **Environment Isolation**: entornos NO deben compartir infraestructura. Error en dev no debe afectar producción. Complementa el [lineamiento de Segmentación y Aislamiento](../../lineamientos/seguridad/06-segmentacion-y-aislamiento.md) mediante **separación física de entornos**.

---

## Isolation Strategy

```yaml
# ✅ AWS Multi-Account Strategy

Talma Organization:

  Root Account (Management)
    │
    ├─► Shared Services Account
    │   - Networking (Transit Gateway)
    │   - DNS (Route 53)
    │   - Monitoring (Central CloudWatch)
    │   - SSO/Identity (AWS IAM Identity Center)
    │
    ├─► Development Account (111111111111)
    │   - VPC: 10.1.0.0/16
    │   - Resources: Devs pueden crear/destruir
    │   - Budget: $500/mes (hard limit)
    │   - Data: Synthetic/fake data
    │
    ├─► QA/Staging Account (222222222222)
    │   - VPC: 10.2.0.0/16
    │   - Resources: Controlled deployments
    │   - Budget: $1000/mes
    │   - Data: Anonimizada de producción
    │
    └─► Production Account (333333333333)
        - VPC: 10.3.0.0/16
        - Resources: Strict change control
        - Budget: $10K/mes + alarms
        - Data: Real PII (encrypted)

Benefits:
  ✅ Blast radius limitado (dev no afecta prod)
  ✅ IAM policies separadas (devs sin prod access)
  ✅ Billing separado (cost tracking claro)
  ✅ Compliance (production audit trail aislado)
```

## Infrastructure as Code

```hcl
# ✅ Terraform: Multi-account deployment

# terraform/environments/dev/main.tf
module "sales_service" {
  source = "../../modules/sales-service"

  environment = "dev"
  aws_account_id = "111111111111"

  vpc_cidr = "10.1.0.0/16"

  # Dev settings
  ecs_task_count  = 1        # Mínimo
  rds_instance    = "t3.micro"
  enable_deletion = true     # ✅ Devs pueden borrar
  backup_retention = 0       # No backups en dev

  # Dev data
  database_name = "sales_dev"
  seed_data     = true       # Synthetic data
}

# terraform/environments/qa/main.tf
module "sales_service" {
  source = "../../modules/sales-service"

  environment = "qa"
  aws_account_id = "222222222222"

  vpc_cidr = "10.2.0.0/16"

  # QA settings
  ecs_task_count  = 2
  rds_instance    = "t3.small"
  enable_deletion = false    # ✅ No delete accidental
  backup_retention = 7       # 7 días

  database_name = "sales_qa"
  seed_data    = false       # Anonimizada de prod
}

# terraform/environments/prod/main.tf
module "sales_service" {
  source = "../../modules/sales-service"

  environment = "prod"
  aws_account_id = "333333333333"

  vpc_cidr = "10.3.0.0/16"

  # Production settings
  ecs_task_count  = 4        # ✅ High availability
  rds_instance    = "r6g.large"
  enable_deletion = false
  backup_retention = 30      # ✅ 30 días + cross-region

  deletion_protection = true  # ✅ Cannot delete
  multi_az           = true   # ✅ Redundancy

  database_name = "sales_prod"
  encryption    = true        # ✅ KMS encryption
}
```

## Access Control

```yaml
# ✅ IAM Policies por entorno

Developers (limited to Dev account):

  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "*",
        "Resource": "*",
        "Condition": {
          "StringEquals": {
            "aws:RequestedRegion": "us-east-1"
          },
          "StringLike": {
            "aws:PrincipalAccount": "111111111111"  # ✅ Dev account only
          }
        }
      },
      {
        "Effect": "Deny",
        "Action": "*",
        "Resource": "*",
        "Condition": {
          "StringEquals": {
            "aws:PrincipalAccount": ["222222222222", "333333333333"]
          }
        }
      }
    ]
  }

QA Engineers (read-only QA, no prod):

  {
    "Effect": "Allow",
    "Action": [
      "ec2:Describe*",
      "ecs:Describe*",
      "rds:Describe*",
      "logs:Get*",
      "logs:Describe*"
    ],
    "Resource": "*",
    "Condition": {
      "StringEquals": {
        "aws:PrincipalAccount": "222222222222"  # ✅ QA account only
      }
    }
  }

DevOps (deploy to all, elevated prod):

  {
    "Effect": "Allow",
    "Action": [
      "ecs:UpdateService",
      "ecs:RegisterTaskDefinition",
      "ecr:PutImage"
    ],
    "Resource": "*",
    "Condition": {
      "StringLike": {
        "aws:PrincipalAccount": ["111111111111", "222222222222", "333333333333"]
      }
    }
  }
  # Production requires MFA
  {
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "StringEquals": {
        "aws:PrincipalAccount": "333333333333"
      },
      "BoolIfExists": {
        "aws:MultiFactorAuthPresent": "false"
      }
    }
  }
```

## Data Isolation

```yaml
# ✅ Datos NO pueden cruzar entornos

Development:
  - Synthetic data (Faker library)
  - No PII real
  - Reset weekly (fresh start)

  Example:
    Customer: John Doe (fake)
    Email: user_dev_123@example.com
    Card: 4111111111111111 (test card)

QA/Staging:
  - Anonimizada de producción
  - PII masked/tokenized
  - Refresh monthly

  Process:
    1. Export prod DB (snapshot)
    2. Anonymize (script):
       - Names → Faker
       - Emails → masked
       - Cards → tokenized
    3. Import to QA

  Example:
    Customer: Jane Smith → User_A123
    Email: jane@example.com → u***@example.com
    Card: 4532... → tok_abc123

Production:
  - Real PII (encrypted)
  - Strict access control
  - Audit all queries

  MUST NOT:
    ❌ Export prod data to dev
    ❌ Test en prod database
    ❌ Dev credentials con prod access
```

## Network Isolation

```yaml
# ✅ VPCs completamente separados

# NO VPC Peering entre dev/prod (isolation completa)

Development VPC (10.1.0.0/16):
  - Dev tiene acceso internet completo
  - No restrictions (experimentos)
  - No sensitive data

QA VPC (10.2.0.0/16):
  - Similar a prod (topología)
  - NAT Gateway (outbound only)
  - Security Groups iguales a prod

Production VPC (10.3.0.0/16):
  - Private subnets (backend)
  - Restrictive Security Groups
  - WAF + Shield
  - VPN para admin access

Cross-Environment Communication: ❌ PROHIBIDO
  - Dev → Prod: NO
  - QA → Prod: NO
  - Solo shared services (DNS, monitoring) via Transit Gateway

Exception: CI/CD Pipeline
  - GitHub Actions → Todos los entornos
  - Usa IAM roles (OIDC)
  - MFA required for prod deploy
```

## Monitoring

```yaml
# ✅ Monitorear acceso cross-environment

CloudTrail (cada cuenta): resource "aws_cloudtrail" "main" {
  name                          = "talma-${var.environment}-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true

  event_selector {
  read_write_type           = "All"
  include_management_events = true
  }
  }

Alerts:
  1. Production Access by Dev User:
    - Event: AssumeRole (from dev user to prod account)
    - Action: ALERT + DENY (should not happen)

  2. Data Export from Production:
    - Event: CreateDBSnapshot (prod account)
    - Action: Alert + manual approval required

  3. Production Resource Deletion:
    - Event: DeleteDBInstance, DeleteTable
    - Action: CRITICAL + revert (deletion protection)

Dashboard (Grafana):
  Environment Health:
    - Dev: 95% uptime OK (experimenting)
    - QA: 99% uptime (testing)
    - Prod: 99.9% uptime REQUIRED

  Cost Tracking:
    - Dev: $450/500 (90% budget)
    - QA: $820/1000 (82%)
    - Prod: $8500/10000 (85%)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar cuentas AWS separadas (dev/qa/prod)
- **MUST** VPCs separados (diferentes CIDR blocks)
- **MUST** IAM policies que restringen cross-account
- **MUST** MFA para production access
- **MUST** anonimizar datos en non-production
- **MUST** CloudTrail en todas las cuentas

### SHOULD (Fuertemente recomendado)

- **SHOULD** no VPC peering dev↔prod
- **SHOULD** budget alarms por cuenta
- **SHOULD** deletion protection en prod
- **SHOULD** auto-refresh QA data (monthly)

### MUST NOT (Prohibido)

- **MUST NOT** dev users con prod access directo
- **MUST NOT** prod data en dev environment
- **MUST NOT** shared infrastructure (VPC, DB)
- **MUST NOT** test en production database

---

## Referencias

- [Lineamiento: Segmentación y Aislamiento](../../lineamientos/seguridad/06-segmentacion-y-aislamiento.md)
- [Network Segmentation](./network-segmentation.md)
- [Data Protection](../../estandares/seguridad/data-protection.md)
