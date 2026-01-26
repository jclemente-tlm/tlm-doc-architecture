---
id: naming-ramas
sidebar_position: 2
title: Naming - Ramas
description: Convención de nomenclatura para ramas en Git
---

## 1. Principio

Las ramas deben identificar claramente su propósito (feature, fix, hotfix, release) y relacionarse con el trabajo a realizar.

## 2. Reglas

### Regla 1: Prefijo por Tipo de Rama

- **Formato**: `{tipo}/{descripcion}`
- **Ejemplo correcto**: `feature/user-login`, `bugfix/fix-null-pointer`, `hotfix/security-patch`
- **Ejemplo incorrecto**: `UserLogin`, `fix_bug`, `HOTFIX-123`
- **Justificación**: Claridad en el propósito de la rama

### Regla 2: Tipos Estándar de Ramas

| Tipo          | Uso                              | Ejemplo                       |
| ------------- | -------------------------------- | ----------------------------- |
| `main`        | Rama principal (producción)      | `main`                        |
| `develop`     | Integración continua (Gitflow)   | `develop`                     |
| `feature/`    | Nueva funcionalidad              | `feature/payment-gateway`     |
| `bugfix/`     | Corrección de bug en develop     | `bugfix/fix-login-validation` |
| `hotfix/`     | Corrección urgente en producción | `hotfix/patch-security-cve`   |
| `release/`    | Preparación de release           | `release/v1.2.0`              |
| `experiment/` | Prueba de concepto (PoC)         | `experiment/graphql-api`      |
| `docs/`       | Solo documentación               | `docs/update-readme`          |

### Regla 3: Formato de Descripción

- **Solo minúsculas**: `feature/user-login` ✅, `feature/UserLogin` ❌
- **Guiones medios (`-`)**: `feature/user-profile-edit` ✅, `feature/user_profile` ❌
- **Sin acentos**: `feature/autenticacion` ❌, `feature/authentication` ✅
- **Máximo 50 caracteres**: Corto y descriptivo

### Regla 4: Incluir Issue/Ticket ID (Opcional pero Recomendado)

- **Formato**: `{tipo}/{ticket-id}-{descripcion}`
- **Ejemplo correcto**: `feature/JIRA-123-user-login`, `bugfix/GH-456-fix-timeout`
- **Justificación**: Trazabilidad entre código y sistema de tickets

## 3. Tabla de Referencia Rápida

| Escenario           | Patrón                  | Ejemplo                         |
| ------------------- | ----------------------- | ------------------------------- |
| Nueva feature       | `feature/{descripcion}` | `feature/oauth-integration`     |
| Fix en desarrollo   | `bugfix/{descripcion}`  | `bugfix/fix-date-parsing`       |
| Fix urgente en prod | `hotfix/{descripcion}`  | `hotfix/patch-sql-injection`    |
| Preparar release    | `release/v{version}`    | `release/v2.1.0`                |
| Con ticket ID       | `feature/{id}-{desc}`   | `feature/TLM-789-notifications` |

## 4. Herramientas de Validación

- **Git Hooks**: Pre-push hook que valida naming con regex
- **GitHub Branch Protection**: Requiere patrón específico
- **Configuración**:

```bash
# .git/hooks/pre-push
#!/bin/bash
branch=$(git rev-parse --abbrev-ref HEAD)
pattern="^(feature|bugfix|hotfix|release|docs|experiment)/[a-z0-9-]+$"

if [[ ! $branch =~ $pattern ]] && [[ $branch != "main" ]] && [[ $branch != "develop" ]]; then
    echo "❌ Branch name '$branch' invalid. Use: {type}/{description}"
    exit 1
fi
```

## 5. Excepciones

- **Ramas protegidas**: `main`, `develop` no siguen patrón
- **Renovate/Dependabot**: Automáticamente creadas (ignorar validación)
- **Ramas personales temporales**: Usar prefijo `personal/{nombre}/`

## 📖 Referencias

### Estándares relacionados

- [Git Workflow](/docs/fundamentos-corporativos/lineamientos/desarrollo/gestion-codigo-fuente)

### Convenciones relacionadas

- [Commits](./03-commits.md)
- [Pull Requests](./05-pull-requests.md)

### Recursos externos

- [Git Branching Model](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
