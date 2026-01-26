---
id: niveles-log
sidebar_position: 1
title: Niveles de Log
description: Convención para uso de niveles de logging
---

## 1. Principio

Los niveles de log deben usarse de manera consistente para facilitar filtrado, alertas y troubleshooting en producción.

## 2. Reglas

### Regla 1: Jerarquía de Niveles

| Nivel   | Severidad | Uso                                       | Producción | Ejemplo                                |
| ------- | --------- | ----------------------------------------- | ---------- | -------------------------------------- |
| `TRACE` | 0         | Debugging ultra-detallado                 | ❌ No      | Entrada/salida de cada función         |
| `DEBUG` | 1         | Información de desarrollo                 | ❌ No      | Valores de variables, flujo lógico     |
| `INFO`  | 2         | Eventos normales del negocio              | ✅ Sí      | Usuario creado, orden procesada        |
| `WARN`  | 3         | Situaciones anormales no críticas         | ✅ Sí      | API externa lenta, caché fallido       |
| `ERROR` | 4         | Errores que requieren atención            | ✅ Sí      | Excepción manejada, validación fallida |
| `FATAL` | 5         | Errores críticos que detienen el servicio | ✅ Sí      | DB inaccesible, OOM, crash             |

### Regla 2: TRACE - Debugging Ultra-detallado

**NO usar en producción**. Solo desarrollo local.

```csharp
// ❌ Demasiado verboso para producción
logger.LogTrace("Entrando a método CalculateTotal()");
logger.LogTrace("Parámetro orderId: {OrderId}", orderId);
logger.LogTrace("Ejecutando query: {Query}", sqlQuery);
logger.LogTrace("Resultado: {Result}", result);
```

### Regla 3: DEBUG - Información de Desarrollo

**NO usar en producción**. Solo ambientes dev/qa.

```typescript
// ✅ Útil en desarrollo
logger.debug("Fetching user from cache", { userId, cacheKey });
logger.debug("Cache miss, querying database");
logger.debug("User found", { user });

// ❌ NO en producción (ruido, posible leak de datos sensibles)
logger.debug("Password hash", { hash }); // ⚠️ Seguridad
```

### Regla 4: INFO - Eventos de Negocio Normales

**SÍ usar en producción**. Flujos principales del negocio.

```csharp
// ✅ Eventos importantes de negocio
logger.LogInformation("User registered successfully. UserId={UserId}, Email={Email}",
    userId, email);
logger.LogInformation("Order placed. OrderId={OrderId}, TotalAmount={Amount}, Currency={Currency}",
    orderId, totalAmount, currency);
logger.LogInformation("Payment processed. PaymentId={PaymentId}, Gateway={Gateway}",
    paymentId, gateway);
logger.LogInformation("Email sent. RecipientId={RecipientId}, Type={EmailType}",
    recipientId, emailType);
```

**Cuándo usar INFO:**

- Inicio/fin de procesos importantes
- Creación/actualización de entidades principales
- Transiciones de estado
- Integraciones exitosas con sistemas externos

### Regla 5: WARN - Situaciones Anormales No Críticas

**SÍ usar en producción**. Degradación del servicio, fallbacks.

```typescript
// ✅ Problemas que NO detienen el flujo
logger.warn("External API timeout, using cached data", {
  api: "payment-gateway",
  timeout: 5000,
});

logger.warn("Database query slow", {
  query: "GetUserOrders",
  durationMs: 3500,
  threshold: 2000,
});

logger.warn("Feature flag disabled for tenant", {
  feature: "new-checkout",
  tenantId: "tlm-pe",
});

logger.warn("Retry attempt", {
  operation: "SendEmail",
  attempt: 2,
  maxAttempts: 3,
});
```

**Cuándo usar WARN:**

- Fallback a comportamiento alternativo
- Reintentos automáticos
- Degradación de performance
- Configuración faltante no crítica
- Uso de valores por defecto

### Regla 6: ERROR - Errores Manejados

**SÍ usar en producción**. Errores que requieren atención pero no crashes.

```csharp
// ✅ Errores manejados
try
{
    await _paymentGateway.ProcessPaymentAsync(payment);
}
catch (PaymentGatewayException ex)
{
    logger.LogError(ex, "Payment processing failed. OrderId={OrderId}, Reason={Reason}",
        orderId, ex.Reason);
    // Lógica de compensación...
}

// ✅ Validaciones de negocio fallidas
if (order.Status == OrderStatus.Cancelled)
{
    logger.LogError("Cannot process cancelled order. OrderId={OrderId}, Status={Status}",
        orderId, order.Status);
    throw new InvalidOperationException("Order is cancelled");
}
```

**Cuándo usar ERROR:**

- Excepciones manejadas
- Validaciones de negocio fallidas
- Errores de integración con sistemas externos
- Data inconsistente detectada
- Recursos no encontrados cuando se esperaban

### Regla 7: FATAL - Errores Críticos

**SÍ usar en producción**. Errores que detienen la aplicación.

```typescript
// ✅ Errores críticos que requieren intervención inmediata
logger.fatal("Cannot connect to database", {
  error: err.message,
  host: dbHost,
  retryCount: 5,
});

logger.fatal("Out of memory", {
  memoryUsageMB: process.memoryUsage().heapUsed / 1024 / 1024,
  threshold: 512,
});

logger.fatal("Critical configuration missing", {
  missingConfig: ["DB_HOST", "API_KEY"],
});

// Generalmente seguido por process.exit(1)
```

**Cuándo usar FATAL:**

- Base de datos inaccesible
- Configuración crítica faltante
- Out of Memory (OOM)
- Corrupción de datos crítica
- Dependencias esenciales no disponibles

## 3. Tabla de Decisión Rápida

| Situación                      | Nivel | Ejemplo                              |
| ------------------------------ | ----- | ------------------------------------ |
| Usuario se registró            | INFO  | `User registered successfully`       |
| Orden creada                   | INFO  | `Order placed`                       |
| Email enviado                  | INFO  | `Email sent`                         |
| API externa lenta (>2s)        | WARN  | `External API slow response`         |
| Cache fallido, usando DB       | WARN  | `Cache miss, fallback to database`   |
| Reintento automático           | WARN  | `Retry attempt 2/3`                  |
| Validación de negocio fallida  | ERROR | `Cannot cancel delivered order`      |
| Excepción manejada             | ERROR | `Payment gateway timeout`            |
| Recurso no encontrado          | ERROR | `User not found`                     |
| DB inaccesible                 | FATAL | `Cannot connect to database`         |
| Configuración crítica faltante | FATAL | `Missing required config: API_KEY`   |
| Crash de aplicación            | FATAL | `Unhandled exception, shutting down` |

## 4. Configuración por Ambiente

### Desarrollo

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft": "Information",
      "System": "Information"
    }
  }
}
```

### Staging

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "System": "Warning"
    }
  }
}
```

### Producción

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "System": "Warning",
      "Microsoft.EntityFrameworkCore": "Error"
    }
  }
}
```

## 5. Herramientas de Validación

### Logger Wrapper (.NET)

```csharp
public static class LoggerExtensions
{
    public static void LogBusinessEvent(
        this ILogger logger,
        string eventName,
        params object[] properties)
    {
        // Siempre INFO para eventos de negocio
        logger.LogInformation("BusinessEvent: {EventName} {@Properties}",
            eventName, properties);
    }

    public static void LogPerformanceWarning(
        this ILogger logger,
        string operation,
        long durationMs,
        long thresholdMs)
    {
        if (durationMs > thresholdMs)
        {
            logger.LogWarning(
                "Performance: {Operation} took {DurationMs}ms (threshold: {ThresholdMs}ms)",
                operation, durationMs, thresholdMs);
        }
    }
}

// Uso
_logger.LogBusinessEvent("OrderPlaced", new { orderId, totalAmount });
_logger.LogPerformanceWarning("GetUserOrders", 3500, 2000);
```

### Logger Wrapper (TypeScript)

```typescript
export class AppLogger {
  constructor(private logger: Logger) {}

  businessEvent(eventName: string, data: Record<string, any>) {
    // Siempre INFO
    this.logger.info(`BusinessEvent: ${eventName}`, data);
  }

  degradedService(service: string, reason: string, fallback: string) {
    // Siempre WARN
    this.logger.warn("Service degraded", { service, reason, fallback });
  }

  criticalError(error: Error, context: Record<string, any>) {
    // ERROR o FATAL según contexto
    const level = this.isCritical(error) ? "fatal" : "error";
    this.logger[level](error.message, { ...context, stack: error.stack });
  }

  private isCritical(error: Error): boolean {
    return (
      error instanceof DatabaseConnectionError ||
      error instanceof OutOfMemoryError
    );
  }
}
```

## 6. Alertas por Nivel

### Configuración de Alertas (CloudWatch/Datadog)

| Nivel | Acción                | Canal                       |
| ----- | --------------------- | --------------------------- |
| TRACE | Ninguna               | -                           |
| DEBUG | Ninguna               | -                           |
| INFO  | Ninguna               | -                           |
| WARN  | Notificar si >100/min | Slack #warnings             |
| ERROR | Notificar si >10/min  | Slack #errors + Email       |
| FATAL | Alerta inmediata      | PagerDuty + Slack #critical |

```typescript
// Ejemplo Datadog Monitor
{
  "name": "High error rate",
  "type": "metric alert",
  "query": "sum(last_5m):sum:app.logs.error{env:prod} > 50",
  "message": "@slack-errors ERROR rate exceeded threshold",
  "priority": 2
}
```

## 📖 Referencias

### Estándares relacionados

- [Logging Estructurado](/docs/fundamentos-corporativos/estandares/observabilidad/logging)

### Convenciones relacionadas

- [Correlation IDs](./02-correlation-ids.md)

### Recursos externos

- [Serilog Levels](https://github.com/serilog/serilog/wiki/Configuration-Basics#minimum-level)
- [Winston Logging Levels](https://github.com/winstonjs/winston#logging-levels)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
