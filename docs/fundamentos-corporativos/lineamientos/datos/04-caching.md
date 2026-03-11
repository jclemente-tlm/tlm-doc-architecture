---
id: caching
sidebar_position: 4
title: Caching
description: Estrategias de caché para reducir latencia, proteger backends y mejorar disponibilidad
---

# Caching

Sin una estrategia de caché deliberada, los servicios someten innecesariamente backends y bases de datos a cargas repetitivas, incrementan latencia y generan indisponibilidades en cascada ante picos de tráfico. Una estrategia de caché bien diseñada reduce latencia, protege backends críticos y mejora disponibilidad, pero requiere definir explícitamente qué cachear, por cuánto tiempo y cómo invalidar, para evitar datos desactualizados que compromentan consistencia o seguridad.

**Este lineamiento aplica a:** APIs con datos de lectura frecuente, validación de tokens JWT (JWKS), sesiones de usuario, configuración de tenants, respuestas de servicios externos y cualquier dato con alta frecuencia de lectura y baja frecuencia de cambio.

**No aplica a:** datos transaccionales que requieren consistencia fuerte; estrategias de almacenamiento persistente — ver [Datos por Dominio](./01-datos-por-dominio.md).

## Estándares Obligatorios

- [Definir TTL explícito para cada entrada cacheada; prohibir caché sin expiración](../../estandares/datos/caching.md#ttl-management)
- [Usar caché distribuido (Redis ElastiCache) para datos compartidos entre instancias](../../estandares/datos/caching.md#distributed-cache-redis-elasticache)
- [Implementar estrategia de invalidación explícita al mutar datos](../../estandares/datos/caching.md#cache-invalidation)
- [No cachear datos sensibles (tokens de acceso completos, contraseñas, PII) sin cifrado](../../estandares/seguridad/data-protection.md)
- [Monitorear hit rate, miss rate y latencia de caché](../../estandares/observabilidad/metrics.md)
- [Declarar dependencia de caché como pendiente si no está implementado (DT)](../../estandares/gobierno/adr-management.md)

## Referencias Relacionadas

- [Consistencia y Sincronización](./02-consistencia-y-sincronizacion.md)
- [Resiliencia y Disponibilidad](../arquitectura/04-resiliencia-y-disponibilidad.md)
- [Escalabilidad y Rendimiento](../arquitectura/05-escalabilidad-y-rendimiento.md)
- [Observabilidad](../operabilidad/05-observabilidad.md)
