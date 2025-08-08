# 3. Contexto y alcance del sistema

![API Gateway - Vista de Contexto](/diagrams/servicios-corporativos/api_gateway.png)

*Figura 3.1: Vista de contexto del `API Gateway`*

## 3.1 Alcance del sistema

| Aspecto   | Descripción                                                                 |
|-----------|-----------------------------------------------------------------------------|
| `Incluido`  | Proxy reverso, autenticación (`OAuth2`/`JWT`), rate limiting, load balancing, observabilidad, resiliencia, multi-tenancy |
| `Excluido`  | Lógica de negocio, persistencia de datos, procesamiento, gestión de usuarios |

## 3.2 Actores externos

| Actor                | Rol         | Interacción                |
|----------------------|-------------|----------------------------|
| `Clientes Web`       | Consumidor  | Solicitudes `HTTP/HTTPS`   |
| `Apps Móviles`       | Consumidor  | APIs `REST`                |
| `Servicios Downstream` | Proveedor | Enrutamiento de solicitudes|
| `Sistema Identidad`  | Proveedor   | Validación de tokens       |
| `Observabilidad`     | Consumidor  | Métricas y logs (`Prometheus`, `Grafana`, `Loki`, `Jaeger`) |

## 3.3 Especificaciones técnicas

| Aspecto                | Especificación                        | Rationale                |
|------------------------|---------------------------------------|--------------------------|
| `Platform`             | `.NET 8` + `ASP.NET Core`             | Rendimiento, ecosistema  |
| `Reverse Proxy`        | `YARP`                                | Microsoft, flexible      |
| `Authentication`       | `OAuth2` + `JWT`                      | Estándar de la industria |
| `Protocol`             | `HTTP/2`, `HTTPS only`                | Seguridad, rendimiento   |
| `Balanceador de Carga` | `ALB` (AWS Application Load Balancer) | Alta disponibilidad      |
| `Circuit Breaker`      | `Polly`                               | Tolerancia a fallos      |
| `Observabilidad`       | `Prometheus`, `Grafana`, `Loki`, `Jaeger` | Stack estándar         |

### Protocolos de Comunicación

| Interface         | Protocol      | Port | Purpose           | Security         |
|-------------------|--------------|------|-------------------|------------------|
| `Client API`      | `HTTPS/TLS 1.3` | 443  | Interfaz pública  | `JWT` + `TLS`    |
| `Health Check`    | `HTTP`          | 8080 | Health probes     | Interno          |
| `Metrics`         | `HTTP`          | 9090 | Scraping Prometheus | Interno        |
| `Admin API`       | `HTTPS`         | 8443 | Configuración     | `mTLS`           |

### Configuración de Red

| Parámetro           | Valor         | Propósito                  |
|---------------------|--------------|----------------------------|
| `TLS Version`       | 1.3 mínimo   | Cumplimiento de seguridad  |
| `HTTP Version`      | HTTP/2       | Optimización de rendimiento|
| `Keep-Alive`        | 60 segundos  | Eficiencia de conexión     |
| `Request Timeout`   | 30 segundos  | Experiencia de usuario     |
| `Header Size Limit` | 32KB         | Seguridad y rendimiento    |

## 3.4 Flujos de datos y sistemas externos

| Sistema                  | Tipo      | Protocolo     | Propósito                | Datos Intercambiados         |
|--------------------------|-----------|--------------|--------------------------|------------------------------|
| `Web Applications`       | Cliente   | `HTTPS/REST` | Acceso usuario           | Requests/responses API       |
| `Mobile Applications`    | Cliente   | `HTTPS/REST` | Acceso móvil             | Llamadas API, push           |
| `Partner Systems`        | Externo   | `HTTPS/REST` | Integración B2B          | Datos de negocio, eventos    |
| `Identity System`        | Interno   | `HTTP/OIDC`  | Autenticación            | Validación tokens, claims    |
| `Notification Service`   | Interno   | `HTTP/REST`  | Mensajería               | Requests, status delivery    |
| `Track & Trace Service`  | Interno   | `HTTP/REST`  | Seguimiento eventos       | Consultas, actualizaciones   |
| `SITA Messaging Service` | Interno   | `HTTP/REST`  | Mensajería aviación      | Requests, updates status     |
| `Configuration Platform` | Interno   | `HTTPS/REST` | Configuración dinámica    | Configs rutas, feature flags |
| `Monitoring Systems`     | Interno   | `HTTP/Metrics`| Observabilidad           | Métricas, logs, traces       |

## 3.5 Multi-tenancy y configuración específica

| Método         | Fuente             | Prioridad | Caso de Uso           |
|---------------|--------------------|-----------|-----------------------|
| `JWT Claims`  | Token claim        | 1         | Usuarios autenticados |
| `API Key`     | Custom header      | 2         | Partners externos     |
| `Subdomain`   | Host header        | 3         | Aplicaciones web      |
| `Query Param` | URL parameter      | 4         | Sistemas legacy       |

| Tenant        | País      | Subdominio                  | Rate Limits     | Backend Pool      |
|---------------|-----------|-----------------------------|-----------------|-------------------|
| `talma-pe`    | Perú      | pe.corporate.talma.com      | 10k req/hour    | pe-backend-pool   |
| `talma-ec`    | Ecuador   | ec.corporate.talma.com      | 5k req/hour     | ec-backend-pool   |
| `talma-co`    | Colombia  | co.corporate.talma.com      | 8k req/hour     | co-backend-pool   |
| `talma-mx`    | México    | mx.corporate.talma.com      | 6k req/hour     | mx-backend-pool   |

## 3.6 Estándares y protocolos

| Categoría         | Estándar/Protocolo | Versión | Uso en el Sistema         |
|-------------------|-------------------|---------|--------------------------|
| `HTTP`            | HTTP/2, HTTP/3    | Latest  | Comunicación cliente      |
| `Security`        | TLS 1.3           | Current | Encriptación en tránsito  |
| `Authentication`  | OAuth2 + JWT      | RFC 6749, RFC 7519 | Autenticación tokens |
| `API Design`      | OpenAPI           | 3.0+    | Especificación de APIs    |
| `Logging`         | JSON estructurado | Custom  | Observabilidad (`Loki`)   |
| `Metrics`         | Prometheus        | Latest  | Monitoreo de rendimiento  |
| `Tracing`         | Jaeger            | Latest  | Trazabilidad distribuida  |

## Referencias

- [Arc42 Context Template](https://docs.arc42.org/section-3/)
- [C4 Model for Architecture](https://c4model.com/)
- [YARP Documentation](https://microsoft.github.io/reverse-proxy/)
- [OAuth2 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Loki](https://grafana.com/oss/loki/)
- [Jaeger](https://www.jaegertracing.io/)

---

> El contexto y alcance del API Gateway están alineados a los modelos C4/Structurizr DSL y la documentación Arc42, garantizando claridad en los límites, actores, protocolos y mecanismos de multi-tenancy del sistema.
