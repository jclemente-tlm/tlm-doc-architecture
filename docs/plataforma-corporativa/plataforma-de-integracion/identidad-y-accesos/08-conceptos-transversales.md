---
sidebar_position: 8
title: Conceptos Transversales
description: Seguridad, multi-tenancy, observabilidad y resiliencia.
---

# 8. Conceptos Transversales

## Seguridad

| Aspecto       | Implementación                | Tecnología |
| ------------- | ----------------------------- | ---------- |
| Autenticación | `OAuth2`/`OIDC`               | `Keycloak` |
| Tokens        | `JWT RS256`                   | Estándar   |
| Federación    | `SAML`/`LDAP` _(planificada)_ | Conectores |
| MFA           | TOTP (6 dígitos, 30s)         | `Keycloak` |
| Brute force   | Habilitado (30 intentos)      | `Keycloak` |

- Defensa en profundidad: WAF, subredes privadas, NACLs, headers seguros, autenticación y autorización centralizadas, rate limiting, audit logging.
- Gestión avanzada de secretos: rotación, control de acceso, auditoría en AWS Secrets Manager.
- Validación `JWT` y autorización basada en claims y `tenant` (`realm`).

## Multi-tenancy y Aislamiento

| Aspecto       | Implementación                                                     | Propósito            |
| ------------- | ------------------------------------------------------------------ | -------------------- |
| Realm corp    | `tlm-corp`: servicios corporativos globales (Grafana, etc.)        | Gestión centralizada |
| Realms país   | `tlm-pe`, `tlm-mx` (configurados); `tlm-ec`, `tlm-co` (pendientes) | Aislamiento total    |
| Usuarios      | Por `tenant` (`realm`)                                             | Separación           |
| Configuración | Por jurisdicción                                                   | Compliance           |

- Aislamiento multinivel: datos, configuración y autenticación independientes por `tenant` (`realm`).
- Configuración dinámica y cacheada por `tenant` (`realm`).

## Tema e Internacionalización

- Tema personalizado `talma-theme` aplicado a los realms `tlm-pe` y `tlm-mx`.
- Personalización de login, account y admin con branding Talma.
- Soporte i18n: español (`es`) como idioma por defecto, inglés (`en`) como alternativo.
- Mensajes traducidos en `keycloak/themes/talma-theme/login/messages/`.

## Observabilidad

- Métricas y health checks habilitados en puerto `9000` (`KC_METRICS_ENABLED`, `KC_HEALTH_ENABLED`).
- Logging con nivel configurable por ambiente (`KC_LOG_LEVEL`); listener `jboss-logging` activo.
- Integración con stack corporativo (Grafana, Mimir, Loki, Tempo) _(pendiente de configuración completa)_.

## Resiliencia

- Circuit breaker y retry en integración con `Keycloak` y servicios externos.
- Bulkhead y timeout para aislar recursos críticos.
- Manejo de errores centralizado y auditado.

## Compliance

- Audit trail de accesos, cambios y exportaciones de datos _(pendiente: eventos deshabilitados, ver DT-06)_.
- Políticas de retención y anonimización _(pendientes de automatización)_.
- Cumplimiento: GDPR, SOX, ISO 27001, controles de acceso y consentimiento.

## Flujos de Integración (M2M)

Flujo `client_credentials` para servicios backend sin interacción de usuario:

```http
POST /auth/realms/{tenant}/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=gestal-pe-dev&client_secret=secreto
```

```json
{
  "access_token": "...",
  "expires_in": 300,
  "token_type": "Bearer",
  "scope": "openid"
}
```

## Performance y Caching

- Access token lifespan: `300s` (5 min).
- SSO session idle timeout: `1800s` (30 min).
- SSO session max lifespan: `36000s` (10 hr).
- Validación JWT en Kong con clave pública RSA embebida en la configuración del gateway (`_consumers.yaml`), sin llamadas a Keycloak por request. La rotación de claves requiere actualizar el gateway y sincronizar.
- Sesión cacheada en memoria por tenant (realm).
- Caching con Redis _(pendiente de implementación)_.
