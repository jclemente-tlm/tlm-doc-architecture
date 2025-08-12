# 9. Decisiones De Arquitectura

## 9.1 Decisiones Principales

| ADR        | Decisión                        | Estado    | Justificación                |
|------------|----------------------------------|-----------|------------------------------|
| `ADR-001`  | `CQRS API`                      | Aprobado  | Separación de responsabilidades |
| `ADR-002`  | `Redis` como cola               | Aprobado  | Rendimiento y simplicidad    |
| `ADR-003`  | `RazorEngine` y `Liquid` plantillas | Aprobado  | Flexibilidad y seguridad     |
| `ADR-004`  | Multi-canal handlers            | Aprobado  | Extensibilidad y modularidad |
| `ADR-005`  | Mensajería basada en base de datos | Aprobado | Portabilidad y cloud agnostic|

## 9.2 Alternativas Evaluadas

| Componente   | Alternativas                | Selección | Razón         |
|--------------|-----------------------------|-----------|---------------|
| Cola         | `RabbitMQ`, `Redis`, `SQS`  | `Redis`   | Simplicidad   |
| Plantillas   | `Liquid`, `Handlebars`, `Razor` | `RazorEngine` y `Liquid` | `.NET` nativo y seguridad |
| Storage      | `S3`, `EFS`, `Database`     | `EFS`     | Compartido    |
| Canales      | Monolítico, Handlers        | Handlers  | Modularidad   |

Las decisiones arquitectónicas del sistema de notificaciones siguen los principios de:

- Portabilidad entre nubes (`cloud agnostic`)
- Contenedores primero
- Mensajería centrada en base de datos y `Redis`
- Multi-tenant nativo
- Comunicación asíncrona basada en eventos de dominio
- Abstracción completa de proveedores
- Desacoplamiento, resiliencia, deduplicación, idempotencia y observabilidad en todos los flujos críticos

## Resumen De Decisiones Arquitectónicas

| #      | Decisión                        | Estado     | Impacto | Fecha       |
|--------|----------------------------------|------------|---------|-------------|
| `ADR-001`| Estrategia Multi-Proveedor     | Aprobado   | Alto    | 2024-01-15  |
| `ADR-002`| Mensajería Basada en Base de Datos | Aprobado | Alto    | 2024-01-25  |
| `ADR-003`| Motor de Plantillas `Liquid` y `RazorEngine` | Aprobado | Medio | 2024-02-05  |
| `ADR-004`| Arquitectura Dirigida por Eventos | Aprobado | Alto    | 2024-02-10  |
| `ADR-005`| Librería NuGet Multi-nube      | Aprobado   | Alto    | 2024-02-15  |

---

## `ADR-001`: Estrategia Multi-Proveedor

- Alta disponibilidad y failover automático por canal (`SendGrid`, `Twilio`, `FCM`, `WhatsApp Business API`, `SES`, `Mailgun`, `360dialog`).
- Abstracción de proveedores y selección dinámica según salud, costo y cobertura.
- Reducción de `SPOF` y optimización de costos.

## `ADR-002`: Mensajería Basada En Base De Datos Y Redis

- Uso de colas en `PostgreSQL` y `Redis` para mensajería y procesamiento asíncrono.
- Portabilidad total entre nubes, sin vendor lock-in.
- ACID y durabilidad garantizada.
- Estrategia de migración futura a colas dedicadas si es necesario.

### Ejemplo de definición de colas

```yaml
NotificationQueues:
  email-notifications:
    type: redis
    retention: 7d
  sms-notifications:
    type: redis
    retention: 7d
  push-notifications:
    type: redis
    retention: 7d
```

## `ADR-003`: Motor De Plantillas Liquid Y RazorEngine

- Plantillas seguras, internacionalizadas y editables por negocio.
- Ejecución en sandbox, filtros personalizados y soporte multi-idioma.
- Separación lógica/presentación y versionado de plantillas.

### Ejemplo de filtro personalizado

```csharp
public class CustomLiquidFilters
{
    public static string Translate(string key, object parameters = null)
    {
        // ...lógica de traducción...
    }
}
Template.RegisterFilter("t", CustomLiquidFilters.Translate);
```

## `ADR-004`: Arquitectura Dirigida Por Eventos

- Eventos de dominio para comunicación asíncrona y desacoplada.
- Registro y auditoría de eventos críticos (`NotificationRequested`, `NotificationSent`, `NotificationDelivered`, `NotificationFailed`).
- Facilidad para agregar nuevos consumidores y handlers.

### Ejemplo de evento de dominio

```csharp
public class NotificationRequested : NotificationDomainEvent
{
    public string NotificationId { get; set; }
    public DateTime? ScheduledAt { get; set; }
}
```

## `ADR-005`: Librería NuGet Multi-nube

- Abstracción de servicios cloud para facilitar despliegue en `AWS`, `Azure` y `GCP`.
- Configuración centralizada y desacoplada.

---

**Notas:**

- Se priorizan la resiliencia, el desacoplamiento, la deduplicación, la idempotencia y la observabilidad en todos los flujos críticos.
- La documentación de ADRs se mantiene actualizada y enlazada a los diagramas y bloques principales.
