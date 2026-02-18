---
id: data-classification
sidebar_position: 30
title: Data Classification
description: Clasificar datos por nivel de sensibilidad para aplicar controles apropiados
---

# Data Classification

## Contexto

Este estándar establece **Data Classification**: asignar nivel de sensibilidad a datos para aplicar controles apropiados. No todos los datos requieren same protection. Complementa el [lineamiento de Protección de Datos](../../lineamientos/seguridad/07-proteccion-de-datos.md) mediante **clasificación sistemática**.

---

## Classification Levels

```yaml
# ✅ 4 niveles de clasificación

Level 1: PUBLIC
  Definición: Datos diseñados para consumo público

  Ejemplos:
    - Marketing materials
    - Public API documentation
    - Press releases
    - Product catalog (precios públicos)

  Controls:
    - Encryption: NO requerido
    - Access: Público (sin authentication)
    - Backup: Opcional
    - Compliance: Ninguno

  Storage: S3 public bucket, CDN

Level 2: INTERNAL
  Definición: Datos para uso interno, no sensibles

  Ejemplos:
    - Internal documentation
    - Project plans
    - Non-PII operational data
    - Application logs (sin PII)

  Controls:
    - Encryption: Recomendado
    - Access: Authentication required
    - Backup: 7 días
    - Compliance: Ninguno

  Storage: S3 private bucket, RDS (no encryption required)

Level 3: CONFIDENTIAL
  Definición: Datos sensibles de negocio

  Ejemplos:
    - Customer orders
    - Business contracts
    - Financial reports
    - Employee data (no PII crítica)
    - API keys (internal)

  Controls:
    - Encryption: OBLIGATORIO (at rest + transit)
    - Access: RBAC (role-based)
    - Backup: 30 días
    - Audit: CloudTrail logs
    - Compliance: SOC 2

  Storage: RDS encrypted, S3 encrypted

Level 4: RESTRICTED
  Definición: Datos altamente sensibles, regulados

  Ejemplos:
    - PII (nombres, emails, direcciones)
    - Payment data (tarjetas, cuentas bancarias)
    - Health information (PHI)
    - Credentials (passwords, tokens)
    - Social security numbers

  Controls:
    - Encryption: OBLIGATORIO (KMS customer-managed keys)
    - Access: Least privilege (individual approval)
    - Backup: 90 días + cross-region
    - Audit: ALL accesses logged
    - Masking: En logs y no-prod
    - Compliance: PCI-DSS, GDPR, HIPAA

  Storage: RDS encrypted + TDE, Secrets Manager
```

## Classification Process

```yaml
# ✅ Cómo clasificar datos

Step 1: Identify Data Assets
  - List todas las entidades/tablas
  - Identificar campos
  - Documentar propósito

  Example (Sales Service):
    - Customers table
    - Orders table
    - Products table
    - Payments table

Step 2: Classify por Campo

  Customers table:
    - customer_id: INTERNAL (UUID, no sensible)
    - email: RESTRICTED (PII)
    - full_name: RESTRICTED (PII)
    - phone: RESTRICTED (PII)
    - address: RESTRICTED (PII)
    - created_at: INTERNAL
    - is_active: INTERNAL

  Orders table:
    - order_id: INTERNAL
    - customer_id: CONFIDENTIAL (indirectly identifies)
    - total: CONFIDENTIAL (business data)
    - status: INTERNAL
    - created_at: INTERNAL

  Payments table:
    - payment_id: INTERNAL
    - order_id: CONFIDENTIAL
    - card_last_4: RESTRICTED (PCI-DSS)
    - card_token: RESTRICTED (PCI-DSS)
    - amount: CONFIDENTIAL

Step 3: Apply Controls

  RESTRICTED fields:
    ✅ Encrypt at rest (KMS)
    ✅ Encrypt in transit (TLS 1.3)
    ✅ Mask en logs
    ✅ Tokenize si posible
    ✅ Access logs (all queries)
    ✅ Row-level security (user sees only own)

  CONFIDENTIAL fields:
    ✅ Encrypt at rest
    ✅ Encrypt in transit
    ✅ RBAC (authorized users only)
    ✅ Backup 30 días

  INTERNAL fields:
    ✅ Authentication required
    ✅ Backup 7 días

Step 4: Document

  Data Classification Matrix (README.md):

  | Entity    | Field        | Classification | Rationale          |
  |-----------|--------------|----------------|--------------------|
  | Customers | email        | RESTRICTED     | PII (GDPR)         |
  | Customers | full_name    | RESTRICTED     | PII (GDPR)         |
  | Orders    | total        | CONFIDENTIAL   | Business sensitive |
  | Payments  | card_last_4  | RESTRICTED     | PCI-DSS            |
```

## Implementation

```csharp
// ✅ Apply classification en código

// Domain Model
public class Customer
{
    public Guid CustomerId { get; set; }  // INTERNAL

    [Classification(Level.Restricted)]
    [PII]
    public string Email { get; set; }  // RESTRICTED

    [Classification(Level.Restricted)]
    [PII]
    public string FullName { get; set; }  // RESTRICTED

    [Classification(Level.Restricted)]
    [PII]
    public string Phone { get; set; }  // RESTRICTED

    [Classification(Level.Confidential)]
    public DateTime CreatedAt { get; set; }  // INTERNAL (but in confidential entity)
}

// Logging Middleware
public class LoggingMiddleware
{
    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        var request = await FormatRequest(context.Request);

        // ✅ Mask RESTRICTED fields antes de log
        var maskedRequest = MaskSensitiveData(request);

        _logger.LogInformation("Request: {Request}", maskedRequest);

        await next(context);
    }

    private string MaskSensitiveData(string data)
    {
        // Mask emails
        data = Regex.Replace(data, @"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            m => MaskEmail(m.Value));

        // Mask credit cards
        data = Regex.Replace(data, @"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
            "****-****-****-****");

        return data;
    }

    private string MaskEmail(string email)
    {
        var parts = email.Split('@');
        if (parts.Length != 2) return email;

        var local = parts[0];
        var domain = parts[1];

        // user@example.com → u***@example.com
        return $"{local[0]}***@{domain}";
    }
}

// Repository Layer (row-level security)
public class CustomerRepository : ICustomerRepository
{
    public async Task<Customer?> GetByIdAsync(Guid customerId)
    {
        // ✅ RESTRICTED data: Audit all access
        _auditLogger.LogAccess(new
        {
            Entity = "Customer",
            Action = "Read",
            UserId = _currentUser.GetUserId(),
            ResourceId = customerId,
            Timestamp = DateTime.UtcNow,
            Classification = "RESTRICTED"
        });

        // ✅ Row-level security (user sees only own)
        var userCustomerId = _currentUser.GetCustomerId();

        if (customerId != userCustomerId && !_currentUser.IsAdmin())
        {
            throw new UnauthorizedAccessException(
                "Cannot access RESTRICTED data of other customer");
        }

        return await _context.Customers.FindAsync(customerId);
    }
}
```

## Database-Level Classification

```sql
-- ✅ PostgreSQL: Row-level security + encryption

-- Enable RLS
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Policy: Users see only own data (RESTRICTED enforcement)
CREATE POLICY customer_isolation ON customers
  FOR ALL
  TO authenticated_user
  USING (customer_id = current_setting('app.current_customer_id')::uuid);

-- Column-level encryption (pgcrypto extension)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt RESTRICTED fields
UPDATE customers
SET
  email_encrypted = pgp_sym_encrypt(email, 'encryption_key'),
  phone_encrypted = pgp_sym_encrypt(phone, 'encryption_key');

-- View que decrypta (solo para authorized queries)
CREATE VIEW customers_decrypted AS
SELECT
  customer_id,
  pgp_sym_decrypt(email_encrypted, 'encryption_key') AS email,
  pgp_sym_decrypt(phone_encrypted, 'encryption_key') AS phone,
  created_at
FROM customers;

-- Grant access solo a app service account
GRANT SELECT ON customers_decrypted TO sales_app_user;
```

## Compliance Mapping

```yaml
# ✅ Classification → Compliance requirements

RESTRICTED → Regulaciones:
  - GDPR (EU General Data Protection Regulation):
      PII fields: email, name, address, phone
      Rights: Access, rectification, deletion, portability
      Consent: Required for processing
      Breach notification: 72 hours

  - PCI-DSS (Payment Card Industry):
      Payment fields: card_number, cvv, cardholder_name
      Requirements: Encryption, access logs, quarterly scans
      Storage: cvv NEVER stored, card_number tokenized

  - HIPAA (Health Insurance Portability):
      PHI fields: medical records, treatments, diagnoses
      Requirements: Encryption, audit trails, BAA agreements

CONFIDENTIAL → Compliance:
  - SOC 2 Type II:
      Access controls: RBAC
      Change management: Tracked
      Monitoring: CloudWatch

  - ISO 27001: ISMS policies
      Risk assessments
      Incident response

INTERNAL → Compliance:
  - General security best practices
  - Internal audit requirements

PUBLIC → Compliance:
  - Ninguno (by definition)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** clasificar todos los datos (4 niveles)
- **MUST** documentar classification (data dictionary)
- **MUST** encriptar RESTRICTED data (at rest + transit)
- **MUST** mask RESTRICTED en logs
- **MUST** audit access a RESTRICTED data
- **MUST** aplicar row-level security (RESTRICTED)

### SHOULD (Fuertemente recomendado)

- **SHOULD** revisar classification anualmente
- **SHOULD** automated classification (via annotations)
- **SHOULD** training para equipos (cómo clasificar)
- **SHOULD** DLP (Data Loss Prevention) tools

### MUST NOT (Prohibido)

- **MUST NOT** exponer RESTRICTED sin encryption
- **MUST NOT** log RESTRICTED sin masking
- **MUST NOT** permitir public access a CONFIDENTIAL/RESTRICTED
- **MUST NOT** copiar RESTRICTED a non-production sin anonymization

---

## Referencias

- [Lineamiento: Protección de Datos](../../lineamientos/seguridad/07-proteccion-de-datos.md)
- [Encryption at Rest](./encryption-at-rest.md)
- [Data Masking](./data-masking.md)
- [GDPR Compliance](./gdpr-compliance.md)
