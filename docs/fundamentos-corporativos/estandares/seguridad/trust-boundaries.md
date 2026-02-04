---
id: trust-boundaries
sidebar_position: 24
title: Límites de Confianza (Trust Boundaries)
description: Estándar para identificar y proteger trust boundaries con validación de entrada, sanitización, autenticación en boundaries y threat modeling
---

# Estándar Técnico — Límites de Confianza

---

## 1. Propósito

Definir límites de confianza (trust boundaries) donde cambia el nivel de trust entre componentes, implementando validación estricta en boundaries, sanitización de datos, autenticación/autorización y defense in depth.

---

## 2. Alcance

**Aplica a:**


- Internet → API Gateway (boundary principal)
- API Gateway → Backend services
- Backend → Base de datos
- Aplicación → Servicios externos
- Usuario → Sistema


**No aplica a:**

- Comunicación dentro del mismo proceso (localhost)

---

## 3. Tecnologías Aprobadas

| Componente           | Tecnología       | Versión mínima | Observaciones            |
| -------------------- | ---------------- | -------------- | ------------------------ |
| **Input Validation** | FluentValidation | 11.0+          | .NET validators          |
| **Sanitization**     | HtmlSanitizer    | 8.0+           | XSS protection           |
| **API Gateway**      | Kong             | 3.5+           | First boundary           |
| **Authentication**   | Keycloak JWT     | 23.0+          | Token validation         |
| **WAF**              | AWS WAF          | -              | Web Application Firewall |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Identificación de Boundaries

- [ ] **Documentar boundaries**: En threat model diagrams
- [ ] **Principal boundary**: Internet → Kong API Gateway
- [ ] **Secondary boundaries**: Kong → Backend, Backend → DB
- [ ] **External boundaries**: App → Third-party APIs

### Validación en Boundaries

- [ ] **Validate ALL inputs**: En cada boundary
- [ ] **Never trust client**: Validar servidor-side siempre
- [ ] **Whitelist approach**: Permitir solo lo esperado
- [ ] **Sanitize outputs**: Escapar HTML/SQL/JSON

### Autenticación/Autorización

- [ ] **Authenticate at boundary**: Kong valida JWT
- [ ] **Authorize at service**: Backend valida permisos
- [ ] **NO bypass**: No asumir request es válido

### Defense in Depth

- [ ] **Multiple layers**: WAF + Kong + App validation
- [ ] **Fail securely**: Denegar por defecto

---

## 5. Trust Boundaries Diagram

### Arquitectura Multi-Layer

```text
┌─────────────────────────────────────────────────────────────┐
│  UNTRUSTED ZONE (Internet)                                  │
│  • Usuarios externos                                         │
│  • Bots, atacantes potenciales                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
        ╔══════════════════════════════════╗
        ║   TRUST BOUNDARY #1              ║
        ║   AWS WAF + ALB                  ║
        ║   • Rate limiting                ║
        ║   • IP filtering                 ║
        ║   • OWASP Top 10 rules          ║
        ╚══════════════════════════════════╝
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  DMZ ZONE (Public Subnet)                                   │
│  • Kong API Gateway (HTTPS only)                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
        ╔══════════════════════════════════╗
        ║   TRUST BOUNDARY #2              ║
        ║   Kong (API Gateway)             ║
        ║   • JWT validation               ║
        ║   • Rate limiting                ║
        ║   • Request validation           ║
        ╚══════════════════════════════════╝
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  APPLICATION ZONE (Private Subnet)                          │
│  • Backend Services (.NET APIs)                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
        ╔══════════════════════════════════╗
        ║   TRUST BOUNDARY #3              ║
        ║   Backend → Database             ║
        ║   • Parameterized queries        ║
        ║   • Least privilege DB user      ║
        ║   • Encrypted connection         ║
        ╚══════════════════════════════════╝
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  DATA ZONE (Private DB Subnet)                              │
│  • PostgreSQL RDS (no public access)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Validación en Boundary #1 (WAF)

### AWS WAF Rules

```hcl
# terraform/waf.tf
resource "aws_wafv2_web_acl" "main" {
  name  = "${var.environment}-api-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  # OWASP Top 10 protection
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  # SQL Injection protection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesSQLiRuleSet"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "SQLInjectionMetric"
      sampled_requests_enabled   = true
    }
  }

  # Rate limiting (1000 req/5min per IP)
  rule {
    name     = "RateLimitRule"
    priority = 3

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitMetric"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "WAFMetric"
    sampled_requests_enabled   = true
  }
}
```

---

## 7. Validación en Boundary #2 (Kong)

### Kong Plugins

```bash
# JWT Validation
curl -X POST http://kong:8001/plugins \
  --data "name=jwt" \
  --data "config.claims_to_verify=exp,nbf"

# Request Validation
curl -X POST http://kong:8001/plugins \
  --data "name=request-validator" \
  --data "config.body_schema={\"type\":\"object\",\"required\":[\"amount\"]}"

# Rate Limiting
curl -X POST http://kong:8001/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=100" \
  --data "config.policy=local"
```

---

## 8. Validación en Boundary #3 (Backend)

### FluentValidation

```csharp
// Validators/CreatePaymentValidator.cs
public class CreatePaymentValidator : AbstractValidator<CreatePaymentRequest>
{
    public CreatePaymentValidator()
    {
        // Validar TODOS los inputs
        RuleFor(x => x.Amount)
            .GreaterThan(0).WithMessage("Amount must be positive")
            .LessThanOrEqualTo(1000000).WithMessage("Amount exceeds maximum");

        RuleFor(x => x.Currency)
            .NotEmpty()
            .Must(BeValidCurrency).WithMessage("Invalid currency code");

        RuleFor(x => x.CustomerId)
            .NotEmpty()
            .Must(BeValidGuid).WithMessage("Invalid customer ID format");

        // Sanitizar strings
        RuleFor(x => x.Description)
            .MaximumLength(500)
            .Must(NotContainScriptTags).WithMessage("Invalid characters in description");
    }

    private bool BeValidCurrency(string currency)
    {
        // Whitelist approach
        var validCurrencies = new[] { "PEN", "USD", "COP", "MXN", "CLP" };
        return validCurrencies.Contains(currency);
    }

    private bool NotContainScriptTags(string input)
    {
        return !input.Contains("<script", StringComparison.OrdinalIgnoreCase);
    }
}
```

### Input Sanitization

```csharp
// Services/InputSanitizer.cs
using Ganss.Xss;

public class InputSanitizer
{
    private readonly HtmlSanitizer _sanitizer;

    public InputSanitizer()
    {
        _sanitizer = new HtmlSanitizer();

        // Whitelist de tags permitidos (muy restrictivo)
        _sanitizer.AllowedTags.Clear();
        _sanitizer.AllowedTags.Add("p");
        _sanitizer.AllowedTags.Add("br");
        _sanitizer.AllowedTags.Add("strong");
        _sanitizer.AllowedTags.Add("em");
    }

    public string SanitizeHtml(string input)
    {
        if (string.IsNullOrEmpty(input))
            return input;

        return _sanitizer.Sanitize(input);
    }

    public string SanitizeSql(string input)
    {
        // NO usar para queries (usar parameterized queries)
        // Solo para logging/display
        return input.Replace("'", "''").Replace("\\", "\\\\");
    }
}
```

---

## 9. Boundary #4 (Database)

### Parameterized Queries (EF Core)

```csharp
// ✅ CORRECTO: Parameterized query
public async Task<List<Customer>> GetCustomersByEmailAsync(string email)
{
    return await _dbContext.Customers
        .Where(c => c.Email == email)  // Parametrizado automáticamente
        .ToListAsync();
}

// ❌ INCORRECTO: String concatenation (SQL Injection vulnerability)
public async Task<List<Customer>> GetCustomersByEmailUnsafeAsync(string email)
{
    var sql = $"SELECT * FROM customers WHERE email = '{email}'";
    return await _dbContext.Customers.FromSqlRaw(sql).ToListAsync();
}

// ✅ CORRECTO: FromSqlRaw con parámetros
public async Task<List<Customer>> GetCustomersByEmailSafeAsync(string email)
{
    return await _dbContext.Customers
        .FromSqlRaw("SELECT * FROM customers WHERE email = {0}", email)
        .ToListAsync();
}
```

### Database User - Least Privilege

```sql
-- Usuario de aplicación con permisos mínimos
CREATE USER app_user WITH PASSWORD 'SecurePassword123!';

-- Solo SELECT, INSERT, UPDATE, DELETE en tablas necesarias
GRANT SELECT, INSERT, UPDATE, DELETE ON customers TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON payments TO app_user;

-- NO dar permisos de:
-- DROP, CREATE, ALTER (DDL operations)
-- GRANT (permission management)
-- SUPER USER

-- Conexión cifrada obligatoria
ALTER USER app_user WITH REQUIRE SSL;
```

---

## 10. Threat Modeling - Trust Boundaries

### Template de Análisis

```markdown
## Trust Boundary: Internet → Kong API Gateway

**Threat**: Inyección SQL en parámetros de query
**STRIDE**: Tampering
**Mitigación**:

1. WAF con SQL injection rules
2. Kong request validation
3. Backend parameterized queries
   **Residual Risk**: Low

---

## Trust Boundary: Kong → Backend Services

**Threat**: Request forgery con JWT inválido
**STRIDE**: Spoofing
**Mitigación**:

1. Kong valida firma JWT con public key
2. Backend verifica claims (tenant_id, roles)
3. No confiar en headers no autenticados
   **Residual Risk**: Low

---

## Trust Boundary: Backend → PostgreSQL

**Threat**: SQL injection via ORM
**STRIDE**: Tampering
**Mitigación**:

1. EF Core parameterized queries
2. Input validation con FluentValidation
3. DB user con least privilege
   **Residual Risk**: Very Low
```

---

## 11. Validación de Cumplimiento

```bash
# Verificar WAF habilitado en ALB
aws wafv2 list-web-acls --scope REGIONAL --region us-east-1

# Test: Intentar SQL injection (debe bloquearse)
curl -i "https://api.talma.com/customers?email=test' OR '1'='1"
# Esperado: HTTP/1.1 403 Forbidden (bloqueado por WAF)

# Test: Request sin JWT (debe fallar)
curl -i https://api.talma.com/payments
# Esperado: HTTP/1.1 401 Unauthorized

# Verificar conexión DB es cifrada
psql -h rds-endpoint.us-east-1.rds.amazonaws.com -U app_user -d app_db -c "SHOW ssl"
# Esperado: ssl | on

# Verificar usuario DB tiene least privilege
psql -h localhost -U app_user -d app_db -c "DROP TABLE customers;"
# Esperado: ERROR: permission denied
```


---

## 12. Referencias


**OWASP:**

- [OWASP Threat M<https://owasp.org/www-community/Threat_Modeling>_Modeling)

- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

**NIST:**
Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

**NIST:**

- [NIST 800-207 Zero Trust](https://csrc.nist.gov/publications/detail/sp/800-207/final)
