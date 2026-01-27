# Observabilidad desde el Diseño

## Enunciado
La observabilidad debe ser una propiedad arquitectónica integrada desde el diseño del sistema.

## Intención
Permitir entender el comportamiento interno del sistema sin depender de suposiciones o acceso directo a la infraestructura.

## Alcance conceptual
Aplica a sistemas distribuidos y no distribuidos.
Es especialmente crítica en arquitecturas desacopladas.

## Implicaciones arquitectónicas
- El sistema debe poder explicar su comportamiento.
- Los flujos deben ser rastreables end-to-end.
- Los fallos deben ser detectables y diagnosticables.
- La observabilidad influye en decisiones de diseño.

## Compensaciones (trade-offs)
Introduce sobrecarga conceptual y operativa, a cambio de mayor confiabilidad, capacidad de diagnóstico y control operativo.
