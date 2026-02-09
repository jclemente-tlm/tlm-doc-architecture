---
id: automatizacion-iac
sidebar_position: 1
title: Automatización e Infraestructura como Código
description: Automatización de despliegues, infraestructura y validaciones mediante CI/CD e IaC
---

# Automatización e Infraestructura como Código

Los procesos manuales repetitivos generan inconsistencias, errores humanos y cuellos de botella que ralentizan entregas y comprometen estabilidad de producción. Gestión manual de infraestructura mediante consolas crea configuraciones no documentadas, deriva entre entornos y ausencia de trazabilidad. Dependencia de conocimiento tribal para despliegues y aprovisionamiento crea riesgos operacionales y dificulta escalamiento de equipos. Automatizar despliegues mediante CI/CD, definir infraestructura como código versionado y automatizar validaciones garantiza consistencia entre ejecuciones, reproducibilidad exacta, reduce lead time, elimina variabilidad humana y permite trazabilidad completa de cambios desde código hasta producción.

**Este lineamiento aplica a:** Despliegues y releases, pruebas (unitarias, integración, e2e), aprovisionamiento de infraestructura cloud (compute, storage, networking), configuración de plataforma, políticas y permisos, validaciones de calidad y seguridad.

## Estándares Obligatorios

- [Automatizar despliegues mediante pipelines CI/CD](../../estandares/desarrollo/cicd-pipelines.md)
- [Definir infraestructura mediante código (Terraform)](../../estandares/infraestructura/infrastructure-as-code.md)
- [Aplicar revisión de código a infraestructura](../../estandares/desarrollo/code-quality-review.md)
- [Integrar validaciones de seguridad en pipelines](../../estandares/desarrollo/cicd-pipelines.md#security-stage)
