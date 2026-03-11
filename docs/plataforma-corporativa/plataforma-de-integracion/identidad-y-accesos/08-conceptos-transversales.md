---
sidebar_position: 8
title: Conceptos Transversales
description: Seguridad, multi-tenancy, observabilidad y resiliencia.
---

# 8. Conceptos Transversales

## Seguridad

| Aspecto       | Implementación    | Tecnología |
| ------------- | ----------------- | ---------- |
| Autenticación | `OAuth2`/`OIDC`   | `Keycloak` |
| Tokens        | `JWT RS256`       | Estándar   |
| Federación    | `SAML`/`LDAP`     | Conectores |
| MFA           | Obligatorio admin | `Keycloak` |

- Defensa en profundidad: WAF, subredes privadas, NACLs, headers seguros, autenticación y autorización centralizadas, rate limiting, audit logging.
- Gestión avanzada de secretos: rotación, control de acceso, auditoría en AWS Secrets Manager.
- Validación `JWT` y autorización basada en claims y `tenant` (`realm`).

## Multi-tenancy y Aislamiento

| Aspecto       | Implementación                 | Propósito         |
| ------------- | ------------------------------ | ----------------- |
| Realms        | Un `tenant` (`realm`) por país | Aislamiento total |
| Usuarios      | Por `tenant` (`realm`)         | Separación        |
| Configuración | Por jurisdicción               | Compliance        |

- Aislamiento multinivel: datos, configuración y autenticación independientes por `tenant` (`realm`).
- Configuración dinámica y cacheada por `tenant` (`realm`).

## Observabilidad

- Logging estructurado con contexto de `realm`, usuario y sesión enviado a **Loki** vía Fluent Bit/FireLens.
- Métricas por `realm` expuestas vía Prometheus y almacenadas en **Mimir** (Grafana).
- Trazas distribuidas con `OpenTelemetry` enviadas a **Tempo**.

## Resiliencia

- Circuit breaker y retry en integración con `Keycloak` y servicios externos.
- Bulkhead y timeout para aislar recursos críticos.
- Manejo de errores centralizado y auditado.

## Compliance

- Audit trail completo de accesos, cambios y exportaciones de datos.
- Políticas de retención y anonimización automatizadas.
- Cumplimiento: GDPR, SOX, ISO 27001, controles de acceso y consentimiento.

## Flujos de Integración (M2M)

Flujo `client_credentials` para servicios backend sin interacción de usuario:

```http
POST /realms/{tenant}/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=app-client&client_secret=secreto
```

```json
{
  "access_token": "...",
  "expires_in": 900,
  "token_type": "Bearer",
  "scope": "profile email tenant:peru"
}
```

## Performance y Caching

- Validación JWT local en Kong con JWKS cacheados, sin llamadas a Keycloak por request.
- Sesión y JWKS cacheados en memoria por `realm`.
- Caching con Redis _(pendiente de implementación)_.
