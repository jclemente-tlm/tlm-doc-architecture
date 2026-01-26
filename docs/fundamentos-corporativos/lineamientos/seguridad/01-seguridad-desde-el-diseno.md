---
id: seguridad-desde-el-diseno
sidebar_position: 1
title: Seguridad desde el Diseño
description: Seguridad como propiedad inherente del sistema desde el diseño
---

# Seguridad desde el Diseño

## 1. Propósito

Establecer que la seguridad debe ser una propiedad inherente del sistema, considerada desde las primeras decisiones de diseño y no como un agregado posterior.

---

## 2. Alcance

Aplica a:

- Todos los sistemas, servicios y componentes diseñados o modificados
- Arquitecturas nuevas y evolución de sistemas existentes
- Integraciones internas y externas
- Infraestructura y plataforma

---

## 3. Lineamientos Obligatorios

- Aplicar Security by Design en todas las decisiones arquitectónicas
- Realizar modelado de amenazas para nuevos sistemas o cambios significativos
- Definir explícitamente los límites de confianza (trust boundaries)
- Reducir la superficie de ataque mediante exposición controlada
- Aplicar defensa en profundidad (múltiples capas de seguridad)

---

## 4. Decisiones de Diseño Esperadas

- Identificación de activos críticos y amenazas
- Definición de trust boundaries y controles en cada límite
- Estrategia de autenticación y autorización
- Mecanismos de protección de datos sensibles
- Controles de seguridad por capa arquitectónica

---

## 5. Antipatrones y Prácticas Prohibidas

- Asumir que entornos internos o redes privadas son confiables por defecto
- Delegar completamente la seguridad a la infraestructura
- Incorporar controles de seguridad solo en etapas finales
- Reutilizar credenciales o identidades entre componentes
- Configuraciones inseguras por defecto

---

## 6. Principios Relacionados

- Seguridad desde el Diseño
- Zero Trust
- Defensa en Profundidad
- Mínimo Privilegio

---

## 7. Validación y Cumplimiento

- Modelado de amenazas documentado en ADRs
- Revisiones de seguridad en architecture reviews
- Pruebas de penetración en sistemas críticos
- Auditoría de controles de seguridad implementados
- Escaneo de vulnerabilidades automatizado en CI/CD
