---
id: zero-trust-network
sidebar_position: 25
title: Zero Trust Network
description: Estándar para implementar arquitectura Zero Trust con never trust always verify, micro-segmentación, JWT verification y mTLS
---

# Estándar Técnico — Zero Trust Network

---

## 1. Propósito

Implementar arquitectura Zero Trust basada en "never trust, always verify", eliminando perímetro de confianza implícito, usando micro-segmentación con Security Groups, autenticación continua con JWT, mTLS para service-to-service y least privilege.

---

## 2. Alcance

**Aplica a:**

- Comunicación entre servicios
- Acceso a APIs
- Conexiones a bases de datos
- Acceso remoto
- Tráfico interno VPC

**No aplica a:**

- Comunicación dentro de contenedor (localhost)

---

## 3. Tecnologías Aprobadas

| Componente       | Tecnología              | Versión mínima | Observaciones             |
| ---------------- | ----------------------- | -------------- | ------------------------- |
| **Network**      | AWS VPC Security Groups | -              | Deny by default           |
| **API Gateway**  | Kong                    | 3.5+           | JWT verification          |
| **Service Mesh** | mTLS (manual)           | -              | Certificados por servicio |
| **Auth**         | Keycloak JWT            | 23.0+          | Token validation          |
| **Encryption**   | TLS 1.3                 | -              | Obligatorio               |
| **Secrets**      | AWS Secrets Manager     | -              | Rotación automática       |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### Principios Zero Trust

- [ ] **Never trust, always verify**: No confiar por ubicación de red
- [ ] **Least privilege**: Mínimos permisos necesarios
- [ ] **Assume breach**: Diseñar asumiendo que ya hubo intrusión
- [ ] **Verify explicitly**: Autenticar y autorizar cada request
- [ ] **Micro-segmentation**: Segmentar por servicio, no por red

### Autenticación

- [ ] **JWT obligatorio**: Todas las APIs requieren JWT válido
- [ ] **Service accounts**: Identidades para comunicación service-to-service
- [ ] **mTLS**: Certificados client para servicios críticos
- [ ] **NO IP whitelisting**: No confiar por IP origen

### Network Segmentation

- [ ] **Security Groups**: Deny-by-default, explicit allows
- [ ] **NO VPN trust**: VPN no otorga acceso automático
- [ ] **Private subnets**: BDs y servicios internos sin IP pública

### Encryption

- [ ] **TLS 1.3**: Obligatorio para todo tráfico
- [ ] **mTLS**: Para comunicación crítica
- [ ] **Encryption in transit**: HTTPS/TLS siempre

---

## 5. AWS - Micro-Segmentación

### Security Groups (Deny by Default)

```hcl
# terraform/security-groups.tf

# Security Group para API Gateway (Kong)
resource "aws_security_group" "kong" {
  name        = "${var.environment}-kong-sg"
  description = "Kong API Gateway"
  vpc_id      = aws_vpc.main.id

  # Ingress: Solo desde ALB
  ingress {
    description     = "HTTPS from ALB"
    from_port       = 8443
    to_port         = 8443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Egress: Solo a servicios backend
  egress {
    description     = "To backend services"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  tags = {
    Name        = "${var.environment}-kong-sg"
    Environment = var.environment
  }
}

# Security Group para Backend Services
resource "aws_security_group" "backend" {
  name        = "${var.environment}-backend-sg"
  description = "Backend services (ECS tasks)"
  vpc_id      = aws_vpc.main.id

  # Ingress: Solo desde Kong
  ingress {
    description     = "HTTP from Kong"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.kong.id]
  }

  # Egress: Solo a PostgreSQL y Redis
  egress {
    description     = "To PostgreSQL"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.postgres.id]
  }

  egress {
    description     = "To Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.redis.id]
  }

  # Egress: HTTPS para llamadas externas (APIs terceros)
  egress {
    description = "HTTPS to Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-backend-sg"
    Environment = var.environment
  }
}

# Security Group para PostgreSQL
resource "aws_security_group" "postgres" {
  name        = "${var.environment}-postgres-sg"
  description = "PostgreSQL RDS"
  vpc_id      = aws_vpc.main.id

  # Ingress: SOLO desde backend services (NO desde Internet)
  ingress {
    description     = "PostgreSQL from backend"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.backend.id]
  }

  # NO egress rules (no necesita salir)

  tags = {
    Name        = "${var.environment}-postgres-sg"
    Environment = var.environment
  }
}
```

---

## 6. Kong - JWT Verification (Always Verify)

### Plugin JWT en Todas las Rutas

```bash
# Configurar JWT plugin globalmente
curl -X POST http://kong:8001/plugins \
  --data "name=jwt" \
  --data "config.key_claim_name=kid" \
  --data "config.secret_is_base64=false" \
  --data "config.claims_to_verify=exp,nbf"

# Configurar Keycloak como issuer
curl -X POST http://kong:8001/consumers \
  --data "username=keycloak"

curl -X POST http://kong:8001/consumers/keycloak/jwt \
  --data "key=talma-realm" \
  --data "algorithm=RS256" \
  --data "rsa_public_key=@/etc/kong/keycloak-public.pem"
```

### Validación de Claims

```yaml
# kong.yml
plugins:
  - name: jwt
    config:
      claims_to_verify:
        - exp # Token no expirado
        - nbf # Not before
        - iat # Issued at
      key_claim_name: kid

  - name: request-transformer
    config:
      add:
        headers:
          - "X-User-Id:$(claims.sub)"
          - "X-Tenant-Id:$(claims.tenant_id)"
          - "X-Roles:$(claims.roles)"
```

---

## 7. .NET - Service-to-Service mTLS

### Cliente HTTP con Certificado

```csharp
// Services/SecureHttpClient.cs
public class SecureHttpClientFactory
{
    private readonly IConfiguration _configuration;

    public HttpClient CreateMtlsClient(string serviceName)
    {
        var handler = new HttpClientHandler();

        // Cargar certificado client desde AWS Secrets Manager
        var certPem = GetClientCertificate(serviceName);
        var cert = X509Certificate2.CreateFromPem(certPem.Certificate, certPem.PrivateKey);

        handler.ClientCertificates.Add(cert);
        handler.ClientCertificateOptions = ClientCertificateOption.Manual;

        // Verificar certificado del servidor
        handler.ServerCertificateCustomValidationCallback = (message, cert, chain, errors) =>
        {
            // Validar CN del certificado
            return cert.Subject.Contains($"CN={serviceName}.talma.internal");
        };

        var client = new HttpClient(handler)
        {
            BaseAddress = new Uri(_configuration[$"Services:{serviceName}:Url"])
        };

        return client;
    }

    private (string Certificate, string PrivateKey) GetClientCertificate(string serviceName)
    {
        // Leer desde AWS Secrets Manager
        var secretName = $"{serviceName}-client-cert";
        // ... implementación AWS SDK
        return (certificate, privateKey);
    }
}

// Program.cs
builder.Services.AddSingleton<SecureHttpClientFactory>();

builder.Services.AddHttpClient("PaymentService")
    .ConfigurePrimaryHttpMessageHandler(sp =>
    {
        var factory = sp.GetRequiredService<SecureHttpClientFactory>();
        return factory.CreateMtlsClient("payment-service").GetType()
            .GetProperty("HttpMessageHandler")
            .GetValue(factory.CreateMtlsClient("payment-service")) as HttpMessageHandler;
    });
```

### Servidor HTTPS con mTLS

```csharp
// Program.cs
builder.WebHost.ConfigureKestrel(options =>
{
    options.ConfigureHttpsDefaults(httpsOptions =>
    {
        httpsOptions.ClientCertificateMode = ClientCertificateMode.RequireCertificate;
        httpsOptions.ClientCertificateValidation = (cert, chain, errors) =>
        {
            // Validar certificado client contra CA conocida
            var trustedCerts = LoadTrustedCertificates();
            return trustedCerts.Any(tc => tc.Thumbprint == cert.Issuer);
        };
    });
});

private static List<X509Certificate2> LoadTrustedCertificates()
{
    // Cargar CA certificates desde AWS Secrets Manager
    // ...
    return certificates;
}
```

---

## 8. Keycloak - Service Accounts

### Crear Service Account

```bash
# Keycloak Admin CLI
kcadm.sh create clients -r talma-internal \
  -s clientId=payment-service \
  -s serviceAccountsEnabled=true \
  -s directAccessGrantsEnabled=false \
  -s standardFlowEnabled=false

# Obtener client secret
kcadm.sh get clients/{client-id}/client-secret -r talma-internal
```

### .NET - Obtener Token para Service Account

```csharp
// Services/ServiceAccountTokenService.cs
public class ServiceAccountTokenService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly IConfiguration _configuration;
    private string _cachedToken;
    private DateTime _tokenExpiry;

    public async Task<string> GetServiceAccountTokenAsync()
    {
        if (!string.IsNullOrEmpty(_cachedToken) && DateTime.UtcNow < _tokenExpiry)
        {
            return _cachedToken;
        }

        var client = _httpClientFactory.CreateClient();
        var tokenEndpoint = $"{_configuration["Keycloak:Authority"]}/protocol/openid-connect/token";

        var request = new HttpRequestMessage(HttpMethod.Post, tokenEndpoint);
        request.Content = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["grant_type"] = "client_credentials",
            ["client_id"] = _configuration["Keycloak:ClientId"],
            ["client_secret"] = _configuration["Keycloak:ClientSecret"],
            ["scope"] = "openid"
        });

        var response = await client.SendAsync(request);
        response.EnsureSuccessStatusCode();

        var tokenResponse = await response.Content.ReadFromJsonAsync<TokenResponse>();

        _cachedToken = tokenResponse.AccessToken;
        _tokenExpiry = DateTime.UtcNow.AddSeconds(tokenResponse.ExpiresIn - 60); // 1min buffer

        return _cachedToken;
    }
}

public record TokenResponse(string AccessToken, int ExpiresIn, string TokenType);
```

---

## 9. Monitoring - Zero Trust Telemetry

### Métricas

```promql
# Requests sin JWT (deben ser 0)
sum(rate(kong_http_requests_total{route=~".+", jwt_verified="false"}[5m]))

# mTLS handshake failures
sum(rate(http_server_tls_handshake_errors_total[5m]))

# Unauthorized access attempts
sum(rate(http_requests_total{status="401"}[5m])) by (route)
```

### Alertas

```yaml
# Prometheus alerts
- alert: RequestsWithoutJWT
  expr: sum(rate(kong_http_requests_total{jwt_verified="false"}[5m])) > 0
  for: 1m
  annotations:
    summary: "Requests bypassing JWT verification detected"

- alert: HighUnauthorizedRate
  expr: sum(rate(http_requests_total{status="401"}[5m])) > 10
  for: 5m
  annotations:
    summary: "High rate of unauthorized access attempts"
```

---

## 10. Validación de Cumplimiento

```bash
# Verificar Security Groups tienen deny-by-default
aws ec2 describe-security-groups --region us-east-1 \
  --query 'SecurityGroups[?length(IpPermissions)==`0`].[GroupId,GroupName]' \
  --output table

# Verificar servicios expuestos NO tienen IP pública
aws ec2 describe-instances --region us-east-1 \
  --filters "Name=tag:Service,Values=backend" \
  --query 'Reservations[].Instances[?PublicIpAddress!=null].[InstanceId,PublicIpAddress]'

# Test: Request sin JWT debe fallar
curl -i https://api.talma.com/payments
# Esperado: HTTP/1.1 401 Unauthorized

# Test: Request con JWT válido
TOKEN=$(curl -X POST https://auth.talma.com/realms/talma-internal/protocol/openid-connect/token \
  -d "grant_type=password&client_id=payment-api&username=test&password=test" | jq -r .access_token)

curl -H "Authorization: Bearer $TOKEN" https://api.talma.com/payments
# Esperado: HTTP/1.1 200 OK
```

---

## 11. Referencias

**NIST:**

- [NIST 800-207 Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)

**Google:**

- [BeyondCorp: A New Approach to Enterprise Security](https://cloud.google.com/beyondcorp)

**Forrester:**

- [The Zero Trust eXtended (ZTX) Ecosystem](https://www.forrester.com/what-it-means/zero-trust/)
