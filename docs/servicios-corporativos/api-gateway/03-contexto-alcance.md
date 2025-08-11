# 3. Contexto Y Alcance Del Sistema

![API Gateway - Vista de Contexto](/diagrams/servicios-corporativos/api_gateway.png)

*Figura 3.1: Vista de contexto del API Gateway como punto de entrada seguro y centralizado para clientes, aplicaciones y sistemas internos y externos.*

## 3.1 Alcance Del Sistema

| Aspecto   | Descripción                                                                 |
|-----------|-----------------------------------------------------------------------------|
| Incluido  | Proxy reverso, autenticación (`OAuth2`/`JWT`), rate limiting, balanceo de carga, observabilidad, resiliencia, multi-tenancy (`realms`) |
| Excluido  | Lógica de negocio, persistencia de datos, procesamiento, gestión de usuarios |

## 3.2 Actores Externos

| Actor                  | Rol         | Interacción                |
|------------------------|-------------|----------------------------|
| `Clientes Web`         | Consumidor  | Solicitudes `HTTP/HTTPS`   |
| `Apps Móviles`         | Consumidor  | APIs `REST`                |
| `Servicios Downstream` | Proveedor   | Enrutamiento de solicitudes|
| `Sistema Identidad`    | Proveedor   | Validación de tokens       |
| `Observabilidad`       | Consumidor  | Métricas y logs (`Prometheus`, `Grafana`, `Loki`, `Jaeger`) |

## 3.3 Flujos De Datos Y Sistemas Externos

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

## Referencias

- [arc42: Context Template](https://docs.arc42.org/section-3/)
- [YARP](https://microsoft.github.io/reverse-proxy/)
- [OAuth2 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Loki](https://grafana.com/oss/loki/)
- [Jaeger](https://www.jaegertracing.io/)
