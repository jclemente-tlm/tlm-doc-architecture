---
title: "ADR-008: Kong API Gateway"
sidebar_position: 8
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de API Gateway para:

- **Enrutamiento inteligente** a microservicios backend (Identity, Notifications, Track & Trace, SITA)
- **Autenticación y autorización centralizada** (`OAuth2`, `JWT`)
- **Rate limiting y throttling** por tenant y endpoint
- **Balanceo de carga y health checks automáticos**
- **Transformación de requests/responses**
- **Observabilidad integrada** (métricas, logs, tracing)
- **Multi-tenancy** con enrutamiento por país/cliente
- **Ecosistema de plugins maduro** para extensibilidad
- **Escalabilidad horizontal** y clustering nativo

La intención estratégica es **maximizar agnosticidad tecnológica**, adoptar estándares de la industria y garantizar capacidades enterprise con soporte comunitario robusto.

Alternativas evaluadas:

- **Kong** (Open source/Enterprise, agnóstico, líder de mercado)
- **AWS API Gateway** (Gestionado AWS, serverless)
- **Azure API Management** (Gestionado Azure, enterprise)
- **Apigee** (Google Cloud, líder enterprise SaaS)
- **YARP (Yet Another Reverse Proxy)** (Microsoft, open source, .NET nativo)
- **Traefik** (Open source, cloud-native)
- **NGINX Plus** (Comercial, agnóstico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                  | Kong                  | AWS API Gateway        | Azure API Management    | Apigee               | YARP              | Traefik           | NGINX Plus           |
| ------------------------- | --------------------- | ---------------------- | ----------------------- | -------------------- | ----------------- | ----------------- | -------------------- |
| **Agnosticidad**          | ✅ Agnóstico          | ❌ Lock-in AWS         | ❌ Lock-in Azure        | ❌ Lock-in GCP       | ⚠️ .NET nativo    | ✅ Agnóstico      | ✅ Agnóstico         |
| **Madurez**               | ✅ Muy alta           | ✅ Muy alta            | ✅ Muy alta             | ✅ Líder enterprise  | ⚠️ Media          | ✅ Alta           | ✅ Muy alta          |
| **Modelo de gestión**     | ⚠️ Self-hosted        | ✅ Gestionado (AWS)    | ✅ Gestionado (Azure)   | ✅ Gestionado (GCP)  | ⚠️ Self-hosted    | ⚠️ Self-hosted    | ⚠️ Self-hosted       |
| **Complejidad operativa** | ⚠️ Media (ECS)        | ✅ Baja (infra AWS)    | ⚠️ Media (vendor nuevo) | ❌ Alta (vendor GCP) | ⚠️ Media (OSS)    | ⚠️ Media (OSS)    | ⚠️ Media (comercial) |
| **Seguridad**             | ✅ Completa           | ✅ IAM/Cognito         | ✅ Azure AD/RBAC        | ✅ Enterprise grade  | ✅ OAuth2/JWT     | ✅ Completa       | ✅ Completa          |
| **Multi-tenancy**         | ✅ Workspaces nativos | ⚠️ Por recursos/stages | ✅ Products/groups      | ✅ Org/Environments  | ⚠️ Manual routing | ⚠️ Por paths      | ⚠️ Manual            |
| **Escalabilidad**         | ✅ Clustering nativo  | ✅ Serverless auto     | ✅ Auto-scaling         | ✅ Global            | ⚠️ Manual con LB  | ✅ K8s/Clustering | ✅ Clustering        |
| **Ecosistema Plugins**    | ✅ Extenso            | ⚠️ AWS integrations    | ✅ Policies extensas    | ✅ Muy completo      | ⚠️ Limitado       | ⚠️ Medio          | ⚠️ Medio             |
| **Observabilidad**        | ✅ Completa           | ✅ CloudWatch          | ✅ App Insights         | ✅ Analytics nativo  | ✅ Nativa .NET    | ✅ Completa       | ✅ Completa          |
| **Comunidad**             | ✅ Muy activa         | ✅ Soporte AWS         | ✅ Soporte Microsoft    | ✅ Soporte Google    | ⚠️ Creciente      | ✅ Activa         | ✅ Activa            |
| **Costos**                | ✅ OSS (+ Enterprise) | ⚠️ Por requests        | ⚠️ Por requests         | ❌ Muy costoso       | ✅ OSS            | ✅ OSS            | ⚠️ Comercial         |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **Kong (OSS)** como solución estándar de API Gateway para todos los servicios corporativos, desplegado en contenedores sobre AWS ECS Fargate, priorizando **agnosticidad tecnológica**, **madurez**, **ecosistema de plugins** y **escalabilidad enterprise**.

### Justificación

- **Agnosticidad total:** no depende de stack tecnológico específico, portable entre clouds y tecnologías
- **Madurez probada:** líder de mercado con millones de implementaciones en producción
- **Ecosistema de plugins extenso:** autenticación (OAuth2, JWT, LDAP), rate limiting, transformaciones, observabilidad
- **Escalabilidad enterprise:** clustering nativo, balanceo distribuido, health checks avanzados
- **Comunidad y soporte:** documentación extensa, comunidad muy activa, opción enterprise disponible
- **Observabilidad integrada:** métricas Prometheus, logs estructurados, tracing distribuido
- **Multi-tenancy nativo:** soporte para workspaces, enrutamiento por tenant
- **Estándar de la industria:** reduce riesgo de lock-in tecnológico

### Alternativas descartadas

- **AWS API Gateway:** lock-in AWS, costos por requests elevados a escala (US$3.50/millón), integración limitada con ecosistema no-AWS, menor flexibilidad para lógica compleja
- **Azure API Management:** lock-in Azure, infraestructura AWS ya establecida (ADR-003, ADR-007), costos premium (US$2.5K/mes tier básico), requiere integración cross-cloud
- **Apigee:** lock-in GCP, **vendor adicional sin infraestructura GCP existente** (requiere cuenta/proyecto/billing GCP activo), **complejidad multi-vendor** (AWS + Azure + GCP) sin beneficio diferencial, **overhead operativo** (tercera consola cloud, tercera facturación, tercer soporte), costos prohibitivos (US$200K+/año enterprise), sobrede-dimensionado para necesidades actuales, complejidad operativa alta
- **YARP:** ecosistema de plugins limitado, acoplamiento con .NET, menor madurez, no cubre casos de uso enterprise complejos
- **Traefik:** buena alternativa pero menor ecosistema de plugins que Kong, menos adopción en casos de uso enterprise complejos
- **NGINX Plus:** costos comerciales elevados (US$2.5K/instancia/año) sin ventajas significativas sobre Kong OSS para casos de uso actuales

---

## ⚠️ CONSECUENCIAS

### Positivas

- ✅ Agnosticidad tecnológica total - portable entre clouds y stacks
- ✅ Ecosistema de plugins maduro reduce desarrollo custom
- ✅ Escalabilidad enterprise probada en producción
- ✅ Observabilidad y seguridad enterprise-grade
- ✅ Comunidad activa y documentación extensa
- ✅ Opción de soporte enterprise si es necesario

### Negativas

- ⚠️ Requiere aprendizaje de configuración Kong (Lua, YAML)
- ⚠️ Complejidad operativa inicial mayor que soluciones .NET nativas
- ⚠️ Costos de infraestructura moderados (US$100K TCO 3 años)

### Mitigaciones

- Capacitación del equipo en Kong y plugins
- Automatización completa con Terraform/IaC
- Documentación interna de patrones y configuraciones
- Monitoreo proactivo de costos

---

## 📚 REFERENCIAS

- [Kong](https://docs.konghq.com/)
- [Kong Plugins Hub](https://docs.konghq.com/hub/)
- [AWS API Gateway](https://aws.amazon.com/api-gateway/)
- [Azure API Management](https://azure.microsoft.com/en-us/services/api-management/)
- [Apigee](https://cloud.google.com/apigee)
- [Traefik](https://doc.traefik.io/traefik/)
- [NGINX Plus](https://www.nginx.com/products/nginx/)
- [YARP](https://microsoft.github.io/reverse-proxy/)
