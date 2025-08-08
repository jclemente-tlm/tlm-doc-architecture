# 9. Decisiones de arquitectura

## 9.1 Decisiones principales

| ADR | Decisión | Estado | Justificación |
|-----|----------|--------|---------------|
| `ADR-001` | `YARP` como proxy | Aceptado | Integración `.NET` nativa |
| `ADR-002` | `Redis` rate limiting | Aceptado | Escalabilidad y consistencia distribuida |
| `ADR-003` | `JWT` + `OAuth2` | Aceptado | Estándar industria, interoperabilidad |
| `ADR-004` | Multi-tenant realms | Aceptado | Aislamiento y flexibilidad |
| `ADR-005` | Health checks multinivel | Aceptado | Observabilidad granular |

## 9.2 Alternativas evaluadas

| Componente | Alternativas | Selección | Razón |
|------------|-------------|-----------|--------|
| `Proxy` | NGINX, Envoy, YARP | `YARP` | `.NET` nativo, extensibilidad |
| `Rate Limiting` | In-memory, Redis, Database | `Redis` | Distribuido, baja latencia |
| `Auth` | Custom, Auth0, Keycloak | `Keycloak` | Control total, integración OIDC |
| `Observabilidad` | Custom, Datadog, Grafana | `Grafana Stack` | Agnóstico, open source |

## 9.3 Decisiones clave (formato ADR)

### ADR-001: Proxy basado en YARP

- **Estado**: Aceptado
- **Fecha**: 2024-01-10
- **Decisores**: Equipo de Arquitectura
- **Contexto**: Se requiere un reverse proxy extensible, nativo en .NET, con soporte para middlewares y configuración dinámica.
- **Decisión**: Se selecciona `YARP` por su integración nativa, soporte de middlewares y flexibilidad.
- **Consecuencias**: Integración rápida, reutilización de stack, pero menor madurez frente a NGINX.

### ADR-002: Rate limiting distribuido con Redis

- **Estado**: Aceptado
- **Fecha**: 2024-01-20
- **Decisores**: Equipo de Arquitectura
- **Contexto**: Se requiere rate limiting consistente entre instancias, baja latencia y tolerancia a fallos.
- **Decisión**: Se implementa rate limiting distribuido con `Redis` (sliding window, fallback local).
- **Consecuencias**: Consistencia, degradación graceful, pero complejidad operativa y dependencia externa.

### ADR-003: Circuit breaker adaptativo por servicio

- **Estado**: Aceptado
- **Fecha**: 2024-01-25
- **Decisores**: Arquitectura, SRE
- **Contexto**: Prevenir fallos en cascada y sobrecarga de servicios backend.
- **Decisión**: Circuit breakers independientes y adaptativos por servicio, con métricas y backoff configurable.
- **Consecuencias**: Prevención efectiva, métricas detalladas, pero tuning y debugging más complejos.

### ADR-004: Validación JWT local con cache y revocación diferida

- **Estado**: Aceptado
- **Fecha**: 2024-02-01
- **Decisores**: Seguridad, Arquitectura
- **Contexto**: Validar JWT tokens con baja latencia y resiliencia ante caídas del servicio de identidad.
- **Decisión**: Validación local con cache y verificación periódica con el servicio de identidad.
- **Consecuencias**: Latencia baja, resiliencia, pero posible ventana de inconsistencia.

### ADR-005: Health checks multinivel y endpoints especializados

- **Estado**: Aceptado
- **Fecha**: 2024-02-05
- **Decisores**: SRE, DevOps
- **Contexto**: Necesidad de monitoreo granular y decisiones de routing por estado real del sistema.
- **Decisión**: Endpoints `/health/live`, `/health/ready`, `/health/detailed` con chequeos por dependencia y recursos.
- **Consecuencias**: Observabilidad granular, integración con Prometheus/Grafana, pero mayor complejidad de configuración.

---

> Todas las decisiones están documentadas en formato ADR, alineadas a los modelos C4/Structurizr DSL y cumplen con los requisitos de seguridad, resiliencia, observabilidad y multi-tenancy definidos para el API Gateway.
