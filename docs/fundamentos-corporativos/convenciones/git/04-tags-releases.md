---
id: tags-releases
sidebar_position: 4
title: Tags y Releases - Semantic Versioning
description: Convención de versionado siguiendo SemVer para tags y releases
---

## 1. Principio

Las versiones deben comunicar claramente el tipo y alcance de cambios en cada release, facilitando la gestión de dependencias y la compatibilidad.

## 2. Reglas

### Regla 1: Formato Semantic Versioning (SemVer)

- **Formato**: `v{MAJOR}.{MINOR}.{PATCH}[-{PRE-RELEASE}][+{BUILD}]`
- **Ejemplo correcto**: `v1.2.3`, `v2.0.0-beta.1`, `v1.5.0+build.123`
- **Ejemplo incorrecto**: `1.2`, `version-1.2.3`, `v1.2.3.4`
- **Justificación**: Estándar universal para versionado semántico

### Regla 2: Incremento de Versiones

| Cambio                             | Incrementar | Ejemplo             |
| ---------------------------------- | ----------- | ------------------- |
| **Breaking change** (incompatible) | MAJOR       | `v1.5.3` → `v2.0.0` |
| **Nueva feature** (compatible)     | MINOR       | `v1.5.3` → `v1.6.0` |
| **Bug fix** (compatible)           | PATCH       | `v1.5.3` → `v1.5.4` |

- **MAJOR (X.0.0)**: Cambios incompatibles con API anterior
- **MINOR (1.X.0)**: Nueva funcionalidad, retrocompatible
- **PATCH (1.5.X)**: Correcciones de bugs, retrocompatible

### Regla 3: Pre-releases

- **Formato**: `v{MAJOR}.{MINOR}.{PATCH}-{identificador}.{numero}`
- **Ejemplos**:
  - `v2.0.0-alpha.1` - Versión alpha
  - `v2.0.0-beta.2` - Versión beta
  - `v2.0.0-rc.1` - Release candidate
- **Uso**: Testing antes de release estable
- **Orden**: `alpha` < `beta` < `rc` < `{release}`

### Regla 4: Build Metadata

- **Formato**: `v{version}+{metadata}`
- **Ejemplo**: `v1.2.3+build.456`, `v2.0.0+20260126.abc123`
- **Uso**: Información de build (CI job ID, commit hash)
- **Nota**: No afecta precedencia de versiones

### Regla 5: Versión Inicial

- **Desarrollo**: `v0.X.Y` - API inestable, puede cambiar
- **Primera release pública**: `v1.0.0`
- **Convención**: Iniciar en `v0.1.0` para desarrollo

## 3. Tabla de Referencia Rápida

| Escenario                | Acción      | Ejemplo             |
| ------------------------ | ----------- | ------------------- |
| Nuevo proyecto           | Iniciar     | `v0.1.0`            |
| Primera release pública  | MAJOR       | `v1.0.0`            |
| Nueva feature compatible | MINOR       | `v1.0.0` → `v1.1.0` |
| Bug fix                  | PATCH       | `v1.1.0` → `v1.1.1` |
| Breaking change          | MAJOR       | `v1.5.3` → `v2.0.0` |
| Beta testing             | Pre-release | `v2.0.0-beta.1`     |
| Build CI/CD              | Metadata    | `v1.2.3+build.789`  |

## 4. Herramientas de Automatización

### Semantic Release (Recomendado)

Genera versiones automáticamente desde commits:

```json
// package.json
{
  "scripts": {
    "semantic-release": "semantic-release"
  },
  "release": {
    "branches": ["main"],
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      "@semantic-release/changelog",
      "@semantic-release/github"
    ]
  }
}
```

### GitVersion (.NET)

```yaml
# GitVersion.yml
mode: Mainline
branches:
  main:
    tag: ""
  develop:
    tag: alpha
  feature:
    tag: feat
  release:
    tag: rc
```

### Manual Tagging

```bash
# Crear tag localmente
git tag -a v1.2.3 -m "Release v1.2.3: Add payment gateway"

# Push tag a remoto
git push origin v1.2.3

# Crear release en GitHub
gh release create v1.2.3 --title "v1.2.3" --notes "Release notes..."
```

## 5. CHANGELOG

Mantener archivo `CHANGELOG.md` con formato [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

## [1.2.0] - 2026-01-26

### Added

- New payment gateway integration
- User profile API endpoints

### Changed

- Improved error handling in auth service

### Fixed

- Null pointer exception in order processing

### Security

- Updated dependencies to fix CVE-2026-12345
```

## 6. Excepciones

- **Monorepos**: Usar independent versioning o fixed versioning según necesidad
- **Librerías internas**: Puede usar `0.X.Y` indefinidamente si solo uso interno
- **Prototipos**: Usar prefijo `v0.0.X-experimental`

## 📖 Referencias

### Estándares relacionados

- [Commits - Conventional Commits](./03-commits.md)

### Convenciones relacionadas

- [Pull Requests](./05-pull-requests.md)

### Recursos externos

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Release](https://semantic-release.gitbook.io/)
- [GitVersion](https://gitversion.net/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
