---
id: 04-convenciones-commits
sidebar_position: 4
title: Convenciones de Commits
---

## Convenciones de Commits

Las convenciones de commits tienen como objetivo estandarizar los mensajes de los commits para facilitar la comprensión del historial, automatizar procesos (como generación de changelogs y versionado) y mejorar la colaboración entre equipos.

- Usa el formato [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):
  - `feat`: nueva funcionalidad
  - `fix`: corrección de errores
  - `docs`: solo documentación
  - `style`: formato, sin cambios de lógica
  - `refactor`: refactorización de código
  - `test`: pruebas
  - `chore`: tareas de mantenimiento

## Ejemplos

- `feat(api): agrega endpoint de autenticación`
- `fix(login): corrige validación de usuario nulo`
- `docs(readme): actualiza instrucciones de despliegue`
- `style(css): ajusta indentación en estilos globales`
- `refactor(core): simplifica lógica de cálculo de impuestos`
- `test(user): agrega pruebas unitarias para registro`
- `chore(ci): actualiza versión de Node en pipeline`

- El mensaje debe ser claro, en presente y en español o inglés según el proyecto.
