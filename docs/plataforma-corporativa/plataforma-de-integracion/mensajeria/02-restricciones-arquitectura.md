---
sidebar_position: 2
title: Restricciones de la Arquitectura
description: Limitaciones técnicas, organizativas y de proceso de la plataforma de mensajería Kafka KRaft.
---

# 2. Restricciones de la Arquitectura

## Restricciones Técnicas

| Restricción              | Valor                                           | Razón                                                                           |
| ------------------------ | ----------------------------------------------- | ------------------------------------------------------------------------------- |
| Tecnología de mensajería | Apache Kafka (KRaft mode)                       | Decisión arquitectónica; elimina dependencia de ZooKeeper                       |
| Versión mínima de Kafka  | `3.3+`                                          | KRaft está en producción estable desde Kafka 3.3                                |
| Plataforma de despliegue | AWS EC2 (no ECS Fargate)                        | Kafka requiere control de red, disco y JVM que EC2 provee mejor                 |
| Contenedores             | Docker en cada instancia EC2                    | Portabilidad y gestión de configuración uniforme                                |
| Topología mínima         | 2 Controllers + 2 Brokers                       | Quórum KRaft requiere mínimo 3 voters; se recomienda separar roles              |
| Factor de replicación    | `replication.factor=2` (mínimo)                 | Alta disponibilidad ante fallo de un broker                                     |
| Almacenamiento           | Volúmenes EBS gp3 dedicados por instancia       | Rendimiento de disco predecible; independiente del ciclo de vida del contenedor |
| Protocolo de red interno | Plaintext dentro de VPC; TLS en tráfico externo | Segmentación de red corporativa (ADR-007)                                       |
| Autenticación            | SASL/SCRAM-SHA-512                              | Estándar corporativo de autenticación de servicios                              |

## Restricciones Organizativas

| Restricción            | Descripción                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------- |
| Propiedad operativa    | El equipo de Plataforma es responsable del ciclo de vida del clúster Kafka                        |
| Creación de topics     | Solo el equipo de Plataforma puede crear topics en producción; via IaC o herramienta aprobada     |
| Convención de nombrado | Los topics siguen la convención `<dominio>.<servicio>.<entidad>.<evento>` definida en el glosario |
| Secretos               | Credenciales SASL y keystores nunca en repositorio; inyectados en EC2 vía AWS Secrets Manager     |
| Multi-país             | Un único clúster compartido con aislamiento por topic naming convention (PE, EC, CO, MX)          |

## Restricciones de Proceso

| Restricción              | Descripción                                                                                              |
| ------------------------ | -------------------------------------------------------------------------------------------------------- |
| Cambios de configuración | Cambios de `server.properties` o `docker-compose.yml` requieren PR + aprobación del equipo de Plataforma |
| Actualización de Kafka   | Requiere plan de rolling upgrade documentado y pruebas en staging antes de producción                    |
| Monitoreo obligatorio    | Todo broker expone métricas JMX al endpoint Prometheus antes de entrar a producción                      |
