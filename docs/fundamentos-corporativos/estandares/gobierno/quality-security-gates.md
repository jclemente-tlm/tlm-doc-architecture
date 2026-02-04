---
id: quality-security-gates
sidebar_position: 5
title: Quality & Security Gates
description: Estándar para implementación de quality gates automatizados en CI/CD que bloquean deploys con issues de calidad o seguridad
---

# Estándar Técnico — Quality & Security Gates

---

## 1. Propósito

Establecer gates automatizados en pipelines de CI/CD para prevenir que código con defectos de calidad, vulnerabilidades de seguridad o incumplimiento de estándares llegue a producción, garantizando calidad y seguridad by design.

---

## 2. Alcance

**Aplica a:**

- Todos los pipelines de CI/CD
- Pull requests antes de merge
- Builds de código fuente
- Imágenes de contenedores
- Infraestructura as Code (Terraform, CloudFormation)
- Dependencias de terceros
- Configuraciones de sistemas

**No aplica a:**

- Scripts de desarrollo local
- Prototipos no destinados a producción
- Hotfixes de emergencia (con proceso de excepción)

---

## 3. Tecnologías Aprobadas

| Componente             | Tecnología        | Uso Principal               | Observaciones              |
| ---------------------- | ----------------- | --------------------------- | -------------------------- |
| **Code Quality**       | SonarQube 10.0+   | SAST, code smells           | Quality Gates obligatorios |
| **Security Scanning**  | Trivy             | Container vulnerabilities   | Fail on CRITICAL           |
| **Dependency Check**   | OWASP Dep-Check   | CVEs en dependencias        | Integrado en build         |
| **Secret Detection**   | TruffleHog        | Secrets en commits          | Pre-commit + CI            |
| **IaC Security**       | Checkov           | Terraform misconfigurations | Policy as Code             |
| **IaC Security**       | tfsec             | Complementario a Checkov    | Terraform-specific         |
| **License Compliance** | FOSSA             | OSS license checking        | Prohibir GPL en backend    |
| **Code Coverage**      | Codecov/Coveralls | Coverage reporting          | Mínimo 80% obligatorio     |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Quality Gates - SonarQube

- [ ] **Coverage:** nuevas líneas > 80%
- [ ] **Duplicación:** < 3% duplicated lines
- [ ] **Maintainability:** Rating A (Technical Debt < 5%)
- [ ] **Reliability:** Rating A (0 bugs CRITICAL/HIGH)
- [ ] **Security:** Rating A (0 vulnerabilities CRITICAL/HIGH)
- [ ] **Security Hotspots:** 100% reviewed

### Security Gates

- [ ] **Container Scan:** 0 vulnerabilidades CRITICAL
- [ ] **Dependency Check:** 0 CVEs HIGH con fix disponible
- [ ] **Secret Detection:** 0 secrets detectados
- [ ] **IaC Security:** tfsec + Checkov pass sin CRITICAL
- [ ] **SAST:** SonarQube Security Rating A

### Performance Gates

- [ ] **Build time:** < 15 minutos (fail si > 20 min)
- [ ] **Docker image size:** < 500MB (warn si > 300MB)
- [ ] **Startup time:** < 30 segundos para APIs

### Compliance Gates

- [ ] **License compliance:** solo licenses permitidas
- [ ] **Policy as Code:** OPA policies pass
- [ ] **Branch protection:** PR reviews + approvals
- [ ] **Commit signing:** GPG-signed commits

---

## 5. Prohibiciones

- ❌ Bypass de quality gates sin excepción formal
- ❌ Deploy con vulnerabilidades CRITICAL abiertas
- ❌ Código sin pasar SonarQube Quality Gate
- ❌ Deshabilitar security scans
- ❌ Merge sin code coverage > umbral
- ❌ Secrets en código fuente
- ❌ Dependencies con CVEs HIGH sin plan de remediación

---

## 6. Configuración Mínima

### SonarQube Quality Gate

```json
{
  "name": "Talma Corporate Standard",
  "conditions": [
    {
      "metric": "new_coverage",
      "op": "LT",
      "error": "80",
      "description": "Coverage on new code < 80%"
    },
    {
      "metric": "new_duplicated_lines_density",
      "op": "GT",
      "error": "3",
      "description": "Duplicated lines > 3%"
    },
    {
      "metric": "new_maintainability_rating",
      "op": "GT",
      "error": "1",
      "description": "Maintainability rating worse than A"
    },
    {
      "metric": "new_reliability_rating",
      "op": "GT",
      "error": "1",
      "description": "Reliability rating worse than A"
    },
    {
      "metric": "new_security_rating",
      "op": "GT",
      "error": "1",
      "description": "Security rating worse than A"
    },
    {
      "metric": "new_security_hotspots_reviewed",
      "op": "LT",
      "error": "100",
      "description": "Security hotspots review < 100%"
    }
  ]
}
```

### GitHub Actions - Quality & Security Pipeline

```yaml
name: Quality & Security Gates

on:
  pull_request:
  push:
    branches: [main, develop]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: SonarQube Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          args: >
            -Dsonar.projectKey=talma-api
            -Dsonar.qualitygate.wait=true
            -Dsonar.qualitygate.timeout=300

      - name: Check Quality Gate
        run: |
          QG_STATUS=$(curl -s -u ${{ secrets.SONAR_TOKEN }}: \
            "https://sonarcloud.io/api/qualitygates/project_status?projectKey=talma-api" \
            | jq -r '.projectStatus.status')

          if [ "$QG_STATUS" != "OK" ]; then
            echo "❌ Quality Gate FAILED: $QG_STATUS"
            exit 1
          fi
          echo "✅ Quality Gate PASSED"

  security-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Trivy Container Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: "fs"
          severity: "CRITICAL,HIGH"
          exit-code: "1"
          format: "sarif"
          output: "trivy-results.sarif"

      - name: OWASP Dependency-Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: "Talma-API"
          path: "."
          format: "HTML,JSON"
          args: >
            --failOnCVSS 7
            --suppression suppression.xml

      - name: Secret Detection
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  iac-security-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          soft_fail: false

      - name: tfsec
        uses: aquasecurity/tfsec-action@v1.0.0
        with:
          working_directory: terraform/
          soft_fail: false

  coverage-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Tests with Coverage
        run: dotnet test --collect:"XPlat Code Coverage"

      - name: Upload to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.cobertura.xml
          fail_ci_if_error: true
          flags: unittests

      - name: Check Coverage Threshold
        run: |
          COVERAGE=$(cat coverage.cobertura.xml | grep line-rate | head -1 | sed 's/.*line-rate="\([^"]*\)".*/\1/')
          COVERAGE_PCT=$(echo "$COVERAGE * 100" | bc)

          if (( $(echo "$COVERAGE_PCT < 80" | bc -l) )); then
            echo "❌ Coverage $COVERAGE_PCT% < 80%"
            exit 1
          fi
          echo "✅ Coverage: $COVERAGE_PCT%"
```

---

## 7. Ejemplos

### Pre-commit Hook - Local Quality Gate

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running pre-commit quality checks..."

# Secret detection
echo "Checking for secrets..."
trufflehog filesystem . --only-verified
if [ $? -ne 0 ]; then
  echo "❌ Secrets detected! Commit blocked."
  exit 1
fi

# Linting
echo "Running linter..."
dotnet format --verify-no-changes
if [ $? -ne 0 ]; then
  echo "❌ Code format issues detected. Run 'dotnet format' to fix."
  exit 1
fi

# Unit tests
echo "Running unit tests..."
dotnet test --no-build
if [ $? -ne 0 ]; then
  echo "❌ Tests failing. Fix before committing."
  exit 1
fi

echo "✅ All pre-commit checks passed!"
```

---

## 8. Validación y Auditoría

### Checklist

- [ ] SonarQube Quality Gate configurado y funcionando
- [ ] Security scans en pipeline (Trivy, OWASP Dep-Check)
- [ ] Coverage mínimo 80% enforced
- [ ] Pre-commit hooks instalados
- [ ] Branch protection con required checks
- [ ] Métricas de quality gates monitoreadas

### Métricas

```promql
# Quality gate pass rate
count(pipeline_run{quality_gate="passed"}) / count(pipeline_run) * 100

# Average time blocked by quality gate
avg(pipeline_duration_blocked_seconds{reason="quality_gate"})

# Top quality gate failures
topk(10, count(quality_gate_failure) by (reason))
```

### Dashboard SLIs

| Métrica                  | SLI   | Alertar si |
| ------------------------ | ----- | ---------- |
| Quality gate pass rate   | > 90% | < 85%      |
| CRITICAL vulns in prod   | 0     | > 0        |
| Code coverage            | > 80% | < 75%      |
| Quality gate bypass rate | < 2%  | > 5%       |

---

## 9. Referencias

**Herramientas:**

- [SonarQube Quality Gates](https://docs.sonarsource.com/sonarqube/latest/user-guide/quality-gates/)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)

**Frameworks:**

- [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)
- [AWS DevOps Best Practices](https://aws.amazon.com/devops/)

**Buenas Prácticas:**

- Google SRE Book - "Release Engineering"
- "Continuous Delivery" - Jez Humble
