# Descomposición y Límites

## 1. Propósito

Definir cómo dividir sistemas en componentes, módulos o servicios, estableciendo límites claros de responsabilidad y propiedad para facilitar mantenimiento, evolución y gobernanza.

---

## 2. Alcance

Aplica a todas las soluciones desarrolladas por la organización, incluyendo:

- Monolitos modulares
- Microservicios
- Arquitecturas orientadas a eventos
- Integraciones internas y externas

---

## 3. Lineamientos Obligatorios

- Identificar límites de responsabilidad por componente o servicio.
- Evitar acoplamiento innecesario entre módulos.
- Documentar la propiedad de cada módulo o servicio.
- Garantizar coherencia en la comunicación y flujo de datos entre límites.

---

## 4. Decisiones de Diseño Esperadas

- Definición de límites claros por componente o servicio.
- Documentación de dependencias entre componentes.
- Mapas de responsabilidad y propiedad técnica y funcional.
- Estrategias de integración y comunicación entre componentes.

---

## 5. Antipatrones y Prácticas Prohibidas

- Componentes sin límites claros.
- Mezcla de responsabilidades en un mismo módulo o servicio.
- Acoplamiento oculto entre componentes.
- Comunicación ad-hoc sin contratos explícitos.

---

## 6. Principios Relacionados

- Arquitectura de Microservicios
- Desacoplamiento y Autonomía
- Contratos de Integración
- Simplicidad Intencional

---

## 7. Validación y Cumplimiento

- Revisiones de diseño para verificar límites y responsabilidades.
- Documentación de decisiones en ADRs.
- Auditorías internas sobre dependencias y propiedad de componentes.
