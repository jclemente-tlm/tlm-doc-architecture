---
id: resiliencia-y-tolerancia-a-fallos
sidebar_position: 3
title: Resiliencia y Tolerancia a Fallos
description: Sistemas diseñados para degradarse, recuperarse y operar ante fallos
---

# Resiliencia y Tolerancia a Fallos

## Declaración del Principio

Los sistemas deben diseñarse asumiendo que los fallos ocurrirán y deben ser capaces de degradarse, recuperarse y continuar operando de forma controlada.

## Justificación

En sistemas modernos, distribuidos e integrados, los fallos no son excepciones sino eventos esperables: servicios externos no disponibles, componentes internos que fallan, picos de carga, errores humanos o condiciones de red adversas. Diseñar asumiendo disponibilidad total genera arquitecturas frágiles que no sobreviven a la realidad operativa.

La resiliencia debe ser una propiedad estructural del sistema, no una reacción operativa. Esto implica diseño defensivo que anticipa escenarios de fallo, degradación controlada priorizando funcionalidades críticas, recuperación automatizada minimizando intervención manual, y aislamiento de fallos evitando propagación en cascada.

Este principio busca mantener la operación continua del sistema ante fallos mediante degradación controlada y recuperación automatizada. Se logra implementando patrones de resiliencia (Circuit Breaker, Retry, Timeout, Bulkhead), diseñando para fallos parciales, validando comportamiento mediante Chaos Engineering, y definiendo SLOs realistas. Se aplica a comunicación entre componentes, integraciones internas y externas, manejo de dependencias, y experiencia del usuario ante fallos, independientemente del estilo arquitectónico adoptado.

## Implicaciones

- Asumir fallos parciales como escenario normal de diseño
- Implementar patrones de resiliencia (Circuit Breaker, Retry, Timeout, Bulkhead)
- Los componentes deben fallar de forma controlada y predecible
- Evitar fallos en cascada mediante aislamiento de dependencias
- Validar comportamiento ante fallos (Chaos Engineering)
- Definir SLOs realistas alineados con capacidades del sistema
- Priorizar funcionalidades críticas en escenarios de degradación
- Requiere mayor esfuerzo inicial a cambio de estabilidad operativa

## Referencias

**Lineamientos relacionados:**

- [Escalabilidad y Rendimiento](../../lineamientos/arquitectura/13-escalabilidad-y-rendimiento.md)
- [Observabilidad y Monitoreo](../../lineamientos/operabilidad/01-observabilidad-y-monitoreo.md)
- [Recuperación ante Desastres](../../lineamientos/operabilidad/02-recuperacion-ante-desastres.md)

**ADRs relacionados:**

- [ADR-011: Redis como Cache Distribuido](../../decisiones-de-arquitectura/adr-011-redis-cache-distribuido.md)
- [ADR-007: AWS ECS Fargate para Contenedores](../../decisiones-de-arquitectura/adr-007-aws-ecs-fargate-contenedores.md)
- [ADR-021: Grafana Stack para Observabilidad](../../decisiones-de-arquitectura/adr-021-grafana-stack-observabilidad.md)

**Frameworks de referencia:**

- [AWS Well-Architected Framework - Reliability Pillar](https://aws.amazon.com/architecture/well-architected/)
- [Azure Well-Architected Framework - Reliability](https://learn.microsoft.com/azure/well-architected/)
- [Google SRE Book](https://sre.google/books/)
