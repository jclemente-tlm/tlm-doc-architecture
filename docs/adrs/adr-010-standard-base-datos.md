---
id: adr-010-estandar-base-datos
title: "Estándar para Bases de Datos"
sidebar_position: 10
---

## ✅ ESTADO

Aceptada – Agosto 2025

---

## 🗺️ CONTEXTO

Los servicios corporativos requieren una base de datos relacional que soporte:

- **Multi-tenancy robusto** con aislamiento por país/cliente (schemas, RLS)
- **Transacciones ACID** para integridad de datos críticos
- **Escalabilidad horizontal** con particionamiento y sharding
- **Alta disponibilidad** con replicación master-slave/streaming
- **Datos semiestructurados** (JSON/JSONB) para flexibilidad
- **Extensibilidad** con plugins y extensiones especializadas
- **Observabilidad** con métricas y logging detallado
- **Cumplimiento regulatorio** con auditoría y cifrado

La intención estratégica es **maximizar agnosticidad** mientras se garantiza robustez empresarial.

Las alternativas evaluadas fueron:

- **PostgreSQL** (Open source, extensible, multi-tenant avanzado)
- **MySQL/MariaDB** (Open source, popular, funcionalidad básica)
- **SQL Server** (Microsoft, propietario, integración .NET)
- **Oracle Database** (Propietario, enterprise, alto costo)
- **Amazon Aurora** (Gestionado AWS, compatible MySQL/PostgreSQL)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio | PostgreSQL | MySQL | SQL Server | Oracle | Aurora |
|----------|------------|-------|------------|--------|--------|
| **Madurez** | ✅ Muy maduro, 25+ años | ✅ Muy maduro, estable | ✅ Maduro, enterprise | ✅ Muy maduro, líder | 🟡 Reciente, gestionado |
| **Ecosistema .NET** | ✅ Excelente con Npgsql | ✅ Muy bueno | ✅ Nativo Microsoft | ✅ Bueno | ✅ Compatible (PostgreSQL/MySQL) |
| **Costos** | ✅ Completamente gratuito | ✅ Gratuito (Community) | ❌ Licencias muy caras | ❌ Licencias muy caras | 🟡 Pago por uso |
| **Rendimiento** | ✅ Excelente OLTP/OLAP | ✅ Muy bueno OLTP | ✅ Excelente enterprise | ✅ Máximo rendimiento | ✅ Muy bueno, gestionado |
| **Características** | ✅ Muy avanzado (JSON, etc) | 🟡 Básico pero sólido | ✅ Muy completo | ✅ Máximas características | 🟡 Compatible, gestionado |
| **Comunidad** | ✅ Muy activa, OSS | ✅ Muy activa | ✅ Soporte Microsoft | ✅ Soporte enterprise | 🟡 Limitada a AWS |
| **Portabilidad** | ✅ Multi-plataforma | ✅ Multi-plataforma | ❌ Principalmente Windows | ❌ Limitada | ❌ Lock-in AWS |

### Matriz de Decisión

| Base de Datos | Madurez | Ecosistema .NET | Costos | Características | Recomendación |
|---------------|---------|-----------------|--------|-----------------|---------------|
| **PostgreSQL** | Excelente | Excelente | Gratuito | Muy avanzado | ✅ **Seleccionada** |
| **SQL Server** | Excelente | Nativo | Muy caro | Muy completo | 🟡 Alternativa |
| **MySQL** | Excelente | Muy bueno | Gratuito | Básico | 🟡 Considerada |
| **Oracle** | Excelente | Bueno | Muy caro | Máximo | ❌ Descartada |
| **Aurora** | Buena | Compatible | Pago por uso | Compatible | ❌ Descartada |

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

### Escenario Base: 5 bases de datos, 4 países, HA + replicación

| Solución | Licenciamiento | Infraestructura | Operación | TCO 3 años |
|----------|----------------|-----------------|-----------|------------|
| **PostgreSQL** | US$0 (OSS) | US$7,200/año | US$18,000/año | **US$75,600** |
| **MySQL/MariaDB** | US$0 (OSS) | US$6,000/año | US$15,000/año | **US$63,000** |
| **SQL Server** | US$60,000/año | US$7,200/año | US$24,000/año | **US$273,600** |
| **Oracle** | US$120,000/año | US$10,800/año | US$36,000/año | **US$500,400** |
| **Aurora PostgreSQL** | Pago por uso | US$0 | US$0 | **US$108,000** |

### Escenario Alto Volumen: 20 bases de datos, multi-región

| Solución | TCO 3 años | Escalabilidad |
|----------|------------|---------------|
| **PostgreSQL** | **US$240,000** | Manual con Citus/sharding |
| **MySQL/MariaDB** | **US$180,000** | Manual, limitada |
| **SQL Server** | **US$900,000** | Manual con Always On |
| **Oracle** | **US$1,800,000** | Manual con RAC |
| **Aurora PostgreSQL** | **US$432,000** | Automática, gestionada |

### Factores de Costo Adicionales

```yaml
Consideraciones PostgreSQL:
  Extensiones: PostGIS, TimescaleDB gratuitas
  Backup/DR: pgBackRest, Barman (OSS) vs US$12K/año comercial
  Monitoreo: pgAdmin, Grafana (OSS) vs US$6K/año comercial
  Soporte: Comunidad gratis vs US$15K/año enterprise
  Migración: US$0 entre PostgreSQL vs US$50K desde propietario
  Capacitación: US$3K vs US$15K para Oracle/SQL Server
```

### Análisis de portabilidad y lock-in

- PostgreSQL y MySQL/MariaDB son open source, ampliamente soportados y portables entre proveedores cloud y on-premises, minimizando lock-in.
- SQL Server y Oracle implican dependencia de proveedor, mayores costos y menor portabilidad.

---

## ✔️ DECISIÓN

Se adopta PostgreSQL como base de datos relacional estándar para todos los servicios y microservicios corporativos que requieran almacenamiento transaccional.

## Justificación

- Open source, sin costos de licenciamiento y bajo costo total de propiedad.
- Soporte avanzado para transacciones ACID, integridad referencial y consultas complejas.
- Ideal para cargas OLTP (alta concurrencia, consistencia, operaciones CRUD).
- Soporte avanzado para JSON, índices, particionamiento y extensiones.
- Disponible en todos los principales proveedores cloud y on-premises.
- Comunidad global activa y abundante documentación.
- Replicación, alta disponibilidad y escalabilidad horizontal.
- Integración con herramientas de CI/CD, automatización y migraciones.
- Permite escenarios multi-tenant y multi-país mediante:
  - Esquemas por tenant (aislamiento lógico).
  - Row-Level Security (RLS) para control de acceso por tenant.
  - Particionamiento de tablas por tenant o país.
  - Flexibilidad para elegir el modelo multi-tenant según el caso de uso.
- Cumplimiento de estándares de seguridad y normativas internacionales.

## Limitaciones

- No es óptimo para almacenamiento de grandes volúmenes de archivos binarios (usar almacenamiento dedicado).
- No es la mejor opción para cargas analíticas masivas (OLAP puro) o procesamiento de eventos en tiempo real.
- Requiere tuning y monitoreo para escalar a cargas muy altas o multi-región.

## Alternativas descartadas

- MySQL/MariaDB: Menor soporte para extensiones avanzadas, modelos multi-tenant complejos y JSON.
- SQL Server: Costos de licenciamiento, lock-in y menor flexibilidad multi-cloud.
- Oracle: Costos muy altos, lock-in, complejidad operativa y menor portabilidad.

---

## ⚠️ CONSECUENCIAS

- Todos los servicios nuevos deben usar PostgreSQL salvo justificación técnica documentada.
- Se debe estandarizar la gestión de migraciones, backups y automatización.

---

## 📚 REFERENCIAS

- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [AWS RDS PostgreSQL](https://aws.amazon.com/rds/postgresql/)
- [Comparativa DB Engines](https://db-engines.com/en/ranking)
- [Arc42: Decisiones de arquitectura](https://arc42.org/decision/)
