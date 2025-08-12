# 4. Estrategia De Solución

## 4.1 Decisiones Clave

| Decisión         | Alternativa Elegida                | Justificación                                                                 |
|------------------|------------------------------------|-------------------------------------------------------------------------------|
| Arquitectura     | `API REST` + procesadores asíncronos | Separación de responsabilidades, escalabilidad y desacoplamiento por colas    |
| Cola             | `Amazon SQS`/`Redis`               | Alta disponibilidad, integración nativa, soporte para `DLQ` y reintentos      |
| Persistencia     | `PostgreSQL`                       | Robustez, soporte multi-tenant, particionamiento y auditoría                  |
| Plantillas       | `Liquid Templates`                  | Flexibilidad, soporte `i18n`, versionado, fallback y fácil integración        |
| Multi-canal      | Adaptadores por canal               | Extensibilidad y desacoplamiento de proveedores externos                      |
| Observabilidad   | `Serilog` + `Prometheus`            | Logging estructurado y métricas centralizadas                                 |
| Seguridad        | `OAuth2`/`JWT` + `RBAC`             | Autenticación robusta y control de acceso granular                            |
| Idempotencia     | `Idempotency-Key` y deduplicación   | Garantía de entrega única y supresión de duplicados en reintentos             |
| Deduplicación    | Hash de payload y control de concurrencia | Evitar envíos repetidos por errores o reintentos                        |
| Versionado de plantillas | Versionado y fallback automático | Soportar cambios sin afectar envíos activos                             |

> Todas las decisiones priorizan resiliencia, trazabilidad, entrega única y facilidad de evolución, alineadas con los objetivos de calidad y restricciones técnicas del sistema.

## 4.2 Patrones Aplicados

| Patrón             | Propósito                                 | Implementación / Componente Principal           |
|--------------------|-------------------------------------------|------------------------------------------------|
| `Outbox`           | Garantía de entrega y consistencia        | Publicación a `SQS`/`Redis` desde `PostgreSQL`  |
| `Adapter`          | Integración multi-canal y desacoplada     | Adaptadores para `Email`, `SMS`, `WhatsApp`, `Push` en `Processors` |
| `Repository`       | Acceso desacoplado a datos                | `Entity Framework Core` en `Notification API` y `Processors` |
| `Validation`       | Validación robusta de requests            | `FluentValidation` en `Notification API`        |
| `Mapping`          | Transformación eficiente de modelos       | `Mapster` en `Notification API` y `Processors`  |
| `Observability`    | Monitoreo y trazabilidad                  | `Serilog`, `Prometheus`, `OpenTelemetry`        |
| `Idempotencia`     | Entrega única ante reintentos             | `Idempotency-Key`, control de duplicados en `Notification API` |
| `Deduplicación`    | Supresión de mensajes repetidos           | Hash de payload, control de concurrencia en colas y procesadores |
| `Versionado de plantillas` | Gestión de cambios y fallback        | Versionado, fallback automático en `Template Controller` |

> El uso de patrones reconocidos permite mantenibilidad, pruebas y evolución incremental, garantizando entrega única, resiliencia y desacoplamiento de proveedores.

## 4.3 Multi-canal

| Canal        | Tecnología/Proveedor              | Propósito                        |
|--------------|----------------------------------|-----------------------------------|
| `Email`      | `Amazon SES`, `SMTP`             | Notificaciones principales        |
| `SMS`        | `AWS SNS`, proveedor local       | Alertas urgentes                  |
| `WhatsApp`   | Proveedor `WhatsApp API`         | Mensajería instantánea            |
| `Push`       | Proveedor `Push API`             | Notificaciones móviles            |

> La arquitectura multi-canal desacopla la lógica de negocio de los proveedores, permitiendo cambios o ampliaciones sin impacto en el core del sistema. El uso de colas, adaptadores, deduplicación e idempotencia garantiza resiliencia, escalabilidad y entrega única.

---

**Notas:**

- El desacoplamiento de proveedores y canales permite tolerancia a fallos, escalabilidad y evolución independiente de cada integración.
- Se prioriza la observabilidad, la trazabilidad y la entrega única en todos los flujos.
