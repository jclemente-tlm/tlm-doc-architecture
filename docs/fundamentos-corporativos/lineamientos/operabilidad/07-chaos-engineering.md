---
id: chaos-engineering
sidebar_position: 7
title: Chaos Engineering
description: Pruebas de resiliencia, game days y experimentación controlada de fallos
---

# Chaos Engineering

Sistemas aparentemente resilientes ocultan puntos de fallo no descubiertos hasta crisis real en producción. Dependencias implícitas no documentadas generan cascadas de fallos inesperadas durante incidentes. Suposiciones sobre comportamiento bajo degradación no validadas causan sorpresas operacionales costosas. Equipos sin experiencia en respuesta a fallos reaccionan lentamente en emergencias. Practicar Chaos Engineering mediante experimentos controlados de inyección de fallos (latencia, pérdida de conexión, saturación de recursos), realizar game days simulando escenarios de crisis y validar sistemáticamente hipótesis de resiliencia descubre debilidades antes de afectar usuarios, entrena equipos en respuesta bajo presión y construye confianza cuantificada en comportamiento del sistema ante adversidad.

**Este lineamiento aplica a:** Experimentos de inyección de fallos controlados, game days y simulacros de crisis, validación de patrones de resiliencia (circuit breakers, timeouts, retries), pruebas de degradación y fallback, observación de comportamiento bajo condiciones adversas.

**No aplica a:** Testing funcional tradicional (ver Estrategia de Pruebas), gestión de incidentes reales (ver Gestión de Incidentes), pruebas de carga convencionales (performance testing).

## Estándares Obligatorios

- [Realizar experimentos de Chaos Engineering en ambientes controlados](../../estandares/operabilidad/chaos-engineering.md#experimentos-controlados)
- [Ejecutar game days periódicos simulando escenarios críticos](../../estandares/operabilidad/chaos-engineering.md#game-days)
- [Validar patrones de resiliencia implementados](../../estandares/operabilidad/chaos-engineering.md#validacion-de-patrones)
- [Documentar hallazgos y acciones correctivas](../../estandares/operabilidad/chaos-engineering.md#documentation)
- [Incrementar complejidad gradualmente (crawl, walk, run)](../../estandares/operabilidad/chaos-engineering.md#progresion-gradual)

## Referencias Relacionadas

- [Resiliencia y Disponibilidad](../arquitectura/04-resiliencia-y-disponibilidad.md) (patrones de resiliencia)
- [Observabilidad](../arquitectura/06-observabilidad.md) (monitoreo durante experimentos)
- [Gestión de Incidentes](./06-gestion-incidentes.md) (respuesta coordinada)
- [Disaster Recovery](./05-disaster-recovery.md) (validación de procedimientos DR)
