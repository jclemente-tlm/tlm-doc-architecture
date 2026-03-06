---
id: app-configuration
sidebar_position: 4
title: Configuración de Aplicaciones
description: Estándar para externalizar configuración usando variables de entorno, IOptions<T> y Azure Key Vault. Prohibido hardcodear valores.
tags: [desarrollo, configuracion, dotnet, options-pattern, keyvault]
---

# Configuración de Aplicaciones

## Contexto

Gestionar configuración fuera del código fuente garantiza que el mismo artefacto funcione en cualquier entorno. Complementa el lineamiento [Configuración de Entornos](../../lineamientos/operabilidad/03-configuracion-entornos.md).

**Cuándo aplicar:** Todo proyecto .NET con valores que varían por entorno (connection strings, URLs, secrets, feature flags).

**Conceptos incluidos:**

- **Configuración Externalizada** — Variables de entorno y archivos por ambiente
- **Strongly Typed Config** — Options pattern con `IOptions<T>`
- **Secrets Management** — Azure Key Vault y credenciales locales

---

## Stack Tecnológico

| Componente  | Tecnología                   | Versión | Uso                          |
| ----------- | ---------------------------- | ------- | ---------------------------- |
| **Config**  | ASP.NET Configuration        | 8.0+    | Sistema de configuración     |
| **Options** | Microsoft.Extensions.Options | 8.0+    | Strongly-typed config        |
| **Secrets** | Azure Key Vault              | —       | Secretos en producción       |
| **Dev**     | dotnet user-secrets          | —       | Secretos en desarrollo local |

---

## Relación entre Conceptos

```mermaid
graph LR
    A[Env Variables] --> C[ASP.NET Config]
    B[appsettings.json] --> C
    C --> D[IOptions T]
    E[Key Vault] --> C
    D --> F[Mismo artifact por ambiente]

    style C fill:#e1f5ff,color:#000000
    style D fill:#e8f5e9,color:#000000
    style E fill:#fce4ec,color:#000000
```

---

## Configuración Externalizada

### ¿Qué es Configuración Externalizada?

Separar configuración del código, permitiendo cambiar comportamiento sin recompilar.

**Principios:**

- **12-Factor App**: Config en environment
- **Secrets separados**: Nunca en código o archivos
- **Por ambiente**: Dev, staging, prod diferentes
- **Centralizado**: Única fuente de verdad
- **Runtime**: Cambios sin redeploy (opcional)

**Propósito:** Flexibilidad, seguridad, portabilidad.

**Beneficios:**
✅ Mismo artifact para todos los ambientes
✅ Secretos seguros
✅ Cambios sin recompilación
✅ Auditoría centralizada

### ASP.NET Configuration

```csharp
// Program.cs - Configuración por capas

var builder = WebApplication.CreateBuilder(args);

// 1. appsettings.json (configuración base)
builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);

// 2. appsettings.{Environment}.json (overrides por ambiente)
builder.Configuration.AddJsonFile(
    $"appsettings.{builder.Environment.EnvironmentName}.json",
    optional: true,
    reloadOnChange: true);

// 3. Environment variables (overrides desde sistema)
builder.Configuration.AddEnvironmentVariables(prefix: "CUSTOMER_SERVICE_");

// 4. AWS Secrets Manager (secretos)
if (!builder.Environment.IsDevelopment())
{
    builder.Configuration.AddSecretsManager(configurator: options =>
    {
        options.SecretFilter = secret => secret.Name.StartsWith("customer-service/");
        options.PollingInterval = TimeSpan.FromMinutes(5);
    });
}

// 5. AWS Parameter Store (parámetros de configuración)
if (!builder.Environment.IsDevelopment())
{
    builder.Configuration.AddSystemsManager(configureSource: source =>
    {
        source.Path = "/customer-service";
        source.Optional = true;
        source.ReloadAfter = TimeSpan.FromMinutes(5);
    });
}

// 6. Command line arguments (overrides finales)
builder.Configuration.AddCommandLine(args);

var app = builder.Build();
```

### Configuration Structure

```json
// appsettings.json - Valores DEFAULT
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "ConnectionStrings": {
    "CustomerDatabase": "Host=localhost;Port=5432;Database=customers;Username=dev;Password=dev"
  },
  "Kafka": {
    "BootstrapServers": "localhost:9092",
    "GroupId": "customer-service",
    "AutoOffsetReset": "Earliest"
  },
  "Redis": {
    "ConnectionString": "localhost:6379",
    "InstanceName": "customer-service:"
  },
  "Features": {
    "EnableCache": true,
    "EnableEventPublishing": true
  },
  "RateLimiting": {
    "PermitLimit": 100,
    "Window": "00:01:00"
  }
}
```

```json
// appsettings.Development.json - Overrides para DEV
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "CustomerService": "Trace"
    }
  },
  "Features": {
    "EnableCache": false // Deshabilitar cache en dev para testing
  }
}
```

```json
// appsettings.Production.json - Overrides para PROD
{
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  },
  "ConnectionStrings": {
    // ❌ NO poner valores reales aquí
    // ✅ Usar AWS Secrets Manager o environment variables
    "CustomerDatabase": "placeholder-will-be-overridden"
  }
}
```

### Strongly Typed Configuration

```csharp
// Configuration/KafkaOptions.cs - Options pattern

public class KafkaOptions
{
    public const string SectionName = "Kafka";

    public string BootstrapServers { get; set; } = default!;
    public string GroupId { get; set; } = default!;
    public string AutoOffsetReset { get; set; } = "Earliest";
    public int SessionTimeoutMs { get; set; } = 30000;
    public bool EnableAutoCommit { get; set; } = false;
}

// Program.cs - Bind configuration
builder.Services.Configure<KafkaOptions>(
    builder.Configuration.GetSection(KafkaOptions.SectionName));

// Validar configuración al inicio
builder.Services.AddOptions<KafkaOptions>()
    .Validate(options =>
    {
        return !string.IsNullOrEmpty(options.BootstrapServers);
    }, "BootstrapServers is required")
    .ValidateOnStart();

// Uso en servicio
public class KafkaProducer
{
    private readonly KafkaOptions _options;

    public KafkaProducer(IOptions<KafkaOptions> options)
    {
        _options = options.Value;
    }

    public async Task PublishAsync(string topic, string message)
    {
        var config = new ProducerConfig
        {
            BootstrapServers = _options.BootstrapServers
        };
        // ...
    }
}
```

### Environment Variables en Docker

```yaml
# docker-compose.yml - Variables de entorno

version: "3.8"

services:
  customer-service:
    image: ghcr.io/talma/customer-service:1.2.3
    environment:
      # ASP.NET Environment
      - ASPNETCORE_ENVIRONMENT=Production

      # Prefijo para separar configs de servicios
      - CUSTOMER_SERVICE_ConnectionStrings__CustomerDatabase=Host=postgres;Port=5432;Database=customers;Username=${DB_USER};Password=${DB_PASSWORD}
      - CUSTOMER_SERVICE_Kafka__BootstrapServers=kafka:9092
      - CUSTOMER_SERVICE_Redis__ConnectionString=redis:6379

      # AWS para Secrets Manager
      - AWS_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

      # Observabilidad
      - CUSTOMER_SERVICE_Logging__LogLevel__Default=Information
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://grafana-alloy:4317

    ports:
      - "8080:8080"

    depends_on:
      - postgres
      - kafka
      - redis

    networks:
      - customer-network

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=customers
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - customer-network

  kafka:
    image: apache/kafka:3.6.1
    environment:
      - KAFKA_NODE_ID=1
      - KAFKA_PROCESS_ROLES=broker,controller
      - KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
      - KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER
      - KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      - KAFKA_CONTROLLER_QUORUM_VOTERS=1@kafka:9093
    networks:
      - customer-network

  redis:
    image: redis:7.2-alpine
    networks:
      - customer-network

networks:
  customer-network:

volumes:
  postgres-data:
```

```bash
# .env - Variables sensibles (NO commitear)
# Agregar .env a .gitignore

DB_USER=customer_user
DB_PASSWORD=Sup3rS3cr3t!
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** externalizar toda configuración que varíe por entorno
- **MUST** usar Options pattern (`IOptions<T>`) para configuración strongly-typed
- **MUST** agregar `ValidateOnStart()` para detectar configuración inválida al arrancar
- **MUST** usar Azure Key Vault o AWS Secrets Manager para secretos en producción
- **MUST** usar `dotnet user-secrets` para secretos en desarrollo local

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar prefijo de servicio en variables de entorno (ej: `CUSTOMER_SERVICE_`)
- **SHOULD** configurar `reloadOnChange: true` para actualizar sin redeploy
- **SHOULD** validar configuración crítica con annotations de `DataAnnotations`

### MUST NOT (Prohibido)

- **MUST NOT** hardcodear valores de configuración en el código fuente
- **MUST NOT** commitear secretos en archivos `appsettings.json` o `.env`
- **MUST NOT** usar `IConfiguration` directamente en servicios de dominio

---

## Referencias

- [Lineamiento Configuración de Entornos](../../lineamientos/operabilidad/03-configuracion-entornos.md) — lineamiento que origina este estándar
- [ASP.NET Core Configuration](https://learn.microsoft.com/aspnet/core/fundamentals/configuration/) — documentación oficial
- [Options pattern](https://learn.microsoft.com/dotnet/core/extensions/options) — patrón `IOptions<T>`
- [Azure Key Vault](https://learn.microsoft.com/azure/key-vault/) — gestión de secretos
- [Package Management](./package-management.md) — gestión de dependencias NuGet

---

**Última actualización**: 5 de marzo de 2026
**Responsable**: Equipo de Arquitectura
