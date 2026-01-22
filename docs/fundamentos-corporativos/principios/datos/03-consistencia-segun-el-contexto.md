# Consistencia según el Contexto

## Enunciado
El nivel de consistencia de los datos debe definirse según el contexto y necesidades del dominio.

## Intención
Evitar imponer consistencia fuerte donde no es necesaria, o inconsistencia donde es crítica.

## Alcance conceptual
Aplica a sistemas distribuidos y orientados a eventos.
No existe un único modelo válido para todos los casos.

## Implicaciones arquitectónicas
- Se aceptan distintos modelos de consistencia.
- La consistencia es una decisión de diseño.
- El dominio define tolerancias y expectativas.

## Compensaciones (trade-offs)
Mayor complejidad conceptual a cambio de mejor escalabilidad y alineación con el negocio.
