# 11. Riesgos y deuda técnica

## 11.1 Riesgos identificados

| Riesgo                        | Probabilidad | Impacto | Mitigación                |
|-------------------------------|--------------|---------|---------------------------|
| Corrupción de base de datos   | Baja         | Alto    | Backups, replicación      |
| Fallo en deduplicación        | Media        | Medio   | Monitoreo, alertas        |
| Bajo rendimiento en consultas | Media        | Medio   | Indexado, optimización    |
| Fallos de integración externa | Media        | Alto    | Monitoreo, fallback       |
| Pérdida de mensajes en SQS    | Baja         | Alto    | DLQ, reintentos           |
| Acceso indebido cross-tenant  | Baja         | Crítico | Validación estricta       |

## 11.2 Deuda técnica

| Área         | Descripción                        | Prioridad | Esfuerzo   |
|--------------|-----------------------------------|-----------|------------|
| Monitoreo    | Métricas de latencia y errores    | Alta      | 1 sprint   |
| Testing      | Pruebas de recuperación y failover| Media     | 2 sprints  |
| Multi-tenant | Automatización de migraciones     | Media     | 2 sprints  |
| Optimización | Indexado y particionamiento       | Baja      | 1 sprint   |

## 11.3 Acciones recomendadas

| Acción                              | Plazo      | Responsable |
|-------------------------------------|------------|-------------|
| Mejorar monitoreo de base de datos  | 2 semanas  | SRE         |
| Implementar réplicas de lectura     | 1 mes      | DevOps      |
| Pruebas de recuperación y failover  | 1 mes      | QA          |
| Automatizar migración multi-tenant  | 2 meses    | Arquitectura|

## 11.4 Matriz de riesgos

| ID      | Categoría             | Probabilidad | Impacto | Score | Owner                  | Descripción breve                                 |
|---------|-----------------------|--------------|---------|-------|------------------------|--------------------------------------------------|
| RT-001  | Performance           | Alta         | Crítico | 20    | Platform Engineering   | Degradación por volumen de eventos                |
| RT-002  | Seguridad/Compliance  | Media        | Crítico | 16    | Seguridad              | Riesgo de acceso cross-tenant                     |
| RT-003  | Integridad de datos   | Media        | Alto    | 12    | Platform Engineering   | Inconsistencias por fallos en procesamiento       |
| RT-004  | Integración           | Media        | Alto    | 10    | Integration Team       | Pérdida de mensajes en SQS                        |

## 11.5 Estrategias de mitigación

- Backups y replicación en PostgreSQL
- Monitoreo de latencia y errores con Prometheus y Grafana
- Validación estricta de tenant en middleware y queries
- Pruebas automáticas de recuperación y consistencia
- Fallback a colas locales ante fallos de integración
- Alertas automáticas para métricas críticas

## 11.6 Métricas de riesgo y deuda técnica

| Métrica                        | Objetivo           | Medición         |
|-------------------------------|--------------------|------------------|
| Latencia de base de datos P95 | < 100ms            | Prometheus       |
| Retraso en procesamiento      | < 3s               | Prometheus       |
| Tasa de error                 | < 0.1%             | Prometheus       |
| Cobertura de código           | > 85%              | CI/CD            |
| Ratio de deuda técnica        | < 5%               | SonarQube        |
| Tasa de duplicación           | < 3%               | SonarQube        |

## 11.7 Proceso de revisión y priorización

- Revisión semanal de riesgos y deuda técnica
- Priorización por impacto y probabilidad
- Escalación a CTO para riesgos críticos
- Refactorización obligatoria ante degradación de métricas clave
