---
id: docker
sidebar_position: 1
title: Estándares para Docker
description: Estándares para construcción, despliegue y gestión de contenedores Docker
---

## 1. Imágenes de Contenedores

- Usar imágenes oficiales y ligeras basadas en versiones LTS estables (evitar versiones experimentales o no soportadas).
- Preferir imágenes **Alpine**; si no es compatible usar imágenes **Slim**.
- Mantener Dockerfiles simples, legibles y con comentarios claros.
- Eliminar dependencias innecesarias y archivos temporales.

**Ejemplo Dockerfile para .NET:**

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src
COPY ["MyApp/MyApp.csproj", "MyApp/"]
RUN dotnet restore "MyApp/MyApp.csproj"
COPY . .
WORKDIR "/src/MyApp"
RUN dotnet publish "MyApp.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

> **Nota:** Alpine puede requerir validación adicional de compatibilidad para aplicaciones .NET.

## 2. Seguridad

- No almacenar credenciales ni secretos en la imagen.
- Escanear imágenes en busca de vulnerabilidades antes de publicar.
- Actualizar periódicamente las imágenes base.
- Usar usuarios no root para ejecutar contenedores.

```dockerfile
# Crear usuario no root
RUN addgroup -g 1001 appuser && adduser -D -u 1001 -G appuser appuser
USER appuser
```

## 3. Versionado y Etiquetado

- Utilizar etiquetas semánticas (`v1.0.0`, `v1.1.0`, etc.).
- Evitar el uso de la etiqueta `latest` en ambientes productivos.
- Incluir el SHA del commit en las tags de desarrollo.

```bash
# Ejemplo de tagging
docker build -t myapp:v1.2.3 .
docker tag myapp:v1.2.3 myapp:v1.2
docker tag myapp:v1.2.3 myapp:v1
```

## 4. Configuración

- Gestionar la configuración mediante variables de entorno.
- Separar la configuración del código fuente.
- Usar secretos gestionados por la plataforma (AWS Secrets Manager, etc.).

**Ejemplo de definición de variables en AWS Fargate (ECS Task Definition):**

```json
{
  "containerDefinitions": [
    {
      "name": "myapp",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:v1.0.0",
      "environment": [
        { "name": "ASPNETCORE_ENVIRONMENT", "value": "Production" },
        { "name": "LOG_LEVEL", "value": "Information" }
      ],
      "secrets": [
        {
          "name": "DB_CONNECTION_STRING",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:db-conn-abc123"
        }
      ]
    }
  ]
}
```

## 5. Orquestación y Despliegue

- Definir recursos mínimos y máximos (CPU, memoria) en los manifiestos.
- Usar estrategias de despliegue seguras (rolling update, blue/green).
- Mantener archivos declarativos organizados y versionados.

**Ejemplo de definición de recursos en AWS Fargate (ECS Task Definition):**

```json
{
  "containerDefinitions": [
    {
      "name": "myapp",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:v1.0.0",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

## 6. Observabilidad

- Integrar los contenedores con sistemas de logging y monitoreo.
- Exponer métricas relevantes para el negocio y la operación.
- Configurar health checks apropiados.
- Escribir logs a stdout/stderr (no a archivos).

```csharp
// ASP.NET Core - Logging a stdout
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddJsonConsole();
```

## 7. Buenas Prácticas

- **Un solo proceso por contenedor** (principio de responsabilidad única).
- **Mantener los contenedores inmutables** (no modificar contenedores en ejecución).
- **Optimizar capas del Dockerfile** (poner comandos que cambian poco al principio).
- **Multi-stage builds** para reducir tamaño de imagen final.
- **Documentar el proceso de construcción y despliegue** en README.

```dockerfile
# Multi-stage build optimizado
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src
# Copiar solo archivos de proyecto primero (mejor uso de cache)
COPY ["*.csproj", "./"]
RUN dotnet restore
# Luego copiar el resto
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final
WORKDIR /app
COPY --from=build /app/publish .
# Usuario no root
RUN addgroup -g 1001 appuser && adduser -D -u 1001 -G appuser appuser
USER appuser
ENTRYPOINT ["dotnet", "MyApp.dll"]
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
