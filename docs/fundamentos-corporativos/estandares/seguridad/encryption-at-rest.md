---
id: encryption-at-rest
sidebar_position: 32
title: Encryption at Rest
description: Cifrar datos almacenados para proteger confidencialidad
---

# Encryption at Rest

## Contexto

Este estándar establece **Encryption at Rest**: TODOS los datos sensibles DEBEN estar cifrados en storage. protege contra acceso físico, snapshots robados, backups expuestos. Complementa el [lineamiento de Protección de Datos](../../lineamientos/seguridad/07-proteccion-de-datos.md) mediante **cifrado en storage**.

---

## Encryption Strategy

```yaml
# ✅ Qué cifrar (por classification)

RESTRICTED data: ✅ MUST encrypt con KMS customer-managed keys
  - RDS databases
  - S3 buckets (PII)
  - EBS volumes
  - Secrets Manager
  - Parameter Store (SecureString)

CONFIDENTIAL data: ✅ MUST encrypt (AWS-managed keys OK)
  - RDS databases
  - S3 buckets
  - EFS file systems
  - DynamoDB tables

INTERNAL data: ✅ SHOULD encrypt (best practice)

PUBLIC data: ⚫ Optional (no sensitive data)

Encryption Types:
  - Server-Side Encryption (SSE): AWS maneja keys
  - Customer-Managed Keys (CMK): Control completo
  - Client-Side Encryption: App cifra antes de enviar
```

## RDS Encryption

```hcl
# ✅ PostgreSQL RDS con encryption

# KMS Key para RDS (customer-managed)
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true  # ✅ Auto-rotate anualmente

  tags = {
    Name = "rds-encryption-key"
    Classification = "RESTRICTED"
  }
}

resource "aws_kms_alias" "rds" {
  name          = "alias/rds-sales-db"
  target_key_id = aws_kms_key.rds.key_id
}

# RDS Instance con encryption
resource "aws_db_instance" "sales" {
  identifier = "sales-db"
  engine     = "postgres"
  engine_version = "16.1"

  instance_class = "db.r6g.large"
  allocated_storage = 100

  # ✅ Encryption ENABLED
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  # ✅ Encrypted backups
  backup_retention_period = 30
  backup_window          = "03:00-04:00"

  # ✅ Encrypted snapshots
  copy_tags_to_snapshot = true

  # ✅ IAM authentication (no passwords en conexión)
  iam_database_authentication_enabled = true

  # ✅ TLS required
  parameter_group_name = aws_db_parameter_group.sales.name

  tags = {
    Classification = "RESTRICTED"
  }
}

# Force SSL connections
resource "aws_db_parameter_group" "sales" {
  name   = "sales-pg"
  family = "postgres16"

  parameter {
    name  = "rds.force_ssl"
    value = "1"  # ✅ TLS required
  }

  parameter {
    name  = "ssl_min_protocol_version"
    value = "TLSv1.3"  # ✅ TLS 1.3 only
  }
}
```

## S3 Encryption

```hcl
# ✅ S3 Bucket con encryption

resource "aws_kms_key" "s3" {
  description = "KMS key for S3 encryption"
  deletion_window_in_days = 30
  enable_key_rotation = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow S3 to use key"
        Effect = "Allow"
        Principal = { Service = "s3.amazonaws.com" }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_s3_bucket" "sales_documents" {
  bucket = "talma-sales-documents"

  tags = {
    Classification = "RESTRICTED"
  }
}

# Server-Side Encryption Configuration
resource "aws_s3_bucket_server_side_encryption_configuration" "sales_documents" {
  bucket = aws_s3_bucket.sales_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true  # ✅ Reduce KMS API calls (cost optimization)
  }
}

# Enforce encryption (deny unencrypted uploads)
resource "aws_s3_bucket_policy" "sales_documents" {
  bucket = aws_s3_bucket.sales_documents.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyUnencryptedObjectUploads"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.sales_documents.arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:x-amz-server-side-encryption" = "aws:kms"
          }
        }
      }
    ]
  })
}
```

## Application-Level Encryption

```csharp
// ✅ Field-level encryption (sensitive fields)

public class CustomerRepository : ICustomerRepository
{
    private readonly SalesDbContext _context;
    private readonly IDataProtector _protector;

    public CustomerRepository(
        SalesDbContext context,
        IDataProtectionProvider dataProtection)
    {
        _context = context;
        _protector = dataProtection.CreateProtector("CustomerData.v1");
    }

    public async Task<Guid> SaveAsync(Customer customer)
    {
        // ✅ Encrypt RESTRICTED fields antes de storage
        var entity = new CustomerEntity
        {
            CustomerId = customer.CustomerId,
            EmailEncrypted = _protector.Protect(customer.Email),
            PhoneEncrypted = _protector.Protect(customer.Phone),
            AddressEncrypted = _protector.Protect(customer.Address),
            CreatedAt = DateTime.UtcNow
        };

        await _context.Customers.AddAsync(entity);
        await _context.SaveChangesAsync();

        return entity.CustomerId;
    }

    public async Task<Customer?> GetByIdAsync(Guid customerId)
    {
        var entity = await _context.Customers.FindAsync(customerId);
        if (entity == null) return null;

        // ✅ Decrypt al leer
        return new Customer
        {
            CustomerId = entity.CustomerId,
            Email = _protector.Unprotect(entity.EmailEncrypted),
            Phone = _protector.Unprotect(entity.PhoneEncrypted),
            Address = _protector.Unprotect(entity.AddressEncrypted),
            CreatedAt = entity.CreatedAt
        };
    }
}

// Startup configuration
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // ✅ Data Protection con AWS KMS
        services.AddDataProtection()
            .PersistKeysToAWSSystemsManager("/DataProtection/Keys")
            .ProtectKeysWithAwsKms(
                kmsKeyId: "arn:aws:kms:us-east-1:123456789012:key/abc-123",
                kmsClient: new AmazonKeyManagementServiceClient()
            );
    }
}
```

## Key Management

```yaml
# ✅ Gestión de KMS Keys

Key Hierarchy:

  Root Key (AWS-managed):
    - Hardware Security Module (HSM)
    - Never leaves AWS
    - Auto-rotates

  Customer Master Key (CMK):
    - Created per service/purpose
    - Rotation: Annual (automatic)
    - Deletion: 30 day window (recovery possible)

    Examples:
      - kms-rds-sales-db
      - kms-s3-documents
      - kms-secrets-manager

  Data Encryption Keys (DEK):
    - Generated per object
    - Encrypted by CMK (envelope encryption)
    - Stored with data

Key Policies:

  Least Privilege:
    - Sales Service: Can Decrypt (read data)
    - Admin: Can Encrypt + Decrypt
    - Backup: Can Decrypt (for restore)

  Segregation:
    - Dev account: Separate keys
    - Prod account: Separate keys
    - No cross-account access

Key Rotation:

  Automatic:
    ✅ Enable for all CMKs
    ✅ AWS rotates annually
    ✅ Old key versions retained (decrypt old data)

  Manual:
    - Create nuevo CMK
    - Re-encrypt data con new key
    - Deprecate old key (after migration)

  Validation:
    aws kms describe-key --key-id alias/rds-sales-db
    # Check: KeyRotationEnabled = true
```

## Monitoring

```yaml
# ✅ Monitorear encryption usage

CloudWatch Metrics:
  1. KMS API Calls:
    - Encrypt/Decrypt operations
    - Alert si spike inusual (possible attack)

  2. Failed Decrypt Attempts:
    - Access denied errors
    - Alert (unauthorized access)

  3. Key Disabled/Deleted:
    - CRITICAL (data inaccesible)
    - Alert immediately

CloudTrail Events:
  Monitor:
    - DisableKey
    - ScheduleKeyDeletion
    - PutKeyPolicy (permission changes)
    - RotateKey

  Alert on:
    - Unauthorized key access
    - Key policy modifications
    - Key deletion attempts

Compliance Checks:
  Daily automated scan: ✅ All RDS instances encrypted?
    ✅ All S3 buckets encrypted?
    ✅ EBS volumes encrypted?
    ✅ Secrets encrypted?

  Script:
    # Check RDS encryption
    aws rds describe-db-instances \
    --query 'DBInstances[?StorageEncrypted==`false`]'

    # Should return empty (all encrypted)
```

## Backup Encryption

```yaml
# ✅ Encrypted backups

RDS Automated Backups:
  - Encrypted if source encrypted ✅
  - Same KMS key as source
  - Retention: 30 días
  - Cross-region: Also encrypted

  Manual snapshot:
    aws rds create-db-snapshot \
      --db-instance-identifier sales-db \
      --db-snapshot-identifier sales-backup-2024-02 \
      --kms-key-id arn:aws:kms:...:key/...  # ✅ Specify key

S3 Cross-Region Replication:
  - Encrypted during replication ✅
  - Can use different key (destination region)

  Config:
    {
      "Rules": [{
        "Status": "Enabled",
        "Priority": 1,
        "Destination": {
          "Bucket": "arn:aws:s3:::talma-backups-us-west-2",
          "EncryptionConfiguration": {
            "ReplicaKmsKeyID": "arn:aws:kms:us-west-2:...:key/..."
          }
        },
        "SourceSelectionCriteria": {
          "SseKmsEncryptedObjects": {
            "Status": "Enabled"  # ✅ Replicate encrypted
          }
        }
      }]
    }

EBS Snapshots:
  - Encrypted if source encrypted
  - Can share encrypted snapshots via KMS grants

  Create:
    aws ec2 create-snapshot \
      --volume-id vol-abc123 \
      --description "Sales DB volume backup" \
      --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Encrypted,Value=true}]'
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** encriptar RESTRICTED y CONFIDENTIAL data at rest
- **MUST** usar KMS customer-managed keys para RESTRICTED
- **MUST** enable key rotation (annual)
- **MUST** enforce encryption (deny unencrypted writes)
- **MUST** encriptar backups y snapshots
- **MUST** usar TLS 1.3 para connections (RDS, etc.)

### SHOULD (Fuertemente recomendado)

- **SHOULD** field-level encryption para PII
- **SHOULD** monitorear KMS usage (CloudWatch)
- **SHOULD** audit key access (CloudTrail)
- **SHOULD** test decryption (disaster recovery)

### MUST NOT (Prohibido)

- **MUST NOT** almacenar RESTRICTED sin encryption
- **MUST NOT** usar hardcoded encryption keys
- **MUST NOT** share keys cross-account sin justificación
- **MUST NOT** disable key rotation

---

## Referencias

- [Lineamiento: Protección de Datos](../../lineamientos/seguridad/07-proteccion-de-datos.md)
- [Data Classification](./data-classification.md)
- [Encryption in Transit](./encryption-in-transit.md)
- [Key Management](./key-management.md)
