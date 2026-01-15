---
title: "SecretsAndConfigs.Shared"
sidebar_position: 1
---

## Objetivo

Paquete NuGet que centraliza el acceso a **secretos y configuraciones** de microservicios .NET 8, con abstracción de proveedor, permitiendo cambios de backend sin desarrollos ni despliegues adicionales.

## Stack inicial

- Secretos: **AWS Secrets Manager**
- Configuración: **AWS Parameter Store**

## Arquitectura

```
SecretsAndConfig.Shared/
│
├── Abstractions/
│   ├── ISecretProvider.cs
│   └── IConfigProvider.cs
├── Helpers/
│   └── Caching, Validations, Logging
├── Extensions/
│   └── ServiceCollectionExtensions.cs // AddSecretsAndConfigBase()
└── Providers/
    └── AWS/
        ├── SecretManagerProvider.cs
        └── ParameterStoreProvider.cs
```

## Integración en microservicios .NET 8

```csharp
var builder = WebApplication.CreateBuilder(args);

// Registrar abstracción
builder.Services.AddSecretsAndConfigBase();

// Registrar proveedor AWS concreto
builder.Services.AddSecretsAndConfigAWS(builder.Configuration);

var app = builder.Build();

// Uso
var dbPassword = app.Services.GetRequiredService<ISecretProvider>().GetSecret("DbPassword");
var featureFlag = app.Services.GetRequiredService<IConfigProvider>().GetParameter("FeatureXEnabled");

app.Run();
```

## Configuración de proveedor AWS

- La selección del proveedor de secretos/configuración se hace mediante `appsettings.json` o variables de entorno.
- Ejemplo de configuración inicial en AWS:

```json
{
  "SecretsProvider": "AWS",
  "SecretsConfig": {
    "Region": "us-east-1"
  }
}
```

- El NuGet selecciona automáticamente el proveedor correcto sin necesidad de redeploy.

## Autorefresh / Caching

- Se implementa caching interno con expiración o polling, asegurando que los microservicios siempre lean valores recientes.
- Ejemplo simplificado:

```csharp
public class CachingSecretProvider : ISecretProvider
{
    private readonly ISecretProvider _inner;
    private readonly MemoryCache _cache = new MemoryCache(new MemoryCacheOptions());
    private readonly TimeSpan _refreshInterval = TimeSpan.FromMinutes(5);

    public CachingSecretProvider(ISecretProvider inner) { _inner = inner; }

    public string GetSecret(string key)
    {
        return _cache.GetOrCreate(key, entry => {
            entry.AbsoluteExpirationRelativeToNow = _refreshInterval;
            return _inner.GetSecret(key);
        });
    }
}
```

## Buenas prácticas

- Nunca guardar secretos en código fuente.
- Usar caching interno para secretos y parámetros críticos.
- Centralizar documentación de keys y parámetros obligatorios para cada microservicio.
- Mantener consistencia de abstracción en todos los microservicios.
