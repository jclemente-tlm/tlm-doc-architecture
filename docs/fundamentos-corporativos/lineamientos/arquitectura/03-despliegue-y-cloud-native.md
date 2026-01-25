# Despliegue y Cloud-Native

## 1. Propósito
Establecer lineamientos para el despliegue de soluciones, asegurando automatización, elasticidad y resiliencia en entornos cloud o distribuidos.

---

## 2. Alcance
Aplica a todas las soluciones que operen en:

- Plataformas cloud (públicas, privadas o híbridas)
- Entornos distribuidos y multi-tenant
- Integraciones críticas y servicios escalables

---

## 3. Lineamientos Obligatorios
- Automatizar despliegues y configuración.
- Gestionar estado y configuración de forma externa al código.
- Diseñar para tolerancia a fallos y reemplazo de componentes.
- Documentar estrategias de escalado y recuperación.

---

## 4. Decisiones de Diseño Esperadas
- Estrategia de despliegue automatizada y reproducible.
- Definición de dependencias de infraestructura.
- Políticas de escalado y recuperación ante fallos.
- Documentación de entornos y configuraciones críticas.

---

## 5. Antipatrones y Prácticas Prohibidas
- Despliegues manuales o ad-hoc.
- Estado embebido en servicios sin respaldo externo.
- Dependencias implícitas de infraestructura.
- Configuración hardcodeada o no versionada.

---

## 6. Principios Relacionados
- Cloud-Native
- Resiliencia y Tolerancia a Fallos
- Observabilidad desde el Diseño
- Automatización como Principio

---

## 7. Validación y Cumplimiento
- Revisión de pipelines de despliegue.
- Auditoría de configuración y escalabilidad.
- Documentación de estrategias en ADRs.
