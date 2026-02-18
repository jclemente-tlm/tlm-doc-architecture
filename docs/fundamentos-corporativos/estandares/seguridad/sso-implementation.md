---
id: sso-implementation
sidebar_position: 1
title: SSO Implementation
description: Single Sign-On con Keycloak para autenticación centralizada y gestión de identidades
---

# SSO Implementation

## Contexto

Este estándar define **SSO (Single Sign-On)**: sistema de autenticación centralizado donde usuarios se autentican **una sola vez** y acceden a **múltiples aplicaciones** sin re-autenticarse. Elimina múltiples credenciales (username/password por aplicación). Complementa el [lineamiento de Identidad y Accesos](../../lineamientos/seguridad/05-identidad-y-accesos.md) mediante **Keycloak** como IdP corporativo.

---

## Concepto Fundamental

```yaml
# Sin SSO (❌) vs Con SSO (✅)

Without SSO (Multiple Logins):

  User:
    Sales App → Login: user/pass (credentials #1)
    Billing App → Login: user/pass (credentials #2)
    HR App → Login: user/pass (credentials #3)
    Analytics → Login: user/pass (credentials #4)

  Problems:
    ❌ Password fatigue (4 passwords to remember)
    ❌ Weak passwords (users recycle same password)
    ❌ Hard to revoke (disable user in 4 systems)
    ❌ No centralized audit (4 separate logs)
    ❌ Onboarding slow (create 4 accounts)

With SSO (Single Login):

  User:
    1. Go to Sales App → Redirect to Keycloak
    2. Login ONCE: user/pass + MFA → Keycloak issues token
    3. Redirect back to Sales App with token ✅ Authenticated

    4. Go to Billing App → Keycloak checks existing session
    5. Already logged in → Auto-redirect with token ✅ NO re-login

    6. Go to HR App → Same ✅ NO re-login
    7. Go to Analytics → Same ✅ NO re-login

  Benefits:
    ✅ Single password (only Keycloak credentials)
    ✅ Strong password policy (enforced centrally)
    ✅ Easy revoke (disable in Keycloak → all apps)
    ✅ Centralized audit (all logins in Keycloak)
    ✅ Fast onboarding (one account, access all)
    ✅ MFA enforced centrally (not per-app)
```

## Architecture

```yaml
# Talma SSO Architecture with Keycloak

Components:

  Keycloak (Identity Provider):
    - URL: https://sso.talma.com
    - Database: PostgreSQL RDS (users, sessions, clients)
    - Deployment: ECS Fargate (2 tasks, multi-AZ)
    - Version: Keycloak 24.x

  Applications (Service Providers):
    - Sales Service (React SPA + .NET API)
    - Billing Service (React SPA + .NET API)
    - HR Portal (React SPA + .NET API)
    - Analytics Dashboard (React SPA)

  External Identity Providers (Federation):
    - Azure AD (for corporate employees)
    - Google Workspace (for contractors)
    - LDAP (legacy on-prem directory)

Flow (OpenID Connect):

  1. User → https://sales.talma.com

  2. Sales App checks: No JWT token → Redirect to Keycloak
     Location: https://sso.talma.com/realms/talma/protocol/openid-connect/auth
       ?client_id=sales-service
       &redirect_uri=https://sales.talma.com/callback
       &response_type=code
       &scope=openid profile email

  3. Keycloak: Show login page
     Username: juan.perez@talma.com
     Password: ********
     MFA: 123456 (TOTP)

  4. Keycloak validates credentials → Issues authorization code
     Redirect: https://sales.talma.com/callback?code=abc123def456

  5. Sales App backend: Exchange code for tokens
     POST https://sso.talma.com/realms/talma/protocol/openid-connect/token
       grant_type=authorization_code
       code=abc123def456
       client_id=sales-service
       client_secret=<secret>

     Response:
       {
         "access_token": "eyJhbGc...",  # JWT (5 min TTL)
         "refresh_token": "eyJhbGc...", # Refresh (30 days TTL)
         "id_token": "eyJhbGc...",      # User info
         "token_type": "Bearer"
       }

  6. Sales App: Store tokens → User authenticated ✅

  7. User → https://billing.talma.com (different app)

  8. Billing App: No JWT → Redirect to Keycloak

  9. Keycloak: Existing session found (cookie) → Auto-login ✅
     (NO password prompt, seamless SSO)

  10. Billing App: Receives new token for billing-service → Authenticated ✅
```

## Keycloak Configuration

```yaml
# Keycloak Realm Configuration

Realm: talma
  Display Name: Talma Platform
  Enabled: true

  Login Settings:
    - User Registration: Disabled (admin creates accounts)
    - Forgot Password: Enabled (self-service reset)
    - Remember Me: Enabled (30 days)
    - Verify Email: Enabled (email verification required)

  Security:
    - Brute Force Detection: Enabled
      Max Login Failures: 5
      Wait Time: 15 minutes
      Quick Login Check: 1000ms
      Max Wait: 900s (15 min)

    - Password Policy:
      Minimum Length: 12
      Uppercase: 1
      Lowercase: 1
      Digits: 1
      Special Chars: 1
      Not Username: true
      Not Email: true
      Password History: 5 (can't reuse last 5)
      Expiration: 90 days

    - OTP Policy (MFA):
      Type: TOTP (Time-based One-Time Password)
      Algorithm: SHA256
      Digits: 6
      Period: 30 seconds
      Initial Counter: 0
      Required for: All users

Clients:

  Client 1: sales-service
    Client ID: sales-service
    Client Protocol: openid-connect
    Access Type: confidential (has client secret)
    Root URL: https://sales.talma.com
    Valid Redirect URIs:
      - https://sales.talma.com/callback
      - http://localhost:3000/callback  # Dev only
    Web Origins:
      - https://sales.talma.com

    Mappers:
      - User Property: email → JWT claim "email"
      - User Property: firstName + lastName → JWT claim "name"
      - User Roles → JWT claim "roles" (array)
      - User Attribute: customerId → JWT claim "customerId"

  Client 2: billing-service
    (Same structure as sales-service)

  Client 3: analytics-dashboard
    Access Type: public (no client secret, SPA)
    PKCE: Required (security for public clients)

Users:

  User: juan.perez@talma.com
    First Name: Juan
    Last Name: Pérez
    Email: juan.perez@talma.com
    Email Verified: true
    Enabled: true

    Credentials:
      Password: (hashed with bcrypt)
      OTP: Configured (Google Authenticator)

    Attributes:
      customerId: cust-123
      department: Sales
      country: PE

    Role Mappings:
      Realm Roles:
        - sales-user
      Client Roles (sales-service):
        - orders:read
        - orders:create
      Client Roles (billing-service):
        - invoices:read

Identity Providers (Federation):

  Azure AD:
    Alias: azure-ad
    Provider: Microsoft
    Client ID: <from Azure App Registration>
    Client Secret: <from Azure>
    Authorization URL: https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/authorize
    Token URL: https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token

    Mapper:
      - Azure AD email → Keycloak username
      - Azure AD groups → Keycloak roles

  Google Workspace:
    Alias: google
    Provider: Google
    Client ID: <from Google Console>
    Client Secret: <from Google>
    Hosted Domain: talma.com (only @talma.com emails)
```

## Implementation (.NET)

```csharp
// ✅ ASP.NET Core with Keycloak SSO

// Startup.cs / Program.cs

public void ConfigureServices(IServiceCollection services)
{
    services.AddAuthentication(options =>
    {
        options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
        options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
    })
    .AddCookie(options =>
    {
        options.Cookie.Name = "SalesServiceAuth";
        options.Cookie.HttpOnly = true;
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
        options.Cookie.SameSite = SameSiteMode.Lax;
        options.ExpireTimeSpan = TimeSpan.FromHours(8);
        options.SlidingExpiration = true;
    })
    .AddOpenIdConnect(options =>
    {
        // ✅ Keycloak configuration
        options.Authority = "https://sso.talma.com/realms/talma";
        options.ClientId = "sales-service";
        options.ClientSecret = Configuration["Keycloak:ClientSecret"]; // From Secrets Manager
        options.ResponseType = OpenIdConnectResponseType.Code;

        // ✅ Scopes
        options.Scope.Clear();
        options.Scope.Add("openid");
        options.Scope.Add("profile");
        options.Scope.Add("email");
        options.Scope.Add("roles");

        // ✅ Token validation
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = "https://sso.talma.com/realms/talma",
            ValidateAudience = true,
            ValidAudience = "sales-service",
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromMinutes(1), // Allow 1 min clock drift
            NameClaimType = "preferred_username",
            RoleClaimType = "roles"
        };

        // ✅ Save tokens for refresh
        options.SaveTokens = true;
        options.GetClaimsFromUserInfoEndpoint = true;

        // ✅ Events
        options.Events = new OpenIdConnectEvents
        {
            OnTokenValidated = context =>
            {
                // Custom claims mapping
                var claims = context.Principal.Claims.ToList();
                var customerId = claims.FirstOrDefault(c => c.Type == "customerId")?.Value;

                if (!string.IsNullOrEmpty(customerId))
                {
                    var identity = (ClaimsIdentity)context.Principal.Identity;
                    identity.AddClaim(new Claim("CustomerId", customerId));
                }

                return Task.CompletedTask;
            }
        };
    });

    services.AddAuthorization(options =>
    {
        options.AddPolicy("RequireSalesUser", policy =>
            policy.RequireRole("sales-user"));

        options.AddPolicy("RequireOrdersRead", policy =>
            policy.RequireClaim("roles", "orders:read"));
    });
}

// ✅ Protected Controller

[ApiController]
[Route("api/orders")]
[Authorize] // ✅ Requires valid JWT from Keycloak
public class OrdersController : ControllerBase
{
    [HttpGet]
    [Authorize(Policy = "RequireOrdersRead")] // ✅ Requires specific permission
    public async Task<IActionResult> GetOrders()
    {
        // ✅ User identity from JWT claims
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var customerId = User.FindFirst("CustomerId")?.Value;
        var roles = User.FindAll("roles").Select(c => c.Value).ToList();

        // Business logic...

        return Ok(orders);
    }

    [HttpGet("me")]
    public IActionResult GetCurrentUser()
    {
        return Ok(new
        {
            UserId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value,
            Email = User.FindFirst(ClaimTypes.Email)?.Value,
            Name = User.FindFirst(ClaimTypes.Name)?.Value,
            Roles = User.FindAll("roles").Select(c => c.Value).ToArray()
        });
    }
}

// ✅ Token Refresh (Silent)

public class TokenRefreshService : IHostedService
{
    private readonly IHttpContextAccessor _httpContextAccessor;
    private Timer _timer;

    public Task StartAsync(CancellationToken cancellationToken)
    {
        // Check token expiry every 2 minutes
        _timer = new Timer(RefreshTokenIfNeeded, null, TimeSpan.Zero, TimeSpan.FromMinutes(2));
        return Task.CompletedTask;
    }

    private async void RefreshTokenIfNeeded(object state)
    {
        var context = _httpContextAccessor.HttpContext;
        if (context?.User?.Identity?.IsAuthenticated != true)
            return;

        // Get token expiry
        var expiresAt = await context.GetTokenAsync("expires_at");
        if (DateTime.Parse(expiresAt) > DateTime.UtcNow.AddMinutes(3))
            return; // Still valid for 3+ minutes

        // ✅ Refresh token
        var refreshToken = await context.GetTokenAsync("refresh_token");

        var client = new HttpClient();
        var response = await client.PostAsync(
            "https://sso.talma.com/realms/talma/protocol/openid-connect/token",
            new FormUrlEncodedContent(new Dictionary<string, string>
            {
                ["grant_type"] = "refresh_token",
                ["refresh_token"] = refreshToken,
                ["client_id"] = "sales-service",
                ["client_secret"] = Configuration["Keycloak:ClientSecret"]
            }));

        if (response.IsSuccessStatusCode)
        {
            var tokens = await response.Content.ReadFromJsonAsync<TokenResponse>();

            // Update tokens in cookie
            var authResult = await context.AuthenticateAsync(CookieAuthenticationDefaults.AuthenticationScheme);
            authResult.Properties.UpdateTokenValue("access_token", tokens.AccessToken);
            authResult.Properties.UpdateTokenValue("refresh_token", tokens.RefreshToken);

            await context.SignInAsync(
                CookieAuthenticationDefaults.AuthenticationScheme,
                authResult.Principal,
                authResult.Properties);
        }
    }
}
```

## Frontend Implementation (React)

```typescript
// ✅ React SPA with Keycloak

// keycloak.ts
import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'https://sso.talma.com',
  realm: 'talma',
  clientId: 'sales-service',
});

export const initKeycloak = async (): Promise<boolean> => {
  try {
    const authenticated = await keycloak.init({
      onLoad: 'login-required', // ✅ Redirect to login if not authenticated
      checkLoginIframe: true,   // ✅ Check session status
      pkceMethod: 'S256',       // ✅ PKCE for security
    });

    if (authenticated) {
      console.log('User authenticated:', keycloak.tokenParsed);

      // ✅ Auto-refresh token before expiry
      setInterval(() => {
        keycloak.updateToken(60).catch(() => {
          console.error('Failed to refresh token');
          keycloak.logout();
        });
      }, 60000); // Check every minute
    }

    return authenticated;
  } catch (error) {
    console.error('Failed to initialize Keycloak', error);
    return false;
  }
};

export default keycloak;

// App.tsx
import { useEffect, useState } from 'react';
import keycloak, { initKeycloak } from './keycloak';

function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initKeycloak().then((auth) => {
      setAuthenticated(auth);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!authenticated) {
    return <div>Not authenticated</div>;
  }

  return (
    <div>
      <h1>Welcome, {keycloak.tokenParsed?.name}</h1>
      <button onClick={() => keycloak.logout()}>Logout</button>

      {/* Protected content */}
      {keycloak.hasRealmRole('sales-user') && (
        <SalesModule />
      )}
    </div>
  );
}

// API calls with token
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api.talma.com',
});

// ✅ Interceptor adds JWT to all requests
api.interceptors.request.use(
  async (config) => {
    if (keycloak.token) {
      // ✅ Refresh if expiring soon
      await keycloak.updateToken(30);
      config.headers.Authorization = `Bearer ${keycloak.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ Interceptor handles 401 (token expired)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token invalid, re-login
      await keycloak.logout();
    }
    return Promise.reject(error);
  }
);

export default api;
```

## Infrastructure (Terraform)

```hcl
# ✅ Keycloak on ECS Fargate

resource "aws_ecs_cluster" "keycloak" {
  name = "keycloak-cluster"
}

resource "aws_ecs_task_definition" "keycloak" {
  family                   = "keycloak"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"

  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.keycloak_task_role.arn

  container_definitions = jsonencode([{
    name  = "keycloak"
    image = "quay.io/keycloak/keycloak:24.0"

    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]

    environment = [
      {
        name  = "KC_DB"
        value = "postgres"
      },
      {
        name  = "KC_DB_URL"
        value = "jdbc:postgresql://${aws_db_instance.keycloak.endpoint}/keycloak"
      },
      {
        name  = "KC_HOSTNAME"
        value = "sso.talma.com"
      },
      {
        name  = "KC_PROXY"
        value = "edge"
      }
    ]

    secrets = [
      {
        name      = "KC_DB_USERNAME"
        valueFrom = aws_secretsmanager_secret.keycloak_db_user.arn
      },
      {
        name      = "KC_DB_PASSWORD"
        valueFrom = aws_secretsmanager_secret.keycloak_db_password.arn
      },
      {
        name      = "KEYCLOAK_ADMIN"
        valueFrom = aws_secretsmanager_secret.keycloak_admin_user.arn
      },
      {
        name      = "KEYCLOAK_ADMIN_PASSWORD"
        valueFrom = aws_secretsmanager_secret.keycloak_admin_password.arn
      }
    ]

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/keycloak"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

resource "aws_ecs_service" "keycloak" {
  name            = "keycloak"
  cluster         = aws_ecs_cluster.keycloak.id
  task_definition = aws_ecs_task_definition.keycloak.arn
  desired_count   = 2  # ✅ High availability
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.keycloak.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.keycloak.arn
    container_name   = "keycloak"
    container_port   = 8080
  }

  health_check_grace_period_seconds = 60
}

# RDS for Keycloak data
resource "aws_db_instance" "keycloak" {
  identifier     = "keycloak-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t4g.medium"

  allocated_storage     = 20
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  db_name  = "keycloak"
  username = "keycloak"

  backup_retention_period = 30
  multi_az                = true

  vpc_security_group_ids = [aws_security_group.keycloak_db.id]
  db_subnet_group_name   = aws_db_subnet_group.keycloak.name

  skip_final_snapshot = false
  final_snapshot_identifier = "keycloak-final-snapshot"
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Keycloak como IdP centralizado
- **MUST** implementar OpenID Connect (OIDC)
- **MUST** requerir MFA para todos los usuarios
- **MUST** enforcar política de contraseñas (12+ chars, complexity)
- **MUST** usar HTTPS para todas las comunicaciones
- **MUST** rotar tokens (access token 5 min, refresh 30 días)

### SHOULD (Fuertemente recomendado)

- **SHOULD** federar con Azure AD / Google Workspace
- **SHOULD** implementar brute force protection
- **SHOULD** usar PKCE para SPAs (public clients)
- **SHOULD** monitorear failed logins (detect attacks)

### MUST NOT (Prohibido)

- **MUST NOT** almacenar contraseñas en aplicaciones
- **MUST NOT** usar HTTP (solo HTTPS)
- **MUST NOT** compartir client secrets en código
- **MUST NOT** usar access tokens de larga duración (> 15 min)

---

## Referencias

- [Lineamiento: Identidad y Accesos](../../lineamientos/seguridad/05-identidad-y-accesos.md)
- [MFA](./mfa.md)
- [Identity Federation](./identity-federation.md)
- [Auth Protocols](./auth-protocols.md)
- [ADR-004: Keycloak SSO](../../../decisiones-de-arquitectura/adr-004-keycloak-sso-autenticacion.md)
