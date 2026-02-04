---
id: container-image-scanning
sidebar_position: 4
title: Container Image Scanning
description: Estándar para escaneo de vulnerabilidades en imágenes Docker con Trivy, bloqueando despliegues con CRITICAL/HIGH en CI/CD
---

# Estándar Técnico — Container Image Scanning

---

## 1. Propósito

Escanear imágenes Docker con Trivy para detectar vulnerabilidades (CVE), secretos expuestos y misconfigurations, bloqueando despliegues con severidad CRITICAL/HIGH en pipeline CI/CD.

---

## 2. Alcance

**Aplica a:**

- Todas las imágenes Docker
- Imágenes base (FROM)
- Dependencias de aplicación (.NET packages)
- Archivos de configuración en imagen

**No aplica a:**

- Imágenes de desarrollo local (opcional)
- Imágenes públicas de terceros (scan informativo)

---

## 3. Tecnologías Aprobadas

| Componente      | Tecnología                | Versión mínima | Observaciones              |
| --------------- | ------------------------- | -------------- | -------------------------- |
| **Scanner**     | Trivy                     | 0.50+          | Aqua Security, open-source |
| **Registry**    | GitHub Container Registry | -              | ghcr.io                    |
| **CI/CD**       | GitHub Actions            | -              | Automatizado               |
| **Reporting**   | Trivy JSON + SARIF        | -              | GitHub Security tab        |
| **Base Images** | .NET Runtime              | 8.0-alpine     | Minimal attack surface     |

⚠️ **NO UTILIZADO:**

- Clair (deprecado en favor de Trivy)
- Aqua Security (commercial)

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Escaneo Automático

- [ ] **CI/CD**: Escanear en cada build antes de push
- [ ] **Block on CRITICAL**: Fallar pipeline si hay vulnerabilidades CRITICAL
- [ ] **Warn on HIGH**: Alertar pero no bloquear (temporal, revisar)
- [ ] **Scan bases**: Incluir imágenes base (FROM)
- [ ] **Scan deps**: Escanear paquetes NuGet

### Reporting

- [ ] **SARIF upload**: Subir a GitHub Security tab
- [ ] **JSON report**: Guardar como artifact
- [ ] **Dashboard**: Metrics en Grafana (opcional)

### Remediation

- [ ] **Actualizar bases**: Usar latest patch version
- [ ] **Actualizar deps**: Upgrade vulnerable packages
- [ ] **Excepciones**: Documentar en `.trivyignore` (temporal)

---

## 5. GitHub Actions Workflow

### `.github/workflows/build.yml`

```yaml
name: Build and Scan Docker Image

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write # Para SARIF upload

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          load: true
          tags: ${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # Escaneo de vulnerabilidades con Trivy
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ github.repository }}:${{ github.sha }}
          format: "sarif"
          output: "trivy-results.sarif"
          severity: "CRITICAL,HIGH,MEDIUM"
          exit-code: "1" # Fallar si encuentra CRITICAL o HIGH
          ignore-unfixed: true # Ignorar si no hay fix disponible

      # Upload a GitHub Security tab
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always() # Subir incluso si falla
        with:
          sarif_file: "trivy-results.sarif"

      # Generar reporte JSON para artifacts
      - name: Run Trivy (JSON format)
        uses: aquasecurity/trivy-action@master
        if: always()
        with:
          image-ref: ${{ github.repository }}:${{ github.sha }}
          format: "json"
          output: "trivy-results.json"
          severity: "CRITICAL,HIGH,MEDIUM,LOW"

      - name: Upload Trivy report artifact
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: trivy-report
          path: trivy-results.json

      # Si pasa escaneo, push a registry
      - name: Log in to GitHub Container Registry
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Push Docker image
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
```

---

## 6. Dockerfile - Best Practices

### Imagen Base Segura

```dockerfile
# Usar Alpine (menor superficie de ataque)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS base
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

# Non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src

# Copiar solo .csproj primero (layer caching)
COPY ["PaymentService/PaymentService.csproj", "PaymentService/"]
RUN dotnet restore "PaymentService/PaymentService.csproj"

# Copiar resto del código
COPY . .
WORKDIR "/src/PaymentService"
RUN dotnet build "PaymentService.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "PaymentService.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "PaymentService.dll"]
```

---

## 7. Local Scanning

### Instalación Trivy

```bash
# macOS
brew install aquasecurity/trivy/trivy

# Linux (Debian/Ubuntu)
sudo apt-get install wget
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Verificar instalación
trivy --version
```

### Escanear Imagen Local

```bash
# Escaneo básico
trivy image payment-service:latest

# Solo CRITICAL y HIGH
trivy image --severity CRITICAL,HIGH payment-service:latest

# Ignorar vulnerabilidades sin fix
trivy image --ignore-unfixed payment-service:latest

# Formato JSON
trivy image --format json --output results.json payment-service:latest

# Formato tabla (legible)
trivy image --format table payment-service:latest

# Escanear y fallar si encuentra CRITICAL
trivy image --exit-code 1 --severity CRITICAL payment-service:latest
```

### Escanear Dockerfile

```bash
# Escanear misconfigurations en Dockerfile
trivy config Dockerfile

# Ejemplos de issues detectados:
# - Running as root
# - Using :latest tag
# - No HEALTHCHECK
# - Secrets hardcoded
```

---

## 8. .trivyignore - Excepciones Temporales

```ini
# .trivyignore
# Ignorar temporalmente (documentar justificación)

# CVE-2024-1234: PostgreSQL client lib, no fix available yet
# Justificación: Vulnerability en modo cliente, no aplicable a nuestro caso
# Review date: 2024-12-31
CVE-2024-1234

# CVE-2024-5678: Alpine apk tools, waiting for Alpine release
# Justificación: No exploitable en contenedor, solo en build-time
# Review date: 2024-11-15
CVE-2024-5678
```

⚠️ **IMPORTANTE:**

- Revisar `.trivyignore` mensualmente
- Documentar razón y fecha de revisión
- NO ignorar CRITICAL sin aprobación CISO

---

## 9. Remediation Strategies

### 1. Actualizar Imagen Base

```dockerfile
# ANTES (vulnerable)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine

# DESPUÉS (actualizada)
FROM mcr.microsoft.com/dotnet/aspnet:8.0.2-alpine3.19
```

### 2. Upgrade Paquetes Vulnerables

```bash
# Detectar paquetes vulnerables
trivy image payment-service:latest --format json | jq '.Results[].Vulnerabilities[] | select(.Severity=="CRITICAL") | {Package: .PkgName, Version: .InstalledVersion, FixedVersion: .FixedVersion}'

# Output:
# {
#   "Package": "System.Text.Json",
#   "Version": "8.0.0",
#   "FixedVersion": "8.0.1"
# }

# Actualizar en .csproj
dotnet add package System.Text.Json --version 8.0.1
```

### 3. Multi-Stage Builds (Reducir Superficie)

```dockerfile
# Solo runtime en imagen final (NO SDK)
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
# ... build ...

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS final  # Más pequeña
COPY --from=build /app/publish .
```

---

## 10. GitHub Security Tab

Después de subir SARIF, ver resultados en:

```
https://github.com/{org}/{repo}/security/code-scanning
```

**Beneficios:**

- Alertas automáticas en PRs
- Tracking de vulnerabilidades
- Integración con Dependabot
- Métricas de seguridad

---

## 11. Validación de Cumplimiento

```bash
# Verificar workflow existe
test -f .github/workflows/build.yml && echo "OK" || echo "MISSING"

# Verificar Trivy instalado localmente
trivy --version

# Escanear todas las imágenes locales
docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>" | xargs -I {} trivy image --severity CRITICAL,HIGH --exit-code 1 {}

# Verificar .trivyignore no tiene CRITICAL sin justificar
if [ -f .trivyignore ]; then
  grep -i "critical" .trivyignore && echo "WARN: Critical CVEs ignored, review justification"
fi
```

---

## 12. Monitoring - Grafana Dashboard

### Métricas de Trivy (JSON logs)

```json
// Parsear resultados Trivy en Loki
{
  "Results": [
    {
      "Vulnerabilities": [
        {
          "Severity": "CRITICAL",
          "PkgName": "openssl",
          "InstalledVersion": "3.0.0",
          "FixedVersion": "3.0.1"
        }
      ]
    }
  ]
}
```

### Panel: Vulnerabilities por Severidad

```promql
sum by (severity) (
  count_over_time({job="trivy"} | json | severity != "" [24h])
)
```

---

## 13. Referencias

**Trivy:**

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub Action](https://github.com/aquasecurity/trivy-action)

**Docker Security:**

- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

**CVE:**

- [National Vulnerability Database](https://nvd.nist.gov/)
