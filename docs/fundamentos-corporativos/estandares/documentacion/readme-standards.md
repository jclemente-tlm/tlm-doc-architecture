---
id: readme-standards
sidebar_position: 3
title: README
description: Estándar para crear documentación README en repositorios, con template completo y convenciones de badges.
---

# README

## Contexto

Este estándar define cómo crear README.md en repositorios, asegurando que todo servicio tenga documentación accesible y actualizada desde el primer contacto. Complementa el lineamiento [Documentación Técnica](../../lineamientos/desarrollo/03-documentacion-tecnica.md).

---

## Stack Tecnológico

| Componente          | Tecnología | Versión | Uso                            |
| ------------------- | ---------- | ------- | ------------------------------ |
| **Documentación**   | Markdown   | -       | Formato de documentos          |
| **Hosting**         | GitHub     | -       | Repositorio y renderizado      |
| **Diagramas**       | Mermaid    | 10.0+   | Diagramas as code              |
| **Generación Docs** | Docusaurus | 3.0+    | Documentación web centralizada |

---

## ¿Qué es un README?

Documento principal del repositorio que proporciona overview del proyecto, cómo instalarlo, usarlo y contribuir.

**Secciones obligatorias:**

1. **Título y descripción**: Qué hace el servicio
2. **Badges**: Estado CI/CD, coverage, versión
3. **Prerequisitos**: Qué se necesita instalar
4. **Primeros Pasos**: Cómo ejecutar localmente
5. **Uso**: Ejemplos de uso
6. **Pruebas**: Cómo ejecutar tests
7. **Deployment**: Cómo desplegar
8. **Tecnologías**: Stack tecnológico
9. **Contribuir**: Link a CONTRIBUTING.md
10. **Licencia**: Tipo de licencia

**Propósito:** Primera impresión, guía rápida para desarrolladores.

**Beneficios:**
✅ Onboarding rápido
✅ Autoservicio para desarrolladores
✅ Documentación actualizada
✅ Profesionalismo

## Plantilla README Completa

````markdown
# Customer Service

[![Build Status](https://github.com/talma/customer-service/actions/workflows/build.yml/badge.svg)](https://github.com/talma/customer-service/actions)
[![Test Coverage](https://codecov.io/gh/talma/customer-service/branch/main/graph/badge.svg)](https://codecov.io/gh/talma/customer-service)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![.NET Version](https://img.shields.io/badge/.NET-8.0-purple.svg)](https://dotnet.microsoft.com/)

Servicio de gestión de clientes para la plataforma de e-commerce, responsable del ciclo de vida completo de clientes incluyendo registro, actualización, consulta y eliminación lógica.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Prerequisitos](#prerequisitos)
- [Primeros Pasos](#primeros-pasos)
- [Uso](#uso)
- [Pruebas](#pruebas)
- [Deployment](#deployment)
- [Stack Tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

## ✨ Características

- ✅ CRUD completo de clientes
- ✅ Validación de documentos (DNI, RUC, CE)
- ✅ Búsqueda por email, documento, nombre
- ✅ Paginación y filtros
- ✅ Events para sincronización con otros servicios
- ✅ Cache con Redis
- ✅ API versionada (v1)
- ✅ OpenAPI/Swagger documentation
- ✅ Health checks
- ✅ Observabilidad con OpenTelemetry

## 🔧 Prerequisitos

Antes de comenzar, asegúrate de tener instalado:

- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0) - v8.0 o superior
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) - v24.0 o superior
- [Git](https://git-scm.com/) - v2.40 o superior
- (Opcional) [Visual Studio 2022](https://visualstudio.microsoft.com/) o [Rider](https://www.jetbrains.com/rider/)

### Verificar instalación

```bash
dotnet --version  # Debe mostrar 8.0.x
docker --version  # Debe mostrar 24.0.x o superior
git --version     # Debe mostrar 2.40.x o superior
```

## 🚀 Primeros Pasos

### 1. Clonar el repositorio

```bash
git clone https://github.com/talma/customer-service.git
cd customer-service
```

### 2. Configurar variables de entorno

```bash
# Copiar template de variables
cp .env.example .env

# Editar .env con tus configuraciones locales
nano .env
```

### 3. Iniciar dependencias con Docker Compose

```bash
# Iniciar PostgreSQL, Redis, Kafka
docker-compose up -d

# Verificar que contenedores estén corriendo
docker-compose ps
```

### 4. Aplicar migraciones de base de datos

```bash
dotnet ef database update --project src/CustomerService.Infrastructure
```

### 5. Ejecutar el servicio

```bash
# Opción 1: Con dotnet CLI
dotnet run --project src/CustomerService.Api

# Opción 2: Con docker-compose (incluye servicio)
docker-compose --profile app up

# El servicio estará disponible en:
# - API: http://localhost:8080
# - Swagger UI: http://localhost:8080/swagger
# - Health checks: http://localhost:8080/health
```

### 6. Verificar que funciona

```bash
# Health check
curl http://localhost:8080/health

# Crear un cliente
curl -X POST http://localhost:8080/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+51987654321",
    "document": {
      "type": "DNI",
      "number": "12345678"
    }
  }'
```

## 📖 Uso

### Endpoints principales

#### Crear cliente

```bash
POST /api/v1/customers
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+51987654321",
  "document": {
    "type": "DNI",
    "number": "87654321"
  }
}
```

#### Obtener cliente por ID

```bash
GET /api/v1/customers/{id}
```

#### Buscar clientes

```bash
GET /api/v1/customers?page=1&pageSize=10&searchTerm=jane
```

#### Actualizar cliente

```bash
PUT /api/v1/customers/{id}
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "+51999999999"
}
```

#### Eliminar cliente (soft delete)

```bash
DELETE /api/v1/customers/{id}
```

### Swagger UI

Documentación interactiva disponible en: http://localhost:8080/swagger

## 🧪 Pruebas

### Unit Tests

```bash
# Ejecutar todos los tests
dotnet test

# Ejecutar tests con coverage
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover

# Ver reporte de coverage
dotnet tool install -g dotnet-reportgenerator-globaltool
reportgenerator -reports:coverage.opencover.xml -targetdir:coverage-report
open coverage-report/index.html
```

### Integration Tests

```bash
# Los integration tests usan Testcontainers (arrancan PostgreSQL automáticamente)
dotnet test --filter "Category=Integration"
```

### Contract Tests

```bash
dotnet test --filter "Category=Contract"
```

## 🚢 Deployment

### Build Docker Image

```bash
# Build imagen
docker build -t customer-service:latest .

# Tag para registry
docker tag customer-service:latest ghcr.io/talma/customer-service:1.0.0

# Push a GitHub Container Registry
docker push ghcr.io/talma/customer-service:1.0.0
```

### Deploy a AWS ECS

```bash
# Via Terraform
cd terraform/
terraform init
terraform plan -var-file=environments/production.tfvars
terraform apply -var-file=environments/production.tfvars

# Via GitHub Actions (recomendado)
# Push a main → auto-deploy a dev
# Create tag v1.0.0 → auto-deploy a staging/production
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

## 🛠 Stack Tecnológico

### Backend

- **.NET 8** - Framework principal
- **ASP.NET Core** - Web API
- **Entity Framework Core 8.0** - ORM
- **FluentValidation 11.0** - Validaciones
- **Polly 8.0** - Resilience patterns

### Bases de Datos

- **PostgreSQL 15** - Base de datos principal
- **Redis 7.2** - Cache

### Messaging

- **Apache Kafka 3.6** - Event streaming (modo Kraft)

### Observabilidad

- **Serilog** - Structured logging
- **OpenTelemetry** - Traces y metrics
- **Grafana Stack** - Visualización (Loki, Mimir, Tempo)

### DevOps

- **Docker** - Contenedores
- **GitHub Actions** - CI/CD
- **Terraform** - Infrastructure as Code
- **AWS ECS Fargate** - Hosting

## 🏗 Arquitectura

### Clean Architecture Layers

```
┌─────────────────────────────────────┐
│         API Layer (ASP.NET Core)    │
│  Controllers, Middleware, Startup   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Application Layer              │
│  Use Cases, DTOs, Validators        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       Domain Layer                  │
│  Entities, Value Objects, Events    │
└─────────────────────────────────────┘
              ↑
┌─────────────────────────────────────┐
│    Infrastructure Layer             │
│  EF Core, Kafka, Redis, etc.        │
└─────────────────────────────────────┘
```

### Documentación completa

- [arc42 Architecture](docs/architecture/arc42.md)
- [Architecture Decision Records](docs/adrs/)
- [API Documentation](http://localhost:8080/swagger)

## 🤝 Contribuir

¡Contribuciones son bienvenidas! Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre:

- Código de conducta
- Proceso de Pull Requests
- Estándares de código
- Convenciones de commits

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 📞 Contacto

- **Equipo**: Customer Team
- **Slack**: #customer-service
- **Email**: customer-team@talma.com

## 🔗 Links Útiles

- [Documentación Completa](https://docs.talma.com/customer-service)
- [Jira Board](https://talma.atlassian.net/browse/CUST)
- [Grafana Dashboard](https://grafana.talma.com/d/customer-service)
- [Runbooks](docs/runbooks/)

---

**Última actualización**: 2026-02-18
````

## Badges Recomendados

```markdown
<!-- Build Status -->

[![Build](https://github.com/{org}/{repo}/actions/workflows/build.yml/badge.svg)](https://github.com/{org}/{repo}/actions)

<!-- Test Coverage -->

[![Coverage](https://codecov.io/gh/{org}/{repo}/branch/main/graph/badge.svg)](https://codecov.io/gh/{org}/{repo})

<!-- License -->

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<!-- Version -->

[![Version](https://img.shields.io/github/v/release/{org}/{repo})](https://github.com/{org}/{repo}/releases)

<!-- Language -->

[![.NET](https://img.shields.io/badge/.NET-8.0-purple.svg)](https://dotnet.microsoft.com/)

<!-- Security -->

[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project={key}&metric=security_rating)](https://sonarcloud.io/dashboard?id={key})
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** incluir README.md en raíz de cada repositorio
- **MUST** incluir secciones: Descripción, Primeros Pasos, Uso, Pruebas
- **MUST** incluir badges de build status y coverage
- **MUST** mantener README actualizado con cambios significativos

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir video walkthroughs para setup inicial
- **SHOULD** incluir ejemplos de uso claros y ejecutables
- **SHOULD** incluir diagrama de arquitectura (C4 Level 1)
- **SHOULD** incluir sección de FAQ si hay preguntas frecuentes

### MAY (Opcional)

- **MAY** incluir sección de troubleshooting
- **MAY** incluir tabla de compatibilidad de versiones
- **MAY** incluir sección de changelog

### MUST NOT (Prohibido)

- **MUST NOT** incluir secretos o credentials en README
- **MUST NOT** documentar sin versionar en Git
- **MUST NOT** dejar README desactualizado (actualizar con cada release)

---

## Referencias

- [Make a README](https://www.makeareadme.com/)
- [Awesome README](https://github.com/matiassingers/awesome-readme)
- [Contributing Guide](./contributing-guide.md)
- [Guía de Onboarding](./onboarding-guide.md)

---

**Última actualización**: 18 de febrero de 2026
**Responsable**: Equipo de Arquitectura
