# 4. Estrategia de solución

## 4.1 Decisiones clave

| Decisión | Alternativa elegida | Justificación |
|----------|-------------------|---------------|
| **Arquitectura** | `API` + `Processor` | Separación responsabilidades |
| **Cola** | `Redis` | Rendimiento |
| **Plantillas** | `RazorEngine` | Flexibilidad |
| **Multi-canal** | Handlers especializados | Extensibilidad |

## 4.2 Patrones aplicados

| Patrón | Propósito | Implementación |
|---------|------------|----------------|
| **CQRS** | Separación comando/consulta | `API`/`Processor` |
| **Template Method** | Procesamiento plantillas | `RazorEngine` |
| **Strategy** | Múltiples canales | Handler pattern |
| **Repository** | Acceso a datos | `Entity Framework` |

## 4.3 Multi-canal

| Canal | Tecnología | Propósito |
|-------|-------------|----------|
| **Email** | `SMTP`/`SendGrid` | Notificaciones principales |
| **SMS** | `Twilio`/`AWS SNS` | Alertas urgentes |
| **Push** | `Firebase`/`APNS` | Móvil |
| **Webhook** | `HTTP POST` | Integraciones |
