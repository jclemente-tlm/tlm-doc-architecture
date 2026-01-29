---
title: "ADR-018: Arquitectura de Microservicios"
sidebar_position: 18
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos multi-tenant requieren una arquitectura que permita:

- **Escalabilidad independiente** por servicio según demanda
- **Equipos autónomos** con ciclos de desarrollo y despliegue independientes
- **Resiliencia distribuida** con aislamiento de fallos
- **Multi-tenancy** con segregación de datos por país/tenant
- **Evolución independiente** de contratos y versiones de API
- **Observabilidad distribuida** (`Prometheus`, `Grafana`, `Loki`, `Jaeger`, `Serilog`, `OpenTelemetry`)
- **Deployment agnóstico** entre cloud providers y on-premises
- **Alineación con Clean Architecture y DDD**

La estrategia prioriza **autonomía, resiliencia y escalabilidad**, minimizando complejidad innecesaria y lock-in.

Alternativas evaluadas:

- **Microservicios distribuidos** (Domain-driven, independientes)
- **Micro-frontends + Microservicios** (Distribución completa)
- **Serverless Functions** (`FaaS` con funciones distribuidas)
- **Service-oriented Monolith** (Monolito con servicios internos)
- **Modular Monolith** (Monolito modular)
- **Monolito clásico** (Aplicación única)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio                | Microservicios | Micro-frontends | Serverless | Service Monolith | Modular Monolith | Monolito |
|------------------------|----------------|-----------------|------------|------------------|------------------|----------|
| **Escalabilidad**      | ✅ Independiente| ✅ Completa      | ✅ Automática| 🟡 Limitada      | 🟡 Limitada      | ❌ Muy limitada |
| **Autonomía Equipos**  | ✅ Total        | ✅ Full-stack    | ✅ Por función| 🟡 Parcial      | 🟡 Parcial       | ❌ Nula |
| **Resiliencia**        | ✅ Aislada      | ✅ Aislada       | ✅ Aislada   | 🟡 Parcial       | 🟡 Parcial       | ❌ Total |
| **Multi-tenancy**      | ✅ Nativo       | 🟡 Complejo      | ✅ Por función| ✅ Interno       | 🟡 App           | 🟡 App |
| **Operación**          | 🟡 Compleja     | 🟡 Compleja      | 🟡 Gestionada| ✅ Simple        | ✅ Simple        | ✅ Muy simple |
| **Time-to-Market**     | 🟡 Lento inicial| 🟡 Lento inicial | ✅ Rápido    | ✅ Moderado      | ✅ Rápido        | ✅ Muy rápido |
| **Costos**             | 🟡 Altos        | 🟡 Altos         | 🟡 Variables | 🟡 Moderados     | ✅ Bajos         | ✅ Muy bajos |

### Matriz de Decisión

| Solución                | Escalabilidad | Autonomía | Resiliencia | Multi-tenancy | Recomendación         |
|------------------------|--------------|-----------|-------------|---------------|-----------------------|
| **Microservicios**     | Excelente    | Excelente | Excelente   | Excelente     | ✅ **Seleccionada**    |
| **Micro-frontends**    | Excelente    | Excelente | Excelente   | Moderada      | 🟡 Alternativa         |
| **Serverless**         | Excelente    | Buena     | Excelente   | Buena         | 🟡 Considerada         |
| **Service Monolith**   | Limitada     | Moderada  | Moderada    | Buena         | 🟡 Considerada         |
| **Modular Monolith**   | Limitada     | Moderada  | Limitada    | Buena         | ❌ Descartada          |
| **Monolito**           | Muy limitada | Mala      | Mala        | Moderada      | ❌ Descartada          |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 5 servicios, 4 países, equipos distribuidos. Costos estimados para desarrollo, infraestructura y operación.

| Solución                | Desarrollo   | Infraestructura | Operación      | TCO 3 años   |
|------------------------|--------------|----------------|---------------|--------------|
| Microservicios         | US$180,000   | US$36,000/año  | US$45,000/año | US$423,000   |
| Micro-frontends + MS   | US$220,000   | US$42,000/año  | US$54,000/año | US$508,000   |
| Serverless Functions   | US$120,000   | US$60,000/año  | US$30,000/año | US$390,000   |
| Service Monolith       | US$100,000   | US$18,000/año  | US$36,000/año | US$262,000   |
| Modular Monolith       | US$80,000    | US$12,000/año  | US$30,000/año | US$206,000   |
| Monolito Clásico       | US$60,000    | US$9,000/año   | US$45,000/año | US$222,000   |

### Escenario Alto Volumen: 20 servicios, multi-región, alta demanda

| Solución                | TCO 3 años   | Escalabilidad           | Tiempo Recuperación |
|------------------------|--------------|------------------------|---------------------|
| Microservicios         | US$1,200,000 | Excelente - Por servicio| 5-15 min            |
| Micro-frontends + MS   | US$1,500,000 | Excelente - Completa    | 5-15 min            |
| Serverless Functions   | US$900,000   | Automática - Infinita   | 0-5 min             |
| Service Monolith       | US$800,000   | Limitada - Vertical     | 15-30 min           |
| Modular Monolith       | US$600,000   | Limitada - Vertical     | 15-30 min           |
| Monolito Clásico       | US$1,800,000 | Muy limitada            | 30-60 min           |

### Factores de Costo Adicionales

```yaml
Consideraciones Microservicios:
  Orquestación: AWS ECS/Fargate managed - US$18K/año
  Observabilidad: Stack OSS (`Prometheus`, `Grafana`, `Loki`, `Jaeger`, `Serilog`, `OpenTelemetry`) vs US$100K/año SaaS
  API Gateway: `YARP` (OSS) vs US$25K/año comercial
  Migración: US$0 entre clouds vs US$200K monolito
  Capacitación: US$15K vs US$5K para monolito
  DevOps: CI/CD complejo vs simple
  Downtime evitado: US$500K/año vs US$2M/año monolito
```

---

## ✔️ DECISIÓN

Se adopta la **arquitectura de microservicios distribuidos** como estrategia principal para los servicios corporativos.

## Justificación

- **Escalabilidad independiente** permite optimizar recursos por servicio
- **Autonomía de equipos** acelera desarrollo y reduce dependencias
- **Resiliencia distribuida** minimiza impacto de fallos individuales
- **Multi-tenancy nativa** facilita segregación por país
- **Evolución independiente** de tecnologías y contratos
- **Alineado con `Domain-Driven Design`, `Clean Architecture`, `CQRS` y patrones empresariales**
- **Observabilidad y monitoreo integrados** (`Prometheus`, `Grafana`, `Loki`, `Jaeger`, `Serilog`, `OpenTelemetry`)

## Alternativas descartadas

- **Monolito clásico/Modular:** limitan escalabilidad, autonomía y resiliencia
- **Service Monolith:** menor autonomía y escalabilidad
- **Serverless puro:** mayor complejidad operativa y lock-in

---

## ⚠️ CONSECUENCIAS

- Los canales y funciones pueden evolucionar y desplegarse de forma independiente
- El sistema es más resiliente y adaptable a nuevos requerimientos
- Se requiere estandarizar la instrumentación de observabilidad y la gestión de despliegues

---

## 📚 REFERENCIAS

- [Microservicios y modularidad](https://martinfowler.com/articles/microservices.html)
- [arc42: Decisiones de arquitectura](https://arc42.org/decision/)
