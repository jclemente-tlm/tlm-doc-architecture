---
id: adr-004-autenticacion-sso
title: "Autenticación mediante SSO"
sidebar_position: 4
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de gestión de identidades que soporte:

- **Autenticación centralizada** (SSO) para todos los servicios
- **Multi-tenancy** para operaciones en Perú, Ecuador, Colombia y México
- **Protocolos estándar** (OAuth2, OIDC, SAML) para integración
- **Federación** con proveedores externos corporativos
- **Escalabilidad** para miles de usuarios concurrentes
- **Portabilidad** entre clouds y on-premises

La intención estratégica es **mantenerse agnóstico** y evitar lock-in con proveedores cloud específicos.

Las alternativas evaluadas fueron:

- **Keycloak** (Open source, Red Hat, agnóstico)
- **Auth0** (SaaS, Okta, gestionado)
- **AWS Cognito** (Gestionado AWS, lock-in)
- **Azure AD B2C** (Gestionado Azure, lock-in)
- **Google Identity Platform** (Gestionado GCP, lock-in)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | Keycloak | Auth0 | AWS Cognito | Azure AD B2C | Google IdP |
|----------|----------|-------|-------------|--------------|------------|
| **Agnosticidad** | ✅ Totalmente agnóstico | 🟡 SaaS independiente | ❌ Lock-in AWS | ❌ Lock-in Azure | ❌ Lock-in GCP |
| **Multi-tenancy** | ✅ Nativo y flexible | ✅ Excelente soporte | 🟡 Básico | ✅ Muy bueno | 🟡 Básico |
| **Protocolos** | ✅ Todos los estándares | ✅ Completo | 🟡 Limitado | ✅ Completo | 🟡 Limitado |
| **Operación** | 🟡 Requiere gestión | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado | ✅ Totalmente gestionado |
| **Personalización** | ✅ Altamente personalizable | 🟡 Limitada | 🟡 Muy limitada | 🟡 Limitada | 🟡 Muy limitada |
| **Costos** | ✅ Solo infraestructura | 🟡 Por usuario activo | 🟡 Por usuario activo | 🟡 Por usuario activo | 🟡 Por usuario activo |

### Matriz de Decisión

| Solución | Agnosticidad | Operación | Costos | Multi-tenancy | Recomendación |
|----------|--------------|-----------|--------|---------------|---------------|
| **Keycloak** | Excelente | Manual | Bajo | Excelente | ✅ **Seleccionada** |
| **Auth0** | Buena | Automática | Alto | Excelente | 🟡 Alternativa |
| **AWS Cognito** | Mala | Automática | Medio | Limitada | ❌ Descartada |
| **Azure AD B2C** | Mala | Automática | Medio | Buena | ❌ Descartada |
| **Google IdP** | Mala | Automática | Medio | Limitada | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 10,000 usuarios activos, 4 países

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **Keycloak** | US$0 (OSS) | US$3,600/año | US$48,000/año | **US$154,800** |
| **Auth0** | US$23/usuario/mes | US$0 | US$12,000/año | **US$864,000** |
| **AWS Cognito** | US$0.0055/MAU | US$0 | US$0 | **US$1,980/año** |
| **Azure AD B2C** | US$0.00325/MAU | US$0 | US$0 | **US$1,170/año** |
| **Google IdP** | US$0.006/MAU | US$0 | US$0 | **US$2,160/año** |

### Escenario Alto Volumen: 50,000 usuarios activos

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| **Keycloak** | **US$240,000** | Lineal con infra |
| **Auth0** | **US$4,140,000** | Automática |
| **AWS Cognito** | **US$9,900** | Automática |
| **Azure AD B2C** | **US$5,850** | Automática |
| **Google IdP** | **US$10,800** | Automática |

## ⚖️ DECISIÓN

**Seleccionamos Keycloak** como proveedor de identidad por:

### Ventajas Clave

- **Máxima agnosticidad**: Deployable en cualquier cloud/on-premises
- **Multi-tenancy robusto**: Realms nativos para separación por país
- **Protocolos completos**: OAuth2, OIDC, SAML 2.0 out-of-the-box
- **Personalización total**: Temas, flujos, extensiones personalizadas
- **Costo predecible**: Sin sorpresas por crecimiento de usuarios
- **Control total**: Datos y configuración bajo control corporativo

### Mitigación de Desventajas

- **Complejidad operacional**: Mitigada con contenedores y automatización
- **Responsabilidad de updates**: Gestionada con CI/CD y testing automatizado
- **Escalabilidad manual**: Planificada con métricas y auto-scaling

### Configuración Multi-tenant

```yaml
Realms por País:
- talma-peru: Usuarios y aplicaciones de Perú
- talma-ecuador: Usuarios y aplicaciones de Ecuador
- talma-colombia: Usuarios y aplicaciones de Colombia
- talma-mexico: Usuarios y aplicaciones de México
```

## 🔄 CONSECUENCIAS

### Positivas

- ✅ **Portabilidad completa** sin dependencias de proveedor
- ✅ **Multi-tenancy nativo** con aislamiento por país
- ✅ **Personalización ilimitada** de flujos y UI
- ✅ **Costos predecibles** independientes del crecimiento
- ✅ **Cumplimiento regulatorio** con control total de datos
- ✅ **Ecosistema .NET** excelente con librerías oficiales

### Negativas

- ❌ **Mayor responsabilidad operacional** requiere expertise
- ❌ **Gestión de actualizaciones** y parches manual
- ❌ **Configuración inicial compleja** para multi-tenancy

### Neutras

- 🔄 **Curva de aprendizaje** inicial pero conocimiento reutilizable
- 🔄 **Monitoreo especializado** requerido pero estándar

## 🏗️ ARQUITECTURA DE DESPLIEGUE

### Configuración de Alta Disponibilidad

```yaml
Keycloak Cluster:
  Instancias: 3 (multi-AZ)
  Load Balancer: YARP/ALB
  Base de Datos: PostgreSQL (replicado)
  Cache: Redis (cluster)
  Sesiones: Sticky sessions + DB persistence
```

### Integración con Servicios

```yaml
Servicios Corporativos:
  API Gateway: OIDC Client + JWT validation
  Notification: Service-to-service OAuth2
  Track & Trace: JWT bearer tokens
  SITA Messaging: Client credentials flow
```

## 📚 REFERENCIAS

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [Multi-tenancy with Keycloak Realms](https://www.keycloak.org/docs/latest/server_admin/#_realms)
- [Keycloak Performance Tuning](https://www.keycloak.org/docs/latest/server_installation/#_clustering)
- [OAuth2 and OIDC Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

---

**Decisión tomada por:** Equipo de Arquitectura + CISO
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
