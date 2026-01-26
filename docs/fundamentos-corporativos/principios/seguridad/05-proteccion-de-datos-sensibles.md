---
sidebar_position: 5
---

# Protección de Datos Sensibles

## Declaración del Principio

La arquitectura debe identificar, clasificar y proteger explícitamente los datos sensibles, asegurando que su almacenamiento, procesamiento y exposición estén alineados con su nivel de criticidad y riesgo.

## Propósito

Reducir el riesgo de exposición, uso indebido o pérdida de información crítica, garantizando que los datos sensibles reciban un tratamiento diferenciado y coherente desde el diseño del sistema.

## Justificación

No todos los datos tienen el mismo valor ni el mismo impacto ante una brecha de seguridad.
Cuando los sistemas tratan toda la información de forma uniforme:

- Se exponen datos críticos innecesariamente
- Se incrementa la superficie de ataque
- Se dificulta el cumplimiento normativo y la auditoría

La protección efectiva de datos sensibles comienza identificándolos y estableciendo decisiones arquitectónicas acordes a su nivel de riesgo, no solo aplicando controles técnicos posteriores.

## Alcance Conceptual

Este principio aplica a:

- Datos personales y sensibles
- Información financiera, contractual o regulada
- Credenciales, secretos y tokens
- Datos críticos para el negocio

Cubre todo el ciclo de vida del dato: generación, transporte, almacenamiento, acceso, uso y eliminación.

## Implicaciones Arquitectónicas

- Los datos sensibles deben identificarse y clasificarse explícitamente.
- El acceso a datos sensibles debe estar estrictamente controlado y justificado.
- La exposición de datos debe minimizarse por diseño.
- La arquitectura debe considerar segregación, aislamiento y protección diferencial.
- Los flujos de datos sensibles deben ser visibles y trazables.
- La persistencia y transporte de datos sensibles requieren medidas adicionales desde el diseño.

## Compensaciones (Trade-offs)

Introduce mayor complejidad en diseño, operación y gobierno de datos, a cambio de reducir significativamente el impacto de incidentes de seguridad, facilitar el cumplimiento normativo y proteger activos críticos del negocio.

## Relación con Decisiones Arquitectónicas (ADRs)

Este principio se refleja en ADRs relacionados con:

- Clasificación y manejo de datos
- Estrategias de almacenamiento y segregación
- Políticas de acceso y exposición de información
- Manejo de secretos y credenciales
- Retención y eliminación de datos
