# 1. Introducción Y Objetivos

El Servicio de Identidad proporciona autenticación, autorización y federación centralizada para servicios corporativos multipaís, con aislamiento multi-tenant (`tenant`/`realm` por país), integración con sistemas cloud y legacy, y cumplimiento normativo internacional. Facilita la gestión de usuarios, autenticación federada, control de acceso basado en roles y cumplimiento regulatorio de forma segura y escalable.

## 1.1 Funcionalidades Clave

| Funcionalidad   | Descripción breve                                                      |
|-----------------|------------------------------------------------------------------------|
| SSO             | Acceso unificado a aplicaciones (`OAuth2`/`OIDC`, `JWT`)               |
| Multi-tenancy   | Aislamiento y gestión por `tenant` (`realm`)                           |
| Federación      | Integración con IdPs externos (`SAML`, `OIDC`, `LDAP`)                 |
| RBAC            | Control de acceso basado en roles                                      |
| MFA             | Autenticación multi-factor para roles críticos                         |
| Auditoría       | Registro estructurado de eventos                                       |
| Observabilidad  | Métricas, trazas y logs centralizados                                  |
| API Gateway     | Validación de tokens y forwarding seguro                               |

## 1.2 Atributos De Calidad

| Atributo       | Objetivo             | Métrica           |
|----------------|---------------------|-------------------|
| Disponibilidad | Alta disponibilidad | `99.9% uptime`    |
| Rendimiento    | Baja latencia       | `p95 < 200ms`     |
| Escalabilidad  | Soporte masivo      | `10,000+ usuarios`|
| Seguridad      | Zero trust, GDPR    | `100% auditado`   |
| Usabilidad     | SSO fluido          | `< 3 clics acceso`|

## 1.3 Tipos De Usuarios Y Roles

| Tipo de Usuario      | Descripción                  | Roles Típicos           | MFA                |
|----------------------|-----------------------------|-------------------------|---------------------|
| Operadores           | Operativo aeroportuario      | Operador, Supervisor    | No                  |
| Gestores             | Gestión y administración     | Gestor, Administrador   | Sí                  |
| Personal de TI       | Técnico y desarrollo         | Desarrollador, SysAdmin | Sí                  |
| Directivos           | Alta gerencia                | Directivo, C-Level      | Sí                  |
| Socios Externos      | Aerolíneas, proveedores      | Socio-Lectura, Escritura| Sí                  |
| Cuentas de Servicio  | Servicios/APIs               | Sistema, Integración    | No (certificado)    |

## 1.4 Stakeholders

| Rol                      | Responsabilidades                | Expectativas                  |
|--------------------------|----------------------------------|-------------------------------|
| CISO                     | Políticas, cumplimiento          | Seguridad robusta             |
| Directores de RRHH       | Ciclo de vida de usuarios        | Gestión simple, roles correctos|
| Directores de TI         | Estándares técnicos, infraestructura | Servicio confiable        |
| Oficiales de Cumplimiento| Cumplimiento regulatorio         | Auditoría completa            |
| Gerentes de Operaciones  | Acceso diario, productividad     | Autenticación rápida          |

## 1.5 Referencias

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth 2.1 Security Mejores Prácticas](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [Arc42 - Introducción y objetivos](https://docs.arc42.org/section-1/)
- [C4 Model - Context & Container](https://c4model.com/)
- [Structurizr DSL](https://structurizr.com/dsl)
