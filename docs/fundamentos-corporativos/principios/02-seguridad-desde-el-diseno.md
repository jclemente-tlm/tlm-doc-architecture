---
id: seguridad-desde-el-diseno
sidebar_position: 2
title: Seguridad desde el Diseño
description: La seguridad debe ser una consideración fundamental desde las decisiones arquitectónicas iniciales, integrándose en la estructura del sistema mediante patrones y prácticas comprobadas.
---

# Seguridad desde el Diseño

## Declaración del Principio

La seguridad debe ser una consideración explícita desde las decisiones arquitectónicas iniciales del sistema y no incorporarse posteriormente como controles aislados o correctivos.

## Justificación

Las decisiones arquitectónicas definen aspectos fundamentales del sistema: qué componentes existen y cómo se relacionan, qué capacidades se exponen y a quién, cómo circulan los datos, y dónde se establecen los límites de confianza.

Si estos elementos se diseñan sin considerar seguridad, los controles añadidos posteriormente solo mitigan síntomas y no las causas del riesgo, generando soluciones frágiles, costosas de mantener y difíciles de corregir. Un diseño seguro desde el inicio reduce significativamente la superficie de ataque, costos de remediación, riesgos operacionales e impacto de incidentes.

Este principio busca integrar la seguridad como propiedad estructural del sistema desde su concepción arquitectónica. Se logra definiendo límites de confianza explícitos, minimizando la superficie de ataque por diseño, implementando defensa en profundidad con múltiples capas de protección, y aplicando mínimo privilegio por defecto. Se aplica a componentes internos, integraciones externas, manejo de datos sensibles y gestión de identidad y accesos.

## Implicaciones

- Definir límites de confianza explícitos desde el diseño
- Minimizar la superficie de ataque por diseño arquitectónico
- Implementar defensa en profundidad con múltiples capas de protección
- Aplicar principio de mínimo privilegio por defecto
- Realizar threat modeling temprano para identificar amenazas y mitigaciones
- Integrar pruebas de seguridad en CI/CD
- Segmentar red y aislar componentes críticos
- Cifrar datos en tránsito y en reposo

## Referencias

**Lineamientos relacionados:**

- [Arquitectura Segura](../lineamientos/seguridad/arquitectura-segura.md)
- [Zero Trust](../lineamientos/seguridad/zero-trust.md)
- [Defensa en Profundidad](../lineamientos/seguridad/defensa-en-profundidad.md)
- [Mínimo Privilegio](../lineamientos/seguridad/minimo-privilegio.md)
- [Identidad y Accesos](../lineamientos/seguridad/identidad-y-accesos.md)
- [Protección de Datos](../lineamientos/seguridad/proteccion-de-datos.md)

**ADRs relacionados:**

- [ADR-003: Keycloak para SSO y Autenticación](/docs/adrs/adr-003-keycloak-sso-autenticacion)
- [ADR-004: AWS Secrets Manager](/docs/adrs/adr-004-aws-secrets-manager)

**Frameworks de referencia:**

- [AWS Well-Architected Framework - Security Pillar](https://aws.amazon.com/architecture/well-architected/)
- [OWASP Secure by Design](https://owasp.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
