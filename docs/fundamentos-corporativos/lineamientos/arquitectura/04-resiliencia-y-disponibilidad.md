# Integración y Comunicación

## 1. Propósito
Definir cómo los componentes, servicios y sistemas intercambian información de manera coherente, segura y mantenible.

---

## 2. Alcance
Aplica a:

- APIs internas y externas
- Eventos y flujos asíncronos
- Integraciones batch y en tiempo real

---

## 3. Lineamientos Obligatorios
- Utilizar contratos explícitos para intercambio de datos.
- Separar comunicación síncrona de asíncrona según necesidad.
- Evitar acoplamiento directo entre productores y consumidores.
- Documentar protocolos, formatos y restricciones de comunicación.

---

## 4. Decisiones de Diseño Esperadas
- Definición de contratos y versiones de APIs o eventos.
- Estrategia de comunicación (síncrona/asíncrona).
- Mecanismos de manejo de errores y resiliencia.
- Documentación de dependencias entre sistemas y servicios.

---

## 5. Antipatrones y Prácticas Prohibidas
- Comunicación implícita entre sistemas.
- Dependencias ocultas de datos.
- Eventos o APIs sin contratos ni versionado.
- Acoplamiento fuerte sin separación de responsabilidades.

---

## 6. Principios Relacionados
- Contratos de Integración
- Contratos de Datos
- Microservicios
- Resiliencia y Tolerancia a Fallos

---

## 7. Validación y Cumplimiento
- Revisión de contratos y dependencias antes de producción.
- Documentación en ADRs de integraciones.
- Auditoría de comunicación y versionado.
