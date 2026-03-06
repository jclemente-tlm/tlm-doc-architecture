---
id: secrets-key-management
sidebar_position: 9
title: Gestión de Secretos y Claves Criptográficas
description: Estándares para gestión de secretos (passwords, API keys) y claves de cifrado
tags: [seguridad, secrets, aws-secrets-manager, aws-kms, cifrado]
---

# Gestión de Secretos y Claves Criptográficas

## Contexto

Este estándar consolida **2 conceptos relacionados** con gestión segura de secretos y claves criptográficas. Define cómo almacenar, rotar y auditar credenciales.

**Conceptos incluidos:**

- **Secrets Management** → Gestión de passwords, API keys, certificates
- **Key Management** → Gestión de claves de cifrado (encryption keys)

---

## Stack Tecnológico

| Componente             | Tecnología          | Versión | Uso                          |
| ---------------------- | ------------------- | ------- | ---------------------------- |
| **Secrets Management** | AWS Secrets Manager | Latest  | Almacenamiento de secretos   |
| **Key Management**     | AWS KMS             | Latest  | Gestión de claves de cifrado |
| **Runtime**            | .NET                | 8.0+    | Aplicaciones                 |
| **IaC**                | Terraform           | 1.7+    | Provisión de secretos/keys   |

---

## Gestión de Secretos

### ¿Qué es?

Almacenamiento seguro, rotación automática y auditoría de secretos (passwords, API keys, certificates, tokens).

**Propósito:** Evitar hardcodear secretos en código o configuración.

**Beneficios:**
✅ Secretos cifrados at-rest y in-transit
✅ Rotación automática
✅ Auditoría de accesos
✅ Separación por ambiente

### Terraform: Crear Secretos

```hcl
# terraform/modules/secrets/main.tf

# Secret para database password
resource "aws_secretsmanager_secret" "database_password" {
  name        = "${var.environment}/database/password"
  description = "PostgreSQL master password for ${var.environment}"

  # Rotación automática cada 30 días
  rotation_rules {
    automatically_after_days = 30
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Valor inicial (luego AWS rota automáticamente)
resource "aws_secretsmanager_secret_version" "database_password" {
  secret_id = aws_secretsmanager_secret.database_password.id

  secret_string = jsonencode({
    username = "postgres"
    password = random_password.database.result
    host     = aws_db_instance.main.address
    port     = 5432
    database = "orders"
  })
}

resource "random_password" "database" {
  length  = 32
  special = true
}

# API Key para servicio externo
resource "aws_secretsmanager_secret" "stripe_api_key" {
  name        = "${var.environment}/stripe/api-key"
  description = "Stripe API key"

  tags = {
    Environment = var.environment
  }
}

# Certificate y private key
resource "aws_secretsmanager_secret" "service_certificate" {
  name        = "${var.environment}/certificates/order-service"
  description = "mTLS certificate for order-service"

  tags = {
    Environment = var.environment
    Service     = "order-service"
  }
}

resource "aws_secretsmanager_secret_version" "service_certificate" {
  secret_id = aws_secretsmanager_secret.service_certificate.id

  secret_string = jsonencode({
    certificate = file("${path.module}/certs/order-service.crt")
    private_key = file("${path.module}/certs/order-service.key")
    ca_cert     = file("${path.module}/certs/ca.crt")
  })
}
```

### .NET: Consumir Secretos

```csharp
// src/Shared/Configuration/SecretsManagerConfigurationSource.cs
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;

public class SecretsManagerConfigurationProvider : ConfigurationProvider
{
    private readonly IAmazonSecretsManager _secretsManager;
    private readonly string _secretName;

    public SecretsManagerConfigurationProvider(string secretName)
    {
        _secretsManager = new AmazonSecretsManagerClient();
        _secretName = secretName;
    }

    public override void Load()
    {
        try
        {
            var request = new GetSecretValueRequest
            {
                SecretId = _secretName
            };

            var response = _secretsManager.GetSecretValueAsync(request).Result;

            if (response.SecretString != null)
            {
                var secrets = JsonSerializer.Deserialize<Dictionary<string, string>>(
                    response.SecretString);

                foreach (var kvp in secrets)
                {
                    Data[kvp.Key] = kvp.Value;
                }
            }
        }
        catch (Exception ex)
        {
            throw new Exception($"Failed to load secrets from {_secretName}", ex);
        }
    }
}

// Extension method para agregar al ConfigurationBuilder
public static class SecretsManagerExtensions
{
    public static IConfigurationBuilder AddSecretsManager(
        this IConfigurationBuilder builder,
        string secretName)
    {
        return builder.Add(new SecretsManagerConfigurationSource(secretName));
    }
}

public class SecretsManagerConfigurationSource : IConfigurationSource
{
    private readonly string _secretName;

    public SecretsManagerConfigurationSource(string secretName)
    {
        _secretName = secretName;
    }

    public IConfigurationProvider Build(IConfigurationBuilder builder)
    {
        return new SecretsManagerConfigurationProvider(_secretName);
    }
}

// Program.cs - Cargar secretos
var builder = WebApplication.CreateBuilder(args);

// Cargar database credentials desde Secrets Manager
builder.Configuration.AddSecretsManager("prod/database/password");

// Ahora las credenciales están disponibles en Configuration
var connectionString =
    $"Host={builder.Configuration["host"]};" +
    $"Port={builder.Configuration["port"]};" +
    $"Database={builder.Configuration["database"]};" +
    $"Username={builder.Configuration["username"]};" +
    $"Password={builder.Configuration["password"]};";

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(connectionString));
```

### Service con Secrets

```csharp
// src/PaymentService/Services/StripePaymentService.cs
public class StripePaymentService
{
    private readonly IAmazonSecretsManager _secretsManager;
    private string _cachedApiKey;
    private DateTime _cacheExpiration;

    public StripePaymentService(IAmazonSecretsManager secretsManager)
    {
        _secretsManager = secretsManager;
    }

    private async Task<string> GetApiKeyAsync()
    {
        // Cache API key por 1 hora (balance entre performance y seguridad)
        if (_cachedApiKey != null && DateTime.UtcNow < _cacheExpiration)
        {
            return _cachedApiKey;
        }

        var request = new GetSecretValueRequest
        {
            SecretId = "prod/stripe/api-key"
        };

        var response = await _secretsManager.GetSecretValueAsync(request);
        var secret = JsonSerializer.Deserialize<Dictionary<string, string>>(
            response.SecretString);

        _cachedApiKey = secret["api_key"];
        _cacheExpiration = DateTime.UtcNow.AddHours(1);

        return _cachedApiKey;
    }

    public async Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request)
    {
        var apiKey = await GetApiKeyAsync();

        // Usar Stripe SDK con API key
        StripeConfiguration.ApiKey = apiKey;

        var options = new ChargeCreateOptions
        {
            Amount = (long)(request.Amount * 100), // Convertir a centavos
            Currency = "pen",
            Source = request.Token,
            Description = $"Payment for order {request.OrderId}"
        };

        var service = new ChargeService();
        var charge = await service.CreateAsync(options);

        return new PaymentResult
        {
            Success = charge.Status == "succeeded",
            TransactionId = charge.Id
        };
    }
}
```

---

## Gestión de Claves Criptográficas

### ¿Qué es?

Gestión de claves criptográficas (encryption keys) usadas para cifrar datos at-rest y in-transit.

**Propósito:** Centralizar, auditar y rotar claves de cifrado.

**Componentes de AWS KMS:**

- **Customer Master Keys (CMK)**: Claves maestras
- **Data Encryption Keys (DEK)**: Claves derivadas
- **Envelope Encryption**: CMK cifra DEK, DEK cifra datos

**Beneficios:**
✅ Claves nunca salen de HSM
✅ Auditoría completa con CloudTrail
✅ Rotación automática anual
✅ Grants para permisos granulares

### Terraform: KMS Keys por Tipo de Dato

```hcl
# terraform/modules/kms/main.tf

# KMS key para EBS volumes
resource "aws_kms_key" "ebs" {
  description             = "KMS key for EBS volume encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true  # Rotación automática cada año

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
        Sid    = "Allow ECS to use the key"
        Effect = "Allow"
        Principal = {
          Service = "ecs.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Purpose = "EBS encryption"
  }
}

resource "aws_kms_alias" "ebs" {
  name          = "alias/${var.environment}-ebs-encryption"
  target_key_id = aws_kms_key.ebs.key_id
}

# KMS key para RDS
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Purpose = "RDS encryption"
  }
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.environment}-rds-encryption"
  target_key_id = aws_kms_key.rds.key_id
}

# KMS key para S3
resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 bucket encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Purpose = "S3 encryption"
  }
}

# KMS key para application-level encryption
resource "aws_kms_key" "application" {
  description             = "KMS key for application data encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

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
        Sid    = "Allow application to encrypt/decrypt"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.order_service.arn
        }
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Purpose = "Application data encryption"
  }
}
```

### .NET: Usar KMS para Envelope Encryption

```csharp
// src/Shared/Encryption/KmsEncryptionService.cs
using Amazon.KeyManagementService;
using Amazon.KeyManagementService.Model;

public class KmsEncryptionService
{
    private readonly IAmazonKeyManagementService _kms;
    private readonly string _keyId;

    public KmsEncryptionService(
        IAmazonKeyManagementService kms,
        IConfiguration configuration)
    {
        _kms = kms;
        _keyId = configuration["Encryption:KmsKeyId"];
    }

    // Envelope encryption: KMS genera y cifra DEK, usamos DEK para cifrar datos
    public async Task<EncryptedData> EncryptAsync(byte[] plaintext)
    {
        // 1. Generar Data Encryption Key (DEK)
        var generateRequest = new GenerateDataKeyRequest
        {
            KeyId = _keyId,
            KeySpec = DataKeySpec.AES_256
        };

        var generateResponse = await _kms.GenerateDataKeyAsync(generateRequest);

        // 2. Usar DEK (plaintext) para cifrar datos con AES
        using var aes = Aes.Create();
        aes.Key = generateResponse.Plaintext.ToArray();
        aes.GenerateIV();

        using var encryptor = aes.CreateEncryptor();
        using var ms = new MemoryStream();

        ms.Write(aes.IV, 0, aes.IV.Length);

        using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
        {
            cs.Write(plaintext, 0, plaintext.Length);
        }

        // 3. Retornar: datos cifrados + DEK cifrado (no plaintext DEK)
        return new EncryptedData
        {
            CiphertextBlob = ms.ToArray(),
            EncryptedDataKey = generateResponse.CiphertextBlob.ToArray()
        };
    }

    public async Task<byte[]> DecryptAsync(EncryptedData encryptedData)
    {
        // 1. Pedir a KMS que descifre el DEK
        var decryptRequest = new DecryptRequest
        {
            CiphertextBlob = new MemoryStream(encryptedData.EncryptedDataKey)
        };

        var decryptResponse = await _kms.DecryptAsync(decryptRequest);
        var dataKey = decryptResponse.Plaintext.ToArray();

        // 2. Usar DEK para descifrar datos
        using var aes = Aes.Create();
        aes.Key = dataKey;

        // Extraer IV del inicio
        var iv = new byte[aes.IV.Length];
        Array.Copy(encryptedData.CiphertextBlob, 0, iv, 0, iv.Length);
        aes.IV = iv;

        using var decryptor = aes.CreateDecryptor();
        using var ms = new MemoryStream(
            encryptedData.CiphertextBlob,
            iv.Length,
            encryptedData.CiphertextBlob.Length - iv.Length);
        using var cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read);
        using var output = new MemoryStream();

        cs.CopyTo(output);
        return output.ToArray();
    }
}

public class EncryptedData
{
    public byte[] CiphertextBlob { get; set; }
    public byte[] EncryptedDataKey { get; set; }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** almacenar todos los secretos en AWS Secrets Manager
- **MUST** rotar secretos críticos cada 90 días máximo
- **MUST** usar KMS para encryption keys
- **MUST** habilitar rotación automática de KMS keys
- **MUST** usar separate KMS keys por tipo de dato (EBS, RDS, S3, app)
- **MUST** habilitar CloudTrail para auditar accesos a secretos/keys

### SHOULD

- **SHOULD** cache secretos en memoria por max 1 hora
- **SHOULD** usar Envelope Encryption para datos grandes
- **SHOULD** separate KMS keys por ambiente (dev/staging/prod)

### MUST NOT

- **MUST NOT** hardcodear secretos en código
- **MUST NOT** commitear secretos a Git
- **MUST NOT** compartir secretos entre ambientes
- **MUST NOT** usar claves de cifrado custom sin KMS

---

## Referencias

- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [AWS KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)
- [Envelope Encryption](https://docs.aws.amazon.com/wellarchitected/latest/financial-services-industry-lens/use-envelope-encryption-with-customer-master-keys.html)
- [Data Protection](./data-protection.md)
- [SSO, MFA y RBAC](./sso-mfa-rbac.md)
