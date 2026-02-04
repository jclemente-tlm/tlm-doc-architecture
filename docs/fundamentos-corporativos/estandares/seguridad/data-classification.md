---
id: data-classification
sidebar_position: 6
title: Clasificación de Datos
description: Estándar para clasificar datos en 4 niveles (Public, Internal, Confidential, Restricted) con controles específicos de seguridad
---

# Estándar Técnico — Clasificación de Datos

---

## 1. Propósito

Establecer sistema de clasificación de datos en 4 niveles (Public, Internal, Confidential, Restricted) con controles de seguridad, encriptación, acceso y retención específicos para cada categoría, cumpliendo GDPR y regulaciones locales.

---

## 2. Alcance

**Aplica a:**

- Todos los datos en sistemas corporativos
- Bases de datos (PostgreSQL, Oracle, SQL Server)
- Archivos en S3
- Documentos en repositorios
- Datos en tránsito y en reposo

**No aplica a:**

- Datos públicos ya publicados oficialmente
- Metadatos de sistema (no sensibles)

---

## 3. Niveles de Clasificación

| Nivel               | Descripción                              | Ejemplos                                           | Impacto si se Compromete |
| ------------------- | ---------------------------------------- | -------------------------------------------------- | ------------------------ |
| **🌐 Public**       | Información pública sin restricciones    | Marketing, precios públicos, comunicados de prensa | BAJO                     |
| **🔒 Internal**     | Información interna solo para empleados  | Políticas internas, org charts, roadmaps           | MEDIO                    |
| **🔐 Confidential** | Información sensible del negocio         | Contratos, financieros, datos de clientes          | ALTO                     |
| **🚨 Restricted**   | Información altamente sensible, regulada | PII, PCI DSS, salud, credenciales                  | CRÍTICO                  |

---

## 4. Tecnologías Aprobadas

| Componente         | Tecnología         | Versión mínima | Observaciones             |
| ------------------ | ------------------ | -------------- | ------------------------- |
| **Encryption**     | AWS KMS            | -              | At-rest encryption        |
| **TLS**            | TLS 1.3            | -              | In-transit encryption     |
| **Masking**        | Entity Framework   | 8.0+           | Column-level encryption   |
| **Access Control** | AWS IAM + Keycloak | -              | RBAC granular             |
| **DLP**            | Manual policies    | -              | Data Loss Prevention      |
| **Tagging**        | AWS Tags           | -              | Clasificación en metadata |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 5. Requisitos Obligatorios 🔴

### Por Nivel de Clasificación

#### 🌐 Public

- [ ] **Sin encriptación obligatoria** (opcional)
- [ ] **Acceso público permitido**
- [ ] **No requiere autenticación**
- [ ] **Puede estar en CDN**
- [ ] **Logs básicos**

#### 🔒 Internal

- [ ] **Encriptación in-transit** (TLS 1.3)
- [ ] **Autenticación obligatoria** (Keycloak SSO)
- [ ] **Acceso solo empleados**
- [ ] **Logs de acceso**
- [ ] **Retención según política corporativa**

#### 🔐 Confidential

- [ ] **Encriptación at-rest** (AWS KMS)
- [ ] **Encriptación in-transit** (TLS 1.3)
- [ ] **MFA obligatorio**
- [ ] **RBAC granular** (claims específicos)
- [ ] **Logs de acceso + auditoría**
- [ ] **Retención mínima/máxima definida**
- [ ] **Data masking en logs**
- [ ] **Backups encriptados**

#### 🚨 Restricted

- [ ] **TODO lo de Confidential +**
- [ ] **Column-level encryption** (BD)
- [ ] **Tokenization** para PCI DSS
- [ ] **Acceso con aprobación** (workflow)
- [ ] **Logs inmutables** (CloudTrail)
- [ ] **Alertas de acceso** (CloudWatch)
- [ ] **Retención regulatoria** (GDPR, SOX)
- [ ] **Right to be forgotten** (GDPR)
- [ ] **Data residency** (país específico)
- [ ] **NO copiar a ambientes no productivos**

---

## 6. Ejemplos de Clasificación

### Restricted 🚨

- **PII**: Nombres completos + DNI/pasaporte
- **PCI DSS**: Números de tarjeta, CVV
- **Salud**: Historiales médicos (HIPAA)
- **Credenciales**: Passwords, API keys, tokens
- **Financiero**: Cuentas bancarias, SSN

### Confidential 🔐

- **Contratos**: Acuerdos con clientes
- **Financiero**: Estados financieros no publicados
- **Estratégico**: Roadmaps de producto
- **Legal**: Documentos legales internos
- **Email corporativo**: Comunicaciones internas

### Internal 🔒

- **Políticas**: Manuales de empleados
- **Organización**: Organigramas
- **Proyectos**: Planes de proyecto internos
- **Configuraciones**: Infraestructura interna

### Public 🌐

- **Marketing**: Blog posts, whitepapers
- **Precios**: Tarifas públicas
- **Documentación**: User guides públicos
- **Comunicados**: Press releases

---

## 7. Implementación por Capa

### Base de Datos - PostgreSQL

```sql
-- Tabla con columnas clasificadas
CREATE TABLE customers (
    id UUID PRIMARY KEY,

    -- PUBLIC 🌐
    country VARCHAR(2),  -- No sensible

    -- INTERNAL 🔒
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    -- CONFIDENTIAL 🔐
    email VARCHAR(255),
    phone VARCHAR(20),

    -- RESTRICTED 🚨 (encriptado)
    full_name BYTEA,  -- Encriptado con KMS
    ssn BYTEA,        -- Encriptado
    credit_card BYTEA -- Tokenizado + encriptado
);

-- Row-Level Security para Confidential/Restricted
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY customer_access ON customers
  USING (
    -- Solo ver datos de su tenant
    tenant_id = current_setting('app.current_tenant')::uuid
    AND
    -- Solo con rol adecuado
    current_setting('app.user_role') IN ('admin', 'customer_service')
  );

-- Audit logging para accesos
CREATE TABLE customer_access_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    accessed_by VARCHAR(255),
    accessed_at TIMESTAMP DEFAULT NOW(),
    action VARCHAR(50),
    ip_address INET
);
```

### .NET - Column Encryption

```csharp
// Entities/Customer.cs
public class Customer
{
    public Guid Id { get; set; }

    // PUBLIC 🌐
    public string Country { get; set; }

    // INTERNAL 🔒
    public DateTime CreatedAt { get; set; }

    // CONFIDENTIAL 🔐
    public string Email { get; set; }
    public string Phone { get; set; }

    // RESTRICTED 🚨 (encriptado)
    [Encrypted]  // Custom attribute
    public string FullName { get; set; }

    [Encrypted]
    public string SSN { get; set; }

    [Tokenized]  // PCI DSS
    public string CreditCard { get; set; }
}

// Services/EncryptionService.cs
public class EncryptionService
{
    private readonly IAmazonKeyManagementService _kms;
    private readonly string _kmsKeyId;

    public async Task<string> EncryptAsync(string plaintext)
    {
        var request = new EncryptRequest
        {
            KeyId = _kmsKeyId,
            Plaintext = new MemoryStream(Encoding.UTF8.GetBytes(plaintext))
        };

        var response = await _kms.EncryptAsync(request);
        return Convert.ToBase64String(response.CiphertextBlob.ToArray());
    }

    public async Task<string> DecryptAsync(string ciphertext)
    {
        var request = new DecryptRequest
        {
            CiphertextBlob = new MemoryStream(Convert.FromBase64String(ciphertext))
        };

        var response = await _kms.DecryptAsync(request);
        return Encoding.UTF8.GetString(response.Plaintext.ToArray());
    }
}

// Interceptor para auto-encrypt/decrypt
public class EncryptionInterceptor : SaveChangesInterceptor
{
    private readonly EncryptionService _encryption;

    public override async ValueTask<InterceptionResult<int>> SavingChangesAsync(
        DbContextEventData eventData,
        InterceptionResult<int> result,
        CancellationToken cancellationToken = default)
    {
        var entries = eventData.Context.ChangeTracker.Entries()
            .Where(e => e.State == EntityState.Added || e.State == EntityState.Modified);

        foreach (var entry in entries)
        {
            foreach (var property in entry.Properties)
            {
                var attribute = property.Metadata.PropertyInfo
                    ?.GetCustomAttribute<EncryptedAttribute>();

                if (attribute != null && property.CurrentValue != null)
                {
                    var plaintext = property.CurrentValue.ToString();
                    property.CurrentValue = await _encryption.EncryptAsync(plaintext);
                }
            }
        }

        return await base.SavingChangesAsync(eventData, result, cancellationToken);
    }
}
```

### Logs - Masking de Datos Sensibles

```csharp
// Logging/SensitiveDataMasker.cs
public class SensitiveDataMasker
{
    private static readonly Regex EmailRegex = new(@"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b");
    private static readonly Regex CreditCardRegex = new(@"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b");
    private static readonly Regex SSNRegex = new(@"\b\d{3}-\d{2}-\d{4}\b");

    public static string Mask(string message)
    {
        if (string.IsNullOrEmpty(message)) return message;

        // Mask emails: user@domain.com → u***@domain.com
        message = EmailRegex.Replace(message, m =>
        {
            var email = m.Value;
            var parts = email.Split('@');
            return $"{parts[0][0]}***@{parts[1]}";
        });

        // Mask credit cards: 4532-1234-5678-9010 → ****-****-****-9010
        message = CreditCardRegex.Replace(message, m => "****-****-****-" + m.Value.Substring(m.Value.Length - 4));

        // Mask SSN: 123-45-6789 → ***-**-6789
        message = SSNRegex.Replace(message, m => "***-**-" + m.Value.Substring(m.Value.Length - 4));

        return message;
    }
}

// Uso con Serilog
Log.Logger = new LoggerConfiguration()
    .Enrich.With(new SensitiveDataMaskingEnricher())
    .WriteTo.GrafanaLoki("http://loki:3100")
    .CreateLogger();
```

---

## 8. AWS Tagging para Clasificación

```hcl
# Terraform - RDS con clasificación
resource "aws_db_instance" "customer_db" {
  identifier     = "customer-db-prod"
  engine         = "postgres"

  # Encryption (CONFIDENTIAL+)
  storage_encrypted = true
  kms_key_id        = aws_kms_key.confidential.arn

  tags = {
    DataClassification = "Confidential"  # 🔐
    Contains_PII       = "true"
    Compliance         = "GDPR"
    RetentionPeriod    = "7-years"
  }
}

resource "aws_s3_bucket" "marketing" {
  bucket = "marketing-assets-prod"

  tags = {
    DataClassification = "Public"  # 🌐
    Contains_PII       = "false"
  }
}

resource "aws_s3_bucket" "customer_documents" {
  bucket = "customer-docs-prod"

  tags = {
    DataClassification = "Restricted"  # 🚨
    Contains_PII       = "true"
    Compliance         = "PCI-DSS,GDPR"
    RetentionPeriod    = "indefinite"
    DataResidency      = "PE"  # Perú
  }
}
```

---

## 9. Matriz de Controles

| Control                   | Public | Internal | Confidential | Restricted |
| ------------------------- | ------ | -------- | ------------ | ---------- |
| **Encryption at-rest**    | ❌     | ❌       | ✅           | ✅         |
| **Encryption in-transit** | ❌     | ✅       | ✅           | ✅         |
| **Authentication**        | ❌     | ✅       | ✅           | ✅         |
| **MFA**                   | ❌     | ❌       | ✅           | ✅         |
| **RBAC**                  | ❌     | ✅       | ✅           | ✅         |
| **Audit logging**         | ❌     | ✅       | ✅           | ✅         |
| **Access approval**       | ❌     | ❌       | ❌           | ✅         |
| **Column encryption**     | ❌     | ❌       | ❌           | ✅         |
| **Tokenization**          | ❌     | ❌       | ❌           | ✅ (PCI)   |
| **Data masking in logs**  | ❌     | ❌       | ✅           | ✅         |
| **Backup encryption**     | ❌     | ❌       | ✅           | ✅         |
| **Data residency**        | ❌     | ❌       | ❌           | ✅         |

---

## 10. Retención de Datos

| Clasificación               | Retención Mínima | Retención Máxima | Justificación         |
| --------------------------- | ---------------- | ---------------- | --------------------- |
| **Public**                  | N/A              | Indefinido       | Sin restricciones     |
| **Internal**                | N/A              | 7 años           | Política corporativa  |
| **Confidential**            | 1 año            | 7 años           | Regulaciones fiscales |
| **Restricted (PII)**        | Según regulación | GDPR: Necesidad  | Right to be forgotten |
| **Restricted (Financiero)** | 7 años           | 10 años          | SOX, regulación local |
| **Restricted (PCI DSS)**    | 0 (tokenizar)    | NO almacenar CVV | PCI DSS 3.2.1         |

---

## 11. Validación de Cumplimiento

```bash
# Verificar tags de clasificación en recursos
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=DataClassification \
  --query 'ResourceTagMappingList[*].[ResourceARN, Tags[?Key==`DataClassification`].Value]'

# Listar recursos SIN clasificación
aws resourcegroupstaggingapi get-resources \
  --resource-type-filters rds s3 \
  | jq -r '.ResourceTagMappingList[] | select(.Tags | map(.Key) | contains(["DataClassification"]) | not) | .ResourceARN'

# Verificar encriptación en RDS (Confidential+)
aws rds describe-db-instances \
  --query 'DBInstances[?!StorageEncrypted].[DBInstanceIdentifier,StorageEncrypted]'
```

---

## 12. Referencias

**Regulaciones:**

- [GDPR - General Data Protection Regulation](https://gdpr.eu/)
- [PCI DSS 4.0](https://www.pcisecuritystandards.org/)

**NIST:**

- [NIST 800-60 - Data Classification](https://csrc.nist.gov/publications/detail/sp/800-60/vol-1-rev-1/final)

**ISO:**

- [ISO 27001:2022 - Asset Classification](https://www.iso.org/standard/27001)
