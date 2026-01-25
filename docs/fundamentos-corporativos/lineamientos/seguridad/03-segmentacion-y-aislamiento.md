---
id: 03-proteccion-de-datos
sidebar_position: 3
title: Protección de datos
---

<!-- ## Principios

- Protege datos sensibles en tránsito y en reposo.
- Usa cifrado fuerte y actualizado.
- Limita el acceso a datos personales.

## Buenas prácticas

- Cumple con normativas de protección de datos.
- Realiza auditorías periódicas.
- Informa a los usuarios sobre el uso de sus datos. -->

# Protección de Datos

## Propósito
Establecer lineamientos arquitectónicos para proteger los datos a lo largo de todo su ciclo de vida, reduciendo riesgos de exposición, uso indebido o incumplimiento normativo.

## Alcance
Aplica a todos los sistemas, servicios y procesos que crean, procesan, transmiten o almacenan datos dentro de la arquitectura corporativa.

## Criterios Arquitectónicos

### Clasificación de Datos
La arquitectura debe reconocer que no todos los datos tienen el mismo nivel de sensibilidad.

Todo sistema debe considerar, como mínimo, las siguientes categorías:
- Datos públicos
- Datos internos
- Datos sensibles
- Datos regulados

Las decisiones de diseño deben contemplar esta clasificación desde el origen del dato y a lo largo de su propagación.

---

### Protección de Datos en Tránsito y en Reposo
Los datos sensibles o regulados deben estar protegidos:
- Durante su transmisión entre componentes
- Durante su almacenamiento persistente

La protección debe ser un **requisito arquitectónico**, independiente del entorno o del mecanismo de despliegue.

---

### Minimización de Datos
Los sistemas deben:
- Recopilar únicamente los datos estrictamente necesarios
- Exponer solo la información requerida para cada caso de uso
- Evitar replicaciones innecesarias entre sistemas o dominios

La minimización reduce la superficie de ataque y simplifica el cumplimiento normativo.

---

## Antipatrones
- Compartir modelos de datos completos entre sistemas
- Persistir información “por si acaso”
- Exponer datos sensibles en logs, eventos o mensajes
- Replicar datos sin una justificación arquitectónica clara

## Resultado Esperado
Arquitecturas que reducen riesgos y exposición mediante un manejo consciente, controlado y responsable de los datos.
