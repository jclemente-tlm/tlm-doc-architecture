---
id: configuracion-entornos
sidebar_position: 2
title: Configuración y Consistencia de Entornos
description: Externalización de configuración y paridad entre entornos para reducir "funciona en mi máquina"
---

# Configuración y Consistencia de Entornos

La divergencia entre entornos de desarrollo, QA y producción genera el síndrome "funciona en mi máquina", donde código validado localmente falla en producción por diferencias en versiones de dependencias, configuraciones hardcodeadas o variables de entorno inconsistentes. Configuración embebida en código impide portabilidad entre entornos y crea riesgos de seguridad al exponer secrets en repositorios. Estas inconsistencias dificultan diagnóstico de problemas, invalidan pruebas y generan incidentes evitables. Externalizar configuración en variables de entorno según 12-Factor App, contenedorizar aplicaciones y garantizar paridad entre ambientes asegura comportamiento predecible, reduce riesgos de despliegue y permite debugging efectivo al reproducir condiciones de producción.

**Este lineamiento aplica a:** Entornos locales de desarrollo, entornos de integración y QA, staging y pre-producción, producción, configuración de aplicaciones, secrets y credenciales, contenedores y orquestación.

## Estándares Obligatorios

- [Externalizar configuración en variables de entorno (12-Factor)](../../estandares/infraestructura/externalize-configuration.md)
- [Gestionar secrets con AWS Secrets Manager](../../estandares/seguridad/secrets-key-management.md)
- [Contenedorizar aplicaciones para consistencia](../../estandares/infraestructura/contenedores.md)
