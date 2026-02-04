---
id: secrets-key-management
sidebar_position: 10
title: Gestión de Secretos y Claves de Encriptación
description: Estándar consolidado para gestión segura de secretos con AWS Secrets Manager y claves de encriptación con AWS KMS, incluyendo rotación automática, auditoría y acceso granular
---

# Estándar Técnico — Gestión de Secretos y Claves de Encriptación

## 1. Propósito

Garantizar almacenamiento seguro, acceso controlado y rotación automática de secretos (credentials, API keys, tokens) y claves de encriptación mediante AWS Secrets Manager y AWS KMS, con auditoría completa vía CloudTrail y principio de mínimo privilegio.

## 2. Alcance

**Aplica a:**

- Credenciales de bases de datos (PostgreSQL, Oracle, SQL Server, Redis)
- API keys de servicios externos
- Tokens de autenticación (JWT signing keys, OAuth client secrets, Keycloak client secrets)
- Certificados SSL/TLS privados
- Claves de cifrado de aplicación
- Encryption at-rest (RDS, S3, EBS)
- Application-level encryption (.NET)
- Firma digital de eventos

**No aplica a:**

- Configuraciones no sensibles (usar AWS Parameter Store)
- Variables de entorno públicas
- Secretos de desarrollo local (usar dotnet user-secrets con gitignore)
- TLS certificates públicos (usar AWS Certificate Manager)
- SSH keys (gestión manual)

## 3. Tecnologías Aprobadas

| Componente           | Tecnología                  | Versión mínima | Observaciones                          |
| -------------------- | --------------------------- | -------------- | -------------------------------------- |
| **Secrets Store**    | AWS Secrets Manager         | -              | Único permitido para producción        |
| **Key Management**   | AWS KMS                     | -              | Customer Managed Keys (CMK)            |
| **Encriptación**     | AES-256 (Symmetric)         | -              | Default para encryption                |
| **Asimétrica**       | RSA-4096, ECC               | -              | Solo para signing                      |
| **.NET SDK Secrets** | AWSSDK.SecretsManager       | 3.7+           | Cliente oficial AWS                    |
| **.NET SDK KMS**     | AWSSDK.KeyManagementService | 3.7+           | Cliente oficial AWS                    |
| **Local Dev**        | dotnet user-secrets         | .NET 8+        | Solo desarrollo local                  |
| **Rotation**         | AWS Lambda                  | -              | Funciones de rotación automática       |
| **Auditoría**        | AWS CloudTrail              | -              | Logs de acceso inmutables              |
| **IaC**              | Terraform                   | 1.6+           | aws_kms_key, aws_secretsmanager_secret |

## 4. Requisitos Obligatorios 🔴

### Gestión de Secretos

- [ ] **AWS Secrets Manager** para todos los secretos en producción
- [ ] **Naming convention:** `/{env}/{service}/{secret-name}` (ej: `/prod/payment-api/db-password`)
- [ ] **Encriptación con CMK** en AWS KMS (NO AWS Managed Keys)
- [ ] **Tags obligatorios:** Environment, Service, Owner, CostCenter
- [ ] **Descripción clara** del propósito del secreto
- [ ] **Secretos separados** por entorno (dev, staging, prod)
- [ ] **Rotación cada 90 días** para credenciales de BD
- [ ] **Rotación cada 180 días** para API keys

### Gestión de Claves KMS

- [ ] **CMK por ambiente:** Separar Dev, Staging, Production
- [ ] **CMK por propósito:** RDS, S3, Secrets, Application
- [ ] **NO AWS Managed Keys:** Usar Customer Managed Keys (control total)
- [ ] **Rotación automática anual** habilitada
- [ ] **Multi-region:** Solo si necesario (disaster recovery)

### Acceso Controlado

- [ ] **IAM Roles** para acceso (NO IAM Users con credenciales estáticas)
- [ ] **Least privilege:** Un servicio = un rol = secretos/keys mínimos
- [ ] **Policies específicas** con resource ARNs (NO wildcards `kms:*` o `secretsmanager:*`)
- [ ] **Key policies** definidas (quién puede usar/administrar)
- [ ] **VPC Endpoints** para acceso sin internet
- [ ] **Retry logic** con exponential backoff

### Auditoría y Compliance

- [ ] **CloudTrail logging** habilitado para GetSecretValue y KMS operations
- [ ] **Alertas CloudWatch** para accesos anómalos o KMS errors
- [ ] **Revisión mensual** de secretos no rotados
- [ ] **Eliminación** de secretos no usados (>6 meses)
- [ ] **Secret versioning** habilitado
- [ ] **Backup** de secretos críticos
- [ ] **Logs inmutables** con retention 90 días mínimo

## 5. Prohibiciones

- ❌ Hardcodear secretos en código fuente
- ❌ Secretos en variables de entorno (excepto inyección runtime)
- ❌ Secretos en archivos de configuración versionados
- ❌ Compartir secretos/keys entre entornos
- ❌ Secretos en logs o mensajes de error
- ❌ IAM Users con access keys estáticas para servicios
- ❌ Secretos sin encriptación at-rest
- ❌ Usar AWS Managed Keys (sin control de policies)
- ❌ KMS wildcards `kms:*` en IAM policies

## 6. AWS Secrets Manager — Configuración

### 6.1 Terraform — Crear Secreto con Rotación

```hcl
# terraform/secrets.tf
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "/prod/payment-api/db-password"
  description             = "PostgreSQL password for payment-api"
  kms_key_id              = aws_kms_key.secrets_production.id
  recovery_window_in_days = 30

  rotation_rules {
    automatically_after_days = 90
  }

  tags = {
    Environment = "production"
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
```

### 6.2 IAM Policy — Acceso a Secreto Específico

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
      "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:/prod/payment-api/*"
    },
    {
      "Effect": "Allow",
      "Action": ["kms:Decrypt", "kms:DescribeKey"],
      "Resource": "arn:aws:kms:us-east-1:123456789012:key/abc123-key-id"
    }
  ]
}
```

### 6.3 .NET — Acceso a Secrets Manager

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

### 6.4 .NET — Service con Cache

```csharp
// Services/SecretsService.cs
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;
using Amazon.SecretsManager.Extensions.Caching;

public class SecretsService
{
    private readonly IAmazonSecretsManager _secretsManager;
    private readonly SecretsManagerCache _cache;
    private readonly ILogger<SecretsService> _logger;

    public SecretsService(
        IAmazonSecretsManager secretsManager,
        ILogger<SecretsService> logger)
    {
        _secretsManager = secretsManager;
        _cache = new SecretsManagerCache(secretsManager);  // TTL default: 1 hora
        _logger = logger;
    }

    public async Task<string> GetSecretAsync(string secretName)
    {
        try
        {
            // Cache automático con TTL
            return await _cache.GetSecretString(secretName);
        }
        catch (ResourceNotFoundException)
        {
            _logger.LogError("Secret {SecretName} not found", secretName);
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to retrieve secret {SecretName}", secretName);
            throw;
        }
    }

    public async Task<DatabaseCredentials> GetDatabaseCredentialsAsync()
    {
        var secretName = $"/{Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT")}/payment-api/db-password";
        var secretJson = await GetSecretAsync(secretName);

        return JsonSerializer.Deserialize<DatabaseCredentials>(secretJson)!;
    }
}

public record DatabaseCredentials(
    string Username,
    string Password,
    string Engine,
    string Host,
    int Port,
    string Dbname);
```

## 7. AWS KMS — Configuración de Claves

### 7.1 Terraform — KMS Keys por Propósito

```hcl
# terraform/kms.tf

# KMS Key para RDS (Production)
resource "aws_kms_key" "rds_production" {
  description             = "KMS key for RDS encryption - Production"
  deletion_window_in_days = 30  # Protección contra borrado accidental
  enable_key_rotation     = true  # ✅ Rotación automática anual

  tags = {
    Environment = "production"
    Service     = "rds"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "rds_production" {
  name          = "alias/rds-production"
  target_key_id = aws_kms_key.rds_production.key_id
}

# Key Policy (quién puede usar)
resource "aws_kms_key_policy" "rds_production" {
  key_id = aws_kms_key.rds_production.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow RDS to use the key"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:CreateGrant"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "rds.us-east-1.amazonaws.com"
          }
        }
      },
      {
        Sid    = "Allow ECS tasks to decrypt"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.ecs_task_role.arn
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
}

# KMS Key para S3
resource "aws_kms_key" "s3_production" {
  description             = "KMS key for S3 bucket encryption - Production"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Environment = "production"
    Service     = "s3"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "s3_production" {
  name          = "alias/s3-production"
  target_key_id = aws_kms_key.s3_production.key_id
}

# KMS Key para Secrets Manager
resource "aws_kms_key" "secrets_production" {
  description             = "KMS key for Secrets Manager - Production"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Environment = "production"
    Service     = "secrets-manager"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "secrets_production" {
  name          = "alias/secrets-production"
  target_key_id = aws_kms_key.secrets_production.key_id
}

# KMS Key para aplicación (custom encryption)
resource "aws_kms_key" "application_production" {
  description             = "KMS key for application-level encryption - Production"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Environment = "production"
    Service     = "payment-api"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "application_production" {
  name          = "alias/app-payment-production"
  target_key_id = aws_kms_key.application_production.key_id
}
```

### 7.2 IAM Policies — Acceso Granular a KMS

#### Policy para ECS Tasks (Solo Decrypt)

```hcl
# IAM policy para ECS task: solo decrypt
resource "aws_iam_policy" "kms_decrypt" {
  name        = "kms-decrypt-application"
  description = "Allow ECS tasks to decrypt with KMS"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [
          aws_kms_key.application_production.arn,
          aws_kms_key.secrets_production.arn  # Para Secrets Manager
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_kms" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.kms_decrypt.arn
}
```

#### Policy para Administradores (Key Management)

```hcl
# IAM policy para admins: gestionar keys
resource "aws_iam_policy" "kms_admin" {
  name        = "kms-key-administrator"
  description = "Allow administrators to manage KMS keys"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Create*",
          "kms:Describe*",
          "kms:Enable*",
          "kms:List*",
          "kms:Put*",
          "kms:Update*",
          "kms:Revoke*",
          "kms:Disable*",
          "kms:Get*",
          "kms:Delete*",
          "kms:ScheduleKeyDeletion",
          "kms:CancelKeyDeletion",
          "kms:TagResource",
          "kms:UntagResource"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = "us-east-1"
          }
        }
      }
    ]
  })
}
```

## 8. Application-Level Encryption con KMS

### 8.1 Instalación .NET

```bash
dotnet add package AWSSDK.KeyManagementService
```

### 8.2 Service de Encriptación

```csharp
// Services/KmsEncryptionService.cs
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;
using System.Security.Cryptography;

public class KmsEncryptionService
{
    private readonly IAmazonKeyManagementService _kmsClient;
    private readonly string _keyId;  // KMS Key ARN o Alias
    private readonly ILogger<KmsEncryptionService> _logger;

    public KmsEncryptionService(
        IAmazonKeyManagementService kmsClient,
        IConfiguration configuration,
        ILogger<KmsEncryptionService> logger)
    {
        _kmsClient = kmsClient;
        _keyId = configuration["AWS:KMS:KeyId"]!;  // alias/app-payment-production
        _logger = logger;
    }

    /// <summary>
    /// Encripta texto pequeño (<4KB) directamente con KMS
    /// </summary>
    public async Task<string> EncryptAsync(string plaintext)
    {
        try
        {
            var request = new EncryptRequest
            {
                KeyId = _keyId,
                Plaintext = new MemoryStream(Encoding.UTF8.GetBytes(plaintext))
            };

            var response = await _kmsClient.EncryptAsync(request);

            // Retornar ciphertext en Base64
            return Convert.ToBase64String(response.CiphertextBlob.ToArray());
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to encrypt data with KMS");
            throw;
        }
    }

    /// <summary>
    /// Decripta texto encriptado con KMS
    /// </summary>
    public async Task<string> DecryptAsync(string ciphertextBase64)
    {
        try
        {
            var ciphertextBlob = Convert.FromBase64String(ciphertextBase64);

            var request = new DecryptRequest
            {
                CiphertextBlob = new MemoryStream(ciphertextBlob)
                // NO necesita KeyId, KMS lo detecta automáticamente
            };

            var response = await _kmsClient.DecryptAsync(request);

            return Encoding.UTF8.GetString(response.Plaintext.ToArray());
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to decrypt data with KMS");
            throw;
        }
    }

    /// <summary>
    /// Envelope encryption (mejor performance para datos grandes >4KB)
    /// </summary>
    public async Task<EncryptedEnvelope> EncryptLargeDataAsync(string plaintext)
    {
        try
        {
            // 1. Generar data key con KMS
            var generateKeyResponse = await _kmsClient.GenerateDataKeyAsync(new GenerateDataKeyRequest
            {
                KeyId = _keyId,
                KeySpec = DataKeySpec.AES_256
            });

            // 2. Encriptar datos con data key (local, sin llamar KMS)
            var dataKey = generateKeyResponse.Plaintext.ToArray();
            var encryptedData = EncryptWithAES(plaintext, dataKey);

            // 3. Retornar encrypted data key + encrypted data
            return new EncryptedEnvelope
            {
                EncryptedDataKey = Convert.ToBase64String(generateKeyResponse.CiphertextBlob.ToArray()),
                EncryptedData = Convert.ToBase64String(encryptedData)
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to encrypt large data with envelope encryption");
            throw;
        }
    }

    /// <summary>
    /// Decripta datos grandes con envelope encryption
    /// </summary>
    public async Task<string> DecryptLargeDataAsync(EncryptedEnvelope envelope)
    {
        try
        {
            // 1. Decriptar data key con KMS
            var encryptedDataKeyBytes = Convert.FromBase64String(envelope.EncryptedDataKey);
            var decryptResponse = await _kmsClient.DecryptAsync(new DecryptRequest
            {
                CiphertextBlob = new MemoryStream(encryptedDataKeyBytes)
            });

            var dataKey = decryptResponse.Plaintext.ToArray();

            // 2. Decriptar datos con data key (local)
            var encryptedData = Convert.FromBase64String(envelope.EncryptedData);
            return DecryptWithAES(encryptedData, dataKey);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to decrypt large data with envelope encryption");
            throw;
        }
    }

    private byte[] EncryptWithAES(string plaintext, byte[] key)
    {
        using var aes = Aes.Create();
        aes.Key = key;
        aes.GenerateIV();

        using var encryptor = aes.CreateEncryptor();
        var plaintextBytes = Encoding.UTF8.GetBytes(plaintext);
        var ciphertext = encryptor.TransformFinalBlock(plaintextBytes, 0, plaintextBytes.Length);

        // Concatenar IV + ciphertext
        var result = new byte[aes.IV.Length + ciphertext.Length];
        Buffer.BlockCopy(aes.IV, 0, result, 0, aes.IV.Length);
        Buffer.BlockCopy(ciphertext, 0, result, aes.IV.Length, ciphertext.Length);

        return result;
    }

    private string DecryptWithAES(byte[] encryptedData, byte[] key)
    {
        using var aes = Aes.Create();
        aes.Key = key;

        // Extraer IV + ciphertext
        var iv = new byte[aes.BlockSize / 8];
        var ciphertext = new byte[encryptedData.Length - iv.Length];
        Buffer.BlockCopy(encryptedData, 0, iv, 0, iv.Length);
        Buffer.BlockCopy(encryptedData, iv.Length, ciphertext, 0, ciphertext.Length);

        aes.IV = iv;

        using var decryptor = aes.CreateDecryptor();
        var plaintextBytes = decryptor.TransformFinalBlock(ciphertext, 0, ciphertext.Length);

        return Encoding.UTF8.GetString(plaintextBytes);
    }
}

public record EncryptedEnvelope
{
    public string EncryptedDataKey { get; init; } = string.Empty;
    public string EncryptedData { get; init; } = string.Empty;
}

// Program.cs
builder.Services.AddAWSService<IAmazonKeyManagementService>();
builder.Services.AddSingleton<KmsEncryptionService>();
```

### 8.3 Uso en Aplicación

```csharp
[ApiController]
[Route("api/v1/[controller]")]
public class PaymentsController : ControllerBase
{
    private readonly KmsEncryptionService _kmsService;

    public PaymentsController(KmsEncryptionService kmsService)
    {
        _kmsService = kmsService;
    }

    [HttpPost("encrypt-card")]
    public async Task<IActionResult> EncryptCreditCard([FromBody] string cardNumber)
    {
        // Encriptar número de tarjeta antes de guardar en BD
        var encryptedCard = await _kmsService.EncryptAsync(cardNumber);

        // Guardar en BD: encryptedCard
        return Ok(new { message = "Card encrypted successfully" });
    }

    [HttpPost("decrypt-card")]
    public async Task<IActionResult> DecryptCreditCard([FromBody] string encryptedCard)
    {
        // Decriptar para procesamiento
        var decryptedCard = await _kmsService.DecryptAsync(encryptedCard);

        // Usar para transacción
        return Ok(new { last4 = decryptedCard.Substring(decryptedCard.Length - 4) });
    }
}
```

## 9. RDS y S3 con KMS Encryption

### 9.1 RDS con KMS

```hcl
resource "aws_db_instance" "main" {
  identifier     = "payment-db-prod"
  engine         = "postgres"
  engine_version = "16.1"

  # Encryption at-rest con KMS
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds_production.arn

  instance_class    = "db.t4g.medium"
  allocated_storage = 100

  # ...
}
```

### 9.2 S3 con KMS

```hcl
resource "aws_s3_bucket" "documents" {
  bucket = "customer-documents-prod"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3_production.arn
    }
    bucket_key_enabled = true  # Reduce KMS API calls (mejor performance)
  }
}

# Bucket policy para forzar encriptación
resource "aws_s3_bucket_policy" "documents_kms" {
  bucket = aws_s3_bucket.documents.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DenyUnencryptedObjectUploads"
      Effect    = "Deny"
      Principal = "*"
      Action    = "s3:PutObject"
      Resource  = "${aws_s3_bucket.documents.arn}/*"
      Condition = {
        StringNotEquals = {
          "s3:x-amz-server-side-encryption" = "aws:kms"
        }
      }
    }]
  })
}
```

## 10. Auditoría y Monitoreo

### 10.1 CloudTrail para Secrets Manager y KMS

```hcl
# terraform/cloudtrail.tf
resource "aws_cloudtrail" "audit" {
  name                          = "secrets-kms-audit-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true  # Inmutabilidad

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }

  # Eventos de Secrets Manager
  event_selector {
    data_resource {
      type   = "AWS::SecretsManager::Secret"
      values = ["arn:aws:secretsmanager:*:${data.aws_caller_identity.current.account_id}:secret:*"]
    }
  }

  # Eventos de KMS
  event_selector {
    data_resource {
      type   = "AWS::KMS::Key"
      values = ["arn:aws:kms:*:${data.aws_caller_identity.current.account_id}:key/*"]
    }
  }
}
```

### 10.2 CloudWatch Alarms

```hcl
# Alarma para errores de KMS
resource "aws_cloudwatch_metric_alarm" "kms_errors" {
  alarm_name          = "kms-decrypt-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "UserErrorCount"
  namespace           = "AWS/KMS"
  period              = 300
  statistic           = "Sum"
  threshold           = 10

  alarm_actions = [aws_sns_topic.alerts.arn]
}

# Alarma para accesos anómalos a secretos
resource "aws_cloudwatch_log_metric_filter" "secret_access_denied" {
  name           = "secret-access-denied"
  log_group_name = aws_cloudwatch_log_group.cloudtrail.name

  pattern = "{ $.eventName = \"GetSecretValue\" && $.errorCode = \"AccessDenied\" }"

  metric_transformation {
    name      = "SecretAccessDenied"
    namespace = "Security"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "secret_access_denied_alarm" {
  alarm_name          = "secret-access-denied"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "SecretAccessDenied"
  namespace           = "Security"
  period              = 300
  statistic           = "Sum"
  threshold           = 5

  alarm_actions = [aws_sns_topic.security_alerts.arn]
}
```

## 11. Validación de Cumplimiento

### 11.1 Comandos de Verificación

```bash
# ============ SECRETS MANAGER ============

# Listar secretos sin rotación en últimos 90 días
aws secretsmanager list-secrets \
  --query "SecretList[?LastRotatedDate<'$(date -u -d '90 days ago' +%Y-%m-%d)'].Name"

# Verificar secretos sin tags
aws secretsmanager list-secrets \
  --query "SecretList[?!Tags].Name"

# Ver accesos recientes a secreto
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=/prod/payment-api/db-password \
  --max-results 50 \
  | jq '.Events[] | {Time: .EventTime, User: .Username, Event: .EventName}'

# Verificar KMS key del secreto
aws secretsmanager describe-secret --secret-id /prod/payment-api/db-password \
  | jq '{Name, KmsKeyId, RotationEnabled, LastRotatedDate}'

# ============ KMS ============

# Listar todas las KMS keys
aws kms list-keys

# Ver detalles de key (rotation enabled?)
aws kms describe-key --key-id alias/rds-production \
  | jq '{KeyId, Enabled, KeyState, KeyRotationEnabled: .KeyMetadata.KeyRotationEnabled}'

# Verificar rotación automática habilitada
aws kms get-key-rotation-status --key-id alias/rds-production
# Output: {"KeyRotationEnabled": true}

# Ver quién puede usar la key
aws kms get-key-policy --key-id alias/rds-production --policy-name default | jq .

# Listar grants activos
aws kms list-grants --key-id alias/rds-production

# Consultar uso en CloudTrail (decrypts última hora)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=Decrypt \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --max-results 50 \
  | jq '.Events[] | {Time: .EventTime, User: .Username, Key: .Resources[0].ResourceName}'

# Verificar keys sin rotación automática
aws kms list-keys --query 'Keys[*].KeyId' --output text | while read key; do
  rotation=$(aws kms get-key-rotation-status --key-id $key 2>/dev/null | jq -r '.KeyRotationEnabled')
  if [ "$rotation" = "false" ]; then
    echo "⚠️  Key $key sin rotación automática"
  fi
done
```

### 11.2 Checklist de Cumplimiento

**Secrets Manager:**

- [ ] Todos los secretos en /prod/\* encriptados con CMK
- [ ] Naming convention `/{env}/{service}/{secret}` aplicada
- [ ] Rotación configurada (90d para DB, 180d para API keys)
- [ ] Tags obligatorios presentes (Environment, Service, Owner)
- [ ] Secretos no usados eliminados (>6 meses)
- [ ] IAM policies con ARNs específicos (NO wildcards)
- [ ] CloudTrail logging habilitado para GetSecretValue
- [ ] Alertas CloudWatch configuradas para access denied

**KMS:**

- [ ] CMK por ambiente (dev, staging, prod)
- [ ] CMK por propósito (RDS, S3, Secrets, App)
- [ ] Rotación automática anual habilitada
- [ ] Key policies definidas (NO solo IAM policies)
- [ ] IAM policies sin `kms:*` wildcard
- [ ] CloudTrail logging habilitado para Decrypt
- [ ] Alertas CloudWatch para KMS errors
- [ ] Deletion window configurado (30 días)

## 12. Métricas de Cumplimiento

| Métrica                          | Target         | Verificación                            |
| -------------------------------- | -------------- | --------------------------------------- |
| **Secretos con rotación**        | 100%           | `list-secrets` + filtro LastRotatedDate |
| **Secretos con CMK**             | 100%           | `describe-secret` → KmsKeyId            |
| **Keys con rotación automática** | 100% CMK       | `get-key-rotation-status`               |
| **Secretos sin tags**            | 0%             | `list-secrets` + query Tags             |
| **IAM policies con wildcards**   | <10%           | Terraform state scan                    |
| **Secrets sin acceso >6 meses**  | 0% (eliminar)  | CloudTrail analysis                     |
| **KMS errors**                   | <5 errores/día | CloudWatch metric                       |
| **Access denied alerts**         | <3/día         | CloudWatch alarm                        |

## 13. Referencias

**AWS Secrets Manager:**

- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [Rotating Secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [AWS Secrets Manager .NET SDK](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/csharp_secrets-manager_code_examples.html)

**AWS KMS:**

- [AWS KMS Documentation](https://docs.aws.amazon.com/kms/)
- [KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)
- [Envelope Encryption](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#enveloping)

**Security Standards:**

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [NIST SP 800-57 - Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)
