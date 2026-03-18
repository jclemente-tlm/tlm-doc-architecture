---
sidebar_position: 11
title: Riesgos y Deuda Técnica
description: Riesgos técnicos y operacionales de la plataforma de mensajería Kafka KRaft.
---

# 11. Riesgos y Deuda Técnica

## Riesgos Técnicos

| ID    | Riesgo                                             | Probabilidad | Impacto | Severidad  | Mitigación                                                                                          |
| ----- | -------------------------------------------------- | ------------ | ------- | ---------- | --------------------------------------------------------------------------------------------------- |
| RT-01 | Pérdida del quórum KRaft (ambos controllers caen)  | Baja         | Crítico | 🔴 Crítico | Distribución en AZs distintas; hoja de ruta para escalar a 3 controllers (DT-01)                    |
| RT-02 | Pérdida de datos por fallo de broker con `acks=1`  | Media        | Alto    | ⚠️ Alto    | Exigir `acks=all` para eventos críticos; documentar política de configuración por tipo de evento    |
| RT-03 | Corrupción del log de datos en volumen EBS         | Baja         | Crítico | 🔴 Crítico | Snapshots EBS diarios; replicación entre brokers como fuente secundaria de recuperación             |
| RT-04 | Incompatibilidad en actualización de versión Kafka | Media        | Alto    | ⚠️ Alto    | Rolling upgrade documentado; pruebas en staging; respetar ventana de compatibilidad entre versiones |

## Riesgos Operacionales

| ID    | Riesgo                                                  | Probabilidad | Impacto | Severidad  | Mitigación                                                                                           |
| ----- | ------------------------------------------------------- | ------------ | ------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| RO-01 | Escalado manual de brokers ante picos de tráfico        | Media        | Medio   | 🟡 Medio   | Monitorear throughput en Grafana; establecer umbral de alerta para iniciar escalado con anticipación |
| RO-02 | Disco lleno en broker por retención no controlada       | Media        | Alto    | ⚠️ Alto    | Alerta al 80% de uso de disco; política de retención por topic revisada trimestralmente              |
| RO-03 | Consumer lag creciente no detectado a tiempo            | Media        | Medio   | 🟡 Medio   | Dashboard de consumer lag en Grafana con alerta en `> 10,000 msgs` por más de 5 minutos              |
| RO-04 | Exposición accidental del puerto `:9092` hacia internet | Baja         | Crítico | 🔴 Crítico | Security Groups restringen `:9092` y `:9093` solo a la VPC privada; revisión periódica de reglas     |

## Deuda Técnica

| ID    | Deuda                                                                        | Prioridad | Acción                                                                                       |
| ----- | ---------------------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------- |
| DT-01 | Quórum KRaft con solo 2 controllers no tolera fallo simultáneo de ambos      | Alta      | Escalar a 3 controllers en una tercera AZ para tolerar la pérdida de 1 controller            |
| DT-02 | Dashboards de Grafana para Kafka no implementados (consumer lag, throughput) | Alta      | Importar dashboards oficiales de Kafka para Grafana; configurar alertas sobre métricas clave |
| DT-03 | Schema Registry no implementado; contratos de mensajes no validados          | Media     | Evaluar Confluent Schema Registry o Apicurio; definir ADR de serialización                   |
| DT-04 | Escalado de brokers es manual; sin automatización ante picos                 | Media     | Diseñar runbook de escalado horizontal; evaluar scripts de Ansible para agregar brokers      |
| DT-05 | TLS entre brokers y producers/consumers no habilitado dentro de la VPC       | Media     | Habilitar listener `SSL` en brokers; configurar truststore en producers/consumers            |
| DT-06 | Snapshots EBS automáticos no configurados en Terraform                       | Alta      | Agregar `aws_dlm_lifecycle_policy` en el repositorio de IaC para snapshots diarios           |

## Plan de Contingencia

| Escenario                           | Respuesta                                                                                                                        |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Broker cae (un nodo)                | Controller promueve réplicas del otro broker como líderes automáticamente; sin intervención manual                               |
| Ambos controllers caen              | Datos en brokers siguen siendo legibles; escrituras de metadatos suspendidas; restaurar al menos 1 controller desde ami/snapshot |
| Disco lleno en un broker            | Aumentar volumen EBS (hot resize con gp3); o reducir retención del topic más pesado temporalmente                                |
| Corrupción de log en un broker      | Eliminar el broker del ISR, limpiar directorio de datos, reiniciar; Kafka re-sincroniza desde el líder                           |
| Restaurar configuración del clúster | `terraform apply` desde repositorio de IaC + `ansible-playbook deploy-broker.yml`                                                |
