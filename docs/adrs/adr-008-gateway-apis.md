---
id: adr-008-api-gateway
title: "API Gateway"
sidebar_position: 8
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren un API Gateway que actúe como punto de entrada único para:

- **Enrutamiento inteligente** a microservicios backend (Identity, Notifications, Track & Trace, SITA)
- **Autenticación y autorización centralizada** con JWT/OAuth2
- **Rate limiting y throttling** por tenant y endpoint
- **Load balancing** con health checks automáticos
- **Transformación de requests/responses** para compatibilidad
- **Observabilidad integrada** (métricas, logs, tracing)
- **Multi-tenancy** con enrutamiento por país/cliente

La intención estratégica es **maximizar agnosticidad** mientras se aprovecha la integración nativa con el stack .NET.

Las alternativas evaluadas fueron:

- **YARP (Yet Another Reverse Proxy)** (Microsoft, open source, .NET nativo)
- **AWS API Gateway** (Gestionado AWS, lock-in)
- **Kong** (Open source/Enterprise, agnóstico)
- **Traefik** (Open source, cloud-native)
- **NGINX Plus** (Comercial, agnóstico)
- **Ocelot** (Open source, .NET específico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | YARP | Ocelot | Kong | Envoy | Traefik |
|----------|------|--------|------|-------|--------|
| **Ecosistema .NET** | ✅ Nativo Microsoft | ✅ Nativo .NET Core | ❌ Requiere integración | ❌ No nativo | 🟡 Soporte básico |
| **Rendimiento** | ✅ Optimizado .NET 6+ | 🟡 Bueno pero limitado | ✅ Muy alto | ✅ Máximo rendimiento | ✅ Alto |
| **Operación** | ✅ Simple configuración | ✅ Fácil JSON config | 🟡 Complejo, muchas opciones | 🟡 Muy complejo | ✅ Autodescubrimiento |
| **Flexibilidad** | ✅ Muy configurable | 🟡 Limitada | ✅ Extensible con plugins | ✅ Máxima flexibilidad | ✅ Muy flexible |
| **Comunidad** | ✅ Microsoft + comunidad | 🟡 Comunidad pequeña | ✅ Muy activa | ✅ CNCF, muy activa | ✅ Activa |
| **Observabilidad** | ✅ Integración nativa | 🟡 Básica | ✅ Completa | ✅ Muy avanzada | ✅ Buena |
| **Costos** | ✅ Gratuito | ✅ Gratuito | 🟡 Enterprise de pago | ✅ Gratuito | ✅ Gratuito |

### Matriz de Decisión

| Solución | Ecosistema .NET | Rendimiento | Operación | Flexibilidad | Recomendación |
|----------|-----------------|-------------|-----------|--------------|---------------|
| **YARP** | Excelente | Excelente | Simple | Muy buena | ✅ **Seleccionada** |
| **Envoy** | Mala | Excelente | Compleja | Excelente | 🟡 Alternativa |
| **Kong** | Mala | Muy buena | Compleja | Excelente | 🟡 Considerada |
| **Traefik** | Básica | Alta | Simple | Muy buena | 🟡 Considerada |
| **Ocelot** | Excelente | Buena | Simple | Limitada | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 10M requests/mes, 4 países, 99.9% uptime

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **YARP** | US$0 (OSS) | US$2,160/año | US$24,000/año | **US$78,480** |
| **AWS API Gateway** | Pago por uso | US$0 | US$0 | **US$126,000** |
| **Kong OSS** | US$0 (OSS) | US$3,600/año | US$36,000/año | **US$118,800** |
| **Traefik** | US$0 (OSS) | US$1,800/año | US$18,000/año | **US$59,400** |
| **NGINX Plus** | US$2,500/año | US$2,160/año | US$24,000/año | **US$85,980** |
| **Ocelot** | US$0 (OSS) | US$1,440/año | US$18,000/año | **US$58,320** |

### Escenario Alto Volumen: 100M requests/mes

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| **YARP** | **US$120,000** | Manual con load balancer |
| **AWS API Gateway** | **US$1,260,000** | Automática |
| **Kong OSS** | **US$180,000** | Manual con clustering |
| **Traefik** | **US$90,000** | Automática con K8s |
| **NGINX Plus** | **US$150,000** | Manual con clustering |
| **Ocelot** | **US$90,000** | Manual con load balancer |

### Factores de Costo Adicionales

```yaml
Consideraciones:
  SSL/TLS: Incluido en todas las soluciones OSS
  Monitoreo: +US$6K/año para soluciones self-hosted
  Backup/DR: +US$3K/año para configuraciones
  Capacitación: US$5K one-time para YARP/.NET
  Migración: US$0 entre soluciones OSS vs US$15K desde AWS
```

### Agnosticismo, lock-in y mitigación

- **Lock-in:** `AWS API Gateway` implica dependencia de `AWS`, mientras que `YARP`, `NGINX`, `Ocelot`, `Kong` y `KrakenD` pueden desplegarse en cualquier infraestructura.
- **Mitigación:** El uso de proxies y gateways `open source` permite migrar entre nubes y `on-premises`, aunque requiere esfuerzo de integración y operación.

---

## ✔️ DECISIÓN

Se utilizará **[YARP (Yet Another Reverse Proxy)](https://microsoft.github.io/reverse-proxy/)** como `API Gateway` para los `microservicios` `.NET`, desplegado en `AWS ECS Fargate`, asegurando soporte para escenarios `multi-tenant` y `multi-país` mediante enrutamiento, autenticación y políticas segmentadas.

## Justificación

- Permite personalización avanzada de rutas y políticas, incluyendo segmentación por tenant y país.
- Facilita la integración con autenticación `OAuth2` y `JWT`, soportando control de acceso `multi-tenant`/`multi-país`.
- Simplifica el despliegue y mantenimiento.
- Integración nativa con `.NET` y ecosistema `C#`.
- Flexibilidad para definir reglas de enrutamiento, balanceo y autenticación personalizada.
- Despliegue sencillo en contenedores y compatibilidad con `ECS Fargate`.
- Menor costo operativo comparado con soluciones gestionadas (`AWS API Gateway`).
- Extensible y personalizable para necesidades futuras y requisitos de segmentación regional o de clientes.

## Alternativas descartadas

- **AWS API Gateway**: Solución gestionada, pero con mayor costo y menor flexibilidad para lógica personalizada.
- **NGINX/Traefik**: Requiere mayor esfuerzo de integración y personalización en entornos `.NET`, y aunque es robusto, no ofrece integración nativa con `C#`.
- **Ocelot**: Aunque es una buena opción para `.NET`, no ofrece tantas características avanzadas como `YARP`.
- **Kong**: Ofrece muchas funcionalidades, pero la versión Enterprise tiene un costo elevado y la versión OSS requiere más configuración.
- **KrakenD**: Gateway potente y flexible, pero requiere mayor configuración y no tiene integración nativa con `.NET`; su comunidad y soporte empresarial son menores comparados con Kong.

---

## ⚠️ CONSECUENCIAS

- El tráfico de entrada se canaliza y controla desde `YARP`.
- La seguridad y el monitoreo se centralizan en el gateway.

---

## 📚 REFERENCIAS

- [YARP](https://microsoft.github.io/reverse-proxy/)
- [AWS API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html)
- [NGINX](https://www.nginx.com/resources/wiki/)
- [Traefik](https://doc.traefik.io/traefik/)
- [Ocelot](https://ocelot.readthedocs.io/en/latest/)
- [Kong](https://docs.konghq.com/)
- [KrakenD](https://www.krakend.io/docs/)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
