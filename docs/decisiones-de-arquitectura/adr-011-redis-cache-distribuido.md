---
title: "ADR-011: Redis Cache Distribuido"
sidebar_position: 11
---

## 🔄 ESTADO

Propuesta – Febrero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución de cache distribuido que permita:

- **Aceleración de acceso a datos críticos y reducción de latencia**
- **Escalabilidad horizontal y alta disponibilidad**
- **Multi-tenancy** con separación por país y cliente
- **Persistencia opcional para datos críticos**
- **Integración nativa con .NET y ecosistema cloud**
- **Observabilidad y monitoreo centralizado**
- **Portabilidad entre clouds y on-premises**
- **Costos controlados y sin lock-in de proveedor**

Alternativas evaluadas:

- **Redis OSS** (open source, self-hosted, clustering, integración .NET)
- **AWS ElastiCache for Redis** (gestionado AWS, alta disponibilidad)
- **Azure Cache for Redis** (gestionado Azure, integración nativa .NET)
- **Valkey** (fork OSS de Redis, Linux Foundation)
- **Memcached OSS** (open source, simple, sin persistencia)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio                | Redis OSS               | AWS ElastiCache for Redis | Azure Cache for Redis    | Valkey                  | Memcached OSS           |
| ----------------------- | ----------------------- | ------------------------- | ------------------------ | ----------------------- | ----------------------- |
| **Agnosticidad**        | ✅ OSS, multi-cloud     | ❌ Lock-in AWS            | ❌ Lock-in Azure         | ✅ OSS, multi-cloud     | ✅ OSS, multi-cloud     |
| **Operación**           | ⚠️ Self-hosted          | ✅ Totalmente gestionado  | ✅ Totalmente gestionado | ⚠️ Self-hosted          | ⚠️ Self-hosted          |
| **Persistencia**        | ✅ Opcional (RDB/AOF)   | ✅ Automática             | ✅ Automática            | ✅ Opcional (RDB/AOF)   | ❌ No                   |
| **Multi-tenancy**       | ✅ Namespaces           | ✅ Namespaces             | ✅ Namespaces            | ✅ Namespaces           | ⚠️ Limitado             |
| **Escalabilidad**       | ✅ Clustering manual    | ✅ Automática             | ✅ Automática            | ✅ Clustering manual    | ⚠️ Manual               |
| **Ecosistema .NET**     | ✅ Excelente            | ✅ Excelente              | ✅ Nativo Microsoft      | ✅ Compatible Redis     | ⚠️ Limitado             |
| **Costos**              | ✅ Solo infraestructura | ⚠️ Pago por uso           | ⚠️ Pago por uso          | ✅ Solo infraestructura | ✅ Solo infraestructura |
| **Comunidad**           | ✅ Muy activa           | ✅ Soporte AWS            | ✅ Soporte Microsoft     | ✅ Linux Foundation     | ✅ Activa               |
| **Alta disponibilidad** | ⚠️ Manual (Sentinel)    | ✅ Multi-AZ automática    | ✅ Geo-replicación       | ⚠️ Manual (Sentinel)    | ⚠️ Manual               |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

## ✔️ DECISIÓN

Se selecciona **Redis OSS (self-hosted)** como solución estándar de cache distribuido para todos los servicios y microservicios corporativos.

## Justificación

- **Control total y portabilidad:** sin lock-in AWS, migrable entre clouds
- **Costos optimizados:** solo infraestructura vs ElastiCache (pago por uso premium)
- Soporte avanzado para estructuras de datos, pub/sub, streams
- Multi-tenancy nativo con namespaces y separación por país
- Escalabilidad horizontal con clustering Redis Cluster
- Persistencia opcional para datos críticos (RDB/AOF)
- Integración excelente con .NET y StackExchange.Redis
- Despliegue en contenedores (ECS Fargate) con automatización Terraform
- Comunidad global activa y abundante documentación
- Observabilidad con Prometheus y Grafana (ya implementados)

## Alternativas descartadas

- **AWS ElastiCache for Redis:** lock-in AWS, costos premium (US$0.034/hora/nodo = ~US$3K/año vs US$600/año self-hosted), menor control operacional
- **Azure Cache for Redis:** lock-in Azure, infraestructura AWS ya establecida (ADR-003, ADR-005, ADR-007), costos similares a ElastiCache, requeriría integración cross-cloud
- **Valkey:** fork muy reciente (2024), ecosistema aún inmaduro, preferible esperar mayor adopción
- **Memcached OSS:** sin persistencia, funcionalidad limitada (solo key-value), no soporta estructuras de datos avanzadas

---

## ⚠️ CONSECUENCIAS

### Positivas

- Soporte avanzado para estructuras de datos (strings, hashes, lists, sets, sorted sets)
- Pub/sub y streams para mensajería ligera
- Multi-tenancy con namespaces por país/tenant
- Escalabilidad horizontal con clustering nativo
- Persistencia opcional (RDB/AOF) para datos críticos
- Integración excelente con .NET (StackExchange.Redis)

### Negativas (Riesgos y Mitigaciones)

- **Operación self-hosted:** mitigada con contenedores (ECS Fargate), automatización Terraform y monitoreo Grafana
- **Alta disponibilidad manual:** requiere configurar Redis Sentinel o Cluster mode, mitigado con IaC y runbooks
- **Gestión memoria:** mitigada con monitoreo proactivo (Prometheus) y políticas eviction (LRU/LFU)
- **Backups manuales:** mitigados con snapshots RDB programados y replicación a S3

---

## 📚 REFERENCIAS

- [Redis Documentation](https://redis.io/documentation)
- [Redis Clustering Guide](https://redis.io/docs/manual/scaling/)
- [StackExchange.Redis](https://github.com/StackExchange/StackExchange.Redis)
- [AWS ElastiCache Pricing](https://aws.amazon.com/elasticache/pricing/)
- [Azure Cache for Redis Pricing](https://azure.microsoft.com/en-us/pricing/details/cache/)
- [Valkey Project](https://valkey.io/)
