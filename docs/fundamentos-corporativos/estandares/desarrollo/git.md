---
id: git
sidebar_position: 5
title: Git y Control de Versiones
description: Estándares de Git para repositorios, ramas, commits, tags y pull requests
---

# Estándar Técnico — Git y Control de Versiones

---

## 1. Propósito

Establecer convenciones consistentes para repositorios Git, branches, commits, tags y pull requests siguiendo Conventional Commits, Semantic Versioning y Git Flow.

---

## 2. Alcance

**Aplica a:**

- Todos los repositorios de código corporativo
- Microservicios, librerías, aplicaciones
- Documentación y configuración de infraestructura

**No aplica a:**

- Repositorios personales/experimentales (usar prefijo `tlm-exp-`)
- Forks temporales de proyectos externos

---

## 3. Tecnologías Aprobadas

| Componente          | Tecnología           | Versión mínima | Observaciones                      |
| ------------------- | -------------------- | -------------- | ---------------------------------- |
| **Control Versión** | Git                  | 2.30+          | Distributed VCS                    |
| **Hosting**         | GitHub Enterprise    | -              | Repositorios corporativos          |
| **Git Hooks**       | Husky.Net            | 0.6+           | Pre-commit/commit-msg hooks (.NET) |
| **Versionado**      | SemVer               | 2.0.0          | Semantic Versioning                |
| **Commits**         | Conventional Commits | 1.0.0          | Commit message convention          |

---

## 4. Requisitos Obligatorios 🔴

### Repositorios

- [ ] Prefijo corporativo `tlm-` en todos los repos
- [ ] Categoría clara: `svc`, `app`, `web`, `lib`, `infra`, `doc`, etc.
- [ ] Nombres descriptivos en kebab-case
- [ ] README.md completo con setup, uso y contribución

### Ramas

- [ ] Prefijos obligatorios: `feature/`, `bugfix/`, `hotfix/`, `release/`
- [ ] Nombres en kebab-case minúsculas
- [ ] Máximo 50 caracteres
- [ ] Ramas protegidas: `main`, `develop` (requieren PR)

### Commits

- [ ] Conventional Commits format: `{tipo}({alcance}): {descripcion}`
- [ ] Tipos válidos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`
- [ ] Imperativo presente: `add` (no `added`, `adds`)
- [ ] Máximo 72 caracteres en subject
- [ ] Breaking changes marcados con `!` o `BREAKING CHANGE:`

### Tags y Versioning

- [ ] Semantic Versioning: `v{MAJOR}.{MINOR}.{PATCH}`
- [ ] Tags anotados (no lightweight): `git tag -a v1.2.3 -m "..."`
- [ ] CHANGELOG.md actualizado en cada release

### Pull Requests

- [ ] Título sigue Conventional Commits
- [ ] Template completo (descripción, testing, checklist)
- [ ] Mínimo 1 approval requerido
- [ ] Tamaño recomendado: <400 líneas

---

## 5. Prohibiciones

- ❌ Repositorios sin prefijo `tlm-`
- ❌ Commits directos a `main` (usar PRs)
- ❌ Mensajes de commit genéricos: `"fix"`, `"update"`, `"WIP"`
- ❌ Tags sin anotación: `git tag v1.2.3`
- ❌ PRs sin reviewers
- ❌ Merge de PRs con CI fallando
- ❌ Secrets en código (usar `.gitignore`, variables de entorno)

---

## 6. Configuración Mínima

### Nomenclatura de Repositorios

**Formato**: `tlm-{categoria}-{nombre}[-{subtipo}]`

| Categoría | Descripción                 | Ejemplo                   |
| --------- | --------------------------- | ------------------------- |
| `svc`     | Microservicio backend       | `tlm-svc-orders`          |
| `app`     | Aplicación monolítica       | `tlm-app-erp`             |
| `web`     | Frontend web                | `tlm-web-portal-clientes` |
| `lib`     | Librería compartida         | `tlm-lib-logging`         |
| `infra`   | Infraestructura como código | `tlm-infra-terraform-aws` |
| `doc`     | Documentación               | `tlm-doc-architecture`    |
| `corp`    | Servicio corporativo        | `tlm-corp-notifications`  |

```bash
✅ Correcto:
tlm-svc-orders
tlm-web-backoffice
tlm-lib-common

❌ Incorrecto:
orders-service
tlm_api_users
TLM-Svc-Orders
```

### Nomenclatura de Ramas

**Formato**: `{tipo}/{descripcion}` o `{tipo}/{ticket-id}-{descripcion}`

| Tipo       | Uso                              | Ejemplo                       |
| ---------- | -------------------------------- | ----------------------------- |
| `main`     | Rama principal (producción)      | `main`                        |
| `develop`  | Integración continua (Gitflow)   | `develop`                     |
| `feature/` | Nueva funcionalidad              | `feature/payment-gateway`     |
| `bugfix/`  | Corrección de bug en develop     | `bugfix/fix-login-validation` |
| `hotfix/`  | Corrección urgente en producción | `hotfix/patch-security-cve`   |
| `release/` | Preparación de release           | `release/v1.2.0`              |
| `docs/`    | Solo documentación               | `docs/update-readme`          |

```bash
✅ Correcto:
feature/oauth-integration
bugfix/fix-date-parsing
hotfix/patch-sql-injection
feature/JIRA-123-user-login

❌ Incorrecto:
UserLogin
fix_bug
HOTFIX-123
```

### Conventional Commits

**Formato**: `{tipo}({alcance}): {descripcion}`

| Tipo       | Uso                         | Impacto SemVer | Ejemplo                                   |
| ---------- | --------------------------- | -------------- | ----------------------------------------- |
| `feat`     | Nueva funcionalidad         | MINOR          | `feat(auth): add OAuth2 support`          |
| `fix`      | Corrección de bug           | PATCH          | `fix(api): handle null response`          |
| `docs`     | Solo documentación          | -              | `docs(readme): update installation steps` |
| `style`    | Formato (sin cambio lógica) | -              | `style(css): fix indentation`             |
| `refactor` | Refactor sin cambiar API    | -              | `refactor(service): simplify logic`       |
| `perf`     | Mejora de performance       | PATCH          | `perf(db): add index to users table`      |
| `test`     | Agregar/modificar tests     | -              | `test(user): add unit tests`              |
| `build`    | Build system, deps          | -              | `build(deps): update NuGet packages`      |
| `ci`       | CI/CD changes               | -              | `ci(github): add deploy workflow`         |
| `chore`    | Mantenimiento               | -              | `chore(deps): update StyleCop`            |

**Breaking Changes**:

```bash
feat(api)!: remove deprecated endpoints

BREAKING CHANGE: Removed /v1/users endpoint, use /v2/users
```

**Estructura Completa**:

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

### Semantic Versioning

**Formato**: `v{MAJOR}.{MINOR}.{PATCH}[-{PRE-RELEASE}][+{BUILD}]`

| Cambio                             | Incrementar | Ejemplo             |
| ---------------------------------- | ----------- | ------------------- |
| **Breaking change** (incompatible) | MAJOR       | `v1.5.3` → `v2.0.0` |
| **Nueva feature** (compatible)     | MINOR       | `v1.5.3` → `v1.6.0` |

| **Bug fix** (compatible)           | PATCH       | `v1.5.3` → `v1.5.4` |

**Pre-releases**:

```bash
v2.0.0-alpha.1   # Versión alpha
v2.0.0-beta.2    # Versión beta

v2.0.0-rc.1      # Release candidate
```

**Crear tag**:

```bash
# Tag anotado (obligatorio)
git tag -a v1.2.3 -m "Release v1.2.3: Add payment gateway"

# Push tag a remoto
git push origin v1.2.3

# Crear release en GitHub
gh release create v1.2.3 --title "v1.2.3" --notes "Release notes..."
```

### Pull Request Template

Crear `.github/pull_request_template.md`:

```markdown
## 📝 Descripción

[Breve descripción de los cambios y su propósito]

## 🎯 Tipo de cambio

- [ ] 🐛 Bug fix
- [ ] ✨ Nueva feature
- [ ] 💥 Breaking change
- [ ] 📚 Documentación
- [ ] ♻️ Refactoring

## 🧪 Testing

- [ ] Tests unitarios agregados/actualizados
- [ ] Tests de integración agregados/actualizados
- [ ] Probado manualmente

**Detalles de testing**:
[Describe cómo probaste los cambios]

## 📋 Checklist

- [ ] El código sigue los estándares del proyecto
- [ ] He revisado mi propio código
- [ ] He agregado tests que validan los cambios
- [ ] Todos los tests pasan localmente
- [ ] He actualizado la documentación

## 🔗 Referencias

Closes #[issue_number]
```

### Git Hooks con Husky.Net

```bash
# Instalar Husky.Net
dotnet tool install --global Husky

# Inicializar en repositorio
cd /path/to/repo
husky install

# Crear hook commit-msg
cat > .husky/commit-msg << 'EOF'
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Validar Conventional Commits
commit_msg=$(cat "$1")
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?: .+"; then
  echo "❌ Commit inválido. Usar formato: type(scope): message"
  exit 1
fi
EOF
chmod +x .husky/commit-msg
```

---

## 7. Validación

### Validar Naming de Repositorios

```bash
# Regex validation
^tlm-[a-z]+-[a-z0-9-]+$

# Ejemplos válidos
tlm-svc-orders
tlm-web-portal-clientes
tlm-lib-logging

# Ejemplos inválidos
orders-service
tlm_api_users
TLM-Svc-Orders
```

### Validar Conventional Commits

```bash
# Git hook automático (ver sección Husky.Net)

# Validación manual con commitlint
npm install --save-dev @commitlint/cli @commitlint/config-conventional
echo "module.exports = {extends: ['@commitlint/config-conventional']}" > commitlint.config.js

# Validar commit message
echo "feat(api): add user endpoint" | npx commitlint
```

### Verificar Tags SemVer

```bash
# Listar tags
git tag -l

# Verificar formato
git tag -l | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$'

# Tags anotados (obligatorio)
git for-each-ref refs/tags
```

**Métricas de cumplimiento:**

| Métrica                    | Target | Verificación              |
| -------------------------- | ------ | ------------------------- |
| Repos con prefijo `tlm-`   | 100%   | Revisar nombres en GitHub |
| Commits Conventional       | >95%   | Git hook validation       |
| PRs con review             | 100%   | GitHub branch protection  |
| Tags SemVer                | 100%   | Regex validation          |
| Ramas con prefijo correcto | 100%   | Git hook validation       |

---

## 8. Referencias

- [C# y .NET](./csharp-dotnet.md) - Husky.Net integration
- [CI/CD Pipelines](../gobierno/cicd-pipelines.md) - Integración continua
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Husky.Net](https://github.com/alirezanet/Husky.Net)
- [Keep a Changelog](https://keepachangelog.com/)
