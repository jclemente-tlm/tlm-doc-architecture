---
id: iam-naming
sidebar_position: 12
title: Nomenclatura de Recursos IAM
description: Estándar de nomenclatura para realms, clients, roles y scopes del IdP (Keycloak) en Talma multitenancy.
tags: [seguridad, keycloak, naming, tenants, multitenancy, iam]
---

# Nomenclatura de Recursos IAM

## Contexto

Este estándar define la nomenclatura obligatoria para realms, clients, roles y scopes en Keycloak. Complementa el [lineamiento de Identidad y Accesos](../../lineamientos/seguridad/identidad-y-accesos.md) asegurando consistencia entre el IdP, el API Gateway y los servicios de la plataforma.

**Decisiones arquitectónicas:** [ADR-001: Estrategia Multi-Tenancy](../../../adrs/adr-001-estrategia-multi-tenancy.md) · [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md)

Cada **tenant** es un realm de Keycloak que agrupa usuarios, clients, roles y configuración de un ámbito operativo (país o corporativo). Una nomenclatura consistente permite:

- Identificar origen, servicio y ambiente desde el nombre del recurso, sin consultar la consola.
- Configurar el API Gateway (`_consumers.yaml`) y variables de entorno sin ambigüedad.
- Automatizar el aprovisionamiento de realm JSONs en `tlm-infra-keycloak`.

:::note Gestión a cargo de Identidad y Accesos
Solo el equipo de **Identidad y Accesos** puede registrar nuevos realms o clients. Los nombres deben seguir este estándar antes de ser agregados al repositorio `tlm-infra-keycloak`.
:::

---

## Stack Tecnológico

| Componente            | Tecnología | Versión | Uso                                             |
| --------------------- | ---------- | ------- | ----------------------------------------------- |
| **Identity Provider** | Keycloak   | 26.4.4+ | Realms, clients, roles, sesiones, token signing |
| **API Gateway**       | Kong       | —       | Validación JWT con clave RSA embebida por realm |

---

## Naming de Realms (Tenants)

### Patrón

```
tlm-{scope}
```

| Parte     | Descripción                                                            |
| --------- | ---------------------------------------------------------------------- |
| `tlm-`    | Prefijo fijo. Identifica el contexto Talma.                            |
| `{scope}` | Código de país ISO 3166-1 alpha-2, o identificador funcional (`corp`). |

### Valores de scope admitidos

| Scope  | Realm      | Estado                                         |
| ------ | ---------- | ---------------------------------------------- |
| `corp` | `tlm-corp` | Activo — servicios y herramientas corporativas |
| `mx`   | `tlm-mx`   | Activo — operación México                      |
| `pe`   | `tlm-pe`   | Activo — operación Perú                        |
| `ec`   | `tlm-ec`   | Pendiente — operación Ecuador                  |
| `co`   | `tlm-co`   | Pendiente — operación Colombia                 |

---

## Naming de Clients

Existen tres roles de client en Keycloak, con configuraciones distintas:

| Rol                     | Tipo Keycloak  | Flujo                | Quién lo usa                                      | Patrón                    |
| ----------------------- | -------------- | -------------------- | ------------------------------------------------- | ------------------------- |
| **Recurso API**         | `bearer-only`  | Ninguno              | API Gateway (valida tokens M2M entrantes)         | `{sistema}-api`           |
| **Recurso API Externo** | `bearer-only`  | Ninguno              | Integración con proveedor externo vía API Gateway | `{sistema}-{recurso}-api` |
| **Consumidor M2M**      | `confidential` | `client_credentials` | Servicio (obtiene tokens para llamar otras APIs)  | `{sistema}-{scope}`       |
| **Herramienta SSO**     | `confidential` | `authorization_code` | Usuario humano (login vía SSO)                    | `{herramienta}`           |

Un backend puede tener simultáneamente un client **Recurso API** y un client **Consumidor M2M**: el primero define la audiencia para tokens que recibe, el segundo le permite obtener tokens para llamar a otras APIs.

### 1. Recurso API — `{sistema}-api`

Client **bearer-only**. Representa el servicio **como recurso** (no como llamante). Su `clientId` es el valor esperado en el claim `aud` del JWT. Cuando el API Gateway valida un token entrante, verifica que `aud` contenga este valor. No obtiene tokens ni autentica llamantes.

Opcionalmente, se pueden definir **client roles** bajo este client para controlar niveles de acceso en tokens de **usuario** (flujo SSO). Para llamadas M2M (`client_credentials`), el claim `aud` es suficiente — no se usan roles en ese flujo.

| Parte       | Descripción                                                                    |
| ----------- | ------------------------------------------------------------------------------ |
| `{sistema}` | Nombre del servicio **que expone** el API, minúsculas, sin guiones internos.   |
| `-api`      | Sufijo fijo. Identifica el client como recurso (resource server), no llamante. |

**Ejemplos:** `sisbon-api` en `tlm-corp` · `gestal-api` en `tlm-pe`

**Configuración Keycloak:** Access Type `bearer-only`, Standard Flow `OFF`, Service Accounts `OFF`.

### 2. Recurso API Externo — `{sistema}-{recurso}-api`

Client **bearer-only**. Representa una integración con un proveedor externo abstraído por el API Gateway. Se registra en el mismo realm que el sistema consumidor (`tlm-{scope}`). El nombre identifica la integración desde el dominio del sistema interno — el proveedor real se configura en `_services.yaml` del API Gateway y es transparente para Keycloak. Si el proveedor cambia, el client de Keycloak no cambia.

| Parte       | Descripción                                                                            |
| ----------- | -------------------------------------------------------------------------------------- |
| `{sistema}` | Nombre del sistema **que consume** la integración, minúsculas, sin guiones internos.   |
| `{recurso}` | Nombre del recurso o capacidad integrada, desde el dominio interno (ej. `ats`, `erp`). |
| `-api`      | Sufijo fijo. Identifica el client como recurso (resource server), no llamante.         |

**Ejemplo:** `gestal-ats-api` en `tlm-pe`

**Configuración Keycloak:** Access Type `bearer-only`, Standard Flow `OFF`, Service Accounts `OFF`.

### 3. Consumidor — `{sistema}-{scope}[-{env}]`

Client **confidential**. Representa el servicio **como llamante**: obtiene tokens via `client_credentials` para autenticarse ante otras APIs internas. Reside en el realm del scope del consumidor: un servicio regional va en `tlm-{scope}` (país), un servicio corporativo va en `tlm-corp`.

| Parte       | Descripción                                                                         |
| ----------- | ----------------------------------------------------------------------------------- |
| `{sistema}` | Nombre del sistema **que consume** (el llamante), minúsculas, sin guiones internos. |
| `{scope}`   | Código de scope del realm donde vive el client.                                     |
| `{env}`     | `dev` o `qa`. **Se omite en producción.**                                           |

**Ejemplos:**

| Client          | Realm    | Ambiente   |
| --------------- | -------- | ---------- |
| `sisbon-mx-dev` | `tlm-mx` | Desarrollo |
| `sisbon-mx-qa`  | `tlm-mx` | QA         |
| `sisbon-mx`     | `tlm-mx` | Producción |
| `gestal-pe-dev` | `tlm-pe` | Desarrollo |
| `gestal-pe-qa`  | `tlm-pe` | QA         |
| `gestal-pe`     | `tlm-pe` | Producción |

**Evolución opcional — multi-tipo:** Si el servicio necesita clients diferenciados por tipo de consumidor (web, móvil, batch), el patrón se extiende a `{sistema}-{tipo}-{scope}[-{env}]`:

```
# Producción (sin sufijo de ambiente)
gestal-app-pe            → Backend/web
gestal-mobile-pe         → App móvil
gestal-batch-pe          → Proceso batch

# No productivo (con sufijo)
gestal-app-pe-dev        → Backend/web — desarrollo
gestal-mobile-pe-qa      → App móvil — QA
gestal-batch-pe-dev      → Proceso batch — desarrollo
```

Aplicar solo cuando haya 2 o más tipos con permisos o rate limits distintos.

**Configuración Keycloak:** Access Type `confidential`, Service Accounts `YES`, Standard Flow `OFF`.

### 4. Herramienta SSO — `{herramienta}`

Client **confidential** con **Standard Flow activo**. Representa una herramienta de plataforma que autentica usuarios humanos vía SSO (Authorization Code). Registrado en `tlm-corp`, sin scope ni env en el nombre.

**Ejemplo:** `grafana`

**Configuración Keycloak:** Access Type `confidential`, Standard Flow `ON`, Service Accounts `OFF`.

:::warning Coherencia Gateway ↔ Keycloak
El `clientId` en Keycloak debe coincidir exactamente con el identificador definido en `_consumers.yaml` del repositorio `tlm-infra-api-gateway`. Una discrepancia impide la validación de tokens en el API Gateway.
:::

---

## Estructura por Tipo de Servicio

### Servicio corporativo (multi-scope)

| Client                  | Realm         | Tipo           | Ambiente   | Ejemplo         |
| ----------------------- | ------------- | -------------- | ---------- | --------------- |
| `{sistema}-api`         | `tlm-corp`    | `bearer-only`  | Todos      | `sisbon-api`    |
| `{sistema}-{scope}-dev` | `tlm-{scope}` | `confidential` | Desarrollo | `sisbon-mx-dev` |
| `{sistema}-{scope}-qa`  | `tlm-{scope}` | `confidential` | QA         | `sisbon-mx-qa`  |
| `{sistema}-{scope}`     | `tlm-{scope}` | `confidential` | Producción | `sisbon-mx`     |

Repetir las filas de consumers por cada scope donde opere el servicio (`tlm-mx`, `tlm-pe`, etc.).

:::info Por qué los consumers van en el realm regional, no en tlm-corp
Cada consumer queda ligado al realm que firma sus tokens. El JWT emitido por `{sistema}-{scope}` tendrá `iss: .../realms/tlm-{scope}`, y el API Gateway valida la firma usando la clave RSA de ese realm. Si el consumer estuviera en `tlm-corp`, el token lo firmaría `tlm-corp`, rompiendo el aislamiento de tenant por país.

Esto implica que el consumer **no puede referenciar automáticamente** a `{sistema}-api` de `tlm-corp` como audience. La solución es agregar un **Audience Protocol Mapper** en cada consumer con el valor literal del resource server:

```
Client: {sistema}-{scope} (tlm-{scope})
→ Mappers → Add Mapper → Tipo: Audience
   Included Custom Audience: {sistema}-api
   Add to access token: ON
```

Repetir para cada consumer de todos los scopes (dev, qa y producción). Esto fuerza que el claim `aud` del JWT incluya `{sistema}-api`, que es lo que el API Gateway verifica.
:::

### Servicio local (scope único)

Un servicio local puede exponer su propio API y además consumir servicios externos abstraídos por el API Gateway. En ese caso requiere un bearer-only por cada recurso protegido:

| Client                    | Realm         | Tipo           | Ambiente   | Ejemplo          |
| ------------------------- | ------------- | -------------- | ---------- | ---------------- |
| `{sistema}-api`           | `tlm-{scope}` | `bearer-only`  | Todos      | `gestal-api`     |
| `{sistema}-{recurso}-api` | `tlm-{scope}` | `bearer-only`  | Todos      | `gestal-ats-api` |
| `{sistema}-{scope}-dev`   | `tlm-{scope}` | `confidential` | Desarrollo | `gestal-pe-dev`  |
| `{sistema}-{scope}-qa`    | `tlm-{scope}` | `confidential` | QA         | `gestal-pe-qa`   |
| `{sistema}-{scope}`       | `tlm-{scope}` | `confidential` | Producción | `gestal-pe`      |

Se crea un client confidential **por ambiente** para aislar credenciales. Todos usan flujo `client_credentials`; el claim `aud` que autoriza el acceso al recurso lo inyecta el Audience Protocol Mapper del consumer.

:::note Integraciones con sistemas externos
Las credenciales de proveedores externos (API keys, client secrets de terceros) **no se almacenan en Keycloak**. Keycloak genera sus propios secrets y no permite ingresar credenciales externas. Las credenciales de terceros deben almacenarse en AWS Secrets Manager y ser consumidas directamente por el servicio. Ver [Gestión de Secretos y Claves Criptográficas](./secrets-key-management.md).
:::

---

## Naming de Roles de Acceso

Solo para tokens de **usuario** (flujo SSO). En M2M el claim `aud` es suficiente; si se necesita granularidad M2M, ver [Client Scopes para M2M](#client-scopes-para-autorización-m2m). Crear roles solo con caso de uso real.

Se definen como **client roles** bajo `{sistema}-api`; al estar scoped al client, no requieren prefijo de sistema.

### Valores estándar

| Rol     | Descripción                                          |
| ------- | ---------------------------------------------------- |
| `read`  | Consulta de datos, sin modificaciones.               |
| `write` | Creación y actualización de datos.                   |
| `admin` | Acceso completo, incluyendo configuración y borrado. |

**Ejemplos:** rol `read` bajo `sisbon-api`, rol `admin` bajo `gestal-api`.

### Cómo aparecen en el JWT de usuario

```json
"resource_access": {
  "gestal-api": {
    "roles": ["read", "write"]
  }
}
```

El servicio verifica `resource_access["{sistema}-api"].roles`. Asignación: **Users** → usuario → **Role Mappings** → Client Roles → `{sistema}-api`.

---

## Naming de Client Scopes (custom)

### Client Scopes para autorización M2M

Usar cuando distintos consumers M2M necesiten niveles de acceso diferentes sobre el mismo recurso. Los scopes viajan en el claim `scope` del JWT y son funcionales cross-realm.

Patrón: `{sistema}:{acción}` — ej. `sisbon:read`, `sisbon:write`, `sisbon:admin`.

Configuración: crear el Client Scope en el realm del consumer → asignarlo como **Default Scope** al consumer client. El servicio receptor verifica el claim `scope` en lugar de `resource_access`.

> Si todos los consumers tienen acceso equivalente, el claim `aud` es suficiente — no crear scopes.

### Client Scopes transversales de plataforma

Scopes sin prefijo de servicio, disponibles en todos los realms:

| Scope             | Uso                                          |
| ----------------- | -------------------------------------------- |
| `service_account` | Clients con flujo `client_credentials` (M2M) |
| `organization`    | Claims de organización/tenant en el token    |

---

## Naming de Servicios Externos en el API Gateway

Los servicios de terceros **expuestos vía el API Gateway** (actúa como proxy hacia un proveedor externo) usan el siguiente patrón en la configuración del API Gateway. Este naming vive en `_services.yaml` y no tiene contraparte en Keycloak — las credenciales del proveedor se almacenan en AWS Secrets Manager, no en Keycloak.

```
ext-{partner}-{sistema}-{env}
```

**Ejemplo:** `ext-talenthub-ats-dev` — el API Gateway routea `/api-dev/gestal/ats` hacia la API de TalentHub.

---

## Checklist de Creación

### Servicio corporativo nuevo

- [ ] Crear realm `tlm-{scope}` si no existe
- [ ] Crear `{sistema}-api` en `tlm-corp` (bearer-only)
- [ ] Por cada scope: crear `{sistema}-{scope}-dev`, `{sistema}-{scope}-qa`, `{sistema}-{scope}`
- [ ] En cada consumer: agregar Audience Mapper con `Included Custom Audience: {sistema}-api`
- [ ] Registrar consumer en `_consumers.yaml` (API Gateway)

### Servicio local nuevo

- [ ] Crear `{sistema}-api` en `tlm-{scope}` (bearer-only)
- [ ] Crear `{sistema}-{scope}-dev`, `{sistema}-{scope}-qa`, `{sistema}-{scope}`
- [ ] Si hay integración con sistema externo: registrar las credenciales del proveedor en AWS Secrets Manager y definir el service en el API Gateway (`ext-{partner}-{sistema}-{env}`)
- [ ] Registrar consumer en `_consumers.yaml` (API Gateway)

---

## Resumen de Patrones

| Entidad                         | Patrón                                             | Ejemplo prod             | Ejemplo no-prod            |
| ------------------------------- | -------------------------------------------------- | ------------------------ | -------------------------- |
| Realm                           | `tlm-{scope}`                                      | `tlm-mx`                 | `tlm-mx` ¹                 |
| Validador API (corp)            | `{sistema}-api` en `tlm-corp`                      | `sisbon-api`             | `sisbon-api` ¹             |
| Validador API (local)           | `{sistema}-api` en `tlm-{scope}`                   | `gestal-api`             | `gestal-api` ¹             |
| Validador API (integración ext) | `{sistema}-{recurso}-api` en `tlm-{scope}`         | `gestal-ats-api`         | `gestal-ats-api` ¹         |
| Consumidor                      | `{sistema}-{scope}[-{env}]`                        | `gestal-pe`              | `gestal-pe-qa`             |
| Consumidor multi-tipo           | `{sistema}-{tipo}-{scope}[-{env}]`                 | `gestal-mobile-pe`       | `gestal-mobile-pe-dev`     |
| Servicio externo (API Gateway)  | `ext-{partner}-{sistema}-{env}`                    | `ext-talenthub-ats-prod` | `ext-talenthub-ats-dev`    |
| Herramienta SSO                 | `{herramienta}` — `confidential`, Standard Flow ON | `grafana`                | `grafana` ¹                |
| Client role (solo SSO)          | `{acción}` bajo `{sistema}-api`                    | `read`, `write`, `admin` | `read`, `write`, `admin` ¹ |

> ¹ El nombre no varía por ambiente — el mismo identificador se usa en dev, qa y producción.

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar `tlm-{scope}` como patrón único para nombres de realms.
- **MUST** usar `corp` para el realm de servicios y herramientas corporativas (cross-scope).
- **MUST** escribir todos los identificadores en minúsculas (realms, clients, roles, scopes).
- **MUST** usar guiones como único separador de palabras en nombres de realms y clients.
- **MUST** incluir sufijo de ambiente (`dev` o `qa`) en todos los clients no productivos.
- **MUST** omitir el sufijo de ambiente en clients de producción.
- **MUST** registrar el `clientId` en Keycloak con el mismo valor que en `_consumers.yaml` del API Gateway.

### SHOULD (Fuertemente recomendado)

- **SHOULD** crear client roles (`read`, `write`, `admin`) bajo `{sistema}-api` solo cuando haya usuarios con niveles de acceso diferenciados (flujo SSO).
- **SHOULD** si se definen roles, usar siempre client roles bajo `{sistema}-api`, nunca realm roles.
- **SHOULD** seguir la progresión `read → write → admin` en los niveles de rol sin saltarse niveles.
- **SHOULD** usar Client Scopes `{sistema}:{acción}` para granularidad M2M cuando distintos consumers necesiten permisos diferenciados.
- **SHOULD** usar el patrón multi-tipo (`{sistema}-{tipo}-{scope}`) solo cuando existan 2 o más tipos de consumidores con permisos o rate limits distintos.

### MUST NOT (Prohibido)

- **MUST NOT** usar nombres de ciudad, región o proyecto como scope de realm.
- **MUST NOT** registrar un client con un scope diferente al del realm donde reside.
- **MUST NOT** usar variaciones de scope que no estén en la tabla de valores admitidos.
- **MUST NOT** crear realms fuera del patrón `tlm-{scope}` sin ADR aprobado.
- **MUST NOT** definir roles de negocio de servicios locales en `tlm-corp`.

---

## Referencias

- [Lineamiento de Identidad y Accesos](../../lineamientos/seguridad/identidad-y-accesos.md) — lineamiento que origina este estándar.
- [ADR-001: Estrategia Multi-Tenancy](../../../adrs/adr-001-estrategia-multi-tenancy.md) — define el modelo de tenants por país/scope.
- [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md) — adopción de Keycloak como IdP centralizado.
- [SSO, MFA y RBAC](./sso-mfa-rbac.md) — estándar complementario de autenticación y control de acceso.
- [Gestión Avanzada de Identidades y Accesos](./iam-advanced.md) — service accounts, JIT access, revisiones de acceso.
- [Keycloak Documentation](https://www.keycloak.org/documentation) — referencia oficial de configuración de realms y clients.
