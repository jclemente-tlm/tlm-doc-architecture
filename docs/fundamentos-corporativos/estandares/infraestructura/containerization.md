---
id: containerization
sidebar_position: 1
title: Contenerización con Docker
description: Estrategia de contenerización para portabilidad y consistencia entre ambientes
---

# Contenerización con Docker

## Contexto

Este estándar define cómo contenerizar aplicaciones usando Docker para garantizar portabilidad, consistencia y despliegues reproducibles. Complementa el [lineamiento de Cloud Native](../../lineamientos/arquitectura/03-cloud-native.md) implementando el **factor II (Dependencies)** y **factor VII (Port Binding)** de 12-Factor App.

---

## Stack Tecnológico

| Componente            | Tecnología                | Versión | Uso                          |
| --------------------- | ------------------------- | ------- | ---------------------------- |
| **Container Runtime** | Docker                    | 24.0+   | Container runtime            |
| **Base Images**       | MCR .NET Images           | 8.0+    | Microsoft Container Registry |
| **Registry**          | GitHub Container Registry | -       | Container image registry     |
| **Orchestration**     | AWS ECS Fargate           | -       | Container orchestration      |

---

## Implementación Técnica

### Dockerfile Multi-Stage

```dockerfile
# ✅ Multi-stage build para optimizar tamaño de imagen

# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src

# ✅ Copy solo .csproj primero (aprovecha cache de Docker)
COPY ["OrdersApi/OrdersApi.csproj", "OrdersApi/"]
COPY ["OrdersApi.Domain/OrdersApi.Domain.csproj", "OrdersApi.Domain/"]
COPY ["OrdersApi.Infrastructure/OrdersApi.Infrastructure.csproj", "OrdersApi.Infrastructure/"]

# ✅ Restore dependencies (cacheado si .csproj no cambia)
RUN dotnet restore "OrdersApi/OrdersApi.csproj"

# ✅ Copy resto del código
COPY . .

# ✅ Build
WORKDIR "/src/OrdersApi"
RUN dotnet build "OrdersApi.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "OrdersApi.csproj" \
    -c Release \
    -o /app/publish \
    --no-restore \
    /p:UseAppHost=false

# Stage 3: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final

# ✅ Non-root user para seguridad
RUN addgroup -g 1000 appuser && \
    adduser -u 1000 -G appuser -s /bin/sh -D appuser

WORKDIR /app

# ✅ Instalar dependencias de sistema solo si es necesario
# RUN apk add --no-cache icu-libs tzdata

# ✅ Copy artifacts desde build stage
COPY --from=publish --chown=appuser:appuser /app/publish .

# ✅ Switch a non-root user
USER appuser

# ✅ Exponer puerto
EXPOSE 8080

# ✅ Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health/live || exit 1

# ✅ Entrypoint exec form (recibe SIGTERM correctamente)
ENTRYPOINT ["dotnet", "OrdersApi.dll"]

# Tamaño final: ~110MB (vs ~700MB con SDK image)
```

### .dockerignore

```gitignore
# ✅ Excluir archivos innecesarios para reducir build context

**/.git
**/.gitignore
**/.vs
**/.vscode
**/bin
**/obj
**/node_modules
**/*.user
**/*.suo
**/TestResults
**/.DS_Store
**/Thumbs.db

# Docs
**/*.md
!README.md

# CI/CD
**/.github
**/.gitlab-ci.yml
**/azure-pipelines.yml

# Local config
**/.env
**/.env.local
**/appsettings.Development.json
```

### Image Tagging Strategy

```yaml
# ✅ Estrategia de tags

# 1. SHA tag (inmutable, para trazabilidad)
ghcr.io/talma/orders-api:sha-abc123def456

# 2. Semantic version tag
ghcr.io/talma/orders-api:v1.2.3

# 3. Environment tag (mutable, apunta a última versión deployed)
ghcr.io/talma/orders-api:production
ghcr.io/talma/orders-api:staging

# 4. Latest tag (mutable, última build exitosa de main)
ghcr.io/talma/orders-api:latest

# ✅ Ejemplo en CI/CD
docker build -t ghcr.io/talma/orders-api:${COMMIT_SHA} .
docker tag ghcr.io/talma/orders-api:${COMMIT_SHA} ghcr.io/talma/orders-api:v${VERSION}
docker tag ghcr.io/talma/orders-api:${COMMIT_SHA} ghcr.io/talma/orders-api:latest
docker push ghcr.io/talma/orders-api --all-tags
```

### GitHub Actions - Build & Push

```yaml
# .github/workflows/docker-build.yml

name: Build and Push Docker Image

on:
  push:
    branches: [main, develop]
    tags: ["v*"]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=sha-

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64 # Fargate solo soporta amd64
```

### Docker Compose para Desarrollo

```yaml
# docker-compose.yml

version: "3.8"

services:
  # ✅ Aplicación
  orders-api:
    build:
      context: .
      dockerfile: Dockerfile
      target: final # O "publish" para debug
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_URLS=http://+:8080
      - ConnectionStrings__OrdersDb=Host=postgres;Database=orders;Username=dev;Password=dev
      - Redis__ConnectionString=redis:6379
      - Kafka__BootstrapServers=kafka:9092
      - AWS_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_ENDPOINT_URL=http://localstack:4566 # LocalStack para AWS services
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      kafka:
        condition: service_started
    networks:
      - talma-network
    volumes:
      # ✅ Hot reload para desarrollo (opcional)
      - ./OrdersApi:/app
    healthcheck:
      test:
        ["CMD", "wget", "--spider", "-q", "http://localhost:8080/health/live"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

  # ✅ PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: orders
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - talma-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev"]
      interval: 5s
      timeout: 5s
      retries: 5

  # ✅ Redis
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - talma-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  # ✅ Kafka
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
    networks:
      - talma-network

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - talma-network

  # ✅ LocalStack (AWS services locales)
  localstack:
    image: localstack/localstack:3.0
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,sqs,secretsmanager,ssm
      - DEBUG=1
    volumes:
      - localstack-data:/var/lib/localstack
    networks:
      - talma-network

volumes:
  postgres-data:
  redis-data:
  localstack-data:

networks:
  talma-network:
    driver: bridge
```

### Security Scanning

```yaml
# ✅ Scan de vulnerabilidades con Trivy

# .github/workflows/security-scan.yml
name: Container Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 0 * * 0" # Weekly scan

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Build image
        run: docker build -t orders-api:scan .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: "orders-api:scan"
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: "trivy-results.sarif"

      - name: Fail on critical vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: "orders-api:scan"
          format: "table"
          exit-code: "1"
          severity: "CRITICAL"
```

### ECS Task Definition

```hcl
# Terraform - ECS Task usando container image

resource "aws_ecs_task_definition" "orders_api" {
  family                   = "orders-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name      = "orders-api"
    # ✅ Usar SHA tag (inmutable)
    image     = "ghcr.io/talma/orders-api:sha-${var.commit_sha}"
    essential = true

    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]

    # ✅ Environment variables
    environment = [
      { name = "ASPNETCORE_ENVIRONMENT", value = "Production" },
      { name = "ASPNETCORE_URLS", value = "http://+:8080" }
    ]

    # ✅ Secrets desde AWS Secrets Manager
    secrets = [
      {
        name      = "ConnectionStrings__OrdersDb"
        valueFrom = aws_secretsmanager_secret.db_connection.arn
      },
      {
        name      = "Redis__ConnectionString"
        valueFrom = "${aws_ssm_parameter.redis_connection.arn}"
      }
    ]

    # ✅ Logs a CloudWatch
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/orders-api"
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
        "awslogs-create-group"  = "true"
      }
    }

    # ✅ Health check
    healthCheck = {
      command     = ["CMD-SHELL", "wget --spider -q http://localhost:8080/health/live || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }

    # ✅ Resource limits
    cpu    = 512
    memory = 1024

    # ✅ Readonly root filesystem para seguridad
    readonlyRootFilesystem = true

    # ✅ Mount /tmp como writable
    mountPoints = [{
      sourceVolume  = "tmp"
      containerPath = "/tmp"
      readOnly      = false
    }]

    stopTimeout = 30
  }])

  # ✅ Volume para /tmp
  volume {
    name = "tmp"
  }
}
```

### Image Size Optimization

```dockerfile
# ✅ Técnicas para reducir tamaño de imagen

# 1. Usar alpine base images
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine
# alpine: ~110MB vs debian: ~220MB

# 2. Self-contained deployment (opcional, mayor tamaño pero no requiere runtime)
RUN dotnet publish -c Release -r linux-musl-x64 --self-contained true

# 3. Trimming (remover código no usado)
RUN dotnet publish -c Release \
    -p:PublishTrimmed=true \
    -p:TrimMode=Link

# 4. ReadyToRun (AOT compilation parcial)
RUN dotnet publish -c Release \
    -p:PublishReadyToRun=true

# 5. Remover símbolos de debug
RUN dotnet publish -c Release \
    -p:DebugType=none \
    -p:DebugSymbols=false

# 6. Multi-arch builds (solo si necesario)
# docker buildx build --platform linux/amd64,linux/arm64 -t image:tag .

# Resultado:
# - Sin optimización: ~220MB
# - Con alpine + trimming: ~80MB
# - Con self-contained + trimming: ~50MB (no requiere runtime)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar multi-stage builds para optimizar tamaño
- **MUST** usar alpine base images cuando sea posible
- **MUST** crear .dockerignore para reducir build context
- **MUST** ejecutar container como non-root user
- **MUST** usar ENTRYPOINT exec form (no shell form)
- **MUST** exponer solo puertos necesarios
- **MUST** incluir HEALTHCHECK en Dockerfile
- **MUST** usar SHA tags para deployments (inmutabilidad)
- **MUST** escanear imágenes con Trivy o equivalente

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar GitHub Container Registry para almacenar imágenes
- **SHOULD** versionar imágenes con semantic versioning
- **SHOULD** implementar Docker Compose para desarrollo local
- **SHOULD** usar BuildKit cache para acelerar builds
- **SHOULD** mantener imágenes < 200MB
- **SHOULD** usar readonly root filesystem cuando sea posible
- **SHOULD** automatizar builds con CI/CD

### MAY (Opcional)

- **MAY** usar self-contained deployments para reducir dependencias
- **MAY** implementar trimming para reducir tamaño
- **MAY** usar multi-arch builds si se requiere ARM support

### MUST NOT (Prohibido)

- **MUST NOT** incluir secretos en imágenes
- **MUST NOT** ejecutar como root user
- **MUST NOT** instalar dependencias innecesarias
- **MUST NOT** usar tags mutables (latest, dev) en producción
- **MUST NOT** incluir SDK en runtime images
- **MUST NOT** hardcodear configuración en Dockerfile
- **MUST NOT** exponer puertos innecesarios

---

## Referencias

- [Lineamiento: Cloud Native](../../lineamientos/arquitectura/03-cloud-native.md)
- [ADR-007: AWS ECS Fargate](../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- [ADR-022: GitHub Container Registry](../../decisiones-de-arquitectura/adr-022-github-container-registry.md)
- Estándares relacionados:
  - [12-Factor App](../arquitectura/twelve-factor-app.md)
  - [Graceful Shutdown](../arquitectura/graceful-shutdown.md)
- Especificaciones:
  - [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
  - [.NET Docker Images](https://hub.docker.com/_/microsoft-dotnet)
  - [Docker Security](https://docs.docker.com/engine/security/)
