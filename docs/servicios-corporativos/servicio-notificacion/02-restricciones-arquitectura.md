# 2. Restricciones de la arquitectura

## 2.1 Restricciones técnicas

| Categoría           | Restricción                | Justificación         |
|---------------------|---------------------------|----------------------|
| Runtime             | `NET 8`                   | Estandarización y soporte corporativo |
| Base de datos       | `PostgreSQL`              | Robustez, ACID, escalabilidad, soporte para sharding y particionamiento |
| Cache/Cola          | `Redis`                   | Rendimiento, desacoplamiento, tolerancia a picos, soporte para `DLQ` |
| Contenedores        | `Docker`                  | Portabilidad y despliegue consistente |
| APIs                | `REST`, `OpenAPI`         | Interoperabilidad y estandarización |
| ORM                 | `Entity Framework Core`   | Productividad y mantenibilidad |
| Validaciones        | `FluentValidation`        | Seguridad y consistencia |
| Logging             | `Serilog`                 | Monitoreo centralizado y logging distribuido |
| Mapeo DTOs          | `Mapster`                 | Eficiencia y simplicidad |
| Testing             | `xUnit`                   | Calidad y automatización |
| Análisis de código  | `SonarQube`               | Mantenibilidad y calidad continua |
| Seguridad IaC       | `Checkov`                 | Cumplimiento y control de infraestructura |
| Deduplicación       | Hash de payload y claves de idempotencia | Evitar duplicados en reintentos y concurrencia |
| Idempotencia        | `Idempotency-Key` en API y procesamiento | Garantizar entrega única ante reintentos |
| Versionado de plantillas | Versionado y fallback automático | Soportar cambios sin afectar envíos activos |

> Todas las tecnologías y patrones deben implementarse usando únicamente las herramientas y librerías aprobadas (`.NET 8`, `PostgreSQL`, `Redis`, `Docker`, `Entity Framework Core`, `FluentValidation`, `Serilog`, `Mapster`, `xUnit`, `SonarQube`, `Checkov`).

## 2.2 Restricciones de rendimiento

| Métrica        | Objetivo                        | Razón              |
|----------------|---------------------------------|--------------------|
| Capacidad      | `100,000+ notificaciones/hora`  | Volumen esperado   |
| Latencia       | `< 5s` envío                    | Experiencia usuario|
| Disponibilidad | `99.9%`                         | SLA empresarial    |
| Escalabilidad  | `Horizontal`                    | Crecimiento mediante desacoplamiento y procesadores independientes |
| Duplicidad     | `< 0.1%` mensajes duplicados    | Calidad de servicio|

> El sistema debe soportar reintentos automáticos, deduplicación, idempotencia y manejo eficiente de picos mediante colas y `DLQ`.

## 2.3 Restricciones de seguridad

| Aspecto         | Requerimiento                | Estándar         |
|-----------------|------------------------------|------------------|
| Cumplimiento    | `GDPR`, `LGPD`               | Regulatorio      |
| Cifrado         | `AES-256`, `TLS 1.3`         | Mejores prácticas|
| Autenticación   | `JWT` obligatorio, rate limiting y protección anti-abuso | Seguridad API   |
| Auditoría       | Trazabilidad completa        | Compliance       |
| Acceso          | `RBAC` y control granular    | Seguridad        |

> La autenticación y autorización se implementa exclusivamente con `Keycloak` y validación de `JWT`.

## 2.4 Restricciones organizacionales

| Área           | Restricción                   | Impacto              |
|----------------|------------------------------|----------------------|
| Multi-tenancy  | Aislamiento por país         | Regulaciones locales |
| Operaciones    | `DevOps 24/7`                | Continuidad negocio  |
| Documentación  | `arc42` actualizada          | Mantenibilidad       |

---

**Notas generales:**

- Todas las configuraciones se gestionan por `scripts`, no por API.
- Autenticación vía `OAuth2` con `JWT` (`client_credentials`).
- Uso obligatorio de contenedores para todos los servicios.
- Multi-tenant y multipaís como requerimiento transversal.
- Cumplimiento de normativas locales de privacidad y mensajería.
- Integración con sistemas externos vía `API REST`.
- Despliegue en `AWS` (`EC2`, `RDS`, `Lambda`, `S3`, etc.).
- Monitoreo centralizado, logging distribuido y archivado de históricos para observabilidad y cumplimiento.
