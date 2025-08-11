# ADR-006: Elección de herramientas de monitoreo

## Estado

Propuesto

## Contexto

Se necesita una solución de monitoreo que se integre con el stack tecnológico actual y que permita la recolección de métricas y logs de las aplicaciones en tiempo real.

## Decisión

Se ha decidido utilizar herramientas de código abierto que se integren fácilmente con nuestra infraestructura existente y que ofrezcan flexibilidad y control sobre los datos.

## Alternativas consideradas

- **Prometheus + Grafana:** para métricas y visualización.
- **ELK Stack (Elasticsearch, Logstash, Kibana):** para recolección y visualización de logs.
- **Jaeger o Zipkin:** para trazado distribuido.

## Alternativas descartadas

- **No instrumentar:** sin observabilidad ni métricas
- **Herramientas propietarias:** lock-in, costos altos y menor flexibilidad
- **Herramientas open source no integradas:** mayor complejidad operativa

## Consecuencias

Se implementará un sistema de monitoreo basado en herramientas de código abierto, evitando el lock-in de proveedores y manteniendo la flexibilidad y control sobre nuestra infraestructura y datos.