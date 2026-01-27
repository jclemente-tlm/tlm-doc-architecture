# Manejo de Errores

## Propósito
Definir criterios arquitectónicos para el manejo consistente de errores en integraciones, permitiendo a los consumidores reaccionar de forma predecible y controlada.

## Alcance
Aplica a todas las APIs y mecanismos de integración expuestos por los sistemas.

## Criterios Arquitectónicos

### Errores técnicos vs funcionales
- Los errores técnicos representan fallos de infraestructura o sistema.
- Los errores funcionales representan reglas de negocio o validaciones.
- La arquitectura debe permitir distinguir claramente ambos tipos.

### Códigos estándar
- Los errores deben identificarse mediante códigos consistentes.
- Los códigos deben permitir clasificación y manejo automatizado.
- El significado del código debe ser estable en el tiempo.

### Mensajes consistentes
- Los mensajes de error deben ser claros y no ambiguos.
- No deben exponer detalles internos o sensibles.
- El formato del error debe ser uniforme entre APIs del mismo dominio.

## Antipatrones
- Uso de mensajes genéricos sin contexto.
- Exposición de excepciones internas o detalles técnicos.
- Errores no clasificados o inconsistentes entre servicios.
- Uso de mensajes distintos para el mismo tipo de error.

## Resultado Esperado
Manejo de errores predecible y consistente, que facilita integración robusta y reduce ambigüedad para los consumidores.
