---
id: 05-versionado-semantico
sidebar_position: 5
title: Versionado semántico
---

## Uso de SemVer

El versionado semántico (SemVer) permite comunicar de forma clara el tipo de cambios realizados en cada versión del software, facilitando la gestión de dependencias y la integración continua.

- Usa [SemVer](https://semver.org/lang/es/): MAJOR.MINOR.PATCH
  - Cambios incompatibles: incrementa MAJOR
  - Nuevas funcionalidades compatibles: incrementa MINOR
  - Correcciones compatibles: incrementa PATCH

## Ejemplos

- `1.0.0`: Primera versión estable.
- `1.1.0`: Se agrega una funcionalidad nueva compatible.
- `1.1.1`: Se corrige un bug menor.
- `2.0.0`: Se introducen cambios incompatibles (por ejemplo, se elimina o cambia un endpoint).

- Documenta los cambios relevantes en un archivo `CHANGELOG.md`.
