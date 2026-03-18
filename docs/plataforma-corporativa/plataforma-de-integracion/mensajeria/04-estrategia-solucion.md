---
sidebar_position: 4
title: Estrategia de Solución
description: Decisiones tecnológicas y de diseño clave de la plataforma de mensajería Kafka KRaft.
---

# 4. Estrategia de Solución

## Decisiones Tecnológicas

| Dimensión           | Decisión                                      | Justificación                                                                            |
| ------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Message broker      | **Apache Kafka**                              | Throughput alto, retención persistente, semántica de replay y ecosistema maduro          |
| Modo de consenso    | **KRaft** (sin ZooKeeper)                     | Elimina dependencia operativa de ZooKeeper; menor latencia de elección de líder (DEC-01) |
| Despliegue          | **Docker en EC2** (no ECS Fargate)            | Control total de red, disco y JVM; Kafka requiere configuración de bajo nivel (DEC-02)   |
| Almacenamiento      | **EBS gp3** montado en cada instancia         | IOPS predecible, bajo costo, persistencia independiente del ciclo del contenedor         |
| Autenticación       | **SASL/SCRAM-SHA-512**                        | Autenticación de productores/consumidores sin PKI compleja                               |
| Separación de roles | **Controllers dedicados** (no modo combinado) | Aislamiento de responsabilidades; controllers no alojan particiones (DEC-03)             |
| Observabilidad      | **JMX Exporter → Prometheus → Mimir/Grafana** | Stack corporativo de observabilidad; dashboards estándar de Kafka en Grafana             |
| Configuración       | **IaC + Ansible/Terraform**                   | Reproducibilidad y trazabilidad de la configuración del clúster                          |

## Modelo de Topología KRaft

```
Quórum KRaft (Controllers):
    Controller-1  ──┐
    Controller-2  ──┼──▶  Consenso Raft (metadata log)**
                        Requiere mínimo 2/3 votes para elección de líder

Capa de datos (Brokers):
    Broker-1  ──┐
    Broker-2  ──┴──▶  Particiones replicadas (replication.factor=2)
```

El quórum de controllers necesita mayoría simple. Con 2 controllers, se tolera **0 fallos** simultáneos en el quórum. Para producción de alta criticidad se recomienda escalar a 3 controllers (ver DT-01).

## Convención de Nombrado de Topics

```
<dominio>.<servicio>.<entidad>.<evento>

Ejemplos:
  logistica.track-trace.shipment.created
  notificaciones.notifications.email.sent
  identidad.identity.user.login-failed
  cdc.erp.tabla-operaciones.row-changed
```

Esta convención permite application de ACLs por prefijo y consulta eficiente de topics por equipo.
