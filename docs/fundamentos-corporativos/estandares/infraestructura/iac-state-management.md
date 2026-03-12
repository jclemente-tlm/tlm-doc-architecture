---
id: iac-state-management
sidebar_position: 3
title: IaC — Gestión de State y Drift
description: Estándares para gestión del Terraform state en S3, versionamiento de módulos y providers, y detección automatizada de drift en infraestructura AWS.
tags: [infraestructura, terraform, iac, state, drift, versionamiento]
---

# IaC — Gestión de State y Drift

## Contexto

El state de Terraform es la fuente de verdad del estado actual de la infraestructura. Este estándar define cómo gestionar el state de forma segura, versionar módulos y providers, y detectar cambios manuales (drift) que rompan la consistencia entre IaC y la infraestructura real. Complementa el lineamiento [Infraestructura como Código](../../lineamientos/operabilidad/infraestructura-como-codigo.md).

**Conceptos incluidos:**

- **State Management** → Backend S3 con locking DynamoDB
- **IaC Versioning** → Pinning de modules y providers
- **Drift Detection** → Detección y remediación de cambios manuales

:::note Implementación gestionada por Plataforma
Este estándar define los **requisitos de gestión de estado e integridad** que todo módulo IaC debe cumplir. La configuración del backend S3/DynamoDB y la automatización de detección de drift son responsabilidad del equipo de **Plataforma**. Consultar en **#platform-support**.
:::

---

## Stack Tecnológico

| Componente          | Tecnología     | Versión | Uso                              |
| ------------------- | -------------- | ------- | -------------------------------- |
| **IaC**             | Terraform      | 1.7+    | Infraestructura como código      |
| **State Backend**   | AWS S3         | -       | Almacenamiento de state          |
| **State Lock**      | AWS DynamoDB   | -       | Locking para prevenir conflictos |
| **Drift Detection** | GitHub Actions | -       | Detección diaria automatizada    |

---

## IaC State Management

Gestión segura y centralizada del Terraform state file en S3 con locking en DynamoDB para prevenir conflictos concurrentes.

**Propósito:** State compartido entre equipo, prevención de corrupción, backup automático con S3 versioning.

**Beneficios:**
✅ State compartido — no local
✅ Locking previene conflictos simultáneos
✅ Versionamiento con S3 versioning
✅ Encryption at rest

### Setup de Backend S3

```hcl
# terraform/backend-setup/main.tf — ejecutar una sola vez

resource "aws_s3_bucket" "terraform_state" {
  bucket = "talma-terraform-state"
  tags   = { Name = "Terraform State", ManagedBy = "Terraform" }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute { name = "LockID", type = "S" }
  tags = { Name = "Terraform State Lock", ManagedBy = "Terraform" }
}
```

### Backend Configuration por Ambiente

```hcl
# environments/production/backend.tf
terraform {
  backend "s3" {
    bucket         = "talma-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### Comandos útiles de State

```bash
# Listar recursos en state
terraform state list

# Inspeccionar recurso específico
terraform state show aws_ecs_service.customer_service

# Mover recurso en state (refactoring)
terraform state mv aws_security_group.old aws_security_group.new

# Importar recurso existente al state
terraform import aws_ecs_cluster.main production-cluster

# Eliminar recurso del state sin destruirlo
terraform state rm aws_instance.example

# Si el lock queda stuck (proceso crashed)
terraform force-unlock <LOCK_ID>
```

---

## IaC Versioning

Versionamiento de módulos Terraform, pinning de provider versions y tagging de releases de infraestructura.

**Propósito:** Reproducibilidad, rollback controlado y actualizaciones predecibles.

### Provider Version Constraints

```hcl
# terraform.tf
terraform {
  required_version = ">= 1.7.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Compatible con 5.x, no 6.x
    }
  }
}
```

### Módulos Versionados

```hcl
# Módulo desde Git con version tag
module "ecs_service" {
  source = "git::https://github.com/talma/terraform-modules.git//ecs-service?ref=v1.2.3"
}

# Alternativa: Terraform Registry
module "ecs_service" {
  source  = "talma/ecs-service/aws"
  version = "~> 1.2"  # Compatible con 1.2.x
}
```

### Sintaxis de Constraint

```hcl
version = "~> 1.2"     # >= 1.2.0, < 1.3.0  (recomendado)
version = "~> 1.2.3"   # >= 1.2.3, < 1.3.0
version = ">= 1.2.0"   # Mayor o igual
version = ">= 1.0, < 2.0"  # Rango explícito
```

### Terraform Version File

```
# .terraform-version (para tfenv / automático en CI)
1.7.0
```

### Release Tagging

```bash
# Tag de release de infraestructura
git tag -a infra-v1.2.3 -m "Release: Customer Service production deployment"
git push origin infra-v1.2.3

# Rollback a versión anterior
git checkout infra-v1.2.2
cd terraform/environments/production
terraform plan    # Revisar cambios de rollback
terraform apply   # Aplicar rollback
```

---

## Drift Detection

Detección de cambios manuales en infraestructura que no están reflejados en el Terraform state, y proceso de remediación.

**Propósito:** Mantener infraestructura consistente con IaC, detectar cambios no autorizados.

**Beneficios:**
✅ Detectar cambios manuales en consola AWS
✅ Compliance enforcement (nadie toca sin PR)
✅ Auditoría de cambios no autorizados

### Detección Manual

```bash
# Detectar drift (refresh-only plan)
terraform plan -refresh-only

# Ejemplo de salida con drift:
#   ~ resource "aws_security_group" "service" {
#       ~ ingress = [...] → [...]  # Cambio manual detectado

# Aplicar refresh al state (acepta cambios manuales como deseados)
terraform apply -refresh-only

# Alternativa: import y codificar el cambio
terraform import aws_security_group_rule.new_rule sg-xxxxx_ingress_tcp_443_443_10.0.0.0/16
```

### Detección Automatizada (Daily)

```yaml
# .github/workflows/drift-detection.yml
name: Drift Detection

on:
  schedule:
    - cron: "0 8 * * *" # Diario a las 8 AM UTC
  workflow_dispatch:

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, production]

    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-terraform
          aws-region: us-east-1

      - run: terraform init
        working-directory: terraform/environments/${{ matrix.environment }}

      - name: Detect Drift
        id: drift
        working-directory: terraform/environments/${{ matrix.environment }}
        run: |
          terraform plan -detailed-exitcode -no-color > plan-output.txt
          echo "exit_code=$?" >> $GITHUB_OUTPUT
        continue-on-error: true
        # Exit codes: 0=sin cambios, 1=error, 2=drift detectado

      - name: Notify Slack if drift
        if: steps.drift.outputs.exit_code == '2'
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
          payload: |
            { "text": "🚨 Drift detectado en `${{ matrix.environment }}`" }

      - name: Create Issue if drift
        if: steps.drift.outputs.exit_code == '2'
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const planOutput = fs.readFileSync(
              'terraform/environments/${{ matrix.environment }}/plan-output.txt', 'utf8');
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Drift Detected: ${{ matrix.environment }}',
              body: `**Environment**: ${{ matrix.environment }}\n\n\`\`\`terraform\n${planOutput}\n\`\`\``,
              labels: ['drift-detection', 'infrastructure']
            });
```

### Remediación de Drift

```bash
# Opción 1: el cambio manual era deseado → codificar en Terraform
resource "aws_security_group_rule" "new_rule" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.service.id
  cidr_blocks       = ["10.0.0.0/16"]
}

# Importar recurso existente al state y luego apply
terraform import aws_security_group_rule.new_rule sg-xxxxx_ingress_tcp_443_443_10.0.0.0/16
terraform plan   # Debe mostrar "No changes"

# Opción 2: el cambio manual NO era deseado → revertir
terraform apply  # Terraform revierte al estado definido en código
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** backend remoto en S3 con encryption habilitado
- **MUST** state locking con DynamoDB
- **MUST** S3 versioning habilitado en el bucket de state
- **MUST** S3 public access blocked en el bucket de state
- **MUST** pin de provider versions con constraint `~> X.Y`
- **MUST** terraform version constraint definido en cada módulo/environment

### SHOULD (Fuertemente recomendado)

- **SHOULD** drift detection automatizado diariamente
- **SHOULD** versionar módulos con Git tags (semver)
- **SHOULD** `.terraform-version` en raíz del proyecto para consistencia de versión

### MAY (Opcional)

- **MAY** usar Terraform Cloud para remote runs y drift detection continuo
- **MAY** aplicar Sentinel policies para governance de infraestructura

### MUST NOT (Prohibido)

- **MUST NOT** guardar state files en Git
- **MUST NOT** usar `terraform apply` sin review en producción
- **MUST NOT** hacer cambios manuales en AWS Console (genera drift)
- **MUST NOT** usar provider versions sin pin (`version = "latest"`)

---

## Referencias

- [Terraform S3 Backend](https://developer.hashicorp.com/terraform/language/settings/backends/s3) — configuración del backend remoto
- [Terraform State Management](https://developer.hashicorp.com/terraform/language/state) — conceptos de state en Terraform
- [Terraform Version Constraints](https://developer.hashicorp.com/terraform/language/expressions/version-constraints) — sintaxis de pinning de versiones
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) — mejores prácticas de infraestructura
- [IaC — Estándares Terraform](./iac-standards.md) — estructura de proyecto, módulos, workflow CI/CD y revisión de cambios
