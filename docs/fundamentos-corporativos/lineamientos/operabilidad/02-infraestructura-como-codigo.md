---
id: infraestructura-como-codigo
sidebar_position: 2
title: Infraestructura como Código (IaC)
description: Aprovisionamiento declarativo, versionado y reproducible de infraestructura
---

# Infraestructura como Código (IaC)

Gestión manual de infraestructura mediante consolas crea configuraciones no documentadas, deriva entre entornos (configuration drift) y ausencia de trazabilidad que dificulta auditorías y troubleshooting. Cambios no versionados previenen rollback ante errores y generan inconsistencias entre development, staging y producción. Conocimiento tribal sobre configuración de infraestructura crea dependencias de personas y riesgos operacionales. Definir infraestructura como código declarativo (Terraform), versionarlo en Git, aplicar code review y automatizar aprovisionamiento garantiza reproducibilidad exacta, elimina deriva de configuración, permite rollback inmediato y habilita disaster recovery predecible mediante recreación completa de entornos desde código.

**Este lineamiento aplica a:** Definición de infraestructura cloud (compute, networking, storage), políticas y permisos IAM, configuración de servicios gestionados, módulos y abstracciones reutilizables, state management, plan/apply workflows.

**No aplica a:** Configuración de aplicaciones en runtime (ver Configuración de Entornos), despliegue de código de aplicaciones (ver CI/CD), migraciones de bases de datos (ver lineamientos de Datos).

## Estándares Obligatorios

- [Implementar infraestructura como código](../../estandares/infraestructura/infrastructure-as-code.md#1-iac-implementation)
- [Versionar código IaC en control de versiones](../../estandares/infraestructura/infrastructure-as-code.md#4-iac-versioning)
- [Realizar code review de IaC](../../estandares/infraestructura/infrastructure-as-code.md#5-iac-code-review)
- [Ejecutar scanning de seguridad en IaC](../../estandares/seguridad/security-scanning.md#3-iac-scanning-terraform)
- [Gestionar state de IaC remotamente](../../estandares/infraestructura/infrastructure-as-code.md#3-iac-state-management)
- [Aplicar workflow plan/apply en IaC](../../estandares/infraestructura/infrastructure-as-code.md#2-iac-workflow)
- [Detectar y prevenir configuration drift](../../estandares/infraestructura/infrastructure-as-code.md#6-drift-detection)

## Referencias Relacionadas

- [CI/CD y Automatización](./01-cicd-pipelines.md) (automatización de provisioning)
- [Configuración de Entornos](./03-configuracion-entornos.md) (configuración de aplicaciones)
- [Disaster Recovery](./04-disaster-recovery.md) (recreación de infraestructura)
- [Segmentación y Aislamiento](../seguridad/06-segmentacion-y-aislamiento.md) (networking, VPCs)
