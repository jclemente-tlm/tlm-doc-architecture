---
id: datos-por-dominio
sidebar_position: 1
title: Datos por Dominio
description: Responsabilidad exclusiva de datos por dominio, esquemas versionados y evolución controlada
---

# Datos por Dominio

Bases de datos compartidas y esquemas implícitos generan acoplamiento oculto, dependencias cíclicas, errores en runtime e incompatibilidades entre servicios. Cada dominio debe ser dueño exclusivo de sus datos, exponiendo acceso únicamente mediante APIs o eventos, nunca por queries directas. Esquemas versionados (migraciones, JSON Schema, AsyncAPI) actúan como contratos explícitos que facilitan autonomía de equipos, despliegues independientes, validación automática y evolución controlada sin romper consumidores existentes.

**Este lineamiento aplica a:** microservicios, módulos en monolitos modulares, esquemas de bases de datos, eventos de dominio, modelos persistidos, mensajes asíncronos e integraciones entre aplicaciones.

## Prácticas Obligatorias

- [Implementar database per service](../../estandares/datos/data-architecture.md#database-per-service)
- [Prohibir bases de datos compartidas](../../estandares/datos/data-architecture.md#no-shared-database)
- [Exponer datos solo mediante APIs o eventos](../../estandares/datos/data-architecture.md#exposición-de-datos)
- [Versionar esquemas de BD con migraciones](../../estandares/datos/database-standards.md#1-database-migrations)
- [Validar datos contra esquemas](../../estandares/datos/database-standards.md#4-data-validation)
- [Aplicar estrategia expand-contract](../../estandares/datos/data-consistency.md#expand-contract-pattern)

## Referencias Relacionadas

- [Propiedad de Datos](./propiedad-de-datos.md)
- [Consistencia y Sincronización](./consistencia-y-sincronizacion.md)
- [Autonomía de Servicios](../arquitectura/autonomia-de-servicios.md)
- [APIs y Contratos de Integración](../integracion/apis-y-contratos.md)
