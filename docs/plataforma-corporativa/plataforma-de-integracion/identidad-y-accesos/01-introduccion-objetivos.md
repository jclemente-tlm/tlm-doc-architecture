---
sidebar_position: 1
title: Introducción y Objetivos
description: Objetivos, requisitos y partes interesadas del Servicio de Identidad basado en Keycloak.
---

# 1. Introducción y Objetivos

El **Servicio de Identidad** centraliza autenticación, autorización y federación para todos los servicios corporativos multipaís.
Está implementado con **Keycloak**, desplegado en contenedores sobre AWS ECS Fargate (ADR-003).

## Funcionalidades Clave

| Funcionalidad  | Descripción                                                                               |
| -------------- | ----------------------------------------------------------------------------------------- |
| SSO            | Acceso unificado a aplicaciones mediante `OAuth2`/`OIDC` y `JWT`                          |
| Multi-tenancy  | Aislamiento por país mediante un `realm` de Keycloak por tenant                           |
| Federación     | Integración con IdPs externos (`SAML`, `OIDC`, `LDAP`)                                    |
| RBAC           | Control de acceso basado en roles                                                         |
| MFA            | Autenticación multi-factor para roles críticos                                            |
| Auditoría      | Registro estructurado de eventos de seguridad                                             |
| Observabilidad | Métricas, logs y trazas integradas con el stack corporativo (Grafana, Mimir, Loki, Tempo) |
| API Gateway    | Validación de tokens JWT por Kong mediante JWKS de cada realm                             |

## Requisitos de Calidad

| Atributo         | Objetivo           | Crítico            |
| ---------------- | ------------------ | ------------------ |
| Disponibilidad   | `99.9%`            | `99.5%`            |
| Latencia auth    | `< 200ms p95`      | `< 500ms`          |
| Throughput       | `5,000 logins/min` | `2,000 logins/min` |
| Validación token | `< 50ms`           | `< 100ms`          |

## Partes Interesadas

| Rol                   | Interés                                         |
| --------------------- | ----------------------------------------------- |
| CISO                  | Políticas de seguridad y cumplimiento normativo |
| Directores de RRHH    | Ciclo de vida de usuarios y onboarding          |
| Equipos de Desarrollo | Integración con OAuth2/OIDC; consumo de tokens  |
| Equipo de Plataforma  | Operación, despliegue y monitoreo de Keycloak   |
| Equipo de Seguridad   | Configuración de MFA, federación y auditoría    |

## Decisión de Tecnología

Keycloak fue seleccionado en [ADR-003](../../../adrs/adr-003-keycloak-sso-autenticacion.md).
