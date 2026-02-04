---
id: architecture-retrospectives
sidebar_position: 1
title: Architecture Retrospectives
description: Estándar para realizar retrospectivas de arquitectura periódicas, capturando lecciones aprendidas y mejorando decisiones futuras
---

# Estándar Técnico — Architecture Retrospectives

---

## 1. Propósito

Establecer un proceso sistemático para revisar decisiones arquitectónicas pasadas, evaluar su efectividad, capturar lecciones aprendidas y aplicar mejoras continuas en el diseño de sistemas.

---

## 2. Alcance

**Aplica a:**

- Decisiones de arquitectura implementadas (ADRs executed)
- Proyectos completados o en fase estable
- Incidentes mayores relacionados con arquitectura
- Cambios tecnológicos significativos
- Migraciones de sistemas
- Equipos de desarrollo y arquitectura

**No aplica a:**

- Decisiones aún no implementadas
- Retrospectivas de sprint (ágil ceremonies)
- Post-mortems de incidentes operacionales puros
- Revisiones de código individuales

---

## 3. Tecnologías Aprobadas

| Componente             | Tecnología   | Uso Principal              | Observaciones                    |
| ---------------------- | ------------ | -------------------------- | -------------------------------- |
| **Documentación**      | Confluence   | Templates y resultados     | Con permisos de equipo           |
| **Documentación**      | Notion       | Alternativa para startups  | Usar database para trackeo       |
| **Colaboración**       | Miro         | Retrospectivas remotas     | Templates de retros predefinidos |
| **Colaboración**       | FigJam       | Whiteboarding colaborativo | Integrado con Figma              |
| **ADR Management**     | ADR Tools    | Versionado de ADRs         | En repositorio Git               |
| **Métricas**           | Grafana      | Visualización de impacto   | Dashboards de decisiones         |
| **Survey**             | Google Forms | Recolección de feedback    | Para retrospectivas async        |
| **Video Conferencing** | Teams/Zoom   | Sesiones sincrónicas       | Grabaciones para documentación   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Frecuencia y Timing

- [ ] **Retrospectivas trimestrales:** mínimo cada 3 meses
- [ ] **Post-proyecto:** dentro de 2 semanas de go-live
- [ ] **Post-incidente mayor:** dentro de 1 semana
- [ ] **Migración completada:** retrospectiva obligatoria
- [ ] **Calendario publicado:** con 2 semanas de anticipación

### Participantes

- [ ] **Arquitecto líder:** facilitador obligatorio
- [ ] **Equipo de desarrollo:** mínimo 3 desarrolladores
- [ ] **Product Owner:** si afecta roadmap
- [ ] **SRE/Ops:** si involucra operaciones
- [ ] **Stakeholders clave:** según decisiones revisadas

### Preparación

- [ ] **ADRs a revisar:** lista enviada con 1 semana de anticipación
- [ ] **Métricas recolectadas:** performance, incidents, costs
- [ ] **Timeline preparado:** hitos de implementación
- [ ] **Feedback previo:** encuesta anónima pre-retro
- [ ] **Agenda compartida:** objetivos claros

### Ejecución

- [ ] **Duración:** 90-120 minutos máximo
- [ ] **Facilitador neutral:** sin defensiveness
- [ ] **Timeboxing:** cada sección con tiempo fijo
- [ ] **Toma de notas:** designar note-taker
- [ ] **Grabación:** con consentimiento del equipo

### Documentación

- [ ] **Template estándar:** usar plantilla corporativa
- [ ] **Secciones obligatorias:** What went well, What didn't, Learnings, Actions
- [ ] **Acción items:** con owner y fecha límite
- [ ] **Publicación:** máximo 3 días post-retro
- [ ] **Accesibilidad:** visible para toda ingeniería

### Seguimiento

- [ ] **Action items tracking:** en herramienta de proyecto
- [ ] **Review en próxima retro:** verificar closure
- [ ] **Actualización de ADRs:** si decisiones cambian
- [ ] **Métricas de mejora:** medir impacto de acciones
- [ ] **Cierre formal:** validar con stakeholders

---

## 5. Prohibiciones

- ❌ Buscar culpables o blame individual
- ❌ Retrospectivas sin preparación previa
- ❌ Ignorar feedback de desarrolladores
- ❌ Action items sin owner asignado
- ❌ No documentar resultados
- ❌ Retrospectivas solo cuando hay problemas
- ❌ Participación no diversa (solo seniors)

---

## 6. Configuración Mínima

### Template Confluence - Architecture Retrospective

```markdown
# Architecture Retrospective — {Project Name}

**Fecha:** {Date}
**Facilitador:** {Architect Name}
**Participantes:** {List of attendees}
**ADRs Revisadas:** {Links to ADRs}

---

## 1. Contexto

**Proyecto:** {Brief description}
**Periodo Revisado:** {Start date - End date}
**Decisiones Arquitectónicas Principales:**

- [ADR-001: Decision Title](link)
- [ADR-005: Another Decision](link)

---

## 2. Métricas de Impacto

| Métrica                 | Antes     | Después   | Delta    |
| ----------------------- | --------- | --------- | -------- |
| Tiempo de build         | 15 min    | 8 min     | -47% ✅  |
| Deploy frequency        | 1x/semana | 5x/semana | +400% ✅ |
| Incidents (P1/P2)       | 12/mes    | 3/mes     | -75% ✅  |
| API response time (p95) | 800ms     | 200ms     | -75% ✅  |
| Infrastructure cost     | $5k/mes   | $8k/mes   | +60% ⚠️  |
| Developer satisfaction  | 6/10      | 8/10      | +33% ✅  |

---

## 3. What Went Well ✅

### Decisiones Acertadas

**ADR-007: Migración a Microservicios**

- Escalabilidad mejoró significativamente
- Teams autónomos redujeron dependencies
- Deploy independiente redujo riesgo

**ADR-012: Implementación de API Gateway (Kong)**

- Centralización de autenticación simplificó seguridad
- Rate limiting previno 3 incidentes potenciales
- Observabilidad mejoró troubleshooting

### Prácticas que Funcionaron

- Code reviews arquitectónicos semanales
- Proof of concepts antes de decisiones grandes
- Documentación temprana en ADRs

---

## 4. What Didn't Go Well ⚠️

### Decisiones Sub-óptimas

**ADR-015: Event Sourcing para todos los módulos**

- ❌ Complejidad operacional subestimada
- ❌ Curva de aprendizaje impactó delivery
- ❌ Debugging de issues tomó 3x más tiempo
- ❌ Costos de storage aumentaron 60%

**Recomendación:** Limitar Event Sourcing solo a dominios que realmente lo requieren (audit, compliance)

**ADR-018: Multi-region desde día 1**

- ❌ Over-engineering para tráfico actual
- ❌ Costo no justificado vs beneficio
- ❌ Complejidad de testing aumentó

**Recomendación:** Single region inicial, multi-region cuando tráfico lo justifique

### Gaps de Proceso

- Falta de performance testing antes de producción
- ADRs escritos después de implementación
- Poca participación de Ops en decisiones

---

## 5. Lecciones Aprendidas 📚

1. **Start Simple, Scale Later:** Multi-region prematura fue costly sin beneficio
2. **PoC > Debate:** Las pruebas de concepto resolvieron más que meetings
3. **Developer Experience Matters:** Complejidad de Event Sourcing afectó moral
4. **Cost Visibility:** Necesitamos dashboards de costo por decisión arquitectónica
5. **Early Performance Testing:** Load testing en staging habría detectado issues
6. **ADRs como Living Docs:** Actualizar ADRs con learnings post-implementation

---

## 6. Action Items 🎯

| #   | Acción                                            | Owner      | Deadline   | Status         |
| --- | ------------------------------------------------- | ---------- | ---------- | -------------- |
| 1   | Refactor Event Sourcing a solo módulos críticos   | @john-dev  | 2024-03-15 | 🟡 In Progress |
| 2   | Implementar cost dashboard por servicio           | @maria-sre | 2024-02-28 | ✅ Done        |
| 3   | Crear template de performance testing             | @pedro-qa  | 2024-03-01 | 🔴 Blocked     |
| 4   | ADR review process: escribir antes de implementar | @sara-arch | 2024-02-20 | ✅ Done        |
| 5   | Incluir SRE en todas architecture reviews         | @sara-arch | Ongoing    | 🟢 Ongoing     |
| 6   | Downgrade multi-region a single-region + DR       | @john-dev  | 2024-04-01 | 🟡 In Progress |

---

## 7. Actualizaciones a ADRs

- **ADR-015:** Actualizar con "Lessons Learned" section
- **ADR-018:** Marcar como SUPERSEDED, crear ADR-025 (Single Region Strategy)
- **ADR-007:** Añadir "Success Metrics" section con datos reales

---

## 8. Métricas de Retrospectiva

- **Preparación:** ✅ 95% de participantes completaron pre-survey
- **Participación:** 12/15 stakeholders asistieron
- **Action Items:** 6 actions, 2 completadas en 2 semanas
- **Satisfacción:** 9/10 en post-retro survey
- **Follow-up:** Próxima retro programada para 2024-06-15

---

## 9. Anexos

- [Pre-Retro Survey Results](link)
- [Metrics Dashboard](link)
- [Grabación de Sesión](link) (acceso restringido)
```

### Miro Template - Remote Retrospective

```
┌─────────────────────────────────────────────────────────┐
│   Architecture Retrospective — {Project Name}           │
│   Facilitador: {Name} | Fecha: {Date}                   │
└─────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ WHAT WENT    │  │ WHAT DIDN'T  │  │ LEARNINGS    │
│ WELL ✅      │  │ GO WELL ⚠️   │  │ 📚           │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ [Sticky 1]   │  │ [Sticky 1]   │  │ [Sticky 1]   │
│ [Sticky 2]   │  │ [Sticky 2]   │  │ [Sticky 2]   │
│ [Sticky 3]   │  │ [Sticky 3]   │  │ [Sticky 3]   │
└──────────────┘  └──────────────┘  └──────────────┘

┌─────────────────────────────────────────────────────────┐
│   ACTION ITEMS (WHO / WHAT / WHEN)                      │
├─────────────────────────────────────────────────────────┤
│   1. [@owner] Action description — Deadline: {date}     │
│   2. [@owner] Action description — Deadline: {date}     │
│   3. [@owner] Action description — Deadline: {date}     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│   PARKING LOT (Temas para próxima sesión)               │
├─────────────────────────────────────────────────────────┤
│   • Topic 1                                              │
│   • Topic 2                                              │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Ejemplos

### Pre-Retro Survey (Google Forms)

```
Architecture Retrospective — Pre-Survey

1. ¿Qué decisión arquitectónica tuvo el MAYOR impacto positivo?
   [Texto libre]

2. ¿Qué decisión te generó más fricciones en desarrollo?
   [Texto libre]

3. En escala 1-10, ¿qué tan satisfecho estás con las decisiones arquitectónicas?
   [1] [2] [3] [4] [5] [6] [7] [8] [9] [10]

4. ¿Qué métricas crees que mejoraron?
   [ ] Performance
   [ ] Reliability
   [ ] Developer Experience
   [ ] Time to Market
   [ ] Costs
   [ ] Security
   [ ] Observability

5. ¿Qué cambiarías si pudieras volver atrás?
   [Texto libre]

6. ¿Qué tema quieres que discutamos en la retro?
   [Texto libre]
```

### Facilitation Script

```markdown
## Architecture Retrospective — Facilitation Guide (120 min)

### 0. Setup (5 min)

- ✅ Verificar que todos pueden ver Miro/whiteboard
- ✅ Explicar reglas: no blame, respeto, timeboxing
- ✅ Designar note-taker
- ✅ Iniciar grabación (con consentimiento)

### 1. Contexto (10 min)

- Revisar ADRs del periodo
- Mostrar métricas clave (antes/después)
- Alinear expectativas

### 2. What Went Well (20 min)

- Silent writing (5 min): cada uno escribe en stickies
- Clustering (5 min): agrupar temas similares
- Discusión (10 min): top 3-5 items

### 3. What Didn't Go Well (20 min)

- Silent writing (5 min)
- Clustering (5 min)
- Discusión (10 min): root cause analysis

### 4. Learnings (15 min)

- Extraer patrones de What Went Well + Didn't Go Well
- Discusión: ¿qué haríamos diferente?

### 5. Action Items (30 min)

- Brainstorming de soluciones
- Priorización (dot voting)
- Definir: WHO, WHAT, WHEN para top 5-7 actions
- Asignar owners

### 6. Wrap-up (10 min)

- Revisar action items
- Próximos pasos
- Meta-retro: ¿qué tal estuvo la sesión?

### 7. Post-Retro (10 min)

- Enviar summary a todos
- Crear tickets para action items
- Actualizar ADRs si aplica
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Retrospectiva realizada cada trimestre
- [ ] Participación de equipo multidisciplinario
- [ ] Documentación publicada en < 3 días
- [ ] Action items con owners y deadlines
- [ ] Follow-up de actions de retro anterior
- [ ] ADRs actualizados con learnings
- [ ] Métricas de impacto medidas

### Métricas

```promql
# Frecuencia de retrospectivas
count(architecture_retrospective_completed) by (quarter)

# Action items completion rate
count(retro_action_items{status="completed"}) / count(retro_action_items) * 100

# Time to closure (action items)
histogram_quantile(0.95, retro_action_item_closure_days)

# Participation rate
count(retro_participants) / count(team_members) * 100
```

### Dashboard SLIs

| Métrica                   | SLI       | Alertar si |
| ------------------------- | --------- | ---------- |
| Retrospectivas/trimestre  | >= 1      | < 1        |
| Participation rate        | > 80%     | < 70%      |
| Action items completion   | > 70%     | < 50%      |
| Time to closure (actions) | < 30 días | > 45 días  |
| Documentation published   | < 3 días  | > 5 días   |

---

## 9. Referencias

**Frameworks:**

- [Agile Retrospectives - Esther Derby & Diana Larsen](https://www.amazon.com/Agile-Retrospectives-Making-Teams-Great/dp/0977616649)
- [Team Topologies - Matthew Skelton](https://teamtopologies.com/)
- [AWS Well-Architected - Operational Excellence](https://aws.amazon.com/architecture/well-architected/)

**Herramientas:**

- [Miro Retrospective Templates](https://miro.com/templates/retrospective/)
- [FunRetrospectives Activities](https://www.funretrospectives.com/)
- [Retromat](https://retromat.org/)

**Buenas Prácticas:**

- Google SRE Book - "Postmortem Culture"
- Spotify Engineering Culture - "Learning from Mistakes"
- Architecture Decision Records (ADR) - Michael Nygard
