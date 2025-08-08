---
id: 01-repositorios
sidebar_position: 1
title: Repositorios
---

## Introducción

Este documento establece las reglas corporativas para la nomenclatura de repositorios en GitHub, el idioma preferente y la estructura mínima de documentación.

## Objetivo

Definir un estándar claro y consistente para nombrar repositorios, facilitando la identificación, clasificación y mantenimiento de los proyectos.

## Alcance

Aplica a todos los equipos de desarrollo, arquitectura, operaciones e infraestructura de la organización.

---

## Prefijo corporativo

Todos los repositorios deben comenzar con el prefijo de la empresa:

**tlm → `tlm-`**

Ejemplo: `tlm-svc-orders`.

---

## Formato de nombres de repositorios

Usamos un formato claro y consistente:

`tlm-<categoria>-<nombre>[-<subtipo>]`

- `<categoria>`: indica el propósito/ámbito del repositorio (ver tabla abajo).
- `<nombre>`: nombre corto, legible y en inglés (sin tildes ni espacios; usa guiones `-`).
- `<subtipo>` (opcional): para precisar, p. ej. `api`, `worker`, `docs`, `infra`.

**Reglas de estilo:**

- minúsculas, guiones (`-`) como separador.
- no caracteres especiales, no espacios, no acentos.
- mantener el nombre razonablemente corto (ideal < 40 caracteres).
- evitar siglas poco claras: si usas una sigla, defínela en el README.

---

### Tabla de categorías (ejemplos)

| Categoría | Uso                                              | Ejemplo de repo           |
|-----------|-------------------------------------------------|--------------------------|
| doc       | Repositorios netamente de documentación y portales (Docusaurus) | `tlm-doc-architecture`    |
| svc       | Microservicio o servicio backend                 | `tlm-svc-orders`          |
| app       | Aplicación monolítica o portal                    | `tlm-app-erp`             |
| int       | Capa de integración / conectores / CDC / middleware | `tlm-int-cdc-kafka`       |
| corp      | Servicios corporativos (agrupan varias funciones internas) | `tlm-corp-notifications`  |
| arc       | Arquetipos / plantillas para iniciar proyectos   | `tlm-arc-api-rest`        |
| lib       | Librerías internas / SDKs                         | `tlm-lib-logging`         |
| infra     | IaC, terraform, playbooks                         | `tlm-infra-kafka`         |
| ops       | Herramientas operativas / scripts                 | `tlm-ops-ci-tools`        |
| tpl       | Boilerplates, plantillas no code                  | `tlm-tpl-service-dotnet`  |
| api       | Repos con sólo definición de contratos (OpenAPI, schemas) | `tlm-api-orders`          |
| web       | Frontend web                                      | `tlm-web-portal-clientes` |

---

**Decisión:** elegir una categoría por repo; si un repo hace varias cosas, priorizar su propósito principal.

---

## Ejemplos de nombres correctos e incorrectos

| Correcto               | Incorrecto         | Explicación                                      |
|------------------------|-------------------|--------------------------------------------------|
| tlm-svc-orders         | orders-tlm        | Prefijo corporativo al inicio                    |
| tlm-api-users          | tlm_users         | Usa guiones, no guion bajo                      |
| tlm-docs-architecture  | docs-tlm-arch     | Prefijo y orden correcto                        |
| tlm-infra-pipelines    | infra-tlm         | Prefijo y categoría al inicio                   |
| tlm-svc-payments       | svc-payments-tlm  | Prefijo y categoría juntos, no al final         |
| tlm-svc-user-profile   | tlm-svc-userprofile| Palabras separadas por guión, no juntas         |

## Buenas prácticas

- Usa nombres descriptivos y consistentes.
- Evita abreviaturas poco claras.
- Mantén la documentación mínima en cada repositorio.

## Referencias

- [Guía oficial de GitHub](https://docs.github.com/es/repositories/creating-and-managing-repositories/about-repositories)
- [Documentación interna de Talma](../README.md)

## Última revisión

- Fecha: 2025-08-08
- Responsable: Equipo de Arquitectura
