---
id: secure-defaults
sidebar_position: 6
title: Secure Defaults
description: Configurar sistemas con defaults seguros, no inseguros que requieren hardening
---

# Secure Defaults

## Contexto

Este estándar establece **Secure Defaults**: sistemas DEBEN arrancar con configuración **segura por defecto**, no insegura. Defaults inseguros causan brechas. Complementa el [lineamiento de Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md) asegurando **seguridad inherente en configuración base**.

---

## Principios Fundamentales

```yaml
# ✅ Secure Defaults = Seguro sin configuración adicional

Philosophy: ❌ "Secure if configured correctly" (requiere expertise)
  ✅ "Secure by default" (funciona seguro out-of-the-box)

Fail-Safe:
  - Si falla configuración → Sistema seguro (no inseguro)
  - Ejemplo: Si TLS cert falla → Rechazar conexión (no fallback HTTP)

Opt-Out Security:
  - Security features ON por defecto
  - Usuario debe explicitly deshabilitar (con warning)

Least Privilege:
  - Permisos mínimos por defecto
  - Usuario debe explicitly solicitar más

Explicit Configuration:
  - No secrets en defaults
  - No "admin/admin" passwords
  - Force user a configurar en primer uso
```

## Configuration Defaults

```yaml
# ✅ Secure vs Insecure Defaults

1. Authentication:
  ❌ Insecure:
    - Default credentials: admin/admin
    - Password opcional
    - No MFA
    - Unlimited login attempts

  ✅ Secure:
    - No default credentials (setup wizard)
    - Password obligatorio (12+ chars, complexity)
    - MFA prompt en primera configuración
    - Rate limiting: 5 intentos/15 min

2. Encryption:
  ❌ Insecure:
    - HTTP allowed (no HTTPS enforcement)
    - TLS 1.0, 1.1 enabled
    - Weak ciphers enabled (RC4, DES)
    - Database sin encryption

  ✅ Secure:
    - HTTPS only (HTTP → HTTPS redirect)
    - TLS 1.3 only (1.2 minimum)
    - Strong ciphers only (AES-GCM, ChaCha20)
    - Database encryption at rest (KMS)

3. Access Control:
  ❌ Insecure:
    - CORS allow all origins (*)
    - No authentication required
    - Public read/write
    - All ports open (0.0.0.0/0)

  ✅ Secure:
    - CORS specific origins only
    - Authentication required (JWT)
    - Private by default (explicit public)
    - Only necessary ports (443 HTTPS)

4. Logging & Monitoring:
  ❌ Insecure:
    - Logs disabled
    - Verbose error messages (stack traces públicos)
    - No audit trail

  ✅ Secure:
    - Logs enabled (CloudWatch)
    - Generic error messages (details en logs)
    - Audit trail (CloudTrail)

5. Debug & Development:
  ❌ Insecure:
    - Debug mode ON en producción
    - Swagger UI público
    - SQL query display en errors
    - Source maps expuestos

  ✅ Secure:
    - Debug OFF en producción
    - Swagger requiere authentication
    - Generic error messages
    - Source maps solo en staging
```

## Application Configuration

```csharp
// ✅ Secure Defaults en ASP.NET Core

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        // ✅ HTTPS Enforcement (Secure Default)
        builder.Services.AddHttpsRedirection(options =>
        {
            options.HttpsPort = 443;
            options.RedirectStatusCode = StatusCodes.Status308PermanentRedirect;
        });

        // ✅ HSTS (Strict Transport Security)
        builder.Services.AddHsts(options =>
        {
            options.MaxAge = TimeSpan.FromDays(365);
            options.IncludeSubDomains = true;
            options.Preload = true;
        });

        // ✅ CORS Restrictive (Secure Default)
        builder.Services.AddCors(options =>
        {
            options.AddDefaultPolicy(policy =>
            {
                policy
                    .WithOrigins("https://app.talma.com")  // ✅ Specific, no wildcard
                    .WithMethods("GET", "POST", "PUT", "DELETE")
                    .WithHeaders("Content-Type", "Authorization")
                    .AllowCredentials();
            });
        });

        // ✅ Security Headers (Secure Default)
        builder.Services.AddAntiforgery(options =>
        {
            options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
            options.Cookie.SameSite = SameSiteMode.Strict;
        });

        var app = builder.Build();

        // ✅ Disable Verbose Errors (Secure Default)
        if (app.Environment.IsProduction())
        {
            app.UseExceptionHandler("/error");  // Generic error page
            app.UseHsts();
        }
        else
        {
            app.UseDeveloperExceptionPage();  // Verbose only in dev
        }

        // ✅ Security Headers Middleware
        app.Use(async (context, next) =>
        {
            context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
            context.Response.Headers.Add("X-Frame-Options", "DENY");
            context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");
            context.Response.Headers.Add("Referrer-Policy", "strict-origin-when-cross-origin");
            context.Response.Headers.Add(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
            );

            await next();
        });

        app.UseHttpsRedirection();  // ✅ Force HTTPS
        app.UseCors();              // ✅ Apply CORS policy
        app.UseAuthentication();    // ✅ Require authentication
        app.UseAuthorization();     // ✅ Enforce authorization

        app.MapControllers();
        app.Run();
    }
}

// ❌ WRONG: Insecure Defaults
/*
// Accepts HTTP (no redirect)
// CORS allow all (*)
// No security headers
// Verbose errors en producción
// No authentication required
*/
```

## Infrastructure Defaults

```yaml
# ✅ Secure Defaults en Terraform (AWS)

# RDS Instance (Secure Defaults)
resource "aws_db_instance" "sales" {
  identifier = "sales-db"
  engine     = "postgres"

  # ✅ Security Defaults
  storage_encrypted            = true                # ✅ Encryption ON
  kms_key_id                  = aws_kms_key.rds.arn

  publicly_accessible         = false               # ✅ Private by default

  deletion_protection         = true                # ✅ Prevent accidental delete

  enabled_cloudwatch_logs_exports = [              # ✅ Logging ON
    "postgresql",
    "upgrade"
  ]

  backup_retention_period     = 30                  # ✅ 30 días backups
  backup_window              = "03:00-04:00"

  auto_minor_version_upgrade = true                 # ✅ Security patches auto

  iam_database_authentication_enabled = true        # ✅ IAM auth (no passwords)

  vpc_security_group_ids = [
    aws_security_group.rds.id                       # ✅ Restrictive SG
  ]

  # ❌ NO usar defaults inseguros:
  # publicly_accessible = true                      ← ❌ NEVER
  # storage_encrypted = false                       ← ❌ NEVER
  # deletion_protection = false                     ← ❌ Risk
}

# Security Group (Secure Defaults)
resource "aws_security_group" "rds" {
  name        = "sales-rds-sg"
  description = "RDS security group (restrictive)"

  # ✅ Explicit ingress (no default allow all)
  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]  # ✅ Only ECS
  }

  # ✅ Explicit egress (no default allow all)
  egress {
    description = "Deny all egress (DB no necesita outbound)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = []  # ✅ Deny all
  }

  # ❌ NO usar defaults inseguros:
  # ingress { cidr_blocks = ["0.0.0.0/0"] }        ← ❌ NEVER
  # egress { cidr_blocks = ["0.0.0.0/0"] }         ← ❌ Usually unnecessary
}

# S3 Bucket (Secure Defaults)
resource "aws_s3_bucket" "sales_invoices" {
  bucket = "talma-sales-invoices"

  # ✅ Security Defaults via separate resources (AWS best practice)
}

resource "aws_s3_bucket_versioning" "sales_invoices" {
  bucket = aws_s3_bucket.sales_invoices.id

  versioning_configuration {
    status = "Enabled"  # ✅ Versioning ON (data protection)
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sales_invoices" {
  bucket = aws_s3_bucket.sales_invoices.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"           # ✅ KMS (not S3-managed)
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true                 # ✅ Reduce KMS costs
  }
}

resource "aws_s3_bucket_public_access_block" "sales_invoices" {
  bucket = aws_s3_bucket.sales_invoices.id

  # ✅ Block ALL public access by default
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "sales_invoices" {
  bucket = aws_s3_bucket.sales_invoices.id

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 90  # ✅ Auto-cleanup (cost + security)
    }
  }
}

# ❌ WRONG: Insecure S3 Defaults
/*
resource "aws_s3_bucket_acl" "sales_invoices" {
  bucket = aws_s3_bucket.sales_invoices.id
  acl    = "public-read"  ← ❌ NEVER public by default
}
*/
```

## Container Defaults

```dockerfile
# ✅ Secure Dockerfile Defaults

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS base

# ✅ Non-root user (Secure Default)
RUN addgroup -g 1001 appuser && \
    adduser -u 1001 -G appuser -s /bin/sh -D appuser

# ✅ Minimal base (Alpine, smaller attack surface)
WORKDIR /app
EXPOSE 8080

# ✅ Readonly filesystem (where possible)
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["Talma.Sales.Api/Talma.Sales.Api.csproj", "Talma.Sales.Api/"]
RUN dotnet restore "Talma.Sales.Api/Talma.Sales.Api.csproj"

COPY . .
WORKDIR "/src/Talma.Sales.Api"
RUN dotnet build -c Release -o /app/build

FROM build AS publish
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# ✅ Run as non-root (Secure Default)
USER appuser

# ✅ Health check (operational security)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health/live || exit 1

# ✅ No hardcoded secrets (use Secrets Manager)
# ✅ No debug tools en production image

ENTRYPOINT ["dotnet", "Talma.Sales.Api.dll"]

# ❌ WRONG: Insecure Dockerfile
/*
FROM mcr.microsoft.com/dotnet/aspnet:8.0  ← ❌ No Alpine (larger)
USER root                                  ← ❌ Root user
EXPOSE 22                                   ← ❌ SSH exposed
ENV DB_PASSWORD=admin123                   ← ❌ Hardcoded secret
RUN apt-get install curl vim netcat        ← ❌ Debug tools (attack surface)
*/
```

## Validation

```yaml
# ✅ Validar Secure Defaults (Automated)

Pre-Deployment Checks:

  1. Terraform Validation:
     tool: checkov
     command: checkov -d . --framework terraform

     Checks:
       ✅ S3 buckets not public
       ✅ RDS encryption enabled
       ✅ Security groups not 0.0.0.0/0
       ✅ IAM policies not wildcard (*)

  2. Container Scanning:
     tool: trivy
     command: trivy image talma/sales-api:latest

     Checks:
       ✅ No critical vulnerabilities
       ✅ Running as non-root
       ✅ No secrets in image
       ✅ Minimal base image

  3. SAST:
     tool: SonarQube

     Checks:
       ✅ No hardcoded secrets
       ✅ HTTPS enforced
       ✅ Authentication required
       ✅ Input validation present

  4. Configuration Audit:
     tool: custom script

     appsettings.Production.json:
       ✅ "DetailedErrors": false
       ✅ "Logging:LogLevel:Default": "Warning"
       ✅ "AllowedHosts": específico (no "*")
       ✅ No secrets (only references a Secrets Manager)

Runtime Validation:

  1. Security Headers:
     curl -I https://api.talma.com

     Expected:
       ✅ Strict-Transport-Security: max-age=31536000
       ✅ X-Content-Type-Options: nosniff
       ✅ X-Frame-Options: DENY
       ✅ Content-Security-Policy: ...
       ❌ Server: [redacted]  (no version disclosure)

  2. TLS Configuration:
     tool: testssl.sh
     command: testssl.sh https://api.talma.com

     Expected:
       ✅ Rating: A or A+
       ✅ TLS 1.3 preferred
       ✅ No weak ciphers
       ✅ Certificate valid

  3. Authentication:
     curl https://api.talma.com/api/orders

     Expected:
       ❌ 401 Unauthorized (not 200 OK)
       "message": "Authentication required"
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** configurar HTTPS enforcement (no HTTP)
- **MUST** habilitar encryption at rest (KMS)
- **MUST** usar TLS 1.3 (mínimo 1.2)
- **MUST** deshabilitar debug mode en producción
- **MUST** configurar security headers (HSTS, CSP, etc.)
- **MUST** usar non-root user en containers
- **MUST** block public access (S3, RDS) por defecto
- **MUST** require strong passwords (12+ chars, complexity)

### SHOULD (Fuertemente recomendado)

- **SHOULD** validar secure defaults con automated tools (checkov, trivy)
- **SHOULD** usar Alpine base images (smaller attack surface)
- **SHOULD** documentar defaults en README
- **SHOULD** fail-safe (si config falla → seguro, no inseguro)

### MUST NOT (Prohibido)

- **MUST NOT** usar default credentials (admin/admin)
- **MUST NOT** hardcodear secrets en configuración
- **MUST NOT** allow CORS wildcard (\*) en producción
- **MUST NOT** exponer verbose errors públicamente
- **MUST NOT** habilitar debug tools en producción containers
- **MUST NOT** hacer recursos públicos por defecto

---

## Referencias

- [Lineamiento: Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md)
- [Security by Design](./security-by-design.md)
- [IaC Scanning](./iac-scanning.md)
- [Container Scanning](./container-scanning.md)
