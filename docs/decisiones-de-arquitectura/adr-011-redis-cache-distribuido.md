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

| Criterio              | Redis | Memcached | In-Memory .NET | Hazelcast | Ignite |
|----------------------|-------|-----------|---------------|-----------|--------|
| **Agnosticidad**     | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ✅ Nativo | 🟡 Java | 🟡 Java |
| **Operación**        | ✅ Simple, clustering | ✅ Simple | ✅ Muy simple | 🟡 Complejo | 🟡 Complejo |
| **Persistencia**     | ✅ Opcional (RDB/AOF) | ❌ No | ❌ No | ✅ Opcional | ✅ Opcional |
| **Multi-tenancy**    | ✅ Namespaces | 🟡 Limitado | 🟡 Limitado | 🟡 Limitado | 🟡 Limitado |
| **Escalabilidad**    | ✅ Clustering | 🟡 Manual | ❌ No | ✅ Nativo | ✅ Nativo |
| **Ecosistema .NET**  | ✅ Excelente | 🟡 Limitado | ✅ Nativo | 🟡 Java | 🟡 Java |
| **Costos**           | ✅ Gratuito OSS | ✅ Gratuito OSS | ✅ Sin costos externos | ✅ Gratuito OSS | ✅ Gratuito OSS |
| **Comunidad**        | ✅ Muy activa | ✅ Activa | ✅ Microsoft | 🟡 Nicho | 🟡 Nicho |
| **Portabilidad**     | ✅ Multi-plataforma | ✅ Multi-plataforma | ❌ Solo .NET | 🟡 Java | 🟡 Java |

### Matriz de Decisión

| Solución         | Rendimiento | Características | Multi-tenancy | Escalabilidad | Recomendación         |
|------------------|-------------|----------------|---------------|---------------|-----------------------|
| **Redis**        | Excelente   | Muy rico       | Excelente     | Excelente     | ✅ **Seleccionada**    |
| **Memcached**    | Muy bueno   | Básico         | Limitado      | Buena         | 🟡 Alternativa         |
| **In-Memory .NET** | Muy bueno | Básico         | Limitado      | Limitada      | 🟡 Casos específicos   |
| **Hazelcast**    | Bueno       | Completo       | Limitado      | Excelente     | ❌ Descartada          |
| **Ignite**       | Bueno       | Completo       | Limitado      | Excelente     | ❌ Descartada          |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 3 instancias, 16GB RAM, multi-región, alta disponibilidad. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución         | Licenciamiento | Infraestructura | Operación      | TCO 3 años   |
|------------------|---------------|----------------|---------------|--------------|
| Redis            | OSS           | US$4,320/año   | US$36,000/año | US$120,960   |
| Memcached        | OSS           | US$3,600/año   | US$24,000/año | US$82,800    |
| Hazelcast        | OSS           | US$6,000/año   | US$30,000/año | US$108,000   |
| Ignite           | OSS           | US$6,000/año   | US$30,000/año | US$108,000   |
| In-Memory .NET   | OSS           | US$0           | US$0          | US$0         |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **Redis:** sin límite práctico, clustering nativo, persistencia opcional
- **Memcached:** sin persistencia, escalabilidad manual
- **Hazelcast/Ignite:** complejidad operativa, requiere expertise Java
- **In-Memory .NET:** limitado a procesos individuales, no distribuido

### Riesgos y mitigación

- **Complejidad operacional Redis:** mitigada con automatización y operadores Kubernetes
- **Gestión de memoria:** monitoreo proactivo y políticas de eviction
- **Alta disponibilidad:** clustering y replicación master-replica
- **Lock-in cloud:** mitigado usando solo tecnologías OSS y despliegue portable

---

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

- Todos los servicios nuevos deben usar Redis salvo justificación técnica documentada
- Se debe estandarizar la gestión de clustering, backups y monitoreo
- El equipo debe mantener expertise básico en operación Redis

---

## 🏗️ ARQUITECTURA DE DESPLIEGUE

- Redis Cluster: 3 masters + 3 replicas, sharding automático
- Failover: Redis Sentinel
- Backup: RDB snapshots + AOF
- Monitoreo: Redis Exporter + Prometheus
- Namespaces por país: `talma:peru:*`, `talma:ecuador:*`, `talma:colombia:*`, `talma:mexico:*`

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs Clave

- **Hit Ratio**: > 95% para datos frecuentes
- **Latencia P99**: < 1ms para operaciones GET
- **Throughput**: > 100K ops/sec por instancia
- **Memoria utilizada**: < 80% del límite
- **Conexiones activas**: Monitoreo de pool

### Alertas Críticas

- Memoria > 85%
- Hit ratio < 90%
- Latencia P99 > 5ms
- Instancias master down
- Replicación lag > 1s

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
