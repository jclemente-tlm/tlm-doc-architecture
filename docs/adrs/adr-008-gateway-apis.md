---
id: adr-008-api-gateway
title: "API Gateway"
sidebar_position: 8
---

## ✅ ESTADO

Aceptada – Agosto 2025

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

La intención estratégica es **maximizar agnosticidad** y aprovechar la integración nativa con el stack `.NET`.

Alternativas evaluadas:

- **YARP (Yet Another Reverse Proxy)** (Microsoft, open source, .NET nativo)
- **AWS API Gateway** (Gestionado AWS, lock-in)
- **Kong** (Open source/Enterprise, agnóstico)
- **Traefik** (Open source, cloud-native)
- **NGINX Plus** (Comercial, agnóstico)
- **Ocelot** (Open source, .NET específico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | YARP | Ocelot | Kong | NGINX Plus | Traefik |
|----------------------|------|--------|------|------------|---------|
| **Agnosticidad**     | ✅ .NET nativo | ✅ .NET nativo | ✅ Agnóstico | ✅ Agnóstico | ✅ Agnóstico |
| **Operación**        | ✅ Simple | ✅ Simple | 🟡 Complejo | 🟡 Complejo | ✅ Simple |
| **Seguridad**        | ✅ Integración OAuth2/JWT | 🟡 Limitada | ✅ Completa | ✅ Completa | ✅ Completa |
| **Ecosistema .NET**  | ✅ Excelente | ✅ Excelente | 🟡 Limitada | 🟡 Limitada | 🟡 Limitada |
| **Escalabilidad**    | ✅ Manual con LB | ✅ Manual con LB | ✅ Clustering | ✅ Clustering | ✅ K8s/Clustering |
| **Observabilidad**   | ✅ Nativa | 🟡 Básica | ✅ Completa | ✅ Completa | ✅ Completa |
| **Costos**           | ✅ OSS | ✅ OSS | ✅ OSS | 🟡 Comercial | ✅ OSS |

### Matriz de Decisión

| Solución                | Agnosticidad | Operación | Seguridad | Ecosistema .NET | Recomendación         |
|------------------------|--------------|-----------|-----------|-----------------|-----------------------|
| **YARP**               | Excelente    | Excelente | Excelente | Excelente       | ✅ **Seleccionada**    |
| **Kong**               | Excelente    | Buena     | Excelente | Limitada        | 🟡 Alternativa         |
| **Traefik**            | Excelente    | Excelente | Excelente | Limitada        | 🟡 Considerada         |
| **NGINX Plus**         | Excelente    | Buena     | Excelente | Limitada        | ❌ Descartada          |
| **Ocelot**             | Excelente    | Excelente | Limitada  | Excelente       | ❌ Descartada          |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 10M requests/mes, 4 países, 99.9% uptime. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución                | Licenciamiento     | Infraestructura | Operación         | TCO 3 años         |
|------------------------|-------------------|----------------|-------------------|--------------------|
| YARP                   | OSS               | US$2,160/año   | US$24,000/año     | US$78,480          |
| AWS API Gateway        | Pago por uso      | US$0           | US$0              | US$126,000         |
| Kong OSS               | OSS               | US$3,600/año   | US$36,000/año     | US$118,800         |
| Traefik                | OSS               | US$1,800/año   | US$18,000/año     | US$59,400          |
| NGINX Plus             | Comercial         | US$2,160/año   | US$24,000/año     | US$85,980          |
| Ocelot                 | OSS               | US$1,440/año   | US$18,000/año     | US$58,320          |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **YARP/Ocelot:** sin límite práctico, depende de infraestructura y balanceo
- **Kong/Traefik/NGINX:** escalabilidad horizontal, clustering
- **AWS API Gateway:** límites por cuenta y región, escalabilidad automática

### Riesgos y mitigación

- **Lock-in cloud:** mitigado con soluciones OSS y despliegue portable
- **Complejidad operativa Kong/NGINX:** mitigada con automatización y capacitación
- **Costos gestionados:** monitoreo y revisión anual

---

## ✔️ DECISIÓN

Se selecciona **YARP** como solución estándar de API Gateway para todos los servicios corporativos, desplegado en contenedores sobre AWS ECS Fargate, priorizando integración nativa, flexibilidad y control operativo.

## Justificación

- Integración nativa con `.NET` y ecosistema C#
- Personalización avanzada de rutas, autenticación y políticas multi-tenant
- Observabilidad y métricas integradas
- Despliegue sencillo y portable en contenedores
- Menor costo operativo y mayor control frente a soluciones gestionadas

## Alternativas descartadas

- **API Gateway propio:** mayor complejidad operativa y mantenimiento
- **AWS API Gateway:** lock-in AWS, costos altos
- **Azure API Management:** lock-in Azure, costos altos
- **Google API Gateway:** lock-in GCP, costos altos

---

## ⚠️ CONSECUENCIAS

- El tráfico de entrada se canaliza y controla desde YARP
- La seguridad y el monitoreo se centralizan en el gateway

---

## 📚 REFERENCIAS

- [YARP](https://microsoft.github.io/reverse-proxy/)
- [AWS API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
- [Kong](https://docs.konghq.com/)
- [Traefik](https://doc.traefik.io/traefik/)
- [NGINX](https://www.nginx.com/resources/wiki/)
- [Ocelot](https://ocelot.readthedocs.io/en/latest/)
