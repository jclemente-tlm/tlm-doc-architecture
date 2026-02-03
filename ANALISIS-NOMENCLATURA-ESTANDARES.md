# Análisis de Nomenclatura y Categorización de Estándares

## 1. Resumen Ejecutivo

**Total de estándares:** 102

**Idiomas encontrados:**

- ❌ **Mezcla inconsistente**: 60% inglés, 40% español
- ⚠️ **Problema**: Falta de convención uniforme

**Categorías actuales:**

- ✅ arquitectura/
- ✅ apis/
- ✅ datos/
- ✅ seguridad/
- ✅ mensajeria/
- ✅ testing/
- ✅ operabilidad/
- ✅ infraestructura/
- ✅ gobierno/
- ✅ observabilidad/
- ✅ documentacion/
- ✅ codigo/

---

## 2. Análisis por Categoría

### 📁 arquitectura/ (11 estándares)

| Archivo                    | Idioma    | Problema | Recomendación |
| -------------------------- | --------- | -------- | ------------- |
| `bounded-contexts.md`      | 🇬🇧 Inglés | ✅ OK    | -             |
| `circuit-breakers.md`      | 🇬🇧 Inglés | ✅ OK    | -             |
| `dependency-management.md` | 🇬🇧 Inglés | ✅ OK    | -             |
| `graceful-degradation.md`  | 🇬🇧 Inglés | ✅ OK    | -             |
| `graceful-shutdown.md`     | 🇬🇧 Inglés | ✅ OK    | -             |
| `horizontal-scaling.md`    | 🇬🇧 Inglés | ✅ OK    | -             |
| `retry-patterns.md`        | 🇬🇧 Inglés | ✅ OK    | -             |
| `saga-pattern.md`          | 🇬🇧 Inglés | ✅ OK    | -             |
| `single-responsibility.md` | 🇬🇧 Inglés | ✅ OK    | -             |
| `stateless-services.md`    | 🇬🇧 Inglés | ✅ OK    | -             |
| `timeouts.md`              | 🇬🇧 Inglés | ✅ OK    | -             |

**Veredicto:** ✅ **100% inglés - CONSISTENTE**

---

### 📁 apis/ (13 estándares)

| Archivo                       | Idioma     | Problema     | Recomendación                       |
| ----------------------------- | ---------- | ------------ | ----------------------------------- |
| `01-diseno-rest.md`           | 🇪🇸 Español | ❌ Mixto     | `rest-design.md`                    |
| `02-seguridad-apis.md`        | 🇪🇸 Español | ❌ Mixto     | `api-security.md`                   |
| `03-validacion-y-errores.md`  | 🇪🇸 Español | ❌ Mixto     | `validation-and-errors.md`          |
| `04-versionado.md`            | 🇪🇸 Español | ❌ Mixto     | `versioning.md`                     |
| `05-performance.md`           | 🇬🇧 Inglés  | ✅ OK        | -                                   |
| `api-portal.md`               | 🇬🇧 Inglés  | ✅ OK        | -                                   |
| `contract-validation.md`      | 🇬🇧 Inglés  | ✅ OK        | -                                   |
| `deprecacion-apis.md`         | 🇪🇸 Español | ❌ Mixto     | `api-deprecation.md`                |
| `error-handling.md`           | 🇬🇧 Inglés  | ✅ OK        | -                                   |
| `openapi-swagger.md`          | 🇬🇧 Inglés  | ✅ OK        | -                                   |
| `rate-limiting-paginacion.md` | 🇪🇸 Español | ❌ Mixto     | `rate-limiting-pagination.md`       |
| `rest-conventions.md`         | 🇬🇧 Inglés  | ✅ OK        | -                                   |
| `versionado.md`               | 🇪🇸 Español | ❌ DUPLICADO | Eliminar (duplica 04-versionado.md) |

**Veredicto:** ❌ **54% inglés, 46% español - INCONSISTENTE**

**Problemas detectados:**

- Duplicado: `versionado.md` y `04-versionado.md`
- Archivos numerados (01-05) mezclados con no numerados
- 6 archivos en español vs 7 en inglés

---

### 📁 datos/ (14 estándares)

| Archivo                        | Idioma    | Problema                               | Recomendación                        |
| ------------------------------ | --------- | -------------------------------------- | ------------------------------------ |
| `02-migrations.md`             | 🇬🇧 Inglés | ⚠️ Numerado                            | `database-migrations.md` (ya existe) |
| `conflict-resolution.md`       | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `consistency-models.md`        | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `consistency-slos.md`          | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `data-access-via-apis.md`      | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `data-lifecycle.md`            | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `data-ownership.md`            | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `database-migrations.md`       | 🇬🇧 Inglés | ✅ OK (DUPLICADO con 02-migrations.md) | -                                    |
| `database-per-service.md`      | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `least-knowledge-principle.md` | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `reconciliation.md`            | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `schema-documentation.md`      | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `schema-evolution.md`          | 🇬🇧 Inglés | ✅ OK                                  | -                                    |
| `schema-registry.md`           | 🇬🇧 Inglés | ⚠️ Pendiente decisión                  | (Usuario dejó para el final)         |
| `schema-validation.md`         | 🇬🇧 Inglés | ✅ OK                                  | -                                    |

**Veredicto:** ✅ **100% inglés - CONSISTENTE**

**Problema:** Duplicado `02-migrations.md` vs `database-migrations.md`

---

### 📁 seguridad/ (25 estándares)

| Archivo                               | Idioma     | Problema | Recomendación                 |
| ------------------------------------- | ---------- | -------- | ----------------------------- |
| `aislamiento-tenants.md`              | 🇪🇸 Español | ❌ Mixto | `tenant-isolation.md`         |
| `clasificacion-datos.md`              | 🇪🇸 Español | ❌ Mixto | `data-classification.md`      |
| `container-image-scanning.md`         | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `data-encryption.md`                  | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `defense-in-depth.md`                 | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `enmascaramiento-datos.md`            | 🇪🇸 Español | ❌ Mixto | `data-masking.md`             |
| `gestion-claves-kms.md`               | 🇪🇸 Español | ❌ Mixto | `key-management.md`           |
| `gestion-secretos.md`                 | 🇪🇸 Español | ❌ Mixto | `secrets-management.md`       |
| `incident-response-program.md`        | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `mfa-configuracion.md`                | 🇪🇸 Español | ❌ Mixto | `mfa-configuration.md`        |
| `minimizacion-datos.md`               | 🇪🇸 Español | ❌ Mixto | `data-minimization.md`        |
| `minimo-privilegio.md`                | 🇪🇸 Español | ❌ Mixto | `least-privilege.md`          |
| `reduccion-superficie-ataque.md`      | 🇪🇸 Español | ❌ Mixto | `attack-surface-reduction.md` |
| `retencion-eliminacion.md`            | 🇪🇸 Español | ❌ Mixto | `data-retention.md`           |
| `security-by-design.md`               | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `segmentacion-redes.md`               | 🇪🇸 Español | ❌ Mixto | `network-segmentation.md`     |
| `separacion-entornos.md`              | 🇪🇸 Español | ❌ Mixto | `environment-separation.md`   |
| `service-identities.md`               | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `software-bill-of-materials.md`       | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `sso-federado.md`                     | 🇪🇸 Español | ❌ Mixto | `sso-federation.md`           |
| `threat-modeling.md`                  | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `trust-boundaries.md`                 | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `vulnerability-management-program.md` | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `vulnerability-scanning.md`           | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `zero-trust-network.md`               | 🇬🇧 Inglés  | ✅ OK    | -                             |
| `zonas-seguridad.md`                  | 🇪🇸 Español | ❌ Mixto | `security-zones.md`           |

**Veredicto:** ❌ **56% inglés, 44% español - INCONSISTENTE**

**Problema crítico:** Categoría más grande y más inconsistente (14 archivos en español)

---

### 📁 mensajeria/ (6 estándares)

| Archivo                | Idioma            | Problema    | Recomendación                            |
| ---------------------- | ----------------- | ----------- | ---------------------------------------- |
| `01-kafka-eventos.md`  | 🇪🇸 Español        | ⚠️ Numerado | `kafka-events.md`                        |
| `dlq.md`               | 🇬🇧 Inglés (sigla) | ✅ OK       | `dead-letter-queue.md` (más descriptivo) |
| `domain-events.md`     | 🇬🇧 Inglés         | ✅ OK       | -                                        |
| `garantias-entrega.md` | 🇪🇸 Español        | ❌ Mixto    | `delivery-guarantees.md`                 |
| `idempotencia.md`      | 🇪🇸 Español        | ❌ Mixto    | `idempotency.md`                         |
| `schemas-eventos.md`   | 🇪🇸 Español        | ❌ Mixto    | `event-schemas.md`                       |
| `topologia-eventos.md` | 🇪🇸 Español        | ❌ Mixto    | `event-topology.md`                      |

**Veredicto:** ❌ **29% inglés, 71% español - INCONSISTENTE**

---

### 📁 testing/ (3 estándares)

| Archivo                   | Idioma    | Problema    | Recomendación          |
| ------------------------- | --------- | ----------- | ---------------------- |
| `01-unit-tests.md`        | 🇬🇧 Inglés | ⚠️ Numerado | `unit-tests.md`        |
| `02-integration-tests.md` | 🇬🇧 Inglés | ⚠️ Numerado | `integration-tests.md` |
| `contract-testing.md`     | 🇬🇧 Inglés | ✅ OK       | -                      |

**Veredicto:** ✅ **100% inglés - CONSISTENTE** (pero con numeración inconsistente)

---

### 📁 operabilidad/ (8 estándares)

| Archivo                     | Idioma             | Problema | Recomendación |
| --------------------------- | ------------------ | -------- | ------------- |
| `cicd-pipelines.md`         | 🇬🇧 Inglés          | ✅ OK    | -             |
| `code-quality-standards.md` | 🇬🇧 Inglés          | ✅ OK    | -             |
| `code-review-policy.md`     | 🇬🇧 Inglés          | ✅ OK    | -             |
| `dev-prod-parity.md`        | 🇬🇧 Inglés          | ✅ OK    | -             |
| `infrastructure-as-code.md` | 🇬🇧 Inglés          | ✅ OK    | -             |
| `quality-security-gates.md` | 🇬🇧 Inglés          | ✅ OK    | -             |
| `slos-slas.md`              | 🇬🇧 Inglés (siglas) | ✅ OK    | -             |
| `testing-pyramid.md`        | 🇬🇧 Inglés          | ✅ OK    | -             |

**Veredicto:** ✅ **100% inglés - CONSISTENTE**

---

### 📁 infraestructura/ (9 estándares)

| Archivo                                  | Idioma     | Problema          | Recomendación                                       |
| ---------------------------------------- | ---------- | ----------------- | --------------------------------------------------- |
| `01-docker.md`                           | 🇬🇧 Inglés  | ⚠️ Numerado       | `docker.md`                                         |
| `02-infraestructura-como-codigo.md`      | 🇪🇸 Español | ❌ Mixto numerado | `infrastructure-as-code.md` (duplica operabilidad/) |
| `03-secrets-management.md`               | 🇬🇧 Inglés  | ⚠️ Numerado       | `secrets-management.md`                             |
| `04-docker-compose.md`                   | 🇬🇧 Inglés  | ⚠️ Numerado       | `docker-compose.md`                                 |
| `cost-alerts.md`                         | 🇬🇧 Inglés  | ✅ OK             | -                                                   |
| `cost-tagging-strategy.md`               | 🇬🇧 Inglés  | ✅ OK             | -                                                   |
| `externalizar-configuracion-12factor.md` | 🇪🇸 Español | ❌ Mixto          | `externalize-configuration.md`                      |
| `reserved-capacity.md`                   | 🇬🇧 Inglés  | ✅ OK             | -                                                   |
| `rightsizing.md`                         | 🇬🇧 Inglés  | ✅ OK             | -                                                   |

**Veredicto:** ❌ **78% inglés, 22% español - INCONSISTENTE**

**Problema:** Duplicado `02-infraestructura-como-codigo.md` con `operabilidad/infrastructure-as-code.md`

---

### 📁 gobierno/ (5 estándares)

| Archivo                          | Idioma    | Problema     | Recomendación               |
| -------------------------------- | --------- | ------------ | --------------------------- |
| `architecture-retrospectives.md` | 🇬🇧 Inglés | ✅ OK        | -                           |
| `architecture-review.md`         | 🇬🇧 Inglés | ⚠️ DUPLICADO | (también en documentacion/) |
| `compliance-validation.md`       | 🇬🇧 Inglés | ✅ OK        | -                           |
| `exception-management.md`        | 🇬🇧 Inglés | ✅ OK        | -                           |
| `review-documentation.md`        | 🇬🇧 Inglés | ✅ OK        | -                           |

**Veredicto:** ✅ **100% inglés - CONSISTENTE**

**Problema:** Duplicado `architecture-review.md` en gobierno/ y documentacion/

---

### 📁 observabilidad/ (5 estándares)

| Archivo                     | Idioma     | Problema          | Recomendación            |
| --------------------------- | ---------- | ----------------- | ------------------------ |
| `01-logging.md`             | 🇬🇧 Inglés  | ⚠️ Numerado       | `logging.md`             |
| `02-monitoreo-metricas.md`  | 🇪🇸 Español | ❌ Mixto numerado | `metrics-monitoring.md`  |
| `03-tracing-distribuido.md` | 🇪🇸 Español | ❌ Mixto numerado | `distributed-tracing.md` |
| `04-correlation-ids.md`     | 🇬🇧 Inglés  | ⚠️ Numerado       | `correlation-ids.md`     |
| `05-health-checks.md`       | 🇬🇧 Inglés  | ⚠️ Numerado       | `health-checks.md`       |

**Veredicto:** ❌ **60% inglés, 40% español - INCONSISTENTE**

**Problema:** Mezcla español/inglés con numeración innecesaria

---

### 📁 documentacion/ (3 estándares)

| Archivo                            | Idioma    | Problema     | Recomendación          |
| ---------------------------------- | --------- | ------------ | ---------------------- |
| `01-arc42.md`                      | 🇬🇧 Inglés | ⚠️ Numerado  | `arc42.md`             |
| `02-c4-model.md`                   | 🇬🇧 Inglés | ⚠️ Numerado  | `c4-model.md`          |
| `03-openapi-swagger.md`            | 🇬🇧 Inglés | ⚠️ Numerado  | `openapi-swagger.md`   |
| `architecture-decision-records.md` | 🇬🇧 Inglés | ✅ OK        | -                      |
| `architecture-review.md`           | 🇬🇧 Inglés | ⚠️ DUPLICADO | (también en gobierno/) |

**Veredicto:** ✅ **100% inglés - CONSISTENTE** (pero con numeración)

---

### 📁 codigo/ (2 estándares)

| Archivo               | Idioma    | Problema               | Recomendación      |
| --------------------- | --------- | ---------------------- | ------------------ |
| `01-csharp-dotnet.md` | 🇬🇧 Inglés | ⚠️ Numerado            | `csharp-dotnet.md` |
| `03-sql.md`           | 🇬🇧 Inglés | ⚠️ Numerado (salto 02) | `sql.md`           |

**Veredicto:** ✅ **100% inglés - CONSISTENTE** (pero numeración con salto)

---

## 3. Problemas Identificados

### 🔴 CRÍTICO

1. **Inconsistencia masiva español/inglés:**
   - 62 archivos en inglés (61%)
   - 40 archivos en español (39%)
   - NO hay convención definida

2. **Duplicados detectados:**
   - `apis/versionado.md` vs `apis/04-versionado.md`
   - `datos/database-migrations.md` vs `datos/02-migrations.md`
   - `gobierno/architecture-review.md` vs `documentacion/architecture-review.md`
   - `infraestructura/02-infraestructura-como-codigo.md` vs `operabilidad/infrastructure-as-code.md`

### ⚠️ ALTO

1. **Numeración inconsistente:**
   - Algunas categorías usan `01-`, `02-`... otras no
   - No hay criterio claro: apis/ mezcla numerados (01-05) con no numerados
   - codigo/ tiene salto de numeración (01, 03 - falta 02)

2. **Categorización ambigua:**
   - `infrastructure-as-code.md` aparece en operabilidad/ (debería estar en infraestructura/)
   - `architecture-review.md` en gobierno/ Y documentacion/ (¿cuál es la correcta?)

### ℹ️ MEDIO

1. **Nomenclatura poco descriptiva:**
   - `dlq.md` → mejor `dead-letter-queue.md`
   - `slos-slas.md` → mejor separar o ser explícito

---

## 4. Recomendaciones

### 🎯 Recomendación 1: Adoptar 100% INGLÉS

**Justificación:**

- ✅ Industria de software usa inglés como estándar
- ✅ Términos técnicos son en inglés (Circuit Breaker, Dead Letter Queue, etc.)
- ✅ Facilita búsqueda y referencia internacional
- ✅ 61% de archivos ya están en inglés
- ✅ Evita traducciones forzadas ("aislamiento-tenants" → mejor "tenant-isolation")

**Acción:** Renombrar 40 archivos de español → inglés

---

### 🎯 Recomendación 2: Eliminar numeración de archivos

**Justificación:**

- ❌ Numeración no aporta valor (el orden se define en sidebars o README)
- ❌ Dificulta mantenimiento (insertar nuevo estándar requiere renumerar)
- ❌ Inconsistente entre categorías
- ✅ Nombres descriptivos son auto-explicativos

**Acción:** Renombrar todos los `01-`, `02-` → nombres sin prefijo

---

### 🎯 Recomendación 3: Eliminar duplicados

| Duplicado                                           | Acción Recomendada                                                      |
| --------------------------------------------------- | ----------------------------------------------------------------------- |
| `apis/versionado.md`                                | ❌ ELIMINAR (mantener `04-versionado.md` → renombrar a `versioning.md`) |
| `datos/02-migrations.md`                            | ❌ ELIMINAR (mantener `database-migrations.md`)                         |
| `documentacion/architecture-review.md`              | ❌ ELIMINAR (mantener en `gobierno/architecture-review.md`)             |
| `infraestructura/02-infraestructura-como-codigo.md` | ❌ ELIMINAR (mantener en `operabilidad/infrastructure-as-code.md`)      |

---

### 🎯 Recomendación 4: Reorganizar categorías

**Mover estándares mal categorizados:**

NO hay problemas graves de categorización. Las 12 categorías son adecuadas.

---

## 5. Plan de Acción Propuesto

### Fase 1: Normalizar idioma (40 archivos)

**Renombrar de español → inglés:**

#### seguridad/ (14 archivos)

- `aislamiento-tenants.md` → `tenant-isolation.md`
- `clasificacion-datos.md` → `data-classification.md`
- `enmascaramiento-datos.md` → `data-masking.md`
- `gestion-claves-kms.md` → `key-management.md`
- `gestion-secretos.md` → `secrets-management.md`
- `mfa-configuracion.md` → `mfa-configuration.md`
- `minimizacion-datos.md` → `data-minimization.md`
- `minimo-privilegio.md` → `least-privilege.md`
- `reduccion-superficie-ataque.md` → `attack-surface-reduction.md`
- `retencion-eliminacion.md` → `data-retention.md`
- `segmentacion-redes.md` → `network-segmentation.md`
- `separacion-entornos.md` → `environment-separation.md`
- `sso-federado.md` → `sso-federation.md`
- `zonas-seguridad.md` → `security-zones.md`

#### mensajeria/ (5 archivos)

- `01-kafka-eventos.md` → `kafka-events.md`
- `garantias-entrega.md` → `delivery-guarantees.md`
- `idempotencia.md` → `idempotency.md`
- `schemas-eventos.md` → `event-schemas.md`
- `topologia-eventos.md` → `event-topology.md`

#### apis/ (6 archivos)

- `01-diseno-rest.md` → `rest-design.md`
- `02-seguridad-apis.md` → `api-security.md`
- `03-validacion-y-errores.md` → `validation-and-errors.md`
- `04-versionado.md` → `versioning.md`
- `deprecacion-apis.md` → `api-deprecation.md`
- `rate-limiting-paginacion.md` → `rate-limiting-pagination.md`

#### observabilidad/ (2 archivos)

- `02-monitoreo-metricas.md` → `metrics-monitoring.md`
- `03-tracing-distribuido.md` → `distributed-tracing.md`

#### infraestructura/ (2 archivos)

- `02-infraestructura-como-codigo.md` → ❌ ELIMINAR (duplicado)
- `externalizar-configuracion-12factor.md` → `externalize-configuration.md`

---

### Fase 2: Eliminar numeración (22 archivos)

- `codigo/01-csharp-dotnet.md` → `csharp-dotnet.md`
- `codigo/03-sql.md` → `sql.md`
- `documentacion/01-arc42.md` → `arc42.md`
- `documentacion/02-c4-model.md` → `c4-model.md`
- `documentacion/03-openapi-swagger.md` → `openapi-swagger.md`
- `infraestructura/01-docker.md` → `docker.md`
- `infraestructura/03-secrets-management.md` → ❌ Renombrar a `secrets-management.md` (sin 03-)
- `infraestructura/04-docker-compose.md` → `docker-compose.md`
- `observabilidad/01-logging.md` → `logging.md`
- `observabilidad/04-correlation-ids.md` → `correlation-ids.md`
- `observabilidad/05-health-checks.md` → `health-checks.md`
- `testing/01-unit-tests.md` → `unit-tests.md`
- `testing/02-integration-tests.md` → `integration-tests.md`

(Ya incluidos en Fase 1: apis/, mensajeria/)

---

### Fase 3: Eliminar duplicados (4 archivos)

1. ❌ ELIMINAR `apis/versionado.md` (mantener versioning.md de Fase 1)
2. ❌ ELIMINAR `datos/02-migrations.md` (mantener database-migrations.md)
3. ❌ ELIMINAR `documentacion/architecture-review.md` (mantener gobierno/architecture-review.md)
4. ❌ ELIMINAR `infraestructura/02-infraestructura-como-codigo.md` (mantener operabilidad/infrastructure-as-code.md)

---

### Fase 4: Mejorar nombres ambiguos (2 archivos)

- `mensajeria/dlq.md` → `dead-letter-queue.md`
- (Opcional) `operabilidad/slos-slas.md` → Mantener (las siglas son universalmente conocidas)

---

## 6. Resultado Esperado

### Antes (estado actual)

```
❌ 102 estándares
❌ 40% español, 60% inglés (INCONSISTENTE)
❌ 22 archivos numerados sin criterio
❌ 4 duplicados
```

### Después (propuesto)

```
✅ 98 estándares (eliminados 4 duplicados)
✅ 100% inglés (CONSISTENTE)
✅ 0 archivos numerados (nombres descriptivos)
✅ 0 duplicados
✅ Nomenclatura clara y profesional
```

---

## 7. Validación de Categorías

Las 12 categorías actuales son **ADECUADAS** y reflejan bien la estructura de una arquitectura corporativa:

1. ✅ **arquitectura/** - Patrones arquitectónicos
2. ✅ **apis/** - Diseño y governance de APIs
3. ✅ **datos/** - Gestión de datos y consistencia
4. ✅ **seguridad/** - Controles de seguridad
5. ✅ **mensajeria/** - Event-driven architecture
6. ✅ **testing/** - Estrategias de testing
7. ✅ **operabilidad/** - DevOps y operaciones
8. ✅ **infraestructura/** - IaC y cloud infrastructure
9. ✅ **gobierno/** - Governance y compliance
10. ✅ **observabilidad/** - Logging, monitoring, tracing
11. ✅ **documentacion/** - Estándares de documentación
12. ✅ **codigo/** - Estándares de código

**NO se requieren cambios en la estructura de categorías.**

---

## 8. Impacto de los Cambios

### Enlaces rotos

⚠️ **CRÍTICO:** Renombrar 66 archivos romperá referencias en:

- Lineamientos que referencian estándares
- README.md de cada categoría
- VALIDACION-COHERENCIA.md
- MATRIZ-TRAZABILIDAD.md
- Documentación ADRs

### Acciones necesarias post-renombrado

1. Actualizar todas las referencias `../../estandares/X.md` en lineamientos
2. Actualizar sidebars.ts (si aplica)
3. Validar con búsqueda global de nombres antiguos
4. Rebuild de Docusaurus

---

## 9. Decisión Requerida

**¿Proceder con el plan de normalización?**

- ✅ **SÍ** - Aplicar renombrado masivo (Fases 1-4)
- ⏸️ **PARCIAL** - Solo normalizar idioma (Fase 1)
- ❌ **NO** - Mantener status quo

**Tiempo estimado:** 2-3 horas (renombrado + actualización de referencias + validación)
