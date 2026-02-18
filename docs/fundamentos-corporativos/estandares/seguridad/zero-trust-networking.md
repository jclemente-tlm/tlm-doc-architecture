---
id: zero-trust-networking
sidebar_position: 2
title: Zero Trust Networking
description: Nunca confiar, siempre verificar - validación en cada petición independiente de origen
---

# Zero Trust Networking

## Contexto

Este estándar establece **Zero Trust Networking**: arquitectura donde **nunca se confía, siempre se verifica** cada petición independientemente del origen de red. El modelo tradicional de perímetro asume que dentro de la red corporativa todo es confiable (❌). Zero Trust verifica **CADA** interacción. Complementa el [lineamiento de Zero Trust](../../lineamientos/seguridad/02-zero-trust.md) enfocándose en **redes y comunicación**.

---

## Concepto Fundamental

```yaml
# Modelo Tradicional (❌) vs Zero Trust (✅)

Traditional Perimeter Model (Castle & Moat):

  Internet (Untrusted)
      │
      ▼
  Firewall ◄── Single control point
      │
      ▼
  Corporate Network (Trusted) ◄── Everything inside trusted ❌
      │
      ├─► Sales Service → Billing Service (no auth ❌)
      ├─► Employee laptop → Database (direct access ❌)
      └─► Contractor → All services (same as employee ❌)

  Problems:
    ❌ Lateral movement (compromised laptop → all systems)
    ❌ No micro-segmentation (every service sees everything)
    ❌ Trust based on network location (IP whitelist)
    ❌ Single breach = full compromise

Zero Trust Model (✅):

  NEVER TRUST, ALWAYS VERIFY

  Internet
      │
      ▼
  Sales Service API
      │
      ├─► Verify: JWT token (authentication) ✅
      ├─► Verify: Token signature (not tampered) ✅
      ├─► Verify: Token not expired ✅
      ├─► Verify: User has permission (authorization) ✅
      ├─► Verify: Rate limit not exceeded ✅
      └─► Verify: Request payload schema valid ✅
      │
      ▼
  Billing Service (internal call)
      │
      ├─► Verify: mTLS certificate (Sales Service identity) ✅
      ├─► Verify: Certificate not revoked ✅
      ├─► Verify: Service has permission (RBAC) ✅
      └─► Verify: Request within SLA limits ✅
      │
      ▼
  Database
      │
      ├─► Verify: IAM authentication (not user/pass) ✅
      ├─► Verify: TLS 1.3 connection ✅
      ├─► Verify: Row-level security (user sees only own data) ✅
      └─► Log: ALL queries (audit trail) ✅

  Benefits:
    ✅ Compromised service can't access others (no lateral movement)
    ✅ Micro-segmentation (service-to-service authorization)
    ✅ Identity-based access (not IP-based)
    ✅ Limited blast radius (breach contained)
```

## Principios Zero Trust

```yaml
# 1. NEVER TRUST, ALWAYS VERIFY

# ❌ Traditional: Source IP in VPC → Allow
if (request.source_ip in "10.0.0.0/8") {
  allow();  // Inside corporate network, trusted
}

# ✅ Zero Trust: Verify identity + permission ALWAYS
if (request.jwt.verify_signature() &&
    request.jwt.not_expired() &&
    user.has_permission("orders:read") &&
    rate_limit.check(user.id)) {
  allow();
} else {
  deny();
}

# 2. LEAST PRIVILEGE ACCESS

# ❌ Traditional: Admin role has all permissions
Role: Admin
  Permissions: *  // All actions, all resources

# ✅ Zero Trust: Granular permissions per resource
Role: OrderAdmin
  Permissions:
    - orders:read
    - orders:update
    - orders:cancel
  Resources:
    - arn:aws:dynamodb:us-east-1:123456789012:table/Orders
  Conditions:
    - StringEquals: { "orders:Region": "LATAM" }  // Only LATAM region

# 3. ASSUME BREACH

# ✅ Design as if attacker is already inside network

Defense in Depth:
  - External attacker → WAF blocks (OWASP rules)
  - Compromised service → mTLS prevents lateral movement
  - Stolen token → Short TTL (5 min) limits window
  - Database breach → Encryption at rest protects data
  - Logs exfiltrated → PII masked in logs

Monitoring:
  - Anomaly detection (user suddenly accessing 10x resources)
  - Impossible travel (login from US then China 1 hour later)
  - Privilege escalation (user queries admin-only table)

# 4. VERIFY EXPLICITLY

# ✅ Multi-factor verification

Authentication:
  - Who: JWT token with user ID
  - What: Token signature verified (not tampered)
  - When: Token expiry checked (not expired)
  - Where: IP geolocation (not from blocked country)
  - How: Device fingerprint (known device)
  - Why: Request context (legítimate business purpose)

Authorization:
  - Resource: orders:read permission
  - Scope: customerId == token.sub (own data only)
  - Time: business hours (9am-6pm LATAM)
  - Volume: < 100 requests/min (rate limit)

# 5. MICRO-SEGMENTATION

# ✅ Segment by workload, not network

Traditional: All backend services in single subnet 10.0.10.0/24
  - Sales can reach Billing ✅
  - Sales can reach HR ❌ (should not)
  - Compromised Sales → Compromised HR

Zero Trust: Workload-based segmentation
  - Sales subnet: 10.0.10.0/25 (Security Group: sg-sales)
  - Billing subnet: 10.0.10.128/25 (Security Group: sg-billing)
  - HR subnet: 10.0.11.0/25 (Security Group: sg-hr)

  Security Group Rules:
    sg-sales:
      Ingress: ALB (sg-alb) on 8080
      Egress: Billing (sg-billing) on 8080, RDS (sg-rds) on 5432
      ❌ NO egress to HR subnet

    sg-hr:
      Ingress: ALB (sg-alb) on 8080
      Egress: RDS (sg-rds-hr) on 5432
      ❌ NO communication with Sales/Billing
```

## Service-to-Service Authentication

```yaml
# ✅ Mutual TLS (mTLS) for service identity

Traditional (❌):
  Sales Service → Billing Service
    POST http://billing-service:8080/api/invoices
    # No authentication, trust based on network

Zero Trust (✅):
  Sales Service → Billing Service
    POST https://billing-service:8080/api/invoices
    Client Certificate: CN=sales-service.talma.com
    Server verifies:
      - Certificate issued by Talma CA
      - Certificate not expired
      - Certificate not revoked (OCSP)
      - CN matches allowed callers (sales-service allowed)

# Implementation: AWS ACM Private CA + ECS

# 1. Create Private CA
resource "aws_acmpca_certificate_authority" "talma" {
  type = "ROOT"
  certificate_authority_configuration {
    key_algorithm     = "RSA_4096"
    signing_algorithm = "SHA512WITHRSA"
    subject {
      common_name         = "Talma Root CA"
      organization        = "Talma"
      organizational_unit = "Platform"
      country             = "PE"
    }
  }
}

# 2. Issue certificate per service
resource "aws_acm_certificate" "sales_service" {
  domain_name       = "sales-service.internal.talma.com"
  certificate_authority_arn = aws_acmpca_certificate_authority.talma.arn

  subject_alternative_names = [
    "sales-service.production.svc.cluster.local"
  ]
}

# 3. ECS Task with mTLS
resource "aws_ecs_task_definition" "sales" {
  container_definitions = jsonencode([{
    name  = "sales-service"
    image = "ghcr.io/talma/sales-service:latest"

    secrets = [
      {
        name      = "TLS_CERT"
        valueFrom = aws_secretsmanager_secret.sales_tls_cert.arn
      },
      {
        name      = "TLS_KEY"
        valueFrom = aws_secretsmanager_secret.sales_tls_key.arn
      }
    ]

    environment = [
      {
        name  = "MTLS_ENABLED"
        value = "true"
      },
      {
        name  = "MTLS_CA_CERT"
        value = "/etc/ssl/certs/talma-ca.crt"
      }
    ]
  }])
}
```

## Implementation in .NET

```csharp
// ✅ Zero Trust HTTP Client (Service-to-Service)

public class ZeroTrustHttpClient
{
    private readonly HttpClient _httpClient;
    private readonly ITokenProvider _tokenProvider;

    public ZeroTrustHttpClient(ITokenProvider tokenProvider)
    {
        _tokenProvider = tokenProvider;

        // ✅ mTLS Client Certificate
        var handler = new HttpClientHandler();
        handler.ClientCertificates.Add(LoadClientCertificate());

        // ✅ Verify server certificate
        handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
        {
            // Check certificate issued by Talma CA
            if (cert.Issuer != "CN=Talma Root CA, O=Talma, C=PE")
                return false;

            // Check certificate not expired
            if (cert.NotAfter < DateTime.UtcNow)
                return false;

            // Check certificate not revoked (OCSP)
            return !IsCertificateRevoked(cert);
        };

        _httpClient = new HttpClient(handler);
    }

    public async Task<InvoiceDto> CreateInvoiceAsync(CreateInvoiceRequest request)
    {
        // ✅ Service-to-service token (JWT with service identity)
        var token = await _tokenProvider.GetServiceTokenAsync();

        var httpRequest = new HttpRequestMessage(HttpMethod.Post,
            "https://billing-service.internal.talma.com/api/invoices")
        {
            Content = JsonContent.Create(request)
        };

        // ✅ Authorization header (service identity)
        httpRequest.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

        // ✅ Request ID (tracing)
        httpRequest.Headers.Add("X-Request-ID", Guid.NewGuid().ToString());

        // ✅ Calling service identity
        httpRequest.Headers.Add("X-Calling-Service", "sales-service");

        var response = await _httpClient.SendAsync(httpRequest);

        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<InvoiceDto>();
    }
}

// ✅ Zero Trust API Controller (Verify Everything)

[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IOrderService _orderService;
    private readonly IAuthorizationService _authz;

    [HttpGet("{id}")]
    [Authorize] // ✅ JWT required
    public async Task<IActionResult> GetOrder(Guid id)
    {
        // ✅ Verify 1: Token signature (done by [Authorize])
        // ✅ Verify 2: Token not expired (done by [Authorize])

        // ✅ Verify 3: User has permission
        var authResult = await _authz.AuthorizeAsync(User, id, "orders:read");
        if (!authResult.Succeeded)
            return Forbid();

        // ✅ Verify 4: Rate limit
        var userId = User.GetUserId();
        if (!await _rateLimiter.AllowRequestAsync(userId))
            return StatusCode(429, "Too many requests");

        // ✅ Verify 5: Input validation
        if (id == Guid.Empty)
            return BadRequest("Invalid order ID");

        var order = await _orderService.GetByIdAsync(id);

        if (order == null)
            return NotFound();

        // ✅ Verify 6: Row-level security (user sees only own data)
        var customerIdClaim = User.GetCustomerId();
        if (order.CustomerId != customerIdClaim && !User.IsInRole("Admin"))
            return Forbid();

        // ✅ Audit log (all access logged)
        await _auditLogger.LogAccessAsync(new AccessLog
        {
            UserId = userId,
            Resource = $"Order:{id}",
            Action = "Read",
            Result = "Success",
            Timestamp = DateTime.UtcNow,
            IpAddress = HttpContext.Connection.RemoteIpAddress?.ToString()
        });

        return Ok(OrderDto.FromEntity(order));
    }
}
```

## Network Policy (Kubernetes)

```yaml
# ✅ Zero Trust Network Policies (Kubernetes)

# Deny all traffic by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress


# Allow Sales Service → Billing Service only
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sales-to-billing
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: billing-service
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: sales-service # ✅ Only Sales can call Billing
      ports:
        - protocol: TCP
          port: 8080


# Allow Sales Service → Database only
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sales-to-database
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: sales-service
  policyTypes:
    - Egress
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres # ✅ Only Database egress
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system # ✅ DNS resolution
      ports:
        - protocol: UDP
          port: 53

# ❌ Block Sales → HR (no business need)
# (Implicitly denied by default-deny-all policy above)
```

## AWS Security Groups (Zero Trust)

```hcl
# ✅ Restrictive Security Groups (Zero Trust in AWS)

# ALB Security Group (Internet-facing)
resource "aws_security_group" "alb" {
  name        = "alb-sg"
  description = "Allow HTTPS from internet"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Internet
    description = "HTTPS from internet"
  }

  egress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.sales_service.id]
    description     = "To Sales Service only"
  }
}

# Sales Service Security Group
resource "aws_security_group" "sales_service" {
  name        = "sales-service-sg"
  description = "Sales Service"
  vpc_id      = aws_vpc.main.id

  # ✅ Ingress: ONLY from ALB
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "From ALB only"
  }

  # ✅ Egress: ONLY to Billing Service and Database
  egress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.billing_service.id]
    description     = "To Billing Service only"
  }

  egress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.rds.id]
    description     = "To Database only"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS for external APIs (Stripe, etc)"
  }

  # ❌ NO egress to 0.0.0.0/0 on all ports
  # ❌ NO egress to HR, Accounting, etc (no business need)
}

# Database Security Group
resource "aws_security_group" "rds" {
  name        = "rds-sg"
  description = "PostgreSQL Database"
  vpc_id      = aws_vpc.main.id

  # ✅ Ingress: ONLY from application services
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [
      aws_security_group.sales_service.id,
      aws_security_group.billing_service.id
    ]
    description = "From application services only"
  }

  # ❌ NO ingress from 0.0.0.0/0 (not public)
  # ❌ NO ingress from developer laptops (use bastion + VPN)

  # ✅ No egress (database doesn't initiate connections)
}
```

## Monitoring & Anomaly Detection

```yaml
# ✅ Detect Zero Trust violations

CloudWatch Logs Insights:

  # Unauthorized service-to-service calls
  fields @timestamp, callingService, targetService, statusCode
  | filter statusCode == 403
  | filter callingService != "sales-service"
  | filter targetService == "billing-service"
  | stats count() by callingService
  # Alert if count > 0 (only Sales should call Billing)

  # Lateral movement attempts
  fields @timestamp, sourceIP, targetService
  | filter statusCode == 403
  | filter targetService in ["hr-service", "accounting-service"]
  | filter sourceIP LIKE /^10\.0\.10\./  # From application subnet
  # Alert: Application trying to access HR (no business need)

AWS GuardDuty:

  Findings:
    - UnauthorizedAccess:EC2/TorClient
      → ECS Task communicating via Tor (data exfiltration)

    - Recon:EC2/PortProbeUnprotectedPort
      → Port scanning inside VPC (attacker reconnaissance)

    - UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration
      → IAM credentials used outside AWS (stolen credentials)

Custom Metrics:

  # Service-to-service auth failures
  aws cloudwatch put-metric-alarm \
    --alarm-name "ServiceAuthFailures" \
    --metric-name "AuthFailureCount" \
    --namespace "ZeroTrust" \
    --statistic Sum \
    --period 300 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold

  # Alert: > 10 auth failures in 5 min (brute force attempt)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** verificar autenticación en CADA petición (no confiar en red)
- **MUST** usar mTLS para comunicación service-to-service
- **MUST** implementar micro-segmentation (Security Groups restrictivos)
- **MUST** aplicar principio de least privilege (permisos granulares)
- **MUST** asumir breach (defense in depth)
- **MUST** auditar TODAS las interacciones (CloudWatch Logs)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Private CA para emitir certificados (AWS ACM PCA)
- **SHOULD** implementar anomaly detection (GuardDuty)
- **SHOULD** rotar certificados automáticamente (< 90 días)
- **SHOULD** verificar revocación de certificados (OCSP)

### MUST NOT (Prohibido)

- **MUST NOT** confiar basándose solo en source IP
- **MUST NOT** permitir comunicación sin autenticación
- **MUST NOT** usar Security Groups permisivos (0.0.0.0/0 egress)
- **MUST NOT** skip verificación de certificados

---

## Referencias

- [Lineamiento: Zero Trust](../../lineamientos/seguridad/02-zero-trust.md)
- [Mutual TLS](./mutual-tls.md)
- [Explicit Verification](./explicit-verification.md)
- [Network Segmentation](./network-segmentation.md)
- [Trust Boundaries](./trust-boundaries.md)
