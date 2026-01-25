---
id: responsabilidad-del-dominio
sidebar_position: 1
title: Responsabilidad del Dominio
description: Los datos deben ser propiedad y responsabilidad del dominio que los gestiona
---

# Responsabilidad del Dominio

## 1. Propósito

Establecer que cada dominio de negocio es responsable de la gestión, calidad e integridad de sus propios datos, evitando bases de datos compartidas y dependencias implícitas.

---

## 2. Alcance

Aplica a:

- Microservicios y servicios distribuidos
- Módulos dentro de monolitos modulares
- Sistemas que comparten datos entre dominios
- Integraciones de datos entre aplicaciones

---

## 3. Lineamientos Obligatorios

- Cada dominio/servicio es dueño de sus propios datos
- No compartir bases de datos entre dominios/servicios
- Exponer datos mediante APIs o eventos, no por acceso directo a BD
- Documentar el esquema y propiedad de cada conjunto de datos
- Aplicar principio de menor conocimiento (datos solo para quién los necesita)

---

## 4. Decisiones de Diseño Esperadas

- Definición de qué datos pertenecen a cada dominio
- Estrategia de acceso a datos entre dominios (APIs, eventos, replicación)
- Esquema de base de datos por dominio
- Políticas de retención y calidad de datos
- Documentación de propiedad de datos (data ownership)

---

## 5. Antipatrones y Prácticas Prohibidas

- Bases de datos compartidas entre servicios
- Acceso directo a tablas de otros dominios
- Modificación de datos ajenos sin pasar por el dueño
- Lógica de negocio duplicada en múltiples dominios
- Dependencias cíclicas de datos entre dominios

---

## 6. Principios Relacionados

- Datos como Responsabilidad del Dominio
- Desacoplamiento y Autonomía
- Arquitectura de Microservicios
- Contratos de Datos

---

## 7. Validación y Cumplimiento

- Revisión de diagramas de arquitectura de datos
- Auditoría de accesos a bases de datos
- Verificación de que no existen conexiones directas entre BDs de diferentes dominios
- Documentación de propiedad en ADRs
- Code reviews verificando acceso a datos mediante APIs
