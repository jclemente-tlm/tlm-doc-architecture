---
id: contratos-y-esquemas
sidebar_position: 2
title: Contratos y Esquemas
description: Definición explícita de contratos de datos y esquemas versionados
---

# Contratos y Esquemas

## 1. Propósito

Garantizar que todo intercambio de datos entre sistemas, servicios o componentes cuente con contratos explícitos, versionados y documentados que faciliten evolución y compatibilidad.

---

## 2. Alcance

Aplica a:

- APIs REST y GraphQL
- Mensajes y eventos asíncronos
- Esquemas de bases de datos compartidos (casos excepcionales)
- Archivos de intercambio (CSV, JSON, XML)
- Integraciones con sistemas externos

---

## 3. Lineamientos Obligatorios

- Definir esquemas explícitos para todos los datos intercambiados
- Versionar contratos de datos (semántico: major.minor.patch)
- Documentar cambios y compatibilidad entre versiones
- Validar datos contra esquemas en tiempo de ejecución
- Mantener retrocompatibilidad o gestionar breaking changes explícitamente

---

## 4. Decisiones de Diseño Esperadas

- Formato de esquemas (OpenAPI, JSON Schema, Avro, Protobuf)
- Estrategia de versionado de contratos
- Política de breaking changes y deprecación
- Herramientas de validación de esquemas
- Registro centralizado de contratos (schema registry)

---

## 5. Antipatrones y Prácticas Prohibidas

- Intercambio de datos sin esquema definido
- Breaking changes sin incremento de versión mayor
- Validación solo en cliente, no en servidor
- Esquemas no versionados o sin documentación
- Cambios implícitos en estructura de datos

---

## 6. Principios Relacionados

- Contratos de Datos
- Contratos de Integración
- Arquitectura Evolutiva
- Desacoplamiento y Autonomía

---

## 7. Validación y Cumplimiento

- Revisión de esquemas en code reviews
- Validación automática de breaking changes en CI/CD
- Tests de compatibilidad entre versiones
- Documentación de contratos en repositorio centralizado
- Auditoría de uso de versiones deprecadas
