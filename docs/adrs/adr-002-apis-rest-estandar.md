# ADR-002: Elección de tecnología para la API

Fecha: 2023-10-05

Estado: Aprobado

## Contexto

Se necesita exponer una API para que los clientes puedan acceder a nuestros servicios de manera segura y eficiente. Se evaluaron varias tecnologías para determinar cuál sería la más adecuada para nuestras necesidades.

## Decisión

Se ha decidido utilizar **REST sobre HTTP/2** con autenticación OAuth 2.0 para la implementación de nuestra API. Esta decisión se basa en la necesidad de estandarización, facilidad de uso y amplia compatibilidad con clientes existentes.

## Alternativas consideradas

- **GraphQL:** Aunque ofrece flexibilidad en las consultas, introduce una complejidad adicional en la implementación y no es tan estandarizado como REST.
- **gRPC:** Proporciona un alto rendimiento y es ideal para la comunicación entre servicios internos, pero no es el mejor enfoque para APIs públicas debido a su menor compatibilidad con clientes web y su complejidad adicional.
- **SOAP:** Es un protocolo estándar para el intercambio de información estructurada, pero se considera obsoleto para nuevos desarrollos debido a su complejidad y a la sobrecarga que implica.

## Alternativas descartadas

- **GraphQL:** mayor complejidad y menor estandarización para APIs públicas
- **gRPC:** no adecuado para consumo externo masivo, menor compatibilidad con clientes web
- **SOAP:** obsoleto para nuevos desarrollos, mayor complejidad

---

Fecha de la próxima revisión: 2024-10-05