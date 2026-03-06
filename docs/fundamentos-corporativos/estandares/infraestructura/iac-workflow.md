---
id: iac-workflow
sidebar_position: 3
title: IaC — Workflow y Code Review
description: Estándares para el workflow CI/CD de Terraform, incluyendo plan automático en PRs, Checkov, Infracost y proceso de revisión de cambios de infraestructura.
tags: [infraestructura, terraform, iac, github-actions, code-review]
---

# IaC — Workflow y Code Review

## Contexto

Los cambios de infraestructura siguen el mismo proceso de revisión que el código de aplicación: PR con plan automático, revisión técnica, aprobación y apply automatizado. Este estándar define el pipeline y el proceso de code review para Terraform. Complementa el lineamiento [Infraestructura como Código](../../lineamientos/operabilidad/02-infraestructura-como-codigo.md).

**Conceptos incluidos:**

- **IaC Workflow** → Pipeline CI/CD con plan en PR y apply en merge
- **IaC Code Review** → Proceso de revisión, checklist y PR template

---

## Stack Tecnológico

| Componente          | Tecnología     | Versión | Uso                         |
| ------------------- | -------------- | ------- | --------------------------- |
| **IaC**             | Terraform      | 1.7+    | Infraestructura como código |
| **CI/CD**           | GitHub Actions | -       | Plan automático y apply     |
| **IaC Scanning**    | Checkov        | 3.0+    | Security y compliance       |
| **Cost Estimation** | Infracost      | 0.10+   | Estimación de costos en PRs |

---

## IaC Workflow

Workflow automatizado de CI/CD para Terraform que ejecuta plan en PRs, requiere approval, y aplica cambios automáticamente después de merge.

**Propósito:** Prevenir cambios manuales, requerir review, y automatizar aplicación de infraestructura.

**Beneficios:**
✅ No acceso directo a AWS Console (IaC only)
✅ Plan visible en PR antes de aprobar
✅ Checkov verifica seguridad antes del apply
✅ Rollback mediante Git revert

### GitHub Actions Workflow

```yaml
# .github/workflows/terraform.yml
name: Terraform CI/CD

on:
  pull_request:
    paths:
      - "terraform/**"
  push:
    branches:
      - main
    paths:
      - "terraform/**"

env:
  TF_VERSION: "1.7.0"
  AWS_REGION: "us-east-1"

jobs:
  # Plan en cada PR
  terraform-plan:
    name: Terraform Plan
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    strategy:
      matrix:
        environment: [dev, staging, production]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-terraform
          aws-region: ${{ env.AWS_REGION }}

      - name: Terraform Format Check
        working-directory: terraform/environments/${{ matrix.environment }}
        run: terraform fmt -check -recursive

      - name: Terraform Init
        working-directory: terraform/environments/${{ matrix.environment }}
        run: terraform init -input=false

      - name: Terraform Validate
        working-directory: terraform/environments/${{ matrix.environment }}
        run: terraform validate

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/environments/${{ matrix.environment }}
          framework: terraform
          output_format: sarif
          output_file_path: checkov-${{ matrix.environment }}.sarif
          soft_fail: false

      - name: Upload Checkov results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: checkov-${{ matrix.environment }}.sarif

      - name: Terraform Plan
        id: plan
        working-directory: terraform/environments/${{ matrix.environment }}
        run: |
          terraform plan -input=false -no-color -out=tfplan
          terraform show -no-color tfplan > plan-output.txt
        continue-on-error: true

      - name: Setup Infracost
        uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate Infracost diff
        working-directory: terraform/environments/${{ matrix.environment }}
        run: |
          infracost breakdown --path . --format json --out-file infracost-${{ matrix.environment }}.json

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
              body: `## Terraform Plan — \`${{ matrix.environment }}\`\n\n<details><summary>Show Plan</summary>\n\n\`\`\`terraform\n${planOutput.slice(0, 65000)}\n\`\`\`\n\n</details>\n\n**Plan Status**: ${{ steps.plan.outcome }}`
            });

      - name: Fail if plan failed
        if: steps.plan.outcome == 'failure'
        run: exit 1

  # Apply en merge a main (dev automático)
  terraform-apply:
    name: Terraform Apply — Dev
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment:
      name: dev

    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-terraform
          aws-region: ${{ env.AWS_REGION }}

      - name: Terraform Init
        working-directory: terraform/environments/dev
        run: terraform init -input=false

      - name: Terraform Apply
        working-directory: terraform/environments/dev
        run: terraform apply -input=false -auto-approve

  # Apply staging/prod con aprobación manual
  terraform-apply-prod:
    name: Terraform Apply — Staging/Prod
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: terraform-apply

    strategy:
      matrix:
        environment: [staging, production]
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

## IaC Code Review

Revisión de cambios de infraestructura antes de aplicarlos, igual que code reviews de aplicación.

**Propósito:** Prevenir errores costosos, validar seguridad, compartir conocimiento del equipo.

### Code Review Checklist

```markdown
## Terraform Code Review Checklist

### General

- [ ] `terraform fmt` ejecutado
- [ ] No hay hardcoded values (usar variables)
- [ ] Variables tienen `description`
- [ ] README actualizado si es módulo

### Security

- [ ] No secrets hardcoded
- [ ] Security groups con least privilege
- [ ] Encryption at rest habilitado
- [ ] IAM roles con least privilege
- [ ] S3 buckets con public access blocked

### Networking

- [ ] Recursos en subnets apropiadas (public/private)
- [ ] Multi-AZ para alta disponibilidad

### Cost

- [ ] Instance sizes apropiados (no over-provisioned)
- [ ] Auto-scaling configurado
- [ ] Tags para cost allocation presentes

### Tagging

- [ ] Tags obligatorios presentes: Environment, ManagedBy, Service, CostCenter, Owner

### State Management

- [ ] Backend configurado correctamente
- [ ] State files excluidos de Git (.gitignore)

### Data Safety

- [ ] Deletion protection en recursos críticos (RDS, S3)
- [ ] `create_before_destroy` para zero-downtime upgrades

### Testing

- [ ] Plan reviewed — no unexpected changes
- [ ] Checkov scan passed
- [ ] Infracost cost impact aceptable
```

### Pull Request Template

````markdown
## Terraform Change Request

### Description

Brief description of infrastructure changes.

### Resources Changed

- [ ] New resources created
- [ ] Existing resources modified
- [ ] Resources deleted

### Checklist

- [ ] `terraform fmt` executed
- [ ] `terraform validate` passed
- [ ] Checkov scan passed
- [ ] Plan output reviewed
- [ ] Cost impact reviewed (Infracost)


### Terraform Plan Output

<details>

<summary>Show Plan</summary>

```terraform

# Plan output posted automatically by GitHub Actions
```
````


</details>


### Cost Impact

- **Estimated monthly cost change**: +$XX USD

### Rollback Plan

1. ...

### Testing

- [ ] Tested in dev environment
- [ ] Validated in staging

### Related Issues

Fixes #XXX

```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** PR requerido para cualquier cambio de infraestructura
- **MUST** `terraform plan` visible como comentario en el PR antes de aprobar
- **MUST** aprobación de al menos un revisor antes de apply en staging/producción
- **MUST** Checkov scan passing antes de merge
- **MUST** usar GitHub Actions environments con aprobación manual para staging y producción

### SHOULD (Fuertemente recomendado)

- **SHOULD** Infracost comment en PR con impacto de costo estimado
- **SHOULD** apply automático a dev en merge a main; aprobación manual para staging/producción

### MUST NOT (Prohibido)

- **MUST NOT** usar `terraform apply` manual en producción sin registro de aprobación
- **MUST NOT** hacer cambios de infraestructura sin PR (no direct push a main)

---

## Referencias

- [Terraform Documentation](https://www.terraform.io/docs) — referencia oficial
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) — recursos AWS
- [Checkov Documentation](https://www.checkov.io/) — security scanning para IaC
- [Infracost](https://www.infracost.io/docs/) — estimación de costos en Terraform
- [GitHub Actions: Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) — aprobaciones manuales en CD
- [IaC — Implementación con Terraform](./iac-implementation.md) — estructura de proyecto y módulos
- [IaC — State y Drift Detection](./iac-state-drift.md) — gestión de state y detección de cambios
```
