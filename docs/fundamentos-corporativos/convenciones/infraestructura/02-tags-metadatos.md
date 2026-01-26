---
id: tags-metadatos
sidebar_position: 2
title: Tags y Metadatos
description: Convención para etiquetado de recursos cloud
---

## 1. Principio

Todos los recursos AWS deben tener tags consistentes para facilitar facturación, auditoría, automatización y gestión del ciclo de vida.

## 2. Reglas

### Regla 1: Tags Obligatorios

Estos tags **DEBEN** estar presentes en TODOS los recursos:

| Tag           | Descripción            | Valores Permitidos                      | Ejemplo                  |
| ------------- | ---------------------- | --------------------------------------- | ------------------------ |
| `Environment` | Ambiente del recurso   | `dev`, `qa`, `stg`, `prod`, `sbx`       | `prod`                   |
| `Project`     | Proyecto o aplicación  | Snake_case                              | `user_management`        |
| `Owner`       | Equipo responsable     | Email del líder técnico                 | `arquitectura@talma.com` |
| `CostCenter`  | Centro de costos       | Código contable                         | `IT-001`                 |
| `ManagedBy`   | Herramienta de gestión | `terraform`, `cloudformation`, `manual` | `terraform`              |

### Regla 2: Tags Recomendados

| Tag                  | Descripción                    | Ejemplo                                            |
| -------------------- | ------------------------------ | -------------------------------------------------- |
| `Name`               | Nombre descriptivo del recurso | `tlm-prod-users-api-ec2-01`                        |
| `Service`            | Servicio de negocio            | `users-api`, `orders-service`                      |
| `Version`            | Versión del software           | `v1.2.3`                                           |
| `Backup`             | Política de backup             | `daily`, `weekly`, `none`                          |
| `DataClassification` | Clasificación de datos         | `public`, `internal`, `confidential`, `restricted` |
| `ComplianceScope`    | Alcance de compliance          | `pci-dss`, `iso27001`, `sox`                       |

### Regla 3: Tags Opcionales

| Tag            | Descripción                 | Ejemplo                   |
| -------------- | --------------------------- | ------------------------- |
| `CreatedBy`    | Usuario que creó el recurso | `jperez@talma.com`        |
| `CreatedDate`  | Fecha de creación           | `2024-01-15`              |
| `BusinessUnit` | Unidad de negocio           | `operations`, `logistics` |
| `Country`      | País del servicio           | `PE`, `CO`, `CL`          |

## 3. Ejemplos de Tagging

### EC2 Instance

```hcl
resource "aws_instance" "api" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"

  tags = {
    Name                = "tlm-prod-users-api-ec2-01"
    Environment         = "prod"
    Project             = "user_management"
    Owner               = "arquitectura@talma.com"
    CostCenter          = "IT-001"
    ManagedBy           = "terraform"
    Service             = "users-api"
    Backup              = "daily"
    DataClassification  = "confidential"
  }
}
```

### S3 Bucket

```hcl
resource "aws_s3_bucket" "documents" {
  bucket = "tlm-prod-documents-pe-s3"

  tags = {
    Name                = "tlm-prod-documents-pe-s3"
    Environment         = "prod"
    Project             = "document_management"
    Owner               = "arquitectura@talma.com"
    CostCenter          = "IT-002"
    ManagedBy           = "terraform"
    DataClassification  = "restricted"
    ComplianceScope     = "iso27001"
    Country             = "PE"
  }
}
```

### RDS Database

```hcl
resource "aws_db_instance" "users" {
  identifier     = "tlm-prod-users-postgres-rds"
  engine         = "postgres"
  engine_version = "15.3"

  tags = {
    Name                = "tlm-prod-users-postgres-rds"
    Environment         = "prod"
    Project             = "user_management"
    Owner               = "arquitectura@talma.com"
    CostCenter          = "IT-001"
    ManagedBy           = "terraform"
    Backup              = "daily"
    DataClassification  = "confidential"
    ComplianceScope     = "pci-dss,iso27001"
  }
}
```

## 4. Estrategia de Facturación (Cost Allocation Tags)

Habilitar estos tags en AWS Cost Explorer:

1. `Environment` - Costos por ambiente
2. `Project` - Costos por proyecto
3. `CostCenter` - Asignación contable
4. `Owner` - Accountability de equipos

```bash
# Activar cost allocation tags
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status \
  TagKey=Environment,Status=Active \
  TagKey=Project,Status=Active \
  TagKey=CostCenter,Status=Active \
  TagKey=Owner,Status=Active
```

## 5. Políticas de Tag Compliance

### AWS Config Rule

```json
{
  "ConfigRuleName": "required-tags",
  "Description": "Verifica que todos los recursos tengan tags obligatorios",
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "REQUIRED_TAGS"
  },
  "InputParameters": {
    "tag1Key": "Environment",
    "tag2Key": "Project",
    "tag3Key": "Owner",
    "tag4Key": "CostCenter",
    "tag5Key": "ManagedBy"
  }
}
```

### Service Control Policy (SCP)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyEC2WithoutRequiredTags",
      "Effect": "Deny",
      "Action": "ec2:RunInstances",
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringNotLike": {
          "aws:RequestTag/Environment": ["dev", "qa", "stg", "prod", "sbx"],
          "aws:RequestTag/Owner": "*@talma.com"
        }
      }
    }
  ]
}
```

## 6. Herramientas de Validación

### Terraform Validation

```hcl
variable "required_tags" {
  type = map(string)
  default = {
    Environment = ""
    Project     = ""
    Owner       = ""
    CostCenter  = ""
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "example" {
  # ... other config ...

  tags = merge(
    var.required_tags,
    {
      Name    = "tlm-${var.environment}-example-ec2"
      Service = "example-api"
    }
  )

  lifecycle {
    precondition {
      condition     = alltrue([for k in keys(var.required_tags) : contains(keys(self.tags), k)])
      error_message = "Faltan tags obligatorios en el recurso."
    }
  }
}
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Verificar que todos los recursos Terraform tengan tags obligatorios
grep -r "resource \"aws_" terraform/ | while read -r line; do
  file=$(echo "$line" | cut -d: -f1)

  # Verificar tags obligatorios
  for tag in Environment Project Owner CostCenter ManagedBy; do
    if ! grep -q "$tag" "$file"; then
      echo "❌ Falta tag '$tag' en $file"
      exit 1
    fi
  done
done

echo "✅ Todos los tags obligatorios presentes"
```

## 7. Reporte de Compliance

### Script de Auditoría

```python
import boto3

required_tags = ['Environment', 'Project', 'Owner', 'CostCenter', 'ManagedBy']

ec2 = boto3.client('ec2')
instances = ec2.describe_instances()

non_compliant = []

for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

        missing_tags = [tag for tag in required_tags if tag not in tags]

        if missing_tags:
            non_compliant.append({
                'InstanceId': instance_id,
                'MissingTags': missing_tags
            })

if non_compliant:
    print("❌ Recursos sin tags obligatorios:")
    for resource in non_compliant:
        print(f"  {resource['InstanceId']}: {', '.join(resource['MissingTags'])}")
else:
    print("✅ Todos los recursos cumplen con tagging policy")
```

## 📖 Referencias

### Estándares relacionados

- [Infraestructura como Código](/docs/fundamentos-corporativos/estandares/infraestructura/iac)

### Convenciones relacionadas

- [Naming AWS](./01-naming-aws.md)

### Recursos externos

- [AWS Tagging Best Practices](https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/tagging-best-practices.html)
- [AWS Cost Allocation Tags](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
