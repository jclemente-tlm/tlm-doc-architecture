---
title: "Especificaciones Generales"
sidebar_position: 1
---

## 1. Imágenes de Contenedores

- Usar imágenes oficiales y ligeras (preferir Alpine o Slim).
- Mantener Dockerfiles simples, legibles y con comentarios claros.
- Eliminar dependencias innecesarias y archivos temporales.

**Ejemplo Dockerfile para .NET (usando imagen slim o alpine):**

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0-slim AS base
# Alternativamente puedes usar: mcr.microsoft.com/dotnet/aspnet:8.0-alpine
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0-slim AS build
# Alternativamente puedes usar: mcr.microsoft.com/dotnet/sdk:8.0-alpine
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

## 3. Versionado y Etiquetado

- Utilizar etiquetas semánticas (`v1.0.0`, `v1.1.0`, etc.).
- Evitar el uso de la etiqueta `latest` en ambientes productivos.

## 4. Configuración

- Gestionar la configuración mediante variables de entorno.
- Separar la configuración del código fuente.

**Ejemplo de definición de variables en AWS Fargate (ECS Task Definition):**

```json
{
  "containerDefinitions": [
    {
      "name": "myapp",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:v1.0.0",
      "environment": [
        { "name": "ASPNETCORE_ENVIRONMENT", "value": "Production" },
        { "name": "ConnectionStrings__Default", "value": "..." }
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
      "cpu": 256
    }
  ]
}
```

## 6. Observabilidad

- Integrar los contenedores con sistemas de logging y monitoreo.
- Exponer métricas relevantes para el negocio y la operación.

## 7. Buenas Prácticas

- Un solo proceso por contenedor.
- Mantener los contenedores inmutables.
- Documentar el proceso de construcción y despliegue.
