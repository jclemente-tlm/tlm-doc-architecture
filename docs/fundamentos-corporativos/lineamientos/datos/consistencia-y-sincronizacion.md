---
id: consistencia-y-sincronizacion
sidebar_position: 2
title: Consistencia y Sincronización
description: Estrategias para mantener consistencia de datos en sistemas distribuidos
---

# Consistencia y Sincronización

Sistemas distribuidos requieren trade-offs entre consistencia, disponibilidad y tolerancia a particiones (Teorema CAP). Forzar consistencia fuerte en todos los casos genera latencias, bloqueos y puntos únicos de fallo. Aceptar consistencia eventual donde sea apropiado mejora disponibilidad y escalabilidad, mientras mecanismos de reconciliación y resolución de conflictos garantizan convergencia final de datos.

**Este lineamiento aplica a:** sistemas distribuidos, datos replicados, eventos asíncronos, integraciones y cachés.

## Prácticas Obligatorias

- [Definir modelo de consistencia por caso de uso](../../estandares/datos/data-consistency.md#modelos-de-consistencia)
- [Implementar saga pattern para transacciones distribuidas](../../estandares/mensajeria/messaging-patterns.md#saga-pattern)
- [Implementar estrategias de resolución de conflictos](../../estandares/datos/data-consistency.md#resolución-de-conflictos)
- [Gestionar replicación de datos](../../estandares/datos/data-consistency.md#replicación-de-datos)
- [Aplicar CQRS cuando corresponda](../../estandares/arquitectura/cqrs.md#cqrs-pattern)
- [Implementar compensaciones para rollback](../../estandares/mensajeria/messaging-patterns.md#compensation-pattern)

## Referencias Relacionadas

- [Datos por Dominio](./datos-por-dominio.md)
- [Propiedad de Datos](./propiedad-de-datos.md)
- [Comunicación Asíncrona y Eventos](../integracion/comunicacion-asincrona-y-eventos.md)
- [Resiliencia y Disponibilidad](../arquitectura/resiliencia-y-disponibilidad.md)
