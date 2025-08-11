# 3. Contexto Y Alcance

![Vista de Contexto](/diagrams/servicios-corporativos/identity_system.png)

*Figura 3.1: Vista de contexto del Servicio de Identidad*

## 3.1 Contexto De Negocio

El Servicio de Identidad centraliza autenticación, autorización y federación para servicios corporativos multipaís, priorizando seguridad, SSO, cumplimiento normativo y eficiencia operativa. La solución es multi-tenant: cada país opera en un `tenant` (`realm`) independiente, garantizando aislamiento y escalabilidad.

| Stakeholder      | Rol                  | Responsabilidad                 | Expectativa                 |
|------------------|----------------------|---------------------------------|-----------------------------|
| CISO             | Seguridad            | Políticas, cumplimiento         | Sistema seguro y auditable  |
| RRHH             | Recursos Humanos     | Gestión de usuarios, onboarding | Proceso eficiente y trazable|
| TI               | Operaciones TI       | Mantenimiento, soporte          | Administración estable y simple |
| Compliance       | Auditoría, regulaciones | Trazabilidad, reportes      | Cumplimiento normativo      |
| Usuarios Finales | Usuarios             | Acceso a aplicaciones           | Experiencia fluida y segura |

## 3.2 Contexto Técnico

```mermaid
graph TD
    subgraph IdPs Externos
        A1[Google Workspace]
        A2[Microsoft AD]
        A3[LDAP Corporativo]
        A4[PKI Gobierno]
    end
    subgraph Tenants (realms)
        T1[Perú]
        T2[Ecuador]
        T3[Colombia]
        T4[México]
    end
    A1 -->|SAML/OIDC| B(Servicio de Identidad - Keycloak)
    A2 -->|SAML/OIDC| B
    A3 -->|LDAP| B
    A4 -->|SAML| B
    B -->|OAuth2/OIDC, JWT| C(API Gateway)
    C -->|Solicitudes autenticadas| D(Ecosistema de Servicios Corporativos)
    D1[Notificaciones]
    D2[Track&Trace]
    D3[Mensajería SITA]
    D4[Aplicaciones Web]
    D --> D1
    D --> D2
    D --> D3
    D --> D4
    B --> T1
    B --> T2
    B --> T3
    B --> T4
```

## 3.3 Fronteras Y Alcance

### Dentro Del Alcance

| Componente                  | Descripción                | Responsabilidad                  |
|-----------------------------|----------------------------|----------------------------------|
| `Keycloak`                  | IdP central multi-tenant   | Autenticación, autorización, gestión de usuarios |
| Gestión de Tenants (`realms`)| Aislamiento por país      | Multi-tenant, configuración      |
| Federación de Usuarios      | Integración IdP externos   | `LDAP`, `SAML`, `OIDC`           |
| Gestión de Tokens           | Ciclo de vida `JWT`        | Generación, validación, renovación|
| Consola de Administración   | Interfaz de gestión        | Administración usuarios/roles    |
| APIs Programáticas          | APIs REST                  | Gestión programática de usuarios |
| Auditoría y Logging         | Eventos de seguridad       | Rastro de auditoría completo     |

### Fuera Del Alcance

| Componente                  | Razón de Exclusión         | Responsable                      |
|-----------------------------|----------------------------|----------------------------------|
| IdPs Externos               | Sistemas de terceros       | Google, Microsoft, TI            |
| Aplicaciones Cliente        | Consumidores de servicios  | Equipos de servicios             |
| Infraestructura de Red      | Capa de infraestructura    | Equipo de infraestructura        |
| Gestión de Certificados     | Infraestructura PKI        | Equipo de seguridad              |
| Plataforma de Monitoreo     | Observabilidad             | Equipo DevOps                    |

## 3.4 Interfaces Externas

| Actor                        | Tipo    | Descripción                        | Interacciones                                 |
|------------------------------|---------|------------------------------------|-----------------------------------------------|
| Administrador Global         | Humano  | Admin global                       | Configuración de tenants (`realms`), políticas|
| Administrador de Tenant (`realm`)| Humano  | Admin por país/tenant (`realm`)    | Gestión de usuarios, roles específicos        |
| Usuario Final                | Humano  | Usuario final                      | Login, gestión de perfil, reset pass          |
| API Gateway                  | Sistema | Proxy de servicios                 | Validación de token, contexto usuario         |
| Servicios Corporativos       | Sistema | Servicios de negocio               | Autenticación, autorización                   |
| IdP Externo                  | Sistema | Proveedores de identidad externos  | Federación de usuarios, SSO                   |
| Sistema HRIS                 | Sistema | Recursos humanos                   | Provisioning de usuarios, roles               |
| Sistema de Monitoreo         | Sistema | Observabilidad                     | Métricas, logs, health checks                 |

## Referencias

- [Arc42 Context Template](https://docs.arc42.org/section-3/)
- [C4 Model for Software Architecture](https://c4model.com/)
- [Keycloak Server Administration Guide](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak Securing Applications Guide](https://www.keycloak.org/docs/latest/securing_apps/)
- [OAuth 2.0 Authorization Framework (RFC 6749)](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [SAML 2.0 Core Specification](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
