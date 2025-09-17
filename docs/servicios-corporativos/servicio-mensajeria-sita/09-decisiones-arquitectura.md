# 9. Decisiones de arquitectura

## 9.1 Decisiones principales

| ADR | Decisión | Estado | Justificación |
|-----|----------|--------|---------------|
| **ADR-001** | Event Processor + Sender | Aceptado | Separación ingesta/envío |
| **ADR-002** | PostgreSQL inicial | Aceptado | Simplicidad |
| **ADR-003** | RazorEngine plantillas | Aceptado | Flexibilidad SITA |
| **ADR-004** | File-based exchange | Aceptado | Protocolo SITA |

## 9.2 Alternativas evaluadas

| Componente | Alternativas | Selección | Razón |
|------------|-------------|-----------|--------|
| **Cola eventos** | RabbitMQ, SNS+SQS, PostgreSQL | PostgreSQL | Simplicidad inicial |
| **Plantillas** | Liquid, Handlebars, Razor | RazorEngine | .NET nativo |
| **Protocolos** | REST, gRPC, File | File | Estándar SITA |
| **Storage** | S3, EFS, Local | EFS | Compartido |

## 9.1 ADR-001: SITA type B protocol implementation

**Estado**: Aceptado
**Fecha**: 2024-01-10
**Decidido por**: Equipo de Arquitectura + Aviation SMEs

### Contexto

Necesidad de comunicación directa con la red global SITA para intercambio de mensajes aeronáuticos estándar con aerolíneas y autoridades de aviación.

### Alternativas consideradas

1. **SITA Type B Directo**: Implementación directa del protocolo SITA
2. **Gateway SITA**: Uso de gateway comercial SITA
3. **Adaptador SITA de Terceros**: Adaptador de terceros
4. **Bridge de Protocolo Personalizado**: Desarrollo de bridge propietario

### Decisión

Adoptamos **Implementación Directa SITA Type B** con fallback a SITA para casos específicos.

### Justificación

- **Control Total**: Manejo directo de protocolos y errores
- **Rendimiento**: Latencia mínima sin capas intermedias
- **Costo**: Eliminación de licensing fees de gateways comerciales
- **Cumplimiento**: Cumplimiento directo con estándares IATA/ICAO
- **Flexibilidad**: Capacidad de adaptación a requerimientos específicos

### Consecuencias

- **Positivas**: Control, rendimiento, costo-efectividad
- **Negativas**: Complejidad de implementación, expertise requerido
- **Mitigación**: Entrenamiento especializado, partnership con expertos SITA

---

## 9.2 ADR-002: Message validation strategy

**Estado**: Aceptado
**Fecha**: 2024-01-15
**Decidido por**: Tech Lead + Aviation Compliance

### Contexto

Mensajes SITA deben cumplir estrictos estándares IATA/ICAO. Errores pueden resultar en multas o suspensión de servicios.

### Alternativas consideradas

1. **Schema-based Validation**: Validación XML/JSON schema
2. **Rule Engine**: Motor de reglas configurable
3. **Hard-coded Validation**: Validación programada específica
4. **External Validation Service**: Servicio de validación externo

### Decisión

Implementamos **Hybrid Approach**: Schema + Rule Engine + Domain Validation.

### Justificación

- **Compliance**: Múltiples niveles de validación para garantizar cumplimiento
- **Flexibility**: Rule engine permite updates sin redeploy
- **Performance**: Schema validation rápida + rules específicas
- **Maintainability**: Separación de concerns entre tipos de validación

### Implementación

```csharp
public class SitaMessageValidator : IMessageValidator
{
    public async Task<ValidationResult> ValidateAsync(SitaMessage message)
    {
        // Level 1: Schema validation
        var schemaResult = await _schemaValidator.ValidateAsync(message);
        if (!schemaResult.IsValid) return schemaResult;

        // Level 2: Business rules
        var rulesResult = await _ruleEngine.EvaluateAsync(message);
        if (!rulesResult.IsValid) return rulesResult;

        // Level 3: Domain validation
        var domainResult = await _domainValidator.ValidateAsync(message);
        return domainResult;
    }
}
```

---

## 9.3 ADR-003: Multi-tenant SITA address management

**Estado**: Aceptado
**Fecha**: 2024-01-20
**Decidido por**: Equipo de Arquitectura

### Contexto

Cada tenant requiere addresses SITA únicos para identificación en la red. Gestión manual es propensa a errores.

### Alternativas consideradas

1. **Manual Assignment**: Asignación manual de addresses
2. **SITA Registry Integration**: Integración con registro SITA
3. **Automated Pool Management**: Pool automático de addresses
4. **Tenant-specific Certificates**: Certificados únicos por tenant

### Decisión

Adoptamos **Automated Pool Management** con SITA Registry Integration.

### Justificación

- **Scalability**: Soporte automático para nuevos tenants
- **Error Reduction**: Eliminación de errores de configuración manual
- **Compliance**: Validación automática contra registro SITA
- **Audit Trail**: Trazabilidad completa de asignaciones

---

## 9.4 ADR-004: Connection pool architecture

**Estado**: Aceptado
**Fecha**: 2024-01-25
**Decidido por**: Tech Lead

### Contexto

Conexiones SITA son costosas de establecer y deben ser reutilizadas eficientemente para performance óptimo.

### Alternativas consideradas

1. **Single Connection**: Una conexión compartida
2. **Connection per Tenant**: Conexión dedicada por tenant
3. **Pooled Connections**: Pool compartido de conexiones
4. **Dynamic Scaling**: Scaling automático basado en carga

### Decisión

Implementamos **Hybrid Pool**: Connection pooling + tenant isolation cuando necesario.

### Justificación

- **Performance**: Reutilización eficiente de conexiones
- **Isolation**: Aislamiento para tenants críticos
- **Resource Optimization**: Uso eficiente de recursos de red
- **High Disponibilidad**: Failover automático entre conexiones

---

## 9.5 ADR-005: Message persistence strategy

**Estado**: Aceptado
**Fecha**: 2024-02-01
**Decidido por**: Data Team + Compliance

### Contexto

Mensajes SITA deben ser almacenados para auditoría, compliance y resolución de problemas. Volumen alto requiere estrategia de storage eficiente.

### Alternativas consideradas

1. **PostgreSQL Only**: Almacenamiento relacional únicamente
2. **Document Database**: MongoDB o similar para flexibilidad
3. **Time Series DB**: InfluxDB para datos temporales
4. **Hybrid Storage**: Combinación de tecnologías

### Decisión

Adoptamos **PostgreSQL with Partitioning** + **S3 for Archival**.

### Justificación

- **Compliance**: ACID transactions para integridad de auditoría
- **Performance**: Partitioning por fecha para queries eficientes
- **Cost**: S3 archival para retención a largo plazo
- **Familiarity**: Expertise existente del equipo en PostgreSQL

---

## 9.6 ADR-006: Manejo de errores and retry strategy

**Estado**: Aceptado
**Fecha**: 2024-02-05
**Decidido por**: Tech Lead + Operations

### Contexto

Red SITA puede tener intermitencias. Mensajes críticos deben ser entregados con alta confiabilidad.

### Alternativas consideradas

1. **Simple Retry**: Retry básico con delay fijo
2. **Exponential Backoff**: Incremento exponencial de delays
3. **Circuit Breaker**: Patrón circuit breaker para protection
4. **Dead Letter Queue**: Queue para mensajes fallidos

### Decisión

Implementamos **Comprehensive Strategy**: Exponential Backoff + Circuit Breaker + DLQ.

### Justificación

- **Reliability**: Múltiples mecanismos para garantizar entrega
- **Protection**: Circuit breaker previene cascading failures
- **Observability**: DLQ permite análisis de patrones de falla
- **Recovery**: Estrategias automáticas y manuales de recovery

---

## 9.7 Resumen de decisiones

| ADR | Decisión | Impacto | Estado |
|-----|----------|---------|---------|
| 001 | SITA Type B Direct | Alto - Protocolo fundamental | ✅ Implementado |
| 002 | Hybrid Validation | Alto - Compliance crítico | ✅ Implementado |
| 003 | Automated Address Pool | Medio - Escalabilidad | ✅ Implementado |
| 004 | Hybrid Connection Pool | Medio - Performance | ✅ Implementado |
| 005 | PostgreSQL + S3 Storage | Alto - Persistence strategy | ✅ Implementado |
| 006 | Comprehensive Retry | Alto - Reliability | ✅ Implementado |

## 9.8 Decisiones pendientes

### PND-001: Message routing optimization

**Contexto**: Routing inteligente basado en latencia y disponibilidad de nodos SITA
**Opciones**: Static routing, dynamic routing, ML-based routing
**Target**: Q3 2024

### PND-002: Real-time analytics integration

**Contexto**: Análisis en tiempo real de patrones de mensajería
**Opciones**: Kafka Streams, Apache Flink, custom analytics
**Target**: Q4 2024

### PND-003: Multi-region SITA deployment

**Contexto**: Despliegue en múltiples regiones para latencia óptima
**Opciones**: Active-passive, active-active, region-specific
**Target**: Q1 2025
