---
sidebar_position: 9
title: Decisiones de Arquitectura
description: Registro de decisiones arquitectónicas del stack de observabilidad corporativo.
---

# 9. Decisiones de Arquitectura

## Decisión Principal

| Campo          | Valor                                                                    |
| -------------- | ------------------------------------------------------------------------ |
| **ADR**        | ADR-014 — Adopción del Grafana Stack OSS para Observabilidad Corporativa |
| **Estado**     | Aceptado                                                                 |
| **Fecha**      | Agosto 2025                                                              |
| **Referencia** | [ADR-014](../../../adrs/adr-014-grafana-stack-observabilidad.md)         |

## Registro de Decisiones de Componente

### DEC-01 — Grafana Stack OSS frente a alternativas SaaS

| Campo             | Valor                                                                                                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID**            | DEC-01                                                                                                                                                                                     |
| **Estado**        | Aceptado                                                                                                                                                                                   |
| **Contexto**      | Se evaluaron Datadog (~$18K–37K/año), Splunk (~$450K/año), AWS CloudWatch y ELK Stack. El volumen y distribución multi-país de los servicios requería una solución escalable sin lock-in.  |
| **Decisión**      | Adoptar el stack Grafana OSS (Loki + Mimir + Tempo + Grafana + Alloy).                                                                                                                     |
| **Consecuencias** | ✅ $0 en licencias; ~$200–500/mes en infraestructura. ✅ Sin lock-in de proveedor. ✅ Stack integrado con correlación nativa entre señales. ⚠️ Requiere ~1 FTE (10-20 h/sem) de operación. |

---

### DEC-02 — Multi-tenancy estratégica (criterios distintos por señal)

| Campo             | Valor                                                                                                                                                                                                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID**            | DEC-02                                                                                                                                                                                                                                                                                     |
| **Estado**        | Aceptado                                                                                                                                                                                                                                                                                   |
| **Contexto**      | Inicialmente se evaluó usar el mismo criterio de tenant para las tres señales (e.g. país para todo). Sin embargo, el tenant óptimo difiere: logs necesitan segregación por país (compliance), métricas por ambiente (dashboards consolidados) y trazas por servicio (integridad de spans). |
| **Decisión**      | Logs → tenant por país; métricas → tenant por ambiente; trazas → tenant por dominio de servicio.                                                                                                                                                                                           |
| **Consecuencias** | ✅ Cada señal sigue el criterio de segregación más adecuado para su caso de uso. ✅ Dashboards de infraestructura muestran todos los países en `prod` en una sola vista. ⚠️ El routing de Envoy requiere lógica Lua para distinguir señal por ruta.                                        |

---

### DEC-03 — Envoy Proxy como gateway unificado con Lua filters

| Campo             | Valor                                                                                                                                                                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **ID**            | DEC-03                                                                                                                                                                                                                                           |
| **Estado**        | Aceptado                                                                                                                                                                                                                                         |
| **Contexto**      | Los agentes Alloy necesitan un único endpoint de destino para simplificar su configuración. La inyección del header `X-Scope-OrgID` diferenciado por señal no puede delegarse al cliente.                                                        |
| **Decisión**      | Usar Envoy Proxy con Lua filters que evalúan la ruta HTTP y reescriben el header `X-Scope-OrgID` antes de reenviar al backend.                                                                                                                   |
| **Consecuencias** | ✅ Los agentes solo necesitan conocer la IP del servidor, no los puertos de cada backend. ✅ La lógica de tenant centralizada en el proxy facilita cambios futuros. ⚠️ Los Lua filters de Envoy requieren conocimiento de la API de Envoy y Lua. |

---

### DEC-04 — Grafana Alloy como recolector universal (reemplaza 3 agentes)

| Campo             | Valor                                                                                                                                                                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID**            | DEC-04                                                                                                                                                                                                                                  |
| **Estado**        | Aceptado                                                                                                                                                                                                                                |
| **Contexto**      | El stack anterior requería Promtail (logs), Prometheus Agent (métricas) y OpenTelemetry Collector (trazas) por separado. Cada agente tenía su propia configuración y ciclo de vida.                                                     |
| **Decisión**      | Usar Grafana Alloy como agente único con pipelines `.alloy` independientes por señal.                                                                                                                                                   |
| **Consecuencias** | ✅ Un solo contenedor por host en lugar de tres. ✅ Configuración unificada con variables de entorno compartidas. ✅ UI de diagnóstico integrada en `:12345`. ⚠️ Sintaxis de configuración `.alloy` (River) tiene curva de aprendizaje. |

---

### DEC-05 — MinIO en lugar de AWS S3 nativo

| Campo             | Valor                                                                                                                                                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ID**            | DEC-05                                                                                                                                                                                                                      |
| **Estado**        | Aceptado                                                                                                                                                                                                                    |
| **Contexto**      | Loki, Mimir y Tempo requieren almacenamiento S3-compatible. AWS S3 nativo implicaría dependencia de red en cada escritura y lectura, además de costos variables.                                                            |
| **Decisión**      | Desplegar MinIO en el mismo host que los backends del servidor.                                                                                                                                                             |
| **Consecuencias** | ✅ Latencia de almacenamiento < 1 ms (loopback de red Docker). ✅ Sin costo por petición S3. ✅ Console web en `:9001` para gestión manual de buckets. ⚠️ Capacidad de almacenamiento ligada al disco del EC2 del servidor. |
