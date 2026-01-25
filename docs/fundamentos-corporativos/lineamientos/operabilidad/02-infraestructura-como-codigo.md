---
id: infraestructura-como-codigo
sidebar_position: 2
title: Infraestructura como Código
description: Gestión de infraestructura mediante código versionado y reproducible
---

# Infraestructura como Código

## 1. Propósito

Establecer que toda infraestructura debe definirse, aprovisionarse y gestionarse mediante código, garantizando reproducibilidad, trazabilidad y automatización.

---

## 2. Alcance

Aplica a:

- Recursos cloud (compute, storage, networking)
- Configuración de plataforma
- Políticas y permisos
- Networking y seguridad
- Bases de datos y servicios gestionados

---

## 3. Lineamientos Obligatorios

- Definir infraestructura mediante IaC (Terraform, CloudFormation, Bicep)
- Versionar código de infraestructura en repositorios
- Aplicar revisión de código (PR) a cambios de infraestructura
- Separar configuración por entorno mediante variables
- Documentar dependencias y orden de aprovisionamiento

---

## 4. Decisiones de Diseño Esperadas

- Herramienta de IaC (Terraform, CloudFormation, CDK)
- Estrategia de state management
- Organización de módulos y componentes reutilizables
- Separación de entornos (workspaces, folders)
- Estrategia de secrets en IaC

---

## 5. Antipatrones y Prácticas Prohibidas

- Cambios manuales en consola cloud
- Infraestructura sin código versionado
- State files no gestionados o en local
- Secretos hardcodeados en código IaC
- Drift entre código y estado real de infraestructura

---

## 6. Principios Relacionados

- Infraestructura como Código
- Automatización como Principio
- Consistencia entre Entornos
- Arquitectura Cloud Native

---

## 7. Validación y Cumplimiento

- Auditoría de recursos cloud vs código IaC
- Detección de drift automática
- Revisión de PRs de infraestructura
- Validación de formato y linting de IaC
- Documentación en ADRs de estrategia IaC
