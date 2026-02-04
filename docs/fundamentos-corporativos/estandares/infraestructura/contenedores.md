---
id: contenedores
sidebar_position: 1
title: Contenedores
description: Estándar técnico completo para construcción, optimización, orquestación y escaneo de contenedores con Docker, Docker Compose y Trivy
---

# Estándar Técnico — Contenedores

---

## 1. Propósito

Garantizar imágenes de contenedores ligeras, seguras y reproducibles mediante multi-stage builds, Alpine/Slim, usuario no-root y Docker Compose para desarrollo local.

---

## 2. Alcance

**Aplica a:**

- **Dockerfile**: Aplicaciones backend (.NET) desplegadas en AWS ECS Fargate
- **Docker Compose**: Desarrollo local multi-contenedor (API + DB + Cache + Broker)
- **Scanning**: Todas las imágenes antes de publicar a ghcr.io
- Entornos: Dev (Compose), Staging/Production (Dockerfile → ECS)

**No aplica a:**

- Scripts one-time locales sin despliegue
- Imágenes de terceros consumidas as-is sin modificar
- Docker Compose en producción (usar ECS/Fargate)

---

## 3. Tecnologías Aprobadas

| Componente         | Tecnología                          | Versión mínima | Observaciones                          |
| ------------------ | ----------------------------------- | -------------- | -------------------------------------- |
| **Docker Engine**  | Docker Engine                       | 24.0+          | BuildKit nativo, multi-platform builds |
| **BuildKit**       | Habilitado por defecto              | 0.12+          | Cache eficiente, builds paralelos      |
| **Imágenes Base**  | Alpine (preferida), Slim            | Latest LTS     | Tamaño reducido 70-80%                 |
| **Scanner**        | Trivy                               | Latest         | CVEs + secrets + misconfigurations     |
| **Registry**       | GitHub Container Registry (ghcr.io) | -              | Registry privado integrado con GitHub  |
| **.NET**           | `dotnet/aspnet:8.0-alpine`          | 8.0            | ~110MB                                 |
| **Docker Compose** | Docker Compose                      | 2.20+          | Formato v3.9                           |
| **Compose Format** | Compose file format                 | 3.9            | Compatible Docker Engine 19.03+        |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Dockerfile (Producción)

- [ ] Multi-stage build (mínimo 2 stages: build + runtime)
- [ ] Imagen base Alpine o Slim
- [ ] Usuario no-root creado (UID 1001)
- [ ] Health check configurado (interval 30s, timeout 5s)
- [ ] Tags semánticos `v<MAJOR>.<MINOR>.<PATCH>` (NO `latest` en prod)
- [ ] Secretos NO hardcodeados (usar AWS Secrets Manager)
- [ ] Escaneo vulnerabilidades ejecutado (Trivy)
- [ ] CVEs críticos resueltos antes de push
- [ ] .dockerignore configurado (.git, node_modules, bin, obj, .env)
- [ ] BuildKit habilitado para cache eficiente
- [ ] Logs a stdout/stderr (NO archivos)
- [ ] Labels OCI (version, maintainer, title)
- [ ] Tamaño de imagen ≤ 200MB

### Docker Compose (Desarrollo)

- [ ] Formato v3.9 (version: "3.9")
- [ ] Archivo base `docker-compose.yml` versionado
- [ ] Override file `docker-compose.override.yml` NO versionado
- [ ] Variables en `.env` (NO versionado), template en `.env.example` (versionado)
- [ ] Health checks configurados para servicios con dependencies
- [ ] Named volumes para persistencia de datos
- [ ] Networks aisladas por stack
- [ ] `depends_on` con `condition: service_healthy`
- [ ] Resource limits (memory, cpu) configurados
- [ ] Onboarding `<10` minutos

### Security Scanning

- [ ] Trivy scan en CI/CD antes de merge
- [ ] 0 CVEs críticos permitidos
- [ ] Scan de secrets habilitado
- [ ] Scan de misconfigurations habilitado

---

## 5. Prohibiciones

### Dockerfile

- ❌ Tags `latest` en producción
- ❌ Usuario root (USER root)
- ❌ Secretos hardcodeados en Dockerfile
- ❌ Imágenes > 200MB sin justificación
- ❌ Builds sin BuildKit habilitado
- ❌ Publicar imágenes con CVEs críticos

### Docker Compose

- ❌ Usar Docker Compose en producción (staging/prod)
- ❌ Versionar archivo `.env` con secretos
- ❌ Hardcodear secrets en docker-compose.yml
- ❌ `depends_on` sin health checks (unsafe)
- ❌ Bind mounts absolutos (usar paths relativos)
- ❌ Servicios sin resource limits

---

## 6. Dockerfile - Multi-Stage Build

### .NET Production Image

```dockerfile
# syntax=docker/dockerfile:1.4

# ============================================================
# STAGE 1: BUILD
# ============================================================
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build

WORKDIR /src

# Restaurar dependencias (cached layer)
COPY ["PaymentApi/PaymentApi.csproj", "PaymentApi/"]
COPY ["PaymentApi.Domain/PaymentApi.Domain.csproj", "PaymentApi.Domain/"]
RUN dotnet restore "PaymentApi/PaymentApi.csproj"

# Copiar código y compilar
COPY . .
WORKDIR "/src/PaymentApi"
RUN dotnet build "PaymentApi.csproj" -c Release -o /app/build

# Publicar (optimizado)
RUN dotnet publish "PaymentApi.csproj" \
    -c Release \
    -o /app/publish \
    --no-restore \
    /p:UseAppHost=false

# ============================================================
# STAGE 2: RUNTIME
# ============================================================
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final

# Metadata (OCI labels)
LABEL org.opencontainers.image.title="Payment API"
LABEL org.opencontainers.image.version="1.2.3"
LABEL org.opencontainers.image.vendor="Talma"
LABEL org.opencontainers.image.source="https://github.com/talma/payment-api"

# Crear usuario no-root
RUN addgroup -g 1001 appuser && \
    adduser -D -u 1001 -G appuser appuser

WORKDIR /app

# Copiar binarios compilados
COPY --from=build --chown=appuser:appuser /app/publish .

# Cambiar a usuario no-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Exponer puerto
EXPOSE 8080

# Entrypoint
ENTRYPOINT ["dotnet", "PaymentApi.dll"]
```

### .dockerignore

```gitignore
# Build artifacts
**/bin/
**/obj/
**/out/

# Git
.git/
.gitignore
.gitattributes

# IDE
.vs/
.vscode/
*.user
*.suo

# Environment
.env
.env.local
**/.DS_Store

# Tests
**/TestResults/

# Docs
README.md
docs/
```

---

## 7. Docker Compose - Desarrollo Local

### docker-compose.yml (Base - Versionado)

```yaml
version: "3.9"

services:
  # API Backend
  payment-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "${API_PORT:-5000}:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_URLS=http://+:8080
      - ConnectionStrings__DefaultConnection=Host=postgres;Port=5432;Database=payment_db;Username=postgres;Password=${POSTGRES_PASSWORD}
      - Redis__ConnectionString=redis:6379
      - Kafka__BootstrapServers=kafka:9092
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      kafka:
        condition: service_started
    networks:
      - app-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M

  # PostgreSQL Database
  postgres:
    image: postgres:${POSTGRES_VERSION:-16}-alpine
    environment:
      POSTGRES_DB: payment_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - app-network
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:${REDIS_VERSION:-7}-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    networks:
      - app-network
    restart: unless-stopped

  # Apache Kafka (KRaft mode)
  kafka:
    image: confluentinc/cp-kafka:${KAFKA_VERSION:-7.5.0}
    ports:
      - "${KAFKA_PORT:-9092}:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT"
      KAFKA_ADVERTISED_LISTENERS: "PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092"
      KAFKA_PROCESS_ROLES: "broker,controller"
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:29093"
      KAFKA_LISTENERS: "PLAINTEXT://kafka:29092,CONTROLLER://kafka:29093,PLAINTEXT_HOST://0.0.0.0:9092"
      KAFKA_INTER_BROKER_LISTENER_NAME: "PLAINTEXT"
      KAFKA_CONTROLLER_LISTENER_NAMES: "CONTROLLER"
      KAFKA_LOG_DIRS: "/tmp/kraft-combined-logs"
      CLUSTER_ID: "MkU3OEVBNTcwNTJENDM2Qk"
    volumes:
      - kafka-data:/var/lib/kafka/data
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  kafka-data:
    driver: local

networks:
  app-network:
    driver: bridge
```

### .env.example (Template - Versionado)

```bash
# Versions
POSTGRES_VERSION=16
REDIS_VERSION=7
KAFKA_VERSION=7.5.0

# Credentials (CHANGE IN LOCAL .env)
POSTGRES_PASSWORD=change_me_in_local_env

# Ports
API_PORT=5000
POSTGRES_PORT=5432
REDIS_PORT=6379
KAFKA_PORT=9092
```

### .env (Local - NO Versionado)

```bash
# Agregar a .gitignore
POSTGRES_PASSWORD=dev_secure_password_123
API_PORT=5000
```

### docker-compose.override.yml (Dev overrides - NO versionado)

```yaml
version: "3.9"

services:
  payment-api:
    build:
      target: build # Hot reload en development
    volumes:
      - ./PaymentApi:/src/PaymentApi:ro # Bind mount para hot reload
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_WATCH_RECOMPILE=true
```

---

## 8. Security Scanning con Trivy

### Scan Completo

```bash
# Scan de vulnerabilidades (CVEs)
trivy image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  --format table \
  ghcr.io/talma/payment-api:v1.2.3

# Scan de secrets expuestos
trivy image \
  --scanners secret \
  --exit-code 1 \
  ghcr.io/talma/payment-api:v1.2.3

# Scan de misconfigurations
trivy image \
  --scanners config \
  --exit-code 1 \
  ghcr.io/talma/payment-api:v1.2.3

# Scan completo (CVEs + secrets + config)
trivy image \
  --scanners vuln,secret,config \
  --severity HIGH,CRITICAL \
  --format json \
  --output trivy-report.json \
  ghcr.io/talma/payment-api:v1.2.3
```

### GitHub Actions - Automated Scanning

```yaml
# .github/workflows/docker-scan.yml
name: Docker Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  trivy-scan:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker Image
        run: |
          docker build -t payment-api:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: payment-api:${{ github.sha }}
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "HIGH,CRITICAL"
          exit-code: "1" # Fail if HIGH/CRITICAL found

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: "trivy-results.sarif"

      - name: Trivy Secret Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: payment-api:${{ github.sha }}
          scan-type: "image"
          scanners: "secret"
          exit-code: "1"
```

---

## 9. BuildKit - Cache Optimization

### Habilitar BuildKit

```bash
# Método 1: Variable de entorno
export DOCKER_BUILDKIT=1
docker build -t payment-api:v1.2.3 .

# Método 2: Docker Daemon config
# /etc/docker/daemon.json
{
  "features": {
    "buildkit": true
  }
}
```

### Cache Mount (Dependencias)

```dockerfile
# Optimización con cache mount para .NET
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build

WORKDIR /src

# Cache de NuGet packages
RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet restore "PaymentApi.csproj"

# Cache de build intermedios
RUN --mount=type=cache,target=/src/obj \
    --mount=type=cache,target=/src/bin \
    dotnet build "PaymentApi.csproj" -c Release
```

### Multi-Platform Builds

```bash
# Crear builder multi-platform
docker buildx create --name multiplatform --use

# Build para AMD64 y ARM64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/talma/payment-api:v1.2.3 \
  --push \
  .
```

---

## 10. Tagging Strategy

### Semántico Versionado

```bash
# Producción: Tags semánticos específicos
docker tag payment-api:local ghcr.io/talma/payment-api:v1.2.3
docker tag payment-api:local ghcr.io/talma/payment-api:v1.2
docker tag payment-api:local ghcr.io/talma/payment-api:v1

# Desarrollo: SHA corto del commit
docker tag payment-api:local ghcr.io/talma/payment-api:sha-a1b2c3d

# Staging: Branch + SHA
docker tag payment-api:local ghcr.io/talma/payment-api:develop-a1b2c3d
```

### NO usar en Producción

```bash
# ❌ MAL: latest es ambiguo
docker tag payment-api:local ghcr.io/talma/payment-api:latest

# ❌ MAL: fecha no es reproducible
docker tag payment-api:local ghcr.io/talma/payment-api:2026-02-04
```

---

## 11. Validación de Cumplimiento

```bash
#!/bin/bash
# scripts/validate-docker.sh

echo "🔍 Validando estándares Docker..."

IMAGE="ghcr.io/talma/payment-api:v1.2.3"

# 1. Verificar tamaño de imagen
echo "1. Tamaño de imagen..."
SIZE=$(docker images $IMAGE --format "{{.Size}}")
echo "   Tamaño: $SIZE (target: <200MB)"

# 2. Verificar usuario no-root
echo "2. Usuario no-root..."
USER=$(docker inspect $IMAGE | jq -r '.[0].Config.User')
if [ "$USER" != "1001" ] && [ "$USER" != "appuser" ]; then
  echo "   ❌ FAIL: Usuario es root"
  exit 1
fi
echo "   ✅ PASS: Usuario $USER"

# 3. Verificar health check
echo "3. Health check..."
HEALTHCHECK=$(docker inspect $IMAGE | jq '.[0].Config.Healthcheck')
if [ "$HEALTHCHECK" == "null" ]; then
  echo "   ❌ FAIL: Sin health check"
  exit 1
fi
echo "   ✅ PASS: Health check configurado"

# 4. Escanear vulnerabilidades
echo "4. Trivy scan (CVEs críticos)..."
trivy image --severity CRITICAL --exit-code 1 $IMAGE
if [ $? -ne 0 ]; then
  echo "   ❌ FAIL: CVEs críticos encontrados"
  exit 1
fi
echo "   ✅ PASS: 0 CVEs críticos"

# 5. Verificar secrets expuestos
echo "5. Trivy secret scan..."
trivy image --scanners secret --exit-code 1 $IMAGE
if [ $? -ne 0 ]; then
  echo "   ❌ FAIL: Secrets encontrados"
  exit 1
fi
echo "   ✅ PASS: No secrets expuestos"

# 6. Verificar labels OCI
echo "6. OCI labels..."
LABELS=$(docker inspect $IMAGE | jq '.[0].Config.Labels')
if [ "$LABELS" == "{}" ] || [ "$LABELS" == "null" ]; then
  echo "   ⚠️  WARN: Sin labels OCI"
fi

# 7. Verificar .dockerignore
echo "7. .dockerignore..."
if [ ! -f .dockerignore ]; then
  echo "   ❌ FAIL: .dockerignore no existe"
  exit 1
fi
echo "   ✅ PASS: .dockerignore configurado"

# 8. Docker Compose (si existe)
if [ -f docker-compose.yml ]; then
  echo "8. Docker Compose validation..."
  docker-compose config > /dev/null
  if [ $? -ne 0 ]; then
    echo "   ❌ FAIL: docker-compose.yml inválido"
    exit 1
  fi
  echo "   ✅ PASS: docker-compose.yml válido"

  # Verificar .env.example
  if [ ! -f .env.example ]; then
    echo "   ⚠️  WARN: .env.example no existe"
  fi

  # Verificar que .env NO está versionado
  if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "   ❌ FAIL: .env está versionado (git tracked)"
    exit 1
  fi
fi

echo "✅ Validación Docker completada exitosamente"
```

### Métricas de Cumplimiento

| Métrica                      | Target  | Verificación                              |
| ---------------------------- | ------- | ----------------------------------------- |
| Tamaño imagen                | ≤ 200MB | `docker images --format "{{.Size}}"`      |
| CVEs críticos                | 0       | `trivy --severity CRITICAL`               |
| Usuario no-root              | 100%    | `docker inspect \| jq .Config.User`       |
| Tags `latest` en prod        | 0%      | ghcr.io registry inspection               |
| Health checks configurados   | 100%    | `docker inspect \| jq .Config.Healthcheck |
| Secrets en imagen            | 0       | `trivy --scanners secret`                 |
| BuildKit habilitado          | 100%    | Check DOCKER_BUILDKIT env var             |
| Docker Compose onboarding    | <10 min | `time docker-compose up -d`               |
| .env versionado              | 0%      | `git ls-files .env`                       |
| Services con resource limits | 100%    | `docker-compose config \| grep limits`    |

---

## 12. Referencias

**Docker:**

- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [BuildKit Documentation](https://github.com/moby/buildkit)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

**Docker Compose:**

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose file version 3 reference](https://docs.docker.com/compose/compose-file/compose-file-v3/)

**Security:**

- [Trivy Scanner](https://trivy.dev/)
- [Container Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

**Talma ADRs:**

- [ADR-007: Contenedores en AWS](../../decisiones-de-arquitectura/adr-007-contenedores-aws.md)
- [ADR-003: Gestión de Secretos](../../decisiones-de-arquitectura/adr-003-gestion-secretos.md)
