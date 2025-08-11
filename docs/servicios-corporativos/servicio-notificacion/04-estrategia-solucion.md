# 4. Estrategia De Solución

## 4.1 Decisiones Clave

| Decisión         | Alternativa Elegida         | Justificación                  |
|------------------|----------------------------|-------------------------------|
| Arquitectura     | `API` + `Processor`        | Separación de responsabilidades|
| Cola             | `Redis`                    | Rendimiento                   |
| Plantillas       | `RazorEngine`              | Flexibilidad                  |
| Multi-canal      | Handlers especializados    | Extensibilidad                |

## 4.2 Patrones Aplicados

| Patrón             | Propósito                        | Implementación           |
|--------------------|----------------------------------|--------------------------|
| CQRS               | Separación comando/consulta      | `API`/`Processor`        |
| Template Method    | Procesamiento de plantillas      | `RazorEngine`            |
| Strategy           | Múltiples canales                | Handler pattern          |
| Repository         | Acceso a datos                   | `Entity Framework Core`  |

## 4.3 Multi-canal

| Canal        | Tecnología                        | Propósito                    |
|--------------|-----------------------------------|------------------------------|
| Email        | `SMTP`, `SendGrid`                | Notificaciones principales   |
| SMS          | `Twilio`, `AWS SNS`               | Alertas urgentes            |
| WhatsApp     | `Twilio`, `360dialog`             | Mensajería instantánea      |
| Push         | `Firebase`, `APNS`                | Notificaciones móviles       |
