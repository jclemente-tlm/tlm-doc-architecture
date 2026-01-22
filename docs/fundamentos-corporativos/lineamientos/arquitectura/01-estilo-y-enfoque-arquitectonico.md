# Estilo y Enfoque Arquitectónico

## Propósito

Definir los estilos arquitectónicos permitidos en la organización, los criterios para su selección y los límites que deben respetarse, con el objetivo de construir soluciones sostenibles, evolutivas y alineadas al negocio.

Este documento establece **criterios arquitectónicos**, no tecnologías ni frameworks.

---

## Estilos arquitectónicos permitidos

### Monolito Modular

Aplicable cuando:

- El dominio es acotado y bien comprendido
- El ritmo de cambio es bajo o moderado
- El equipo es reducido o centralizado
- La complejidad operativa debe mantenerse baja

Criterios obligatorios:

- Separación explícita de módulos por responsabilidad
- Dependencias unidireccionales entre módulos
- Prohibición de dependencias circulares
- Capacidad de evolución hacia una arquitectura distribuida

---

### Arquitectura de Microservicios

Aplicable cuando:

- Existen dominios claramente desacoplables
- Se requiere escalabilidad independiente
- Hay múltiples equipos con autonomía
- El dominio presenta alta variabilidad o crecimiento

Criterios obligatorios:

- Cada servicio representa una capacidad de negocio
- Autonomía en despliegue y evolución
- Datos encapsulados por servicio
- Comunicación mediante contratos explícitos

---

### Arquitectura Orientada a Eventos

Aplicable cuando:

- Se requiere desacoplamiento temporal
- Se manejan flujos asíncronos
- Existen múltiples consumidores de información
- Se prioriza escalabilidad y resiliencia

Criterios obligatorios:

- Eventos representan hechos del dominio
- Productores desconocen a los consumidores
- Diseño tolerante a consistencia eventual

---

## Antipatrones a evitar

- Uso de microservicios sin necesidad real
- Arquitecturas híbridas sin reglas claras
- Acoplamiento fuerte entre componentes
- Dependencias técnicas ocultas
- Selección de estilo basada en moda o tecnología
