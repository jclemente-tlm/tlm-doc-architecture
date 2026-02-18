---
id: consistencia-y-sincronizacion
sidebar_position: 2
title: Consistencia y Sincronización
description: Estrategias para mantener consistencia de datos en sistemas distribuidos
---

# Consistencia y Sincronización

Sistemas distribuidos requieren trade-offs entre consistencia, disponibilidad y tolerancia a particiones (Teorema CAP). Forzar consistencia fuerte en todos los casos genera latencias, bloqueos y puntos únicos de fallo. Aceptar consistencia eventual donde sea apropiado mejora disponibilidad y escalabilidad, mientras mecanismos de reconciliación y resolución de conflictos garantizan convergencia final de datos.

**Este lineamiento aplica a:** sistemas distribuidos, datos replicados, eventos asíncronos, integraciones y cachés.

## Estándares Obligatorios

- [Definir modelo de consistencia por caso de uso](../../estandares/datos/consistency-models.md)
- [Implementar saga pattern para transacciones distribuidas](../../estandares/arquitectura/saga-pattern.md)
- [Implementar estrategias de resolución de conflictos](../../estandares/datos/conflict-resolution.md)
- [Gestionar replicación de datos](../../estandares/datos/data-replication.md)
- [Aplicar CQRS cuando corresponda](../../estandares/arquitectura/cqrs-pattern.md)
- [Implementar compensaciones para rollback](../../estandares/arquitectura/compensation-pattern.md)
