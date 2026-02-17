---
title: "ADR-010: PostgreSQL Base de Datos"
sidebar_position: 10
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una solución robusta de base de datos relacional para:

- **Multi-tenancy robusto** con aislamiento por país/cliente (schemas, RLS)
- **Transacciones ACID** para integridad de datos críticos
- **Escalabilidad horizontal** (particionamiento, sharding)
- **Alta disponibilidad y replicación**
- **Soporte para datos semiestructurados** (JSON/JSONB)
- **Extensibilidad** con plugins y extensiones
- **Observabilidad** (métricas, logs, auditoría)
- **Cumplimiento regulatorio y cifrado**

La intención estratégica es **maximizar agnosticidad** y robustez empresarial, minimizando lock-in y costos.

Alternativas evaluadas:

- **PostgreSQL** (Open source, extensible, multi-tenant avanzado)
- **MySQL/MariaDB** (Open source, popular, funcionalidad básica)
- **SQL Server** (Microsoft, propietario, integración .NET)
- **Oracle Database** (Propietario, enterprise, alto costo)
- **Amazon Aurora** (Gestionado AWS, compatible MySQL/PostgreSQL)

## 🔍 COMPARATIVA DE ALTERNATIVAS

| Criterio                  | PostgreSQL                                   | MySQL                                        | Microsoft SQL Server                   | Oracle                                   | AWS Aurora                           |
| ------------------------- | -------------------------------------------- | -------------------------------------------- | -------------------------------------- | ---------------------------------------- | ------------------------------------ |
| **Agnosticidad**          | ✅ OSS, multi-cloud                          | ✅ OSS, multi-cloud                          | ❌ Lock-in Microsoft                   | ❌ Lock-in Oracle                        | ❌ Lock-in AWS                       |
| **Madurez**               | ✅ Muy alta (1996, ACID std)                 | ✅ Muy alta (1995, web std)                  | ✅ Muy alta (1989, Microsoft)          | ✅ Muy alta (1979, enterprise)           | ✅ Alta (2014, Aurora)               |
| **Adopción**              | ✅ Muy alta (16K⭐, DB del año)              | ✅ Muy alta (28K⭐, web standard)            | ✅ Muy alta (Microsoft legacy)         | ✅ Muy alta (enterprise líder)           | ✅ Alta (MySQL/PG compatible)        |
| **Modelo de gestión**     | ⚠️ Self-hosted                               | ⚠️ Self-hosted                               | ⚠️ Self-hosted                         | ⚠️ Self-hosted                           | ✅ Gestionado (AWS)                  |
| **Complejidad operativa** | ⚠️ Media (0.5 FTE, 5-10h/sem)                | ⚠️ Media (0.5 FTE, 5-10h/sem)                | ⚠️ Alta (1 FTE, 10-20h/sem)            | ❌ Muy Alta (2+ FTE, 20-40h/sem)         | ✅ Baja (0.25 FTE, <5h/sem)          |
| **Seguridad**             | ✅ Avanzada, RLS, cifrado                    | ⚠️ Básica                                    | ✅ Enterprise                          | ✅ Enterprise                            | ✅ Enterprise                        |
| **Integración .NET**      | ✅ Npgsql (20M+ DL/mes, .NET 6+, async/EF)   | ✅ MySql.Data (15M+ DL/mes, .NET 6+, EF)     | ✅ System.Data.SqlClient (nativo .NET) | ✅ Oracle.ManagedDataAccess (2M+ DL/mes) | ✅ Npgsql compatible                 |
| **Multi-tenancy**         | ✅ Schemas + RLS avanzado                    | ⚠️ Sin RLS nativo                            | ✅ Schemas + RLS                       | ✅ VPD avanzado                          | ✅ PostgreSQL                        |
| **Latencia**              | ✅ p95 <10ms                                 | ✅ p95 <10ms                                 | ✅ p95 <5ms                            | ✅ p95 <5ms                              | ✅ p95 <5ms                          |
| **Rendimiento**           | ✅ 5K-10K TPS                                | ✅ 5K-10K TPS                                | ✅ 10K+ TPS                            | ✅ 20K+ TPS                              | ✅ 15K+ TPS                          |
| **Escalabilidad**         | ✅ Hasta 10TB+ DB, 20K TPS (Apple, Spotify)  | ⚠️ <1TB DB máx recomendado (InnoDB limits)   | ⚠️ Hasta 4TB+ DB (Always On)           | ⚠️ Multi-TB DB, 50K+ TPS (RAC Oracle)    | ✅ Hasta 100TB+ DB, 40K TPS (Aurora) |
| **Alta disponibilidad**   | ✅ 99.9% estimado (replicación master-slave) | ⚠️ 99.5% estimado (replicación master-slave) | ✅ 99.99% SLA (Always On clustering)   | ✅ 99.99% SLA (RAC clustering)           | ✅ 99.99% SLA Multi-AZ               |
| **Extensibilidad**        | ✅ Plugins, JSONB, PostGIS                   | ⚠️ Limitada                                  | ⚠️ Limitada                            | ✅ Máxima                                | ⚠️ Limitada                          |
| **Portabilidad**          | ✅ Multi-plataforma                          | ✅ Multi-plataforma                          | ❌ Windows principal                   | ❌ Limitada                              | ❌ AWS                               |
| **Costos**                | ✅ $0 licencia + ~$100-300/mes infra         | ✅ $0 licencia + ~$100-300/mes infra         | ❌ $967-14.5K/mes licencia             | ❌ $47.5K/processor/año + 22% soporte    | ⚠️ $0.017-0.68/h (~$12-500/mes)      |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **PostgreSQL** como base de datos relacional estándar para todos los servicios y microservicios corporativos que requieran almacenamiento transaccional.

### Justificación

- Open source, sin costos de licenciamiento y bajo TCO
- Soporte avanzado para transacciones ACID, integridad referencial y consultas complejas
- Ideal para cargas OLTP y escenarios multi-tenant/multi-país (schemas, RLS, particionamiento)
- Extensibilidad: JSONB, PostGIS, TimescaleDB, plugins
- Portabilidad total entre cloud y on-premises
- Comunidad global activa y abundante documentación
- Replicación, alta disponibilidad y escalabilidad horizontal
- Integración con herramientas de CI/CD, automatización y migraciones
- Cumplimiento de estándares de seguridad y normativas internacionales

### Alternativas descartadas

- **MySQL/MariaDB:** menor soporte para extensiones avanzadas, multi-tenant más limitado (no RLS nativo), JSONB menos optimizado
- **SQL Server:** costos de licenciamiento prohibitivos (US$14K+ Standard, US$55K+ Enterprise), lock-in Microsoft, menor flexibilidad multi-cloud
- **Oracle:** costos muy altos (US$47.5K/processor + soporte 22%), lock-in vendor, complejidad operativa excesiva, menor portabilidad
- **Aurora:** lock-in AWS, menor portabilidad multi-cloud, costos crecientes vs PostgreSQL self-hosted

---

## ⚠️ CONSECUENCIAS

### Positivas

- Transacciones ACID y consistencia fuerte para datos críticos
- Multi-tenancy avanzado con schemas, RLS y particionamiento
- Extensibilidad: JSONB, PostGIS, TimescaleDB, custom extensions
- Portabilidad total entre clouds y on-premises
- Replicación y alta disponibilidad nativas
- Comunidad activa y ecosistema maduro

### Negativas (Riesgos y Mitigaciones)

- **Complejidad tuning:** mitigada con automatización, monitoreo Prometheus y buenas prácticas documentadas
- **Escalabilidad horizontal:** limitada vs NoSQL - mitigada con particionamiento, Citus y sharding
- **Operación self-managed:** mitigada con automatización Terraform y managed services (RDS)

---

## 📚 REFERENCIAS

- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [AWS RDS PostgreSQL](https://aws.amazon.com/rds/postgresql/)
- [Comparativa DB Engines](https://db-engines.com/en/ranking)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
