---
id: api-authentication
sidebar_position: 13
title: Autenticación de APIs — JWT y API Keys
description: Estándar de autenticación de APIs en Talma. JWT es el mecanismo por defecto; API Key es la excepción para consumidores externos sin identidad en Keycloak.
tags: [seguridad, jwt, api-key, autenticación, oauth2, keycloak]
---

# Autenticación de APIs — JWT y API Keys

## Contexto

Este estándar define el mecanismo de autenticación para las APIs de Talma. Complementa el [lineamiento de Identidad y Accesos](../../lineamientos/seguridad/identidad-y-accesos.md) estableciendo los criterios de selección según el tipo de consumidor.

**Decisiones arquitectónicas:** [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md) · [ADR-010: Kong API Gateway](../../../adrs/adr-010-kong-api-gateway.md)

**JWT es el mecanismo por defecto.** Todo consumidor — usuario, servicio interno o sistema externo — debe autenticarse con JWT salvo que exista una razón explícita y documentada que lo impida. El API Key es la excepción, no una alternativa a elección libre.

La distinción fundamental es una sola: **¿la identidad del llamante importa para el servicio receptor?**

- **JWT** → la identidad está firmada y verificada. Habilita RBAC, trazabilidad por usuario/tenant y propagación de contexto entre servicios. Es obligatorio cuando la identidad importa — y en la práctica la identidad casi siempre importa.
- **API Key** → solo acredita que el llamante tiene acceso permitido. No transporta identidad. Válido únicamente cuando el consumidor no puede participar en el flujo OAuth2 y la identidad es genuinamente irrelevante.

---

## Stack Tecnológico

| Componente            | Tecnología | Versión | Uso                                            |
| --------------------- | ---------- | ------- | ---------------------------------------------- |
| **Identity Provider** | Keycloak   | 26.4.4+ | Emisión de JWT (OAuth2 / OIDC)                 |
| **API Gateway**       | Kong       | —       | Validación de JWT y API Keys en capa de acceso |
| **Runtime**           | .NET       | 8.0+    | Validación de JWT en servicios internos        |

---

## Modelo de Decisión — JWT vs API Key

## JWT — Mecanismo por defecto

JWT es obligatorio para cualquier consumidor que pueda obtener un token de Keycloak. No es una opción entre varias: es el estándar de la plataforma.

Usar JWT cuando el consumidor es un servicio interno **no es opcional**. Aunque el servicio destino no aplique RBAC en ese endpoint, el JWT garantiza trazabilidad de origen, contexto de tenant y la posibilidad de agregar controles sin cambiar el mecanismo de autenticación en el futuro.

JWT es necesario cuando:

- El servicio aplica RBAC (los permisos dependen de los claims del token).
- Se requiere trazabilidad de operaciones por usuario o por servicio origen.
- La llamada opera en contexto de un tenant específico (`X-Tenant` o claim del JWT).
- El consumidor es un servicio interno de Talma (la identidad del servicio origen siempre importa).

| Escenario | Flujo OAuth2 | Ejemplo |
| ----------------------------------- | ------------------ | -------------------------------------- |
| Usuario autenticado → API | Authorization Code | App web/móvil con sesión SSO |
| Servicio Talma → API Talma (M2M) | Client Credentials | `sisbon-mx` llama a API de SISBON |
| Sistema externo con client Keycloak | Client Credentials | `gestal-ext-ats` llama a API de Gestal |

El consumidor obtiene un access token de Keycloak y lo envía en cada request: `Authorization: Bearer <jwt>`. El receptor valida la firma y lee los claims sin llamar a Keycloak.

## API Key — Excepción para consumidores sin identidad OAuth2

El API Key solo es válido cuando el consumidor **no puede** participar en el flujo OAuth2 y la identidad es genuinamente irrelevante para el servicio receptor. No es una alternativa más simple a JWT ni una opción para evitar la configuración de un client en Keycloak.

:::warning Antes de usar API Key, verifica que aplica
Si el consumidor puede obtener un client en Keycloak, **debe** usar JWT. Usar API Key para evitar la complejidad de configurar OAuth2 no es una justificación válida.
:::

API Key es válida únicamente cuando:

- El consumidor es un sistema externo de terceros sin client provisionado en Keycloak.
- Es un acceso de solo lectura donde lo único que importa es el nivel de acceso, no quién accede.
- Son scripts, pipelines de CI/CD o herramientas internas que no operan en contexto de un usuario o servicio con identidad relevante.
- El proveedor externo envía webhooks donde no hay flujo interactivo de autenticación posible.

| Escenario | Ejemplo |
| --------------------------------------------- | ----------------------------------------------------- |
| Partner externo integrado por el gateway | TalentHub ATS llamando a endpoints expuestos |
| Webhook entrante de proveedor externo | Notificación de pago de Stripe hacia endpoint Talma |
| Acceso a sandbox / entorno desarrollo externo | Partner probando integración antes de producción |
| Script o pipeline sin contexto de usuario | Job de sincronización con sistema legado externo |

El API Key se envía en cada request vía header: `X-Api-Key: <key>`. No tiene expiración automática — la rotación es responsabilidad del equipo de plataforma en coordinación con el consumidor.

---

## Mecanismos Prohibidos

Los siguientes mecanismos **no deben usarse** en ninguna circunstancia. Son vulnerabilidades conocidas o incompatibles con el modelo de seguridad de la plataforma.

| Mecanismo                                                        | Razón                                                               |
| ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| **HTTP Basic Auth**                                              | Credenciales en cada request; no soporta expiración ni revocación   |
| **Token sin expiración (`exp`)**                                 | No revocable en caso de compromiso                                  |
| **API Key en query string**                                      | Queda registrada en logs de acceso y proxies intermedios            |
| **Credenciales hardcodeadas**                                    | Rotación imposible; exposición en repositorios                      |
| **JWT firmado con secret simétrico (HS256) en integración Kong** | Kong usa clave RSA (RS256) por realm; HS256 no aplica en este stack |

:::warning API Keys no reemplazan JWT en servicios internos
Usar API Keys entre servicios Talma (en lugar de JWT) elimina el contexto de identidad del token, impide la trazabilidad por usuario/tenant y viola el principio de mínimo privilegio. Todo servicio interno debe usar JWT con `client_credentials`.
:::

---

## Ejemplo Comparativo

```text
// ❌ MAL: Servicio interno usando API Key entre microservicios
GET /api/sisbon/operaciones
X-Api-Key: abc123

// ✅ BIEN: Servicio interno usando JWT con client_credentials
POST /realms/tlm-mx/protocol/openid-connect/token
  client_id: sisbon-mx
  client_secret: <secret>
  grant_type: client_credentials

→ access_token: eyJhbGciOiJSUzI1NiJ9...

GET /api/sisbon/operaciones
Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...
```

```text
// ❌ MAL: Partner externo usando JWT cuando no tiene client Keycloak
// → No hay realm, no hay client, no hay forma de emitir el token

// ✅ BIEN: Partner externo usando API Key provisionada por Kong
GET /api/gestal/ats/postulaciones
X-Api-Key: <api-key-del-partner>
```

---

## Matriz de Selección Rápida

| Tipo de consumidor                       | Tiene client en Keycloak | Mecanismo                                   |
| ---------------------------------------- | ------------------------ | ------------------------------------------- |
| Usuario humano (SSO)                     | Sí                       | JWT (Authorization Code)                    |
| Servicio interno Talma (M2M)             | Sí                       | JWT (Client Credentials)                    |
| Sistema externo con client aprovisionado | Sí                       | JWT (Client Credentials)                    |
| Partner externo sin client Keycloak      | No                       | API Key                                     |
| Webhook entrante de tercero              | No                       | API Key + HMAC (si el proveedor lo soporta) |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar JWT para toda comunicación entre servicios internos de Talma.
- **MUST** usar el flujo `client_credentials` para autenticación M2M (servicio → servicio).
- **MUST** enviar tokens JWT en el header `Authorization: Bearer <token>`.
- **MUST** enviar API Keys en el header `X-Api-Key`, nunca en query strings.
- **MUST** usar tokens con claim `exp` (expiración definida).
- **MUST** validar la firma del JWT con la clave pública RSA del realm en el punto de entrada (gateway o servicio).

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar `client_credentials` con `service_account` scope para procesos batch y workers.
- **SHOULD** rotar API Keys de partners cada 12 meses o ante sospecha de compromiso.
- **SHOULD** registrar y auditar el uso de API Keys por partner en Kong.

### MUST NOT (Prohibido)

- **MUST NOT** usar HTTP Basic Auth en ningún servicio o integración.
- **MUST NOT** emitir tokens sin expiración (`exp`).
- **MUST NOT** incluir API Keys en URLs (query string, path).
- **MUST NOT** usar API Keys para comunicación entre servicios internos de Talma.
- **MUST NOT** hardcodear credenciales (client secrets, API keys) en código fuente o imágenes.

---

## Referencias

- [Lineamiento de Identidad y Accesos](../../lineamientos/seguridad/identidad-y-accesos.md) — lineamiento que origina este estándar.
- [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md) — adopción de Keycloak y OAuth2/OIDC como estándar de autenticación.
- [ADR-010: Kong API Gateway](../../../adrs/adr-010-kong-api-gateway.md) — Kong como punto de validación de autenticación.
- [Nomenclatura de Recursos en Keycloak](./keycloak-resource-naming.md) — naming de clients y roles.
- [SSO, MFA y RBAC](./sso-mfa-rbac.md) — configuración de autenticación en servicios .NET.
- [Gestión de Secretos y Claves Criptográficas](./secrets-key-management.md) — almacenamiento de client secrets y API keys.
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749) — especificación del protocolo.
