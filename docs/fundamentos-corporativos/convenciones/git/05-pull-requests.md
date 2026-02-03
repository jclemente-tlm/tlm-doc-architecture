---
id: pull-requests
sidebar_position: 5
title: Pull Requests
description: Convención para títulos, descripciones y proceso de PRs
---

## 1. Principio

Los Pull Requests deben comunicar claramente qué cambios se proponen, por qué son necesarios y cómo han sido validados.

## 2. Reglas

### Regla 1: Título del PR

- **Formato**: Seguir Conventional Commits
- **Ejemplo correcto**: `feat(api): add user authentication endpoint`
- **Ejemplo incorrecto**: `Update code`, `PR for feature`, `WIP`
- **Justificación**: Consistencia con commits, automatización de releases

### Regla 2: Template de Descripción

Incluir las siguientes secciones:

```markdown
## 📝 Descripción

[Breve descripción de los cambios y su propósito]

## 🎯 Tipo de cambio

- [ ] 🐛 Bug fix (cambio que corrige un issue)
- [ ] ✨ Nueva feature (cambio que agrega funcionalidad)
- [ ] 💥 Breaking change (fix o feature que rompe compatibilidad)
- [ ] 📚 Documentación
- [ ] ♻️ Refactoring
- [ ] ⚡ Performance

## 🧪 Testing

- [ ] Tests unitarios agregados/actualizados
- [ ] Tests de integración agregados/actualizados
- [ ] Tests E2E agregados/actualizados (si aplica)
- [ ] Probado manualmente

**Detalles de testing**:
[Describe cómo probaste los cambios]

## 📸 Screenshots (si aplica)

[Capturas de pantalla para cambios UI]

## 📋 Checklist

- [ ] El código sigue los estándares del proyecto
- [ ] He revisado mi propio código
- [ ] He comentado código complejo si es necesario
- [ ] He actualizado la documentación
- [ ] Mis cambios no generan warnings nuevos
- [ ] He agregado tests que validan los cambios
- [ ] Todos los tests pasan localmente
- [ ] He actualizado el CHANGELOG (si aplica)

## 🔗 Referencias

Closes #[issue_number]
Refs #[related_issue]
```

### Regla 3: Tamaño del PR

- **Recomendado**: < 400 líneas cambiadas
- **Máximo**: < 800 líneas (si es mayor, dividir en PRs más pequeños)
- **Justificación**: PRs pequeños son más fáciles de revisar y menos propensos a bugs

### Regla 4: Labels Obligatorios

| Label              | Uso                   |
| ------------------ | --------------------- |
| `feature`          | Nueva funcionalidad   |
| `bugfix`           | Corrección de bug     |
| `hotfix`           | Corrección urgente    |
| `documentation`    | Solo docs             |
| `dependencies`     | Actualización de deps |
| `breaking-change`  | Cambio incompatible   |
| `needs-review`     | Requiere revisión     |
| `work-in-progress` | WIP, no merge         |

### Regla 5: Reviewers y Approvals

- **Mínimo 1 approval** requerido antes de merge
- **2 approvals** para breaking changes o cambios críticos
- **Code owner review** automático si configurado en `.github/CODEOWNERS`

## 3. Proceso de Review

### Checklist del Reviewer

- [ ] El código es claro y mantenible
- [ ] Tests cubren los cambios
- [ ] No hay código duplicado
- [ ] No hay hardcoded secrets o configuraciones
- [ ] Manejo de errores es apropiado
- [ ] Performance es aceptable
- [ ] Documentación está actualizada

### Comentarios Constructivos

- **Usar prefijos**:
  - `MUST:` - Cambio obligatorio
  - `SHOULD:` - Cambio recomendado
  - `NIT:` - Sugerencia menor (nitpick)
  - `QUESTION:` - Pregunta o clarificación

**Ejemplo**:

```
MUST: Agregar validación de null para evitar NullPointerException
SHOULD: Considerar extraer esta lógica a un método separado
NIT: Renombrar variable `x` a algo más descriptivo
QUESTION: ¿Por qué usamos este approach en vez de X?
```

## 4. Merge Strategies

### Squash Merge (Recomendado para feature branches)

- **Cuándo**: Features, bugfixes pequeños
- **Beneficio**: Historial limpio, un commit por feature
- **Commit message**: Usar título del PR

### Merge Commit (Para releases)

- **Cuándo**: Merge de `develop` a `main`, releases
- **Beneficio**: Preserva historial completo

### Rebase Merge (Para equipos avanzados)

- **Cuándo**: Preferencia del equipo, historial lineal
- **Riesgo**: Requiere disciplina, puede causar conflictos

## 5. Herramientas de Automatización

### GitHub PR Template

Crear `.github/pull_request_template.md`:

```markdown
## 📝 Descripción

## 🎯 Tipo de cambio

- [ ] 🐛 Bug fix
- [ ] ✨ Nueva feature

## 🧪 Testing

## 📋 Checklist

- [ ] Tests pasan
- [ ] Documentación actualizada
```

### Automatización de Reviews con GitHub Actions

```yaml
# .github/workflows/pr-validation.yml
name: PR Validation

on: pull_request

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # PR muy grande
      - name: Check PR size
        run: |
          CHANGES=$(git diff --stat origin/${{ github.base_ref }}...HEAD | tail -1 | awk '{print $4+$6}')
          if [ $CHANGES -gt 800 ]; then
            echo "::warning::PR muy grande ($CHANGES líneas). Considerar dividir en PRs más pequeños."
          fi
const hasChangelog = danger.git.modified_files.includes("CHANGELOG.md");
const isFeature = danger.github.pr.title.startsWith("feat");
if (isFeature && !hasChangelog) {
  warn("Considera actualizar el CHANGELOG para esta feature.");
}
```

## 📖 Referencias

### Estándares relacionados

- [Commits](./03-commits.md)
- [Code Review Guidelines](/docs/fundamentos-corporativos/lineamientos/desarrollo/code-review)

### Recursos externos

- [GitHub PR Best Practices](https://github.com/blog/1943-how-to-write-the-perfect-pull-request)
- [Google Code Review Guide](https://google.github.io/eng-practices/review/)
- [Danger.js](https://danger.systems/js/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
