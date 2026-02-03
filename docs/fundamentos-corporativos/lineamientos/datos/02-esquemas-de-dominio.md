---
id: esquemas-de-dominio
sidebar_position: 2
title: Esquemas de Dominio
description: Definición explícita de esquemas de dominio versionados y documentados
---

# Esquemas de Dominio

Esquemas implícitos o sin versionar generan errores en runtime, incompatibilidades entre servicios y dificultad para evolucionar modelos. Migraciones versionadas (Flyway, Liquibase) y esquemas documentados (JSON Schema, Avro) actúan como contratos explícitos que permiten validación automática y evolución controlada sin romper consumidores existentes.

**Este lineamiento aplica a:** esquemas de bases de datos, eventos de dominio, modelos persistidos, mensajes asíncronos y archivos de intercambio.

## Estándares Obligatorios

- [Versionar esquemas de BD con migraciones automatizadas](../../estandares/datos/database-migrations.md)
- [Documentar esquemas de eventos con JSON Schema o Avro](../../estandares/mensajeria/schemas-eventos.md)
- [Validar datos contra esquemas antes de persistir](../../estandares/datos/schema-validation.md)
- [Gestionar cambios con estrategias expand-contract](../../estandares/datos/schema-evolution.md)
- [Publicar esquemas en registro centralizado](../../estandares/datos/schema-registry.md)
