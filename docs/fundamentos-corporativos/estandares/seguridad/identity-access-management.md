---
id: identity-access-management
sidebar_position: 9
title: Gestión de Identidades y Accesos
description: Estándares consolidados de SSO con Keycloak, MFA, identidades de servicios y principio de mínimo privilegio
---

# Estándar Técnico — Gestión de Identidades y Accesos (IAM)

## 1. Propósito

Implementar gestión integral de identidades y accesos mediante Single Sign-On (SSO) con Keycloak, autenticación multi-factor (MFA) obligatoria, identidades de servicios sin credentials hardcodeados, y principio de mínimo privilegio en AWS IAM y RBAC.

## 2. Alcance

**Aplica a:**

- Usuarios internos (empleados)
- Usuarios externos (clientes)
- Servicios backend (.NET APIs)
- Acceso a aplicaciones web
- Comunicación service-to-service
- Acceso a AWS resources (S3, Secrets Manager, RDS)
- Permisos de base de datos

**No aplica a:**

- Ambientes dev local (dotnet user-secrets)
- Prototipos sin datos reales

## 3. Tecnologías Aprobadas

| Componente            | Tecnología                                        | Versión mínima | Observaciones        |
| --------------------- | ------------------------------------------------- | -------------- | -------------------- |
| **Identity Provider** | Keycloak                                          | 23.0+          | Self-hosted SSO      |
| **Protocol**          | OpenID Connect 1.0                                | -              | OAuth 2.0 + identity |
| **Token Type**        | JWT RS256                                         | -              | Asymmetric signing   |
| **Session Store**     | Redis                                             | 7.2+           | Shared sessions      |
| **MFA TOTP**          | Google Authenticator                              | -              | RFC 6238             |
| **MFA WebAuthn**      | YubiKey, Windows Hello                            | -              | FIDO2                |
| **.NET Client**       | Microsoft.AspNetCore.Authentication.OpenIdConnect | 8.0+           | OIDC middleware      |
| **AWS Identity**      | IAM Roles for ECS                                 | -              | Workload identity    |
| **Secrets**           | AWS Secrets Manager                               | -              | NO env vars          |
| **Database**          | PostgreSQL roles                                  | 16+            | Row-level security   |
| **Auditing**          | AWS CloudTrail                                    | -              | Logs de acceso       |
| **SDK**               | AWS SDK for .NET                                  | 3.7+           | AssumeRole           |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

## 4. Requisitos Obligatorios 🔴

### SSO y Autenticación

- [ ] **Keycloak SSO** para todas las aplicaciones
- [ ] **Realms separados:** `talma-internal` (empleados), `talma-customers` (clientes)
- [ ] **JWT RS256** con tokens de 15 minutos
- [ ] **HTTPS obligatorio** (TLS 1.3)
- [ ] **Claims estándar:** sub, email, name, roles
- [ ] **Custom claims:** tenant_id, permissions

### Multi-Factor Authentication

- [ ] **MFA obligatorio** para acceso a producción
- [ ] **TOTP** (Google Authenticator) como método principal
- [ ] **WebAuthn** (YubiKey) como alternativa
- [ ] **Backup codes** (10 one-time codes)
- [ ] **NO SMS** (vulnerabilidad SIM swapping)
- [ ] **Re-authentication** cada 8 horas en producción

### Service Identities

- [ ] **AWS IAM Roles** por cada servicio ECS
- [ ] **Keycloak Service Accounts** para APIs internas
- [ ] **NO hardcoded credentials**
- [ ] **Short-lived tokens** (15 minutos)
- [ ] **Auto-rotation** de secrets

### Least Privilege

- [ ] **NO usar IAM Users** para servicios
- [ ] **Un rol por servicio** (no compartir)
- [ ] **Policies específicas** (NO wildcards innecesarios)
- [ ] **Deny-by-default** (permisos explícitos)
- [ ] **Revisión trimestral** de permisos

## 5. Single Sign-On (SSO) con Keycloak

### 5.1 Configuración de Keycloak

```yaml
# docker-compose.yml
version: "3.8"

services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    command: start
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: ${KC_DB_PASSWORD}
      KC_HOSTNAME: auth.talma.com
      KC_HOSTNAME_STRICT: true
      KC_HTTP_ENABLED: false
      KC_HTTPS_CERTIFICATE_FILE: /opt/keycloak/conf/cert.pem
      KC_HTTPS_CERTIFICATE_KEY_FILE: /opt/keycloak/conf/key.pem
    ports:
      - "8443:8443"
    volumes:
      - ./keycloak-certs:/opt/keycloak/conf
    depends_on:
      - postgres

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: ${KC_DB_PASSWORD}
    volumes:
      - keycloak_db:/var/lib/postgresql/data

volumes:
  keycloak_db:
```

### 5.2 .NET Integration con JWT

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.Authority = "https://auth.talma.com:8443/realms/talma-internal";
    options.Audience = "payment-api";
    options.RequireHttpsMetadata = true;

    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidIssuer = "https://auth.talma.com:8443/realms/talma-internal",
        ValidateAudience = true,
        ValidAudience = "payment-api",
        ValidateLifetime = true,
        ClockSkew = TimeSpan.FromMinutes(1),
        ValidateIssuerSigningKey = true
    };

    options.Events = new JwtBearerEvents
    {
        OnAuthenticationFailed = context =>
        {
            Log.Error("JWT validation failed: {Error}", context.Exception.Message);
            return Task.CompletedTask;
        },
        OnTokenValidated = context =>
        {
            var userId = context.Principal?.FindFirst(ClaimTypes.NameIdentifier)?.Value;
            Log.Information("User {UserId} authenticated", userId);
            return Task.CompletedTask;
        }
    };
});

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("RequireAdmin", policy =>
        policy.RequireClaim("realm_access", "admin"));

    options.AddPolicy("RequirePaymentAccess", policy =>
        policy.RequireClaim("realm_access", "payment:write"));
});

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

### 5.3 Protected Controller

```csharp
[ApiController]
[Route("api/v1/[controller]")]
[Authorize]
public class PaymentsController : ControllerBase
{
    [HttpGet]
    [Authorize(Policy = "RequirePaymentAccess")]
    public IActionResult GetPayments()
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var email = User.FindFirst(ClaimTypes.Email)?.Value;
        var roles = User.FindAll("realm_access").Select(c => c.Value).ToList();

        return Ok(new { userId, email, roles });
    }

    [HttpPost]
    [Authorize(Policy = "RequirePaymentAccess")]
    public async Task<IActionResult> CreatePayment([FromBody] CreatePaymentRequest request)
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        // ...
        return CreatedAtAction(nameof(GetPayment), new { id = payment.Id }, payment);
    }
}
```

## 6. Multi-Factor Authentication (MFA)

### 6.1 Configuración en Keycloak

```bash
# Habilitar TOTP en Keycloak Admin Console
# 1. Authentication → Required Actions → "Configure OTP" (Default Action)
# 2. Authentication → Flows → Browser
#    - Username Password Form (REQUIRED)
#    - OTP Form (REQUIRED)
# 3. Authentication → Policies → OTP Policy
#    - OTP Type: Time-based (TOTP)
#    - Hash Algorithm: SHA256
#    - Digits: 6
#    - Period: 30 segundos

# Habilitar WebAuthn
# 1. Authentication → Required Actions → "Webauthn Register"
# 2. Authentication → Policies → WebAuthn Policy
#    - Relying Party: Talma
#    - Signature Algorithms: ES256, RS256
#    - Authenticator Attachment: platform, cross-platform
```

### 6.2 Políticas de MFA

| Ambiente          | MFA                           | Grace Period | Re-auth  |
| ----------------- | ----------------------------- | ------------ | -------- |
| **Producción**    | Obligatorio                   | 7 días       | 8 horas  |
| **Staging**       | Opcional (recomendado admins) | -            | 24 horas |
| **Dev**           | Opcional                      | -            | -        |
| **Admin Console** | Siempre obligatorio           | 0 días       | 4 horas  |

### 6.3 Verificar MFA en .NET (Opcional)

```csharp
// Attributes/RequireMfaAttribute.cs
public class RequireMfaAttribute : AuthorizeAttribute, IAuthorizationRequirement
{
}

public class RequireMfaHandler : AuthorizationHandler<RequireMfaAttribute>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        RequireMfaAttribute requirement)
    {
        // ACR (Authentication Context Class Reference)
        // Keycloak set acr=1 si MFA fue usado
        var acrClaim = context.User.FindFirst("acr")?.Value;

        if (acrClaim == "1" || acrClaim == "2")
        {
            context.Succeed(requirement);
        }
        else
        {
            context.Fail();
        }

        return Task.CompletedTask;
    }
}

// Uso en controller
[Authorize]
[RequireMfa]
public class AdminController : ControllerBase
{
    // Solo accesible si usuario autenticó con MFA
}
```

## 7. Service Identities — AWS IAM Roles

### 7.1 IAM Role por Servicio

```hcl
# terraform/iam-payment-api.tf
resource "aws_iam_role" "payment_api_task" {
  name = "ecs-task-payment-api-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# Policy: Secrets Manager (SOLO secrets de payment-api)
resource "aws_iam_role_policy" "payment_api_secrets" {
  role = aws_iam_role.payment_api_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ]
      Resource = "arn:aws:secretsmanager:${var.region}:${var.account_id}:secret:/${var.environment}/payment-api/*"
    }]
  })
}

# Policy: S3 (SOLO prefix específico)
resource "aws_iam_role_policy" "payment_api_s3" {
  role = aws_iam_role.payment_api_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject"
      ]
      Resource = "arn:aws:s3:::${var.bucket_name}/payments/*"
    }]
  })
}

# ECS Task Definition
resource "aws_ecs_task_definition" "payment_api" {
  family                   = "payment-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"

  task_role_arn      = aws_iam_role.payment_api_task.arn
  execution_role_arn = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name  = "payment-api"
    image = "${var.ecr_repository}/payment-api:${var.image_tag}"
  }])
}
```

### 7.2 .NET — AWS SDK sin Credentials

```csharp
// Services/SecretsService.cs
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;

public class SecretsService
{
    private readonly IAmazonSecretsManager _secretsManager;

    public SecretsService()
    {
        // ✅ SDK usa automáticamente IAM Role del ECS Task
        _secretsManager = new AmazonSecretsManagerClient();
    }

    public async Task<string> GetSecretAsync(string secretName)
    {
        var request = new GetSecretValueRequest { SecretId = secretName };
        var response = await _secretsManager.GetSecretValueAsync(request);
        return response.SecretString;
    }
}

// Services/S3Service.cs
using Amazon.S3;
using Amazon.S3.Model;

public class S3Service
{
    private readonly IAmazonS3 _s3Client;

    public S3Service()
    {
        // ✅ SDK usa automáticamente IAM Role del ECS Task
        _s3Client = new AmazonS3Client();
    }

    public async Task<string> UploadFileAsync(string key, Stream stream)
    {
        var request = new PutObjectRequest
        {
            BucketName = "talma-payments-prod",
            Key = key,
            InputStream = stream,
            ServerSideEncryptionMethod = ServerSideEncryptionMethod.AWSKMS
        };

        await _s3Client.PutObjectAsync(request);
        return $"s3://talma-payments-prod/{key}";
    }
}
```

### 7.3 Keycloak Service Accounts

```bash
# Crear service account para payment-api
kcadm.sh create clients -r talma-internal \
  -s clientId=payment-api-service \
  -s enabled=true \
  -s serviceAccountsEnabled=true \
  -s directAccessGrantsEnabled=false

# Asignar roles
kcadm.sh add-roles -r talma-internal \
  --uusername service-account-payment-api-service \
  --rolename payment:read \
  --rolename payment:write
```

```csharp
// Obtener token service account
public class KeycloakServiceClient
{
    private readonly HttpClient _httpClient;

    public async Task<string> GetServiceTokenAsync()
    {
        var clientId = "payment-api-service";
        var clientSecret = await _secretsService.GetSecretAsync("keycloak/payment-api-secret");

        var request = new Dictionary<string, string>
        {
            ["grant_type"] = "client_credentials",
            ["client_id"] = clientId,
            ["client_secret"] = clientSecret
        };

        var response = await _httpClient.PostAsync(
            "https://auth.talma.com:8443/realms/talma-internal/protocol/openid-connect/token",
            new FormUrlEncodedContent(request));

        var content = await response.Content.ReadFromJsonAsync<TokenResponse>();
        return content.AccessToken;
    }
}
```

## 8. Least Privilege — RBAC Granular

### 8.1 Roles Específicos (NO "admin" global)

```json
// Keycloak Realm Roles
{
  "roles": [
    {
      "name": "payment:read",
      "description": "Ver pagos (read-only)"
    },
    {
      "name": "payment:write",
      "description": "Crear/modificar pagos"
    },
    {
      "name": "payment:approve",
      "description": "Aprobar pagos >$10,000"
    },
    {
      "name": "order:read",
      "description": "Ver órdenes"
    },
    {
      "name": "order:write",
      "description": "Crear órdenes"
    },
    {
      "name": "report:financial",
      "description": "Acceso a reportes financieros"
    }
  ]
}
```

### 8.2 .NET — Claims-Based Authorization

```csharp
// Program.cs
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("CanCreatePayment", policy =>
        policy.RequireClaim("realm_access", "payment:write"));

    options.AddPolicy("CanApprovePayment", policy =>
        policy.RequireClaim("realm_access", "payment:approve"));

    options.AddPolicy("CanViewFinancialReports", policy =>
        policy.RequireClaim("realm_access", "report:financial"));

    options.AddPolicy("CanManageOrders", policy =>
        policy.RequireAssertion(context =>
            context.User.HasClaim("realm_access", "order:write") &&
            context.User.HasClaim("realm_access", "order:read")));
});

// Controller
[Authorize(Policy = "CanApprovePayment")]
[HttpPost("approve/{id}")]
public async Task<IActionResult> ApprovePayment(Guid id)
{
    // Solo usuarios con claim "payment:approve"
    await _paymentService.ApproveAsync(id);
    return Ok();
}
```

### 8.3 PostgreSQL — Row-Level Security

```sql
-- Crear usuario por aplicación (NO usar superuser)
CREATE USER payment_api WITH PASSWORD 'secret';
GRANT CONNECT ON DATABASE talma_db TO payment_api;
GRANT USAGE ON SCHEMA public TO payment_api;
GRANT SELECT, INSERT, UPDATE ON TABLE payments TO payment_api;

-- Row-level security para multi-tenancy
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON payments
  USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Application set tenant_id en cada request
-- SET LOCAL app.tenant_id = 'tenant-uuid';
```

```csharp
// .NET — Set tenant_id por request
public class TenantInterceptor : DbConnectionInterceptor
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public override async ValueTask<InterceptionResult> ConnectionOpeningAsync(
        DbConnection connection,
        ConnectionEventData eventData,
        InterceptionResult result,
        CancellationToken cancellationToken = default)
    {
        var tenantId = _httpContextAccessor.HttpContext?.User
            .FindFirst("tenant_id")?.Value;

        if (!string.IsNullOrEmpty(tenantId))
        {
            using var command = connection.CreateCommand();
            command.CommandText = $"SET LOCAL app.tenant_id = '{tenantId}'";
            await command.ExecuteNonQueryAsync(cancellationToken);
        }

        return result;
    }
}
```

## 9. Auditoría y Monitoreo

### 9.1 CloudTrail — Logs de IAM

```hcl
# terraform/cloudtrail.tf
resource "aws_cloudtrail" "main" {
  name                          = "cloudtrail-${var.environment}"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  enable_log_file_validation    = true
  is_multi_region_trail         = true
  include_global_service_events = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }
}

# Alertas de eventos críticos
resource "aws_cloudwatch_event_rule" "iam_changes" {
  name        = "iam-changes-${var.environment}"
  description = "Alert on IAM policy changes"

  event_pattern = jsonencode({
    source      = ["aws.iam"]
    detail-type = [
      "AWS API Call via CloudTrail"
    ]
    detail = {
      eventName = [
        "PutUserPolicy",
        "PutRolePolicy",
        "AttachUserPolicy",
        "AttachRolePolicy",
        "CreateAccessKey"
      ]
    }
  })
}
```

### 9.2 Keycloak — Event Logging

```bash
# Keycloak Admin Console
# Realm Settings → Events → Config
# - Save Events: ON
# - Event Listeners: + jboss-logging
# - Saved Types:
#   - LOGIN
#   - LOGIN_ERROR
#   - LOGOUT
#   - UPDATE_CREDENTIAL
#   - GRANT_CONSENT
#   - REVOKE_GRANT

# Logs exportados a Grafana Loki
```

```csharp
// appsettings.json — Serilog
{
  "Serilog": {
    "WriteTo": [
      {
        "Name": "GrafanaLoki",
        "Args": {
          "uri": "https://loki.talma.com",
          "labels": [
            { "key": "app", "value": "payment-api" },
            { "key": "event_type", "value": "authentication" }
          ]
        }
      }
    ]
  }
}
```

## 10. Revisión de Accesos

### 10.1 Auditoría Trimestral

```bash
# AWS IAM Access Analyzer
aws accessanalyzer create-analyzer \
  --analyzer-name unused-permissions-analyzer \
  --type ACCOUNT

# Generar reporte de permisos no usados (últimos 90 días)
aws accessanalyzer list-findings \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/unused-permissions-analyzer \
  --filter '{"status": {"eq": ["ACTIVE"]}}' \
  --max-results 100

# Keycloak — Usuarios sin actividad 90 días
kcadm.sh get users -r talma-internal \
  --fields id,username,createdTimestamp \
  | jq '.[] | select(.createdTimestamp < (now - 7776000) * 1000)'
```

### 10.2 Checklist de Revisión

- [ ] Revisar roles IAM no usados (CloudTrail logs)
- [ ] Eliminar usuarios Keycloak inactivos >90 días
- [ ] Validar permisos de service accounts
- [ ] Revisar políticas con wildcards (`*`)
- [ ] Verificar MFA habilitado en todos los admins
- [ ] Auditar cambios de roles en últimos 90 días
- [ ] Verificar rotation de secrets activa

## 11. Validación de Cumplimiento

### Checklist

- [ ] Keycloak configurado con realms separados
- [ ] JWT RS256 con tokens de 15 minutos
- [ ] MFA obligatorio en producción
- [ ] IAM Roles por servicio (NO shared roles)
- [ ] Policies IAM sin wildcards innecesarios
- [ ] Service accounts sin credentials hardcodeados
- [ ] PostgreSQL users dedicados por aplicación
- [ ] Row-level security habilitado
- [ ] CloudTrail activo con alertas
- [ ] Revisión trimestral de accesos programada

### Comandos de Validación

```bash
# Verificar token JWT
curl -H "Authorization: Bearer $TOKEN" https://api.talma.com/api/v1/payments

# Verificar claims en JWT
echo $TOKEN | jwt decode -

# Verificar IAM role en ECS task
aws ecs describe-task-definition --task-definition payment-api \
  | jq '.taskDefinition.taskRoleArn'

# Verificar permisos PostgreSQL
psql -U payment_api -c "\du payment_api"
psql -U payment_api -c "\dp payments"

# Verificar MFA en Keycloak
kcadm.sh get users/{user-id} -r talma-internal \
  | jq '.requiredActions'
```

## 12. Métricas de Cumplimiento

| Métrica                            | Target      | Verificación        |
| ---------------------------------- | ----------- | ------------------- |
| **MFA habilitado**                 | 100% admins | Keycloak reports    |
| **Service accounts con IAM Roles** | 100%        | CloudTrail          |
| **Tokens lifetime**                | ≤15 minutos | Keycloak config     |
| **Permisos revisados**             | Trimestral  | IAM Access Analyzer |
| **Usuarios inactivos removidos**   | <90 días    | Keycloak audit      |
| **Policies sin wildcards**         | >90%        | Terraform scan      |
| **Secrets rotados**                | <90 días    | Secrets Manager     |

## 13. Prohibiciones

- ❌ IAM Users para servicios (usar IAM Roles)
- ❌ Credentials hardcodeados en código/env vars
- ❌ Roles compartidos entre servicios
- ❌ Wildcards `*` en IAM policies sin justificación
- ❌ Tokens lifetime >30 minutos
- ❌ Usuarios con acceso a producción sin MFA
- ❌ Superuser PostgreSQL en aplicaciones
- ❌ Roles "admin" globales (usar roles granulares)
- ❌ SMS como MFA (usar TOTP/WebAuthn)

## 14. Referencias

**Keycloak:**

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OpenID Connect 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [OAuth 2.0](https://oauth.net/2/)

**AWS:**

- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [IAM Roles for Tasks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)

**Standards:**

- [NIST SP 800-63B - Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
