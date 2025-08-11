---
id: adr-004-autenticacion-sso
title: "Autenticación Centralizada SSO y Multi-Tenancy"
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

| Criterio | Keycloak | Auth0 | AWS Cognito | Azure AD B2C | Google IdP |
|----------|----------|-------|-------------|--------------|------------|
| **Agnosticidad** | ❌ Lock-in OSS | 🟡 SaaS independiente | ❌ Lock-in AWS | ❌ Lock-in Azure | ❌ Lock-in GCP |
| **Operación** | 🟡 Requiere gestión | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado |
| **Seguridad** | ✅ Enterprise grade | ✅ Enterprise grade | ✅ Enterprise grade | ✅ Enterprise grade | ✅ Enterprise grade |
| **Multi-tenancy** | ✅ Nativo y flexible | ✅ Excelente soporte | 🟡 Básico | ✅ Muy bueno | 🟡 Básico |
| **Protocolos** | ✅ Todos los estándares | ✅ Completo | 🟡 Limitado | ✅ Completo | 🟡 Limitado |
| **Personalización** | ✅ Altamente personalizable | 🟡 Limitada | 🟡 Muy limitada | 🟡 Limitada | 🟡 Muy limitada |
| **Costos** | ✅ Solo infraestructura | 🟡 Por usuario activo | 🟡 Por usuario activo | 🟡 Por usuario activo | 🟡 Por usuario activo |

### Matriz de Decisión

| Solución | Agnosticidad | Operación | Seguridad | Multi-tenancy | Recomendación |
|----------|--------------|-----------|-----------|---------------|---------------|
| **Keycloak** | Mala | Manual | Excelente | Excelente | ✅ **Seleccionada** |
| **Auth0** | Mala | Excelente | Excelente | Excelente | 🟡 Alternativa |
| **AWS Cognito** | Mala | Excelente | Excelente | Limitada | ❌ Descartada |
| **Azure AD B2C** | Mala | Excelente | Excelente | Buena | ❌ Descartada |
| **Google IdP** | Mala | Excelente | Excelente | Limitada | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario de referencia: 10,000 usuarios activos, 4 países

> **Metodología y supuestos:** Se asume un uso promedio de 10,000 usuarios activos, 4 países, considerando operación, escalabilidad y personalización. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según el crecimiento de usuarios y la infraestructura.

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|----------------|-----------|------------|
| Keycloak | US$0 (OSS) | US$3,600/año | US$48,000/año | US$154,800 |
| Auth0 | US$23/usuario/mes | US$0 | US$12,000/año | US$864,000 |
| AWS Cognito | US$0.0055/MAU | US$0 | US$0 | US$1,980/año |
| Azure AD B2C | US$0.00325/MAU | US$0 | US$0 | US$1,170/año |
| Google IdP | US$0.006/MAU | US$0 | US$0 | US$2,160/año |

### Escenario Alto Volumen: 50,000 usuarios activos

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| Keycloak | US$240,000 | Lineal con infraestructura |
| Auth0 | US$4,140,000 | Automática |
| AWS Cognito | US$9,900 | Automática |
| Azure AD B2C | US$5,850 | Automática |
| Google IdP | US$10,800 | Automática |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **Keycloak:** Sin límite práctico de usuarios, escalabilidad horizontal, personalización total.
- **Auth0/AWS Cognito/Azure AD B2C/Google IdP:** Límite por usuario activo, escalabilidad automática, personalización limitada.

### Riesgos y mitigación

- **Complejidad operacional:** mitigada con contenedores y automatización.
- **Gestión de actualizaciones:** gestionada con CI/CD y testing automatizado.
- **Curva de aprendizaje:** mitigada con capacitación y documentación.

---

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

- El ciclo de vida de identidades será gestionado exclusivamente en Keycloak.
- Las aplicaciones y microservicios deben validar JWT y claims emitidos por Keycloak.
- Se documentará el uso y acceso en los manuales de operación y seguridad.
- Se implementarán las mitigaciones descritas y un plan de revisión anual.

---

## 🏗️ ARQUITECTURA DE DESPLIEGUE

- Cluster Keycloak: 3 instancias multi-AZ
- Load Balancer: `YARP`/ALB
- Base de datos: `PostgreSQL` replicado
- Cache: `Redis` cluster
- Sesiones: sticky sessions + persistencia en base de datos
- Realms por país: `talma-peru`, `talma-ecuador`, `talma-colombia`, `talma-mexico`

### Integración con servicios

- API Gateway: OIDC Client + validación de JWT
- Notification: OAuth2 service-to-service
- Track & Trace: JWT bearer tokens
- SITA Messaging: Client credentials flow

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
