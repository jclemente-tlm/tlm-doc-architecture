---
sidebar_position: 6
title: Vista de Tiempo de Ejecución
description: Flujos de autenticación, federación y validación de tokens.
---

# 6. Vista de Tiempo de Ejecución

## Escenario: Autenticación con MFA

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Browser as Browser
    participant GW as API Gateway (Kong)
    participant ALB as ALB
    participant KC as Keycloak

    User->>Browser: Accede a aplicación
    Browser->>GW: GET /app/dashboard
    GW->>Browser: HTTP 401
    Browser->>ALB: GET /auth/realms/{tenant}/protocol/openid-connect/auth
    ALB->>KC: Reenviar solicitud
    KC->>Browser: Formulario de login
    User->>Browser: Ingresa credenciales
    Browser->>ALB: POST /auth/realms/{tenant}/login-actions/authenticate
    ALB->>KC: Reenviar solicitud
    KC->>Browser: Solicitar código TOTP
    User->>Browser: Ingresa código
    Browser->>ALB: POST /auth/realms/{tenant}/login-actions/required-action
    ALB->>KC: Reenviar solicitud
    KC->>Browser: HTTP 302 + authorization_code
    Browser->>ALB: POST /auth/realms/{tenant}/protocol/openid-connect/token
    ALB->>KC: Reenviar solicitud
    KC->>Browser: JWT tokens
    Browser->>GW: GET /app/dashboard + Bearer token
    GW->>GW: Validar JWT (JWKS local)
    GW->>Browser: HTTP 200 + dashboard
    alt Login desde nueva ubicación
        KC-->>User: Email de alerta de seguridad
    end
```

### Manejo de Errores

| Escenario             | Respuesta | Recuperación                            |
| --------------------- | --------- | --------------------------------------- |
| LDAP no disponible    | HTTP 503  | Fallback a usuarios locales             |
| MFA fallido (3 veces) | Lockout   | Email de desbloqueo                     |
| Audit Service caído   | Continuar | Almacenamiento local y replay posterior |

## Escenario: Federación SAML _(planificada)_

> Este flujo aplica cuando se configure federación con IdPs externos. Actualmente no hay Identity Providers configurados en los realms.

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Browser as Browser
    participant ALB as ALB
    participant KC as Keycloak (SP)
    participant IdP as IdP Externo

    User->>Browser: Click "Login with IdP"
    Browser->>ALB: GET /auth/realms/{tenant}/broker/idp-saml/login
    ALB->>KC: Reenviar solicitud
    KC->>Browser: Redirect a IdP con SAML AuthnRequest
    Browser->>IdP: POST SAML AuthnRequest
    IdP->>User: Autenticación
    User->>IdP: Autorizar acceso
    IdP->>Browser: SAML Response
    Browser->>ALB: POST SAML Response
    ALB->>KC: Reenviar solicitud
    KC->>KC: Validar assertion, mapear usuario, crear sesión
    KC->>Browser: HTTP 302 + authorization_code
    Browser->>ALB: POST /auth/realms/{tenant}/protocol/openid-connect/token
    ALB->>KC: Reenviar solicitud
    KC->>Browser: JWT tokens
```

## Escenario: Generación de Token M2M (Client Credentials)

Flujo para servicios backend que se comunican entre sí sin intervención de un usuario (e.g., worker, microservicio, job).

```mermaid
sequenceDiagram
    participant SvcA as Servicio A (cliente)
    participant ALB as ALB
    participant KC as Keycloak

    SvcA->>ALB: POST /auth/realms/{tenant}/protocol/openid-connect/token<br/>grant_type=client_credentials<br/>client_id & client_secret
    ALB->>KC: Reenviar solicitud
    KC->>KC: Validar credenciales y scopes
    KC->>SvcA: Access Token (JWT) + expires_in

    alt Token expirado
        SvcA->>ALB: POST /token (renovar con client_credentials)
        ALB->>KC: Reenviar solicitud
        KC->>SvcA: Nuevo Access Token
    end
```

### Ejemplo de solicitud HTTP

```http
POST /auth/realms/tlm-pe/protocol/openid-connect/token
Host: keycloak.talma.internal
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=gestal-pe-dev
&client_secret=<SECRET>
&scope=openid
```

**Respuesta:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 300,
  "token_type": "Bearer",
  "scope": "openid"
}
```

### Ejemplo en C# (.NET 8)

```csharp
public class KeycloakM2MTokenService(IHttpClientFactory httpClientFactory, IOptions<KeycloakOptions> options)
{
    private readonly KeycloakOptions _options = options.Value;

    public async Task<string> GetAccessTokenAsync(CancellationToken cancellationToken = default)
    {
        var client = httpClientFactory.CreateClient("keycloak");

        var body = new Dictionary<string, string>
        {
            ["grant_type"]    = "client_credentials",
            ["client_id"]     = _options.ClientId,
            ["client_secret"] = _options.ClientSecret,
            ["scope"]         = _options.Scopes,
        };

        var response = await client.PostAsync(
            $"/realms/{_options.Realm}/protocol/openid-connect/token",
            new FormUrlEncodedContent(body),
            cancellationToken);

        response.EnsureSuccessStatusCode();

        var payload = await response.Content.ReadFromJsonAsync<TokenResponse>(cancellationToken);
        return payload!.AccessToken;
    }
}
```

> **Nota:** el token debe cachearse por `expires_in - margen (p.ej. 30 s)` para evitar solicitudes innecesarias a Keycloak.

### Manejo de Errores

| Escenario                 | Respuesta HTTP  | Acción recomendada                                   |
| ------------------------- | --------------- | ---------------------------------------------------- |
| `client_secret` inválido  | 401             | Revisar configuración; no reintentar sin corrección  |
| Scope no autorizado       | 400             | Verificar roles/scopes del cliente en Keycloak       |
| Keycloak no disponible    | 503             | Reintentar con backoff exponencial (máx. 3 intentos) |
| Token expirado en uso     | 401 del recurso | Renovar token y reintentar la solicitud original     |
| `client_id` no encontrado | 401             | Verificar realm y nombre del cliente                 |
