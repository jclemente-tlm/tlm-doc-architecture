---
id: control-versiones
sidebar_position: 4
title: Control de Versiones
description: Git workflows, estrategias de branching, commits semánticos y versionado
---

# Control de Versiones

Uso inconsistente de control de versiones genera historial confuso, conflictos frecuentes y dificultad para rastrear origen de bugs. Ausencia de estrategia de branching clara provoca despliegues accidentales, bloqueos entre equipos y complicaciones en manejo de releases. Commits sin convención dificultan generación de changelogs automáticos y comprensión de cambios históricos. Versionado inconsistente de artefactos impide correlación entre código, imagen Docker y deployment en ambiente. Establecer Git workflow consistente (trunk-based o GitFlow según contexto), commits semánticos, versionado automático mediante CI/CD y protección de ramas principales garantiza historial limpio, colaboración fluida, releases predecibles y trazabilidad end-to-end.

**Este lineamiento aplica a:** git workflows y estrategias de branching, formato de commits (Conventional Commits), estrategias de merge (merge commits vs squash vs rebase), versionado de artefactos (SemVer), tagging y releases, protección de ramas principales.

## Prácticas Obligatorias

- [Definir Git workflow corporativo](../../estandares/desarrollo/git-workflow.md#1-git-workflow)
- [Aplicar estrategia de branching](../../estandares/desarrollo/git-workflow.md#2-branching-strategy)
- [Usar conventional commits](../../estandares/desarrollo/git-workflow.md#5-conventional-commits)
- [Aplicar semantic versioning](../../estandares/desarrollo/versioning.md)
- [Proteger ramas principales](../../estandares/desarrollo/git-workflow.md#4-branch-protection)
- [Definir estrategia de merge](../../estandares/desarrollo/git-workflow.md#3-merge-strategies)

## Referencias Relacionadas

- [Calidad de Código](./calidad-codigo.md) (code review obligatorio)
- [CI/CD y Automatización](../operabilidad/cicd-pipelines.md) (pipelines CI/CD)
- [Documentación Técnica](./documentacion-tecnica.md) (changelogs, release notes)
