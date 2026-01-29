---
id: estructura-proyectos
sidebar_position: 4
title: Estructura de Proyectos
description: Convención para organizar carpetas y archivos en proyectos
---

## 1. Principio

La estructura de directorios debe ser consistente, predecible y seguir convenciones establecidas por la comunidad de cada tecnología para facilitar la navegación.

## 2. Reglas

### Regla 1: Proyectos .NET - Estructura por Capas

```
src/
├── TalmaApp.Api/                      # Capa de presentación (Web API)
│   ├── Controllers/
│   ├── Filters/
│   ├── Middleware/
│   ├── Models/                        # DTOs de request/response
│   ├── Program.cs
│   └── appsettings.json
├── TalmaApp.Application/              # Casos de uso / Lógica de aplicación
│   ├── UseCases/
│   │   ├── Users/
│   │   │   ├── CreateUser/
│   │   │   │   ├── CreateUserCommand.cs
│   │   │   │   ├── CreateUserHandler.cs
│   │   │   │   └── CreateUserValidator.cs
│   │   │   └── GetUser/
│   │   └── Orders/
│   ├── Common/
│   │   ├── Behaviors/                 # MediatR behaviors
│   │   ├── Interfaces/
│   │   └── Mappings/
│   └── DependencyInjection.cs
├── TalmaApp.Domain/                   # Entidades de dominio
│   ├── Entities/
│   │   ├── User.cs
│   │   └── Order.cs
│   ├── ValueObjects/
│   ├── Enums/
│   ├── Events/
│   └── Exceptions/
├── TalmaApp.Infrastructure/           # Implementaciones concretas
│   ├── Persistence/
│   │   ├── ApplicationDbContext.cs
│   │   ├── Configurations/
│   │   └── Repositories/
│   ├── Services/
│   ├── ExternalApis/
│   └── DependencyInjection.cs
└── TalmaApp.Shared/                   # Compartido entre capas
    ├── Constants/
    ├── Extensions/
    └── Helpers/

tests/
├── TalmaApp.UnitTests/
├── TalmaApp.IntegrationTests/
└── TalmaApp.ArchitectureTests/
```

### Regla 2: Infraestructura (Terraform/IaC)

```
infrastructure/
├── modules/                           # Módulos reutilizables
│   ├── networking/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/
│   └── database/
├── environments/                      # Por ambiente
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── prod/
├── scripts/                           # Scripts de deployment
│   ├── deploy.sh
│   └── destroy.sh
└── docs/
    └── architecture.md
```

## 3. Reglas Generales de Organización

### Regla A: Un Concepto, Una Carpeta

```
✅ Correcto:
src/
├── users/
│   ├── user.controller.ts
│   ├── user.service.ts
│   ├── user.repository.ts
│   └── user.entity.ts

❌ Incorrecto (mezclado):
src/
├── controllers/
│   ├── user.controller.ts
│   └── order.controller.ts
├── services/
│   ├── user.service.ts
│   └── order.service.ts
```

### Regla B: Máximo 7 Archivos por Carpeta

Si una carpeta tiene >7 archivos, considerar subdividir:

```
✅ Subdividir:
src/users/
├── dto/
├── entities/
├── services/
└── repositories/

❌ Muchos archivos sueltos:
src/users/
├── create-user.dto.ts
├── update-user.dto.ts
├── user.entity.ts
├── user-profile.entity.ts
├── user.service.ts
├── user-auth.service.ts
├── user.repository.ts
└── ... (10+ archivos)
```

### Regla C: Nomenclatura de Carpetas

- **kebab-case**: `user-management/`, `order-processing/`
- **Singular vs Plural**:
  - Plural para colecciones: `users/`, `orders/`, `components/`
  - Singular para conceptos: `config/`, `shared/`, `infrastructure/`

## 4. Patrones de Archivos

### .NET

```
User.cs                    # Entidad
UserDto.cs                 # DTO
IUserRepository.cs         # Interfaz
UserRepository.cs          # Implementación
UserService.cs             # Servicio
CreateUserCommand.cs       # Comando CQRS
UserProfile.cs             # Mapster profile
```

## 5. Archivos de Configuración en Raíz

```
proyecto/
├── .editorconfig
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── README.md
└── CHANGELOG.md
```

## 6. Carpeta `docs/`

```
docs/
├── README.md              # Overview del proyecto
├── api/
│   └── openapi.yaml
├── architecture/
│   ├── c4-diagrams.md
│   └── adrs/
│       ├── 001-framework-selection.md
│       └── 002-database-choice.md
├── development/
│   ├── setup.md
│   ├── coding-standards.md
│   └── testing.md
└── deployment/
    ├── ci-cd.md
    └── environments.md
```

## 7. Herramientas de Validación

### Arquitectura Tests (.NET)

```csharp
[Fact]
public void Domain_ShouldNotDependOn_Infrastructure()
{
    var result = Types.InAssembly(DomainAssembly)
        .Should()
        .NotHaveDependencyOn("TalmaApp.Infrastructure")
        .GetResult();

    result.IsSuccessful.Should().BeTrue();
}
```

### EditorConfig para Consistencia

```ini
# .editorconfig
root = true

[*]
charset = utf-8
insert_final_newline = true
trim_trailing_whitespace = true

[*.cs]
indent_style = space
indent_size = 4

[*.{json,yml,yaml}]
indent_style = space
indent_size = 2
```

## 📖 Referencias

### Estándares relacionados

- [C# y .NET](/docs/fundamentos-corporativos/estandares/codigo/csharp-dotnet)
- [Infraestructura como Código](/docs/fundamentos-corporativos/estandares/infraestructura/infraestructura-como-codigo)

### Convenciones relacionadas

- [Naming C#](./01-naming-csharp.md)
- [Naming Endpoints](/docs/fundamentos-corporativos/convenciones/apis/01-naming-endpoints)

### Recursos externos

- [Clean Architecture - Jason Taylor](https://github.com/jasontaylordev/CleanArchitecture)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
