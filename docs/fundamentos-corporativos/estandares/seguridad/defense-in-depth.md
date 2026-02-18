---
id: defense-in-depth
sidebar_position: 1
title: Defense in Depth
description: Defensa en profundidad - múltiples capas de seguridad para protección redundante
---

# Defense in Depth

## Contexto

Este estándar define **Defense in Depth**: estrategia de seguridad con **múltiples capas** de controles. Si una capa falla, otras capas protegen el sistema. Ninguna capa única es suficiente; la combinación proporciona seguridad robusta. Complementa [Security by Design](./security-by-design.md) y [Network Segmentation](./network-segmentation.md).

---

## Concepto Fundamental

```yaml
# ✅ Defense in Depth (7 Layers)

Medieval Castle Analogy:

  Layer 1: Moat (perimeter)
  Layer 2: Outer wall (network)
  Layer 3: Guards (authentication)
  Layer 4: Inner wall (application)
  Layer 5: Vault (data)
  Layer 6: Guards inside (monitoring)
  Layer 7: Escape tunnels (incident response)

Modern Architecture:

  Layer 1: Perimeter Security (WAF, DDoS protection)
  Layer 2: Network Security (Security Groups, NACLs)
  Layer 3: Identity & Access (Authentication, Authorization)
  Layer 4: Application Security (Input validation, HTTPS)
  Layer 5: Data Security (Encryption, masking)
  Layer 6: Monitoring & Detection (CloudWatch, GuardDuty)
  Layer 7: Incident Response (Playbooks, backups)

Principle:
  If attacker breaches Layer 1 → Still blocked by Layer 2
  If attacker breaches Layer 2 → Still blocked by Layer 3
  If attacker breaches Layer 3 → Still blocked by Layer 4
  ...and so on

Example Attack Path (WITHOUT Defense in Depth):

  1. Attacker bypasses WAF → ✅ Access to API
  2. No authentication → ✅ Access to all endpoints
  3. No authorization → ✅ Access to all data
  4. No encryption → ✅ Read sensitive data
  5. No monitoring → ❌ Attack undetected

  Result: Complete breach

Example Attack Path (WITH Defense in Depth):

  1. Attacker bypasses WAF → ⚠️ Reaches API
  2. Authentication required → ❌ BLOCKED (no valid token)

  (If attacker steals token somehow):
  3. Authorization checks → ❌ BLOCKED (token lacks permissions)

  (If attacker escalates privileges):
  4. Data encryption → ❌ Can't read encrypted fields

  (If attacker has decryption key):
  5. Monitoring detects anomaly → 🚨 ALERT (unusual data access)
  6. Incident response → 🔒 Account disabled, attacker blocked

  Result: Attack contained
```

## Layer 1: Perimeter Security

```yaml
# ✅ Perimeter Defense (Edge Protection)

WAF (Web Application Firewall):

  AWS WAF with Managed Rules:

  resource "aws_wafv2_web_acl" "main" {
    name  = "talma-waf"
    scope = "REGIONAL"

    default_action {
      allow {}
    }

    # ✅ AWS Managed Rules
    rule {
      name     = "AWSManagedRulesCommonRuleSet"
      priority = 1

      override_action {
        none {}
      }

      statement {
        managed_rule_group_statement {
          vendor_name = "AWS"
          name        = "AWSManagedRulesCommonRuleSet"

          # Blocks: SQL injection, XSS, LFI, RFI
        }
      }
    }

    # ✅ Rate Limiting
    rule {
      name     = "RateLimitRule"
      priority = 2

      action {
        block {}
      }

      statement {
        rate_based_statement {
          limit              = 2000  # 2000 requests per 5 minutes
          aggregate_key_type = "IP"
        }
      }
    }

    # ✅ Geo Blocking (block countries with no business presence)
    rule {
      name     = "GeoBlockRule"
      priority = 3

      action {
        block {}
      }

      statement {
        geo_match_statement {
          country_codes = ["CN", "RU", "KP"]  # Example: Block high-risk countries
        }
      }
    }
  }

DDoS Protection:

  AWS Shield Standard (Automatic, Free):
    - Layer 3/4 DDoS protection (SYN flood, UDP reflection)
    - Automatic detection and mitigation

  AWS Shield Advanced (Optional, for critical services):
    - Cost: $3000/month
    - Advanced DDoS protection
    - 24/7 DDoS Response Team (DRT)
    - Cost protection (no charges during DDoS)
    - Use for: Payment service, critical APIs

CloudFront (CDN with DDoS mitigation):

  resource "aws_cloudfront_distribution" "api" {
    enabled = true

    origin {
      domain_name = aws_lb.main.dns_name
      origin_id   = "ALB"

      custom_origin_config {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "https-only"
      }
    }

    # ✅ HTTPS Only
    default_cache_behavior {
      viewer_protocol_policy = "redirect-to-https"

      # ✅ Security Headers
      response_headers_policy_id = aws_cloudfront_response_headers_policy.security.id
    }

    # ✅ Geo Restrictions
    restrictions {
      geo_restriction {
        restriction_type = "whitelist"
        locations        = ["PE", "US", "BR", "CL"]  # Talma operates in these countries
      }
    }

    # ✅ WAF Association
    web_acl_id = aws_wafv2_web_acl.main.arn
  }
```

## Layer 2: Network Security

```yaml
# ✅ Network Defense (Segmentation)

Security Groups (Stateful Firewall):

  # ✅ ALB Security Group (Internet-facing)
  resource "aws_security_group" "alb" {
    name = "alb-sg"

    ingress {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]  # HTTPS from internet
    }

    egress {
      from_port       = 5000
      to_port         = 5000
      protocol        = "tcp"
      security_groups = [aws_security_group.app.id]  # Only to app instances
    }
  }

  # ✅ Application Security Group (Private)
  resource "aws_security_group" "app" {
    name = "app-sg"

    ingress {
      from_port       = 5000
      to_port         = 5000
      protocol        = "tcp"
      security_groups = [aws_security_group.alb.id]  # Only from ALB
    }

    egress {
      from_port       = 5432
      to_port         = 5432
      protocol        = "tcp"
      security_groups = [aws_security_group.db.id]  # Only to database
    }

    egress {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]  # HTTPS to internet (for external APIs)
    }
  }

  # ✅ Database Security Group (Isolated)
  resource "aws_security_group" "db" {
    name = "db-sg"

    ingress {
      from_port       = 5432
      to_port         = 5432
      protocol        = "tcp"
      security_groups = [aws_security_group.app.id]  # Only from app instances
    }

    egress {
      # No egress rules (database doesn't initiate connections)
    }
  }

Network ACLs (Stateless Firewall, Backup Layer):

  resource "aws_network_acl" "private" {
    vpc_id     = aws_vpc.main.id
    subnet_ids = aws_subnet.private[*].id

    # ✅ Allow inbound from VPC CIDR only
    ingress {
      rule_no    = 100
      protocol   = "tcp"
      action     = "allow"
      cidr_block = "10.0.0.0/16"
      from_port  = 0
      to_port    = 65535
    }

    # ✅ Deny all other inbound
    ingress {
      rule_no    = 200
      protocol   = "-1"
      action     = "deny"
      cidr_block = "0.0.0.0/0"
    }
  }

VPC Flow Logs (Network Monitoring):

  resource "aws_flow_log" "main" {
    vpc_id          = aws_vpc.main.id
    traffic_type    = "ALL"
    log_destination = aws_cloudwatch_log_group.vpc_flow_logs.arn

    # Logs all accepted/rejected traffic
  }

  # Alert on suspicious patterns
  resource "aws_cloudwatch_log_metric_filter" "ssh_from_internet" {
    name           = "SSHFromInternet"
    log_group_name = aws_cloudwatch_log_group.vpc_flow_logs.name
    pattern        = "[version, account, eni, source, destination, srcport, dstport=\"22\", protocol=\"6\", packets, bytes, windowstart, windowend, action=\"ACCEPT\", flowlogstatus]"

    metric_transformation {
      name      = "SSHFromInternet"
      namespace = "Security"
      value     = "1"
    }
  }

  resource "aws_cloudwatch_metric_alarm" "ssh_alert" {
    alarm_name          = "SSHFromInternet"
    comparison_operator = "GreaterThanThreshold"
    evaluation_periods  = 1
    metric_name         = "SSHFromInternet"
    namespace           = "Security"
    period              = 300
    statistic           = "Sum"
    threshold           = 0

    alarm_actions = [aws_sns_topic.security_alerts.arn]
  }
```

## Layer 3: Identity & Access Management

```yaml
# ✅ IAM Defense (Authentication & Authorization)

Authentication (Keycloak + MFA):

  # See [MFA Standard](./mfa.md) and [SSO Implementation](./sso-implementation.md)

  - Username + Password (something you know)
  - TOTP/SMS (something you have)
  - Optional: Biometric (something you are)

Authorization (RBAC + ABAC):

  # See [RBAC Standard](./rbac.md)

  services.AddAuthorization(options =>
  {
      // ✅ Role-Based
      options.AddPolicy("AdminOnly", policy =>
          policy.RequireRole("Admin"));

      // ✅ Attribute-Based
      options.AddPolicy("CanAccessOrder", policy =>
          policy.Requirements.Add(new OrderOwnershipRequirement()));
  });

  public class OrderOwnershipHandler : AuthorizationHandler<OrderOwnershipRequirement, Order>
  {
      protected override Task HandleRequirementAsync(
          AuthorizationHandlerContext context,
          OrderOwnershipRequirement requirement,
          Order order)
      {
          var userId = context.User.FindFirst("sub")?.Value;

          // ✅ Users can only access their own orders
          if (order.CustomerId == userId)
              context.Succeed(requirement);

          // ✅ Admins can access all orders
          if (context.User.IsInRole("Admin"))
              context.Succeed(requirement);

          return Task.CompletedTask;
      }
  }

Least Privilege (IAM Roles):

  # ✅ ECS Task Role (minimal permissions)
  resource "aws_iam_role" "ecs_task" {
    name = "sales-service-task-role"

    assume_role_policy = jsonencode({
      Statement = [{
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }]
    })
  }

  resource "aws_iam_role_policy" "ecs_task" {
    role = aws_iam_role.ecs_task.id

    policy = jsonencode({
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "s3:GetObject",
            "s3:PutObject"
          ]
          Resource = "arn:aws:s3:::talma-invoices/*"  # ✅ Only specific bucket
        },
        {
          Effect = "Allow"
          Action = [
            "secretsmanager:GetSecretValue"
          ]
          Resource = "arn:aws:secretsmanager:*:*:secret:sales-service/*"  # ✅ Only own secrets
        },
        {
          Effect = "Deny"
          Action = [
            "iam:*",
            "s3:DeleteBucket",
            "rds:DeleteDBInstance"
          ]
          Resource = "*"  # ✅ Explicitly deny destructive actions
        }
      ]
    })
  }
```

## Layer 4: Application Security

```yaml
# ✅ Application Defense (Input Validation, Output Encoding)

Input Validation:

  public class CreateOrderRequest
  {
      [Required]
      [StringLength(50, MinimumLength = 1)]
      public string CustomerName { get; set; }

      [Required]
      [EmailAddress]
      public string Email { get; set; }

      [Range(1, 1000000)]
      public decimal Total { get; set; }

      [Required]
      [MinLength(1)]
      public List<OrderItem> Items { get; set; }
  }

  [HttpPost]
  public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
  {
      // ✅ ASP.NET automatically validates using attributes
      if (!ModelState.IsValid)
          return BadRequest(ModelState);

      // ✅ Additional business validation
      if (request.Items.Sum(i => i.Price * i.Quantity) != request.Total)
          return BadRequest("Total mismatch");

      // ✅ Sanitize input (remove SQL injection attempts)
      request.CustomerName = _sanitizer.Sanitize(request.CustomerName);

      var order = await _orderService.CreateAsync(request);
      return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
  }

SQL Injection Prevention:

  # ❌ VULNERABLE (string concatenation)
  var sql = $"SELECT * FROM orders WHERE customer_id = '{customerId}'";
  var orders = await _db.QueryAsync<Order>(sql);

  # ✅ SAFE (parameterized query)
  var sql = "SELECT * FROM orders WHERE customer_id = @customerId";
  var orders = await _db.QueryAsync<Order>(sql, new { customerId });

  # ✅ SAFE (Entity Framework)
  var orders = await _context.Orders
      .Where(o => o.CustomerId == customerId)
      .ToListAsync();

XSS Prevention:

  # ❌ VULNERABLE (render user input directly)
  <div>Welcome, <%= user.name %></div>

  # ✅ SAFE (HTML encode)
  <div>Welcome, <%= Html.Encode(user.name) %></div>

  # ✅ SAFE (Razor automatically encodes)
  <div>Welcome, @Model.Name</div>

HTTPS Enforcement:

  # Startup.cs
  app.UseHttpsRedirection();  // ✅ Redirect HTTP → HTTPS

  app.UseHsts();  // ✅ HTTP Strict Transport Security

  services.AddHsts(options =>
  {
      options.MaxAge = TimeSpan.FromDays(365);
      options.IncludeSubDomains = true;
      options.Preload = true;
  });

Security Headers:

  app.Use(async (context, next) =>
  {
      // ✅ Prevent clickjacking
      context.Response.Headers.Add("X-Frame-Options", "DENY");

      // ✅ Prevent MIME sniffing
      context.Response.Headers.Add("X-Content-Type-Options", "nosniff");

      // ✅ XSS protection
      context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");

      // ✅ Content Security Policy
      context.Response.Headers.Add("Content-Security-Policy",
          "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';");

      // ✅ Referrer Policy
      context.Response.Headers.Add("Referrer-Policy", "strict-origin-when-cross-origin");

      await next();
  });
```

## Layer 5: Data Security

```yaml
# ✅ Data Defense (Encryption, Masking)

Encryption at Rest:

  # See [Encryption at Rest Standard](./encryption-at-rest.md)

  RDS:
    storage_encrypted = true
    kms_key_id        = aws_kms_key.rds.arn

  S3:
    server_side_encryption_configuration {
      rule {
        apply_server_side_encryption_by_default {
          sse_algorithm     = "aws:kms"
          kms_master_key_id = aws_kms_key.s3.arn
        }
      }
    }

Encryption in Transit:

  # See [Encryption in Transit Standard](./encryption-in-transit.md)

  HTTPS: TLS 1.3
  Database: SSL/TLS connection
  Internal: mTLS between services

Data Masking:

  public class Order
  {
      public Guid Id { get; set; }

      [PersonalData]
      [JsonConverter(typeof(MaskingConverter))]
      public string CustomerName { get; set; }  // "John Doe" → "J*** D***"

      [PersonalData]
      [JsonConverter(typeof(MaskingConverter))]
      public string Email { get; set; }  // "john@example.com" → "j***@example.com"

      [CreditCard]
      [JsonConverter(typeof(MaskingConverter))]
      public string CreditCard { get; set; }  // "4111111111111111" → "************1111"
  }

  public class MaskingConverter : JsonConverter<string>
  {
      public override string Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
      {
          return reader.GetString();
      }

      public override void Write(Utf8JsonWriter writer, string value, JsonSerializerOptions options)
      {
          // ✅ Mask based on user role
          var user = _httpContextAccessor.HttpContext.User;

          if (user.IsInRole("Admin") || user.IsInRole("Auditor"))
          {
              writer.WriteStringValue(value);  // ✅ Full value for admins
          }
          else
          {
              writer.WriteStringValue(MaskString(value));  // ✅ Masked for regular users
          }
      }

      private string MaskString(string input)
      {
          if (string.IsNullOrEmpty(input) || input.Length < 4)
              return "****";

          return input.Substring(0, 1) + "***" + input.Substring(input.Length - 1);
      }
  }

Data Loss Prevention:

  # ✅ Prevent accidental exposure in logs

  _logger.LogInformation("Processing order {OrderId} for customer {CustomerId}",
      order.Id,
      order.CustomerId);  // ✅ Log IDs only

  # ❌ DON'T log sensitive data
  _logger.LogInformation("Order: {Order}", JsonSerializer.Serialize(order));  // ❌ Contains PII
```

## Layer 6: Monitoring & Detection

```yaml
# ✅ Detection Defense (Logging, Alerting, Anomaly Detection)

CloudWatch Logs (Centralized Logging):

  # Application logs
  _logger.LogWarning("Failed login attempt for user {UserId} from IP {IpAddress}",
      userId, ipAddress);

  # Security events
  _logger.LogError("Unauthorized access attempt to order {OrderId} by user {UserId}",
      orderId, userId);

CloudWatch Alarms (Threshold-Based):

  # Alert on high error rate
  resource "aws_cloudwatch_metric_alarm" "high_errors" {
    alarm_name          = "HighErrorRate"
    comparison_operator = "GreaterThanThreshold"
    evaluation_periods  = 2
    metric_name         = "5xxErrors"
    namespace           = "AWS/ApplicationELB"
    period              = 300
    statistic           = "Sum"
    threshold           = 50

    alarm_actions = [aws_sns_topic.alerts.arn]
  }

AWS GuardDuty (Threat Detection):

  resource "aws_guardduty_detector" "main" {
    enable = true

    # Monitors:
    # - VPC Flow Logs (suspicious traffic)
    # - CloudTrail (unusual API calls)
    # - DNS logs (command & control communication)
  }

  # Example findings:
  # - Backdoor:EC2/C&CActivity.B (EC2 querying malicious domain)
  # - UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration (credentials stolen)
  # - Recon:IAMUser/MaliciousIPCaller (API calls from known attacker IP)

AWS Security Hub (Centralized Security):

  resource "aws_securityhub_account" "main" {}

  resource "aws_securityhub_standards_subscription" "cis" {
    standards_arn = "arn:aws:securityhub:us-east-1::standards/cis-aws-foundations-benchmark/v/1.4.0"
  }

  # Aggregates findings from:
  # - GuardDuty
  # - Inspector
  # - Macie
  # - IAM Access Analyzer

Anomaly Detection:

  # CloudWatch Anomaly Detection (ML-based)
  resource "aws_cloudwatch_metric_alarm" "anomaly" {
    alarm_name          = "ApiCallAnomalyDetection"
    comparison_operator = "GreaterThanUpperThreshold"
    evaluation_periods  = 2
    threshold_metric_id = "e1"

    metric_query {
      id          = "e1"
      expression  = "ANOMALY_DETECTION_BAND(m1)"
      label       = "ApiCallCount (Expected)"
      return_data = true
    }

    metric_query {
      id = "m1"
      metric {
        metric_name = "ApiCallCount"
        namespace   = "CustomMetrics"
        period      = 300
        stat        = "Average"
      }
    }
  }
```

## Layer 7: Incident Response

```yaml
# ✅ Response Defense (Playbooks, Backups)

Incident Response Playbook:

  # Security breach detected

  1. Detect:
     - GuardDuty alerts "UnauthorizedAccess"
     - SNS notification to security team

  2. Contain:
     - Disable compromised IAM user
     - Revoke active sessions (force re-authentication)
     - Block attacker IP in WAF

     AWS CLI:
       aws iam delete-access-key --user-name compromised-user --access-key-id AKIA...
       aws wafv2 update-ip-set --id abc123 --addresses "1.2.3.4/32"

  3. Investigate:
     - Review CloudTrail logs (attacker actions)
     - Check data access logs (what was accessed?)
     - Identify attack vector (how did they get in?)

  4. Eradicate:
     - Patch vulnerability
     - Rotate all credentials
     - Update security groups

  5. Recover:
     - Restore from backup (if needed)
     - Re-enable services
     - Monitor for re-infection

  6. Post-Mortem:
     - Document incident (timeline, impact, root cause)
     - Update runbooks
     - Implement preventive measures

Automated Response (Lambda):

  import boto3

  def lambda_handler(event, context):
      # Triggered by GuardDuty finding

      finding = event['detail']
      finding_type = finding['type']

      if finding_type == "UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration":
          # ✅ Credentials stolen - disable user immediately
          iam = boto3.client('iam')
          user_name = finding['resource']['accessKeyDetails']['userName']
          access_key_id = finding['resource']['accessKeyDetails']['accessKeyId']

          # Disable access key
          iam.update_access_key(
              UserName=user_name,
              AccessKeyId=access_key_id,
              Status='Inactive'
          )

          # Send alert
          sns = boto3.client('sns')
          sns.publish(
              TopicArn='arn:aws:sns:us-east-1:123456789012:security',
              Subject='🚨 IAM Credentials Compromised',
              Message=f'User {user_name} access key {access_key_id} has been disabled due to potential compromise.'
          )

Backups (Recovery):

  # See [Disaster Recovery Standard](./disaster-recovery.md)

  RDS Automated Backups:
    backup_retention_period = 7  # 7 days of backups
    backup_window          = "03:00-04:00"  # Daily backup at 3 AM

  RDS Manual Snapshots:
    - Before major deployments
    - Before database migrations
    - Weekly (retained 30 days)

  Recovery Point Objective (RPO): 24 hours (daily backups)
  Recovery Time Objective (RTO): 1 hour (restore from snapshot)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** implementar al menos 5 capas de defensa (perimeter, network, IAM, application, data)
- **MUST** usar WAF en todos los ALBs públicos (SQL injection, XSS protection)
- **MUST** configurar Security Groups con least privilege (deny by default)
- **MUST** requerir autenticación + autorización en todas las APIs
- **MUST** validar todo input del usuario (whitelisting preferred)
- **MUST** usar parameterized queries (prevent SQL injection)
- **MUST** encriptar datos sensitivos at rest (KMS) and in transit (TLS)
- **MUST** habilitar CloudTrail + VPC Flow Logs (auditing)
- **MUST** tener incident response playbook documentado

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar AWS GuardDuty para threat detection
- **SHOULD** implementar automated incident response (Lambda)
- **SHOULD** hacer penetration testing anualmente
- **SHOULD** usar anomaly detection (CloudWatch ML)
- **SHOULD** implementar data masking (PII protection)

### MUST NOT (Prohibido)

- **MUST NOT** confiar en una sola capa de seguridad (defense in depth required)
- **MUST NOT** exponer database directamente a internet (always behind app layer)
- **MUST NOT** log sensitive data (passwords, credit cards, tokens)
- **MUST NOT** disable security controls "temporalmente" (always re-enable)

---

## Referencias

- [Security by Design](./security-by-design.md)
- [Network Segmentation](./network-segmentation.md)
- [MFA](./mfa.md)
- [RBAC](./rbac.md)
- [Encryption at Rest](./encryption-at-rest.md)
- [Encryption in Transit](./encryption-in-transit.md)
- [Incident Response](../operabilidad/incident-response.md)
