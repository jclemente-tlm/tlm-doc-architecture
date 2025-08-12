# 10. Requisitos De Calidad

Este capítulo define los atributos de calidad del Sistema de Notificaciones, estableciendo métricas cuantificables, criterios de aceptación y escenarios de validación alineados a estándares internacionales y regulaciones aplicables.

## 10.1 Rendimiento y Eficiencia

| Métrica                | Objetivo             | Medición         |
|------------------------|---------------------|------------------|
| `Latencia de envío`    | `< 500ms p95`       | `Prometheus`     |
| `Throughput`           | `1,000 notificaciones/min` | Pruebas de carga |
| `Disponibilidad`       | `99.9%`             | Health checks    |
| `Procesamiento en cola`| `< 30s`             | Monitoreo        |

### Objetivos de Latencia y Rendimiento

| Operación                | P50    | P95    | P99    | SLA Crítico   |
|--------------------------|--------|--------|--------|---------------|
| `Solicitud API (sync)`   | `100ms`| `200ms`| `500ms`| `< 1s`        |
| `Renderizado plantilla`  | `20ms` | `50ms` | `100ms`| `< 200ms`     |
| `Llamada API proveedor`  | `200ms`| `800ms`| `2s`   | `< 5s`        |
| `Entrega Email`          | `30s`  | `2min` | `5min` | `< 10min`     |
| `Entrega SMS`            | `5s`   | `30s`  | `1min` | `< 2min`      |
| `Notificación Push`      | `1s`   | `5s`   | `10s`  | `< 30s`       |
| `Entrega WhatsApp`       | `10s`  | `1min` | `3min` | `< 5min`      |

### Capacidad y Pruebas de Estrés

- Carga normal: `1,000 req/min` API, `5,000` emails/hora, `2,000` SMS/hora, `10,000` push/hora, `1,000` WhatsApp/hora
- Carga pico: `5,000 req/min` API, `50,000` emails/hora, `20,000` SMS/hora, `100,000` push/hora, `10,000` WhatsApp/hora
- Objetivo de estrés: `10x` carga normal, ráfaga `30 min` sostenidos, sin pérdida de mensajes

### Autoescalado y Utilización de Recursos

- Umbral CPU: `70%`
- Umbral profundidad de cola: `1,000 mensajes`
- Instancias mínimas: `2`, máximas: `50`
- Escalado por canal y tipo de notificación

## 10.2 Disponibilidad Y Confiabilidad

- SLA global: `99.9%` (`43.2 min/mes`)
- SLA por canal: `Email 99.95%`, `SMS 99.9%`, `Push 99.8%`, `WhatsApp 99.5%`
- Delivery SLA: `Email 95% < 10min`, `SMS 98% < 2min`, `Push 99% < 30s`, `WhatsApp 90% < 5min`
- Errores: `API 4xx < 2%`, `API 5xx < 0.5%`, `proveedor < 1%`, `plantillas < 0.1%`
- Despliegue multi-AZ, balanceo con `ALB`, réplicas de base de datos
- Recuperación ante desastres: `RTO 30 min`, `RPO 5 min`, backups `WAL`/snapshots, failover automático

## 10.3 Seguridad Y Compliance

- Autenticación y autorización: `Keycloak`, `OAuth2`, `JWT`, `scopes`, `RBAC` por rol y tenant
- Protección de datos: `TLS 1.3`, `AES-256`, cifrado en reposo y en tránsito, hash/cifrado de `PII`
- Cumplimiento: `GDPR`, `CAN-SPAM`, `TCPA`, leyes locales (`Perú`, `Ecuador`, `Colombia`, `México`)
- Retención y purga automática de datos sensibles

## 10.4 Usabilidad Y Experiencia

- API `RESTful`, `OpenAPI 3.0`, errores uniformes, paginación, documentación interactiva
- `Rate limiting`, mensajes claros, versionado
- Editor de plantillas `WYSIWYG`, preview, validación, versionado, accesibilidad, biblioteca, `A/B testing`

## 10.5 Mantenibilidad Y Observabilidad

- Logging estructurado: `Serilog`, formato `JSON`, exportado a `Loki`, retención `90d/2a`
- Métricas: `Prometheus` (envíos, éxito, uso plantillas, costos, satisfacción, latencia, errores, colas, recursos, DB)
- Trazas: `OpenTelemetry`, visualización en `Jaeger`
- `SLO`/`SLI`: disponibilidad, error rate, percentiles
- Alertas críticas: error `>5%`, caídas, colas detenidas, fallos proveedor

## 10.6 Testabilidad Y Gates De Calidad

- Pirámide de pruebas: unitarias (`>90%` cobertura), integración (`DB`, `APIs`), E2E (flujos completos)
- Herramientas: `xUnit`, `Moq`, `TestContainers`, `NBomber`, `Pact`, `Playwright`
- Quality Gates: `SonarQube`, cobertura, seguridad, performance, startup

## 10.7 Escalabilidad E Interoperabilidad

- API `stateless`, autoescalado horizontal, hasta `50` instancias por región
- Procesadores escalables por canal, work-stealing
- Base de datos: réplicas, pooling, particionado
- Integración: `REST` (OpenAPI, JSON), `Webhook` (HMAC, retries, DLQ), `GraphQL` (queries, subscripciones)
- Mensajería y colas: `Redis` y `PostgreSQL`, sin dependencias de `Kafka`, `SQS`, `RabbitMQ` ni `Azure SB`

## 10.8 Escenarios De Calidad

- Disponibilidad: failover automático, recuperación < 30s
- Performance: autoescalado ante picos, procesamiento < 10min
- Seguridad: bloqueo y alerta ante acceso no autorizado, 0% accesos exitosos
- Multi-tenancy: aislamiento total, 100% aislamiento de datos

## 10.9 Matriz De Calidad

| Atributo      | Criticidad | Escenario Principal         | Métrica Objetivo                |
|--------------|------------|----------------------------|---------------------------------|
| Disponibilidad| Alta       | Failover automático        | 99.9% uptime                    |
| Performance   | Alta       | Procesamiento de picos     | < 200ms API, 10K/min procesamiento |
| Seguridad     | Crítica    | Protección datos PII       | 0 brechas, Compliance GDPR      |
| Fiabilidad    | Alta       | Entrega garantizada        | 99.99% delivery rate            |
| Mantenibilidad| Media      | Despliegues sin downtime   | < 5 min deployment              |
| Escalabilidad | Alta       | Auto-scaling               | Escalado lineal hasta 100K/min  |

---

**Notas:**

- Se priorizan la resiliencia, la observabilidad, la entrega única y el cumplimiento en todos los escenarios.
- Las métricas y umbrales se monitorean y ajustan de forma continua según la demanda y la evolución del sistema.
