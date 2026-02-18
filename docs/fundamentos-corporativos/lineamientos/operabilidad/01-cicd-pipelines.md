---
id: cicd-pipelines
sidebar_position: 1
title: CI/CD y Automatización de Despliegues
description: Pipelines automatizados, integración continua y despliegues controlados
---

# CI/CD y Automatización de Despliegues

Despliegues manuales generan inconsistencias entre entornos, errores humanos y cuellos de botella que ralentizan entregas y comprometen estabilidad de producción. Ausencia de validaciones automatizadas permite que bugs, vulnerabilidades y regresiones lleguen a producción. Dependencia de conocimiento tribal para releases crea riesgos operacionales y dificulta escalamiento de equipos. Implementar pipelines CI/CD con validaciones automatizadas (testing, security scanning, quality gates), despliegues reproducibles y estrategias de rollback garantiza entregas predecibles, reduce lead time, elimina variabilidad humana y permite trazabilidad completa desde commit hasta producción.

**Este lineamiento aplica a:** Pipelines de integración continua, automatización de builds, ejecución de pruebas (unitarias, integración, e2e), validaciones de calidad y seguridad, estrategias de deployment (blue/green, canary, rolling), automatización de rollbacks, release management.

**No aplica a:** Infraestructura como código (ver IaC), gestión de configuración de aplicaciones (ver Configuración de Entornos), versionado de código fuente (ver Control de Versiones en Desarrollo).

## Estándares Obligatorios

- [Implementar pipelines CI/CD automatizados](../../estandares/operabilidad/cicd-pipelines.md)
- [Automatizar build y empaquetado](../../estandares/operabilidad/build-automation.md)
- [Ejecutar testing automatizado en pipelines](../../estandares/testing/test-automation.md)
- [Integrar SAST en pipelines](../../estandares/desarrollo/sast.md)
- [Integrar SCA (dependency scanning)](../../estandares/seguridad/dependency-scanning.md)
- [Implementar quality gates](../../estandares/desarrollo/quality-gates.md)
- [Aplicar estrategias de deployment](../../estandares/operabilidad/deployment-strategies.md)
- [Automatizar rollback](../../estandares/operabilidad/rollback-automation.md)
- [Gestionar artifacts y registries](../../estandares/operabilidad/artifact-management.md)
- [Implementar traceability desde commit a producción](../../estandares/operabilidad/deployment-traceability.md)

## Referencias Relacionadas

- [Control de Versiones](../desarrollo/04-control-versiones.md) (versionado y tagging)
- [Infraestructura como Código](./02-infraestructura-como-codigo.md) (aprovisionamiento automatizado)
- [Estrategia de Pruebas](../desarrollo/02-estrategia-pruebas.md) (tipos de testing)
- [Calidad de Código](../desarrollo/01-calidad-codigo.md) (análisis estático)
