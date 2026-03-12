---
id: onboarding-guide
sidebar_position: 5
title: Guías de Onboarding
description: Estándar para crear guías de onboarding que acorten el tiempo de ramp-up de nuevos miembros del equipo.
---

# Guías de Onboarding

## Contexto

Este estándar define cómo crear guías de onboarding para que nuevos desarrolladores se pongan productivos rápidamente. Complementa el lineamiento [Documentación Técnica](../../lineamientos/desarrollo/documentacion-tecnica.md).

---

## Stack Tecnológico

| Componente        | Tecnología | Versión | Uso                       |
| ----------------- | ---------- | ------- | ------------------------- |
| **Documentación** | Markdown   | -       | Formato del documento     |
| **Hosting**       | GitHub     | -       | Repositorio y acceso      |
| **Diagramas**     | Mermaid    | 10.0+   | Diagramas de arquitectura |
| **Colaboración**  | Slack      | -       | Comunicación del equipo   |

---

## ¿Qué es una Guía de Onboarding?

Documento paso a paso para que nuevos desarrolladores del equipo se pongan productivos rápidamente.

**Secciones típicas:**

1. **Bienvenida**: Introducción al equipo y proyecto
2. **Setup de ambiente**: Paso a paso para configurar máquina
3. **Arquitectura**: Overview técnico
4. **Workflows**: Cómo trabajamos día a día
5. **Herramientas**: Accesos y configuración
6. **Primeras tareas**: Tareas iniciales para aprender

**Propósito:** Acortar tiempo de ramp-up de nuevos miembros.

**Beneficios:**
✅ Onboarding más rápido
✅ Menos preguntas repetitivas
✅ Experiencia consistente
✅ Autonomía desde día 1

## Plantilla de Guía de Onboarding

````markdown
# Onboarding Guide - Customer Service Team

¡Bienvenido al equipo de Customer Service! 🎉

Esta guía te ayudará a estar productivo en tu primer día/semana.

## 📅 Timeline

### Día 1 (Bienvenida y Setup)

- ✅ Completar setup de ambiente
- ✅ Ejecutar proyecto localmente
- ✅ Reunión con equipo (intro)
- ✅ Configurar herramientas

### Semana 1 (Contexto)

- ✅ Leer documentación arquitectónica
- ✅ Code walkthrough con mentor
- ✅ Resolver primera tarea (bug fix pequeño)
- ✅ Participar en daily standups

### Mes 1 (Autonomía)

- ✅ Implementar feature pequeña
- ✅ Participar en code reviews
- ✅ Presentar demo en sprint review
- ✅ Contribuir a documentación

## 👥 Conoce al Equipo

### Customer Service Team

- **Tech Lead**: Juan Pérez (@juanp) - Arquitectura, decisiones técnicas
- **Senior Dev**: María García (@mariag) - Mentora, code reviews
- **Dev**: Carlos Ruiz (@carlosr) - Features, testing
- **QA**: Ana Torres (@anat) - Testing, quality assurance

### Contactos Clave

- **Product Owner**: Luis Mendoza (@luism)
- **Arquitecto**: Roberto Silva (@robertos)
- **DevOps**: Laura Jiménez (@lauraj)

## 🛠 Setup del Ambiente (Día 1)

### 1. Herramientas Requeridas

#### Instalar Software

```bash
# 1. .NET 8 SDK
# Descargar desde: https://dotnet.microsoft.com/download/dotnet/8.0
dotnet --version  # Verificar instalación

# 2. Git
# Descargar desde: https://git-scm.com/
git --version

# 3. Docker Desktop
# Descargar desde: https://www.docker.com/products/docker-desktop/
docker --version

# 4. IDE (elegir uno)
# - Visual Studio 2022: https://visualstudio.microsoft.com/
# - Rider: https://www.jetbrains.com/rider/
# - VS Code: https://code.visualstudio.com/
```
````

#### Extensiones Recomendadas (VS Code)

- C# (Microsoft)
- C# Dev Kit
- Docker
- GitLens
- REST Client
- Markdown All in One
- SonarLint

### 2. Accesos y Configuración

#### GitHub

```bash
# 1. Solicitar acceso a organización GitHub
# Contactar: @devops-team en Slack #it-support

# 2. Configurar SSH key
ssh-keygen -t ed25519 -C "tu.email@talma.com"
cat ~/.ssh/id_ed25519.pub  # Copiar y agregar a GitHub

# 3. Verificar acceso
git clone git@github.com:talma/customer-service.git
```

#### AWS

```bash
# 1. Solicitar acceso IAM
# Contactar: @devops-team en Slack #aws-access

# 2. Configurar AWS CLI
aws configure
# AWS Access Key ID: [tu-access-key]
# AWS Secret Access Key: [tu-secret-key]
# Default region: us-east-1
# Default output format: json

# 3. Verificar acceso
aws sts get-caller-identity
```

#### Keycloak

```bash
# 1. Solicitar cuenta en Keycloak
# Contactar: @security-team en Slack #identity-access

# 2. URL: https://keycloak.talma.com
# 3. Configurar MFA
```

#### Herramientas Adicionales

- **Jira**: https://talma.atlassian.net - Solicitar acceso a board CUST
- **Slack**: Canales: #customer-service, #tech-general, #deployments
- **Grafana**: https://grafana.talma.com - Dashboards de observabilidad
- **SonarQube**: https://sonar.talma.com - Quality gates

### 3. Clonar y Ejecutar Proyecto

```bash
# 1. Clonar repositorio
git clone git@github.com:talma/customer-service.git
cd customer-service

# 2. Configurar environment
cp .env.example .env
# Editar .env con valores de desarrollo (ver #customer-service-credentials en Slack)

# 3. Iniciar dependencias
docker-compose up -d

# 4. Aplicar migraciones
dotnet ef database update --project src/CustomerService.Infrastructure

# 5. Restaurar packages
dotnet restore

# 6. Ejecutar proyecto
dotnet run --project src/CustomerService.Api

# 7. Verificar
curl http://localhost:8080/health  # Debe retornar "Healthy"
open http://localhost:8080/swagger  # Swagger UI
```

### 4. Ejecutar Tests

```bash
# Unit tests
dotnet test --filter "Category=Unit"

# Integration tests (usa Testcontainers, puede tardar la primera vez)
dotnet test --filter "Category=Integration"

# Todos los tests con coverage
dotnet test /p:CollectCoverage=true
```

## 🏗 Arquitectura del Proyecto

### Overview

Customer Service es un microservicio que gestiona el ciclo de vida de clientes.

**Responsabilidades:**

- CRUD de clientes
- Validación de documentos
- Búsqueda y filtrado
- Publicación de eventos de ciclo de vida

**NO es responsable de:**

- Procesamiento de órdenes (Order Service)
- Notificaciones (Notification Service)
- Autenticación (Keycloak)

### Clean Architecture Layers

```
CustomerService/
├── CustomerService.Api/           # API Layer (Controllers, Middleware)
├── CustomerService.Application/   # Application Layer (Use Cases, DTOs)
├── CustomerService.Domain/        # Domain Layer (Entities, Business Rules)
└── CustomerService.Infrastructure/ # Infrastructure (DB, Kafka, Redis)
```

### Tecnologías Clave

- **.NET 8**: Framework
- **PostgreSQL 15**: Base de datos principal
- **Redis 7.2**: Cache
- **Apache Kafka 3.6**: Events
- **Entity Framework Core**: ORM
- **FluentValidation**: Validaciones
- **Polly**: Resilience patterns
- **Serilog + OpenTelemetry**: Observabilidad

### Documentación Completa

- [arc42 Architecture](docs/architecture/arc42.md)
- [ADRs](docs/adrs/)
- [C4 Diagrams](docs/c4-diagrams/)

## 🔄 Workflows Diarios

### Daily Standup

- **Cuándo**: Lunes a Viernes 9:00 AM
- **Dónde**: Slack Huddle en #customer-service
- **Duración**: 15 minutos
- **Formato**: ¿Qué hice ayer? ¿Qué haré hoy? ¿Impedimentos?

### Sprint Planning

- **Cuándo**: Lunes cada 2 semanas, 10:00 AM
- **Duración**: 2 horas
- **Artefactos**: Jira board, backlog refinado

### Sprint Review & Retro

- **Cuándo**: Viernes cada 2 semanas, 3:00 PM
- **Review**: Demo de features (30 min)
- **Retro**: Retrospectiva (30 min)

### Code Reviews

- **Todos los PRs requieren 1 aprobación** mínimo
- **SLA de review**: 24 horas
- **Cómo solicitar review**: Tag a @customer-team en PR

### Deployment

- **Dev**: Auto-deploy al hacer merge a main
- **Staging**: Auto-deploy al crear tag `v*-rc*`
- **Production**: Manual approval después de tag `v*`

## 📚 Recursos de Aprendizaje

### Internos (LEER PRIMERO)

- [ ] [README.md](README.md)
- [ ] [CONTRIBUTING.md](CONTRIBUTING.md)
- [ ] [arc42 Architecture](docs/architecture/arc42.md)
- [ ] [ADR-001 a ADR-010](docs/adrs/)
- [ ] [Runbooks](docs/runbooks/)

### Clean Architecture

- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Clean Architecture in .NET](https://www.youtube.com/watch?v=dK4Yb6-LxAk)

### Domain-Driven Design

- [DDD Fundamentals](https://www.pluralsight.com/courses/domain-driven-design-fundamentals)
- [Domain-Driven Design Distilled (Book)](https://www.amazon.com/Domain-Driven-Design-Distilled-Vaughn-Vernon/dp/0134434420)

### .NET y C#

- [.NET Documentation](https://docs.microsoft.com/en-us/dotnet/)
- [C# Language Reference](https://docs.microsoft.com/en-us/dotnet/csharp/)
- [ASP.NET Core Fundamentals](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/)

## ✅ Primeras Tareas

### Semana 1

#### Tarea 1: Bug Fix Pequeño (Día 2-3)

**Objetivo**: Familiarizarte con codebase y workflow.

```bash
# 1. Buscar issue con label "good-first-issue" en Jira
# Ejemplo: CUST-101 "Validación de formato de email no acepta + en email"

# 2. Crear branch
git checkout -b bugfix/CUST-101-fix-email-validation

# 3. Implementar fix
# Archivo: src/CustomerService.Domain/ValueObjects/Email.cs

# 4. Agregar test
# Archivo: tests/CustomerService.UnitTests/Domain/EmailTests.cs

# 5. Commit y PR
git commit -m "fix(domain): accept + character in email validation"
git push origin bugfix/CUST-101-fix-email-validation

# 6. Crear PR y solicitar review a @mentor
```

#### Tarea 2: Mejorar Documentación (Día 4)

**Objetivo**: Contribuir y familiarizarte con docs.

- Encuentra algo confuso en README o onboarding guide
- Propón mejora o agrega clarificación
- Crea PR con cambio

### Semana 2

#### Tarea 3: Feature Pequeña (Día 6-10)

**Objetivo**: Implementar feature end-to-end.

```bash
# Ejemplo: CUST-150 "Agregar campo middle_name a Customer"

# Pasos:
# 1. Agregar propiedad en Domain entity
# 2. Agregar columna en DB (migration)
# 3. Actualizar DTOs
# 4. Actualizar validadores
# 5. Tests (unit + integration)
# 6. Update API documentation
# 7. PR y review
```

## 🆘 ¿Bloqueado?

### Checklist de Troubleshooting

- [ ] ¿Leíste el README?
- [ ] ¿Buscaste en Slack?
- [ ] ¿Revisaste logs?
- [ ] ¿Consultaste documentación oficial?

### Pedir Ayuda

1. **Slack #customer-service**: Para preguntas generales del proyecto
2. **Tu mentor**: Para preguntas específicas de código
3. **#tech-general**: Para preguntas técnicas generales
4. **#help-desk**: Para problemas de accesos/permisos

### Office Hours

- **Mentor**: Martes y Jueves 2-3pm (disponible para pair programming)
- **Tech Lead**: Miércoles 10-11am (para preguntas arquitectónicas)

## 🎓 Certificaciones Opcionales

Si quieres profundizar:

- **Microsoft Certified: Azure Developer Associate**
- **AWS Certified Developer - Associate**
- **.NET Foundation Courses** (gratis)

## 📝 Feedback

Tu feedback sobre este onboarding es valioso:

- **Después de Semana 1**: Completar [encuesta de onboarding](link)
- **Después de Mes 1**: Reunión 1-on-1 con Tech Lead

---

**¡Bienvenido al equipo! 🚀**

Si tienes alguna pregunta, no dudes en preguntar en #customer-service.

```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** crear onboarding guide para equipos nuevos
- **MUST** incluir setup paso a paso del ambiente
- **MUST** incluir primeras tareas para nuevos miembros
- **MUST** actualizar basado en feedback de onboarding

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir timeline explícito (día 1, semana 1, mes 1)
- **SHOULD** incluir directorio del equipo con canales de contacto
- **SHOULD** incluir recursos de aprendizaje internos y externos
- **SHOULD** incluir checklist de setup verificable

### MAY (Opcional)

- **MAY** grabar sesiones de onboarding para asíncronos
- **MAY** incluir material de certificaciones opcionales
- **MAY** incluir encuesta de feedback al final

### MUST NOT (Prohibido)

- **MUST NOT** documentar sin versionar en Git
- **MUST NOT** incluir credenciales o secrets reales en el documento
- **MUST NOT** dejar el onboarding guide desactualizado más de 6 meses

---

## Referencias

- [README](./readme-standards.md)
- [Contributing Guide](./contributing-guide.md)
- [Runbooks](../operabilidad/runbooks.md)

---

**Última actualización**: 18 de febrero de 2026
**Responsable**: Equipo de Arquitectura
```
