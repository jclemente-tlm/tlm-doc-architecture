---
id: consistencia-entre-entornos
sidebar_position: 3
title: Consistencia entre Entornos
description: Paridad entre entornos para reducir "funciona en mi máquina"
---

# Consistencia entre Entornos

La divergencia entre entornos de desarrollo, QA y producción genera el síndrome "funciona en mi máquina", donde código validado localmente falla en producción por diferencias en versiones de dependencias, configuraciones o variables de entorno. Estas inconsistencias dificultan diagnóstico de problemas, invalidan pruebas y generan incidentes evitables. Contenedorizar aplicaciones, gestionar configuración externamente y validar paridad entre ambientes garantiza comportamiento predecible, reduce riesgos de despliegue y permite debugging efectivo al reproducir condiciones de producción.

**Este lineamiento aplica a:** Entornos locales de desarrollo, entornos de integración y QA, staging y pre-producción, producción, contenedores y orquestación.

## Estándares Obligatorios

- [Garantizar paridad entre dev y producción](../../estandares/operabilidad/dev-prod-parity.md)
- [Externalizar configuración en variables de entorno](../../estandares/infraestructura/externalizar-configuracion-12factor.md)
