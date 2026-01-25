---
id: despliegue-y-cloud-native
sidebar_position: 3
title: Despliegue y Cloud Native
description: Lineamientos para despliegue automatizado, elasticidad y resiliencia en cloud
---

# Despliegue y Cloud Native

## 1. Propósito

Garantizar que los sistemas se desplieguen de forma automatizada, sean resilientes por diseño y aprovechen las capacidades cloud para elasticidad y disponibilidad.

---

## 2. Alcance

Aplica a:

- Aplicaciones cloud native (nuevas)
- Migración de aplicaciones a cloud
- Servicios containerizados
- Plataformas multi-tenant

No aplica a:

- Aplicaciones on-premise sin planes de migración
- Sistemas legacy sin containerización

---

## 3. Lineamientos Obligatorios

**Despliegue:**

- Automatizar 100% del proceso de despliegue (CI/CD)
- Usar contenedores para portabilidad y consistencia
- Implementar estrategias de despliegue seguras (blue-green, canary)
- Versionado semántico de artefactos desplegables

**Configuración:**

- Externalizar configuración (12-factor app)
- Gestionar secretos con servicios dedicados (AWS Secrets Manager, Vault)
- Variables de entorno para configuración por entorno
- Nunca hardcodear configuraciones en código

**Diseño cloud native:**

- Diseñar servicios como stateless (estado en BD/cache externo)
- Preparar para escalado horizontal automático
- Implementar health checks y readiness probes
- Asumir que los componentes fallarán

---

## 4. Decisiones de Diseño Esperadas

- Pipeline de CI/CD completo (build, test, deploy)
- Estrategia de contenedorización (Dockerfile, imágenes base)
- Gestión de secretos y configuración
- Políticas de auto-scaling (métricas, umbrales)
- Estrategia de rollback ante fallos
- Topología de despliegue multi-región (si aplica)

---

## 5. Antipatrones y Prácticas Prohibidas

- Despliegues manuales a producción
- Estado persistido en filesystem del contenedor
- Configuración hardcodeada por entorno
- Dependencias de infraestructura no documentadas
- Servicios stateful sin estrategia de persistencia
- Secretos en código o repositorio

---

## 6. Principios Relacionados

- Arquitectura Cloud Native
- Automatización como Principio
- Infraestructura como Código
- Resiliencia y Tolerancia a Fallos
- Consistencia entre Entornos

---

## 7. Validación y Cumplimiento

- Verificación de pipeline CI/CD funcional
- Auditoría de configuración externalizada
- Escaneo de secretos en código
- Pruebas de escalado automático
- Validación de health checks
- Documentación en ADR de estrategia de despliegue
