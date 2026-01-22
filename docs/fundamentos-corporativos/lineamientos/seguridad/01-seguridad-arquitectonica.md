---
id: 01-seguridad-arquitectonica
sidebar_position: 1
title: Seguridad Arquitectónica
---

<!-- ## Principios

- Valida y sanitiza todas las entradas del usuario.
- Usa autenticación y autorización robustas.
- No expongas información sensible en logs o mensajes de error.
- Mantén las dependencias actualizadas.

## Buenas prácticas

- Usa herramientas de análisis estático.
- Aplica el principio de menor privilegio.
- Revisa el código para detectar vulnerabilidades. -->


# Seguridad Arquitectónica

## Propósito
Establecer lineamientos arquitectónicos para incorporar la seguridad como una propiedad inherente del sistema, asegurando que sea considerada desde las primeras decisiones de diseño y no como un agregado posterior.

## Alcance
Aplica a todos los sistemas, servicios y componentes diseñados, modificados o integrados bajo la arquitectura corporativa.

## Criterios Arquitectónicos

### Seguridad desde el Diseño (Security by Design)
La arquitectura debe considerar la seguridad desde las decisiones iniciales de diseño.

Los sistemas deben:
- Diseñar componentes considerando escenarios de abuso y uso indebido
- Reducir la superficie de ataque mediante exposición controlada
- Evitar dependencias innecesarias o implícitas
- Preferir configuraciones seguras por defecto

La ausencia de controles de seguridad explícitos se considera un defecto de diseño arquitectónico.

---

### Modelado de Amenazas (Threat Modeling)
La arquitectura debe incorporar análisis sistemático de amenazas como parte del diseño.

El análisis debe incluir:
- Identificación de activos críticos
- Identificación de actores y fuentes de amenaza
- Evaluación de vectores de ataque
- Análisis de impacto y probabilidad

El modelado de amenazas es obligatorio en los siguientes casos:
- Diseño de nuevos sistemas
- Cambios arquitectónicos relevantes
- Exposición de nuevas interfaces, integraciones o canales de acceso

---

### Definición de Límites de Confianza (Trust Boundaries)
La arquitectura debe definir explícitamente los límites de confianza del sistema.

Estos límites deben identificarse:
- Entre sistemas internos y externos
- Entre capas de la solución
- Entre servicios o componentes
- Entre tenants, dominios o contextos organizacionales

Todo cruce de un límite de confianza debe implicar controles explícitos de validación, autenticación y autorización.

---

## Antipatrones
- Asumir que entornos internos o redes privadas son confiables por defecto
- Delegar completamente la seguridad a la infraestructura o al entorno de despliegue
- Incorporar controles de seguridad únicamente en etapas finales del ciclo de vida
- Reutilizar credenciales, secretos o identidades entre componentes

## Resultado Esperado
Arquitecturas con seguridad integrada, coherente y auditable, alineadas con los objetivos de protección y gobierno del sistema.
