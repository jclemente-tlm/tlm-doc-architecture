---
title: "Arquitectura de Microservicios"
sidebar_position: 18
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos multi-tenant requieren una arquitectura que soporte:

- **Escalabilidad independiente** por servicio según demanda específica
- **Equipos autónomos** con ciclos de desarrollo y despliegue independientes
- **Resiliencia distribuida** con aislamiento de fallos entre servicios
- **Multi-tenancy** con segregación de datos por país/tenant
- **Tecnologías heterogéneas** cuando sea justificado por dominio
- **Evolución independiente** de contratos y versiones de API
- **Observabilidad distribuida** con trazabilidad end-to-end
- **Deployment agnóstico** entre cloud providers y on-premises

La intención estratégica es **balancear autonomía vs complejidad operacional** para servicios empresariales.

Las alternativas evaluadas fueron:

- **Microservicios distribuidos** (Domain-driven, independientes)
- **Modular Monolith** (Monolito con módulos bien definidos)
- **Service-oriented Monolith** (Monolito con servicios internos)
- **Micro-frontends + Microservicios** (Distribución completa)
- **Monolito clásico** (Aplicación única sin modularidad)
- **Serverless Functions** (FaaS con funciones distribuidas)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | Microservicios | Modular Monolith | Service Monolith | Micro-frontends | Monolito | Serverless |
|----------|----------------|------------------|------------------|-----------------|----------|------------|
| **Escalabilidad** | ✅ Independiente por servicio | 🟡 Solo vertical | 🟡 Limitada | ✅ Frontend + backend | ❌ Muy limitada | ✅ Automática |
| **Autonomía Equipos** | ✅ Equipos independientes | 🟡 Equipos por módulo | 🟡 Equipos por servicio | ✅ Full-stack teams | ❌ Equipo monolítico | ✅ Equipos por función |
| **Resiliencia** | ✅ Fallos aislados | 🟡 Fallo total | 🟡 Fallo parcial | ✅ Fallos aislados | ❌ Fallo total | ✅ Fallos aislados |
| **Multi-tenancy** | ✅ Por servicio | ✅ Por módulo | ✅ Por servicio interno | 🟡 Complejo | 🟡 A nivel app | ✅ Por función |
| **Operación** | 🟡 Muy compleja | ✅ Simple | 🟡 Moderada | 🟡 Compleja | ✅ Muy simple | 🟡 Gestionada |
| **Time-to-Market** | 🟡 Lento inicial | ✅ Rápido | ✅ Moderado | 🟡 Lento inicial | ✅ Muy rápido | ✅ Rápido |
| **Costos** | 🟡 Altos | ✅ Bajos | 🟡 Moderados | 🟡 Altos | ✅ Muy bajos | 🟡 Variables |

### Matriz de Decisión

| Solución | Escalabilidad | Autonomía | Resiliencia | Multi-tenancy | Recomendación |
|----------|---------------|-------------|-------------|---------------|---------------|
| **Microservicios** | Excelente | Excelente | Excelente | Excelente | ✅ **Seleccionada** |
| **Micro-frontends** | Excelente | Excelente | Excelente | Moderada | 🟡 Alternativa |
| **Serverless** | Excelente | Buena | Excelente | Buena | 🟡 Considerada |
| **Service Monolith** | Limitada | Moderada | Moderada | Buena | 🟡 Considerada |
| **Modular Monolith** | Limitada | Moderada | Limitada | Buena | ❌ Descartada |
| **Monolito** | Muy limitada | Mala | Mala | Moderada | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 5 servicios, 4 países, equipos distribuidos

| Solución | Desarrollo | Infraestructura | Operación | TCO 3 años |
|----------|------------|-----------------|-----------|------------|
| **Microservicios** | US$180,000 | US$36,000/año | US$45,000/año | **US$423,000** |
| **Micro-frontends + MS** | US$220,000 | US$42,000/año | US$54,000/año | **US$508,000** |
| **Serverless Functions** | US$120,000 | US$60,000/año | US$30,000/año | **US$390,000** |
| **Service Monolith** | US$100,000 | US$18,000/año | US$36,000/año | **US$262,000** |
| **Modular Monolith** | US$80,000 | US$12,000/año | US$30,000/año | **US$206,000** |
| **Monolito Clásico** | US$60,000 | US$9,000/año | US$45,000/año | **US$222,000** |

### Escenario Alto Volumen: 20 servicios, multi-región, alta demanda

| Solución | TCO 3 años | Escalabilidad | Tiempo Recuperación |
|----------|------------|---------------|---------------------|
| **Microservicios** | **US$1,200,000** | Excelente - Por servicio | 5-15 min |
| **Micro-frontends + MS** | **US$1,500,000** | Excelente - Completa | 5-15 min |
| **Serverless Functions** | **US$900,000** | Automática - Infinita | 0-5 min |
| **Service Monolith** | **US$800,000** | Limitada - Vertical | 15-30 min |
| **Modular Monolith** | **US$600,000** | Limitada - Vertical | 15-30 min |
| **Monolito Clásico** | **US$1,800,000** | Muy limitada | 30-60 min |

### Factores de Costo Adicionales

```yaml
Consideraciones Microservicios:
  Orquestación: Kubernetes vs US$50K/año managed
  Service Mesh: Istio (OSS) vs US$30K/año comercial
  Observabilidad: Stack OSS vs US$100K/año SaaS
  API Gateway: YARP (OSS) vs US$25K/año comercial
  Migración: US$0 entre clouds vs US$200K monolito
  Capacitación: US$15K vs US$5K para monolito
  DevOps: CI/CD complejo vs simple
  Downtime evitado: US$500K/año vs US$2M/año monolito
```

---

## ✔️ DECISIÓN

Se adopta **arquitectura de microservicios distribuidos** como estrategia principal para los servicios corporativos.

## Justificación

- **Escalabilidad independiente** permite optimizar recursos por servicio
- **Autonomía de equipos** acelera desarrollo y reduce dependencias
- **Resiliencia distribuida** minimiza impacto de fallos individuales
- **Multi-tenancy nativa** facilita segregación por país
- **Evolución independiente** de tecnologías y contratos
- **Alineado con Domain-Driven Design** y patrones empresariales

---

## ⚠️ CONSECUENCIAS

- Los canales y funciones pueden evolucionar y desplegarse de forma independiente.
- El sistema es más resiliente y adaptable a nuevos requerimientos.

---

## 📚 REFERENCIAS

- [Microservicios y modularidad](https://martinfowler.com/articles/microservices.html)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
