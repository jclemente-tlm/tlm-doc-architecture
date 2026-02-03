---
id: responsabilidad-del-dominio
sidebar_position: 1
title: Responsabilidad del Dominio
description: Los datos deben ser propiedad y responsabilidad del dominio que los gestiona
---

# Responsabilidad del Dominio

Bases de datos compartidas generan acoplamiento implícito, dependencias cíclicas y fricción en evolución de esquemas. Cada dominio debe ser dueño de sus datos, exponiendo acceso mediante APIs o eventos, no por queries directas. Esta separación facilita autonomía de equipos, despliegues independientes y evolución controlada de modelos de datos sin romper otros servicios.

**Este lineamiento aplica a:** microservicios, módulos en monolitos modulares, sistemas con datos compartidos e integraciones entre aplicaciones.

## Estándares Obligatorios

- [Asignar propiedad exclusiva de datos por dominio](../../estandares/datos/data-ownership.md)
- [Evitar bases de datos compartidas entre servicios](../../estandares/datos/database-per-service.md)
- [Exponer datos mediante APIs o eventos, no acceso directo](../../estandares/datos/data-access-via-apis.md)
- [Documentar esquema y propiedad de datos por dominio](../../estandares/datos/schema-documentation.md)
- [Aplicar principio de menor conocimiento en datos](../../estandares/datos/least-knowledge-principle.md)
