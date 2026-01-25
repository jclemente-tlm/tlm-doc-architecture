---
id: identidad-y-accesos
sidebar_position: 2
title: Identidad y Accesos
description: Gestión de identidades, autenticación y autorización
---

# Identidad y Accesos

## 1. Propósito

Establecer cómo gestionar identidades, autenticación y autorización de manera centralizada, segura y auditable.

---

## 2. Alcance

Aplica a:

- Aplicaciones web y móviles
- APIs internas y externas
- Servicios backend
- Acceso a infraestructura y plataforma
- Integraciones entre sistemas

---

## 3. Lineamientos Obligatorios

- Usar identidad federada y SSO corporativo para usuarios
- Implementar autenticación multifactor (MFA) para accesos críticos
- Aplicar mínimo privilegio en autorizaciones
- Gestionar identidades de servicios con service accounts/managed identities
- No almacenar credenciales en código o configuración

---

## 4. Decisiones de Diseño Esperadas

- Proveedor de identidad y protocolo de autenticación (OAuth2, OIDC, SAML)
- Estrategia de autorización (RBAC, ABAC, claims-based)
- Gestión de tokens y sesiones
- Políticas de rotación de credenciales
- Estrategia de MFA para diferentes tipos de usuarios

---

## 5. Antipatrones y Prácticas Prohibidas

- Autenticación custom en lugar de estándares (OAuth2/OIDC)
- Credenciales hardcodeadas en código
- Tokens o secretos compartidos entre servicios
- Autorización solo en cliente (sin validación en servidor)
- Ausencia de MFA en accesos administrativos

---

## 6. Principios Relacionados

- Gestión de Identidades y Accesos
- Mínimo Privilegio
- Zero Trust
- Seguridad desde el Diseño

---

## 7. Validación y Cumplimiento

- Revisión de flujos de autenticación y autorización
- Auditoría de permisos y roles asignados
- Escaneo de secretos en repositorios de código
- Pruebas de seguridad de autenticación (pentest)
- Documentación en ADRs de estrategia de identidad
