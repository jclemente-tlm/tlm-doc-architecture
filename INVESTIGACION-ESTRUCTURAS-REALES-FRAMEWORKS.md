# Investigación: Estructuras REALES de Lineamientos/Principles en Frameworks y Empresas

**Fecha:** 2 de febrero de 2026
**Objetivo:** Documentar las estructuras EXACTAS que usan frameworks y empresas reconocidas para documentar principios, lineamientos y guidelines.

---

## 1. TOGAF 10 - Architecture Principles

**Status:** No encontrado (requiere acceso con login)

**Observación:**

- El sitio oficial de TOGAF requiere autenticación para acceder al contenido completo del estándar
- Referencia: <https://pubs.opengroup.org/togaf-standard/architecture-content/chap08.html> (redirige a login)
- Documentación disponible públicamente es limitada

**Siguiente paso:**
Requeriría acceso licenciado a TOGAF Standard 10th Edition para obtener estructura exacta.

---

## 2. AWS Well-Architected Framework - Design Principles

**Estructura encontrada:** Por Pilar (no por principio individual)

### Organización General

- **6 Pilares:** Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability
- Cada pilar contiene **Design Principles** agrupados
- NO hay estructura estándar para CADA principio individual
- Los principios son **listados breves** dentro de cada pilar

### Formato típico de pilar

1. **Introduction** - Descripción del pilar
2. **Design Principles** - Lista de 5-7 principios (solo nombre y 1-2 párrafos)
3. **Best Practices** - Prácticas recomendadas detalladas
4. **Questions** - Para assessment
5. **Resources** - Referencias adicionales

### Ejemplo (Operational Excellence)

- Perform operations as code
- Make frequent, small, reversible changes
- Refine operations procedures frequently
- Anticipate failure
- Learn from all operational failures

**Total secciones por principio:** 1-2 (solo nombre + descripción breve)
**¿Incluye ejemplos?:** No directamente en principios
**¿Incluye trade-offs?:** No explícitamente
**¿Incluye antipatrones?:** No
**Longitud típica:** 1-3 párrafos por principio

**Referencia:** <https://aws.amazon.com/architecture/well-architected/>

---

## 3. Azure Well-Architected Framework - Design Principles

**Estructura encontrada:** TABLA DE RECOMENDACIONES por principio

### Estructura EXACTA (Reliability Pillar)

Cada "Design Principle" contiene:

1. **Principle Name** (ej: "Design for business requirements")
2. **Tabla con 2 columnas:**
   - **Column 1: Recommendation** - Lista de recomendaciones específicas
   - **Column 2: Benefit** - Beneficio de cada recomendación

### Secciones principales encontradas

1. **Design for business requirements**
2. **Design for resilience**
3. **Design for recovery**
4. **Design for operations**
5. **Keep it simple**

### Ejemplo REAL (Design for resilience)

| Recommendation                                                                                        | Benefit                                                                                                                                 |
| ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Distinguish components that are on the critical path from those that can function in a degraded state | Not all components need to be equally reliable. Determining criticality helps you design according to the criticality of each component |
| Identify potential failure points in the system, especially for the critical components               | You can analyze failure cases, blast radius, and intensity of fault                                                                     |
| Build self-preservation capabilities by using design patterns correctly                               | The system will be able to prevent a problem from affecting downstream components                                                       |

**Total secciones por principio:** 1 tabla con múltiples filas
**¿Incluye ejemplos?:** Sí (integrados en recomendaciones)
**¿Incluye trade-offs?:** Sí (implícitos en beneficios vs costos)
**¿Incluye antipatrones?:** No directamente
**Longitud típica:** 5-10 recomendaciones por principio

**Referencia:** <https://learn.microsoft.com/en-us/azure/well-architected/reliability/principles>

---

## 4. Google Cloud Architecture Framework

**Status:** Requiere acceso adicional

**Observación:**

- URL redirige a docs.cloud.google.com (requiere navegación adicional)
- No se pudo obtener estructura específica sin navegación profunda
- Framework existe pero estructura exacta no accesible en búsqueda inicial

**Referencia:** <https://cloud.google.com/architecture/framework>

---

## 5. Google SRE Book - Principles

**Estructura encontrada:** NARRATIVE + SECTIONS

### Estructura EXACTA (Ejemplo: "Embracing Risk")

**Secciones principales:**

1. **Introduction narrative** (sin título formal)
2. **Managing Risk**
3. **Measuring Service Risk**
   - Time-based availability
   - Aggregate availability
4. **Risk Tolerance of Services**
   - Identifying the Risk Tolerance of Consumer Services
     - Target level of availability
     - Types of failures
     - Cost
     - Other service metrics
   - Identifying the Risk Tolerance of Infrastructure Services
5. **Motivation for Error Budgets**
   - Forming Your Error Budget
   - Benefits
   - **Key Insights** (bullet points)

### Ejemplo REAL (Monitoring Distributed Systems)

**Secciones:**

1. **Definitions** - Glosario de términos
2. **Why Monitor?** - Propósito
3. **Setting Reasonable Expectations for Monitoring** - Contexto
4. **Symptoms Versus Causes** - Conceptos clave
5. **Black-Box Versus White-Box** - Enfoques
6. **The Four Golden Signals** - Core principles
7. **Worrying About Your Tail** - Detalles técnicos
8. **Choosing an Appropriate Resolution** - Implementación
9. **As Simple as Possible, No Simpler** - Filosofía
10. **Tying These Principles Together** - Integración
11. **Monitoring for the Long Term** - Casos de estudio
    - Bigtable SRE: A Tale of Over-Alerting
    - Gmail: Predictable, Scriptable Responses
    - The Long Run
12. **Conclusion** - Resumen

**Total secciones:** 10-12 secciones por capítulo/principio
**¿Incluye ejemplos?:** Sí (casos de estudio extensos de Google)
**¿Incluye trade-offs?:** Sí (explícitamente discutidos)
**¿Incluye antipatrones?:** Sí (ejemplos de qué NO hacer)
**Longitud típica:** 15-30 páginas por principio/capítulo

**Referencia:** <https://sre.google/sre-book/table-of-contents/>

---

## 6. ISO/IEC 42010 - Architecture Description

**Estructura encontrada:** ESTÁNDAR FORMAL

### Información obtenida

- Es un **estándar internacional** para descripción de arquitecturas
- Define **requisitos** para describir arquitecturas de sistemas, software y enterprise
- Hace distinción estricta entre:
  - **Architecture** (la cosa en sí)
  - **Architecture Description** (la documentación)

### Conceptos clave mencionados

- **Architecture rationale** - Justificación de decisiones
- **Architecture frameworks** - Marcos de trabajo
- **Architecture description languages** - Lenguajes de descripción
- **Architecture decisions** - Captura de decisiones
- **Correspondences** - Consistencia entre modelos y vistas

**Total secciones:** No especificado (es un estándar completo)
**¿Incluye ejemplos?:** Probable (estándares ISO suelen incluir ejemplos)
**¿Incluye trade-offs?:** Sí (implícito en decisiones arquitectónicas)
**¿Incluye antipatrones?:** No encontrado
**Longitud típica:** Estándar completo (documento formal)

**Referencia:** <https://www.iso.org/standard/74393.html> (ISO/IEC/IEEE 42010:2022)

---

## 7. Netflix Engineering Culture

**Estructura encontrada:** VALORES ORGANIZACIONALES

### Estructura EXACTA

**4 Core Principles:**

1. **THE DREAM TEAM**
2. **PEOPLE OVER PROCESS**
3. **UNCOMFORTABLY EXCITING**
4. **GREAT AND ALWAYS BETTER**

### Dentro de cada principio

- **Narrative explanation** (varios párrafos)
- **Values list** (para Dream Team):
  - SELFLESSNESS
  - JUDGMENT
  - CANDOR
  - CREATIVITY
  - COURAGE
  - INCLUSION
  - CURIOSITY
  - RESILIENCE

### Formato de cada valor

- **Nombre del valor**
- **1-2 frases** describiendo el comportamiento esperado

### Ejemplo REAL

```
SELFLESSNESS
You are humble when searching for the best ideas; you seek what's best for
Netflix, not yourself or your team; you take time to help others succeed.

JUDGMENT
You look beyond short term fixes in favor of long term solutions; you make wise
decisions despite ambiguity; you use data to inform your intuition.
```

**Total secciones:** 4 principios + 8 valores
**¿Incluye ejemplos?:** Sí (narrativos, integrados en texto)
**¿Incluye trade-offs?:** Sí (discutidos narrativamente)
**¿Incluye antipatrones?:** Sí (qué NO es Netflix culture)
**Longitud típica:** 2-5 párrafos por principio + valores listados

**Referencia:** <https://jobs.netflix.com/culture>

---

## 8. Spotify Engineering Principles

**Status:** No encontrado como documento formal

**Observación:**

- Sitio de diseño disponible (spotify.design)
- Sitio de ingeniería disponible (engineering.atspotify.com)
- NO se encontró documento formal de "Engineering Principles"
- Publican blog posts sobre prácticas específicas
- No estructura estandarizada para principios

**Referencia:** <https://engineering.atspotify.com/>

---

## 9. Airbnb Engineering Principles

**Status:** No encontrado como documento formal

**Observación:**

- Blog técnico en Medium disponible
- Publican artículos sobre tecnología y prácticas
- NO se encontró documento formal de "Engineering Principles" público
- Contenido es principalmente en forma de artículos técnicos

**Referencia:** <https://medium.com/airbnb-engineering>

---

## 10. Microsoft Engineering Fundamentals

**Estructura encontrada:** PLAYBOOK CON CHECKLIST

### Estructura EXACTA

**Organización:**

- **Engineering Fundamentals Playbook**
- **Secciones principales:**
  1. Why Have a Playbook
  2. General Guidance (bullet points)
  3. Topical sections:
     - Agile Development
     - Automated Testing
     - CI/CD
     - Code Reviews
     - Design
     - Documentation
     - Observability
     - Security
     - Source Control
     - etc.

### Formato típico de cada tema

- **Overview/Introduction**
- **Best Practices** (bullet lists)
- **Recipes** (how-to guides)
- **Tools** (recommended tooling)
- **Checklists** (verification)

### Ejemplo REAL (General Guidance)

```
• Keep the code quality bar high.
• Value quality and precision over 'getting things done'.
• Work diligently on the one important thing.
• As a distributed team take time to share context via wiki, teams and backlog items.
• Make the simple thing work now. Build fewer features today, but ensure they work
  amazingly. Then add more features tomorrow.
• Avoid adding scope to a backlog item, instead add a new backlog item.
• Our goal is to ship incremental customer value.
```

**Total secciones:** 15+ áreas temáticas
**¿Incluye ejemplos?:** Sí (recipes y templates)
**¿Incluye trade-offs?:** Sí (en secciones específicas)
**¿Incluye antipatrones?:** Sí (implícitos en best practices)
**Longitud típica:** 1-5 páginas por tema

**Referencia:** <https://microsoft.github.io/code-with-engineering-playbook/>

---

## TABLA COMPARATIVA FINAL

| Framework/Empresa | Secciones     | Ejemplos   | Trade-offs     | Antipatrones  | Longitud típica      | Formato                      |
| ----------------- | ------------- | ---------- | -------------- | ------------- | -------------------- | ---------------------------- |
| **TOGAF 10**      | No encontrado | ?          | ?              | ?             | ?                    | Estándar formal              |
| **AWS WAF**       | 1-2           | No directo | No             | No            | 1-3 párrafos         | Lista narrativa              |
| **Azure WAF**     | 1 (tabla)     | Sí         | Sí (implícito) | No            | 5-10 recomendaciones | Tabla Recommendation/Benefit |
| **Google Cloud**  | No accesible  | ?          | ?              | ?             | ?                    | ?                            |
| **Google SRE**    | 10-12         | Sí         | Sí             | Sí            | 15-30 páginas        | Narrative + subsecciones     |
| **ISO/IEC 42010** | Múltiples     | Probable   | Sí             | No encontrado | Documento completo   | Estándar ISO                 |
| **Netflix**       | 4+8 valores   | Sí         | Sí             | Sí            | 2-5 párrafos         | Narrativo + valores          |
| **Spotify**       | No encontrado | -          | -              | -             | -                    | Blog posts                   |
| **Airbnb**        | No encontrado | -          | -              | -             | -                    | Blog posts                   |
| **Microsoft**     | 15+ temas     | Sí         | Sí             | Sí            | 1-5 páginas          | Playbook + checklist         |

---

## HALLAZGOS CLAVE

### Patrones Identificados

1. **Formato Narrativo (Google SRE, Netflix)**
   - Explicación extensa con storytelling
   - Casos de estudio reales
   - Múltiples subsecciones
   - Trade-offs explícitos

2. **Formato Tabla (Azure WAF)**
   - Recomendación + Beneficio
   - Conciso y escaneable
   - Trade-offs implícitos
   - Orientado a acción

3. **Formato Lista (AWS WAF)**
   - Nombre + descripción breve
   - Sin estructura profunda
   - Agrupados por pilar
   - Conciso

4. **Formato Playbook (Microsoft)**
   - Guidance + Checklists
   - Múltiples áreas temáticas
   - Orientado a práctica
   - Recipes y templates

### Elementos comunes encontrados

✅ **Nombre del principio**
✅ **Descripción/Explicación**
✅ **Ejemplos** (en formatos narrativos)
⚠️ **Trade-offs** (solo en formatos extensos)
⚠️ **Antipatrones** (solo Google SRE y Netflix lo hacen explícito)
❌ **Estructura estándar universal** - NO EXISTE

### Lo que NO hacen

- ❌ Incluir "Contexto" como sección separada (está integrado)
- ❌ Sección formal de "Rationale" (excepto ISO/IEC 42010)
- ❌ Antipatrones como sección estándar
- ❌ Métricas de éxito por principio
- ❌ Referencias cruzadas formales

---

## CONCLUSIONES

### Para documentación de Lineamientos/Principles

**Formato MINIMALISTA (AWS):**

- Nombre + 1-2 párrafos
- Sin subsecciones
- Agrupados por categoría

**Formato TABLA (Azure):**

- Tabla Recomendación/Beneficio
- Altamente escaneable
- Orientado a acción directa

**Formato EXTENSO (Google SRE):**

- Capítulo completo
- Múltiples subsecciones
- Ejemplos reales extensos
- Trade-offs y antipatrones

**Formato CULTURAL (Netflix):**

- Narrativo
- Valores + comportamientos
- Ejemplos integrados
- "Qué NO somos"

### Recomendación según contexto

- **Lineamientos técnicos:** Azure (Tabla) o AWS (Lista breve)
- **Principios de ingeniería:** Google SRE (Extenso con ejemplos)
- **Principios culturales:** Netflix (Narrativo + valores)
- **Guías de práctica:** Microsoft (Playbook + checklist)

### NO existe un estándar universal

La longitud, estructura y profundidad dependen de:

1. **Audiencia** (desarrolladores vs arquitectos vs líderes)
2. **Objetivo** (cultural vs técnico vs normativo)
3. **Contexto de uso** (referencia vs aprendizaje vs compliance)

---

**Fecha de investigación:** 2 de febrero de 2026
**Fuentes:** Sitios oficiales de cada framework/empresa
**Limitaciones:** Algunos contenidos requieren autenticación o no están públicamente disponibles
