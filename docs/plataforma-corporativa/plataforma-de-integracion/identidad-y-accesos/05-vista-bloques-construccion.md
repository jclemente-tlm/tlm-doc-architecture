---
sidebar_position: 5
title: Vista de Bloques de Construcción
description: Componentes del Servicio de Identidad y sus responsabilidades.
---

# 5. Vista de Bloques de Construcción

![Sistema de Identidad - Vista de Componentes](/diagrams/servicios-corporativos/identity_system.png)

## Componentes Principales

| Componente    | Responsabilidad                                  | Tecnología                                | Interfaces                   |
| ------------- | ------------------------------------------------ | ----------------------------------------- | ---------------------------- |
| Keycloak Core | IdP central multi-tenant, un `realm` por país    | Keycloak 23+ (imagen oficial), PostgreSQL | OAuth2/OIDC, SAML, Admin API |
| PostgreSQL    | Almacenamiento de identidades y configuración    | PostgreSQL 15+                            | JDBC                         |
| Federación    | Integración con IdPs externos (AD, LDAP, Google) | Conectores Keycloak                       | SAML, OIDC, LDAP             |
| Consola Admin | Gestión de realms, clientes, roles y usuarios    | Keycloak Admin Console                    | Web UI, Admin API            |

## Interfaces Externas

| Servicio             | Propósito                          |
| -------------------- | ---------------------------------- |
| API Gateway (Kong)   | Validación de tokens JWT           |
| Notification Service | MFA, alertas de acceso             |
| Audit Service        | Registro de eventos de seguridad   |
| Corporate Services   | Contexto de usuario y organización |
| Federation Partners  | IdPs externos por país             |
| Observabilidad (OBS) | Métricas, trazas, logs             |
