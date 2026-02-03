---
id: health-checks
sidebar_position: 5
title: Health Checks
description: Implementación de liveness y readiness probes para orquestadores
---

# Estándar Técnico — Health Checks

## 1. Propósito

Proporcionar endpoints de diagnóstico para que orquestadores (AWS ECS Fargate, ECS, ALB) detecten automáticamente servicios degradados o no disponibles y gestionen restarts/traffic routing.

## 2. Alcance

**Aplica a:**

- Servicios containerizados (AWS ECS Fargate, ECS, Docker)
- APIs REST detrás de load balancers
- Workers procesando mensajes

**No aplica a:**

- Scripts batch ejecutados por scheduler (cron)
- Funciones serverless (Lambda health es responsabilidad de AWS)

## 3. Tipos de Health Checks

### Liveness Probe

**Propósito:** Detectar si el proceso está "vivo" (no bloqueado, no deadlocked).

**Criterio:** Responde 200 OK si el proceso puede responder requests básicos.

**Acción en fallo:** Orquestador reinicia el contenedor.

**Endpoint:** `GET /health/live`

### Readiness Probe

**Propósito:** Detectar si el servicio está listo para recibir tráfico (DB conectada, dependencias disponibles).

**Criterio:** Responde 200 OK si todas las dependencias críticas están funcionales.

**Acción en fallo:** Orquestador retira el pod del pool de balanceo (no lo reinicia).

**Endpoint:** `GET /health/ready`

## 4. Requisitos Obligatorios

- Ambos endpoints deben responder en **<500ms** (timeout corto para evitar cascading failures)
- **NO** autenticar health checks (públicos para orquestadores)
- Readiness debe validar: DB connection pool, APIs externas críticas, colas de mensajes
- Liveness debe ser simple y rápido (solo validar proceso vivo)
- Responder con código HTTP apropiado:
  - `200 OK`: Healthy
  - `503 Service Unavailable`: Unhealthy
- Incluir detalles en response body (opcional pero recomendado):

```json
{
  "status": "Healthy",
  "checks": {
    "database": "Healthy",
    "cache": "Degraded",
    "externalApi": "Healthy"
  },
  "duration": "00:00:00.0234567"
}
```

## 5. Ejemplo de Implementación

### .NET con Microsoft.Extensions.Diagnostics.HealthChecks

```csharp
// Program.cs
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "database", tags: new[] { "ready" })
    .AddRedis(redisConnection, name: "cache", tags: new[] { "ready" })
    .AddUrlGroup(new Uri("https://api.externa.com/health"), name: "externalApi", tags: new[] { "ready" });

var app = builder.Build();

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false // No ejecuta checks, solo ping
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready"),
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});
```

### AWS ECS Fargate Probes

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: mi-servicio
      livenessProbe:
        httpGet:
          path: /health/live
          port: 8080
        initialDelaySeconds: 10
        periodSeconds: 10
        timeoutSeconds: 1
        failureThreshold: 3
      readinessProbe:
        httpGet:
          path: /health/ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 5
        timeoutSeconds: 1
        failureThreshold: 2
```

### AWS ECS Task Definition

```json
{
  "healthCheck": {
    "command": [
      "CMD-SHELL",
      "curl -f http://localhost:8080/health/live || exit 1"
    ],
    "interval": 30,
    "timeout": 5,
    "retries": 3,
    "startPeriod": 60
  }
}
```

## 6. Mejores Prácticas

- **Liveness ligero:** NO validar dependencias externas (evitar false positives)
- **Readiness exhaustivo:** Validar DB, cache, APIs críticas
- **Timeouts cortos:** <500ms para evitar timeout cascades
- **Degradación parcial:** Readiness puede retornar 200 con warnings si puede operar parcialmente
- **Métricas:** Emitir métrica de health check failures para alertas

## 7. Validación

**Pre-producción:**

- Simular fallo de DB y validar readiness retorna 503
- Validar liveness no se afecta por fallo de dependencias
- Confirmar tiempos de respuesta <500ms bajo carga

**Post-producción:**

- Monitorear restarts automáticos por liveness failures
- Alertas si >10% pods unhealthy por >5min

## 8. Referencias

- [Microsoft Docs - Health Checks](https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks)
- [AWS ECS Fargate Liveness/Readiness Probes](https://AWS ECS Fargate.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Lineamiento de Observabilidad](../../lineamientos/arquitectura/05-observabilidad.md)
