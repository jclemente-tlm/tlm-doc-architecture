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

| Criterio                  | Keycloak                                            | Auth0                                           | AWS Cognito                                     | Azure AD B2C                                | Google Identity Platform                    |
| ------------------------- | --------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------- | ------------------------------------------- | ------------------------------------------- |
| **Agnosticidad**          | ✅ OSS, portátil                                    | ⚠️ SaaS independiente                           | ❌ Lock-in AWS                                  | ❌ Lock-in Azure                            | ❌ Lock-in GCP                              |
| **Madurez**               | ✅ Muy alta (2014, producción estable)              | ✅ Muy alta (líder SaaS)                        | ✅ Alta (2016, AWS ecosystem)                   | ✅ Muy alta (Microsoft AD legacy)           | ⚠️ Media (2017, Firebase integration)       |
| **Adopción**              | ✅ Muy alta (21K⭐, Red Hat cases)                  | ✅ Muy alta (15K+ empresas)                     | ✅ Alta (AWS adoption)                          | ✅ Muy alta (Microsoft enterprise)          | ⚠️ Media (Firebase focus)                   |
| **Modelo de gestión**     | ⚠️ Self-hosted                                      | ✅ Gestionado (SaaS)                            | ✅ Gestionado (AWS)                             | ✅ Gestionado (Azure)                       | ✅ Gestionado (GCP)                         |
| **Complejidad operativa** | ⚠️ Alta (1 FTE, 10-20h/sem)                         | ✅ Baja (0.25 FTE, <5h/sem)                     | ✅ Baja (0.25 FTE, <5h/sem)                     | ⚠️ Media (0.5 FTE, 5-10h/sem)               | ⚠️ Alta (1 FTE, 10-20h/sem)                 |
| **Seguridad**             | ✅ Enterprise grade                                 | ✅ Enterprise grade                             | ✅ Enterprise grade                             | ✅ Enterprise grade                         | ✅ Enterprise grade                         |
| **Integración .NET**      | ✅ Keycloak.AuthServices.\* (100K+ DL/mes, .NET 6+) | ✅ Auth0.AspNetCore.Authentication (2M+ DL/mes) | ✅ AWSSDK.CognitoIdentityProvider (10M+ DL/mes) | ✅ Azure.Identity + MSAL (10M+ DL/mes cada) | ⚠️ Google.Cloud.IdentityPlatform (limitado) |
| **Multi-tenancy**         | ✅ Nativo y flexible                                | ✅ Excelente soporte                            | ⚠️ Básico                                       | ✅ Muy bueno                                | ⚠️ Básico                                   |
| **Escalabilidad**         | ✅ Hasta 100K+ usuarios concurrentes (Red Hat)      | ✅ Millones usuarios máx (SaaS global)          | ✅ Hasta 100M+ usuarios (Amazon scale)          | ✅ Millones usuarios máx (Microsoft)        | ✅ Hasta 100M+ usuarios (Google scale)      |
| **Rendimiento**           | ✅ <50ms p95 (local cache)                          | ✅ <100ms p95                                   | ✅ <100ms p95                                   | ✅ <150ms p95                               | ⚠️ 100-300ms variable                       |
| **Alta disponibilidad**   | ✅ 99.9% estimado (clustering multi-nodo)           | ✅ 99.99% SLA                                   | ✅ 99.99% SLA Multi-AZ                          | ✅ 99.99% SLA                               | ✅ 99.9% SLA Multi-region                   |
| **Protocolos**            | ✅ Todos los estándares                             | ✅ Completo                                     | ⚠️ Limitado                                     | ✅ Completo                                 | ⚠️ Limitado                                 |
| **Federación**            | ✅ SAML, OIDC, LDAP                                 | ✅ Social + Enterprise                          | ⚠️ Limitada                                     | ✅ AD completo                              | ⚠️ Limitada                                 |
| **Personalización**       | ✅ Altamente personalizable                         | ⚠️ Limitada                                     | ⚠️ Muy limitada                                 | ⚠️ Limitada                                 | ⚠️ Muy limitada                             |
| **Costos**                | ✅ $0 licencia + ~$150-300/mes infra                | ❌ $23-240/mes + por usuario                    | ✅ Gratis (50K MAU/mes) + $0.0055/MAU           | ✅ Gratis (50K MAU/mes) + $0.00325/MAU      | ✅ Gratis (50K MAU/mes) + $0.00275/MAU      |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **Keycloak** como solución para la gestión de identidades y autenticación centralizada en todos los entornos del sistema corporativo.

### Justificación

- Integración nativa con protocolos estándar y ecosistema `.NET`
- Multi-tenancy robusto con aislamiento por país (`tenant (realm)`)
- Personalización total de flujos y UI
- Costos predecibles y control total de datos
- Portabilidad y despliegue en cualquier cloud/on-premises
- Menor complejidad operativa frente a SaaS, con control total

### Alternativas descartadas

- **Auth0:** costos altos (US$23-240/mes base + usuarios), lock-in SaaS, personalización limitada
- **AWS Cognito:** limitaciones en protocolos (sin SAML completo), lock-in AWS, multi-tenancy básico
- **Azure AD B2C:** lock-in Azure, infraestructura AWS ya establecida, integración menos fluida
- **Google Identity Platform:** lock-in GCP, **vendor adicional sin infraestructura GCP existente** (requiere cuenta/proyecto/billing GCP activo), **SDK .NET adicional** (Google.Cloud.IdentityPlatform) a mantener, **complejidad multi-vendor** (AWS + Azure + GCP) sin beneficio diferencial, **overhead operativo** (tercera consola cloud, tercera facturación, tercer soporte), capacidades multi-tenancy limitadas, menor adopción enterprise

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
- [Auth0](https://auth0.com/)
- [Multi-tenancy with Keycloak Realms](https://www.keycloak.org/docs/latest/server_admin/#_realms)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_clustering)
- [OAuth2 and OIDC Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

---

**Decisión tomada por:** Equipo de Arquitectura + CISO
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
