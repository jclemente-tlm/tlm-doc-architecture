---
id: propiedad-de-datos
sidebar_position: 3
title: Propiedad de Datos
description: Cada dominio es responsable exclusivo de sus datos sin compartir almacenamiento
---

# Propiedad de Datos

Cada dominio de negocio es responsable exclusivo de sus propios datos: definición, calidad, integridad y evolución, sin compartir almacenamiento ni permitir acceso directo desde otros dominios. Cuando múltiples dominios acceden a una misma base de datos, se genera acoplamiento oculto, los cambios de esquema afectan múltiples servicios y se pierde claridad sobre responsabilidades. El ownership claro establece límites arquitectónicos fundamentales y habilita autonomía real mediante exposición de datos vía APIs o eventos.

**Este lineamiento aplica a:** arquitecturas de microservicios, monolitos modulares con límites de dominio, sistemas distribuidos, plataformas multi-dominio.

## Estándares Obligatorios

- [Asignar base de datos independiente por dominio/servicio](../../estandares/datos/database-per-service.md)
- [Prohibir acceso directo a bases de datos de otros dominios](../../estandares/datos/no-shared-database.md)
- [Exponer datos mediante APIs o eventos](../../estandares/datos/data-exposure.md)
- [Documentar ownership de cada conjunto de datos](../../estandares/datos/data-catalog.md)
- [Gestionar replicación controlada cuando sea necesaria](../../estandares/datos/data-replication.md)

## Referencias Relacionadas

- [Datos por Dominio](01-datos-por-dominio.md)
- [Autonomía de Servicios](../arquitectura/10-autonomia-de-servicios.md)
- [Modelado de Dominio](../arquitectura/09-modelado-de-dominio.md)
