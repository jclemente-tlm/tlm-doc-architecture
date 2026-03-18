---
sidebar_position: 2
title: Restricciones de la Arquitectura
description: Limitaciones técnicas, organizativas y de proceso del servicio CDC con Debezium.
---

# 2. Restricciones de la Arquitectura

## Restricciones Técnicas

| Restricción                      | Valor                                               | Razón                                                                               |
| -------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Motor de CDC                     | Debezium (Kafka Connect)                            | ADR-009; integración nativa con Kafka (ADR-008)                                     |
| Plataforma de despliegue         | AWS EC2 (contenedor Docker)                         | Consistente con el modelo Docker-en-EC2 del clúster Kafka; mismo modelo operacional |
| Formato de mensaje               | JSON                                                | Interoperabilidad con consumidores heterogéneos sin Schema Registry                 |
| Naming de topics CDC             | `<base-de-datos>.<schema>.<tabla>`                  | Convención por defecto de Debezium; trazabilidad directa a la fuente                |
| Almacenamiento de offsets        | Kafka topic `connect-offsets`                       | Gestión de posición de lectura persistente en Kafka                                 |
| Almacenamiento de schema history | Kafka topic `connect-schema-changes`                | Historial de cambios de esquema requerido por Debezium                              |
| Método de CDC                    | Log-based (transaction logs / WAL)                  | Sin impacto en la BD origen; menor latencia que polling o triggers                  |
| Replicación lógica en PostgreSQL | `wal_level=logical` obligatorio en BD origen        | Requisito de Debezium para leer el WAL de PostgreSQL                                |
| Credenciales de BD               | Usuario con permisos de replicación (`REPLICATION`) | Mínimo privilegio necesario para lectura del WAL                                    |
| Imagen Docker                    | `debezium/connect:2.5` (imagen oficial)             | Versión LTS estable; no usar `latest`                                               |

## Restricciones Organizativas

| Restricción             | Descripción                                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Propiedad operativa     | El equipo de Plataforma gestiona el ciclo de vida de los conectores Debezium                                          |
| Creación de conectores  | Solo vía IaC (Terraform + API de Kafka Connect); sin cambios manuales en producción                                   |
| Permisos de replicación | La habilitación de replicación lógica en BD origen requiere aprobación del DBA responsable                            |
| Datos sensibles         | Columnas con PII deben ser enmascaradas vía SMT antes de publicarse en Kafka; responsabilidad del equipo de Seguridad |
| Secretos                | Credenciales de BD nunca en repositorio; inyectadas vía AWS Secrets Manager (referenciadas en `docker-compose.yml`)   |

## Restricciones de Proceso

| Restricción                 | Descripción                                                                                                       |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Configuración de conectores | Cambios en la configuración del conector (filtros, SMT, tablas incluidas) requieren PR + revisión de Arquitectura |
| Snapshot inicial            | El snapshot inicial de tablas grandes debe planificarse en ventanas de bajo tráfico para evitar impacto en la BD  |
| Actualización de Debezium   | Requiere pruebas en staging; verificar compatibilidad de offset format entre versiones                            |
