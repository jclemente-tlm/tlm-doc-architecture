# 4. Estrategia de Solución

## 4.1 Decisiones Clave

| Decisión         | Alternativa Elegida         | Justificación                  |
|------------------|----------------------------|-------------------------------|
| **Arquitectura** | `API` + `Event Processor`  | Separación de responsabilidades |
| **Almacenamiento** | `Event Sourcing`           | Trazabilidad completa          |
| **Deduplicación** | Por `tenant` + `key`       | Prevención de duplicados        |
| **Propagación**   | `Event-driven`             | Integración con SITA            |

## 4.2 Patrones Aplicados

| Patrón             | Propósito                  | Implementación         |
|--------------------|---------------------------|------------------------|
| **CQRS**           | Separación comando/consulta| `API`/`Processor`      |
| **Event Sourcing** | Trazabilidad de eventos    | `PostgreSQL`           |
| **Deduplication**  | Prevención de duplicados   | Hash + timestamp       |
| **Publisher**      | Propagación de eventos     | Queue                  |

## 4.3 Trazabilidad

| Aspecto         | Implementación         | Tecnología         |
|-----------------|-----------------------|--------------------|
| **Eventos**     | Inmutables             | `Event store`      |
| **Timeline**    | Cronológico            | Consultas optimizadas |
| **Deduplicación** | Por `tenant`           | Hash keys          |
| **Propagación** | Asíncrona              | `SITA Messaging`   |
