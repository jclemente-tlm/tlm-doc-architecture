---
id: independent-deployment
sidebar_position: 8
title: Despliegue Independiente
description: Estándares para desplegar servicios de forma independiente sin acoplamiento de releases, usando contenedores, feature flags y estrategias sin downtime.
tags: [infraestructura, deployment, docker, feature-flags, blue-green]
---

# Despliegue Independiente

## Contexto

Cada servicio debe poder desplegarse sin coordinación con otros equipos. Complementa el lineamiento [Autonomía de Servicios](../../lineamientos/arquitectura/10-autonomia-de-servicios.md).

**Cuándo aplicar:** Todo servicio en arquitectura de microservicios o que comparta pipeline con otros equipos.

---

## Stack Tecnológico

| Componente      | Tecnología     | Versión | Uso                      |
| --------------- | -------------- | ------- | ------------------------ |
| **Containers**  | Docker         | 24+     | Empaquetado del servicio |
| **Orquestador** | Kubernetes     | 1.28+   | Despliegue en clúster    |
| **CI/CD**       | GitHub Actions | —       | Pipeline automatizado    |
| **Flags**       | Feature Flags  | —       | Dark launches / canary   |

---

## Despliegue Independiente

### ¿Qué es Despliegue Independiente?

Capacidad de desplegar un servicio sin coordinación con otros servicios, habilitando autonomía y velocidad.

**Requisitos:**

- **Versioned APIs**: Contratos versionados
- **Backward compatibility**: Sin breaking changes
- **Database per service**: Sin shared database
- **Async communication**: Eventos para sincronización
- **Feature flags**: Habilitar features gradualmente

**Propósito:** Autonomía de equipos, despliegues frecuentes, menor riesgo.

**Beneficios:**
✅ Deploy cuando equipo decide
✅ Rollback independiente
✅ Testing aislado
✅ Menor coordinación

### Deployment Pipeline Independiente

```yaml
# .github/workflows/deploy.yml
# Pipeline de deployment independiente

name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: "Environment to deploy"
        required: true
        type: choice
        options:
          - dev
          - staging
          - production

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Restore
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore

      - name: Test
        run: dotnet test --no-build --verbosity normal

  build-image:
    name: Build Docker Image
    needs: test
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}

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
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy-dev:
    name: Deploy to Dev
    needs: build-image
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: dev
      url: https://customer-api.dev.talma.internal
    steps:
      - name: Deploy to ECS
        run: |
          # Actualizar task definition en ECS
          aws ecs update-service \
            --cluster customer-service-dev \
            --service customer-api \
            --force-new-deployment \
            --region us-east-1

  deploy-staging:
    name: Deploy to Staging
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://customer-api.staging.talma.internal
    steps:
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster customer-service-staging \
            --service customer-api \
            --force-new-deployment \
            --region us-east-1

  deploy-production:
    name: Deploy to Production
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://customer-api.talma.com
    steps:
      - name: Deploy to ECS
        run: |
          # Blue-Green deployment
          aws ecs update-service \
            --cluster customer-service-prod \
            --service customer-api \
            --force-new-deployment \
            --region us-east-1

      - name: Monitor deployment
        run: |
          # Esperar deployment completo
          aws ecs wait services-stable \
            --cluster customer-service-prod \
            --services customer-api \
            --region us-east-1
```

### Contract Testing

```csharp
// Tests/ContractTests/CustomerApiContractTests.cs
// Verificar que cambios no rompen contratos

public class CustomerApiContractTests
{
    [Fact]
    public async Task GetCustomer_Response_MaintainsBackwardCompatibility()
    {
        // Arrange
        var client = new HttpClient { BaseAddress = new Uri("http://localhost:8080") };

        // Act
        var response = await client.GetAsync("/api/v1/customers/550e8400-e29b-41d4-a716-446655440000");
        var json = await response.Content.ReadAsStringAsync();
        var customer = JsonSerializer.Deserialize<CustomerDto>(json);

        // Assert - Verificar campos requeridos existen
        customer.Should().NotBeNull();
        customer!.Id.Should().NotBeEmpty();
        customer.Name.Should().NotBeNullOrEmpty();
        customer.Email.Should().NotBeNullOrEmpty();

        // ✅ Nuevos campos opcionales OK
        // ❌ Remover campos existentes = BREAKING CHANGE
        // ❌ Cambiar tipo de campo = BREAKING CHANGE
        // ❌ Hacer campo opcional requerido = BREAKING CHANGE
    }

    [Fact]
    public async Task CreateCustomer_AcceptsLegacyFormat()
    {
        // Arrange - Request antiguo (v1.0)
        var legacyRequest = new
        {
            name = "John Doe",
            email = "john@example.com"
            // phone era opcional, ahora requerido pero debe funcionar sin él
        };

        var client = new HttpClient { BaseAddress = new Uri("http://localhost:8080") };
        var content = new StringContent(
            JsonSerializer.Serialize(legacyRequest),
            Encoding.UTF8,
            "application/json");

        // Act
        var response = await client.PostAsync("/api/v1/customers", content);

        // Assert - Debe seguir funcionando
        response.StatusCode.Should().Be(HttpStatusCode.Created);
    }
}
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

**Pipeline:**

- **MUST** cada servicio tener su propio pipeline CI/CD independiente
- **MUST** pipeline incluir etapas: test → build → deploy-dev → deploy-staging → deploy-production
- **MUST** usar environments de GitHub Actions con aprobaciones para producción
- **MUST** requerir que todos los tests pasen antes de proceder al build

**Compatibilidad:**

- **MUST** mantener backward compatibility en APIs públicas entre versiones
- **MUST** versionar contratos de API (e.g., `/api/v1/`, `/api/v2/`)
- **MUST** ejecutar contract tests antes de cada deploy a producción
- **MUST** no realizar breaking changes sin deprecation period mínimo de un sprint

**Deployment:**

- **MUST** cada servicio tener su propia task definition en ECS (sin compartir)
- **MUST** usar estrategia de deployment que permita rollback en menos de 5 minutos
- **MUST** monitorear deployment con health checks y `ecs wait services-stable`

**Database:**

- **MUST** aplicar migraciones de base de datos de forma backward compatible (Expand-Contract Pattern)
- **MUST** nunca compartir base de datos entre servicios

### SHOULD (Fuertemente recomendado)

- **SHOULD** implementar feature flags para dark launches y canary releases
- **SHOULD** usar blue-green o rolling deployment en producción para zero downtime
- **SHOULD** configurar alertas de CloudWatch que disparen rollback automático ante error rate elevado
- **SHOULD** publicar evento de dominio al completar deploy exitoso (para trazabilidad)
- **SHOULD** etiquetar imágenes Docker con el SHA del commit que generó el deploy

### MAY (Opcional)

- **MAY** implementar canary releases con route ponderado (10% → 50% → 100%)
- **MAY** usar AWS CodeDeploy para orquestar blue-green en ECS
- **MAY** integrar smoke tests automáticos post-deploy antes de promover al siguiente ambiente

### MUST NOT (Prohibido)

- **MUST NOT** compartir pipeline CI/CD entre servicios distintos
- **MUST NOT** coordinar deploys con otros equipos como pre-requisito (acoplamiento de releases)
- **MUST NOT** introducir breaking changes sin incrementar versión mayor de la API
- **MUST NOT** realizar deploy manual en producción sin registro de aprobación

---

## Referencias

- [GitHub Actions: Environments & Deployments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment) — ambientes y aprobaciones en CI/CD
- [AWS ECS Rolling Update](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html) — estrategia de despliegue rolling en ECS
- [AWS ECS Blue/Green Deployment](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-bluegreen.html) — despliegue blue/green en ECS
- [Pact — Consumer Driven Contract Testing](https://docs.pact.io/) — contract testing entre servicios
- [Microsoft API Versioning](https://github.com/dotnet/aspnet-api-versioning) — versionado de APIs en ASP.NET Core
- [Expand-Contract Pattern (Parallel Change)](https://martinfowler.com/bliki/ParallelChange.html) — patrón para migraciones backward compatible
- [Feature Toggles (Feature Flags)](https://martinfowler.com/articles/feature-toggles.html) — habilitación gradual de funcionalidades
- [Sam Newman — Independent Deployability](https://samnewman.io/blog/2021/08/12/why-i-no-longer-use-the-term-microservices/) — principio de desplieguabilidad independiente
- [Containerización](./containerization.md) — empaquetado de servicios en contenedores
- [Infrastructure as Code — Implementación](./iac-implementation.md) — provisioning de pipelines y recursos
- [Externalización de Configuración](./externalize-configuration.md) — gestión de configuración por ambiente
