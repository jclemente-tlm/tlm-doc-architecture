---
id: load-balancing
sidebar_position: 2
title: Load Balancing
description: Distribución de carga con Application Load Balancer y Kong API Gateway
---

# Load Balancing

## Contexto

Este estándar define cómo configurar load balancing para distribuir tráfico entre múltiples instancias, mejorar disponibilidad y optimizar utilización de recursos. Complementa el [lineamiento de Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md) especificando **cómo balancear carga** en diferentes capas.

---

## Stack Tecnológico

| Componente       | Tecnología                    | Versión | Uso                              |
| ---------------- | ----------------------------- | ------- | -------------------------------- |
| **Layer 7 LB**   | AWS Application Load Balancer | -       | Load balancing HTTP/HTTPS        |
| **API Gateway**  | Kong API Gateway              | 3.4+    | API gateway con routing avanzado |
| **Service Mesh** | AWS App Mesh (opcional)       | -       | Advanced traffic management      |

---

## Implementación Técnica

### Capas de Load Balancing

```yaml
# Arquitectura de Load Balancing en Talma

Internet
  ↓
AWS ALB (Layer 7)  # ✅ SSL/TLS termination, path-based routing
  ↓
Kong API Gateway   # ✅ API management, rate limiting, authentication
  ↓
ECS Services       # ✅ Multiple tasks (auto-scaled)
```

### Application Load Balancer (Terraform)

```hcl
# Application Load Balancer
resource "aws_lb" "main" {
  name               = "tlm-main-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids

  # ✅ Habilitar deletion protection en producción
  enable_deletion_protection = var.environment == "production"

  # ✅ Logging a S3
  access_logs {
    bucket  = aws_s3_bucket.alb_logs.id
    prefix  = "alb"
    enabled = true
  }

  # ✅ HTTP/2 habilitado por default
  enable_http2 = true

  # ✅ Drop invalid headers
  drop_invalid_header_fields = true

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# HTTPS Listener (port 443)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.main.arn

  # ✅ Default action: forward to Kong API Gateway
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.kong.arn
  }
}

# HTTP Listener (port 80) - Redirect a HTTPS
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}
```

### Target Groups

```hcl
# Target Group - Kong API Gateway
resource "aws_lb_target_group" "kong" {
  name     = "tlm-kong-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  target_type = "ip"  # ✅ Para Fargate

  # ✅ Health check configuration
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  # ✅ Deregistration delay (connection draining)
  deregistration_delay = 30

  # ✅ Stickiness (use solo cuando sea necesario)
  stickiness {
    enabled = false  # ✅ Stateless design no requiere sticky sessions
    type    = "lb_cookie"
    cookie_duration = 3600
  }
}

# Target Group - Orders API (directo, bypass Kong si necesario)
resource "aws_lb_target_group" "orders_api" {
  name     = "tlm-orders-api-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  deregistration_delay = 30
}
```

### Path-Based Routing

```hcl
# Routing basado en path para diferentes services
resource "aws_lb_listener_rule" "orders_api_direct" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.orders_api.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/orders/*"]
    }
  }
}

# Routing basado en host header
resource "aws_lb_listener_rule" "api_subdomain" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 90

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.kong.arn
  }

  condition {
    host_header {
      values = ["api.talma.com", "api.*.talma.com"]
    }
  }
}

# Fixed response para health check externo
resource "aws_lb_listener_rule" "health" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  action {
    type = "fixed-response"

    fixed_response {
      content_type = "text/plain"
      message_body = "OK"
      status_code  = "200"
    }
  }

  condition {
    path_pattern {
      values = ["/health"]
    }
  }
}
```

### Kong API Gateway Load Balancing

```yaml
# Kong Service para Orders API con load balancing
services:
  - name: orders-api
    url: http://orders-api-tasks.local:8080

    # ✅ Retries automáticos
    retries: 3

    # ✅ Timeouts
    connect_timeout: 5000
    write_timeout: 60000
    read_timeout: 60000

# Kong Upstream (pool de targets)
upstreams:
  - name: orders-api-upstream

    # ✅ Algoritmo de balanceo
    algorithm: round-robin # round-robin, consistent-hashing, least-connections

    # ✅ Hash basado en header para sticky sessions (si necesario)
    hash_on: header
    hash_on_header: X-User-ID
    hash_fallback: ip

    # ✅ Health checks activos
    healthchecks:
      active:
        type: http
        http_path: /health
        healthy:
          interval: 10
          successes: 2
        unhealthy:
          interval: 5
          http_failures: 3
          timeouts: 2

      # ✅ Health checks pasivos (basado en tráfico real)
      passive:
        type: http
        healthy:
          successes: 5
        unhealthy:
          http_failures: 5
          timeouts: 3

    # ✅ Slots para targets
    slots: 10000

# Kong Targets (instancias del servicio)
targets:
  - upstream: orders-api-upstream
    target: orders-api-01.local:8080
    weight: 100

  - upstream: orders-api-upstream
    target: orders-api-02.local:8080
    weight: 100

  - upstream: orders-api-upstream
    target: orders-api-03.local:8080
    weight: 100

# Kong Routes
routes:
  - name: orders-route
    service: orders-api
    paths:
      - /api/v1/orders
    methods:
      - GET
      - POST
      - PUT
      - DELETE
    strip_path: false
    preserve_host: true
```

### kong Load Balancing Algorithms

```yaml
# ✅ Round Robin - Default, distribución uniforme
upstreams:
  - name: orders-api-upstream
    algorithm: round-robin

# ✅ Consistent Hashing - Sticky sessions por user/session
upstreams:
  - name: catalog-api-upstream
    algorithm: consistent-hashing
    hash_on: header
    hash_on_header: X-User-ID
    # Mismo usuario siempre al mismo backend

# ✅ Least Connections - Para cargas desiguales
upstreams:
  - name: analytics-api-upstream
    algorithm: least-connections
    # Envía requests al backend con menos conexiones activas

# ✅ Weighted Round Robin - Blue/Green deployments
targets:
  - upstream: orders-api-upstream
    target: orders-api-blue.local:8080
    weight: 90  # 90% del tráfico

  - upstream: orders-api-upstream
    target: orders-api-green.local:8080
    weight: 10  # 10% del tráfico (canary)
```

### Circuit Breaker en Kong

```yaml
# Plugin: Circuit Breaker
plugins:
  - name: proxy-cache
    service: orders-api
    config:
      # ✅ Cache responses cuando backend está down
      cache_ttl: 300
      strategy: memory

  # ✅ Request Termination cuando todos los targets unhealthy
  - name: request-termination
    service: orders-api
    config:
      status_code: 503
      message: "Service temporarily unavailable"
```

### Connection Pooling en Kong

```yaml
# Kong configuration (kong.conf)
upstream_keepalive_pool_size = 100  # ✅ Pool size por worker
upstream_keepalive_max_requests = 10000  # ✅ Requests por connection
upstream_keepalive_idle_timeout = 60  # ✅ Idle timeout (segundos)

# Nginx configuration
nginx_http_upstream_keepalive = 320  # ✅ Keepalive connections
nginx_http_upstream_keepalive_requests = 10000
nginx_http_upstream_keepalive_timeout = 60s
```

### Métricas de Load Balancing

```yaml
# ALB Metrics (CloudWatch)
ALBRequestCount: # Total requests
ALBTargetResponseTime: # Latency promedio
HealthyHostCount: # Targets healthy
UnHealthyHostCount: # Targets unhealthy
HTTPCode_Target_2XX_Count: # Success responses
HTTPCode_Target_5XX_Count: # Error responses
RejectedConnectionCount: # Connections rechazadas
TargetConnectionErrorCount: # Connection errors

# Kong Metrics (Prometheus)
kong_http_requests_total: # Total requests por service/route
kong_latency_bucket: # Latency histogram
kong_upstream_target_health: # Health status de targets
kong_bandwidth_bytes: # Bytes transferidos
kong_datastore_reachable: # DB connectivity
```

### Dashboard de Monitoreo

```yaml
# Grafana Dashboard Panels

# ✅ Request Rate por Service
sum(rate(kong_http_requests_total[5m])) by (service)

# ✅ Target Distribution
sum by (target) (kong_upstream_target_health{state="healthy"})

# ✅ ALB Latency P95
quantile(0.95, aws_alb_target_response_time)

# ✅ Error Rate
sum(rate(kong_http_requests_total{status=~"5.."}[5m])) /
sum(rate(kong_http_requests_total[5m])) * 100

# ✅ Healthy Targets Percentage
(aws_alb_healthy_host_count /
 (aws_alb_healthy_host_count + aws_alb_unhealthy_host_count)) * 100
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar Application Load Balancer para tráfico HTTP/HTTPS
- **MUST** configurar health checks en todos los target groups
- **MUST** configurar deregistration_delay (connection draining)
- **MUST** habilitar access logs en S3
- **MUST** usar TLS 1.3 como mínimo (ssl_policy)
- **MUST** configurar múltiples AZs para high availability
- **MUST** monitorear métricas de ALB (latency, targets healthy)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar Kong API Gateway para APIs públicas
- **SHOULD** configurar algoritmos de balanceo apropiados
- **SHOULD** implementar health checks activos y pasivos
- **SHOULD** configurar connection pooling
- **SHOULD** usar path-based routing para microservices
- **SHOULD** habilitar HTTP/2 en ALB
- **SHOULD** evitar sticky sessions (preferir stateless design)

### MAY (Opcional)

- **MAY** implementar weighted routing para canary deployments
- **MAY** usar consistent hashing si sticky sessions es necesario
- **MAY** configurar fixed responses para endpoints simples
- **MAY** implementar service mesh (App Mesh) para advanced routing
- **MAY** usar Lambda targets para serverless backends

### MUST NOT (Prohibido)

- **MUST NOT** usar Network Load Balancer para HTTP/HTTPS
- **MUST NOT** depender de sticky sessions para funcionalidad crítica
- **MUST NOT** configurar health_check interval < 10s
- **MUST NOT** usar TLS < 1.2
- **MUST NOT** ignorar targets unhealthy
- **MUST NOT** configurar deregistration_delay muy alto (> 60s)

---

## Referencias

- [Lineamiento: Escalabilidad y Rendimiento](../../lineamientos/arquitectura/05-escalabilidad-y-rendimiento.md)
- Estándares relacionados:
  - [Diseño Stateless](../../estandares/arquitectura/stateless-design.md)
  - [Auto-Scaling](horizontal-scaling.md)
- ADRs:
  - [ADR-008: Kong API Gateway](../../../decisiones-de-arquitectura/adr-008-kong-api-gateway.md)
- Especificaciones:
  - [AWS ALB Documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
  - [Kong Load Balancing](https://docs.konghq.com/gateway/latest/how-kong-works/load-balancing/)
