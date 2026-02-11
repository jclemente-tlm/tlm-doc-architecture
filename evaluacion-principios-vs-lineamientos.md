# Evaluación: ¿Qué son Principios vs Lineamientos?

## 📚 Marco Conceptual

### ¿Qué es un PRINCIPIO?

**Valor fundamental, universal, atemporal**

- Declara **VALORES** o **CREENCIAS** sobre cómo debe ser el sistema
- Es **filosófico**, no técnico
- **Atemporal** - No depende de tecnología específica
- **Universal** - Aplica independiente del contexto técnico
- **Orientativo** - Guía decisiones, no dicta implementación

**Ejemplo:** "La seguridad debe considerarse desde el diseño" → Es un valor

### ¿Qué es un LINEAMIENTO?

**Regla práctica, técnica, contextual**

- Declara **CÓMO** implementar los valores (principios)
- Es **prescriptivo** - Da directrices concretas
- **Contextual** - Depende de tecnología, estilo arquitectónico
- **Práctico** - Puede obsoletizarse con el tiempo
- **Específico** - Detalla decisiones técnicas

**Ejemplo:** "Los servicios deben tener su propia base de datos" → Es una regla técnica

---

## 🔍 Análisis de tus 12 "Principios" Actuales

### ARQUITECTURA (7)

| #   | Título                                | ¿Es Principio? | Evaluación                                                                                |
| --- | ------------------------------------- | -------------- | ----------------------------------------------------------------------------------------- |
| 1   | **Arquitectura Limpia**               | ✅ **SÍ**      | **PRINCIPIO** - Valor fundamental: separar negocio de tecnología. Atemporal, filosófico.  |
| 2   | **DDD**                               | ⚠️ **DUDOSO**  | **ENFOQUE/METODOLOGÍA** - Es más un enfoque técnico que un valor. Podría ser lineamiento. |
| 3   | **Bajo Acoplamiento**                 | ✅ **SÍ**      | **PRINCIPIO** - Valor fundamental: minimizar dependencias. Universal, atemporal.          |
| 4   | **Autonomía de Servicios**            | ❌ **NO**      | **LINEAMIENTO** - Regla técnica específica para microservicios. Contextual, no universal. |
| 5   | **Arquitectura Evolutiva**            | ✅ **SÍ**      | **PRINCIPIO** - Valor fundamental: diseñar para el cambio. Filosófico, atemporal.         |
| 6   | **Simplicidad Intencional**           | ✅ **SÍ**      | **PRINCIPIO** - Valor fundamental: evitar sobreingeniería. Filosófico, universal.         |
| 7   | **Resiliencia y Tolerancia a Fallos** | ✅ **SÍ**      | **PRINCIPIO** - Valor fundamental: asumir fallos. Universal, atemporal.                   |

### DATOS (1)

| #   | Título                 | ¿Es Principio? | Evaluación                                                                               |
| --- | ---------------------- | -------------- | ---------------------------------------------------------------------------------------- |
| 8   | **Propiedad de Datos** | ❌ **NO**      | **LINEAMIENTO** - Regla técnica: "database per service". Específico para microservicios. |

### SEGURIDAD (4)

| #   | Título                        | ¿Es Principio? | Evaluación                                                                                |
| --- | ----------------------------- | -------------- | ----------------------------------------------------------------------------------------- |
| 9   | **Seguridad desde el Diseño** | ✅ **SÍ**      | **PRINCIPIO** - Valor fundamental: pensar seguridad desde el inicio. Filosófico.          |
| 10  | **Zero Trust**                | ⚠️ **DUDOSO**  | **ENFOQUE/MODELO** - Es un modelo de seguridad, no solo un valor. Podría ser lineamiento. |
| 11  | **Defensa en Profundidad**    | ⚠️ **DUDOSO**  | **ESTRATEGIA** - Es una estrategia técnica, no un valor puro. Podría ser lineamiento.     |
| 12  | **Mínimo Privilegio**         | ✅ **SÍ**      | **PRINCIPIO** - Valor fundamental: restringir accesos. Universal, atemporal.              |

---

## 📊 Resultado del Análisis

### Clasificación Final

#### ✅ **SON PRINCIPIOS PUROS** (7)

**ARQUITECTURA (5)**

1. ✅ Arquitectura Limpia
2. ✅ Bajo Acoplamiento
3. ✅ Arquitectura Evolutiva
4. ✅ Simplicidad Intencional
5. ✅ Resiliencia y Tolerancia a Fallos

**SEGURIDAD (2)** 6. ✅ Seguridad desde el Diseño 7. ✅ Mínimo Privilegio

---

#### ⚠️ **ENFOQUES/MODELOS** (Frontera difusa - podrían ser principios o lineamientos)

**ARQUITECTURA (1)**

- ⚠️ **DDD (Diseño Orientado al Dominio)**
  - **Problema**: Es más una **metodología/enfoque** que un valor puro
  - **Razón para mantener**: Si lo reescribes como "El diseño debe reflejar el dominio del negocio" es un principio
  - **Decisión**: Podría quedarse si se reformula como valor, no como metodología

**SEGURIDAD (2)**

- ⚠️ **Zero Trust**
  - **Problema**: Es un **modelo de seguridad** específico, no solo un valor
  - **Razón para mantener**: Declara un valor fundamental ("nunca confiar por defecto")
  - **Decisión**: Frontera difusa

- ⚠️ **Defensa en Profundidad**
  - **Problema**: Es una **estrategia técnica** (capas múltiples)
  - **Razón para mantener**: Declara un valor ("no depender de un solo control")
  - **Decisión**: Frontera difusa

---

#### ❌ **SON LINEAMIENTOS TÉCNICOS** (2)

Estos **NO** son principios puros, son **reglas técnicas específicas**:

**ARQUITECTURA (1)**

- ❌ **Autonomía de Servicios**
  - **Por qué**: Regla específica para **microservicios**
  - **No es universal**: No aplica a monolitos
  - **Es prescriptivo**: Dicta cómo diseñar servicios
  - **Debe moverse a**: `lineamientos/arquitectura/`
  - **Justificación**: "Cada servicio con su base de datos" es una regla técnica, no un valor fundamental

**DATOS (1)**

- ❌ **Propiedad de Datos**
  - **Por qué**: Regla técnica: "database per service pattern"
  - **No es universal**: Solo aplica en arquitecturas distribuidas
  - **Es prescriptivo**: Dicta cómo gestionar bases de datos
  - **Debe moverse a**: `lineamientos/datos/`
  - **Justificación**: Es una implementación del principio más general de "Autonomía"

---

## 🎯 Recomendaciones

### Opción A: **PURISTA** (Mantener solo principios fundamentales)

**Principios que quedan (7):**

```
principios/
├── arquitectura/
│   ├── 01-arquitectura-limpia.md ✅
│   ├── 02-bajo-acoplamiento.md ✅ (renombrado de 03)
│   ├── 03-arquitectura-evolutiva.md ✅ (renombrado de 05)
│   ├── 04-simplicidad-intencional.md ✅ (renombrado de 06)
│   └── 05-resiliencia-y-tolerancia-a-fallos.md ✅ (renombrado de 07)
│
└── seguridad/
    ├── 01-seguridad-desde-el-diseno.md ✅
    └── 02-minimo-privilegio.md ✅ (renombrado de 04)
```

**Lineamientos que se agregan (4):**

```
lineamientos/
├── arquitectura/
│   ├── 01-diseno-orientado-al-dominio.md ➕ (movido de principios)
│   ├── 02-autonomia-de-servicios.md ➕ (movido de principios)
│   └── ...existentes
│
├── datos/
│   ├── 01-propiedad-de-datos.md ➕ (movido de principios)
│   └── ...existentes
│
└── seguridad/
    ├── 06-zero-trust.md ➕ (movido de principios)
    ├── 07-defensa-en-profundidad.md ➕ (movido de principios)
    └── ...existentes
```

**Resultado:**

- ✅ **7 principios puros** (solo valores fundamentales)
- ✅ Separación conceptual perfecta
- ✅ Mantiene 4 conceptos importantes como lineamientos

---

### Opción B: **PRAGMÁTICO** (Mantener frontera difusa)

**Principios que quedan (10):**

```
principios/
├── arquitectura/
│   ├── 01-arquitectura-limpia.md ✅
│   ├── 02-diseno-orientado-al-dominio.md ⚠️ (reformular como valor)
│   ├── 03-bajo-acoplamiento.md ✅
│   ├── 04-arquitectura-evolutiva.md ✅
│   ├── 05-simplicidad-intencional.md ✅
│   └── 06-resiliencia-y-tolerancia-a-fallos.md ✅
│
└── seguridad/
    ├── 01-seguridad-desde-el-diseno.md ✅
    ├── 02-zero-trust.md ⚠️ (reformular como valor)
    ├── 03-defensa-en-profundidad.md ⚠️ (reformular como valor)
    └── 04-minimo-privilegio.md ✅
```

**Lineamientos que se agregan (2):**

```
lineamientos/
├── arquitectura/
│   ├── ...autonomia-de-servicios.md ➕ (movido de principios)
│   └── ...existentes
│
└── datos/
    ├── ...propiedad-de-datos.md ➕ (movido de principios)
    └── ...existentes
```

**Resultado:**

- ✅ **10 principios** (algunos en frontera)
- ⚠️ Menos pureza conceptual
- ✅ Mantiene Zero Trust, DDD como principios (con reformulación)

---

### Opción C: **MÍNIMO** (Solo mover los 2 claramente técnicos)

**Principios que quedan (10):**

```
principios/
├── arquitectura/
│   ├── 01-arquitectura-limpia.md ✅
│   ├── 02-diseno-orientado-al-dominio.md ⚠️
│   ├── 03-bajo-acoplamiento.md ✅
│   ├── 04-arquitectura-evolutiva.md ✅
│   ├── 05-simplicidad-intencional.md ✅
│   └── 06-resiliencia-y-tolerancia-a-fallos.md ✅
│
└── seguridad/
    ├── 01-seguridad-desde-el-diseno.md ✅
    ├── 02-zero-trust.md ⚠️
    ├── 03-defensa-en-profundidad.md ⚠️
    └── 04-minimo-privilegio.md ✅
```

**Solo mover los 2 claramente técnicos:**

```
lineamientos/
├── arquitectura/
│   ├── ...autonomia-de-servicios.md ➕
│   └── ...existentes
│
└── datos/
    ├── ...propiedad-de-datos.md ➕
    └── ...existentes
```

---

## 🔥 Mi Recomendación: **Opción A (PURISTA)**

### ¿Por qué?

1. **Claridad conceptual máxima**
   - Los principios quedan como **valores puros**
   - Los lineamientos como **reglas técnicas**
   - Separación cristalina

2. **Coherencia con tu modelo de 3 niveles**
   - Ya tienes `principios/` → `lineamientos/` → `estándares/`
   - Aprovecha esa estructura limpia

3. **DDD, Zero Trust, Defensa en Profundidad son valiosos**
   - No los pierdes, solo los reclasificas
   - Como lineamientos siguen siendo importantes
   - De hecho, ganan especificidad técnica

4. **7 principios es un número ideal**
   - Fácil de recordar
   - Fácil de comunicar
   - Cada uno es indiscutiblemente fundamental

### Resultado Final con Opción A:

```
✅ 7 PRINCIPIOS FUNDAMENTALES
═════════════════════════════

ARQUITECTURA (5 principios):
1. Arquitectura Limpia
2. Bajo Acoplamiento
3. Arquitectura Evolutiva
4. Simplicidad Intencional
5. Resiliencia y Tolerancia a Fallos

SEGURIDAD (2 principios):
6. Seguridad desde el Diseño
7. Mínimo Privilegio

═════════════════════════════
+ 26 LINEAMIENTOS (22 actuales + 4 nuevos)

arquitectura/: DDD, Autonomía (+ existentes)
datos/: Propiedad de Datos (+ existentes)
seguridad/: Zero Trust, Defensa en Profundidad (+ existentes)
```

---

## ✅ Plan de Acción (Opción A)

### Paso 1: Mover archivos a lineamientos

```bash
# Mover principios que son lineamientos
mv docs/fundamentos-corporativos/principios/arquitectura/02-diseno-orientado-al-dominio.md \
   docs/fundamentos-corporativos/lineamientos/arquitectura/08-diseno-orientado-al-dominio.md

mv docs/fundamentos-corporativos/principios/arquitectura/04-autonomia-de-servicios.md \
   docs/fundamentos-corporativos/lineamientos/arquitectura/09-autonomia-de-servicios.md

mv docs/fundamentos-corporativos/principios/datos/01-propiedad-de-datos.md \
   docs/fundamentos-corporativos/lineamientos/datos/03-propiedad-de-datos.md

mv docs/fundamentos-corporativos/principios/seguridad/02-zero-trust.md \
   docs/fundamentos-corporativos/lineamientos/seguridad/06-zero-trust.md

mv docs/fundamentos-corporativos/principios/seguridad/03-defensa-en-profundidad.md \
   docs/fundamentos-corporativos/lineamientos/seguridad/07-defensa-en-profundidad.md
```

### Paso 2: Renumerar principios restantes

```
arquitectura/
├── 01-arquitectura-limpia.md
├── 02-bajo-acoplamiento.md (antes 03)
├── 03-arquitectura-evolutiva.md (antes 05)
├── 04-simplicidad-intencional.md (antes 06)
└── 05-resiliencia-y-tolerancia-a-fallos.md (antes 07)

seguridad/
├── 01-seguridad-desde-el-diseno.md
└── 02-minimo-privilegio.md (antes 04)
```

### Paso 3: Actualizar referencias cruzadas

- Actualizar links en otros documentos
- Actualizar `_category_.json`
- Actualizar sidebar

---

**¿Qué opción prefieres? ¿Opción A (7 principios puros) o alguna de las otras?**
