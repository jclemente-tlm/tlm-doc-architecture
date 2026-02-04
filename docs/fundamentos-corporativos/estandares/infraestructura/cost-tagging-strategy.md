---
id: cost-tagging-strategy
sidebar_position: 6
title: Estrategia de Tagging de Costos
description: Estándar para etiquetado AWS obligatorio de recursos con Environment, Service, Owner, CostCenter para atribución de costos
---

# Estándar Técnico — Estrategia de Tagging de Costos

---

## 1. Propósito

Garantizar atribución precisa de costos mediante etiquetado **obligatorio** de todos los recursos AWS con tags estándar (Environment, Service, Owner, CostCenter), validado en CI/CD con Checkov y reportes mensuales por equipo.

---

## 2. Alcance

**Aplica a:**

- **Todos** los recursos AWS con soporte de tags (EC2, ECS, RDS, S3, etc.)
- Recursos creados manualmente (consola AWS)
- Recursos provisionados con Terraform
- Recursos de infraestructura compartida

**No aplica a:**

- Recursos AWS sin soporte de tags (algunos recursos transitorios)
- Recursos de cuentas sandbox personales

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología        | Versión mínima | Observaciones            |
| ----------------- | ----------------- | -------------- | ------------------------ |
| **IaC**           | Terraform         | 1.6+           | Gestión recursos AWS     |
| **Validación**    | Checkov           | 3.0+           | Policy as Code para tags |
| **Cost Explorer** | AWS Cost Explorer | -              | Reportes por tags        |
| **Enforcement**   | AWS Tag Policies  | -              | Service Control Policies |
| **CI/CD**         | GitHub Actions    | -              | Validación automática    |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Tags Obligatorios 🔴

### 4.1 Tags Mínimos Requeridos

| Tag             | Descripción                    | Valores permitidos               | Ejemplo         |
| --------------- | ------------------------------ | -------------------------------- | --------------- |
| **Environment** | Entorno de deployment          | `dev`, `staging`, `prod`         | `prod`          |
| **Service**     | Nombre del servicio/aplicación | kebab-case alfanumérico          | `payment-api`   |
| **Owner**       | Equipo responsable             | Nombre del equipo                | `platform-team` |
| **CostCenter**  | Centro de costos               | Código contabilidad              | `engineering`   |
| **ManagedBy**   | Herramienta de provisión       | `terraform`, `manual`, `console` | `terraform`     |
| **Project**     | Proyecto/iniciativa            | Nombre proyecto                  | `ecommerce-v2`  |

### 4.2 Tags Opcionales Recomendados

| Tag            | Descripción              | Ejemplo                   |
| -------------- | ------------------------ | ------------------------- |
| **Backup**     | Política de backup       | `daily`, `weekly`, `none` |
| **Compliance** | Requisito regulatorio    | `pci-dss`, `sox`, `none`  |
| **Version**    | Versión de la aplicación | `v1.2.3`                  |
| **Repository** | Repositorio Git          | `tlm-svc-payment`         |

---

## 5. Implementación Obligatoria

### 5.1 Terraform - Tag Defaults

```hcl
# variables.tf
variable "common_tags" {
  description = "Tags comunes aplicados a todos los recursos"
  type        = map(string)
  default = {
    ManagedBy   = "terraform"
    Project     = "platform-core"
    CostCenter  = "engineering"
  }
}

variable "environment" {
  description = "Entorno de deployment"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment debe ser: dev, staging o prod"
  }
}

# locals.tf
locals {
  tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      Service     = var.service_name
      Owner       = var.team_owner
      CostCenter  = var.cost_center
    }
  )
}

# Uso en recursos
resource "aws_ecs_service" "app" {
  name            = "${var.service_name}-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn

  tags = local.tags
}

resource "aws_s3_bucket" "storage" {
  bucket = "${var.service_name}-storage-${var.environment}"

  tags = merge(
    local.tags,
    {
      DataClassification = "confidential"
      Backup             = "daily"
    }
  )
}
```

### 5.2 Checkov - Validación de Tags

```yaml
# .checkov.yml
framework:
  - terraform

check:
  - CKV_AWS_CUSTOM_001

# custom_checks/tag_validation.py
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class RequiredTagsCheck(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all resources have required tags"
        id = "CKV_AWS_CUSTOM_001"
        supported_resources = ['*']
        categories = ['CONVENTION']
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        required_tags = ['Environment', 'Service', 'Owner', 'CostCenter', 'ManagedBy']

        if 'tags' not in conf:
            return CheckResult.FAILED

        tags = conf['tags'][0]
        missing_tags = [tag for tag in required_tags if tag not in tags]

        if missing_tags:
            self.evaluated_keys = ['tags']
            return CheckResult.FAILED

        return CheckResult.PASSED

check = RequiredTagsCheck()
```

### 5.3 GitHub Actions - Validación CI/CD

```yaml
# .github/workflows/terraform-validate.yml
name: Terraform Validation

on:
  pull_request:
    paths:
      - "infrastructure/**"

jobs:
  validate-tags:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Checkov Tag Validation
        uses: bridgecrewio/checkov-action@master
        with:
          directory: infrastructure/
          framework: terraform
          check: CKV_AWS_CUSTOM_001
          soft_fail: false # Bloquea merge si faltan tags

      - name: Terraform Plan with Tag Report
        run: |
          cd infrastructure/
          terraform init
          terraform plan -out=tfplan
          terraform show -json tfplan | jq '.planned_values.root_module.resources[] | select(.values.tags == null) | .address' > missing_tags.txt

          if [ -s missing_tags.txt ]; then
            echo "❌ Recursos sin tags obligatorios:"
            cat missing_tags.txt
            exit 1
          fi
```

---

## 6. AWS Tag Policies (Enforcement)

```json
{
  "tags": {
    "Environment": {
      "tag_key": {
        "@@assign": "Environment"
      },
      "tag_value": {
        "@@assign": ["dev", "staging", "prod"]
      },
      "enforced_for": {
        "@@assign": [
          "ec2:instance",
          "ecs:cluster",
          "ecs:service",
          "rds:db",
          "s3:bucket"
        ]
      }
    },
    "CostCenter": {
      "tag_key": {
        "@@assign": "CostCenter"
      },
      "enforced_for": {
        "@@assign": ["*"]
      }
    }
  }
}
```

---

## 7. Reportes de Costos por Tags

### AWS CLI - Cost Explorer Query

```bash
# Costos por Environment
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=TAG,Key=Environment

# Costos por Service
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=TAG,Key=Service \
  --filter file://filter.json

# filter.json
{
  "Tags": {
    "Key": "Environment",
    "Values": ["prod"]
  }
}
```

### Terraform - Cost Allocation Tags

```hcl
# billing.tf
resource "aws_ce_cost_category" "environment" {
  name         = "EnvironmentCategory"
  rule_version = "CostCategoryExpression.v1"

  rule {
    value = "Production"
    rule {
      tags {
        key    = "Environment"
        values = ["prod"]
      }
    }
  }

  rule {
    value = "Non-Production"
    rule {
      tags {
        key    = "Environment"
        values = ["dev", "staging"]
      }
    }
  }
}

# Activar cost allocation tags
resource "aws_ce_cost_allocation_tag" "environment" {
  tag_key = "Environment"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "service" {
  tag_key = "Service"
  status  = "Active"
}
```

---

## 8. Remediation - Tag Faltantes

```bash
# Script para agregar tags a recursos existentes
#!/bin/bash
# tag-resources.sh

ENVIRONMENT="prod"
SERVICE="payment-api"
OWNER="platform-team"
COST_CENTER="engineering"

# Taggear instancias ECS
aws ecs list-services --cluster prod-cluster | jq -r '.serviceArns[]' | while read service_arn; do
  aws ecs tag-resource --resource-arn "$service_arn" --tags \
    key=Environment,value=$ENVIRONMENT \
    key=Service,value=$SERVICE \
    key=Owner,value=$OWNER \
    key=CostCenter,value=$COST_CENTER \
    key=ManagedBy,value=script
done

# Taggear buckets S3
aws s3api list-buckets --query 'Buckets[*].Name' --output text | while read bucket; do
  aws s3api put-bucket-tagging --bucket "$bucket" --tagging \
    "TagSet=[
      {Key=Environment,Value=$ENVIRONMENT},
      {Key=Service,Value=$SERVICE},
      {Key=Owner,Value=$OWNER},
      {Key=CostCenter,Value=$COST_CENTER}
    ]"
done
```

---

## 9. Validación de Cumplimiento

```bash
# Listar recursos sin tag Environment
aws resourcegroupstaggingapi get-resources \
  --resource-type-filters ec2:instance ecs:service rds:db s3:bucket \
  --query 'ResourceTagMappingList[?!Tags[?Key==`Environment`]].ResourceARN'

# Reportar compliance por equipo
aws resourcegroupstaggingapi get-compliance-summary \
  --target-id-filters "Environment=prod" \
  --group-by TARGET_ID

# Dashboard Grafana - Tag Compliance
SELECT
  COUNT(CASE WHEN tags.Environment IS NULL THEN 1 END) * 100.0 / COUNT(*) as missing_environment_pct,
  COUNT(CASE WHEN tags.CostCenter IS NULL THEN 1 END) * 100.0 / COUNT(*) as missing_costcenter_pct
FROM aws_resources
WHERE created_date >= current_date - interval '30 days'
```

---

## 10. Referencias

**AWS:**

- [AWS Tagging Best Practices](https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/tagging-best-practices.html)
- [Cost Allocation Tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html)

**FinOps:**

- [FinOps Foundation - Tagging Standards](https://www.finops.org/framework/capabilities/cost-allocation/)
- [Cloud FinOps (O'Reilly)](https://www.oreilly.com/library/view/cloud-finops/9781492054610/)
