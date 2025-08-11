# 2. Restricciones De La Arquitectura

## 2.1 Restricciones Técnicas

| Categoría           | Restricción                | Justificación         |
|---------------------|---------------------------|----------------------|
| Runtime             | `NET 8`                   | Estándar corporativo |
| Base de datos       | `PostgreSQL`              | Robustez y ACID      |
| Cache/Cola          | `Redis`                   | Rendimiento          |
| Contenedores        | `Docker`                  | Portabilidad         |
| APIs                | `REST`, `OpenAPI`         | Estándar industria   |
| ORM                 | `Entity Framework Core`   | Productividad        |
| Validaciones        | `FluentValidation`        | Seguridad            |
| Logging             | `Serilog`                 | Monitoreo            |
| Mapeo DTOs          | `Mapster`                 | Eficiencia           |
| Testing             | `xUnit`                   | Calidad              |
| Análisis de código  | `SonarQube`               | Mantenibilidad       |
| Seguridad IaC       | `Checkov`                 | Cumplimiento         |

## 2.2 Restricciones De Rendimiento

| Métrica        | Objetivo                        | Razón              |
|----------------|---------------------------------|--------------------|
| Capacidad      | `100,000+ notificaciones/hora`  | Volumen esperado   |
| Latencia       | `< 5s envío`                    | Experiencia usuario|
| Disponibilidad | `99.9%`                         | SLA empresarial    |
| Escalabilidad  | `Horizontal`                    | Crecimiento        |

## 2.3 Restricciones De Seguridad

| Aspecto         | Requerimiento                | Estándar         |
|-----------------|------------------------------|------------------|
| Cumplimiento    | `GDPR`, `LGPD`               | Regulatorio      |
| Cifrado         | `AES-256`, `TLS 1.3`         | Mejores prácticas|
| Autenticación   | `JWT` obligatorio            | Zero trust       |
| Auditoría       | Trazabilidad completa        | Compliance       |

## 2.4 Restricciones Organizacionales

| Área           | Restricción                   | Impacto              |
|----------------|------------------------------|----------------------|
| Multi-tenancy  | Aislamiento por país         | Regulaciones locales |
| Operaciones    | `DevOps 24/7`                | Continuidad negocio  |
| Documentación  | `arc42` actualizada          | Mantenibilidad       |

> Nota: Todas las configuraciones se gestionan por `scripts`, no por API. La autenticación es vía `OAuth2` con `JWT` (`client_credentials`).

- Uso obligatorio de contenedores para todos los servicios.
- Multi-tenant y multipaís como requerimiento transversal.
- Cumplimiento de normativas locales de privacidad y mensajería.
- Integración con sistemas externos vía `API REST` y `Kafka`.
- Despliegue en `AWS` (`EC2`, `RDS`, `Lambda`, `S3`, etc.).
