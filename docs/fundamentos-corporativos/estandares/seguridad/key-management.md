---
id: key-management
sidebar_position: 12
title: Key Management (KMS)
description: Estándar para gestión de claves de encriptación con AWS KMS, rotación automática, auditoría y acceso granular
---

# Estándar Técnico — Key Management

---

## 1. Propósito

Gestionar claves de encriptación con AWS KMS (Key Management Service), implementando rotación automática, auditoría completa (CloudTrail), separación por ambiente y acceso granular mediante IAM policies.

---

## 2. Alcance

**Aplica a:**

- Encryption at-rest (RDS, S3, EBS)
- Secrets en AWS Secrets Manager
- Application-level encryption (.NET)
- Firma digital de eventos
- Tokenización de datos sensibles

**No aplica a:**

- TLS certificates (usar ACM)
- SSH keys (gestión manual)

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología                  | Versión mínima | Observaciones               |
| -------------- | --------------------------- | -------------- | --------------------------- |
| **KMS**        | AWS KMS                     | -              | Customer Managed Keys (CMK) |
| **Key Type**   | Symmetric (AES-256)         | -              | Default para encryption     |
| **Asymmetric** | RSA-4096, ECC               | -              | Solo para signing           |
| **SDK**        | AWSSDK.KeyManagementService | 3.7+           | .NET integration            |
| **Auditing**   | AWS CloudTrail              | -              | Immutable logs              |
| **IaC**        | Terraform                   | 1.6+           | aws_kms_key resource        |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Tipos de Claves

- [ ] **CMK por ambiente**: Separar Dev, Staging, Production
- [ ] **CMK por propósito**: RDS, S3, Secrets, Application
- [ ] **NO usar AWS Managed Keys**: Usar Customer Managed Keys (control total)
- [ ] **Multi-region**: Solo si necesario (disaster recovery)

### Rotación

- [ ] **Automática anual**: Habilitar rotación de KMS keys
- [ ] **Backward compatible**: KMS mantiene versiones antiguas para decrypt
- [ ] **Secrets rotation**: 90 días para DB credentials

### Acceso

- [ ] **Least privilege**: IAM policies específicas por servicio
- [ ] **NO wildcard**: `kms:*` prohibido
- [ ] **Key policies**: Definir quién puede usar/administrar
- [ ] **Grants**: Para acceso temporal (ECS tasks)

### Auditoría

- [ ] **CloudTrail**: Registrar todos los usos de keys
- [ ] **Alertas**: CloudWatch alarms en KMS errors
- [ ] **Retention**: Logs inmutables por 90 días mínimo

---

## 5. Terraform - KMS Keys

### KMS Key por Ambiente

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
    Service     = "payment-service"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "application_production" {
  name          = "alias/app-payment-production"
  target_key_id = aws_kms_key.application_production.key_id
}
```

---

## 6. IAM Policies - Acceso Granular

### ECS Task Role (Application)

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

### Admin Role (Key Management)

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
          "kms:CancelKeyDeletion"
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

---

## 7. .NET - Encryption con KMS

### Instalación

```bash
dotnet add package AWSSDK.KeyManagementService
```

### Service para Encriptación

```csharp
// Services/KmsEncryptionService.cs
public class KmsEncryptionService
{
    private readonly IAmazonKeyManagementService _kmsClient;
    private readonly string _keyId;  // KMS Key ARN o Alias

    public KmsEncryptionService(
        IAmazonKeyManagementService kmsClient,
        IConfiguration configuration)
    {
        _kmsClient = kmsClient;
        _keyId = configuration["AWS:KMS:KeyId"]!;  // alias/app-payment-production
    }

    public async Task<string> EncryptAsync(string plaintext)
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

    public async Task<string> DecryptAsync(string ciphertextBase64)
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

    // Envelope encryption (mejor performance para datos grandes)
    public async Task<(string DataKey, string EncryptedData)> EncryptLargeDataAsync(string plaintext)
    {
        // 1. Generar data key
        var generateKeyResponse = await _kmsClient.GenerateDataKeyAsync(new GenerateDataKeyRequest
        {
            KeyId = _keyId,
            KeySpec = DataKeySpec.AES_256
        });

        // 2. Encriptar datos con data key (local)
        var dataKey = generateKeyResponse.Plaintext.ToArray();
        var encryptedData = EncryptWithAES(plaintext, dataKey);

        // 3. Retornar encrypted data key + encrypted data
        var encryptedDataKey = Convert.ToBase64String(generateKeyResponse.CiphertextBlob.ToArray());

        return (encryptedDataKey, Convert.ToBase64String(encryptedData));
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
}

// Program.cs
builder.Services.AddAWSService<IAmazonKeyManagementService>();
builder.Services.AddSingleton<KmsEncryptionService>();
```

---

## 8. RDS con KMS Encryption

```hcl
resource "aws_db_instance" "main" {
  identifier     = "payment-db-prod"
  engine         = "postgres"
  engine_version = "14.10"

  # Encryption at-rest con KMS
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds_production.arn

  # ...
}
```

---

## 9. S3 con KMS Encryption

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
    bucket_key_enabled = true  # Reduce KMS API calls
  }
}
```

---

## 10. CloudTrail - Auditoría

```hcl
# CloudTrail para KMS audit logging
resource "aws_cloudtrail" "kms_audit" {
  name                          = "kms-audit-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true  # Inmutabilidad

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    # Solo eventos KMS
    data_resource {
      type   = "AWS::KMS::Key"
      values = ["arn:aws:kms:*:${data.aws_caller_identity.current.account_id}:key/*"]
    }
  }
}

# CloudWatch alarm para KMS errors
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
```

---

## 11. Validación de Cumplimiento

```bash
# Listar todas las KMS keys
aws kms list-keys

# Ver detalles de key (rotation enabled?)
aws kms describe-key --key-id alias/rds-production | jq '{KeyId, Enabled, KeyState, KeyRotationEnabled: .KeyMetadata.KeyRotationEnabled}'

# Ver quién puede usar la key
aws kms get-key-policy --key-id alias/rds-production --policy-name default | jq .

# Verificar rotación automática habilitada
aws kms get-key-rotation-status --key-id alias/rds-production
# Output: {"KeyRotationEnabled": true}

# Listar grants activos
aws kms list-grants --key-id alias/rds-production

# Consultar uso en CloudTrail (decrypts última hora)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=Decrypt \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --max-results 50
```

---

## 12. Referencias

**AWS:**

- [AWS KMS Documentation](https://docs.aws.amazon.com/kms/)
- [KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)

**NIST:**

- [NIST SP 800-57 - Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)

**OWASP:**

- [Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
