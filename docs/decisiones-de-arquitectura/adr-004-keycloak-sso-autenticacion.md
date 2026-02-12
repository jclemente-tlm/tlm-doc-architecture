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
- **Auth0** (SaaS, gestionado)
- **AWS Cognito** (gestionado AWS)
- **Azure AD B2C** (gestionado Azure)
- **Google Identity Platform** (gestionado GCP)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | Keycloak                    | Auth0                    | AWS Cognito              | Azure AD B2C             | Google IdP               |
| ------------------- | --------------------------- | ------------------------ | ------------------------ | ------------------------ | ------------------------ |
| **Agnosticidad**    | ❌ Lock-in OSS              | ⚠️ SaaS independiente    | ❌ Lock-in AWS           | ❌ Lock-in Azure         | ❌ Lock-in GCP           |
| **Operación**       | ⚠️ Requiere gestión         | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado |
| **Seguridad**       | ✅ Enterprise grade         | ✅ Enterprise grade      | ✅ Enterprise grade      | ✅ Enterprise grade      | ✅ Enterprise grade      |
| **Multi-tenancy**   | ✅ Nativo y flexible        | ✅ Excelente soporte     | ⚠️ Básico                | ✅ Muy bueno             | ⚠️ Básico                |
| **Protocolos**      | ✅ Todos los estándares     | ✅ Completo              | ⚠️ Limitado              | ✅ Completo              | ⚠️ Limitado              |
| **Personalización** | ✅ Altamente personalizable | ⚠️ Limitada              | ⚠️ Muy limitada          | ⚠️ Limitada              | ⚠️ Muy limitada          |
| **Costos**          | ✅ Solo infraestructura     | ⚠️ Por usuario activo    | ⚠️ Por usuario activo    | ⚠️ Por usuario activo    | ⚠️ Por usuario activo    |

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

- **Auth0:** Costos altos y lock-in SaaS
- **AWS Cognito:** Limitada integración y lock-in AWS
- **Azure AD B2C:** Limitada integración y lock-in Azure
- **Google IdP:** Limitada integración y lock-in GCP

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
- [Multi-tenancy with Keycloak Realms](https://www.keycloak.org/docs/latest/server_admin/#_realms)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_clustering)
- [OAuth2 and OIDC Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

---

**Decisión tomada por:** Equipo de Arquitectura + CISO
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
