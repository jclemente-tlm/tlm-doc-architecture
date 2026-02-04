---
id: security-architecture
sidebar_position: 11
title: Arquitectura de Seguridad
description: Estándares consolidados de Security by Design, Defensa en Profundidad y Reducción de Superficie de Ataque
---

# Estándar Técnico — Arquitectura de Seguridad

## 1. Propósito

Garantizar seguridad integral desde diseño mediante tres pilares complementarios: Security by Design (threat modeling, OWASP Top 10, security reviews), Defensa en Profundidad (múltiples capas de protección), y Reducción de Superficie de Ataque (minimal containers, hardening, least privilege).

## 2. Alcance

**Aplica a:**

- Nuevas aplicaciones y microservicios
- Cambios arquitectónicos significativos (ADRs)
- Toda la infraestructura AWS
- Aplicaciones en ECS Fargate
- Bases de datos (PostgreSQL, Oracle, SQL Server)
- APIs REST públicas y privadas
- Container images y configuraciones

**No aplica a:**

- Ambientes dev/sandbox (puede relajarse algunos controles)
- Prototipos temporales sin datos reales
- Refactors internos sin cambio de superficie de ataque

## 3. Tecnologías Aprobadas

| Componente          | Tecnología                | Versión mínima | Observaciones                    |
| ------------------- | ------------------------- | -------------- | -------------------------------- |
| **Cloud**           | AWS                       | -              | ECS Fargate, S3, Secrets Manager |
| **Threat Modeling** | OWASP Threat Dragon       | 2.0+           | Modelado visual de amenazas      |
| **SAST**            | SonarQube Community       | 10.0+          | Análisis estático                |
| **Dependency Scan** | OWASP Dependency-Check    | 9.0+           | CVE en librerías                 |
| **Container Scan**  | Trivy                     | 0.48+          | Scan de imágenes Docker          |
| **IaC Security**    | Checkov                   | 3.0+           | Terraform scanning               |
| **WAF**             | AWS WAF                   | -              | Managed rules + custom           |
| **Network**         | AWS VPC, Security Groups  | -              | Segmentación                     |
| **Gateway**         | Kong                      | 3.5+           | Rate limiting, auth              |
| **IDS/IPS**         | AWS GuardDuty             | -              | Threat detection                 |
| **Encryption**      | AWS KMS                   | -              | At-rest encryption               |
| **TLS**             | TLS 1.3                   | -              | In-transit encryption            |
| **Backup**          | AWS Backup                | -              | Automated backups                |
| **Monitoring**      | Grafana Stack             | -              | Loki + Mimir + Tempo             |
| **SIEM**            | CloudTrail + Grafana Loki | -              | Security logs                    |
| **SSO**             | Keycloak                  | -              | Autenticación centralizada       |
| **Base Image**      | Alpine Linux              | 3.18+          | Minimal footprint                |
| **Runtime Image**   | Distroless                | -              | Google distroless/dotnet         |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

## 4. Requisitos Obligatorios 🔴

### Security by Design

- [ ] **Threat Modeling** obligatorio para nuevas aplicaciones o cambios arquitectónicos
- [ ] **Security review** en ADRs (sección dedicada)
- [ ] **OWASP Top 10** considerado explícitamente
- [ ] **Trust boundaries** identificados en diagramas
- [ ] **SAST** en cada pull request (SonarQube)
- [ ] **Dependency scanning** automático (OWASP Dependency-Check)
- [ ] **Container scanning** de imágenes Docker (Trivy)
- [ ] **IaC security scanning** (Checkov)

### Defensa en Profundidad (7 Capas)

- [ ] **Capa 1 - Perímetro:** AWS WAF + CloudFlare
- [ ] **Capa 2 - Red:** VPC isolation + Security Groups deny-by-default
- [ ] **Capa 3 - Gateway:** Kong rate limiting + JWT validation
- [ ] **Capa 4 - Aplicación:** Input validation + SAST
- [ ] **Capa 5 - Identidad:** Keycloak SSO + MFA + RBAC
- [ ] **Capa 6 - Datos:** Encryption at-rest/in-transit + backups
- [ ] **Capa 7 - Monitoreo:** CloudTrail + GuardDuty + Grafana alertas

### Reducción de Superficie de Ataque

- [ ] **Minimal base images:** Alpine o Distroless (NO ubuntu:latest)
- [ ] **Multi-stage builds:** Runtime sin build tools
- [ ] **Non-root user:** UID > 1000
- [ ] **Read-only filesystem:** Excepto /tmp
- [ ] **Solo ports necesarios:** Cerrar todo lo demás
- [ ] **Minimal dependencies:** Solo paquetes necesarios
- [ ] **Disable admin endpoints:** /swagger, /metrics sin auth en producción

## 5. Security by Design — Threat Modeling

### 5.1 Template Threat Model Document

```markdown
# Threat Model - Payment API

## System Overview

**Descripción:** API REST para procesamiento de pagos
**Trust Boundaries:** Kong Gateway → Payment API → PostgreSQL
**Assets:** Datos de pagos (PCI DSS), transacciones financieras

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

### 5.2 OWASP Top 10 Checklist

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

### 5.3 Security Review en ADRs

```markdown
# ADR-XXX: Implementar Payment Gateway

## Security Considerations 🔒

### Threats Identificados

1. **Credential theft**: Integración con gateway requiere API key
   - Mitigation: AWS Secrets Manager con rotación automática
2. **Data in transit**: Comunicación con gateway externo
   - Mitigation: TLS 1.3 + certificate pinning

### Controls Implementados

- [ ] API keys en AWS Secrets Manager
- [ ] HTTPS obligatorio (TLS 1.3)
- [ ] Rate limiting: 100 req/min en Kong
- [ ] Webhook signature validation (HMAC SHA256)
- [ ] Audit logging de transacciones en Grafana Loki

### Residual Risks

- **MEDIUM**: DDoS en webhook endpoint
  - Acceptance: Rate limiting + AWS WAF protección

### Security Sign-off

- [ ] Security Architect: @security-lead
- [ ] Date: 2025-01-15
```

## 6. Defensa en Profundidad — 7 Capas

### 6.1 Modelo de Capas

| Capa              | Control                       | Tecnología                  | Estado         |
| ----------------- | ----------------------------- | --------------------------- | -------------- |
| **1. Perímetro**  | WAF, DDoS protection          | AWS WAF, CloudFlare         | 🔴 Obligatorio |
| **2. Red**        | Segmentación, Security Groups | VPC, Security Groups        | 🔴 Obligatorio |
| **3. Gateway**    | Rate limiting, autenticación  | Kong API Gateway            | 🔴 Obligatorio |
| **4. Aplicación** | Input validation, SAST        | FluentValidation, SonarQube | 🔴 Obligatorio |
| **5. Identidad**  | SSO, MFA, RBAC                | Keycloak, JWT RS256         | 🔴 Obligatorio |
| **6. Datos**      | Encriptación, backups         | AWS KMS, RDS encryption     | 🔴 Obligatorio |
| **7. Monitoreo**  | IDS, logging, alertas         | Grafana, CloudTrail         | 🔴 Obligatorio |

### 6.2 Capa 1: AWS WAF

```hcl
# terraform/waf.tf
resource "aws_wafv2_web_acl" "main" {
  name  = "api-waf-${var.environment}"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  # OWASP Top 10
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
      metric_name                = "OWASPTop10Metric"
      sampled_requests_enabled   = true
    }
  }

  # Rate Limiting
  rule {
    name     = "RateLimitRule"
    priority = 2

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

  # Geo-blocking
  rule {
    name     = "GeoBlockingRule"
    priority = 3

    action {
      block {}
    }

    statement {
      not_statement {
        statement {
          geo_match_statement {
            country_codes = ["PE", "CL", "CO", "EC"]
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "GeoBlockingMetric"
      sampled_requests_enabled   = true
    }
  }
}

resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}
```

### 6.3 Capa 2: Network Segmentation

```hcl
# terraform/vpc.tf
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
}

# Subnets públicas (SOLO para ALB)
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
}

# Subnets privadas (aplicaciones ECS)
resource "aws_subnet" "private_app" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]
}

# Subnets privadas (bases de datos)
resource "aws_subnet" "private_db" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 20)
  availability_zone = data.aws_availability_zones.available.names[count.index]
}

# Security Group: ECS Tasks (deny-by-default)
resource "aws_security_group" "ecs_tasks" {
  name        = "ecs-tasks-${var.environment}"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  # Ingress: SOLO desde ALB
  ingress {
    description     = "HTTP from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Egress: SOLO necesario
  egress {
    description     = "PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.rds.id]
  }

  egress {
    description = "HTTPS externos"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### 6.4 Capa 3: Kong API Gateway

```yaml
# kong.yaml - Rate Limiting + JWT
plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 5000
      policy: local
      fault_tolerant: true

  - name: jwt
    config:
      claims_to_verify:
        - exp
        - nbf
      key_claim_name: kid
      secret_is_base64: false

  - name: request-size-limiting
    config:
      allowed_payload_size: 1 # 1MB max

  - name: ip-restriction
    config:
      deny: [] # Blacklist IPs
      allow: # Whitelist para APIs internas
        - 10.0.0.0/8
```

### 6.5 Capa 4: Aplicación — Input Validation

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers(options =>
{
    // Deshabilitar formatters no usados
    options.InputFormatters.RemoveType<XmlSerializerInputFormatter>();
    options.OutputFormatters.RemoveType<XmlSerializerOutputFormatter>();
});

// FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<Program>();
builder.Services.AddFluentValidationAutoValidation();

var app = builder.Build();

// NO exponer en producción
if (!app.Environment.IsProduction())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// Remover headers innecesarios
app.Use(async (context, next) =>
{
    context.Response.Headers.Remove("Server");
    context.Response.Headers.Remove("X-Powered-By");
    context.Response.Headers.Remove("X-AspNet-Version");
    await next();
});

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

```csharp
// Validators/CreatePaymentValidator.cs
using FluentValidation;

public class CreatePaymentValidator : AbstractValidator<CreatePaymentRequest>
{
    public CreatePaymentValidator()
    {
        RuleFor(x => x.Amount)
            .GreaterThan(0).WithMessage("Amount must be positive")
            .LessThanOrEqualTo(1000000).WithMessage("Amount exceeds maximum");

        RuleFor(x => x.Currency)
            .NotEmpty()
            .Matches("^[A-Z]{3}$").WithMessage("Invalid currency code");

        RuleFor(x => x.OrderId)
            .NotEmpty()
            .MaximumLength(50);
    }
}
```

### 6.6 Capa 5: Identidad — Keycloak SSO

```csharp
// Program.cs - JWT Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = "https://sso.talma.com/realms/payment";
        options.Audience = "payment-api";
        options.RequireHttpsMetadata = true;

        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ClockSkew = TimeSpan.Zero
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireClaim("role", "admin"));

    options.AddPolicy("PaymentWrite", policy =>
        policy.RequireClaim("permissions", "payment:write"));
});
```

```csharp
// Controllers/PaymentController.cs
[ApiController]
[Route("api/v1/payments")]
[Authorize]
public class PaymentController : ControllerBase
{
    [HttpPost]
    [Authorize(Policy = "PaymentWrite")]
    public async Task<IActionResult> CreatePayment([FromBody] CreatePaymentRequest request)
    {
        // Solo usuarios con claim "permissions: payment:write"
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        // ...
    }

    [HttpDelete("{id}")]
    [Authorize(Policy = "AdminOnly")]
    public async Task<IActionResult> DeletePayment(Guid id)
    {
        // Solo admins
        // ...
    }
}
```

### 6.7 Capa 6: Datos — Encriptación

```hcl
# terraform/encryption.tf

# KMS Key
resource "aws_kms_key" "main" {
  description             = "KMS key for ${var.environment} encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.environment}-encryption"
  target_key_id = aws_kms_key.main.key_id
}

# RDS con encriptación
resource "aws_db_instance" "main" {
  identifier     = "${var.service_name}-${var.environment}"
  engine         = "postgres"
  engine_version = "16.1"

  storage_encrypted = true
  kms_key_id        = aws_kms_key.main.arn

  backup_retention_period = 30
  backup_window           = "03:00-04:00"

  enabled_cloudwatch_logs_exports = ["postgresql"]

  parameter_group_name = aws_db_parameter_group.ssl_required.name
}

resource "aws_db_parameter_group" "ssl_required" {
  name   = "${var.service_name}-ssl-${var.environment}"
  family = "postgres16"

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }
}

# S3 con encriptación
resource "aws_s3_bucket" "main" {
  bucket = "${var.service_name}-${var.environment}"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
  }
}
```

### 6.8 Capa 7: Monitoreo — Grafana + CloudTrail

```hcl
# terraform/monitoring.tf

# CloudTrail
resource "aws_cloudtrail" "main" {
  name                          = "cloudtrail-${var.environment}"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  enable_log_file_validation    = true
  is_multi_region_trail         = true
  include_global_service_events = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::${aws_s3_bucket.main.id}/*"]
    }
  }
}

# GuardDuty
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
  }
}

# EventBridge rule para alertas
resource "aws_cloudwatch_event_rule" "security_alerts" {
  name        = "security-alerts-${var.environment}"
  description = "Security events from GuardDuty"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [4, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6, 6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 8, 8.0, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9]
    }
  })
}
```

```csharp
// appsettings.json - Serilog + Grafana Loki
{
  "Serilog": {
    "Using": ["Serilog.Sinks.Grafana.Loki"],
    "MinimumLevel": "Information",
    "WriteTo": [
      {
        "Name": "GrafanaLoki",
        "Args": {
          "uri": "https://loki.talma.com",
          "labels": [
            { "key": "app", "value": "payment-api" },
            { "key": "environment", "value": "production" }
          ],
          "propertiesAsLabels": ["level"]
        }
      }
    ],
    "Enrich": ["FromLogContext", "WithMachineName"]
  }
}
```

## 7. Reducción de Superficie de Ataque

### 7.1 Dockerfile - Minimal Image (Alpine)

```dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src

COPY ["PaymentApi/PaymentApi.csproj", "PaymentApi/"]
RUN dotnet restore "PaymentApi/PaymentApi.csproj"

COPY . .
WORKDIR "/src/PaymentApi"
RUN dotnet build "PaymentApi.csproj" -c Release -o /app/build
RUN dotnet publish "PaymentApi.csproj" -c Release -o /app/publish

# Stage 2: Runtime (Alpine minimal)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS runtime

# Crear usuario non-root
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

# Instalar SOLO dependencias necesarias
RUN apk add --no-cache ca-certificates tzdata

# Remover package manager
RUN apk del apk-tools

WORKDIR /app
COPY --from=build --chown=appuser:appgroup /app/publish .

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "PaymentApi.dll"]
```

### 7.2 ECS Task Definition - Hardening

```hcl
# terraform/ecs.tf
resource "aws_ecs_task_definition" "payment_api" {
  family                   = "payment-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([{
    name  = "payment-api"
    image = "${var.ecr_repository}/payment-api:${var.image_tag}"

    readonlyRootFilesystem = true
    privileged             = false
    user                   = "1001"

    mountPoints = [{
      sourceVolume  = "tmp"
      containerPath = "/tmp"
      readOnly      = false
    }]

    linuxParameters = {
      capabilities = {
        drop = ["ALL"]
        add  = []
      }
    }

    secrets = [
      {
        name      = "ConnectionStrings__DefaultConnection"
        valueFrom = aws_secretsmanager_secret.db_connection.arn
      }
    ]
  }])

  volume {
    name = "tmp"
  }

  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn
}
```

### 7.3 Security Group - Minimal Ports

```hcl
# terraform/security-groups.tf
resource "aws_security_group" "backend" {
  name        = "${var.environment}-backend-sg"
  vpc_id      = aws_vpc.main.id

  # SOLO port 8080 desde Kong
  ingress {
    description     = "HTTP from Kong"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.kong.id]
  }

  # Egress específico
  egress {
    description     = "To PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.postgres.id]
  }

  egress {
    description = "HTTPS for external APIs"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

## 8. CI/CD Security Pipeline

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

      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: "payment-api"
          path: "."
          format: "SARIF"
          args: >
            --failOnCVSS 7
            --enableRetired

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: dependency-check-report.sarif

  container-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Image
        run: docker build -t payment-api:${{ github.sha }} .

      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: payment-api:${{ github.sha }}
          format: "sarif"
          exit-code: "1"
          severity: "CRITICAL,HIGH"

      - name: Upload Trivy SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-results.sarif

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

## 9. Security Testing

### Unit Tests - Autorización

```csharp
// Tests/AuthorizationTests.cs
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
        var response = await _client.GetAsync("/api/v1/payments");
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task CreatePayment_WithInvalidRole_Returns403()
    {
        var token = GenerateJwtToken(role: "ReadOnly");
        _client.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", token);

        var response = await _client.PostAsJsonAsync("/api/v1/payments", new { });
        response.StatusCode.Should().Be(HttpStatusCode.Forbidden);
    }

    [Fact]
    public async Task CreatePayment_WithSqlInjectionAttempt_ReturnsBadRequest()
    {
        var payload = new { amount = "100'; DROP TABLE Payments; --" };
        var response = await _client.PostAsJsonAsync("/api/v1/payments", payload);
        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }
}
```

## 10. Validación de Cumplimiento

### Checklist

- [ ] Threat model documentado para aplicaciones críticas
- [ ] Security review en ADRs con sign-off
- [ ] AWS WAF habilitado con OWASP managed rules
- [ ] VPC con subnets privadas para aplicaciones
- [ ] Security Groups deny-by-default
- [ ] Kong Gateway con rate limiting
- [ ] Keycloak SSO con MFA habilitado
- [ ] Encriptación at-rest (KMS) y in-transit (TLS 1.3)
- [ ] CloudTrail + GuardDuty activos
- [ ] Container images Alpine o Distroless
- [ ] Non-root user en containers (UID > 1000)
- [ ] Read-only root filesystem
- [ ] SAST/DAST/Container scan en CI/CD

### Comandos de Validación

```bash
# SAST local
dotnet sonarscanner begin /k:"payment-api" /d:sonar.host.url="https://sonar.talma.com"
dotnet build
dotnet sonarscanner end

# Dependency scan
dotnet list package --vulnerable --include-transitive

# Container scan
trivy image ghcr.io/payment-api:latest --severity HIGH,CRITICAL

# IaC scan
checkov -d infrastructure/ --framework terraform

# Verificar non-root user
docker inspect payment-api:latest | jq '.[0].Config.User'

# Verificar puertos expuestos
docker inspect payment-api:latest | jq '.[0].Config.ExposedPorts'

# Verificar tamaño imagen
docker images | grep payment-api
```

## 11. Métricas de Cumplimiento

| Métrica                        | Target                       | Verificación    |
| ------------------------------ | ---------------------------- | --------------- |
| **Threat models documentados** | 100% nuevas apps             | ADR review      |
| **Security reviews en ADRs**   | 100% cambios arquitectónicos | Code review     |
| **SAST coverage**              | 100% PRs                     | CI/CD gates     |
| **Container vulnerabilities**  | 0 CRITICAL                   | Trivy scan      |
| **IaC misconfigurations**      | 0 HIGH/CRITICAL              | Checkov scan    |
| **Images Alpine/Distroless**   | 100%                         | Docker inspect  |
| **Non-root containers**        | 100%                         | Docker inspect  |
| **Encryption at-rest**         | 100%                         | Terraform state |
| **TLS 1.3**                    | 100%                         | SSL Labs scan   |
| **GuardDuty findings**         | `<5 MEDIUM/mes`              | AWS Console     |

## 12. Prohibiciones

- ❌ Deployar sin threat model en aplicaciones críticas
- ❌ ADRs sin security review section
- ❌ Ubuntu/Debian base images (usar Alpine/Distroless)
- ❌ Containers con root user
- ❌ Swagger/admin endpoints en producción sin autenticación
- ❌ Security Groups con 0.0.0.0/0 en ingress (excepto ALB)
- ❌ Secrets hardcodeados (usar AWS Secrets Manager)
- ❌ Comunicación HTTP (TLS 1.3 obligatorio)
- ❌ Logs sin sanitización de datos sensibles
- ❌ Deployar con vulnerabilidades CRITICAL sin mitigación

## 13. Referencias

**OWASP:**

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

**AWS:**

- [AWS Security Best Practices](https://docs.aws.amazon.com/security/)
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/)
- [AWS WAF Documentation](https://docs.aws.amazon.com/waf/)

**Microsoft:**

- [Microsoft Security Development Lifecycle](https://www.microsoft.com/en-us/securityengineering/sdl/)
- [.NET Secure Coding Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/security/)

**Standards:**

- [NIST SP 800-53 - Security Controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
