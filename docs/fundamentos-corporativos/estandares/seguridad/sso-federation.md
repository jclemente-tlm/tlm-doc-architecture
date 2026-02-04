---
id: sso-federation
sidebar_position: 19
title: SSO y Federación
description: Estándar para implementar Single Sign-On con Keycloak usando OpenID Connect, autenticación centralizada y federación de identidades
---

# Estándar Técnico — SSO y Federación

---

## 1. Propósito

Implementar Single Sign-On (SSO) con Keycloak 23.0+ usando OpenID Connect (OIDC), centralizando autenticación de usuarios, generando JWT tokens (RS256), y federando con proveedores externos (Google, Azure AD).

---

## 2. Alcance

**Aplica a:**

- Aplicaciones web (.NET, React)
- APIs backend (ASP.NET Core)
- Usuarios internos (empleados)
- Usuarios externos (clientes) en realm separado
- Federación con Azure AD (opcional)

**No aplica a:**

- Service-to-service auth (usar service accounts)
- APIs públicas sin autenticación

---

## 3. Tecnologías Aprobadas

| Componente            | Tecnología                                        | Versión mínima | Observaciones              |
| --------------------- | ------------------------------------------------- | -------------- | -------------------------- |
| **Identity Provider** | Keycloak                                          | 23.0+          | Self-hosted                |
| **Protocol**          | OpenID Connect 1.0                                | -              | OAuth 2.0 + identity layer |
| **Token Type**        | JWT RS256                                         | -              | Asymmetric signing         |
| **Session Store**     | Redis                                             | 7.2+           | Shared sessions            |
| **.NET Client**       | Microsoft.AspNetCore.Authentication.OpenIdConnect | 8.0+           | OIDC middleware            |
| **Frontend**          | oidc-client-ts                                    | 3.0+           | SPA authentication         |

⚠️ **NO UTILIZADO:**

- SAML 2.0 (legacy, preferir OIDC)
- Auth0 (comercial, preferir OSS)

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Keycloak Setup

- [ ] **Realms separados**: `talma-internal` (empleados), `talma-customers` (clientes)
- [ ] **Clients por aplicación**: payment-web, payment-api, admin-portal
- [ ] **JWT RS256**: Tokens firmados con RSA (NO HS256)
- [ ] **Token TTL**: Access token 15min, Refresh token 30 días
- [ ] **HTTPS obligatorio**: NO permitir HTTP

### Tokens

- [ ] **Claims estándar**: sub, email, name, roles
- [ ] **Custom claims**: tenant_id, permissions
- [ ] **Token validation**: Verificar firma, issuer, audience, expiration
- [ ] **Refresh tokens**: Implementar refresh automático

### Federación

- [ ] **Azure AD**: Para empleados (opcional)
- [ ] **Google OAuth**: Para clientes externos (opcional)
- [ ] **LDAP/AD**: Sincronización de usuarios (opcional)

---

## 5. Keycloak - Configuración

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    command: start-dev
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: ${KC_DB_PASSWORD}
      KC_HOSTNAME: auth.talma.com
      KC_HOSTNAME_STRICT: true
      KC_HTTP_ENABLED: false # HTTPS only
      KC_HTTPS_CERTIFICATE_FILE: /opt/keycloak/conf/cert.pem
      KC_HTTPS_CERTIFICATE_KEY_FILE: /opt/keycloak/conf/key.pem
    ports:
      - "8443:8443"
    volumes:
      - ./keycloak-certs:/opt/keycloak/conf
    depends_on:
      - postgres

  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: ${KC_DB_PASSWORD}
    volumes:
      - keycloak_db:/var/lib/postgresql/data

volumes:
  keycloak_db:
```

### Crear Realm

```bash
# Usar Keycloak Admin UI: https://auth.talma.com:8443/admin
# O usar Keycloak Admin CLI

# Login
/opt/keycloak/bin/kcadm.sh config credentials \
  --server https://auth.talma.com:8443 \
  --realm master \
  --user admin \
  --password ${KEYCLOAK_ADMIN_PASSWORD}

# Crear realm
/opt/keycloak/bin/kcadm.sh create realms \
  -s realm=talma-internal \
  -s enabled=true \
  -s sslRequired=all

# Crear client (payment-api)
/opt/keycloak/bin/kcadm.sh create clients -r talma-internal \
  -s clientId=payment-api \
  -s enabled=true \
  -s publicClient=false \
  -s serviceAccountsEnabled=true \
  -s directAccessGrantsEnabled=false \
  -s standardFlowEnabled=true \
  -s 'redirectUris=["https://api.talma.com/*"]' \
  -s 'webOrigins=["https://api.talma.com"]'
```

---

## 6. .NET - OIDC Integration

### Instalación

```bash
dotnet add package Microsoft.AspNetCore.Authentication.OpenIdConnect
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
```

### Configuración

```csharp
// Program.cs

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
        ClockSkew = TimeSpan.FromMinutes(1),  // Tolerancia de 1min

        ValidateIssuerSigningKey = true,
        // Keycloak public key se descarga automáticamente de /.well-known/jwks.json
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
        policy.RequireClaim("realm_access_roles", "admin"));

    options.AddPolicy("RequirePaymentAccess", policy =>
        policy.RequireClaim("resource_access_payment-api_roles", "payment:write"));
});

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
```

### Protected Controller

```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize]  // Require JWT token
public class PaymentsController : ControllerBase
{
    [HttpGet]
    public IActionResult GetPayments()
    {
        var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        var email = User.FindFirst(ClaimTypes.Email)?.Value;
        var roles = User.FindAll("realm_access_roles").Select(c => c.Value).ToList();

        return Ok(new
        {
            userId,
            email,
            roles
        });
    }

    [HttpPost]
    [Authorize(Policy = "RequirePaymentAccess")]  // Requiere claim específico
    public IActionResult CreatePayment([FromBody] CreatePaymentRequest request)
    {
        // Solo usuarios con permiso payment:write
        return Ok();
    }
}
```

---

## 7. Frontend (React) - OIDC

### Instalación

```bash
npm install oidc-client-ts
```

### Configuración

```typescript
// src/auth/AuthService.ts
import { UserManager, WebStorageStateStore } from "oidc-client-ts";

const oidcConfig = {
  authority: "https://auth.talma.com:8443/realms/talma-internal",
  client_id: "payment-web",
  redirect_uri: "https://app.talma.com/callback",
  post_logout_redirect_uri: "https://app.talma.com",
  response_type: "code", // Authorization Code Flow
  scope: "openid profile email",
  automaticSilentRenew: true, // Refresh automático
  userStore: new WebStorageStateStore({ store: window.localStorage }),
};

export const userManager = new UserManager(oidcConfig);

export const login = () => {
  userManager.signinRedirect();
};

export const logout = () => {
  userManager.signoutRedirect();
};

export const getUser = async () => {
  return await userManager.getUser();
};

export const getAccessToken = async () => {
  const user = await getUser();
  return user?.access_token;
};
```

### Protected Route

```typescript
// src/components/ProtectedRoute.tsx
import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { getUser } from '../auth/AuthService';

export const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    getUser().then(user => {
      setIsAuthenticated(!!user && !user.expired);
    });
  }, []);

  if (isAuthenticated === null) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};
```

### API Call con Token

```typescript
// src/services/PaymentService.ts
import { getAccessToken } from "../auth/AuthService";

export const getPayments = async () => {
  const token = await getAccessToken();

  const response = await fetch("https://api.talma.com/api/payments", {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  return await response.json();
};
```

---

## 8. Federación - Azure AD

### Configurar en Keycloak

1. **Admin Console** → Realm `talma-internal` → **Identity Providers**
2. **Add provider** → **Microsoft**
3. Configurar:
   - **Client ID**: Azure AD Application ID
   - **Client Secret**: Azure AD Secret
   - **Default Scopes**: `openid profile email`

### Flujo

```text
Usuario → Login con Azure AD → Azure AD autentica → Keycloak recibe token → Crea sesión Keycloak → Genera JWT Keycloak → Aplicación
```

---

## 9. Validación de Cumplimiento

```bash
# Verificar Keycloak accesible
curl -k https://auth.talma.com:8443/realms/talma-internal/.well-known/openid-configuration | jq .

# Verificar JWKS endpoint
curl -k https://auth.talma.com:8443/realms/talma-internal/protocol/openid-connect/certs | jq .

# Obtener token (testing)
curl -k -X POST https://auth.talma.com:8443/realms/talma-internal/protocol/openid-connect/token \
  -d "grant_type=password" \
  -d "client_id=payment-api" \
  -d "client_secret=${CLIENT_SECRET}" \
  -d "username=test@talma.com" \
  -d "password=password123" \
  | jq -r '.access_token'

# Decodificar JWT (usando jwt.io o jwt-cli)
jwt decode <token>
```

---

## 10. Referencias

**Keycloak:**

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [Keycloak OIDC Endpoints](https://www.keycloak.org/docs/latest/securing_apps/#endpoints)

**OIDC:**

- [OpenID Connect Spec](https://openid.net/connect/)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
