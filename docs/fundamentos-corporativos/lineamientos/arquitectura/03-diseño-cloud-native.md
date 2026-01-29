---
id: diseno-cloud-native
sidebar_position: 3
title: Diseño Cloud Native
description: Principios de diseño para sistemas que operan en entornos cloud dinámicos y escalables
---

# Diseño Cloud Native

## 1. Propósito

Definir cómo diseñar sistemas que aprovechen las capacidades cloud (elasticidad, resiliencia, dinamismo) mediante principios arquitectónicos fundamentales.

> **Nota:** Para automatización de despliegues (CI/CD) ver [Automatización](../operabilidad/01-automatizacion.md). Para gestión de infraestructura ver [IaC](../operabilidad/02-infraestructura-como-codigo.md).

---

## 2. Alcance

Aplica a:

- Aplicaciones diseñadas para cloud (públicas, privadas, híbridas)
- Migración de aplicaciones a cloud
- Servicios distribuidos y containerizados
- Plataformas multi-tenant

No aplica a:

- Aplicaciones on-premise sin planes de migración
- Sistemas legacy sin evolución cloud

---

## 3. Lineamientos Obligatorios

**Principios 12-Factor App:**

- Externalizar toda la configuración (variables de entorno)
- Tratar logs como streams de eventos
- Procesos stateless (estado en servicios externos)
- Servicios backing como recursos adjuntos

**Diseño para resiliencia:**

- Asumir que componentes fallarán (design for failure)
- Implementar health checks (liveness, readiness)
- Preparar para terminación abrupta (graceful shutdown)
- Tolerar reemplazos de instancias sin pérdida de funcionalidad

**Escalabilidad horizontal:**

- Diseñar servicios para escalar horizontalmente (agregar instancias)
- Sin afinidad de sesión (session affinity)
- Sin estado local persistente
- Idempotencia en operaciones críticas

**Configuración y secretos:**

- Nunca hardcodear configuraciones
- Gestionar secretos en AWS Secrets Manager con rotación automática
- Configuración inyectada en runtime, no en build time

---

## 4. Decisiones de Diseño Esperadas

- Estrategia de externalización de configuración
- Gestión de secretos (herramienta, rotación, acceso)
- Diseño de health checks (qué verifican, timeouts)
- Estrategia de manejo de estado (BD, cache, storage)
- Políticas de auto-scaling (métricas trigger, límites)
- Topología de despliegue multi-región (si aplica)
- Manejo de graceful shutdown

---

## 5. Antipatrones y Prácticas Prohibidas

- Estado persistido en filesystem del contenedor
- Configuración hardcodeada por entorno
- Secretos en código, variables de entorno o repositorio
- Servicios que requieren instancias específicas (sticky sessions)
- Dependencias de IP o nombres de host estáticos
- Lógica que asume persistencia local
- Health checks que siempre retornan 200 sin validar dependencias

---

## 6. Principios Relacionados

- [Arquitectura Cloud Native](../../estilos-arquitectonicos/cloud-native.md)
- Resiliencia y Tolerancia a Fallos
- Consistencia entre Entornos
- Desacoplamiento y Autonomía

---

## 7. Validación y Cumplimiento

- Auditoría de configuración externalizada (no hardcodeada)
- Escaneo de secretos en código y configuración
- Pruebas de escalado horizontal (agregar/quitar instancias)
- Validación de health checks (liveness y readiness)
- Pruebas de chaos engineering (terminación de instancias)
- Verificación de graceful shutdown
- Documentación en ADR de decisiones cloud native
