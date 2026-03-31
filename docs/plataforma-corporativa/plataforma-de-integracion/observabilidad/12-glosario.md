---
sidebar_position: 12
title: Glosario
description: Términos y acrónimos del stack de observabilidad corporativo.
---

# 12. Glosario

## Términos del Dominio

| Término               | Definición                                                                                                                                                      |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| **Observabilidad**    | Capacidad de inferir el estado interno de un sistema a partir de sus salidas externas: logs, métricas y trazas.                                                 |
| **Log**               | Registro de evento discreto generado por una aplicación, con timestamp, nivel (INFO/WARN/ERROR) y mensaje.                                                      |
| **Métrica**           | Valor numérico medido a lo largo del tiempo (serie temporal). Ej.: CPU %, requests por segundo, latencia p95.                                                   |
| **Traza distribuida** | Registro de la ejecución de una operación a través de múltiples servicios, compuesta por spans enlazados por `traceId`.                                         |
| **Span**              | Unidad de trabajo dentro de una traza; representa una operación concreta (llamada HTTP, consulta a BD).                                                         |
| **traceId**           | Identificador único de una traza distribuida; propagado por el SDK OpenTelemetry en headers HTTP y en los logs.                                                 |
| **Tenant**            | Unidad de aislamiento de datos en el stack. En este sistema: país (logs), ambiente (métricas) o dominio de servicio (trazas).                                   |
| **X-Scope-OrgID**     | Header HTTP estándar del stack LGTM para indicar el tenant al que pertenece la señal entrante.                                                                  |
| **Multi-tenancy**     | Capacidad de una plataforma de servir a múltiples tenants con datos aislados en una misma infraestructura.                                                      |
| **Pipeline**          | Definición de un flujo de procesamiento de datos en Grafana Alloy (archivo `.alloy`): fuente → transformación → destino.                                        |
| **WAL**               | Write-Ahead Log. Mecanismo de durabilidad de Loki/Mimir/Tempo: los datos se escriben primero en WAL local antes de persistir en MinIO.                          |
| **Bucket**            | Unidad de almacenamiento en MinIO/S3. Cada backend tiene su propio bucket (`loki-data`, `mimir-blocks`, `tempo-data`).                                          |
| **Modo monolítico**   | Configuración de Loki/Mimir/Tempo donde todos los componentes internos corren en un solo proceso. Simplicidad operativa a expensas de escalabilidad horizontal. |
| **cAdvisor**          | Container Advisor. Expone métricas de recursos (CPU, memoria, red) de los contenedores Docker para que Alloy las recolecte.                                     |
| **Derived Fields**    | Configuración en Grafana que detecta patrones en logs (ej.: `traceId=xxx`) y crea un enlace al data source de trazas.                                           |
| **LogQL**             | Lenguaje de consulta de Loki (similar a PromQL). Permite filtrar y agregar logs. Ej.: `{job="orders"}                                                           | = "error"`. |
| **PromQL**            | Lenguaje de consulta de Prometheus/Mimir para métricas. Ej.: `rate(http_requests_total[5m])`.                                                                   |
| **TraceQL**           | Lenguaje de consulta de Tempo para trazas. Ej.: `{resource.service.name="orders" && duration > 1s}`.                                                            |
| **SLO**               | Service Level Objective. Meta de calidad de servicio expresada como porcentaje (ej.: disponibilidad ≥ 99,9%).                                                   |
| **SLI**               | Service Level Indicator. Métrica que mide el cumplimiento de un SLO (ej.: ratio de peticiones exitosas).                                                        |
| **Retención**         | Período durante el cual los datos permanecen en el almacenamiento antes de ser eliminados automáticamente.                                                      |

## Acrónimos

| Acrónimo | Significado                                                    |
| -------- | -------------------------------------------------------------- |
| **LGTM** | Loki + Grafana + Tempo + Mimir (stack oficial de Grafana Labs) |
| **OTLP** | OpenTelemetry Protocol                                         |
| **OTel** | OpenTelemetry                                                  |
| **WAL**  | Write-Ahead Log                                                |
| **SLO**  | Service Level Objective                                        |
| **SLI**  | Service Level Indicator                                        |
| **APM**  | Application Performance Monitoring                             |
| **OSS**  | Open Source Software                                           |
| **TSDB** | Time Series Database                                           |
| **IaC**  | Infrastructure as Code                                         |
| **SSO**  | Single Sign-On                                                 |
| **gRPC** | Google Remote Procedure Call                                   |
