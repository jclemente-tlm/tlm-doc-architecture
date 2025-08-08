# 1. Introducción y objetivos

Sistema especializado para generación y transmisión de mensajes aeronáuticos SITA.

## 1.1 Propósito y funcionalidades

| Funcionalidad | Descripción |
|---------------|-------------|
| **Mensajes SITA** | Generación de mensajes SITATEX |
| **Plantillas** | Motor de plantillas aeronáuticas |
| **Enrutamiento** | Direccionamiento AFTN |
| **Transmisión** | Envío a red SITA global |
| **Trazabilidad** | Seguimiento de entregas |
| **Cumplimiento** | Estándares ICAO |

## 1.2 Objetivos de calidad

| Atributo | Objetivo | Métrica |
|----------|----------|--------|
| **Disponibilidad** | Operación continua | 99.95% uptime |
| **Latencia** | Transmisión rápida | < 30s extremo a extremo |
| **Capacidad** | Alto volumen | 10,000 mensajes/hora |
| **Cumplimiento** | Estándares ICAO | 100% conformidad |

El **Sistema de Mensajería SITA** es un servicio especializado diseñado para generar, procesar y entregar mensajes SITA (Société Internationale de Télécommunications Aéronautiques) para aerolíneas y partners del ecosistema aeronáutico. Proporciona integración confiable con la red SITA global y sistemas aeroportuarios.

## 1.1 Descripción general de los requisitos

### Propósito del Sistema

El sistema actúa como puente entre los eventos corporativos internos y la red SITA global, transformando eventos de negocio en mensajes SITA estandarizados y gestionando la entrega confiable a aerolíneas y sistemas de partners.

### Contexto del Dominio SITA

SITA es la red de comunicaciones más grande del mundo para la industria aérea, conectando aerolíneas, aeropuertos, agencias de viajes y otros actores del ecosistema aeronáutico. Los mensajes SITA siguen estándares internacionales (IATA, ICAO) para garantizar interoperabilidad global.

### Arquitectura del Sistema

| Componente | Propósito | Tecnología |
|------------|-----------|------------|
| **Procesador de Eventos** | Consume eventos del Track & Trace, aplica reglas de negocio | .NET 8 Background Services |
| **Generador de Mensajes** | Transforma eventos en mensajes SITA según plantillas | Motor de Plantillas (Liquid), Reglas de Negocio |
| **Motor de Entrega** | Entrega confiable a partners SITA vía múltiples protocolos | SFTP, HTTP/S, Transferencia de Archivos |
| **Gestor de Configuración** | Gestión de plantillas, mapeos y configuración por partner | Plataforma de Configuración Dinámica |

### Requisitos Funcionales Principales

| ID | Requisito | Descripción Detallada |
|----|-----------|-----------------------|
| **RF-SITA-01** | **Generación de Mensajes** | Generación de mensajes SITA (MVTC, LDMC, etc.) desde eventos internos |
| **RF-SITA-02** | **Gestión de Plantillas** | Plantillas configurables por aerolínea y tipo de mensaje |
| **RF-SITA-03** | **Entrega Multi-Protocolo** | Entrega vía SFTP, HTTP/S, email según preferencias del partner |
| **RF-SITA-04** | **Configuración de Partner** | Configuración específica por aerolínea (formatos, protocolos, horarios) |
| **RF-SITA-05** | **Programación de Entrega** | Envío programado según horarios específicos del partner |
| **RF-SITA-06** | **Reintentos y Manejo de Errores** | Reintentos inteligentes con escalación manual para fallos persistentes |
| **RF-SITA-07** | **Validación de Formato** | Validación de mensajes SITA según estándares IATA antes del envío |
| **RF-SITA-08** | **Auditoría y Cumplimiento** | Seguimiento completo para auditorías y cumplimiento regulatorio |
| **RF-SITA-09** | **Soporte Multi-tenant** | Soporte para múltiples aeropuertos/países con configuración independiente |
| **RF-SITA-10** | **Monitoreo en Tiempo Real** | Paneles para monitoreo de entregas y estado de partners |

### Tipos de Mensajes SITA Soportados

| Tipo Mensaje | Estándar | Propósito | Frecuencia Típica |
|--------------|----------|-----------|-------------------|
| **MVTC** | IATA SSIM | Movement messages (vuelos) | Por movimiento |
| **LDMC** | IATA SSIM | Load messages (carga) | Por vuelo |
| **BSMC** | IATA RP 1745 | Baggage messages | Por pieza |
| **NOTAM** | ICAO Doc 8126 | Notice to Airmen | As needed |
| **METAR/TAF** | ICAO Annex 3 | Weather information | Hourly/scheduled |
| **Custom** | Partner-specific | Mensajes específicos por aerolínea | Variable |

### Requisitos No Funcionales

| Categoría | Requisito | Objetivo | Medición |
|-----------|-----------|--------|----------|
| **Confiabilidad** | Tasa éxito entrega mensajes | 99.9% | Seguimiento entregas |
| **Rendimiento** | Capacidad procesamiento mensajes | 1,000 mensajes/hora | Monitoreo rendimiento |
| **Disponibilidad** | Tiempo actividad sistema | 99.9% | Monitoreo SLA |
| **Cumplimiento** | Cumplimiento red SITA | 100% cumplimiento estándares | Validación formato |
| **Seguridad** | Transmisión segura | Cifrado en tránsito | Auditorías seguridad |
| **Auditabilidad** | Rastro auditoría completo mensajes | 100% mensajes rastreados | Reportes auditoría |

### Partners y Protocolos de Integración

| Tipo Partner | Método Integración | Protocolo | Seguridad |
|--------------|-------------------|----------|----------|
| **Aerolíneas Principales** | Red SITA directa | SITATEX, X.25 | Estándares seguridad SITA |
| **Aerolíneas Regionales** | Transferencia archivos | SFTP, HTTPS | TLS 1.3, autenticación basada claves |
| **Operadores Tierra** | Integración API | API REST, WebHooks | OAuth2 + JWT |
| **Operadores Carga** | Archivos lote | SFTP, entrega programada | Autenticación basada certificados |
| **Agencias Gubernamentales** | Portal seguro | Carga HTTPS | PKI gubernamental |

## 1.2 Objetivos de calidad

### Objetivos Primarios

| Prioridad | Objetivo | Escenario | Métrica Objetivo |
|-----------|----------|-----------|------------------|
| **1** | **Cumplimiento** | Mensajes cumplen estándares SITA/IATA al 100% | Cero violaciones cumplimiento |
| **2** | **Confiabilidad** | Entrega garantizada de mensajes críticos | 99.9% éxito entrega |
| **3** | **Puntualidad** | Entrega dentro de ventanas tiempo requeridas | 95% entrega a tiempo |

### Objetivos Secundarios

| Objetivo | Descripción | Métrica |
|----------|-------------|---------|
| **Flexibilidad** | Fácil adición de nuevos partners y formatos | < 1 semana integración |
| **Observabilidad** | Visibilidad completa del pipeline de mensajes | 100% mensajes rastreados |
| **Eficiencia Costos** | Optimización de costos de transmisión | < $0.10 por mensaje |
| **Mantenibilidad** | Gestión simple de plantillas y configuraciones | Configuración autoservicio |

### Atributos de Calidad Específicos

| Atributo | Definición | Implementación | Verificación |
|----------|------------|----------------|--------------|
| **Integridad Mensaje** | Mensajes entregados sin corrupción | Checksums, firmas digitales | Validación automatizada |
| **Garantía Entrega** | Confirmación de entrega exitosa | Seguimiento acuse recibo | Verificación recepción |
| **Cumplimiento Formato** | Adherencia a estándares SITA/IATA | Validación schema, verificación formato | Pruebas cumplimiento |
| **SLA Partner** | Cumplimiento de SLAs específicos por partner | Monitoreo SLA, alertas | Reportes SLA |

## 1.3 Partes interesadas

### Stakeholders Principales

| Rol | Contacto | Responsabilidades | Expectativas |
|-----|----------|-------------------|--------------|
| **Operaciones Aeroportuarias** | Gestión Operaciones | Definición de mensajes críticos, SLAs | Entrega confiable, estado tiempo real |
| **Relaciones Aerolíneas** | Gestión Partners | Relaciones con aerolíneas, incorporación | Integración fluida partners |
| **Integración TI** | Equipos Desarrollo | Integración técnica, resolución problemas | APIs claras, documentación completa |
| **Oficial Cumplimiento** | Legal/Cumplimiento | Cumplimiento regulatorio, auditorías | Rastros auditoría completos, reportes cumplimiento |
| **Técnico SITA** | Representantes SITA | Estándares técnicos, certificación | Cumplimiento estándares, certificación |

### Partners Externos (Consumidores)

| Partner | Relationship | Messages Consumed | Technical Contact |
|---------|--------------|-------------------|-------------------|
| **LATAM Airlines** | Major partner | MVTC, LDMC, BSMC | LATAM IT Team |
| **Copa Airlines** | Regional partner | MVTC, Custom messages | Copa Operations |
| **Avianca** | Strategic partner | Full message suite | Avianca Technical |
| **Local Ground Handlers** | Service providers | Ground operation messages | Ops teams |
| **Cargo Companies** | Logistics partners | Cargo-specific messages | Cargo IT teams |

### Sistemas Proveedores (Upstream)

| Sistema | Data Provided | Integration Type | SLA |
|---------|---------------|------------------|-----|
| **Track & Trace** | Flight events, operational events | Event streaming | < 30 sec |
| **Flight Information** | Schedule changes, delays | Real-time API | < 5 sec |
| **Ground Operations** | Baggage, cargo, services | Batch + real-time | < 1 min |
| **Weather Systems** | METAR, TAF data | Scheduled updates | Hourly |
| **Configuration Platform** | Templates, partner settings | Polling | 30 sec intervals |

### Autoridades Regulatorias

| Authority | Jurisdiction | Compliance Requirements | Reporting |
|-----------|--------------|------------------------|-----------|
| **DGAC Peru** | Peru aviation authority | Flight movement reporting | Daily |
| **DGAC Ecuador** | Ecuador aviation authority | Operational compliance | Weekly |
| **Aerocivil Colombia** | Colombia aviation authority | Safety reporting | As required |
| **AFAC Mexico** | Mexico aviation authority | Movement tracking | Real-time |
| **IATA** | International standards | Message format compliance | Periodic audits |

### Matriz de Comunicación

| Stakeholder | Frecuencia | Canal | Contenido |
|-------------|------------|-------|-----------|
| **Airport Operations** | Real-time | Dashboards, alerts | Message delivery status, partner status |
| **Airline Relations** | Weekly | Status reports | Partner SLA compliance, issues |
| **IT Integration** | Daily | Monitoring, logs | System health, error rates |
| **Compliance** | Monthly | Formal reports | Audit trails, compliance metrics |
| **SITA Technical** | Quarterly | Technical reviews | Standards compliance, certification status |

### Escalation Matrix

| Issue Type | L1 Support | L2 Support | L3 Support | External |
|------------|------------|------------|------------|----------|
| **Delivery Failures** | Equipo DevOps | Development Team | System Architect | Partner Technical |
| **Format Issues** | Operations | SITA Specialist | Technical Lead | SITA Certification |
| **Partner Problems** | Account Manager | Technical Support | Solution Architect | Partner Management |
| **Compliance Issues** | Compliance Officer | Equipo Legal | Executive Leadership | Regulatory Authority |
