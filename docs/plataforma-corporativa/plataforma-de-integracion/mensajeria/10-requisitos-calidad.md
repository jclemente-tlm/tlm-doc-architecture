---
sidebar_position: 10
title: Requisitos de Calidad
description: Atributos y escenarios de calidad de la plataforma de mensajería Kafka KRaft.
---

# 10. Requisitos de Calidad

## Rendimiento

| Métrica                         | Objetivo         | Crítico          | Medición                                   |
| ------------------------------- | ---------------- | ---------------- | ------------------------------------------ |
| Throughput productor por broker | `> 50,000 msg/s` | `> 20,000 msg/s` | Métricas JMX → Mimir, dashboard Grafana    |
| Latencia de produce (p95)       | `< 20ms`         | `< 50ms`         | Métricas del producer (`record-send-rate`) |
| Latencia end-to-end (p95)       | `< 100ms`        | `< 200ms`        | Diferencia timestamp produce vs consume    |
| Consumer lag                    | `< 1,000 msgs`   | `< 10,000 msgs`  | `kafka_consumer_lag` en Grafana            |

## Disponibilidad

| Componente                   | SLA   | Downtime máx./mes | RTO                                               |
| ---------------------------- | ----- | ----------------- | ------------------------------------------------- |
| Clúster Kafka (2 brokers)    | 99.9% | 43.2 min          | < 30s (elección automática de líder de partición) |
| Quórum KRaft (2 controllers) | 99.9% | 43.2 min          | < 30s (elección de líder Raft)                    |
| Volúmenes EBS (gp3 multi-AZ) | 99.9% | 43.2 min          | EC2 en diferente AZ asume liderazgo               |

## Durabilidad

| Aspecto                 | Requisito                                                 | Implementación                      |
| ----------------------- | --------------------------------------------------------- | ----------------------------------- |
| Pérdida de mensajes     | Cero pérdida para eventos críticos                        | `acks=all`, `min.insync.replicas=2` |
| Retención mínima        | 7 días para todos los topics                              | `log.retention.hours=168`           |
| Replicación             | Factor 2 obligatorio                                      | `default.replication.factor=2`      |
| Persistencia de offsets | Offsets nunca en memoria; siempre en `__consumer_offsets` | Configuración por defecto de Kafka  |

## Seguridad

| Aspecto             | Requisito                                        | Implementación                           |
| ------------------- | ------------------------------------------------ | ---------------------------------------- |
| Autenticación       | Obligatoria para todos los producers y consumers | SASL/SCRAM-SHA-512                       |
| Autorización        | ACLs por prefijo de dominio                      | Kafka ACL API (`kafka-acls.sh`)          |
| Cifrado en tránsito | TLS para conexiones desde fuera de la VPC        | Listener `SSL` en puerto `:9093` externo |
| Secretos            | Nunca en repositorio ni en imágenes              | AWS Secrets Manager                      |

## Escenarios de Calidad

| ID   | Estímulo                                            | Respuesta Esperada                                                                           |
| ---- | --------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Q-01 | 50,000 mensajes/s sostenidos hacia un topic         | Latencia p95 < 20ms; sin pérdida de mensajes; consumer lag < 1,000                           |
| Q-02 | Broker-1 falla abruptamente                         | Controller promueve réplicas en Broker-2 como líderes en < 30s; producers reconectan solos   |
| Q-03 | Controller-1 falla                                  | Controller-2 asume el quórum KRaft; operaciones de metadatos suspendidas < 30s; datos OK     |
| Q-04 | Consumer group A se detiene 6 horas                 | Mensajes retenidos 7 días; al reiniciar, consumer retoma desde el último offset confirmado   |
| Q-05 | Disco de Broker-1 al 90%                            | Alerta disparada en Grafana; broker no acepta nuevas escrituras; equipo notificado en < 5min |
| Q-06 | Producer publica con `acks=all` a broker sin quórum | Kafka retorna `NotEnoughReplicasException`; producer reintenta según `retries` configurado   |
