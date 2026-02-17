---
id: datos-por-dominio
sidebar_position: 1
title: Datos por Dominio
description: Responsabilidad exclusiva de datos por dominio, esquemas versionados y evolución controlada
---

# Datos por Dominio

Bases de datos compartidas y esquemas implícitos generan acoplamiento oculto, dependencias cíclicas, errores en runtime e incompatibilidades entre servicios. Cada dominio debe ser dueño exclusivo de sus datos, exponiendo acceso únicamente mediante APIs o eventos, nunca por queries directas. Esquemas versionados (migraciones, JSON Schema, AsyncAPI) actúan como contratos explícitos que facilitan autonomía de equipos, despliegues independientes, validación automática y evolución controlada sin romper consumidores existentes.

**Este lineamiento aplica a:** microservicios, módulos en monolitos modulares, esquemas de bases de datos, eventos de dominio, modelos persistidos, mensajes asíncronos e integraciones entre aplicaciones.

## Estándares Obligatorios

### Propiedad y Responsabilidad

- [Asignar propiedad exclusiva de datos por dominio (database per service)](../../estandares/datos/database-standards.md)
- [Evitar bases de datos compartidas entre servicios](../../estandares/datos/database-standards.md)
- [Exponer datos mediante APIs o eventos, no acceso directo a BD](../../estandares/arquitectura/bounded-contexts.md)

### Esquemas Versionados

- [Versionar esquemas de BD con migraciones automatizadas (Flyway/Liquibase)](../../estandares/datos/database-standards.md#4-requisitos-obligatorios)
- [Documentar esquemas de eventos con JSON Schema o AsyncAPI](../../estandares/mensajeria/kafka-messaging.md)
- [Validar datos contra esquemas antes de persistir](../../estandares/datos/database-standards.md)

### Evolución de Esquemas

- [Gestionar cambios con estrategias expand-contract (backward compatible)](../../estandares/datos/database-standards.md)
- [Mantener retrocompatibilidad en eventos y APIs de datos](../../estandares/mensajeria/kafka-messaging.md)
- [Documentar propiedad y lifecycle de datos por dominio](../../estandares/arquitectura/bounded-contexts.md)
