---
id: api-authentication
sidebar_position: 13
title: Autenticación de APIs — JWT y API Keys
description: Estándar de selección entre JWT y API Keys para autenticación de APIs en Talma. Define cuándo usar cada mecanismo y las prohibiciones aplicables.
tags: [seguridad, jwt, api-key, autenticación, oauth2, keycloak, kong]
---

# Autenticación de APIs — JWT y API Keys

## Contexto

Este estándar define cuándo usar JWT y cuándo usar API Keys para autenticar llamadas a las APIs de Talma. Complementa el [lineamiento de Identidad y Accesos](../../lineamientos/seguridad/identidad-y-accesos.md) estableciendo los criterios de selección de mecanismo según el tipo de consumidor.

**Decisiones arquitectónicas:** [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md) · [ADR-010: Kong API Gateway](../../../adrs/adr-010-kong-api-gateway.md)

JWT y API Keys son **complementarios**, no alternativos. Cada uno resuelve un problema diferente:

- **JWT** → transporta identidad verificada + permisos. El receptor sabe _quién_ hace la llamada.
- **API Key** → valida acceso de un cliente conocido. No transporta identidad de usuario.

---

## Stack Tecnológico

| Componente            | Tecnología | Versión | Uso                                            |
| --------------------- | ---------- | ------- | ---------------------------------------------- |
| **Identity Provider** | Keycloak   | 26.4.4+ | Emisión de JWT (OAuth2 / OIDC)                 |
| **API Gateway**       | Kong       | —       | Validación de JWT y API Keys en capa de acceso |
| **Runtime**           | .NET       | 8.0+    | Validación de JWT en servicios internos        |

---

## Modelo de Decisión — JWT vs API Key

### Usa JWT cuando

El consumidor tiene una **identidad conocida en Keycloak**: es un usuario humano, un servicio interno de Talma, o un sistema externo al que Talma le ha provisionado un client.

| Escenario                           | Flujo OAuth2       | Ejemplo                                |
| ----------------------------------- | ------------------ | -------------------------------------- |
| Usuario autenticado → API           | Authorization Code | App web/móvil con sesión SSO           |
| Servicio Talma → API Talma (M2M)    | Client Credentials | `sisbon-mx` llama a API de SISBON      |
| Sistema externo con client Keycloak | Client Credentials | `gestal-ext-ats` llama a API de Gestal |

**Ciclo de vida del token:**

1. El consumidor autentica contra Keycloak y obtiene un access token (JWT, vigencia 300s).
2. Envía el token en cada request: `Authorization: Bearer <jwt>`.
3. Kong valida la firma con la clave pública RSA del realm correspondiente.
4. Si el token expira, el consumidor solicita uno nuevo.

### Usa API Key cuando

El consumidor es un **sistema externo de terceros** que no tiene ni tendrá un client en Keycloak, o cuando se necesita acceso programático simple sin contexto de identidad de usuario.

| Escenario                                     | Ejemplo                                               |
| --------------------------------------------- | ----------------------------------------------------- |
| Partner externo integrado por Kong            | TalentHub ATS llamando a endpoints expuestos por Kong |
| Webhook entrante de proveedor externo         | Notificación de pago de Stripe hacia endpoint Talma   |
| Acceso a sandbox / entorno desarrollo externo | Partner probando integración antes de producción      |

**Ciclo de vida del API Key:**

1. El equipo de Identidad genera la API Key y la entrega al socio de forma segura (AWS Secrets Manager).
2. El socio la envía en cada request vía header: `X-Api-Key: <key>`.
3. Kong valida la key contra su registro de consumidores.
4. La rotación se gestiona coordinadamente con el socio externo.

---

## Mecanismos Prohibidos

| Mecanismo                                                        | Razón                                                               |
| ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| **HTTP Basic Auth**                                              | Credenciales en cada request; no soporta expiración ni revocación   |
| **Token sin expiración (`exp`)**                                 | No revocable en caso de compromiso                                  |
| **API Key en query string**                                      | Queda registrada en logs de acceso y proxies intermedios            |
| **Credenciales hardcodeadas**                                    | Rotación imposible; exposición en repositorios                      |
| **JWT firmado con secret simétrico (HS256) en integración Kong** | Kong usa clave RSA (RS256) por realm; HS256 no aplica en este stack |

:::warning API Keys no reemplazan JWT en servicios internos
Usar API Keys entre servicios Talma (en lugar de JWT) elimina el contexto de identidad del token, impide la trazabilidad por usuario/tenant y viola el principio de mínimo privilegio. Todo servicio interno **MUST** usar JWT con `client_credentials`.
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
- **MUST** configurar la validación de JWT en Kong con la clave pública RSA del realm.

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
