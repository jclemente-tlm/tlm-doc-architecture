---
title: "ADR-010: Kong API Gateway"
sidebar_position: 10
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

| Criterio                          | Kong                                      | AWS API Gateway                          | Azure API Management            | Apigee                          | YARP                        | Traefik                        | NGINX Plus                    |
| --------------------------------- | ----------------------------------------- | ---------------------------------------- | ------------------------------- | ------------------------------- | --------------------------- | ------------------------------ | ----------------------------- |
| **Agnosticidad**                  | ✅ Agnóstico                              | ❌ Lock-in AWS                           | ❌ Lock-in Azure                | ❌ Lock-in GCP                  | ⚠️ .NET nativo              | ✅ Agnóstico                   | ✅ Agnóstico                  |
| **Madurez**                       | ✅ Muy alta (2015, OSS estable)           | ✅ Muy alta (2015, AWS std)              | ✅ Muy alta (2016, Azure std)   | ✅ Muy alta (2004, enterprise)  | ⚠️ Media (2020, reciente)   | ✅ Alta (2015, CNCF)           | ✅ Muy alta (2004, comercial) |
| **Adopción**                      | ✅ Muy alta (39K⭐, líder OSS)            | ✅ Muy alta (AWS standard)               | ✅ Muy alta (Azure std)         | ✅ Muy alta (GCP enterprise)    | ⚠️ Media (.NET ecosystem)   | ✅ Alta (50K⭐, cloud-native)  | ✅ Muy alta (comercial cases) |
| **Modelo de gestión**             | ⚠️ Self-hosted                            | ✅ Gestionado (AWS)                      | ✅ Gestionado (Azure)           | ✅ Gestionado (GCP)             | ⚠️ Self-hosted              | ⚠️ Self-hosted                 | ⚠️ Self-hosted                |
| **Complejidad operativa**         | ⚠️ Alta (1 FTE, 10-20h/sem)               | ✅ Baja (0.25 FTE, `<5h/sem)`              | ⚠️ Media (0.5 FTE, 5-10h/sem)   | ⚠️ Alta (1 FTE, 10-20h/sem)     | ⚠️ Alta (1 FTE, 10-20h/sem) | ⚠️ Alta (1 FTE, 10-20h/sem)    | ⚠️ Media (0.5 FTE, 5-10h/sem) |
| **Seguridad**                     | ✅ Completa                               | ✅ IAM/Cognito                           | ✅ Azure AD/RBAC                | ✅ Enterprise grade             | ✅ OAuth2/JWT               | ✅ Completa                    | ✅ Completa                   |
| **Multi-tenancy**                 | ✅ Workspaces nativos                     | ⚠️ Por recursos/stages                   | ✅ Products/groups              | ✅ Org/Environments             | ⚠️ Manual routing           | ⚠️ Por paths                   | ⚠️ Manual                     |
| **Latencia**                      | ✅ p95 `<10ms `                             | ✅ p95 `<100ms `                           | ✅ p95 `<50ms `                   | ✅ p95 `<50ms `                   | ✅ p95 `<5ms `                | ✅ p95 `<10ms `                  | ✅ p95 `<5ms `                  |
| **Rendimiento**                   | ✅ 10K+ req/seg                           | ⚠️ 5K-10K req/seg                        | ✅ 10K+ req/seg                 | ✅ 10K+ req/seg                 | ✅ 50K+ req/seg (.NET perf) | ✅ 10K+ req/seg                | ✅ 20K+ req/seg               |
| **Escalabilidad**                 | ✅ Hasta 100K+ req/seg (Netflix)          | ✅ Millones req/seg máx (AWS serverless) | ✅ Hasta 50K+ req/seg (Azure)   | ✅ 200K+ req/seg (Google)       | ⚠️ Hasta 20K req/seg máx    | ✅ Hasta 30K+ req/seg (Lyft)   | ✅ Hasta 40K+ req/seg (Tyk)   |
| **Ecosistema Plugins**            | ✅ Extenso                                | ⚠️ AWS integrations                      | ✅ Policies extensas            | ✅ Muy completo                 | ⚠️ Limitado                 | ⚠️ Medio                       | ⚠️ Medio                      |
| **Rate Limiting**                 | ✅ Local, cluster, Redis (sliding window) | ✅ Request/burst quotas (AWS)            | ✅ Rate, quota policies         | ✅ Quota, spike arrest          | ⚠️ Custom implementation    | ✅ Token bucket, sliding       | ✅ Request rate limiting      |
| **Capacidades de transformación** | ✅ Request/response transform plugins     | ⚠️ VTL templates (limitado)              | ✅ Policies set-header, rewrite | ✅ Mediation policies (XSLT)    | ✅ Custom middleware        | ⚠️ Middleware (limitado)       | ✅ Lua scripting, njs         |
| **Circuit Breaker**               | ✅ Proxy-cache, circuit-breaker plugins   | ⚠️ Manual Lambda implementation          | ✅ Circuit breaker policy       | ✅ Fault handling               | ⚠️ Custom implementation    | ⚠️ Retry plugin (limitado)     | ⚠️ Manual config              |
| **Soporte de protocolos**         | ✅ HTTP/1.1, HTTP/2, gRPC, WebSocket      | ✅ HTTP/1.1, HTTP/2, WebSocket           | ✅ HTTP/1.1, HTTP/2, SOAP       | ✅ HTTP/1.1, HTTP/2, gRPC, SOAP | ✅ HTTP/1.1, HTTP/2, gRPC   | ✅ HTTP/1.1, HTTP/2, gRPC, TCP | ✅ HTTP/1.1, HTTP/2, gRPC     |
| **Caché**                         | ✅ Proxy-cache (Redis, memory)            | ⚠️ External API Gateway cache            | ✅ External/internal cache      | ✅ Response cache               | ⚠️ Custom ASP.NET cache     | ⚠️ No cache nativo             | ✅ FastCGI, proxy cache       |
| **Costos**                        | ✅ $0 licencia + ~$100-200/mes infra      | ⚠️ $3.50/millón requests (~$100-500/mes) | ⚠️ $2.5K-15K/mes (según tier)   | ❌ $200K+/año enterprise        | ✅ $0 licencia              | ✅ $0 licencia                 | ⚠️ $2.5K/instancia/año        |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **Kong (OSS)** como solución estándar de API Gateway para todos los servicios corporativos, desplegado en contenedores sobre AWS ECS Fargate, priorizando **agnosticidad tecnológica**, **madurez**, **ecosistema de plugins** y **escalabilidad enterprise**.

### Justificación

- **Agnosticidad total:** no depende de stack tecnológico específico, portable entre clouds y tecnologías
- **Madurez probada:** líder de mercado con millones de implementaciones en producción
- **Ecosistema de plugins extenso:** autenticación (OAuth2, JWT, LDAP), rate limiting, transformaciones, monitoreo
- **Escalabilidad enterprise:** clustering nativo, balanceo distribuido, health checks avanzados
- **Comunidad y soporte:** documentación extensa, comunidad muy activa, opción enterprise disponible
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
- ✅ Seguridad enterprise-grade con múltiples métodos de autenticación
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
