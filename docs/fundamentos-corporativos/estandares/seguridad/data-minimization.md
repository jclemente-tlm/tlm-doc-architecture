---
id: data-minimization
sidebar_position: 7
title: Minimización de Datos
description: Estándar para minimizar recolección de datos según GDPR Article 5, selective logging, data anonymization y purpose limitation
---

# Estándar Técnico — Minimización de Datos

---

## 1. Propósito

Implementar principio de minimización de datos (GDPR Article 5.1.c) recolectando únicamente datos necesarios para propósito específico, evitando PII innecesarios en logs, anonimizando datos analíticos y estableciendo TTL para datos temporales.

---

## 2. Alcance

**Aplica a:**

- Diseño de APIs (request/response)
- Formularios de captura
- Logs de aplicación
- Bases de datos
- Reportes y analytics
- Backups

**No aplica a:**

- Datos requeridos por regulación (retención legal)

---

## 3. Tecnologías Aprobadas

| Componente     | Tecnología            | Versión mínima | Observaciones          |
| -------------- | --------------------- | -------------- | ---------------------- |
| **Logging**    | Serilog               | 3.0+           | Enrichers para masking |
| **Database**   | PostgreSQL            | 14+            | Views anonimizadas     |
| **Analytics**  | Agregaciones anónimas | -              | Sin PII                |
| **Validation** | FluentValidation      | 11.0+          | Reglas de negocio      |
| **Encryption** | AWS KMS               | -              | Encrypt-at-rest        |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Principio de Minimización (GDPR)

- [ ] **Solo lo necesario**: Recolectar mínimo dato requerido
- [ ] **Purpose limitation**: Usar dato solo para propósito declarado
- [ ] **NO "por si acaso"**: NO guardar "podría ser útil después"
- [ ] **Justificar cada campo**: Documentar por qué se recolecta

### Logging Selectivo

- [ ] **NO PII en logs**: No loggear email, nombres, DNI completo
- [ ] **Masked data**: Si es necesario, enmascarar (j\*\*\*@example.com)
- [ ] **Structured logging**: JSON con campos controlados
- [ ] **TTL en logs**: 90 días máximo

### Anonimización

- [ ] **Analytics sin PII**: Usar IDs agregados, no datos personales
- [ ] **Aggregated reports**: Reportes con datos agregados (conteos, promedios)
- [ ] **Pseudonymization**: Hash de IDs cuando sea necesario

### APIs

- [ ] **Optional fields**: Campos opcionales cuando sea posible
- [ ] **NO requerir más de lo necesario**: Evitar "required: true" innecesario
- [ ] **Partial responses**: Permitir especificar campos deseados

---

## 5. API Design - Minimización

### Request: Solo Campos Necesarios

```csharp
// ❌ MAL: Pedir más datos de los necesarios
public record CreatePaymentRequest(
    string Email,           // ¿Realmente necesario?
    string FullName,        // ¿Para qué?
    string Phone,           // ¿Se usa?
    string Address,         // ¿Obligatorio?
    string DNI,             // ¿Requerido por regulación?
    decimal Amount,
    string Currency
);

// ✅ BIEN: Solo lo estrictamente necesario
public record CreatePaymentRequest(
    Guid CustomerId,        // Referencia a customer existente (no duplicar datos)
    decimal Amount,
    string Currency
);

// Si necesitas customer data, hacer lookup en BD
public async Task<PaymentResult> CreatePaymentAsync(CreatePaymentRequest request)
{
    var customer = await _dbContext.Customers.FindAsync(request.CustomerId);
    // Usar customer.Email solo si es necesario para transacción
}
```

### Response: Partial Responses

```csharp
// Controllers/CustomersController.cs
[HttpGet("{id}")]
public async Task<IActionResult> GetCustomer(Guid id, [FromQuery] string fields = null)
{
    var customer = await _dbContext.Customers.FindAsync(id);

    if (customer == null)
        return NotFound();

    // Si no se especifican fields, retornar subset seguro
    if (string.IsNullOrEmpty(fields))
    {
        return Ok(new
        {
            customer.Id,
            customer.Email,
            customer.CreatedAt
            // NO retornar: FullName, Phone, Address por defecto
        });
    }

    // Permitir especificar campos deseados
    // GET /customers/123?fields=id,email,fullName
    var requestedFields = fields.Split(',').Select(f => f.Trim().ToLower());
    var response = new Dictionary<string, object>();

    if (requestedFields.Contains("id")) response["id"] = customer.Id;
    if (requestedFields.Contains("email")) response["email"] = customer.Email;
    if (requestedFields.Contains("fullname")) response["fullName"] = customer.FullName;
    // ...

    return Ok(response);
}
```

---

## 6. Serilog - Logging Sin PII

### Configuración con Enricher

```csharp
// Program.cs
Log.Logger = new LoggerConfiguration()
    .Enrich.With<SensitiveDataMaskingEnricher>()
    .WriteTo.Loki(_configuration["Loki:Url"])
    .CreateLogger();

// Logging/SensitiveDataMaskingEnricher.cs
public class SensitiveDataMaskingEnricher : ILogEventEnricher
{
    private static readonly Regex EmailRegex = new(@"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b");
    private static readonly Regex PhoneRegex = new(@"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b");
    private static readonly Regex DniRegex = new(@"\b\d{8}\b");

    public void Enrich(LogEvent logEvent, ILogEventPropertyFactory propertyFactory)
    {
        foreach (var property in logEvent.Properties.ToList())
        {
            if (property.Value is ScalarValue scalarValue && scalarValue.Value is string stringValue)
            {
                var masked = stringValue;

                // Mask emails: j***@example.com
                masked = EmailRegex.Replace(masked, m =>
                {
                    var parts = m.Value.Split('@');
                    return $"{parts[0][0]}***@{parts[1]}";
                });

                // Mask phones: ***-***-9999
                masked = PhoneRegex.Replace(masked, "***-***-****");

                // Mask DNI: ****5678
                masked = DniRegex.Replace(masked, m => $"****{m.Value.Substring(4)}");

                if (masked != stringValue)
                {
                    logEvent.RemovePropertyIfPresent(property.Key);
                    logEvent.AddPropertyIfAbsent(propertyFactory.CreateProperty(
                        property.Key,
                        masked));
                }
            }
        }
    }
}
```

### Logging Seguro

```csharp
// ❌ MAL: Loggear PII
_logger.LogInformation("Payment created for user {Email} with amount {Amount}",
    customer.Email, payment.Amount);

// ✅ BIEN: Usar IDs, no PII
_logger.LogInformation("Payment {PaymentId} created for customer {CustomerId} with amount {Amount}",
    payment.Id, customer.Id, payment.Amount);

// ✅ BIEN: Si es necesario loggear email, será enmascarado automáticamente
_logger.LogDebug("Sending notification to {Email}", customer.Email);
// Log result: "Sending notification to j***@example.com"
```

---

## 7. PostgreSQL - Vistas Anonimizadas

### Vista para Analytics (Sin PII)

```sql
-- Vista con datos agregados (NO PII)
CREATE VIEW payments_analytics AS
SELECT
  DATE_TRUNC('day', created_at) as payment_date,
  tenant_id,
  currency,
  COUNT(*) as transaction_count,
  SUM(amount) as total_amount,
  AVG(amount) as average_amount,
  -- NO incluir: email, full_name, DNI
  NULL as customer_id  -- Anonymized
FROM payments
GROUP BY DATE_TRUNC('day', created_at), tenant_id, currency;

-- Usar en reportes
SELECT * FROM payments_analytics
WHERE payment_date >= '2024-01-01'
  AND tenant_id = 'PE';
```

### Función para Pseudonymization

```sql
-- Hash de customer_id para analytics cross-tenant
CREATE OR REPLACE FUNCTION pseudonymize_customer_id(customer_id UUID)
RETURNS TEXT AS $$
BEGIN
  RETURN encode(digest(customer_id::text, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Vista con pseudonymized IDs
CREATE VIEW customer_behavior_analytics AS
SELECT
  pseudonymize_customer_id(customer_id) as pseudonymized_id,
  COUNT(*) as payment_count,
  AVG(amount) as average_payment,
  MAX(created_at) as last_payment_date
FROM payments
GROUP BY customer_id;
```

---

## 8. .NET - Validación de Necesidad

### FluentValidation con Purpose

```csharp
// Validators/CreateCustomerValidator.cs
public class CreateCustomerValidator : AbstractValidator<CreateCustomerRequest>
{
    public CreateCustomerValidator()
    {
        // Email: REQUERIDO (para notificaciones transaccionales)
        RuleFor(x => x.Email)
            .NotEmpty().WithMessage("Email is required for transaction notifications")
            .EmailAddress();

        // Phone: OPCIONAL (no es necesario para flujo principal)
        RuleFor(x => x.Phone)
            .Must(BeValidPhoneOrEmpty)
            .WithMessage("Phone must be valid if provided");

        // Address: OPCIONAL (solo si se requiere envío físico)
        When(x => x.RequiresPhysicalDelivery, () =>
        {
            RuleFor(x => x.Address)
                .NotEmpty()
                .WithMessage("Address is required for physical delivery");
        });

        // DNI: Validar solo si regulación lo requiere
        When(x => x.TenantId == "PE", () =>  // SUNAT requiere DNI en Perú
        {
            RuleFor(x => x.DNI)
                .NotEmpty()
                .Length(8)
                .WithMessage("DNI is required by SUNAT regulation in Peru");
        });
    }
}
```

### Data Retention Policies

```csharp
// Entities/TemporaryData.cs
public class PasswordResetToken
{
    public Guid Id { get; set; }
    public Guid UserId { get; set; }
    public string Token { get; set; } = null!;
    public DateTime CreatedAt { get; set; }
    public DateTime ExpiresAt { get; set; }  // TTL: 1 hora
}

// Background job para cleanup
public async Task CleanupExpiredTokensAsync()
{
    var expired = await _dbContext.PasswordResetTokens
        .Where(t => t.ExpiresAt < DateTime.UtcNow)
        .ToListAsync();

    _dbContext.PasswordResetTokens.RemoveRange(expired);
    await _dbContext.SaveChangesAsync();

    _logger.LogInformation("Cleaned up {Count} expired tokens", expired.Count);
}
```

---

## 9. Documentación - Purpose Declaration

### Privacy Policy Template

```markdown
## Datos Recolectados y Propósito

| Campo            | Propósito                      | Base Legal       | Retención        |
| ---------------- | ------------------------------ | ---------------- | ---------------- |
| **Email**        | Notificaciones transaccionales | Contractual      | 7 años           |
| **Full Name**    | Identificación de cliente      | Contractual      | 7 años           |
| **Phone**        | Contacto urgente (opcional)    | Consentimiento   | Hasta revocación |
| **Address**      | Envío de documentos físicos    | Contractual      | 7 años           |
| **DNI**          | Cumplimiento regulatorio SUNAT | Legal obligation | 7 años           |
| **Payment data** | Procesamiento de pagos         | Contractual      | 7 años           |

### Datos NO Recolectados

- Geolocalización precisa (solo país)
- Navegación web (sin tracking)
- Datos biométricos
- Orientación política/religiosa
```

---

## 10. Validación de Cumplimiento

```bash
# Verificar logs NO contienen emails sin enmascarar
grep -r "@" /var/log/app/ | grep -v "\*\*\*@"
# Esperado: Sin resultados (todos los emails están enmascarados)

# Contar campos en tablas vs campos realmente usados
psql -h localhost -U app_user -d app_db <<EOF
SELECT
  table_name,
  COUNT(*) as total_columns
FROM information_schema.columns
WHERE table_schema = 'public'
GROUP BY table_name
ORDER BY total_columns DESC;
EOF

# Verificar analytics sin PII
psql -h localhost -U app_user -d app_db <<EOF
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'payments_analytics'
  AND column_name IN ('email', 'full_name', 'dni', 'phone');
-- Esperado: 0 rows (sin PII)
EOF
```

---

## 11. Referencias

**GDPR:**

- [GDPR Article 5 - Data Minimization](https://gdpr.eu/article-5-how-to-process-personal-data/)
- [Privacy by Design](https://gdpr.eu/privacy-by-design/)

**OWASP:**

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
