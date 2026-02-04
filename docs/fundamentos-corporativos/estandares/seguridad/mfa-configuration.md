---
id: mfa-configuration
sidebar_position: 13
title: Multi-Factor Authentication (MFA)
description: Estándar para implementar MFA con Keycloak usando TOTP (Google Authenticator) y WebAuthn (YubiKey), obligatorio para producción
---

# Estándar Técnico — Multi-Factor Authentication

---

## 1. Propósito

Implementar autenticación de múltiples factores (MFA) con Keycloak usando TOTP (Time-based One-Time Password) y WebAuthn (FIDO2), obligatorio para acceso a producción, opcional para dev/staging.

---

## 2. Alcance

**Aplica a:**

- Usuarios con acceso a producción (admins, ops)
- APIs administrativas
- Consolas de gestión
- Acceso SSH a servidores (fuera de alcance aquí)

**No aplica a:**

- APIs de servicio a servicio (usar service accounts)
- Usuarios finales (opcional, configurar por tenant)

---

## 3. Tecnologías Aprobadas

| Componente            | Tecnología                  | Versión mínima | Observaciones       |
| --------------------- | --------------------------- | -------------- | ------------------- |
| **Identity Provider** | Keycloak                    | 23.0+          | MFA integrado       |
| **TOTP**              | Google Authenticator, Authy | -              | RFC 6238            |
| **WebAuthn**          | YubiKey, Windows Hello      | -              | FIDO2               |
| **Backup Codes**      | Keycloak generados          | -              | One-time recovery   |
| **.NET Client**       | No requiere cambios         | -              | Keycloak maneja MFA |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

### MFA Obligatorio

- [ ] **Producción**: MFA obligatorio para todos los usuarios
- [ ] **Staging**: MFA opcional (recomendado para admins)
- [ ] **Dev**: MFA opcional
- [ ] **Admin console**: MFA siempre obligatorio

### Métodos Soportados

- [ ] **TOTP**: Google Authenticator, Authy (principal)
- [ ] **WebAuthn**: YubiKey, biométricos (alternativa)
- [ ] **Backup codes**: 10 códigos one-time generados
- [ ] **NO SMS**: No usar SMS por vulnerabilidades (SIM swapping)

### Políticas

- [ ] **Grace period**: 7 días para configurar MFA (usuarios nuevos)
- [ ] **Re-authentication**: Cada 8 horas en producción
- [ ] **Recovery**: Backup codes guardados de forma segura
- [ ] **Bypass**: Solo con aprobación CISO (emergencias)

---

## 5. Keycloak - Configurar MFA

### Habilitar TOTP

1. **Admin Console** → Realm `talma-internal`
2. **Authentication** → **Required Actions**
3. Habilitar: `Configure OTP` (Default Action)
4. **Authentication** → **Flows** → **Browser**
5. Editar flow:
   - Username Password Form (REQUIRED)
   - **OTP Form** (REQUIRED)

### Configurar OTP Policy

1. **Authentication** → **Policies** → **OTP Policy**
2. Configurar:
   - **OTP Type**: Time-based (TOTP)
   - **OTP Hash Algorithm**: SHA256
   - **Number of Digits**: 6
   - **Look Ahead Window**: 1
   - **OTP Token Period**: 30 segundos

### Habilitar WebAuthn

1. **Authentication** → **Required Actions**
2. Habilitar: `Webauthn Register`
3. **Authentication** → **Policies** → **WebAuthn Policy**
4. Configurar:
   - **Relying Party Entity Name**: Talma
   - **Signature Algorithms**: ES256, RS256
   - **Authenticator Attachment**: platform, cross-platform
   - **User Verification Requirement**: preferred

### Conditional MFA (Por Grupo)

```bash
# Keycloak Admin CLI

# Crear grupo "production-users"
kcadm.sh create groups -r talma-internal -s name=production-users

# Añadir usuario al grupo
kcadm.sh update users/{user-id}/groups/{group-id} -r talma-internal

# En Authentication Flow, configurar Conditional OTP:
# Condition - User in Group: production-users
# OTP Form: REQUIRED
```

---

## 6. Usuario - Configurar TOTP

### Proceso de Registro

1. **Login** primera vez → Keycloak redirige a configuración MFA
2. **Escanear QR** con Google Authenticator / Authy
3. **Ingresar código** de 6 dígitos para validar
4. **Guardar backup codes** (10 códigos one-time)
5. **Confirmar** configuración

### Google Authenticator

```text
otpauth://totp/Talma:user@example.com?secret=BASE32SECRET&issuer=Talma
```

### Backup Codes

Keycloak genera automáticamente 10 códigos:

```text
Backup Codes (usar solo una vez):

1. A1B2-C3D4-E5F6
2. G7H8-I9J0-K1L2
3. M3N4-O5P6-Q7R8
...

⚠️ Guardar en lugar seguro (Password Manager)
```

---

## 7. .NET - Integración (Transparente)

No requiere cambios en código .NET. Keycloak maneja MFA:

```csharp
// Program.cs - Configuración estándar
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.Authority = "https://auth.talma.com:8443/realms/talma-internal";
    options.Audience = "payment-api";
    // ...
});

// Keycloak valida MFA antes de emitir JWT
// JWT ya incluye información de MFA en claims
```

### Verificar MFA en JWT (Opcional)

```csharp
[Authorize]
[RequireMfa]  // Custom attribute
public class AdminController : ControllerBase
{
    // Solo accesible si usuario autenticó con MFA
}

// Attributes/RequireMfaAttribute.cs
public class RequireMfaAttribute : AuthorizeAttribute, IAuthorizationRequirement
{
}

public class RequireMfaHandler : AuthorizationHandler<RequireMfaAttribute>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        RequireMfaAttribute requirement)
    {
        var acrClaim = context.User.FindFirst("acr")?.Value;

        // ACR (Authentication Context Class Reference)
        // Keycloak set acr=1 si MFA fue usado
        if (acrClaim == "1" || acrClaim == "2")
        {
            context.Succeed(requirement);
        }
        else
        {
            context.Fail();
        }

        return Task.CompletedTask;
    }
}
```

---

## 8. WebAuthn - YubiKey

### Registro

1. **Login** → **Account Console** → **Signing In**
2. **Set up Security Key**
3. **Insertar YubiKey** y tocar botón
4. **Nombrar dispositivo**: "YubiKey 5 NFC"
5. **Confirmar** registro

### Login con YubiKey

1. **Ingresar username/password**
2. **Keycloak solicita MFA**
3. **Insertar YubiKey** y tocar
4. **Autenticado** ✅

---

## 9. Recuperación - Backup Codes

### Usar Backup Code

1. **Login** → Username/Password
2. **MFA prompt**: "Enter OTP"
3. **Clic**: "Use backup code"
4. **Ingresar código**: `A1B2-C3D4-E5F6`
5. **Código se invalida** (one-time use)

### Regenerar Backup Codes

1. **Account Console** → **Signing In**
2. **Backup Codes** → **Regenerate**
3. **Guardar nuevos códigos**

---

## 10. Bypass MFA (Emergencia)

### Procedimiento de Emergencia

```bash
# Solo con aprobación CISO
# Keycloak Admin CLI

# Deshabilitar MFA temporal para usuario
kcadm.sh update users/{user-id} -r talma-internal \
  -s 'requiredActions=["CONFIGURE_TOTP"]' \
  -s enabled=true

# Usuario debe re-configurar MFA en próximo login
```

⚠️ **Requiere:**

- Ticket de aprobación CISO
- Documentar en audit log
- Notificar al usuario
- Forzar re-configuración inmediata

---

## 11. Monitoring

### Métricas

```promql
# Usuarios sin MFA configurado
keycloak_users_without_mfa{realm="talma-internal"}

# Logins fallidos por MFA
rate(keycloak_login_failures{reason="invalid_otp"}[5m])

# Uso de backup codes
count_over_time({job="keycloak"} |= "backup code used" [24h])
```

### Alertas

```yaml
# Prometheus alert
- alert: MFANotConfiguredProduction
  expr: keycloak_users_without_mfa{environment="production"} > 0
  for: 24h
  annotations:
    summary: "Usuarios en producción sin MFA configurado"
```

---

## 12. Validación de Cumplimiento

```bash
# Verificar MFA habilitado en realm
kcadm.sh get authentication/required-actions -r talma-internal | jq '.[] | select(.alias=="CONFIGURE_TOTP")'

# Listar usuarios SIN MFA configurado
kcadm.sh get users -r talma-internal --fields id,username,totp | jq '.[] | select(.totp==false)'

# Verificar OTP policy
kcadm.sh get authentication/config/{config-id} -r talma-internal

# Contar logins con MFA en últimos 7 días
psql -h keycloak-db -U keycloak <<EOF
SELECT COUNT(*)
FROM event_entity
WHERE type = 'LOGIN'
  AND details_json->>'auth_method' = 'otp'
  AND event_time > NOW() - INTERVAL '7 days';
EOF
```

---

## 13. Referencias

**NIST:**

- [NIST 800-63B - Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)

**FIDO:**

- [FIDO2 WebAuthn](https://fidoalliance.org/fido2/)
- [WebAuthn Spec](https://www.w3.org/TR/webauthn-2/)

**Keycloak:**

- [Keycloak OTP Policies](https://www.keycloak.org/docs/latest/server_admin/#otp-policies)
- [Keycloak WebAuthn](https://www.keycloak.org/docs/latest/server_admin/#webauthn)
