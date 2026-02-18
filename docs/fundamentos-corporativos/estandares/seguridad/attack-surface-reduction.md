---
id: attack-surface-reduction
sidebar_position: 4
title: Attack Surface Reduction
description: Minimizar puntos de exposición y vectores de ataque en la arquitectura
---

# Attack Surface Reduction

## Contexto

Este estándar define estrategias para **reducir superficie de ataque**: minimizar puntos de exposición que atacantes pueden explotar. Menos surface = menos vulnerabilidades. Complementa el [lineamiento de Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md) mediante **minimización proactiva de riesgos**.

---

## Conceptos Fundamentales

```yaml
# ✅ Attack Surface = Suma de vectores de ataque

Components:
  1. Network Surface:
    - Puertos abiertos
    - Endpoints públicos
    - Protocolos expuestos

  2. Application Surface:
    - APIs públicas
    - Input fields
    - Upload capabilities

  3. Human Surface:
    - Usuarios con acceso
    - Credenciales activas
    - Permisos otorgados

Reduction Strategies:
  ✅ Eliminate: Remover componentes innecesarios
  ✅ Isolate: Separar zonas de confianza
  ✅ Restrict: Limitar acceso (least privilege)
  ✅ Harden: Configurar secure defaults
  ✅ Monitor: Detectar anomalías

Metrics:
  - Endpoints públicos (target: minimizar)
  - Open ports (target: solo necesarios)
  - Usuarios con admin access (target: < 5)
  - Services with internet access (target: 0 para backend)
  - Third-party integrations (target: auditar quarterly)
```

## Network Surface Reduction

```yaml
# ✅ Minimizar exposición de red

❌ Arquitectura Insegura (High Surface):

  Internet
     │
     ├─────────► ECS Task :22 (SSH)     ← ❌ SSH público
     ├─────────► ECS Task :8080 (HTTP)  ← ❌ HTTP directo
     ├─────────► RDS :5432              ← ❌ Database público
     └─────────► ElastiCache :6379      ← ❌ Redis público

  Problems:
    - 4 servicios expuestos directamente
    - SSH brute-force attacks
    - Database direct access (no auth layer)
    - Redis no authentication por defecto

✅ Arquitectura Segura (Low Surface):

  Internet
     │
     └─────────► ALB :443 (HTTPS only)
                   │
                   ├─► ECS Task (private subnet, no SSH)
                   │      │
                   │      ├─► RDS (private subnet :5432)
                   │      └─► ElastiCache (private subnet :6379)
                   │
                   └─► Bastion Host (solo VPN users)

  Improvements:
    ✅ 1 endpoint público (ALB) vs 4
    ✅ Backend sin acceso internet (private subnet)
    ✅ SSH solo via bastion (MFA required)
    ✅ Database/Redis no accesibles desde internet
    ✅ NAT Gateway para outbound only

  Attack Surface Reduction: 75%
```

## Port and Protocol Hardening

```yaml
# ✅ Cerrar puertos innecesarios

Security Group (Sales Service):

  ❌ Permissive (High Risk):
    Inbound:
      - 0.0.0.0/0 → 0-65535 (ALL PORTS)  ← ❌ Disaster

  ✅ Restrictive (Low Risk):
    Inbound:
      - ALB SG → 8080 (HTTP)             ← Solo ALB puede llamar
      - Bastion SG → 22 (SSH)            ← Solo bastion (emergencias)

    Outbound:
      - RDS SG → 5432 (PostgreSQL)
      - MSK SG → 9092 (Kafka)
      - 0.0.0.0/0 → 443 (HTTPS)          ← External APIs only
      - Deny all others                   ← Default deny

  Result: 2 inbound rules (vs all ports)

Protocol Hardening:

  ✅ TLS 1.3 only (no TLS 1.0, 1.1, 1.2)
  ✅ Strong ciphers only:
     - TLS_AES_128_GCM_SHA256
     - TLS_AES_256_GCM_SHA384
     - TLS_CHACHA20_POLY1305_SHA256

  ❌ Disable weak ciphers:
     - RC4, DES, 3DES
     - MD5-based
     - Export-grade

  ✅ Disable unnecessary protocols:
     - FTP (use SFTP)
     - Telnet (use SSH)
     - HTTP (use HTTPS)
     - SMBv1 (use SMBv3)
```

## Application Surface Reduction

```yaml
# ✅ Minimizar funcionalidad expuesta

API Endpoints:
  ❌ Over-Exposed (20 endpoints): GET    /api/orders
    POST   /api/orders
    PUT    /api/orders/{id}
    PATCH  /api/orders/{id}
    DELETE /api/orders/{id}
    GET    /api/orders/{id}/lines
    POST   /api/orders/{id}/lines
    DELETE /api/orders/{id}/lines/{lineId}
    GET    /api/customers
    POST   /api/customers
    PUT    /api/customers/{id}
    DELETE /api/customers/{id}   ← ❌ Dangerous
    GET    /api/internal/metrics  ← ❌ Info disclosure
    GET    /api/admin/config      ← ❌ Config exposure
    POST   /api/admin/sql         ← ❌ SQL execution!!
    ... 5 más innecesarios

  ✅ Minimal (8 endpoints): GET    /api/orders              ← List own orders
    POST   /api/orders              ← Create order
    GET    /api/orders/{id}         ← Get single order
    PATCH  /api/orders/{id}/cancel  ← Cancel (no full UPDATE)

    GET    /api/customers/me        ← Own profile only
    PATCH  /api/customers/me        ← Update own profile

    GET    /health/live             ← Health check
    GET    /health/ready            ← Readiness check

  Removed: ❌ DELETE orders (soft-delete via cancel)
    ❌ Admin endpoints (separate admin API)
    ❌ Full UPDATE (PATCH con campos específicos más seguro)
    ❌ SQL execution (obvio)
    ❌ Metrics públicos (usar CloudWatch)

  Attack Surface: -60% (20 → 8 endpoints)

Feature Reduction:
  ❌ Expansión de Features (Risk):
    - File upload (arbitrary types)
    - Embed JavaScript en notes
    - Export to arbitrary formats
    - Execute custom reports (SQL injection risk)

  ✅ Minimal Features (Secure):
    - File upload: Solo images (PNG, JPG), < 5MB, virus scan
    - Notes: Plain text only, HTML encode
    - Export: PDF only (formato fijo)
    - Reports: Pre-defined queries (no custom SQL)
```

## Dependency Surface Reduction

```csharp
// ❌ Excessive Dependencies (High Risk)

// Package references (50+ packages)
<Project Sdk="Microsoft.NET.Sdk.Web">
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" />        // ❌ Redundant (System.Text.Json built-in)
    <PackageReference Include="jQuery" />                  // ❌ Frontend lib en backend
    <PackageReference Include="MongoDB.Driver" />          // ❌ No usado
    <PackageReference Include="RabbitMQ.Client" />         // ❌ Cambiamos a Kafka
    <PackageReference Include="Autofac" />                 // ❌ Built-in DI suficiente
    <PackageReference Include="AutoMapper" />              // ❌ Manual mapping más claro
    <PackageReference Include="Polly" />                   // ❌ No usado actualmente
    <PackageReference Include="Serilog.Sinks.Seq" />       // ❌ No tenemos Seq
    ... 42 más
  </ItemGroup>
</Project>

// Problems:
// - 50 dependencies = 50 potential vulnerabilities
// - Transitive dependencies: 150+ total packages
// - Dependabot alerts: 12 high/critical

// ✅ Minimal Dependencies (Low Risk)

<Project Sdk="Microsoft.NET.Sdk.Web">
  <ItemGroup>
    <!-- Core (necesarios) -->
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />
    <PackageReference Include="Confluent.Kafka" Version="2.3.0" />
    <PackageReference Include="FluentValidation.AspNetCore" Version="11.3.0" />

    <!-- Authentication -->
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.0" />

    <!-- AWS -->
    <PackageReference Include="AWSSDK.SecretsManager" Version="3.7.300" />

    <!-- Testing -->
    <PackageReference Include="xUnit" Version="2.6.0" />
    <PackageReference Include="Moq" Version="4.20.0" />
    <PackageReference Include="Testcontainers.PostgreSql" Version="3.6.0" />
  </ItemGroup>
</Project>

// Result:
// ✅ 9 dependencies (vs 50)
// ✅ 25 transitive (vs 150)
// ✅ 0 alerts (vs 12)
// ✅ Faster builds (less download)
// ✅ Smaller container image (200MB vs 450MB)

// Audit quarterly:
dotnet list package --vulnerable --include-transitive
```

## Access Surface Reduction

```yaml
# ✅ Minimizar usuarios con acceso privilegiado

IAM Users (AWS):

  ❌ Over-Privileged (10 admin users):
    - dev1@talma.com (AdministratorAccess)   ← ❌ Full access
    - dev2@talma.com (AdministratorAccess)
    - dev3@talma.com (PowerUserAccess)
    - qa1@talma.com (AdministratorAccess)    ← ❌ QA no necesita
    - contractor1 (AdministratorAccess)      ← ❌ External!!
    ... 5 más

  ✅ Least Privilege (3 admin, rest limited):
    - platform-admin@talma.com (AdministratorAccess)  ← Solo 1 persona
    - security-admin@talma.com (SecurityAudit + IAM)
    - billing-admin@talma.com (Billing only)

    - dev-team@talma.com (Custom: Deploy, Logs, Metrics)  ← No delete
    - qa-team@talma.com (ReadOnly + Logs)
    - contractor@talma.com (Zero standing permissions)    ← JIT access

  Reduction: 10 admin → 3 admin

Service Accounts:

  ❌ Broad Permissions:
    {
      "Statement": [{
        "Effect": "Allow",
        "Action": "*",              ← ❌ ALL actions
        "Resource": "*"             ← ❌ ALL resources
      }]
    }

  ✅ Scoped Permissions:
    {
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "secretsmanager:GetSecretValue"  ← Solo leer secrets
          ],
          "Resource": "arn:aws:secretsmanager:us-east-1:123:secret:sales/*"
        },
        {
          "Effect": "Allow",
          "Action": [
            "s3:GetObject"                   ← Solo leer S3
          ],
          "Resource": "arn:aws:s3:::sales-invoices/*"
        }
      ]
    }

Credential Rotation:

  ✅ Short-lived credentials:
    - IAM roles (ECS tasks): Rotate every 15 min (automatic)
    - Service accounts: Rotate monthly
    - Database passwords: Rotate quarterly (Secrets Manager)

  ✅ Revoke unused:
    - Last used > 90 days → Disable
    - Last used > 180 days → Delete

    Script:
      aws iam get-credential-report
      # Parse last_used_date
      # Disable if > 90 days
```

## Monitoring and Detection

```yaml
# ✅ Detectar expansión de attack surface

CloudWatch Alarms:

  1. New Public Endpoint Created:
     - Event: CreateLoadBalancer (internet-facing)
     - Alert: Slack #security
     - Action: Manual review required

  2. Security Group Modified:
     - Event: AuthorizeSecurityGroupIngress (source 0.0.0.0/0)
     - Alert: PagerDuty (high priority)
     - Action: Auto-revert + incident

  3. IAM Admin Created:
     - Event: AttachUserPolicy (AdministratorAccess)
     - Alert: Email + Slack
     - Action: Require approval (manual)

  4. S3 Bucket Made Public:
     - Event: PutBucketPolicy (public read)
     - Alert: Critical alert
     - Action: Auto-revert (Lambda)

Periodic Audits:

  Monthly:
    ✅ Review open ports (nmap scan)
    ✅ Review public endpoints (API catalog)
    ✅ Review IAM users with admin (should be < 5)
    ✅ Review unused credentials (disable > 90 days)

  Quarterly:
    ✅ Dependency audit (dotnet list package --vulnerable)
    ✅ Container scan (Trivy)
    ✅ Attack surface assessment (external scan)

  Annually:
    ✅ Penetration testing (external firm)
    ✅ Architecture security review

Metrics Dashboard:

  Attack Surface Metrics (Grafana):
    - Public endpoints: 3 (target: < 5)
    - Open ports per service: 2 avg (target: < 3)
    - Admin users: 3 (target: < 5)
    - Dependencies with CVEs: 0 (target: 0 high/critical)
    - Services with internet access: 0 backend (target: 0)

  Trend: Reducing over time ✅
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar private subnets para backend services (no internet direct)
- **MUST** minimizar security group rules (solo puertos/protocolos necesarios)
- **MUST** aplicar principle of least privilege (IAM roles)
- **MUST** remover dependencies no usadas (audit quarterly)
- **MUST** deshabilitar protocols/ciphers débiles (TLS 1.3 only)
- **MUST** cerrar endpoints administrativos (separate admin API)
- **MUST** rotar credenciales regularmente

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar bastion host para SSH (no directo a instances)
- **SHOULD** implementar API Gateway (centralize security)
- **SHOULD** monitorear creación de recursos públicos (CloudWatch)
- **SHOULD** realizar attack surface assessment (quarterly)
- **SHOULD** usar JIT access para operaciones privilegiadas

### MUST NOT (Prohibido)

- **MUST NOT** exponer databases directamente a internet
- **MUST NOT** usar security groups permissive (0.0.0.0/0 all ports)
- **MUST NOT** otorgar AdministratorAccess sin justificación
- **MUST NOT** mantener credenciales no usadas (> 90 días)
- **MUST NOT** exponer metrics/admin endpoints públicamente

---

## Referencias

- [Lineamiento: Arquitectura Segura](../../lineamientos/seguridad/01-arquitectura-segura.md)
- [Security by Design](./security-by-design.md)
- [Trust Boundaries](./trust-boundaries.md)
- [Network Security](./network-security.md)
- [IAM Best Practices](./identity-access-management.md)
