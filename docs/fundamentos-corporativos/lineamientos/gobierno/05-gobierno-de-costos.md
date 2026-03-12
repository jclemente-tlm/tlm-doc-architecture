---
id: gobierno-de-costos
sidebar_position: 5
title: Gobierno de Costos
description: Visibilidad, asignación y control del gasto en infraestructura cloud mediante etiquetado de recursos, revisiones periódicas y optimización continua
---

# Gobierno de Costos

El gasto en infraestructura cloud sin supervisión activa genera sorpresas presupuestarias, recursos huérfanos y arquitecturas que optimizan rendimiento sin considerar costo. La ausencia de etiquetado impide asignar costos a equipos y servicios, eliminando la responsabilidad individual sobre el consumo. Implementar gobierno de costos como disciplina de arquitectura — con etiquetado obligatorio, revisiones mensuales, alertas y criterios de optimización — alinea decisiones técnicas con viabilidad económica sostenible.

**Este lineamiento aplica a:** todos los recursos AWS gestionados por Terraform (ECS, RDS, ElastiCache, VPC, S3, CloudWatch, Secrets Manager, Load Balancers), entornos de producción, staging y QA.

## Prácticas Obligatorias

- [Etiquetar todos los recursos AWS con Service, Environment, Team y CostCenter](../../estandares/infraestructura/cloud-cost-optimization.md)
- [Configurar alertas de presupuesto en AWS Budgets por servicio y entorno](../../estandares/infraestructura/cloud-cost-optimization.md)
- [Revisar Cost Explorer mensualmente por equipo de servicio](../../estandares/infraestructura/cloud-cost-optimization.md)
- [Aplicar escalado a cero en entornos no-prod fuera del horario laboral](../../estandares/infraestructura/cloud-cost-optimization.md)
- [Dimensionar CPU/memoria según métricas reales, no estimaciones](../../estandares/infraestructura/cloud-cost-optimization.md)
- [Documentar cost-tradeoffs en ADRs cuando la decisión impacta costos significativamente](../../estandares/gobierno/adr-management.md)

## Referencias Relacionadas

- [Cloud Native](../arquitectura/03-cloud-native.md) (diseño stateless y eficiencia operativa)
- [Infraestructura como Código](../operabilidad/02-infraestructura-como-codigo.md) (todos los recursos vía Terraform)
- [Decisiones Arquitectónicas](./01-decisiones-arquitectonicas.md) (registrar cost-tradeoffs)
- [Estándar Cloud Cost Optimization](../../estandares/infraestructura/cloud-cost-optimization.md)
