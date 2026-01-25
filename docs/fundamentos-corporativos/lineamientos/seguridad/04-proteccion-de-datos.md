---
id: proteccion-de-datos
sidebar_position: 4
title: Protección de Datos
description: Protección de datos sensibles a lo largo de su ciclo de vida
---

# Protección de Datos

## 1. Propósito

Establecer cómo proteger datos sensibles durante todo su ciclo de vida: creación, procesamiento, transmisión, almacenamiento y eliminación.

---

## 2. Alcance

Aplica a:

- Datos personales (PII)
- Datos financieros y de pago
- Datos de salud (PHI)
- Secretos y credenciales
- Datos confidenciales de negocio

---

## 3. Lineamientos Obligatorios

- Clasificar datos según sensibilidad (público, interno, sensible, regulado)
- Cifrar datos sensibles en tránsito (TLS 1.2+)
- Cifrar datos sensibles en reposo según clasificación
- Aplicar enmascaramiento/tokenización donde corresponda
- Gestionar claves de cifrado con servicios dedicados (KMS)

---

## 4. Decisiones de Diseño Esperadas

- Clasificación de datos por tipo y sensibilidad
- Estrategia de cifrado (algoritmos, gestión de claves)
- Métodos de enmascaramiento o tokenización
- Políticas de retención y eliminación segura
- Controles de acceso a datos sensibles

---

## 5. Antipatrones y Prácticas Prohibidas

- Almacenar datos sensibles sin cifrar
- Transmitir datos sensibles sin TLS
- Logs o trazas con datos sensibles
- Claves de cifrado en código o configuración
- Ausencia de clasificación de datos

---

## 6. Principios Relacionados

- Protección de Datos Sensibles
- Seguridad desde el Diseño
- Mínimo Privilegio
- Defensa en Profundidad

---

## 7. Validación y Cumplimiento

- Revisión de clasificación de datos
- Escaneo de secretos en código y logs
- Auditoría de configuración de cifrado
- Verificación de uso de TLS en todas las comunicaciones
- Pruebas de acceso no autorizado a datos sensibles
