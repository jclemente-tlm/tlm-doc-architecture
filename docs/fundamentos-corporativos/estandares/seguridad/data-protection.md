---
id: data-protection
sidebar_position: 7
title: Data Protection
description: Estándares consolidados para cifrado at-rest y in-transit, enmascaramiento, clasificación, minimización, prevención de pérdida de datos y seguridad general de datos
tags:
  [
    seguridad,
    cifrado,
    data-masking,
    clasificacion-datos,
    aws-kms,
    postgresql,
    tls,
  ]
---

# Data Protection

## Contexto

Este estándar consolida **7 conceptos relacionados** con la protección de datos en reposo, tránsito y uso. Complementa los lineamientos de seguridad asegurando confidencialidad, integridad y disponibilidad de información sensible.

**Conceptos incluidos:**

- **Encryption at Rest** → Cifrado de datos almacenados (DB, S3, volúmenes)
- **Encryption in Transit** → Cifrado de datos en tránsito (TLS/HTTPS)
- **Data Masking** → Enmascaramiento de datos sensibles en logs y UIs
- **Data Classification** → Clasificación de sensibilidad (Public, Internal, Confidential, Secret)
- **Data Minimization** → Recopilar solo datos estrictamente necesarios
- **Data Loss Prevention (DLP)** → Prevenir exfiltración de datos sensibles
- **Data Security** → Controles generales de seguridad de datos

---

## Stack Tecnológico

| Componente              | Tecnología       | Versión  | Uso                            |
| ----------------------- | ---------------- | -------- | ------------------------------ |
| **Database**            | PostgreSQL       | 15+      | Almacenamiento de datos        |
| **Database Encryption** | pgcrypto         | Built-in | Column-level encryption        |
| **Key Management**      | AWS KMS          | Latest   | Gestión de claves de cifrado   |
| **Object Storage**      | AWS S3           | Latest   | Almacenamiento de archivos     |
| **TLS Termination**     | Kong API Gateway | 3.5+     | TLS/HTTPS termination          |
| **Logging**             | Serilog          | 3.1+     | Structured logging con masking |
| **Runtime**             | .NET             | 8.0+     | Aplicaciones                   |

---

## Cifrado en Reposo

### ¿Qué es Encryption at Rest?

Cifrado de datos almacenados en discos, bases de datos, backups y almacenamiento de objetos. Protege datos cuando el sistema está comprometido o medios físicos son robados.

**Propósito:** Proteger confidencialidad de datos incluso si se accede físicamente al storage.

**Métodos:**

- **Full Disk Encryption (FDE)**: Todo el volumen cifrado (AWS EBS encryption)
- **Database Encryption**: Transparent Data Encryption (TDE) o column-level
- **Application-level Encryption**: Aplicación cifra antes de almacenar
- **File/Object Encryption**: Archivos individuales cifrados (S3 SSE)

**Beneficios:**
✅ Protección contra robo físico
✅ Compliance con PCI-DSS, HIPAA, GDPR
✅ Protección de backups
✅ Defensa en profundidad

### Implementación: PostgreSQL Column-Level Encryption

```csharp
// src/Shared/Security/DataEncryption.cs
using System.Security.Cryptography;
using System.Text;

public class DataEncryptionService
{
    private readonly byte[] _encryptionKey;

    public DataEncryptionService(IConfiguration configuration)
    {
        // Obtener clave desde AWS KMS o Secrets Manager
        var base64Key = configuration["Encryption:DataKey"];
        _encryptionKey = Convert.FromBase64String(base64Key);
    }

    public string EncryptString(string plainText)
    {
        if (string.IsNullOrEmpty(plainText))
            return plainText;

        using var aes = Aes.Create();
        aes.Key = _encryptionKey;
        aes.GenerateIV();

        using var encryptor = aes.CreateEncryptor();
        using var ms = new MemoryStream();

        // Escribir IV al inicio (necesario para decrypt)
        ms.Write(aes.IV, 0, aes.IV.Length);

        using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
        using (var sw = new StreamWriter(cs))
        {
            sw.Write(plainText);
        }

        return Convert.ToBase64String(ms.ToArray());
    }

    public string DecryptString(string cipherText)
    {
        if (string.IsNullOrEmpty(cipherText))
            return cipherText;

        var cipherBytes = Convert.FromBase64String(cipherText);

        using var aes = Aes.Create();
        aes.Key = _encryptionKey;

        // Extraer IV del inicio
        var iv = new byte[aes.IV.Length];
        Array.Copy(cipherBytes, 0, iv, 0, iv.Length);
        aes.IV = iv;

        using var decryptor = aes.CreateDecryptor();
        using var ms = new MemoryStream(cipherBytes, iv.Length, cipherBytes.Length - iv.Length);
        using var cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read);
        using var sr = new StreamReader(cs);

        return sr.ReadToEnd();
    }
}

// Entity con campo cifrado
public class Customer
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }

    // Número de tarjeta cifrado
    public string EncryptedCreditCard { get; set; }

    [NotMapped] // No mapear directamente a columna
    public string CreditCardNumber
    {
        get => _encryptionService.DecryptString(EncryptedCreditCard);
        set => EncryptedCreditCard = _encryptionService.EncryptString(value);
    }
}

// Service usando cifrado
public class CustomerService
{
    private readonly DataEncryptionService _encryption;
    private readonly AppDbContext _context;

    public async Task CreateCustomerAsync(CreateCustomerRequest request)
    {
        var customer = new Customer
        {
            Name = request.Name,
            Email = request.Email,
            CreditCardNumber = request.CreditCardNumber // Automáticamente cifrado
        };

        _context.Customers.Add(customer);
        await _context.SaveChangesAsync();
    }
}
```

### PostgreSQL: Transparent Column Encryption con pgcrypto

```sql
-- Habilitar extensión pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Crear tabla con columna cifrada
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    encrypted_credit_card BYTEA,  -- Almacenar cifrado
    created_at TIMESTAMP DEFAULT NOW()
);

-- Función para cifrar
CREATE OR REPLACE FUNCTION encrypt_credit_card(plain_text TEXT, key TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(plain_text, key);
END;
$$ LANGUAGE plpgsql;

-- Función para descifrar
CREATE OR REPLACE FUNCTION decrypt_credit_card(cipher_text BYTEA, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(cipher_text, key);
END;
$$ LANGUAGE plpgsql;

-- Insert cifrado
INSERT INTO customers (name, email, encrypted_credit_card)
VALUES (
    'Juan Perez',
    'juan@example.com',
    encrypt_credit_card('4532-1234-5678-9010', 'encryption_key_from_kms')
);

-- Select descifrado
SELECT
    id,
    name,
    email,
    decrypt_credit_card(encrypted_credit_card, 'encryption_key_from_kms') AS credit_card
FROM customers;
```

### Terraform: AWS EBS Volume Encryption

```hcl
# terraform/modules/ecs-task/main.tf

# EBS volumes cifrados por defecto
resource "aws_ebs_encryption_by_default" "enabled" {
  enabled = true
}

# KMS key para cifrado EBS
resource "aws_kms_key" "ebs" {
  description = "KMS key for EBS volume encryption"

  enable_key_rotation = true  # Rotación automática anual

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
    Purpose = "EBS volume encryption"
  }
}

resource "aws_kms_alias" "ebs" {
  name          = "alias/ebs-encryption"
  target_key_id = aws_kms_key.ebs.key_id
}

# RDS instance con encryption
resource "aws_db_instance" "main" {
  identifier = "orders-db-prod"

  engine         = "postgres"
  engine_version = "15.4"

  # Cifrado at-rest obligatorio
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  # ... otras configuraciones ...
}

# S3 bucket con cifrado
resource "aws_s3_bucket" "data" {
  bucket = "talma-data-prod"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true  # Reduce llamadas a KMS
  }
}
```

---

## Cifrado en Tránsito

### ¿Qué es Encryption in Transit?

Cifrado de datos mientras se transmiten entre sistemas usando TLS (Transport Layer Security). Protege contra interceptación y man-in-the-middle.

**Propósito:** Garantizar confidencialidad e integridad durante transmisión.

**Componentes:**

- **TLS 1.3**: Protocolo de cifrado moderno
- **Certificate Validation**: Validar identidad del servidor
- **Mutual TLS (mTLS)**: Autenticación bidireccional
- **Perfect Forward Secrecy**: Claves de sesión únicas

**Beneficios:**
✅ Protección contra eavesdropping
✅ Protección contra MITM attacks
✅ Cumplimiento PCI-DSS, HIPAA
✅ Confianza del usuario (HTTPS)

### Configuración: .NET HTTPS Strict

```csharp
// src/OrderService.Api/Program.cs
var builder = WebApplication.CreateBuilder(args);

// Forzar HTTPS en todas las requests
builder.Services.AddHttpsRedirection(options =>
{
    options.RedirectStatusCode = StatusCodes.Status308PermanentRedirect;
    options.HttpsPort = 443;
});

// HSTS (HTTP Strict Transport Security)
builder.Services.AddHsts(options =>
{
    options.MaxAge = TimeSpan.FromDays(365);
    options.IncludeSubDomains = true;
    options.Preload = true; // Incluir en HSTS preload list
});

// Configurar Kestrel para TLS 1.3 only
builder.WebHost.ConfigureKestrel(options =>
{
    options.ConfigureHttpsDefaults(httpsOptions =>
    {
        // Solo TLS 1.3 (más seguro)
        httpsOptions.SslProtocols = SslProtocols.Tls13;

        // Carga certificado desde AWS Secrets Manager
        httpsOptions.ServerCertificateSelector = (context, name) =>
        {
            return LoadCertificateFromSecretsManager("tls/order-service/certificate");
        };
    });
});

var app = builder.Build();

// Middleware ordering correcto
if (!app.Environment.IsDevelopment())
{
    app.UseHsts(); // HSTS solo en producción
}

app.UseHttpsRedirection(); // Redirigir HTTP → HTTPS

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.Run();
```

### Kong API Gateway: TLS Termination

```yaml
# kong/services/order-service.yaml
services:
  - name: order-service
    protocol: https # Upstream usa HTTPS también
    host: order-service.internal
    port: 443

    # Verificar certificado del upstream
    tls_verify: true
    ca_certificates:
      - internal-ca

routes:
  - name: order-routes
    protocols:
      - https # Solo HTTPS, no HTTP
    hosts:
      - api.talma.com
    paths:
      - /api/orders

    strip_path: false
    preserve_host: false

# Global TLS configuration
_global:
  ssl_protocols: TLSv1.3 # Solo TLS 1.3
  ssl_ciphers: TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256
  ssl_prefer_server_ciphers: on

# Plugin: Force HTTPS
plugins:
  - name: request-termination
    service: order-service
    config:
      status_code: 426 # Upgrade Required
      message: "HTTPS is required"
    protocols:
      - http # Solo aplica a HTTP, fuerza upgrade

  # HSTS Header
  - name: response-transformer
    config:
      add:
        headers:
          - "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"
```

### HttpClient: Validar Certificados

```csharp
// src/Shared/Http/SecureHttpClientFactory.cs
public class SecureHttpClientFactory
{
    public HttpClient CreateSecureClient()
    {
        var handler = new HttpClientHandler
        {
            // Validación estricta de certificados
            ServerCertificateCustomValidationCallback =
                (request, cert, chain, errors) =>
                {
                    // En producción: rechazar cualquier error
                    if (errors == SslPolicyErrors.None)
                        return true;

                    // Log errores para auditoría
                    _logger.LogError(
                        "Certificate validation failed: {Errors}, Issuer: {Issuer}, Subject: {Subject}",
                        errors,
                        cert?.Issuer,
                        cert?.Subject);

                    return false; // Rechazar
                },

            // Forzar TLS 1.3
            SslProtocols = SslProtocols.Tls13
        };

        return new HttpClient(handler);
    }
}
```

---

## Enmascaramiento de Datos

### ¿Qué es Data Masking?

Técnica de ofuscar datos sensibles reemplazándolos con valores enmascarados, manteniendo formato pero ocultando información real. Usado en logs, pantallas, reportes.

**Propósito:** Prevenir exposición de PII/datos sensibles en contextos no autorizados.

**Tipos:**

- **Static Masking**: Enmascarar en copia de base de datos (para dev/test)
- **Dynamic Masking**: Enmascarar en presentación según permisos del usuario
- **Log Masking**: Enmascarar automáticamente en logs

**Beneficios:**
✅ Compliance con GDPR, PCI-DSS
✅ Prevenir leaks en logs
✅ Datos realistas para testing sin exponer información real
✅ Protección de PII

### Implementación: Log Masking con Serilog

```csharp
// src/Shared/Logging/DataMaskingEnricher.cs
using Serilog.Core;
using Serilog.Events;
using System.Text.RegularExpressions;

public class DataMaskingEnricher : ILogEventEnricher
{
    // Patterns para detectar datos sensibles
    private static readonly Regex CreditCardPattern =
new Regex(@"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b");

    private static readonly Regex EmailPattern =
        new Regex(@"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b");

    private static readonly Regex SsnPattern =
        new Regex(@"\b\d{3}-\d{2}-\d{4}\b");

    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory propertyFactory)
    {
        if (logEvent.MessageTemplate.Text == null)
            return;

        var maskedMessage = logEvent.MessageTemplate.Text;

        // Enmascarar tarjetas de crédito: 4532-****-****-9010
        maskedMessage = CreditCardPattern.Replace(maskedMessage, match =>
        {
            var card = match.Value.Replace("-", "").Replace(" ", "");
            return $"{card.Substring(0, 4)}-****-****-{card.Substring(12)}";
        });

        // Enmascarar emails: j***@example.com
        maskedMessage = EmailPattern.Replace(maskedMessage, match =>
        {
            var parts = match.Value.Split('@');
            var username = parts[0];
            var maskedUsername = username.Length > 2
                ? $"{username[0]}***{username[^1]}"
                : "***";
            return $"{maskedUsername}@{parts[1]}";
        });

        // Enmascarar SSN: ***-**-9876
        maskedMessage = SsnPattern.Replace(maskedMessage, match =>
        {
            var ssn = match.Value.Split('-');
            return $"***-**-{ssn[2]}";
        });

        // Reemplazar mensaje con versión enmascarada
        logEvent.AddOrUpdateProperty(
            propertyFactory.CreateProperty("MaskedMessage", maskedMessage));
    }
}

// Program.cs - Configurar Serilog con masking
Log.Logger = new LoggerConfiguration()
    .Enrich.With<DataMaskingEnricher>()
    .WriteTo.Console(
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss} [{Level:u3}] {MaskedMessage}{NewLine}{Exception}")
    .WriteTo.File("logs/app.log",
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss} [{Level:u3}] {MaskedMessage}{NewLine}{Exception}")
    .CreateLogger();

// Ejemplo de uso
_logger.LogInformation(
    "Processing payment for card {CreditCard} and email {Email}",
    "4532-1234-5678-9010",
    "juan.perez@example.com");

// Output enmascarado:
// "Processing payment for card 4532-****-****-9010 and email j***@example.com"
```

### Dynamic Masking en API Response

```csharp
// src/Shared/Security/DataMaskingExtensions.cs
public static class DataMaskingExtensions
{
    public static string MaskCreditCard(this string creditCard)
    {
        if (string.IsNullOrEmpty(creditCard) || creditCard.Length < 13)
            return "****";

        var cleaned = creditCard.Replace("-", "").Replace(" ", "");
        return $"{cleaned.Substring(0, 4)}-****-****-{cleaned.Substring(cleaned.Length - 4)}";
    }

    public static string MaskEmail(this string email)
    {
        if (string.IsNullOrEmpty(email) || !email.Contains('@'))
            return "***@***.com";

        var parts = email.Split('@');
        var username = parts[0];

        if (username.Length <= 2)
            return $"***@{parts[1]}";

        return $"{username[0]}***{username[^1]}@{parts[1]}";
    }

    public static string MaskPhone(this string phone)
    {
        if (string.IsNullOrEmpty(phone))
            return "***-***-****";

        var cleaned = Regex.Replace(phone, @"\D", "");
        if (cleaned.Length < 10)
            return "***-***-****";

        return $"***-***-{cleaned.Substring(cleaned.Length - 4)}";
    }
}

// DTO con masking
public class CustomerDto
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }
    public string Phone { get; set; }
    public string CreditCard { get; set; }

    public static CustomerDto FromEntity(Customer entity, ClaimsPrincipal user)
    {
        var hasFullAccess = user.HasClaim("permission", "customer:view_sensitive");

        return new CustomerDto
        {
            Id = entity.Id,
            Name = entity.Name,

            // Enmascarar si el usuario no tiene permisos completos
            Email = hasFullAccess ? entity.Email : entity.Email.MaskEmail(),
            Phone = hasFullAccess ? entity.Phone : entity.Phone.MaskPhone(),
            CreditCard = hasFullAccess
                ? entity.CreditCardNumber
                : entity.CreditCardNumber.MaskCreditCard()
        };
    }
}
```

---

## Clasificación de Datos

### ¿Qué es Data Classification?

Esquema para etiquetar datos según su nivel de sensibilidad, determinando controles de seguridad apropiados.

**Niveles de clasificación:**

- **Public**: Puede ser público (sin impacto si se divulga)
- **Internal**: Uso interno, no público (bajo impacto)
- **Confidential**: Datos sensibles de negocio (impacto medio)
- **Secret/Restricted**: Altamente sensible (impacto alto: PII, financiero)

**Propósito:** Aplicar controles de seguridad proporcionales al riesgo.

**Beneficios:**
✅ Protección adecuada según sensibilidad
✅ Compliance con GDPR (data minimization)
✅ Priorización de esfuerzos de seguridad
✅ Claridad en manejo de datos

### Implementación: Data Classification Entity

```csharp
// src/Shared/Security/DataClassification.cs
public enum DataClassification
{
    Public = 1,        // Puede ser divulgado públicamente
    Internal = 2,      // Solo uso interno
    Confidential = 3,  // Información sensible de negocio
    Secret = 4         // Altamente sensible (PII, financiero)
}

// Attribute para marcar propiedades sensibles
[AttributeUsage(AttributeTargets.Property)]
public class DataClassificationAttribute : Attribute
{
    public DataClassification Level { get; }

    public DataClassificationAttribute(DataClassification level)
    {
        Level = level;
    }
}

// Entity con clasificación
public class Customer
{
    public int Id { get; set; }

    [DataClassification(DataClassification.Public)]
    public string Name { get; set; }

    [DataClassification(DataClassification.Internal)]
    public string Email { get; set; }

    [DataClassification(DataClassification.Confidential)]
    public string Phone { get; set; }

    [DataClassification(DataClassification.Secret)]
    public string CreditCardNumber { get; set; }

    [DataClassification(DataClassification.Secret)]
    public string Ssn { get; set; }

    [DataClassification(DataClassification.Confidential)]
    public decimal CreditLimit { get; set; }
}

// Service para aplicar controles basados en clasificación
public class DataClassificationService
{
    public bool CanUserAccessProperty(
        ClaimsPrincipal user,
        PropertyInfo property)
    {
        var classificationAttr = property.GetCustomAttribute<DataClassificationAttribute>();
        if (classificationAttr == null)
            return true; // Sin clasificación, permitir

        var userClearanceLevel = GetUserClearanceLevel(user);

        // Usuario debe tener clearance >= clasificación del dato
        return (int)userClearanceLevel >= (int)classificationAttr.Level;
    }

    private DataClassification GetUserClearanceLevel(ClaimsPrincipal user)
    {
        var clearanceClaim = user.FindFirst("clearance_level")?.Value;
        if (Enum.TryParse<DataClassification>(clearanceClaim, out var level))
            return level;

        return DataClassification.Internal; // Default
    }

    public T FilterPropertiesByClassification<T>(T entity, ClaimsPrincipal user) where T : class
    {
        var properties = typeof(T).GetProperties();

        foreach (var property in properties)
        {
            if (!CanUserAccessProperty(user, property))
            {
                // Enmascarar o establecer null
                if (property.PropertyType == typeof(string))
                {
                    property.SetValue(entity, "[REDACTED]");
                }
                else
                {
                    property.SetValue(entity, null);
                }
            }
        }

        return entity;
    }
}
```

### PostgreSQL: Row-Level Security por Clasificación

```sql
-- Tabla con clasificación de datos
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    credit_card_number VARCHAR(20),
    ssn VARCHAR(11),
    classification VARCHAR(20) DEFAULT 'confidential'  -- public, internal, confidential, secret
);

-- Habilitar Row-Level Security
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Policy: Solo usuarios con clearance adecuado pueden ver datos secret
CREATE POLICY customer_secret_policy ON customers
    FOR SELECT
    USING (
        CASE
            WHEN classification = 'secret' THEN
                current_setting('app.user_clearance', true) >= '4'
            WHEN classification = 'confidential' THEN
                current_setting('app.user_clearance', true) >= '3'
            WHEN classification = 'internal' THEN
                current_setting('app.user_clearance', true) >= '2'
            ELSE true  -- Public
        END
    );

-- .NET: Setear clearance level al conectar
using var connection = new NpgsqlConnection(connectionString);
await connection.OpenAsync();

// Setear clearance level del usuario
var clearanceLevel = User.FindFirst("clearance_level")?.Value ?? "2";
using var cmd = new NpgsqlCommand($"SET app.user_clearance = {clearanceLevel}", connection);
await cmd.ExecuteNonQueryAsync();

// Ahora las queries respetan RLS automáticamente
var customers = await connection.QueryAsync<Customer>("SELECT * FROM customers");
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

**Encryption:**

- **MUST** cifrar todos los datos at-rest (EBS, RDS, S3) con AES-256
- **MUST** usar TLS 1.3 para todas las comunicaciones
- **MUST** almacenar claves de cifrado en AWS KMS
- **MUST** rotar claves de cifrado anualmente

**Data Masking:**

- **MUST** enmascarar PII en logs automáticamente
- **MUST** enmascarar números de tarjeta en UIs (solo últimos 4 dígitos)
- **MUST** no logear credenciales, tokens, secrets

**Classification:**

- **MUST** clasificar todos los datos sensibles (Confidential/Secret)
- **MUST** aplicar controles según clasificación
- **MUST** etiquetar tablas/buckets con nivel de clasificación

**Data Minimization:**

- **MUST** recopilar solo datos estrictamente necesarios
- **MUST** eliminar datos después del retention period
- **MUST** anonimizar datos para analytics

**DLP:**

- **MUST** prevenir exfiltración de datos (bloquear uploads no autorizados)
- **MUST** monitorear transferencias de datos sensibles
- **MUST** restringir copiar/pegar de datos confidenciales en web apps

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar column-level encryption para PII
- **SHOULD** implementar certificate pinning en apps móviles
- **SHOULD** habilitar CloudTrail para auditar acceso a KMS keys
- **SHOULD** usar separate KMS keys por tipo de dato

### MUST NOT (Prohibido)

- **MUST NOT** almacenar datos sensibles sin cifrar
- **MUST NOT** usar TLS 1.2 o inferior (deprecated)
- **MUST NOT** logear PII sin enmascarar
- **MUST NOT** compartir claves de cifrado entre ambientes

---

## Referencias

- [AWS KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)
- [PostgreSQL Encryption](https://www.postgresql.org/docs/current/encryption-options.html)
- [.NET Data Protection](https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Secrets & Key Management](./secrets-key-management.md)
- [Segmentación y Controles de Red](./network-segmentation.md)
