---
id: seguridad-desde-el-diseno
sidebar_position: 4
title: Seguridad desde el Diseño
description: La seguridad debe ser una consideración fundamental desde las decisiones arquitectónicas iniciales, integrándose en la estructura del sistema mediante patrones y prácticas comprobadas.
---

# Seguridad desde el Diseño

## Declaración del Principio

**La seguridad debe ser una consideración explícita desde las decisiones arquitectónicas iniciales del sistema y no incorporarse posteriormente como controles aislados o correctivos.**

## Contexto

La seguridad como atributo de calidad es reconocida por todos los frameworks de arquitectura modernos (AWS, Azure, Google Cloud, ISO 25010) como un pilar fundamental. Un diseño seguro desde el inicio reduce significativamente:

- Superficie de ataque
- Costos de remediación
- Riesgos operacionales
- Impacto de incidentes de seguridad

Este principio está alineado con:

- **AWS Well-Architected**: Security Pillar
- **Azure Well-Architected**: Security Pillar
- **OWASP**: Secure by Design principles
- **NIST Cybersecurity Framework**: Protect function

## Fundamento

### Por Qué es Importante

Las decisiones arquitectónicas definen aspectos fundamentales del sistema:

- Qué componentes existen y cómo se relacionan
- Qué capacidades se exponen y a quién
- Cómo circulan los datos dentro y fuera del sistema
- Dónde se establecen los límites de confianza

Si estos elementos se diseñan sin considerar seguridad, los controles añadidos posteriormente solo mitigan síntomas y no las causas del riesgo, generando soluciones frágiles, costosas de mantener y difíciles de corregir.

### Aspectos Clave

1. **Límites de Confianza**: Definición explícita de zonas de confianza
2. **Superficie de Ataque**: Minimización por diseño
3. **Defensa en Profundidad**: Múltiples capas de protección
4. **Principio de Mínimo Privilegio**: Acceso restringido por defecto
5. **Seguridad por Defecto**: Configuraciones seguras desde el inicio

## Lineamientos que Implementan este Principio

Este principio fundamental se implementa a través de los siguientes lineamientos:

### 🔐 [Zero Trust](../../lineamientos/seguridad/06-zero-trust.md)

Modelo de seguridad que no confía en ningún actor por defecto, requiriendo verificación continua independientemente de la ubicación o contexto.

**Aplica cuando**: Diseñas arquitecturas distribuidas o con múltiples puntos de acceso

### 🛡️ [Defensa en Profundidad](../../lineamientos/seguridad/07-defensa-en-profundidad.md)

Estrategia que establece múltiples capas de controles de seguridad, de modo que si una falla, otras sigan protegiendo el sistema.

**Aplica cuando**: Proteges activos críticos o datos sensibles

### 🔑 [Mínimo Privilegio](../../lineamientos/seguridad/08-minimo-privilegio.md)

Práctica que asegura que cada usuario, componente o sistema opere con el nivel mínimo de privilegios necesario para su función.

**Aplica cuando**: Diseñas sistemas de identidad, acceso o autorización

### 👤 [Identidad y Accesos](../../lineamientos/seguridad/02-identidad-y-accesos.md)

Gestión centralizada y consistente de autenticación, autorización y control de acceso.

**Aplica cuando**: Implementas autenticación o control de acceso a recursos

## Implicaciones

### Para Equipos de Desarrollo

- **Threat Modeling**: Identificación temprana de amenazas y mitigaciones
- **Security Testing**: Pruebas de seguridad integradas en CI/CD
- **Secure Coding**: Prácticas de codificación segura (OWASP)
- **Dependency Management**: Análisis de vulnerabilidades en dependencias

### Para Arquitectura

- **Componentes críticos identificados**: Desde el diseño
- **Límites de confianza explícitos**: Documentados y validados
- **Exposición mínima**: Solo lo necesario
- **Segmentación de red**: Aislamiento de componentes
- **Cifrado**: En tránsito y en reposo

### Para el Negocio

- **Reducción de riesgos**: Menor probabilidad de incidentes
- **Cumplimiento normativo**: Facilita certificaciones y auditorías
- **Confianza del cliente**: Mayor credibilidad
- **Costos reducidos**: Menos remediación post-producción

## Ejemplos

### ✅ Cumple el Principio

```csharp
// API Gateway con autenticación y autorización desde el diseño
[Authorize(Policy = "RequireNotificationAccess")]
[ApiController]
[Route("api/notifications")]
public class NotificationsController : ControllerBase
{
    private readonly INotificationService _service;
    private readonly ICurrentUserService _currentUser;

    public NotificationsController(
        INotificationService service,
        ICurrentUserService currentUser)
    {
        _service = service;
        _currentUser = currentUser;
    }

    [HttpGet]
    public async Task<IActionResult> GetMyNotifications()
    {
        // Principio de mínimo privilegio: usuario solo ve sus propias notificaciones
        var userId = _currentUser.GetUserId();
        var notifications = await _service.GetByUserIdAsync(userId);

        return Ok(notifications);
    }

    [HttpPost]
    [Authorize(Roles = "Admin")]
    public async Task<IActionResult> SendBroadcast([FromBody] BroadcastRequest request)
    {
        // Segregación: solo admins pueden enviar broadcasts
        await _service.SendBroadcastAsync(request);
        return Ok();
    }
}
```

### ❌ Viola el Principio

```csharp
// Sin autenticación, sin autorización, sin validación
[ApiController]
[Route("api/notifications")]
public class NotificationsController : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        // PROBLEMA: Expone todas las notificaciones sin control de acceso
        var connString = ConfigurationManager.ConnectionStrings["Default"].ConnectionString;
        using var conn = new SqlConnection(connString);

        // PROBLEMA: SQL Injection vulnerable, credenciales elevadas
        var sql = $"SELECT * FROM Notifications WHERE UserId = '{Request.Query["userId"]}'";
        var notifications = await conn.QueryAsync(sql);

        return Ok(notifications);
    }
}
```

## Métricas de Éxito

### Indicadores Técnicos

- **Vulnerabilidades críticas**: = 0 en producción
- **Cobertura de autenticación**: 100% de endpoints protegidos
- **Secrets en código**: = 0 (usar secretos gestionados)
- **Tiempo de remediación**: < 24h para vulnerabilidades críticas

### Indicadores de Negocio

- **Incidentes de seguridad**: Tendencia decreciente
- **Auditorías exitosas**: > 95% cumplimiento
- **Tiempo de certificación**: Reducción año tras año
- **Costo de incidentes**: Tendencia decreciente

## Referencias

### Estándares de Industria

- [AWS Well-Architected Framework - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [Azure Well-Architected Framework - Security](https://learn.microsoft.com/azure/well-architected/security/)
- [OWASP Secure by Design](https://owasp.org/www-project-security-by-design-principles/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### Lineamientos Relacionados

- [Zero Trust](../../lineamientos/seguridad/06-zero-trust.md)
- [Defensa en Profundidad](../../lineamientos/seguridad/07-defensa-en-profundidad.md)
- [Mínimo Privilegio](../../lineamientos/seguridad/08-minimo-privilegio.md)
- [Identidad y Accesos](../../lineamientos/seguridad/02-identidad-y-accesos.md)
- [Protección de Datos](../../lineamientos/seguridad/04-proteccion-de-datos.md)

### ADRs Relacionados

- [ADR-004: Keycloak para SSO y Autenticación](../../../decisiones-de-arquitectura/adr-004-keycloak-sso-autenticacion.md)
- [ADR-003: AWS Secrets Manager](../../../decisiones-de-arquitectura/adr-003-aws-secrets-manager.md)

---

**Versión**: 1.0
**Última actualización**: 2026-02-11
**Estado**: Aprobado
