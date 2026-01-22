# Descomposición y Límites Arquitectónicos

## Propósito

Establecer reglas claras para la descomposición de sistemas, la definición de límites y la asignación de responsabilidades, evitando arquitecturas acopladas y sistemas espagueti.

---

## Bounded Contexts

- Cada contexto representa un modelo de dominio consistente
- No se comparten modelos internos entre contextos
- La integración entre contextos se realiza mediante contratos

---

## Autonomía de servicios

Un servicio debe ser autónomo en:

- Evolución
- Despliegue
- Datos
- Decisiones internas de diseño

No se permite:

- Acceso directo a datos de otro servicio
- Dependencias implícitas de ejecución

---

## Reglas de dependencia

- Las dependencias deben ser explícitas
- Prohibidas dependencias circulares
- La comunicación entre dominios se realiza vía contratos
- Las dependencias técnicas no deben dictar el diseño del dominio

---

## Ownership técnico

- Cada servicio o contexto tiene un responsable claro
- El ownership incluye calidad, seguridad y evolución
- Las decisiones locales deben respetar principios globales
