---
id: iam-advanced
sidebar_position: 4
title: Gestión Avanzada de Identidades y Accesos
description: Estándares para ABAC, federación de identidades, ciclo de vida, JIT access, cuentas de servicio, revisiones de acceso y políticas de contraseñas
tags:
  [
    seguridad,
    abac,
    identity-federation,
    jit-access,
    service-accounts,
    keycloak,
    aws-secrets-manager,
  ]
---

# Gestión Avanzada de Identidades y Accesos

## Contexto

Este estándar consolida **8 conceptos relacionados** con gestión avanzada de identidades, acceso contextual y ciclo de vida. Complementa los patrones base de SSO/MFA/RBAC con capacidades de autorización granular y gobernanza de identidades.

**Conceptos incluidos:**

- **Attribute-Based Access Control (ABAC)** → Permisos basados en atributos contextuales (tenant, horario, clasificación)
- **Identity Federation** → Confianza entre múltiples proveedores de identidad (IdP)
- **Identity Lifecycle** → Gestión de ciclo de vida (provisioning, modificación, deprovisioning)
- **Just-in-Time (JIT) Access** → Acceso temporal elevado solo cuando se necesita
- **Service Accounts** → Cuentas para servicios/aplicaciones no humanos
- **Service Identity** → Identidad de servicios con mTLS y certificados X.509
- **Access Reviews** → Revisión periódica de permisos asignados
- **Password Policies** → Políticas de contraseñas robustas

---

## Stack Tecnológico

| Componente            | Tecnología          | Versión | Uso                         |
| --------------------- | ------------------- | ------- | --------------------------- |
| **Identity Provider** | Keycloak            | 23.0+   | Federación, lifecycle, ABAC |
| **Runtime**           | .NET                | 8.0+    | Aplicaciones                |
| **Service Mesh**      | AWS App Mesh        | Latest  | Service identity & mTLS     |
| **Secrets**           | AWS Secrets Manager | Latest  | Service account credentials |

---

## Control de Acceso Basado en Atributos (ABAC)

### ¿Qué es ABAC?

Modelo de control de acceso donde las decisiones se basan en atributos del sujeto, recurso, acción y contexto. Más flexible que RBAC.

**Estructura:**

- **Subject attributes**: user_id, department, clearance_level
- **Resource attributes**: owner_id, classification, tenant_id
- **Action**: read, write, delete
- **Environment**: time, location, IP address

**Ejemplo de política:**

- _"Permitir si (user.department == 'Finance' AND resource.classification == 'public' AND environment.time >= 08:00 AND environment.time `<= 18:00`)"_

**Beneficios:**
✅ Control de acceso muy granular
✅ Políticas dinámicas basadas en contexto
✅ Soporta multi-tenancy fácilmente
✅ Compliance con regulaciones complejas

### Implementación: ABAC Policy Engine

```csharp
// src/Shared/Authorization/AbacPolicyEngine.cs
public class AbacPolicyEngine
{
    public async Task<bool> EvaluateAsync(
        AccessRequest request,
        ClaimsPrincipal principal,
        HttpContext httpContext)
    {
        var subject = ExtractSubjectAttributes(principal);
        var resource = await ExtractResourceAttributesAsync(request.ResourceId);
        var environment = ExtractEnvironmentAttributes(httpContext);

        var policies = GetApplicablePolicies(request.Action, resource.Type);

        foreach (var policy in policies.OrderBy(p => p.Priority))
        {
            var result = policy.Evaluate(subject, resource, environment);

            if (result == PolicyDecision.Deny)
                return false;

            if (result == PolicyDecision.Allow)
                return true;
        }

        return false; // Deny por defecto
    }

    private SubjectAttributes ExtractSubjectAttributes(ClaimsPrincipal principal)
    {
        return new SubjectAttributes
        {
            UserId = principal.FindFirst("sub")?.Value,
            TenantId = principal.FindFirst("tenant_id")?.Value,
            Department = principal.FindFirst("department")?.Value,
            ClearanceLevel = int.Parse(principal.FindFirst("clearance_level")?.Value ?? "0"),
            Roles = principal.FindAll("realm_access.roles").Select(c => c.Value).ToList()
        };
    }

    private EnvironmentAttributes ExtractEnvironmentAttributes(HttpContext httpContext)
    {
        return new EnvironmentAttributes
        {
            Timestamp = DateTime.UtcNow,
            Hour = DateTime.UtcNow.Hour,
            DayOfWeek = DateTime.UtcNow.DayOfWeek,
            IpAddress = httpContext.Connection.RemoteIpAddress?.ToString()
        };
    }
}

// Policy: Aislamiento por tenant (multi-tenancy)
public class TenantIsolationPolicy : IAbacPolicy
{
    public int Priority => 100;

    public PolicyDecision Evaluate(
        SubjectAttributes subject,
        ResourceAttributes resource,
        EnvironmentAttributes environment)
    {
        if (subject.TenantId != resource.TenantId)
            return PolicyDecision.Deny;

        return PolicyDecision.NotApplicable;
    }
}

// Policy: Horario laboral para datos confidenciales
public class BusinessHoursPolicy : IAbacPolicy
{
    public int Priority => 30;

    public PolicyDecision Evaluate(
        SubjectAttributes subject,
        ResourceAttributes resource,
        EnvironmentAttributes environment)
    {
        if (resource.Classification == "confidential")
        {
            var isBusinessHours = environment.Hour >= 8 && environment.Hour <= 18 &&
                                  environment.DayOfWeek != DayOfWeek.Saturday &&
                                  environment.DayOfWeek != DayOfWeek.Sunday;

            if (!isBusinessHours)
                return PolicyDecision.Deny;
        }

        return PolicyDecision.NotApplicable;
    }
}

// Uso en Controller
[HttpGet("{id}")]
public async Task<IActionResult> GetOrder(string id)
{
    var hasAccess = await _abacEngine.EvaluateAsync(
        new AccessRequest { ResourceId = id, Action = "read" },
        User, HttpContext);

    if (!hasAccess)
        return Forbid();

    return Ok(await _orderService.GetByIdAsync(id));
}
```

---

## Federación de Identidades

### ¿Qué es Identity Federation?

Confianza entre múltiples proveedores de identidad (IdP) permitiendo que usuarios autenticados en un IdP accedan a recursos de otros sin re-autenticarse.

**Propósito:** Permitir SSO entre organizaciones, soportar login social (Google, Microsoft).

**Protocolos:**

- **SAML 2.0**: Enterprise federation
- **OpenID Connect**: Modern web/mobile apps
- **WS-Federation**: Legacy Microsoft

**Beneficios:**
✅ B2B collaboration sin gestionar credenciales externas
✅ Social login para clientes
✅ Reducción de surface de ataque (no almacenar passwords externos)

### Configuración: Keycloak Identity Broker

```yaml
# Keycloak: Configurar Google como Identity Provider
{
  "alias": "google",
  "providerId": "google",
  "enabled": true,
  "config":
    {
      "clientId": "your-google-client-id.apps.googleusercontent.com",
      "clientSecret": "your-google-client-secret",
      "defaultScope": "openid profile email",
      "hosteddomain": "talma.pe",
    },
  "trustEmail": true,
}
```

```csharp
// .NET: Soportar múltiples IdPs a través de Keycloak broker
builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = "Cookies";
    options.DefaultChallengeScheme = "oidc";
})
.AddCookie("Cookies")
.AddOpenIdConnect("oidc", options =>
{
    options.Authority = "https://keycloak.talma.local/realms/talma";
    options.ClientId = "web-app";
    options.ClientSecret = "secret";
    options.ResponseType = "code";

    options.Scope.Add("openid");
    options.Scope.Add("profile");
    options.Scope.Add("email");

    options.TokenValidationParameters.NameClaimType = "preferred_username";
    options.TokenValidationParameters.RoleClaimType = "realm_access.roles";
});
```

---

## Ciclo de Vida de Identidades

### ¿Qué es Identity Lifecycle?

Gestión completa del ciclo de vida de identidades: provisioning (creación), modificación, deprovisioning (eliminación).

**Fases:**

1. **Provisioning**: Onboarding de nuevos usuarios/servicios
2. **Modification**: Cambios de roles, permisos, atributos
3. **Deprovisioning**: Offboarding, revocación de accesos

**Propósito:** Garantizar que solo identidades activas y válidas tengan acceso.

**Beneficios:**
✅ Reducción de cuentas huérfanas
✅ Compliance con SOX, GDPR
✅ Automatización de onboarding/offboarding

### Implementación: Provisioning Automatizado

```csharp
// src/Shared/Identity/UserProvisioningService.cs
public class UserProvisioningService
{
    public async Task<UserProvisioningResult> ProvisionUserAsync(NewUserRequest request)
    {
        // 1. Crear usuario en Keycloak
        var userId = await _keycloak.CreateUserAsync(new KeycloakUser
        {
            Username = request.Email,
            Email = request.Email,
            FirstName = request.FirstName,
            LastName = request.LastName,
            Enabled = true,
            EmailVerified = false,
            Attributes = new Dictionary<string, string>
            {
                { "department", request.Department },
                { "employee_id", request.EmployeeId },
                { "tenant_id", request.TenantId },
                { "hire_date", DateTime.UtcNow.ToString("O") }
            }
        });

        // 2. Asignar roles por defecto según departamento
        var defaultRoles = GetDefaultRolesForDepartment(request.Department);
        await _keycloak.AssignRolesToUserAsync(userId, defaultRoles);

        // 3. Forzar cambio de password y configuración de MFA
        await _keycloak.SetRequiredActionsAsync(userId, new[]
        {
            "UPDATE_PASSWORD",
            "CONFIGURE_TOTP",
            "VERIFY_EMAIL"
        });

        // 4. Enviar email de bienvenida
        await _emailService.SendWelcomeEmailAsync(request.Email, userId);

        // 5. Auditar provisioning
        await _auditLog.LogAsync(new AuditEvent
        {
            Action = "USER_PROVISIONED",
            UserId = userId,
            Details = $"User {request.Email} provisioned with roles: {string.Join(", ", defaultRoles)}"
        });

        return new UserProvisioningResult { UserId = userId, Success = true };
    }

    public async Task DeprovisionUserAsync(string userId, string reason)
    {
        // 1. Deshabilitar usuario (preservar para auditoría)
        await _keycloak.DisableUserAsync(userId);

        // 2. Revocar tokens activos
        await _keycloak.LogoutUserAsync(userId);

        // 3. Remover todos los roles
        var userRoles = await _keycloak.GetUserRolesAsync(userId);
        await _keycloak.RemoveRolesFromUserAsync(userId, userRoles);

        // 4. Marcar deprovisioning
        await _keycloak.UpdateUserAttributesAsync(userId, new Dictionary<string, string>
        {
            { "deprovisioned_at", DateTime.UtcNow.ToString("O") },
            { "deprovisioning_reason", reason }
        });

        await _auditLog.LogAsync(new AuditEvent
        {
            Action = "USER_DEPROVISIONED",
            UserId = userId,
            Details = $"Reason: {reason}"
        });
    }
}
```

---

## Acceso Just-in-Time (JIT)

### ¿Qué es JIT Access?

Acceso temporal elevado otorgado solo cuando se necesita, por tiempo limitado, con aprobación y auditoría.

**Propósito:** Minimizar privilegios permanentes, reducir surface de ataque.

**Características:**

- **Time-bound**: Expira automáticamente (máx. 8 horas)
- **Approval workflow**: Requiere aprobación de manager/security
- **Justification**: Usuario debe justificar por qué necesita acceso
- **Audit trail**: Registro completo de uso

**Beneficios:**
✅ Least privilege dinámico
✅ Reducción de cuentas privilegiadas permanentes
✅ Compliance con SOX, PCI-DSS

### Implementación: JIT Elevation Service

```csharp
// src/Shared/Security/JitAccessService.cs
public class JitAccessService
{
    public async Task<JitAccessRequest> RequestElevatedAccessAsync(
        string userId,
        string[] requestedRoles,
        string justification,
        TimeSpan duration)
    {
        if (duration > TimeSpan.FromHours(8))
            throw new InvalidOperationException("Max JIT access duration is 8 hours");

        var request = new JitAccessRequest
        {
            Id = Guid.NewGuid().ToString(),
            UserId = userId,
            RequestedRoles = requestedRoles,
            Justification = justification,
            RequestedDuration = duration,
            Status = JitAccessStatus.PendingApproval,
            RequestedAt = DateTime.UtcNow,
            ExpiresAt = DateTime.UtcNow.Add(duration)
        };

        await _approvalWorkflow.SubmitForApprovalAsync(request);

        await _auditLog.LogAsync(new AuditEvent
        {
            Action = "JIT_ACCESS_REQUESTED",
            UserId = userId,
            Details = $"Roles: {string.Join(", ", requestedRoles)}, Justification: {justification}"
        });

        return request;
    }

    public async Task ApproveJitAccessAsync(string requestId, string approverId)
    {
        var request = await _approvalWorkflow.GetRequestAsync(requestId);

        await _keycloak.AssignRolesToUserAsync(request.UserId, request.RequestedRoles);

        request.Status = JitAccessStatus.Approved;
        request.ApprovedBy = approverId;
        await _approvalWorkflow.UpdateRequestAsync(request);

        // Programar revocación automática al expirar
        BackgroundJob.Schedule(
            () => RevokeJitAccessAsync(request.Id),
            request.ExpiresAt);

        await _auditLog.LogAsync(new AuditEvent
        {
            Action = "JIT_ACCESS_APPROVED",
            UserId = request.UserId,
            PerformedBy = approverId,
            Details = $"Roles: {string.Join(", ", request.RequestedRoles)}, Expires: {request.ExpiresAt}"
        });
    }

    public async Task RevokeJitAccessAsync(string requestId)
    {
        var request = await _approvalWorkflow.GetRequestAsync(requestId);

        await _keycloak.RemoveRolesFromUserAsync(request.UserId, request.RequestedRoles);
        await _keycloak.LogoutUserAsync(request.UserId);

        request.Status = JitAccessStatus.Revoked;
        request.RevokedAt = DateTime.UtcNow;
        await _approvalWorkflow.UpdateRequestAsync(request);

        await _auditLog.LogAsync(new AuditEvent
        {
            Action = "JIT_ACCESS_REVOKED",
            UserId = request.UserId,
            Details = $"Roles removed: {string.Join(", ", request.RequestedRoles)}"
        });
    }
}
```

---

## Cuentas de Servicio

### ¿Qué son Service Accounts?

Cuentas de identidad para servicios/aplicaciones (no humanos) que necesitan autenticarse y acceder a recursos.

**Propósito:** Autenticación service-to-service sin usar credenciales de usuario.

**Características:**

- **No interactive login**: No pueden hacer login web
- **Long-lived credentials**: Certificados, client secrets
- **Limited permissions**: Least privilege estricto
- **Auditable**: Rastrear acciones del servicio

**Beneficios:**
✅ Separación de identidades humanas vs servicios
✅ Rotación de credenciales automatizada
✅ Prevención de uso indebido de cuentas personales

### Implementación: Client Credentials Flow

```csharp
// src/PaymentService/Services/OrderServiceClient.cs
public class OrderServiceClient
{
    public async Task<Order> GetOrderAsync(string orderId)
    {
        var token = await GetServiceAccessTokenAsync();

        _httpClient.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", token);

        var response = await _httpClient.GetAsync($"/api/orders/{orderId}");
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Order>();
    }

    private async Task<string> GetServiceAccessTokenAsync()
    {
        const string cacheKey = "service_account_token";

        if (_cache.TryGetValue(cacheKey, out string cachedToken))
            return cachedToken;

        // OAuth 2.0 Client Credentials Flow
        var tokenEndpoint = $"{_configuration["Keycloak:Authority"]}/protocol/openid-connect/token";

        var request = new HttpRequestMessage(HttpMethod.Post, tokenEndpoint)
        {
            Content = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                { "grant_type", "client_credentials" },
                { "client_id", "payment-service" },
                { "client_secret", await GetClientSecretAsync() },
                { "scope", "orders:read payments:write" }
            })
        };

        using var client = new HttpClient();
        var response = await client.SendAsync(request);
        var tokenResponse = await response.Content.ReadFromJsonAsync<TokenResponse>();

        var cacheExpiration = TimeSpan.FromSeconds(tokenResponse.ExpiresIn * 0.9);
        _cache.Set(cacheKey, tokenResponse.AccessToken, cacheExpiration);

        return tokenResponse.AccessToken;
    }

    private async Task<string> GetClientSecretAsync()
    {
        // Obtener desde AWS Secrets Manager
        return await _secretsManager.GetSecretAsync("keycloak/payment-service/client-secret");
    }
}
```

### Configuración Keycloak: Service Account Client

```json
{
  "clientId": "payment-service",
  "enabled": true,
  "protocol": "openid-connect",
  "publicClient": false,
  "serviceAccountsEnabled": true,
  "standardFlowEnabled": false,
  "directAccessGrantsEnabled": false,
  "clientAuthenticatorType": "client-secret"
}
```

---

## Identidad de Servicios, Revisiones y Políticas de Contraseñas

### Identidad de Servicios (Service Identity)

- Identidad basada en mTLS con certificados X.509
- Cada servicio tiene certificado único
- Ver [Zero Trust Networking](./zero-trust-networking.md) para detalles de mTLS

### Revisiones de Acceso

Revisión trimestral obligatoria de permisos asignados.

```csharp
// Background job para detectar accesos sin uso (> 90 días)
public class UnusedAccessDetector : IHostedService
{
    public async Task DetectUnusedAccessAsync()
    {
        var users = await _keycloak.GetAllUsersAsync();
        var unusedAccess = new List<UnusedAccessReport>();

        foreach (var user in users)
        {
            var lastLogin = await _auditLog.GetLastLoginAsync(user.Id);

            if (lastLogin < DateTime.UtcNow.AddDays(-90))
            {
                var roles = await _keycloak.GetUserRolesAsync(user.Id);
                unusedAccess.Add(new UnusedAccessReport
                {
                    UserId = user.Id,
                    Email = user.Email,
                    LastLogin = lastLogin,
                    Roles = roles
                });
            }
        }

        await _emailService.SendAccessReviewReportAsync(unusedAccess);
    }
}
```

### Políticas de Contraseñas

```json
// Keycloak Password Policy
{
  "passwordPolicy": "length(12) and upperCase(1) and lowerCase(1) and digits(1) and specialChars(1) and notUsername(undefined) and passwordHistory(5) and forceExpiredPasswordChange(90)"
}
```

**Reglas:**

- Mínimo 12 caracteres
- Complejidad: mayúsculas, minúsculas, números, símbolos
- No reusar últimas 5 contraseñas
- Expiración cada 90 días
- Forzar cambio en primer login

---

## Monitoreo y Observabilidad

```promql
# Solicitudes JIT pendientes
sum(jit_access_requests{status="pending"})

# Cuentas inactivas detectadas
sum(inactive_accounts_total)

# Service account token failures
sum(rate(service_account_token_failures_total[5m]))
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar ABAC para multi-tenancy (aislar datos por tenant)
- **MUST** usar service accounts para comunicación service-to-service
- **MUST** almacenar client secrets en AWS Secrets Manager
- **MUST** rotar secrets de service accounts cada 90 días
- **MUST** realizar access review trimestral
- **MUST** deshabilitar cuentas inactivas > 90 días

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar JIT access para operaciones administrativas
- **SHOULD** usar identity federation para clientes (Google, Microsoft social login)
- **SHOULD** automatizar provisioning/deprovisioning con SCIM
- **SHOULD** usar mTLS para service identity

### MAY (Opcional)

- **MAY** implementar risk-based authentication
- **MAY** soportar FIDO2/WebAuthn para autenticación sin password

### MUST NOT (Prohibido)

- **MUST NOT** otorgar permisos de admin permanentemente sin justificación
- **MUST NOT** usar cuentas compartidas entre servicios
- **MUST NOT** hardcodear client secrets en código

---

## Referencias

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth 2.0 Client Credentials](https://oauth.net/2/grant-types/client-credentials/)
- [ABAC — NIST](https://nvlpubs.nist.gov/nistpubs/specialpublications/NIST.SP.800-162.pdf)
- [SSO, MFA y RBAC](./sso-mfa-rbac.md)
- [Zero Trust Networking](./zero-trust-networking.md)
- [Security Governance](./security-governance.md)
