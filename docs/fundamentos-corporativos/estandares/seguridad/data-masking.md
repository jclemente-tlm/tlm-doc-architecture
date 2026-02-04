---
id: data-masking
sidebar_position: 7
title: Data Masking
description: Estándar para enmascarar datos sensibles (PII, PCI DSS) en logs, bases de datos y APIs mediante regex, hashing y tokenización
---

# Estándar Técnico — Data Masking

---

## 1. Propósito

Enmascarar datos sensibles (PII, PCI DSS) en logs, bases de datos no-productivas y respuestas de APIs mediante técnicas de masking, hashing y tokenización, cumpliendo GDPR y PCI DSS.

---

## 2. Alcance

**Aplica a:**

- Logs de aplicación (Serilog → Grafana Loki)
- Bases de datos de desarrollo/testing
- Respuestas de APIs (parámetros sensibles)
- Reportes y exportaciones
- Stack traces en errores

**No aplica a:**

- Base de datos productiva encriptada (usar column encryption)
- Datos ya anonimizados

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología           | Versión mínima | Observaciones          |
| ----------------- | -------------------- | -------------- | ---------------------- |
| **Logging**       | Serilog              | 3.1+           | Enrichers para masking |
| **Regex Masking** | .NET Regex           | -              | Patterns para PII/PCI  |
| **Hashing**       | SHA256               | -              | One-way hashing        |
| **Tokenization**  | Custom / Stripe      | -              | PCI DSS compliant      |
| **DB Masking**    | PostgreSQL Functions | 14+            | pg_crypto              |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Datos a Enmascarar

- [ ] **PII**: Email, teléfono, dirección, nombres completos, DNI
- [ ] **PCI DSS**: Números de tarjeta, CVV, PINs
- [ ] **Credenciales**: Passwords, API keys, tokens
- [ ] **Salud**: Historiales médicos (HIPAA)
- [ ] **Financiero**: Números de cuenta, SSN

### Técnicas por Tipo

| Dato          | Técnica          | Ejemplo                     | Reversible        |
| ------------- | ---------------- | --------------------------- | ----------------- |
| **Email**     | Partial masking  | j\*\*\*@example.com         | No                |
| **Teléfono**  | Last 4 digits    | **_-_**-1234                | No                |
| **Tarjeta**   | Last 4 digits    | \***\*-\*\***-\*\*\*\*-5678 | No (PCI DSS)      |
| **DNI**       | Hashing          | SHA256(dni)                 | No                |
| **Nombre**    | Pseudonymization | Usuario_12345               | Sí (lookup table) |
| **Dirección** | Generalization   | Lima, Perú (sin calle)      | No                |

### Logging

- [ ] **Auto-masking**: Enricher de Serilog automático
- [ ] **Regex patterns**: Detectar PII/PCI en mensajes
- [ ] **Stack traces**: Remover datos sensibles de excepciones
- [ ] **Structured logging**: NO logear objetos completos sin sanitizar

---

## 5. Serilog - Auto Masking

### Enricher Personalizado

```csharp
// Logging/SensitiveDataMaskingEnricher.cs
public class SensitiveDataMaskingEnricher : ILogEventEnricher
{
    // Regex patterns
    private static readonly Regex EmailRegex = new(
        @"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        RegexOptions.Compiled);

    private static readonly Regex PhoneRegex = new(
        @"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        RegexOptions.Compiled);

    private static readonly Regex CreditCardRegex = new(
        @"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        RegexOptions.Compiled);

    private static readonly Regex SSNRegex = new(
        @"\b\d{3}-\d{2}-\d{4}\b",
        RegexOptions.Compiled);

    private static readonly Regex ApiKeyRegex = new(
        @"\b[A-Za-z0-9]{32,}\b",  // API keys suelen ser largos
        RegexOptions.Compiled);

    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory propertyFactory)
    {
        if (logEvent.MessageTemplate.Text == null)
            return;

        // Masking en message template
        var originalMessage = logEvent.RenderMessage();
        var maskedMessage = MaskSensitiveData(originalMessage);

        if (originalMessage != maskedMessage)
        {
            logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty(
                "OriginalMessageMasked",
                true));
        }

        // Masking en properties
        foreach (var property in logEvent.Properties.ToList())
        {
            if (property.Value is ScalarValue scalar && scalar.Value is string str)
            {
                var masked = MaskSensitiveData(str);
                if (masked != str)
                {
                    logEvent.RemovePropertyIfPresent(property.Key);
                    logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty(
                        property.Key,
                        masked));
                }
            }
        }
    }

    public static string MaskSensitiveData(string input)
    {
        if (string.IsNullOrEmpty(input))
            return input;

        var masked = input;

        // Mask emails: user@domain.com → u***@domain.com
        masked = EmailRegex.Replace(masked, match =>
        {
            var email = match.Value;
            var parts = email.Split('@');
            if (parts.Length == 2)
            {
                var localPart = parts[0];
                var maskedLocal = localPart.Length > 1
                    ? $"{localPart[0]}***"
                    : "***";
                return $"{maskedLocal}@{parts[1]}";
            }
            return "***@***.***";
        });

        // Mask phones: 555-123-4567 → ***-***-4567
        masked = PhoneRegex.Replace(masked, match =>
        {
            var phone = match.Value.Replace("-", "").Replace(".", "");
            return $"***-***-{phone.Substring(phone.Length - 4)}";
        });

        // Mask credit cards: 4532-1234-5678-9010 → ****-****-****-9010
        masked = CreditCardRegex.Replace(masked, match =>
        {
            var card = match.Value.Replace(" ", "").Replace("-", "");
            return $"****-****-****-{card.Substring(card.Length - 4)}";
        });

        // Mask SSN: 123-45-6789 → ***-**-6789
        masked = SSNRegex.Replace(masked, match =>
        {
            var ssn = match.Value;
            return $"***-**-{ssn.Substring(ssn.Length - 4)}";
        });

        // Mask API keys: sk_live_abc123... → sk_***
        masked = ApiKeyRegex.Replace(masked, match =>
        {
            var key = match.Value;
            if (key.StartsWith("sk_") || key.StartsWith("pk_"))
            {
                return $"{key.Substring(0, 3)}***";
            }
            return "***API_KEY***";
        });

        return masked;
    }
}
```

### Configuración Serilog

```csharp
// Program.cs
Log.Logger = new LoggerConfiguration()
    .Enrich.With<SensitiveDataMaskingEnricher>()  // ✅ Auto-masking
    .WriteTo.GrafanaLoki("http://loki:3100")
    .CreateLogger();

// Uso
Log.Information("User {Email} created payment with card {CardNumber}",
    "john.doe@example.com",  // → j***@example.com
    "4532-1234-5678-9010");  // → ****-****-****-9010
```

---

## 6. Base de Datos - Masking en Dev/Test

### PostgreSQL - pg_crypto

```sql
-- Instalar extensión
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Función para mask de emails
CREATE OR REPLACE FUNCTION mask_email(email TEXT)
RETURNS TEXT AS $$
DECLARE
    parts TEXT[];
    local_part TEXT;
    domain_part TEXT;
BEGIN
    IF email IS NULL OR email = '' THEN
        RETURN email;
    END IF;

    parts := string_to_array(email, '@');
    IF array_length(parts, 1) = 2 THEN
        local_part := parts[1];
        domain_part := parts[2];

        -- Mask: user@domain.com → u***@domain.com
        RETURN substring(local_part, 1, 1) || '***@' || domain_part;
    ELSE
        RETURN '***@***.***';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Función para mask de tarjetas
CREATE OR REPLACE FUNCTION mask_credit_card(card TEXT)
RETURNS TEXT AS $$
BEGIN
    IF card IS NULL OR length(card) < 4 THEN
        RETURN '****';
    END IF;

    -- 4532123456789010 → ************9010
    RETURN repeat('*', length(card) - 4) || substring(card, length(card) - 3, 4);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Función para hash de DNI (irreversible)
CREATE OR REPLACE FUNCTION hash_dni(dni TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(digest(dni, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

### Copiar Datos de Prod a Dev (Masked)

```sql
-- Script para clonar datos enmascarados
INSERT INTO dev.customers (
    id,
    email,
    phone,
    credit_card,
    dni_hash,
    created_at
)
SELECT
    id,
    mask_email(email),                    -- Email masked
    '***-***-' || substring(phone, length(phone) - 3, 4),  -- Phone masked
    mask_credit_card(credit_card),        -- Card masked
    hash_dni(dni),                        -- DNI hashed
    created_at
FROM prod.customers
WHERE created_at > NOW() - INTERVAL '30 days'
LIMIT 1000;  -- Solo subset para testing
```

---

## 7. API Responses - Masking

### DTOs con Masking Automático

```csharp
// Attributes/MaskAttribute.cs
[AttributeUsage(AttributeTargets.Property)]
public class MaskAttribute : Attribute
{
    public MaskType Type { get; }

    public MaskAttribute(MaskType type)
    {
        Type = type;
    }
}

public enum MaskType
{
    Email,
    Phone,
    CreditCard,
    FullMask
}

// DTOs/CustomerDto.cs
public class CustomerDto
{
    public Guid Id { get; set; }

    [Mask(MaskType.Email)]
    public string Email { get; set; } = null!;

    [Mask(MaskType.Phone)]
    public string Phone { get; set; } = null!;

    [Mask(MaskType.CreditCard)]
    public string CreditCard { get; set; } = null!;

    public DateTime CreatedAt { get; set; }
}

// Filters/MaskingResultFilter.cs
public class MaskingResultFilter : IAsyncResultFilter
{
    public async Task OnResultExecutionAsync(
        ResultExecutingContext context,
        ResultExecutionDelegate next)
    {
        if (context.Result is ObjectResult objectResult)
        {
            objectResult.Value = MaskObject(objectResult.Value);
        }

        await next();
    }

    private object? MaskObject(object? obj)
    {
        if (obj == null) return null;

        var type = obj.GetType();

        // Si es colección
        if (obj is IEnumerable enumerable and not string)
        {
            return enumerable.Cast<object>().Select(MaskObject).ToList();
        }

        // Si es objeto simple
        foreach (var property in type.GetProperties())
        {
            var maskAttribute = property.GetCustomAttribute<MaskAttribute>();
            if (maskAttribute != null)
            {
                var value = property.GetValue(obj) as string;
                if (!string.IsNullOrEmpty(value))
                {
                    var masked = maskAttribute.Type switch
                    {
                        MaskType.Email => MaskEmail(value),
                        MaskType.Phone => MaskPhone(value),
                        MaskType.CreditCard => MaskCreditCard(value),
                        MaskType.FullMask => "***",
                        _ => value
                    };

                    property.SetValue(obj, masked);
                }
            }
        }

        return obj;
    }

    private static string MaskEmail(string email)
    {
        var parts = email.Split('@');
        return parts.Length == 2
            ? $"{parts[0][0]}***@{parts[1]}"
            : "***@***.***";
    }

    private static string MaskPhone(string phone)
    {
        return phone.Length >= 4
            ? $"***-***-{phone.Substring(phone.Length - 4)}"
            : "***";
    }

    private static string MaskCreditCard(string card)
    {
        return card.Length >= 4
            ? $"****-****-****-{card.Substring(card.Length - 4)}"
            : "****";
    }
}

// Registrar en Program.cs
builder.Services.AddControllers(options =>
{
    options.Filters.Add<MaskingResultFilter>();
});
```

---

## 8. Validación de Cumplimiento

```bash
# Verificar logs NO contienen datos sensibles
grep -r "@" logs/*.log | grep -v "@domain.com" && echo "WARN: Unmasked emails in logs"

# Verificar Serilog enricher configurado
grep -r "SensitiveDataMaskingEnricher" src/ || echo "MISSING: Masking enricher"

# Test masking functions en PostgreSQL
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  mask_email('john.doe@example.com'),       -- Expect: j***@example.com
  mask_credit_card('4532123456789010'),     -- Expect: ************9010
  hash_dni('12345678')                       -- Expect: SHA256 hash
;
EOF
```

---

## 9. Referencias

**GDPR:**

- [GDPR Data Protection](https://gdpr.eu/data-protection/)
- [Pseudonymization (Article 4)](https://gdpr.eu/article-4-definitions/)

**PCI DSS:**

- [PCI DSS Requirement 3.4 - Masking](https://www.pcisecuritystandards.org/)

**OWASP:**

- [OWASP Data Protection](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
