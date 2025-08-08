# 12. Glosario

## 12.1 Términos principales

| Término | Definición |
|----------|------------|
| **SITA** | Société Internationale de Télécommunications Aéronautiques |
| **SITATEX** | Protocolo de mensajería telegráfica SITA |
| **AFTN** | Aeronautical Fixed Telecommunication Network |
| **Type B** | Formato de mensaje operacional SITA |
| **TTY** | Teletypewriter - formato texto |
| **EDIFACT** | Electronic Data Interchange For Administration |
| **Partner** | Aerolínea o entidad conectada |
| **Template** | Plantilla para generar mensajes SITA |
| **Event-driven** | Arquitectura basada en eventos |
| **File-based** | Intercambio mediante archivos |

## 12.2 Acrónimos

| Acrónimo | Significado |
|-----------|-------------|
| **IATA** | International Air Transport Association |
| **ICAO** | International Civil Aviation Organization |
| **SFTP** | SSH File Transfer Protocol |
| **PKI** | Public Key Infrastructure |
| **CDC** | Change Data Capture |

## A

**ACARS** (Aircraft Communications Addressing and Reporting System)
: Sistema de comunicación digital utilizado para transmitir mensajes cortos entre aeronaves y estaciones terrestres via radio o satélite.

**Indicador de Dirección** (Address Indicator)
: Código de 7 caracteres que identifica únicamente una terminal o aplicación en la red SITA. Formato: XXXXYZZ donde XXXX=ubicación, Y=empresa, ZZ=aplicación.

**ADS-B** (Automatic Dependent Surveillance-Broadcast)
: Sistema de vigilancia que permite a las aeronaves determinar su posición vía satélite y transmitir esta información periódicamente.

**AFTN** (Aeronautical Fixed Telecommunication Network)
: Red mundial de telecomunicaciones fijas para el intercambio de mensajes relacionados con la seguridad de vuelos.

**ARINC** (Aeronautical Radio Incorporated)
: Organización que desarrolla estándares para la industria de aviación, especialmente en comunicaciones y aviónica.

## B

**Procesamiento por Lotes** (Batch Processing)
: Procesamiento de mensajes en grupos (lotes) para optimizar eficiencia de red y recursos computacionales.

**BRS** (Business Recovery Services)
: Servicios de recuperación empresarial que garantizan continuidad operacional ante desastres.

## C

**Toma de Decisiones Colaborativa** (C-DM - Collaborative Decision Making)
: Proceso colaborativo entre aeropuertos, aerolíneas y control de tráfico aéreo para optimizar operaciones.

**CPDLC** (Controller-Pilot Data Link Communications)
: Sistema de enlace de datos que permite comunicación digital directa entre controladores de tráfico aéreo y pilotos.

**CSM** (Common Services Model)
: Modelo de servicios comunes de SITA que proporciona funcionalidades compartidas a múltiples aplicaciones.

## D

**DCS** (Departure Control System)
: Sistema que maneja el proceso de salida de pasajeros, incluyendo check-in, boarding y gestión de equipaje.

**Cola de Mensajes Fallidos** (Dead Letter Queue - DLQ)
: Cola especial donde se almacenan mensajes que no pudieron ser procesados después de múltiples intentos.

**DSL** (Domain Specific Language)
: Lenguaje de programación especializado para un dominio particular de problemas.

## E

**EDIFACT** (Electronic Data Interchange for Administration, Commerce and Transport)
: Estándar internacional para intercambio electrónico de datos estructurados entre sistemas informáticos.

**Event Sourcing**
: Patrón arquitectónico donde todos los cambios de estado se almacenan como secuencia de eventos inmutables.

## F

**FFM** (Flight Manifest Message)
: Mensaje SITA que contiene el manifiesto de vuelo con información detallada de pasajeros y carga.

**Flight Information Region (FIR)**
: Región específica de espacio aéreo donde un país tiene responsabilidad de proporcionar servicios de información de vuelo.

## G

**Ground Handling**
: Servicios proporcionados a aeronaves mientras están en tierra, incluyendo carga, descarga, limpieza y mantenimiento.

**GTW** (Gateway)
: Punto de interconexión entre diferentes redes o protocolos de comunicación.

## H

**Health Check**
: Verificación automática del estado operacional de servicios y componentes del sistema.

**HPA** (Horizontal Pod Autoscaler)
: Mecanismo de Kubernetes que automáticamente ajusta el número de pods basado en métricas como CPU o memoria.

## I

**IATA** (International Air Transport Association)
: Asociación comercial de aerolíneas del mundo que desarrolla estándares para la industria.

**ICAO** (International Civil Aviation Organization)
: Agencia especializada de las Naciones Unidas que regula la aviación civil internacional.

**Idempotency**
: Propiedad de operaciones que pueden ser aplicadas múltiples veces sin cambiar el resultado más allá de la aplicación inicial.

## J

**JWT** (JSON Web Token)
: Estándar abierto para transmitir información de forma segura entre partes como un objeto JSON compacto y auto-contenido.

## K

**KPI** (Key Performance Indicator)
: Métrica utilizada para evaluar el éxito en el logro de objetivos específicos.

## L

**Load Balancer**
: Dispositivo que distribuye cargas de trabajo de red o aplicación a través de múltiples servidores.

**LTM** (Local Traffic Manager)
: Componente que gestiona y distribuye tráfico dentro de un centro de datos local.

## M

**Message Sequence Number**
: Número único secuencial asignado a cada mensaje para garantizar orden y detectar duplicados.

**MTBF** (Mean Time Between Failures)
: Tiempo promedio entre fallos de un sistema o componente.

**MTTR** (Mean Time To Recovery)
: Tiempo promedio requerido para restaurar un sistema después de un fallo.

**Multi-tenancy**
: Arquitectura donde una instancia de software sirve a múltiples tenants (inquilinos) con datos y configuraciones aisladas.

## N

**Network Partitioning**
: División de una red en segmentos aislados debido a fallos de conectividad.

**NOC** (Network Operations Center)
: Centro centralizado desde donde se monitorea, controla y mantiene una red de telecomunicaciones.

## O

**OAuth2**
: Framework de autorización que permite a aplicaciones obtener acceso limitado a servicios web.

**OIDC** (OpenID Connect)
: Capa de identidad sobre OAuth 2.0 que permite verificar la identidad de usuarios.

**OTel** (OpenTelemetry)
: Framework de observabilidad para generar, recopilar y exportar datos de telemetría.

## P

**PagerDuty**
: Plataforma de gestión de incidentes que proporciona alertas y respuesta automatizada.

**Partition Tolerance**
: Capacidad de un sistema distribuido de continuar operando a pesar de fallos de red.

**PKI** (Public Key Infrastructure)
: Marco de trabajo para gestión de certificados digitales y criptografía de clave pública.

**PNR** (Passenger Name Record)
: Registro que contiene el itinerario de un pasajero específico en sistemas de reservas.

## Q

**Queue Depth**
: Número de mensajes actualmente esperando en una cola para ser procesados.

**QoS** (Quality of Service)
: Medida de rendimiento de un servicio de red, especialmente en términos de latencia, capacidad de procesamiento y confiabilidad.

## R

**RabbitMQ**
: Broker de mensajes que implementa el protocolo AMQP para messaging empresarial.

**Redis**
: Base de datos en memoria utilizada como cache, broker de mensajes y almacén de datos.

**RPO** (Recovery Point Objective)
: Máxima cantidad de datos que una organización puede permitirse perder durante un desastre.

**RTO** (Recovery Time Objective)
: Tiempo máximo que una organización puede tolerar para restaurar servicios después de un desastre.

## S

**SIEM** (Security Information and Event Management)
: Solución que proporciona análisis en tiempo real de alertas de seguridad generadas por aplicaciones y hardware de red.

**SITA** (Société Internationale de Télécommunications Aéronautiques)
: Empresa multinacional de tecnología de la información que proporciona telecomunicaciones e IT a la industria de transporte aéreo.

**SITATEX**
: Red global de telecomunicaciones de SITA que conecta más de 1,000 ubicaciones en 200+ países.

**SSO** (Single Sign-On)
: Método de autenticación que permite a usuarios acceder múltiples aplicaciones con un solo conjunto de credenciales.

## T

**Tenant**
: Entidad organizacional (cliente, empresa, división) que comparte una instancia de software multi-tenant con aislamiento de datos.

**Capacidad de procesamiento**
: Cantidad de trabajo realizado por unidad de tiempo, típicamente medido en transacciones por segundo.

**TLS** (Transport Layer Security)
: Protocolo criptográfico que proporciona comunicaciones seguras sobre una red informática.

**Type B Message**
: Formato estándar de mensaje SITA para comunicaciones aeronáuticas con estructura específica de headers y contenido.

## U

**Uptime**
: Porcentaje de tiempo que un sistema está operacional y disponible para uso.

**UTC** (Coordinated Universal Time)
: Estándar de tiempo utilizado mundialmente, especialmente crítico en operaciones aeronáuticas.

## V

**Vault** (HashiCorp)
: Herramienta para almacenar y acceder secretos de forma segura, incluyendo certificados y claves.

**VPN** (Virtual Private Network)
: Red privada virtual que extiende una red privada a través de una red pública.

## W

**WebSocket**
: Protocolo de comunicación que proporciona canales de comunicación full-duplex sobre una conexión TCP.

**Workflow Engine**
: Sistema que gestiona y ejecuta procesos de negocio automatizados definidos como workflows.

## X

**X.509**
: Estándar que define el formato de certificados de clave pública utilizados en muchos protocolos de internet.

**XML** (eXtensible Markup Language)
: Lenguaje de marcado que define reglas para codificar documentos de forma legible tanto para humanos como máquinas.

## Y

**YAML** (YAML Ain't Markup Language)
: Estándar de serialización de datos legible por humanos utilizado para archivos de configuración.

**YARP** (Yet Another Reverse Proxy)
: Biblioteca .NET para construir proxies reversos de alto rendimiento.

## Z

**Zero Downtime Deployment**
: Técnica de despliegue que permite actualizar aplicaciones sin interrumpir el servicio.

**Zone**
: Región geográfica o lógica utilizada para organizar recursos de infraestructura y mejorar disponibilidad.
