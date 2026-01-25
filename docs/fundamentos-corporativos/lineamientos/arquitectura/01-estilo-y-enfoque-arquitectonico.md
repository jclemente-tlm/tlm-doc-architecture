# Estilo y Enfoque Arquitectónico

## 1. Propósito

Definir los estilos arquitectónicos permitidos, criterios de selección y límites, asegurando soluciones sostenibles, escalables y alineadas al negocio.

---

## 2. Alcance

Aplica a todas las soluciones desarrolladas por la organización:

- Aplicaciones internas y externas
- Plataformas distribuidas y monolitos
- Integraciones internas y con terceros

No aplica a configuraciones operativas específicas ni decisiones tecnológicas menores que no impacten la arquitectura general.

---

## 3. Lineamientos Obligatorios

- Seleccionar un **estilo arquitectónico** válido y documentado.
- No mezclar estilos sin justificación aprobada.
- Estilos permitidos:
  - **Monolito Modular:** dominios acotados, bajo cambio, equipos pequeños.
    - Separación clara de módulos
    - Dependencias unidireccionales
    - Evolución posible hacia arquitectura distribuida
  - **Microservicios:** dominios desacoplables, crecimiento sostenido, múltiples equipos autónomos.
    - Cada servicio representa una capacidad de negocio
    - Autonomía en despliegue y evolución
    - Datos encapsulados por servicio
    - Comunicación mediante contratos explícitos
  - **Arquitectura Orientada a Eventos:** desacoplamiento temporal, flujos asíncronos, alta resiliencia.
    - Eventos representan hechos del dominio
    - Productores desconocen a los consumidores
    - Consistencia eventual tolerada

---

## 4. Decisiones de Diseño Esperadas

- Definición clara del estilo arquitectónico adoptado.
- Documentación de límites y responsabilidades de módulos o servicios.
- Estrategia de comunicación entre componentes (síncrona o asíncrona) alineada al estilo.
- Justificación de desviaciones respecto a los estilos definidos.

---

## 5. Antipatrones y Prácticas Prohibidas

- Selección de estilo basada en moda o tecnología.
- Microservicios para dominios triviales o con bajo cambio.
- Mezcla de estilos sin reglas claras.
- Dependencias técnicas ocultas o acoplamiento no documentado.

---

## 6. Principios Relacionados

- Arquitectura Limpia
- Arquitectura de Microservicios
- Arquitectura Orientada a Eventos
- Simplicidad Intencional
- Desacoplamiento y Autonomía

---

## 7. Validación y Cumplimiento

- Revisiones de arquitectura antes de producción.
- Documentación de decisiones arquitectónicas y estilo adoptado en ADRs.
- Auditorías internas para verificar límites, responsabilidades y comunicación entre componentes.
