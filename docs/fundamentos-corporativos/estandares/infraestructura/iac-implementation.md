---
id: iac-implementation
sidebar_position: 2
title: IaC — Implementación con Terraform
description: Estándares para implementar infraestructura como código con Terraform, incluyendo estructura modular, módulos reutilizables y configuración por ambiente en AWS.
tags: [infraestructura, terraform, iac, aws, modulos]
---

# IaC — Implementación con Terraform

## Contexto

Toda la infraestructura de Talma en AWS se gestiona como código con Terraform. Este estándar define la estructura modular de proyecto, los patrones de módulos reutilizables y la configuración por ambiente. Complementa el lineamiento [Infraestructura como Código](../../lineamientos/operabilidad/02-infraestructura-como-codigo.md).

**Conceptos incluidos:**

- **Estructura de Proyecto** → Organización de módulos y environments
- **Módulos Reutilizables** → Patrones de módulos ECS, VPC, RDS
- **Environment Configuration** → Configuración reproducible por ambiente

---

## Stack Tecnológico

| Componente          | Tecnología     | Versión | Uso                             |
| ------------------- | -------------- | ------- | ------------------------------- |
| **IaC**             | Terraform      | 1.7+    | Provisioning de infraestructura |
| **Cloud Provider**  | AWS            | -       | Proveedor de nube               |
| **CI/CD**           | GitHub Actions | -       | Automated plan y apply          |
| **IaC Scanning**    | Checkov        | 3.0+    | Security y compliance scanning  |
| **Cost Estimation** | Infracost      | 0.10+   | Estimación de costos en PRs     |

---

## ¿Qué es Infrastructure as Code?

Implementación base de infraestructura como código usando Terraform para provisionar recursos AWS de forma declarativa, versionada y reproducible.

**Propósito:** Infraestructura como código versionado en Git, reproducible en múltiples entornos, con historial de cambios auditable.

**Beneficios:**
✅ **Reproducibilidad** — Misma infraestructura en dev/staging/prod
✅ **Versionamiento** — Historial completo en Git
✅ **Colaboración** — Code review antes de aplicar cambios
✅ **Disaster Recovery** — Recrear infraestructura desde código
✅ **Documentación** — El código es documentación viva

---

## Estructura de Proyecto

```
terraform/
├── modules/
│   ├── ecs-service/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── rds-postgres/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   └── ...
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
├── .terraform-version
└── README.md
```

---

## Módulo ECS Service

```hcl
# modules/ecs-service/main.tf
terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_ecs_task_definition" "service" {
  family                   = var.service_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = var.service_name
      image     = var.container_image
      essential = true

      portMappings = [{ containerPort = var.container_port, protocol = "tcp" }]

      environment = [
        for key, value in var.environment_variables : { name = key, value = value }
      ]

      secrets = [
        for secret in var.secrets : { name = secret.name, valueFrom = secret.arn }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.service_name}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = merge(var.common_tags, { Name = var.service_name })
}

resource "aws_ecs_service" "service" {
  name             = var.service_name
  cluster          = var.cluster_id
  task_definition  = aws_ecs_task_definition.service.arn
  desired_count    = var.desired_count
  launch_type      = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.service.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.service.arn
    container_name   = var.service_name
    container_port   = var.container_port
  }

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100

    deployment_circuit_breaker {
      enable   = true
      rollback = true
    }
  }

  health_check_grace_period_seconds = 60
  tags = var.common_tags
}

resource "aws_security_group" "service" {
  name_prefix = "${var.service_name}-"
  description = "Security group for ${var.service_name}"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, { Name = "${var.service_name}-sg" })
}

resource "aws_cloudwatch_log_group" "service" {
  name              = "/ecs/${var.service_name}"
  retention_in_days = var.log_retention_days
  tags              = var.common_tags
}
```

```hcl
# modules/ecs-service/variables.tf
variable "service_name"          { type = string }
variable "container_image"       { type = string }
variable "container_port"        { type = number; default = 8080 }
variable "cpu"                   { type = number; default = 512 }
variable "memory"                { type = number; default = 1024 }
variable "desired_count"         { type = number; default = 2 }
variable "cluster_id"            { type = string }
variable "vpc_id"                { type = string }
variable "private_subnet_ids"    { type = list(string) }
variable "alb_security_group_id" { type = string }
variable "aws_region"            { type = string }
variable "log_retention_days"    { type = number; default = 30 }
variable "environment_variables" { type = map(string); default = {} }
variable "secrets" {
  type = list(object({ name = string, arn = string }))
  default = []
}
variable "common_tags" { type = map(string) }
```

---

## Environment Configuration

```hcl
# environments/production/main.tf
terraform {
  required_version = ">= 1.7.0"

  backend "s3" {
    bucket         = "talma-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }

  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "production"
      ManagedBy   = "Terraform"
      Project     = "Customer Service"
    }
  }
}

module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr             = var.vpc_cidr
  availability_zones   = var.availability_zones
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  environment          = "production"
  common_tags          = local.common_tags
}

resource "aws_ecs_cluster" "main" {
  name = "production-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = local.common_tags
}

module "customer_service" {
  source = "../../modules/ecs-service"

  service_name          = "customer-service"
  container_image       = var.customer_service_image
  container_port        = 8080
  cpu                   = 512
  memory                = 1024
  desired_count         = 3
  cluster_id            = aws_ecs_cluster.main.id
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  alb_security_group_id = module.alb.security_group_id
  aws_region            = var.aws_region
  log_retention_days    = 90
  common_tags           = local.common_tags

  environment_variables = {
    ASPNETCORE_ENVIRONMENT = "Production"
  }

  secrets = [
    { name = "ConnectionStrings__PostgreSQL", arn = aws_secretsmanager_secret.customer_db.arn },
    { name = "Redis__ConnectionString",       arn = aws_secretsmanager_secret.redis.arn }
  ]
}

locals {
  common_tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
    Service     = "Customer Service"
    CostCenter  = "Engineering"
    Owner       = "platform-team@talma.com"
  }
}
```

```hcl
# environments/production/terraform.tfvars
aws_region         = "us-east-1"
vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

customer_service_image = "ghcr.io/talma/customer-service:1.2.3"
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Terraform como única herramienta de IaC (sin cambios manuales en consola AWS)
- **MUST** 100% de infraestructura en Terraform
- **MUST** estructura modular: separar `modules/` de `environments/`
- **MUST** usar módulos reutilizables (no duplicar recursos entre environments)
- **MUST** aplicar tags obligatorios a todos los recursos: `Environment`, `ManagedBy`, `Service`, `CostCenter`, `Owner`

### SHOULD (Fuertemente recomendado)

- **SHOULD** Infracost integrado en PRs para estimación de costo de cambios
- **SHOULD** multi-AZ para recursos de alta disponibilidad (ECS, RDS)

### MAY (Opcional)

- **MAY** usar Terraform Cloud para remote runs y governance
- **MAY** usar Terragrunt para eliminar repetición de backend configuration

### MUST NOT (Obligatorio)

- **MUST NOT** hacer cambios manuales en AWS Console
- **MUST NOT** hardcodear secrets en código Terraform
- **MUST NOT** omitir tags obligatorios (Checkov los valida en pipeline)

---

## Referencias

- [Terraform Documentation](https://www.terraform.io/docs) — referencia oficial de Terraform
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) — recursos AWS para Terraform
- [Terraform Best Practices](https://www.terraform-best-practices.com/) — estructura y patrones recomendados
- [Checkov Documentation](https://www.checkov.io/) — seguridad y compliance en IaC
- [IaC — Workflow y Code Review](./iac-workflow.md) — pipeline CI/CD y proceso de revisión
- [IaC — State y Drift Detection](./iac-state-drift.md) — gestión de state y detección de cambios
- [Contenerización](./containerization.md) — imágenes Docker desplegadas con este módulo ECS
- [Redes Virtuales](./virtual-networks.md) — módulo VPC usado en environment configuration
