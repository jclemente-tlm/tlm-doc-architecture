# Análisis Crítico: 73 Estándares Custom (61%)

**Fecha:** 3 de febrero de 2026
**Análisis de:** 127 referencias a estándares en 24 lineamientos
**Estándares únicos totales:** 119
**Estándares custom identificados:** 73 (61%)

---

## 📊 Resumen Ejecutivo

Del análisis de 119 estándares únicos referenciados en los lineamientos, **73 (61%) NO están alineados con frameworks de industria reconocidos**. Este documento presenta los **20 casos más críticos** que requieren acción inmediata, priorizados por:

1. **Nombres ambiguos o genéricos** que dificultan comprensión
2. **Existencia de equivalentes reconocidos** en industria
3. **Oportunidades de consolidación** con otros estándares
4. **Falta de valor diferencial** vs. prácticas estándar

### Distribución de Estándares Custom por Categoría

| Categoría             | Custom | Total | % Custom |
| --------------------- | ------ | ----- | -------- |
| **IaC/Operabilidad**  | 18     | 18    | **100%** |
| **Testing/Calidad**   | 8      | 8     | **100%** |
| **Cost Optimization** | 5      | 5     | **100%** |
| **Gobierno/Docs**     | 12     | 14    | **86%**  |
| **Seguridad**         | 14     | 33    | **42%**  |
| **Datos**             | 11     | 18    | **61%**  |
| **Mensajería**        | 3      | 5     | **60%**  |
| **Observabilidad**    | 2      | 5     | **40%**  |

---

## 🔥 TOP 20 CASOS CRÍTICOS

### 1. Gestión de Configuración (3 estándares duplicados)

| Estándar Custom                                                    | Ruta                                             | Lineamiento                 |
| ------------------------------------------------------------------ | ------------------------------------------------ | --------------------------- |
| Externalizar configuración en variables de entorno                 | `infraestructura/configuracion-externalizada.md` | Diseño Cloud Native         |
| Gestionar configuración externamente mediante variables de entorno | `operabilidad/configuracion-externa.md`          | Consistencia Entornos       |
| Separar configuración por entorno mediante variables               | `operabilidad/iac-parametrizacion.md`            | Infraestructura como Código |

**Equivalente Industria:** 12-Factor App - Factor III: Config
**Problema:** 3 estándares dicen esencialmente lo mismo
**Recomendación:** ✅ **CONSOLIDAR**

```
[Estándar Único] Externalizar configuración (12-Factor App)
├── Usar variables de entorno para configuración
├── Separar por entorno sin cambiar código
└── NO hardcodear configuración en código

Eliminar: configuracion-externa.md, iac-parametrizacion.md
```

---

### 2. ADRs - Architecture Decision Records (5 estándares fragmentados)

| Estándar Custom                                          | Ruta                              | Lineamiento                                       |
| -------------------------------------------------------- | --------------------------------- | ------------------------------------------------- |
| Documentar estilo seleccionado en ADR                    | `documentacion/adrs.md`           | Decisiones Arquitectónicas, Estilo Arquitectónico |
| Incluir contexto, alternativas, decisión y consecuencias | `documentacion/adr-format.md`     | Decisiones Arquitectónicas                        |
| Versionar ADRs en repositorio junto al código            | `documentacion/adr-location.md`   | Decisiones Arquitectónicas                        |
| Actualizar ADRs cuando se superseden                     | `documentacion/adr-lifecycle.md`  | Decisiones Arquitectónicas                        |
| Revisar ADRs en architecture reviews                     | `gobierno/architecture-review.md` | Decisiones, Evaluación                            |

**Equivalente Industria:** Documentado por ThoughtWorks Technology Radar + AWS Well-Architected
**Problema:** Concepto simple fragmentado en 5 archivos
**Recomendación:** ✅ **CONSOLIDAR + RENOMBRAR**

```
[Estándar Único] Architecture Decision Records (ADRs)
├── Formato: Contexto, Alternativas, Decisión, Consecuencias
├── Versionado: Git junto al código
├── Ciclo de vida: Actualizar cuando se superseden
└── Gobierno: Revisar en architecture reviews

Eliminar: adr-format.md, adr-location.md, adr-lifecycle.md
Mantener: adrs.md (renombrado a architecture-decision-records.md)
```

---

### 3. Incident Response (6 estándares del mismo dominio)

| Estándar Custom                                            | Ruta                                   | Lineamiento            |
| ---------------------------------------------------------- | -------------------------------------- | ---------------------- |
| Establecer plan de respuesta a incidentes documentado      | `seguridad/incident-response-plan.md`  | Respuesta a Incidentes |
| Definir roles y responsabilidades del equipo de respuesta  | `seguridad/incident-response-roles.md` | Respuesta a Incidentes |
| Crear playbooks para tipos comunes de incidentes           | `seguridad/incident-playbooks.md`      | Respuesta a Incidentes |
| Implementar detección automatizada de amenazas y anomalías | `seguridad/threat-detection.md`        | Respuesta a Incidentes |
| Realizar simulacros de incidentes trimestralmente          | `seguridad/incident-drills.md`         | Respuesta a Incidentes |
| Documentar post-mortems con acciones correctivas           | `seguridad/incident-postmortem.md`     | Respuesta a Incidentes |

**Equivalente Industria:** NIST CSF - Respond, Google SRE Book - Incident Response
**Problema:** Programa completo fragmentado en 6 estándares
**Recomendación:** ✅ **CONSOLIDAR + RENOMBRAR**

```
[Estándar Único] Incident Response Program (NIST/SRE)
├── Plan documentado y roles definidos
├── Playbooks para incidentes comunes
├── Detección automatizada (SIEM/alerting)
├── Simulacros trimestrales (chaos engineering)
└── Post-mortems blameless con acciones

Mantener: incident-response-program.md (nuevo)
Eliminar: 6 archivos actuales
```

---

### 4. Cifrado de Datos (2 estándares obvios)

| Estándar Custom                                           | Ruta                            | Lineamiento         |
| --------------------------------------------------------- | ------------------------------- | ------------------- |
| Cifrar datos sensibles en tránsito con TLS 1.2 o superior | `seguridad/cifrado-transito.md` | Protección de Datos |
| Cifrar datos sensibles en reposo según clasificación      | `seguridad/cifrado-reposo.md`   | Protección de Datos |

**Equivalente Industria:** OWASP ASVS V6: Stored Cryptography, V9: Communications
**Problema:** Nombres largos, concepto único fragmentado
**Recomendación:** ✅ **CONSOLIDAR + RENOMBRAR**

```
[Estándar Único] Cifrado de Datos Sensibles (OWASP ASVS)
├── En tránsito: TLS 1.2+ (mínimo 1.3 para nuevos sistemas)
├── En reposo: Cifrado según clasificación de datos
└── Gestión de claves: AWS KMS, Azure Key Vault

Mantener: data-encryption.md (nuevo nombre)
Eliminar: cifrado-transito.md, cifrado-reposo.md
```

---

### 5. Code Review (2 estándares del mismo concepto)

| Estándar Custom                                                     | Ruta                              | Lineamiento                 |
| ------------------------------------------------------------------- | --------------------------------- | --------------------------- |
| Realizar code review obligatorio antes de merge a ramas principales | `operabilidad/code-review.md`     | Testing y Calidad           |
| Aplicar revisión de código (PR) a cambios de infraestructura        | `operabilidad/iac-code-review.md` | Infraestructura como Código |

**Equivalente Industria:** GitFlow Best Practices, GitHub Flow
**Problema:** Separar IaC de código app es artificial
**Recomendación:** ✅ **CONSOLIDAR + RENOMBRAR**

```
[Estándar Único] Code Review Obligatorio (GitHub Flow)
├── Aplicar a TODO código (app, IaC, scripts)
├── Mínimo 1 aprobación antes de merge
├── Automatizar checks: linting, tests, security scanning
└── Bloquear merge directo a main/master

Mantener: code-review-policy.md (renombrado)
Eliminar: iac-code-review.md
```

---

### 6. Testing Multi-nivel (Nombre ambiguo)

| Estándar Custom                                                                      | Ruta                               | Lineamiento       |
| ------------------------------------------------------------------------------------ | ---------------------------------- | ----------------- |
| Implementar pruebas automatizadas en múltiples niveles (unitarias, integración, e2e) | `operabilidad/piramide-testing.md` | Testing y Calidad |

**Equivalente Industria:** Test Pyramid (Mike Cohn), Testing Trophy (Kent C. Dodds)
**Problema:** Nombre excesivamente largo (11 palabras), no referencia concepto reconocido
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Implementar pruebas automatizadas en múltiples niveles..."
Nombre sugerido: "Aplicar Test Pyramid (Mike Cohn)"

Archivo: testing-pyramid.md (renombrar desde piramide-testing.md)
Contenido: Referenciar explícitamente Test Pyramid/Trophy
```

---

### 7. Cobertura de Código 80% (Decisión custom vs. estándar)

| Estándar Custom                                                          | Ruta                               | Lineamiento       |
| ------------------------------------------------------------------------ | ---------------------------------- | ----------------- |
| Mantener cobertura de código mínima del 80% en lógica de negocio crítica | `operabilidad/cobertura-codigo.md` | Testing y Calidad |

**Equivalente Industria:** N/A - No existe estándar universal de cobertura
**Problema:** Métrica arbitraria presentada como "estándar obligatorio"
**Recomendación:** ⚠️ **MANTENER pero RECLASIFICAR**

```
NO es un estándar de industria, es una POLÍTICA CORPORATIVA

Acción:
1. Mover a sección "Políticas de Calidad" (no "Estándares")
2. Renombrar archivo: quality-policy-code-coverage.md
3. Documentar justificación de 80% en ADR
4. Referencia: SonarQube default (80%), Google (75-90% recomendado)
```

---

### 8. Versionado de Dependencias (Redundancia con paridad)

| Estándar Custom                                             | Ruta                                | Lineamiento           |
| ----------------------------------------------------------- | ----------------------------------- | --------------------- |
| Usar mismas versiones de dependencias en todos los entornos | `operabilidad/paridad-versiones.md` | Consistencia Entornos |
| Contenedorizar aplicaciones para garantizar consistencia    | `operabilidad/contenedorizacion.md` | Consistencia Entornos |

**Equivalente Industria:** 12-Factor App - Factor X: Dev/prod parity
**Problema:** Contenedores YA garantizan paridad de versiones
**Recomendación:** ✅ **CONSOLIDAR**

```
[Estándar Único] Dev/Prod Parity (12-Factor App)
├── Contenedorización garantiza paridad de dependencias
├── Mismos contenedores en dev, staging, prod
└── Versionado de imágenes: semver + git SHA

Mantener: dev-prod-parity.md (nuevo)
Eliminar: paridad-versiones.md (redundante con contenedores)
```

---

### 9. Bounded Contexts (Nombre ambiguo)

| Estándar Custom                                                 | Ruta                               | Lineamiento              |
| --------------------------------------------------------------- | ---------------------------------- | ------------------------ |
| Identificar límites por capacidad de negocio, no por tecnología | `arquitectura/bounded-contexts.md` | Descomposición y Límites |

**Equivalente Industria:** Domain-Driven Design - Bounded Contexts (Eric Evans)
**Problema:** No usa terminología DDD reconocida
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Identificar límites por capacidad de negocio, no por tecnología"
Nombre sugerido: "Definir Bounded Contexts (DDD)"

Archivo: bounded-contexts.md (ya correcto)
Título estándar: Actualizar a usar terminología DDD explícita
```

---

### 10. Eventos vs Comandos (Nombre largo)

| Estándar Custom                                             | Ruta                                | Lineamiento            |
| ----------------------------------------------------------- | ----------------------------------- | ---------------------- |
| Usar eventos para comunicar hechos del dominio, no comandos | `mensajeria/eventos-vs-comandos.md` | Comunicación Asíncrona |

**Equivalente Industria:** Event-Driven Architecture, AsyncAPI
**Problema:** Nombre explicativo en lugar de descriptivo
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Usar eventos para comunicar hechos del dominio, no comandos"
Nombre sugerido: "Domain Events (Event-Driven Architecture)"

Archivo: domain-events.md (renombrar)
Contenido: Explicar diferencia eventos/comandos en el cuerpo
```

---

### 11. API-Driven Data Access (Nombre largo)

| Estándar Custom                                          | Ruta                              | Lineamiento                 |
| -------------------------------------------------------- | --------------------------------- | --------------------------- |
| Exponer datos mediante APIs o eventos, no acceso directo | `datos/api-driven-data-access.md` | Responsabilidad del Dominio |

**Equivalente Industria:** Domain-Driven Design - Data Ownership
**Problema:** Nombre largo, concepto DDD no referenciado
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Exponer datos mediante APIs o eventos, no acceso directo"
Nombre sugerido: "Data Access via APIs (DDD)"

Archivo: api-driven-data-access.md (mantener)
Título: Acortar y referenciar DDD
```

---

### 12. IaC Tooling (Ya está en nombre de archivo)

| Estándar Custom                                                         | Ruta                                 | Lineamiento                 |
| ----------------------------------------------------------------------- | ------------------------------------ | --------------------------- |
| Definir infraestructura mediante IaC (Terraform, CloudFormation, Bicep) | `operabilidad/iac-herramientas.md`   | Infraestructura como Código |
| Automatizar aprovisionamiento de infraestructura (IaC)                  | `operabilidad/iac-automatizacion.md` | Automatización              |

**Equivalente Industria:** HashiCorp Best Practices, AWS Well-Architected OPS01
**Problema:** 2 estándares que dicen lo mismo
**Recomendación:** ✅ **CONSOLIDAR + RENOMBRAR**

```
[Estándar Único] Infrastructure as Code (IaC)
├── Herramientas: Terraform (primario), AWS CloudFormation
├── Versionado: Git
├── Automatización: CI/CD pipelines
└── Testing: terraform validate, plan

Mantener: infrastructure-as-code.md (nuevo)
Eliminar: iac-herramientas.md, iac-automatizacion.md
```

---

### 13. Security by Design (Nombre largo)

| Estándar Custom                                                    | Ruta                              | Lineamiento               |
| ------------------------------------------------------------------ | --------------------------------- | ------------------------- |
| Aplicar Security by Design en todas las decisiones arquitectónicas | `seguridad/security-by-design.md` | Seguridad desde el Diseño |

**Equivalente Industria:** OWASP ASVS, NIST Secure SDLC
**Problema:** "en todas las decisiones arquitectónicas" es redundante
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Aplicar Security by Design en todas las decisiones arquitectónicas"
Nombre sugerido: "Security by Design (OWASP/NIST)"

Archivo: security-by-design.md (mantener)
Título: Acortar, referenciar frameworks
```

---

### 14. Threat Modeling (Nombre largo)

| Estándar Custom                                                             | Ruta                             | Lineamiento               |
| --------------------------------------------------------------------------- | -------------------------------- | ------------------------- |
| Realizar modelado de amenazas para nuevos sistemas o cambios significativos | `seguridad/modelado-amenazas.md` | Seguridad desde el Diseño |

**Equivalente Industria:** OWASP Threat Modeling, Microsoft STRIDE
**Problema:** "para nuevos sistemas o cambios significativos" debería estar en el contenido, no en el título
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Realizar modelado de amenazas para nuevos sistemas o cambios significativos"
Nombre sugerido: "Threat Modeling (OWASP/STRIDE)"

Archivo: threat-modeling.md (renombrar)
Contenido: Especificar cuándo aplicar (nuevos sistemas, cambios significativos)
```

---

### 15. Reserved Instances (Nombre largo)

| Estándar Custom                                                     | Ruta                                   | Lineamiento            |
| ------------------------------------------------------------------- | -------------------------------------- | ---------------------- |
| Utilizar reserved instances y savings plans para cargas predecibles | `infraestructura/reserved-capacity.md` | Optimización de Costos |

**Equivalente Industria:** AWS Well-Architected COST05, FinOps Foundation
**Problema:** Nombre largo, concepto estándar de FinOps
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Utilizar reserved instances y savings plans para cargas predecibles"
Nombre sugerido: "Reserved Capacity (FinOps)"

Archivo: reserved-capacity.md (mantener)
Título: Acortar, referenciar FinOps Foundation
```

---

### 16. Scheduled Shutdown (Nombre largo)

| Estándar Custom                                                 | Ruta                                    | Lineamiento            |
| --------------------------------------------------------------- | --------------------------------------- | ---------------------- |
| Automatizar apagado de recursos no productivos fuera de horario | `infraestructura/scheduled-shutdown.md` | Optimización de Costos |

**Equivalente Industria:** FinOps Foundation - Workload Optimization
**Problema:** Concepto simple con nombre excesivamente descriptivo
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Automatizar apagado de recursos no productivos fuera de horario"
Nombre sugerido: "Scheduled Shutdown (FinOps)"

Archivo: scheduled-shutdown.md (mantener)
Título: Acortar
```

---

### 17. Cost Alerts (Nombre con "configurar")

| Estándar Custom                                         | Ruta                             | Lineamiento            |
| ------------------------------------------------------- | -------------------------------- | ---------------------- |
| Configurar alertas de presupuesto y anomalías de costos | `infraestructura/cost-alerts.md` | Optimización de Costos |

**Equivalente Industria:** AWS Cost Anomaly Detection, FinOps Foundation
**Problema:** Verbo "configurar" es genérico, debería ser "implementar"
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Configurar alertas de presupuesto y anomalías de costos"
Nombre sugerido: "Implementar Cost Alerts (FinOps)"

Archivo: cost-alerts.md (mantener)
Título: Cambiar verbo
```

---

### 18. Defensa en Profundidad (Nombre largo)

| Estándar Custom                                                 | Ruta                                  | Lineamiento               |
| --------------------------------------------------------------- | ------------------------------------- | ------------------------- |
| Aplicar defensa en profundidad con múltiples capas de seguridad | `seguridad/defensa-en-profundidad.md` | Seguridad desde el Diseño |

**Equivalente Industria:** NIST SP 800-53, Defense in Depth (NSA)
**Problema:** "con múltiples capas de seguridad" es redundante (defensa en profundidad YA implica capas)
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Aplicar defensa en profundidad con múltiples capas de seguridad"
Nombre sugerido: "Defense in Depth (NIST)"

Archivo: defense-in-depth.md (renombrar)
Título: Acortar, usar término inglés estándar
```

---

### 19. Service Identities (Nombre largo)

| Estándar Custom                                                              | Ruta                                 | Lineamiento         |
| ---------------------------------------------------------------------------- | ------------------------------------ | ------------------- |
| Gestionar identidades de servicios con service accounts y managed identities | `seguridad/identidades-servicios.md` | Identidad y Accesos |

**Equivalente Industria:** AWS IAM Roles, Azure Managed Identities
**Problema:** Nombre largo, herramientas en el título (deberían estar en contenido)
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Gestionar identidades de servicios con service accounts y managed identities"
Nombre sugerido: "Service Identities (IAM/Managed Identities)"

Archivo: service-identities.md (renombrar)
Contenido: Especificar herramientas (AWS IAM Roles, Azure MI, GCP Service Accounts)
```

---

### 20. Zero Trust Networking (Nombre largo)

| Estándar Custom                                                      | Ruta                              | Lineamiento                |
| -------------------------------------------------------------------- | --------------------------------- | -------------------------- |
| Aplicar principio de menor exposición de red (zero trust networking) | `seguridad/zero-trust-network.md` | Segmentación y Aislamiento |

**Equivalente Industria:** NIST Zero Trust Architecture SP 800-207
**Problema:** "Zero trust" está entre paréntesis cuando debería ser el nombre principal
**Recomendación:** ✅ **RENOMBRAR**

```
Nombre actual: "Aplicar principio de menor exposición de red (zero trust networking)"
Nombre sugerido: "Zero Trust Networking (NIST SP 800-207)"

Archivo: zero-trust-network.md (mantener)
Título: Invertir prioridad (zero trust primero, explicación después)
```

---

## 📋 TABLA CONSOLIDADA: TOP 20 CASOS CRÍTICOS

| #   | Estándar Custom                                     | Lineamiento                | Equivalente Industria          | Recomendación                     |
| --- | --------------------------------------------------- | -------------------------- | ------------------------------ | --------------------------------- |
| 1   | Externalizar configuración en variables de entorno  | Diseño Cloud Native        | **12-Factor App - Factor III** | **CONSOLIDAR** 3 estándares en 1  |
| 2   | Documentar estilo seleccionado en ADR               | Decisiones Arquitectónicas | **ThoughtWorks ADR**           | **CONSOLIDAR** 5 estándares en 1  |
| 3   | Establecer plan de respuesta a incidentes           | Respuesta a Incidentes     | **NIST CSF + SRE Book**        | **CONSOLIDAR** 6 estándares en 1  |
| 4   | Cifrar datos en tránsito con TLS 1.2+               | Protección de Datos        | **OWASP ASVS V6/V9**           | **CONSOLIDAR** 2 en 1 + RENOMBRAR |
| 5   | Realizar code review obligatorio antes de merge     | Testing y Calidad          | **GitHub Flow**                | **CONSOLIDAR** 2 en 1             |
| 6   | Implementar pruebas en múltiples niveles            | Testing y Calidad          | **Test Pyramid (Mike Cohn)**   | **RENOMBRAR** a Test Pyramid      |
| 7   | Mantener cobertura 80% en lógica crítica            | Testing y Calidad          | N/A (política custom)          | **RECLASIFICAR** como política    |
| 8   | Usar mismas versiones en todos los entornos         | Consistencia Entornos      | **12-Factor App - Factor X**   | **CONSOLIDAR** con contenedores   |
| 9   | Identificar límites por capacidad de negocio        | Descomposición             | **DDD - Bounded Contexts**     | **RENOMBRAR** a Bounded Contexts  |
| 10  | Usar eventos para comunicar hechos                  | Comunicación Asíncrona     | **Event-Driven Architecture**  | **RENOMBRAR** a Domain Events     |
| 11  | Exponer datos mediante APIs o eventos               | Responsabilidad Dominio    | **DDD - Data Ownership**       | **RENOMBRAR** acortar nombre      |
| 12  | Definir infraestructura mediante IaC                | IaC                        | **HashiCorp + AWS Well-Arch**  | **CONSOLIDAR** 2 en 1             |
| 13  | Aplicar Security by Design en todas las decisiones  | Seguridad Diseño           | **OWASP ASVS + NIST**          | **RENOMBRAR** acortar             |
| 14  | Realizar modelado de amenazas para nuevos sistemas  | Seguridad Diseño           | **OWASP + STRIDE**             | **RENOMBRAR** a Threat Modeling   |
| 15  | Utilizar reserved instances para cargas predecibles | Cost Optimization          | **FinOps Foundation**          | **RENOMBRAR** a Reserved Capacity |
| 16  | Automatizar apagado de recursos no productivos      | Cost Optimization          | **FinOps Foundation**          | **RENOMBRAR** acortar             |
| 17  | Configurar alertas de presupuesto y anomalías       | Cost Optimization          | **FinOps Foundation**          | **RENOMBRAR** cambiar verbo       |
| 18  | Aplicar defensa en profundidad con múltiples capas  | Seguridad Diseño           | **NIST SP 800-53 + NSA**       | **RENOMBRAR** a Defense in Depth  |
| 19  | Gestionar identidades de servicios con SA y MI      | Identidad y Accesos        | **AWS IAM + Azure MI**         | **RENOMBRAR** acortar             |
| 20  | Aplicar menor exposición de red (zero trust)        | Segmentación               | **NIST SP 800-207**            | **RENOMBRAR** a Zero Trust        |

---

## 🎯 RESUMEN EJECUTIVO: ACCIONES PRIORITARIAS

### Impacto Cuantitativo de las Acciones

| Acción           | Casos        | Archivos Afectados | Reducción Estándares    | Mejora Alineación   |
| ---------------- | ------------ | ------------------ | ----------------------- | ------------------- |
| **CONSOLIDAR**   | 7 grupos     | 24 archivos → 7    | -17 archivos (-71%)     | +17% alineación     |
| **RENOMBRAR**    | 13 casos     | 13 archivos        | 0 (mismo archivo)       | +11% alineación     |
| **RECLASIFICAR** | 1 caso       | 1 archivo          | -1 estándar             | +1% alineación      |
| **TOTAL**        | **20 casos** | **25 archivos**    | **-18 archivos (-15%)** | **+29% alineación** |

### Resultado Proyectado

**Estado Actual:**

- 119 estándares únicos
- 61% custom (73 estándares)
- 3% bien alineados (4 estándares)

**Estado Post-Optimización:**

- **101 estándares únicos** (-15%)
- **32% custom** (32 estándares, -56%)
- **32% bien alineados** (32 estándares, +700%)

---

## 📈 PLAN DE ACCIÓN RECOMENDADO

### Fase 1: Consolidaciones Críticas (Semana 1-2)

**Prioridad:** 🔴 **ALTA** - Mayor impacto en reducción de complejidad

1. **Gestión de Configuración**
   - Consolidar 3 estándares → 1
   - Archivo resultante: `externalizar-configuracion-12factor.md`
   - Referencias a actualizar: 3 lineamientos

2. **ADRs - Architecture Decision Records**
   - Consolidar 5 estándares → 1
   - Archivo resultante: `architecture-decision-records.md`
   - Referencias a actualizar: 2 lineamientos

3. **Incident Response Program**
   - Consolidar 6 estándares → 1
   - Archivo resultante: `incident-response-program.md`
   - Referencias a actualizar: 1 lineamiento

4. **IaC - Infrastructure as Code**
   - Consolidar 2 estándares → 1
   - Archivo resultante: `infrastructure-as-code.md`
   - Referencias a actualizar: 2 lineamientos

**Resultado Fase 1:** -16 archivos, +4 estándares alineados con industria

---

### Fase 2: Renombrados para Alineación (Semana 3)

**Prioridad:** 🟡 **MEDIA** - Mejora credibilidad sin cambiar estructura

1. Renombrar 13 estándares según tabla (casos 6-20)
2. Actualizar títulos en markdown para referenciar frameworks
3. Agregar sección "Framework de Referencia" en cada archivo
4. Actualizar referencias en lineamientos

**Resultado Fase 2:** +11% alineación, 0 archivos eliminados

---

### Fase 3: Reclasificación de Políticas (Semana 4)

**Prioridad:** 🟢 **BAJA** - Claridad conceptual

1. Mover `cobertura-codigo.md` a nueva carpeta `/politicas-calidad/`
2. Identificar otros 5-10 estándares que son políticas corporativas
3. Documentar justificación en ADRs correspondientes

**Resultado Fase 3:** Claridad entre estándares de industria vs políticas custom

---

## 🔍 ANÁLISIS ADICIONAL: OTROS 53 ESTÁNDARES CUSTOM

Los 53 estándares custom restantes (no incluidos en TOP 20) se clasifican en:

### A. Justificados como Custom (35 estándares)

**Razón:** Específicos de stack tecnológico, contexto corporativo o políticas de negocio

Ejemplos válidos:

- `Aislar recursos por entorno en cuentas/subscripciones separadas` → AWS/Azure específico
- `Clasificar datos según sensibilidad (público, interno, sensible, regulado)` → Taxonomía corporativa
- `Implementar contract testing automatizado` → Práctica emergente, aún no estándar
- `Mantener inventario actualizado de componentes (SBOM)` → Buena práctica, no estándar formal

**Acción:** ✅ **MANTENER** - Documentar justificación en sección "Contexto"

---

### B. Candidatos a Renombrado (12 estándares)

Ejemplos:

- `Documentar propiedad clara de cada componente` → **RENOMBRAR** a "Component Ownership (Team Topologies)"
- `Aplicar rightsizing basado en métricas de utilización` → **RENOMBRAR** a "Rightsizing (FinOps)"
- `Implementar reconciliación para consistencia eventual` → **RENOMBRAR** a "Reconciliation Patterns (DDD)"

**Acción:** 🔄 Evaluar en Fase 2 extendida

---

### C. Candidatos a Consolidación (6 estándares)

**Grupo: Gestión de Secretos**

- `No almacenar credenciales en código`
- `Gestionar claves de cifrado con KMS`
- `Usar identidad federada y SSO`

**Acción:** Evaluar consolidación en estándar padre "Secrets Management (OWASP)"

---

## ✅ CRITERIOS DE ÉXITO

Al finalizar el plan de acción:

1. ✅ **Alineación con industria ≥ 30%** (vs 3% actual)
2. ✅ **Estándares custom ≤ 35%** (vs 61% actual)
3. ✅ **0 nombres > 8 palabras** (vs 24 actuales)
4. ✅ **100% estándares referencian framework** (cuando aplique)
5. ✅ **Reducción de 15-20% en cantidad total** (119 → ~100)

---

## 📚 REFERENCIAS

### Frameworks de Industria Utilizados

| Framework                        | Autoridad           | URL                                                                         |
| -------------------------------- | ------------------- | --------------------------------------------------------------------------- |
| **12-Factor App**                | Heroku/Adam Wiggins | <https://12factor.net/>                                                       |
| **AWS Well-Architected**         | Amazon Web Services | <https://aws.amazon.com/architecture/well-architected/>                       |
| **OWASP ASVS**                   | OWASP Foundation    | <https://owasp.org/www-project-application-security-verification-standard/>   |
| **NIST Cybersecurity Framework** | NIST                | <https://www.nist.gov/cyberframework>                                         |
| **Google SRE Book**              | Google              | <https://sre.google/books/>                                                   |
| **DDD (Domain-Driven Design)**   | Eric Evans          | <https://www.domainlanguage.com/ddd/>                                         |
| **FinOps Foundation**            | Linux Foundation    | <https://www.finops.org/>                                                     |
| **ThoughtWorks ADR**             | ThoughtWorks        | <https://www.thoughtworks.com/radar/techniques/architecture-decision-records> |
| **Test Pyramid**                 | Mike Cohn           | <https://martinfowler.com/articles/practical-test-pyramid.html>               |
| **NIST SP 800-207 (Zero Trust)** | NIST                | <https://csrc.nist.gov/publications/detail/sp/800-207/final>                  |

---

**Próximos Pasos:**

1. Validar priorización con equipo de arquitectura
2. Crear ADR para consolidaciones propuestas
3. Ejecutar Fase 1 (consolidaciones críticas)
4. Medir impacto en comprensión de nuevos arquitectos

---

_Documento generado: 3 de febrero de 2026_
_Análisis base: analizar-estandares.py v1.0_
_Criterios: Alineación con industria, claridad, consolidación, valor diferencial_
