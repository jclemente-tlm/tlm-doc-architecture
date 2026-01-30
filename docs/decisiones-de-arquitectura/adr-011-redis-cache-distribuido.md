---
title: "ADR-011: Redis Cache Distribuido"
sidebar_position: 11
---

## ✅ ESTADO

Aceptada – Agosto 2025

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

- **Redis** (open source, clustering, integración .NET, multi-tenant)
- **Memcached** (open source, simple, sin persistencia)
- **In-Memory .NET** (nativo, limitado a escenarios específicos)
- **Hazelcast** (open source, Java, complejidad operativa)
- **Apache Ignite** (open source, Java, complejidad operativa)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio            | Redis                 | Memcached           | In-Memory .NET         | Hazelcast       | Ignite          |
| ------------------- | --------------------- | ------------------- | ---------------------- | --------------- | --------------- |
| **Agnosticidad**    | ✅ OSS, multi-cloud   | ✅ OSS, multi-cloud | ✅ Nativo              | 🟡 Java         | 🟡 Java         |
| **Operación**       | ✅ Simple, clustering | ✅ Simple           | ✅ Muy simple          | 🟡 Complejo     | 🟡 Complejo     |
| **Persistencia**    | ✅ Opcional (RDB/AOF) | ❌ No               | ❌ No                  | ✅ Opcional     | ✅ Opcional     |
| **Multi-tenancy**   | ✅ Namespaces         | 🟡 Limitado         | 🟡 Limitado            | 🟡 Limitado     | 🟡 Limitado     |
| **Escalabilidad**   | ✅ Clustering         | 🟡 Manual           | ❌ No                  | ✅ Nativo       | ✅ Nativo       |
| **Ecosistema .NET** | ✅ Excelente          | 🟡 Limitado         | ✅ Nativo              | 🟡 Java         | 🟡 Java         |
| **Costos**          | ✅ Gratuito OSS       | ✅ Gratuito OSS     | ✅ Sin costos externos | ✅ Gratuito OSS | ✅ Gratuito OSS |
| **Comunidad**       | ✅ Muy activa         | ✅ Activa           | ✅ Microsoft           | 🟡 Nicho        | 🟡 Nicho        |
| **Portabilidad**    | ✅ Multi-plataforma   | ✅ Multi-plataforma | ❌ Solo .NET           | 🟡 Java         | 🟡 Java         |

## ✔️ DECISIÓN

Se selecciona **Redis** como solución estándar de cache distribuido para todos los servicios y microservicios corporativos.

## Justificación

- Open source, sin costos de licenciamiento y bajo TCO
- Soporte avanzado para estructuras de datos, pub/sub, streams
- Multi-tenancy nativo con namespaces y separación por país
- Escalabilidad horizontal automática con clustering
- Persistencia opcional para datos críticos
- Integración excelente con .NET y StackExchange.Redis
- Portabilidad total entre cloud y on-premises
- Comunidad global activa y abundante documentación
- Observabilidad y monitoreo con Prometheus y Grafana

## Alternativas descartadas

- **Memcached:** sin persistencia, funcionalidad limitada
- **In-Memory .NET:** no distribuido, solo para escenarios simples
- **Hazelcast:** complejidad operativa, requiere expertise Java
- **Ignite:** complejidad operativa, requiere expertise Java

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

- **Complejidad operacional:** mitigada con automatización Terraform y operadores Kubernetes
- **Gestión memoria:** mitigada con monitoreo proactivo y políticas eviction (LRU/LFU)
- **Alta disponibilidad:** requiere clustering y replicación master-replica configuradas

---

## 📚 REFERENCIAS

- [Redis Documentation](https://redis.io/documentation)
- [Redis Clustering Guide](https://redis.io/docs/manual/scaling/)
- [StackExchange.Redis](https://github.com/StackExchange/StackExchange.Redis)
- [Redis Best Practices](https://redis.io/docs/manual/clients-guide/)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
