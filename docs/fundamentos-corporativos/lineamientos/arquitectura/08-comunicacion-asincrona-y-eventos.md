---
id: comunicacion-asincrona-y-eventos
sidebar_position: 8
title: Comunicación Asíncrona y Eventos
description: Lineamientos para mensajería asíncrona y arquitectura orientada a eventos
---

# Comunicación Asíncrona y Eventos

## 1. Propósito

Establecer cómo diseñar e implementar comunicación asíncrona mediante mensajes y eventos, garantizando desacoplamiento y resiliencia.

---

## 2. Alcance

Aplica a:

- Mensajería entre servicios (queues, topics)
- Arquitectura orientada a eventos (event-driven)
- Event sourcing y CQRS
- Integraciones asíncronas
- Notificaciones y webhooks

---

## 3. Lineamientos Obligatorios

- Definir esquemas de eventos (AsyncAPI, JSON Schema, Avro)
- Usar eventos para comunicar hechos del dominio, no comandos
- Implementar idempotencia en consumidores
- Garantizar at-least-once o exactly-once delivery según criticidad
- Documentar topología de eventos (productores, consumidores, topics)

---

## 4. Decisiones de Diseño Esperadas

- Plataforma de mensajería (Apache Kafka con Confluent.Kafka)
- Estrategia de naming de topics
- Formato de mensajes y versionado (Avro con Schema Registry)
- Garantías de entrega (at-least-once, exactly-once)
- Estrategia de dead letter topics (DLT)

---

## 5. Antipatrones y Prácticas Prohibidas

- Eventos sin esquema definido
- Eventos como comandos (imperativos)
- Consumidores sin idempotencia
- Ausencia de DLQ para mensajes fallidos
- Eventos con datos sensibles sin cifrar

---

## 6. Principios Relacionados

- [Arquitectura Orientada a Eventos](../../estilos-arquitectonicos/eventos.md)
- Desacoplamiento y Autonomía
- Resiliencia y Tolerancia a Fallos
- Contratos de Datos

---

## 7. Validación y Cumplimiento

- Validación de esquemas de eventos
- Pruebas de idempotencia de consumidores
- Monitoreo de DLQ y mensajes no procesados
- Documentación de eventos en AsyncAPI
- Auditoría de flujos de eventos end-to-end
