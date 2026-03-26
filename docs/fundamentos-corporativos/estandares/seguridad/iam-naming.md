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

Existen seis tipos de client definidos en este estándar, cada uno con configuración y patrón de nombre distintos:

| Tipo                          | Tipo Keycloak  | Flujo                | Quién lo usa                                                                 | Patrón                             |
| ----------------------------- | -------------- | -------------------- | ---------------------------------------------------------------------------- | ---------------------------------- |
| **Recurso API**               | `bearer-only`  | Ninguno              | API Gateway (valida tokens M2M entrantes)                                    | `{sistema}-api`                    |
| **Recurso API Externo**       | `bearer-only`  | Ninguno              | Integración con proveedor externo vía API Gateway                            | `{sistema}-{recurso}-api`          |
| **Consumidor M2M**            | `confidential` | `client_credentials` | Servicio llamante (obtiene tokens para llamar otras APIs)                    | `{sistema}-{scope}[-{env}]`        |
| **Consumidor M2M multi-tipo** | `confidential` | `client_credentials` | Servicio llamante con múltiples tipos de acceso o componentes independientes | `{sistema}-{tipo}-{scope}[-{env}]` |
| **Consumidor M2M B2B**        | `confidential` | `client_credentials` | Partner externo que consume una API de Talma (integración inbound)           | `ext-{partner}-{scope}[-{env}]`    |
| **Herramienta SSO**           | `confidential` | `authorization_code` | Usuario humano (login vía SSO)                                               | `{herramienta}`                    |

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

### 3. Consumidor M2M — `{sistema}-{scope}[-{env}]`

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

**Configuración Keycloak:** Access Type `confidential`, Service Accounts `YES`, Standard Flow `OFF`.

**Un solo consumidor, múltiples destinos:** El patrón base es un client por sistema con tantos **Audience Protocol Mappers** como APIs destino necesite llamar. El Audience Mapper inyecta un string en el claim `aud` del token — no referencia un realm, por lo que funciona tanto para resource servers locales (`gestal-api` en `tlm-pe`) como corporativos (`sisbon-api` en `tlm-corp`). Crear un client separado por destino solo se justifica cuando se requiera rotación o revocación de credenciales independiente por integración.

### 4. Consumidor M2M multi-tipo — `{sistema}-{tipo}-{scope}[-{env}]`

Client **confidential**. Extensión del patrón base de consumidor cuando el sistema requiere clients diferenciados dentro del mismo scope.

El valor de `{tipo}` puede expresar dos motivaciones:

- **Canal de acceso** (`app`, `mobile`, `batch`): diferentes tipos de consumidor con permisos o rate limits distintos.
- **Componente del sistema** (`procservice`, `procworker`, `scheduler`…): múltiples procesos con secretos independientes, por ejemplo para rotación o revocación aislada por componente.

| Parte       | Descripción                                                                      |
| ----------- | -------------------------------------------------------------------------------- |
| `{sistema}` | Nombre del sistema que consume, minúsculas, sin guiones internos.                |
| `{tipo}`    | Canal de acceso o identificador de componente. Minúsculas, sin guiones internos. |
| `{scope}`   | Código de scope del realm donde vive el client.                                  |
| `{env}`     | `dev` o `qa`. **Se omite en producción.**                                        |

**Ejemplos:**

```
# Por canal de acceso
gestal-app-pe            → Backend/web
gestal-mobile-pe         → App móvil
gestal-batch-pe-dev      → Proceso batch — desarrollo

# Por componente del sistema
siata-procservice-pe     → Servicio de procesamiento
siata-procworker-pe-dev  → Worker de procesamiento — desarrollo
```

Aplicar solo cuando haya 2 o más tipos o componentes con necesidades de credenciales, permisos o rate limits distintos.

**Configuración Keycloak:** Access Type `confidential`, Service Accounts `YES`, Standard Flow `OFF`.

### 5. Herramienta SSO — `{herramienta}`

Client **confidential** con **Standard Flow activo**. Representa una herramienta de plataforma que autentica usuarios humanos vía SSO (Authorization Code). Registrado en `tlm-corp`, sin scope ni env en el nombre.

**Ejemplo:** `grafana`

**Configuración Keycloak:** Access Type `confidential`, Standard Flow `ON`, Service Accounts `OFF`.

### 6. Consumidor M2M B2B — `ext-{partner}-{scope}[-{env}]`

Client **confidential**. Representa un partner externo (empresa tercera o sistema de integración B2B) que obtiene tokens via `client_credentials` para llamar APIs de Talma. El prefijo `ext-` lo diferencia de los consumidores internos y permite identificarlo en logs y en el API Gateway sin ambigüedad.

El client vive en el realm del scope de la integración — no en `tlm-corp`, aunque el recurso destino sea corporativo. Esto mantiene el aislamiento de firma por tenant y la trazabilidad por país.

| Parte       | Descripción                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------- |
| `ext-`      | Prefijo fijo. Identifica al llamante como partner externo, no un servicio interno de Talma. |
| `{partner}` | Nombre del partner o sistema externo, minúsculas, sin guiones internos (ej. `nomina360`).   |
| `{scope}`   | Código de scope del realm donde vive el client (país de la integración).                    |
| `{env}`     | `dev` o `qa`. **Se omite en producción.**                                                   |

**Ejemplo — `nomina360` integrado con Ecuador consumiendo `marcaciones-api`:**

| Client                 | Realm    | Ambiente   |
| ---------------------- | -------- | ---------- |
| `ext-nomina360-ec-dev` | `tlm-ec` | Desarrollo |
| `ext-nomina360-ec-qa`  | `tlm-ec` | QA         |
| `ext-nomina360-ec`     | `tlm-ec` | Producción |

En cada uno agregar un Audience Protocol Mapper con `Included Custom Audience: marcaciones-api`. Como `marcaciones-api` reside en `tlm-corp`, aplica el mismo mecanismo cross-realm que para consumidores internos: el claim `aud` del JWT firmado por `tlm-ec` incluirá `marcaciones-api`, que es lo que el API Gateway verifica.

**Configuración Keycloak:** Access Type `confidential`, Service Accounts `YES`, Standard Flow `OFF`.

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

Repetir las filas de consumidores por cada scope donde opere el servicio (`tlm-mx`, `tlm-pe`, etc.).

:::info Por qué los consumidores van en el realm regional, no en tlm-corp
Cada consumidor queda ligado al realm que firma sus tokens. El JWT emitido por `{sistema}-{scope}` tendrá `iss: .../realms/tlm-{scope}`, y el API Gateway valida la firma usando la clave RSA de ese realm. Si el consumidor estuviera en `tlm-corp`, el token lo firmaría `tlm-corp`, rompiendo el aislamiento de tenant por país.

Esto implica que el consumidor **no puede referenciar automáticamente** a `{sistema}-api` de `tlm-corp` como audience. La solución es agregar un **Audience Protocol Mapper** en cada consumidor con el valor literal del resource server:

```
Client: {sistema}-{scope} (tlm-{scope})
→ Mappers → Add Mapper → Tipo: Audience
   Included Custom Audience: {sistema}-api
   Add to access token: ON
```

Repetir para cada consumidor de todos los scopes (dev, qa y producción). Esto fuerza que el claim `aud` del JWT incluya `{sistema}-api`, que es lo que el API Gateway verifica.
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

Se crea un client confidential **por ambiente** para aislar credenciales. Todos usan flujo `client_credentials`; el claim `aud` que autoriza el acceso al recurso lo inyecta el Audience Protocol Mapper del consumidor.

:::note Integraciones con sistemas externos
Las credenciales de proveedores externos (API keys, client secrets de terceros) **no se almacenan en Keycloak**. Keycloak genera sus propios secrets y no permite ingresar credenciales externas. Las credenciales de terceros deben almacenarse en AWS Secrets Manager y ser consumidas directamente por el servicio. Ver [Gestión de Secretos y Claves Criptográficas](./secrets-key-management.md).
:::

### Integración B2B (partner externo consume API de Talma)

Partner externo con acceso restringido a un scope específico. El resource server puede residir en `tlm-corp` (API corporativa) o en un realm regional, pero los clients del partner siempre van en el realm del scope de la integración.

**Ejemplo: `nomina360` integrado con Ecuador consume `marcaciones-api` (corporativa)**

| Client                 | Realm      | Tipo           | Ambiente   |
| ---------------------- | ---------- | -------------- | ---------- |
| `marcaciones-api`      | `tlm-corp` | `bearer-only`  | Todos      |
| `ext-nomina360-ec-dev` | `tlm-ec`   | `confidential` | Desarrollo |
| `ext-nomina360-ec-qa`  | `tlm-ec`   | `confidential` | QA         |
| `ext-nomina360-ec`     | `tlm-ec`   | `confidential` | Producción |

Como `marcaciones-api` está en `tlm-corp` y los consumers en `tlm-ec`, se requiere Audience Protocol Mapper en cada client del partner con `Included Custom Audience: marcaciones-api`. Si el partner solo opera en un scope, no se replica la estructura a otros realms.

El secret de Keycloak de cada client se entrega al equipo del partner por canal seguro (nunca por correo ni repositorio). El secret puede rotarse de forma independiente por ambiente sin afectar a otros partners.

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

Usar cuando distintos consumidores M2M necesiten niveles de acceso diferentes sobre el mismo recurso. Los scopes viajan en el claim `scope` del JWT y son funcionales cross-realm.

Patrón: `{sistema}:{acción}` — ej. `sisbon:read`, `sisbon:write`, `sisbon:admin`.

Configuración: crear el Client Scope en el realm del consumidor → asignarlo como **Default Scope** al consumidor client. El servicio receptor verifica el claim `scope` en lugar de `resource_access`.

> Si todos los consumidores tienen acceso equivalente, el claim `aud` es suficiente — no crear scopes.

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
- [ ] En cada consumidor: agregar Audience Mapper con `Included Custom Audience: {sistema}-api`
- [ ] Registrar consumidor en `_consumers.yaml` (API Gateway)

### Servicio local nuevo

- [ ] Crear `{sistema}-api` en `tlm-{scope}` (bearer-only)
- [ ] Crear `{sistema}-{scope}-dev`, `{sistema}-{scope}-qa`, `{sistema}-{scope}`
- [ ] Si hay integración con sistema externo: registrar las credenciales del proveedor en AWS Secrets Manager y definir el service en el API Gateway (`ext-{partner}-{sistema}-{env}`)
- [ ] Registrar consumidor en `_consumers.yaml` (API Gateway)

### Partner externo nuevo (B2B inbound)

- [ ] Verificar que `{sistema}-api` existe en el realm correspondiente (bearer-only)
- [ ] Crear `ext-{partner}-{scope}-dev`, `ext-{partner}-{scope}-qa`, `ext-{partner}-{scope}` en `tlm-{scope}`
- [ ] En cada client del partner: agregar Audience Protocol Mapper con `Included Custom Audience: {sistema}-api`
- [ ] Entregar client secret al equipo del partner por canal seguro (nunca por email ni repositorio)
- [ ] Registrar el consumidor en `_consumers.yaml` (API Gateway) si el acceso es vía Gateway
- [ ] Documentar el scope de la integración (qué APIs puede llamar y desde qué scope)

---

## Resumen de Patrones

| Entidad                        | Patrón                                                                                                                              | Ejemplo prod             | Ejemplo no-prod            |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | -------------------------- |
| Realm                          | `tlm-{scope}`                                                                                                                       | `tlm-mx`                 | `tlm-mx` ¹                 |
| Recurso API (corp)             | `{sistema}-api` en `tlm-corp`                                                                                                       | `sisbon-api`             | `sisbon-api` ¹             |
| Recurso API (local)            | `{sistema}-api` en `tlm-{scope}`                                                                                                    | `gestal-api`             | `gestal-api` ¹             |
| Recurso API Externo            | `{sistema}-{recurso}-api` en `tlm-{scope}`                                                                                          | `gestal-ats-api`         | `gestal-ats-api` ¹         |
| Consumidor M2M                 | `{sistema}-{scope}[-{env}]`                                                                                                         | `gestal-pe`              | `gestal-pe-qa`             |
| Consumidor M2M multi-tipo      | `{sistema}-{tipo}-{scope}[-{env}]` — `{tipo}` puede ser canal (`app`, `mobile`, `batch`) o componente (`procservice`, `procworker`) | `gestal-mobile-pe`       | `gestal-mobile-pe-dev`     |
| Consumidor M2M B2B             | `ext-{partner}-{scope}[-{env}]` en `tlm-{scope}`                                                                                    | `ext-nomina360-ec`       | `ext-nomina360-ec-qa`      |
| Servicio externo (API Gateway) | `ext-{partner}-{sistema}-{env}`                                                                                                     | `ext-talenthub-ats-prod` | `ext-talenthub-ats-dev`    |
| Herramienta SSO                | `{herramienta}`                                                                                                                     | `grafana`                | `grafana` ¹                |
| Client role (solo SSO)         | `{acción}` bajo `{sistema}-api`                                                                                                     | `read`, `write`, `admin` | `read`, `write`, `admin` ¹ |

> ¹ El nombre no varía por ambiente — el mismo identificador se usa en dev, qa y producción.

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar `tlm-{scope}` como patrón único para nombres de realms.
- **MUST** usar `corp` para el realm de servicios y herramientas corporativas (cross-scope).
- **MUST** escribir todos los identificadores en minúsculas (realms, clients, roles, scopes).
- **MUST** usar guiones como único separador de palabras en nombres de realms y clients.
- **MUST** escribir cada segmento variable (`{sistema}`, `{tipo}`, `{recurso}`) sin guiones internos; el guion es exclusivo del separador entre segmentos (ej. `extractimpo-api`, no `extract-impo-api`).
- **MUST** usar el sufijo `-api` en todos los clients `bearer-only`.
- **MUST** incluir sufijo de ambiente (`dev` o `qa`) en todos los clients no productivos.
- **MUST** omitir el sufijo de ambiente en clients de producción.
- **MUST** registrar el `clientId` en Keycloak con el mismo valor que en `_consumers.yaml` del API Gateway.

### SHOULD (Fuertemente recomendado)

- **SHOULD** crear client roles (`read`, `write`, `admin`) bajo `{sistema}-api` solo cuando haya usuarios con niveles de acceso diferenciados (flujo SSO).
- **SHOULD** si se definen roles, usar siempre client roles bajo `{sistema}-api`, nunca realm roles.
- **SHOULD** seguir la progresión `read → write → admin` en los niveles de rol sin saltarse niveles.
- **SHOULD** usar Client Scopes `{sistema}:{acción}` para granularidad M2M cuando distintos consumidores necesiten permisos diferenciados.
- **SHOULD** usar el patrón multi-tipo (`{sistema}-{tipo}-{scope}`) solo cuando existan 2 o más tipos de consumidores con permisos o rate limits distintos, o 2 o más componentes del sistema con necesidad de secretos independientes.

### MUST NOT (Prohibido)

- **MUST NOT** usar nombres de ciudad, región o proyecto como scope de realm.
- **MUST NOT** registrar un client con un scope diferente al del realm donde reside.
- **MUST NOT** usar variaciones de scope que no estén en la tabla de valores admitidos.
- **MUST NOT** crear realms fuera del patrón `tlm-{scope}` sin ADR aprobado.
- **MUST NOT** definir roles de negocio de servicios locales en `tlm-corp`.
- **MUST NOT** crear un client separado por cada API destino; usar Audience Protocol Mappers para registrar múltiples valores en el claim `aud`.
- **MUST NOT** incluir scope ni sufijo de ambiente en el nombre de herramientas SSO (`{herramienta}`).
- **MUST NOT** crear un client B2B (`ext-{partner}`) para integraciones outbound (cuando Talma llama al partner); en ese caso las credenciales del partner se almacenan en AWS Secrets Manager.
- **MUST NOT** compartir secrets de clients B2B con otros partners ni entre ambientes; cada client tiene su propio secret rotable de forma independiente.

---

## Referencias

- [Lineamiento de Identidad y Accesos](../../lineamientos/seguridad/identidad-y-accesos.md) — lineamiento que origina este estándar.
- [ADR-001: Estrategia Multi-Tenancy](../../../adrs/adr-001-estrategia-multi-tenancy.md) — define el modelo de tenants por país/scope.
- [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md) — adopción de Keycloak como IdP centralizado.
- [SSO, MFA y RBAC](./sso-mfa-rbac.md) — estándar complementario de autenticación y control de acceso.
- [Gestión Avanzada de Identidades y Accesos](./iam-advanced.md) — service accounts, JIT access, revisiones de acceso.
- [Keycloak Documentation](https://www.keycloak.org/documentation) — referencia oficial de configuración de realms y clients.
