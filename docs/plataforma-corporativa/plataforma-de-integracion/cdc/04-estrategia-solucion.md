---
sidebar_position: 4
title: Estrategia de Solución
description: Decisiones tecnológicas y de diseño clave del servicio CDC con Debezium.
---

# 4. Estrategia de Solución

## Decisiones Tecnológicas

| Dimensión              | Decisión                                       | Justificación                                                                          |
| ---------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------- |
| Motor CDC              | **Debezium** (Kafka Connect)                   | Log-based, agnosticidad tecnológica, integración nativa con Kafka (ADR-009)            |
| Despliegue             | **AWS EC2 (contenedor Docker)**                | Consistente con el modelo Docker-en-EC2 del clúster Kafka; mismo modelo operacional    |
| Formato de mensaje     | **JSON**                                       | Interoperabilidad sin dependencia de Schema Registry; legible por cualquier consumidor |
| Naming de topics       | **`<base-de-datos>.<schema>.<tabla>`**         | Convención por defecto de Debezium; trazabilidad inmediata al origen del dato          |
| Almacenamiento offsets | **Kafka** (`connect-offsets`)                  | Reutiliza infraestructura existente; no requiere almacenamiento externo adicional      |
| Configuración          | **Kafka Connect REST API vía IaC** (Terraform) | Trazabilidad GitOps; sin cambios manuales en producción                                |
| Transformaciones       | **SMT** (Single Message Transforms)            | Filtrado, enmascaramiento y enriquecimiento de mensajes sin código adicional           |
| Observabilidad         | **JMX Exporter → Prometheus → Mimir/Grafana**  | Stack corporativo de observabilidad                                                    |

## Modelo de Mensajes CDC (Formato JSON)

Cada evento publicado por Debezium sigue la estructura estándar:

```json
{
  "before": { "id": 1, "nombre": "Ejemplo", "estado": "ACTIVO" },
  "after": { "id": 1, "nombre": "Ejemplo", "estado": "INACTIVO" },
  "op": "u",
  "ts_ms": 1710000000000,
  "source": {
    "db": "base-ops",
    "schema": "public",
    "table": "operaciones",
    "connector": "postgresql"
  }
}
```

| Campo    | Descripción                                                                      |
| -------- | -------------------------------------------------------------------------------- |
| `before` | Estado de la fila antes del cambio (`null` en INSERT)                            |
| `after`  | Estado de la fila después del cambio (`null` en DELETE)                          |
| `op`     | Tipo de operación: `c` (create), `u` (update), `d` (delete), `r` (read/snapshot) |
| `ts_ms`  | Timestamp del cambio en la base de datos (en milisegundos)                       |
| `source` | Metadata de origen: base de datos, schema, tabla, conector                       |

## Convención de Naming de Topics CDC

```
<base-de-datos>.<schema>.<tabla>

Ejemplos:
  base-ops.public.operaciones
  base-ops.public.clientes
  base-erp.dbo.facturas
  base-legacy.inventario.productos
```

Esta convención es la configuración por defecto de Debezium (`topic.prefix` = nombre de la BD). Permite filtrar eventos por origen mediante prefijos en las ACLs de Kafka.
