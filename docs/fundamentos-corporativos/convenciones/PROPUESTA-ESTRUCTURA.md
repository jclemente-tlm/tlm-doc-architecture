# Análisis: Estructura Propuesta de Convenciones

## 🎯 Diferencia entre Estándares y Convenciones

### **Estándares**

- Definen **QUÉ** tecnología usar y **CÓMO** implementarla
- Ejemplos: "Usar xUnit para testing", "Usar Terraform para IaC", "Usar Serilog para logging"
- Incluyen ejemplos de código completos
- Nivel: Tecnología/Framework específico

### **Convenciones**

- Definen **FORMATOS** y **NOMBRES** específicos y concretos
- Ejemplos: "Variables en camelCase", "Archivos en kebab-case", "Commits con Conventional Commits"
- Reglas sintácticas y de formato
- Nivel: Sintaxis/Naming/Formato

---

## 📊 Estructura Actual (9 archivos)

### **nombres/** (4 archivos)

1. `01-repositorios.md` - Naming de repos GitHub (tlm-svc-orders)
2. `02-ramas.md` - Naming de branches (feature/_, hotfix/_)
3. `03-archivos-y-carpetas.md` - Naming de files y folders
4. `04-objetos-base-datos.md` - Naming de tablas, columnas, vistas, procedures

### **estrategia-de-ramas/** (5 archivos)

1. `01-gitflow.md` - GitFlow branching strategy
2. `02-trunk-based.md` - Trunk-based development
3. `03-feature-hotfix-release.md` - Feature branches, hotfix, release
4. `04-convenciones-commits.md` - Conventional Commits
5. `05-versionado-semantico.md` - Semantic Versioning (SemVer)

---

## ❌ Problemas Identificados

### 1. **Solapamiento con Estándares**

- Naming de objetos de BD ya está en estándar SQL
- Estrategias de ramas podría estar en lineamiento de versionado

### 2. **Faltan Convenciones Críticas**

- **Código**: Naming de variables, clases, funciones por lenguaje
- **APIs**: Naming de endpoints, parámetros, headers
- **Infraestructura**: Naming de recursos AWS/Azure
- **Testing**: Naming de tests, fixtures, mocks
- **Documentación**: Formato de ADRs, READMEs

### 3. **Inconsistencias**

- Algunos archivos muy básicos (40 líneas)
- Otros muy detallados (150+ líneas)
- Falta estructura uniforme

---

## ✅ Propuesta de Estructura Óptima

### **Principio de Diseño**

> Las convenciones deben ser **REGLAS ESPECÍFICAS Y VERIFICABLES** (sintaxis, formato, estructura, proceso) que se aplican consistentemente en toda la organización.

### **Tipos de Convenciones (más allá de naming)**

1. **Naming** - Cómo nombrar cosas (variables, archivos, recursos)
2. **Formato/Estilo** - Indentación, comillas, line length, import order
3. **Estructura** - Organización de proyectos, folders, módulos
4. **Comentarios** - JSDoc, XMLDoc, TODO/FIXME patterns
5. **Proceso** - Git workflow, PR templates, code review
6. **Configuración** - Environment variables, feature flags, settings
7. **Seguridad** - Secret handling, headers, dependency updates
8. **Datos** - Fechas (ISO 8601), moneda, paginación, i18n

---

## 📁 Estructura Propuesta Completa

```
convenciones/
├── README.md                           # Índice general con tipos de convenciones
│
├── codigo/                             # Código fuente (naming + formato)
│   ├── _category_.json
│   ├── 01-naming-csharp.md            # PascalCase clases, camelCase vars, IInterface
│   ├── 02-naming-typescript.md        # camelCase, PascalCase, prefijos I/T
│   ├── 03-naming-python.md            # snake_case, PEP 8
│   ├── 04-formato-csharp.md           # Indentación 4 spaces, braces, using order
│   ├── 05-formato-typescript.md       # 2 spaces, single quotes, semicolons
│   ├── 06-comentarios-codigo.md       # JSDoc, XMLDoc, TODO/FIXME format
│   └── 07-estructura-proyectos.md     # Folder structure, layers, modules
│
├── apis/                               # APIs REST (naming + formato)
│   ├── _category_.json
│   ├── 01-naming-endpoints.md         # /api/v1/orders, kebab-case, plurales
│   ├── 02-naming-parametros.md        # ?pageSize=20, camelCase query params
│   ├── 03-headers-http.md             # X-Correlation-ID, X-Request-ID, X-Tenant-ID
│   ├── 04-formato-respuestas.md       # RFC 7807 errors, pagination envelope
│   ├── 05-formato-fechas.md           # ISO 8601, UTC timezone
│   └── 06-formato-moneda.md           # Decimal precision, currency codes
│
├── infraestructura/                    # Cloud/Infra (naming + config)
│   ├── _category_.json
│   ├── 01-naming-aws.md               # tlm-{env}-{service}-{resource}
│   ├── 02-naming-azure.md             # rg-tlm-prod-eastus pattern
│   ├── 03-naming-terraform.md         # var.*, module.*, output.*
│   ├── 04-naming-docker.md            # image tags, container names, labels
│   ├── 05-naming-kubernetes.md        # namespaces, pods, services, configmaps
│   ├── 06-tags-metadatos.md           # Tags obligatorios (Environment, Owner, CostCenter)
│   └── 07-variables-entorno.md        # Prefijos, formato, jerarquía
│
├── git/                                # Git workflow (naming + proceso)
│   ├── _category_.json
│   ├── 01-naming-repositorios.md      # tlm-svc-*, tlm-app-* ✅ Ya existe
│   ├── 02-naming-ramas.md             # feature/*, hotfix/* ✅ Ya existe
│   ├── 03-commits.md                  # Conventional Commits ✅ Ya existe
│   ├── 04-tags-releases.md            # v1.2.3, SemVer ✅ Ya existe
│   ├── 05-pull-requests.md            # PR title, description template
│   ├── 06-code-review.md              # Review checklist, approval rules
│   └── 07-merge-strategies.md         # Squash vs Merge vs Rebase
│
├── testing/                            # Testing (naming + estructura)
│   ├── _category_.json
│   ├── 01-naming-unit-tests.md        # Should_*, Given_When_Then, AAA
│   ├── 02-naming-integration-tests.md # Test fixtures naming, builders
│   ├── 03-naming-e2e-tests.md         # Page objects, selectors (data-testid)
│   ├── 04-organizacion-tests.md       # Folder structure, __tests__, spec vs test
│   ├── 05-test-data.md                # Fixtures location, factories, builders
│   └── 06-coverage-thresholds.md      # Minimum coverage, excludes
│
├── base-datos/                         # Base de datos (naming + migraciones)
│   ├── _category_.json
│   ├── 01-naming-postgresql.md        # snake_case, singular, vw_, sp_
│   ├── 02-naming-oracle.md            # UPPER_CASE, VW_, SP_
│   ├── 03-naming-sqlserver.md         # PascalCase o snake_case
│   ├── 04-naming-indices.md           # idx_{table}_{columns}, uk_{table}_{columns}
│   ├── 05-naming-constraints.md       # fk_, pk_, ck_, df_ prefixes
│   ├── 06-migraciones.md              # Timestamp + description, up/down
│   └── 07-seed-data.md                # Seed file organization, idempotencia
│
├── documentacion/                      # Docs (formato + estructura)
│   ├── _category_.json
│   ├── 01-adrs.md                     # ADR-NNN-titulo.md, MADR template
│   ├── 02-readmes.md                  # README structure, badges, sections
│   ├── 03-openapi-swagger.md          # Descriptions, examples, tags, security
│   ├── 04-comentarios-codigo.md       # When/how to comment, what to avoid
│   └── 05-changelog.md                # Keep a Changelog format
│
├── mensajeria/                         # Eventos/Mensajes (naming + formato)
│   ├── _category_.json
│   ├── 01-naming-eventos-kafka.md     # domain.entity.action (orders.order.created)
│   ├── 02-naming-topics-kafka.md      # Topic naming, partitions
│   ├── 03-naming-queues-sqs.md        # {env}-{service}-{purpose}
│   ├── 04-naming-topics-pubsub.md     # projects/{project}/topics/{topic}
│   ├── 05-formato-eventos.md          # Event envelope structure, metadata
│   └── 06-versionado-schemas.md       # Schema evolution, compatibility
│
├── logs/                               # Logging (formato + contenido)
│   ├── _category_.json
│   ├── 01-niveles-log.md              # Cuándo usar DEBUG, INFO, WARN, ERROR, FATAL
│   ├── 02-formato-mensajes.md         # Structured logging format (JSON)
│   ├── 03-correlation-ids.md          # Propagation, format, headers
│   ├── 04-pii-datos-sensibles.md      # What NOT to log, masking rules
│   └── 05-contexto-logs.md            # Required fields (timestamp, service, env)
│
├── seguridad/                          # Seguridad (proceso + validación)
│   ├── _category_.json
│   ├── 01-secretos.md                 # Never commit secrets, .env patterns
│   ├── 02-dependencias.md             # Update frequency, vulnerability scanning
│   ├── 03-headers-seguridad.md        # CORS, CSP, HSTS, X-Frame-Options
│   ├── 04-autenticacion.md            # Token format, expiration, refresh
│   └── 05-validacion-input.md         # Sanitization, allowlist vs blocklist
│
└── cicd/                               # CI/CD (naming + estructura)
    ├── _category_.json
    ├── 01-naming-pipelines.md         # Pipeline file naming, job names
    ├── 02-naming-artifacts.md         # Build artifacts, versioning
    ├── 03-variables-secretos.md       # Environment variables in CI/CD
    ├── 04-stages-jobs.md              # Pipeline stage organization
    └── 05-deployment-strategies.md    # Blue-green, canary, rolling patterns
```

---

## 🔄 Migración desde Estructura Actual

### **Mantener**

✅ `nombres/01-repositorios.md` → `git/01-repositorios.md`
✅ `nombres/02-ramas.md` → `git/02-ramas.md`
✅ `estrategia-de-ramas/04-convenciones-commits.md` → `git/03-commits.md`
✅ `estrategia-de-ramas/05-versionado-semantico.md` → `git/04-tags-releases.md`

### **Eliminar o Mover**

❌ `nombres/03-archivos-y-carpetas.md` - Demasiado general, mover a lineamiento
❌ `nombres/04-objetos-base-datos.md` - Ya cubierto en estándar SQL
❌ `estrategia-de-ramas/01-gitflow.md` - Mover a lineamiento de versionado
❌ `estrategia-de-ramas/02-trunk-based.md` - Mover a lineamiento de versionado
❌ `estrategia-de-ramas/03-feature-hotfix-release.md` - Consolidar en git/02-ramas.md

### **Crear Nuevas**

🆕 `codigo/01-csharp.md` - Naming conventions C#
🆕 `codigo/02-typescript.md` - Naming conventions TypeScript
🆕 `codigo/03-sql.md` - Consolidar naming SQL
🆕 `apis/01-recursos-endpoints.md` - REST naming
🆕 `apis/02-parametros-query.md` - Query params naming
🆕 `infraestructura/01-recursos-aws.md` - AWS naming
🆕 `testing/01-unit-tests.md` - Test naming patterns
🆕 `documentacion/01-adrs.md` - ADR template

---

## 📝 Formato Estándar de Cada Convención

```markdown
---
id: nombre-convencion
sidebar_position: N
title: Título Descriptivo
description: Descripción breve
---

## 1. Principio

¿Qué se estandariza y por qué?

## 2. Reglas

### Regla 1: [Nombre]

- **Formato**: `formato_exacto`
- **Ejemplo correcto**: `ejemplo_bueno`
- **Ejemplo incorrecto**: `ejemplo_malo`
- **Justificación**: Por qué esta regla

### Regla 2: [Nombre]

...

## 3. Tabla de Referencia Rápida

| Elemento | Formato    | Ejemplo       |
| -------- | ---------- | ------------- |
| Clase    | PascalCase | `UserService` |
| Variable | camelCase  | `userId`      |

## 4. Herramientas de Validación

- **Linter**: ESLint, StyleCop
- **Configuración**: archivo `.eslintrc.json`

## 5. Excepciones

Casos donde NO se aplica la convención.

## 📖 Referencias

### Estándares relacionados

- [Estándar X](link)

### Recursos externos

- [Guía oficial](link)
```

---

## 🎯 Criterios de Éxito

1. ✅ **Sin solapamiento**: Nada que ya esté en estándares
2. ✅ **Verificable**: Puede validarse con linters/hooks
3. ✅ **Corto**: 50-150 líneas máximo por archivo
4. ✅ **Específico**: Reglas concretas, no conceptos
5. ✅ **Consistente**: Mismo formato en todos los archivos

---

## 📊 Resumen por Tipo de Convención

### **1. Naming (Nomenclatura)** - ~25 archivos

Cómo nombrar variables, clases, archivos, recursos, endpoints, tablas, etc.

### **2. Formato/Estilo** - ~8 archivos

Indentación, comillas, punto y coma, line length, import order, braces

### **3. Estructura** - ~8 archivos

Organización de folders, proyectos, layers, módulos, tests

### **4. Proceso/Workflow** - ~8 archivos

Git workflow, PR templates, code review, merge strategies, deployment

### **5. Formato de Datos** - ~10 archivos

Fechas (ISO 8601), moneda, paginación, eventos, logs, responses

### **6. Seguridad** - ~5 archivos

Secretos, headers, validación, dependencias

### **7. Configuración** - ~6 archivos

Environment variables, feature flags, tags, metadata

**Total estimado: ~70 convenciones**

---

## 🎯 Criterios para Incluir una Convención

✅ **SÍ incluir si:**

- Es una regla específica y verificable
- Se aplica consistentemente en toda la organización
- Puede automatizarse (linter, pre-commit hook, pipeline check)
- Afecta directamente la consistencia del código/infraestructura
- Es independiente de la tecnología específica O es crítica para una tech key

❌ **NO incluir si:**

- Ya está cubierto en un estándar (ejemplo: cómo estructurar un Dockerfile)
- Es un concepto arquitectónico (va en lineamientos)
- Es muy específico de un proyecto particular
- Cambia frecuentemente según contexto
- Es una preferencia personal sin impacto en calidad

---

## 📋 Convenciones Prioritarias (MVP - Fase 1)

### **Debe tener para arrancar** (~20 archivos):

**Código:**

1. Naming C# (clases, variables, interfaces)
2. Naming TypeScript (variables, types, interfaces)
3. Comentarios código (JSDoc, XMLDoc, TODO format)
4. Estructura de proyectos (.NET, Node.js)

**APIs:** 5. Naming endpoints (/api/v1/resources) 6. Headers HTTP (X-Correlation-ID, etc.) 7. Formato respuestas (RFC 7807, pagination) 8. Formato fechas y moneda

**Git:** 9. ✅ Repositorios (ya existe) 10. ✅ Ramas (ya existe) 11. ✅ Commits (ya existe) 12. Pull Requests (template, checklist)

**Infraestructura:** 13. Naming recursos AWS 14. Tags obligatorios (Environment, Owner, CostCenter) 15. Variables de entorno (formato, jerarquía)

**Base de Datos:** 16. Naming PostgreSQL (tablas, columnas) 17. Naming migraciones

**Logs:** 18. Niveles de log (cuándo usar cada uno) 19. Correlation IDs (propagación)

**Seguridad:** 20. Manejo de secretos (never commit, patterns)
