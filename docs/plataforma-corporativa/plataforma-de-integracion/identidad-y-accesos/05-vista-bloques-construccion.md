---
sidebar_position: 5
title: Vista de Bloques de Construcción
description: Componentes del Servicio de Identidad y sus responsabilidades.
---

# 5. Vista de Bloques de Construcción

![Sistema de Identidad - Vista de Componentes](/diagrams/servicios-corporativos/identity_system.png)

## Componentes Principales

| Componente     | Responsabilidad                                  | Tecnología                                           | Interfaces                   |
| -------------- | ------------------------------------------------ | ---------------------------------------------------- | ---------------------------- |
| Keycloak Core  | IdP central multi-tenant, un `realm` por tenant  | Keycloak 26.4.4 (`quay.io/keycloak/keycloak`), Docker | OAuth2/OIDC, SAML, Admin API |
| PostgreSQL     | Almacenamiento de identidades y configuración    | PostgreSQL 16+ (Alpine)                               | JDBC                         |
| Tema `talma`   | Branding corporativo en login, account y admin   | CSS + propiedades Keycloak                            | i18n (`es`/`en`)             |
| Consola Admin  | Gestión de realms, clientes, roles y usuarios    | Keycloak Admin Console                                | Web UI, Admin API            |

## Realms Configurados

| Realm      | Display Name       | Tema           | Clientes                                     | Roles Custom                                 | Estado       |
| ---------- | ------------------ | -------------- | -------------------------------------------- | -------------------------------------------- | ------------ |
| `tlm-corp` | Talma Corporativo  | _(por defecto)_ | `grafana`, `sisbon-client-dev`                | `viewer`, `admin`, `editor` (Grafana)         | Configurado  |
| `tlm-pe`   | Talma Perú        | `talma-theme`  | `gestal-ext-ats`, `gestal-pe-dev`, `gestal-pe-qa` | `sisbon:read/write/admin`, `gestal:read/write/admin` | Configurado  |
| `tlm-mx`   | Talma México      | `talma-theme`  | `sisbon-mx-dev`, `sisbon-mx-qa`              | `sisbon:read/write/admin`                    | Configurado  |
| `tlm-ec`   | Talma Ecuador      | `talma-theme`  | _por definir_                                | _por definir_                                | Pendiente    |
| `tlm-co`   | Talma Colombia     | `talma-theme`  | _por definir_                                | _por definir_                                | Pendiente    |

## Client Scopes Custom

| Scope             | Descripción                                                          | Protocolo      |
| ----------------- | -------------------------------------------------------------------- | -------------- |
| `service_account` | Claims específicos para cuentas de servicio (client_id, host, IP)    | `openid-connect` |
| `organization`    | Claims sobre la organización a la que pertenece el sujeto            | `openid-connect` |

## Interfaces Externas

| Servicio             | Propósito                          |
| -------------------- | ---------------------------------- |
| API Gateway (Kong)   | Validación de tokens JWT           |
| Notification Service | MFA, alertas de acceso             |
| Audit Service        | Registro de eventos de seguridad   |
| Corporate Services   | Contexto de usuario y organización |
| Federation Partners  | IdPs externos por país             |
| Observabilidad (OBS) | Métricas, trazas, logs             |
