# Contratos de Datos

## Enunciado
El intercambio de datos entre dominios debe realizarse mediante contratos explícitos y acordados.

## Intención
Evitar dependencias implícitas sobre estructuras internas de datos.

## Alcance conceptual
Aplica a integraciones, eventos, APIs y flujos batch.

## Implicaciones arquitectónicas
- Los esquemas expuestos son parte del contrato.
- Los cambios deben ser gestionados.
- El consumidor no asume detalles internos.

## Compensaciones (trade-offs)
Reduce flexibilidad inmediata a cambio de estabilidad, gobernanza y evolución controlada.
