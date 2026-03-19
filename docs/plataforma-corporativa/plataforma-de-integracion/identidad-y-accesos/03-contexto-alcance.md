---
sidebar_position: 3
title: Contexto y Alcance
description: Límites del sistema de identidad y sus interfaces externas.
---

# 3. Contexto y Alcance

## Contexto del Sistema

Keycloak actúa como IdP central para todos los servicios corporativos multipaís.
No contiene lógica de negocio; gestiona identidades, sesiones y tokens para los servicios que lo consumen.

## Contexto Técnico

```mermaid
graph LR
    subgraph IdPs Externos - planificado
        A1[Google Workspace]
        A2[Microsoft AD]
        A3[LDAP Corporativo]
    end

    subgraph Tenants / Realms
        T0[tlm-corp]
        T1[tlm-pe]
        T2[tlm-mx]
        T3[tlm-ec - pendiente]
        T4[tlm-co - pendiente]
    end

    KC[Keycloak 26.4.4]
    GW[Kong API Gateway]
    SVC[Servicios Corporativos]
    OBS[Observabilidad\nMétricas :9000]

    A1 -.->|SAML/OIDC| KC
    A2 -.->|LDAP| KC
    A3 -.->|LDAP| KC
    KC --> T0
    KC --> T1
    KC --> T2
    KC -.-> T3
    KC -.-> T4
    KC -->|JWKS| GW
    GW -->|requests autenticados| SVC
    KC -->|métricas / health| OBS
```

> Las líneas punteadas hacia IdPs externos indican integración planificada, aún no configurada.

## Dentro del Alcance

| Componente        | Responsabilidad                                                              |
| ----------------- | ---------------------------------------------------------------------------- |
| Keycloak          | IdP central multi-tenant; autenticación, autorización, gestión de usuarios   |
| Realm corporativo | `tlm-corp`: realm global para servicios internos (Grafana, herramientas)     |
| Realms por país   | `tlm-pe`, `tlm-mx`: configurados. `tlm-ec`, `tlm-co`: pendientes de creación |
| Tema corporativo  | `talma-theme`: branding personalizado para login, account y admin            |
| Gestión de tokens | Ciclo de vida de JWT: generación, validación, renovación (`accessToken: 300s`) |
| Auditoría         | Registro de eventos de seguridad _(pendiente de habilitación)_               |

## Fuera de Alcance

- IdPs externos (Google, Microsoft AD, LDAP corporativo) — gestionados por terceros o TI.
- Lógica de negocio de los servicios que consumen tokens.
- Validación de tokens por request — responsabilidad de Kong (ADR-010).

## Interfaces Externas

| Actor                             | Tipo    | Descripción                                      |
| --------------------------------- | ------- | ------------------------------------------------ |
| Administrador Global              | Humano  | Configuración de tenants (`realms`), políticas   |
| Administrador de Tenant (`realm`) | Humano  | Gestión de usuarios y roles específicos por país |
| Usuario Final                     | Humano  | Login, gestión de perfil, reset de contraseña    |
| API Gateway (Kong)                | Sistema | Validación de token JWT, contexto de usuario     |
| Servicios Corporativos            | Sistema | Autenticación y autorización                     |
| IdP Externo                       | Sistema | Federación de usuarios (SAML, OIDC, LDAP)        |
| Sistema de Monitoreo              | Sistema | Métricas, logs, health checks                    |
