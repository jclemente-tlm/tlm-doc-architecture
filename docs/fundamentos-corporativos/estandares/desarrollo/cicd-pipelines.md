---
id: cicd-pipelines
sidebar_position: 1
title: CI/CD Pipelines
description: Estándar para diseño, configuración y operación de pipelines de CI/CD con GitHub Actions
---

# Estándar Técnico — CI/CD Pipelines

---

## 1. Propósito

Establecer prácticas estándar para diseñar, implementar y operar pipelines de integración continua y entrega continua (CI/CD), garantizando builds reproducibles, despliegues seguros y trazabilidad completa.

---

## 2. Alcance

**Aplica a:**

- Todos los repositorios de código fuente
- Pipelines de build, test y deploy
- Automatización de releases
- Infrastructure as Code (IaC)
- Despliegues a entornos dev, staging y producción
- Multi-tenant deployments

**No aplica a:**

- Scripts de desarrollo local
- Procesos manuales de emergencia documentados
- Experimentos en feature branches sin merge

---

## 3. Tecnologías Aprobadas

| Componente             | Tecnología      | Uso Principal             | Observaciones             |
| ---------------------- | --------------- | ------------------------- | ------------------------- |
| **CI/CD Platform**     | GitHub Actions  | Todos los repositorios    | Único permitido           |
| **Container Registry** | GitHub Packages | Imágenes Docker (ghcr.io) | Integrado con GitHub      |
| **Artifact Storage**   | S3              | Artifacts, reportes, logs | Con versionado habilitado |
| **Secrets Management** | AWS Secrets Mgr | Credenciales de deploy    | Rotación automática       |
| **IaC Execution**      | Terraform       | Plan/Apply automatizado   | State en S3+DynamoDB      |
| **Quality Gates**      | SonarQube 10.0+ | Code quality, security    | Quality Gate obligatorio  |
| **Security Scanning**  | Trivy           | Container vulnerabilities | Fail on CRITICAL          |
| **Dependency Check**   | OWASP Dep-Check | Dependencias vulnerables  | Integrado en pipeline     |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Estructura de Pipeline

- [ ] **Stages definidos:** build → test → security → deploy
- [ ] **Triggers claros:** push, pull request, schedule, manual
- [ ] **Branch protection:** main/master requiere PR + approvals
- [ ] **Pipeline as Code:** YAML versionado en repositorio
- [ ] **Naming convention:** `{env}-{app}-{action}.yml`

### Build Stage

- [ ] **Reproducible builds:** versión de herramientas pinned
- [ ] **Cache dependencies:** npm, maven, nuget, pip
- [ ] **Semantic versioning:** usar GitVersion o similar
- [ ] **Build artifacts:** almacenar con retention policy
- [ ] **Multi-arch builds:** si aplica (amd64, arm64)

### Test Stage

- [ ] **Unit tests:** coverage mínimo 80%
- [ ] **Integration tests:** contra servicios reales o testcontainers
- [ ] **Code coverage:** publicar reporte, fail si < umbral
- [ ] **Test results:** formato JUnit/NUnit para trending
- [ ] **Parallel execution:** optimizar tiempos de pipeline

### Security Stage

- [ ] **SAST:** SonarQube con Quality Gate obligatorio
- [ ] **Dependency scanning:** OWASP Dependency-Check
- [ ] **Container scanning:** Trivy o equivalente
- [ ] **Secret detection:** GitGuardian, TruffleHog
- [ ] **License compliance:** verificar OSS licenses permitidas

### Deploy Stage

- [ ] **Approval gates:** manual para producción
- [ ] **Deployment strategy:** blue-green, canary o rolling
- [ ] **Health checks:** validar deploy exitoso
- [ ] **Rollback automático:** si health checks fallan
- [ ] **Deploy notifications:** Slack, Teams, email

### Observabilidad

- [ ] **Pipeline metrics:** duración, success rate
- [ ] **Failed build alerts:** notificar equipo inmediatamente
- [ ] **Deployment tracking:** vincular commits con releases
- [ ] **Audit logs:** quién deployó qué, cuándo
- [ ] **Pipeline logs:** retención 90 días mínimo

---

## 5. Prohibiciones

- ❌ Secrets hardcoded en código o YAML
- ❌ Deploy directo a producción sin gates
- ❌ Builds no reproducibles (dependencias flotantes)
- ❌ Ignorar fallos en tests o security scans
- ❌ Pipelines sin versionamiento
- ❌ Deploy sin rollback strategy
- ❌ Falta de audit trail de deployments

---

## 6. Configuración Mínima

### GitHub Actions - Build & Deploy

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:

env:
  DOTNET_VERSION: "8.0.x"
  NODE_VERSION: "20.x"
  AWS_REGION: us-east-1

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Para GitVersion

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.nuget/packages
          key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj') }}
          restore-keys: |
            ${{ runner.os }}-nuget-

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --configuration Release --no-restore

      - name: Run unit tests
        run: dotnet test --no-build --configuration Release --verbosity normal --collect:"XPlat Code Coverage"

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.cobertura.xml
          fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: "fs"
          scan-ref: "."
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"
          exit-code: "1"

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

      - name: OWASP Dependency-Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: "Talma-Service"
          path: "."
          format: "HTML"
          args: >
            --failOnCVSS 7
            --enableRetired

  deploy-dev:
    runs-on: ubuntu-latest
    needs: [build, security]
    if: github.ref == 'refs/heads/develop'
    environment: development

    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_DEV }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster talma-dev-cluster \
            --service talma-api \
            --force-new-deployment

      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster talma-dev-cluster \
            --services talma-api

      - name: Health check
        run: |
          curl -f https://api-dev.talma.com/health || exit 1

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "✅ Deploy to DEV successful: ${{ github.sha }}"
            }

  deploy-prod:
    runs-on: ubuntu-latest
    needs: [build, security]
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_PROD }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Blue-Green Deploy
        run: |
          # Desplegar nueva versión (green)
          aws ecs create-service \
            --cluster talma-prod-cluster \
            --service-name talma-api-green \
            --task-definition talma-api:${{ github.sha }} \
            --desired-count 2

          # Esperar estabilidad
          aws ecs wait services-stable \
            --cluster talma-prod-cluster \
            --services talma-api-green

          # Health check
          curl -f https://api-green.talma.com/health

          # Switch traffic
          aws elbv2 modify-listener \
            --listener-arn ${{ secrets.ALB_LISTENER_ARN }} \
            --default-actions TargetGroupArn=${{ secrets.GREEN_TG_ARN }}

          # Esperar 5 min, luego eliminar blue
          sleep 300
          aws ecs delete-service \
            --cluster talma-prod-cluster \
            --service talma-api-blue \
            --force
```

### Azure DevOps - YAML Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: "ubuntu-latest"

variables:
  buildConfiguration: "Release"
  dotnetVersion: "8.0.x"

stages:
  - stage: Build
    jobs:
      - job: BuildAndTest
        steps:
          - task: UseDotNet@2
            inputs:
              version: $(dotnetVersion)

          - task: DotNetCoreCLI@2
            displayName: "Restore dependencies"
            inputs:
              command: "restore"

          - task: DotNetCoreCLI@2
            displayName: "Build"
            inputs:
              command: "build"
              arguments: "--configuration $(buildConfiguration) --no-restore"

          - task: DotNetCoreCLI@2
            displayName: "Run tests"
            inputs:
              command: "test"
              arguments: '--configuration $(buildConfiguration) --no-build --collect:"XPlat Code Coverage"'
              publishTestResults: true

          - task: PublishCodeCoverageResults@2
            inputs:
              summaryFileLocation: "$(Agent.TempDirectory)/**/coverage.cobertura.xml"
              failIfCoverageEmpty: true

  - stage: Security
    dependsOn: Build
    jobs:
      - job: SecurityScans
        steps:
          - task: SonarCloudPrepare@2
            inputs:
              SonarCloud: "SonarCloud-Connection"
              organization: "talma"
              scannerMode: "MSBuild"
              projectKey: "talma-api"

          - task: SonarCloudAnalyze@2

          - task: SonarCloudPublish@2
            inputs:
              pollingTimeoutSec: "300"

          - task: dependency-check-build-task@6
            inputs:
              projectName: "Talma API"
              scanPath: "$(Build.SourcesDirectory)"
              format: "HTML"
              failOnCVSS: "7"

  - stage: DeployDev
    dependsOn: Security
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/develop'))
    jobs:
      - deployment: DeployToDev
        environment: "development"
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: "Azure-Dev"
                    appName: "talma-api-dev"
                    package: "$(Pipeline.Workspace)/**/*.zip"
                    deploymentMethod: "auto"
```

---

## 7. Ejemplos

### Terraform Pipeline

```yaml
# .github/workflows/terraform.yml
name: Terraform CI/CD

on:
  push:
    branches: [main]
    paths:
      - "terraform/**"
  pull_request:
    paths:
      - "terraform/**"

jobs:
  terraform:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./terraform

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.0
          cli_config_credentials_token: ${{ secrets.TF_API_TOKEN }}

      - name: Terraform Format
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        run: terraform plan -out=tfplan
        env:
          TF_VAR_environment: production

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve tfplan
```

### Monorepo Pipeline

```yaml
# .github/workflows/monorepo.yml
name: Monorepo CI/CD

on:
  push:
    branches: [main, develop]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      web: ${{ steps.filter.outputs.web }}
      shared: ${{ steps.filter.outputs.shared }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'apps/api/**'
              - 'libs/shared/**'
            web:
              - 'apps/web/**'
              - 'libs/shared/**'
            shared:
              - 'libs/shared/**'

  build-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build API
        run: |
          cd apps/api
          dotnet build

  build-web:
    needs: detect-changes
    if: needs.detect-changes.outputs.web == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Web
        run: |
          cd apps/web
          npm ci
          npm run build
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] Pipeline YAML versionado en repositorio
- [ ] Secrets almacenados en vault (no en código)
- [ ] Quality gates configurados y funcionando
- [ ] Branch protection rules habilitadas
- [ ] Deployment approvals configurados
- [ ] Rollback strategy documentada y probada
- [ ] Métricas de pipeline monitoreadas

### Métricas

```promql
# Deployment frequency
count(github_workflow_run{conclusion="success", name=~".*deploy.*"}) by (repository)

# Mean time to deployment
histogram_quantile(0.95, github_workflow_run_duration_seconds)

# Change failure rate
count(github_workflow_run{conclusion="failure"}) / count(github_workflow_run)

# Mean time to recovery (rollback)
avg(rollback_duration_seconds) by (environment)
```

### Dashboard SLIs

| Métrica                   | SLI        | Alertar si   |
| ------------------------- | ---------- | ------------ |
| Build success rate        | > 95%      | < 90%        |
| Pipeline duration         | < 15 min   | > 20 min     |
| Security scan failures    | 0 CRITICAL | > 0 CRITICAL |
| Deploy success rate       | > 99%      | < 95%        |
| Time to deploy (main→PRD) | < 30 min   | > 60 min     |

---

## 9. Referencias

**Frameworks:**

- [AWS Well-Architected - Operational Excellence](https://aws.amazon.com/architecture/well-architected/)
- [DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)

**Herramientas:**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Terraform Cloud](https://developer.hashicorp.com/terraform/cloud-docs)

**Security:**

- [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)
- [SonarQube Quality Gates](https://docs.sonarsource.com/sonarqube/latest/user-guide/quality-gates/)

**Buenas Prácticas:**

- Google SRE Book - "Release Engineering"
- "Continuous Delivery" - Jez Humble & David Farley
