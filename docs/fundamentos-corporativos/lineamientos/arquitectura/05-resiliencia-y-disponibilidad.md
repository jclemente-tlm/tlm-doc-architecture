# Resiliencia y Disponibilidad

## Propósito

Establecer principios arquitectónicos para diseñar sistemas tolerantes a fallos, capaces de mantener niveles aceptables de servicio ante errores, picos de carga o fallos parciales.

## Alcance

Aplica a todos los sistemas, servicios y componentes desplegados en ambientes productivos y no productivos, independientemente del estilo arquitectónico adoptado.

## Criterios Arquitectónicos

### Manejo de fallos
- Se deben definir **timeouts explícitos** para toda comunicación remota.
- Los **reintentos (retries)** deben ser limitados y controlados, evitando bucles infinitos o sobrecarga.
- Se deben implementar **circuit breakers** para aislar fallos y prevenir propagación de errores.

### SLA y SLO (conceptual)
- Cada sistema debe definir de manera conceptual sus **expectativas de disponibilidad y rendimiento (SLA/SLO)**.
- La arquitectura debe ser coherente con los objetivos de servicio definidos.

### Degradación controlada
- Los sistemas deben soportar **degradación controlada**, priorizando funcionalidades críticas.
- El diseño debe prevenir **fallos en cascada** entre componentes o servicios dependientes.

## Antipatrones

- Reintentos ilimitados sin control de tiempo o cantidad.
- Dependencia de disponibilidad total de servicios externos.
- Fallos no controlados que afectan a múltiples componentes.
- Diseños que no consideran degradación funcional.

## Resultado Esperado

Sistemas resilientes, predecibles ante fallos y alineados a objetivos de disponibilidad definidos, reduciendo el impacto operativo y mejorando la continuidad del negocio.
