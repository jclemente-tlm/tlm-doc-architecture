---
id: adr-016-logging-estructurado
title: "Logging Estructurado"
sidebar_position: 16
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos multi-tenant requieren una solución de logging que permita:

- **Logging estructurado** (JSON) para análisis automatizado
- **Correlación distribuida** entre microservicios con trace IDs
- **Multi-tenancy** con segregación de logs por país/tenant
- **Centralización** para análisis y alertas unificadas
- **Retención configurable** por tipo de log y compliance
- **Performance** bajo alta carga sin impacto en latencia
- **Ecosistema .NET** nativo con ASP.NET Core y Entity Framework
- **Sinks agnósticos** para evitar lock-in

La estrategia prioriza **flexibilidad, observabilidad y simplicidad operativa** usando tecnologías y patrones aprobados.

Alternativas evaluadas:

- **Serilog** (estructurado, .NET, ecosistema extenso)
- **OpenTelemetry Logging** (estándar CNCF, emergente)
- **NLog** (tradicional, .NET)
- **Microsoft.Extensions.Logging** (nativo .NET, básico)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio                | Serilog                  | OpenTelemetry Logging | NLog                  | MS.Extensions.Logging |
|------------------------|--------------------------|----------------------|-----------------------|----------------------|
| **Logging estructurado**| ✅ Nativo, JSON          | ✅ Estándar CNCF      | 🟡 Configurable       | 🟡 Básico            |
| **Ecosistema .NET**    | ✅ Excelente             | ✅ Oficial            | ✅ Muy maduro         | ✅ Nativo            |
| **Sinks/Destinos**     | ✅ 200+ sinks            | ✅ Exporters extensos | ✅ Muchos targets      | 🟡 Providers básicos |
| **Rendimiento**        | ✅ Muy optimizado        | ✅ Bueno              | ✅ Excelente          | ✅ Bueno             |
| **Multi-tenancy**      | ✅ Contexto enriquecido  | ✅ Contexto avanzado  | 🟡 Manual             | 🟡 Scopes básicos    |
| **Agnosticidad**       | ✅ Totalmente agnóstico  | ✅ Estándar abierto   | ✅ Totalmente agnóstico| ✅ Agnóstico         |
| **Madurez**            | ✅ Muy maduro, activo    | 🟡 Emergente          | ✅ Muy maduro         | ✅ Oficial           |

### Matriz de Decisión

| Solución                  | Estructurado | Ecosistema .NET | Sinks      | Rendimiento | Recomendación         |
|--------------------------|--------------|-----------------|------------|-------------|-----------------------|
| **Serilog**              | Excelente    | Excelente       | Excelente  | Excelente   | ✅ **Seleccionada**    |
| **OpenTelemetry Logging**| Excelente    | Bueno           | Extensos   | Bueno       | 🟡 Alternativa         |
| **NLog**                 | Configurable | Muy maduro      | Muchos     | Excelente   | 🟡 Considerada         |
| **MS.Extensions.Logging**| Básico       | Nativo          | Básicos    | Bueno       | 🟡 Considerada         |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 5 servicios, 100GB logs/mes, retención 90 días. Costos estimados para almacenamiento, operación y monitoreo.

| Solución                | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|-------------------------|---------------|----------------|---------------|--------------|
| Serilog + Loki          | OSS           | US$4,800/año   | US$15,000/año | US$59,400    |
| Serilog + ELK Stack     | OSS           | US$7,200/año   | US$18,000/año | US$75,600    |
| Serilog + Seq           | US$3,600/año  | US$3,600/año   | US$12,000/año | US$57,600    |
| OpenTelemetry + Jaeger  | OSS           | US$6,000/año   | US$24,000/año | US$90,000    |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **Loki/ELK/Seq:** límites por volumen, retención y escalabilidad
- **OpenTelemetry:** integración emergente, requiere validación

### Riesgos y mitigación

- **Lock-in de sinks propietarios:** mitigado usando sinks OSS y configuración desacoplada
- **Complejidad operativa ELK:** mitigada con automatización y monitoreo
- **Costos variables cloud:** monitoreo y revisión anual

---

## ✔️ DECISIÓN

Se selecciona **Serilog** como librería estándar de logging estructurado para todos los servicios `.NET` del ecosistema corporativo.

## Justificación

- Soporte nativo para sinks como consola, archivos, `Loki`, `Seq`, `Elasticsearch`, etc.
- Logging estructurado (`JSON`) y enriquecimiento de logs
- Integración sencilla con `ASP.NET Core` y frameworks `.NET`
- Amplia comunidad y documentación
- Facilita integración con sistemas de monitoreo y observabilidad (`Prometheus`, `Grafana`, `Loki`, `Jaeger`)
- Permite incluir información de `tenant` y `país` en los logs, facilitando trazabilidad y auditoría multi-tenant

## Alternativas descartadas

- **NLog/log4net:** menor soporte para logging estructurado y sinks modernos
- **MS.Extensions.Logging:** funcionalidad básica, no estructurado por defecto

---

## ⚠️ CONSECUENCIAS

- Todos los servicios `.NET` deben implementar `Serilog` para logging estructurado
- Se debe estandarizar el formato y la gestión de logs (`JSON`)
- El código debe desacoplarse de sinks propietarios mediante configuración

---

## 📚 REFERENCIAS

- [Serilog Docs](https://serilog.net/)
- [Serilog Sinks](https://github.com/serilog/serilog/wiki/Provided-Sinks)
- [OpenTelemetry Logging](https://opentelemetry.io/docs/instrumentation/net/logging/)
- [arc42: Decisiones de arquitectura](https://arc42.org/decision/)
