---
id: logging
sidebar_position: 1
title: Logging Estructurado
description: Estándares para logging estructurado con Serilog 3.1+, Winston 3.11+ y correlation IDs
---

# Estándar Técnico — Logging Estructurado

---

## 1. Propósito
Garantizar trazabilidad y debugging en entornos distribuidos mediante logging estructurado JSON con correlation IDs para correlacionar requests entre microservicios y enmascarar datos sensibles (passwords, tokens, PII).

---

## 2. Alcance

**Aplica a:**
- APIs REST (.NET, Node.js) y microservicios backend
- Workers, background jobs, Lambdas AWS

**No aplica a:**
- Logs de infraestructura (Docker, Kubernetes) - usar CloudWatch/Datadog
- Desarrollo local (puede usar formato simple/colorizado)
- Métricas de performance (ver [Monitoreo y Métricas](./02-monitoreo-metricas.md))

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Logger .NET** | Serilog + Serilog.AspNetCore | 3.1+ / 8.0+ | Logging estructurado con sinks configurables |
| **Logger Node.js** | Winston | 3.11+ | Transports configurables (Console, File, CloudWatch) |
| **Sinks** | Serilog.Sinks.Console, Serilog.Sinks.File | 5.0+ | JSON en prod, rotación diaria, retención 7 días |
| **Centralización** | AWS CloudWatch Logs | - | Sink: Serilog.Sinks.AwsCloudWatch, winston-cloudwatch |
| **Rotación** | winston-daily-rotate-file | 4.7+ | Rotación automática Node.js |

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
- [ ] Logs estructurados vía `ILogger<T>` (.NET) o Winston logger (Node.js)

---

## 5. Prohibiciones

- ❌ Logs en texto plano en producción
- ❌ `Console.WriteLine()` o `console.log()` directo (usar logger estructurado)
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
    .WriteTo.AmazonCloudWatch("/talma/api/production")
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

### Node.js
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'talma-api' },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/app.log', maxsize: 100000000, maxFiles: 7 })
  ]
});

// Middleware Correlation ID
app.use((req, res, next) => {
  req.correlationId = req.headers['x-correlation-id'] || uuidv4();
  res.setHeader('x-correlation-id', req.correlationId);
  next();
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
npm test -- --grep "logging"
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|
| Logs en JSON | 100% | `jq` parse exitoso |
| Correlation ID presente | 100% | `grep CorrelationId` |
| Passwords enmascarados | 100% | `grep -i password` retorna 0 |
| Nivel Debug/Trace en prod | 0% | CloudWatch Insights query |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-016: Logging Estructurado](../../../decisiones-de-arquitectura/adr-016-logging-estructurado.md)
- [Monitoreo y Métricas](./02-monitoreo-metricas.md)
- [Serilog Documentation](https://serilog.net/)
- [Winston Documentation](https://github.com/winstonjs/winston)
