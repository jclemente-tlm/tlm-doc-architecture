---
title: "ADR-016: Serilog Logging Estructurado"
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

| Criterio                 | Serilog                 | OpenTelemetry Logging | NLog                    | MS.Extensions.Logging |
| ------------------------ | ----------------------- | --------------------- | ----------------------- | --------------------- |
| **Logging estructurado** | ✅ Nativo, JSON         | ✅ Estándar CNCF      | 🟡 Configurable         | 🟡 Básico             |
| **Ecosistema .NET**      | ✅ Excelente            | ✅ Oficial            | ✅ Muy maduro           | ✅ Nativo             |
| **Sinks/Destinos**       | ✅ 200+ sinks           | ✅ Exporters extensos | ✅ Muchos targets       | 🟡 Providers básicos  |
| **Rendimiento**          | ✅ Muy optimizado       | ✅ Bueno              | ✅ Excelente            | ✅ Bueno              |
| **Multi-tenancy**        | ✅ Contexto enriquecido | ✅ Contexto avanzado  | 🟡 Manual               | 🟡 Scopes básicos     |
| **Agnosticidad**         | ✅ Totalmente agnóstico | ✅ Estándar abierto   | ✅ Totalmente agnóstico | ✅ Agnóstico          |
| **Madurez**              | ✅ Muy maduro, activo   | 🟡 Emergente          | ✅ Muy maduro           | ✅ Oficial            |

### Matriz de Decisión

| Solución                  | Estructurado | Ecosistema .NET | Sinks     | Rendimiento | Recomendación       |
| ------------------------- | ------------ | --------------- | --------- | ----------- | ------------------- |
| **Serilog**               | Excelente    | Excelente       | Excelente | Excelente   | ✅ **Seleccionada** |
| **OpenTelemetry Logging** | Excelente    | Bueno           | Extensos  | Bueno       | 🟡 Alternativa      |
| **NLog**                  | Configurable | Muy maduro      | Muchos    | Excelente   | 🟡 Considerada      |
| **MS.Extensions.Logging** | Básico       | Nativo          | Básicos   | Bueno       | 🟡 Considerada      |

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

- **OpenTelemetry Logging:** emergente, integración aún en maduración
- **NLog:** alternativa válida, pero menor ecosistema de sinks
- **MS.Extensions.Logging:** demasiado básico para logging estructurado avanzado

---

## ⚠️ CONSECUENCIAS

### Positivas

- Logging estructurado JSON con enriquecimiento automático de contexto
- Más de 200 sinks disponibles para diferentes destinos
- Integración nativa con ASP.NET Core y OpenTelemetry
- Soporte multi-tenancy con enrichers personalizados
- Rendimiento optimizado para alta carga

### Negativas (Riesgos y Mitigaciones)

- **Lock-in de sinks propietarios:** mitigado usando sinks OSS (Loki, Seq OSS) y configuración desacoplada
- **Complejidad configuración:** mitigada con plantillas estándar corporativas
- **Costos almacenamiento logs:** mitigados con políticas de retención y agregación

---

## 📚 REFERENCIAS

- [Serilog Documentation](https://serilog.net/)
- [Serilog Sinks](https://github.com/serilog/serilog/wiki/Provided-Sinks)
- [OpenTelemetry Logging](https://opentelemetry.io/docs/instrumentation/net/logging/)
- [ADR-021: Stack de Observabilidad](./adr-021-observabilidad.md)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
