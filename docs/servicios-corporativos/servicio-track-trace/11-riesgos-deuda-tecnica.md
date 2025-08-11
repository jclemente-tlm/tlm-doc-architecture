# 11. Riesgos y Deuda Técnica

## 11.1 Riesgos Identificados

| Riesgo                  | Probabilidad | Impacto | Mitigación                |
|-------------------------|--------------|---------|---------------------------|
| `Event store corruption`| Baja         | Alto    | Backups, replicación      |
| `Deduplicación failure` | Media        | Medio   | Monitoreo, alertas        |
| `Query performance`     | Media        | Medio   | Indexado, optimización    |
| `Integration failures`  | Media        | Alto    | Monitoreo, fallback       |

## 11.2 Deuda Técnica

| Área         | Descripción                | Prioridad | Esfuerzo   |
|--------------|---------------------------|-----------|------------|
| `Monitoring` | Métricas event sourcing    | Alta      | 1 sprint   |
| `Testing`    | Pruebas event replay      | Media     | 2 sprints  |
| `Migration`  | Readiness multi-tenant    | Media     | 3 sprints  |
| `Proyecciones`| Optimización de esquema   | Baja      | 1 sprint   |

## 11.3 Acciones Recomendadas

| Acción                        | Plazo      | Responsable |
|-------------------------------|------------|-------------|
| Configurar monitoreo event store | 2 semanas | SRE         |
| Implementar read replicas        | 1 mes     | DevOps      |
| Pruebas de event replay         | 1 mes     | QA          |
| Preparar migración multi-tenant | 2 meses   | Arquitectura|

## 11.4 Matriz de Riesgos

| ID      | Categoría             | Probabilidad | Impacto | Score | Owner                  | Descripción breve                                 |
|---------|-----------------------|--------------|---------|-------|------------------------|--------------------------------------------------|
| `RT-001`| Performance           | Alta         | Crítico | 20    | Platform Engineering   | Degradación por volumen de eventos                |
| `RT-002`| Seguridad/Compliance  | Media        | Crítico | 16    | Seguridad              | Riesgo de acceso cross-tenant                     |
| `RT-003`| Integridad de datos   | Media        | Alto    | 12    | Platform Engineering   | Inconsistencias entre event store y read models   |
| `RT-004`| Integración           | Media        | Alto    | 10    | Integration Team       | Pérdida de mensajes en event bus                  |

## 11.5 Estrategias de Mitigación

- Backups y replicación en `PostgreSQL`
- Monitoreo de latencia y lag de proyecciones con `Prometheus` y `Grafana`
- Validación estricta de tenant (realm) en middleware y queries
- Pruebas automáticas de event replay y consistencia
- Fallback a colas locales ante fallos de integración
- Alertas automáticas para métricas críticas

## 11.6 Métricas de Riesgo y Deuda Técnica

| Métrica                        | Objetivo           | Medición         |
|-------------------------------|--------------------|------------------|
| `Event Store latency P95`     | `< 100ms`          | `Prometheus`     |
| `Read model lag`              | `< 3s`             | `Prometheus`     |
| `Error rate`                  | `< 0.1%`           | `Prometheus`     |
| `Code coverage`               | `> 85%`            | `CI/CD`          |
| `Technical debt ratio`        | `< 5%`             | `SonarQube`      |
| `Duplication rate`            | `< 3%`             | `SonarQube`      |

## 11.7 Proceso de Revisión y Priorización

- Revisión semanal de riesgos y deuda técnica
- Priorización por impacto y probabilidad
- Escalación a CTO para riesgos críticos
- Refactorización obligatoria ante degradación de métricas clave

---

Todos los riesgos, métricas y acciones reflejan únicamente tecnologías, patrones y decisiones aprobadas en los ADRs y DSL. No se incluyen dependencias, módulos ni ejemplos que no estén alineados con la arquitectura oficial.
