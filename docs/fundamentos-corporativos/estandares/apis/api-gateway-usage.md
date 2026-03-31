---
id: api-gateway-usage
sidebar_position: 6
title: Uso del API Gateway
description: Estándar para determinar cuándo un servicio debe exponerse a través del API gateway y cuándo la comunicación directa entre servicios es la opción correcta.
tags: [apis, api-gateway, seguridad, integración, norte-sur, este-oeste, gateway-offloading]
---

# Uso del API Gateway

## Contexto

Este estándar define cuándo un servicio **debe** exponerse a través del API gateway y cuándo **no es necesario** hacerlo. La decisión se basa en dos criterios independientes: si el tráfico cruza el perímetro de red privada, y si se necesita aplicar funcionalidades transversales de forma centralizada (Gateway Offloading).

Complementa el [lineamiento de APIs y Contratos de Integración](../../lineamientos/integracion/apis-y-contratos.md).

:::note Implementación actual
La implementación del API gateway es Kong OSS. Los detalles de configuración y operación están en [ADR-010: Kong API Gateway](../../../adrs/adr-010-kong-api-gateway.md).
:::

---

## Criterios para usar el API Gateway

Un servicio se expone a través del gateway cuando se cumple **al menos uno** de estos dos criterios:

1. **El tráfico cruza el perímetro de red privada** — cualquier consumidor externo al perímetro debe pasar por el gateway.
2. **Se requiere Gateway Offloading** — necesidad de aplicar funcionalidades transversales de forma centralizada (rate limiting, propagación de headers, abstracción de credenciales), independientemente de si el tráfico es interno o externo.

Ambos criterios pueden aplicar simultáneamente. Si ninguno aplica, la comunicación directa es la opción correcta.

---

## Escenarios por tipo de tráfico

### Tráfico de entrada desde consumidores externos — Requiere gateway

Flujo: **Consumidor externo → API Gateway → Servicio**

Todo tráfico que proviene de fuera del perímetro de red privada **debe** ingresar por el API gateway. No existe ruta directa desde el exterior hacia ningún servicio.

```
Consumidor externo
(usuario / partner / sistema externo / país remoto)
          │
          ▼
   [API Gateway]  ◀── autenticación (JWT / API Key)
          │            rate limiting
          │            enrutamiento
          ▼
   [Servicio]
```

Un servicio debe exponerse a través del API gateway cuando lo consume:

- Un usuario final desde una app web o móvil.
- Un partner o cliente externo integrado vía API.
- Un proveedor externo que envía webhooks.
- Una aplicación o servicio de otro país de Talma que no comparte red privada con el destino.
- Una aplicación o servicio on-premise conectado por internet (sin VPN o peering privado hacia la plataforma cloud).

### Tráfico entre servicios con red privada compartida — Directo por defecto

Flujo: **Servicio A → Servicio B** (misma red privada)

Cuando dos servicios comparten red privada — ya sea en el mismo cluster cloud, en la misma red on-premise o conectados por VPN interna — la comunicación se realiza **directamente** sin pasar por el gateway. Es el caso más común porque evita latencia innecesaria y no introduce puntos adicionales de fallo.

```
[Servicio A] ──────────────▶ [Servicio B]
              llamada directa
              JWT client_credentials
              DNS interno
```

La autenticación se gestiona con JWT emitido por Keycloak usando el flujo `client_credentials`. El servicio receptor valida el token localmente.

Un servicio **no** necesita exponerse por el gateway cuando lo llama:

- Otro servicio del mismo cluster cloud.
- Un servicio on-premise dentro de la misma red interna.
- Un servicio conectado por VPN corporativa o peering privado.
- Un servicio de plataforma consumido únicamente de forma interna (almacenamiento, notificaciones, etc.).

:::tip
Aun en red privada compartida, puede justificarse enrutar por el gateway si se necesita aplicar Gateway Offloading sobre ese servicio (rate limiting por consumidor, propagación garantizada de headers, etc.). Ver la sección **Gateway Offloading** más abajo.
:::

### Tráfico entre servicios sin red privada compartida — Evaluar caso

Flujo: **Servicio A (red X) → Servicio B (red Y)**

Cuando dos servicios internos de Talma no comparten red privada (distintos países sin interconexión privada, on-premise sin VPN hacia cloud), se evalúan dos opciones:

| Opción | Cuándo usarla |
| ------------------------------- | -------------------------------------------------------------------- |
| **Gateway del destino** | El servicio destino ya expone su API a través de su propio gateway |
| **mTLS directo** | Conexión directa autenticada con certificados mutuos entre los dos perímetros |

### Tráfico de salida hacia terceros y proveedores

Flujo: **Servicio → API externa (proveedor / ERP / sistema legado)**

Para tráfico de salida existen dos opciones válidas dependiendo del contexto:

| Opción | Cuándo usarla |
| --------------------------- | ----------------------------------------------------------------------------- |
| **Egress directo** | Un único servicio consume ese tercero y gestiona sus propias credenciales |
| **Gateway como proxy de egress** | Múltiples servicios consumen el mismo tercero, o se requiere centralizar credenciales, observabilidad o abstracción del endpoint externo |

Usar el gateway como proxy de egress tiene sentido cuando:

- Varios servicios de la plataforma integran con el mismo proveedor externo (evita duplicar credenciales y configuración en cada servicio).
- Se quiere un único punto para rotar credenciales o actualizar el endpoint del tercero sin tocar código.
- Se necesita observabilidad centralizada de todas las llamadas salientes hacia integraciones externas.

:::warning El gateway de egress no reemplaza el manejo de errores del servicio
Usar el gateway como proxy de egress no exime al servicio de manejar timeouts, reintentos y circuit breaking hacia el tercero. La lógica de resiliencia sigue siendo responsabilidad del servicio.
:::

---

## Gateway Offloading — Funcionalidades transversales en el gateway

El patrón Gateway Offloading consiste en centralizar en el gateway las funcionalidades transversales que, de otro modo, cada servicio tendría que implementar por separado. Aplica a cualquier tipo de tráfico que pase por el gateway: tráfico externo entrante, egress hacia terceros, y también tráfico interno cuando se decide enrutarlo por el gateway.

Es el segundo criterio de decisión para usar el gateway: si un servicio — aunque esté dentro de la red privada — necesita que se le apliquen estas funcionalidades de forma centralizada y uniforme, exponerlo a través del gateway es la opción correcta.

Las funcionalidades que se descargan en el gateway son aquellas que:

- Son idénticas para todos los consumidores del servicio (sin variación por negocio).
- No requieren acceso a datos de dominio del servicio.
- Su duplicación en cada servicio o consumidor genera riesgo de inconsistencia.

| Funcionalidad | Sin offloading | Con offloading en gateway |
| ----------------------------- | --------------------------------------------- | ----------------------------------------------- |
| Terminación TLS | Cada servicio gestiona su certificado | Un único punto TLS; los servicios reciben HTTP interno |
| Validación de JWT | Cada servicio implementa la validación | El gateway valida una vez; el servicio solo usa los claims |
| Rate limiting | Cada servicio implementa sus propios límites | Límites centralizados por consumidor o ruta |
| Headers de traza y tenant | Cada servicio los inyecta o los pierde | El gateway los propaga de forma garantizada |
| Credenciales con terceros | Cada servicio actualiza sus propias credenciales | Se actualiza en un único lugar (egress vía gateway) |

:::tip Cuándo no aplicar offloading
Si una funcionalidad varía según la lógica de negocio del servicio — como la autorización por recurso o la validación de datos de dominio — **no** pertenece al gateway. El offloading aplica solo a funcionalidades genéricas y transversales.
:::

---

## Responsabilidades — Gateway vs Servicio

### El gateway es responsable de

| Responsabilidad                              | Cuándo aplica                              |
| -------------------------------------------- | ------------------------------------------ |
| Validación del JWT (firma y expiración)      | Tráfico norte-sur autenticado con Bearer   |
| Validación de API Keys                       | Integraciones de partners externos         |
| Rate limiting por consumidor o ruta          | Todas las rutas públicas                   |
| Terminación TLS                              | Todo tráfico entrante desde internet       |
| Enrutamiento hacia el servicio upstream      | Toda ruta registrada en el gateway         |
| Propagación de headers de traza y tenant     | Antes de llegar al servicio                |

El gateway actúa **antes** de que el request llegue al servicio. No tiene acceso a la lógica de negocio ni a la base de datos.

### El servicio es responsable de

| Responsabilidad                              | Dónde                                      |
| -------------------------------------------- | ------------------------------------------ |
| Autorización por claims del JWT              | Middleware en el servicio (política .NET)  |
| Validación de negocio de los datos entrantes | Controller / Handler                       |
| Logs de auditoría de operaciones             | Servicio → sistema de logging centralizado |
| Control de acceso a nivel de recurso         | Servicio backend                           |

:::danger El gateway no reemplaza la autorización del servicio
Que el gateway haya validado el JWT **no implica que el usuario tenga permiso para el recurso específico**. La autorización basada en roles y claims es siempre responsabilidad del servicio. No elimines las verificaciones de autorización del backend.
:::

---

## Ejemplos

```text
// ✅ CORRECTO: App móvil (consumidor externo) → Gateway → Servicio
GET https://api.talma.com/mx/gestal/postulaciones
Authorization: Bearer <jwt>

→ Gateway valida JWT del realm tlm-mx
→ Gateway enruta hacia gestal-api:8080
→ gestal-api verifica claims y devuelve resultado
```

```text
// ✅ CORRECTO: Servicio de Perú consume API de México (sin red privada compartida)
GET https://api.talma.com/mx/operaciones/vuelos
Authorization: Bearer <jwt>

→ El servicio peruano llega por internet al gateway de México
→ Gateway valida JWT y enruta al servicio destino
```

```text
// ✅ CORRECTO: Comunicación interna (misma red privada) → llamada directa
// sisbon-mx llama a notification-service dentro de la misma red
POST http://notification-service.internal/eventos
Authorization: Bearer <jwt client_credentials>

→ notification-service valida JWT localmente
→ No pasa por el gateway
```

```text
// ✅ CORRECTO: Servicio on-premise con VPN al cloud → llamada directa
// Sistema legado con VPN/peering privado al cluster cloud
POST http://inventario-api.internal/stock
Authorization: Bearer <jwt client_credentials>

→ Comparten red privada vía VPN → no requiere gateway
```

```text
// ✅ CORRECTO: Servicio consume API de proveedor externo — egress directo
// cargo-service llama al API de un proveedor de logística (único consumidor)
GET https://api.proveedor-logistica.com/envios/ABC123
Authorization: Bearer <token-del-proveedor>

→ Tráfico de salida directo desde el servicio
→ El servicio gestiona sus propias credenciales con el proveedor
```

```text
// ✅ CORRECTO: Múltiples servicios consumen el mismo tercero — egress vía gateway
// facturacion-mx, compras-mx y contabilidad-mx integran con el mismo ERP externo
GET http://gateway.internal/erp-externo/facturas/2026
Authorization: Bearer <jwt interno>

→ El gateway abstrae el endpoint real del ERP
→ Credenciales del ERP configuradas una sola vez en el gateway
→ Observabilidad centralizada de todas las llamadas al ERP
```

```text
// ❌ INCORRECTO: Servicio enrutando por el gateway para llamar a otro servicio de la misma red
POST https://api.talma.com/mx/notificaciones/eventos
Authorization: Bearer <jwt>

→ Latencia innecesaria
→ El gateway registra tráfico que es puramente interno
→ Viola el estándar de comunicación interna
```

---

## Requisitos

### MUST (Obligatorio)

- **MUST** exponer a través del API gateway todo servicio que reciba tráfico desde fuera del perímetro de red privada.
- **MUST** requerir autenticación (JWT o API Key) en el gateway para toda ruta expuesta al exterior.
- **MUST** aplicar rate limiting a todas las rutas públicas registradas en el gateway.
- **MUST** gestionar el registro de rutas y consumidores en el gateway mediante control de versiones (GitOps).

### SHOULD (Fuertemente recomendado)

- **SHOULD** propagar headers de traza (`X-Request-Id`, `X-Tenant`) desde el gateway hacia el upstream.
- **SHOULD** versionar las rutas expuestas (`/v1/`, `/v2/`) alineado con el versionado de la API.
- **SHOULD** registrar métricas del gateway en el sistema centralizado de observabilidad.
- **SHOULD** usar VPN o peering privado para interconectar redes entre países o entre on-premise y cloud, cuando sea posible, para evitar que tráfico interno transite por internet.

### MUST NOT (Prohibido)

- **MUST NOT** enrutar por el gateway llamadas entre servicios que ya comparten red privada.
- **MUST NOT** exponer servicios directamente a internet sin pasar por el gateway.
- **MUST NOT** aplicar lógica de autorización de negocio en el gateway (solo autenticación y rate limiting).
- **MUST NOT** autenticar consumidores externos con usuario y contraseña en texto plano.

---

## Referencias

- [Lineamiento de APIs y Contratos de Integración](../../lineamientos/integracion/apis-y-contratos.md) — lineamiento que origina este estándar.
- [ADR-010: Kong API Gateway](../../../adrs/adr-010-kong-api-gateway.md) — decisión de implementación y configuración operativa.
- [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md) — emisión de JWT para tráfico este-oeste.
- [Autenticación de APIs — JWT y API Keys](../seguridad/api-authentication.md) — mecanismos de autenticación en el gateway.
- [Estándares de APIs REST](./api-rest-standards.md) — diseño de contratos expuestos por el gateway.
