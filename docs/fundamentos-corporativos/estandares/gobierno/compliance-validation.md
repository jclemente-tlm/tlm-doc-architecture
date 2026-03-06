---
id: compliance-validation
sidebar_position: 4
title: Compliance y Validación Automatizada
description: Validación de adherencia a estándares corporativos mediante checklists manuales y pipelines de CI/CD con SonarQube, Trivy, Checkov y OWASP.
tags: [gobierno, compliance, sonarqube, trivy, checkov]
---

# Compliance y Validación Automatizada

## Contexto

Este estándar define cómo verificar que servicios, código e infraestructura cumplen con los lineamientos corporativos, tanto mediante validación manual estructurada como mediante herramientas automatizadas en CI/CD.

**Conceptos incluidos:**

- **Compliance Validation** → Checklists y proceso de verificación manual por categoría
- **Automated Compliance** → Pipeline de GitHub Actions con SonarQube, Trivy, Checkov y OWASP

---

## Stack Tecnológico

| Componente              | Tecnología             | Versión | Uso                                 |
| ----------------------- | ---------------------- | ------- | ----------------------------------- |
| **SAST**                | SonarQube Community    | 10.0+   | Quality gates, security hotspots    |
| **Container Scanning**  | Trivy                  | 0.50+   | Vulnerabilidades en imágenes Docker |
| **IaC Scanning**        | Checkov                | 3.0+    | Issues de seguridad en Terraform    |
| **Dependency Scanning** | OWASP Dependency-Check | 9.0+    | CVEs en dependencias                |
| **CI/CD**               | GitHub Actions         | Latest  | Orquestación de compliance checks   |
| **IaC**                 | Terraform              | 1.7+    | Validación de configuraciones       |

---

## Compliance Validation

### ¿Qué es Compliance Validation?

Proceso de verificar que servicios, infraestructura y código cumplen con lineamientos, estándares y políticas corporativas.

**Tipos de validación:**

1. **Automated** — Ejecutada en CI/CD (SAST, container scanning, linting)
2. **Manual** — Ejecutada en architecture reviews y audits
3. **Continuous** — Monitoreo de drift en producción

### Checklists por Categoría

#### Seguridad

```markdown
- [ ] Autenticación JWT vía Keycloak
- [ ] RBAC implementado (no solo autenticación)
- [ ] Secrets en AWS Secrets Manager (no hardcoded, no en env vars plain text)
- [ ] Encryption at rest: RDS/S3 con encryption habilitado
- [ ] Encryption in transit: TLS 1.2+ en todas las comunicaciones
- [ ] Imagen Docker escaneada con Trivy, sin Critical CVEs
- [ ] Dependencias escaneadas, sin High CVEs sin plan
- [ ] Security groups con least privilege
- [ ] Audit logs para operaciones sensibles
```

#### APIs

```markdown
- [ ] Recursos con sustantivos plurales, verbos HTTP correctos
- [ ] Versionamiento /api/v1/ en todos los endpoints
- [ ] RFC 7807 ProblemDetails para 4xx/5xx
- [ ] Pagination implementada para listas (page, pageSize)
- [ ] OpenAPI specification actualizada
- [ ] Rate limiting en APIs públicas
- [ ] CORS configurado apropiadamente
- [ ] /health endpoint implementado
```

#### Datos

```markdown
- [ ] Database per service (no shared DB entre servicios)
- [ ] Servicio es dueño de sus propios datos
- [ ] Entity Framework Migrations versionadas en Git
- [ ] Automated backups habilitados (RDS)
- [ ] Connection pooling configurado
- [ ] Índices creados para queries frecuentes
- [ ] FluentValidation para todas las entradas
```

#### Infraestructura

```markdown
- [ ] 100% de infraestructura en Terraform
- [ ] Terraform state en S3 con locking (DynamoDB)
- [ ] Tags en todos los recursos: Environment, Service, Owner, CostCenter
- [ ] Servicios críticos con redundancia multi-AZ
- [ ] VPC con subnets públicas/privadas, NAT Gateway
- [ ] CloudWatch alarms para recursos críticos
- [ ] Budget alerts configurados
```

#### Observabilidad

```markdown
- [ ] Serilog con JSON format
- [ ] X-Correlation-ID en todos los logs
- [ ] OpenTelemetry instrumentado
- [ ] Prometheus metrics expuestas (/metrics)
- [ ] Grafana dashboard para el servicio
- [ ] Alertas críticas configuradas (error rate, latency)
- [ ] SLOs definidos para servicios críticos
```

### Plantilla de Informe de Cumplimiento

```markdown
# Informe de Cumplimiento - [Nombre del Servicio]

**Servicio**: [Nombre del servicio]
**Responsable**: [Tech Lead] | **Fecha**: YYYY-MM-DD | **Validador**: [Arquitecto]

---

## Cumplimiento General: XX% ([🟢/🟡/🔴] [CALIFICACIÓN])

- 🟢 Excelente: 90-100% | 🟢 Bueno: 80-89%
- 🟡 Requiere Mejora: 70-79% | 🔴 Crítico: < 70%

---

## Cumplimiento por Categoría

| Categoría       | Puntaje | Estado   |
| --------------- | ------- | -------- |
| Seguridad       | XX/10   | 🟢/🟡/🔴 |
| APIs            | XX/8    | 🟢/🟡/🔴 |
| Datos           | XX/7    | 🟢/🟡/🔴 |
| Infraestructura | XX/7    | 🟢/🟡/🔴 |
| Observabilidad  | XX/7    | 🟢/🟡/🔴 |
| Testing         | XX/10   | 🟢/🟡/🔴 |
| Documentación   | XX/15   | 🟢/🟡/🔴 |

---

## Elementos No Conformes

### 🔴 Alta Severidad

**NC-N: [Título]**

- **Estándar**: [link al estándar]
- **Estado Actual**: [qué hay actualmente]
- **Estado Esperado**: [qué debería haber]
- **Riesgo**: [impacto si no se corrige]
- **Remediación**: [acción concreta]
- **Plazo**: [N] días | **Responsable**: @handle

---

## Plan de Acción

| Ítem | Severidad | Responsable | Fecha límite | Estado         |
| ---- | --------- | ----------- | ------------ | -------------- |
| NC-N | Alta      | @handle     | YYYY-MM-DD   | ⏳ Planificado |

---

## Próxima Revisión: [YYYY-MM-DD]
```

---

## Automated Compliance

### ¿Qué es Automated Compliance?

Automatización de compliance checks integrada en CI/CD pipelines, proporcionando feedback inmediato sobre violaciones. Principio shift-left: detectar antes de deployment.

**Herramientas:**

| Herramienta     | Detecta                                   | Cuando falla, bloquea merge |
| --------------- | ----------------------------------------- | --------------------------- |
| SonarQube       | Code quality, security hotspots, coverage | Quality Gate no pasa        |
| Trivy           | CVEs en imágenes Docker                   | Critical o High encontrado  |
| Checkov         | Misconfigs en Terraform                   | Issues no suprimidos        |
| OWASP Dep-Check | CVEs en dependencias .NET                 | CVSS ≥ 7.0                  |
| markdownlint    | Formato de documentación                  | Reglas violadas             |

### GitHub Actions — Pipeline Completo

```yaml
# .github/workflows/compliance-checks.yml
name: Compliance Checks

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  sonarqube:
    name: SonarQube Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"
      - run: dotnet restore
      - run: dotnet build --no-restore --configuration Release
      - run: |
          dotnet test --no-build --configuration Release \
            /p:CollectCoverage=true /p:CoverletOutputFormat=opencover
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@v2
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
        with:
          args: >
            -Dsonar.projectKey=customer-service
            -Dsonar.cs.opencover.reportsPaths=**/coverage.opencover.xml
            -Dsonar.qualitygate.wait=true

  trivy-scan:
    name: Trivy Container Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t customer-service:${{ github.sha }} .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: customer-service:${{ github.sha }}
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"
          exit-code: "1"
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: "trivy-results.sarif"

  checkov-scan:
    name: Checkov IaC Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          output_file_path: checkov-results.sarif
          soft_fail: false
          skip_check: CKV_AWS_20,CKV_AWS_23 # Excepciones aprobadas

  dependency-check:
    name: OWASP Dependency Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"
      - uses: dependency-check/Dependency-Check_Action@main
        with:
          project: "customer-service"
          path: "."
          format: "JSON"
          args: >
            --failOnCVSS 7
            --suppression suppression.xml

  markdown-lint:
    name: Markdown Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: articulate/markdown-lint-action@v1
        with:
          config: .markdownlint.json
          files: "docs/**/*.md"

  adr-validation:
    name: ADR Format Validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/validate-adrs.sh

  compliance-summary:
    name: Compliance Summary
    runs-on: ubuntu-latest
    needs:
      [sonarqube, trivy-scan, checkov-scan, dependency-check, markdown-lint]
    if: always()
    steps:
      - name: Write Summary
        run: |
          echo "## 📊 Compliance Check Results" >> $GITHUB_STEP_SUMMARY
          echo "| Check | Status |" >> $GITHUB_STEP_SUMMARY
          echo "|-------|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| SonarQube | ${{ needs.sonarqube.result == 'success' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Trivy | ${{ needs.trivy-scan.result == 'success' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Checkov | ${{ needs.checkov-scan.result == 'success' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Dependency Check | ${{ needs.dependency-check.result == 'success' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
          echo "| Markdown Lint | ${{ needs.markdown-lint.result == 'success' && '✅' || '❌' }} |" >> $GITHUB_STEP_SUMMARY
```

### Quality Gates (sonar-project.properties)

```ini
sonar.projectKey=customer-service
sonar.projectName=Customer Service
sonar.sources=src
sonar.tests=tests
sonar.cs.opencover.reportsPaths=**/coverage.opencover.xml

# Quality Gates (configurado en SonarQube UI)
# Coverage > 80% | New Code Coverage > 85%
# Duplications < 3% | Maintainability: A
# Reliability: A | Security: A
# Security Hotspots Reviewed: 100%
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** validar compliance en CI/CD para todo PR a main/develop
- **MUST** ejecutar SAST (SonarQube) con quality gate que bloquee merge si no pasa
- **MUST** escanear imágenes Docker con Trivy — Critical/High bloquean merge
- **MUST** escanear Terraform con Checkov antes de plan/apply
- **MUST** audituar compliance manualmente al menos trimestralmente
- **MUST** generar compliance report con score y plan de remediación

### SHOULD (Fuertemente recomendado)

- **SHOULD** habilitar GitHub Security tab para visualizar SARIF reports
- **SHOULD** configurar quality gates para New Code (cobertura del código nuevo > 85%)
- **SHOULD** definir suppression.xml para excepciones aprobadas en Checkov/OWASP
- **SHOULD** publicar compliance dashboard en Grafana con tendencias históricas

### MUST NOT (Prohibido)

- **MUST NOT** mergear PRs con vulnerabilidades Critical/High sin plan de remediación
- **MUST NOT** omitir compliance checks en pipelines de servicios en producción
- **MUST NOT** deshabilitar quality gates permanentemente

---

## Referencias

- [Gestión de Excepciones](./exception-management.md) — proceso cuando no hay compliance
- [Ownership de Servicios](./service-ownership.md) — accountability por compliance
- [Architecture Board y Auditorías](./architecture-board-audits.md) — auditorías periódicas
- [SonarQube Quality Gates](https://docs.sonarsource.com/sonarqube/latest/user-guide/quality-gates/) — configuración
- [Trivy Documentation](https://aquasecurity.github.io/trivy/) — container scanning
- [Checkov Documentation](https://www.checkov.io/1.Welcome/What%20is%20Checkov.html) — IaC scanning
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/) — dependency scanning
