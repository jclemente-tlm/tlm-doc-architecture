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
- **YARP (Yet Another Reverse Proxy)** (Microsoft, open source, .NET nativo)
- **Traefik** (Open source, cloud-native)
- **NGINX Plus** (Comercial, agnóstico)
- **Ocelot** (Open source, .NET específico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio               | Kong                  | YARP             | Traefik           | NGINX Plus    | Ocelot           |
| ---------------------- | --------------------- | ---------------- | ----------------- | ------------- | ---------------- |
| **Agnosticidad**       | ✅ Agnóstico          | 🟡 .NET nativo   | ✅ Agnóstico      | ✅ Agnóstico  | 🟡 .NET nativo   |
| **Madurez**            | ✅ Muy alta           | 🟡 Media         | ✅ Alta           | ✅ Muy alta   | 🟡 Baja          |
| **Ecosistema Plugins** | ✅ Extenso            | 🟡 Limitado      | 🟡 Medio          | 🟡 Medio      | ❌ Limitado      |
| **Seguridad**          | ✅ Completa           | ✅ OAuth2/JWT    | ✅ Completa       | ✅ Completa   | 🟡 Limitada      |
| **Escalabilidad**      | ✅ Clustering nativo  | 🟡 Manual con LB | ✅ K8s/Clustering | ✅ Clustering | 🟡 Manual con LB |
| **Observabilidad**     | ✅ Completa           | ✅ Nativa .NET   | ✅ Completa       | ✅ Completa   | 🟡 Básica        |
| **Comunidad**          | ✅ Muy activa         | 🟡 Creciente     | ✅ Activa         | ✅ Activa     | 🟡 Pequeña       |
| **Costos**             | ✅ OSS (+ Enterprise) | ✅ OSS           | ✅ OSS            | 🟡 Comercial  | ✅ OSS           |

---

## ✔️ DECISIÓN

Se selecciona **Kong (OSS)** como solución estándar de API Gateway para todos los servicios corporativos, desplegado en contenedores sobre AWS ECS Fargate, priorizando **agnosticidad tecnológica**, **madurez**, **ecosistema de plugins** y **escalabilidad enterprise**.

## Justificación

- **Agnosticidad total:** no depende de stack tecnológico específico, portable entre clouds y tecnologías
- **Madurez probada:** líder de mercado con millones de implementaciones en producción
- **Ecosistema de plugins extenso:** autenticación (OAuth2, JWT, LDAP), rate limiting, transformaciones, observabilidad
- **Escalabilidad enterprise:** clustering nativo, balanceo distribuido, health checks avanzados
- **Comunidad y soporte:** documentación extensa, comunidad muy activa, opción enterprise disponible
- **Observabilidad integrada:** métricas Prometheus, logs estructurados, tracing distribuido
- **Multi-tenancy nativo:** soporte para workspaces, enrutamiento por tenant
- **Estándar de la industria:** reduce riesgo de lock-in tecnológico

## Alternativas descartadas

- **YARP:** ecosistema de plugins limitado, acoplamiento con .NET, menor madurez
- **Traefik:** buena alternativa pero menor ecosistema de plugins que Kong
- **NGINX Plus:** costos comerciales elevados sin ventajas significativas sobre Kong OSS
- **Ocelot:** proyecto menos activo, capacidades enterprise limitadas

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
- [Traefik](https://doc.traefik.io/traefik/)
- [NGINX Plus](https://www.nginx.com/products/nginx/)
- [YARP](https://microsoft.github.io/reverse-proxy/)
- [Ocelot](https://ocelot.readthedocs.io/)
