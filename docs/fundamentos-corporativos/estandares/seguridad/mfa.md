---
id: mfa
sidebar_position: 6
title: Multi-Factor Authentication (MFA)
description: Autenticación de dos factores obligatoria con TOTP para proteger acceso a sistemas
---

# Multi-Factor Authentication (MFA)

## Contexto

Este estándar define **MFA (Multi-Factor Authentication)**: autenticación que requiere **dos o más factores de verificación** para acceder a sistemas. Contraseñas solas son insuficientes (phishing, robo, adivinación). MFA reduce exitosamente ataques de credenciales en **99.9%** (Microsoft). Complementa el [lineamiento de Identidad y Accesos](../../lineamientos/seguridad/05-identidad-y-accesos.md) agregando **segunda capa de protección**.

---

## Concepto Fundamental

```yaml
# Factores de Autenticación

Factor 1: Something you KNOW
  - Password
  - PIN
  - Security question

  ❌ Risk: Can be stolen (phishing), guessed (weak), shared

Factor 2: Something you HAVE
  - Mobile phone (SMS, push notification)
  - TOTP app (Google Authenticator, Authy)
  - Hardware token (YubiKey)
  - Smart card

  ✅ Benefit: Attacker needs physical device

Factor 3: Something you ARE (Biometric)
  - Fingerprint
  - Face recognition
  - Iris scan
  - Voice recognition

  ✅ Benefit: Can't be stolen (inherent to person)

# MFA = At least 2 different factors

Example Combinations:

1. Password + TOTP (✅ Most common):
   - User enters password (Factor 1: KNOW)
   - User enters 6-digit code from Google Authenticator (Factor 2: HAVE)
   - ✅ Two different factors

2. Password + SMS (⚠️ Acceptable but less secure):
   - User enters password (Factor 1: KNOW)
   - User receives SMS with code (Factor 2: HAVE phone)
   - ⚠️ SMS can be intercepted (SIM swap attack)

3. Password + Password (❌ NOT MFA):
   - User enters password (Factor 1: KNOW)
   - User enters another password (Factor 1: KNOW)
   - ❌ Same factor twice, NOT multi-factor

4. Fingerprint + Password (✅ Strong):
   - User scans fingerprint (Factor 3: ARE)
   - User enters password (Factor 1: KNOW)
   - ✅ Two different factors

5. Hardware Token (YubiKey) + PIN (✅ Strongest):
   - User inserts YubiKey (Factor 2: HAVE)
   - User enters PIN (Factor 1: KNOW)
   - ✅ Phishing-resistant
```

## TOTP Implementation (Recommended)

```yaml
# ✅ Time-based One-Time Password (TOTP)

Standard: RFC 6238
Algorithm: HMAC-SHA1 or SHA256
Code Length: 6 digits
Time Step: 30 seconds (code changes every 30s)
Tolerance: ±1 time step (allow previous/next code)

# How TOTP Works

Setup (One-time):

  1. Server generates secret key (random 160-bit)
     Secret: JBSWY3DPEHPK3PXP

  2. Server shows QR code to user
     URL: otpauth://totp/Talma:juan.perez@talma.com?secret=JBSWY3DPEHPK3PXP&issuer=Talma

  3. User scans QR with Google Authenticator
     App stores secret locally (encrypted)

  4. Server stores secret in database (encrypted)
     Table: user_mfa_secrets (user_id, secret_encrypted, enabled)

Login (Every time):

  1. User enters username + password → ✅ Verified

  2. Server checks: MFA enabled? → Yes

  3. Server prompts: "Enter 6-digit code from authenticator"

  4. User opens Google Authenticator
     App generates code using:
       - Secret key (stored locally)
       - Current time (Unix timestamp / 30)
       - HMAC-SHA1 algorithm

     Code: 123456

  5. User enters: 123456

  6. Server generates expected code:
     - Retrieves user's secret (decrypt)
     - Current time = 1706457600 (Unix timestamp)
     - Time step = 1706457600 / 30 = 56881920
     - HMAC-SHA1(secret, time_step) → 123456

  7. Server compares: User code == Expected code?
     - Also checks ±1 time step (clock drift tolerance)
     - If match → ✅ AUTHENTICATED
     - If no match → ❌ DENIED

Security:
  ✅ Phishing-resistant (code expires in 30s)
  ✅ Offline (no SMS, no internet needed)
  ✅ No SIM swap risk (not phone-based)
  ✅ Device-independent (backup codes available)
```

## Implementation (.NET)

```csharp
// ✅ TOTP MFA Implementation with Keycloak

// 1. Enable MFA for User

public class MfaService : IMfaService
{
    private readonly IKeycloakAdminClient _keycloak;
    private readonly IQRCodeGenerator _qrCode;

    public async Task<MfaSetupResponse> EnableMfaAsync(Guid userId)
    {
        // ✅ Generate secret (160-bit = 32 base32 chars)
        var secret = GenerateSecret();

        // ✅ Store secret in Keycloak user attributes
        await _keycloak.UpdateUserAttributesAsync(userId, new Dictionary<string, string>
        {
            ["mfa_secret"] = secret,
            ["mfa_enabled"] = "true"
        });

        // ✅ Generate QR code URL
        var user = await _keycloak.GetUserAsync(userId);
        var qrUrl = $"otpauth://totp/Talma:{user.Email}?secret={secret}&issuer=Talma&algorithm=SHA1&digits=6&period=30";

        // ✅ Generate QR code image
        var qrCodeImage = _qrCode.Generate(qrUrl);

        // ✅ Generate backup codes (10 single-use codes)
        var backupCodes = GenerateBackupCodes(10);
        await _keycloak.UpdateUserAttributesAsync(userId, new Dictionary<string, string>
        {
            ["mfa_backup_codes"] = JsonSerializer.Serialize(backupCodes.Select(c => Hash(c)))
        });

        return new MfaSetupResponse
        {
            Secret = secret,
            QrCodeImage = qrCodeImage,
            BackupCodes = backupCodes,
            ManualEntryKey = FormatSecretForManualEntry(secret) // "JBSW Y3DP EHPK 3PXP"
        };
    }

    private string GenerateSecret()
    {
        var bytes = new byte[20]; // 160 bits
        using var rng = RandomNumberGenerator.Create();
        rng.GetBytes(bytes);
        return Base32.Encode(bytes); // "JBSWY3DPEHPK3PXP"
    }

    private List<string> GenerateBackupCodes(int count)
    {
        var codes = new List<string>();
        for (int i = 0; i < count; i++)
        {
            var code = GenerateRandomCode(8); // 8 digits: 12345678
            codes.Add(code);
        }
        return codes;
    }
}

// 2. Verify TOTP Code

public class TotpVerifier : ITotpVerifier
{
    private const int TimeStepSeconds = 30;
    private const int CodeDigits = 6;
    private const int WindowSize = 1; // Check ±1 time step

    public async Task<bool> VerifyCodeAsync(Guid userId, string code)
    {
        // ✅ Retrieve user's secret
        var user = await _keycloak.GetUserAsync(userId);
        var secretBase32 = user.Attributes["mfa_secret"];
        var secretBytes = Base32.Decode(secretBase32);

        // ✅ Get current Unix timestamp
        var unixTimestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        var currentTimeStep = unixTimestamp / TimeStepSeconds;

        // ✅ Check current time step + window (±1)
        for (int i = -WindowSize; i <= WindowSize; i++)
        {
            var timeStep = currentTimeStep + i;
            var expectedCode = GenerateTotpCode(secretBytes, timeStep);

            if (expectedCode == code)
            {
                // ✅ Valid code
                await LogMfaSuccessAsync(userId);
                return true;
            }
        }

        // ❌ Invalid code, check backup codes
        if (await VerifyBackupCodeAsync(userId, code))
        {
            await LogMfaSuccessAsync(userId, isBackupCode: true);
            return true;
        }

        await LogMfaFailureAsync(userId, code);
        return false;
    }

    private string GenerateTotpCode(byte[] secret, long timeStep)
    {
        // ✅ Convert time step to byte array (big-endian)
        var timeBytes = BitConverter.GetBytes(timeStep);
        if (BitConverter.IsLittleEndian)
            Array.Reverse(timeBytes);

        // ✅ HMAC-SHA1
        using var hmac = new HMACSHA1(secret);
        var hash = hmac.ComputeHash(timeBytes);

        // ✅ Dynamic truncation (RFC 6238)
        var offset = hash[hash.Length - 1] & 0x0F;
        var binaryCode = ((hash[offset] & 0x7F) << 24)
                       | ((hash[offset + 1] & 0xFF) << 16)
                       | ((hash[offset + 2] & 0xFF) << 8)
                       | (hash[offset + 3] & 0xFF);

        // ✅ Generate 6-digit code
        var code = binaryCode % (int)Math.Pow(10, CodeDigits);
        return code.ToString($"D{CodeDigits}"); // "123456"
    }

    private async Task<bool> VerifyBackupCodeAsync(Guid userId, string code)
    {
        var user = await _keycloak.GetUserAsync(userId);
        var backupCodesJson = user.Attributes["mfa_backup_codes"];
        var backupCodesHashed = JsonSerializer.Deserialize<List<string>>(backupCodesJson);

        var codeHash = Hash(code);

        if (backupCodesHashed.Contains(codeHash))
        {
            // ✅ Valid backup code, remove it (single-use)
            backupCodesHashed.Remove(codeHash);
            await _keycloak.UpdateUserAttributesAsync(userId, new Dictionary<string, string>
            {
                ["mfa_backup_codes"] = JsonSerializer.Serialize(backupCodesHashed)
            });
            return true;
        }

        return false;
    }
}

// 3. Middleware (Enforce MFA)

public class MfaMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context, IKeycloakClient keycloak)
    {
        if (!context.User.Identity?.IsAuthenticated ?? false)
        {
            await _next(context);
            return;
        }

        var userId = context.User.GetUserId();
        var user = await keycloak.GetUserAsync(userId);

        // ✅ Check if MFA required
        var mfaEnabled = user.Attributes.TryGetValue("mfa_enabled", out var enabled)
            && enabled == "true";

        var mfaVerified = context.Session.GetString("mfa_verified") == "true";

        if (mfaEnabled && !mfaVerified)
        {
            // ✅ Redirect to MFA verification page
            context.Response.Redirect("/auth/mfa-verify");
            return;
        }

        await _next(context);
    }
}
```

## Keycloak MFA Configuration

```yaml
# ✅ Keycloak OTP Policy Configuration

Realm Settings → Authentication → OTP Policy:

  Supported Applications:
    - ✅ FreeOTP
    - ✅ Google Authenticator
    - ✅ Microsoft Authenticator

  OTP Type: Time-based (TOTP)

  OTP Hash Algorithm: SHA256 (recommended, more secure than SHA1)

  Number of Digits: 6

  Look Ahead Window: 1
    (Accept codes from ±1 time step = ±30 seconds)

  OTP Token Period: 30 seconds

# Required Actions

Authentication → Required Actions:

  ✅ Configure OTP
    - User Action: CONFIGURE_TOTP
    - Enabled: true
    - Default Action: false (don't force on login, admin enables per-user)

# Authentication Flow

Authentication → Flows → Browser Flow:

  Step 1: Cookie (check existing session)
    Alternative: Username/Password

  Step 2: OTP Form (if MFA enrolled)
    Required: true
    Requirement: CONDITIONAL (only if user has MFA enabled)

# Conditional Flows

Create "MFA Required for Admin" subflow:

  Condition: User in Role "admin"
  Execution: OTP Form (REQUIRED)

Result:
  - Regular users: Password only
  - Admin users: Password + MFA (enforced)
```

## SMS OTP (Alternative, Less Secure)

```csharp
// ⚠️ SMS OTP (acceptable but less secure than TOTP)

public class SmsOtpService : ISmsOtpService
{
    private readonly ITwilioClient _twilio;
    private readonly IRedisCache _cache;

    public async Task SendOtpAsync(string phoneNumber)
    {
        // ✅ Generate 6-digit code
        var code = GenerateRandomCode(6); // "123456"

        // ✅ Store in Redis (5 min expiry)
        var key = $"sms_otp:{phoneNumber}";
        await _cache.SetAsync(key, code, TimeSpan.FromMinutes(5));

        // ✅ Send SMS via Twilio
        await _twilio.SendSmsAsync(phoneNumber, $"Your Talma verification code: {code}. Valid for 5 minutes.");

        // ✅ Rate limit (max 3 SMS per hour)
        await _cache.IncrementAsync($"sms_rate:{phoneNumber}", TimeSpan.FromHours(1));
    }

    public async Task<bool> VerifyOtpAsync(string phoneNumber, string code)
    {
        // ✅ Retrieve stored code
        var key = $"sms_otp:{phoneNumber}";
        var storedCode = await _cache.GetAsync(key);

        if (storedCode == null)
            return false; // Expired or not sent

        if (storedCode != code)
        {
            // ❌ Invalid code
            await LogMfaFailureAsync(phoneNumber, code);
            return false;
        }

        // ✅ Valid code, delete it (single-use)
        await _cache.DeleteAsync(key);
        await LogMfaSuccessAsync(phoneNumber);
        return true;
    }
}

// ⚠️ SMS Security Risks

Vulnerabilities:
  1. SIM Swap Attack:
     - Attacker convinces carrier to transfer number to new SIM
     - Attacker receives SMS codes
     - Mitigation: Use TOTP instead, or verify identity before SIM swap

  2. SS7 Protocol Vulnerability:
     - Telecom protocol allows SMS interception
     - Nation-state attacks
     - Mitigation: Use TOTP (not network-based)

  3. SMS Delivery Delay:
     - Code may arrive after expiry
     - User frustration
     - Mitigation: Longer expiry (5 min)

Recommendation: Use SMS only as fallback, prefer TOTP
```

## Backup Codes

```yaml
# ✅ Backup Codes (Device Lost Recovery)

Purpose:
  - User loses phone with authenticator app
  - Can still access account using backup code

Generation:
  - 10 single-use codes
  - 8-10 characters alphanumeric
  - Example: "A3F7-2B9D", "7K2P-9XM4"

Storage:
  - Hashed (like passwords)
  - Stored in database per user
  - Cannot be retrieved, only validated

Usage:
  1. User tries to login → MFA prompt
  2. User doesn't have phone → "Use backup code"
  3. User enters backup code → Verified
  4. Code is deleted (single-use)
  5. User re-enables MFA on new device

Display:
  - Show codes only ONCE during MFA setup
  - User must save securely (password manager, print)
  - Warning: "Save these codes, you won't see them again"
```

## Enforcement by Role

```yaml
# ✅ MFA Policy by User Role

Configuration:

  Role: admin, platform-engineer, security-engineer
    MFA: REQUIRED (cannot be disabled)
    Method: TOTP (Authenticator app)
    Grace Period: None (enforce immediately)

  Role: developer, qa-engineer
    MFA: RECOMMENDED (prompt to enable)
    Method: TOTP or SMS
    Grace Period: 30 days (then enforce)

  Role: business-user, read-only
    MFA: OPTIONAL (user choice)
    Method: Any
    Grace Period: N/A

Implementation (Keycloak):

  Authentication → Flows → Create "MFA for Admins":

    Condition: User has role "admin"
    Execution: OTP Form (REQUIRED)

  Authentication → Flows → Create "MFA Recommended":

    Condition: User in role "developer"
    Execution: OTP Form (CONDITIONAL)
    + Show banner: "Enable MFA for better security"

# Production Access

Policy: Production access REQUIRES MFA

  - Deploy to production → MFA verified in last 1 hour
  - SSH to bastion → MFA verified
  - AWS Console production account → MFA required
  - Database admin access → MFA required

Enforcement:
  - IAM policy condition: "aws:MultiFactorAuthPresent": "true"
  - GitHub branch protection: MFA required for merge to main
  - VPN access: MFA required (Duo, Okta)
```

## Monitoring

```yaml
# ✅ MFA Metrics & Alerts

Metrics:

  MFA Enrollment Rate:
    - Total users with MFA enabled / Total users
    - Target: > 80%
    - Alert: < 60% (low adoption)

  MFA Verification Failures:
    - Failed MFA attempts per day
    - Alert: > 10 failures from same user (brute force)

  MFA Bypass Attempts:
    - Users trying to disable MFA without verification
    - Alert: Any attempt (investigate)

CloudWatch Logs:

  Filter Pattern: "MFA_FAILURE"

  fields @timestamp, userId, attemptedCode, ipAddress
  | filter event == "MFA_FAILURE"
  | stats count() by userId
  | sort count desc
  # Alert if same user > 5 failures (account compromise?)

Alerts:

  - MFA disabled for admin user → CRITICAL (manual approval required)
  - MFA verification failure rate > 5% → Investigate (UX issue?)
  - Backup code used → INFO (user lost device, verify identity)
```

---

## Requisitos Técnicos

### MUST (Obligatorio)

- **MUST** requerir MFA para roles admin/platform-engineer
- **MUST** usar TOTP con apps estándar (Google Authenticator, Authy)
- **MUST** proveer backup codes (10 single-use)
- **MUST** almacenar secrets encryptados (not plain text)
- **MUST** usar time window ±1 step (clock drift tolerance)
- **MUST** rate limit intentos (max 5 per 15 min)

### SHOULD (Fuertemente recomendado)

- **SHOULD** usar SHA256 hash algorithm (not SHA1)
- **SHOULD** enforce MFA para production access
- **SHOULD** proveer QR code + manual entry (accessibility)
- **SHOULD** permitir múltiples dispositivos (phone + tablet)

### MUST NOT (Prohibido)

- **MUST NOT** usar SMS como único factor (SIM swap risk)
- **MUST NOT** permitir admin sin MFA
- **MUST NOT** almacenar TOTP secrets sin encryptar
- **MUST NOT** reusar backup codes (must be single-use)

---

## Referencias

- [Lineamiento: Identidad y Accesos](../../lineamientos/seguridad/05-identidad-y-accesos.md)
- [SSO Implementation](./sso-implementation.md)
- [Password Policies](./password-policies.md)
- [Identity Lifecycle](./identity-lifecycle.md)
- [RFC 6238 - TOTP](https://datatracker.ietf.org/doc/html/rfc6238)
