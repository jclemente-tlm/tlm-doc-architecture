---
id: zero-trust-verification
sidebar_position: 2
title: Verificación Explícita, Assume Breach y Trust Boundaries
description: Estándares para verificación continua de contexto, diseño asumiendo compromiso y gestión de límites de confianza entre servicios
tags:
  [
    seguridad,
    zero-trust,
    verificacion-explicita,
    assume-breach,
    trust-boundaries,
    dotnet,
  ]
---

# Verificación Explícita, Assume Breach y Trust Boundaries

## Contexto

Este estándar consolida **3 conceptos relacionados** con la verificación activa y el diseño defensivo en arquitecturas Zero Trust. Complementa los fundamentos de red de [Zero Trust Networking y mTLS](./zero-trust-networking.md).

**Conceptos incluidos:**

- **Explicit Verification** → Verificar siempre, nunca asumir. Validar identidad, dispositivo y contexto en cada acceso
- **Assume Breach** → Diseñar asumiendo que el sistema ya ha sido comprometido. Minimizar radio de impacto y detectar movimiento lateral
- **Trust Boundaries** → Definir explícitamente los límites de confianza entre componentes. Validar en cada cruce de boundary

---

## Stack Tecnológico

| Componente         | Tecnología       | Versión | Uso                                    |
| ------------------ | ---------------- | ------- | -------------------------------------- |
| **Runtime**        | .NET             | 8.0+    | Aplicaciones y middleware              |
| **Validation**     | FluentValidation | 11.0+   | Validación en trust boundaries         |
| **API Gateway**    | Kong             | 3.5+    | Policies y rate limiting               |
| **Infrastructure** | AWS VPC          | Latest  | Segmentación de red por trust level    |
| **IaC**            | Terraform        | 1.6+    | Network trust boundaries automatizados |

---

## Verificación Explícita

### ¿Qué es la Verificación Explícita?

Principio Zero Trust que requiere verificar siempre todos los factores disponibles: identidad, ubicación, dispositivo, servicio, carga de trabajo, datos y anomalías.

**Propósito:** Nunca asumir que un usuario o servicio es confiable, incluso si ya fue autenticado.

**Factores de verificación:**

- **Identidad**: ¿Quién es el usuario? (autenticación + MFA)
- **Dispositivo**: ¿Es un dispositivo conocido y saludable?
- **Ubicación**: ¿Desde dónde accede? (geolocalización, hora)
- **Servicio**: ¿Qué servicio hace el request? (mutual auth)
- **Datos**: ¿A qué datos accede y por qué?
- **Anomalías**: ¿El comportamiento es normal?

**Beneficios:**
✅ Detecta accesos anómalos aunque se tengan credenciales válidas
✅ Contexto completo para mejor toma de decisiones
✅ Protege contra robo de credenciales

### Implementación: Motor de Políticas de Acceso

```csharp
// src/Shared/Security/AccessPolicyEngine.cs
public class AccessPolicyEngine
{
    private readonly IGeoLocationService _geoLocation;
    private readonly IDeviceRegistrationService _deviceRegistry;

    public async Task<AccessDecision> EvaluateAsync(
        ClaimsPrincipal principal,
        string resource,
        string action,
        HttpContext context)
    {
        var verificationContext = await BuildVerificationContextAsync(principal, context);

        // Policy 1: Verificación de identidad
        if (!verificationContext.IsAuthenticated)
            return AccessDecision.Deny("Not authenticated");

        // Policy 2: MFA requerido para recursos sensibles
        if (IsSensitiveResource(resource) && !verificationContext.MfaVerified)
            return AccessDecision.Deny("MFA required for sensitive resources");

        // Policy 3: Política de ubicación
        var locationDecision = await _locationPolicy.EvaluateAsync(verificationContext);
        if (!locationDecision.Allowed)
            return AccessDecision.Deny($"Location policy: {locationDecision.Reason}");

        // Policy 4: Política de tiempo de acceso
        var timeDecision = _timePolicy.Evaluate(verificationContext);
        if (!timeDecision.Allowed)
            return AccessDecision.Deny($"Time policy: {timeDecision.Reason}");

        // Policy 5: Risk score
        if (verificationContext.RiskScore > 0.7)
            return AccessDecision.Challenge("High risk score - step-up auth required");

        return AccessDecision.Allow();
    }

    private async Task<VerificationContext> BuildVerificationContextAsync(
        ClaimsPrincipal principal,
        HttpContext context)
    {
        var userId = principal?.FindFirst("sub")?.Value;
        var geoData = await _geoLocation.GetAsync(context.Connection.RemoteIpAddress);

        return new VerificationContext
        {
            UserId = userId,
            IsAuthenticated = principal?.Identity?.IsAuthenticated ?? false,
            MfaVerified = principal?.FindFirst("amr")?.Value?.Contains("mfa") ?? false,
            GeoLocation = geoData,
            Timestamp = DateTime.UtcNow,
            RiskScore = await CalculateRiskScoreAsync(userId, geoData, context)
        };
    }
}

public class LocationPolicy
{
    public async Task<PolicyDecision> EvaluateAsync(VerificationContext context)
    {
        var allowedCountries = new[] { "PE", "CL", "CO", "US" };

        if (context.GeoLocation?.CountryCode != null &&
            !allowedCountries.Contains(context.GeoLocation.CountryCode))
        {
            return PolicyDecision.Deny(
                $"Country '{context.GeoLocation.CountryCode}' not in allowed list");
        }

        return PolicyDecision.Allow();
    }
}

public class TimePolicy
{
    public PolicyDecision Evaluate(VerificationContext context)
    {
        var hour = context.Timestamp.Hour;

        if (context.Resource.StartsWith("/api/admin") && (hour < 8 || hour > 18))
        {
            return PolicyDecision.Deny("Admin access restricted to business hours (8-18 UTC)");
        }

        return PolicyDecision.Allow();
    }
}
```

### Permisos Basados en Claims

```csharp
// src/Shared/Security/PermissionHandler.cs
public class PermissionRequirement : IAuthorizationRequirement
{
    public string Permission { get; }
    public PermissionRequirement(string permission) => Permission = permission;
}

public class PermissionHandler : AuthorizationHandler<PermissionRequirement>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        PermissionRequirement requirement)
    {
        var permissions = context.User
            .FindFirst("permissions")?.Value?.Split(',') ?? [];

        if (permissions.Contains(requirement.Permission))
            context.Succeed(requirement);
        else
        {
            _logger.LogWarning(
                "Permission denied: User {UserId} lacks {Permission}",
                context.User.FindFirst("sub")?.Value,
                requirement.Permission);
        }

        return Task.CompletedTask;
    }
}
```

---

## Diseño Assume Breach

### ¿Qué es Assume Breach?

Principio de diseño que asume el sistema ya ha sido comprometido y diseña para minimizar el radio de impacto, detectar violaciones rápidamente y facilitar la recuperación.

**Propósito:** Reducir el tiempo de respuesta ante incidentes y minimizar el impacto de una breach.

**Estrategias:**

- **Segmentación**: Dividir en zonas para limitar movimiento lateral
- **Least Privilege**: Solo los permisos mínimos necesarios
- **Logging completo**: Registrar todo para forensics
- **Detección de anomalías**: Alertas en tiempo real
- **Incident response**: Playbooks de respuesta predefinidos

**Beneficios:**
✅ Limita el radio de impacto de una comprensión
✅ Detecta movimiento lateral rápidamente
✅ Facilita forensics post-incident
✅ Mejora el tiempo de respuesta

### Detección de Movimiento Lateral

```csharp
// src/Shared/Security/LateralMovementDetector.cs
public class LateralMovementDetector
{
    private readonly IDistributedCache _cache;

    public async Task<LateralMovementRisk> AnalyzeAsync(
        string userId,
        string sourceService,
        string targetService,
        string action)
    {
        var patterns = await GetAccessPatternsAsync(userId);
        var risk = CalculateRisk(patterns, sourceService, targetService, action);

        if (risk.Score > 0.8)
        {
            await _alerting.SendAsync(new SecurityAlert
            {
                Type = "LateralMovementDetected",
                UserId = userId,
                SourceService = sourceService,
                TargetService = targetService,
                RiskScore = risk.Score,
                Timestamp = DateTime.UtcNow
            });
        }

        await RecordAccessPatternAsync(userId, sourceService, targetService, action);
        return risk;
    }

    private LateralMovementRisk CalculateRisk(
        IEnumerable<AccessPattern> patterns,
        string sourceService,
        string targetService,
        string action)
    {
        var riskFactors = new List<string>();
        double score = 0;

        // ¿Es una ruta nueva? (+0.3)
        var isNewPath = !patterns.Any(p =>
            p.SourceService == sourceService &&
            p.TargetService == targetService);
        if (isNewPath)
        {
            riskFactors.Add("New access path");
            score += 0.3;
        }

        // ¿Acceso en horas no habituales? (+0.2)
        var hour = DateTime.UtcNow.Hour;
        if (hour < 7 || hour > 20)
        {
            riskFactors.Add("Off-hours access");
            score += 0.2;
        }

        // ¿Muchos servicios distintos en poco tiempo? (+0.5)
        var recentUnique = patterns
            .Where(p => p.Timestamp > DateTime.UtcNow.AddMinutes(-5))
            .Select(p => p.TargetService)
            .Distinct()
            .Count();
        if (recentUnique > 5)
        {
            riskFactors.Add("Multiple services in short period");
            score += 0.5;
        }

        return new LateralMovementRisk { Score = score, Factors = riskFactors };
    }
}
```

---

## Límites de Confianza (Trust Boundaries)

### ¿Qué son los Trust Boundaries?

Fronteras entre componentes o sistemas con diferentes niveles de confianza. Todo dato o petición que cruce un trust boundary DEBE ser validado.

**Propósito:** Prevenir que datos maliciosos o no validados pasen de una zona de baja confianza a una de alta confianza.

**Tipos de boundaries:**

- **Red**: DMZ ↔ Red interna ↔ Red de datos
- **Servicio**: API públicas ↔ Servicios internos ↔ Base de datos
- **Proceso**: Web tier ↔ Business tier ↔ Data tier
- **Tenant**: Aislamiento multi-tenant

**Acciones en cada boundary:**

1. **Validar**: Verificar formato y contenido de los datos
2. **Sanitizar**: Eliminar caracteres peligrosos
3. **Autorizar**: Verificar permisos para cruzar el boundary
4. **Auditar**: Registrar el cruce del boundary

### Validación en Boundaries con FluentValidation

```csharp
// src/OrderService.Application/Validators/CreateOrderValidator.cs
public class CreateOrderValidator : AbstractValidator<CreateOrderCommand>
{
    public CreateOrderValidator()
    {
        // Validar en el boundary: datos externos → servicio interno
        RuleFor(x => x.CustomerId)
            .NotEmpty()
            .Matches(@"^[a-zA-Z0-9\-]{1,50}$")
            .WithMessage("CustomerId must be alphanumeric, max 50 chars");

        RuleFor(x => x.ProductIds)
            .NotEmpty()
            .Must(ids => ids.All(id => Guid.TryParse(id, out _)))
            .WithMessage("All ProductIds must be valid GUIDs");

        RuleFor(x => x.TotalAmount)
            .GreaterThan(0)
            .LessThanOrEqualTo(1_000_000)
            .WithMessage("TotalAmount must be between 0.01 and 1,000,000");

        // Sanitización activa
        RuleFor(x => x.Notes)
            .MaximumLength(500)
            .Must(notes => !ContainsDangerousContent(notes))
            .WithMessage("Notes contain invalid content");
    }

    private bool ContainsDangerousContent(string? input)
    {
        if (string.IsNullOrEmpty(input))
            return false;

        var dangerousPatterns = new[] { "<script", "javascript:", "DROP TABLE", "--" };
        return dangerousPatterns.Any(p =>
            input.Contains(p, StringComparison.OrdinalIgnoreCase));
    }
}
```

### Middleware de Validación en Boundary

```csharp
// src/Shared/Security/InputValidationMiddleware.cs
public class InputValidationMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        // Validar en boundary: Internet → API Gateway → Servicio
        if (context.Request.ContentType?.Contains("application/json") == true)
        {
            context.Request.EnableBuffering();
            var body = await new StreamReader(context.Request.Body).ReadToEndAsync();
            context.Request.Body.Position = 0;

            if (body.Length > MaxBodySize)
            {
                context.Response.StatusCode = StatusCodes.Status413PayloadTooLarge;
                return;
            }

            if (ContainsDangerousContent(body))
            {
                _logger.LogWarning(
                    "Dangerous content detected from IP {IpAddress}",
                    context.Connection.RemoteIpAddress);
                context.Response.StatusCode = StatusCodes.Status400BadRequest;
                return;
            }
        }

        await _next(context);
    }
}
```

### Trust Boundaries de Red en Terraform

```hcl
# terraform/modules/trust-boundaries/main.tf
resource "aws_security_group" "public_tier" {
  name   = "public-tier"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from Internet — boundary: Internet → DMZ"
  }

  egress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.private_tier.id]
    description     = "Allow to private tier only — boundary: DMZ → Private"
  }
}

resource "aws_security_group" "private_tier" {
  name   = "private-tier"
  vpc_id = var.vpc_id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.public_tier.id]
    description     = "From DMZ only — trust boundary enforcement"
  }

  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.data_tier.id]
    description     = "DB access — boundary: Private → Data"
  }
}
```

---

## Monitoreo y Observabilidad

```csharp
// src/Shared/Observability/ZeroTrustMetrics.cs
public class ZeroTrustMetrics
{
    private readonly Counter<long> _accessDeniedCounter;
    private readonly Counter<long> _lateralMovementAlertsCounter;
    private readonly Histogram<double> _accessDecisionDuration;
    private readonly Counter<long> _trustBoundaryViolationsCounter;

    public ZeroTrustMetrics(IMeterFactory meterFactory)
    {
        var meter = meterFactory.Create("ZeroTrust.Security");

        _accessDeniedCounter = meter.CreateCounter<long>(
            "zero_trust_access_denied_total",
            description: "Total access denied by policy engine");

        _lateralMovementAlertsCounter = meter.CreateCounter<long>(
            "zero_trust_lateral_movement_alerts_total",
            description: "Total lateral movement alerts");

        _accessDecisionDuration = meter.CreateHistogram<double>(
            "zero_trust_access_decision_duration_seconds",
            description: "Time to evaluate access decision");

        _trustBoundaryViolationsCounter = meter.CreateCounter<long>(
            "zero_trust_trust_boundary_violations_total",
            description: "Total trust boundary violations detected");
    }

    public void RecordAccessDenied(string policy, string reason) =>
        _accessDeniedCounter.Add(1, new("policy", policy), new("reason", reason));

    public void RecordLateralMovementAlert(string userId, double riskScore) =>
        _lateralMovementAlertsCounter.Add(1,
            new("user_id", userId),
            new("risk_level", riskScore > 0.9 ? "critical" : "high"));

    public IDisposable MeasureAccessDecision() =>
        new DurationTracker(_accessDecisionDuration);

    public void RecordTrustBoundaryViolation(string boundary, string type) =>
        _trustBoundaryViolationsCounter.Add(1,
            new("boundary", boundary),
            new("violation_type", type));
}
```

```promql
# Accesos denegados por política en los últimos 5 minutos
sum by (policy, reason) (rate(zero_trust_access_denied_total[5m])) > 10

# Alertas de movimiento lateral (siempre crítico)
sum(increase(zero_trust_lateral_movement_alerts_total[5m])) > 0

# Violaciones de trust boundaries
sum by (boundary) (rate(zero_trust_trust_boundary_violations_total[5m])) > 0

# Tiempo de evaluación de acceso elevado (> 500ms)
histogram_quantile(0.95, rate(zero_trust_access_decision_duration_seconds_bucket[5m])) > 0.5
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** verificar identidad, dispositivo y contexto en cada acceso (location + time)
- **MUST** implementar MFA para acceso a recursos sensibles
- **MUST** registrar todos los accesos con contexto completo para auditoría forense
- **MUST** segmentar servicios para minimizar radio de impacto ante compromiso
- **MUST** implementar least privilege en todos los roles y permisos
- **MUST** definir trust boundaries explícitos entre todos los componentes
- **MUST** validar todos los datos en cada cruce de trust boundary
- **MUST** sanitizar inputs en el boundary con data no confiable

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar detección de movimiento lateral
- **SHOULD** calcular risk score per-request para anomalías
- **SHOULD** usar circuit breakers en límites de servicio
- **SHOULD** implementar canary access policies para cambios de permisos

### MAY (Opcional)

- **MAY** implementar honeypot endpoints para detección temprana
- **MAY** utilizar ML para detección de comportamientos anómalos

### MUST NOT (Prohibido)

- **MUST NOT** confiar implícitamente en datos provenientes de otra zona de confianza
- **MUST NOT** permitir que datos de zonas públicas lleguen a BD sin validación
- **MUST NOT** otorgar permisos permanentes para acceso de emergencia
- **MUST NOT** saltarse validación por "context" de red interna

---

## Referencias

- [NIST Zero Trust Architecture (SP 800-207)](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- [AWS Zero Trust on AWS](https://docs.aws.amazon.com/whitepapers/latest/zero-trust-architectures/zero-trust-architectures.html)
- [Microsoft Zero Trust Guidance Center](https://www.microsoft.com/en-us/security/business/zero-trust)
- [Google BeyondCorp Enterprise](https://cloud.google.com/beyondcorp)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Zero Trust Networking y mTLS](./zero-trust-networking.md)
- [SSO, MFA y RBAC](./sso-mfa-rbac.md)
- [Gobernanza de Seguridad](./security-governance.md)
