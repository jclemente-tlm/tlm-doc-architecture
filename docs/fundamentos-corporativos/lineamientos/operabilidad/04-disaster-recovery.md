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

- [Definir objetivos RPO/RTO para cada sistema crítico](../../estandares/operabilidad/disaster-recovery.md#definicion-de-objetivos)
- [Implementar backups automatizados con retención apropiada](../../estandares/operabilidad/disaster-recovery.md#estrategia-de-backups)
- [Probar procedimientos de restauración al menos trimestralmente](../../estandares/operabilidad/disaster-recovery.md#pruebas-de-recuperacion)
- [Documentar runbooks de DR actualizados y accesibles](../../estandares/operabilidad/disaster-recovery.md#documentacion-de-procedimientos)
- [Realizar simulacros de DR con equipos involucrados](../../estandares/operabilidad/disaster-recovery.md#simulacros)

## Referencias Relacionadas

- [Resiliencia y Disponibilidad](../arquitectura/04-resiliencia-y-disponibilidad.md) (patrones de resiliencia)
- [Gestión de Incidentes](./05-gestion-incidentes.md) (respuesta a incidentes operacionales)
- [Observabilidad](../arquitectura/05-observabilidad.md) (detección temprana de problemas)
