---
id: secrets-management
sidebar_position: 15
title: Gestión de Secretos
description: Estándar para gestión segura de secretos usando AWS Secrets Manager con rotación automática, encriptación KMS y auditoría completa
---

# Estándar Técnico — Gestión de Secretos

---

## 1. Propósito

Garantizar almacenamiento, acceso y rotación seguros de secretos (credenciales, API keys, tokens) usando AWS Secrets Manager con encriptación KMS, rotación automática y auditoría mediante CloudTrail.

---

## 2. Alcance

**Aplica a:**

- Credenciales de bases de datos (PostgreSQL, Oracle, SQL Server, Redis)
- API keys de servicios externos
- Tokens de autenticación (JWT signing keys, OAuth client secrets)
- Certificados SSL/TLS privados
- Claves de cifrado de aplicación

**No aplica a:**

- Configuraciones no sensibles (usar AWS Parameter Store)
- Variables de entorno públicas
- Secretos de desarrollo local (usar .env con gitignore)

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología            | Versión mínima | Observaciones                     |
| ----------------- | --------------------- | -------------- | --------------------------------- |
| **Secrets Store** | AWS Secrets Manager   | -              | Único permitido para producción   |
| **Encriptación**  | AWS KMS               | -              | Customer Managed Keys obligatorio |
| **.NET SDK**      | AWSSDK.SecretsManager | 3.7+           | Cliente oficial AWS               |
| **Local Dev**     | dotnet user-secrets   | .NET 8+        | Solo desarrollo local             |
| **Rotation**      | AWS Lambda            | -              | Funciones de rotación automática  |
| **Auditoría**     | AWS CloudTrail        | -              | Logs de acceso a secretos         |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Almacenamiento de Secretos

- [ ] **AWS Secrets Manager** para todos los secretos en producción
- [ ] Naming convention: `/{env}/{service}/{secret-name}` (ej: `/prod/payment-api/db-password`)
- [ ] Encriptación con Customer Managed Keys (CMK) en AWS KMS
- [ ] Tags obligatorios: `Environment`, `Service`, `Owner`, `CostCenter`
- [ ] Descripción clara del propósito del secreto
- [ ] Secretos separados por entorno (dev, staging, prod)

### Rotación Automática

- [ ] **Rotación cada 90 días** para credenciales de BD
- [ ] Rotación cada 180 días para API keys
- [ ] Lambda functions para rotación automática
- [ ] Validación post-rotación (health check)
- [ ] Rollback automático si rotación falla
- [ ] Notificación SNS en caso de fallo de rotación

### Acceso a Secretos

- [ ] **IAM Roles** para acceso (NO IAM Users con credenciales estáticas)
- [ ] Principio de least privilege (un servicio = un rol = secretos mínimos)
- [ ] Policies basadas en resource ARNs específicos
- [ ] VPC Endpoints para acceso sin internet
- [ ] Retry logic con exponential backoff
- [ ] Cache de secretos con TTL corto (máx 5 minutos)

### Auditoría y Compliance

- [ ] CloudTrail logging habilitado para GetSecretValue
- [ ] Alertas CloudWatch para accesos anómalos
- [ ] Revisión mensual de secretos no rotados
- [ ] Eliminación de secretos no usados (>6 meses)
- [ ] Secret versioning habilitado
- [ ] Backup de secretos críticos

---

## 5. Prohibiciones

- ❌ Hardcodear secretos en código fuente
- ❌ Secretos en variables de entorno (CI/CD excepto inyección runtime)
- ❌ Secretos en archivos de configuración versionados
- ❌ Compartir secretos entre entornos
- ❌ Secretos en logs o mensajes de error
- ❌ Usar IAM Users con access keys estáticas
- ❌ Secretos sin encriptación at-rest

---

## 6. Configuración Mínima

### .NET - Acceso a AWS Secrets Manager

```csharp
// Program.cs
using Amazon.SecretsManager;
using Amazon.SecretsManager.Extensions.Caching;

var builder = WebApplication.CreateBuilder(args);

// Configurar AWS Secrets Manager
builder.Configuration.AddSecretsManager(configurator: options =>
{
    options.SecretFilter = secret => secret.Name.StartsWith($"/{builder.Environment.EnvironmentName}/");
    options.KeyGenerator = (secret, name) => name.Replace($"/{builder.Environment.EnvironmentName}/", "")
                                                  .Replace("/", ":");
    options.PollingInterval = TimeSpan.FromMinutes(5);
});

var app = builder.Build();
app.Run();
```

### Acceso Manual a Secreto

```csharp
public class DatabaseConnectionService
{
    private readonly IAmazonSecretsManager _secretsManager;
    private readonly SecretsManagerCache _cache;
    private readonly ILogger<DatabaseConnectionService> _logger;

    public DatabaseConnectionService(
        IAmazonSecretsManager secretsManager,
        ILogger<DatabaseConnectionService> logger)
    {
        _secretsManager = secretsManager;
        _cache = new SecretsManagerCache(secretsManager);
        _logger = logger;
    }

    public async Task<string> GetConnectionStringAsync()
    {
        try
        {
            var secretName = $"/{Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT")}/payment-api/db-password";
            var secretValue = await _cache.GetSecretString(secretName);

            return BuildConnectionString(secretValue);
        }
        catch (ResourceNotFoundException)
        {
            _logger.LogError("Secret not found");
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to retrieve secret");
            throw;
        }
    }

    private string BuildConnectionString(string password)
    {
        var host = Environment.GetEnvironmentVariable("DB_HOST");
        var database = Environment.GetEnvironmentVariable("DB_NAME");

        return $"Host={host};Database={database};Password={password};";
    }
}
```

### Terraform - Crear Secreto con Rotación

```hcl
# secrets.tf
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "/prod/payment-api/db-password"
  description             = "PostgreSQL password for payment-api"
  kms_key_id              = aws_kms_key.secrets.id
  recovery_window_in_days = 30

  rotation_rules {
    automatically_after_days = 90
  }

  tags = {
    Environment = "prod"
    Service     = "payment-api"
    Owner       = "platform-team"
    CostCenter  = "engineering"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "payment_user"
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.payment.endpoint
    port     = 5432
    dbname   = "payment_db"
  })
}

resource "aws_secretsmanager_secret_rotation" "db_password" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = aws_lambda_function.rotate_secret.arn

  rotation_rules {
    automatically_after_days = 90
  }
}

# KMS key para encriptación
resource "aws_kms_key" "secrets" {
  description             = "KMS key for Secrets Manager"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "secrets-manager-key"
  }
}
```

### IAM Policy - Acceso a Secreto

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789:secret:/prod/payment-api/*"
    },
    {
      "Effect": "Allow",
      "Action": ["kms:Decrypt", "kms:DescribeKey"],
      "Resource": "arn:aws:kms:us-east-1:123456789:key/abc123"
    }
  ]
}
```

---

## 7. Validación de Cumplimiento

```bash
# Verificar secretos sin rotación en últimos 90 días
aws secretsmanager list-secrets \
  --query "SecretList[?LastRotatedDate<'$(date -u -d '90 days ago' +%Y-%m-%d)'].Name"

# Verificar secretos sin tags
aws secretsmanager list-secrets \
  --query "SecretList[?!Tags].Name"

# Verificar accesos recientes a secreto
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=/prod/payment-api/db-password \
  --max-results 50
```

---

## 8. Referencias

**AWS:**

- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [Rotating Secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)

**Security:**

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)

**.NET:**

- [AWS Secrets Manager .NET SDK](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/csharp_secrets-manager_code_examples.html)
