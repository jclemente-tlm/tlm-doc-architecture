---
id: cicd-pipelines
sidebar_position: 1
title: CI/CD y Automatización de Despliegues
description: Pipelines automatizados, integración continua y despliegues controlados
---

# CI/CD y Automatización de Despliegues

Despliegues manuales generan inconsistencias entre entornos, errores humanos y cuellos de botella que ralentizan entregas y comprometen estabilidad de producción. Ausencia de validaciones automatizadas permite que bugs, vulnerabilidades y regresiones lleguen a producción. Dependencia de conocimiento tribal para releases crea riesgos operacionales y dificulta escalamiento de equipos. Implementar pipelines CI/CD con validaciones automatizadas (testing, security scanning, quality gates), despliegues reproducibles y estrategias de rollback garantiza entregas predecibles, reduce lead time, elimina variabilidad humana y permite trazabilidad completa desde commit hasta producción.

**Este lineamiento aplica a:** pipelines de integración continua, automatización de builds, ejecución de pruebas (unitarias, integración, e2e), validaciones de calidad y seguridad, estrategias de deployment (blue/green, canary, rolling), automatización de rollbacks, release management.

## Prácticas Obligatorias

- [Implementar pipelines CI/CD automatizados](../../estandares/operabilidad/cicd-deployment.md#1-ci-cd-pipelines)
- [Automatizar build y empaquetado](../../estandares/operabilidad/cicd-deployment.md#2-build-automation)
- [Integrar SCA (dependency scanning)](../../estandares/seguridad/security-scanning.md#2-dependency-scanning)
- [Aplicar estrategias de deployment](../../estandares/operabilidad/cicd-deployment.md#3-deployment-strategies)
- [Automatizar rollback](../../estandares/operabilidad/cicd-deployment.md#5-rollback-automation)
- [Gestionar artifacts y registries](../../estandares/operabilidad/cicd-deployment.md#6-artifact-management)
- [Implementar traceability desde commit a producción](../../estandares/operabilidad/cicd-deployment.md#4-deployment-traceability)

## Referencias Relacionadas

- [Control de Versiones](../desarrollo/04-control-versiones.md) (versionado y tagging)
- [Infraestructura como Código](./02-infraestructura-como-codigo.md) (aprovisionamiento automatizado)
- [Estrategia de Pruebas](../desarrollo/02-estrategia-pruebas.md) (tipos de testing)
- [Calidad de Código](../desarrollo/01-calidad-codigo.md) (análisis estático)
