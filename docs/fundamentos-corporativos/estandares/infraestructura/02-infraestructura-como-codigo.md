---
id: infraestructura-como-codigo
sidebar_position: 2
title: Infraestructura como Código
description: Estándares para definir, provisionar y gestionar infraestructura mediante código
---

**Versiones mínimas requeridas:**

- Terraform: 1.6+
- AWS CDK: 2.100+ (si aplica)
- Pulumi: 3.80+ (si aplica)

## 1. Principios

- **Everything as Code**: Toda infraestructura debe estar definida como código.
- **Versionado**: Código de infraestructura debe estar en repositorios Git.
- **Inmutabilidad**: Preferir recrear recursos en lugar de modificarlos.
- **Idempotencia**: Aplicar el mismo código múltiples veces produce el mismo resultado.
- **Revisión**: Todo cambio de infraestructura debe pasar por code review (PR).

## 2. Herramientas Recomendadas

### Terraform (Recomendado)

- **Uso**: Infraestructura multi-cloud, recursos de AWS, networking, bases de datos.
- **Ventajas**: Agnóstico de cloud, amplia comunidad, state management robusto.

### AWS CDK

- **Uso**: Infraestructura específica de AWS usando lenguajes de programación (C#, TypeScript).
- **Ventajas**: Type-safe, reutilización de código, integración nativa con AWS.

## 3. Estructura de Proyecto Terraform

```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── ecs-service/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   └── rds-postgres/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── README.md
└── README.md
```

## 4. Ejemplo de Módulo Terraform

### modules/ecs-service/main.tf

```hcl
resource "aws_ecs_task_definition" "this" {
  family                   = var.service_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn           = var.task_role_arn

  container_definitions = jsonencode([{
    name      = var.service_name
    image     = var.image
    essential = true

    portMappings = [{
      containerPort = var.container_port
      protocol      = "tcp"
    }]

    environment = var.environment_variables

    secrets = var.secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${var.service_name}"
        "awslogs-region"        = var.region
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
  }])

  tags = merge(var.tags, {
    Name        = var.service_name
    ManagedBy   = "Terraform"
    Environment = var.environment
  })
}

resource "aws_ecs_service" "this" {
  name            = var.service_name
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = var.security_group_ids
    assign_public_ip = var.assign_public_ip
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.service_name
    container_port   = var.container_port
  }

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  tags = merge(var.tags, {
    Name        = var.service_name
    ManagedBy   = "Terraform"
    Environment = var.environment
  })
}
```

### modules/ecs-service/variables.tf

```hcl
variable "service_name" {
  description = "Nombre del servicio ECS"
  type        = string
}

variable "environment" {
  description = "Entorno (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment debe ser dev, staging o production."
  }
}

variable "cpu" {
  description = "CPU units para la tarea"
  type        = number
  default     = 256
}

variable "memory" {
  description = "Memoria en MB para la tarea"
  type        = number
  default     = 512
}

variable "image" {
  description = "Imagen Docker completa (registry/image:tag)"
  type        = string
}

variable "container_port" {
  description = "Puerto del contenedor"
  type        = number
  default     = 80
}

variable "desired_count" {
  description = "Número de tareas deseadas"
  type        = number
  default     = 2
}

variable "tags" {
  description = "Tags comunes para todos los recursos"
  type        = map(string)
  default     = {}
}
```

## 5. State Management

### Remote State con S3 y DynamoDB

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "talma-terraform-state"
    key            = "environments/production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"

    # Usar profile específico o IAM role
    profile = "talma-production"
  }
}
```

### Crear bucket y tabla de lock

```hcl
# setup/backend-resources.tf
resource "aws_s3_bucket" "terraform_state" {
  bucket = "talma-terraform-state"

  tags = {
    Name      = "Terraform State"
    ManagedBy = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "terraform-state-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name      = "Terraform State Lock"
    ManagedBy = "Terraform"
  }
}
```

## 6. Gestión de Secretos

```hcl
# ❌ INCORRECTO - Secretos hardcodeados
resource "aws_db_instance" "this" {
  username = "admin"
  password = "supersecret123"  # NUNCA hacer esto
}

# ✅ CORRECTO - Usar AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "rds/production/master-password"
}

resource "aws_db_instance" "this" {
  username = "admin"
  password = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["password"]
}

# ✅ CORRECTO - Usar variables de entorno o archivos .tfvars (no commiteados)
variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

resource "aws_db_instance" "this" {
  username = "admin"
  password = var.db_password
}
```

### .gitignore para Terraform

```
# .gitignore
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl
terraform.tfvars
*.tfvars
!terraform.tfvars.example
override.tf
override.tf.json
*_override.tf
*_override.tf.json
crash.log
```

## 7. Buenas Prácticas

### Naming Conventions

```hcl
# Recursos
resource "aws_vpc" "main" {
  # Usar nombres descriptivos y consistentes
  cidr_block = "10.0.0.0/16"

  tags = {
    Name        = "talma-${var.environment}-vpc"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "talma-platform"
  }
}

# Variables
variable "environment" {
  description = "Nombre del entorno"
  type        = string
}

variable "vpc_cidr_block" {
  description = "CIDR block para VPC"
  type        = string
  default     = "10.0.0.0/16"
}
```

### Outputs

```hcl
# outputs.tf
output "vpc_id" {
  description = "ID de la VPC creada"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs de las subnets privadas"
  value       = aws_subnet.private[*].id
}

output "database_endpoint" {
  description = "Endpoint de la base de datos"
  value       = aws_db_instance.this.endpoint
  sensitive   = true
}
```

### Validaciones

```hcl
variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t3.micro"

  validation {
    condition     = can(regex("^t3\\.(micro|small|medium)$", var.instance_type))
    error_message = "Instance type debe ser t3.micro, t3.small o t3.medium."
  }
}
```

## 8. Workflow de Terraform

```bash
# 1. Inicializar (solo primera vez o cambios en providers)
terraform init

# 2. Validar sintaxis
terraform validate

# 3. Formatear código
terraform fmt -recursive

# 4. Plan (siempre antes de apply)
terraform plan -out=tfplan

# 5. Aplicar cambios
terraform apply tfplan

# 6. Ver estado actual
terraform show

# 7. Destruir recursos (con precaución)
terraform destroy
```

## 9. CI/CD para IaC

### GitHub Actions ejemplo

```yaml
name: Terraform

on:
  pull_request:
    paths:
      - "infrastructure/**"
  push:
    branches:
      - main
    paths:
      - "infrastructure/**"

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0

      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/environments/production

      - name: Terraform Validate
        run: terraform validate
        working-directory: infrastructure/environments/production

      - name: Terraform Format Check
        run: terraform fmt -check -recursive
        working-directory: infrastructure

      - name: Terraform Plan
        if: github.event_name == 'pull_request'
        run: terraform plan
        working-directory: infrastructure/environments/production

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve
        working-directory: infrastructure/environments/production
```

## 📖 Referencias

### Lineamientos relacionados

- [Infraestructura como Código](/docs/fundamentos-corporativos/lineamientos/operabilidad/infraestructura-como-codigo)
- [Automatización](/docs/fundamentos-corporativos/lineamientos/operabilidad/automatizacion)

### ADRs relacionados

- [ADR-006: Infraestructura como Código](/docs/decisiones-de-arquitectura/adr-006-infraestructura-iac)

### Recursos externos

- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS CDK Best Practices](https://docs.aws.amazon.com/cdk/v2/guide/best-practices.html)
- [Terraform Registry](https://registry.terraform.io/)
