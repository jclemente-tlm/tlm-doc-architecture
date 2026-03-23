---
id: keycloak-resource-naming
sidebar_position: 12
title: Nomenclatura de Recursos en Keycloak
description: Estándar de nomenclatura para realms, clients, roles y scopes en Keycloak multitenancy Talma.
tags: [seguridad, keycloak, naming, tenants, multitenancy, iam]
---

# Nomenclatura de Recursos en Keycloak

## Contexto

Este estándar define la nomenclatura obligatoria para realms, clients, roles y scopes en Keycloak. Complementa el [lineamiento de Identidad y Accesos](../../lineamientos/seguridad/identidad-y-accesos.md) asegurando consistencia entre el IdP, el API Gateway y los servicios de la plataforma.

**Decisiones arquitectónicas:** [ADR-001: Estrategia Multi-Tenancy](../../../adrs/adr-001-estrategia-multi-tenancy.md) · [ADR-003: Keycloak SSO Autenticación](../../../adrs/adr-003-keycloak-sso-autenticacion.md)

Cada **tenant** es un realm de Keycloak que agrupa usuarios, clients, roles y configuración de un ámbito operativo (país o corporativo). Una nomenclatura consistente permite:

- Identificar origen, servicio y ambiente desde el nombre del recurso, sin consultar la consola.
- Configurar el API Gateway (`_consumers.yaml`) y variables de entorno sin ambigüedad.
- Automatizar el aprovisionamiento de realm JSONs vía `_gen_prod_realms.py`.

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

| Rol | Tipo Keycloak | Flujo | Quién lo usa | Patrón |
| --- | ------------- | ----- | ------------ | ------ |
| **Recurso API** | `bearer-only` | Ninguno | Kong (valida tokens M2M entrantes) | `{sistema}-api` |
| **Consumidor M2M** | `confidential` | `client_credentials` | Servicio (obtiene tokens para llamar otras APIs) | `{sistema}-{scope}` |
| **Herramienta SSO** | `confidential` | `authorization_code` | Usuario humano (login vía SSO) | `{herramienta}` |

Un backend puede tener simultáneamente un client **Recurso API** y un client **Consumidor M2M**: el primero define la audiencia para tokens que recibe, el segundo le permite obtener tokens para llamar a otras APIs.

> `sisbon-api` y `gestal-pe` en el mismo realm no son lo mismo: `-api` es el resource server (su `clientId` va en el claim `aud` y aloja los client roles); sin `-api` es el caller M2M (obtiene tokens). El servicio .NET verifica `resource_access["gestal-api"].roles`; el consumer que llama a esa API necesita tener esos client roles asignados.

### 1. Recurso API — `{sistema}-api`

Client **bearer-only**. Representa el servicio **como recurso** (no como llamante). Su `clientId` es el valor esperado en el claim `aud` del JWT. Cuando Kong valida un token entrante, verifica que `aud` contenga este valor. No obtiene tokens ni autentica llamantes.

Los roles de acceso (`read`, `write`, `admin`) se definen como **client roles** bajo este client. Keycloak los incluye en `resource_access.{clientId}.roles` del JWT cuando el consumer tiene esos roles asignados. Esto los aisla completamente de los roles de otros sistemas en el mismo realm.

| Tipo de servicio          | Realm donde se registra | Ejemplo                  |
| ------------------------- | ----------------------- | ------------------------ |
| Corporativo (multi-scope) | `tlm-corp`              | `sisbon-api`             |
| Local (scope único)       | `tlm-{scope}`           | `gestal-api` en `tlm-pe` |

**Configuración Keycloak:** Access Type `bearer-only`, Standard Flow `OFF`, Service Accounts `OFF`.

### 2. Consumidor — `{sistema}-{scope}[-{env}]`

Client **confidential**. Representa el servicio **como llamante**: obtiene tokens via `client_credentials` para autenticarse ante otras APIs internas. Reside en el realm del scope del consumidor.

| Parte        | Descripción                                           |
| ------------ | ----------------------------------------------------- |
| `{sistema}` | Nombre del sistema, minúsculas, sin guiones internos. |
| `{scope}`    | Código de scope del realm donde vive el client.       |
| `{env}`      | `dev` o `qa`. **Se omite en producción.**             |

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

### 3. Herramienta SSO — `{herramienta}`

Client **confidential** con **Standard Flow activo**. Representa una herramienta de plataforma que autentica usuarios humanos vía SSO (Authorization Code). Registrado en `tlm-corp`, sin scope ni env en el nombre.

**Ejemplo:** `grafana`

**Configuración Keycloak:** Access Type `confidential`, Standard Flow `ON`, Service Accounts `OFF`.

:::warning Coherencia Gateway ↔ Keycloak
El `clientId` en Keycloak debe coincidir exactamente con el identificador definido en `_consumers.yaml` del repositorio `tlm-infra-api-gateway`. Una discrepancia impide la validación de tokens en el API Gateway.
:::

---

## Estructura por Tipo de Servicio

### Servicio corporativo (multi-scope) — ejemplo: SISBON

```
Realm: tlm-corp
└─ sisbon-api          → Validador bearer-only

Realm: tlm-mx
├─ sisbon-mx-dev
├─ sisbon-mx-qa
└─ sisbon-mx           → Producción

Realm: tlm-pe
├─ sisbon-pe-dev
└─ sisbon-pe-qa
```

### Servicio local (scope único) — ejemplo: GESTAL (Perú)

```
Realm: tlm-pe
├─ gestal-api          → Validador bearer-only
├─ gestal-pe-dev
├─ gestal-pe-qa
└─ gestal-pe           → Producción
```

:::note Integraciones con sistemas externos
Las credenciales de proveedores externos (API keys, client secrets de terceros) **no se almacenan en Keycloak**. Keycloak genera sus propios secrets y no permite ingresar credenciales externas. Las credenciales de terceros deben almacenarse en AWS Secrets Manager y ser consumidas directamente por el servicio. Ver [Gestión de Secretos y Claves Criptográficas](./secrets-key-management.md).
:::

---

## Naming de Roles de Acceso

Los roles de acceso son **client roles** definidos bajo el client `{sistema}-api` de cada servicio. Al estar scoped al client, no requieren prefijo de sistema — el namespace ya es el `clientId`.

### Valores estándar

| Rol     | Descripción                                          |
| ------- | ---------------------------------------------------- |
| `read`  | Consulta de datos, sin modificaciones.               |
| `write` | Creación y actualización de datos.                   |
| `admin` | Acceso completo, incluyendo configuración y borrado. |

**Ejemplos:** rol `read` bajo `sisbon-api`, rol `admin` bajo `gestal-api`.

### Dónde se definen

| Tipo de servicio          | Client donde se crean los roles |
| ------------------------- | ------------------------------- |
| Corporativo (multi-scope) | `{sistema}-api` en `tlm-corp`   |
| Local (scope único)       | `{sistema}-api` en `tlm-{scope}`|

### Cómo aparecen en el JWT

```json
"resource_access": {
  "gestal-api": {
    "roles": ["read", "write"]
  }
}
```

El servicio verifica `resource_access["{sistema}-api"].roles`. Para que el rol aparezca en el token, hay que asignarlo al service account del consumer: en Keycloak, ir al consumer client → **Service Account Roles** → seleccionar `{sistema}-api` en el dropdown de Client Roles → asignar el rol.

---

## Naming de Client Scopes (custom)

Scopes personalizados de recursos específicos siguen el patrón de los client roles: nombre simple sin prefijo de sistema, porque el namespace ya es el `clientId` del resource server.

```
{recurso}
```

Scopes transversales de plataforma (sin prefijo de servicio):

| Scope             | Uso                                          |
| ----------------- | -------------------------------------------- |
| `service_account` | Clients con flujo `client_credentials` (M2M) |
| `organization`    | Claims de organización/tenant en el token    |

---

## Naming de Servicios Externos en Kong

Los servicios de terceros **expuestos vía Kong** (Kong actúa como proxy hacia un proveedor externo) usan el siguiente patrón en la configuración de Kong. Este naming vive en `_services.yaml` y no tiene contraparte en Keycloak — las credenciales del proveedor se almacenan en AWS Secrets Manager, no en Keycloak.

```
ext-{partner}-{sistema}-{env}
```

**Ejemplo:** `ext-talenthub-ats-dev` — Kong routea `/api-dev/gestal/ats` hacia la API de TalentHub.

---

## Checklist de Creación

### Servicio corporativo nuevo

- [ ] Crear realm `tlm-{scope}` si no existe
- [ ] Crear `{sistema}-api` en `tlm-corp` (bearer-only)
- [ ] Definir client roles `read`, `write`, `admin` bajo `{sistema}-api`
- [ ] Por cada scope: crear `{sistema}-{scope}-dev`, `{sistema}-{scope}-qa`, `{sistema}-{scope}`
- [ ] Registrar consumer en `_consumers.yaml` (Kong)

### Servicio local nuevo

- [ ] Crear `{sistema}-api` en `tlm-{scope}` (bearer-only)
- [ ] Definir client roles `read`, `write`, `admin` bajo `{sistema}-api`
- [ ] Crear `{sistema}-{scope}-dev`, `{sistema}-{scope}-qa`, `{sistema}-{scope}`
- [ ] Si hay integración con sistema externo: registrar las credenciales del proveedor en AWS Secrets Manager y definir el service en Kong (`ext-{partner}-{sistema}-{env}`)
- [ ] Registrar consumer en `_consumers.yaml` (Kong)

---

## Resumen de Patrones

| Entidad                   | Patrón                              | Ejemplo prod             | Ejemplo no-prod         |
| ------------------------- | ----------------------------------- | ------------------------ | ----------------------- |
| Realm                     | `tlm-{scope}`                       | `tlm-mx`                 | —                       |
| Validador API (corp)      | `{sistema}-api` en `tlm-corp`      | `sisbon-api`             | —                       |
| Validador API (local)     | `{sistema}-api` en `tlm-{scope}`   | `gestal-api`             | —                       |
| Consumidor                | `{sistema}-{scope}[-{env}]`        | `gestal-pe`              | `gestal-pe-qa`          |
| Consumidor multi-tipo     | `{sistema}-{tipo}-{scope}[-{env}]` | `gestal-mobile-pe`       | `gestal-mobile-pe-dev`  |
| Servicio externo (Kong)   | `ext-{partner}-{sistema}-{env}`    | `ext-talenthub-ats-prod` | `ext-talenthub-ats-dev` |
| Herramienta SSO           | `{herramienta}` — `confidential`, Standard Flow ON | `grafana`               | —                       |
| Client role               | `{acción}` bajo `{sistema}-api`    | `read`, `write`, `admin` | —                       |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar `tlm-{scope}` como patrón único para nombres de realms.
- **MUST** usar `corp` para el realm de servicios y herramientas corporativas (cross-scope).
- **MUST** escribir todos los identificadores en minúsculas (realms, clients, roles, scopes).
- **MUST** usar guiones como único separador de palabras en nombres de realms y clients.
- **MUST** incluir sufijo de ambiente (`dev` o `qa`) en todos los clients no productivos.
- **MUST** omitir el sufijo de ambiente en clients de producción.
- **MUST** definir los roles de acceso (`read`, `write`, `admin`) como client roles bajo `{sistema}-api`, no como realm roles.
- **MUST** registrar el `clientId` en Keycloak con el mismo valor que en `_consumers.yaml` de Kong.

### SHOULD (Fuertemente recomendado)

- **SHOULD** seguir la progresión `read → write → admin` en los niveles de rol sin saltarse niveles.
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
