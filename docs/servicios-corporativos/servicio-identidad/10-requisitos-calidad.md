# 10. Requisitos De Calidad

## 10.1 Rendimiento

| Métrica              | Objetivo         | Medición      |
|----------------------|-----------------|--------------|
| Latencia auth        | `< 200ms p95`   | `Prometheus` |
| Throughput           | `5k logins/min` | Load testing |
| Disponibilidad       | `99.95%`        | Health checks|
| Token validation     | `< 50ms`        | Benchmarks   |

- Instrumentación y monitoreo continuo en todos los entornos.
- Criterios de aceptación claros y cuantificables para cada métrica.

## 10.2 Seguridad

| Aspecto      | Requisito           | Implementación |
|--------------|---------------------|----------------|
| MFA          | Obligatorio admin   | `Keycloak`     |
| Tokens       | `JWT RS256`         | Certificados   |
| Passwords    | Políticas fuertes   | `Keycloak`     |
| Audit        | Todos los eventos   | Logs           |

- Cumplimiento de políticas de contraseñas, MFA y auditoría de eventos críticos.
- Validación y rotación periódica de certificados y secretos.

## 10.3 Escalabilidad

| Aspecto      | Objetivo                    | Estrategia     |
|--------------|-----------------------------|----------------|
| Usuarios     | `100k` por `tenant` (`realm`)| Autoescalado   |
| Tenants      | `50+` países                | Multi-tenant   |
| Sessions     | `10k` concurrentes          | `PostgreSQL`   |
| Federación   | Múltiples IdP               | Híbrida        |

- Arquitectura multi-tenant y autoescalable.
- Pruebas de carga periódicas para validar límites y crecimiento.

## 10.4 Latencia Y Capacidad Crítica

| Operación                  | P50   | P95   | P99   | SLA Crítico |
|----------------------------|-------|-------|-------|-------------|
| Inicio de sesión inicial   | 300ms | 800ms | 1.5s  | `< 2s`      |
| Validación token (cache)   | 5ms   | 15ms  | 30ms  | `< 50ms`    |
| Validación token (no cache)| 50ms  | 120ms | 200ms | `< 300ms`   |
| Renovación token           | 80ms  | 200ms | 400ms | `< 500ms`   |
| Cierre sesión              | 100ms | 250ms | 500ms | `< 1s`      |
| Desafío MFA                | 200ms | 500ms | 1s    | `< 2s`      |
| Federación externa         | 800ms | 2s    | 4s    | `< 5s`      |

- SLAs definidos y medidos para operaciones críticas.
- Alertas automáticas ante degradación de performance.

## 10.5 Referencias

- [Arc42 Quality Requirements](https://docs.arc42.org/section-10/)
- [Keycloak Performance Docs](https://www.keycloak.org/docs/latest/server_admin/#performance)
- [C4 Model for Software Architecture](https://c4model.com/)
