# 2. Restricciones De La Arquitectura

Esta sección documenta las limitaciones técnicas, organizativas, de proceso y de cumplimiento que condicionan el diseño y la evolución del Servicio de Identidad. Todas las restricciones aquí descritas son obligatorias y deben ser consideradas en cada decisión arquitectónica.

## 2.1 Técnicas Y De Plataforma

| Categoría     | Restricción           | Impacto en la arquitectura           |
|--------------|----------------------|--------------------------------------|
| Plataforma   | `Keycloak 23+`       | Define IdP, APIs y federación        |
| Base de datos| `PostgreSQL`         | Esquema multi-tenant, alta disponibilidad |
| Contenedores | `Docker`             | Portabilidad y despliegue            |
| Orquestación | `AWS ECS` + `Terraform` | Infraestructura como código, escalabilidad |
| Protocolos   | `OAuth2`/`OIDC`, `SAML` | Interoperabilidad y seguridad     |

## 2.2 Rendimiento Y Disponibilidad

| Métrica               | Objetivo      | Justificación           |
|-----------------------|--------------|------------------------|
| Usuarios concurrentes | `10,000+`    | Escalabilidad regional  |
| Latencia              | `< 100ms`    | Experiencia usuario     |
| Disponibilidad        | `99.9%`      | SLA corporativo         |
| Failover              | `< 2 minutos`| Resiliencia ante fallos |

## 2.3 Seguridad Y Compliance

| Aspecto       | Requerimiento                | Referencia                |
|---------------|-----------------------------|---------------------------|
| Cumplimiento  | GDPR, ISO 27001, SOX        | Ver referencias           |
| MFA           | Obligatorio para admins      | Acceso crítico            |
| Cifrado       | `TLS 1.3`, `AES-256`        | Protección de datos en tránsito y reposo |
| Token         | `JWT RS256`                 | Integridad y autenticidad |

## 2.4 Organizacionales Y Operativas

| Área           | Restricción                        | Impacto                  |
|----------------|------------------------------------|--------------------------|
| Operaciones    | DevOps 24/7                        | Soporte continuo         |
| Multi-tenancy  | Aislamiento por `tenant` (`realm`) | Independencia de clientes|
| Documentación  | Arc42 + ADR                        | Trazabilidad de decisiones|
| Automatización | `Terraform`, CI/CD                 | Despliegue seguro y repetible |

## 2.5 Monitoreo Y Observabilidad

| Herramienta   | Propósito                | Integración                |
|---------------|--------------------------|----------------------------|
| `Prometheus`  | Métricas de aplicación   | Exportador Keycloak        |
| `Grafana`     | Visualización            | Dashboards multi-tenant    |
| `Loki`        | Logs centralizados       | Logging estructurado       |
| `Jaeger`      | Trazas distribuidas      | OTLP (`OpenTelemetry`)     |
| `CloudWatch`  | Monitoreo infraestructura| ECS, RDS, ALB              |

## 2.6 Referencias Y Normativas

- [Keycloak Server Installation Guide](https://www.keycloak.org/docs/latest/server_installation/)
- [Keycloak High Availability Guide](https://www.keycloak.org/docs/latest/server_installation/#_clustering)
- [Keycloak Security Hardening](https://www.keycloak.org/docs/latest/server_installation/#_hardening)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [SAML 2.0 Core](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
- [GDPR Regulation (EU) 2016/679](https://gdpr-info.eu/)
- [Sarbanes-Oxley Act (SOX)](https://www.congress.gov/bill/107th-congress/house-bill/3763)
- [ISO/IEC 27001:2013](https://www.iso.org/standard/54534.html)
- [Arc42 - Restricciones](https://docs.arc42.org/section-2/)
- [C4 Model DSL](https://c4model.com/)
- [Structurizr DSL](https://structurizr.com/dsl)
