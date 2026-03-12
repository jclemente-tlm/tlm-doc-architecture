---
id: iac-standards
sidebar_position: 2
title: IaC — Estándares Terraform
description: Estándares para implementar infraestructura como código con Terraform, incluyendo estructura modular, módulos reutilizables, pipeline CI/CD y proceso de revisión de cambios.
tags: [infraestructura, terraform, iac, aws, github-actions, code-review]
---

# IaC — Estándares Terraform

## Contexto

Toda la infraestructura de Talma en AWS se gestiona como código con Terraform. Este estándar define la estructura modular, los módulos reutilizables, el pipeline CI/CD y el proceso de revisión de cambios. Complementa el lineamiento [Infraestructura como Código](../../lineamientos/operabilidad/infraestructura-como-codigo.md).

**Conceptos incluidos:**

- **Estructura de Proyecto** → Organización de módulos y environments
- **Módulos Reutilizables** → Patrones de módulos ECS, VPC, RDS
- **IaC Workflow** → Pipeline CI/CD con plan en PR y apply en merge
- **IaC Code Review** → Proceso de revisión, checklist y PR template

:::note Implementación gestionada por Plataforma
Este estándar define los **requisitos que los servicios deben cumplir**. El diseño, aprovisionamiento y operación de la infraestructura Terraform son responsabilidad del equipo de **Plataforma**. Consultar en **#platform-support**.
:::

---

## Stack Tecnológico

| Componente          | Tecnología     | Versión | Uso                             |
| ------------------- | -------------- | ------- | ------------------------------- |
| **IaC**             | Terraform      | 1.7+    | Provisioning de infraestructura |
| **Cloud Provider**  | AWS            | -       | Proveedor de nube               |
| **CI/CD**           | GitHub Actions | -       | Plan automático y apply         |
| **IaC Scanning**    | Checkov        | 3.0+    | Security y compliance scanning  |
| **Cost Estimation** | Infracost      | 0.10+   | Estimación de costos en PRs     |

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
│   └── rds-postgres/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── production/
├── .terraform-version
└── README.md
```

---

## Módulo ECS Service

```hcl
# modules/ecs-service/main.tf
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
  name            = var.service_name
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.service.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

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
  tags                              = var.common_tags
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
  type    = list(object({ name = string, arn = string }))
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
    tags = { Environment = "production", ManagedBy = "Terraform" }
  }
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
```

---

## IaC Workflow

Pipeline automatizado de CI/CD para Terraform: plan en PRs, aprobación manual para staging/prod, y apply automático en dev.

**Beneficios:**
✅ No acceso directo a AWS Console (IaC only)
✅ Plan visible en PR antes de aprobar
✅ Checkov verifica seguridad antes del apply
✅ Rollback mediante Git revert

```yaml
# .github/workflows/terraform.yml
name: Terraform CI/CD

on:
  pull_request:
    paths: ["terraform/**"]
  push:
    branches: [main]
    paths: ["terraform/**"]

env:
  TF_VERSION: "1.7.0"
  AWS_REGION: "us-east-1"

jobs:
  terraform-plan:
    name: Terraform Plan
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    strategy:
      matrix:
        environment: [dev, staging, production]

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-terraform
          aws-region: ${{ env.AWS_REGION }}

      - name: Terraform Format Check
        working-directory: terraform/environments/${{ matrix.environment }}
        run: terraform fmt -check -recursive

      - name: Terraform Init + Validate
        working-directory: terraform/environments/${{ matrix.environment }}
        run: terraform init -input=false && terraform validate

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/environments/${{ matrix.environment }}
          framework: terraform
          output_format: sarif
          output_file_path: checkov-${{ matrix.environment }}.sarif
          soft_fail: false

      - name: Terraform Plan
        id: plan
        working-directory: terraform/environments/${{ matrix.environment }}
        run: |
          terraform plan -input=false -no-color -out=tfplan
          terraform show -no-color tfplan > plan-output.txt
        continue-on-error: true

      - name: Comment PR with plan
        uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const planOutput = fs.readFileSync(
              'terraform/environments/${{ matrix.environment }}/plan-output.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Terraform Plan — \`${{ matrix.environment }}\`\n\n<details><summary>Show Plan</summary>\n\n\`\`\`terraform\n${planOutput.slice(0, 65000)}\n\`\`\`\n\n</details>`
            });

  # Apply automático a dev; aprobación manual para staging/prod
  terraform-apply:
    name: Terraform Apply
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    strategy:
      matrix:
        environment: [dev, staging, production]
      max-parallel: 1
    environment:
      name: ${{ matrix.environment }}

    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-terraform
          aws-region: ${{ env.AWS_REGION }}
      - run: terraform init -input=false
        working-directory: terraform/environments/${{ matrix.environment }}
      - run: terraform apply -input=false -auto-approve
        working-directory: terraform/environments/${{ matrix.environment }}
```

---

## Code Review Checklist

```markdown
## Terraform Code Review Checklist

### General

- [ ] `terraform fmt` ejecutado
- [ ] No hardcoded values (usar variables)
- [ ] Variables tienen `description`

### Security

- [ ] No secrets hardcoded
- [ ] Security groups con least privilege
- [ ] Encryption at rest habilitado
- [ ] IAM roles con least privilege
- [ ] S3 buckets con public access blocked

### Cost

- [ ] Instance sizes apropiados (no over-provisioned)
- [ ] Tags obligatorios presentes: Environment, ManagedBy, Service, CostCenter, Owner

### State y Data Safety

- [ ] Backend configurado correctamente
- [ ] State files excluidos de Git (.gitignore)
- [ ] Deletion protection en recursos críticos (RDS, S3)

### Testing

- [ ] Plan reviewed — no unexpected changes
- [ ] Checkov scan passed
- [ ] Infracost cost impact aceptable
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Terraform como única herramienta de IaC (sin cambios manuales en consola AWS)
- **MUST** estructura modular: separar `modules/` de `environments/`
- **MUST** aplicar tags obligatorios a todos los recursos: `Environment`, `ManagedBy`, `Service`, `CostCenter`, `Owner`
- **MUST** PR requerido para cualquier cambio de infraestructura
- **MUST** `terraform plan` visible como comentario en el PR antes de aprobar
- **MUST** aprobación de al menos un revisor antes de apply en staging/producción
- **MUST** Checkov scan passing antes de merge
- **MUST** usar GitHub Actions environments con aprobación manual para staging y producción

### SHOULD (Fuertemente recomendado)

- **SHOULD** Infracost integrado en PRs para estimación de costo
- **SHOULD** multi-AZ para recursos de alta disponibilidad (ECS, RDS)
- **SHOULD** apply automático a dev en merge a main; aprobación manual para staging/producción

### MUST NOT (Prohibido)

- **MUST NOT** hacer cambios manuales en AWS Console
- **MUST NOT** hardcodear secrets en código Terraform
- **MUST NOT** omitir tags obligatorios
- **MUST NOT** hacer cambios de infraestructura sin PR (no direct push a main)

---

## Referencias

- [Terraform Documentation](https://www.terraform.io/docs) — referencia oficial de Terraform
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) — recursos AWS
- [Checkov Documentation](https://www.checkov.io/) — seguridad y compliance en IaC
- [Infracost](https://www.infracost.io/docs/) — estimación de costos en Terraform
- [GitHub Actions: Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) — aprobaciones manuales en CD
- [IaC — State y Gestión de Drift](./iac-state-management.md) — gestión de state y detección de cambios
- [Contenerización](./containerization.md) — imágenes Docker desplegadas con este módulo ECS
- [Redes Virtuales](./virtual-networks.md) — módulo VPC usado en environment configuration
