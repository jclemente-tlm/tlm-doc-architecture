# 8. Conceptos Transversales

## 8.1 Seguridad

| Aspecto       | Implementación         | Tecnología   |
|---------------|-----------------------|--------------|
| Autenticación | `OAuth2`/`OIDC`       | `Keycloak`   |
| Tokens        | `JWT RS256`           | Estándar     |
| Federación    | `SAML`/`LDAP`         | Conectores   |
| MFA           | Obligatorio admin     | `Keycloak`   |

- Defensa en profundidad: WAF, subredes privadas, NACLs, headers seguros, autenticación y autorización centralizadas, rate limiting, audit logging.
- Gestión avanzada de secretos: rotación, control de acceso, auditoría en AWS Secrets Manager.
- Validación `JWT` y autorización basada en claims y `tenant` (`realm`).

## 8.2 Multi-Tenancy Y Aislamiento

| Aspecto       | Implementación               | Propósito         |
|---------------|-----------------------------|-------------------|
| Realms        | Un `tenant` (`realm`) por país | Aislamiento total |
| Usuarios      | Por `tenant` (`realm`)         | Separación        |
| Configuración | Por jurisdicción               | Compliance        |

- Aislamiento multinivel: datos, configuración y autenticación independientes por `tenant` (`realm`).
- Configuración dinámica y cacheada por `tenant` (`realm`).

## 8.3 Observabilidad Y Telemetría

- Logging estructurado con contexto de `tenant` (`realm`), usuario y sesión.
- Métricas técnicas y de negocio instrumentadas por `tenant` (`realm`) y expuestas vía `Prometheus`.
- Trazado distribuido con `OpenTelemetry` y `Jaeger`, enriquecido con tags de `tenant` (`realm`) y usuario.

## 8.4 Resiliencia Y Manejo De Errores

- Circuit breaker y retry en integración con `Keycloak` y servicios externos.
- Bulkhead y timeout para aislar recursos críticos.
- Manejo de errores centralizado y auditado.

## 8.5 Compliance Y Gobierno

- Audit trail completo de accesos, cambios y exportaciones de datos.
- Políticas de retención y anonimización automatizadas.
- Cumplimiento: GDPR, SOX, ISO 27001, controles de acceso y consentimiento.

## 8.6 Performance Y Caching

- Estrategia de caching multinivel: memoria local, `Redis`, cache HTTP.
- Optimización de queries y uso de índices por `tenant` (`realm`).
- Métricas de latencia y throughput monitorizadas y alertadas.

## 8.7 Referencias

- [Keycloak Security Docs](https://www.keycloak.org/docs/latest/server_admin/#security)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [Arc42 Crosscutting Concepts](https://docs.arc42.org/section-8/)
- [C4 Model for Software Architecture](https://c4model.com/)
