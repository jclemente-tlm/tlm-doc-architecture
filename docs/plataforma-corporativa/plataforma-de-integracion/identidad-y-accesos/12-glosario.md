---
sidebar_position: 12
title: Glosario
description: Términos y acrónimos del Servicio de Identidad.
---

# 12. Glosario

| Término / Acrónimo                     | Definición                                                                                       |
| -------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **IdP** (Identity Provider)            | Servicio que autentica y gestiona identidades de usuarios.                                       |
| **Keycloak**                           | Plataforma open source para gestión de identidad y acceso, multi-tenant.                         |
| **Realm**                              | Entidad lógica en Keycloak que representa un tenant aislado. Equivale a un país en este sistema. |
| **Tenant**                             | Contexto aislado de usuarios, configuración y políticas. En este sistema = `realm` por país.     |
| **Federation**                         | Integración con proveedores externos de identidad (LDAP, SAML, OIDC).                            |
| **JWT** (JSON Web Token)               | Formato estándar firmado para autenticación y autorización entre servicios.                      |
| **OAuth2**                             | Protocolo estándar de autorización para APIs.                                                    |
| **OIDC** (OpenID Connect)              | Capa de autenticación sobre OAuth2.                                                              |
| **SAML**                               | Security Assertion Markup Language, estándar de federación empresarial.                          |
| **MFA** (Multi-Factor Authentication)  | Autenticación con múltiples factores; obligatorio para administración.                           |
| **SSO** (Single Sign-On)               | Acceso único a múltiples sistemas con una sola autenticación.                                    |
| **JWKS**                               | JSON Web Key Set, endpoint público con las claves de firma de tokens.                            |
| **TOTP**                               | Time-based One-Time Password, código temporal para MFA.                                          |
| **Loki**                               | Sistema de agregación de logs (Grafana). Destino de logs de Keycloak.                            |
| **Tempo**                              | Backend de trazas distribuidas (Grafana). Recibe trazas vía OTLP/Zipkin.                         |
| **Mimir**                              | Backend de métricas Prometheus a largo plazo (Grafana).                                          |
| **FireLens**                           | Integración de AWS ECS con Fluent Bit para enrutamiento de logs.                                 |
| **ALB** (Application Load Balancer)    | Balanceador de carga HTTP/HTTPS de AWS.                                                          |
| **ECS** (Elastic Container Service)    | Servicio de orquestación de contenedores de AWS.                                                 |
| **RDS**                                | Relational Database Service de AWS. Hospeda PostgreSQL para Keycloak.                            |
| **ADR** (Architecture Decision Record) | Registro formal de una decisión arquitectónica.                                                  |
| **DEC**                                | Decisión local de arquitectura dentro del servicio, complementaria a un ADR.                     |
| **IaC** (Infrastructure as Code)       | Gestión de infraestructura mediante código versionado (Terraform).                               |
