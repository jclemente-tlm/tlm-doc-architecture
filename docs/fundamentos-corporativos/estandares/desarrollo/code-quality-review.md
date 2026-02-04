---
id: code-quality-review
sidebar_position: 3
title: Calidad de Código y Revisión de Código
description: Estándar consolidado para control de calidad automatizado con SonarQube, cobertura de código, quality gates en CI/CD y revisión de código obligatoria siguiendo GitHub Flow
---

# Estándar Técnico — Calidad y Revisión de Código

## 1. Propósito

Quality gates automatizados (SonarQube, Coverlet) y code review obligatorio con aprobación técnica en PRs.

## 2. Alcance

**Aplica a:**

- Todo código .NET 8+ (backend, APIs, servicios)
- Infrastructure as Code (Terraform)
- Scripts de base de datos (migrations, stored procedures)
- Pull requests a branches protegidas (main, develop)
- Pipelines de CI/CD en GitHub Actions
- Configuraciones críticas (CI/CD pipelines, security policies)
- Documentación técnica (ADRs, estándares)

**No aplica a:**

- Scripts de infraestructura no críticos (bash dev)
- Código generado automáticamente
- Prototipos descartables (< 1 semana de vida)
- Migraciones de base de datos (EF Core Migrations - excluidas de cobertura)
- Hotfixes SEV-1 en producción (revisar post-merge)
- Configuraciones dev/sandbox personales
- Documentación no técnica (marketing, user guides)

## 3. Tecnologías Aprobadas

| Componente           | Tecnología             | Versión mínima | Observaciones                 |
| -------------------- | ---------------------- | -------------- | ----------------------------- |
| **Static Analysis**  | SonarQube Community    | 10.0+          | SAST + code smells            |
| **Linting**          | Roslyn Analyzers       | Built-in       | .NET analyzers                |
| **Code Coverage**    | Coverlet               | 6.0+           | Cross-platform .NET           |
| **Mutation Testing** | Stryker.NET            | 4.0+           | Opcional pero recomendado     |
| **Security Scan**    | OWASP Dependency-Check | 9.0+           | Vulnerabilidades de librerías |
| **CI/CD**            | GitHub Actions         | -              | Automatización de gates       |
| **IDE Integration**  | SonarLint              | Latest         | Feedback en tiempo real       |
| **VCS**              | GitHub                 | -              | GitHub Flow workflow          |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

## 4. Requisitos Obligatorios 🔴

### 4.1 Quality Gates Bloqueantes

- [ ] **Bugs críticos:** 0 blocker/critical bugs
- [ ] **Vulnerabilidades:** 0 blocker/critical vulnerabilities
- [ ] **Code Smells:** Rating A o B (< 50 code smells)
- [ ] **Security Hotspots:** 100% reviewed
- [ ] **Duplicación:** < 3% código duplicado
- [ ] **Complejidad cognitiva:** < 15 por función
- [ ] **Cobertura de código:** ≥ umbral definido por tipo

### 4.2 Cobertura por Tipo de Código

- [ ] **Lógica de negocio crítica:** ≥ 80% cobertura
- [ ] **Servicios de aplicación:** ≥ 70% cobertura
- [ ] **Infraestructura/utilidades:** ≥ 60% cobertura
- [ ] **Controllers/UI:** ≥ 50% cobertura

### 4.3 Métricas de Cobertura

- [ ] **Line Coverage:** Líneas ejecutadas
- [ ] **Branch Coverage:** Ramas condicionales
- [ ] **Mutation Score:** Opcional (≥ 70%)

### 4.4 Proceso de Code Review

- [ ] **Branch protection** habilitado en `main`/`master`
- [ ] **Mínimo 1 aprobación** de reviewer técnico antes de merge
- [ ] **CI/CD passing:** tests, linters, security scans OK
- [ ] **NO self-approval** (autor ≠ reviewer)
- [ ] **Max 48 horas** para primera revisión (SLA)
- [ ] **Cambios menores** (<50 líneas): 1 reviewer
- [ ] **Cambios mayores** (>200 líneas): 2 reviewers O arquitecto
- [ ] **IaC changes:** Reviewer con experiencia AWS/Terraform

### 4.5 Responsabilidades del Autor

- [ ] **PR title descriptivo:** `[TICKET-123] Add user authentication`
- [ ] **Descripción clara:** Qué cambia, por qué, cómo testear
- [ ] **Self-review** antes de pedir aprobación
- [ ] **Tests incluidos** (unit + integration cuando aplique)
- [ ] **Documentación actualizada** (README, ADRs si aplica)
- [ ] **Commits atómicos** con mensajes claros
- [ ] **PR pequeño** (<400 líneas idealmente, max 800)

### 4.6 Responsabilidades del Reviewer

- [ ] **Revisar en <48 horas** (priorizar PRs bloqueantes)
- [ ] **Comentarios constructivos** (no solo críticas)
- [ ] **Verificar checklist completo** (funcionalidad, seguridad, performance, arquitectura)
- [ ] **Probar localmente** si cambios complejos
- [ ] **Aprobar SOLO si entiendes completamente**
- [ ] **Sugerir mejoras** (NO reescribir todo)
- [ ] **Distinguir:** Bloqueante vs nice-to-have

### 4.7 Exclusiones de Cobertura Permitidas

- [ ] Código generado automáticamente
- [ ] DTOs/POCOs sin lógica
- [ ] Program.cs/Startup.cs (configuración)
- [ ] Migraciones de base de datos
- [ ] Archivos \*.Designer.cs

## 5. Prohibiciones

- ❌ Merge sin pasar quality gates
- ❌ Merge sin code review (excepto hotfix SEV-1)
- ❌ Deshabilitar analyzers para "hacer pasar" el build
- ❌ Secretos o credentials en código
- ❌ `#pragma warning disable` sin justificación en comentario
- ❌ Reducir umbrales de cobertura sin ADR aprobado
- ❌ Code smells con severidad "Critical" sin resolver
- ❌ Self-approval de PRs
- ❌ PRs >800 líneas sin justificación

## 6. Configuración de Quality Gates

### 6.1 SonarQube Configuration

```properties
# sonar-project.properties
# Proyecto
sonar.projectKey=talma-payment-api
sonar.projectName=Payment API
sonar.projectVersion=1.0.0

# Código fuente
sonar.sources=src
sonar.tests=tests
sonar.sourceEncoding=UTF-8

# Exclusiones
sonar.coverage.exclusions=**/Migrations/**,**/Program.cs,**/*.Designer.cs
sonar.exclusions=**/obj/**,**/bin/**,**/*.Generated.cs

# .NET específico
sonar.cs.opencover.reportsPaths=**/coverage.opencover.xml
sonar.cs.vstest.reportsPaths=**/*.trx

# Quality Gate
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300
```

### 6.2 Roslyn Analyzers

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <AnalysisLevel>latest</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="SonarAnalyzer.CSharp" Version="9.12.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
    <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="8.0.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
  </ItemGroup>

  <!-- Warnings as Errors -->
  <PropertyGroup>
    <WarningsAsErrors>
      S1200,   <!-- Classes should not be coupled to too many other classes -->
      S3776,   <!-- Cognitive Complexity of methods should not be too high -->
      CA1062,  <!-- Validate arguments of public methods -->
      CA2007   <!-- Do not directly await a Task -->
    </WarningsAsErrors>
  </PropertyGroup>
</Project>
```

### 6.3 Coverlet Configuration

```xml
<!-- PaymentApi.csproj -->
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <!-- Coverlet -->
  <ItemGroup>
    <PackageReference Include="coverlet.collector" Version="6.0.0">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
  </ItemGroup>

  <PropertyGroup>
    <CollectCoverage>true</CollectCoverage>
    <CoverletOutputFormat>opencover,cobertura,json</CoverletOutputFormat>
    <CoverletOutput>./coverage/</CoverletOutput>

    <!-- Umbrales -->
    <Threshold>80</Threshold>
    <ThresholdType>line,branch</ThresholdType>
    <ThresholdStat>total</ThresholdStat>

    <!-- Exclusiones -->
    <ExcludeByFile>**/Migrations/**/*.cs,**/Program.cs</ExcludeByFile>
    <ExcludeByAttribute>GeneratedCodeAttribute,ExcludeFromCodeCoverageAttribute</ExcludeByAttribute>
  </PropertyGroup>
</Project>
```

## 7. GitHub Actions — Pipeline Integrado

```yaml
# .github/workflows/quality-gates.yml
name: Quality Gates & Code Review

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  quality-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Shallow clones should be disabled for SonarQube

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      # SonarQube Scan
      - name: Install SonarScanner
        run: dotnet tool install --global dotnet-sonarscanner

      - name: Begin SonarQube Analysis
        run: |
          dotnet sonarscanner begin \
            /k:"talma-payment-api" \
            /d:sonar.host.url="${{ secrets.SONAR_HOST_URL }}" \
            /d:sonar.token="${{ secrets.SONAR_TOKEN }}" \
            /d:sonar.cs.opencover.reportsPaths="**/coverage.opencover.xml"

      # Build + Tests + Coverage
      - name: Build and Test
        run: |
          dotnet build --configuration Release --no-incremental
          dotnet test \
            --configuration Release \
            --no-build \
            --collect:"XPlat Code Coverage" \
            --results-directory ./coverage \
            -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=opencover

      - name: End SonarQube Analysis
        run: dotnet sonarscanner end /d:sonar.token="${{ secrets.SONAR_TOKEN }}"

      # Coverage Report
      - name: Code Coverage Report
        uses: irongut/CodeCoverageSummary@v1.3.0
        with:
          filename: coverage/**/coverage.opencover.xml
          badge: true
          fail_below_min: true
          format: markdown
          hide_branch_rate: false
          hide_complexity: false
          indicators: true
          output: both
          thresholds: "70 80"

      - name: Add Coverage PR Comment
        uses: marocchino/sticky-pull-request-comment@v2
        if: github.event_name == 'pull_request'
        with:
          recreate: true
          path: code-coverage-results.md

      # Quality Gate Status Check
      - name: SonarQube Quality Gate Check
        uses: sonarsource/sonarqube-quality-gate-action@master
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      # Dependency Vulnerability Scan
      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: "payment-api"
          path: "."
          format: "JSON"
          failBuildOnCVSS: 7

      - name: Upload Dependency Check Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: dependency-check-report
          path: dependency-check-report.json
```

## 8. Checklist de Code Review

### 8.1 Funcionalidad

- [ ] Cumple requisitos del ticket/feature
- [ ] Casos edge cubiertos (inputs vacíos, null, errores de red)
- [ ] Validaciones de entrada implementadas
- [ ] Manejo de errores apropiado (try-catch, logs)
- [ ] Comportamiento idempotente cuando aplique

### 8.2 Seguridad

- [ ] **NO secrets hardcodeados** (passwords, API keys, tokens)
- [ ] **Inputs sanitizados** (prevención SQL injection, XSS)
- [ ] **Autenticación/autorización correcta** (atributos `[Authorize]`)
- [ ] **HTTPS enforced** para APIs públicas
- [ ] **Logs NO exponen información sensible** (PII, passwords)
- [ ] **Dependencias sin vulnerabilidades críticas** (`dotnet list package --vulnerable`)
- [ ] **Claims validation** para autorización granular

### 8.3 Performance

- [ ] **Queries BD eficientes** (índices, NO N+1)
- [ ] **Uso apropiado de caché** (Redis, memory cache)
- [ ] **Paginación implementada** para listas grandes (NO `SELECT *` sin LIMIT)
- [ ] **Async/await usado correctamente** (NO blocking calls)
- [ ] **Conexiones BD/HTTP cerradas apropiadamente**
- [ ] **Circuit breakers** implementados para llamadas externas
- [ ] **Timeouts configurados** (HttpClient, DB connections)

### 8.4 Arquitectura y Diseño

- [ ] **Sigue principios SOLID** (responsabilidad única, etc.)
- [ ] **Consistente con patrones del proyecto** (repositories, services)
- [ ] **NO lógica de negocio en controllers**
- [ ] **Inyección de dependencias usada correctamente**
- [ ] **Nombres claros y descriptivos** (métodos, variables, clases)
- [ ] **Separation of Concerns** (UI, lógica, datos)

### 8.5 Testing

- [ ] **Unit tests para lógica de negocio** (coverage >80%)
- [ ] **Integration tests para APIs/BD** cuando aplique
- [ ] **Tests pasan localmente Y en CI**
- [ ] **Tests nombrados:** `MethodName_Scenario_ExpectedResult`
- [ ] **Mocks usados apropiadamente** (NO dependencias reales en unit tests)
- [ ] **Arrange-Act-Assert pattern** (AAA)
- [ ] **Tests aislados** (no dependencias entre tests)

### 8.6 Infrastructure as Code

- [ ] **Recursos parametrizados** (NO hardcodear IPs, ARNs)
- [ ] **Tags obligatorios:** `Environment`, `Project`, `Owner`, `CostCenter`
- [ ] **Security groups restrictivos** (NO `0.0.0.0/0` en producción)
- [ ] **Encryption habilitado** (RDS, S3, EBS con KMS)
- [ ] **Terraform plan ejecutado y validado**
- [ ] **State backend configurado** (S3 + DynamoDB)
- [ ] **Least privilege IAM policies** (NO wildcards `*`)

### 8.7 Documentación

- [ ] **README actualizado** si cambian comandos/setup
- [ ] **ADR creado** si decisión arquitectónica significativa
- [ ] **Comentarios en código SOLO cuando necesario** (código auto-explicativo primero)
- [ ] **API endpoints documentados** (Swagger/OpenAPI)
- [ ] **Environment variables documentadas**

## 9. Tamaño de PRs

| Tamaño | Líneas  | Tiempo Revisión | Reviewers      | Recomendación            |
| ------ | ------- | --------------- | -------------- | ------------------------ |
| **XS** | <50     | <30 min         | 1              | ✅ Ideal                 |
| **S**  | 50-200  | 1 hora          | 1              | ✅ OK                    |
| **M**  | 200-400 | 2-3 horas       | 1-2            | ⚠️ Considerar dividir    |
| **L**  | 400-800 | >4 horas        | 2              | 🔴 Dividir si es posible |
| **XL** | >800    | >1 día          | 2 + arquitecto | 🔴 Dividir obligatorio   |

**PRs >800 líneas requieren justificación** (ej: migration masivo, generación código).

## 10. Branch Protection Rules

```yaml
# GitHub Branch Protection Settings para 'main'
require_pull_request_reviews: true
required_approving_review_count: 1
dismiss_stale_reviews: true # Nueva commit → re-approval
require_code_owner_reviews: false # Opcional, para equipos grandes
require_status_checks_before_merging: true
required_status_checks:
  - ci/build
  - ci/test
  - security/dependency-check
  - sonarqube/quality-gate
  - coverage/threshold
enforce_admins: true # Ni admins pueden bypass
allow_force_pushes: false
allow_deletions: false
require_linear_history: true # Squash or rebase (NO merge commits)
```

## 11. PR Template

```markdown
## Descripción

[Breve resumen del cambio]

## Ticket

Closes #[TICKET-ID]

## Tipo de cambio

- [ ] Feature nueva
- [ ] Bug fix
- [ ] Refactoring
- [ ] Cambio de infraestructura
- [ ] Documentación

## Cómo testear

1. Levantar ambiente local: `docker-compose up`
2. Ejecutar: `curl -X POST http://localhost:5000/api/orders`
3. Verificar: response 201 Created

## Checklist

- [ ] Self-review realizado
- [ ] Tests agregados/actualizados (coverage >80%)
- [ ] Documentación actualizada
- [ ] CI passing (build, tests, SonarQube, dependency-check)
- [ ] NO secrets hardcodeados
- [ ] Cobertura de código cumple umbral
- [ ] SonarQube Quality Gate: PASSED

## Screenshots (si aplica)

[Capturas de pantalla para cambios UI]

## Impacto

- [ ] Breaking change (requiere migración de clientes)
- [ ] Cambio backward-compatible
- [ ] Impacto en performance (describir)
```

## 12. Excepciones

**Hotfixes SEV-1**: Merge sin review permitido, post-merge review dentro de 24h.
**Cambios cosméticos** (typos, formateo): 1 approval suficiente.

## 13. Validación de Cumplimiento

### 13.1 Script de Validación Local

```bash
#!/bin/bash
# scripts/validate-code-quality.sh

echo "🔍 Validando estándares de calidad de código..."

# 1. Verificar SonarQube configurado
echo "1. SonarQube configuración..."
test -f sonar-project.properties && echo "✅ sonar-project.properties exists" || echo "❌ Missing sonar-project.properties"

# 2. Verificar Roslyn Analyzers
echo "2. Roslyn Analyzers..."
grep -r "SonarAnalyzer.CSharp" **/*.csproj && echo "✅ SonarAnalyzer configured" || echo "❌ Missing SonarAnalyzer"

# 3. Ejecutar análisis estático
echo "3. Ejecutando análisis estático..."
dotnet build /p:TreatWarningsAsErrors=true

# 4. Ejecutar tests con cobertura
echo "4. Ejecutando tests con cobertura..."
dotnet test \
  --collect:"XPlat Code Coverage" \
  --results-directory ./coverage \
  -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=opencover

# 5. Verificar umbrales de cobertura
echo "5. Verificando umbrales de cobertura..."
COVERAGE=$(grep -oP 'line-rate="\K[^"]+' coverage/**/coverage.cobertura.xml | head -1)
COVERAGE_PERCENT=$(echo "$COVERAGE * 100" | bc)
echo "Cobertura actual: ${COVERAGE_PERCENT}%"

if (( $(echo "$COVERAGE_PERCENT < 70" | bc -l) )); then
  echo "❌ Cobertura por debajo del umbral (70%)"
  exit 1
else
  echo "✅ Cobertura cumple umbral"
fi

# 6. Verificar vulnerabilidades
echo "6. Verificando vulnerabilidades de dependencias..."
dotnet list package --vulnerable --include-transitive

# 7. Verificar secrets hardcodeados
echo "7. Verificando secrets hardcodeados..."
git diff --cached | grep -iE "(password|apikey|secret|token)" && echo "⚠️ Posible secret hardcodeado" || echo "✅ No secrets detectados"

echo "✅ Validación de calidad completada"
```

### 13.2 Métricas de Cumplimiento

| Métrica                        | Target    | Verificación                       |
| ------------------------------ | --------- | ---------------------------------- |
| **Bugs críticos**              | 0         | SonarQube dashboard                |
| **Vulnerabilidades críticas**  | 0         | SonarQube + OWASP Dependency-Check |
| **Code Smells rating**         | A o B     | SonarQube maintainability          |
| **Cobertura de código**        | ≥ 70%     | Coverage report en PR              |
| **Complejidad cognitiva**      | < 15      | SonarQube complexity metrics       |
| **Duplicación**                | < 3%      | SonarQube duplications             |
| **Security Hotspots reviewed** | 100%      | SonarQube security review          |
| **Build warnings**             | 0         | GitHub Actions build log           |
| **PRs mergeados sin review**   | 0%        | GitHub audit log                   |
| **Tiempo primera revisión**    | <48 horas | GitHub metrics                     |
| **PRs >800 líneas**            | <5%       | GitHub metrics                     |

### 13.3 Comandos de Verificación

```bash
# Verificar SonarQube Quality Gate
PROJECT_STATUS=$(curl -s -u "$SONAR_TOKEN:" \
  "$SONAR_HOST_URL/api/qualitygates/project_status?projectKey=talma-payment-api" \
  | jq -r '.projectStatus.status')

if [ "$PROJECT_STATUS" = "OK" ]; then
  echo "✅ SonarQube Quality Gate: PASSED"
else
  echo "❌ SonarQube Quality Gate: FAILED"
  exit 1
fi

# Verificar branch protection activo
gh api repos/:owner/:repo/branches/main/protection \
  | jq '{required_pull_request_reviews, required_status_checks, enforce_admins}'

# Verificar PRs sin review
gh pr list --state merged --json number,reviews --jq '.[] | select(.reviews | length == 0)'

# Verificar cobertura de código
dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage
reportgenerator -reports:"coverage/**/coverage.cobertura.xml" -targetdir:"coverage/report" -reporttypes:Html
echo "Reporte disponible en: coverage/report/index.html"
```

## 14. Referencias

**SonarQube:**

- [SonarQube Quality Model](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [SonarQube for .NET](https://docs.sonarqube.org/latest/analyzing-source-code/languages/csharp/)
- [SonarLint IDE Extension](https://www.sonarsource.com/products/sonarlint/)

**Code Quality:**

- [Google Code Review Guidelines](https://google.github.io/eng-practices/review/)
- [Clean Code, Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Refactoring, Martin Fowler](https://martinfowler.com/books/refactoring.html)

**Testing:**

- [Coverlet Documentation](https://github.com/coverlet-coverage/coverlet)
- [Stryker.NET Mutation Testing](https://stryker-mutator.io/docs/stryker-net/introduction/)
- [xUnit Best Practices](https://xunit.net/docs/getting-started/netcore/cmdline)

**Security:**

- [OWASP ASVS V14 - SAST](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)

**GitHub:**

- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [About pull request reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews)
