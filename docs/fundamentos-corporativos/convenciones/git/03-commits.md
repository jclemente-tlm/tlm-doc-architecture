---
id: commits
sidebar_position: 3
title: Commits - Conventional Commits
description: Convención de mensajes de commits siguiendo Conventional Commits
---

## 1. Principio

Los mensajes de commits deben ser claros, consistentes y semánticos para facilitar la lectura del historial, automatizar changelogs y habilitar versionado semántico automático.

## 2. Reglas

### Regla 1: Formato Conventional Commits

- **Formato**: `{tipo}({alcance}): {descripcion}`
- **Ejemplo correcto**: `feat(api): add user authentication endpoint`
- **Ejemplo incorrecto**: `Added new feature`, `fix bug`, `WIP`
- **Justificación**: Estándar de la industria, automatización de releases

### Regla 2: Tipos Obligatorios

| Tipo       | Uso                         | Impacto SemVer | Ejemplo                                   |
| ---------- | --------------------------- | -------------- | ----------------------------------------- |
| `feat`     | Nueva funcionalidad         | MINOR          | `feat(auth): add OAuth2 support`          |
| `fix`      | Corrección de bug           | PATCH          | `fix(api): handle null response`          |
| `docs`     | Solo documentación          | -              | `docs(readme): update installation steps` |
| `style`    | Formato (sin cambio lógica) | -              | `style(css): fix indentation`             |
| `refactor` | Refactor sin cambiar API    | -              | `refactor(service): simplify logic`       |
| `perf`     | Mejora de performance       | PATCH          | `perf(db): add index to users table`      |
| `test`     | Agregar/modificar tests     | -              | `test(user): add unit tests`              |
| `build`    | Build system, deps          | -              | `build(npm): update dependencies`         |
| `ci`       | CI/CD changes               | -              | `ci(github): add deploy workflow`         |
| `chore`    | Mantenimiento               | -              | `chore(deps): update eslint`              |

### Regla 3: Breaking Changes

- **Formato**: Agregar `!` después del tipo o incluir `BREAKING CHANGE:` en el body
- **Ejemplo**:

  ```
  feat(api)!: remove deprecated endpoints

  BREAKING CHANGE: Removed /v1/users endpoint, use /v2/users
  ```

- **Impacto SemVer**: MAJOR
- **Justificación**: Alerta de cambios incompatibles

### Regla 4: Estructura Completa (Header + Body + Footer)

```
{tipo}({alcance}): {descripcion corta}

[body opcional: explicación detallada]

[footer opcional: referencias a issues, breaking changes]
```

**Ejemplo completo**:

```
feat(payments): integrate Stripe payment gateway

- Add Stripe SDK dependency
- Implement payment webhook handler
- Add database migrations for transactions

Closes #123
Refs #456
```

### Regla 5: Descripción Clara

- **Imperativo presente**: `add` ✅, `added` ❌, `adds` ❌
- **Minúsculas**: `add feature` ✅, `Add Feature` ❌
- **Sin punto final**: `add login` ✅, `add login.` ❌
- **Máximo 72 caracteres**: Corto y específico

## 3. Tabla de Referencia Rápida

| Escenario               | Tipo       | Ejemplo                                     |
| ----------------------- | ---------- | ------------------------------------------- |
| Nueva API endpoint      | `feat`     | `feat(api): add GET /orders endpoint`       |
| Fix de bug              | `fix`      | `fix(auth): prevent token expiration`       |
| Actualizar README       | `docs`     | `docs: update deployment instructions`      |
| Refactor sin cambio API | `refactor` | `refactor(service): extract helper methods` |
| Breaking change         | `feat!`    | `feat(api)!: change response format`        |
| Actualizar dependencia  | `chore`    | `chore(deps): upgrade dotnet to 8.0`        |

## 4. Herramientas de Validación

### Commitlint (.NET/Node.js)

```bash
# Instalar commitlint
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# .commitlintrc.json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [2, "always", [
      "feat", "fix", "docs", "style", "refactor",
      "perf", "test", "build", "ci", "chore"
    ]],
    "subject-case": [2, "always", "lower-case"]
  }
}
```

### Husky Pre-commit Hook

```json
// package.json
{
  "husky": {
    "hooks": {
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  }
}
```

## 5. Excepciones

- **Merge commits**: Usar mensaje default de Git
- **Revert commits**: `revert: {commit original}`
- **Commits iniciales**: `chore: initial commit` aceptable

## 📖 Referencias

### Estándares relacionados

- [Versionado Semántico](./04-tags-releases.md)
- [Pull Requests](./05-pull-requests.md)

### Recursos externos

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Commitlint](https://commitlint.js.org/)
- [Semantic Release](https://semantic-release.gitbook.io/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
