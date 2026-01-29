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

### Comparativa Cualitativa

| Criterio              | PostgreSQL | MySQL | SQL Server | Oracle | Aurora |
|----------------------|------------|-------|------------|--------|--------|
| **Agnosticidad**     | ✅ OSS, multi-cloud | ✅ OSS, multi-cloud | ❌ Lock-in Microsoft | ❌ Lock-in Oracle | ❌ Lock-in AWS |
| **Operación**        | ✅ Simple, automatizable | ✅ Simple | 🟡 Compleja | 🟡 Compleja | ✅ Gestionado |
| **Seguridad**        | ✅ Avanzada, RLS, cifrado | 🟡 Básica | ✅ Enterprise | ✅ Enterprise | ✅ Enterprise |
| **Ecosistema .NET**  | ✅ Excelente (Npgsql) | ✅ Muy bueno | ✅ Nativo | ✅ Bueno | ✅ Compatible |
| **Escalabilidad**    | ✅ Particionamiento, sharding | 🟡 Limitada | 🟡 Always On | 🟡 RAC | ✅ Automática |
| **Extensibilidad**   | ✅ Plugins, JSONB, PostGIS | 🟡 Limitada | 🟡 Limitada | ✅ Máxima | 🟡 Limitada |
| **Costos**           | ✅ Gratuito | ✅ Gratuito | ❌ Muy caro | ❌ Muy caro | 🟡 Pago por uso |
| **Comunidad**        | ✅ Muy activa | ✅ Muy activa | ✅ Soporte Microsoft | ✅ Soporte enterprise | 🟡 Limitada AWS |
| **Portabilidad**     | ✅ Multi-plataforma | ✅ Multi-plataforma | ❌ Windows principal | ❌ Limitada | ❌ AWS |

### Matriz de Decisión

| Solución        | Agnosticidad | Operación | Seguridad | Ecosistema .NET | Recomendación         |
|-----------------|--------------|-----------|-----------|-----------------|-----------------------|
| **PostgreSQL**  | Excelente    | Excelente | Excelente | Excelente       | ✅ **Seleccionada**    |
| **MySQL**       | Excelente    | Excelente | Buena     | Muy buena       | 🟡 Considerada         |
| **SQL Server**  | Mala         | Buena     | Excelente | Nativo          | 🟡 Alternativa         |
| **Oracle**      | Mala         | Buena     | Excelente | Buena           | ❌ Descartada          |
| **Aurora**      | Mala         | Excelente | Excelente | Compatible      | ❌ Descartada          |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Metodología y supuestos:** Se asume un uso promedio de 5 bases de datos, 4 países, alta disponibilidad y replicación. El TCO (Total Cost of Ownership) se calcula para un horizonte de 3 años, incluyendo costos directos y estimaciones de operación. Los valores pueden variar según volumen y proveedor.

| Solución                | Licenciamiento     | Infraestructura | Operación         | TCO 3 años         |
|------------------------|-------------------|----------------|-------------------|--------------------|
| PostgreSQL             | OSS               | US$7,200/año   | US$18,000/año     | US$75,600          |
| MySQL/MariaDB          | OSS               | US$6,000/año   | US$15,000/año     | US$63,000          |
| SQL Server             | US$60,000/año     | US$7,200/año   | US$24,000/año     | US$273,600         |
| Oracle                 | US$120,000/año    | US$10,800/año  | US$36,000/año     | US$500,400         |
| Aurora PostgreSQL      | Pago por uso      | US$0           | US$0              | US$108,000         |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **PostgreSQL:** sin límite práctico, escalabilidad horizontal con Citus/sharding
- **MySQL/MariaDB:** sin límite práctico, escalabilidad limitada
- **SQL Server/Oracle:** límites por licencia y plataforma
- **Aurora:** límites AWS, escalabilidad automática

### Riesgos y mitigación

- **Lock-in propietario:** mitigado usando solo tecnologías OSS y modelos portables
- **Complejidad tuning:** mitigada con automatización y monitoreo
- **Costos variables cloud:** monitoreo y revisión anual

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

- **MySQL/MariaDB:** menor soporte para extensiones avanzadas y modelos multi-tenant complejos
- **SQL Server:** costos de licenciamiento, lock-in y menor flexibilidad multi-cloud
- **Oracle:** costos muy altos, lock-in, complejidad operativa y menor portabilidad
- **Aurora:** lock-in AWS, menor portabilidad

---

## ⚠️ CONSECUENCIAS

- Todos los servicios nuevos deben usar PostgreSQL salvo justificación técnica documentada
- Se debe estandarizar la gestión de migraciones, backups y automatización

---

## 📚 REFERENCIAS

- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [AWS RDS PostgreSQL](https://aws.amazon.com/rds/postgresql/)
- [Comparativa DB Engines](https://db-engines.com/en/ranking)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
