<!-- # Seguridad desde el Diseño

## Enunciado

La seguridad debe considerarse una propiedad inherente del sistema desde su definición arquitectónica.

## Intención

Evitar arquitecturas que dependan de controles externos o correctivos tardíos.

## Alcance conceptual

Aplica a todo sistema sin excepción.

## Implicaciones arquitectónicas

- La seguridad influye en decisiones estructurales.
- Se consideran escenarios de abuso.
- La arquitectura reduce superficie de ataque.

## Compensaciones (trade-offs)

Puede aumentar complejidad inicial, a cambio de menor riesgo y mayor control. -->

# Seguridad desde el Diseño

## Declaración del Principio
La seguridad debe ser considerada explícitamente en las decisiones arquitectónicas iniciales del sistema y no añadirse posteriormente como un conjunto de controles aislados.

## Propósito
Reducir riesgos previsibles desde la estructura del sistema, evitando depender únicamente de controles correctivos o configuraciones posteriores.

## Justificación
Las decisiones arquitectónicas determinan:

- Qué componentes existen y cómo se relacionan
- Qué capacidades se exponen y a quién
- Cómo circulan los datos dentro y fuera del sistema
- Dónde se establecen los límites de confianza

Si estos aspectos se definen sin considerar seguridad, los controles añadidos posteriormente solo mitigan síntomas y no eliminan las causas del riesgo, generando soluciones frágiles y costosas de corregir.

## Alcance Conceptual
Aplica a decisiones relacionadas con:

- Definición de componentes, responsabilidades y dependencias
- Exposición de servicios, APIs, eventos e integraciones
- Flujo, persistencia y acceso a datos
- Identificación de activos críticos y puntos de acceso

Este principio no reemplaza controles técnicos, sino que define el marco en el que dichos controles son coherentes y efectivos.

## Implicaciones Arquitectónicas
- Identificación temprana de componentes y datos críticos.
- Definición explícita de límites y relaciones de confianza.
- Exposición intencional y mínima de capacidades.
- Estructuras que dificulten el acceso no autorizado por diseño.
- Consideración de escenarios de uso indebido desde la arquitectura.

## Compensaciones (Trade-offs)
Requiere mayor análisis y discusión en etapas tempranas del diseño, a cambio de reducir significativamente el riesgo, la deuda técnica en seguridad y los costos de corrección posteriores.

## Relación con Decisiones Arquitectónicas (ADRs)
Este principio se materializa en ADRs relacionados con:

- Límites entre sistemas y dominios
- Estrategias de integración y exposición
- Modelos de acceso y confianza
- Manejo y circulación de datos sensibles
