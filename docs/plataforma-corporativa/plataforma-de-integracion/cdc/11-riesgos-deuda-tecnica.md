---
sidebar_position: 11
title: Riesgos y Deuda Técnica
description: Mapa de riesgos y deuda técnica del servicio CDC con Debezium.
---

# 11. Riesgos y Deuda Técnica

## Riesgos Técnicos

| ID    | Riesgo                                                   | Severidad | Probabilidad | Mitigación                                                                              |
| ----- | -------------------------------------------------------- | --------- | ------------ | --------------------------------------------------------------------------------------- |
| RT-01 | Inflado del disco de la BD por replication slot inactivo | 🔴 Alta   | Media        | Monitorear `pg_replication_slots`; alertar si el lag supera 1 GB de WAL acumulado       |
| RT-02 | Invalidación del replication slot tras restart de la BD  | 🔴 Alta   | Baja         | Procedimiento documentado de recreación de slot + snapshot; alerta ante conector FAILED |
| RT-03 | Saturación del pipeline WAL bajo carga extrema           | ⚠️ Media  | Baja         | Pruebas de carga con 15k ev/s; ajustar `max.queue.size` y `max.batch.size` del conector |
| RT-04 | Pérdida de offset por fallo total del clúster Kafka      | ⚠️ Media  | Muy Baja     | Backup periódico del topic `connect-offsets`; snapshot mode `initial` como recovery     |

## Riesgos Operacionales

| ID    | Riesgo                                                      | Severidad | Probabilidad | Mitigación                                                                                       |
| ----- | ----------------------------------------------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------ |
| RO-01 | Impacto en rendimiento de la BD durante el snapshot inicial | ⚠️ Media  | Alta         | Programar snapshots en ventanas de baja carga; usar `snapshot.fetch.size` controlado             |
| RO-02 | Conector en estado FAILED sin alertas activas               | 🔴 Alta   | Media        | Configurar alerta por `task_status != 0`; verificar estado diariamente hasta DT-03               |
| RO-03 | Credenciales de conector expiradas sin rotación automática  | 🟡 Baja   | Media        | Usar AWS Secrets Manager con rotación automática; conector refrescado al reiniciar el contenedor |

## Deuda Técnica

| ID    | Descripción                                                                                     | Área           | Esfuerzo | Impacto si no se resuelve                                                        |
| ----- | ----------------------------------------------------------------------------------------------- | -------------- | -------- | -------------------------------------------------------------------------------- |
| DT-01 | Sin Schema Registry: consumidores no pueden validar el contrato del mensaje de forma automática | Integración    | Alto     | Cambios de esquema en la BD pueden romper consumidores sin aviso previo          |
| DT-02 | Enmascaramiento PII no es obligatorio: el proceso de registro de conectores no lo valida        | Seguridad      | Medio    | Datos sensibles en Kafka pueden quedar expuestos a consumidores no autorizados   |
| DT-03 | Dashboards Grafana para lag de CDC no implementados                                             | Observabilidad | Bajo     | Degradación del servicio puede pasar desapercibida hasta que afecte consumidores |
| DT-04 | Registro de conectores no está automatizado por IaC: requiere `POST /connectors` manual         | Automatización | Medio    | Alta dependencia del equipo de Plataforma para onboarding de nuevas tablas       |

## Plan de Contingencia

| Escenario                                     | Respuesta                                                                                                                         |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Replication slot invalidado                   | Eliminar y recrear el conector con `snapshot.mode=initial`; notificar a consumidores del re-snapshot                              |
| Worker no responde                            | Docker reinicia el contenedor automáticamente (restart policy); si persiste, revisar logs en Loki y reconectar a la instancia EC2 |
| Disco de BD Origin saturado por slot inactivo | Pausar el conector (`PUT /connectors/{name}/pause`); recrear slot tras restaurar espacio                                          |
| BD Origin no disponible ≥ 10 min              | Conector en FAILED; cuando la BD restablezca, reiniciar conector (`POST /connectors/{name}/resume`)                               |
