---
id: docker
sidebar_position: 1
title: Estándares para Docker
description: Estándar técnico obligatorio para construcción, optimización y despliegue seguro de contenedores Docker
---

# Docker

## 1. Propósito

Definir la configuración técnica obligatoria para construir, optimizar y desplegar contenedores Docker en Talma mediante:
- **Imágenes multi-stage** con Alpine/Slim para reducir tamaño 70-80%
- **Seguridad** con usuarios no-root, escaneo de vulnerabilidades, no hardcodear secretos
- **Versionado semántico** con tags inmutables (`v1.2.3`, NO `latest`)
- **BuildKit** para builds paralelos y cache eficiente
- **Health checks** para monitoreo de disponibilidad

Garantiza imágenes ligeras (<200MB), seguras (0 CVEs críticos) y reproducibles.

## 2. Alcance

### Aplica a:

- ✅ Todas las aplicaciones backend (.NET, Node.js, Python) desplegadas en contenedores
- ✅ APIs REST, microservicios, workers, jobs
- ✅ Imágenes publicadas en Amazon ECR/Azure ACR
- ✅ Entornos Dev, Staging, Production

### NO aplica a:

- ❌ Scripts one-time ejecutados localmente sin despliegue
- ❌ Contenedores de testing efímeros sin publicación
- ❌ Imágenes de terceros consumidas as-is (solo para imágenes propias)

## 3. Tecnologías Obligatorias

| Categoría          | Tecnología / Configuración                | Versión   | Justificación                           |
| ------------------ | ----------------------------------------- | --------- | --------------------------------------- |
| **Docker Engine**  | Docker Engine                             | 24.0+     | BuildKit nativo, multi-platform builds  |
| **BuildKit**       | Habilitado por defecto                    | 0.12+     | Cache eficiente, builds paralelos       |
| **Imágenes Base**  | Alpine (preferida), Slim (alternativa)    | Latest LTS| Tamaño reducido 70-80%                  |
| **Scanner**        | Trivy, Snyk, AWS ECR scan                 | Latest    | Detecta CVEs antes de publicar          |
| **Registry**       | Amazon ECR, Azure ACR                     | -         | Registries privados con IAM/RBAC        |

### Imágenes Base Recomendadas

| Stack       | Imagen Base Recomendada                   | Tamaño    | Alternativa                          |
| ----------- | ----------------------------------------- | --------- | ------------------------------------ |
| **.NET 8**  | `mcr.microsoft.com/dotnet/aspnet:8.0-alpine` | ~110MB    | `dotnet/aspnet:8.0-jammy-chiseled` (Ubuntu) |
| **Node.js** | `node:20-alpine3.19`                      | ~120MB    | `node:20-slim`                       |
| **Python**  | `python:3.12-alpine3.19`                  | ~50MB     | `python:3.12-slim`                   |

## 4. Configuración Técnica Obligatoria

### 4.1 Dockerfile Multi-Stage para .NET

### 4.1 Dockerfile Multi-Stage para .NET

```dockerfile
# syntax=docker/dockerfile:1.4

# ===== Build Stage =====
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src

# ✅ Copiar solo csproj primero (mejor cache)
COPY ["src/Talma.Users.Api/Talma.Users.Api.csproj", "src/Talma.Users.Api/"]
COPY ["src/Talma.Users.Application/Talma.Users.Application.csproj", "src/Talma.Users.Application/"]
COPY ["src/Talma.Users.Domain/Talma.Users.Domain.csproj", "src/Talma.Users.Domain/"]
COPY ["src/Talma.Users.Infrastructure/Talma.Users.Infrastructure.csproj", "src/Talma.Users.Infrastructure/"]

# ✅ Restore (cacheado mientras no cambien csproj)
RUN dotnet restore "src/Talma.Users.Api/Talma.Users.Api.csproj"

# ✅ Copiar resto del código
COPY src/ src/

# ✅ Build y Publish
WORKDIR "/src/src/Talma.Users.Api"
RUN dotnet publish "Talma.Users.Api.csproj" \
    -c Release \
    -o /app/publish \
    --no-restore \
    /p:UseAppHost=false

# ===== Runtime Stage =====
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final

# ✅ Metadata con labels
LABEL org.opencontainers.image.title="Talma Users API" \
      org.opencontainers.image.description="API REST para gestión de usuarios" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.vendor="Talma" \
      maintainer="arquitectura@talma.com"

# ✅ Instalar curl para health checks
RUN apk add --no-cache curl

# ✅ Crear usuario no-root
RUN addgroup -g 1001 appuser && \
    adduser -D -u 1001 -G appuser appuser

WORKDIR /app

# ✅ Copiar binarios desde build stage
COPY --from=build --chown=appuser:appuser /app/publish .

# ✅ Cambiar a usuario no-root
USER appuser

# ✅ Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

ENTRYPOINT ["dotnet", "Talma.Users.Api.dll"]
```

### 4.2 Dockerfile Multi-Stage para Node.js

```dockerfile
# syntax=docker/dockerfile:1.4

# ===== Build Stage =====
FROM node:20-alpine3.19 AS build
WORKDIR /app

# ✅ Copiar package files primero
COPY package.json package-lock.json ./

# ✅ Install dependencies (con cache mount)
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

# ✅ Copiar código fuente
COPY . .

# ✅ Build (si aplica - Next.js, NestJS, etc.)
RUN npm run build

# ===== Runtime Stage =====
FROM node:20-alpine3.19 AS final

LABEL org.opencontainers.image.title="Talma Orders API" \
      org.opencontainers.image.version="1.0.0"

# ✅ Instalar curl para health checks
RUN apk add --no-cache curl

# ✅ Crear usuario no-root
RUN addgroup -g 1001 appuser && \
    adduser -D -u 1001 -G appuser appuser

WORKDIR /app

# ✅ Copiar node_modules y build desde stage anterior
COPY --from=build --chown=appuser:appuser /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appuser /app/dist ./dist
COPY --from=build --chown=appuser:appuser /app/package.json ./

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["node", "dist/main.js"]
```

### 4.3 .dockerignore para Optimizar Builds

```bash
# ✅ Excluir archivos innecesarios para reducir context size

# Git
.git/
.gitignore
.gitattributes

# Node.js
node_modules/
npm-debug.log
.npm/
*.log

# .NET
bin/
obj/
*.user
*.suo
*.cache
*.dll
*.pdb

# IDEs
.vscode/
.vs/
.idea/
*.swp
*.swo

# Testing
coverage/
*.test.js
*.spec.js

# CI/CD
.github/
.gitlab-ci.yml
azure-pipelines.yml

# Docs
README.md
docs/
*.md

# Environment files (NO incluir en imagen)
.env
.env.*
!.env.example
```

### 4.4 Build con BuildKit (Cache Eficiente)

```bash
# ✅ Habilitar BuildKit (mejor performance)
export DOCKER_BUILDKIT=1

# ✅ Build con cache inline
docker build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t talma-users-api:v1.0.0 \
    -f Dockerfile \
    .

# ✅ Build multi-platform (ARM64 + AMD64)
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t talma-users-api:v1.0.0 \
    --push \
    .

# ✅ Build con secrets (no exponer en layers)
docker build \
    --secret id=npmrc,src=$HOME/.npmrc \
    -t talma-users-api:v1.0.0 \
    .

# En Dockerfile:
# RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
#     npm install
```

## 5. Ejemplos de Implementación

### 5.1 Tagging y Push a Amazon ECR

```bash
# ✅ Login a ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# ✅ Build con tags múltiples
docker build -t talma-users-api:v1.2.3 .

# ✅ Tag semántico (MAJOR.MINOR.PATCH)
docker tag talma-users-api:v1.2.3 123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:v1.2.3
docker tag talma-users-api:v1.2.3 123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:v1.2
docker tag talma-users-api:v1.2.3 123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:v1
docker tag talma-users-api:v1.2.3 123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:latest

# ✅ Push todas las tags
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:v1.2.3
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:v1.2
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:v1
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:latest
```

### 5.2 Health Check Configurado en ECS Task Definition

```json
{
  "family": "talma-users-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "talma-users-api",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/talma-users-api:v1.2.3",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "ASPNETCORE_ENVIRONMENT", "value": "Production" },
        { "name": "ASPNETCORE_URLS", "value": "http://+:8080" }
      ],
      "secrets": [
        {
          "name": "ConnectionStrings__Default",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/users-api/db-conn"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/talma-users-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 5.3 Escaneo de Vulnerabilidades con Trivy

```bash
# ✅ Escanear imagen antes de push
trivy image --severity HIGH,CRITICAL talma-users-api:v1.2.3

# ✅ Output JSON para CI/CD
trivy image --format json --output trivy-report.json talma-users-api:v1.2.3

# ✅ Fallar build si hay CVEs críticos
trivy image --exit-code 1 --severity CRITICAL talma-users-api:v1.2.3

# ✅ Escaneo en pipeline CI/CD (.github/workflows/build.yml)
# - name: Scan image
#   run: |
#     docker run --rm \
#       -v /var/run/docker.sock:/var/run/docker.sock \
#       aquasec/trivy:latest image \
#       --exit-code 1 --severity CRITICAL \
#       talma-users-api:${{ github.sha }}
```

## 6. Mejores Prácticas

### 6.1 Optimización de Capas

```dockerfile
# ❌ MAL - Múltiples capas innecesarias
RUN apk add curl
RUN apk add bash
RUN apk add git

# ✅ BIEN - Una sola capa
RUN apk add --no-cache curl bash git

# ❌ MAL - Copiar todo de una vez (invalida cache fácilmente)
COPY . /app

# ✅ BIEN - Copiar dependencias primero, luego código
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

### 6.2 Logging a stdout/stderr

```csharp
// ✅ ASP.NET Core - Logging estructurado a stdout
var builder = WebApplication.CreateBuilder(args);

builder.Logging.ClearProviders();
builder.Logging.AddJsonConsole(options =>
{
    options.IncludeScopes = true;
    options.TimestampFormat = "yyyy-MM-dd'T'HH:mm:ss.fffzzz";
    options.JsonWriterOptions = new JsonWriterOptions
    {
        Indented = false
    };
});

var app = builder.Build();
app.Run();
```

```typescript
// ✅ Node.js - Winston con formato JSON
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console()
  ]
});

logger.info('Server started', { port: 3000 });
```

### 6.3 Variables de Entorno y Secretos

```bash
# ✅ BIEN - Usar AWS Secrets Manager en ECS
# Task Definition:
"secrets": [
  {
    "name": "DB_PASSWORD",
    "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-password"
  }
]

# ❌ MAL - Hardcodear en Dockerfile
# ENV DB_PASSWORD=MySecretPassword123  ❌ NUNCA HACER

# ❌ MAL - Pasar en docker run
# docker run -e DB_PASSWORD=MySecret talma-api  ❌ Visible en logs

# ✅ BIEN - Usar archivos de secretos (local dev)
docker run --env-file .env.secrets talma-api
```

## 7. Antipatrones (NO Hacer)

### ❌ Antipatrón 1: Usar Tag `latest` en Production

```bash
# ❌ MAL - Tag mutable en producción
docker pull talma-users-api:latest
# Problema: No sabes qué versión estás desplegando

# ✅ BIEN - Tag inmutable con semantic versioning
docker pull talma-users-api:v1.2.3
# Garantiza reproducibilidad
```

**Problema**: Tag `latest` es mutable, no sabes qué código estás desplegando, imposible rollback confiable.  
**Solución**: Usar semantic versioning (`v1.2.3`), tags inmutables, trazabilidad con Git SHA.

### ❌ Antipatrón 2: Ejecutar Contenedores como Root

```dockerfile
# ❌ MAL - Usuario root por defecto
FROM node:20-alpine
WORKDIR /app
COPY . .
CMD ["node", "server.js"]
# Contenedor corre como root (UID 0) ❌

# ✅ BIEN - Usuario no-root explícito
FROM node:20-alpine

RUN addgroup -g 1001 appuser && \
    adduser -D -u 1001 -G appuser appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

USER appuser
CMD ["node", "server.js"]
```

**Problema**: Contenedores root pueden escapar y comprometer el host, violan principio de least privilege.  
**Solución**: Crear usuario no-root (UID 1001), usar `USER` directive, `--chown` en COPY.

### ❌ Antipatrón 3: Hardcodear Secretos en Imagen

```dockerfile
# ❌ MAL - Secretos en variables de entorno (quedan en layers)
FROM node:20-alpine
ENV DB_PASSWORD="SuperSecretPassword123"
ENV API_KEY="sk_live_abc123def456"
# ❌ Secretos visibles con `docker history`

# ✅ BIEN - Inyectar secretos en runtime
FROM node:20-alpine
# NO hardcodear secretos

# En ECS Task Definition:
# "secrets": [
#   {
#     "name": "DB_PASSWORD",
#     "valueFrom": "arn:aws:secretsmanager:..."
#   }
# ]
```

**Problema**: Secretos hardcodeados quedan en layers de imagen, visibles con `docker history`, leak en registry.  
**Solución**: AWS Secrets Manager, Azure Key Vault, variables en runtime, NUNCA en Dockerfile.

### ❌ Antipatrón 4: Imágenes Grandes Sin Multi-Stage

```dockerfile
# ❌ MAL - Imagen con SDK completo (800MB+)
FROM mcr.microsoft.com/dotnet/sdk:8.0
WORKDIR /app
COPY . .
RUN dotnet publish -c Release -o /app/publish
ENTRYPOINT ["dotnet", "/app/publish/MyApp.dll"]
# Imagen final: 800MB+ ❌

# ✅ BIEN - Multi-stage build (120MB)
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "MyApp.dll"]
# Imagen final: 120MB ✅ (85% reducción)
```

**Problema**: Imágenes grandes (>500MB) aumentan tiempo de pull, costo de almacenamiento, superficie de ataque.  
**Solución**: Multi-stage builds, imágenes Alpine/Slim, copiar solo binarios finales.

## 8. Validación y Cumplimiento

### 8.1 Checklist de Implementación

- [ ] **Multi-stage build** implementado (build + runtime separados)
- [ ] **Imagen base Alpine o Slim** utilizada
- [ ] **Usuario no-root** creado y configurado (UID 1001)
- [ ] **Health check** definido en Dockerfile
- [ ] **Tags semánticos** aplicados (`v1.2.3`, NO `latest` en prod)
- [ ] **Secrets** NO hardcodeados (usar Secrets Manager)
- [ ] **Escaneo de vulnerabilidades** ejecutado (Trivy/Snyk)
- [ ] **CVEs críticos** resueltos antes de push
- [ ] **.dockerignore** configurado (reduce context size)
- [ ] **BuildKit** habilitado para cache eficiente
- [ ] **Logs a stdout/stderr** (NO archivos)
- [ ] **Labels OCI** agregados (version, maintainer)

### 8.2 Métricas de Cumplimiento

| Métrica                              | Target       | Verificación                        |
| ------------------------------------ | ------------ | ----------------------------------- |
| Tamaño de imagen final               | ≤ 200MB      | `docker images` output              |
| CVEs críticos                        | 0            | Trivy scan con `--severity CRITICAL`|
| Tiempo de build                      | ≤ 5 min      | CI/CD logs                          |
| Tiempo de pull (primera vez)         | ≤ 1 min      | ECS deployment logs                 |
| Contenedores ejecutando como root    | 0%           | `docker inspect` (User != root)     |
| Imágenes con tag `latest` en prod    | 0%           | ECR registry inspection             |

## 9. Referencias

### Estándares Relacionados

- [Docker Compose](./04-docker-compose.md) - Orquestación local multi-contenedor
- [Infraestructura como Código](./02-infraestructura-como-codigo.md) - Terraform para ECS/Fargate
- [Secrets Management](./03-secrets-management.md) - AWS Secrets Manager integration

### Convenciones Relacionadas

- [Naming Infraestructura](../../convenciones/infraestructura/01-naming.md) - Nomenclatura de imágenes

### Lineamientos Relacionados

- [Despliegue y DevOps](../../lineamientos/desarrollo/despliegue-y-devops.md) - CI/CD pipelines
- [Seguridad Aplicativa](../../lineamientos/seguridad/seguridad-aplicativa.md) - Seguridad en contenedores

### Principios Relacionados

- [Seguridad por Diseño](../../principios/arquitectura/07-seguridad-por-diseno.md) - Principio de least privilege
- [Eficiencia y Optimización](../../principios/arquitectura/08-eficiencia-optimizacion.md) - Optimización de recursos

### ADRs Relacionados

- [ADR-007: Contenedores en AWS](../../../decisiones-de-arquitectura/adr-007-contenedores-aws.md)
- [ADR-003: Gestión de Secretos](../../../decisiones-de-arquitectura/adr-003-gestion-secretos.md)

### Documentación Externa

- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) - Docker official docs
- [BuildKit Documentation](https://github.com/moby/buildkit/blob/master/README.md) - BuildKit features
- [Trivy Vulnerability Scanner](https://trivy.dev/) - Container scanning tool
- [OCI Image Spec](https://github.com/opencontainers/image-spec) - Container image standards

---

**Última actualización**: 27 de enero 2026  
**Responsable**: Equipo de Arquitectura
```

## 8. .dockerignore

Usar `.dockerignore` para excluir archivos innecesarios del contexto de build:

```
# .dockerignore
bin/
obj/
node_modules/
.git/
.gitignore
*.md
.vscode/
.vs/
Dockerfile
docker-compose*.yml
```

## 📖 Referencias

### Lineamientos relacionados

- [Diseño Cloud Native](/docs/fundamentos-corporativos/lineamientos/arquitectura/diseno-cloud-native)
- [Infraestructura como Código](/docs/fundamentos-corporativos/lineamientos/operabilidad/infraestructura-como-codigo)

### ADRs relacionados

- [ADR-007: Contenedores en AWS](/docs/decisiones-de-arquitectura/adr-007-contenedores-aws)

### Recursos externos

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Security Best Practices](https://docs.docker.com/engine/security/)
