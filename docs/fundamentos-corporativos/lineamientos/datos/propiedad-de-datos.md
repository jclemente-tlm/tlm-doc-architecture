---
id: propiedad-de-datos
sidebar_position: 3
title: Propiedad de Datos
description: Cada dominio es responsable exclusivo de sus datos sin compartir almacenamiento
---

# Propiedad de Datos

Cada dominio de negocio es responsable exclusivo de sus propios datos: definición, calidad, integridad y evolución, sin compartir almacenamiento ni permitir acceso directo desde otros dominios. Cuando múltiples dominios acceden a una misma base de datos, se genera acoplamiento oculto, los cambios de esquema afectan múltiples servicios y se pierde claridad sobre responsabilidades. El ownership claro establece límites arquitectónicos fundamentales y habilita autonomía real mediante exposición de datos vía APIs o eventos.

**Este lineamiento aplica a:** arquitecturas de microservicios, monolitos modulares con límites de dominio, sistemas distribuidos, plataformas multi-dominio.

## Prácticas Obligatorias

- [Definir ownership explícito de datos](../../estandares/datos/data-architecture.md#3-data-ownership)
- [Documentar ownership en catálogo de datos](../../estandares/datos/data-architecture.md#5-data-catalog)
- [Establecer gobernanza de datos](../../estandares/datos/data-architecture.md#4-data-governance)
- [Exponer datos solo mediante APIs o eventos, nunca por acceso directo](../../estandares/datos/data-architecture.md#6-data-exposure)
- [Versionar esquemas de acceso con migraciones controladas](../../estandares/datos/database-standards.md#1-database-migrations)

## Referencias Relacionadas

- [Datos por Dominio](datos-por-dominio.md)
- [Autonomía de Servicios](../arquitectura/autonomia-de-servicios.md)
- [Modelado de Dominio](../arquitectura/modelado-de-dominio.md)
