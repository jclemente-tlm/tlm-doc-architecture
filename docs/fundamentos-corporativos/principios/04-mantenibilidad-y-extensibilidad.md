---
id: mantenibilidad-y-extensibilidad
sidebar_position: 4
title: Mantenibilidad y Extensibilidad
description: Los sistemas deben ser diseñados para facilitar su evolución, comprensión y modificación a lo largo del tiempo, minimizando el costo de cambio y maximizando la capacidad de adaptación.
---

# Mantenibilidad y Extensibilidad

## Declaración del Principio

Los sistemas deben ser diseñados para facilitar su evolución, comprensión y modificación a lo largo del tiempo, minimizando el costo de cambio y maximizando la capacidad de adaptación a nuevos requisitos.

## Justificación

La mantenibilidad y extensibilidad son atributos de calidad reconocidos internacionalmente (ISO/IEC 25010) que determinan el costo total de propiedad del software. El 70-80% del costo de software está en mantenimiento, no en desarrollo inicial.

Sistemas mantenibles reducen el esfuerzo necesario para corregir defectos, agregar funcionalidades, adaptarse a cambios del entorno y comprender el código existente. Facilitan la detección y corrección de defectos, reducen dependencia de individuos específicos y permiten adaptación ágil a cambios de mercado.

Este principio busca minimizar el costo de cambio y maximizar la capacidad de adaptación del sistema a lo largo de su ciclo de vida. Se logra mediante código auto-documentado con nombres descriptivos, estructura lógica predecible, modularidad con bajo acoplamiento, aislamiento de decisiones técnicas, y evitando complejidad innecesaria. Se aplica a arquitectura de sistemas, diseño de componentes, prácticas de codificación, documentación técnica, y procesos de desarrollo y operación.

## Implicaciones

- Documentar decisiones arquitectónicas mediante ADRs
- Aplicar patrones de diseño consistentes y reutilizar soluciones probadas
- Separar capas y módulos con responsabilidades claras
- Mantener cobertura de tests que facilite cambios seguros
- Realizar code reviews enfocados en mantenibilidad
- Evitar sobreingeniería manteniendo soluciones proporcionales al problema
- Invertir en refactoring y mejora continua del código
- Requiere mayor inversión inicial a cambio de velocidad sostenible a largo plazo

## Referencias

**Lineamientos relacionados:**

- [Arquitectura Limpia](../lineamientos/arquitectura/11-arquitectura-limpia.md)
- [Arquitectura Evolutiva](../lineamientos/arquitectura/12-arquitectura-evolutiva.md)
- [Simplicidad Intencional](../lineamientos/arquitectura/13-simplicidad-intencional.md)
- [Modelado de Dominio](../lineamientos/arquitectura/09-modelado-de-dominio.md)

**ADRs relacionados:**

- [ADR-012: GitHub Actions para CI/CD](/docs/adrs/adr-012-github-actions-cicd)

**Frameworks de referencia:**

- [ISO/IEC 25010:2011 - Software Quality Model](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [AWS Well-Architected Framework - Operational Excellence](https://aws.amazon.com/architecture/well-architected/)
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)
