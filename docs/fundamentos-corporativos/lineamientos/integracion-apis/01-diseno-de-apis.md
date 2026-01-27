# Diseño de APIs

## Propósito
Definir criterios arquitectónicos para el diseño de APIs como mecanismos de integración entre sistemas, asegurando alineación con el dominio de negocio, desacoplamiento y evolución controlada.

## Alcance
Aplica a todas las APIs expuestas para consumo interno o externo, independientemente del protocolo o tecnología utilizada.

## Criterios Arquitectónicos

### Diseño orientado a dominio
- Las APIs deben exponer **capacidades de negocio**, no estructuras técnicas internas.
- Los recursos u operaciones deben reflejar **conceptos del dominio**, no tablas o entidades persistentes.
- La semántica de la API debe ser estable y comprensible fuera del contexto técnico.

### APIs como contratos
- Una API es un **contrato formal** entre productor y consumidor.
- El contrato es independiente de la implementación interna.
- Los cambios en una API deben evaluarse por su impacto en los consumidores.

### Separación experiencia / sistema
- Las APIs orientadas a experiencia (canales, clientes) no deben acoplarse a sistemas internos.
- Las APIs de sistema exponen capacidades reutilizables del dominio.
- No se permite que un sistema interno dependa directamente de una API diseñada para experiencia.

## Antipatrones
- APIs que reflejan modelos internos o estructuras de base de datos.
- Endpoints genéricos sin semántica de negocio clara.
- Uso de APIs como mecanismo de integración temporal sin contrato estable.
- Mezclar responsabilidades de experiencia y sistema en una misma API.

## Resultado Esperado
APIs claras, estables y alineadas al dominio, que permiten integración sostenible y evolución independiente de los sistemas.
