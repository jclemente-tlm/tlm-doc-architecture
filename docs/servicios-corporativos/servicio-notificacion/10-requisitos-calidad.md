# 10. Requisitos de Calidad

Este capítulo define los atributos de calidad del **Sistema de Notificaciones**, estableciendo métricas cuantificables, criterios de aceptación y escenarios de validación alineados a estándares internacionales (ISO/IEC 25010, NIST, SRE) y regulaciones (GDPR, CAN-SPAM, TCPA).

## 10.1 Rendimiento y Eficiencia

| Métrica                  | Objetivo           | Medición         |
|--------------------------|-------------------|------------------|
| **Latencia envío**       | < 500ms p95       | Prometheus       |
| **Throughput**           | 1k notificaciones/min | Load testing  |
| **Disponibilidad**       | 99.9%             | Health checks    |
| **Cola processing**      | < 30s             | Monitoreo        |

### 10.1.1 Objetivos de Latencia y Rendimiento

| Operación                  | P50   | P95   | P99   | SLA Crítico |
|----------------------------|-------|-------|-------|-------------|
| **Solicitud API (sync)**   | 100ms | 200ms | 500ms | < 1s        |
| **Renderizado plantilla**  | 20ms  | 50ms  | 100ms | < 200ms     |
| **Llamada API proveedor**  | 200ms | 800ms | 2s    | < 5s        |
| **Entrega Email**          | 30s   | 2min  | 5min  | < 10min     |
| **Entrega SMS**            | 5s    | 30s   | 1min  | < 2min      |
| **Notificación Push**      | 1s    | 5s    | 10s   | < 30s       |
| **Entrega WhatsApp**       | 10s   | 1min  | 3min  | < 5min      |

### 10.1.2 Capacidad y Pruebas de Estrés

```yaml
Requisitos de Capacidad:
  Carga Normal:
    - Solicitudes API: 1,000 req/min
    - Emails: 5,000/hora
    - SMS: 2,000/hora
    - Push: 10,000/hora
    - WhatsApp: 1,000/hora
  Carga Pico:
    - Solicitudes API: 5,000 req/min
    - Emails: 50,000/hora
    - SMS: 20,000/hora
    - Push: 100,000/hora
    - WhatsApp: 10,000/hora
  Objetivos Estrés:
    - Capacidad Máxima: 10x carga normal
    - Ráfaga: 30 min sostenidos
    - Sin pérdida de mensajes durante picos
```

### 10.1.3 Auto-scaling y Utilización de Recursos

```csharp
public class NotificationServiceScalingPolicy
{
    public ScalingMetrics GetScalingMetrics() => new()
    {
        CpuThreshold = 70,
        CpuScaleOutCooldown = 300,
        CpuScaleInCooldown = 600,
        QueueDepthThreshold = 1000,
        QueueDepthScaleOutCooldown = 180,
        QueueDepthScaleInCooldown = 900,
        ResponseTimeThreshold = 500,
        ResponseTimeScaleOutCooldown = 300,
        MinInstances = 2,
        MaxInstances = 50,
        EmailQueueDepth = 500,
        SmsQueueDepth = 200,
        PushQueueDepth = 2000
    };
}
```

## 10.2 Disponibilidad y Confiabilidad

### 10.2.1 SLA y Arquitectura Alta Disponibilidad

```yaml
SLA:
  Sistema: 99.9% (43.2 min/mes)
  Email: 99.95%
  SMS: 99.9%
  Push: 99.8%
  WhatsApp: 99.5%
Delivery SLA:
  Email: 95% < 10min
  SMS: 98% < 2min
  Push: 99% < 30s
  WhatsApp: 90% < 5min
Errores:
  API 4xx: < 2%
  API 5xx: < 0.5%
  Proveedor: < 1%
  Plantillas: < 0.1%
```

```yaml
Multi-AZ Deployment:
  Región Primaria: us-east-1
    - AZ-1a: 2 API, 2 processors
    - AZ-1b: 2 API, 2 processors
    - AZ-1c: 1 API, 1 processor (standby)
  Región Secundaria: us-west-2
    - AZ-2a: 1 API, 1 processor (standby)
    - DB: Read replica
Balanceador de Carga:
  ALB: Health check /health/ready
  DB: PgBouncer, replicas lectura
```

### 10.2.2 Estrategia de Recuperación ante Desastres

```yaml
Recovery:
  RTO: 30 min
  RPO: 5 min
  Backups: WAL, snapshots 6h, cross-region
  Failover: ALB + CloudWatch, DNS manual, proveedor secundario
```

## 10.3 Seguridad y Compliance

### 10.3.1 Requisitos de Seguridad

```yaml
Auth:
  OAuth2 client_credentials, JWT, scopes
RBAC:
  admin: CRUD, cross-tenant
  operator: envío, métricas, plantillas
  viewer: solo lectura
  processor: interno
Protección Datos:
  TLS 1.3, AES-256, TDE, S3 encryption
  PII: hash, cifrado, retención 30 días
```

### 10.3.2 Requisitos de Compliance

```yaml
GDPR:
  Minimización, purga automática, consentimiento, derecho a borrado
CAN-SPAM:
  Unsubscribe, remitente claro, asunto, dirección física
TCPA:
  Opt-in, opt-out, horarios, frecuencia
Locales:
  Perú, Ecuador, Colombia, México: leyes locales de datos
```

## 10.4 Usabilidad y Experiencia

### 10.4.1 Calidad de API y UX Plantillas

```yaml
API:
  RESTful, OpenAPI 3.0, errores uniformes, paginación
  Documentación interactiva, ejemplos, versionado
  Rate limiting, mensajes claros
UX Plantillas:
  Editor WYSIWYG, preview, validación, versionado
  Accesibilidad, drag-and-drop, biblioteca, A/B testing
  Tutoriales, ayuda contextual, mejores prácticas
```

## 10.5 Mantenibilidad y Observabilidad

### 10.5.1 Logging, Métricas y Alertas

```yaml
Logging: JSON, DEBUG-ERROR, retención 90d/2a
Métricas: envíos, éxito, uso plantillas, costos, satisfacción
Técnicas: latencia, errores, colas, recursos, DB
SLO/SLI: disponibilidad, error rate, percentiles
Alertas críticas: error >5%, caídas, colas detenidas, fallos proveedor
Escalado: L1-L4 según criticidad
```

## 10.6 Testabilidad y Gates de Calidad

```yaml
Test Pyramid:
  Unit: >90% cobertura, <30s
  Integración: DB, APIs, Kafka, <5min
  E2E: flujos completos, <30min
Herramientas: xUnit, Moq, TestContainers, NBomber, Pact, Playwright
Quality Gates: SonarQube, cobertura, seguridad, performance, startup
```

## 10.7 Escalabilidad e Interoperabilidad

### 10.7.1 Escalado y Estándares de Integración

```yaml
Escalado:
  API: stateless, auto-scaling, 50/región
  Procesadores: scaling por canal, Kafka, work-stealing
  DB: replicas, pooling, particionado
  Vertical: API 16vCPU/32GB, DB 64vCPU/256GB
Integración:
  REST: OpenAPI, JSON, errores estándar
  Webhook: HMAC, retries, DLQ
  GraphQL: queries complejas, subscripciones
  Mensajería: Kafka (Avro, multi-tenant), SQS, RabbitMQ, Azure SB
```

*[Diagrama C4 - Quality Attributes Implementation]*

## Referencias

- [ISO/IEC 25010 - Systems and software Requisitos de Calidad](https://www.iso.org/standard/35733.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [SRE Mejores Prácticas](https://sre.google/sre-book/table-of-contents/)
- [GDPR Official Text](https://gdpr.eu/tag/gdpr/)
- [CAN-SPAM Act Guide](https://www.ftc.gov/tips-advice/business-center/guidance/can-spam-act-compliance-guide-business)
- [TCPA Compliance Guide](https://www.fcc.gov/document/tcpa-rules)

## 10.8 Escenarios de Calidad

### 10.8.1 Disponibilidad

- **Fuente**: Monitoreo
- **Estímulo**: Falla de instancia
- **Respuesta**: Failover automático
- **Medida**: Recuperación < 30s

### 10.8.2 Performance

- **Fuente**: Cliente
- **Estímulo**: Pico 50K notificaciones/5min
- **Respuesta**: Auto-scaling
- **Medida**: Procesamiento < 10min

### 10.8.3 Seguridad

- **Fuente**: Atacante
- **Estímulo**: Acceso no autorizado
- **Respuesta**: Bloqueo y alerta
- **Medida**: 0% accesos exitosos

### 10.8.4 Multi-tenancy

- **Fuente**: Tenant A
- **Estímulo**: Consulta de datos
- **Respuesta**: Aislamiento total
- **Medida**: 100% aislamiento

## 10.9 Matriz de Calidad

| Atributo      | Criticidad | Escenario Principal         | Métrica Objetivo                |
|--------------|------------|----------------------------|---------------------------------|
| Disponibilidad| Alta       | Failover automático        | 99.9% uptime                    |
| Performance   | Alta       | Procesamiento de picos     | < 200ms API, 10K/min procesamiento |
| Seguridad     | Crítica    | Protección datos PII       | 0 brechas, Compliance GDPR      |
| Fiabilidad    | Alta       | Entrega garantizada        | 99.99% delivery rate            |
| Mantenibilidad| Media      | Despliegues sin downtime   | < 5 min deployment              |
| Escalabilidad | Alta       | Auto-scaling               | Linear scaling hasta 100K/min    |
