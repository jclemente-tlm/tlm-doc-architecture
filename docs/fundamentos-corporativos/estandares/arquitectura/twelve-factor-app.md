---
id: twelve-factor-app
sidebar_position: 1
title: Metodología 12-Factor App
description: Metodología para construir aplicaciones cloud-native con portabilidad y escalabilidad
---

# Metodología 12-Factor App

## Contexto

Este estándar define cómo implementar los [12 factores](https://12factor.net/) para construir aplicaciones cloud-native. Complementa el [lineamiento de Cloud Native](../../lineamientos/arquitectura/03-cloud-native.md) asegurando **portabilidad, declaratividad y escalabilidad** en entornos cloud.

---

## Stack Tecnológico

| Componente        | Tecnología          | Versión | Uso                         |
| ----------------- | ------------------- | ------- | --------------------------- |
| **Framework**     | ASP.NET Core        | 8.0+    | Framework base cloud-native |
| **Contenedores**  | Docker              | 24.0+   | Containerization            |
| **Orchestration** | AWS ECS Fargate     | -       | Container orchestration     |
| **Config**        | AWS Parameter Store | -       | Configuration management    |
| **Secrets**       | AWS Secrets Manager | -       | Secrets management          |
| **Logs**          | Grafana Loki        | 2.9+    | Centralized logging         |

---

## Los 12 Factores

### I. Codebase

**Principio:** Un codebase rastreado en control de versiones, múltiples deploys

```yaml
# ✅ Cumplimiento

✅ Hacer:
- Un repositorio Git por servicio
- Múltiples branches (develop, staging, production)
- Múltiples deploys desde mismo codebase (dev, qa, prod)
- Versioning con tags semánticos (v1.2.3)

❌ No hacer:
- Múltiples repos para misma app
- Código duplicado entre ambientes
- Configuración hardcoded por ambiente
- Branches por ambiente (anti-pattern)

# Estructura recomendada
talma/orders-service/
├── .git/
├── src/
├── tests/
├── Dockerfile
├── .github/workflows/  # CI/CD para todos los ambientes
└── README.md
```

### II. Dependencies

**Principio:** Declarar y aislar dependencias explícitamente

```csharp
// ✅ Dependencies explícitas en .csproj
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <!-- ✅ Versiones explícitas (no floating versions) -->
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.0" />
    <PackageReference Include="StackExchange.Redis" Version="2.7.10" />
    <PackageReference Include="AWSSDK.S3" Version="3.7.307" />
    <PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />

    <!-- ❌ Evitar floating versions como 8.* o 8.0.* -->
  </ItemGroup>
</Project>

// ✅ Package lock para reproducibilidad
// packages.lock.json se genera automáticamente
```

```dockerfile
# ✅ Dependencies aisladas en contenedor
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS base
WORKDIR /app

# ✅ Todas las dependencias están en la imagen
# No requiere instalaciones externas en runtime
COPY --from=build /app/publish .

# ❌ No instalar dependencias en runtime
# RUN apt-get install... (anti-pattern)
```

### III. Config

**Principio:** Configuración en el entorno, no en código

```csharp
// ✅ Configuration desde environment variables
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // ✅ Leer desde appsettings.json + env vars
        services.AddDbContext<OrdersDbContext>(options =>
        {
            // DATABASE_URL override appsettings.json
            var connectionString = Configuration.GetConnectionString("OrdersDb");
            options.UseNpgsql(connectionString);
        });

        // ✅ AWS services desde env vars
        services.AddAWSService<IAmazonS3>();

        // ✅ Redis desde env vars
        services.AddStackExchangeRedisCache(options =>
        {
            options.Configuration = Configuration["Redis:ConnectionString"];
        });
    }
}

// appsettings.json (valores por defecto)
{
  "ConnectionStrings": {
    "OrdersDb": "Host=localhost;Database=orders;Username=dev;Password=dev"
  },
  "Redis": {
    "ConnectionString": "localhost:6379"
  }
}

// ✅ Environment variables override (ECS Task Definition)
Environment:
  - Name: ConnectionStrings__OrdersDb
    Value: "Host=prod-db.talma.internal;Database=orders;Username=orders_api;Password={{ssm:/prod/orders/db-password}}"
  - Name: Redis__ConnectionString
    Value: "prod-redis.talma.internal:6379"
```

```bash
# ✅ Local development con .env
DATABASE_URL=Host=localhost;Database=orders;Username=dev;Password=dev
REDIS_URL=localhost:6379
AWS_REGION=us-east-1

# ❌ No commitear .env con valores productivos
```

### IV. Backing Services

**Principio:** Tratar backing services como recursos adjuntos

```csharp
// ✅ Backing services intercambiables via configuración

public interface IStorageService
{
    Task<string> UploadFileAsync(Stream file, string key);
}

// ✅ Implementación S3 (production)
public class S3StorageService : IStorageService
{
    private readonly IAmazonS3 _s3Client;

    public async Task<string> UploadFileAsync(Stream file, string key)
    {
        await _s3Client.PutObjectAsync(new PutObjectRequest
        {
            BucketName = _bucketName,
            Key = key,
            InputStream = file
        });

        return $"s3://{_bucketName}/{key}";
    }
}

// ✅ Implementación local filesystem (development)
public class LocalStorageService : IStorageService
{
    public async Task<string> UploadFileAsync(Stream file, string key)
    {
        var path = Path.Combine(_basePath, key);
        using var fileStream = File.Create(path);
        await file.CopyToAsync(fileStream);
        return path;
    }
}

// ✅ Registration basado en ambiente
builder.Services.AddSingleton<IStorageService>(sp =>
{
    var env = sp.GetRequiredService<IWebHostEnvironment>();
    return env.IsProduction()
        ? new S3StorageService(sp.GetRequiredService<IAmazonS3>())
        : new LocalStorageService("/tmp/uploads");
});

// ✅ Cambiar de proveedor solo requiere cambio de configuración
// Database: PostgreSQL → MySQL (cambiar connection string)
// Cache: Redis → Memcached (cambiar implementation)
// Queue: SQS → Kafka (cambiar implementation)
```

### V. Build, Release, Run

**Principio:** Separar estrictamente las etapas de construcción y ejecución

```yaml
# ✅ Pipeline CI/CD con 3 etapas separadas

# 1. BUILD: Código → Artefacto
build:
  stage: build
  script:
    - dotnet build -c Release
    - dotnet test
    - dotnet publish -c Release -o ./publish
    - docker build -t orders-api:${CI_COMMIT_SHA} .
    - docker push ghcr.io/talma/orders-api:${CI_COMMIT_SHA}
  artifacts:
    paths:
      - ./publish

# 2. RELEASE: Artefacto + Config → Release
release:
  stage: release
  script:
    - |
      # ✅ Crear release manifest
      cat > release-manifest.json <<EOF
      {
        "version": "${CI_COMMIT_SHA}",
        "image": "ghcr.io/talma/orders-api:${CI_COMMIT_SHA}",
        "config": {
          "DATABASE_URL": "{{ssm:/prod/orders/db-url}}",
          "REDIS_URL": "{{ssm:/prod/orders/redis-url}}"
        }
      }
      EOF
    - aws s3 cp release-manifest.json s3://talma-releases/orders-api/${CI_COMMIT_SHA}/

# 3. RUN: Ejecutar release en ambiente
deploy-production:
  stage: deploy
  script:
    - |
      # ✅ Deploy release inmutable
      aws ecs update-service \
        --cluster production \
        --service orders-api \
        --task-definition orders-api:${TASK_DEF_REVISION} \
        --force-new-deployment
  environment:
    name: production
  when: manual

# ❌ Anti-pattern: Compilar en producción
# RUN dotnet build ... (NO)
```

### VI. Processes

**Principio:** Ejecutar la app como uno o más procesos stateless

```csharp
// ✅ Stateless: sin estado local

public class OrdersController : ControllerBase
{
    private readonly IDistributedCache _cache;  // ✅ Estado en Redis
    private readonly OrdersDbContext _db;       // ✅ Estado en PostgreSQL

    // ❌ NO usar estado local
    // private static List<Order> _orders = new();  // Anti-pattern

    [HttpPost]
    public async Task<IActionResult> CreateOrder(CreateOrderRequest request)
    {
        // ✅ Todo el estado persiste en backing services
        var order = new Order { /* ... */ };
        await _db.Orders.AddAsync(order);
        await _db.SaveChangesAsync();

        // ✅ Cache en Redis (compartido entre instancias)
        await _cache.SetStringAsync(
            $"order:{order.Id}",
            JsonSerializer.Serialize(order),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(15)
            });

        return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
    }
}

// ✅ Session en Redis
builder.Services.AddSession(options =>
{
    options.Cookie.Name = ".Talma.Session";
    options.IdleTimeout = TimeSpan.FromMinutes(30);
});

builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration["Redis:ConnectionString"];
});
```

### VII. Port Binding

**Principio:** Exportar servicios via port binding

```csharp
// ✅ Self-contained service con HTTP server embebido

// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Kestrel como HTTP server self-contained
builder.WebHost.ConfigureKestrel(options =>
{
    // ✅ Bind a puerto desde env var
    var port = int.Parse(Environment.GetEnvironmentVariable("PORT") ?? "8080");
    options.ListenAnyIP(port);
});

var app = builder.Build();
app.Run();

// ✅ No requiere IIS, Apache, Nginx (opcional para reverse proxy)
```

```dockerfile
# Dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine
WORKDIR /app
COPY --from=build /app/publish .

# ✅ Exponer puerto
EXPOSE 8080

# ✅ Self-contained: inicia su propio HTTP server
ENTRYPOINT ["dotnet", "OrdersApi.dll"]
```

```yaml
# ECS Task Definition
{
  "containerDefinitions":
    [
      {
        "name": "orders-api",
        "image": "ghcr.io/talma/orders-api:latest",
        "portMappings": [{ "containerPort": 8080, "protocol": "tcp" }],
        "environment":
          [
            { "name": "PORT", "value": "8080" },
            { "name": "ASPNETCORE_URLS", "value": "http://+:8080" },
          ],
      },
    ],
}
```

### VIII. Concurrency

**Principio:** Escalar horizontalmente via process model

```yaml
# ✅ Escalar agregando más procesos (containers)

# ECS Auto Scaling
resource "aws_appautoscaling_target" "orders_api" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/production/orders-api"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "orders_api_cpu" {
  name               = "orders-api-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.orders_api.resource_id
  scalable_dimension = aws_appautoscaling_target.orders_api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.orders_api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0  # ✅ Escalar cuando CPU > 70%
  }
}

# ✅ Resultado: 2-10 instancias del mismo proceso
# Load balancer distribuye tráfico entre instancias
```

### IX. Disposability

**Principio:** Maximizar robustez con fast startup y graceful shutdown

```csharp
// ✅ Fast startup: minimizar tiempo de inicialización

public class Program
{
    public static async Task Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);

        // ✅ Configuración lazy: no pre-cargar todo
        builder.Services.AddDbContext<OrdersDbContext>();

        var app = builder.Build();

        // ✅ NO ejecutar migrations en startup (usar job separado)
        // await ApplyMigrationsAsync();  // Anti-pattern

        // ✅ Graceful shutdown con timeout
        var lifetime = app.Services.GetRequiredService<IHostApplicationLifetime>();
        lifetime.ApplicationStopping.Register(() =>
        {
            Console.WriteLine("Application is stopping. Draining connections...");
        });

        await app.RunAsync();
    }
}

// ✅ Implementar graceful shutdown
builder.Services.AddHostedService<GracefulShutdownService>();

public class GracefulShutdownService : IHostedService
{
    private readonly ILogger<GracefulShutdownService> _logger;
    private readonly IHostApplicationLifetime _lifetime;

    public Task StartAsync(CancellationToken cancellationToken) => Task.CompletedTask;

    public async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Graceful shutdown initiated");

        // ✅ Esperar requests en vuelo (máx 30s)
        await Task.Delay(TimeSpan.FromSeconds(30), cancellationToken);

        _logger.LogInformation("Graceful shutdown completed");
        return Task.CompletedTask;
    }
}

// ✅ ECS deregistration delay (ALB espera 30s antes de terminar)
resource "aws_lb_target_group" "orders_api" {
  deregistration_delay = 30
}
```

### X. Dev/Prod Parity

**Principio:** Mantener desarrollo, staging y producción lo más similares posible

```yaml
# ✅ Mismo stack en todos los ambientes

Development:
  - Docker Compose con PostgreSQL, Redis, Kafka
  - Código en contenedor
  - Variables de entorno

Staging:
  - AWS ECS Fargate (igual que prod)
  - RDS PostgreSQL (igual que prod)
  - ElastiCache Redis (igual que prod)
  - MSK Kafka (igual que prod)
  - Configuración vía Parameter Store

Production:
  - AWS ECS Fargate
  - RDS PostgreSQL
  - ElastiCache Redis
  - MSK Kafka
  - Configuración vía Parameter Store

# ✅ Minimizar gaps:
# - Time gap: Deploy varias veces al día
# - Personnel gap: Devs hacen deploy
# - Tools gap: Mismo Docker, mismo PostgreSQL version
```

```yaml
# docker-compose.yml para desarrollo
version: "3.8"
services:
  orders-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=Host=postgres;Database=orders;Username=dev;Password=dev
      - REDIS_URL=redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine # ✅ Misma version que RDS
    environment:
      POSTGRES_DB: orders
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev

  redis:
    image: redis:7.2-alpine # ✅ Misma version que ElastiCache
```

### XI. Logs

**Principio:** Tratar logs como event streams

```csharp
// ✅ Logs a stdout/stderr (no archivos)

// Program.cs
var builder = WebApplication.CreateBuilder(args);

// ✅ Logs a console (stdout)
builder.Logging.ClearProviders();
builder.Logging.AddConsole();

// ✅ Structured logging con Serilog
builder.Host.UseSerilog((context, configuration) =>
{
    configuration
        .ReadFrom.Configuration(context.Configuration)
        .WriteTo.Console(new JsonFormatter())  // ✅ JSON a stdout
        .Enrich.FromLogContext()
        .Enrich.WithProperty("Application", "OrdersApi")
        .Enrich.WithProperty("Environment", context.HostingEnvironment.EnvironmentName);
});

// ✅ NO escribir logs a archivos locales
// .WriteTo.File("/var/log/app.log")  // Anti-pattern

// ✅ Log aggregation externo (Grafana Loki)
// ECS captura stdout → CloudWatch Logs → Loki
```

```json
// ✅ Logs estructurados (JSON)
{
  "@timestamp": "2026-02-18T10:30:45.123Z",
  "level": "Information",
  "message": "Order created successfully",
  "properties": {
    "OrderId": "123e4567-e89b-12d3-a456-426614174000",
    "CustomerId": "cust_123",
    "Amount": 150.0,
    "Application": "OrdersApi",
    "Environment": "production",
    "TraceId": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
  }
}
```

### XII. Admin Processes

**Principio:** Ejecutar tasks administrativas como procesos one-off

```csharp
// ✅ Migration como job one-off separado

// MigrationJob/Program.cs
public class MigrationJob
{
    public static async Task Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);
        builder.Services.AddDbContext<OrdersDbContext>();

        var app = builder.Build();

        // ✅ Ejecutar migrations
        using var scope = app.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<OrdersDbContext>();

        Console.WriteLine("Applying database migrations...");
        await db.Database.MigrateAsync();
        Console.WriteLine("Migrations applied successfully");

        // ✅ Proceso termina (no server)
    }
}

// ✅ ECS Task one-off (no service)
aws ecs run-task \
  --cluster production \
  --task-definition orders-migration:5 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-abc],securityGroups=[sg-xyz]}"

// ✅ Otras tareas administrativas como one-off tasks:
// - Database seeding
// - Data migrations
// - Cache warming
// - Reports generation
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar los 12 factores en nuevas aplicaciones
- **MUST** usar control de versiones (Git)
- **MUST** declarar dependencias explícitamente
- **MUST** externalizar configuración en variables de entorno
- **MUST** diseñar servicios stateless (sin estado local)
- **MUST** escribir logs a stdout/stderr (no archivos)
- **MUST** implementar graceful shutdown
- **MUST** usar contenedores (Docker)

### SHOULD (Fuertemente recomendado)

- **SHOULD** minimizar tiempo de startup (< 30s)
- **SHOULD** usar mismos backing services en dev/staging/prod
- **SHOULD** escalar horizontalmente con más procesos
- **SHOULD** ejecutar admin tasks como one-off processes
- **SHOULD** mantener dev/prod parity
- **SHOULD** versionar releases con semantic versioning

### MAY (Opcional)

- **MAY** usar Docker Compose para desarrollo local
- **MAY** implementar health checks para orchestration
- **MAY** usar feature flags para deployment gradual

### MUST NOT (Prohibido)

- **MUST NOT** hardcodear configuración en código
- **MUST NOT** almacenar estado en filesystem local
- **MUST NOT** escribir logs a archivos locales
- **MUST NOT** ejecutar migrations en startup de la app
- **MUST NOT** usar diferentes tecnologías entre dev y prod
- **MUST NOT** compilar código en ambiente productivo

---

## Referencias

- [Lineamiento: Cloud Native](../../lineamientos/arquitectura/03-cloud-native.md)
- [ADR-003: AWS Secrets Manager](../../decisiones-de-arquitectura/adr-003-aws-secrets-manager.md)
- [ADR-005: AWS Parameter Store](../../decisiones-de-arquitectura/adr-005-aws-parameter-store-configs.md)
- [ADR-007: AWS ECS Fargate](../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- Estándares relacionados:
  - [Stateless Design](stateless-design.md)
  - [Graceful Shutdown](graceful-shutdown.md)
  - [Containerization](../../estandares/infraestructura/containerization.md)
- Especificaciones:
  - [The Twelve-Factor App](https://12factor.net/)
  - [Beyond the Twelve-Factor App](https://www.oreilly.com/library/view/beyond-the-twelve-factor/9781492042631/)
