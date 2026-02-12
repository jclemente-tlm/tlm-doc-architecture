# Package Management - NuGet Packages

> **Estándar corporativo** para gestión de paquetes NuGet internos.
> **Registry estándar**: GitHub Packages
> **Integración**: GitHub Actions (CI/CD)

---

## 🎯 Objetivo

Centralizar y estandarizar la distribución de librerías compartidas entre microservicios mediante paquetes NuGet internos, garantizando versionamiento consistente, control de acceso y automatización CI/CD.

## 📋 Alcance

- Publicación de NuGets internos corporativos
- Consumo de paquetes desde microservicios .NET
- Control de acceso y seguridad
- Versionamiento semántico (SemVer)
- Automatización de publicación en pipelines CI/CD
- Gestión de dependencias compartidas

---

## 📦 Paquetes Corporativos Estándar

### Librerías Actuales

| Paquete                     | Descripción                               | Repositorio                |
| --------------------------- | ----------------------------------------- | -------------------------- |
| **Observability.Shared**    | Logging, métricas, tracing, health checks | `tlm-shared-observability` |
| **SecretsAndConfig.Shared** | Gestión de secretos y configuraciones     | `tlm-shared-secrets`       |

### Convenciones de Naming

```
Talma.<Dominio>.<Componente>

Ejemplos:
- Talma.Observability.Logging
- Talma.Security.Authentication
- Talma.Data.Repository
- Talma.Messaging.Kafka
```

---

## 🛠️ Registry Estándar: GitHub Packages

### Selección

**GitHub Packages** se establece como registry estándar por:

- **Costo**: Sin costo adicional (incluido en GitHub)
- **Integración**: Nativa con GitHub Actions y repositorios existentes
- **Seguridad**: PAT, OIDC, RBAC granular por repositorio
- **Agnosticidad**: Compatible con AWS/Azure/GCP, sin lock-in
- **Automatización**: Publicación automática desde pipelines CI/CD
- **Versionamiento**: SemVer con soporte pre-release

### Alternativas evaluadas

- **AWS CodeArtifact**: lock-in AWS, costos variables (US$0.05/GB storage + US$0.05/request)
- **Azure Artifacts**: lock-in Azure, costos US$2/usuario/mes (5 usuarios gratis)
- **MyGet**: SaaS costoso (US$11-45/mes), sin ventaja diferencial
- **ProGet**: self-hosted complejo, costos US$300/año base
- **Artifactory/Nexus**: enterprise-grade sobrede-dimensionado, costos licencia + infraestructura
- **Feed privado NuGet.org**: control acceso limitado, seguridad básica

---

## 📐 Implementación

### 1. Configuración de Repositorio

Cada librería compartida debe tener su propio repositorio en GitHub con estructura:

```
talma-shared-observability/
├── src/
│   └── Talma.Observability/
│       ├── Talma.Observability.csproj
│       ├── Logging/
│       ├── Metrics/
│       └── Tracing/
├── tests/
│   └── Talma.Observability.Tests/
├── .github/
│   └── workflows/
│       └── publish.yml
├── README.md
└── CHANGELOG.md
```

### 2. Configuración del Proyecto (.csproj)

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <PackageId>Talma.Observability</PackageId>
    <Version>1.2.3</Version>
    <Authors>Talma Corporation</Authors>
    <Company>Talma</Company>
    <Description>Shared observability libraries for microservices</Description>
    <RepositoryUrl>https://github.com/talma-corp/talma-shared-observability</RepositoryUrl>
    <PackageTags>observability;logging;metrics;tracing</PackageTags>
    <GeneratePackageOnBuild>true</GeneratePackageOnBuild>
  </PropertyGroup>

  <ItemGroup>
    <!-- Dependencias -->
    <PackageReference Include="Serilog" Version="3.1.1" />
    <PackageReference Include="Prometheus.Client" Version="8.0.0" />
  </ItemGroup>
</Project>
```

### 3. GitHub Actions Workflow (Publicación)

```yaml
name: Publish NuGet Package

on:
  push:
    tags:
      - "v*.*.*" # Trigger en tags semánticos (v1.2.3)

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --configuration Release --no-restore

      - name: Run tests
        run: dotnet test --configuration Release --no-build

      - name: Pack NuGet
        run: dotnet pack --configuration Release --no-build --output ./nupkg

      - name: Publish to GitHub Packages
        run: |
          dotnet nuget push ./nupkg/*.nupkg \
            --source "https://nuget.pkg.github.com/talma-corp/index.json" \
            --api-key ${{ secrets.GITHUB_TOKEN }} \
            --skip-duplicate
```

### 4. Configuración en Microservicios (Consumo)

Archivo `NuGet.config` en cada microservicio:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <!-- GitHub Packages privado -->
    <add key="github-talma" value="https://nuget.pkg.github.com/talma-corp/index.json" />
    <!-- NuGet.org público (fallback) -->
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
  </packageSources>

  <packageSourceCredentials>
    <github-talma>
      <add key="Username" value="%GITHUB_USERNAME%" />
      <add key="ClearTextPassword" value="%GITHUB_TOKEN%" />
    </github-talma>
  </packageSourceCredentials>
</configuration>
```

Variables de entorno (GitHub Actions):

```yaml
env:
  GITHUB_USERNAME: ${{ github.actor }}
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 5. Consumo en Proyecto (.csproj)

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <!-- Paquetes corporativos -->
    <PackageReference Include="Talma.Observability" Version="1.2.3" />
    <PackageReference Include="Talma.SecretsAndConfig" Version="2.0.1" />
  </ItemGroup>
</Project>
```

---

## ⚙️ Versionamiento Semántico (SemVer)

### Formato: `MAJOR.MINOR.PATCH`

```
1.2.3
│ │ │
│ │ └─ PATCH: Bug fixes, sin cambios API
│ └─── MINOR: Nueva funcionalidad, compatible backwards
└───── MAJOR: Breaking changes, incompatibilidad

Pre-release:
1.2.3-alpha.1
1.2.3-beta.2
1.2.3-rc.1
```

### Reglas de Versionamiento

| Cambio                     | Incremento | Ejemplo       |
| -------------------------- | ---------- | ------------- |
| Bug fix                    | PATCH      | 1.2.3 → 1.2.4 |
| Nueva feature (compatible) | MINOR      | 1.2.4 → 1.3.0 |
| Breaking change            | MAJOR      | 1.3.0 → 2.0.0 |
| Pre-release testing        | Suffix     | 2.0.0-beta.1  |

### Estrategia de Publicación

```bash
# Desarrollo activo (main branch)
1.2.3-dev.20260212.1

# Release candidate
1.3.0-rc.1

# Producción
1.3.0
```

---

## 🔐 Seguridad y Control de Acceso

### Autenticación con PAT (Personal Access Token)

Crear PAT en GitHub con scopes:

- ✅ `read:packages` (consumir paquetes)
- ✅ `write:packages` (publicar paquetes)
- ✅ `repo` (acceso repositorio)

```bash
# Configurar token localmente
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxx"

# O configurar en NuGet.config
dotnet nuget update source github-talma \
  --username YOUR_USERNAME \
  --password $GITHUB_TOKEN \
  --store-password-in-clear-text
```

### RBAC (Control de Acceso)

| Rol            | Permisos            | Usuarios                      |
| -------------- | ------------------- | ----------------------------- |
| **Maintainer** | Publicar + consumir | Tech leads, arquitectos       |
| **Developer**  | Consumir solamente  | Developers microservicios     |
| **CI/CD**      | Publicar + consumir | GitHub Actions (GITHUB_TOKEN) |

---

## 📊 Métricas y KPIs

### Indicadores de Seguimiento

- **Package adoption rate**: % de microservicios usando paquetes corporativos
- **Version consistency**: % de servicios en última versión estable
- **Dependency staleness**: Edad promedio de versiones usadas
- **Download count**: Total descargas por paquete
- **Breaking changes frequency**: Rate de cambios MAJOR

### Dashboard Grafana

```promql
# Dependencias desactualizadas
sum(nuget_package_outdated{status="outdated"}) by (package)

# Versiones más usadas
count(nuget_package_version) by (package, version)

# Tasa de adopción
(count(services_using_corporate_packages) / count(total_services)) * 100
```

---

## 🔧 Troubleshooting

### Problema: Error 401 Unauthorized

```bash
# Solución: Verificar token y permisos
echo $GITHUB_TOKEN | dotnet nuget push --source github-talma

# Regenerar token con scopes correctos
# GitHub → Settings → Developer settings → Personal access tokens
```

### Problema: Paquete no encontrado

```bash
# Limpiar cache local
dotnet nuget locals all --clear

# Verificar sources
dotnet nuget list source

# Reinstalar paquete
dotnet remove package Talma.Observability
dotnet add package Talma.Observability --version 1.2.3
```

### Problema: Versión conflictiva

```bash
# Listar dependencias transitivas
dotnet list package --include-transitive

# Forzar versión específica
<PackageReference Include="Talma.Observability" Version="1.2.3" />
```

---

## 📋 Checklist Publicación de Paquete

**Pre-publicación**:

- [ ] Tests unitarios pasando (coverage >= 80%)
- [ ] CHANGELOG.md actualizado
- [ ] Versionamiento semántico correcto
- [ ] README.md con ejemplos de uso
- [ ] Dependencias actualizadas y seguras

**Publicación**:

- [ ] Tag creado en formato `v1.2.3`
- [ ] GitHub Actions pipeline exitoso
- [ ] Paquete visible en GitHub Packages
- [ ] Descarga manual verificada

**Post-publicación**:

- [ ] Microservicios notificados de nueva versión
- [ ] Documentación corporativa actualizada
- [ ] Anuncio en canal Slack #architecture

---

## 🎯 Mejores Prácticas

### Librería Compartida

```csharp
// ✅ Buena práctica: API estable, clara, documentada
namespace Talma.Observability;

/// <summary>
/// Configura observabilidad estándar para microservicios.
/// </summary>
public static class ObservabilityExtensions
{
    /// <summary>
    /// Agrega logging, métricas y tracing configurados.
    /// </summary>
    public static IServiceCollection AddTalmaObservability(
        this IServiceCollection services,
        ObservabilityOptions options)
    {
        // Implementación
    }
}
```

### Consumo en Microservicio

```csharp
// ✅ Consumo simple y declarativo
builder.Services.AddTalmaObservability(new ObservabilityOptions
{
    ServiceName = "servicio-identidad",
    Environment = "production"
});
```

### Evitar Breaking Changes

```csharp
// ❌ Breaking change (eliminar método público)
// public void OldMethod() { }

// ✅ Deprecación gradual
[Obsolete("Use NewMethod instead. Will be removed in v3.0.0")]
public void OldMethod() => NewMethod();

public void NewMethod() { }
```

---

## 🔗 Integración con Otros Estándares

- **CI/CD**: [GitHub Actions - ADR-009](../../decisiones-de-arquitectura/adr-009-github-actions-cicd.md)
- **Code Quality**: [SonarQube SAST](../desarrollo/code-quality-sast.md)
- **Container Registry**: [GitHub Container Registry - ADR-022](../../decisiones-de-arquitectura/adr-022-github-container-registry.md)
- **Testing**: [Estándar de Unit Testing](../testing/unit-testing.md)

---

## 📚 Referencias

- [GitHub Packages - NuGet Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-nuget-registry)
- [NuGet.config Reference](https://learn.microsoft.com/en-us/nuget/consume-packages/configuring-nuget-behavior)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [.NET Package Authoring](https://learn.microsoft.com/en-us/nuget/create-packages/creating-a-package-dotnet-cli)
- [Best Practices for NuGet Packages](https://learn.microsoft.com/en-us/nuget/create-packages/package-authoring-best-practices)

---

**Tipo**: Estándar de desarrollo
**Categoría**: Package Management / CI/CD
**Última actualización**: Febrero 2026
**Revisión**: Semestral
