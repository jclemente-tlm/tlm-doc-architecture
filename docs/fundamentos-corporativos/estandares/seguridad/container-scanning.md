# Container Security Scanning

> **Estándar corporativo** para escaneo de vulnerabilidades en imágenes de contenedores.
> **Herramienta estándar**: Trivy
> **Integración**: GitHub Actions (CI/CD)

---

## 🎯 Objetivo

Detectar vulnerabilidades de seguridad en imágenes Docker antes de despliegue en producción, implementando **shift-left security** en el ciclo de desarrollo.

## 📋 Alcance

- Escaneo de imágenes Docker de microservicios .NET
- Detección de vulnerabilidades en OS packages (Alpine, Debian, Ubuntu)
- Análisis de dependencias .NET (NuGet packages)
- Escaneo de librerías y binarios
- Integración obligatoria en pipelines CI/CD

---

## 🛠️ Herramienta Estándar: Trivy

### Selección

**Trivy** (Aqua Security) se establece como herramienta estándar corporativa por:

- **Costo**: OSS gratuito, sin licencias
- **Performance**: < 30s por imagen, no impacta pipelines
- **Cobertura**: OS packages + dependencias + librerías
- **Integración**: GitHub Actions nativo (marketplace oficial)
- **Reportes**: SARIF integrado con GitHub Security tab
- **Madurez**: 22K+ stars, comunidad activa, actualizaciones frecuentes

### Alternativas evaluadas

- **Grype** (Anchore): buena alternativa OSS, menor ecosistema
- **Snyk Container**: SaaS completo pero costoso (US$98/dev/mes)
- **AWS ECR Scanning**: lock-in AWS, solo funciona con ECR
- **Docker Scout**: inmaduro (2023), funcionalidad básica

---

## 📐 Implementación

### 1. Configuración GitHub Actions

```yaml
name: Security Scan

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t ${{ github.repository }}:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ github.repository }}:${{ github.sha }}
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH"
          exit-code: "1" # Fail on CRITICAL/HIGH

      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: "trivy-results.sarif"
```

### 2. Niveles de Severidad

| Severidad    | Acción              | Descripción                                       |
| ------------ | ------------------- | ------------------------------------------------- |
| **CRITICAL** | ❌ Block deployment | Vulnerabilidades críticas, parchar inmediatamente |
| **HIGH**     | ❌ Block deployment | Vulnerabilidades graves, parchar en 7 días        |
| **MEDIUM**   | ⚠️ Warning          | Vulnerabilidades moderadas, revisar y planificar  |
| **LOW**      | ✅ Allow            | Vulnerabilidades menores, backlog técnico         |

### 3. Configuración Trivy

Archivo `.trivyignore` para falsos positivos documentados:

```
# CVE-2023-XXXX - False positive: no aplica a nuestra configuración
# Razón: Alpine usa musl-libc que no es afectada
CVE-2023-XXXX

# CVE-2024-YYYY - Accepted risk
# Razón: Parche no disponible, mitigación implementada en WAF
# Aprobado por: Security Team
# Fecha: 2026-01-15
CVE-2024-YYYY
```

### 4. Reporte de Resultados

Trivy genera reportes en múltiples formatos:

```bash
# SARIF (GitHub Security tab)
trivy image --format sarif --output results.sarif myimage:tag

# JSON (procesamiento automático)
trivy image --format json --output results.json myimage:tag

# HTML (reportes ejecutivos)
trivy image --format template --template "@contrib/html.tpl" --output report.html myimage:tag

# Tabla (consola)
trivy image myimage:tag
```

---

## ⚙️ Configuraciones Recomendadas

### Escaneo Completo

```yaml
- name: Full security scan
  run: |
    trivy image \
      --severity CRITICAL,HIGH,MEDIUM \
      --vuln-type os,library \
      --format sarif \
      --output trivy-results.sarif \
      myimage:tag
```

### Escaneo Solo Dependencias

```yaml
- name: Scan dependencies only
  run: |
    trivy image \
      --vuln-type library \
      --scanners vuln \
      myimage:tag
```

### Escaneo con Cache

```yaml
- name: Scan with cache
  run: |
    trivy image \
      --cache-dir /tmp/trivy-cache \
      --download-db-only  # Primera ejecución

    trivy image \
      --cache-dir /tmp/trivy-cache \
      --skip-db-update \
      myimage:tag
```

---

## 📊 Métricas y KPIs

### Indicadores de Seguimiento

- **Vulnerabilities detected**: Total de vulnerabilidades encontradas
- **Critical/High blocking rate**: % de builds bloqueados por severidad crítica/alta
- **Mean Time to Remediate (MTTR)**: Tiempo promedio de corrección
- **False positive rate**: % de falsos positivos reportados
- **Scan coverage**: % de imágenes escaneadas vs desplegadas

### Dashboard Grafana

```promql
# Total vulnerabilidades críticas
sum(trivy_vulnerabilities{severity="CRITICAL"})

# Tasa de bloqueos en CI/CD
rate(trivy_scan_failures_total[1h])

# Tiempo de escaneo (p95)
histogram_quantile(0.95, rate(trivy_scan_duration_seconds_bucket[5m]))
```

---

## 🔧 Troubleshooting

### Problema: Escaneos lentos

```bash
# Solución: Usar cache local
trivy image --cache-dir /tmp/trivy-cache myimage:tag

# Solución: Actualizar DB separadamente
trivy image --download-db-only
```

### Problema: Falsos positivos recurrentes

```bash
# Crear .trivyignore con justificación
echo "CVE-XXXX # Razón documentada" >> .trivyignore
```

### Problema: Base de datos desactualizada

```bash
# Forzar actualización
trivy image --skip-db-update=false myimage:tag
```

---

## 📚 Referencias

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub Action](https://github.com/aquasecurity/trivy-action)
- [OWASP Container Security](https://owasp.org/www-project-docker-top-10/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [GitHub Actions - ADR-009](../../decisiones-de-arquitectura/adr-009-github-actions-cicd.md)

---

**Tipo**: Estándar de seguridad
**Categoría**: DevSecOps
**Última actualización**: Febrero 2026
**Revisión**: Anual
