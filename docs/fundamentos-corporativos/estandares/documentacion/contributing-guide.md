---
id: contributing-guide
sidebar_position: 4
title: Guía de Contribución
description: Estándar para crear guías de contribución (CONTRIBUTING.md) con workflow, estándares de código y convenciones de commits.
---

# Guía de Contribución

## Contexto

Este estándar define cómo crear CONTRIBUTING.md para repositorios, estableciendo un proceso claro para contribuciones internas y externas consistentes. Complementa el lineamiento [Documentación Técnica](../../lineamientos/desarrollo/documentacion-tecnica.md).

---

## Stack Tecnológico

| Componente        | Tecnología           | Versión | Uso                         |
| ----------------- | -------------------- | ------- | --------------------------- |
| **Documentación** | Markdown             | -       | Formato del documento       |
| **Commits**       | Conventional Commits | 1.0+    | Formato estándar de commits |
| **Linting**       | markdownlint         | -       | Validación de markdown      |
| **CI/CD**         | GitHub Actions       | -       | Automatización de checks    |

---

## ¿Qué es un Contributing Guide?

Documento que explica cómo contribuir al proyecto, incluyendo workflow, estándares y convenciones.

**Secciones típicas:**

1. **Código de Conducta**: Comportamiento esperado
2. **Cómo contribuir**: Proceso general
3. **Reportar bugs**: Template de bug reports
4. **Solicitar features**: Template de feature requests
5. **Pull Requests**: Proceso de PRs
6. **Estándares de código**: Convenciones
7. **Pruebas**: Requisitos de tests
8. **Commits**: Conventional commits

**Propósito:** Facilitar contribuciones externas e internas consistentes.

**Beneficios:**
✅ Contribuciones consistentes
✅ Menos fricción para contribuir
✅ Calidad mantenida
✅ Proceso claro

## Plantilla CONTRIBUTING.md

````markdown
# Contributing to Customer Service

¡Gracias por considerar contribuir a Customer Service! 🎉

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Puedo Contribuir](#cómo-puedo-contribuir)
- [Proceso de Development](#proceso-de-development)
- [Pull Requests](#pull-requests)
- [Estándares de Código](#estándares-de-código)
- [Guía de Pruebas](#guía-de-pruebas)
- [Convenciones de Commits](#convenciones-de-commits)

## 📜 Código de Conducta

Este proyecto adhiere al [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Al participar, se espera que mantengas este código.

### Resumen

- **Sé respetuoso**: Trata a todos con respeto
- **Sé colaborativo**: Trabaja constructivamente con otros
- **Sé inclusivo**: Da la bienvenida a diferentes perspectivas
- **Reporta problemas**: Si ves comportamiento inapropiado, repórtalo

## 🤔 Cómo Puedo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor crea un issue con:

**Template de Bug Report:**

```markdown
**Descripción del Bug**
Descripción clara y concisa del bug.

**Pasos para Reproducir**

1. Ir a '...'
2. Hacer click en '...'
3. Ver error

**Comportamiento Esperado**
Qué esperabas que sucediera.

**Screenshots**
Si aplica, agrega screenshots.

**Ambiente**

- OS: [ej. Windows 11]
- .NET Version: [ej. 8.0.2]
- Version: [ej. 1.2.3]

**Contexto Adicional**
Cualquier otra información relevante.
```

### Solicitar Features

Para nuevas features, crea un issue con:

**Template de Feature Request:**

```markdown
**¿Tu feature request está relacionada con un problema?**
Descripción clara del problema. Ej. "Siempre me frustra cuando [...]"

**Describe la solución que te gustaría**
Descripción clara y concisa de lo que quieres que suceda.

**Describe alternativas que consideraste**
Descripción de soluciones o features alternativas.

**Contexto adicional**
Screenshots, mockups, o información adicional.
```

## 🔨 Proceso de Development

### 1. Setup del Ambiente

```bash
# Fork el repositorio (si eres externo)
# Clonar
git clone https://github.com/talma/customer-service.git
cd customer-service

# Instalar dependencias
dotnet restore

# Configurar environment
cp .env.example .env

# Iniciar dependencias
docker-compose up -d

# Aplicar migraciones
dotnet ef database update
```

### 2. Crear Feature Branch

```bash
# Desde main actualizado
git checkout main
git pull origin main

# Crear branch con naming convention
git checkout -b feature/JIRA-123-add-email-validation
```

### 3. Desarrollar

- Escribe código siguiendo [estándares](#estándares-de-código)
- Agrega tests (coverage > 80%)
- Ejecuta tests localmente
- Commit con [conventional commits](#convenciones-de-commits)

### 4. Push y PR

```bash
# Push a tu fork/branch
git push origin feature/JIRA-123-add-email-validation

# Crear Pull Request en GitHub
# Completar template de PR
```

## 🔄 Pull Requests

### Checklist antes de enviar PR

- [ ] Mi código sigue el estilo del proyecto
- [ ] He realizado self-review de mi código
- [ ] He comentado código complejo si es necesario
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan nuevos warnings
- [ ] He agregado tests que validan mi fix/feature
- [ ] Tests nuevos y existentes pasan localmente
- [ ] He verificado que no hay secretos expuestos
- [ ] He seguido conventional commits
- [ ] He actualizado CHANGELOG.md (si aplica)

### Template de Pull Request

```markdown
## Descripción

Descripción clara de los cambios realizados.

## Tipo de cambio

- [ ] Bug fix (cambio que corrige un issue)
- [ ] New feature (cambio que agrega funcionalidad)
- [ ] Breaking change (fix o feature que causa que funcionalidad existente no funcione como esperado)
- [ ] Documentation update

## Referencias

- Fixes: JIRA-123
- Related: JIRA-456

## ¿Cómo se ha testeado?

Descripción de tests ejecutados.

## Screenshots (si aplica)

Para cambios de UI.

## Checklist

- [ ] Tests pass localmente
- [ ] Code coverage > 80%
- [ ] Documentation updated
- [ ] Self-reviewed
```

### Proceso de Review

1. **Automated Checks**: CI/CD ejecuta builds, tests, security scans
2. **Code Review**: Al menos 1 aprobación requerida
3. **Address Comments**: Resolver todos los comentarios
4. **Merge**: Squash and merge (generalmente)

## 💻 Estándares de Código

### Naming Conventions

```csharp
// Clases: PascalCase
public class CustomerService { }

// Interfaces: I + PascalCase
public interface ICustomerRepository { }

// Métodos: PascalCase, async → Async suffix
public async Task<Customer> GetCustomerAsync(Guid id) { }

// Properties: PascalCase
public string Name { get; set; }

// Private fields: _camelCase
private readonly ILogger _logger;

// Constants: PascalCase
private const int MaxRetries = 3;

// Local variables y parameters: camelCase
var customerId = Guid.NewGuid();
public void ProcessCustomer(string customerId) { }
```

### Code Style

- **Indentación**: 4 espacios
- **Llaves**: Estilo C# (nueva línea)
- **Line length**: Max 120 caracteres
- **Using directives**: Fuera de namespace, ordenados alfabéticamente
- **var**: Usar cuando tipo es obvio
- **Nullable**: Habilitar nullable reference types

### EditorConfig

El proyecto incluye `.editorconfig` que enforcea estilo automáticamente.

```bash
# Verificar formato
dotnet format --verify-no-changes

# Auto-formatear
dotnet format
```

## 🧪 Guía de Pruebas

### Coverage Mínimo

- **Línea coverage**: > 80%
- **Branch coverage**: > 75%
- **Unit tests**: Para toda lógica de negocio
- **Integration tests**: Para repositorios y external calls

### Estructura de Tests

```csharp
// Naming: [Method]_[Scenario]_[ExpectedResult]
[Fact]
public void CreateCustomer_WithValidData_ReturnsCustomer()
{
    // Arrange
    var request = new CreateCustomerRequest
    {
        Name = "John Doe",
        Email = "john@example.com"
    };

    // Act
    var result = _useCase.Execute(request);

    // Assert
    result.Should().NotBeNull();
    result.Name.Should().Be("John Doe");
}
```

### Herramientas de Prueba

- **xUnit**: Framework de testing
- **Moq**: Mocking
- **FluentAssertions**: Assertions legibles
- **Testcontainers**: Integration tests con PostgreSQL real

### Ejecutar Tests

```bash
# Todos los tests
dotnet test

# Solo unit tests
dotnet test --filter "Category=Unit"

# Con coverage
dotnet test /p:CollectCoverage=true /p:CoverletOutputFormat=opencover
```

## 📝 Convenciones de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/).

### Formato

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Tipos

- **feat**: Nueva funcionalidad
- **fix**: Bug fix
- **docs**: Solo cambios en documentación
- **style**: Formato (espacios, puntos y coma, etc.)
- **refactor**: Refactorización sin cambio funcional
- **perf**: Mejora de performance
- **test**: Agregar o modificar tests
- **chore**: Mantenimiento (dependencies, build, etc.)
- **ci**: Cambios en CI/CD

### Ejemplos

```bash
# Feature simple
git commit -m "feat(customer): add email validation"

# Bug fix con detalles
git commit -m "fix(customer): prevent duplicate email registration

- Add unique constraint on email column
- Add proper error handling
- Add test for duplicate email scenario

Fixes: JIRA-456"

# Breaking change
git commit -m "feat!(api): change customer response format

BREAKING CHANGE: Customer API response now includes nested address object
instead of flat structure. Clients must update to handle new format.

Refs: JIRA-789"
```

## 🎯 Revisión de PRs

### Como Reviewer

- **Sé constructivo**: Sugerencias, no órdenes
- **Explica el "por qué"**: No solo qué cambiar, sino por qué
- **Reconoce buen trabajo**: Comenta aspectos positivos
- **Aprueba cuando esté listo**: No busques perfección

### Como Author

- **Responde a comentarios**: Aclara o implementa sugerencias
- **No te lo tomes personal**: Feedback es sobre código, no sobre ti
- **Haz preguntas**: Si no entiendes un comentario, pregunta

## 🆘 ¿Necesitas Ayuda?

- **Slack**: #customer-service
- **Email**: customer-team@talma.com
- **Office Hours**: Martes 3-4pm con arquitecto

## 📚 Referencias

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [.NET Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

¡Gracias por contribuir! 🚀
````

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** incluir CONTRIBUTING.md en repositorios open source o con múltiples contribuidores
- **MUST** incluir proceso de PR y code review
- **MUST** incluir convenciones de código y commits
- **MUST** incluir cómo reportar bugs y solicitar features

### SHOULD (Fuertemente recomendado)

- **SHOULD** incluir templates de bug report y feature request
- **SHOULD** incluir checklist de PR explícito
- **SHOULD** incluir proceso de setup inicial del ambiente
- **SHOULD** incluir requisitos mínimos de coverage

### MAY (Opcional)

- **MAY** incluir guía de pair programming
- **MAY** incluir proceso de office hours con el equipo
- **MAY** incluir política de branches más detallada

### MUST NOT (Prohibido)

- **MUST NOT** documentar sin versionar en Git
- **MUST NOT** incluir credenciales o secretos en CONTRIBUTING.md
- **MUST NOT** omitir el proceso de PR y code review

---

## Referencias

- [GitHub Docs - Setting guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors)
- [Contributor Covenant](https://www.contributor-covenant.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [README](./readme-standards.md)
- [Guía de Onboarding](./onboarding-guide.md)

---

**Última actualización**: 18 de febrero de 2026
**Responsable**: Equipo de Arquitectura
