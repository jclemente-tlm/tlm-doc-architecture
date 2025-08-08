---
id: adr-011-cache-distribuido
title: "Cache Distribuido"
sidebar_position: 11
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución de caché distribuida para:

- **Reducir latencia** en consultas frecuentes y datos de referencia
- **Mejorar rendimiento** de APIs con alta concurrencia
- **Almacenar sesiones** de usuarios de forma distribuida
- **Cache de configuraciones** y metadatos compartidos
- **Soporte multi-tenant** con aislamiento por país/cliente
- **Portabilidad** entre clouds y on-premises

La intención estratégica es **mantenerse agnóstico** y seleccionar una solución portable y escalable.

Las alternativas evaluadas fueron:

- **Redis** (Open source, in-memory, agnóstico)
- **Memcached** (Open source, simple, agnóstico)
- **Hazelcast** (Open source, distribuido, Java)
- **Apache Ignite** (Open source, distribuido, Java)
- **In-Memory .NET** (Propietario, local, .NET)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | Redis | Memcached | Hazelcast | Apache Ignite | In-Memory .NET |
|----------|-------|-----------|-----------|---------------|----------------|
| **Rendimiento** | ✅ Excelente, sub-ms | ✅ Excelente, muy rápido | ✅ Muy bueno | ✅ Muy bueno | ✅ Excelente local |
| **Características** | ✅ Muy rico (pub/sub, etc) | 🟡 Solo key-value básico | ✅ Completo, distribuido | ✅ Completo, SQL | 🟡 Básico, local |
| **Ecosistema .NET** | ✅ StackExchange.Redis | 🟡 Soporte básico | ✅ Cliente oficial | 🟡 Soporte limitado | ✅ Nativo .NET |
| **Escalabilidad** | ✅ Cluster, sharding | ✅ Horizontal simple | ✅ Distribuido nativo | ✅ Distribuido nativo | 🟡 Solo vertical |
| **Operación** | ✅ Simple, bien documentado | ✅ Muy simple | 🟡 Complejo, Java | 🟡 Complejo, Java | ✅ Sin infraestructura |
| **Comunidad** | ✅ Muy activa, popular | ✅ Madura, estable | 🟡 Activa, nicho | 🟡 Menor, Apache | ✅ Microsoft + .NET |
| **Costos** | ✅ Gratuito OSS | ✅ Completamente gratuito | 🟡 Enterprise de pago | ✅ Gratuito Apache | ✅ Sin costos externos |

### Matriz de Decisión

| Solución | Rendimiento | Características | Ecosistema .NET | Escalabilidad | Recomendación |
|----------|-------------|-----------------|-----------------|---------------|--------------|
| **Redis** | Excelente | Muy rico | Excelente | Excelente | ✅ **Seleccionada** |
| **Memcached** | Excelente | Básico | Limitado | Buena | 🟡 Alternativa |
| **In-Memory .NET** | Excelente | Básico | Nativo | Limitada | 🟡 Casos específicos |
| **Hazelcast** | Muy bueno | Completo | Bueno | Excelente | ❌ Descartada |
| **Apache Ignite** | Muy bueno | Completo | Limitado | Excelente | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 16GB RAM, 3 instancias, multi-región

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **Redis** | US$0 (OSS) | US$4,320/año | US$36,000/año | **US$120,960** |
| **Memcached** | US$0 (OSS) | US$3,600/año | US$24,000/año | **US$82,800** |
| **ElastiCache** | Pago por uso | US$0 | US$0 | **US$15,768/año** |
| **Azure Cache** | Pago por uso | US$0 | US$0 | **US$17,280/año** |
| **Memorystore** | Pago por uso | US$0 | US$0 | **US$16,200/año** |

### Escenario Alto Volumen: 128GB RAM, cluster

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| **Redis** | **US$360,000** | Manual con clustering |
| **ElastiCache** | **US$126,144** | Automática |
| **Azure Cache** | **US$138,240** | Automática |
| **Memorystore** | **US$129,600** | Automática |
| **Memcached** | **US$240,000** | Manual, sin persistencia |

## ⚖️ DECISIÓN

**Seleccionamos Redis** como solución de caché por:

### Ventajas Clave
- **Máxima agnosticidad**: Deployable en cualquier infraestructura
- **Funcionalidades ricas**: Estructuras de datos avanzadas, pub/sub, streams
- **Persistencia opcional**: RDB + AOF para durabilidad
- **Clustering nativo**: Escalabilidad horizontal automática
- **Multi-tenancy**: Namespaces y bases de datos separadas
- **Ecosistema maduro**: Herramientas, monitoreo, librerías

### Mitigación de Desventajas
- **Complejidad operacional**: Mitigada con Kubernetes operators y automatización
- **Gestión de memoria**: Monitoreo proactivo y políticas de eviction
- **Alta disponibilidad**: Configuración master-replica con sentinel

### Patrones de Uso Definidos
```yaml
Casos de Uso por Servicio:
  API Gateway:
    - Rate limiting counters
    - JWT blacklist
    - Configuraciones dinámicas

  Servicio Identidad:
    - Sesiones de usuario
    - Tokens de refresh
    - Configuraciones de realm

  Servicio Notificación:
    - Templates compilados
    - Configuraciones de canal
    - Métricas en tiempo real

  Track & Trace:
    - Estados de entidad
    - Snapshots de agregados
    - Índices de búsqueda
```

## 🔄 CONSECUENCIAS

### Positivas
- ✅ **Portabilidad completa** sin dependencias de proveedor
- ✅ **Rendimiento superior** con latencias sub-milisegundo
- ✅ **Funcionalidades avanzadas** más allá del caché simple
- ✅ **Persistencia opcional** para datos críticos
- ✅ **Multi-tenancy nativo** con separación por namespace
- ✅ **Integración .NET excelente** con StackExchange.Redis

### Negativas
- ❌ **Mayor responsabilidad operacional** requiere expertise
- ❌ **Gestión de memoria manual** y políticas de eviction
- ❌ **Configuración de clustering** compleja para alta disponibilidad

### Neutras
- 🔄 **Monitoreo especializado** requerido pero estándar
- 🔄 **Backup y recovery** necesarios para datos persistentes

## 🏗️ ARQUITECTURA DE DESPLIEGUE

### Configuración de Alta Disponibilidad
```yaml
Redis Cluster:
  Topología: 3 masters + 3 replicas
  Sharding: Automático por hash slots
  Failover: Redis Sentinel
  Backup: RDB snapshots + AOF
  Monitoreo: Redis Exporter + Prometheus
```

### Configuración Multi-tenant
```yaml
Separación por País:
  talma:peru:*     # Namespace para Perú
  talma:ecuador:*  # Namespace para Ecuador
  talma:colombia:* # Namespace para Colombia
  talma:mexico:*   # Namespace para México
```

### Políticas de Caché
```yaml
Configuraciones:
  maxmemory: 80% de RAM disponible
  maxmemory-policy: allkeys-lru
  timeout: 300s para conexiones idle
  tcp-keepalive: 300s

TTL por Tipo de Dato:
  Configuraciones: 1 hora
  Sesiones: 24 horas
  Templates: 4 horas
  Métricas: 5 minutos
```

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

## 📚 REFERENCIAS

- [Redis Documentation](https://redis.io/documentation)
- [Redis Clustering Guide](https://redis.io/docs/manual/scaling/)
- [StackExchange.Redis](https://github.com/StackExchange/StackExchange.Redis)
- [Redis Best Practices](https://redis.io/docs/manual/clients-guide/)

---

**Decisión tomada por:** Equipo de Arquitectura
**Fecha:** Agosto 2025
**Próxima revisión:** Agosto 2026
