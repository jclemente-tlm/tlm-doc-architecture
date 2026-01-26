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

### Regla 2: Proyectos TypeScript/Node.js - Modular

```
src/
├── modules/                           # Módulos de dominio
│   ├── users/
│   │   ├── dto/
│   │   │   ├── create-user.dto.ts
│   │   │   └── update-user.dto.ts
│   │   ├── entities/
│   │   │   └── user.entity.ts
│   │   ├── repositories/
│   │   │   └── user.repository.ts
│   │   ├── services/
│   │   │   └── user.service.ts
│   │   ├── controllers/
│   │   │   └── user.controller.ts
│   │   └── users.module.ts
│   └── orders/
│       └── ... (misma estructura)
├── common/                            # Código compartido
│   ├── decorators/
│   ├── filters/
│   ├── guards/
│   ├── interceptors/
│   ├── pipes/
│   └── middleware/
├── config/                            # Configuraciones
│   ├── database.config.ts
│   ├── app.config.ts
│   └── env.validation.ts
├── infrastructure/                    # Servicios de infraestructura
│   ├── database/
│   ├── messaging/
│   ├── cache/
│   └── logging/
├── shared/                            # Utilidades genéricas
│   ├── constants/
│   ├── types/
│   ├── utils/
│   └── interfaces/
├── app.module.ts
└── main.ts

tests/
├── unit/
│   └── modules/
│       └── users/
└── e2e/
    └── users.e2e-spec.ts
```

### Regla 3: Frontend React/Next.js

```
src/
├── app/                               # Next.js App Router
│   ├── (auth)/                        # Route groups
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/
│   │   ├── users/
│   │   └── orders/
│   ├── layout.tsx
│   └── page.tsx
├── components/                        # Componentes React
│   ├── ui/                            # Componentes base (botones, inputs)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── modal.tsx
│   ├── features/                      # Componentes de negocio
│   │   ├── user-list/
│   │   └── order-summary/
│   └── layout/                        # Header, Footer, Sidebar
├── hooks/                             # Custom hooks
│   ├── use-user.ts
│   └── use-debounce.ts
├── lib/                               # Utilidades y configuración
│   ├── api-client.ts
│   ├── utils.ts
│   └── validations.ts
├── services/                          # Llamadas a APIs
│   ├── user.service.ts
│   └── order.service.ts
├── store/                             # State management (Redux/Zustand)
│   ├── slices/
│   │   ├── user.slice.ts
│   │   └── order.slice.ts
│   └── store.ts
├── types/                             # TypeScript types
│   ├── user.types.ts
│   └── api.types.ts
└── styles/
    ├── globals.css
    └── themes/

public/
├── images/
├── fonts/
└── icons/
```

### Regla 4: Infraestructura (Terraform/IaC)

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
UserProfile.cs             # AutoMapper profile
```

### TypeScript

```
user.entity.ts             # Entidad
user.dto.ts                # DTO
user.interface.ts          # Interface
user.repository.ts         # Repository
user.service.ts            # Service
user.controller.ts         # Controller
user.module.ts             # Module
user.spec.ts               # Tests
```

## 5. Archivos de Configuración en Raíz

```
proyecto/
├── .editorconfig
├── .gitignore
├── .env.example
├── .eslintrc.json         # o .eslintrc.js
├── .prettierrc
├── tsconfig.json          # TypeScript
├── jest.config.js         # Testing
├── docker-compose.yml
├── Dockerfile
├── package.json
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

### ESLint Import Order (TypeScript)

```json
{
  "plugins": ["import"],
  "rules": {
    "import/order": [
      "error",
      {
        "groups": [
          "builtin", // Node.js built-ins
          "external", // npm packages
          "internal", // Internal modules
          ["parent", "sibling", "index"]
        ],
        "newlines-between": "always"
      }
    ]
  }
}
```

## 📖 Referencias

### Estándares relacionados

- [C# y .NET](/docs/fundamentos-corporativos/estandares/codigo/csharp-dotnet)
- [TypeScript](/docs/fundamentos-corporativos/estandares/codigo/typescript)

### Convenciones relacionadas

- [Naming C#](./01-naming-csharp.md)
- [Naming TypeScript](./02-naming-typescript.md)

### Recursos externos

- [Clean Architecture - Jason Taylor](https://github.com/jasontaylordev/CleanArchitecture)
- [NestJS Project Structure](https://docs.nestjs.com/first-steps)
- [Next.js Project Structure](https://nextjs.org/docs/getting-started/project-structure)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
