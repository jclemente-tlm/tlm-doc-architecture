# 6. Vista de tiempo de ejecución

## 6.1 Escenarios principales

| Escenario               | Flujo                              | Componentes         |
|-------------------------|------------------------------------|---------------------|
| `Envío inmediato`         | `Notification API` → `Colas de Canal` → `Procesadores de Canal` → `Proveedor Externo` → `Notification Database` | `Notification API`, `emailQueue`, `smsQueue`, `whatsappQueue`, `pushQueue`, `emailProcessor`, `smsProcessor`, `whatsappProcessor`, `pushProcessor`, `Notification Database`, `Attachment Storage` |
| `Envío programado`        | `Notification Scheduler` → `Colas de Canal` → `Procesadores de Canal` → `Proveedor Externo` → `Notification Database` | `Notification API`, `Notification Scheduler`, `emailQueue`, `smsQueue`, `whatsappQueue`, `pushQueue`, `emailProcessor`, `smsProcessor`, `whatsappProcessor`, `pushProcessor`, `Notification Database` |

## 6.2 Patrones de interacción

| Patrón      | Descripción                   | Tecnología / Componente         |
|-------------|------------------------------|---------------------------------|
| `CQRS`      | Separación comando/consulta  | `Notification API`, `emailProcessor`, `smsProcessor`, `whatsappProcessor`, `pushProcessor` |
| `Queue`     | Cola de mensajes             | `emailQueue`, `smsQueue`, `whatsappQueue`, `pushQueue` |
| `Template`  | Procesamiento de plantillas  | `Template Engine`               |

Esta sección describe los principales escenarios de ejecución del sistema, mostrando cómo los componentes interactúan durante el tiempo de ejecución para cumplir con los casos de uso más relevantes arquitectónicamente. Se priorizan la resiliencia, el desacoplamiento, la deduplicación, la idempotencia y la observabilidad en todos los flujos.

## 6.3 Escenario: envío transaccional individual

### Participantes

- `Cliente`
- `Notification API`
- `Notification Database`
- Colas de Canal (`emailQueue`, `smsQueue`, `whatsappQueue`, `pushQueue`)
- Procesadores de Canal (`emailProcessor`, `smsProcessor`, `whatsappProcessor`, `pushProcessor`)
- Proveedor Externo

### Flujo principal

```mermaid
sequenceDiagram
    participant Cliente as Cliente
    participant API as Notification API
    participant DB as Notification Database
    participant ColasCanal as Colas de Canal
    participant ProcCanal as Procesadores de Canal
    participant Proveedor as Proveedor Externo

    Cliente->>API: 1. Solicita envío de notificación
    API->>API: 2.1. Valida datos de la solicitud
    API->>API: 2.2. Autentica y autoriza al cliente
    API->>API: 2.3. Valida reglas de negocio
    API->>API: 2.4. Construye mensaje de notificación
    API->>DB: 3. Persiste notificación
    API->>ColasCanal: 4. Publica mensaje en colas por canal
    API->>API: 5. Registra logs y métricas
    API->>Cliente: 6. Confirma recepción (`HTTP 202`)

    ColasCanal->>ProcCanal: 7. Procesadores de canal consumen mensaje
    ProcCanal->>API: 8. Obtienen adjuntos si aplica
    ProcCanal->>Proveedor: 9. Envía notificación al proveedor externo
    ProcCanal->>DB: 10. Actualiza estado final
```

### Aspectos notables

- El flujo implementa desacoplamiento total entre recepción, procesamiento y entrega mediante colas y procesadores independientes.
- La deduplicación e idempotencia se garantizan en la `Notification API` y en los procesadores de canal.
- La observabilidad se implementa con logs estructurados (`Serilog`), métricas (`Prometheus`) y trazas distribuidas (`OpenTelemetry`).
- La resiliencia se logra mediante reintentos automáticos, `DLQ` y fallback de proveedores.
- Todos los nombres y responsabilidades de los componentes coinciden con el DSL.

## 6.4 Métricas de ejecución

| Métrica                   | Target                | Medición                |
|---------------------------|----------------------|-------------------------|
| `API Response Time`       | `p95 < 100ms`        | Monitoreo APM           |
| `Event Processing`        | `< 500ms`            | Métricas personalizadas |
| `End-to-End Delivery`     | `< 30s` (transactional) | Métricas de negocio |
| `Capacidad de procesamiento` | `10K req/min/instancia` | Pruebas de carga   |

---

**Notas:**

- El sistema está diseñado para soportar picos de tráfico, garantizar entrega única y trazabilidad completa.
- El desacoplamiento y la resiliencia permiten tolerancia a fallos y recuperación automática ante errores de proveedores.
- La arquitectura prioriza la observabilidad y la entrega única en todos los escenarios.
