---
id: disaster-recovery
sidebar_position: 4
title: Disaster Recovery y Continuidad
description: Planes de recuperación ante desastres, backups, RPO/RTO y pruebas de resiliencia
---

# Disaster Recovery y Continuidad

Ausencia de plan de recuperación ante desastres expone organización a pérdida permanente de datos críticos y downtime prolongado. Backups no probados generan falsa sensación de seguridad que colapsa en crisis real. Desconocimiento de objetivos de recuperación (RPO/RTO) previene asignación adecuada de recursos y priorización de sistemas críticos. Falta de runbooks actualizados y equipos no entrenados retrasa recuperación hasta horas o días. Definir planes de Disaster Recovery con RPO/RTO por sistema, implementar backups automatizados y probados regularmente, documentar procedimientos de restauración y realizar simulacros periódicos garantiza recuperación predecible, minimiza pérdida de datos y reduce impacto de incidentes catastróficos en continuidad del negocio.

**Este lineamiento aplica a:** definición de objetivos de recuperación (RPO/RTO), estrategias de backup y restauración, planes de Disaster Recovery por sistema crítico, procedimientos de failover y switchover, simulacros y pruebas de DR, runbooks de recuperación actualizados.

## Prácticas Obligatorias

- [Definir RPO/RTO por sistema](../../estandares/operabilidad/disaster-recovery.md#6-rpo-rto-definition)
- [Implementar backups automatizados](../../estandares/operabilidad/disaster-recovery.md#1-backup-automation)
- [Definir políticas de retención](../../estandares/operabilidad/disaster-recovery.md#2-backup-retention)
- [Probar restauración periódicamente](../../estandares/operabilidad/disaster-recovery.md#3-restore-testing)
- [Documentar runbooks de recuperación](../../estandares/operabilidad/disaster-recovery.md#5-dr-runbooks)
- [Realizar simulacros de DR](../../estandares/operabilidad/disaster-recovery.md#4-dr-drills)
- [Implementar multi-region failover](../../estandares/operabilidad/disaster-recovery.md#7-multi-region-failover)

## Referencias Relacionadas

- [Resiliencia y Disponibilidad](../arquitectura/04-resiliencia-y-disponibilidad.md) (patrones de resiliencia)
- [Observabilidad](../arquitectura/06-observabilidad.md) (detección temprana de problemas)
- [CI/CD Pipelines](./01-cicd-pipelines.md) (automatización de deployments y rollbacks)
