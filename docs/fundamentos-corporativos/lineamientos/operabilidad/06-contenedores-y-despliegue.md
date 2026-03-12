---
id: contenedores-y-despliegue
sidebar_position: 6
title: Contenedores y Despliegue
description: Lineamientos para contenerización, imágenes reproducibles y estrategias de despliegue en ECS Fargate
---

# Contenedores y Despliegue

Imágenes construidas de forma inconsistente, con secretos embebidos o sin estrategias de despliegue seguro generan deriva entre entornos, vulnerabilidades ocultas y rollbacks costosos. Contenerizar con imágenes reproducibles, mínimas y auditables, combinadas con estrategias de despliegue controladas (rolling, blue/green), garantiza portabilidad, trazabilidad y capacidad de recuperación rápida ante fallos.

**Este lineamiento aplica a:** servicios desplegados en contenedores Docker sobre AWS ECS Fargate, imágenes de aplicaciones .NET, Kong, Keycloak y cualquier workload contenedorizado en la plataforma corporativa.

## Prácticas Obligatorias

- [Usar imágenes base oficiales LTS (Alpine o Slim cuando disponible)](../../estandares/infraestructura/containerization.md)
- [Aplicar multi-stage builds para minimizar tamaño de imagen](../../estandares/infraestructura/containerization.md)
- [No embeber secretos ni credenciales en imágenes](../../estandares/infraestructura/containerization.md)
- [Etiquetar imágenes con versión semántica, nunca con `latest`](../../estandares/infraestructura/containerization.md)
- [Habilitar health checks en contenedores](../../estandares/operabilidad/deployment.md)
- [Aplicar estrategia de despliegue rolling o blue/green](../../estandares/operabilidad/deployment.md)
- [Habilitar despliegue independiente por servicio](../../estandares/infraestructura/independent-deployment.md)
- [Gestionar secrets vía AWS Secrets Manager, no en variables de entorno planas](../../estandares/infraestructura/containerization.md)

## Referencias Relacionadas

- [CI/CD y Automatización](./01-cicd-pipelines.md)
- [Infraestructura como Código](./02-infraestructura-como-codigo.md)
- [Observabilidad](./05-observabilidad.md)
- [Configuración de Entornos](./03-configuracion-entornos.md)
