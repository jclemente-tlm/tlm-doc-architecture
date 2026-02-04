---
id: software-bill-of-materials
sidebar_position: 21
title: Software Bill of Materials (SBOM)
description: Estándar para generar SBOM con CycloneDX, tracking de dependencias, vulnerability scanning y compliance con Executive Order 14028
---

# Estándar Técnico — Software Bill of Materials

---

## 1. Propósito

Generar Software Bill of Materials (SBOM) en formato CycloneDX para inventario de componentes, tracking de vulnerabilidades, compliance regulatorio y supply chain security, automatizado en CI/CD.

---

## 2. Alcance

**Aplica a:**

- Aplicaciones .NET
- Container images
- Dependencias NuGet
- Librerías JavaScript (frontend)
- Base images de Docker

**No aplica a:**

- Código propietario (no third-party)

---

## 3. Tecnologías Aprobadas

| Componente                | Tecnología       | Versión mínima | Observaciones       |
| ------------------------- | ---------------- | -------------- | ------------------- |
| **SBOM Format**           | CycloneDX        | 1.5+           | JSON/XML            |
| **Generator (.NET)**      | CycloneDX CLI    | 0.9+           | NuGet packages      |
| **Generator (Container)** | Syft             | 0.98+          | Anchore tool        |
| **Storage**               | GitHub Artifacts | -              | SBOM repository     |
| **Scanning**              | Trivy            | 0.48+          | Vulnerability check |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Generación de SBOM

- [ ] **Formato**: CycloneDX 1.5+ (JSON)
- [ ] **Automated**: Generar en cada build CI/CD
- [ ] **Versioned**: SBOM por cada release version
- [ ] **Stored**: Artifact repository (GitHub)

### Contenido SBOM

- [ ] **Components**: Todas las dependencias transitivas
- [ ] **Versions**: Versión exacta (no ranges)
- [ ] **Licenses**: Licencia de cada componente
- [ ] **Hashes**: SHA-256 de cada componente

### Scanning

- [ ] **Vulnerability check**: Trivy contra SBOM
- [ ] **License compliance**: No GPL en producción
- [ ] **Outdated components**: Detectar versiones antiguas

### Compliance

- [ ] **Executive Order 14028**: SBOM para software federal (si aplica)
- [ ] **NTIA Minimum Elements**: Cumplir requisitos mínimos

---

## 5. CycloneDX - Formato SBOM

### Estructura Básica

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79",
  "version": 1,
  "metadata": {
    "timestamp": "2024-01-15T12:00:00Z",
    "component": {
      "type": "application",
      "name": "payment-api",
      "version": "1.2.3",
      "purl": "pkg:github/talma/payment-api@1.2.3"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "Newtonsoft.Json",
      "version": "13.0.3",
      "purl": "pkg:nuget/Newtonsoft.Json@13.0.3",
      "licenses": [
        {
          "license": {
            "id": "MIT"
          }
        }
      ],
      "hashes": [
        {
          "alg": "SHA-256",
          "content": "abc123..."
        }
      ]
    },
    {
      "type": "library",
      "name": "Serilog",
      "version": "3.1.1",
      "purl": "pkg:nuget/Serilog@3.1.1",
      "licenses": [
        {
          "license": {
            "id": "Apache-2.0"
          }
        }
      ]
    }
  ]
}
```

---

## 6. Generación SBOM - .NET

### CycloneDX CLI

```bash
# Instalar CycloneDX CLI
dotnet tool install --global CycloneDX

# Generar SBOM desde proyecto .NET
cd PaymentApi/
dotnet cyclonedx PaymentApi.csproj -o sbom/ -f json

# Resultado: sbom/bom.json
```

### GitHub Actions Workflow

```yaml
# .github/workflows/sbom.yml
name: Generate SBOM

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Install CycloneDX
        run: dotnet tool install --global CycloneDX

      - name: Generate SBOM
        run: |
          dotnet cyclonedx PaymentApi/PaymentApi.csproj \
            -o sbom/ \
            -f json \
            --json-serialization-options Indented

      - name: Upload SBOM artifact
        uses: actions/upload-artifact@v4
        with:
          name: sbom-${{ github.sha }}
          path: sbom/bom.json
          retention-days: 90

      - name: Scan SBOM for vulnerabilities
        run: |
          docker run --rm -v $(pwd)/sbom:/sbom \
            aquasec/trivy sbom /sbom/bom.json \
            --severity HIGH,CRITICAL \
            --exit-code 1
```

---

## 7. Generación SBOM - Container Images

### Syft (Anchore)

```bash
# Instalar Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Generar SBOM desde imagen Docker
syft packages payment-api:1.2.3 -o cyclonedx-json > sbom-container.json

# Generar desde Dockerfile
docker build -t payment-api:1.2.3 .
syft packages docker:payment-api:1.2.3 -o cyclonedx-json > sbom.json
```

### GitHub Actions

```yaml
# .github/workflows/container-sbom.yml
- name: Build Docker image
  run: docker build -t payment-api:${{ github.sha }} .

- name: Generate container SBOM
  uses: anchore/sbom-action@v0
  with:
    image: payment-api:${{ github.sha }}
    format: cyclonedx-json
    output-file: sbom-container.json

- name: Upload container SBOM
  uses: actions/upload-artifact@v4
  with:
    name: sbom-container-${{ github.sha }}
    path: sbom-container.json
```

---

## 8. Vulnerability Scanning con SBOM

### Trivy SBOM Scan

```bash
# Escanear SBOM generado
trivy sbom sbom/bom.json \
  --severity HIGH,CRITICAL \
  --format table

# Output:
# ┌─────────────────┬──────────────┬──────────┬────────────────┐
# │    Library      │ Vulnerability│ Severity │  Fixed Version │
# ├─────────────────┼──────────────┼──────────┼────────────────┤
# │ System.Text.Json│ CVE-2024-1234│  HIGH    │ 8.0.1          │
# │ Newtonsoft.Json │ CVE-2024-5678│ CRITICAL │ 13.0.4         │
# └─────────────────┴──────────────┴──────────┴────────────────┘

# Guardar resultado en SARIF (para GitHub Security tab)
trivy sbom sbom/bom.json \
  --format sarif \
  --output trivy-results.sarif
```

### GitHub Actions - Upload SARIF

```yaml
- name: Scan SBOM
  run: |
    trivy sbom sbom/bom.json \
      --format sarif \
      --output trivy-results.sarif

- name: Upload SARIF to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

---

## 9. License Compliance

### Detectar Licencias No Permitidas

```bash
# Extraer licencias del SBOM
jq '.components[] | {name: .name, license: .licenses[0].license.id}' sbom/bom.json

# Resultado:
# {"name": "Newtonsoft.Json", "license": "MIT"}
# {"name": "Serilog", "license": "Apache-2.0"}
# {"name": "SomeLib", "license": "GPL-3.0"} ⚠️ NO PERMITIDA
```

### Script de Validación

```bash
#!/bin/bash
# scripts/check-licenses.sh

FORBIDDEN_LICENSES=("GPL-2.0" "GPL-3.0" "AGPL-3.0")
SBOM_FILE="sbom/bom.json"

# Extraer licencias
LICENSES=$(jq -r '.components[] | .licenses[]?.license.id' $SBOM_FILE | sort -u)

for LICENSE in $LICENSES; do
  if [[ " ${FORBIDDEN_LICENSES[@]} " =~ " ${LICENSE} " ]]; then
    echo "❌ ERROR: Forbidden license detected: $LICENSE"
    exit 1
  fi
done

echo "✅ All licenses are compliant"
```

---

## 10. SBOM Storage & Versioning

### GitHub Releases

```yaml
# .github/workflows/release.yml
- name: Create Release
  uses: actions/create-release@v1
  with:
    tag_name: ${{ github.ref }}
    release_name: Release ${{ github.ref }}

- name: Upload SBOM to Release
  uses: actions/upload-release-asset@v1
  with:
    upload_url: ${{ steps.create_release.outputs.upload_url }}
    asset_path: sbom/bom.json
    asset_name: sbom-payment-api-${{ github.ref }}.json
    asset_content_type: application/json
```

### Artifact Repository

```bash
# Subir SBOM a S3
aws s3 cp sbom/bom.json \
  s3://talma-sbom-repository/payment-api/1.2.3/sbom.json \
  --metadata version=1.2.3,timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Descargar SBOM histórico
aws s3 ls s3://talma-sbom-repository/payment-api/ --recursive
```

---

## 11. NTIA Minimum Elements

### Checklist SBOM Compliance

```yaml
ntia_minimum_elements:
  - ✅ Supplier Name: "Talma"
  - ✅ Component Name: "payment-api"
  - ✅ Version: "1.2.3"
  - ✅ Unique Identifier: "pkg:github/talma/payment-api@1.2.3"
  - ✅ Dependency Relationships: Components tree
  - ✅ Author of SBOM: "GitHub Actions"
  - ✅ Timestamp: "2024-01-15T12:00:00Z"
```

---

## 12. Validación de Cumplimiento

```bash
# Verificar SBOM es válido CycloneDX
curl -X POST https://sbom.cyclonedx.org/validate \
  -F "file=@sbom/bom.json"

# Contar componentes en SBOM
jq '.components | length' sbom/bom.json
# Esperado: > 50 (dependencias directas + transitivas)

# Verificar todas las dependencias tienen versión exacta
jq '.components[] | select(.version == null or .version == "")' sbom/bom.json
# Esperado: Sin resultados (todos tienen versión)

# Verificar todas las dependencias tienen licencia
jq '.components[] | select(.licenses == null or .licenses == [])' sbom/bom.json
# Esperado: Sin resultados (todos tienen licencia)
```

---

## 13. Referencias

**NTIA:**

- [NTIA SBOM Minimum Elements](https://www.ntia.gov/sites/default/files/publications/sbom_minimum_elements_report_0.pdf)

**CycloneDX:**

- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [CycloneDX .NET Tool](https://github.com/CycloneDX/cyclonedx-dotnet)

**CISA:**

- [Executive Order 14028](https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/)
