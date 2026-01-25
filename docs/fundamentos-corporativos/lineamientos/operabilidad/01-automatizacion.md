---
id: automatizacion
sidebar_position: 1
title: Automatización
description: Automatización de procesos repetitivos y propensos a error
---

# Automatización

## 1. Propósito

Establecer que los procesos repetitivos, manuales y propensos a error deben automatizarse para garantizar consistencia, velocidad y confiabilidad.

---

## 2. Alcance

Aplica a:

- Despliegues y releases
- Pruebas (unitarias, integración, e2e)
- Aprovisionamiento de infraestructura
- Configuración de entornos
- Validaciones de calidad y seguridad

---

## 3. Lineamientos Obligatorios

- Automatizar despliegues mediante CI/CD
- Automatizar pruebas y ejecución en cada cambio
- Automatizar aprovisionamiento de infraestructura (IaC)
- Automatizar validaciones de seguridad y calidad
- Documentar y versionar scripts de automatización

---

## 4. Decisiones de Diseño Esperadas

- Plataforma de CI/CD (GitHub Actions, GitLab CI, Jenkins)
- Estrategia de pipelines (por proyecto, compartidos)
- Herramientas de automatización de infraestructura
- Niveles de pruebas automatizadas
- Gates de calidad y aprobaciones en pipelines

---

## 5. Antipatrones y Prácticas Prohibidas

- Despliegues manuales a producción
- Configuración manual de entornos
- Pruebas solo manuales sin automatización
- Scripts de automatización no versionados
- Dependencia de conocimiento tribal para deploys

---

## 6. Principios Relacionados

- Automatización como Principio
- Infraestructura como Código
- Consistencia entre Entornos
- Calidad desde el Diseño

---

## 7. Validación y Cumplimiento

- Auditoría de pipelines de CI/CD configurados
- Revisión de cobertura de pruebas automatizadas
- Verificación de uso de IaC
- Documentación de procesos automatizados
- Métricas de deployment frequency y lead time
