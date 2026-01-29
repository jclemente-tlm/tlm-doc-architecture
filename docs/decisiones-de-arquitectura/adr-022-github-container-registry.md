---
title: "ADR-022: GitHub Container Registry"
sidebar_position: 22
---

## ✅ ESTADO

Aceptada – Enero 2026

---

## 🗺️ CONTEXTO

Los servicios corporativos desplegados en contenedores requieren un registry centralizado para:

- **Almacenamiento de imágenes Docker** para microservicios .NET 8+
- **Integración con GitHub Actions** para CI/CD automatizado
- **Control de acceso** con autenticación y autorización por repositorio
- **Escaneo de seguridad** integrado con pipelines
- **Versionado semántico** y gestión de tags
- **Alta disponibilidad** con replicación global
- **Costos controlados** y escalabilidad automática
- **Compatibilidad con AWS ECS/Fargate** (ADR-007)

La estrategia prioriza **integración con CI/CD existente, seguridad y costos** evitando lock-in innecesario.

Alternativas evaluadas:

- **GitHub Container Registry (ghcr.io)** (integrado GitHub, gratis para públicos, autenticación GitHub)
- **Amazon ECR** (nativo AWS, integración IAM, pago por uso)
- **Azure Container Registry** (nativo Azure, lock-in Microsoft)
- **Docker Hub** (público, rate limits, costos altos privados)
- **Harbor** (self-hosted OSS, operación manual)

## 🔍 COMPARATIVA DE ALTERNATIVAS

### Comparativa Cualitativa

| Criterio              | GitHub Container Registry | Amazon ECR | Azure ACR | Docker Hub | Harbor (Self-hosted) |
|----------------------|---------------------------|------------|-----------|------------|---------------------|
| **Agnosticidad**     | ✅ Multi-cloud | ❌ Lock-in AWS | ❌ Lock-in Azure | ✅ Agnóstico | ✅ OSS, agnóstico |
| **Integración CI/CD**| ✅ Nativa GitHub Actions | ✅ AWS SDK | 🟡 Azure DevOps | 🟡 Manual | 🟡 Manual |
| **Autenticación**    | ✅ GitHub tokens (PAT, OIDC) | ✅ IAM roles | ✅ Azure AD | 🟡 Docker login | 🟡 Usuarios locales |
| **Seguridad**        | ✅ GitHub Advanced Security | ✅ ECR Image Scanning | ✅ Defender for Containers | 🟡 Básico | ✅ Trivy integrado |
| **Costos**           | ✅ Gratis (públicos), bajo privados | 🟡 US$0.10/GB storage | 🟡 US$5/mes + storage | ❌ US$7/mes por repo | ✅ Solo infraestructura |
| **Alta disponibilidad** | ✅ Global, gestionado | ✅ Multi-AZ | ✅ Geo-replicación | ✅ Gestionado | 🟡 Manual |
| **Performance**      | ✅ CDN global | ✅ VPC Endpoints | ✅ Muy bueno | 🟡 Rate limits | 🟡 Depende infra |
| **Ecosistema .NET**  | ✅ Excelente | ✅ Excelente | ✅ Nativo Microsoft | ✅ Excelente | ✅ Excelente |

### Matriz de Decisión

| Solución                  | Integración CI/CD | Seguridad | Costos | Performance | Recomendación         |
|--------------------------|-------------------|-----------|--------|-------------|-----------------------|
| **GitHub Container Registry** | Excelente    | Excelente | Excelente | Excelente   | ✅ **Seleccionada**    |
| **Amazon ECR**           | Muy buena     | Excelente | Media  | Excelente   | 🟡 Alternativa         |
| **Azure ACR**            | Buena         | Excelente | Media  | Muy buena   | ❌ Descartada          |
| **Docker Hub**           | Media         | Básica    | Mala   | Media       | ❌ Descartada          |
| **Harbor**               | Media         | Excelente | Buena  | Media       | ❌ Descartada          |

---

## 💰 ANÁLISIS DE COSTOS (TCO 3 años)

> **Supuesto:** 20 imágenes privadas, 50GB storage promedio, 5 pulls/día, CI/CD automatizado

| Solución         | Licenciamiento | Storage (3 años) | Transfer | Operación | TCO 3 años   |
|------------------|---------------|------------------|----------|-----------|--------------|
| GitHub Container Registry | Gratis (Open Source) | US$0 | US$0 | US$0 | **US$0** |
| GitHub Container Registry | Privado | US$600 | US$0 | US$0 | **US$600** |
| Amazon ECR       | US$0          | US$1,800         | US$360   | US$0      | US$2,160     |
| Azure ACR        | US$540        | US$1,800         | US$240   | US$0      | US$2,580     |
| Docker Hub       | US$2,520      | Incluido         | Incluido | US$0      | US$2,520     |
| Harbor           | OSS           | US$3,600         | US$0     | US$18,000 | US$21,600    |

---

## Consideraciones técnicas y riesgos

### Límites clave

- **GitHub Container Registry:** 
  - Storage: Ilimitado (pago según plan)
  - Bandwidth: Ilimitado para públicos, límites por plan privados
  - Pulls: Sin rate limits para autenticados
  - Retención: Configurable, cleanup automático

- **Amazon ECR:**
  - Storage: Ilimitado, US$0.10/GB/mes
  - Lifecycle policies para cleanup automático
  - VPC Endpoints para optimizar costos de transferencia

### Riesgos y mitigación

- **Dependencia de GitHub:** Mitigado con capacidad de migrar imágenes a ECR si necesario
- **Costos de storage privado:** Mitigado con políticas de retención y cleanup automático
- **Autenticación:** Usar OIDC (OpenID Connect) en vez de PAT para mayor seguridad

---

## ✔️ DECISIÓN

Se selecciona **GitHub Container Registry (ghcr.io)** como registry corporativo de contenedores.

## Justificación

- **Integración perfecta con GitHub Actions** (ADR-009) - autenticación automática via GITHUB_TOKEN
- **Costo cero** para repositorios públicos, bajo para privados
- **Seguridad integrada** con GitHub Advanced Security y dependabot
- **Namespace por organización** - `ghcr.io/talma-corp/{servicio}:{version}`
- **Multi-arquitectura** - soporte AMD64 y ARM64 nativo
- **Agnóstico de cloud** - funciona con ECS, EKS, GKE, AKS
- **Sin vendor lock-in** - compatible con Docker registry API v2
- **Migratable** - fácil exportar/importar imágenes si cambio necesario

## Alternativas descartadas

- **Amazon ECR:** Costos por storage/transfer, lock-in AWS, autenticación IAM compleja para CI/CD externo
- **Azure ACR:** Lock-in Azure, no integrado con GitHub Actions nativamente
- **Docker Hub:** Rate limits agresivos, costos altos para privados, no integrado CI/CD
- **Harbor:** Operación manual compleja, costos de infra y mantenimiento altos

---

## ⚠️ CONSECUENCIAS

### Positivas
- Pipeline CI/CD simplificado con autenticación automática GITHUB_TOKEN
- Costos predecibles y bajos (o cero para OSS)
- Namespace consistente: `ghcr.io/talma-corp/{servicio}:{version}`
- Security scanning integrado en GitHub Actions
- Alta disponibilidad global sin configuración adicional

### Negativas
- Dependencia de GitHub (aunque bajo riesgo por API estándar Docker registry)
- Costos de storage crecen con cantidad de imágenes (mitigable con retention policies)
- Menos integrado con AWS IAM comparado con ECR (pero OIDC lo resuelve)

### Implementación requerida
- Crear namespace `ghcr.io/talma-corp/` en organización GitHub
- Configurar OIDC en GitHub Actions para autenticación sin secretos
- Definir naming convention: `ghcr.io/talma-corp/{servicio}:{version}`
- Implementar retention policy: mantener últimas 10 versiones + tags `latest`, `stable`
- Configurar security scanning con Trivy en pipeline (ADR-023)
- Documentar proceso de pull en ECS task definitions

---

## 🏗️ CONFIGURACIÓN Y BUENAS PRÁCTICAS

### Naming Convention

```bash
# Formato estándar
ghcr.io/talma-corp/{servicio}:{version}

# Ejemplos
ghcr.io/talma-corp/orders-api:v1.2.3
ghcr.io/talma-corp/orders-api:latest
ghcr.io/talma-corp/orders-api:stable
ghcr.io/talma-corp/orders-api:sha-abc1234

# Multi-arquitectura
ghcr.io/talma-corp/orders-api:v1.2.3-amd64
ghcr.io/talma-corp/orders-api:v1.2.3-arm64
```

### GitHub Actions Workflow

```yaml
name: Build and Push to GHCR

on:
  push:
    branches: [main]
    tags: ['v*']

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/talma-corp/orders-api:${{ github.sha }}
            ghcr.io/talma-corp/orders-api:latest
          cache-from: type=registry,ref=ghcr.io/talma-corp/orders-api:latest
          cache-to: type=inline
```

### ECS Task Definition

```json
{
  "family": "orders-api",
  "containerDefinitions": [
    {
      "name": "orders-api",
      "image": "ghcr.io/talma-corp/orders-api:v1.2.3",
      "repositoryCredentials": {
        "credentialsParameter": "arn:aws:secretsmanager:us-east-1:123456789012:secret:github-token"
      }
    }
  ]
}
```

### Retention Policy (GitHub Actions)

```yaml
# .github/workflows/cleanup-ghcr.yml
name: Cleanup old images
on:
  schedule:
    - cron: '0 2 * * 0' # Weekly

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/delete-package-versions@v4
        with:
          package-name: 'orders-api'
          package-type: 'container'
          min-versions-to-keep: 10
          delete-only-untagged-versions: true
```

---

## 📊 MÉTRICAS Y MONITOREO

### KPIs Clave

- **Pull success rate:** > 99.9%
- **Push latency:** < 30s (p95)
- **Storage growth:** < 10GB/mes
- **Image scan findings:** 0 critical, < 5 high

### Alertas Críticas

- Fallos de autenticación en CI/CD
- Storage > 100GB (revisar retention)
- Critical CVEs detectados en escaneo
- Pull failures > 1% en última hora

---

## 📚 REFERENCIAS

- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Registry API v2](https://docs.docker.com/registry/spec/api/)
- [ADR-007: AWS ECS Fargate Contenedores](./adr-007-aws-ecs-fargate-contenedores.md)
- [ADR-009: GitHub Actions CI/CD](./adr-009-github-actions-cicd.md)
- [ADR-023: Trivy + Checkov Security Scanning](./adr-023-trivy-checkov-security-scanning.md)

---

**Decisión tomada por:** Equipo de Arquitectura + DevOps
**Fecha:** Enero 2026
**Próxima revisión:** Enero 2027
