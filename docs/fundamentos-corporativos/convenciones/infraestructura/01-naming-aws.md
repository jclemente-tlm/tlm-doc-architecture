---
id: naming-aws
sidebar_position: 1
title: Naming - Recursos AWS
description: Convención de nomenclatura para recursos en AWS
---

## 1. Principio

Los nombres de recursos AWS deben ser descriptivos, incluir el ambiente y seguir convenciones que faciliten la gestión, facturación y auditoría.

## 2. Reglas

### Regla 1: Estructura General

- **Formato**: `tlm-{ambiente}-{servicio}-{recurso}-{descriptor}`
- **Ejemplo correcto**: `tlm-prod-users-api-lb`, `tlm-dev-orders-db-rds`
- **Ejemplo incorrecto**: `prod-api`, `users-database`, `lb-1`

### Regla 2: Ambientes Estándar

| Ambiente   | Código | Uso                          |
| ---------- | ------ | ---------------------------- |
| Desarrollo | `dev`  | Desarrollo local/integración |
| QA/Testing | `qa`   | Pruebas funcionales          |
| Staging    | `stg`  | Pre-producción               |
| Producción | `prod` | Ambiente productivo          |
| Sandbox    | `sbx`  | Experimentación              |

```
✅ Correcto:
tlm-dev-users-api-asg
tlm-prod-orders-db-rds
tlm-stg-payments-queue-sqs

❌ Incorrecto:
tlm-development-users-api  # Usar código corto
talma-prod-api             # Falta servicio y recurso
users-prod                 # Falta prefijo tlm
```

### Regla 3: EC2 Instances

- **Formato**: `tlm-{env}-{servicio}-{tipo}-ec2-{index}`
- **Ejemplos**:
  - `tlm-prod-users-api-ec2-01`
  - `tlm-dev-bastion-jump-ec2-01`
  - `tlm-prod-workers-batch-ec2-03`

### Regla 4: S3 Buckets

- **Formato**: `tlm-{env}-{proposito}-{pais?}-s3`
- **Restricción**: Solo minúsculas, números, guiones (AWS requirement)
- **Ejemplos**:
  - `tlm-prod-documents-pe-s3`
  - `tlm-dev-logs-s3`
  - `tlm-prod-backups-s3`

```
✅ Correcto:
tlm-prod-invoices-pe-s3
tlm-dev-temp-files-s3

❌ Incorrecto:
tlm-prod-Invoices-s3       # Mayúsculas no permitidas
prod-invoices              # Falta prefijo y sufijo
tlm_prod_invoices_s3       # Guiones bajos no permitidos
```

### Regla 5: RDS Databases

- **Formato**: `tlm-{env}-{servicio}-{engine}-rds`
- **Ejemplos**:
  - `tlm-prod-users-postgres-rds`
  - `tlm-dev-orders-mysql-rds`
  - `tlm-prod-analytics-aurora-rds`

### Regla 6: ECS/EKS Clusters

- **Formato**: `tlm-{env}-{tipo}-cluster`
- **Ejemplos**:
  - `tlm-prod-ecs-cluster`
  - `tlm-dev-eks-cluster`
  - `tlm-stg-ecs-cluster`

### Regla 7: ECS Services

- **Formato**: `tlm-{env}-{servicio}-svc`
- **Ejemplos**:
  - `tlm-prod-users-api-svc`
  - `tlm-dev-notifications-worker-svc`

### Regla 8: Load Balancers

- **Formato**: `tlm-{env}-{servicio}-{tipo}-lb`
- **Tipos**: `alb` (Application), `nlb` (Network)
- **Ejemplos**:
  - `tlm-prod-api-gateway-alb`
  - `tlm-dev-internal-nlb`

### Regla 9: Security Groups

- **Formato**: `tlm-{env}-{servicio}-{regla}-sg`
- **Ejemplos**:
  - `tlm-prod-api-public-sg`
  - `tlm-dev-db-internal-sg`
  - `tlm-prod-redis-cache-sg`

### Regla 10: Lambda Functions

- **Formato**: `tlm-{env}-{servicio}-{funcion}-lambda`
- **Ejemplos**:
  - `tlm-prod-orders-process-payment-lambda`
  - `tlm-dev-users-send-welcome-email-lambda`

### Regla 11: SQS Queues

- **Formato**: `tlm-{env}-{servicio}-{proposito}-queue`
- **Ejemplos**:
  - `tlm-prod-orders-processing-queue`
  - `tlm-dev-notifications-email-queue`
  - `tlm-prod-orders-processing-dlq` (Dead Letter Queue)

### Regla 12: SNS Topics

- **Formato**: `tlm-{env}-{servicio}-{evento}-topic`
- **Ejemplos**:
  - `tlm-prod-orders-created-topic`
  - `tlm-dev-users-registered-topic`

## 3. Tabla de Sufijos por Tipo de Recurso

| Recurso AWS          | Sufijo          | Ejemplo                         |
| -------------------- | --------------- | ------------------------------- |
| EC2 Instance         | `-ec2`          | `tlm-prod-api-ec2-01`           |
| S3 Bucket            | `-s3`           | `tlm-prod-documents-s3`         |
| RDS Database         | `-rds`          | `tlm-prod-users-postgres-rds`   |
| ECS Cluster          | `-cluster`      | `tlm-prod-ecs-cluster`          |
| ECS Service          | `-svc`          | `tlm-prod-users-api-svc`        |
| Load Balancer        | `-alb` / `-nlb` | `tlm-prod-api-alb`              |
| Security Group       | `-sg`           | `tlm-prod-api-public-sg`        |
| Lambda Function      | `-lambda`       | `tlm-prod-process-order-lambda` |
| SQS Queue            | `-queue`        | `tlm-prod-orders-queue`         |
| SNS Topic            | `-topic`        | `tlm-prod-order-created-topic`  |
| VPC                  | `-vpc`          | `tlm-prod-main-vpc`             |
| Subnet               | `-subnet`       | `tlm-prod-public-subnet-1a`     |
| IAM Role             | `-role`         | `tlm-prod-ecs-task-role`        |
| CloudWatch Log Group | `-logs`         | `/aws/lambda/tlm-prod-api-logs` |

## 4. Multi-región

Incluir código de región cuando se tenga infraestructura en múltiples regiones:

```
tlm-prod-api-use1-ec2-01    # us-east-1
tlm-prod-api-usw2-ec2-01    # us-west-2
tlm-prod-db-sae1-rds        # sa-east-1 (São Paulo)
```

## 5. Herramientas de Validación

### Terraform Validation

```hcl
variable "environment" {
  type        = string
  description = "Environment name"

  validation {
    condition     = contains(["dev", "qa", "stg", "prod", "sbx"], var.environment)
    error_message = "Environment must be one of: dev, qa, stg, prod, sbx."
  }
}

locals {
  name_prefix = "tlm-${var.environment}-${var.service_name}"

  ec2_name    = "${local.name_prefix}-ec2"
  rds_name    = "${local.name_prefix}-postgres-rds"
  s3_name     = "${local.name_prefix}-data-s3"
}

resource "aws_instance" "app" {
  tags = {
    Name = "${local.ec2_name}-01"
  }
}
```

### AWS CLI Validation Script

```bash
#!/bin/bash

# Validar que todos los recursos tengan prefijo tlm-
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[Tags[?Key==`Name`].Value]' \
  --output text | grep -v "^tlm-" | while read -r name; do
    echo "⚠️  Instance sin prefijo tlm-: $name"
done
```

## 📖 Referencias

### Estándares relacionados

- [Infraestructura como Código](/docs/fundamentos-corporativos/estandares/infraestructura/iac)

### Convenciones relacionadas

- [Tags y Metadatos](./02-tags-metadatos.md)
- [Variables de Entorno](./03-variables-entorno.md)

### Recursos externos

- [AWS Tagging Best Practices](https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/tagging-best-practices.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
