---
id: logging
sidebar_position: 1
title: Logging Estructurado
description: Estándares para logging estructurado, niveles de log y correlation IDs
---

## 1. Principios de Logging

- **Structured logging**: Usar formato estructurado (JSON) en lugar de texto plano.
- **Correlation IDs**: Incluir identificadores de correlación para tracing distribuido.
- **Niveles apropiados**: Usar niveles de log correctamente (Trace, Debug, Information, Warning, Error, Critical).
- **No loggear datos sensibles**: Nunca loggear passwords, tokens, PII sin enmascarar.
- **Performance**: Evitar logging excesivo que impacte performance.

## 2. Niveles de Log

| Nivel           | Uso                                      | Ejemplo                                               |
| --------------- | ---------------------------------------- | ----------------------------------------------------- |
| **Trace**       | Debugging detallado (desarrollo)         | Entrada/salida de métodos, valores de variables       |
| **Debug**       | Información de debugging                 | Queries SQL, parámetros de funciones                  |
| **Information** | Eventos importantes del flujo            | Usuario autenticado, orden creada, proceso completado |
| **Warning**     | Situaciones anormales recuperables       | Cache no disponible (fallback a DB), reintentos       |
| **Error**       | Errores que impiden una operación        | Excepción capturada, validación fallida               |
| **Critical**    | Errores que requieren atención inmediata | Base de datos caída, servicio crítico inaccesible     |

## 3. Implementación con Serilog (C#)

### Configuración básica

```csharp
// Program.cs
using Serilog;
using Serilog.Events;

// Configuración de Serilog
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .MinimumLevel.Override("System", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithEnvironmentName()
    .Enrich.WithProperty("Application", "TalmaAPI")
    .WriteTo.Console(new JsonFormatter())
    .WriteTo.File(
        new JsonFormatter(),
        "logs/app-.json",
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 7)
    .CreateLogger();

var builder = WebApplication.CreateBuilder(args);

// Usar Serilog como logger
builder.Host.UseSerilog();

var app = builder.Build();

// Middleware para correlation ID
app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-ID"].FirstOrDefault()
        ?? Guid.NewGuid().ToString();

    context.Response.Headers.Add("X-Correlation-ID", correlationId);

    using (LogContext.PushProperty("CorrelationId", correlationId))
    using (LogContext.PushProperty("RequestPath", context.Request.Path))
    using (LogContext.PushProperty("RequestMethod", context.Request.Method))
    {
        await next();
    }
});

// Request logging
app.UseSerilogRequestLogging(options =>
{
    options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
    {
        diagnosticContext.Set("RequestHost", httpContext.Request.Host.Value);
        diagnosticContext.Set("RequestScheme", httpContext.Request.Scheme);
        diagnosticContext.Set("UserAgent", httpContext.Request.Headers["User-Agent"].ToString());

        if (httpContext.User.Identity?.IsAuthenticated == true)
        {
            diagnosticContext.Set("UserId", httpContext.User.FindFirst("sub")?.Value);
            diagnosticContext.Set("UserEmail", httpContext.User.FindFirst("email")?.Value);
        }
    };
});

app.Run();
```

### Uso en servicios

```csharp
public class UserService
{
    private readonly ILogger<UserService> _logger;
    private readonly IUserRepository _repository;

    public UserService(ILogger<UserService> logger, IUserRepository repository)
    {
        _logger = logger;
        _repository = repository;
    }

    public async Task<User> GetUserAsync(int userId)
    {
        _logger.LogInformation("Getting user {UserId}", userId);

        try
        {
            var user = await _repository.GetUserAsync(userId);

            if (user == null)
            {
                _logger.LogWarning("User {UserId} not found", userId);
                return null;
            }

            _logger.LogInformation(
                "Successfully retrieved user {UserId} with email {Email}",
                userId,
                user.Email);

            return user;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Error retrieving user {UserId}",
                userId);
            throw;
        }
    }

    public async Task<User> CreateUserAsync(CreateUserRequest request)
    {
        using (_logger.BeginScope(new Dictionary<string, object>
        {
            ["Operation"] = "CreateUser",
            ["Email"] = request.Email
        }))
        {
            _logger.LogInformation("Creating new user");

            try
            {
                var user = await _repository.CreateUserAsync(request);

                _logger.LogInformation(
                    "User created successfully with ID {UserId}",
                    user.Id);

                return user;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create user");
                throw;
            }
        }
    }
}
```

## 4. Implementación con Winston (TypeScript/Node.js)

```typescript
import winston from "winston";

// Configuración de Winston
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json(),
  ),
  defaultMeta: {
    service: "talma-api",
    environment: process.env.NODE_ENV,
  },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple(),
      ),
    }),
    new winston.transports.File({
      filename: "logs/error.log",
      level: "error",
    }),
    new winston.transports.File({
      filename: "logs/combined.log",
    }),
  ],
});

export default logger;

// Uso en servicios
class UserService {
  async getUser(userId: number): Promise<User | null> {
    logger.info("Getting user", { userId });

    try {
      const user = await this.repository.getUser(userId);

      if (!user) {
        logger.warn("User not found", { userId });
        return null;
      }

      logger.info("Successfully retrieved user", {
        userId,
        email: user.email,
      });

      return user;
    } catch (error) {
      logger.error("Error retrieving user", {
        userId,
        error: error.message,
        stack: error.stack,
      });
      throw error;
    }
  }
}

// Middleware para correlation ID
app.use((req, res, next) => {
  const correlationId = req.headers["x-correlation-id"] || uuid();
  res.setHeader("X-Correlation-ID", correlationId);

  req.logger = logger.child({
    correlationId,
    requestPath: req.path,
    requestMethod: req.method,
  });

  next();
});
```

## 5. Formato de Log Estructurado

### Ejemplo de log JSON

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "Information",
  "message": "Successfully retrieved user {UserId} with email {Email}",
  "properties": {
    "UserId": 123,
    "Email": "juan@talma.pe",
    "CorrelationId": "a9b8c7d6-5432-10fe-dcba-0987654321ff",
    "RequestPath": "/api/v1/users/123",
    "RequestMethod": "GET",
    "Application": "TalmaAPI",
    "Environment": "Production",
    "MachineName": "web-server-01"
  }
}
```

### Ejemplo de log de error

```json
{
  "timestamp": "2024-01-15T10:31:12.456Z",
  "level": "Error",
  "message": "Error retrieving user {UserId}",
  "properties": {
    "UserId": 999,
    "CorrelationId": "b1c2d3e4-6543-21ed-cba9-1234567890ab",
    "RequestPath": "/api/v1/users/999",
    "ExceptionType": "SqlException",
    "ExceptionMessage": "Connection timeout",
    "StackTrace": "at UserRepository.GetUserAsync..."
  }
}
```

## 6. Prácticas de Seguridad

### Enmascaramiento de datos sensibles

```csharp
public class SensitiveDataFilter : ILogEventFilter
{
    private static readonly string[] SensitiveFields = {
        "password", "token", "secret", "apikey", "authorization"
    };

    public bool IsEnabled(LogEvent logEvent)
    {
        foreach (var property in logEvent.Properties)
        {
            if (SensitiveFields.Any(field =>
                property.Key.Contains(field, StringComparison.OrdinalIgnoreCase)))
            {
                logEvent.RemovePropertyIfPresent(property.Key);
                logEvent.AddOrUpdateProperty(
                    new LogEventProperty(property.Key, new ScalarValue("***REDACTED***")));
            }
        }

        return true;
    }
}

// Configuración
Log.Logger = new LoggerConfiguration()
    .Filter.With<SensitiveDataFilter>()
    .CreateLogger();
```

## 7. Integración con Sistemas de Observabilidad

### AWS CloudWatch

```csharp
// Serilog.Sinks.AwsCloudWatch
.WriteTo.AmazonCloudWatch(
    logGroup: "/talma/api/production",
    logStreamPrefix: "web-server",
    restrictedToMinimumLevel: LogEventLevel.Information,
    cloudWatchClient: new AmazonCloudWatchLogsClient())
```

### Elasticsearch (ELK Stack)

```csharp
// Serilog.Sinks.Elasticsearch
.WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri("http://elasticsearch:9200"))
{
    IndexFormat = "talma-api-logs-{0:yyyy.MM.dd}",
    AutoRegisterTemplate = true,
    NumberOfShards = 2,
    NumberOfReplicas = 1
})
```

## 8. Checklist de Logging

- [ ] **JSON format**: Logs en formato JSON estructurado
- [ ] **Correlation IDs**: Incluidos en todos los logs
- [ ] **Niveles apropiados**: Uso correcto de Information/Warning/Error
- [ ] **No datos sensibles**: Passwords/tokens enmascarados
- [ ] **Performance**: Sin logging excesivo en hot paths
- [ ] **Contexto suficiente**: Información para debugging efectivo
- [ ] **Centralización**: Logs enviados a sistema centralizado (CloudWatch/ELK)

## 📖 Referencias

### Lineamientos relacionados

- [Observabilidad](/docs/fundamentos-corporativos/lineamientos/arquitectura/observabilidad)

### ADRs relacionados

- [ADR-016: Logging estructurado](/docs/decisiones-de-arquitectura/adr-016-logging-estructurado)

### Recursos externos

- [Serilog Documentation](https://serilog.net/)
- [Winston Documentation](https://github.com/winstonjs/winston)
- [Structured Logging Best Practices](https://www.loggly.com/ultimate-guide/node-logging-basics/)
