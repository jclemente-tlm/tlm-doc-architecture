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

| Criterio                | PostgreSQL                    | MySQL               | Microsoft SQL Server | Oracle                | AWS Aurora      |
| ----------------------- | ----------------------------- | ------------------- | -------------------- | --------------------- | --------------- |
| **Agnosticidad**        | ✅ OSS, multi-cloud           | ✅ OSS, multi-cloud | ❌ Lock-in Microsoft | ❌ Lock-in Oracle     | ❌ Lock-in AWS  |
| **Operación**           | ✅ Simple, automatizable      | ✅ Simple           | ⚠️ Compleja          | ⚠️ Compleja           | ✅ Gestionado   |
| **Seguridad**           | ✅ Avanzada, RLS, cifrado     | ⚠️ Básica           | ✅ Enterprise        | ✅ Enterprise         | ✅ Enterprise   |
| **Ecosistema .NET**     | ✅ Excelente (Npgsql)         | ✅ Muy bueno        | ✅ Nativo            | ✅ Bueno              | ✅ Compatible   |
| **Escalabilidad**       | ✅ Particionamiento, sharding | ⚠️ Limitada         | ⚠️ Always On         | ⚠️ RAC                | ✅ Automática   |
| **Extensibilidad**      | ✅ Plugins, JSONB, PostGIS    | ⚠️ Limitada         | ⚠️ Limitada          | ✅ Máxima             | ⚠️ Limitada     |
| **Costos**              | ✅ Gratuito                   | ✅ Gratuito         | ❌ Muy caro          | ❌ Muy caro           | ⚠️ Pago por uso |
| **Alta disponibilidad** | ✅ Replicación nativa         | ⚠️ Replicación      | ✅ Always On         | ✅ RAC                | ✅ Multi-AZ     |
| **Comunidad**           | ✅ Muy activa (15K⭐)         | ✅ Muy activa       | ✅ Soporte Microsoft | ✅ Soporte enterprise | ⚠️ Limitada AWS |
| **Portabilidad**        | ✅ Multi-plataforma           | ✅ Multi-plataforma | ❌ Windows principal | ❌ Limitada           | ❌ AWS          |

**Leyenda:** ✅ Cumple completamente | ⚠️ Cumple parcialmente | ❌ No cumple

---

## ✔️ DECISIÓN

Se selecciona **PostgreSQL** como base de datos relacional estándar para todos los servicios y microservicios corporativos que requieran almacenamiento transaccional.

## Justificación

- Open source, sin costos de licenciamiento y bajo TCO
- Soporte avanzado para transacciones ACID, integridad referencial y consultas complejas
- Ideal para cargas OLTP y escenarios multi-tenant/multi-país (schemas, RLS, particionamiento)
- Extensibilidad: JSONB, PostGIS, TimescaleDB, plugins
- Portabilidad total entre cloud y on-premises
- Comunidad global activa y abundante documentación
- Replicación, alta disponibilidad y escalabilidad horizontal
- Integración con herramientas de CI/CD, automatización y migraciones
- Cumplimiento de estándares de seguridad y normativas internacionales

## Alternativas descartadas

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
