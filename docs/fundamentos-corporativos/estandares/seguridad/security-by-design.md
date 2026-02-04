---
id: security-by-design
sidebar_position: 11
title: Security by Design
description: Estándar para integrar seguridad desde diseño con threat modeling, OWASP Top 10, security reviews obligatorios y SAST/DAST
---

# Estándar Técnico — Security by Design

---

## 1. Propósito

Garantizar que la seguridad se incorpore desde las fases iniciales de diseño mediante threat modeling, revisión de OWASP Top 10, security reviews obligatorios en ADRs, y validación con SAST/DAST antes de producción.

---

## 2. Alcance

**Aplica a:**

- Nuevas aplicaciones y microservicios
- Cambios arquitectónicos significativos (ADRs)
- Integraciones con sistemas externos
- Cambios en modelos de datos o autenticación
- APIs públicas o privadas

**No aplica a:**

- Refactors internos sin cambio de superficie de ataque
- Cambios de configuración menores
- Prototipos sin datos reales

---

## 3. Tecnologías Aprobadas

| Componente           | Tecnología             | Versión mínima | Observaciones               |
| -------------------- | ---------------------- | -------------- | --------------------------- |
| **Threat Modeling**  | OWASP Threat Dragon    | 2.0+           | Modelado visual de amenazas |
| **SAST**             | SonarQube Community    | 10.0+          | Análisis estático           |
| **DAST**             | OWASP ZAP              | 2.14+          | Pruebas dinámicas           |
| **Dependency Scan**  | OWASP Dependency-Check | 9.0+           | CVE en librerías            |
| **Container Scan**   | Trivy                  | 0.50+          | Scan de imágenes Docker     |
| **IaC Security**     | Checkov                | 3.0+           | Terraform/CloudFormation    |
| **Security Testing** | xUnit + IdentityModel  | .NET 8+        | Tests de autorización       |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### 4.1 Fase de Diseño

- [ ] **Threat Modeling** obligatorio para nuevas aplicaciones o cambios arquitectónicos
- [ ] **Security review** en ADRs (sección dedicada)
- [ ] **OWASP Top 10** considerado explícitamente
- [ ] **Trust boundaries** identificados en diagramas
- [ ] **Superficie de ataque** documentada
- [ ] **Principio least privilege** aplicado desde diseño

### 4.2 Fase de Desarrollo

- [ ] **SAST** en cada pull request (SonarQube)
- [ ] **Dependency scanning** automático (OWASP Dependency-Check)
- [ ] **Secrets scanning** pre-commit (TruffleHog)
- [ ] **Unit tests de seguridad** (autorización, input validation)
- [ ] **Secure coding guidelines** seguidas (.NET Secure Coding)

### 4.3 Fase de Pre-Producción

- [ ] **DAST** en staging (OWASP ZAP)
- [ ] **Container scanning** de imágenes Docker (Trivy)
- [ ] **IaC security scanning** (Checkov)
- [ ] **Penetration testing** para cambios críticos
- [ ] **Security sign-off** antes de go-live

---

## 5. Threat Modeling - STRIDE

### Template Threat Model Document

```markdown
# Threat Model - Payment API

## System Overview

**Descripción:** API REST para procesamiento de pagos con Stripe
**Trust Boundaries:** Kong Gateway → Payment API → PostgreSQL
**Assets:** Datos de tarjetas (PCI DSS), transacciones financieras

## Threats (STRIDE)

| ID    | Threat              | STRIDE Category | Risk   | Mitigation                             |
| ----- | ------------------- | --------------- | ------ | -------------------------------------- |
| T-001 | SQL Injection       | Tampering       | HIGH   | Usar EF Core parametrizado, NO raw SQL |
| T-002 | JWT token theft     | Spoofing        | MEDIUM | HTTPS + short TTL (15min) + rotation   |
| T-003 | Unauthorized access | Elevation       | HIGH   | RBAC con Keycloak, claims-based auth   |
| T-004 | Log injection       | Tampering       | LOW    | Sanitizar inputs antes de logging      |
| T-005 | DDoS                | Denial          | MEDIUM | Rate limiting en Kong (100 req/min)    |

## Security Controls

- ✅ HTTPS/TLS 1.3 obligatorio
- ✅ JWT RS256 con Keycloak
- ✅ Input validation con FluentValidation
- ✅ Output encoding (evitar XSS)
- ✅ CORS restrictivo (whitelist)
- ✅ Secrets en AWS Secrets Manager
```

### OWASP Threat Dragon (UI)

```bash
# Instalar Threat Dragon local
npx @owasp/threat-dragon-desktop

# Crear modelo visual:
# 1. Definir procesos, data stores, external entities
# 2. Marcar trust boundaries
# 3. Generar amenazas STRIDE automáticamente
# 4. Exportar como JSON en repo
```

---

## 6. OWASP Top 10 Checklist

### Para CADA nueva aplicación

| #       | Vulnerabilidad            | Control Implementado         | Verificación          |
| ------- | ------------------------- | ---------------------------- | --------------------- |
| **A01** | Broken Access Control     | RBAC con Keycloak + claims   | Tests unitarios authz |
| **A02** | Cryptographic Failures    | TLS 1.3 + AWS KMS encryption | Checkov scan          |
| **A03** | Injection                 | EF Core parametrizado        | SonarQube SAST        |
| **A04** | Insecure Design           | Threat modeling obligatorio  | ADR security section  |
| **A05** | Security Misconfiguration | Checkov + Trivy scans        | CI/CD gates           |
| **A06** | Vulnerable Components     | OWASP Dep-Check              | GitHub Dependabot     |
| **A07** | Auth/Authz Failures       | JWT RS256 + MFA Keycloak     | Penetration testing   |
| **A08** | Data Integrity Failures   | Firma digital + checksums    | Tests integridad      |
| **A09** | Logging Failures          | Serilog + Grafana Loki       | Correlación trace_id  |
| **A10** | SSRF                      | Whitelist URLs externas      | Code review           |

---

## 7. Security Review en ADRs

### Template ADR con Security Section

```markdown
# ADR-XXX: Implementar Payment Gateway

## Contexto

[...]

## Decisión

[...]

## Security Considerations 🔒

### Threats Identificados

1. **Credential theft**: Integración con Stripe requiere API key
   - Mitigation: AWS Secrets Manager con rotación automática
2. **PCI DSS compliance**: Datos de tarjetas
   - Mitigation: Usar Stripe Elements (no almacenar CVV)

### Controls Implementados

- [ ] API keys en Secrets Manager
- [ ] HTTPS obligatorio (TLS 1.3)
- [ ] Rate limiting: 100 req/min
- [ ] Webhook signature validation (HMAC SHA256)
- [ ] Audit logging de transacciones

### Residual Risks

- **MEDIUM**: DDoS en webhook endpoint
  - Acceptance: Rate limiting + CloudFlare protección

### Security Sign-off

- [ ] Security Architect: @juan.perez
- [ ] Date: 2024-12-15
```

---

## 8. CI/CD Security Pipeline

### GitHub Actions - Security Gates

```yaml
# .github/workflows/security-scan.yml
name: Security Scanning

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: SonarQube SAST
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.projectKey=payment-api
            -Dsonar.qualitygate.wait=true

      - name: Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: "payment-api"
          path: "."
          format: "HTML"
          args: >
            --failOnCVSS 7
            --enableRetired

      - name: Secrets Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker Image
        run: docker build -t payment-api:${{ github.sha }} .

      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: payment-api:${{ github.sha }}
          format: "sarif"
          exit-code: "1" # Fail on CRITICAL
          severity: "CRITICAL,HIGH"

  iac-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Checkov Scan
        uses: bridgecrewio/checkov-action@master
        with:
          directory: infrastructure/
          framework: terraform
          soft_fail: false
```

---

## 9. Security Testing

### Unit Tests - Autorización

```csharp
// Tests/AuthorizationTests.cs
using Xunit;
using Microsoft.AspNetCore.Mvc.Testing;

public class AuthorizationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public AuthorizationTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetPayments_WithoutToken_Returns401()
    {
        // Act
        var response = await _client.GetAsync("/api/payments");

        // Assert
        Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
    }

    [Fact]
    public async Task GetPayments_WithInvalidRole_Returns403()
    {
        // Arrange
        var token = GenerateJwtToken(role: "ReadOnly");
        _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await _client.GetAsync("/api/payments");

        // Assert
        Assert.Equal(HttpStatusCode.Forbidden, response.StatusCode);
    }

    [Fact]
    public async Task CreatePayment_WithSqlInjectionAttempt_ReturnsValidationError()
    {
        // Arrange
        var payload = new { amount = "100'; DROP TABLE Payments; --" };

        // Act
        var response = await _client.PostAsJsonAsync("/api/payments", payload);

        // Assert
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }
}
```

---

## 10. Validación de Cumplimiento

```bash
# Verificar threat model existe
ls -la docs/threat-models/

# Ejecutar SAST local
dotnet tool install --global dotnet-sonarscanner
sonarscanner begin /k:"payment-api"
dotnet build --no-incremental
sonarscanner end

# DAST con OWASP ZAP
docker run -t zaproxy/zap-baseline -t https://staging.payment-api.com

# Dependency scan
dotnet list package --vulnerable --include-transitive

# Container scan
trivy image ghcr.io/tlm-svc-payment:latest --severity HIGH,CRITICAL
```

---

## 11. Referencias

**OWASP:**

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

**Microsoft:**

- [Microsoft Security Development Lifecycle](https://www.microsoft.com/en-us/securityengineering/sdl/)
- [.NET Secure Coding Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/security/)

**NIST:**

- [NIST SP 800-53 - Security Controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
