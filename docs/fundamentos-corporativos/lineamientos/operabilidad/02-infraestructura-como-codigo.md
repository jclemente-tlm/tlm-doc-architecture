---
id: infraestructura-como-codigo
sidebar_position: 2
title: Infraestructura como Código
description: Gestión de infraestructura mediante código versionado y reproducible
---

# Infraestructura como Código

La gestión manual de infraestructura mediante consolas genera configuraciones no documentadas, deriva entre entornos y ausencia de trazabilidad que dificultan auditorías y reproducibilidad. Cambios manuales crean inconsistencias, riesgos de seguridad y dependencia de conocimiento tribal para mantener ambientes. Definir infraestructura como código versionado permite revisiones de pares, automatización completa, reproducibilidad exacta entre entornos y trazabilidad de cambios mediante Git, transformando infraestructura en artefacto gestionable con prácticas de ingeniería de software.

**Este lineamiento aplica a:** Recursos cloud (compute, storage, networking), configuración de plataforma, políticas y permisos, networking y seguridad, bases de datos y servicios gestionados.

## Estándares Obligatorios

- [Definir infraestructura mediante código](../../estandares/operabilidad/infrastructure-as-code.md)
- [Versionar código de infraestructura en repositorios](../../estandares/operabilidad/iac-versionado.md)
- [Aplicar revisión de código a infraestructura](../../estandares/operabilidad/code-review-policy.md)
- [Documentar dependencias y orden de aprovisionamiento](../../estandares/operabilidad/iac-dependencias.md)
