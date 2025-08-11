# 8. Conceptos Transversales

## 8.1 Seguridad

| Aspecto         | Implementación         | Tecnología         |
|-----------------|-----------------------|--------------------|
| Autenticación   | JWT (`Keycloak`)      | OAuth2, .NET 8     |
| Autorización    | Claims y roles        | .NET 8             |
| Cifrado         | TLS 1.3, AES-256      | HTTPS              |
| Datos sensibles | Tokenización, cifrado | AES-256            |

## 8.2 Observabilidad

| Tipo        | Herramienta     | Propósito         |
|-------------|-----------------|-------------------|
| Logs        | `Serilog`       | Registro eventos  |
| Métricas    | `Prometheus`    | Monitoreo         |
| Trazas      | `OpenTelemetry`, `Jaeger` | Trazabilidad |
| Health      | Health Checks   | Estado servicios  |

## 8.3 Multi-tenancy

| Aspecto         | Implementación         | Propósito              |
|-----------------|-----------------------|------------------------|
| Aislamiento     | Por tenant (realm)    | Separación de datos    |
| Deduplicación   | Por tenant (realm)    | Prevención duplicados  |
| Rate limiting   | Por organización      | Protección recursos    |

## 8.4 Modelo de Dominio

- `Event Sourcing` como principio arquitectónico: todos los cambios de estado se capturan como eventos inmutables en el `Event Store`.
- `CQRS` aplicado: separación de comandos y consultas en la capa de aplicación.
- Proyecciones especializadas para consultas y dashboards.

## 8.5 Seguridad

- Autenticación y autorización con `Keycloak` (JWT), validación de claims y roles.
- Aislamiento de datos por tenant (realm) usando esquemas separados y filtros automáticos.
- Cifrado en tránsito (`TLS 1.3`) y en reposo (`AES-256`).
- Cumplimiento normativo: GDPR, SOX, auditoría completa.

## 8.6 Comunicación e Integración

- Comunicación basada en eventos (`Event Bus`) para integración con sistemas externos (`SITA Messaging`).
- Publicación y consumo de eventos con garantía transaccional.
- Integración API REST con validación y control de errores.

## 8.7 Persistencia

- `Tracking Database` en `PostgreSQL` como almacén de eventos y proyecciones.
- Esquema por tenant (realm) para aislamiento.
- Proyecciones para consultas optimizadas.

## 8.8 Observabilidad

- Logs estructurados con `Serilog`.
- Métricas expuestas vía `Prometheus`.
- Trazas distribuidas con `OpenTelemetry` y visualización en `Jaeger`.
- Health checks y endpoints de monitoreo.

## 8.9 Testing

- Pruebas unitarias y de integración sobre lógica de dominio y eventos.
- Validación de contratos de eventos y proyecciones.
