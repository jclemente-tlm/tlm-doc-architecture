---
id: api-gateway-usage
sidebar_position: 6
title: Uso del API Gateway (Kong)
description: Estándar para determinar cuándo enrutar tráfico a través de Kong, qué responsabilidades corresponden al gateway vs al servicio, y qué está prohibido hacer en Kong.
tags: [apis, kong, api-gateway, seguridad, integración, norte-sur, este-oeste]
---

# Uso del API Gateway (Kong)

## Contexto

Este estándar define cuándo usar Kong como API Gateway, qué tipos de tráfico le corresponden, y la delimitación de responsabilidades entre Kong y los servicios backend. Complementa el [lineamiento de APIs y Contratos de Integración](../../lineamientos/integracion/apis-y-contratos.md).

**Decisión arquitectónica:** [ADR-010: Kong API Gateway](../../../adrs/adr-010-kong-api-gateway.md) — Kong OSS sobre ECS Fargate. Objetivo: p95 < 10ms latencia añadida, > 10 000 req/s.

El problema central que resuelve Kong es ser el **único punto de entrada controlado** para tráfico no originado dentro del mismo cluster de servicios. No es un bus de integración ni un orquestador: es un proxy inteligente con capacidades de autenticación, rate limiting y enrutamiento.

---

## Stack Tecnológico

| Componente          | Tecnología                  | Versión | Uso                                     |
| ------------------- | --------------------------- | ------- | --------------------------------------- |
| **API Gateway**     | Kong OSS                    | —       | Proxy de entrada norte-sur              |
| **Infraestructura** | AWS ECS Fargate             | —       | Runtime de Kong                         |
| **Configuración**   | Declarative config (`deck`) | —       | GitOps de rutas, plugins y consumidores |

---

## Modelo de Tráfico — Norte-Sur vs Este-Oeste

### Tráfico Norte-Sur (requiere Kong)

Flujo: **Internet / Sistema externo → Kong → Servicio interno**

Todo tráfico que proviene de fuera del cluster (usuarios, partners, sistemas SaaS, webhooks) **DEBE** pasar por Kong. No existe ruta directa desde internet hacia ningún servicio.

```
Internet
   │
   ▼
[Kong] ◀── valida JWT / API Key
   │         aplica rate limiting
   │         verifica rutas
   ▼
[Servicio A]
```

**Aplica a:**


- Usuarios autenticados consumiendo APIs desde apps web o móviles.
- Partners externos integrados vía API Key.
- Webhooks entrantes de proveedores externos.
- Sistemas SaaS de Talma que consumen APIs internas.

### Tráfico Este-Oeste (sin Kong)

Flujo: **Servicio A → Servicio B** (mismo cluster)

La llamada entre servicios dentro del mismo cluster ECS/red privada se realiza **directamente** sin pasar por Kong. Agregar Kong en este flujo añade latencia innecesaria y crea un punto único de fallo para tráfico interno.

```
[Servicio A] ──────────────▶ [Servicio B]
              (llamada directa,
               JWT client_credentials,
               DNS interno)
```

La autenticación en este-oeste se gestiona con JWT generado por Keycloak (`client_credentials`). El servicio receptor valida el JWT localmente.


**Aplica a:**

- Llamadas síncronas entre microservicios del mismo dominio.
- Llamadas a servicios de plataforma interna (almacenamiento, notificaciones, etc.).

### Tráfico Cross-Cluster o Cross-Region

Flujo: **Servicio en Cluster A → Servicio en Cluster B**

Cuando el servicio destino no comparte red privada con el origen, se usan dos opciones válidas:

| Opción                        | Cuándo usarla                                                       |
| ----------------------------- | ------------------------------------------------------------------- |
| **Kong como proxy de egress** | El cluster destino expone sus APIs a través de su propio Kong       |
| **mTLS directo**              | Conexión directa autenticada con certificados mutuos entre clusters |

---

## Responsabilidades: Kong vs Servicio

### Kong es responsable de

| Responsabilidad                        | Plugin / Mecanismo                           |
| -------------------------------------- | -------------------------------------------- |
| Validación de JWT (firma + expiración) | `jwt` plugin con clave pública RSA del realm |
| Validación de API Keys                 | `key-auth` plugin                            |
| Rate limiting por consumidor / ruta    | `rate-limiting` plugin                       |
| Terminación TLS                        | AWS ALB → Kong                               |
| Enrutamiento hacia upstream            | `service` + `route` declarativos             |
| Transformación básica de headers       | `request-transformer` plugin                 |

Kong **no** tiene acceso a la lógica de negocio ni a la base de datos del servicio. Actúa antes de que el request llegue al servicio.

### El servicio es responsable de

| Responsabilidad                              | Dónde                                      |
| -------------------------------------------- | ------------------------------------------ |
| Autorización por claims del JWT              | Middleware en el servicio (`.NET` policy)  |
| Validación de negocio de los datos entrantes | Controller / Handler                       |
| Logs de auditoría de operaciones             | Servicio → sistema de logging centralizado |
| Control de acceso a nivel de recurso         | Servicio backend                           |

:::danger Kong no reemplaza la autorización del servicio
Que Kong haya validado el JWT **no implica que el usuario tenga permiso para el recurso específico**. La autorización basada en roles y claims es siempre responsabilidad del servicio. No elimines las verificaciones de autorización del backend.
:::

---

## Configuración de Kong en GitOps

Kong se configura de forma declarativa con `deck`. Los archivos viven en el repositorio `tlm-infra-kong`. Un cambio en una ruta, plugin o consumidor se aplica mediante pull request + `make sync-{env}`.


**Archivos de configuración relevantes:**

- `_consumers.yaml` — consumidores (incluye clave RSA embebida para validación JWT)
- `_services.yaml` — upstreams y definición de services
- `_routes.yaml` — rutas expuestas por Kong
- `_plugins.yaml` — plugins globales y por ruta

Cualquier nueva integración o exposición de API **MUST** tener su configuración declarativa en este repositorio antes de llegar a producción.

---

## Ejemplos de Uso Correcto

```text
// ✅ BIEN: App web (norte-sur) → Kong → Servicio
GET https://api.talma.com/mx/gestal/postulaciones
Authorization: Bearer <jwt>

→ Kong valida JWT del realm tlm-mx
→ Kong enruta hacia gestal-api:8080
→ gestal-api verifica claims y devuelve resultado
```

```text
// ✅ BIEN: Servicio interno (este-oeste) → llamada directa
// sisbon-mx llama a notification-service en el mismo cluster
POST http://notification-service.internal/eventos
Authorization: Bearer <jwt client_credentials>

→ notification-service valida JWT localmente
→ No pasa por Kong
```

```text
// ❌ MAL: Servicio interno enrutando por Kong para llamar a otro servicio interno
POST https://api.talma.com/mx/notificaciones/eventos
Authorization: Bearer <jwt>

→ Latencia innecesaria (~10ms extra)
→ Kong registrado como punto de tráfico interno
→ Viola el estándar este-oeste
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** enrutar por Kong todo tráfico de origen externo al cluster (norte-sur).
- **MUST** configurar autenticación (JWT o API Key) en Kong para toda ruta expuesta a internet.
- **MUST** gestionar la configuración de Kong de forma declarativa en el repositorio `tlm-infra-kong`.
- **MUST** aplicar rate limiting a todas las rutas públicas.
- **MUST** usar el plugin `jwt` con la clave pública RSA del realm correspondiente.

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar el plugin `request-transformer` para añadir headers de traza (`X-Request-Id`, `X-Tenant`) antes del upstream.
- **SHOULD** registrar métricas de Kong en el sistema centralizado de observabilidad.
- **SHOULD** versionar las rutas de Kong (`/v1/`, `/v2/`) alineado con el versionado de la API.

### MUST NOT (Prohibido)

- **MUST NOT** enrutar tráfico este-oeste (servicio → servicio mismo cluster) a través de Kong.
- **MUST NOT** exponer servicios internos directamente a internet sin pasar por Kong.
- **MUST NOT** configurar autenticación con `basic-auth` plugin en Kong.
- **MUST NOT** aplicar lógica de autorización de negocio en plugins de Kong (solo autenticación).
- **MUST NOT** modificar la configuración de Kong directamente en consola o CLI sin actualizar el repositorio declarativo.

---

## Referencias

- [Lineamiento de APIs y Contratos de Integración](../../lineamientos/integracion/apis-y-contratos.md) — lineamiento que origina este estándar.
- [ADR-010: Kong API Gateway](../../../adrs/adr-010-kong-api-gateway.md) — adopción de Kong y justificación de la arquitectura norte-sur.
- [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md) — emisión de JWT que Kong valida.
- [Autenticación de APIs — JWT y API Keys](../seguridad/api-authentication.md) — mecanism de autenticación aplicados en Kong.
- [Estándares de APIs REST](./api-rest-standards.md) — diseño de contratos que Kong expone.
- [Kong OSS Documentation](https://docs.konghq.com/) — referencia oficial del gateway.
