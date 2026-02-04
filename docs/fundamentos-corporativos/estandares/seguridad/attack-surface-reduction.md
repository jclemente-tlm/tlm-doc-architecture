---
id: attack-surface-reduction
sidebar_position: 1
title: Reducción de Superficie de Ataque
description: Estándar para minimizar superficie de ataque con minimal containers, disable unused features, least privilege y security hardening
---

# Estándar Técnico — Reducción de Superficie de Ataque

---

## 1. Propósito

Minimizar superficie de ataque eliminando componentes innecesarios, deshabilitando features no usados, usando minimal container images (Alpine/Distroless), aplicando least privilege y hardening de configuraciones.

---

## 2. Alcance

**Aplica a:**

- Container images (Dockerfile)
- Configuración de servidores
- APIs expuestas
- Servicios de red
- Dependencias de software
- Ports abiertos

**No aplica a:**

- Funcionalidad requerida por negocio

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología          | Versión mínima | Observaciones            |
| ----------------- | ------------------- | -------------- | ------------------------ |
| **Base Image**    | Alpine Linux        | 3.18+          | Minimal footprint        |
| **Runtime Image** | Distroless          | -              | Google distroless/dotnet |
| **Scanner**       | Trivy               | 0.48+          | Vulnerabilidades         |
| **Hardening**     | CIS Benchmarks      | -              | Docker/Kubernetes        |
| **Firewall**      | AWS Security Groups | -              | Deny by default          |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Containers

- [ ] **Minimal base images**: Alpine o Distroless (NO ubuntu:latest)
- [ ] **Multi-stage builds**: Runtime sin build tools
- [ ] **Non-root user**: UID > 1000
- [ ] **Read-only filesystem**: Excepto /tmp
- [ ] **NO shells**: Eliminar bash/sh en producción

### Network

- [ ] **Solo ports necesarios**: Cerrar todo lo demás
- [ ] **NO telnet/FTP**: Usar SSH/SFTP cifrado
- [ ] **Disable IPv6**: Si no se usa
- [ ] **Firewall deny-by-default**: Explicit allows

### Software

- [ ] **Minimal dependencies**: Solo paquetes necesarios
- [ ] **NO debug tools**: En producción (gdb, strace, etc.)
- [ ] **Remove package managers**: apk, apt en runtime
- [ ] **Disable unused features**: Módulos no requeridos

### Services

- [ ] **Disable admin endpoints**: /swagger, /metrics sin auth
- [ ] **NO directory listing**: 403 en vez de 404
- [ ] **Remove default accounts**: admin/admin

---

## 5. Dockerfile - Minimal Images

### Multi-Stage Build con Alpine

```dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src

# Copiar solo .csproj primero (cache optimization)
COPY ["PaymentApi/PaymentApi.csproj", "PaymentApi/"]
RUN dotnet restore "PaymentApi/PaymentApi.csproj"

# Copiar código y compilar
COPY . .
WORKDIR "/src/PaymentApi"
RUN dotnet build "PaymentApi.csproj" -c Release -o /app/build
RUN dotnet publish "PaymentApi.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 2: Runtime (Alpine minimal)
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS runtime

# Crear usuario non-root
RUN addgroup -g 1001 appgroup && \
    adduser -D -u 1001 -G appgroup appuser

# Instalar SOLO dependencias necesarias
RUN apk add --no-cache \
    ca-certificates \
    tzdata

# Remover package manager después de instalación
RUN apk del apk-tools

WORKDIR /app

# Copiar binarios desde build stage
COPY --from=build --chown=appuser:appgroup /app/publish .

# Cambiar a non-root user
USER appuser

# Configurar read-only filesystem (excepto /tmp)
VOLUME /tmp

# Exponer SOLO port necesario
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

ENTRYPOINT ["dotnet", "PaymentApi.dll"]
```

### Distroless (Mínimo Absoluto)

```dockerfile
# Stage 1: Build (igual que arriba)
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
# ... (build steps)

# Stage 2: Runtime con Distroless (NO shell, NO package manager)
FROM gcr.io/distroless/dotnet:8

WORKDIR /app
COPY --from=build /app/publish .

USER 1001:1001

EXPOSE 8080

# Distroless NO tiene shell, usar exec form
ENTRYPOINT ["dotnet", "PaymentApi.dll"]
```

### Comparación de Tamaños

```bash
# Ubuntu base
IMAGE                              SIZE
mcr.microsoft.com/dotnet/aspnet:8.0        216MB

# Alpine
mcr.microsoft.com/dotnet/aspnet:8.0-alpine 116MB  # -46%

# Distroless
gcr.io/distroless/dotnet:8                  89MB  # -59%
```

---

## 6. Security Hardening - Container Runtime

### ECS Task Definition (Read-Only Root)

```hcl
# terraform/ecs.tf
resource "aws_ecs_task_definition" "payment_api" {
  family                   = "payment-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([{
    name  = "payment-api"
    image = "${var.ecr_repository}/payment-api:${var.image_tag}"

    # Security hardening
    readonlyRootFilesystem = true  # ✅ Read-only root
    privileged             = false  # ✅ NO privileged mode
    user                   = "1001" # ✅ Non-root user

    # Mount /tmp como writable (único directorio escribible)
    mountPoints = [{
      sourceVolume  = "tmp"
      containerPath = "/tmp"
      readOnly      = false
    }]

    # Linux capabilities: Drop ALL, add solo necesarios
    linuxParameters = {
      capabilities = {
        drop = ["ALL"]
        add  = []  # Vacío = NO capabilities (más seguro)
      }
    }

    # Environment variables desde Secrets Manager
    secrets = [
      {
        name      = "ConnectionStrings__DefaultConnection"
        valueFrom = aws_secretsmanager_secret.db_connection.arn
      }
    ]
  }])

  # Volume para /tmp
  volume {
    name = "tmp"
  }

  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn
}
```

---

## 7. .NET - Disable Unused Features

### Program.cs - Minimal Surface

```csharp
var builder = WebApplication.CreateBuilder(args);

// ❌ NO habilitar features innecesarios
// builder.Services.AddSwaggerGen();  // Solo en dev
// builder.Services.AddCors();        // Solo si es necesario

// ✅ Solo servicios necesarios
builder.Services.AddControllers(options =>
{
    // Deshabilitar formatters no usados
    options.InputFormatters.RemoveType<XmlSerializerInputFormatter>();
    options.OutputFormatters.RemoveType<XmlSerializerOutputFormatter>();
});

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(/* ... */);

var app = builder.Build();

// ❌ NO exponer en producción
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
else
{
    // Producción: NO Swagger, NO detailed errors
    app.UseExceptionHandler("/error");
}

// ❌ NO exponer headers innecesarios
app.Use(async (context, next) =>
{
    context.Response.Headers.Remove("Server");
    context.Response.Headers.Remove("X-Powered-By");
    context.Response.Headers.Remove("X-AspNet-Version");
    await next();
});

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### Disable Development Endpoints

```csharp
// Controllers/DebugController.cs
#if DEBUG
[ApiController]
[Route("api/debug")]
public class DebugController : ControllerBase
{
    [HttpGet("env")]
    public IActionResult GetEnvironmentVariables()
    {
        return Ok(Environment.GetEnvironmentVariables());
    }
}
#endif
// ✅ Este controller NO existe en Release build
```

---

## 8. Network - Minimal Ports

### Security Group (Solo Port Necesario)

```hcl
# terraform/security-groups.tf
resource "aws_security_group" "backend" {
  name        = "${var.environment}-backend-sg"
  description = "Backend API"
  vpc_id      = aws_vpc.main.id

  # Ingress: SOLO port 8080 desde Kong
  ingress {
    description     = "HTTP from Kong"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.kong.id]
  }

  # ❌ NO abrir rangos amplios
  # ingress {
  #   from_port   = 0
  #   to_port     = 65535  # ❌ TODO abierto
  #   protocol    = "tcp"
  # }

  # ❌ NO abrir SSH (usar AWS Systems Manager Session Manager)
  # ingress {
  #   from_port   = 22
  #   to_port     = 22
  #   protocol    = "tcp"
  # }

  # Egress: Específico (no 0.0.0.0/0)
  egress {
    description     = "To PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.postgres.id]
  }

  egress {
    description = "HTTPS for external APIs"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # OK para HTTPS saliente
  }
}
```

---

## 9. PostgreSQL - Disable Unused Extensions

```sql
-- Listar extensiones instaladas
SELECT * FROM pg_extension;

-- Remover extensiones no usadas
DROP EXTENSION IF EXISTS plpython3u;  -- Python procedural language (riesgo)
DROP EXTENSION IF EXISTS adminpack;   -- Admin tools (no necesario)

-- Mantener solo necesarios
-- uuid-ossp (UUIDs)
-- pg_stat_statements (monitoring)
-- pg_trgm (text search)

-- Deshabilitar funciones peligrosas
REVOKE ALL ON FUNCTION pg_read_file(text) FROM PUBLIC;
REVOKE ALL ON FUNCTION pg_ls_dir(text) FROM PUBLIC;
```

---

## 10. Validación de Cumplimiento

```bash
# Escanear imagen con Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image payment-api:latest \
  --severity HIGH,CRITICAL \
  --exit-code 1

# Verificar imagen corre como non-root
docker inspect payment-api:latest | jq '.[0].Config.User'
# Esperado: "1001" o "appuser"

# Verificar NO hay shell
docker run --rm payment-api:latest sh
# Esperado: Error (no shell disponible)

# Contar puertos expuestos
docker inspect payment-api:latest | jq '.[0].Config.ExposedPorts | length'
# Esperado: 1 (solo 8080)

# Verificar Security Groups tienen minimal ports
aws ec2 describe-security-groups --group-ids sg-xxx \
  --query 'SecurityGroups[0].IpPermissions[*].[FromPort,ToPort]'
# Esperado: Solo ports necesarios
```

---

## 11. Referencias

**CIS Benchmarks:**

- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)

**OWASP:**

- [OWASP Attack Surface Analysis](https://owasp.org/www-community/Attack_Surface_Analysis_Cheat_Sheet)

**NIST:**

- [NIST 800-190 Container Security](https://csrc.nist.gov/publications/detail/sp/800-190/final)
