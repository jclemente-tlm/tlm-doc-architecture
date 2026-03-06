---
id: configuracion-entornos
sidebar_position: 3
title: Configuración y Consistencia de Entornos
description: Externalización de configuración y paridad entre entornos para reducir "funciona en mi máquina"
---

# Configuración y Consistencia de Entornos

La divergencia entre entornos de desarrollo, QA y producción genera el síndrome "funciona en mi máquina", donde código validado localmente falla en producción por diferencias en versiones de dependencias, configuraciones hardcodeadas o variables de entorno inconsistentes. Configuración embebida en código impide portabilidad entre entornos y crea riesgos de seguridad al exponer secrets en repositorios. Estas inconsistencias dificultan diagnóstico de problemas, invalidan pruebas y generan incidentes evitables. Externalizar configuración en variables de entorno según 12-Factor App, contenerizar aplicaciones y garantizar paridad entre ambientes asegura comportamiento predecible, reduce riesgos de despliegue y permite debugging efectivo al reproducir condiciones de producción.

**Este lineamiento aplica a:** Entornos locales de desarrollo, entornos de integración y QA, staging y pre-producción, producción, configuración de aplicaciones, secrets y credenciales, contenedores y orquestación.

## Estándares Obligatorios

- [Externalizar configuración (12-Factor App)](../../estandares/infraestructura/externalize-configuration.md)
- [Gestionar secretos de forma segura](../../estandares/seguridad/secrets-key-management.md#1-secrets-management)
- [Gestionar configuración centralizada](../../estandares/infraestructura/centralized-configuration.md)
- [Garantizar paridad entre entornos](../../estandares/infraestructura/environment-parity.md)
- [Gestionar variables por entorno](../../estandares/infraestructura/externalize-configuration.md)
- [Nunca hardcodear configuración](../../estandares/desarrollo/app-configuration.md)
