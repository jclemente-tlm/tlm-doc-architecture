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
    participant KC as Keycloak
    participant AuditSvc as Audit Service

    User->>Browser: Accede a aplicación
    Browser->>GW: GET /app/dashboard
    GW->>Browser: HTTP 401
    Browser->>KC: GET /realms/{tenant}/protocol/openid-connect/auth
    KC->>Browser: Formulario de login
    User->>Browser: Ingresa credenciales
    Browser->>KC: POST login-actions/authenticate
    KC->>AuditSvc: LOG: LOGIN_ATTEMPT
    KC->>Browser: Solicitar código TOTP
    User->>Browser: Ingresa código
    Browser->>KC: POST login-actions/required-action
    KC->>AuditSvc: LOG: MFA_SUCCESS
    KC->>Browser: HTTP 302 + authorization_code
    Browser->>KC: POST /realms/{tenant}/protocol/openid-connect/token
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

## Escenario: Federación SAML

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Browser as Browser
    participant KC as Keycloak (SP)
    participant IdP as IdP Externo
    participant AuditSvc as Audit Service

    User->>Browser: Click "Login with IdP"
    Browser->>KC: GET /realms/{tenant}/broker/idp-saml/login
    KC->>Browser: Redirect a IdP con SAML AuthnRequest
    Browser->>IdP: POST SAML AuthnRequest
    IdP->>User: Autenticación
    User->>IdP: Autorizar acceso
    IdP->>Browser: SAML Response
    Browser->>KC: POST SAML Response
    KC->>KC: Validar assertion, mapear usuario, crear sesión
    KC->>AuditSvc: LOG: FEDERATED_LOGIN
    KC->>Browser: HTTP 302 + authorization_code
    Browser->>KC: POST /realms/{tenant}/protocol/openid-connect/token
    KC->>Browser: JWT tokens
```
