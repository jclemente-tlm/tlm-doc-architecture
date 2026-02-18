---
id: build-automation
sidebar_position: 2
title: Build Automation
description: Automatización de compilación, pruebas y empaquetado mediante pipelines CI/CD
---

# Build Automation

## Contexto

Este estándar establece **Build Automation**: proceso de **compilación, pruebas y empaquetado automatizado** mediante pipelines CI/CD. Builds manuales son lentos, inconsistentes y propensos a errores. Complementa el [lineamiento de CI/CD Pipelines](../../lineamientos/operabilidad/01-cicd-pipelines.md) enfocándose en la **fase de construcción**.

---

## Concepto Fundamental

```yaml
# Build Manual (❌) vs Automated (✅)

Manual Build:
  Developer: 1. git pull
    2. dotnet restore
    3. dotnet build -c Release
    4. dotnet test
    5. docker build -t sales-service:v1.2.3 .
    6. docker push ghcr.io/talma/sales-service:v1.2.3
    7. Update Terraform image tag
    8. terraform apply

  Problems: ❌ Forgot step (no tests run)
    ❌ Different environment (works on my machine)
    ❌ Manual version tag (typo v1.2.3 vs v1.23)
    ❌ Takes 15-20 min (human time)
    ❌ No validation (SonarQube skip)

Automated Build (✅):
  GitHub Actions on push to main: 1. Checkout code
    2. Setup .NET SDK (deterministic version)
    3. Restore dependencies (with cache)
    4. Build with Release config
    5. Run unit tests (fail pipeline if fails)
    6. Run integration tests
    7. SonarQube analysis (quality gate)
    8. Security scan (Trivy, Snyk)
    9. Docker build (multi-stage)
    10. Push to GHCR (auto tag from commit SHA)
    11. Update Task Definition (auto deploy to dev)

  Benefits: ✅ Repeatable (same steps every time)
    ✅ Fast (5-7 min, parallelized)
    ✅ Validated (all gates passed)
    ✅ Auditable (logs + artifacts stored)
    ✅ Zero human effort (trigger on push)
```

## Pipeline Structure

```yaml
# .github/workflows/build.yml

name: Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  DOTNET_VERSION: "8.0.x"
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ✅ Job 1: Build & Test
  build:
    runs-on: ubuntu-latest

    steps:
      # Checkout code
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Full history for SonarQube

      # Setup .NET SDK (deterministic)
      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}

      # Restore dependencies (with cache)
      - name: Cache NuGet Packages
        uses: actions/cache@v3
        with:
          path: ~/.nuget/packages
          key: ${{ runner.os }}-nuget-${{ hashFiles('**/packages.lock.json') }}

      - name: Restore Dependencies
        run: dotnet restore

      # Build (Release config)
      - name: Build
        run: dotnet build --configuration Release --no-restore

      # Run Tests (Unit + Integration)
      - name: Unit Tests
        run: dotnet test tests/SalesService.UnitTests --configuration Release --no-build --logger "trx;LogFileName=unit-tests.trx"

      - name: Integration Tests
        run: dotnet test tests/SalesService.IntegrationTests --configuration Release --no-build --logger "trx;LogFileName=integration-tests.trx"
        env:
          DATABASE_URL: postgres://localhost:5432/test
          KAFKA_BROKERS: localhost:9092

      # Upload test results
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: |
            tests/**/*.trx
            tests/**/TestResults/*

      # Test Coverage
      - name: Code Coverage
        run: |
          dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage
          dotnet tool install --global dotnet-reportgenerator-globaltool
          reportgenerator -reports:./coverage/**/coverage.cobertura.xml -targetdir:./coverage/report -reporttypes:Html

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/**/coverage.cobertura.xml
          fail_ci_if_error: true

  # ✅ Job 2: Quality Analysis
  quality:
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # SonarQube Analysis
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        with:
          args: >
            -Dsonar.projectKey=sales-service
            -Dsonar.sources=src/
            -Dsonar.tests=tests/
            -Dsonar.cs.opencover.reportsPaths=coverage/**/coverage.opencover.xml
            -Dsonar.coverage.exclusions=**/*Tests.cs,**/Program.cs

      # Quality Gate Check
      - name: SonarQube Quality Gate
        uses: sonarsource/sonarqube-quality-gate-action@master
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        # ✅ Pipeline fails if quality gate fails

  # ✅ Job 3: Security Scan
  security:
    runs-on: ubuntu-latest
    needs: build

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # Dependency Vulnerabilities (Snyk)
      - name: Snyk Dependency Scan
        uses: snyk/actions/dotnet@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high --fail-on=all

      # SAST (Static Analysis)
      - name: SAST Security Scan
        run: |
          dotnet tool install --global security-scan
          security-scan --project SalesService.csproj --fail-on-high

  # ✅ Job 4: Docker Build & Push
  docker:
    runs-on: ubuntu-latest
    needs: [build, quality, security]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'

    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # Docker Buildx (multi-platform)
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # Login to GitHub Container Registry
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # Extract metadata (tags, labels)
      - name: Extract Metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}

      # Build and push
      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

      # Trivy Security Scan (container image)
      - name: Trivy Image Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ steps.meta.outputs.version }}
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"
          exit-code: "1" # Fail if critical vulns

      - name: Upload Trivy Results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: "trivy-results.sarif"
```

## Dockerfile Optimization

```dockerfile
# ✅ Multi-stage build (reduce image size)

# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src

# Copy csproj first (layer caching)
COPY ["src/SalesService/SalesService.csproj", "src/SalesService/"]
COPY ["src/SalesService.Domain/SalesService.Domain.csproj", "src/SalesService.Domain/"]
COPY ["src/SalesService.Infrastructure/SalesService.Infrastructure.csproj", "src/SalesService.Infrastructure/"]

# Restore dependencies (cached if csproj unchanged)
RUN dotnet restore "src/SalesService/SalesService.csproj"

# Copy source code
COPY . .

# Build
WORKDIR "/src/src/SalesService"
RUN dotnet build "SalesService.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "SalesService.csproj" -c Release -o /app/publish \
    --no-restore \
    --self-contained false \
    /p:PublishTrimmed=false

# Stage 3: Runtime (minimal image)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final
WORKDIR /app

# ✅ Non-root user (security)
RUN addgroup -g 1001 appuser && \
    adduser -u 1001 -G appuser -s /bin/sh -D appuser && \
    chown -R appuser:appuser /app

USER appuser

# Copy published artifacts
COPY --from=publish /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Environment variables
ENV ASPNETCORE_URLS=http://+:8080 \
    ASPNETCORE_ENVIRONMENT=Production \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false

ENTRYPOINT ["dotnet", "SalesService.dll"]
```

## Build Optimization

```yaml
# Técnicas para builds rápidos

1. Layer Caching:

   Dockerfile:
     # ✅ Copy dependencies first (changes infrequently)
     COPY package.json package-lock.json ./
     RUN npm install

     # ✅ Copy source code last (changes frequently)
     COPY . .

   Result: Dependencies cached, rebuild only code layer

2. Parallel Jobs:

   GitHub Actions:
     build:
       strategy:
         matrix:
           os: [ubuntu-latest, windows-latest]
           dotnet: ['6.0.x', '8.0.x']
       steps:
         - run: dotnet test

   Result: 4 combinations run in parallel

3. Dependency Caching:

   - uses: actions/cache@v3
     with:
       path: ~/.nuget/packages
       key: ${{ runner.os }}-nuget-${{ hashFiles('**/packages.lock.json') }}

   Result: Restore takes 10s instead of 2 min

4. Incremental Build:

   dotnet build --no-restore  # Skip restore (already done)
   dotnet test --no-build     # Skip build (already done)

   Result: Avoid duplicate work

5. Remote Caching:

   Docker Buildx:
     cache-from: type=gha  # GitHub Actions cache
     cache-to: type=gha,mode=max

   Result: Share layers across builds
```

## Quality Gates

```yaml
# Pipeline debe fallar si:

Gate 1: Tests Fail

  - name: Unit Tests
    run: dotnet test --logger "trx"

  # ✅ Exit code 1 if any test fails → Pipeline stops

Gate 2: Coverage < Threshold

  - name: Coverage Check
    run: |
      COVERAGE=$(jq '.summary.lineCoverage' coverage/summary.json)
      if (( $(echo "$COVERAGE < 80" | bc -l) )); then
        echo "Coverage $COVERAGE% < 80% threshold"
        exit 1
      fi

Gate 3: SonarQube Quality Gate

  - name: SonarQube Quality Gate
    uses: sonarsource/sonarqube-quality-gate-action@master
    timeout-minutes: 5

  # ✅ Fails if:
  #   - Code smells > 50
  #   - Duplications > 3%
  #   - Security hotspots > 0

Gate 4: High Severity Vulnerabilities

  - name: Snyk Scan
    run: snyk test --severity-threshold=high --fail-on=all

  # ✅ Fails if high/critical vulnerabilities found

Gate 5: Container Security

  - name: Trivy Scan
    run: |
      trivy image --severity CRITICAL,HIGH --exit-code 1 \
        ghcr.io/talma/sales-service:${{ github.sha }}

  # ✅ Fails if critical vulnerabilities in image

Gate 6: Dockerfile Best Practices

  - name: Hadolint
    run: docker run --rm -i hadolint/hadolint < Dockerfile

  # ✅ Checks:
  #   - Non-root user
  #   - No hardcoded secrets
  #   - HEALTHCHECK defined
  #   - Minimal base image
```

## Artifacts Management

```yaml
# Build Artifacts Storage

GitHub Packages (GHCR):
  Docker Images:
    - URL: ghcr.io/talma/sales-service:main-a1b2c3d
    - Retention: 30 days for dev, 90 days for prod tags
    - Cleanup: Delete untagged after 7 days

  NuGet Packages (shared libraries):
    - URL: https://nuget.pkg.github.com/talma/index.json
    - Versioning: SemVer (1.2.3)

AWS S3 (build logs and test reports): s3://talma-ci-artifacts/
  ├─ builds/
  │   └─ sales-service/
  │       └─ main/
  │           └─ a1b2c3d/
  │               ├─ build.log
  │               ├─ test-results.trx
  │               └─ coverage-report.html
  └─ releases/
  └─ sales-service-v1.2.3.zip

Test Results:
  GitHub Actions Artifacts:
    - name: test-results
      path: tests/**/TestResults/*.trx
      retention-days: 30

SBOM (Software Bill of Materials):
  - name: Generate SBOM
    run: |
      syft ghcr.io/talma/sales-service:${{ github.sha }} \
        -o spdx-json > sbom.spdx.json

  - name: Upload SBOM
    uses: actions/upload-artifact@v3
    with:
      name: sbom
      path: sbom.spdx.json
```

## Build Metrics

```yaml
# Monitorear performance del pipeline

Metrics:

  Build Duration:
    - Target: < 10 min (total pipeline)
    - Alert: > 15 min (investigate bottleneck)
    - Dashboard: Grafana "CI/CD Performance"

  Success Rate:
    - Target: > 95% (green builds)
    - Alert: < 90% (frequent failures)
    - Cause: Flaky tests, infrastructure issues

  Queue Time:
    - Target: < 1 min (start immediately)
    - Alert: > 5 min (runner shortage)
    - Action: Add more runners

  Cache Hit Rate:
    - Target: > 80% (dependencies cached)
    - Alert: < 50% (cache not working)
    - Fix: Verify cache key stability

GitHub Actions Insights:

  - Navigate: Repo → Insights → Actions
  - View:
    - Workflow runs (success/fail trend)
    - Job duration (identify slow steps)
    - Concurrent jobs (runner utilization)

Custom Dashboard:

  Prometheus metrics from GitHub API:
    - workflow_run_duration_seconds
    - workflow_run_conclusion (success/failure)
    - workflow_queue_time_seconds

  Grafana dashboard "CI/CD Health"
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** automatizar build en cada push a main/develop
- **MUST** ejecutar unit tests en pipeline (fail on error)
- **MUST** validar coverage mínimo 80%
- **MUST** ejecutar security scan (Snyk, Trivy)
- **MUST** usar multi-stage Dockerfile (minimize image size)
- **MUST** generar artifacts versionados (Docker tags con commit SHA)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar dependency caching (NuGet, npm)
- **SHOULD** paralelizar jobs independientes (build + quality + security)
- **SHOULD** ejecutar integration tests en pipeline
- **SHOULD** generar SBOM (Software Bill of Materials)
- **SHOULD** monitorear build duration (< 10 min target)

### MUST NOT (Prohibido)

- **MUST NOT** hardcodear secrets en Dockerfile o workflow
- **MUST NOT** usar `latest` tag en production (use immutable tags)
- **MUST NOT** skip tests en pipeline (no `--no-test` flag)
- **MUST NOT** run as root en container (use non-root user)

---

## Referencias

- [Lineamiento: CI/CD Pipelines](../../lineamientos/operabilidad/01-cicd-pipelines.md)
- [Container Scanning](../seguridad/container-scanning.md)
- [SBOM Generation](../seguridad/sbom.md)
- [Deployment Strategies](./deployment-strategies.md)
- [Artifact Management](./artifact-management.md)
