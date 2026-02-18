---
id: secrets-management
sidebar_position: 3
title: Secrets Management
description: Gestión segura de secretos - credenciales, API keys, tokens sin hardcoding
---

# Secrets Management

## Contexto

Este estándar define **Secrets Management**: almacenamiento y acceso seguro de **credenciales sensibles** (passwords, API keys, tokens, certificates). **NUNCA** en código fuente, variables de entorno estáticas o archivos de configuración. Usa servicios dedicados con encriptación, auditoría y rotación automática. Complementa [Encryption at Rest](../seguridad/encryption-at-rest.md) y [Least Privilege](../seguridad/rbac.md).

---

## Concepto Fundamental

```yaml
# ✅ Secrets Management

What is a Secret?

  - Database passwords (PostgreSQL, Redis)
  - API keys (Stripe, SendGrid, Google Maps)
  - OAuth tokens (GitHub, Google, Facebook)
  - Encryption keys (AES keys, JWT signing keys)
  - TLS certificates (private keys)
  - Service account credentials (AWS access keys)

❌ BAD: Secrets in Code

  public class PaymentService
  {
      private const string StripeApiKey = "sk_live_abc123xyz";  // ❌ NEVER DO THIS

      public async Task ProcessPayment(decimal amount)
      {
          var stripe = new StripeClient(StripeApiKey);
          // ...
      }
  }

  Risks:
    - Exposed in Git history (forever)
    - Visible in code reviews (multiple people see)
    - Visible in CI/CD logs (pipeline outputs)
    - Difficult to rotate (requires code change + deployment)

❌ BAD: Secrets in appsettings.json

  {
    "ConnectionStrings": {
      "DefaultConnection": "Host=db.talma.com;Username=admin;Password=P@ssw0rd123"  // ❌ NEVER
    },
    "Stripe": {
      "ApiKey": "sk_live_abc123xyz"  // ❌ NEVER
    }
  }

  Risks:
    - Committed to Git
    - Different per environment (dev/qa/prod) → Multiple files → Confusing
    - No audit trail (who accessed secret?)

✅ GOOD: Secrets in AWS Secrets Manager

  {
    "ConnectionStrings": {
      "DefaultConnection": "{{resolve:secretsmanager:sales-service/db-connection}}"
    },
    "Stripe": {
      "ApiKey": "{{resolve:secretsmanager:sales-service/stripe-api-key}}"
    }
  }

  Benefits:
    ✅ Encrypted at rest (KMS)
    ✅ Encrypted in transit (TLS)
    ✅ Audit trail (CloudTrail logs)
    ✅ Automatic rotation (password changes every 30 days)
    ✅ Access control (IAM policies)
    ✅ Versioning (rollback if needed)
```

## AWS Secrets Manager

```yaml
# ✅ AWS Secrets Manager (Preferred for Production)

Create Secret (Terraform):

  resource "aws_secretsmanager_secret" "db_password" {
    name        = "sales-service/db-password"
    description = "PostgreSQL password for Sales Service"

    # ✅ Automatic rotation every 30 days
    rotation_rules {
      automatically_after_days = 30
    }
  }

  resource "aws_secretsmanager_secret_version" "db_password" {
    secret_id     = aws_secretsmanager_secret.db_password.id
    secret_string = random_password.db_password.result  # Generate random password
  }

  resource "aws_secretsmanager_secret_rotation" "db_password" {
    secret_id           = aws_secretsmanager_secret.db_password.id
    rotation_lambda_arn = aws_lambda_function.rotate_db_password.arn

    rotation_rules {
      automatically_after_days = 30
    }
  }

Retrieve Secret (.NET):

  using Amazon.SecretsManager;
  using Amazon.SecretsManager.Model;

  public class SecretService
  {
      private readonly IAmazonSecretsManager _secretsManager;
      private readonly IMemoryCache _cache;

      public async Task<string> GetSecretAsync(string secretName)
      {
          // ✅ Check cache first (avoid repeated API calls)
          if (_cache.TryGetValue(secretName, out string cachedSecret))
              return cachedSecret;

          // ✅ Retrieve from AWS Secrets Manager
          var request = new GetSecretValueRequest
          {
              SecretId = secretName
          };

          var response = await _secretsManager.GetSecretValueAsync(request);

          var secret = response.SecretString;

          // ✅ Cache for 5 minutes (balance between freshness and API calls)
          _cache.Set(secretName, secret, TimeSpan.FromMinutes(5));

          return secret;
      }
  }

  // Usage
  var dbPassword = await _secretService.GetSecretAsync("sales-service/db-password");
  var connectionString = $"Host=db.talma.com;Username=postgres;Password={dbPassword}";

Retrieve Secret (Startup):

  public class Startup
  {
      public void ConfigureServices(IServiceCollection services)
      {
          // ✅ Load secrets at startup
          var secretService = new SecretService(
              new AmazonSecretsManagerClient(),
              new MemoryCache(new MemoryCacheOptions())
          );

          var dbPassword = secretService.GetSecretAsync("sales-service/db-password").Result;
          var stripeApiKey = secretService.GetSecretAsync("sales-service/stripe-api-key").Result;

          services.AddDbContext<SalesDbContext>(options =>
              options.UseNpgsql($"Host=db.talma.com;Username=postgres;Password={dbPassword}")
          );

          services.AddSingleton(new StripeClient(stripeApiKey));
      }
  }

IAM Policy (Least Privilege):

  resource "aws_iam_role_policy" "ecs_task_secrets" {
    role = aws_iam_role.ecs_task.id

    policy = jsonencode({
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "secretsmanager:GetSecretValue",
            "secretsmanager:DescribeSecret"
          ]
          Resource = [
            "arn:aws:secretsmanager:us-east-1:123456789012:secret:sales-service/*"
          ]
        },
        {
          Effect = "Deny"
          Action = [
            "secretsmanager:DeleteSecret",
            "secretsmanager:PutSecretValue"
          ]
          Resource = "*"  # ✅ Application cannot modify/delete secrets
        }
      ]
    })
  }
```

## AWS Systems Manager Parameter Store

```yaml
# ✅ Parameter Store (Alternative for Non-Secret Config)

When to Use:

  Secrets Manager: Sensitive data (passwords, API keys) with auto-rotation
  Parameter Store: Non-sensitive config (URLs, feature flags) without rotation

Create Parameter (Terraform):

  resource "aws_ssm_parameter" "api_url" {
    name  = "/sales-service/api-url"
    type  = "String"
    value = "https://api.talma.com"
  }

  resource "aws_ssm_parameter" "db_password" {
    name  = "/sales-service/db-password"
    type  = "SecureString"  # ✅ Encrypted with KMS
    value = random_password.db_password.result

    key_id = aws_kms_key.ssm.id  # ✅ Custom KMS key
  }

Retrieve Parameter (.NET):

  using Amazon.SimpleSystemsManagement;
  using Amazon.SimpleSystemsManagement.Model;

  public class ParameterStoreService
  {
      private readonly IAmazonSimpleSystemsManagement _ssmClient;

      public async Task<string> GetParameterAsync(string name, bool decrypt = true)
      {
          var request = new GetParameterRequest
          {
              Name = name,
              WithDecryption = decrypt  # ✅ Decrypt SecureString
          };

          var response = await _ssmClient.GetParameterAsync(request);
          return response.Parameter.Value;
      }
  }

Cost Comparison:

  Secrets Manager:
    - Cost: $0.40 per secret per month + $0.05 per 10,000 API calls
    - Features: Auto-rotation, cross-region replication, versioning
    - Use for: Passwords, API keys, tokens

  Parameter Store (Standard):
    - Cost: Free
    - Features: Basic KMS encryption, versioning
    - Limits: Max 10,000 parameters
    - Use for: Non-sensitive config

  Parameter Store (Advanced):
    - Cost: $0.05 per parameter per month
    - Features: Higher limits, parameter policies, change notifications
```

## Secret Rotation

```yaml
# ✅ Automatic Secret Rotation

Database Password Rotation (Lambda):

  import boto3
  import psycopg2
  import os

  secrets_manager = boto3.client('secretsmanager')

  def lambda_handler(event, context):
      """
      Rotate RDS PostgreSQL password

      Steps:
        1. Create new password
        2. Update database with new password
        3. Update secret in Secrets Manager
        4. Verify applications can connect with new password
      """

      secret_arn = event['SecretId']
      token = event['ClientRequestToken']
      step = event['Step']

      # Get current secret
      current_secret = secrets_manager.get_secret_value(SecretId=secret_arn)
      current_creds = json.loads(current_secret['SecretString'])

      if step == 'createSecret':
          # ✅ Generate new password
          new_password = generate_random_password(32)

          secrets_manager.put_secret_value(
              SecretId=secret_arn,
              SecretString=json.dumps({
                  'username': current_creds['username'],
                  'password': new_password,
                  'host': current_creds['host'],
                  'port': current_creds['port'],
                  'dbname': current_creds['dbname']
              }),
              VersionStages=['AWSPENDING'],
              ClientRequestToken=token
          )

      elif step == 'setSecret':
          # ✅ Update database with new password
          pending_secret = secrets_manager.get_secret_value(
              SecretId=secret_arn,
              VersionStage='AWSPENDING'
          )
          pending_creds = json.loads(pending_secret['SecretString'])

          # Connect with current (old) password
          conn = psycopg2.connect(
              host=current_creds['host'],
              port=current_creds['port'],
              user=current_creds['username'],
              password=current_creds['password'],
              dbname=current_creds['dbname']
          )

          # Update password
          cursor = conn.cursor()
          cursor.execute(f"ALTER USER {current_creds['username']} PASSWORD '{pending_creds['password']}';")
          conn.commit()
          conn.close()

      elif step == 'testSecret':
          # ✅ Test new password works
          pending_secret = secrets_manager.get_secret_value(
              SecretId=secret_arn,
              VersionStage='AWSPENDING'
          )
          pending_creds = json.loads(pending_secret['SecretString'])

          conn = psycopg2.connect(
              host=pending_creds['host'],
              port=pending_creds['port'],
              user=pending_creds['username'],
              password=pending_creds['password'],
              dbname=pending_creds['dbname']
          )
          conn.close()

      elif step == 'finishSecret':
          # ✅ Promote new password to AWSCURRENT
          secrets_manager.update_secret_version_stage(
              SecretId=secret_arn,
              VersionStage='AWSCURRENT',
              MoveToVersionId=token,
              RemoveFromVersionId=current_secret['VersionId']
          )

  def generate_random_password(length):
      import string
      import secrets

      alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
      return ''.join(secrets.choice(alphabet) for _ in range(length))

Rotation Schedule:

  Passwords: Every 30 days
  API Keys: Every 90 days (coordinate with vendor)
  TLS Certificates: Every 365 days (or before expiry)
  Encryption Keys: Every 180 days

Zero-Downtime Rotation Strategy:

  1. Multi-Version Support:
     - Applications support both old and new credentials simultaneously
     - Use credential caching with short TTL (5 minutes)

  2. Gradual Rollout:
     - t0: Old password active (AWSCURRENT)
     - t1: New password created (AWSPENDING)
     - t2: Database updated, both passwords valid
     - t3: Applications refresh cache, start using new password
     - t4: After 5 minutes, all apps using new password
     - t5: New password promoted (AWSCURRENT), old password deprecated

  3. Rollback:
     - If new password fails validation, keep old password as AWSCURRENT
     - Alert operations team for manual intervention
```

## Environment Variables (Anti-Pattern)

```yaml
# ⚠️ Environment Variables (Use with Caution)

Acceptable Use Cases:

  1. Local Development (Never Production):

     # .env (NOT committed to Git)
     DATABASE_URL=postgres://postgres:postgres@localhost:5432/sales
     STRIPE_API_KEY=sk_test_abc123  # ✅ Test key only

     # .gitignore
     .env

  2. CI/CD Pipelines (GitHub Actions Secrets):

     # .github/workflows/deploy.yml
     - name: Deploy
       env:
         AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
         AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
       run: |
         aws ecs update-service ...

     ✅ GitHub Secrets are encrypted
     ✅ Not visible in logs (masked)

❌ Production Anti-Patterns:

  1. Plain Text Environment Variables (ECS Task Definition):

     # ❌ DON'T DO THIS
     {
       "environment": [
         {
           "name": "DATABASE_PASSWORD",
           "value": "P@ssw0rd123"  # ❌ Visible in console, API calls, CloudTrail
         }
       ]
     }

  2. Dockerfile ENV (Baked into Image):

     # ❌ DON'T DO THIS
     FROM mcr.microsoft.com/dotnet/aspnet:8.0
     ENV STRIPE_API_KEY=sk_live_abc123  # ❌ In image layers, anyone with image access sees it

  3. Kubernetes ConfigMap (Plain Text):

     # ❌ DON'T DO THIS
     apiVersion: v1
     kind: ConfigMap
     data:
       database-password: "P@ssw0rd123"  # ❌ Stored unencrypted in etcd

✅ Production Patterns:

  1. ECS Task Definition (Secrets Manager Reference):

     {
       "secrets": [
         {
           "name": "DATABASE_PASSWORD",
           "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:sales-service/db-password"
         }
       ]
     }

     ✅ Fetched at container startup
     ✅ Injected as environment variable (in-memory only)
     ✅ Not visible in console/API

  2. Kubernetes Secret (Encrypted):

     apiVersion: v1
     kind: Secret
     type: Opaque
     metadata:
       name: db-password
     data:
       password: <base64-encoded>  # ✅ Encrypted at rest in etcd

     # Reference in Pod
     env:
       - name: DATABASE_PASSWORD
         valueFrom:
           secretKeyRef:
             name: db-password
             key: password
```

## Auditing & Monitoring

```yaml
# ✅ Secrets Access Auditing

CloudTrail (Who Accessed What):

  # Log all Secrets Manager API calls
  resource "aws_cloudtrail" "secrets_audit" {
    name           = "secrets-audit-trail"
    s3_bucket_name = aws_s3_bucket.cloudtrail.id

    event_selector {
      read_write_type           = "All"
      include_management_events = true

      data_resource {
        type   = "AWS::SecretsManager::Secret"
        values = ["arn:aws:secretsmanager:*:*:secret:*"]
      }
    }
  }

  # Query who accessed secret
  aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=ResourceName,AttributeValue=sales-service/db-password \
    --start-time 2024-01-28T00:00:00Z

  # Result
  {
    "EventName": "GetSecretValue",
    "Username": "sales-service-task-role",
    "EventTime": "2024-01-28T12:34:56Z",
    "Resources": [
      {
        "ResourceName": "sales-service/db-password"
      }
    ]
  }

CloudWatch Alarms (Suspicious Activity):

  # Alert on GetSecretValue from unexpected IAM roles
  resource "aws_cloudwatch_log_metric_filter" "unauthorized_secret_access" {
    name           = "UnauthorizedSecretAccess"
    log_group_name = aws_cloudwatch_log_group.cloudtrail.name
    pattern        = "{ ($.eventName = GetSecretValue) && ($.errorCode = AccessDenied) }"

    metric_transformation {
      name      = "UnauthorizedSecretAccess"
      namespace = "Security"
      value     = "1"
    }
  }

  resource "aws_cloudwatch_metric_alarm" "unauthorized_secret_access" {
    alarm_name          = "UnauthorizedSecretAccess"
    comparison_operator = "GreaterThanThreshold"
    evaluation_periods  = 1
    metric_name         = "UnauthorizedSecretAccess"
    namespace           = "Security"
    period              = 300
    statistic           = "Sum"
    threshold           = 0

    alarm_actions = [aws_sns_topic.security_alerts.arn]
  }

Secret Expiration Monitoring:

  # Alert 30 days before TLS certificate expires
  resource "aws_cloudwatch_event_rule" "cert_expiry" {
    name                = "certificate-expiry-warning"
    schedule_expression = "rate(1 day)"
  }

  resource "aws_cloudwatch_event_target" "cert_expiry" {
    rule      = aws_cloudwatch_event_rule.cert_expiry.name
    target_id = "CheckCertificateExpiry"
    arn       = aws_lambda_function.check_cert_expiry.arn
  }

  # Lambda checks cert expiry date
  def lambda_handler(event, context):
      secrets = secrets_manager.list_secrets()

      for secret in secrets:
          if 'tls-certificate' in secret['Name']:
              cert_data = secrets_manager.get_secret_value(SecretId=secret['ARN'])
              cert = x509.load_pem_x509_certificate(cert_data.encode())

              days_until_expiry = (cert.not_valid_after - datetime.now()).days

              if days_until_expiry < 30:
                  sns.publish(
                      TopicArn='arn:aws:sns:us-east-1:123456789012:security',
                      Subject=f'⚠️ Certificate Expiring Soon',
                      Message=f'Certificate {secret["Name"]} expires in {days_until_expiry} days'
                  )
```

## Development Workflow

```yaml
# ✅ Secrets in Development vs Production

Local Development:

  # Use .env file (NOT committed)
  DATABASE_URL=postgres://postgres:postgres@localhost:5432/sales_dev
  STRIPE_API_KEY=sk_test_abc123  # ✅ Test API key

  # Load in application
  DotNetEnv.Env.Load();  # NuGet: DotNetEnv
  var dbUrl = Environment.GetEnvironmentVariable("DATABASE_URL");

CI/CD (GitHub Actions):

  # Store in GitHub Secrets (Settings → Secrets)

  # .github/workflows/test.yml
  - name: Run Tests
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
      STRIPE_API_KEY: ${{ secrets.STRIPE_API_KEY }}
    run: dotnet test

QA/Staging:

  # Use AWS Secrets Manager (non-production account)
  aws secretsmanager create-secret \
    --name sales-service/db-password \
    --secret-string "QAP@ssw0rd456" \
    --region us-east-1 \
    --profile qa

Production:

  # Use AWS Secrets Manager (production account)
  aws secretsmanager create-secret \
    --name sales-service/db-password \
    --secret-string "ProdP@ssw0rd789SecureRandom" \
    --region us-east-1 \
    --profile prod \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/production-kms

  # Enable automatic rotation
  aws secretsmanager rotate-secret \
    --secret-id sales-service/db-password \
    --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:RotateDBPassword \
    --rotation-rules AutomaticallyAfterDays=30
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** usar AWS Secrets Manager para passwords, API keys, tokens en producción
- **MUST** usar KMS encryption para secrets at rest
- **MUST** rotar database passwords cada 30 días (automatic rotation)
- **MUST** usar IAM roles con least privilege (read-only for applications)
- **MUST** habilitar CloudTrail para auditar secret access
- **MUST** NEVER commit secrets a Git (use .gitignore for .env)
- **MUST** usar different secrets por environment (dev/qa/prod)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar secret caching (5-minute TTL, reduce API calls)
- **SHOULD** monitorear unauthorized access attempts (CloudWatch alarms)
- **SHOULD** generar random passwords (min 32 characters, mixed case + numbers + symbols)
- **SHOULD** usar ECS task definition secrets (not environment variables)
- **SHOULD** alert 30 days before certificate expiry

### MUST NOT (Prohibido)

- **MUST NOT** commit secrets to Git (code, config files, Dockerfiles)
- **MUST NOT** log secrets (sanitize logs, redact sensitive data)
- **MUST NOT** use plain text environment variables en ECS/Kubernetes
- **MUST NOT** hardcode secrets in code ("const ApiKey = ...")
- **MUST NOT** share secrets via email, Slack, wikis (use Secrets Manager + IAM)

---

## Referencias

- [Encryption at Rest](../seguridad/encryption-at-rest.md)
- [RBAC](../seguridad/rbac.md)
- [Least Privilege](../seguridad/rbac.md)
- [ADR-003: AWS Secrets Manager](../../decisiones-de-arquitectura/adr-003-aws-secrets-manager.md)
- [Infrastructure as Code](./infrastructure-as-code.md)
