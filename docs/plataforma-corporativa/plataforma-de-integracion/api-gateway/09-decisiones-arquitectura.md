# 9. Decisiones De Arquitectura

## 9.1 Decisiones Principales

| ADR        | Decisión                  | Estado    | Justificación                        |
|------------|---------------------------|-----------|--------------------------------------|
| `ADR-001`  | YARP como proxy           | Aceptado  | Integración `.NET` nativa            |
| `ADR-002`  | Redis rate limiting       | Aceptado  | Escalabilidad y consistencia distribuida |
| `ADR-003`  | JWT + OAuth2              | Aceptado  | Estándar industria, interoperabilidad|
| `ADR-004`  | Multi-tenant realms       | Aceptado  | Aislamiento y flexibilidad           |
| `ADR-005`  | Health checks multinivel  | Aceptado  | Observabilidad granular              |

## 9.2 Alternativas Evaluadas

| Componente        | Alternativas           | Selección | Razón                        |
|-------------------|-----------------------|-----------|------------------------------|
| Proxy             | NGINX, Envoy, YARP    | YARP      | `.NET` nativo, extensibilidad|
| Rate Limiting     | In-memory, Redis, Database | Redis | Distribuido, baja latencia   |
| Auth              | Custom, Auth0, Keycloak | Keycloak | Control total, integración OIDC |
| Observabilidad    | Custom, Datadog, Grafana | Grafana Stack | Agnóstico, open source |

## 9.3 Decisiones Clave (Formato ADR)

### ADR-001: Proxy Basado En YARP

- **Estado**: Aceptado
- **Fecha**: 2024-01-10
- **Decisores**: Equipo de Arquitectura
- **Contexto**: Se requiere un reverse proxy extensible, nativo en `.NET`, con soporte para middlewares y configuración dinámica.
- **Decisión**: Se selecciona YARP por su integración nativa, soporte de middlewares y flexibilidad.
- **Consecuencias**: Integración rápida, reutilización de stack, pero menor madurez frente a NGINX.

### ADR-002: Rate Limiting Distribuido Con Redis

- **Estado**: Aceptado
- **Fecha**: 2024-01-20
- **Decisores**: Equipo de Arquitectura
- **Contexto**: Se requiere rate limiting consistente entre instancias, baja latencia y tolerancia a fallos.
- **Decisión**: Rate limiting distribuido con Redis (sliding window, fallback local).
- **Consecuencias**: Consistencia, degradación controlada, mayor complejidad operativa y dependencia externa.

### ADR-003: Circuit Breaker Adaptativo Por Servicio

- **Estado**: Aceptado
- **Fecha**: 2024-01-25
- **Decisores**: Arquitectura, SRE
- **Contexto**: Prevenir fallos en cascada y sobrecarga de servicios backend.
- **Decisión**: Circuit breakers independientes y adaptativos por servicio, con métricas y backoff configurable.
- **Consecuencias**: Prevención efectiva, métricas detalladas, tuning y debugging más complejos.

### ADR-004: Validación JWT Local Con Cache Y Revocación Diferida

- **Estado**: Aceptado
- **Fecha**: 2024-02-01
- **Decisores**: Seguridad, Arquitectura
- **Contexto**: Validar JWT tokens con baja latencia y resiliencia ante caídas del servicio de identidad.
- **Decisión**: Validación local con cache y verificación periódica con el servicio de identidad.
- **Consecuencias**: Latencia baja, resiliencia, posible ventana de inconsistencia.

### ADR-005: Health Checks Multinivel Y Endpoints Especializados

- **Estado**: Aceptado
- **Fecha**: 2024-02-05
- **Decisores**: SRE, DevOps
- **Contexto**: Necesidad de monitoreo granular y decisiones de routing por estado real del sistema.
- **Decisión**: Endpoints `/health/live`, `/health/ready`, `/health/detailed` con chequeos por dependencia y recursos.
- **Consecuencias**: Observabilidad granular, integración con Prometheus y Grafana, mayor complejidad de configuración.

---
