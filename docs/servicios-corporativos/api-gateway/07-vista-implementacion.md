# 7. Vista de implementación

## 7.1 Estructura del proyecto

| Componente         | Ubicación           | Tecnología         |
|--------------------|--------------------|--------------------|
| `API Gateway`      | `/src/ApiGateway`  | `.NET 8 Web API`   |
| `YARP`             | `Microsoft.ReverseProxy` | `YARP 2.0+`      |
| `Redis`            | `AWS ElastiCache`  | `Redis 7+`         |
| `Configuración`    | `AWS Secrets Manager` | `JSON`           |
| `Docker`           | `/docker`          | `Dockerfile`        |
| `Scripts`          | `/scripts`         | `PowerShell/Bash`   |

## 7.2 Dependencias principales

| Dependencia            | Versión | Propósito                |
|------------------------|---------|--------------------------|
| `YARP`                 | 2.0+    | `Reverse Proxy`          |
| `StackExchange.Redis`  | 2.6+    | `Rate limiting`          |
| `Polly`                | 7.0+    | `Resiliencia`            |
| `Serilog`              | 3.0+    | `Logging`                |
| `Redis`                | 7.0+    | `Cache y rate limiting`  |

---

## 7.3 Infraestructura y despliegue

### 7.3.1 Arquitectura de contenedores (local)

```yaml
# docker-compose.yml para desarrollo local
version: '3.8'
services:
  api-gateway:
    build:
      context: ./src/ApiGateway
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
      - "8443:8443"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_URLS=http://+:8080;https://+:8443
      - ASPNETCORE_Kestrel__Certificates__Default__Password=password
      - ASPNETCORE_Kestrel__Certificates__Default__Path=/https/certificate.pfx
    volumes:
      - ./certs:/https:ro
      - ./config:/app/config:ro
    networks:
      - gateway-network
    depends_on:
      - redis
      - identity-service
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - gateway-network
    restart: unless-stopped

  identity-service:
    image: identity-service:latest
    ports:
      - "8081:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
    networks:
      - gateway-network
    restart: unless-stopped

networks:
  gateway-network:
    driver: bridge

volumes:
  redis-data:
```

### 7.3.2 Dockerfile optimizado

```dockerfile
# Etapa de construcción
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj and restore dependencies
COPY ["ApiGateway.csproj", "."]
RUN dotnet restore "ApiGateway.csproj"

# Copiar código fuente y construir
COPY . .
RUN dotnet build "ApiGateway.csproj" -c Release -o /app/build

# Publish stage
FROM build AS publish
RUN dotnet publish "ApiGateway.csproj" -c Release -o /app/publish \
    --no-restore --no-build

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install required packages for observability
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy published application
COPY --from=publish /app/publish .

# Set ownership and permissions
RUN chown -R appuser:appuser /app
USER appuser

# Verificación de salud
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose ports
EXPOSE 8080
EXPOSE 8443

ENTRYPOINT ["dotnet", "ApiGateway.dll"]
```

### 7.3.3 Despliegue en AWS ECS con Terraform

```hcl
# infrastructure/terraform/api-gateway-ecs.tf
resource "aws_ecs_cluster" "api_gateway" {
  name = "api-gateway-cluster"
}

resource "aws_ecs_task_definition" "api_gateway" {
  family                   = "api-gateway"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "api-gateway"
      image     = "${var.ecr_repo_url}:latest"
      cpu       = 512
      memory    = 1024
      essential = true
      portMappings = [
        { containerPort = 8080, hostPort = 8080 },
        { containerPort = 8443, hostPort = 8443 }
      ]
      environment = [
        { name = "ASPNETCORE_ENVIRONMENT", value = "Production" },
        { name = "ConnectionStrings__Redis", value = var.redis_connection_string },
        { name = "Authentication__Authority", value = var.identity_authority }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/api-gateway"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 10
      }
    }
  ])
}

resource "aws_ecs_service" "api_gateway" {
  name            = "api-gateway-service"
  cluster         = aws_ecs_cluster.api_gateway.id
  task_definition = aws_ecs_task_definition.api_gateway.arn
  desired_count   = 3
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = var.private_subnets
    security_groups  = [aws_security_group.api_gateway.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.api_gateway.arn
    container_name   = "api-gateway"
    container_port   = 8080
  }
  depends_on = [aws_lb_listener.api_gateway]
}

# ElastiCache Redis Cluster
resource "aws_elasticache_replication_group" "redis_cluster" {
  replication_group_id       = "api-gateway-redis"
  description                = "Redis cluster for API Gateway"

  node_type                  = "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = "default.redis7"

  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled          = true

  subnet_group_name = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Environment = "production"
    Service     = "api-gateway"
  }
}
```

---

## 7.4 Configuración y secretos

### 7.4.1 Configuración de la aplicación

```json
// appsettings.Production.json (fragmento)
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning"
    }
  },
  "ReverseProxy": {
    "Routes": {
      "identity-route": {
        "ClusterId": "identity-cluster",
        "Match": { "Path": "/api/identity/{**catch-all}" }
      }
    },
    "Clusters": {
      "identity-cluster": {
        "Destinations": {
          "identity-1": { "Address": "http://identity-service:8080" }
        }
      }
    }
  },
  "Authentication": {
    "Authority": "https://identity.corporate-services.local",
    "RequireHttpsMetadata": true
  },
  "RateLimiting": {
    "DefaultPolicy": {
      "PermitLimit": 1000,
      "Window": "00:01:00"
    }
  },
  "Observability": {
    "ServiceName": "api-gateway",
    "Jaeger": { "AgentHost": "jaeger-agent", "AgentPort": 6831 },
    "Prometheus": { "Enabled": true, "Path": "/metrics" }
  }
}
```

### 7.4.2 Gestión de secretos

- `AWS Secrets Manager` para credenciales sensibles (`Redis`, JWT, certificados TLS).
- Acceso a secretos vía variables de entorno y configuración segura en tiempo de despliegue.

---

## 7.5 Infraestructura como código

- Todo el despliegue productivo se realiza con `Terraform` sobre AWS (`ECS Fargate`, `ElastiCache`, `ALB`, `Secrets Manager`).
- Los entornos de desarrollo usan `docker-compose` y scripts Bash/PowerShell.
- Los pipelines CI/CD integran validaciones de seguridad (`Checkov`), análisis de código (`SonarQube`) y despliegue automatizado (`GitHub Actions`).

---

## 7.6 CI/CD Pipeline

- Pipeline basado en `GitHub Actions` con etapas de build, test, análisis de seguridad (`Trivy`), análisis de calidad (`SonarCloud`), build/push de imagen y despliegue a AWS ECS vía `Terraform` y `Helm`.
- Ejemplo de workflow:

```yaml
# .github/workflows/api-gateway-deploy.yml
name: API Gateway CI/CD

on:
  push:
    branches: [ main, develop ]
    paths: [ 'src/ApiGateway/**' ]
  pull_request:
    branches: [ main ]
    paths: [ 'src/ApiGateway/**' ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: corporate-services/api-gateway

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Setup .NET
      uses: actions/setup-dotnet@v3
      with:
        dotnet-version: '8.0.x'

    - name: Restore dependencies
      run: dotnet restore src/ApiGateway/ApiGateway.csproj

    - name: Build
      run: dotnet build src/ApiGateway/ApiGateway.csproj --no-restore

    - name: Test
      run: dotnet test src/ApiGateway.Tests/ApiGateway.Tests.csproj --no-build --verbosity normal --collect:"XPlat Code Coverage"

    - name: SonarCloud Scan
      uses: SonarSource/sonarcloud-github-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: 'src/ApiGateway'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  build-and-push:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: src/ApiGateway
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Update kubeconfig
      run: aws eks update-kubeconfig --name corporate-services-cluster

    - name: Deploy to EKS
      run: |
        helm upgrade --install api-gateway ./helm/api-gateway \
          --namespace corporate-services \
          --create-namespace \
          --set image.tag=${{ github.sha }} \
          --set environment=production \
          --wait

    - name: Verify deployment
      run: |
        kubectl rollout status deployment/api-gateway -n corporate-services
        kubectl get pods -n corporate-services -l app=api-gateway
```

---

## 7.7 Monitoring y observabilidad

- Stack de observabilidad: `Prometheus` (métricas), `Grafana` (dashboards), `Loki` (logs), `Jaeger` (tracing distribuido).
- Dashboards y alertas preconfiguradas para latencia, errores 5xx, disponibilidad y saturación de recursos.
- Exporters y anotaciones automáticas en los contenedores para scraping de métricas y logs estructurados.
- Ejemplo de configuración Prometheus:

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "api-gateway-alerts.yml"

scrape_configs:
  - job_name: 'api-gateway'
    kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
            - corporate-services
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: api-gateway-service
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        action: keep
        regex: http
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)

alertas:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 7.7.2 Alertas rules

```yaml
# monitoring/prometheus/api-gateway-alerts.yml
groups:
- name: api-gateway
  rules:
  - alert: APIGatewayHighErrorRate
    expr: (rate(http_requests_total{job="api-gateway",code=~"5.."}[5m]) / rate(http_requests_total{job="api-gateway"}[5m])) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "API Gateway error rate is above 5%"
      description: "API Gateway error rate is {{ $value | humanizePercentage }} for the last 5 minutes"

  - alert: APIGatewayHighLatency
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="api-gateway"}[5m])) > 1
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "API Gateway 95th percentile latency is high"
      description: "API Gateway 95th percentile latency is {{ $value }}s"

  - alert: APIGatewayDown
    expr: up{job="api-gateway"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "API Gateway is down"
      description: "API Gateway has been down for more than 1 minute"
```

---

> La implementación del API Gateway sigue los principios de Clean Architecture, IaC, seguridad y observabilidad, alineada a los ADRs y modelos C4/Structurizr DSL del sistema.
