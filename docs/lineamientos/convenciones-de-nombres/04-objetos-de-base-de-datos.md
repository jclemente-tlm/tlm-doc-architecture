---
title: "Objetos de base de datos"
description: "Lineamientos para nombrar tablas, columnas, vistas y procedimientos en bases de datos."
sidebar_position: 4
---

## Introducción

Este documento define las reglas para nombrar objetos de base de datos en los proyectos de Talma, facilitando la comprensión y el mantenimiento de los esquemas.

## Objetivo

Establecer un estándar claro y consistente para nombrar tablas, columnas, vistas y procedimientos almacenados.

## Alcance

Aplica a todos los proyectos y equipos que diseñen o modifiquen bases de datos relacionales en Talma.

## Detalles

### Tablas

- Utiliza nombres en singular y en inglés: `user`, `order`.
- Separa las palabras con guiones bajos (`_`): `order_item`.
- Evita abreviaturas innecesarias para mayor claridad.

### Columnas

- Usa nombres descriptivos, en inglés y en minúsculas: `created_at`, `user_id`.
- Prefiere nombres autoexplicativos sobre abreviaturas.
- Para claves foráneas, utiliza el sufijo `_id`: `customer_id`.

### Vistas y procedimientos almacenados

- Prefija el nombre según el tipo:
  - `vw_` para vistas: `vw_active_users`
  - `sp_` para procedimientos almacenados: `sp_update_order_status`
- El nombre debe reflejar claramente la función o el resultado.

## Ejemplos

| Correcto           | Incorrecto         |
|--------------------|-------------------|
| `user_id`          | `UserID`          |
| `created_at`       | `fechaCreacion`   |
| `vw_active_users`  | `vistaUsuarios`   |
| `sp_update_order_status` | `actualizarEstadoOrden` |

## Buenas prácticas generales

- No utilices palabras reservadas del motor de base de datos.
- Mantén la consistencia en los nombres a lo largo del esquema.
- Documenta todos los cambios en el esquema y justifica las decisiones de nomenclatura.
- Revisa y actualiza periódicamente los nombres para asegurar claridad y alineación con los estándares.

## Convenciones por motor

| Motor         | Tablas/Columnas         | Vistas           | Procedimientos         |
|--------------|-------------------------|------------------|-----------------------|
| PostgreSQL   | minúsculas, snake_case  | vw_nombre        | sp_nombre             |
| Oracle       | MAYÚSCULAS, snake_case  | VW_NOMBRE        | SP_NOMBRE             |
| SQL Server   | PascalCase o snake_case | vwNombre/vw_nombre | spNombre/sp_nombre   |

### Ejemplos por motor

**PostgreSQL**

- Tabla: `order_item`
- Columna: `created_at`
- Vista: `vw_active_users`
- Procedimiento: `sp_update_order_status`

**Oracle**

- Tabla: `ORDER_ITEM`
- Columna: `CREATED_AT`
- Vista: `VW_ACTIVE_USERS`
- Procedimiento: `SP_UPDATE_ORDER_STATUS`

**SQL Server**

- Tabla: `OrderItem` o `order_item`
- Columna: `CreatedAt` o `created_at`
- Vista: `vwActiveUsers` o `vw_active_users`
- Procedimiento: `spUpdateOrderStatus` o `sp_update_order_status`

## Referencias

- [Guía de estilo de SQL Server](https://docs.microsoft.com/es-es/sql/relational-databases/databases/database-identifiers?view=sql-server-ver16)
- [Documentación interna de Talma](../README.md)

## Última revisión

- Fecha: 2025-08-08
- Responsable: Equipo de Arquitectura
