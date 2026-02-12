---
title: "ADR-004: Keycloak SSO Autenticación"
sidebar_position: 4
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de gestión de identidades para:

- **Autenticación centralizada (SSO) para todos los servicios**
- **Multi-tenancy** para operaciones en Perú, Ecuador, Colombia y México
- **Protocolos estándar (OAuth2, OIDC, SAML) para integración**
- **Federación con proveedores externos corporativos**
- **Escalabilidad para miles de usuarios concurrentes**
- **Portabilidad entre clouds y on-premises**

La intención estratégica es mantener agnosticidad y evitar lock-in con proveedores cloud específicos.

Las alternativas evaluadas fueron:

- **Keycloak** (open source, agnóstico)
- **Okta** (líder SaaS identity, enterprise)
- **FusionAuth** (OSS alternativa moderna)
- **Auth0** (SaaS, gestionado)
- **AWS Cognito** (gestionado AWS)
- **Azure AD B2C** (gestionado Azure)
- **Google Identity Platform** (gestionado GCP)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | Keycloak                    | Okta                     | FusionAuth               | Auth0                    | AWS Cognito              | Azure AD B2C             | Google IdP               |
| ------------------- | --------------------------- | ------------------------ | ------------------------ | ------------------------ | ------------------------ | ------------------------ | ------------------------ |
| **Agnosticidad**    | ✅ OSS, portátil            | ⚠️ SaaS independiente    | ✅ OSS, portátil         | ⚠️ SaaS independiente    | ❌ Lock-in AWS           | ❌ Lock-in Azure         | ❌ Lock-in GCP           |
| **Operación**       | ⚠️ Requiere gestión         | ✅ Totalmente gestionado | ⚠️ Requiere gestión      | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado |
| **Seguridad**       | ✅ Enterprise grade         | ✅ Líder mercado         | ✅ Enterprise grade      | ✅ Enterprise grade      | ✅ Enterprise grade      | ✅ Enterprise grade      | ✅ Enterprise grade      |
| **Multi-tenancy**   | ✅ Nativo y flexible        | ✅ Excelente soporte     | ✅ Nativo y flexible     | ✅ Excelente soporte     | ⚠️ Básico                | ✅ Muy bueno             | ⚠️ Básico                |
| **Protocolos**      | ✅ Todos los estándares     | ✅ Completo              | ✅ Todos los estándares  | ✅ Completo              | ⚠️ Limitado              | ✅ Completo              | ⚠️ Limitado              |
| **Personalización** | ✅ Altamente personalizable | ⚠️ Limitada              | ✅ Altamente flexible    | ⚠️ Limitada              | ⚠️ Muy limitada          | ⚠️ Limitada              | ⚠️ Muy limitada          |
| **Comunidad**       | ✅ Muy activa (21K⭐)       | ✅ Enterprise líder      | ✅ Activa (6K⭐)         | ✅ Enterprise            | ✅ Soporte AWS           | ✅ Soporte Microsoft     | ✅ Soporte Google        |
| **Costos**          | ✅ Solo infraestructura     | ❌ Enterprise costoso    | ✅ Community + comercial | ⚠️ Por usuario activo    | ⚠️ Por usuario activo    | ⚠️ Por usuario activo    | ⚠️ Por usuario activo    |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **Keycloak** como solución para la gestión de identidades y autenticación centralizada en todos los entornos del sistema corporativo.

## Justificación

- Integración nativa con protocolos estándar y ecosistema `.NET`
- Multi-tenancy robusto con aislamiento por país (`tenant (realm)`)
- Personalización total de flujos y UI
- Costos predecibles y control total de datos
- Portabilidad y despliegue en cualquier cloud/on-premises
- Menor complejidad operativa frente a SaaS, con control total

## Alternativas descartadas

- **Okta:** costos enterprise prohibitivos (US$2-15/usuario/mes = US$24K-180K/año para 1K usuarios), lock-in SaaS, menor control sobre datos sensibles
- **FusionAuth:** menor madurez vs Keycloak (2018 vs 2014), comunidad más pequeña, ecosistema de plugins limitado
- **Auth0:** costos altos (US$23-240/mes base + usuarios), lock-in SaaS, personalización limitada
- **AWS Cognito:** limitaciones en protocolos (sin SAML completo), lock-in AWS, multi-tenancy básico
- **Azure AD B2C:** lock-in Azure, infraestructura AWS ya establecida, integración menos fluida
- **Google IdP:** lock-in GCP, capacidades multi-tenancy limitadas, menor adopción enterprise

---

## ⚠️ CONSECUENCIAS

### Positivas

- El ciclo de vida de identidades será gestionado exclusivamente en Keycloak.
- Las aplicaciones y microservicios deben validar JWT y claims emitidos por Keycloak.
- Se documentará el uso y acceso en los manuales de operación y seguridad.

### Negativas (Riesgos y Mitigaciones)

- **Complejidad operacional:** mitigada con contenedores y automatización.
- **Gestión de actualizaciones:** gestionada con CI/CD y testing automatizado.
- **Curva de aprendizaje:** mitigada con capacitación y documentación.

---

## 📚 REFERENCIAS

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [Okta Identity Cloud](https://www.okta.com/)
- [FusionAuth](https://fusionauth.io/)
- [Auth0](https://auth0.com/)
- [Multi-tenancy with Keycloak Realms](https://www.keycloak.org/docs/latest/server_admin/#_realms)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_clustering)
- [OAuth2 and OIDC Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

---

**Decisión tomada por:** Equipo de Arquitectura + CISO
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
