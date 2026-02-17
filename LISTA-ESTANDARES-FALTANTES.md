# Lista de Estándares Faltantes - Plan de Creación

## 🔴 PRIORIDAD 1 - CRÍTICO (Crear esta semana)

### 1. seguridad/data-protection.md

**Referencias:** 6 veces en seguridad/07-proteccion-de-datos.md

**Contenido requerido:**

- Clasificación de datos (público, interno, sensible, regulado)
- Cifrado en tránsito y reposo
- Enmascaramiento y tokenización
- Integración con KMS (AWS Secrets Manager)
- Minimización de datos
- Políticas de retención y eliminación

**Secciones específicas referenciadas:**

- `#classification`
- `#encryption`

---

### 2. operabilidad/disaster-recovery.md

**Referencias:** 5 veces en operabilidad/04-disaster-recovery.md
**Contenido requerido:**

- Definición de objetivos RPO/RTO por sistema
- Estrategia de backups automatizados

- Procedimientos de restauración
- Runbooks actualizados
- Simulacros periódicos

**Secciones específicas referenciadas:**

- `#definicion-de-objetivos`
- `#estrategia-de-backups`
- `#pruebas-de-recuperacion`

- `#documentacion-de-procedimientos`

- `#simulacros`

---

### 3. gobierno/architecture-review.md

**Referencias:** 3 veces

- gobierno/02-revisiones-arquitectonicas.md
- gobierno/01-decisiones-arquitectonicas.md
- arquitectura/01-estilo-y-enfoque-arquitectonico.md

**Contenido requerido:**

- Proceso de architecture review

- Cuándo realizar reviews
- Checklist de validación
- Participantes y roles
- Documentación de resultados

---

### 4. desarrollo/repositorios.md

**Referencias:** 3 veces

- desarrollo/04-control-versiones.md
- desarrollo/03-documentacion-tecnica.md

- operabilidad/02-infraestructura-como-codigo.md

**Contenido requerido:**

- Estrategia de branching (Git Flow, Trunk-based)
- Commits semánticos (Conventional Commits)
- Versionado de artefactos (SemVer)
- Estructura obligatoria del README
- Protección de ramas
- Políticas de merge

**Secciones específicas referenciadas:**

- `#estrategia-de-branching`

- `#commits-semanticos`
- `#versionado-de-artefactos`
- `#estructura-obligatoria-del-readme`

---

## ⚡ PRIORIDAD 2 - ALTA (Próxima iteración)

### 5. gobierno/review-documentation.md

**Referencias:** gobierno/02-revisiones-arquitectonicas.md
**Contenido:** Cómo documentar resultados de reviews

### 6. gobierno/architecture-retrospectives.md

**Referencias:** gobierno/02-revisiones-arquitectonicas.md

**Contenido:** Retrospectivas post-implementación

### 7. gobierno/compliance-validation.md

**Referencias:** gobierno/03-cumplimiento-y-excepciones.md
**Contenido:** Validación de cumplimiento de lineamientos

### 8. gobierno/exception-management.md

**Referencias:** gobierno/03-cumplimiento-y-excepciones.md
**Contenido:** Proceso formal de excepciones con ADR

### 9. seguridad/security-by-design.md

**Referencias:** seguridad/01-seguridad-desde-el-diseno.md
**Contenido:** Aplicar seguridad desde diseño

### 10. seguridad/environment-separation.md

**Referencias:** seguridad/06-segmentacion-y-aislamiento.md

**Contenido:** Aislamiento de entornos en cuentas separadas

### 11. seguridad/security-zones.md

**Referencias:** seguridad/06-segmentacion-y-aislamiento.md
**Contenido:** Documentación de zonas de seguridad

### 12. seguridad/trust-boundaries.md

**Referencias:** seguridad/01-seguridad-desde-el-diseno.md
**Contenido:** Definición de límites de confianza

### 13. seguridad/attack-surface-reduction.md

**Referencias:** seguridad/01-seguridad-desde-el-diseno.md
**Contenido:** Reducir superficie de ataque

---

## 📋 PRIORIDAD 3 - MEDIA

### 14. arquitectura/stateless-services.md

**Referencias:** arquitectura/03-cloud-native.md
**Contenido:** Diseño de servicios stateless

### 15. arquitectura/horizontal-scaling.md

**Referencias:** arquitectura/03-cloud-native.md
**Contenido:** Escalabilidad horizontal

### 16. arquitectura/single-responsibility.md

**Referencias:** arquitectura/02-descomposicion-y-limites.md
**Contenido:** Responsabilidad única por componente

### 17. observabilidad/health-checks.md

**Referencias:** arquitectura/03-cloud-native.md
**Contenido:** Implementación de health checks (liveness/readiness)
**Nota:** Podría ser una sección en observability.md

### 18. apis/openapi-specification.md

**Referencias:** desarrollo/03-documentacion-tecnica.md
**Contenido:** Especificación de APIs con OpenAPI 3.0+

---

## 🔄 DUPLICADOS A RESOLVER (Actualizar referencias)

### ❌ Referencias que apuntan a ubicaciones incorrectas

1. **ADR: arquitectura/ vs documentacion/**
   - ❌ `arquitectura/architectural-decision-records.md`
   - ✅ Existe: `documentacion/architecture-decision-records.md`
   - **Acción:** Actualizar referencia en desarrollo/03-documentacion-tecnica.md

2. **arc42: arquitectura/ vs documentacion/**
   - ❌ `arquitectura/arc42.md`
   - ✅ Existe: `documentacion/arc42.md`
   - **Acción:** Actualizar referencia en desarrollo/03-documentacion-tecnica.md

3. **C4 Model: arquitectura/ vs documentacion/**
   - ❌ `arquitectura/c4-model.md`
   - ✅ Existe: `documentacion/c4-model.md`
   - **Acción:** Actualizar referencia en desarrollo/03-documentacion-tecnica.md

4. **Data Protection: seguridad/ vs datos/**
   - ❌ `seguridad/data-protection.md`
   - ✅ Existe: `datos/data-protection.md`
   - **Decisión:** ¿Mover a seguridad/ o actualizar referencias?
   - **Referencias:** 6 veces en seguridad/07-proteccion-de-datos.md

5. **Container Scanning: nombres diferentes**
   - ❌ `seguridad/container-image-scanning.md`
   - ✅ Existe: `seguridad/container-scanning.md`
   - **Acción:** Actualizar referencia en seguridad/08-gestion-vulnerabilidades.md

---

## ➕ SECCIONES FALTANTES EN ARCHIVOS EXISTENTES

### testing/testing-standards.md

**Faltan secciones:**

- `#contract-tests` - Referenciado en arquitectura/07-apis-y-contratos.md

**Acción:** Agregar sección sobre contract testing (Pact, etc.)

---

## 📂 Estructura de Carpetas Actual

```

estandares/
├── apis/              (1 archivo)
├── arquitectura/      (4 archivos)
├── datos/             (2 archivos)

├── desarrollo/        (7 archivos)
├── documentacion/     (3 archivos) ← arc42, ADR, C4
├── infraestructura/   (4 archivos)
├── mensajeria/        (1 archivo)

├── observabilidad/    (1 archivo)
├── seguridad/         (9 archivos)
└── testing/           (1 archivo)
```

### Carpeta FALTANTE a crear

```

estandares/
└── gobierno/          (0 archivos) ← CREAR CARPETA
    ├── architecture-review.md
    ├── review-documentation.md
    ├── architecture-retrospectives.md
    ├── compliance-validation.md
    └── exception-management.md
```

---

## 🎯 Orden de Ejecución Recomendado

### Día 1

- [ ] Crear carpeta `gobierno/`
- [ ] Crear `seguridad/data-protection.md` (o mover desde datos/)

### Día 2

- [ ] Crear `operabilidad/disaster-recovery.md`
- [ ] Crear `gobierno/architecture-review.md`

### Día 3

- [ ] Crear `desarrollo/repositorios.md`
- [ ] Resolver duplicados (actualizar 5 referencias)

### Día 4

- [ ] Crear estándares de gobierno restantes (review-documentation, retrospectives)
- [ ] Agregar sección `#contract-tests` a testing-standards.md

### Día 5

- [ ] Validación con script
- [ ] Review de coherencia
- [ ] Documentar en README

---

## 🛠️ Comandos Útiles

**Crear carpeta gobierno:**

```bash
mkdir -p docs/fundamentos-corporativos/estandares/gobierno
```

**Validar después de crear archivos:**

```bash
./scripts/validar-referencias-estandares.sh
```

**Buscar todas las referencias a un estándar específico:**

```bash
grep -r "data-protection.md" docs/fundamentos-corporativos/lineamientos/
```

**Listar lineamientos sin referencias:**

```bash
grep -L "../../estandares/" docs/fundamentos-corporativos/lineamientos/*/*.md
```

---

## 📊 Progreso Tracking

**Meta:** 44 estándares faltantes + 5 duplicados = 49 items

- [ ] Prioridad 1: 4 estándares (0/4)
- [ ] Prioridad 2: 9 estándares (0/9)
- [ ] Prioridad 3: 5 estándares (0/5)
- [ ] Duplicados: 5 referencias (0/5)
- [ ] Secciones: 1 sección (0/1)
- [ ] Otros: 26 estándares (evaluar necesidad)

**Total:** 0/49 (0%)

---

> **Próximo paso:** Comenzar con los 4 estándares críticos de Prioridad 1
