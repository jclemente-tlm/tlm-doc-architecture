---
id: variables-entorno
sidebar_position: 3
title: Variables de Entorno
description: Convención para naming y manejo de variables de entorno
---

## 1. Principio

Las variables de entorno deben tener nombres consistentes, estar bien documentadas y seguir jerarquías claras para configuración de aplicaciones.

## 2. Reglas

### Regla 1: Prefijo Corporativo

- **Formato**: `TLM_{CATEGORIA}_{NOMBRE}`
- **Ejemplo correcto**: `TLM_DB_HOST`, `TLM_API_KEY`, `TLM_LOG_LEVEL`
- **Ejemplo incorrecto**: `DB_HOST`, `API_KEY`, `log_level`

### Regla 2: UPPER_SNAKE_CASE

- **Formato**: Mayúsculas con guiones bajos
- **Ejemplo correcto**: `TLM_DATABASE_CONNECTION_STRING`
- **Ejemplo incorrecto**: `TLM_databaseConnectionString`, `tlm-database-connection`

### Regla 3: Jerarquía por Categorías

| Categoría      | Prefijo        | Ejemplos                                       |
| -------------- | -------------- | ---------------------------------------------- |
| Base de Datos  | `TLM_DB_`      | `TLM_DB_HOST`, `TLM_DB_PORT`, `TLM_DB_NAME`    |
| API Externa    | `TLM_API_`     | `TLM_API_BASE_URL`, `TLM_API_TIMEOUT`          |
| Caché          | `TLM_CACHE_`   | `TLM_CACHE_REDIS_URL`, `TLM_CACHE_TTL`         |
| Logging        | `TLM_LOG_`     | `TLM_LOG_LEVEL`, `TLM_LOG_FORMAT`              |
| Mensajería     | `TLM_MSG_`     | `TLM_MSG_KAFKA_BROKERS`, `TLM_MSG_SQS_QUEUE`   |
| Seguridad      | `TLM_SEC_`     | `TLM_SEC_JWT_SECRET`, `TLM_SEC_ENCRYPTION_KEY` |
| Features Flags | `TLM_FEATURE_` | `TLM_FEATURE_NEW_CHECKOUT_ENABLED`             |
| Observabilidad | `TLM_OBS_`     | `TLM_OBS_APM_URL`, `TLM_OBS_TRACE_ENABLED`     |

## 3. Variables Estándar por Ambiente

```bash
# Ambiente
TLM_ENVIRONMENT=prod  # dev, qa, stg, prod

# Aplicación
TLM_APP_NAME=users-api
TLM_APP_VERSION=1.2.3
TLM_APP_PORT=8080

# Base de Datos
TLM_DB_HOST=postgres.talma.internal
TLM_DB_PORT=5432
TLM_DB_NAME=users_db
TLM_DB_USER=app_user
TLM_DB_PASSWORD=<SECRET>  # Desde vault/secrets manager
TLM_DB_SSL_MODE=require
TLM_DB_POOL_SIZE=20

# Redis Cache
TLM_CACHE_REDIS_URL=redis://cache.talma.internal:6379
TLM_CACHE_TTL_SECONDS=3600
TLM_CACHE_ENABLED=true

# Logging
TLM_LOG_LEVEL=info  # debug, info, warn, error
TLM_LOG_FORMAT=json
TLM_LOG_OUTPUT=stdout

# Observabilidad
TLM_OBS_APM_URL=https://apm.talma.com
TLM_OBS_TRACE_ENABLED=true
TLM_OBS_METRICS_ENABLED=true

# Multi-tenancy
TLM_TENANT_ID=tlm-pe
TLM_TENANT_COUNTRY=PE
```

## 4. Archivo `.env.example`

Siempre incluir en el repositorio:

```bash
# .env.example
# Copiar a .env y completar valores sensibles

# ==================================
# APPLICATION
# ==================================
TLM_ENVIRONMENT=dev
TLM_APP_NAME=users-api
TLM_APP_PORT=8080

# ==================================
# DATABASE
# ==================================
TLM_DB_HOST=localhost
TLM_DB_PORT=5432
TLM_DB_NAME=users_db
TLM_DB_USER=postgres
TLM_DB_PASSWORD=<YOUR_PASSWORD>  # ⚠️ NUNCA commitear con valor real

# ==================================
# REDIS CACHE
# ==================================
TLM_CACHE_REDIS_URL=redis://localhost:6379
TLM_CACHE_TTL_SECONDS=3600

# ==================================
# LOGGING
# ==================================
TLM_LOG_LEVEL=debug
TLM_LOG_FORMAT=json
```

## 5. Validación de Variables Requeridas

### .NET

```csharp
public class EnvironmentValidator
{
    private static readonly string[] RequiredVars = new[]
    {
        "TLM_ENVIRONMENT",
        "TLM_DB_HOST",
        "TLM_DB_NAME",
        "TLM_DB_USER",
        "TLM_DB_PASSWORD"
    };

    public static void ValidateRequiredVariables()
    {
        var missing = RequiredVars
            .Where(varName => string.IsNullOrEmpty(Environment.GetEnvironmentVariable(varName)))
            .ToList();

        if (missing.Any())
        {
            throw new InvalidOperationException(
                $"Faltan variables de entorno requeridas: {string.Join(", ", missing)}"
            );
        }
    }
}

// En Program.cs
EnvironmentValidator.ValidateRequiredVariables();
```

### TypeScript/Node.js

```typescript
import { config } from "dotenv";
import { z } from "zod";

// Cargar .env
config();

// Schema de validación
const envSchema = z.object({
  TLM_ENVIRONMENT: z.enum(["dev", "qa", "stg", "prod"]),
  TLM_APP_NAME: z.string(),
  TLM_APP_PORT: z.coerce.number().default(8080),
  TLM_DB_HOST: z.string(),
  TLM_DB_PORT: z.coerce.number().default(5432),
  TLM_DB_NAME: z.string(),
  TLM_DB_USER: z.string(),
  TLM_DB_PASSWORD: z.string(),
  TLM_LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
  TLM_CACHE_REDIS_URL: z.string().optional(),
});

// Validar y exportar
export const env = envSchema.parse(process.env);

// Uso tipado
console.log(`Conectando a ${env.TLM_DB_HOST}:${env.TLM_DB_PORT}`);
```

## 6. Secretos vs Configuración

### ✅ Variables de Configuración (OK en .env)

```bash
TLM_ENVIRONMENT=prod
TLM_APP_PORT=8080
TLM_LOG_LEVEL=info
TLM_CACHE_TTL_SECONDS=3600
TLM_FEATURE_NEW_UI_ENABLED=true
```

### ❌ Secretos (NUNCA en .env, usar Vault/Secrets Manager)

```bash
# ❌ NUNCA commitear estas variables con valores reales
TLM_DB_PASSWORD=<FROM_VAULT>
TLM_API_KEY=<FROM_VAULT>
TLM_SEC_JWT_SECRET=<FROM_VAULT>
TLM_SEC_ENCRYPTION_KEY=<FROM_VAULT>
TLM_AWS_ACCESS_KEY_ID=<FROM_VAULT>
TLM_AWS_SECRET_ACCESS_KEY=<FROM_VAULT>
```

## 7. Carga desde AWS Secrets Manager

```typescript
import {
  SecretsManagerClient,
  GetSecretValueCommand,
} from "@aws-sdk/client-secrets-manager";

export async function loadSecrets() {
  const client = new SecretsManagerClient({ region: "us-east-1" });

  const secretName = `tlm/${process.env.TLM_ENVIRONMENT}/users-api`;

  const response = await client.send(
    new GetSecretValueCommand({ SecretId: secretName }),
  );

  const secrets = JSON.parse(response.SecretString!);

  // Inyectar en process.env
  process.env.TLM_DB_PASSWORD = secrets.dbPassword;
  process.env.TLM_API_KEY = secrets.apiKey;
}

// En main.ts
await loadSecrets();
```

## 8. Docker y Kubernetes

### Dockerfile

```dockerfile
FROM node:20-alpine

# Variables de build (no sensibles)
ARG TLM_APP_VERSION
ENV TLM_APP_VERSION=${TLM_APP_VERSION}

WORKDIR /app
COPY . .

RUN npm ci --only=production

# Puerto desde variable (con default)
ENV TLM_APP_PORT=8080
EXPOSE ${TLM_APP_PORT}

CMD ["node", "dist/main.js"]
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: users-api-config
data:
  TLM_ENVIRONMENT: "prod"
  TLM_APP_NAME: "users-api"
  TLM_APP_PORT: "8080"
  TLM_LOG_LEVEL: "info"
  TLM_CACHE_TTL_SECONDS: "3600"
```

### Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: users-api-secrets
type: Opaque
stringData:
  TLM_DB_PASSWORD: <base64-encoded>
  TLM_API_KEY: <base64-encoded>
```

### Deployment con Envs

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: users-api
spec:
  template:
    spec:
      containers:
        - name: api
          image: users-api:1.2.3
          envFrom:
            - configMapRef:
                name: users-api-config
            - secretRef:
                name: users-api-secrets
```

## 9. Herramientas de Validación

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Verificar que no se commiteen secretos
if git diff --cached | grep -E "PASSWORD|API_KEY|SECRET|ACCESS_KEY" | grep -v "FROM_VAULT"; then
  echo "❌ Posible secreto detectado en commit"
  echo "   Usar <FROM_VAULT> o <SECRET> como placeholder"
  exit 1
fi

# Verificar .gitignore incluye .env
if ! grep -q "^\.env$" .gitignore; then
  echo "❌ Falta .env en .gitignore"
  exit 1
fi

echo "✅ Validaciones de variables de entorno pasadas"
```

## 📖 Referencias

### Estándares relacionados

- [Gestión de Configuraciones](/docs/fundamentos-corporativos/estandares/infraestructura/configuraciones)

### Convenciones relacionadas

- [Manejo de Secretos](/docs/fundamentos-corporativos/convenciones/seguridad/manejo-secretos)

### Recursos externos

- [12 Factor App - Config](https://12factor.net/config)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)

---

**Última revisión**: 26 de enero 2026
**Responsable**: Equipo de Arquitectura
