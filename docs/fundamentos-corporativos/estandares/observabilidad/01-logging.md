---
id: logging
sidebar_position: 1
title: Logging Estructurado
description: Estándares para logging estructurado con Serilog 3.1+ y correlation IDs
---

# Estándar Técnico — Logging Estructurado

---

## 1. Propósito
Garantizar trazabilidad y debugging en entornos distribuidos mediante logging estructurado JSON con correlation IDs para correlacionar requests entre microservicios y enmascarar datos sensibles (passwords, tokens, PII).

---

## 2. Alcance

**Aplica a:**
- APIs REST (.NET) y microservicios backend
- Workers, background jobs, Lambdas AWS

**No aplica a:**
- Logs de infraestructura (Docker, AWS ECS) - usar Loki directamente
- Desarrollo local (puede usar formato simple/colorizado)
- Métricas de performance (ver [Monitoreo y Métricas](./02-monitoreo-metricas.md))

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Logger** | Serilog + Serilog.AspNetCore | 3.1+ / 8.0+ | Logging estructurado .NET |
| **OpenTelemetry** | OpenTelemetry.Exporter.OpenTelemetryProtocol | 1.7+ | Exportar logs a Loki via OTLP |
| **Centralización** | Grafana Loki | 2.9+ | Almacenamiento logs agregados |
| **Collector** | Grafana Alloy | 1.0+ | Recolector OpenTelemetry |
| **Visualización** | Grafana | 10.0+ | Dashboards y alertas |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Formato JSON estructurado en producción (NO texto plano)
- [ ] Correlation ID único por request (header `X-Correlation-ID`)
- [ ] Niveles de log: Information, Warning, Error, Critical (NO Trace/Debug en prod)
- [ ] Enmascaramiento de datos sensibles: passwords, tokens, API keys, PII
- [ ] Enrichers: MachineName, EnvironmentName, Application, Version
- [ ] Request logging automático: HTTP method, path, status code, elapsed time
- [ ] Logs a stdout/stderr (NO archivos en contenedores)
- [ ] Retención: Error=90d, Warning/Info=30d, Debug=7d
- [ ] Contexto en excepciones: UserId, CorrelationId, RequestPath
- [ ] Logs estructurados vía `ILogger<T>` (.NET)

---

## 5. Prohibiciones

- ❌ Logs en texto plano en producción
- ❌ `Console.WriteLine()` directo (usar `ILogger<T>` estructurado)
- ❌ Passwords, tokens, API keys sin enmascarar
- ❌ Logs síncronos que bloquean requests (usar async sinks)
- ❌ Nivel Trace/Debug en producción (filtrar con MinimumLevel)
- ❌ Logs sin correlation ID en arquitecturas distribuidas

---

## 6. Configuración Mínima

### .NET
```csharp
// Program.cs
using Serilog;

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithProperty("Application", "TalmaAPI")
    .WriteTo.Console(new JsonFormatter())
    .WriteTo.OpenTelemetry(options => {
        options.Endpoint = "http://grafana-alloy:4317";
    })
    .CreateLogger();

builder.Host.UseSerilog();

// Middleware Correlation ID
app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-ID"].FirstOrDefault() ?? Guid.NewGuid().ToString();
    using (LogContext.PushProperty("CorrelationId", correlationId))
        await next();
});
```

---

## 7. Validación

**Comandos de validación:**

```bash
# Verificar formato JSON
jq . logs/app.json

# Verificar correlation IDs
grep "CorrelationId" logs/app.json | jq '.CorrelationId'

# Verificar niveles de log
jq '.Level' logs/app.json | sort | uniq

# Verificar NO hay passwords sin enmascarar
grep -i "password" logs/app.json

# Tests unitarios
dotnet test --filter Category=Logging
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|
| Logs en JSON | 100% | `jq` parse exitoso |
| Correlation ID presente | 100% | `grep CorrelationId` |
| Passwords enmascarados | 100% | `grep -i password` retorna 0 |
| Nivel Debug/Trace en prod | 0% | Grafana Loki query: `{app="talma"} |= "Debug" or "Trace"` |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-016: Logging Estructurado](../../../decisiones-de-arquitectura/adr-016-logging-estructurado.md)
- [Monitoreo y Métricas](./02-monitoreo-metricas.md)
- [Serilog Documentation](https://serilog.net/)
- [OpenTelemetry Documentation](https://opentelemetry.io/)
