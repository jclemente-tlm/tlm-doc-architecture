---
id: control-versiones
sidebar_position: 4
title: Control de Versiones
description: Git workflows, estrategias de branching, commits semánticos y versionado
---

# Control de Versiones

Uso inconsistente de control de versiones genera historial confuso, conflictos frecuentes y dificultad para rastrear origen de bugs. Ausencia de estrategia de branching clara provoca despliegues accidentales, bloqueos entre equipos y complicaciones en manejo de releases. Commits sin convención dificultan generación de changelogs automáticos y comprensión de cambios históricos. Versionado inconsistente de artefactos impide correlación entre código, imagen Docker y deployment en ambiente. Establecer Git workflow consistente (trunk-based o GitFlow según contexto), commits semánticos, versionado automático mediante CI/CD y protección de ramas principales garantiza historial limpio, colaboración fluida, releases predecibles y trazabilidad end-to-end.

**Este lineamiento aplica a:** Git workflows y estrategias de branching, formato de commits (Conventional Commits), estrategias de merge (merge commits vs squash vs rebase), versionado de artefactos (SemVer), tagging y releases, protección de ramas principales.

**No aplica a:** Control de versiones de bases de datos (migraciones), versionado de APIs (ver estándares de APIs), versionado de infraestructura (IaC).

## Estándares Obligatorios

- [Usar Git workflows y estrategias de branching consistentes](../../estandares/desarrollo/repositorios.md#estrategia-de-branching)
- [Aplicar commits semánticos (Conventional Commits)](../../estandares/desarrollo/repositorios.md#commits-semanticos)
- [Versionar artefactos con Semantic Versioning (SemVer)](../../estandares/desarrollo/repositorios.md#versionado-de-artefactos)
- [Proteger ramas principales con políticas de merge](../../estandares/desarrollo/code-quality-review.md#4-requisitos-obligatorios)
- [Automatizar versionado y tagging en pipelines CI/CD](../../estandares/desarrollo/cicd-pipelines.md)

## Referencias Relacionadas

- [Calidad de Código](./01-calidad-codigo.md) (code review obligatorio)
- [CI/CD y Automatización](../operabilidad/01-cicd-pipelines.md) (pipelines CI/CD)
- [Documentación Técnica](./03-documentacion-tecnica.md) (changelogs, release notes)
