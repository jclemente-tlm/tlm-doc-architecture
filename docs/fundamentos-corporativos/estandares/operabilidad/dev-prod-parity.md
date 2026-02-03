---
id: dev-prod-parity
sidebar_position: 6
title: Paridad Dev/Producción (12-Factor App)
description: Estándar para garantizar paridad entre entornos según 12-Factor App Factor X, minimizando diferencias en dependencias, datos y configuración.
---

# Estándar Técnico — Paridad Dev/Producción (12-Factor App)

---

## 1. Propósito

Garantizar **paridad máxima** entre entornos de desarrollo, staging y producción según **12-Factor App Factor X**, reduciendo bugs causados por diferencias de versiones, configuración o infraestructura.

---

## 2. Alcance

**Aplica a:**

- Versiones de frameworks (.NET)
- Bases de datos (PostgreSQL, Oracle, SQL Server, Redis)
- Servicios de mensajería (Apache Kafka)
- Configuración de infraestructura (networking, security groups)
- Imágenes Docker y dependencias de contenedores

**No aplica a:**

- Volumen de datos (dev puede tener dataset reducido)
- Recursos de infraestructura (dev: 1 instancia, prod: 3+)
- Monitoreo/alerting (dev: relajado, prod: crítico)

---

## 3. Requisitos Obligatorios 🔴

### 3.1 Versiones de Dependencias

- [ ] **Misma versión** de runtime en todos los entornos:
  - .NET SDK: `8.0.x` (mismo minor version)
- [ ] **Misma versión** de BD:
  - PostgreSQL: `15.x` en dev/staging/prod
  - Oracle: `19c` en dev/staging/prod
  - SQL Server: `2022` en dev/staging/prod
  - Redis: `7.2.x` en dev/staging/prod
- [ ] **Misma versión** de librerías críticas (Entity Framework Core, Serilog, OpenTelemetry)
- [ ] Uso de **lock files** para dependencias:
  - .NET: `packages.lock.json`

### 3.2 Contenedorización

- [ ] **Dockerfile identical** para todos los entornos (NO `Dockerfile.dev` vs `Dockerfile.prod`)
- [ ] **Multi-stage builds** con stage `development` y `production` (misma base image)
- [ ] **Imágenes base versionadas explícitamente**:
  - ✅ `mcr.microsoft.com/dotnet/aspnet:8.0.1-alpine3.19`
  - ❌ `mcr.microsoft.com/dotnet/aspnet:latest`
- [ ] **Docker Compose** para desarrollo local (simula arquitectura de producción)
- [ ] **Mismas env vars** (nombres, formato) en dev/staging/prod (valores diferentes OK)

### 3.3 Base de Datos

- [ ] **Mismo motor** en todos los entornos (NO SQLite dev, PostgreSQL prod)
- [ ] **Mismas extensiones** de BD (PostGIS, pg_trgm, etc.)
- [ ] **Migrations** ejecutadas en orden idéntico dev → staging → prod
- [ ] **Seeders** para datos de prueba en dev/staging (NO en prod)

### 3.4 Configuración Externa

- [ ] **Variables de entorno** como mecanismo único de config
- [ ] **Mismos nombres** de env vars (valores difieren por entorno):

  ```bash
  # dev
  DATABASE__CONNECTIONSTRING=Host=localhost;Database=orders_dev

  # prod
  DATABASE__CONNECTIONSTRING=Host=rds.prod.amazonaws.com;Database=orders
  ```

- [ ] **NO lógica condicional por entorno** en código:

  ```csharp
  // ❌ MAL
  if (Environment.IsProduction())
      UsePostgreSQL();
  else
      UseSQLite();

  // ✅ BIEN
  var connectionString = Configuration["Database__ConnectionString"];
  UseDatabase(connectionString); // Mismo código, diferente config
  ```

---

## 4. Configuración Mínima

### 4.1 Dockerfile Multi-Stage

```dockerfile
# Base común
FROM mcr.microsoft.com/dotnet/aspnet:8.0.1-alpine3.19 AS base
WORKDIR /app
EXPOSE 80

# Build (igual para dev y prod)
FROM mcr.microsoft.com/dotnet/sdk:8.0.1-alpine3.19 AS build
WORKDIR /src
COPY ["Orders.API/Orders.API.csproj", "Orders.API/"]
RUN dotnet restore
COPY . .
RUN dotnet build -c Release -o /app/build

# Publish
FROM build AS publish
RUN dotnet publish -c Release -o /app/publish

# Runtime (production)
FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Orders.API.dll"]
```

### 4.2 Docker Compose para Dev Local

```yaml
# docker-compose.yml (simula arquitectura de producción)
version: "3.8"

services:
  api:
    build: .
    ports:
      - "5000:80"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - Database__ConnectionString=Host=postgres;Database=orders_dev;Username=postgres;Password=dev123
      - Redis__Endpoint=redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15.5-alpine # Misma versión que RDS en prod
    environment:
      POSTGRES_DB: orders_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"

  redis:
    image: redis:7.2.3-alpine # Misma versión que ElastiCache en prod
    ports:
      - "6379:6379"
```

### 4.3 Lock Files

```bash
# .NET: packages.lock.json
dotnet restore --locked-mode # Falla si lock file desactualizado
```

### 4.4 CI/CD Validation

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15.5-alpine # Misma versión que producción
        env:
          POSTGRES_DB: orders_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: test123
        ports:
          - 5432:5432

      redis:
        image: redis:7.2.3-alpine # Misma versión que producción
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x" # Misma versión que producción

      - run: dotnet restore --locked-mode # Valida lock file
      - run: dotnet build
      - run: dotnet test
```

---

## 5. Prohibiciones

- ❌ SQLite (o in-memory DB) en dev, PostgreSQL en prod
- ❌ Versiones diferentes de runtime (.NET 7 dev, .NET 8 prod)
- ❌ Lógica condicional por entorno en código de aplicación
- ❌ Imágenes Docker con tag `latest` (NO reproducible)
- ❌ `Dockerfile.dev` separado de `Dockerfile` (debe ser mismo build)
- ❌ Configuración hardcodeada en código (NO `if (env == "prod") ...`)

---

## 6. Gaps Permitidos

| Aspecto              | Dev                             | Producción              | Justificación   |
| -------------------- | ------------------------------- | ----------------------- | --------------- |
| **Volumen de datos** | Dataset reducido (1K registros) | Millones de registros   | Performance dev |
| **Recursos**         | 1 instancia, 1 vCPU             | 3+ instancias, 4 vCPU   | Costos          |
| **Monitoreo**        | Logs en consola                 | CloudWatch + alertas    | Complejidad     |
| **Backups**          | Sin backups automatizados       | Diarios + point-in-time | Costos          |
| **Networking**       | Localhost                       | Multi-AZ VPC            | Simplicidad     |

**Crítico:** Lo que SÍ debe ser idéntico es **código, versiones, configuración (nombres)**.

---

## 7. Validación

**Checklist de cumplimiento:**

- [ ] `docker inspect <image>` muestra misma base image version en dev/staging/prod
- [ ] `SELECT version()` en PostgreSQL dev/staging/prod → mismo minor version
- [ ] `dotnet --version` en dev/CI/prod → mismo SDK version
- [ ] Lock file `packages.lock.json` committed en git
- [ ] Docker Compose en dev simula servicios de producción (PostgreSQL, Redis)
- [ ] CI ejecuta tests contra mismas versiones de servicios que producción
- [ ] NO condicionales `if (Environment == "Production")` en código de aplicación

**Métricas de cumplimiento:**

| Métrica                             | Target | Verificación              |
| ----------------------------------- | ------ | ------------------------- |
| Versiones idénticas (runtime, BD)   | 100%   | Infrastructure audit      |
| Lock files actualizados             | 100%   | CI checks (--locked-mode) |
| Docker base images versionadas      | 100%   | Dockerfile review         |
| Código sin condicionales de entorno | 100%   | SonarQube custom rule     |

Incumplimientos generan bugs en prod causados por diferencias de entorno.

---

## 8. Referencias

- [12-Factor App — Dev/Prod Parity (Factor X)](https://12factor.net/dev-prod-parity)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Estándar: Externalizar Configuración](externalizar-configuracion-12factor.md)
- [ADR-007: Contenedores en AWS ECS](../../../decisiones-de-arquitectura/adr-007-contenedores-aws.md)
