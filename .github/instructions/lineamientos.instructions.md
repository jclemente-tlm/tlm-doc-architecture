---
title: Instrucciones para GitHub Copilot para Generar Documentación Clara y Precisa
description: Guía para que GitHub Copilot cree documentación siguiendo mejores prácticas, con ejemplos claros y sin ser redundante.
---

# Instrucciones para GitHub Copilot en la Creación de Documentación

## Objetivo

Generar documentación clara, precisa y útil, que siga las mejores prácticas y estándares de la industria, sin ser compleja o pomposa.

## Recomendaciones para Copilot

- Usa un lenguaje simple y directo, evita tecnicismos innecesarios.
- Cubre todos los puntos importantes sin dejar información esencial fuera.
- Organiza la documentación en secciones lógicas y fáciles de seguir.
- Incorpora ejemplos prácticos cuando ayuden a la comprensión.
- Evita redundancias y explicaciones demasiado largas.
- Utiliza formatos estándar como Markdown con frontmatter YAML para títulos y descripciones.
- Usa listas, tablas o diagramas para clarificar conceptos cuando sea útil.
- Incluye enlaces a recursos oficiales o documentación complementaria.
- Mantén un tono profesional pero accesible, sin ser excesivamente formal.

## Aplicando principios de Clean Code a la documentación

- **Claridad ante todo:** la documentación debe ser fácil de leer y entender.
- **Simplicidad:** evita explicaciones innecesarias y complicaciones.
- **Consistencia:** usa estilos, formatos y estructuras uniformes en toda la documentación.
- **Modularidad:** divide el contenido en secciones y documentos pequeños y enfocados.
- **Nombres significativos:** usa títulos y nombres de archivos claros y representativos.
- **Evita duplicación:** si algo ya está documentado, referencia en lugar de repetir.
- **Actualización constante:** la documentación debe reflejar siempre el estado actual del proyecto.

## Estructura sugerida para documentos

La siguiente estructura es una recomendación para ayudar a organizar la documentación de forma clara y coherente.
No es obligatorio incluir todos los campos si no aplican al contenido específico.

1. **Título claro y descriptivo**
2. **Introducción breve**: qué trata el documento y para quién es.
3. **Objetivo**: qué se busca lograr con este contenido.
4. **Alcance**: límites o contexto donde aplica.
5. **Detalles / Contenido principal**: explicación ordenada y completa.
6. **Ejemplos**: si aplican, para ilustrar conceptos.
7. **Referencias**: links o documentos relacionados.
8. **Resumen o conclusión** (opcional).

## Ejemplo básico de frontmatter YAML con organización para Docusaurus

```md
---
id: 01-repositorios
sidebar_position: 1
title: Repositorios
description: Normas para nombrar y organizar repositorios de código.
---
