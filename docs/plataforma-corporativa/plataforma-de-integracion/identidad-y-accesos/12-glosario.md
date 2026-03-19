---
sidebar_position: 12
title: Glosario
description: Términos y acrónimos del Servicio de Identidad.
---

# 12. Glosario

## Términos del Dominio

| Término        | Definición                                                                                     |
| -------------- | ---------------------------------------------------------------------------------------------- |
| **Keycloak**   | Plataforma open source para gestión de identidad y acceso, multi-tenant.                       |
| **Realm**      | Entidad lógica en Keycloak que representa un tenant aislado con usuarios, clientes y políticas propias. |
| **Tenant**     | Contexto aislado de usuarios, configuración y políticas. En este sistema = `realm` por país o función corporativa. |
| **Federation** | Integración con proveedores externos de identidad (LDAP, SAML, OIDC).                         |
| **talma-theme**| Tema personalizado de Keycloak con branding Talma para login, account y admin.                  |
| **nonprod**    | Ambiente de infraestructura compartido para los ambientes lógicos `dev` y `qa`.                |

## Acrónimos

| Acrónimo | Significado                                                                          |
| -------- | ------------------------------------------------------------------------------------ |
| **IdP**  | Identity Provider — servicio que autentica y gestiona identidades de usuarios.        |
| **JWT**  | JSON Web Token — formato estándar firmado para autenticación entre servicios.         |
| **JWKS** | JSON Web Key Set — endpoint público con las claves de firma de tokens.                |
| **OAuth2** | Protocolo estándar de autorización para APIs.                                      |
| **OIDC** | OpenID Connect — capa de autenticación sobre OAuth2.                                 |
| **SAML** | Security Assertion Markup Language — estándar de federación empresarial.              |
| **MFA**  | Multi-Factor Authentication — autenticación con múltiples factores.                   |
| **SSO**  | Single Sign-On — acceso único a múltiples sistemas con una sola autenticación.        |
| **TOTP** | Time-based One-Time Password — código temporal para MFA (6 dígitos, 30s, HmacSHA1).  |
| **ALB**  | Application Load Balancer — balanceador de carga HTTP/HTTPS de AWS.                   |
| **EC2**  | Elastic Compute Cloud — servicio de cómputo de AWS.                                   |
| **RDS**  | Relational Database Service — servicio de base de datos gestionada de AWS.             |
| **ADR**  | Architecture Decision Record — registro formal de una decisión arquitectónica.         |
| **DEC**  | Decisión local de arquitectura dentro del servicio, complementaria a un ADR.          |
| **IaC**  | Infrastructure as Code — gestión de infraestructura mediante código versionado.        |
