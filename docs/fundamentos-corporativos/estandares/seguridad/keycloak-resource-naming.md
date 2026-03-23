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

Existen cuatro patrones según el rol del client:

### 1. Validador de API — `{servicio}-api`

Client **bearer-only** — solo valida tokens, no autentica usuarios ni solicita credenciales. Lo registra el equipo de Identidad como referencia del servicio ante Kong.

| Tipo de servicio          | Realm donde se registra | Ejemplo                  |
| ------------------------- | ----------------------- | ------------------------ |
| Corporativo (multi-scope) | `tlm-corp`              | `sisbon-api`             |
| Local (scope único)       | `tlm-{scope}`           | `gestal-api` en `tlm-pe` |

**Configuración Keycloak:** Access Type `bearer-only`, Standard Flow `OFF`, Service Accounts `OFF`.

### 2. Consumidor — `{servicio}-{scope}[-{env}]`

Client **confidential** — solicita tokens para consumir APIs internas. Reside en el realm del scope del consumidor.

| Parte        | Descripción                                           |
| ------------ | ----------------------------------------------------- |
| `{servicio}` | Nombre del sistema, minúsculas, sin guiones internos. |
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

**Evolución opcional — multi-tipo:** Si el servicio necesita clients diferenciados por tipo de consumidor (web, móvil, batch), el patrón se extiende a `{servicio}-{tipo}-{scope}[-{env}]`:

```
gestal-app-pe-prod       → Backend/web
gestal-mobile-pe-prod    → App móvil
gestal-batch-pe-prod     → Proceso batch
```

Aplicar solo cuando haya 2 o más tipos con permisos o rate limits distintos.

**Configuración Keycloak:** Access Type `confidential`, Service Accounts `YES`, Standard Flow `OFF`.

### 3. Integración externa — `{servicio}-ext-{partner}`

Client para autenticar la llamada de Talma hacia un sistema externo de terceros.

**Ejemplo:** `gestal-ext-ats` en `tlm-pe` — client que obtiene credenciales para conectarse al ATS externo.

### 4. Herramienta de plataforma

Para herramientas de observabilidad registradas en `tlm-corp`, se usa el nombre de la herramienta sin scope ni env.

**Ejemplo:** `grafana`

:::warning Coherencia Gateway ↔ Keycloak
El `clientId` en Keycloak debe coincidir exactamente con el identificador definido en `_consumers.yaml` del repositorio `tlm-infra-kong`. Una discrepancia impide la validación de tokens en el API Gateway.
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
├─ gestal-pe           → Producción
└─ gestal-ext-ats      → Integración con ATS externo
```

---

## Naming de Roles de Realm

### Patrón

```
{servicio}:{acción}
```

**Ejemplos:** `sisbon:read`, `sisbon:write`, `sisbon:admin`, `gestal:read`, `gestal:admin`

### Niveles de acción

| Acción  | Descripción                                          |
| ------- | ---------------------------------------------------- |
| `read`  | Consulta de datos, sin modificaciones.               |
| `write` | Creación y actualización de datos.                   |
| `admin` | Acceso completo, incluyendo configuración y borrado. |

### Dónde se definen los roles

| Tipo de servicio          | Realm donde se crean los roles |
| ------------------------- | ------------------------------ |
| Corporativo (multi-scope) | `tlm-corp`                     |
| Local (scope único)       | `tlm-{scope}` del servicio     |

---

## Naming de Client Scopes (custom)

Scopes personalizados siguen el mismo patrón que los roles:

```
{servicio}:{recurso}
```

Scopes transversales de plataforma (sin prefijo de servicio):

| Scope             | Uso                                          |
| ----------------- | -------------------------------------------- |
| `service_account` | Clients con flujo `client_credentials` (M2M) |
| `organization`    | Claims de organización/tenant en el token    |

---

## Naming de Servicios Externos en Kong

Los servicios de terceros **expuestos vía Kong** (Kong actúa como proxy hacia un proveedor externo) usan un patrón distinto al de los clients de Keycloak:

```
ext-{partner}-{servicio}-{env}
```

**Ejemplo:** `ext-talenthub-ats-dev` — Kong routea `/api-dev/gestal/ats` hacia la API de TalentHub.

Este naming vive en la configuración de Kong (`_services.yaml`), no en Keycloak.

| Entidad         | Patrón                           | Dónde vive     | Propósito                                                    |
| --------------- | -------------------------------- | -------------- | ------------------------------------------------------------ |
| Client Keycloak | `{servicio}-ext-{partner}`       | Keycloak realm | Identidad que **obtiene** tokens para llamar al externo      |
| Service Kong    | `ext-{partner}-{servicio}-{env}` | Kong config    | Proxy que **expone** el servicio externo a clientes internos |

---

## Checklist de Creación

### Servicio corporativo nuevo

- [ ] Crear realm `tlm-{scope}` si no existe
- [ ] Crear `{servicio}-api` en `tlm-corp` (bearer-only)
- [ ] Por cada scope: crear `{servicio}-{scope}-dev`, `{servicio}-{scope}-qa`, `{servicio}-{scope}`
- [ ] Definir roles `{servicio}:read/write/admin` en `tlm-corp`
- [ ] Registrar consumer en `_consumers.yaml` (Kong)

### Servicio local nuevo

- [ ] Crear `{servicio}-api` en `tlm-{scope}` (bearer-only)
- [ ] Crear `{servicio}-{scope}-dev`, `{servicio}-{scope}-qa`, `{servicio}-{scope}`
- [ ] Si hay integración externa: crear `{servicio}-ext-{partner}` en Keycloak y `ext-{partner}-{servicio}-{env}` en Kong
- [ ] Definir roles `{servicio}:read/write/admin` en `tlm-{scope}`
- [ ] Registrar consumer en `_consumers.yaml` (Kong)

---

## Resumen de Patrones

| Entidad                   | Patrón                              | Ejemplo prod             | Ejemplo no-prod         |
| ------------------------- | ----------------------------------- | ------------------------ | ----------------------- |
| Realm                     | `tlm-{scope}`                       | `tlm-mx`                 | —                       |
| Validador API (corp)      | `{servicio}-api` en `tlm-corp`      | `sisbon-api`             | —                       |
| Validador API (local)     | `{servicio}-api` en `tlm-{scope}`   | `gestal-api`             | —                       |
| Consumidor                | `{servicio}-{scope}[-{env}]`        | `gestal-pe`              | `gestal-pe-qa`          |
| Consumidor multi-tipo     | `{servicio}-{tipo}-{scope}[-{env}]` | `gestal-mobile-pe`       | `gestal-mobile-pe-dev`  |
| Client externo (Keycloak) | `{servicio}-ext-{partner}`          | `gestal-ext-ats`         | —                       |
| Servicio externo (Kong)   | `ext-{partner}-{servicio}-{env}`    | `ext-talenthub-ats-prod` | `ext-talenthub-ats-dev` |
| Herramienta plataforma    | `{herramienta}`                     | `grafana`                | —                       |
| Rol                       | `{servicio}:{acción}`               | `sisbon:admin`           | —                       |

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar `tlm-{scope}` como patrón único para nombres de realms.
- **MUST** usar `corp` para el realm de servicios y herramientas corporativas (cross-scope).
- **MUST** escribir todos los identificadores en minúsculas (realms, clients, roles, scopes).
- **MUST** usar guiones como único separador de palabras en nombres de realms y clients.
- **MUST** incluir sufijo de ambiente (`dev` o `qa`) en todos los clients no productivos.
- **MUST** omitir el sufijo de ambiente en clients de producción.
- **MUST** usar `:` como separador en nombres de roles (`{servicio}:{acción}`).
- **MUST** registrar el `clientId` en Keycloak con el mismo valor que en `_consumers.yaml` de Kong.

### SHOULD (Fuertemente recomendado)

- **SHOULD** seguir la progresión `read → write → admin` en los niveles de rol sin saltarse niveles.
- **SHOULD** usar el patrón multi-tipo (`{servicio}-{tipo}-{scope}`) solo cuando existan 2 o más tipos de consumidores con permisos o rate limits distintos.

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
