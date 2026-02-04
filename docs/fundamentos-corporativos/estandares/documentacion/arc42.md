---
id: arc42
sidebar_position: 1
title: arc42 - Plantilla de Documentación
description: Estándar para documentar arquitecturas de software usando la plantilla arc42 con sus 12 secciones principales.
---

# Estándar Técnico — arc42 - Plantilla de Documentación

---

## 1. Propósito

Establecer arc42 como plantilla estándar para documentar arquitecturas de sistemas críticos en Markdown versionado con Git.

---

## 2. Alcance

**Aplica a:**

- Sistemas críticos de negocio
- Aplicaciones multi-equipo (>5 desarrolladores)
- Proyectos >6 meses de duración
- Migraciones y modernizaciones
- Integraciones complejas (>3 sistemas externos)

**No aplica a:**

- POCs simples (`<1` mes)
- Scripts de automatización
- Proyectos sin integraciones externas

---

## 3. Tecnologías Aprobadas

| Componente      | Tecnología         | Versión mínima  | Observaciones        |
| --------------- | ------------------ | --------------- | -------------------- |
| **Formato**     | Markdown           | CommonMark      | Documentación        |
| **Versionado**  | Git                | 2.40+           | Control versiones    |
| **Portal**      | Docusaurus         | 3.0+            | Publicación docs     |
| **Diagramas**   | Structurizr DSL    | 2.0+            | C4 Model (preferido) |
| **Alternativa** | PlantUML / Mermaid | 1.2024+ / 10.0+ | Diagramas UML        |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] arc42 con 12 secciones completas
- [ ] Markdown versionado en Git
- [ ] Integración con C4 Model para diagramas
- [ ] Docusaurus para publicación
- [ ] Sección 1: Introducción (propósito, stakeholders, objetivos)
- [ ] Sección 3: Contexto (fronteras del sistema)
- [ ] Sección 5: Vista Bloques (contenedores, componentes)
- [ ] Sección 9: ADRs (decisiones arquitectónicas)
- [ ] Sección 10: Requisitos Calidad (performance, seguridad)
- [ ] Actualización con cada cambio arquitectónico mayor
- [ ] Code review de documentación en PRs
- [ ] README.md con índice de navegación

---

## 5. Prohibiciones

- ❌ Documentación en formatos propietarios (Word, PowerPoint)
- ❌ Diagramas sin fuente editable (PNG/JPG sin .dsl/.puml)
- ❌ Documentación desactualizada (>3 meses sin cambios)
- ❌ Secciones vacías (marcar como "No aplica" si necesario)
- ❌ Diagramas en Draw.io/Lucidchart (usar Structurizr/PlantUML)
- ❌ Documentación fuera de Git (wikis separadas)
- ❌ Duplicación entre arc42 y otras fuentes

---

## 6. Configuración Mínima

```bash
# Estructura arc42 en repositorio
docs/
├── arquitectura/
│   ├── README.md                         # Índice principal
│   ├── 01-introduccion-objetivos.md
│   ├── 02-restricciones.md
│   ├── 03-contexto-alcance.md
│   ├── 04-estrategia-solucion.md
│   ├── 05-vista-bloques.md
│   ├── 06-vista-runtime.md
│   ├── 07-vista-despliegue.md
│   ├── 08-conceptos-transversales.md
│   ├── 09-decisiones-arquitectura.md      # Índice ADRs
│   ├── 10-requisitos-calidad.md
│   ├── 11-riesgos-deuda-tecnica.md
│   └── 12-glosario.md
├── diagramas/
│   ├── context.dsl                       # C4 Level 1
│   ├── containers.dsl                    # C4 Level 2
│   └── components/                       # C4 Level 3
└── decisiones/
    └── (Ver estándar ADRs)
```

```markdown
<!-- 01-introduccion-objetivos.md -->

# 1. Introducción y Objetivos

## Propósito

Sistema de Gestión de Usuarios (SGU) permite administración centralizada de usuarios, roles y permisos.

## Stakeholders

| Rol        | Expectativas                 |
| ---------- | ---------------------------- |
| Empleados  | Acceso rápido a aplicaciones |
| IT         | Gestión centralizada         |
| Compliance | Trazabilidad de accesos      |

## Objetivos de Negocio

- Centralizar gestión de identidades
- Reducir onboarding de 2 días a 2 horas
- Cumplir SOC 2 / ISO 27001

## Objetivos Técnicos

- SSO con OAuth 2.0 / OpenID Connect
- 99.9% uptime SLA
- <200ms respuesta (p95)
```

```markdown
<!-- 03-contexto-alcance.md -->

# 3. Contexto y Alcance

## Diagrama de Contexto

![Contexto](../../diagrams/context.png)

**Fuente**: [diagrams/context.dsl](../../diagrams/context.dsl)

## Fronteras del Sistema

**Dentro del alcance:**

- Autenticación/autorización
- Gestión usuarios/roles
- SSO con OAuth 2.0

**Fuera del alcance:**

- Provisionamiento hardware
- Gestión empleados (responsabilidad SAP HR)
```

---

## 7. Validación

```bash
# Validar links rotos
markdown-link-check docs/arquitectura/*.md

# Verificar estructura
ls docs/arquitectura/ | grep -E "0[1-9]|1[0-2]"

# Build documentación (si usa Docusaurus)
docusaurus build

# Preview local
docusaurus serve
```

**Métricas de cumplimiento:**

| Métrica                       | Target     | Verificación            |
| ----------------------------- | ---------- | ----------------------- |
| 12 secciones completas        | 100%       | `ls docs/arquitectura/` |
| Documentación actualizada     | `<3` meses | Git log commits         |
| Diagramas con fuente editable | 100%       | `.dsl`/`.puml` files    |
| Publicado en Docusaurus       | 100%       | URL accesible           |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [C4 Model](02-c4-model.md)
- [OpenAPI/Swagger](03-openapi-swagger.md)
- [arc42 Template](https://arc42.org/)
- [arc42 Examples](https://arc42.org/examples)
- [Structurizr DSL](https://structurizr.com/dsl)
