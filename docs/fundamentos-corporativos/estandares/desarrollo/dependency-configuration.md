---
id: dependency-configuration
sidebar_position: 3
title: Gestión de Dependencias y Configuración
description: Estándares para gestión de paquetes, versionamiento semántico, configuración externalizada, despliegue independiente y estándares de código de base de datos.
---

# Gestión de Dependencias y Configuración

## Contexto

Este estándar define las prácticas para gestión de dependencias, configuración y despliegue de servicios, asegurando independencia, trazabilidad y operación segura. Complementa los lineamientos [Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md) y [Configuración de Entornos](../../lineamientos/operabilidad/03-configuracion-entornos.md).

**Conceptos incluidos:**

- **Package Management** → Gestión de paquetes NuGet
- **Semantic Versioning** → Versionamiento semántico
- **No Hardcoded Config** → Configuración externalizada
- **Independent Deployment** → Despliegue independiente
- **Database Code Standards** → Estándares de código de BD

---

## Stack Tecnológico

| Componente           | Tecnología            | Versión | Uso                          |
| -------------------- | --------------------- | ------- | ---------------------------- |
| **Package Manager**  | NuGet                 | 6.8+    | Gestión de dependencias .NET |
| **Registry**         | GitHub Packages       | -       | Registro privado de paquetes |
| **Configuration**    | ASP.NET Configuration | 8.0+    | Sistema de configuración     |
| **Secrets**          | AWS Secrets Manager   | -       | Gestión de secretos          |
| **Parameters**       | AWS Parameter Store   | -       | Parámetros de configuración  |
| **Environment Vars** | Docker Compose / ECS  | -       | Variables de entorno         |

---

## Conceptos Fundamentales

Este estándar cubre 5 aspectos de dependencias y configuración:

### Índice de Conceptos

1. **Package Management**: Gestión centralizada de paquetes
2. **Semantic Versioning**: Versionamiento predecible
3. **No Hardcoded Config**: Externalización de configuración
4. **Independent Deployment**: Autonomía de despliegue
5. **Database Code Standards**: Calidad en código de BD

### Relación entre Conceptos

```mermaid
graph TB
    A[Package Management] --> B[Semantic Versioning]
    B --> C[Independent Deployment]
    D[No Hardcoded Config] --> C
    E[Database Code Standards] --> F[Quality]
    C --> G[Autonomous Services]
    F --> G

    style A fill:#e1f5ff
    style D fill:#ffe1e1
    style C fill:#e8f5e9
```

---

## 1. Package Management

### ¿Qué es Package Management?

Gestión centralizada de dependencias externas (NuGet packages) asegurando versiones consistentes, seguridad y actualización controlada.

**Aspectos clave:**

- **Central Package Management**: Versiones en un solo lugar
- **Lock files**: Reproducibilidad de builds
- **Private registry**: Paquetes internos seguros
- **Vulnerability scanning**: Detección de CVEs
- **Dependency updates**: Actualización controlada

**Propósito:** Dependencias consistentes, seguras y actualizadas.

**Beneficios:**
✅ Versiones consistentes entre servicios
✅ Detección temprana de vulnerabilidades
✅ Builds reproducibles
✅ Gestión centralizada

### Central Package Management (CPM)

```xml
<!-- Directory.Packages.props - Raíz del repositorio -->
<!-- Habilitar Central Package Management en .NET 7+ -->

<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
    <CentralPackageTransitivePinningEnabled>true</CentralPackageTransitivePinningEnabled>
  </PropertyGroup>

  <ItemGroup Label="Microsoft Packages">
    <PackageVersion Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.2" />
    <PackageVersion Include="Microsoft.EntityFrameworkCore" Version="8.0.2" />
    <PackageVersion Include="Microsoft.EntityFrameworkCore.Design" Version="8.0.2" />
    <PackageVersion Include="Microsoft.Extensions.Configuration.EnvironmentVariables" Version="8.0.0" />
    <PackageVersion Include="Microsoft.Extensions.Diagnostics.HealthChecks" Version="8.0.2" />
    <PackageVersion Include="Microsoft.Extensions.Logging.Console" Version="8.0.0" />
  </ItemGroup>

  <ItemGroup Label="Database Drivers">
    <PackageVersion Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="8.0.2" />
    <PackageVersion Include="Oracle.EntityFrameworkCore" Version="8.23.4" />
    <PackageVersion Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.2" />
  </ItemGroup>

  <ItemGroup Label="Observability">
    <PackageVersion Include="Serilog.AspNetCore" Version="8.0.1" />
    <PackageVersion Include="Serilog.Sinks.Console" Version="5.0.1" />
    <PackageVersion Include="OpenTelemetry" Version="1.7.0" />
    <PackageVersion Include="OpenTelemetry.Exporter.OpenTelemetryProtocol" Version="1.7.0" />
    <PackageVersion Include="OpenTelemetry.Instrumentation.AspNetCore" Version="1.7.1" />
  </ItemGroup>

  <ItemGroup Label="Resilience">
    <PackageVersion Include="Polly" Version="8.2.1" />
    <PackageVersion Include="Polly.Extensions.Http" Version="3.0.0" />
  </ItemGroup>

  <ItemGroup Label="Validation">
    <PackageVersion Include="FluentValidation" Version="11.9.0" />
    <PackageVersion Include="FluentValidation.AspNetCore" Version="11.3.0" />
  </ItemGroup>

  <ItemGroup Label="Messaging">
    <PackageVersion Include="Confluent.Kafka" Version="2.3.0" />
  </ItemGroup>

  <ItemGroup Label="Cache">
    <PackageVersion Include="StackExchange.Redis" Version="2.7.17" />
  </ItemGroup>

  <ItemGroup Label="AWS">
    <PackageVersion Include="AWSSDK.Core" Version="3.7.304.14" />
    <PackageVersion Include="AWSSDK.SecretsManager" Version="3.7.303" />
    <PackageVersion Include="AWSSDK.SimpleSystemsManagement" Version="3.7.305.1" />
    <PackageVersion Include="AWSSDK.S3" Version="3.7.307.17" />
  </ItemGroup>

  <ItemGroup Label="Testing">
    <PackageVersion Include="xunit" Version="2.6.6" />
    <PackageVersion Include="xunit.runner.visualstudio" Version="2.5.6" />
    <PackageVersion Include="Moq" Version="4.20.70" />
    <PackageVersion Include="FluentAssertions" Version="6.12.0" />
    <PackageVersion Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
    <PackageVersion Include="Testcontainers" Version="3.7.0" />
    <PackageVersion Include="Testcontainers.PostgreSql" Version="3.7.0" />
  </ItemGroup>

  <ItemGroup Label="Code Analysis">
    <PackageVersion Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="8.0.0" />
    <PackageVersion Include="StyleCop.Analyzers" Version="1.2.0-beta.507" />
    <PackageVersion Include="SonarAnalyzer.CSharp" Version="9.16.0.82469" />
  </ItemGroup>
</Project>
```

```xml
<!-- CustomerService.Api.csproj - Proyecto individual -->
<!-- Solo referencias SIN versiones (versión viene de Directory.Packages.props) -->

<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" />
    <PackageReference Include="Microsoft.EntityFrameworkCore" />
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" />
    <PackageReference Include="Serilog.AspNetCore" />
    <PackageReference Include="OpenTelemetry.Instrumentation.AspNetCore" />
    <PackageReference Include="Polly" />
    <PackageReference Include="FluentValidation.AspNetCore" />
    <PackageReference Include="AWSSDK.SecretsManager" />
    <PackageReference Include="StackExchange.Redis" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\CustomerService.Application\CustomerService.Application.csproj" />
    <ProjectReference Include="..\CustomerService.Infrastructure\CustomerService.Infrastructure.csproj" />
  </ItemGroup>
</Project>
```

### Package Lock Files

```xml
<!-- packages.lock.json - Generado automáticamente -->
<!-- Asegura builds reproducibles con versiones exactas -->

<!-- Habilitar lock files en Directory.Build.props -->
<Project>
  <PropertyGroup>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode Condition="'$(CI)' == 'true'">true</RestoreLockedMode>
  </PropertyGroup>
</Project>
```

```bash
# Generar/actualizar lock file
dotnet restore

# Restaurar en modo locked (CI/CD)
dotnet restore --locked-mode

# Si lock file está desactualizado, el build fallará
# Forzar actualización:
dotnet restore --force-evaluate
```

### Private NuGet Registry

```xml
<!-- nuget.config - Configuración de fuentes de paquetes -->

<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <!-- NuGet oficial -->
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" protocolVersion="3" />

    <!-- GitHub Packages (paquetes privados Talma) -->
    <add key="talma-github" value="https://nuget.pkg.github.com/talma/index.json" />
  </packageSources>

  <packageSourceCredentials>
    <talma-github>
      <add key="Username" value="%GITHUB_USERNAME%" />
      <add key="ClearTextPassword" value="%GITHUB_TOKEN%" />
    </talma-github>
  </packageSourceCredentials>

  <disabledPackageSources>
    <!-- Deshabilitar fuentes no confiables -->
  </disabledPackageSources>
</configuration>
```

```yaml
# .github/workflows/publish-package.yml
# Publicar paquete NuGet interno

name: Publish NuGet Package

on:
  push:
    tags:
      - "v*"

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      packages: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"
          source-url: https://nuget.pkg.github.com/talma/index.json
        env:
          NUGET_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Pack
        run: dotnet pack --configuration Release -p:Version=${GITHUB_REF#refs/tags/v}

      - name: Publish to GitHub Packages
        run: dotnet nuget push "**/*.nupkg" --source "https://nuget.pkg.github.com/talma/index.json" --api-key ${{ secrets.GITHUB_TOKEN }}
```

### Vulnerability Scanning

```yaml
# .github/workflows/dependency-audit.yml
# Escaneo de vulnerabilidades en dependencias

name: Dependency Audit

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 2 * * 1" # Semanal

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Restore dependencies
        run: dotnet restore

      - name: List vulnerable packages
        run: |
          dotnet list package --vulnerable --include-transitive 2>&1 | tee vulnerable.txt

          if grep -q "Critical\|High" vulnerable.txt; then
            echo "❌ Critical or High vulnerabilities found:"
            grep "Critical\|High" vulnerable.txt
            exit 1
          else
            echo "✅ No critical vulnerabilities found"
          fi

      - name: Check for deprecated packages
        run: |
          dotnet list package --deprecated 2>&1 | tee deprecated.txt

          if grep -q "deprecated" deprecated.txt; then
            echo "⚠️ Deprecated packages found:"
            grep "deprecated" deprecated.txt
          fi
```

---

## 2. Semantic Versioning

### ¿Qué es Semantic Versioning?

Sistema de versionamiento usando formato **MAJOR.MINOR.PATCH** para comunicar tipo de cambios.

**Formato: X.Y.Z**

- **MAJOR (X)**: Cambios incompatibles (breaking changes)
- **MINOR (Y)**: Nueva funcionalidad compatible
- **PATCH (Z)**: Bug fixes compatibles

**Ejemplos:**

- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: Nueva feature
- `1.1.0` → `2.0.0`: Breaking change

**Propósito:** Comunicar impacto de cambios, gestión segura de actualizaciones.

**Beneficios:**
✅ Expectativas claras de compatibilidad
✅ Actualizaciones seguras
✅ Mejor comunicación entre equipos
✅ Automatización de releases

### Versionamiento de Servicios

```xml
<!-- Directory.Build.props - Versionamiento centralizado -->

<Project>
  <PropertyGroup>
    <!-- Version para todos los proyectos -->
    <Version>1.2.3</Version>

    <!-- Metadata adicional -->
    <AssemblyVersion>1.2.3.0</AssemblyVersion>
    <FileVersion>1.2.3.0</FileVersion>
    <InformationalVersion>1.2.3+$(GitCommitHash)</InformationalVersion>

    <!-- Copyright -->
    <Copyright>Copyright © Talma 2026</Copyright>
    <Company>Talma</Company>
  </PropertyGroup>
</Project>
```

```yaml
# .github/workflows/versioning.yml
# Automatizar versionamiento con tags

name: Release

on:
  push:
    tags:
      - "v*.*.*"

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Extract version
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT

          IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"
          echo "major=$MAJOR" >> $GITHUB_OUTPUT
          echo "minor=$MINOR" >> $GITHUB_OUTPUT
          echo "patch=$PATCH" >> $GITHUB_OUTPUT

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Build with version
        run: |
          dotnet build --configuration Release \
            -p:Version=${{ steps.version.outputs.version }} \
            -p:AssemblyVersion=${{ steps.version.outputs.version }}.0

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          name: Release v${{ steps.version.outputs.version }}
          generate_release_notes: true
          draft: false
          prerelease: false
```

### API Versioning

```csharp
// Program.cs - API Versioning con Semantic Versioning

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;
    options.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),
        new HeaderApiVersionReader("X-Api-Version"));
}).AddApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV";
    options.SubstituteApiVersionInUrl = true;
});

var app = builder.Build();

// Endpoints versionados
app.MapGet("/api/v1/customers", () => "Version 1.0")
    .WithApiVersionSet()
    .HasApiVersion(new ApiVersion(1, 0));

app.MapGet("/api/v2/customers", () => "Version 2.0")
    .WithApiVersionSet()
    .HasApiVersion(new ApiVersion(2, 0));

app.Run();
```

---

## 3. No Hardcoded Config

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

## 4. Independent Deployment

### ¿Qué es Despliegue Independiente?

Capacidad de desplegar un servicio sin coordinación con otros servicios, habilitando autonomía y velocidad.

**Requisitos:**

- **Versioned APIs**: Contratos versionados
- **Backward compatibility**: Sin breaking changes
- **Database per service**: Sin shared database
- **Async communication**: Eventos para sincronización
- **Feature flags**: Habilitar features gradualmente

**Propósito:** Autonomía de equipos, despliegues frecuentes, menor riesgo.

**Beneficios:**
✅ Deploy cuando equipo decide
✅ Rollback independiente
✅ Testing aislado
✅ Menor coordinación

### Deployment Pipeline Independiente

```yaml
# .github/workflows/deploy.yml
# Pipeline de deployment independiente

name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: "Environment to deploy"
        required: true
        type: choice
        options:
          - dev
          - staging
          - production

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Restore
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore

      - name: Test
        run: dotnet test --no-build --verbosity normal

  build-image:
    name: Build Docker Image
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy-dev:
    name: Deploy to Dev
    needs: build-image
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: dev
      url: https://customer-api.dev.talma.internal
    steps:
      - name: Deploy to ECS
        run: |
          # Actualizar task definition en ECS
          aws ecs update-service \
            --cluster customer-service-dev \
            --service customer-api \
            --force-new-deployment \
            --region us-east-1

  deploy-staging:
    name: Deploy to Staging
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://customer-api.staging.talma.internal
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster customer-service-staging \
            --service customer-api \
            --force-new-deployment \
            --region us-east-1

  deploy-production:
    name: Deploy to Production
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://customer-api.talma.com
    steps:
      - name: Deploy to ECS
        run: |
          # Blue-Green deployment
          aws ecs update-service \
            --cluster customer-service-prod \
            --service customer-api \
            --force-new-deployment \
            --region us-east-1

      - name: Monitor deployment
        run: |
          # Esperar deployment completo
          aws ecs wait services-stable \
            --cluster customer-service-prod \
            --services customer-api \
            --region us-east-1
```

### Contract Testing

```csharp
// Tests/ContractTests/CustomerApiContractTests.cs
// Verificar que cambios no rompen contratos

public class CustomerApiContractTests
{
    [Fact]
    public async Task GetCustomer_Response_MaintainsBackwardCompatibility()
    {
        // Arrange
        var client = new HttpClient { BaseAddress = new Uri("http://localhost:8080") };

        // Act
        var response = await client.GetAsync("/api/v1/customers/550e8400-e29b-41d4-a716-446655440000");
        var json = await response.Content.ReadAsStringAsync();
        var customer = JsonSerializer.Deserialize<CustomerDto>(json);

        // Assert - Verificar campos requeridos existen
        customer.Should().NotBeNull();
        customer!.Id.Should().NotBeEmpty();
        customer.Name.Should().NotBeNullOrEmpty();
        customer.Email.Should().NotBeNullOrEmpty();

        // ✅ Nuevos campos opcionales OK
        // ❌ Remover campos existentes = BREAKING CHANGE
        // ❌ Cambiar tipo de campo = BREAKING CHANGE
        // ❌ Hacer campo opcional requerido = BREAKING CHANGE
    }

    [Fact]
    public async Task CreateCustomer_AcceptsLegacyFormat()
    {
        // Arrange - Request antiguo (v1.0)
        var legacyRequest = new
        {
            name = "John Doe",
            email = "john@example.com"
            // phone era opcional, ahora requerido pero debe funcionar sin él
        };

        var client = new HttpClient { BaseAddress = new Uri("http://localhost:8080") };
        var content = new StringContent(
            JsonSerializer.Serialize(legacyRequest),
            Encoding.UTF8,
            "application/json");

        // Act
        var response = await client.PostAsync("/api/v1/customers", content);

        // Assert - Debe seguir funcionando
        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }
}
```

---

## 5. Database Code Standards

### ¿Qué son Database Code Standards?

Conjunto de prácticas para escribir código de base de datos (stored procedures, functions, triggers) con calidad y mantenibilidad.

**Aspectos:**

- **Naming conventions**: Consistencia en nombres
- **Code structure**: Organización legible
- **Error handling**: Manejo apropiado de errores
- **Performance**: Queries optimizados
- **Version control**: Scripts en Git
- **Testing**: Tests para lógica de BD

**Propósito:** Código de BD mantenible, performante y versionado.

**Beneficios:**
✅ Código legible y consistente
✅ Mejor performance
✅ Trazabilidad de cambios
✅ Testing automatizado

### SQL Naming Conventions

```sql
-- ✅ BUENO: Naming conventions consistentes

-- Schemas: lowercase, singular
CREATE SCHEMA customer;
CREATE SCHEMA order;

-- Tables: lowercase, plural, snake_case
CREATE TABLE customer.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes: ix_{table}_{columns}
CREATE INDEX ix_customers_email ON customer.customers (email);
CREATE INDEX ix_customers_created_at ON customer.customers (created_at);

-- Unique constraints: uq_{table}_{columns}
ALTER TABLE customer.customers
ADD CONSTRAINT uq_customers_email UNIQUE (email);

-- Foreign keys: fk_{table}_{referenced_table}
ALTER TABLE customer.addresses
ADD CONSTRAINT fk_addresses_customers
FOREIGN KEY (customer_id) REFERENCES customer.customers(id);

-- Check constraints: ck_{table}_{condition}
ALTER TABLE customer.customers
ADD CONSTRAINT ck_customers_email_format
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Views: v_{name}
CREATE VIEW customer.v_active_customers AS
SELECT * FROM customer.customers WHERE deleted_at IS NULL;

-- Functions: fn_{name} o {action}_{entity}
CREATE FUNCTION customer.fn_get_customer_by_email(p_email VARCHAR)
RETURNS TABLE (id UUID, name VARCHAR, email VARCHAR)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.email
    FROM customer.customers c
    WHERE c.email = p_email;
END;
$$ LANGUAGE plpgsql;

-- Stored procedures: sp_{action}_{entity}
CREATE PROCEDURE customer.sp_archive_customer(p_customer_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE customer.customers
    SET deleted_at = CURRENT_TIMESTAMP
    WHERE id = p_customer_id;
END;
$$;
```

### Stored Procedures Best Practices

```sql
-- ✅ BUENO: Stored procedure con mejores prácticas

CREATE OR REPLACE PROCEDURE customer.sp_create_customer(
    p_name VARCHAR(100),
    p_email VARCHAR(254),
    p_phone VARCHAR(20),
    p_document_type VARCHAR(10),
    p_document_number VARCHAR(20),
    OUT p_customer_id UUID,
    OUT p_error_code VARCHAR(50),
    OUT p_error_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_existing_count INT;
BEGIN
    -- 1. Inicializar outputs
    p_customer_id := NULL;
    p_error_code := NULL;
    p_error_message := NULL;

    -- 2. Validaciones
    IF p_name IS NULL OR LENGTH(TRIM(p_name)) < 2 THEN
        p_error_code := 'INVALID_NAME';
        p_error_message := 'Name must be at least 2 characters';
        RETURN;
    END IF;

    IF p_email IS NULL OR p_email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        p_error_code := 'INVALID_EMAIL';
        p_error_message := 'Invalid email format';
        RETURN;
    END IF;

    -- 3. Verificar duplicados
    SELECT COUNT(*) INTO v_existing_count
    FROM customer.customers
    WHERE email = p_email;

    IF v_existing_count > 0 THEN
        p_error_code := 'DUPLICATE_EMAIL';
        p_error_message := 'Email already exists';
        RETURN;
    END IF;

    -- 4. Insertar
    INSERT INTO customer.customers (
        name,
        email,
        phone,
        document_type,
        document_number,
        created_at
    )
    VALUES (
        TRIM(p_name),
        LOWER(p_email),
        p_phone,
        p_document_type,
        p_document_number,
        CURRENT_TIMESTAMP
    )
    RETURNING id INTO p_customer_id;

    -- 5. Success
    RAISE NOTICE 'Customer created successfully: %', p_customer_id;

EXCEPTION
    WHEN unique_violation THEN
        p_error_code := 'DUPLICATE_KEY';
        p_error_message := 'Duplicate key violation';
    WHEN OTHERS THEN
        p_error_code := 'INTERNAL_ERROR';
        p_error_message := SQLERRM;
        RAISE WARNING 'Error creating customer: %', SQLERRM;
END;
$$;

-- Uso desde C#
/*
var parameters = new[]
{
    new NpgsqlParameter("p_name", "John Doe"),
    new NpgsqlParameter("p_email", "john@example.com"),
    new NpgsqlParameter("p_phone", "+51987654321"),
    new NpgsqlParameter("p_document_type", "DNI"),
    new NpgsqlParameter("p_document_number", "12345678"),
    new NpgsqlParameter("p_customer_id", DbType.Guid) { Direction = ParameterDirection.Output },
    new NpgsqlParameter("p_error_code", DbType.String) { Direction = ParameterDirection.Output, Size = 50 },
    new NpgsqlParameter("p_error_message", DbType.String) { Direction = ParameterDirection.Output, Size = -1 }
};

await context.Database.ExecuteSqlRawAsync(
    "CALL customer.sp_create_customer($1, $2, $3, $4, $5, $6, $7, $8)",
    parameters);

var customerId = (Guid?)parameters[5].Value;
var errorCode = parameters[6].Value as string;
var errorMessage = parameters[7].Value as string;
*/
```

### Query Performance

```sql
-- ❌ MALO: Query sin optimizar

-- Problema 1: SELECT *
SELECT * FROM customer.customers;

-- Problema 2: Sin índice
SELECT * FROM customer.customers WHERE email = 'john@example.com';

-- Problema 3: Function en WHERE (no usa índice)
SELECT * FROM customer.customers WHERE LOWER(email) = 'john@example.com';

-- Problema 4: OR condition (dificulta índices)
SELECT * FROM customer.customers WHERE name = 'John' OR email = 'john@example.com';

-- ✅ BUENO: Query optimizado

-- Solución 1: Solo columnas necesarias
SELECT id, name, email FROM customer.customers;

-- Solución 2: Índice en columna de búsqueda
CREATE INDEX ix_customers_email ON customer.customers (email);
SELECT id, name, email FROM customer.customers WHERE email = 'john@example.com';

-- Solución 3: Almacenar lowercase en columna separada o usar índice funcional
CREATE INDEX ix_customers_email_lower ON customer.customers (LOWER(email));
SELECT id, name, email FROM customer.customers WHERE LOWER(email) = 'john@example.com';

-- Solución 4: Separar en queries o usar UNION
SELECT id, name, email FROM customer.customers WHERE name = 'John'
UNION
SELECT id, name, email FROM customer.customers WHERE email = 'john@example.com';

-- Análisis de performance
EXPLAIN ANALYZE
SELECT id, name, email
FROM customer.customers
WHERE email = 'john@example.com';

-- Resultado esperado:
-- Index Scan using ix_customers_email on customers (cost=0.28..8.29 rows=1 width=44)
```

---

## Implementación Integrada

### Setup Completo de Servicio

```bash
# 1. Crear estructura con CPM
mkdir customer-service
cd customer-service

# 2. Crear Directory.Packages.props (CPM)
# (contenido mostrado anteriormente)

# 3. Crear Directory.Build.props (configuración global)
cat > Directory.Build.props << 'EOF'
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <LangVersion>latest</LangVersion>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <Version>1.0.0</Version>
  </PropertyGroup>
</Project>
EOF

# 4. Crear nuget.config
cat > nuget.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="talma-github" value="https://nuget.pkg.github.com/talma/index.json" />
  </packageSources>
</configuration>
EOF

# 5. Crear proyectos
dotnet new sln -n CustomerService
dotnet new webapi -n CustomerService.Api
dotnet new classlib -n CustomerService.Domain
dotnet new classlib -n CustomerService.Application
dotnet new classlib -n CustomerService.Infrastructure
dotnet new xunit -n CustomerService.Tests

dotnet sln add **/*.csproj

# 6. Configurar appsettings
cat > CustomerService.Api/appsettings.json << 'EOF'
{
  "ConnectionStrings": {
    "CustomerDatabase": "Host=localhost;Port=5432;Database=customers;Username=dev;Password=dev"
  },
  "Kafka": {
    "BootstrapServers": "localhost:9092",
    "GroupId": "customer-service"
  }
}
EOF

# 7. Crear docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  customer-api:
    build: .
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - CUSTOMER_SERVICE_ConnectionStrings__CustomerDatabase=Host=postgres;Database=customers;Username=dev;Password=dev
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - kafka

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=customers
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=dev
    ports:
      - "5432:5432"

  kafka:
    image: apache/kafka:3.6.1
    environment:
      - KAFKA_NODE_ID=1
      - KAFKA_PROCESS_ROLES=broker,controller
    ports:
      - "9092:9092"
EOF

# 8. Crear .env.example (no .env real)
cat > .env.example << 'EOF'
DB_USER=customer_user
DB_PASSWORD=CHANGE_ME
AWS_ACCESS_KEY_ID=CHANGE_ME
AWS_SECRET_ACCESS_KEY=CHANGE_ME
EOF

# 9. Actualizar .gitignore
cat >> .gitignore << 'EOF'
.env
appsettings.*.json
!appsettings.Development.json
EOF
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

**Package Management:**

- **MUST** usar Central Package Management (Directory.Packages.props)
- **MUST** habilitar package lock files
- **MUST** escanear dependencias por vulnerabilidades en CI/CD
- **MUST** resolver vulnerabilidades Critical/High antes de deployment
- **MUST** mantener dependencias actualizadas

**Semantic Versioning:**

- **MUST** usar Semantic Versioning (MAJOR.MINOR.PATCH)
- **MUST** incrementar MAJOR en breaking changes
- **MUST** versionar APIs públicas
- **MUST** mantener changelog

**No Hardcoded Config:**

- **MUST** externalizar toda configuración
- **MUST** usar environment variables para secretos
- **MUST** NO commitear secretos en código
- **MUST** NO commitear appsettings con valores reales de producción
- **MUST** usar AWS Secrets Manager para secretos en producción

**Independent Deployment:**

- **MUST** desplegar sin coordinación con otros servicios
- **MUST** mantener backward compatibility en APIs
- **MUST** versionar contratos de API
- **MUST** incluir contract tests en pipeline

**Database Code:**

- **MUST** usar naming conventions consistentes (snake_case PostgreSQL)
- **MUST** versionar scripts SQL en Git
- **MUST** incluir error handling en stored procedures
- **MUST** optimizar queries (usar EXPLAIN ANALYZE)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar private NuGet registry para paquetes internos
- **SHOULD** automatizar actualizaciones de dependencias (Dependabot)
- **SHOULD** usar Options pattern para strongly-typed configuration
- **SHOULD** implementar health checks que verifiquen dependencias
- **SHOULD** usar feature flags para habilitar funcionalidad gradualmente
- **SHOULD** testear migraciones en ambientes inferiores primero
- **SHOULD** documentar stored procedures con comentarios

### MAY (Opcional)

- **MAY** usar configuration reloading en runtime
- **MAY** implementar circuit breakers para dependencias externas
- **MAY** usar canary deployments para reducir riesgo
- **MAY** implementar automated rollback en caso de fallos

### MUST NOT (Prohibido)

- **MUST NOT** commitear secretos en código o archivos de configuración
- **MUST NOT** usar shared database entre servicios
- **MUST NOT** hacer breaking changes sin incrementar MAJOR version
- **MUST NOT** desplegar sin pasar tests
- **MUST NOT** usar SELECT \* en queries de producción
- **MUST NOT** hardcodear connection strings en código

---

## Referencias

**Documentación oficial:**

- [NuGet Central Package Management](https://learn.microsoft.com/nuget/consume-packages/central-package-management)
- [Semantic Versioning](https://semver.org/)
- [ASP.NET Configuration](https://learn.microsoft.com/aspnet/core/fundamentals/configuration/)
- [12-Factor App](https://12factor.net/)

**AWS:**

- [Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)

**Relacionados:**

- [Git Workflow](./git-workflow.md)
- [Database Standards](../datos/database-standards.md)
- [CI/CD Deployment](../operabilidad/cicd-deployment.md)

---

**Última actualización**: 18 de febrero de 2026
**Responsable**: Equipo de Arquitectura
