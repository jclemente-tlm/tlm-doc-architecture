---
id: ownership-de-datos
sidebar_position: 1
title: Ownership de Datos por Dominio
description: Cada dominio es responsable exclusivo de sus datos sin compartir almacenamiento
---

# Ownership de Datos por Dominio

## 1. Declaración

Cada dominio de negocio es responsable exclusivo de sus propios datos: su definición, calidad, integridad y evolución, sin compartir almacenamiento ni permitir acceso directo desde otros dominios.

## 2. Justificación

Este principio busca garantizar autonomía de dominios, evitar acoplamiento implícito vía bases de datos compartidas y permitir evolución independiente de datos y esquemas.

Cuando múltiples dominios acceden directamente a una misma base de datos:

- Se genera acoplamiento oculto difícil de detectar
- Los cambios de esquema afectan a múltiples servicios
- Se pierde claridad sobre quién es responsable de la calidad de datos
- La evolución independiente se vuelve imposible

El ownership claro de datos establece límites arquitectónicos fundamentales y habilita autonomía real de dominios.

Cada dominio debe ser dueño de sus datos, no compartirlos directamente, y exponer información mediante APIs o eventos.

## 3. Alcance y Contexto

Aplica a:

- Arquitecturas de microservicios
- Monolitos modulares con límites de dominio
- Sistemas distribuidos
- Plataformas multi-dominio

No implica duplicación descontrolada de datos, sino ownership claro y acceso mediante interfaces definidas.

## 4. Implicaciones

- Cada dominio/servicio tiene su propia base de datos.
- No se permite acceso directo a bases de datos de otros dominios.
- Los datos se exponen mediante APIs, eventos o mecanismos de replicación controlada.
- El ownership de cada conjunto de datos debe estar documentado.
- Los cambios de esquema son responsabilidad exclusiva del dominio dueño.

**Compensaciones (Trade-offs):**

Puede generar duplicación controlada de datos, a cambio de mayor autonomía, claridad semántica y capacidad de evolución.
