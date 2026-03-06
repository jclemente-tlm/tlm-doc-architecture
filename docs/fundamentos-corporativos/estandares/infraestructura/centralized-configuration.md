---
id: centralized-configuration
sidebar_position: 6
title: Configuración Centralizada
description: Estándares para gestión centralizada de configuración con AWS Parameter Store y Secrets Manager, incluyendo naming conventions, IAM policies y acceso desde .NET 8.
tags: [infraestructura, configuracion, aws, parametros, secretos, terraform]
---

# Configuración Centralizada

## Contexto

Uso de AWS Parameter Store y Secrets Manager como single source of truth para configuración en runtime, con provisioning vía Terraform y acceso granular por IAM. Complementa el lineamiento [Infraestructura como Código](../../lineamientos/operabilidad/02-infraestructura-como-codigo.md) y el principio [XII-Factor Config](https://12factor.net/config).

**Conceptos incluidos:**

- **Parameter Store** → Configuración no sensible centralizada
- **Secrets Manager** → Secrets con cifrado KMS y rotación automática
- **IAM Policies** → Control de acceso granular por servicio y ambiente

---

## Stack Tecnológico

| Componente              | Tecnología          | Versión | Uso                                  |
| ----------------------- | ------------------- | ------- | ------------------------------------ |
| **Centralized Config**  | AWS Parameter Store | -       | Configuración no sensible            |
| **Secrets Management**  | AWS Secrets Manager | -       | Configuración sensible (credentials) |
| **Encryption**          | AWS KMS             | -       | Cifrado de secrets                   |
| **IaC**                 | Terraform           | 1.7+    | Provisioning de parámetros           |
| **ECS Task Definition** | AWS ECS Fargate     | -       | Inyección de secrets en containers   |

---

## Parameter Store vs Secrets Manager

| Característica    | Parameter Store        | Secrets Manager                    |
| ----------------- | ---------------------- | ---------------------------------- |
| **Uso**           | Config no sensible     | Secrets (passwords, keys)          |
| **Costo**         | Gratis (Standard tier) | $0.40/secret/mes + $0.05/10K calls |
| **Encryption**    | Opcional (KMS)         | Obligatorio (KMS)                  |
| **Auto-rotation** | No                     | Sí (para RDS, etc.)                |
| **Versioning**    | Sí                     | Sí                                 |
| **IAM Control**   | Sí                     | Sí                                 |

**Regla simple:**

- **Secrets Manager**: Passwords, API keys, tokens, certificates
- **Parameter Store**: Todo lo demás (URLs, timeouts, feature flags)

**Beneficios:**
✅ Single source of truth
✅ No secrets en código
✅ Auditoría completa (CloudTrail)
✅ Rotación automática de secrets
✅ Control granular de acceso (IAM)
✅ Cambios sin redeploy

### Naming Convention para Parameter Store

```
/{service-name}/{environment}/{category}/{parameter-name}

Ejemplos:
/customer-service/production/database/host
/customer-service/production/resilience/retry-attempts
/customer-service/production/features/enable-advanced-search
/customer-service/staging/database/host
```

### Provisioning con Terraform

```hcl
# terraform/modules/parameter-store/main.tf

# Configuración no sensible
resource "aws_ssm_parameter" "database_host" {
  name  = "/${var.service_name}/${var.environment}/database/host"
  type  = "String"
  value = var.database_host

  tags = {
    Service     = var.service_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_ssm_parameter" "retry_attempts" {
  name  = "/${var.service_name}/${var.environment}/resilience/retry-attempts"
  type  = "String"
  value = "3"

  tags = {
    Service     = var.service_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Configuración sensible (cifrada con KMS)
resource "aws_ssm_parameter" "database_password" {
  name   = "/${var.service_name}/${var.environment}/database/password"
  type   = "SecureString"
  value  = random_password.db_password.result
  key_id = aws_kms_key.parameter_store.id

  tags = {
    Service     = var.service_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

### Provisioning Secrets Manager

```hcl
# terraform/modules/secrets-manager/main.tf

# Database credentials
resource "aws_secretsmanager_secret" "customer_db" {
  name = "${var.service_name}/${var.environment}/database/credentials"

  tags = {
    Service     = var.service_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_secretsmanager_secret_version" "customer_db" {
  secret_id = aws_secretsmanager_secret.customer_db.id

  # JSON format para múltiples valores
  secret_string = jsonencode({
    username          = "customer_svc"
    password          = random_password.db_password.result
    host              = aws_db_instance.customer_db.address
    port              = aws_db_instance.customer_db.port
    dbname            = aws_db_instance.customer_db.db_name
    connectionString  = "Host=${aws_db_instance.customer_db.address};Port=${aws_db_instance.customer_db.port};Database=${aws_db_instance.customer_db.db_name};Username=customer_svc;Password=${random_password.db_password.result}"
  })
}

# External API key
resource "aws_secretsmanager_secret" "external_api_key" {
  name = "${var.service_name}/${var.environment}/apis/external-service-key"

  tags = {
    Service     = var.service_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
```

### IAM Policy para ECS Task

```hcl
# terraform/modules/ecs/iam.tf

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.service_name}-${var.environment}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# Leer Parameter Store
resource "aws_iam_role_policy" "parameter_store_read" {
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
      Resource = "arn:aws:ssm:${var.aws_region}:${var.aws_account_id}:parameter/${var.service_name}/${var.environment}/*"
    }]
  })
}

# Leer Secrets Manager
resource "aws_iam_role_policy" "secrets_manager_read" {
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:${var.service_name}/${var.environment}/*"
    }]
  })
}

# KMS decrypt
resource "aws_iam_role_policy" "kms_decrypt" {
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["kms:Decrypt"]
      Resource = aws_kms_key.secrets.arn
    }]
  })
}
```

### Leer desde .NET 8

```csharp
// Program.cs — integración con AWS Systems Manager
using Amazon.Extensions.NETCore.Setup;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddSystemsManager(configureSource =>
{
    configureSource.Path = $"/customer-service/{builder.Environment.EnvironmentName}";
    configureSource.ReloadAfter = TimeSpan.FromMinutes(5);
});

// Binding fuertemente tipado
builder.Services.Configure<ResilienceSettings>(
    builder.Configuration.GetSection("resilience"));

var app = builder.Build();
app.Run();
```

```csharp
// Leer Secrets Manager directamente (para conexiones al startup)
public class SecretsService
{
    private readonly IAmazonSecretsManager _secretsManager;

    public SecretsService(IAmazonSecretsManager secretsManager)
    {
        _secretsManager = secretsManager;
    }

    public async Task<DatabaseCredentials> GetDatabaseCredentialsAsync()
    {
        var response = await _secretsManager.GetSecretValueAsync(
            new GetSecretValueRequest
            {
                SecretId = "customer-service/production/database/credentials"
            });

        return JsonSerializer.Deserialize<DatabaseCredentials>(response.SecretString);
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar AWS Parameter Store para configuración non-sensitive
- **MUST** usar AWS Secrets Manager para secrets (passwords, API keys, tokens)
- **MUST** provisionar configuración vía Terraform (no manual en consola)
- **MUST** usar IAM policies con least privilege para control de acceso a configuración
- **MUST** usar naming convention `/{service-name}/{environment}/{category}/{param}` en Parameter Store

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar mismo mecanismo de secrets en dev/staging/prod (Secrets Manager)
- **SHOULD** habilitar rotación automática de secrets de RDS en Secrets Manager
- **SHOULD** encriptar Parameter Store values sensibles con KMS custom keys

### MAY (Opcional)

- **MAY** usar AWS AppConfig para configuración dinámica con canary releases
- **MAY** implementar configuration versioning con rollback a versión anterior
- **MAY** usar `AddSystemsManager` con `ReloadAfter` para hot reload de config

### MUST NOT (Prohibido)

- **MUST NOT** crear parámetros o secrets manualmente en consola AWS (usar Terraform)
- **MUST NOT** usar archivos de configuración environment-specific versionados en Git con secrets

---

## Referencias

- [XII-Factor — III. Config](https://12factor.net/config) — principio de configuración externalizada
- [AWS Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) — servicio de configuración centralizada
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/) — gestión de secrets con rotación automática
- [ECS Task Definition Secrets](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-secrets.html) — inyección segura de secrets en contenedores
- [Configuration in ASP.NET Core](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/) — integración con AWS SDK en .NET 8
- [Externalización de Configuración](./externalize-configuration.md) — separación de config del código y variables de entorno
- [Paridad de Ambientes](./environment-parity.md) — consistencia de configuración entre ambientes
- [Infrastructure as Code — Implementación](./iac-implementation.md) — módulos Terraform para provisioning de config
- [Secrets Management](../seguridad/secrets-key-management.md) — gestión de secrets y rotación de claves
