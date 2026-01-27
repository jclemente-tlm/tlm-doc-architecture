# Contratos y Versionado

## Propósito
Establecer criterios arquitectónicos para la evolución de contratos de integración, garantizando compatibilidad, estabilidad y control del impacto sobre los consumidores.

## Alcance
Aplica a todos los contratos de integración expuestos por la organización, incluyendo APIs síncronas y mecanismos asíncronos.

## Criterios Arquitectónicos

### Compatibilidad hacia atrás
- Los cambios deben preservar compatibilidad siempre que sea posible.
- Las extensiones son preferidas sobre modificaciones destructivas.
- Un consumidor existente no debe romperse por cambios no versionados.

### Estrategia de versionado
- El versionado debe ser explícito y predecible.
- Las versiones representan contratos distintos, no simples iteraciones técnicas.
- El versionado debe reflejar cambios semánticos relevantes para los consumidores.

### Deprecación
- Todo contrato a retirar debe pasar por un proceso de deprecación.
- La deprecación debe ser comunicada con anticipación suficiente.
- Debe coexistir más de una versión cuando sea necesario para transición controlada.

## Antipatrones
- Cambios incompatibles sin versionado.
- Versionar por cada cambio menor sin impacto real.
- Eliminar contratos sin estrategia de transición.
- Consumidores forzados a migrar sin planificación.

## Resultado Esperado
Contratos de integración estables, evolutivos y gobernables, que minimizan riesgos operativos y facilitan la adopción de cambios.
