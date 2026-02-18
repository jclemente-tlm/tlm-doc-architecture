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

- [Implementar database per service](../../estandares/datos/database-per-service.md)
- [Prohibir bases de datos compartidas](../../estandares/datos/no-shared-database.md)
- [Exponer datos solo mediante APIs o eventos](../../estandares/datos/data-exposure.md)
- [Versionar esquemas de BD con migraciones](../../estandares/datos/database-migrations.md)
- [Validar datos contra esquemas](../../estandares/datos/data-validation.md)
- [Aplicar estrategia expand-contract](../../estandares/datos/expand-contract-pattern.md)
