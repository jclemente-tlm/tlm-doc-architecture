# 6. Vista De Tiempo De Ejecución

## 6.1 Escenarios Principales

| Escenario         | Flujo                                 | Componentes           |
|-------------------|---------------------------------------|-----------------------|
| Autenticación     | Usuario → `Keycloak` → `JWT`          | Keycloak Core         |
| Validación Token  | Servicio → `Keycloak` → Validación    | JWT Validation        |
| Federación        | IdP externo → `Keycloak` → Usuario    | Federation Connectors |

## 6.2 Patrones De Interacción

| Patrón        | Descripción                | Tecnología |
|---------------|---------------------------|------------|
| OAuth2/OIDC   | Flujo de autenticación    | Estándar   |
| JWT           | Tokens de acceso          | RS256      |
| SAML          | Federación legacy         | SAML 2.0   |

## 6.3 Escenario: Autenticación De Usuario Con MFA

### Participantes

- User Browser
- API Gateway (`YARP`)
- `Keycloak` (`tenant`/`realm`)
- Identity Management API
- Token Validation Service
- Audit Service
- Notification Service

### Flujo De Ejecución

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Browser as Browser
    participant Gateway as API Gateway
    participant KC as Keycloak
    participant IdAPI as Identity API
    participant TokenSvc as Token Service
    participant AuditSvc as Audit Service
    participant NotifSvc as Notification
    User->>Browser: Accede a aplicación
    Browser->>Gateway: GET /app/dashboard
    Gateway->>Gateway: Verificar Authorization header
    Gateway->>Browser: HTTP 401 + WWW-Authenticate
    Browser->>KC: GET /auth/realms/tenant/protocol/openid-connect/auth
    KC->>KC: Verificar sesión
    KC->>Browser: Render login form
    Browser->>User: Mostrar login
    User->>Browser: Ingresa credenciales
    Browser->>KC: POST /auth/realms/tenant/login-actions/authenticate
    KC->>KC: Validar credenciales
    KC->>AuditSvc: LOG: LOGIN_ATTEMPT
    KC->>Browser: Render MFA challenge
    Browser->>User: Solicitar código TOTP
    User->>Browser: Ingresa código
    Browser->>KC: POST /auth/realms/tenant/login-actions/required-action
    KC->>KC: Validar TOTP
    KC->>AuditSvc: LOG: MFA_SUCCESS
    KC->>IdAPI: GET /api/v1/users/{userId}/profile
    IdAPI->>KC: Enhanced user profile
    KC->>KC: Crear sesión + generar tokens JWT
    KC->>AuditSvc: LOG: LOGIN_SUCCESS
    KC->>Browser: HTTP 302 redirect + authorization_code
    Browser->>KC: POST /auth/realms/tenant/protocol/openid-connect/token
    KC->>Browser: JWT tokens
    Browser->>Gateway: GET /app/dashboard + Bearer token
    Gateway->>TokenSvc: gRPC ValidateToken(jwt)
    TokenSvc->>TokenSvc: Verificar firma + claims
    TokenSvc->>Gateway: Token válido
    Gateway->>Gateway: Aplicar políticas
    Gateway->>Browser: HTTP 200 + dashboard
    Browser->>User: Mostrar aplicación
    alt Login desde nueva ubicación/dispositivo
        KC->>NotifSvc: Send security alert
        NotifSvc->>User: Email de alerta
    end
```

### Métricas De Performance

| Fase                        | Target     | Medición           | Monitoreo           |
|-----------------------------|------------|--------------------|---------------------|
| Redirección inicial         | `< 50ms`   | Gateway latency    | `Prometheus`        |
| Render login form           | `< 200ms`  | Keycloak response  | Application metrics |
| Validación credenciales     | `< 300ms`  | LDAP/DB query      | Custom metrics      |
| Validación MFA              | `< 100ms`  | TOTP algorithm     | Auth metrics        |
| Token generation            | `< 200ms`  | JWT creation       | Session metrics     |
| Token validation            | `< 10ms`   | gRPC/cache         | Token metrics       |
| Flujo completo              | `< 2s`     | End-to-end         | Synthetic monitoring|

### Manejo De Errores Y Resiliencia

| Escenario Error         | Respuesta      | Acción De Recuperación                |
|------------------------|----------------|---------------------------------------|
| LDAP Unavailable       | HTTP 503       | Fallback a usuarios locales           |
| MFA Failure (3x)       | Lockout        | Email de desbloqueo + notificación    |
| Token Service Down     | HTTP 503       | Circuit breaker + validación local    |
| Audit Service Down     | Continuar      | Store local + replay posterior        |

## 6.4 Escenario: Federación Con IdP SAML

### Participantes

- Usuario Corporativo
- `Keycloak` (SP)
- IdP Externo (IdP)
- Procesador SAML
- Servicio de Auditoría

### Flujo De Ejecución

```mermaid
sequenceDiagram
    participant User as Usuario
    participant Browser as Browser
    participant KC as Keycloak (SP)
    participant IdP as IdP Externo (IdP)
    participant SAMLProc as Procesador SAML
    participant AuditSvc as Servicio de Auditoría
    User->>Browser: Click "Login with IdP"
    Browser->>KC: GET /auth/realms/tenant/broker/idp-saml/login
    KC->>KC: Generar SAML AuthnRequest
    KC->>Browser: Redirect a IdP SAML
    Browser->>IdP: POST SAML AuthnRequest
    IdP->>IdP: Validar dominio/usuario
    IdP->>User: Autenticación (según IdP)
    User->>IdP: Autorizar acceso
    IdP->>IdP: Generar SAML Response
    IdP->>Browser: SAML Response
    Browser->>KC: POST SAML Response
    KC->>SAMLProc: Procesar assertion
    SAMLProc->>KC: Validar assertion
    KC->>KC: Mapear usuario, crear sesión
    KC->>AuditSvc: LOG: FEDERATED_LOGIN
    KC->>Browser: HTTP 302 redirect + authorization_code
    Browser->>KC: POST /auth/realms/tenant/protocol/openid-connect/token
    KC->>Browser: JWT tokens
    Browser->>User: Acceso a aplicación
```

> Este escenario describe la federación SAML entre un IdP externo corporativo y `Keycloak` en arquitectura multi-tenant. El flujo refleja la integración real, trazabilidad y auditoría, sin pasos ni componentes ajenos.

## 6.5 Métricas Y Monitoreo De Escenarios

- Todas las fases instrumentadas con `Prometheus`, `Grafana` y logs estructurados.
- Trazas distribuidas para flujos críticos (`OpenTelemetry`, `Jaeger`).
- Alertas automáticas ante degradación de performance o fallos de integración.

## 6.6 Referencias

- [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [Arc42 Runtime View](https://docs.arc42.org/section-6/)
- [C4 Model for Software Architecture](https://c4model.com/)

---
