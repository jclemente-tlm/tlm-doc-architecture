# Estándar Técnico — Bases de Datos y Consistencia

## 1. Propósito

Definir los estándares obligatorios para gestión de bases de datos, migraciones, ownership, patrones de consistencia, SLOs y resolución de conflictos en arquitecturas modernas (microservicios, multi-tenant, distribuidas).

## 2. Alcance

**Aplica a:**

- Microservicios y bounded contexts
- PostgreSQL 14+ y bases distribuidas
- Migraciones, replicación, cache distribuido
- Event-driven architectures

**No aplica a:**

- Aplicaciones monolíticas sin migraciones
- Sistemas single-instance sin replicación

## 3. Tecnologías Aprobadas

| Componente         | Tecnología    | Versión mínima | Observaciones               |
| ------------------ | ------------- | -------------- | --------------------------- |
| Relacional         | PostgreSQL    | 14+            | Default para datos críticos |
| Migrations         | EF Core       | 8.0+           | .NET native migrations      |
| Versionado scripts | Git           | -              | Scripts en src/Database     |
| Ownership catalog  | Backstage     | 1.20+          | Service catalog             |
| Monitoring         | Grafana Mimir | 2.10+          | Replication lag, SLOs       |

## 4. Requisitos Obligatorios 🔴

### Migraciones y Scripts

- Naming: Script{Version}\_\_{Description}.sql
- Scripts idempotentes y versionados
- Un cambio lógico = un script
- Transacciones explícitas
- Rollback scripts para cambios críticos
- Testing en dev/staging antes de prod
- Historial en tabla SchemaVersions

### Database per Service

- Una BD por servicio (schema separado mínimo)
- Credenciales exclusivas por servicio
- Network isolation y RBAC
- Owner gestiona schema y migrations
- Prohibido JOIN cross-service
- Consistencia eventual cross-service via eventos

### Ownership y Bounded Context

- Una entidad = un owner service
- Write access exclusivo del owner
- Read access via API del owner
- Ownership documentado (tabla, ADR)
- Bounded contexts claros y documentados

### Consistencia y Modelos

- Strong consistency para transacciones críticas
- Eventual consistency para cache, analytics
- Causal consistency para eventos ordenados
- Documentar modelo en ADR
- Configuración explícita de isolation level
- SLOs de staleness, replication lag, convergence

### SLOs y Monitoreo

- Replication lag <5s (warning 2.5s, crítico 5s)
- Staleness cache <2min
- Convergence time <30s
- Métricas: replication_lag_seconds, cache_staleness_seconds, event_propagation_duration
- Dashboards y alertas en Grafana

### Resolución de Conflictos

- Estrategia explícita por tipo de dato (LWW, CRDT, merge)
- Timestamps UTC y version numbers
- Detección y log de conflictos
- CRDTs para sets, contadores, textos colaborativos
- Custom merge function documentada

## 5. Prohibiciones ❌

- Scripts sin versionado secuencial
- Cambios manuales directos en producción
- JOIN entre schemas de servicios distintos
- Ownership ambiguo o compartido
- Acceso directo a BD de otro servicio
- Falta de rollback o testing en migraciones
- Falta de monitoreo de SLOs de consistencia

## 6. Configuración / Implementación

### Ejemplo: Script de migración

```sql
-- Script0001__CreateUsersTable.sql
BEGIN;
CREATE TABLE users (
  id uuid PRIMARY KEY,
  email text NOT NULL UNIQUE
);
COMMIT;
```

### Ejemplo: Database per Service

```yaml
services:
  user-db:
    image: postgres:14
    environment:
      POSTGRES_DB: userdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: secret
    networks:
      - user-net
  order-db:
    image: postgres:14
    environment:
      POSTGRES_DB: orderdb
      POSTGRES_USER: order
      POSTGRES_PASSWORD: secret
    networks:
      - order-net
```

### Ejemplo: Ownership catalog (Backstage)

```yaml
apiVersion: backstage.io/v1alpha1
kind: System
metadata:
  name: user-management
  owner: team-user
spec:
  domain: users
```

### Ejemplo: Consistency SLOs (PromQL)

```promql
max_over_time(replication_lag_seconds[5m]) > 5
```

### Ejemplo: Resolución de conflictos (LWW)

```sql
UPDATE items SET value = $newValue, updated_at = $now
WHERE id = $id AND updated_at < $now;
```

## 7. Validación

- Validar versionado y ejecución de migraciones
- Revisar ownership y documentación de bounded contexts
- Verificar configuración de isolation level y consistencia
- Monitorear métricas de SLOs y replication lag
- Auditar logs de conflictos y merges

## 8. Schema Evolution y Documentación

**Migrations:** EF Core Migrations con expand-contract pattern para zero-downtime deploys. Añadir columna nueva (expand), migrar datos, eliminar vieja (contract). Rollback plan obligatorio.

**Documentación:** SQL COMMENT ON para tablas/columnas. Diagramas ER en dbdiagram.io/PlantUML versionados en repo. SchemaSpy para HTML docs autogenerados.

---

## 9. Referencias

- [ADR-010 Standard Base de Datos](../../../decisiones-de-arquitectura/adr-010-standard-base-datos.md)
- [ADR-019 Configuración Scripts BD](../../../decisiones-de-arquitectura/adr-019-configuraciones-scripts-bd.md)
- [Entity Framework Migrations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/14/index.html)
- [Backstage Ownership](https://backstage.io/docs/features/software-catalog/descriptor-format/)
- [Prometheus Consistency SLOs](https://prometheus.io/docs/practices/instrumentation/)
- [CRDTs](https://crdt.tech/)
- [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem)
- [PACELC Theorem](https://en.wikipedia.org/wiki/PACELC_theorem)
