# 4. Estrategia de solución

## 4.1 Decisiones clave

| Decisión | Alternativa elegida | Justificación |
|----------|-------------------|---------------|
| **Arquitectura** | API + Event Processor | Separación responsabilidades |
| **Almacenamiento** | Event Sourcing | Trazabilidad completa |
| **Deduplicación** | Por tenant + key | Prevención duplicados |
| **Propagación** | Event-driven | Integración SITA |

## 4.2 Patrones aplicados

| Patrón | Propósito | Implementación |
|---------|------------|----------------|
| **CQRS** | Separación comando/consulta | API/Processor |
| **Event Sourcing** | Trazabilidad eventos | PostgreSQL |
| **Deduplication** | Prevención duplicados | Hash + timestamp |
| **Publisher** | Propagación eventos | Queue |

## 4.3 Trazabilidad

| Aspecto | Implementación | Tecnología |
|---------|-----------------|-------------|
| **Eventos** | Inmutables | Event store |
| **Timeline** | Cronológico | Consultas optimizadas |
| **Deduplicación** | Por tenant | Hash keys |
| **Propagación** | Asíncrona | SITA Messaging |
