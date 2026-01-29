---
id: docker
sidebar_position: 1
title: Estándares para Docker
description: Estándar técnico obligatorio para construcción, optimización y despliegue seguro de contenedores Docker
---

# Estándar Técnico — Docker

---

## 1. Propósito
Garantizar imágenes de contenedores ligeras (<200MB), seguras (0 CVEs críticos) y reproducibles mediante multi-stage builds, Alpine/Slim, usuario no-root, tags semánticos y BuildKit.

---

## 2. Alcance

**Aplica a:**
- Aplicaciones backend (.NET) desplegadas en contenedores
- APIs REST, microservicios, workers, jobs en GitHub Container Registry
- Entornos Dev, Staging, Production

**No aplica a:**
- Scripts one-time locales sin despliegue
- Contenedores de testing efímeros sin publicación
- Imágenes de terceros consumidas as-is

---

## 3. Tecnologías Aprobadas

| Componente | Tecnología | Versión mínima | Observaciones |
|-----------|------------|----------------|---------------|
| **Docker Engine** | Docker Engine | 24.0+ | BuildKit nativo, multi-platform builds |
| **BuildKit** | Habilitado por defecto | 0.12+ | Cache eficiente, builds paralelos |
| **Imágenes Base** | Alpine (preferida), Slim | Latest LTS | Tamaño reducido 70-80% |
| **Scanner** | Trivy | Latest | Detecta CVEs antes de publicar |
| **Registry** | GitHub Container Registry (ghcr.io) | - | Registry privado integrado con GitHub |
| **.NET** | `dotnet/aspnet:8.0-alpine` | 8.0 | ~110MB |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Multi-stage build (mínimo 2 stages: build + runtime)
- [ ] Imagen base Alpine o Slim
- [ ] Usuario no-root creado (UID 1001)
- [ ] Health check configurado (interval 30s, timeout 5s)
- [ ] Tags semánticos v<MAJOR>.<MINOR>.<PATCH> (NO `latest` en prod)
- [ ] Secretos NO hardcodeados (usar Secrets Manager)
- [ ] Escaneo vulnerabilidades ejecutado (Trivy)
- [ ] CVEs críticos resueltos antes de push
- [ ] .dockerignore configurado (.git, node_modules, bin, obj, .env)
- [ ] BuildKit habilitado para cache eficiente
- [ ] Logs a stdout/stderr (NO archivos)
- [ ] Labels OCI (version, maintainer, title)
- [ ] Tamaño de imagen ≤ 200MB

---

## 5. Prohibiciones

- ❌ Tags `latest` en producción
- ❌ Usuario root (USER root)
- ❌ Secretos hardcodeados en Dockerfile
- ❌ Imágenes > 200MB sin justificación
- ❌ Builds sin BuildKit habilitado
- ❌ Publicar imágenes con CVEs críticos

---

## 6. Configuración Mínima

### .NET
```dockerfile
# syntax=docker/dockerfile:1.4
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src
COPY ["MyApp.csproj", "./"]
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final
RUN addgroup -g 1001 appuser && adduser -D -u 1001 -G appuser appuser
WORKDIR /app
COPY --from=build --chown=appuser:appuser /app/publish .
USER appuser
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8080/health || exit 1
EXPOSE 8080
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

---

## 7. Validación

```bash
# Escanear vulnerabilidades
trivy image --severity HIGH,CRITICAL myimage:v1.0.0

# Verificar usuario no-root
docker inspect myimage:v1.0.0 | jq '.[0].Config.User'

# Verificar health check
docker inspect myimage:v1.0.0 | jq '.[0].Config.Healthcheck'

# Verificar tamaño
docker images myimage:v1.0.0 --format "{{.Size}}"

# Verificar BuildKit usado
git log -1 --format=%B | grep DOCKER_BUILDKIT
```

**Métricas de cumplimiento:**

| Métrica | Target | Verificación |
|---------|--------|--------------|  
| Tamaño imagen | ≤ 200MB | `docker images` output |
| CVEs críticos | 0 | `trivy --severity CRITICAL` |
| Usuario no-root | 100% | `docker inspect \| grep User` |
| Tags `latest` en prod | 0% | ghcr.io registry inspection |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [ADR-007: Contenedores en AWS](../../../decisiones-de-arquitectura/adr-007-contenedores-aws.md)
- [ADR-003: Gestión de Secretos](../../../decisiones-de-arquitectura/adr-003-gestion-secretos.md)
- [Docker Compose](./04-docker-compose.md)
- [Infraestructura como Código](./02-infraestructura-como-codigo.md)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [BuildKit Documentation](https://github.com/moby/buildkit)
- [Trivy Scanner](https://trivy.dev/)
