---
title: "Ramas"
description: "Lineamientos para la nomenclatura de ramas en Git."
id: 02-ramas
sidebar_position: 2
---

## Objetivo

Asegurar una nomenclatura clara, predecible y alineada con el flujo de trabajo de Git.

## Alcance

Aplica a todos los equipos que gestionan ramas en repositorios de Talma.

## Detalles

### Reglas generales

- Usa solo minúsculas y guiones medios (`-`) como separador.
- No uses espacios, acentos ni caracteres especiales.
- El nombre debe ser descriptivo y breve.

### Convenciones principales

- `main` o `master`: rama principal de producción.
- `develop`: rama de integración (si aplica Gitflow).
- `feature/<descripción-corta>`: nuevas funcionalidades. Ejemplo: `feature/login-api`
- `bugfix/<descripción-corta>`: corrección de errores. Ejemplo: `bugfix/fix-login`
- `hotfix/<descripción-corta>`: corrección urgente en producción. Ejemplo: `hotfix/patch-typo`
- `release/<versión>`: preparación de una nueva versión. Ejemplo: `release/1.2.0`
- `experiment/<descripción>`: pruebas o prototipos.

### Ejemplos

| Correcto                | Incorrecto         |
|-------------------------|-------------------|
| feature/login-api       | Feature/LoginApi   |
| bugfix/fix-login        | bug_fix/fixLogin   |
| release/1.2.0           | release-1.2.0      |

## Buenas prácticas

- Relaciona el nombre con el objetivo de la rama.
- Si aplica, incluye el número de ticket o tarea: `feature/1234-login-api`.
- Elimina ramas que ya no se usen.

## Referencias

- [Git Branch Naming](https://nvie.com/posts/a-successful-git-branching-model/)
- [Documentación interna de Talma](../README.md)

## Última revisión

- Fecha: 2025-08-08
- Responsable: Equipo de Arquitectura
