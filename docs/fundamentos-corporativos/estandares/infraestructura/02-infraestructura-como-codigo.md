---
id: infraestructura-como-codigo
sidebar_position: 2
title: Infraestructura como Código (IaC)
description: Estándar técnico obligatorio para definir, provisionar y gestionar infraestructura cloud mediante Terraform con state remoto, módulos reutilizables y GitOps
---

# Infraestructura como Código (IaC)

## 1. Propósito

Definir la configuración técnica obligatoria para gestionar infraestructura cloud como código mediante:
- **Terraform** como herramienta principal (1.6+) con HCL declarativo
- **State remoto** en S3 con DynamoDB locking para trabajo colaborativo
- **Módulos reutilizables** para VPC, ECS, RDS con versionado semántico
- **GitOps workflow** con PR reviews, plan automático, apply manual
- **Separación de entornos** (dev, staging, production) con workspaces

Garantiza infraestructura reproducible, auditable, versionada y con zero-drift.

## 2. Alcance

### Aplica a:

- ✅ Toda infraestructura AWS (VPC, ECS, RDS, S3, IAM, etc.)
- ✅ Recursos cloud en dev, staging, production
- ✅ Networking, compute, storage, databases, seguridad
- ✅ Infraestructura compartida (VPCs, subnets, security groups)

### NO aplica a:

- ❌ Configuraciones dentro de contenedores (usar variables de entorno)
- ❌ Código de aplicación (deployment se gestiona con CI/CD)
- ❌ Secretos (usar AWS Secrets Manager, NO Terraform state)
- ❌ Cambios manuales urgentes (documentar y revertir a código ASAP)

## 3. Tecnologías Obligatorias

| Categoría          | Tecnología / Configuración                | Versión   | Justificación                           |
| ------------------ | ----------------------------------------- | --------- | --------------------------------------- |
| **IaC Tool**       | Terraform                                 | 1.6+      | Agnóstico cloud, state management robusto |
| **State Backend**  | S3 + DynamoDB                             | -         | State remoto compartido con locking     |
| **Registry**       | Terraform Registry (público/privado)      | -         | Módulos versionados y reutilizables     |
| **Validation**     | `terraform fmt`, `terraform validate`     | Built-in  | Sintaxis y formato consistente          |
| **Linting**        | tflint                                    | 0.50+     | Detecta errores y malas prácticas       |
| **Security Scan**  | Checkov, tfsec                            | Latest    | Detecta vulnerabilidades de seguridad   |
| **CI/CD**          | GitHub Actions, GitLab CI                 | -         | Automatización de plan/apply            |

### Herramientas Alternativas (Casos Específicos)

| Herramienta | Uso Recomendado                           | Cuándo Usar                          |
| ----------- | ----------------------------------------- | ------------------------------------ |
| AWS CDK     | Infraestructura compleja específica AWS   | Si se requiere lógica compleja en C#/TS |
| Pulumi      | Multi-cloud con lenguajes generales       | Equipos sin experiencia en HCL       |

## 4. Configuración Técnica Obligatoria

### 4.1 Estructura de Proyecto Terraform

```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   ├── backend.tf
│   │   └── outputs.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   ├── backend.tf
│   │   └── outputs.tf
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       ├── backend.tf
│       └── outputs.tf
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── README.md
│   │   └── versions.tf
│   ├── ecs-service/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── README.md
│   │   └── versions.tf
│   └── rds-postgres/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       ├── README.md
│       └── versions.tf
├── .tflint.hcl
├── .terraform-version
└── README.md
```

### 4.2 Backend Remoto con S3 + DynamoDB

```hcl
# environments/production/backend.tf
terraform {
  backend "s3" {
    bucket         = "talma-terraform-state-prod"
    key            = "production/infrastructure.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "talma-terraform-locks"
    
    # ✅ Versionado de state
    versioning = true
    
    # ✅ Tags para auditoría
    tags = {
      Environment = "production"
      ManagedBy   = "Terraform"
      Team        = "Platform"
    }
  }
  
  required_version = ">= 1.6.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

### 4.3 Configuración de Provider AWS

```hcl
# environments/production/main.tf
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = "production"
      ManagedBy   = "Terraform"
      Project     = "Talma Platform"
      Owner       = "Platform Team"
    }
  }
  
  # ✅ Asumir rol con permisos mínimos
  assume_role {
    role_arn = "arn:aws:iam::123456789012:role/TerraformExecutionRole"
  }
}

# ✅ Data sources para información existente
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}
```

### 4.4 Variables con Validación

```hcl
# environments/production/variables.tf
variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production"
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block"
  }
}

variable "ecs_task_cpu" {
  description = "CPU units for ECS task (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 256
  
  validation {
    condition     = contains([256, 512, 1024, 2048, 4096], var.ecs_task_cpu)
    error_message = "CPU must be a valid Fargate CPU value"
  }
}

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  
  validation {
    condition     = can(regex("^db\\.", var.rds_instance_class))
    error_message = "Instance class must start with 'db.'"
  }
}
```

### 4.5 Outputs para Interoperabilidad

```hcl
# environments/production/outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = module.vpc.private_subnet_ids
}

output "ecs_cluster_name" {
  description = "Name of ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.endpoint
  sensitive   = false # Endpoint NO es secreto (host:port público)
}

output "rds_password_secret_arn" {
  description = "ARN of secret containing RDS password"
  value       = aws_secretsmanager_secret.rds_password.arn
  sensitive   = true # ✅ Marcar secretos como sensitive
}
```

## 5. Ejemplos de Implementación

### 5.1 Módulo VPC Reutilizable

```hcl
# modules/vpc/main.tf
terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-vpc"
  })
}

resource "aws_subnet" "private" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = var.availability_zones[count.index]
  
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-private-${var.availability_zones[count.index]}"
    Tier = "private"
  })
}

resource "aws_subnet" "public" {
  count = length(var.availability_zones)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-public-${var.availability_zones[count.index]}"
    Tier = "public"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-igw"
  })
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? length(var.availability_zones) : 0
  domain = "vpc"
  
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-eip-nat-${count.index + 1}"
  })
  
  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? length(var.availability_zones) : 0
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(var.tags, {
    Name = "${var.name_prefix}-nat-${count.index + 1}"
  })
}

# modules/vpc/variables.tf
variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Whether to create NAT Gateways"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# modules/vpc/outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}
```

### 5.2 Uso del Módulo VPC

```hcl
# environments/production/main.tf
module "vpc" {
  source = "../../modules/vpc"
  
  name_prefix        = "talma-prod"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  enable_nat_gateway = true
  
  tags = {
    Environment = "production"
    Project     = "Talma Platform"
  }
}

module "ecs_cluster" {
  source = "../../modules/ecs-cluster"
  
  name_prefix = "talma-prod"
  vpc_id      = module.vpc.vpc_id
  
  tags = {
    Environment = "production"
  }
}

module "users_api_service" {
  source = "../../modules/ecs-service"
  
  service_name = "users-api"
  cluster_id   = module.ecs_cluster.cluster_id
  
  image          = "123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:v1.2.3"
  cpu            = 256
  memory         = 512
  desired_count  = 3
  container_port = 8080
  
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids = [aws_security_group.ecs_tasks.id]
  
  environment_variables = [
    {
      name  = "ASPNETCORE_ENVIRONMENT"
      value = "Production"
    },
    {
      name  = "ASPNETCORE_URLS"
      value = "http://+:8080"
    }
  ]
  
  secrets = [
    {
      name      = "ConnectionStrings__Default"
      valueFrom = aws_secretsmanager_secret.db_connection.arn
    }
  ]
  
  tags = {
    Environment = "production"
    Service     = "users-api"
  }
}
```

### 5.3 Módulo ECS Service

```hcl
# modules/ecs-service/main.tf
resource "aws_ecs_task_definition" "this" {
  family                   = var.service_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  
  container_definitions = jsonencode([{
    name      = var.service_name
    image     = var.image
    essential = true
    
    portMappings = [{
      containerPort = var.container_port
      protocol      = "tcp"
    }]
    
    environment = var.environment_variables
    secrets     = var.secrets
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${var.service_name}"
        "awslogs-region"        = data.aws_region.current.name
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
    Name = var.service_name
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
    assign_public_ip = false
  }
  
  dynamic "load_balancer" {
    for_each = var.target_group_arn != null ? [1] : []
    
    content {
      target_group_arn = var.target_group_arn
      container_name   = var.service_name
      container_port   = var.container_port
    }
  }
  
  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }
  
  tags = var.tags
}
```

## 6. Mejores Prácticas

### 6.1 GitOps Workflow

```bash
# 1. Crear feature branch
git checkout -b infra/add-rds-database

# 2. Modificar código Terraform
vim environments/production/main.tf

# 3. Formatear código
terraform fmt -recursive

# 4. Validar sintaxis
terraform validate

# 5. Plan (en CI/CD automático)
terraform plan -out=tfplan

# 6. Commit y push
git add .
git commit -m "feat(infra): add RDS PostgreSQL for users service"
git push origin infra/add-rds-database

# 7. Crear PR → CI ejecuta terraform plan automáticamente

# 8. Review de PR → Aprobar

# 9. Apply manual (con confirmación)
terraform apply tfplan

# 10. Merge PR a main
```

### 6.2 Naming Conventions

```hcl
# ✅ Patrón: {company}-{environment}-{resource}-{function}

resource "aws_ecs_cluster" "main" {
  name = "talma-prod-ecs-cluster"
}

resource "aws_s3_bucket" "logs" {
  bucket = "talma-prod-logs-${data.aws_caller_identity.current.account_id}"
}

resource "aws_security_group" "ecs_tasks" {
  name        = "talma-prod-sg-ecs-tasks"
  description = "Security group for ECS tasks"
  vpc_id      = module.vpc.vpc_id
}

# ✅ Tags consistentes
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "Talma Platform"
    Owner       = "Platform Team"
    CostCenter  = "Engineering"
  }
}

resource "aws_instance" "example" {
  # ...
  tags = merge(local.common_tags, {
    Name = "talma-prod-ec2-bastion"
  })
}
```

### 6.3 State Management

```bash
# ✅ Listar workspaces
terraform workspace list

# ✅ Crear nuevo workspace
terraform workspace new staging

# ✅ Cambiar de workspace
terraform workspace select production

# ✅ Ver state actual
terraform show

# ✅ Listar recursos en state
terraform state list

# ✅ Inspeccionar recurso específico
terraform state show aws_ecs_cluster.main

# ✅ Importar recurso existente
terraform import aws_s3_bucket.logs talma-prod-logs-123456789012

# ✅ Remover recurso del state (sin destruirlo)
terraform state rm aws_instance.temporary
```

## 7. Antipatrones (NO Hacer)

### ❌ Antipatrón 1: Hardcodear Valores en lugar de Variables

```hcl
# ❌ MAL - Valores hardcodeados
resource "aws_ecs_task_definition" "app" {
  family = "my-app"
  cpu    = 256
  memory = 512
  # Difícil de reutilizar, no parametrizable
}

# ✅ BIEN - Usar variables
variable "service_name" {
  description = "Name of the service"
  type        = string
}

variable "cpu" {
  description = "CPU units"
  type        = number
  default     = 256
}

variable "memory" {
  description = "Memory in MB"
  type        = number
  default     = 512
}

resource "aws_ecs_task_definition" "app" {
  family = var.service_name
  cpu    = var.cpu
  memory = var.memory
}
```

**Problema**: Código no reutilizable, difícil de adaptar a diferentes entornos.  
**Solución**: Parametrizar con variables, valores por defecto razonables, validaciones.

### ❌ Antipatrón 2: State Local en lugar de Remoto

```hcl
# ❌ MAL - State local (terraform.tfstate en filesystem)
# No hay backend configurado → state queda en disco local
# Problemas: no compartido, sin locking, fácil de perder

# ✅ BIEN - State remoto con locking
terraform {
  backend "s3" {
    bucket         = "talma-terraform-state-prod"
    key            = "production/infrastructure.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "talma-terraform-locks"
  }
}
```

**Problema**: State local no se comparte con equipo, sin locking (corrupciones), fácil de perder.  
**Solución**: Backend S3 + DynamoDB para state compartido, versionado, con locking.

### ❌ Antipatrón 3: No Usar Módulos (Código Duplicado)

```hcl
# ❌ MAL - Repetir configuración en cada entorno
# environments/dev/main.tf
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  # ... 50 líneas de configuración ...
}

# environments/staging/main.tf
resource "aws_vpc" "main" {
  cidr_block = "10.1.0.0/16"
  # ... 50 líneas duplicadas ...
}

# environments/production/main.tf
resource "aws_vpc" "main" {
  cidr_block = "10.2.0.0/16"
  # ... 50 líneas duplicadas ...
}

# ✅ BIEN - Módulo reutilizable
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  # ...
}

# environments/production/main.tf
module "vpc" {
  source   = "../../modules/vpc"
  vpc_cidr = "10.2.0.0/16"
}
```

**Problema**: Código duplicado, inconsistencias entre entornos, difícil mantenimiento.  
**Solución**: Módulos reutilizables con variables, DRY principle, versionado de módulos.

### ❌ Antipatrón 4: Secretos en Terraform Code o State

```hcl
# ❌ MAL - Password hardcodeado en código
resource "aws_db_instance" "main" {
  username = "admin"
  password = "SuperSecretPassword123!" # ❌ En Git y en state
}

# ✅ BIEN - Secreto en Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name = "prod/rds/master-password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db.result
}

resource "random_password" "db" {
  length  = 32
  special = true
}

resource "aws_db_instance" "main" {
  username               = "admin"
  password               = random_password.db.result
  manage_master_user_password = false
}

# ✅ Referencia al secreto (NO al valor)
output "db_password_secret_arn" {
  value     = aws_secretsmanager_secret.db_password.arn
  sensitive = true
}
```

**Problema**: Secretos en Git y state file (plaintext), exposición de credenciales.  
**Solución**: AWS Secrets Manager, `random_password`, outputs sensitive, NO valores en código.

## 8. Validación y Cumplimiento

### 8.1 Checklist de Implementación

- [ ] **Backend S3** configurado con encryption y DynamoDB locking
- [ ] **Variables** parametrizadas con validaciones
- [ ] **Módulos** creados para recursos reutilizables (VPC, ECS, RDS)
- [ ] **Tags** aplicados consistentemente a todos los recursos
- [ ] **Outputs** definidos para interoperabilidad
- [ ] **terraform fmt** ejecutado en pre-commit hook
- [ ] **terraform validate** pasando sin errores
- [ ] **tflint** configurado y pasando
- [ ] **Checkov/tfsec** ejecutado (0 HIGH/CRITICAL)
- [ ] **GitOps** workflow implementado (PR → Plan → Review → Apply)
- [ ] **Secretos** NO en código ni state (usar Secrets Manager)
- [ ] **Documentación** README.md actualizado con uso de módulos

### 8.2 Métricas de Cumplimiento

| Métrica                              | Target       | Verificación                        |
| ------------------------------------ | ------------ | ----------------------------------- |
| Recursos gestionados por Terraform   | 100%         | `terraform state list` vs AWS Console |
| Drift detectado                      | 0%           | `terraform plan` sin cambios        |
| Secretos en state file               | 0            | Grep state por passwords/keys       |
| Módulos reutilizados                 | ≥ 80%        | Count de module blocks vs resources |
| PRs con terraform plan automático    | 100%         | CI/CD logs                          |
| Vulnerabilidades HIGH/CRITICAL       | 0            | Checkov/tfsec scan                  |

## 9. Referencias

### Estándares Relacionados

- [Docker](./01-docker.md) - Imágenes para desplegar en ECS
- [Secrets Management](./03-secrets-management.md) - Gestión de secretos en Terraform
- [Docker Compose](./04-docker-compose.md) - Orquestación local antes de IaC

### Convenciones Relacionadas

- [Naming AWS](../../convenciones/infraestructura/01-naming-aws.md) - Nomenclatura de recursos AWS
- [Tags y Metadatos](../../convenciones/infraestructura/02-tags-metadatos.md) - Etiquetado de recursos
- [Variables de Entorno](../../convenciones/infraestructura/03-variables-entorno.md) - Gestión de configuración

### Lineamientos Relacionados

- [Despliegue y DevOps](../../lineamientos/desarrollo/despliegue-y-devops.md) - CI/CD con Terraform
- [Seguridad en Infraestructura](../../lineamientos/seguridad/seguridad-infraestructura.md) - Security best practices

### Principios Relacionados

- [Automatización](../../principios/arquitectura/09-automatizacion.md) - Infraestructura automatizada
- [Reproducibilidad](../../principios/arquitectura/10-reproducibilidad.md) - Environments idénticos

### ADRs Relacionados

- [ADR-006: Infraestructura como Código](../../../decisiones-de-arquitectura/adr-006-infraestructura-iac.md)
- [ADR-003: Gestión de Secretos](../../../decisiones-de-arquitectura/adr-003-gestion-secretos.md)

### Documentación Externa

- [Terraform Best Practices](https://www.terraform-best-practices.com/) - Community guide
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) - Official docs
- [tflint](https://github.com/terraform-linters/tflint) - Linter pluggable
- [Checkov](https://www.checkov.io/) - Security scanner IaC

---

**Última actualización**: 27 de enero 2026  
**Responsable**: Equipo de Arquitectura
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
