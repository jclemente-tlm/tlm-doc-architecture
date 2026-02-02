---
id: esquemas-de-dominio
sidebar_position: 2
title: Esquemas de Dominio
description: Datos de dominio con esquemas explícitos, versionados y documentados
---

# Esquemas de Dominio

## 1. Declaración del Principio

Los datos del dominio (modelos, esquemas de BD, eventos de negocio) deben definirse mediante esquemas explícitos, versionados y documentados que permitan evolución controlada.

## 2. Propósito

Asegurar que los datos de dominio tengan definiciones claras, estables y evolutivas que faciliten comprensión, validación y cambios controlados.

> **Nota:** Este principio se enfoca en **esquemas de datos de dominio** (BD, modelos, eventos). Para contratos de APIs ver [Contratos de Comunicación](../../arquitectura/09-contratos-de-comunicacion.md).

## 3. Justificación

Cuando los esquemas de datos son implícitos, sin versionar o sin documentar, se genera fragilidad ante cambios, pérdida de control sobre la evolución y dificultad para mantener calidad de datos.

Los esquemas de dominio establecen una definición clara de estructuras de datos, tipos, restricciones y semántica del negocio.

## 4. Alcance Conceptual

Aplica específicamente a:

- Esquemas de bases de datos (tablas, columnas, tipos, constraints)
- Modelos de dominio persistidos
- Eventos de dominio (estructura de eventos de negocio)
- Esquemas de mensajes de dominio
- Archivos de intercambio de datos del dominio

No aplica a:

- Contratos de APIs REST/GraphQL (ver Contratos de Comunicación)
- DTOs de transporte (ver Contratos de Comunicación)

Este principio no prescribe tecnologías específicas, sino la necesidad de definiciones explícitas.

## 5. Implicaciones Arquitectónicas

- Los esquemas de BD deben gestionarse mediante migraciones versionadas.
- Los eventos de dominio deben tener esquemas documentados (JSON Schema, Avro).
- Los cambios de esquema deben evaluarse por su impacto (breaking vs non-breaking).
- La evolución de esquemas debe seguir estrategias compatibles (expand-contract).
- Los esquemas definen la semántica del dato, no solo su estructura.
- El versionado y la validación son mecanismos clave para calidad de datos.

## 6. Compensaciones (Trade-offs)

Reduce la flexibilidad inmediata para modificar estructuras internas, a cambio de mayor estabilidad, gobernanza y sostenibilidad del ecosistema de sistemas.

## 7. Relación con Decisiones Arquitectónicas (ADRs)

Este principio suele materializarse en decisiones relacionadas con:

- Versionado de esquemas y contratos
- Definición de datos públicos versus internos
- Estrategias de compatibilidad y evolución entre productores y consumidores
