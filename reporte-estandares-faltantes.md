# Reporte: Estándares Técnicos Faltantes

**Generado:** 2026-02-17
**Estado:** Listo para implementación v1.0

---

## Resumen Ejecutivo

| Métrica                                      | Cantidad                        |
| -------------------------------------------- | ------------------------------- |
| **Estándares existentes**                    | 33                              |
| **Referencias totales en lineamientos**      | 181                             |
| **Estándares faltantes (referencias rotas)** | 54                              |
| **Carpetas faltantes**                       | 2 (`governo/`, `operabilidad/`) |

### Desglose por Prioridad

| Prioridad      | Cantidad | Criterio       |
| -------------- | -------- | -------------- |
| 🔴 **CRÍTICA** | 6        | 3+ referencias |
| 🟠 **ALTA**    | 12       | 2 referencias  |
| 🟡 **MEDIA**   | 36       | 1 referencia   |

---

## 🔴 Prioridad CRÍTICA (3+ referencias)

Estos estándares son referenciados por múltiples lineamientos y deben crearse primero para garantizar coherencia estructural.

### 1. `documentacion/adr-template.md` (4 referencias)

**Descripción:** Plantilla estándar para Architecture Decision Records (ADR).

**Referenciado desde:**

- [arquitectura/13-simplicidad-intencional.md](docs/fundamentos-corporativos/lineamientos/arquitectura/13-simplicidad-intencional.md)
  - _"Documentar decisiones arquitectónicas de forma comprensible"_
- [arquitectura/12-arquitectura-evolutiva.md](docs/fundamentos-corporativos/lineamientos/arquitectura/12-arquitectura-evolutiva.md)
  - _"Documentar decisiones arquitectónicas con ADRs"_
- [arquitectura/01-estilo-y-enfoque-arquitectonico.md](docs/fundamentos-corporativos/lineamientos/arquitectura/01-estilo-y-enfoque-arquitectonico.md)
  - _"Documentar estilo seleccionado en ADR"_
- [gobierno/01-decisiones-arquitectonicas.md](docs/fundamentos-corporativos/lineamientos/gobierno/01-decisiones-arquitectonicas.md)
  - _"Documentar decisiones significativas en ADRs"_

**Recomendación:** Crear como plantilla Markdown con secciones: Contexto, Decisión, Consecuencias, Alternativas consideradas, Estado.

---

### 2. `gobierno/architecture-review.md` (4 referencias)

**Descripción:** Proceso formal de revisión arquitectónica: cuándo, quién, cómo.

**Referenciado desde:**

- [arquitectura/12-arquitectura-evolutiva.md](docs/fundamentos-corporativos/lineamientos/arquitectura/12-arquitectura-evolutiva.md)
  - _"Revisar y ajustar decisiones arquitectónicas periódicamente"_
- [arquitectura/01-estilo-y-enfoque-arquitectonico.md](docs/fundamentos-corporativos/lineamientos/arquitectura/01-estilo-y-enfoque-arquitectonico.md)
  - _"Validar coherencia entre estilo declarado y decisiones técnicas"_
- [gobierno/01-decisiones-arquitectonicas.md](docs/fundamentos-corporativos/lineamientos/gobierno/01-decisiones-arquitectonicas.md)
  - _"Revisar ADRs en architecture reviews"_
- [gobierno/02-revisiones-arquitectonicas.md](docs/fundamentos-corporativos/lineamientos/gobierno/02-revisiones-arquitectonicas.md)
  - _"Realizar architecture review antes de implementaciones significativas"_

**Recomendación:** Definir criterios de entrada/salida, participantes obligatorios, checklist de validación, periodicidad.

---

### 3. `datos/database-per-service.md` (3 referencias)

**Descripción:** Estándar para asignar bases de datos independientes por servicio/dominio.

**Referenciado desde:**

- [datos/03-propiedad-de-datos.md](docs/fundamentos-corporativos/lineamientos/datos/03-propiedad-de-datos.md)
  - _"Asignar base de datos independiente por dominio/servicio"_
- [arquitectura/10-autonomia-de-servicios.md](docs/fundamentos-corporativos/lineamientos/arquitectura/10-autonomia-de-servicios.md)
  - _"Implementar ownership completo de datos por servicio"_

**Recomendación:** Especificar aislamiento lógico vs físico, estrategias de deployment, migraciones, backups por servicio.

---

### 4. `mensajeria/async-messaging.md` (3 referencias)

**Descripción:** Patrones y estándares para mensajería asíncrona general (complemento a Kafka específico).

**Referenciado desde:**

- [arquitectura/10-autonomia-de-servicios.md](docs/fundamentos-corporativos/lineamientos/arquitectura/10-autonomia-de-servicios.md)
  - _"Utilizar comunicación asíncrona cuando sea posible"_
- [arquitectura/05-escalabilidad-y-rendimiento.md](docs/fundamentos-corporativos/lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md)
  - _"Mover operaciones costosas a procesamiento asíncrono"_

**Recomendación:** Puede consolidarse con `kafka-messaging.md` o crear para patrones generales (SQS, webhooks, polling).

---

### 5. `desarrollo/repositorios.md` (3 referencias)

**Descripción:** Estándares de estructura de repositorios Git, README, branching, commits semánticos.

**Referenciado desde:**

- [desarrollo/03-documentacion-tecnica.md](docs/fundamentos-corporativos/lineamientos/desarrollo/03-documentacion-tecnica.md)
  - _"Mantener README actualizado en todos los repositorios"_
- [desarrollo/04-control-versiones.md](docs/fundamentos-corporativos/lineamientos/desarrollo/04-control-versiones.md)
  - _"Usar Git workflows y estrategias de branching consistentes"_
  - _"Aplicar commits semánticos (Conventional Commits)"_
  - _"Versionar artefactos con Semantic Versioning (SemVer)"_
- [operabilidad/02-infraestructura-como-codigo.md](docs/fundamentos-corporativos/lineamientos/operabilidad/02-infraestructura-como-codigo.md)
  - _"Versionar código de infraestructura en repositorios Git"_

**Recomendación:** Definir estructura obligatoria de README, trunk-based vs GitFlow, semantic versioning, monorepo vs polyrepo.

---

### 6. `operabilidad/disaster-recovery.md` (5 referencias)

**Descripción:** Estrategias de backup, RPO/RTO, runbooks, procedimientos de restauración.

**Referenciado desde:**

- [operabilidad/04-disaster-recovery.md](docs/fundamentos-corporativos/lineamientos/operabilidad/04-disaster-recovery.md)
  - _"Definir objetivos RPO/RTO para cada sistema crítico"_
  - _"Implementar backups automatizados con retención apropiada"_
  - _"Probar procedimientos de restauración al menos trimestralmente"_
  - _"Documentar runbooks de DR actualizados y accesibles"_
  - _"Realizar simulacros de DR con equipos involucrados"_

**Recomendación:** Crear carpeta `operabilidad/` primero. Definir matriz RPO/RTO, estrategias de backup, checklist de simulacros.

---

## 🟠 Prioridad ALTA (2 referencias)

Estándares con impacto significativo que deben crearse después de los críticos.

### Seguridad (4 estándares)

#### `seguridad/authorization.md` (3 referencias)

- Referenciado en: minimo-privilegio, defensa-en-profundidad, zero-trust
- **Contenido sugerido:** RBAC, ABAC, permisos granulares, políticas de autorización

#### `seguridad/authentication.md` (1 referencia)

- Referenciado en: zero-trust
- **Contenido sugerido:** SSO, MFA, OAuth2/OIDC, gestión de sesiones

#### `seguridad/rbac.md` (1 referencia)

- Referenciado en: minimo-privilegio
- **Contenido sugerido:** Roles corporativos, permisos por rol, herencia de roles

#### `seguridad/access-review.md` (1 referencia)

- Referenciado en: minimo-privilegio
- **Contenido sugerido:** Auditorías periódicas de acceso, revalidación trimestral, revocación automática

### Datos (4 estándares)

#### `datos/no-shared-database.md` (1 referencia)

- Referenciado en: propiedad-de-datos
- **Consolidación sugerida:** Puede fusionarse con `database-per-service.md`

#### `datos/data-exposure.md` (1 referencia)

- Referenciado en: propiedad-de-datos
- **Contenido sugerido:** APIs de datos, eventos de dominio, vistas materializadas

#### `datos/data-catalog.md` (1 referencia)

- Referenciado en: propiedad-de-datos
- **Contenido sugerido:** Inventario de datasets, ownership, metadatos, lineage

#### `datos/data-replication.md` (1 referencia)

- Referenciado en: propiedad-de-datos
- **Contenido sugerido:** CDC, read replicas, sincronización eventual

### Gobierno (4 estándares)

#### `gobierno/review-documentation.md` (1 referencia)

- Referenciado en: revisiones-arquitectonicas
- **Contenido sugerido:** Actas de architecture reviews, registro de decisiones, acciones y seguimiento

#### `gobierno/architecture-retrospectives.md` (1 referencia)

- Referenciado en: revisiones-arquitectonicas
- **Contenido sugerido:** Retrospectivas post-go-live, lecciones aprendidas, mejora continua

#### `gobierno/compliance-validation.md` (1 referencia)

- Referenciado en: cumplimiento-y-excepciones
- **Contenido sugerido:** Auditorías de cumplimiento, validaciones automatizadas, reportes

#### `governo/exception-management.md` (1 referencia)

- Referenciado en: cumplimiento-y-excepciones
- **Contenido sugerido:** Proceso formal de excepciones, aprobación, documentación en ADR, vigencia temporal

---

## 🟡 Prioridad MEDIA (1 referencia)

Estos estándares pueden consolidarse, crearse según demanda, o convertirse en secciones de estándares existentes.

### Arquitectura (7 estándares)

| Estándar                    | Lineamiento                 | Acción Recomendada                                                   |
| --------------------------- | --------------------------- | -------------------------------------------------------------------- |
| `complexity-analysis.md`    | simplicidad-intencional     | Crear: Métricas de complejidad ciclomática, análisis costo-beneficio |
| `technology-selection.md`   | simplicidad-intencional     | Crear: Matriz de evaluación, radar tecnológico                       |
| `dependency-inversion.md`   | arquitectura-limpia         | **Consolidar** en `bounded-contexts.md` como sección                 |
| `hexagonal-architecture.md` | arquitectura-limpia         | Crear: Patrón hexagonal, ports & adapters                            |
| `caching-strategies.md`     | escalabilidad-y-rendimiento | Crear: Redis, cache aside, write-through, TTL                        |
| `dependency-management.md`  | descomposicion-y-limites    | **Consolidar** en `bounded-contexts.md`                              |

### Desarrollo (2 estándares)

| Estándar                    | Lineamiento            | Acción Recomendada                          |
| --------------------------- | ---------------------- | ------------------------------------------- |
| `independent-deployment.md` | autonomia-de-servicios | Crear: Feature flags, blue/green, canary    |
| `refactoring-practices.md`  | arquitectura-evolutiva | Crear: Strangler fig, branch by abstraction |

### APIs (1 estándar)

| Estándar            | Lineamiento                              | Acción Recomendada                          |
| ------------------- | ---------------------------------------- | ------------------------------------------- |
| `api-versioning.md` | apis-y-contratos, autonomia-de-servicios | Crear: URL-based, header-based, deprecación |

### Infraestructura (1 estándar)

| Estándar          | Lineamiento                 | Acción Recomendada                    |
| ----------------- | --------------------------- | ------------------------------------- |
| `auto-scaling.md` | escalabilidad-y-rendimiento | Crear: HPA, target tracking, métricas |

### Datos (2 estándares)

| Estándar                   | Lineamiento                 | Acción Recomendada                          |
| -------------------------- | --------------------------- | ------------------------------------------- |
| `database-optimization.md` | escalabilidad-y-rendimiento | Crear: Índices, query optimization, EXPLAIN |

### Seguridad (1 estándar)

| Estándar                   | Lineamiento       | Acción Recomendada                              |
| -------------------------- | ----------------- | ----------------------------------------------- |
| `segregation-of-duties.md` | minimo-privilegio | Crear: Separación de responsabilidades críticas |

---

## 📁 Carpetas Faltantes

Crear estas carpetas en `docs/fundamentos-corporativos/estandares/`:

### 1. `governo/` (5 estándares pendientes)

- `architecture-review.md` (🔴 CRÍTICO)
- `review-documentation.md` (🟠 ALTO)
- `architecture-retrospectives.md` (🟠 ALTO)
- `compliance-validation.md` (🟠 ALTO)
- `exception-management.md` (🟠 ALTO)

### 2. `operabilidad/` (1 estándar pendiente)

- `disaster-recovery.md` (🔴 CRÍTICO)

---

## ✅ Estándares Mejor Referenciados (Existentes)

Estos estándares ya existen y tienen múltiples referencias. Sirven como **plantilla de calidad** para estándares nuevos:

| Estándar                           | Referencias | Ubicación         |
| ---------------------------------- | ----------- | ----------------- |
| `bounded-contexts.md`              | 17          | `arquitectura/`   |
| `kafka-messaging.md`               | 13          | `mensajeria/`     |
| `observability.md`                 | 11          | `observabilidad/` |
| `resilience-patterns.md`           | 9           | `arquitectura/`   |
| `api-rest-standards.md`            | 8           | `apis/`           |
| `code-quality-review.md`           | 6           | `desarrollo/`     |
| `security-architecture.md`         | 6           | `seguridad/`      |
| `cicd-pipelines.md`                | 5           | `desarrollo/`     |
| `architecture-decision-records.md` | 4           | `documentacion/`  |
| `network-security.md`              | 4           | `seguridad/`      |

---

## 📋 Plan de Implementación

### Fase 1: Fundamentos (Semana 1-2) 🔴

Crear estándares críticos que desbloquean múltiples lineamientos:

1. **Governo** (crear carpeta):
   - `architecture-review.md` - Proceso de revisión arquitectónica
   - `exception-management.md` - Gestión formal de excepciones

2. **Documentación**:
   - `adr-template.md` - Plantilla estándar de ADRs

3. **Operabilidad** (crear carpeta):
   - `disaster-recovery.md` - DR, backups, RPO/RTO

4. **Datos**:
   - `database-per-service.md` - Aislamiento de datos por servicio

5. **Desarrollo**:
   - `repositorios.md` - Estándares de Git, README, branching

6. **Mensajería**:
   - `async-messaging.md` - Patrones asíncronos generales

---

### Fase 2: Consolidación (Semana 3) 🟠

Crear estándares de alta prioridad y consolidar donde sea posible:

1. **Seguridad** (4 estándares):
   - `authorization.md` (RBAC/ABAC)
   - `authentication.md` (SSO/MFA)
   - `rbac.md` (Roles corporativos)
   - `access-review.md` (Auditorías de acceso)

2. **Governo** (completar carpeta):
   - `review-documentation.md`
   - `architecture-retrospectives.md`
   - `compliance-validation.md`

3. **Datos** (4 estándares):
   - `data-exposure.md`
   - `data-catalog.md`
   - `data-replication.md`
   - Considerar fusión `no-shared-database.md` → `database-per-service.md`

---

### Fase 3: Especialización (Semana 4) 🟡

Crear estándares específicos según demanda:

1. **Arquitectura**:
   - `caching-strategies.md` (Redis, patterns)
   - `hexagonal-architecture.md` (Ports & Adapters)
   - `complexity-analysis.md` (Métricas, análisis)
   - `technology-selection.md` (Matriz de evaluación)

2. **Infraestructura**:
   - `auto-scaling.md` (HPA, métricas)

3. **Desarrollo**:
   - `independent-deployment.md` (Feature flags)
   - `refactoring-practices.md` (Strangler fig)

4. **APIs**:
   - `api-versioning.md` (Estrategias de versionado)

5. **Datos**:
   - `database-optimization.md` (Índices, queries)

6. **Seguridad**:
   - `segregation-of-duties.md`

---

## 🎯 Criterios de Éxito v1.0

| Métrica                              | Objetivo | Estado Actual       |
| ------------------------------------ | -------- | ------------------- |
| Estándares críticos creados          | 6/6      | ⏳ 0/6              |
| Estándares alta prioridad creados    | 12/12    | ⏳ 0/12             |
| Referencias rotas restantes          | < 10     | ❌ 54               |
| Carpetas completas                   | 2/2      | ❌ 0/2              |
| Estándares con plantilla consistente | 100%     | ✅ 33/33 existentes |
| Validación de enlaces                | PASS     | ⏳ Pendiente        |

---

## 🔄 Oportunidades de Consolidación

Algunos estándares pueden fusionarse para evitar fragmentación excesiva:

### Opción 1: Fusionar Autenticación/Autorización

- `authentication.md` + `authorization.md` → `identity-access-management.md` (YA EXISTE)
- **Ventaja:** Centraliza IAM en un solo estándar
- **Desventaja:** Estándar más grande y menos enfocado

### Opción 2: Fusionar Database Standards

- `no-shared-database.md` → Sección en `database-per-service.md`
- `database-optimization.md` → Sección en `database-standards.md` (YA EXISTE)
- **Ventaja:** Menos archivos para mantener
- **Desventaja:** Estándares de datos más complejos

### Opción 3: Fusionar Dependency Management

- `dependency-management.md` + `dependency-inversion.md` → Secciones en `bounded-contexts.md` (YA EXISTE)
- **Ventaja:** Cohesión arquitectónica
- **Desventaja:** `bounded-contexts.md` ya tiene 17 referencias (muy usado)

**Recomendación:** Aplicar Opción 2 (fusionar database standards) para reducir complejidad de carpeta `datos/`.

---

## 📌 Notas Finales

1. **Estándares huérfanos corregidos**: 8/8 ✅
   - Todos los estándares existentes ahora tienen al menos 1 referencia

2. **Plantilla de estándares**: Usar `bounded-contexts.md`, `kafka-messaging.md` u `observability.md` como referencia

3. **Revisión post-creación**: Ejecutar script de validación después de cada fase para confirmar reducción de referencias rotas

4. **ADRs pendientes**: Varios lineamientos mencionan ADRs en carpeta `decisiones-de-arquitectura/` - validar alineación

---

## Comandos Útiles

```bash
# Validar enlaces rotos después de crear estándares
python3 scripts/validar-broken-links.py

# Contar referencias a un estándar específico
grep -r "ruta/del/estandar.md" docs/fundamentos-corporativos/lineamientos/

# Listar estándares sin referencias (huérfanos)
# [Ejecutar script de validación actualizado]
```

---

**Generado automáticamente** | [Volver a lineamientos](docs/fundamentos-corporativos/lineamientos/)
