# Convenciones Técnicas Talma

Las convenciones son **reglas específicas y verificables** sobre nomenclatura, formato, estructura y procesos que se aplican consistentemente en toda la organización.

## 📋 ¿Qué es una Convención?

Una convención define **CÓMO** escribir código, nombrar recursos, formatear archivos y estructurar proyectos:

- ✅ **Naming**: Cómo nombrar variables, clases, archivos, recursos
- ✅ **Formato**: Indentación, comillas, line length, import order
- ✅ **Estructura**: Organización de folders, proyectos, módulos
- ✅ **Proceso**: Git workflow, PR templates, code review
- ✅ **Datos**: Fechas (ISO 8601), moneda, paginación, eventos

## 🆚 Diferencia: Convención vs Estándar vs Lineamiento

| Nivel           | Propósito                   | Ejemplo                                            |
| --------------- | --------------------------- | -------------------------------------------------- |
| **Principio**   | Filosofía conceptual        | "Seguridad desde el Diseño"                        |
| **Lineamiento** | Directiva arquitectónica    | "Aplicar OWASP Top 10 en todas las APIs"           |
| **Estándar**    | Tecnología/Framework        | "Usar JWT con RS256, expiración 15min"             |
| **Convención**  | Regla sintáctica específica | "Tokens en header `Authorization: Bearer {token}`" |

---

## 📁 Estructura de Convenciones

### [Git](./git/) - Repositorios, Branches, Commits, PRs

Convenciones para control de versiones y colaboración:

1. **[Naming - Repositorios](./git/01-naming-repositorios.md)** - `tlm-svc-orders`, `tlm-app-erp`
2. **[Naming - Ramas](./git/02-naming-ramas.md)** - `feature/user-login`, `hotfix/security-patch`
3. **[Commits](./git/03-commits.md)** - Conventional Commits (`feat:`, `fix:`, `docs:`)
4. **[Tags y Releases](./git/04-tags-releases.md)** - Semantic Versioning (`v1.2.3`)
5. **[Pull Requests](./git/05-pull-requests.md)** - Templates, labels, review process

### [Código](./codigo/) - Naming y Formato de Código Fuente

Convenciones de nomenclatura por lenguaje:

1. **[Naming - C#](./codigo/01-naming-csharp.md)** - PascalCase clases, camelCase vars, `_private`, `IInterface`
2. **[Comentarios Código](./codigo/03-comentarios-codigo.md)** - XMLDoc, TODO/FIXME format
3. **[Estructura de Proyectos](./codigo/04-estructura-proyectos.md)** - Folder organization, layers, modules

### [APIs](./apis/) - REST Naming y Formatos

Convenciones para diseño de APIs REST:

1. **Naming - Endpoints** ⏭️ - `/api/v1/orders`, kebab-case, plurales
2. **Headers HTTP** ⏭️ - `X-Correlation-ID`, `X-Request-ID`, `X-Tenant-ID`
3. **Formato Respuestas** ⏭️ - RFC 7807 errors, pagination envelope
4. **Formato Fechas y Moneda** ⏭️ - ISO 8601, UTC, decimal precision

### [Infraestructura](./infraestructura/) - Cloud Resources

Convenciones para recursos cloud e infraestructura:

1. **Naming - AWS** ⏭️ - `tlm-{env}-{service}-{resource}`
2. **Tags y Metadatos** ⏭️ - Tags obligatorios (`Environment`, `Owner`, `CostCenter`)
3. **Variables de Entorno** ⏭️ - `TLM_DB_HOST`, prefijos, jerarquía

### [Base de Datos](./base-datos/) - Tablas, Columnas, Migraciones

Convenciones para objetos de base de datos:

1. **Naming - PostgreSQL** ⏭️ - `snake_case`, singular, `vw_`, `sp_`, `idx_`
2. **Naming - Migraciones** ⏭️ - `V{version}__{description}.sql`

### [Logs](./logs/) - Logging Estructurado

Convenciones para logs y trazabilidad:

1. **Niveles de Log** ⏭️ - Cuándo usar DEBUG/INFO/WARN/ERROR/FATAL
2. **Correlation IDs** ⏭️ - Propagación, formato UUID, headers

### [Seguridad](./seguridad/) - Manejo de Secretos

Convenciones de seguridad:

1. **Manejo de Secretos** ⏭️ - Never commit, `.env` patterns, scanning

---

## 🎯 Estado de Implementación

**Convenciones Completadas**: 20/20 (100%) ✅

### ✅ Completadas (MVP Fase 1)

- [x] **Git** (5/5): Repositorios, Ramas, Commits, Tags, Pull Requests
- [x] **Código** (3/3): Naming C#, Comentarios, Estructura proyectos
- [x] **APIs** (4/4): Endpoints, Headers HTTP, Respuestas, Fechas y Moneda
- [x] **Infraestructura** (3/3): Naming AWS, Tags y Metadatos, Variables de Entorno
- [x] **Base de Datos** (2/2): Naming PostgreSQL, Naming Migraciones
- [x] **Logs** (2/2): Niveles de Log, Correlation IDs
- [x] **Seguridad** (1/1): Manejo de Secretos

### ⏭️ Próximos Pasos (Fase 2 - Opcional)

- [ ] Testing: Naming tests, Coverage, Test data
- [ ] Mensajería: Kafka topics, Event schemas
- [ ] Documentación: README, CHANGELOG, ADRs
- [ ] CI/CD: Pipeline naming, Artifacts, Environments

---

## 📖 Cómo Usar estas Convenciones

### 1. Consulta Rápida

Usa la tabla de referencia en cada convención para consultas rápidas.

### 2. Validación Automática

Cada convención incluye sección de "Herramientas de Validación" con:

- Configuración de linters (StyleCop, Terraform fmt)
- Pre-commit hooks
- CI/CD checks

### 3. Onboarding

Nuevos desarrolladores deben leer convenciones de:

- C# y .NET (lenguaje principal)
- Git (commits, branches, PRs)
- Base de datos (si trabaja con BD)

---

## 🔧 Herramientas Recomendadas

| Categoría  | Herramienta        | Propósito                   |
| ---------- | ------------------ | --------------------------- |
| Git        | Husky.Net / Git Hooks | Validar mensajes de commits |
| Git        | Husky              | Pre-commit hooks            |
| C#         | StyleCop Analyzers | Naming conventions          |
| C#         | .editorconfig      | Formato código              |
| C#         | SonarQube          | Calidad y seguridad         |
| General    | EditorConfig       | Consistencia entre IDEs     |

---

## ❓ FAQ

### ¿Cuándo aplicar estas convenciones?

**Siempre** en:

- Código nuevo
- Refactorings mayores
- Nuevos proyectos

**Gradualmente** en:

- Código legacy (al modificarlo)

### ¿Qué pasa si violo una convención?

- **CI/CD**: Pipeline puede fallar si hay linters configurados
- **Code Review**: Reviewers lo señalarán
- **Consecuencia**: Retrasos en merge

### ¿Puedo proponer cambios a las convenciones?

Sí, mediante:

1. Crear issue explicando el cambio
2. Discutir con equipo de arquitectura
3. Actualizar convención si se aprueba

---

## 📚 Referencias

### Lineamientos Relacionados

- [Calidad de Código](/docs/fundamentos-corporativos/lineamientos/desarrollo/calidad-de-codigo)
- [Gestión de Código Fuente](/docs/fundamentos-corporativos/lineamientos/desarrollo/gestion-codigo-fuente)

### Estándares Relacionados

- [C# Clean Code](/docs/fundamentos-corporativos/estandares/codigo/csharp-dotnet)
- [APIs REST](/docs/fundamentos-corporativos/estandares/apis/)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura

---

## 🚀 Próximos Pasos

1. **Fase 1 (MVP)**: Completar 20 convenciones prioritarias
2. **Fase 2**: Agregar convenciones adicionales (Testing, Mensajería, Docs, CI/CD)
3. **Fase 3**: Automatización completa con linters y pipelines
4. **Fase 4**: Capacitación y adopción en todos los equipos
