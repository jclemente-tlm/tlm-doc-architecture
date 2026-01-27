---
id: logging
sidebar_position: 1
title: Logging Estructurado
description: Estándares para logging estructurado con Serilog 3.1+, Winston 3.11+ y correlation IDs
---

## 1. Propósito

Este estándar define cómo implementar logging estructurado en aplicaciones de Talma para garantizar trazabilidad, debugging efectivo y observabilidad en entornos distribuidos. Establece el uso de:
- **Formato JSON estructurado** en lugar de texto plano
- **Correlation IDs** para tracing distribuido entre microservicios
- **Niveles de log apropiados** (Trace, Debug, Information, Warning, Error, Critical)
- **Enmascaramiento de datos sensibles** (passwords, tokens, PII)

Permite investigar incidentes correlacionando logs de múltiples servicios mediante correlation IDs únicos por request.

**Versión**: 1.0  
**Última actualización**: 2025-08-08

## 2. Alcance

### Aplica a:
- APIs REST (ASP.NET Core 8.0+, Express.js 4.18+)
- Microservicios backend (.NET, Node.js)
- Workers y background jobs (Hangfire, BullMQ)
- Lambdas AWS (con structured logging)
- Middleware de logging HTTP (request/response logging)

### No aplica a:
- Logs de infraestructura (Docker, Kubernetes, AWS) - gestionados por CloudWatch/Datadog
- Logs de desarrollo local (puede usar formato simple/colorizado)
- Logs de debugging temporal (usar Debug level, se filtra en producción)
- Métricas de performance (ver [Monitoreo y Métricas](./02-monitoreo-metricas.md))

## 3. Tecnologías Obligatorias

| Tecnología | Versión Mínima | Propósito |
|------------|----------------|-----------|
| **Serilog** | 3.1+ | Logging estructurado .NET con sinks configurables |
| **Serilog.AspNetCore** | 8.0+ | Integración con ASP.NET Core y request logging |
| **Serilog.Sinks.Console** | 5.0+ | Output a consola en formato JSON (producción) o simple (desarrollo) |
| **Serilog.Sinks.File** | 5.0+ | Logs rotados por día con retención de 7 días |
| **Serilog.Enrichers.Environment** | 2.3+ | Enrichers: MachineName, EnvironmentName, etc. |
| **Winston** | 3.11+ | Logging estructurado Node.js con transports configurables |
| **winston-daily-rotate-file** | 4.7+ | Rotación diaria de archivos de log en Node.js |
| **AWS CloudWatch Logs** | - | Centralización de logs en AWS (sink: Serilog.Sinks.AwsCloudWatch) |

## 4. Especificaciones Técnicas

### 4.1 Niveles de Log

| Nivel | Uso | Ejemplo | Retención |
|-------|-----|---------|-----------|
| **Trace** | Debugging detallado (desarrollo) | Entrada/salida de métodos, valores de variables | No se envía a producción |
| **Debug** | Información de debugging | Queries SQL, parámetros de funciones | 7 días en producción |
| **Information** | Eventos importantes del flujo | Usuario autenticado, orden creada, proceso completado | 30 días |
| **Warning** | Situaciones anormales recuperables | Cache no disponible (fallback a DB), reintentos | 30 días |
| **Error** | Errores que impiden una operación | Excepción capturada, validación fallida, API externa caída | 90 días |
| **Critical** | Errores que requieren atención inmediata | Base de datos caída, servicio crítico inaccesible | 365 días |

### 4.2 Configuración de Serilog (.NET)

```csharp
// Program.cs
using Serilog;
using Serilog.Events;
using Serilog.Formatting.Json;

// Configuración de Serilog
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .MinimumLevel.Override("Microsoft.EntityFrameworkCore", LogEventLevel.Warning)
    .MinimumLevel.Override("System", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithEnvironmentName()
    .Enrich.WithProperty("Application", "TalmaAPI")
    .Enrich.WithProperty("Version", "1.0.0")
    .WriteTo.Console(new JsonFormatter()) // JSON en producción
    .WriteTo.File(
        new JsonFormatter(),
        "logs/app-.json",
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 7,
        fileSizeLimitBytes: 100_000_000) // 100MB por archivo
    .WriteTo.AmazonCloudWatch(
        logGroup: "/talma/api/production",
        logStreamPrefix: Environment.MachineName,
        restrictedToMinimumLevel: LogEventLevel.Information)
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
    using (LogContext.PushProperty("UserAgent", context.Request.Headers["User-Agent"].ToString()))
    {
        await next();
    }
});

// Request logging automático
app.UseSerilogRequestLogging(options =>
{
    options.MessageTemplate = "HTTP {RequestMethod} {RequestPath} responded {StatusCode} in {Elapsed:0.0000} ms";
    options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
    {
        diagnosticContext.Set("RequestHost", httpContext.Request.Host.Value);
        diagnosticContext.Set("RequestScheme", httpContext.Request.Scheme);
        diagnosticContext.Set("ClientIP", httpContext.Connection.RemoteIpAddress);

        if (httpContext.User.Identity?.IsAuthenticated == true)
        {
            diagnosticContext.Set("UserId", httpContext.User.FindFirst("sub")?.Value);
            diagnosticContext.Set("UserEmail", httpContext.User.FindFirst("email")?.Value);
        }
    };
});

app.Run();

// Cleanup
Log.CloseAndFlush();
```

### 4.3 Uso de Logging en Servicios (.NET)

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

    public async Task<User?> GetUserAsync(Guid userId, CancellationToken cancellationToken)
    {
        _logger.LogInformation("Getting user {UserId}", userId);

        try
        {
            var user = await _repository.GetUserAsync(userId, cancellationToken);

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

    public async Task<User> CreateUserAsync(
        CreateUserRequest request, 
        CancellationToken cancellationToken)
    {
        using (_logger.BeginScope(new Dictionary<string, object>
        {
            ["Operation"] = "CreateUser",
            ["Email"] = request.Email,
            ["RequestId"] = Guid.NewGuid()
        }))
        {
            _logger.LogInformation("Creating new user with email {Email}", request.Email);

            try
            {
                var user = await _repository.CreateUserAsync(request, cancellationToken);

                _logger.LogInformation(
                    "User created successfully with ID {UserId}",
                    user.Id);

                return user;
            }
            catch (DbUpdateException ex)
            {
                _logger.LogError(ex, "Database error creating user");
                throw;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error creating user");
                throw;
            }
        }
    }
}
```

### 4.4 Configuración de Winston (Node.js/TypeScript)

```typescript
// logger.ts
import winston from "winston";
import DailyRotateFile from "winston-daily-rotate-file";

const logFormat = winston.format.combine(
  winston.format.timestamp({ format: "YYYY-MM-DD HH:mm:ss.SSS" }),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: logFormat,
  defaultMeta: {
    service: "talma-api",
    environment: process.env.NODE_ENV || "development",
    version: process.env.APP_VERSION || "1.0.0",
  },
  transports: [
    // Console (JSON en producción, simple en desarrollo)
    new winston.transports.Console({
      format:
        process.env.NODE_ENV === "production"
          ? winston.format.json()
          : winston.format.combine(
              winston.format.colorize(),
              winston.format.simple()
            ),
    }),

    // File rotation para errores
    new DailyRotateFile({
      filename: "logs/error-%DATE%.log",
      datePattern: "YYYY-MM-DD",
      level: "error",
      maxSize: "100m",
      maxFiles: "90d",
    }),

    // File rotation para todos los logs
    new DailyRotateFile({
      filename: "logs/combined-%DATE%.log",
      datePattern: "YYYY-MM-DD",
      maxSize: "100m",
      maxFiles: "30d",
    }),
  ],
});

export default logger;

// middleware.ts - Correlation ID middleware
import { Request, Response, NextFunction } from "express";
import { v4 as uuidv4 } from "uuid";
import logger from "./logger";

export interface RequestWithLogger extends Request {
  correlationId: string;
  logger: winston.Logger;
}

export function correlationIdMiddleware(
  req: RequestWithLogger,
  res: Response,
  next: NextFunction
) {
  const correlationId = (req.headers["x-correlation-id"] as string) || uuidv4();

  req.correlationId = correlationId;
  res.setHeader("X-Correlation-ID", correlationId);

  req.logger = logger.child({
    correlationId,
    requestPath: req.path,
    requestMethod: req.method,
    userAgent: req.headers["user-agent"],
  });

  next();
}

// Logging middleware para HTTP requests
export function requestLoggingMiddleware(
  req: RequestWithLogger,
  res: Response,
  next: NextFunction
) {
  const startTime = Date.now();

  res.on("finish", () => {
    const duration = Date.now() - startTime;

    req.logger.info("HTTP request completed", {
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration,
      clientIP: req.ip,
    });
  });

  next();
}
```

### 4.5 Uso de Logging en Servicios (TypeScript)

```typescript
// userService.ts
import logger from "./logger";

export class UserService {
  async getUser(userId: string, correlationId: string): Promise<User | null> {
    const log = logger.child({ correlationId, userId });
    log.info("Getting user");

    try {
      const user = await this.repository.getUser(userId);

      if (!user) {
        log.warn("User not found");
        return null;
      }

      log.info("Successfully retrieved user", {
        email: user.email,
        isActive: user.isActive,
      });

      return user;
    } catch (error) {
      log.error("Error retrieving user", {
        error: error.message,
        stack: error.stack,
      });
      throw error;
    }
  }

  async createUser(
    request: CreateUserRequest,
    correlationId: string
  ): Promise<User> {
    const log = logger.child({
      correlationId,
      operation: "CreateUser",
      email: request.email,
    });

    log.info("Creating new user");

    try {
      const user = await this.repository.createUser(request);

      log.info("User created successfully", {
        userId: user.id,
      });

      return user;
    } catch (error) {
      log.error("Failed to create user", {
        error: error.message,
        stack: error.stack,
      });
      throw error;
    }
  }
}
```

### 4.6 Formato de Log Estructurado

**Ejemplo de log JSON (.NET):**

```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "Information",
  "message": "Successfully retrieved user {UserId} with email {Email}",
  "properties": {
    "UserId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "Email": "juan@talma.pe",
    "CorrelationId": "a9b8c7d6-5432-10fe-dcba-0987654321ff",
    "RequestPath": "/api/v1/users/3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "RequestMethod": "GET",
    "Application": "TalmaAPI",
    "Environment": "Production",
    "MachineName": "web-server-01",
    "Version": "1.0.0"
  }
}
```

**Ejemplo de log de error (Node.js):**

```json
{
  "timestamp": "2025-01-15T10:31:12.456",
  "level": "error",
  "message": "Error retrieving user",
  "service": "talma-api",
  "environment": "production",
  "version": "1.0.0",
  "correlationId": "b1c2d3e4-6543-21ed-cba9-1234567890ab",
  "userId": "999",
  "requestPath": "/api/v1/users/999",
  "error": "User not found in database",
  "stack": "Error: User not found in database\n    at UserRepository.getUser (/app/repositories/userRepository.ts:45:15)"
}
```

### 4.7 Enmascaramiento de Datos Sensibles

```csharp
// Filtro de Serilog para enmascarar datos sensibles
public class SensitiveDataDestructuringPolicy : IDestructuringPolicy
{
    private static readonly string[] SensitiveFields = {
        "password", "token", "secret", "apikey", "authorization",
        "creditcard", "ssn", "pin", "refreshtoken"
    };

    public bool TryDestructure(
        object value,
        ILogEventPropertyValueFactory propertyValueFactory,
        out LogEventPropertyValue result)
    {
        if (value is string stringValue)
        {
            result = new ScalarValue("***REDACTED***");
            return true;
        }

        result = null;
        return false;
    }
}

// Configuración
Log.Logger = new LoggerConfiguration()
    .Destructure.With<SensitiveDataDestructuringPolicy>()
    .CreateLogger();

// Middleware para enmascarar headers sensibles
app.Use(async (context, next) =>
{
    var authorization = context.Request.Headers["Authorization"].ToString();
    if (!string.IsNullOrEmpty(authorization))
    {
        LogContext.PushProperty("Authorization", "Bearer ***REDACTED***");
    }

    await next();
});
```

```typescript
// Winston: Formatter para enmascarar datos sensibles
const sensitiveFields = [
  "password",
  "token",
  "secret",
  "apiKey",
  "authorization",
  "creditCard",
];

const maskSensitiveData = winston.format((info) => {
  const masked = { ...info };

  for (const field of sensitiveFields) {
    if (masked[field]) {
      masked[field] = "***REDACTED***";
    }
  }

  // Enmascarar en nested objects
  if (masked.request && masked.request.headers) {
    if (masked.request.headers.authorization) {
      masked.request.headers.authorization = "Bearer ***REDACTED***";
    }
  }

  return masked;
});

const logger = winston.createLogger({
  format: winston.format.combine(maskSensitiveData(), winston.format.json()),
  // ...
});
```

## 5. Buenas Prácticas

### 5.1 Correlation IDs

1. **Generar correlation ID en API Gateway o primer servicio**
2. **Propagar correlation ID en headers** (`X-Correlation-ID`)
3. **Incluir correlation ID en todos los logs** mediante `LogContext` (Serilog) o `child logger` (Winston)
4. **Propagar correlation ID a servicios downstream** en llamadas HTTP

```csharp
// Cliente HTTP con correlation ID
public class TalmaHttpClient
{
    private readonly HttpClient _httpClient;
    private readonly IHttpContextAccessor _httpContextAccessor;

    public async Task<T> GetAsync<T>(string url, CancellationToken cancellationToken)
    {
        var request = new HttpRequestMessage(HttpMethod.Get, url);

        // Propagar correlation ID
        var correlationId = _httpContextAccessor.HttpContext?
            .Response.Headers["X-Correlation-ID"].ToString();
        
        if (!string.IsNullOrEmpty(correlationId))
        {
            request.Headers.Add("X-Correlation-ID", correlationId);
        }

        var response = await _httpClient.SendAsync(request, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<T>(cancellationToken);
    }
}
```

### 5.2 Structured Logging

```csharp
// ✅ CORRECTO: Structured logging con propiedades
_logger.LogInformation(
    "Order {OrderId} created for user {UserId} with total {TotalAmount}",
    order.Id,
    order.UserId,
    order.TotalAmount);

// ❌ INCORRECTO: String interpolation (no structured)
_logger.LogInformation($"Order {order.Id} created for user {order.UserId}");
```

### 5.3 Log Scopes

```csharp
// Usar scopes para agrupar logs relacionados
using (_logger.BeginScope("Processing order {OrderId}", orderId))
{
    _logger.LogInformation("Validating order");
    await ValidateOrderAsync(orderId);

    _logger.LogInformation("Processing payment");
    await ProcessPaymentAsync(orderId);

    _logger.LogInformation("Sending confirmation email");
    await SendEmailAsync(orderId);
}

// Todos los logs dentro del scope incluirán OrderId automáticamente
```

### 5.4 Performance

```csharp
// ✅ CORRECTO: Evitar logging en hot paths
if (_logger.IsEnabled(LogLevel.Debug))
{
    _logger.LogDebug("Processing item {ItemId} with complex data {Data}",
        itemId,
        JsonSerializer.Serialize(complexObject));
}

// ❌ INCORRECTO: Logging excesivo en loop (genera overhead)
foreach (var item in items) // 10,000 items
{
    _logger.LogInformation("Processing item {ItemId}", item.Id);
    ProcessItem(item);
}

// ✅ CORRECTO: Log agregado
_logger.LogInformation("Processing {ItemCount} items", items.Count);
foreach (var item in items)
{
    ProcessItem(item);
}
_logger.LogInformation("Processed {ItemCount} items successfully", items.Count);
```

## 6. Antipatrones

### 6.1 ❌ Logging de Datos Sensibles
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

### 6.1 ❌ Logging de Datos Sensibles

**Problema**:
```csharp
// ❌ Loggear password en texto plano
_logger.LogInformation(
    "User {UserId} logged in with password {Password}",
    userId,
    user.Password); // PELIGRO: password expuesto en logs

// ❌ Loggear tokens completos
_logger.LogInformation(
    "Received authorization token: {Token}",
    Request.Headers["Authorization"]); // PELIGRO: token JWT expuesto
```

**Solución**:
```csharp
// ✅ Nunca loggear passwords
_logger.LogInformation("User {UserId} logged in successfully", userId);

// ✅ Enmascarar tokens parcialmente (solo para debugging)
var token = Request.Headers["Authorization"].ToString();
var maskedToken = token.Length > 10 
    ? $"{token.Substring(0, 10)}***REDACTED***" 
    : "***REDACTED***";

_logger.LogDebug("Received authorization token: {Token}", maskedToken);

// ✅ Usar filtro de enmascaramiento automático (ver sección 4.7)
```

### 6.2 ❌ String Interpolation en Logs

**Problema**:
```csharp
// ❌ String interpolation destruye structured logging
_logger.LogInformation($"User {userId} created order {orderId}");

// Log resultante:
// { "message": "User 123 created order 456" } // NO structured, imposible filtrar por userId
```

**Solución**:
```csharp
// ✅ Usar placeholders para structured logging
_logger.LogInformation(
    "User {UserId} created order {OrderId}",
    userId,
    orderId);

// Log resultante:
// {
//   "message": "User {UserId} created order {OrderId}",
//   "properties": { "UserId": 123, "OrderId": 456 }
// } // STRUCTURED, se puede filtrar por UserId = 123
```

### 6.3 ❌ Logging Excesivo en Loops

**Problema**:
```csharp
// ❌ Logging en cada iteración (10,000 logs para 10,000 items)
foreach (var item in items) // 10,000 items
{
    _logger.LogInformation("Processing item {ItemId}", item.Id);
    ProcessItem(item);
    _logger.LogInformation("Processed item {ItemId} successfully", item.Id);
}

// Genera 20,000 logs, overhead de performance y almacenamiento
```

**Solución**:
```csharp
// ✅ Logging agregado (2 logs en total)
_logger.LogInformation("Processing {ItemCount} items", items.Count);

var processedCount = 0;
var failedCount = 0;

foreach (var item in items)
{
    try
    {
        ProcessItem(item);
        processedCount++;
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Failed to process item {ItemId}", item.Id);
        failedCount++;
    }
}

_logger.LogInformation(
    "Processed {ProcessedCount} items successfully, {FailedCount} failed",
    processedCount,
    failedCount);
```

### 6.4 ❌ Ausencia de Correlation IDs

**Problema**:
```csharp
// ❌ Sin correlation ID, imposible correlacionar logs entre servicios
// Servicio 1 (API Gateway)
_logger.LogInformation("Received request to /api/orders");

// Servicio 2 (Order Service)
_logger.LogInformation("Creating order");

// Servicio 3 (Payment Service)
_logger.LogInformation("Processing payment");

// Imposible saber qué logs pertenecen al mismo request
```

**Solución**:
```csharp
// ✅ Propagar correlation ID en todos los servicios
// API Gateway
var correlationId = Guid.NewGuid().ToString();
LogContext.PushProperty("CorrelationId", correlationId);
_logger.LogInformation("Received request to /api/orders");

// Order Service (recibe X-Correlation-ID header)
var correlationId = Request.Headers["X-Correlation-ID"];
LogContext.PushProperty("CorrelationId", correlationId);
_logger.LogInformation("Creating order");

// Payment Service (recibe X-Correlation-ID header)
var correlationId = Request.Headers["X-Correlation-ID"];
LogContext.PushProperty("CorrelationId", correlationId);
_logger.LogInformation("Processing payment");

// Ahora se pueden filtrar logs por CorrelationId: "a9b8c7d6-5432-10fe-dcba-0987654321ff"
```

## 7. Validación y Testing

### 7.1 Tests Unitarios de Logging

```csharp
public class UserServiceTests
{
    [Fact]
    public async Task GetUserAsync_UserNotFound_LogsWarning()
    {
        // Arrange
        var loggerMock = new Mock<ILogger<UserService>>();
        var repositoryMock = new Mock<IUserRepository>();
        repositoryMock
            .Setup(r => r.GetUserAsync(It.IsAny<Guid>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync((User?)null);

        var service = new UserService(loggerMock.Object, repositoryMock.Object);

        // Act
        var result = await service.GetUserAsync(Guid.NewGuid(), CancellationToken.None);

        // Assert
        result.Should().BeNull();
        loggerMock.Verify(
            x => x.Log(
                LogLevel.Warning,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("not found")),
                null,
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }
}
```

### 7.2 Verificación de Logs en Tests de Integración

```csharp
public class LoggingIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    private readonly InMemorySink _logSink;

    public LoggingIntegrationTests(WebApplicationFactory<Program> factory)
    {
        _logSink = new InMemorySink();

        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.UseSerilog((context, config) =>
            {
                config.WriteTo.Sink(_logSink);
            });
        }).CreateClient();
    }

    [Fact]
    public async Task GetUser_Success_LogsInformation()
    {
        // Act
        var response = await _client.GetAsync("/api/v1/users/3fa85f64-5717-4562-b3fc-2c963f66afa6");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var logs = _logSink.LogEvents;
        logs.Should().Contain(l =>
            l.Level == LogEventLevel.Information &&
            l.MessageTemplate.Text.Contains("Successfully retrieved user"));
    }
}

public class InMemorySink : ILogEventSink
{
    public List<LogEvent> LogEvents { get; } = new();

    public void Emit(LogEvent logEvent)
    {
        LogEvents.Add(logEvent);
    }
}
```

### 7.3 Validación de Correlation IDs

```csharp
[Fact]
public async Task Request_WithoutCorrelationId_GeneratesNewOne()
{
    // Act
    var response = await _client.GetAsync("/api/v1/users");

    // Assert
    response.Headers.Should().ContainKey("X-Correlation-ID");
    var correlationId = response.Headers.GetValues("X-Correlation-ID").First();
    correlationId.Should().NotBeNullOrWhiteSpace();
    Guid.TryParse(correlationId, out _).Should().BeTrue();
}

[Fact]
public async Task Request_WithCorrelationId_PropagatesToResponse()
{
    // Arrange
    var correlationId = Guid.NewGuid().ToString();
    _client.DefaultRequestHeaders.Add("X-Correlation-ID", correlationId);

    // Act
    var response = await _client.GetAsync("/api/v1/users");

    // Assert
    response.Headers.GetValues("X-Correlation-ID").First().Should().Be(correlationId);
}
```

## 8. Referencias

### Lineamientos Relacionados
- [Observabilidad](/docs/fundamentos-corporativos/lineamientos/arquitectura/observabilidad) - Estrategia general de observabilidad
- [Seguridad desde el Diseño](/docs/fundamentos-corporativos/lineamientos/seguridad/seguridad-desde-el-diseno) - Protección de datos sensibles en logs

### Estándares Relacionados
- [Monitoreo y Métricas](./02-monitoreo-metricas.md) - Métricas complementarias a logs
- [Desarrollo con TypeScript](../codigo/02-typescript.md) - Configuración de logging en Node.js

### ADRs Relacionados
- [ADR-016: Logging Estructurado](/docs/decisiones-de-arquitectura/adr-016-logging-estructurado) - Decisión de usar Serilog y Winston

### Recursos Externos
- [Serilog Documentation](https://serilog.net/)
- [Serilog Best Practices](https://github.com/serilog/serilog/wiki/Structured-Data)
- [Winston Documentation](https://github.com/winstonjs/winston)
- [AWS CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html)
- [Structured Logging Best Practices](https://www.loggly.com/ultimate-guide/node-logging-basics/)

## 9. Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-08-08 | Equipo de Arquitectura | Versión inicial con template de 9 secciones |

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
