
# 3. Contexto y alcance

El sistema SITA Messaging se integra en el ecosistema corporativo para gestionar la generación, transmisión y monitoreo de mensajes aeronáuticos bajo estándares internacionales, interactuando con sistemas internos y externos clave.

![Servicios Corporativos - Vista de Contexto](/diagrams/servicios-corporativos/corporate_services.png)

*Figura 3.1: Vista de contexto de los Servicios Corporativos*

![Sistema SITA Messaging - Vista de Contexto](/diagrams/servicios-corporativos/sita_messaging_system.png)

*Figura 3.2: Vista de contexto del Sistema SITA Messaging*

## 3.1 Alcance del sistema

| Aspecto      | Descripción                                                                 |
|--------------|-----------------------------------------------------------------------------|
| Incluido     | Generación y transmisión de mensajes SITA, plantillas, enrutamiento AFTN, integración con Track & Trace, monitoreo, auditoría, cumplimiento de protocolos aeronáuticos. |
| Excluido     | Lógica de vuelos, gestión de itinerarios, edición de mensajes, administración de usuarios finales. |

## 3.2 Actores y sistemas externos

| Actor/Sistema         | Rol         | Interacción principal                        |
|----------------------|-------------|---------------------------------------------|
| Track & Trace        | Proveedor   | Eventos operacionales para mensajería        |
| Red SITA Global      | Destinatario| Transmisión y recepción de mensajes SITA     |
| Partners aeronáuticos| Destinatario| Recepción y coordinación operativa           |
| Identidad            | Proveedor   | Autenticación y autorización                 |
| Observabilidad       | Consumidor  | Métricas, logs y alertas                     |
