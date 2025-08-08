---
id: adr-016-logging-estructurado
title: "Logging Estructurado"
sidebar_position: 16
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos multi-tenant requieren una solución de logging que soporte:

- **Logging estructurado** (JSON) para analisis automatizado
- **Correlacion distribuida** entre microservicios con trace IDs
- **Multi-tenancy** con segregacion de logs por pais/tenant
- **Centralizacion** para analisis y alertas unificadas
- **Retencion configurable** por tipo de log y compliance
- **Performance** bajo alta carga sin impacto en latencia
- **Ecosistema .NET** nativa con ASP.NET Core y Entity Framework
- **Sinks agnosticos** para evitar lock-in con proveedores especificos

La intencion estrategica es **balancear flexibilidad vs simplicidad operacional** para logging empresarial.

Las alternativas evaluadas fueron:

- **Serilog** (Estructurado, .NET, ecosistema extenso)
- **NLog** (Tradicional, .NET, configuración XML/JSON)
- **log4net** (Legacy, Apache, configuración XML)
- **Microsoft.Extensions.Logging** (Nativo .NET, básico)
- **Elastic Common Schema (ECS)** (Estándar Elastic)
- **OpenTelemetry Logging** (Estándar CNCF, emergente)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | Serilog | NLog | log4net | MS.Ext.Logging | ECS | OpenTelemetry |
|----------|---------|------|---------|----------------|-----|---------------|
| **Logging Estructurado** | ✅ Nativo, JSON | 🟡 Con configuración | ❌ Solo texto | 🟡 Básico | ✅ Estándar Elastic | ✅ Estándar CNCF |
| **Ecosistema .NET** | ✅ Diseñado para .NET | ✅ Muy maduro .NET | 🟡 Legacy .NET | ✅ Nativo Microsoft | 🟡 Requiere integración | ✅ Soporte oficial |
| **Sinks/Destinos** | ✅ 200+ sinks | ✅ Muchos targets | 🟡 Appenders limitados | 🟡 Providers básicos | 🟡 Solo Elastic | ✅ Exporters extensos |
| **Rendimiento** | ✅ Muy optimizado | ✅ Excelente | 🟡 Moderado | ✅ Bueno | ✅ Bueno | ✅ Bueno |
| **Multi-tenancy** | ✅ Context enriquecido | 🟡 Con configuración | 🟡 Manual | 🟡 Scopes básicos | ✅ Contexto rico | ✅ Contexto avanzado |
| **Agnosticidad** | ✅ Totalmente agnóstico | ✅ Totalmente agnóstico | ✅ Totalmente agnóstico | ✅ Agnóstico | 🟡 Elastic-oriented | ✅ Estándar abierto |
| **Madurez** | ✅ Muy maduro, activo | ✅ Muy maduro | 🟡 Legacy, poco activo | ✅ Microsoft oficial | 🟡 Emergente | 🟡 Emergente |

### Matriz de Decisión

| Solución | Estructurado | Ecosistema .NET | Sinks | Rendimiento | Recomendación |
|----------|--------------|-----------------|-------|-------------|---------------|
| **Serilog** | Excelente | Excelente | Excelente | Excelente | ✅ **Seleccionada** |
| **OpenTelemetry** | Excelente | Bueno | Extensos | Bueno | 🟡 Alternativa |
| **NLog** | Configurable | Muy maduro | Muchos | Excelente | 🟡 Considerada |
| **MS.Extensions.Logging** | Básico | Nativo | Básicos | Bueno | 🟡 Considerada |
| **ECS** | Estándar | Limitado | Solo Elastic | Bueno | ❌ Descartada |
| **log4net** | No | Legacy | Limitados | Moderado | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 5 servicios, 100GB logs/mes, retención 90 días

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **Serilog + ELK Stack** | US$0 (OSS) | US$7,200/año | US$18,000/año | **US$75,600** |
| **Serilog + Seq** | US$3,600/año | US$3,600/año | US$12,000/año | **US$57,600** |
| **Serilog + Loki** | US$0 (OSS) | US$4,800/año | US$15,000/año | **US$59,400** |
| **NLog + ELK Stack** | US$0 (OSS) | US$7,200/año | US$21,000/año | **US$84,600** |
| **OpenTelemetry + Jaeger** | US$0 (OSS) | US$6,000/año | US$24,000/año | **US$90,000** |
| **Datadog Logs** | US$45,600/año | US$0 | US$6,000/año | **US$154,800** |

### Escenario Alto Volumen: 20 servicios, 1TB logs/mes, multi-región

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| **Serilog + ELK Stack** | **US$240,000** | Manual con clustering |
| **Serilog + Seq** | **US$180,000** | Manual con clustering |
| **Serilog + Loki** | **US$150,000** | Automática con Grafana Cloud |
| **NLog + ELK Stack** | **US$270,000** | Manual con clustering |
| **OpenTelemetry + Jaeger** | **US$300,000** | Manual con clustering |
| **Datadog Logs** | **US$1,368,000** | Automática, gestionada |

### Factores de Costo Adicionales

```yaml
Consideraciones Serilog:
  Sinks adicionales: Gratuitos (OSS) vs US$50/mes comerciales
  Enrichers: Gratuitos vs US$20/mes para comerciales
  Configuración: Code-first vs XML (sin costo adicional)
  Retención: Configurable por sink vs fijo en SaaS
  Migración: US$0 entre sinks vs US$25K desde propietario
  Capacitación: US$2K vs US$10K para stacks complejos
  Personalización: Ilimitada vs limitada en SaaS
```

---

## ✔️ DECISIÓN

Se adopta `Serilog` como librería estándar de logging estructurado para todos los servicios `.NET` del ecosistema corporativo.

## Justificación

- Soporte nativo para `sinks` como consola, archivos, `Seq`, `Elasticsearch`, etc.
- Permite logging estructurado (`JSON`) y enriquecimiento de logs.
- Integración sencilla con `ASP.NET Core` y otros frameworks `.NET`.
- Amplia comunidad y documentación.
- Facilita la integración con sistemas de monitoreo y observabilidad.
- Permite incluir información de `tenant` y `país` en los logs, facilitando la trazabilidad y auditoría en entornos `multi-tenant` y `multi-país`.

## Alternativas descartadas

- NLog/log4net: Menor soporte para logging estructurado y sinks modernos.

---

## ⚠️ CONSECUENCIAS

- Todos los servicios .NET deben implementar Serilog para logging estructurado.
- Se debe estandarizar el formato y la gestión de logs.

---

## 📚 REFERENCIAS

- [Serilog Docs](https://serilog.net/)
- [Serilog Sinks](https://github.com/serilog/serilog/wiki/Provided-Sinks)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
