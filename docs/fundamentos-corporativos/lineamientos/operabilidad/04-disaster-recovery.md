---
id: disaster-recovery
sidebar_position: 4
title: Disaster Recovery y Continuidad
description: Planes de recuperación ante desastres, backups, RPO/RTO y pruebas de resiliencia
---

# Disaster Recovery y Continuidad

Ausencia de plan de recuperación ante desastres expone organización a pérdida permanente de datos críticos y downtime prolongado. Backups no probados generan falsa sensación de seguridad que colapsa en crisis real. Desconocimiento de objetivos de recuperación (RPO/RTO) previene asignación adecuada de recursos y priorización de sistemas críticos. Falta de runbooks actualizados y equipos no entrenados retrasa recuperación hasta horas o días. Definir planes de Disaster Recovery con RPO/RTO por sistema, implementar backups automatizados y probados regularmente, documentar procedimientos de restauración y realizar simulacros periódicos garantiza recuperación predecible, minimiza pérdida de datos y reduce impacto de incidentes catastróficos en continuidad del negocio.

**Este lineamiento aplica a:** Definición de objetivos de recuperación (RPO/RTO), estrategias de backup y restauración, planes de Disaster Recovery por sistema crítico, procedimientos de failover y switchover, simulacros y pruebas de DR, runbooks de recuperación actualizados.

**No aplica a:** Resiliencia de aplicaciones en condiciones normales (ver Resiliencia y Disponibilidad), gestión de incidentes operacionales (ver Gestión de Incidentes), backups de desarrollo/QA.

## Estándares Obligatorios

- [Definir RPO/RTO por sistema](../../estandares/operabilidad/rpo-rto-definition.md)
- [Implementar backups automatizados](../../estandares/operabilidad/backup-automation.md)
- [Definir políticas de retención](../../estandares/operabilidad/backup-retention.md)
- [Probar restauración periódicamente](../../estandares/operabilidad/restore-testing.md)
- [Documentar runbooks de recuperación](../../estandares/operabilidad/dr-runbooks.md)
- [Realizar simulacros de DR](../../estandares/operabilidad/dr-drills.md)
- [Implementar multi-region failover](../../estandares/operabilidad/multi-region-failover.md)
- [Mantener plan de continuidad de negocio](../../estandares/operabilidad/business-continuity-plan.md)
- [Definir cadena de comunicación en desastres](../../estandares/operabilidad/incident-communication.md)

## Referencias Relacionadas

- [Resiliencia y Disponibilidad](../arquitectura/04-resiliencia-y-disponibilidad.md) (patrones de resiliencia)
- [Observabilidad](../arquitectura/06-observabilidad.md) (detección temprana de problemas)
- [CI/CD Pipelines](./01-cicd-pipelines.md) (automatización de deployments y rollbacks)
