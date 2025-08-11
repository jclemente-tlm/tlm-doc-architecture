# 6. Vista De Tiempo De Ejecución

## 6.1 Escenarios Principales

| Escenario                  | Flujo principal                                      | Componentes involucrados                |
|----------------------------|-----------------------------------------------------|-----------------------------------------|
| Proxy request              | Cliente → Gateway → Backend                         | `YARP`, `ALB`, `.NET 8`                |
| Autenticación              | Validación JWT → Claims                             | `Auth Middleware`, `Keycloak`           |
| Rate limiting              | Request → `Redis` → Allow/Deny                     | `Rate Limiter`, `Redis`                 |
| Circuit breaker            | Proxy → `Polly` → Servicio/Fallback                 | `Polly`, `YARP`                        |
| Observabilidad             | Request → Logging/Metrics/Tracing                   | `Serilog`, `Loki`, `Prometheus`, `Jaeger` |

## 6.2 Flujos De Interacción Y Patrones

- Autenticación y enrutamiento: validación de token `JWT` (cache en `Redis`), resolución de tenant, rate limiting y enrutamiento al backend, enriqueciendo headers con información relevante.
- Health checks y circuit breaker: monitoreo activo, apertura/cierre de circuitos y failover automático.
- Rate limiting distribuido: ventana deslizante de `1 minuto`, sincronización vía `Redis`, headers estándar en respuesta.
- Failover y degradación: switchover automático, degradación controlada bajo sobrecarga, priorización de clientes premium.
- Multi-tenancy: resolución de tenant vía claims `JWT`, `API Key`, subdominio o query param; routing inteligente por tier y país.
- Observabilidad: trazabilidad distribuida (`Jaeger`), métricas en tiempo real (`Prometheus`), logs estructurados (`Loki`), dashboards y alertas (`Grafana`).

## 6.3 Ejemplos De Ejecución (Diagramas De Secuencia)

### 6.3.1 Flujo De Autenticación Y Enrutamiento

```mermaid
sequenceDiagram
    participant Client as Cliente Web/Mobile
    participant Gateway as API Gateway
    participant Auth as Identity Service
    participant Service as Target Service
    participant Redis as Redis Cache
    Client->>Gateway: Request con token JWT
    Gateway->>Redis: Verificar token en cache
    alt Token en cache
        Redis->>Gateway: Token válido
    else Token no en cache
        Gateway->>Auth: Validar token
        Auth->>Gateway: Resultado validación
        Gateway->>Redis: Cachear token
    end
    Gateway->>Gateway: Resolver tenant y aplicar rate limiting
    Gateway->>Service: Forward con headers enriquecidos
    Service->>Gateway: Response
    Gateway->>Client: Response con headers de rate limit
```

### 6.3.2 Health Check Y Circuit Breaker

```mermaid
sequenceDiagram
    participant Monitor as Health Monitor
    participant Gateway as API Gateway
    participant Service1 as Service Instance 1
    participant Service2 as Service Instance 2
    participant Circuit as Circuit Breaker
    loop Cada 30s
        Monitor->>Service1: Health check
        Monitor->>Service2: Health check
        alt Healthy
            Service1->>Monitor: 200 OK
        else Unhealthy
            Service2->>Monitor: 500/Error
            Monitor->>Circuit: Open circuit
        end
    end
    Gateway->>Circuit: Check state
    Circuit->>Gateway: Circuit OPEN
    Gateway->>Service1: Route only to healthy
```

### 6.3.3 Rate Limiting Distribuido

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant Gateway1 as Gateway 1
    participant Gateway2 as Gateway 2
    participant Redis as Redis
    Client->>Gateway1: Request
    Gateway1->>Redis: INCR rate_limit
    Redis->>Gateway1: Counter
    Gateway1->>Client: 200 OK
    Client->>Gateway2: Request
    Gateway2->>Redis: INCR rate_limit
    Redis->>Gateway2: Counter
    Gateway2->>Client: 200 OK
    Note over Gateway1,Redis: Al superar límite
    Gateway1->>Client: 429 Too Many Requests
```

### 6.3.4 Failover Automático Y Degradación

```mermaid
sequenceDiagram
    participant Client as Cliente
    participant Gateway as API Gateway
    participant Primary as Servicio Primario
    participant Secondary as Servicio Secundario
    participant Monitor as Health Monitor
    Client->>Gateway: Request
    Gateway->>Primary: Forward
    Primary->>Gateway: Response
    Gateway->>Client: Response
    Note over Primary: Falla
    Monitor->>Gateway: Mark primary unhealthy
    Gateway->>Secondary: Forward
    Secondary->>Gateway: Response
    Gateway->>Client: Response
```

### 6.3.5 Multi-Tenancy Y Routing Inteligente

```mermaid
sequenceDiagram
    participant ClientA as Tenant Premium
    participant ClientB as Tenant Standard
    participant Gateway as API Gateway
    participant PremiumService as Premium Instance
    participant StandardService as Standard Instance
    ClientA->>Gateway: Request (premium)
    Gateway->>PremiumService: Route
    PremiumService->>Gateway: Response
    Gateway->>ClientA: Response
    ClientB->>Gateway: Request (standard)
    Gateway->>StandardService: Route
    StandardService->>Gateway: Response
    Gateway->>ClientB: Response
```

### 6.3.6 Observabilidad Y Monitoreo

```mermaid
sequenceDiagram
    participant Gateway as API Gateway
    participant Metrics as Metrics Collector
    participant Prometheus as Prometheus
    participant Grafana as Grafana
    participant Loki as Loki
    participant Jaeger as Jaeger
    Gateway->>Metrics: Record metrics
    Gateway->>Loki: Log request
    Gateway->>Jaeger: Trace span
    Metrics->>Prometheus: Scrape
    Grafana->>Prometheus: Query
    Grafana->>Loki: Query logs
    Grafana->>Jaeger: Query traces
```

## 6.4 Objetivos De Rendimiento Y SLA

| Operación                  | Target           | Timeout | SLA    |
|----------------------------|------------------|---------|--------|
| Token validation (cache)   | `< 10ms`         | `100ms` | `99.9%`  |
| Token validation (fresh)   | `< 100ms`        | `500ms` | `99.5%`  |
| Request routing            | `< 5ms`          | `50ms`  | `99.9%`  |
| Health check               | `< 200ms`        | `5s`    | `95%`    |
| Rate limit check           | `< 5ms`          | `100ms` | `99.9%`  |
| Config reload              | `< 1s`           | `30s`   | `99%`    |
| Circuit breaker            | `< 100ms`        | `500ms` | `99%`    |

## 6.5 Manejo De Errores Y Resiliencia

- Timeout downstream: `30s`, `3 reintentos` con backoff, circuit breaker tras `5 fallos`, responde `504` con `retry-after`.
- Identity service caído: cache de tokens extendido `1h`, solo requests con tokens válidos, responde `503` para nuevas autenticaciones.
- Degradación bajo carga: priorización de clientes premium, cola para estándar, `503` si no hay capacidad.

---
