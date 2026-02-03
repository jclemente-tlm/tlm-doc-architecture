---
id: docker-compose
sidebar_position: 4
title: Docker Compose
description: Estándar técnico obligatorio para orquestación multi-contenedor en desarrollo local con Docker Compose, health checks, volúmenes y networks
---

# Estándar Técnico — Docker Compose

---

## 1. Propósito

Garantizar entornos de desarrollo idénticos entre equipos mediante Docker Compose v2.20+ (formato v3.9), separación de entornos con override files, health checks, volúmenes nombrados y onboarding `<10` min.

---

## 2. Alcance

**Aplica a:**

- Desarrollo local multi-contenedor (API + DB + Cache + Broker)
- CI/CD pipelines para testing automatizado
- Hot reload de código durante desarrollo

**No aplica a:**

- Producción (usar AWS ECS/Fargate)
- Staging/Pre-producción (usar orquestadores cloud)
- Contenedores standalone simples (usar `docker run`)

---

## 3. Tecnologías Aprobadas

| Componente        | Tecnología                 | Versión mínima | Observaciones                             |
| ----------------- | -------------------------- | -------------- | ----------------------------------------- |
| **Compose**       | Docker Compose             | 2.20+          | Orquestación declarativa multi-contenedor |
| **Formato**       | Compose file format        | 3.9            | Compatible Docker Engine 19.03+           |
| **Variables**     | .env files + ${VAR}        | -              | Configuración por entorno                 |
| **Networks**      | Bridge driver              | -              | Aislamiento de servicios                  |
| **Volúmenes**     | Named volumes, bind mounts | -              | Persistencia y hot reload                 |
| **Health Checks** | healthcheck directive      | -              | Dependencias confiables                   |

> El uso de tecnologías no listadas requiere aprobación de Arquitectura.

---

## 4. Requisitos Obligatorios 🔴

- [ ] Formato v3.9 (version: "3.9")
- [ ] Archivo base `docker-compose.yml` versionado
- [ ] Override file `docker-compose.override.yml` NO versionado
- [ ] Variables en `.env` (NO versionado), template en `.env.example` (versionado)
- [ ] Health checks configurados para todos los servicios con dependencies
- [ ] Named volumes para persistencia de datos
- [ ] Networks aisladas por stack
- [ ] Nomenclatura servicios: `{proyecto}-{servicio}-{tipo}`
- [ ] `depends_on` con `condition: service_healthy`
- [ ] Restart policy: `restart: unless-stopped` en desarrollo
- [ ] Resource limits (memory, cpu) configurados
- [ ] Ports expuestos solo los necesarios

---

## 5. Prohibiciones

- ❌ Usar Docker Compose en producción
- ❌ Versionar archivo `.env` con secretos
- ❌ Hardcodear secrets en docker-compose.yml
- ❌ `depends_on` sin health checks (unsafe)
- ❌ Bind mounts absolutos (usar paths relativos)
- ❌ Servicios sin resource limits

---

## 6. Configuración Mínima

```yaml
# docker-compose.yml (BASE - versionado)
version: "3.9"

services:
  api:
    build: .
    ports:
      - "${API_PORT:-5000}:5000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgres://user:${POSTGRES_PASSWORD}@db:5432/appdb
    networks:
      - app-network
    restart: unless-stopped

  db:
    image: postgres:${POSTGRES_VERSION:-16}-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:${REDIS_VERSION:-7}-alpine
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
    networks:
      - app-network

volumes:
  postgres-data:
  redis-data:

networks:
  app-network:
    driver: bridge
```

```bash
# .env.example (VERSIONADO - template)
POSTGRES_VERSION=16
POSTGRES_PASSWORD=change_me_in_local_env
REDIS_VERSION=7
API_PORT=5000

# .env (NO VERSIONADO - valores reales locales)
POSTGRES_VERSION=16
POSTGRES_PASSWORD=dev_password_secure_123
REDIS_VERSION=7
API_PORT=5000
```

---

## 7. Validación

```bash
# Validar sintaxis
docker-compose config

# Verificar health checks
docker-compose ps

# Logs de servicios
docker-compose logs -f api

# Verificar networks
docker network ls | grep app-network

# Verificar volúmenes
docker volume ls | grep postgres-data

# Tiempo de inicio (debe ser <2 min)
time docker-compose up -d

# Cleanup
docker-compose down -v
```

**Métricas de cumplimiento:**

| Métrica                      | Target   | Verificación                              |
| ---------------------------- | -------- | ----------------------------------------- |
| Tiempo onboarding            | < 10 min | `time docker-compose up -d` < 2min        |
| Health checks pasando        | 100%     | `docker-compose ps` all healthy           |
| Secrets en repo              | 0        | `.env` en .gitignore                      |
| Services con resource limits | 100%     | `docker-compose config \| grep -c limits` |

Incumplimientos deben corregirse o documentarse mediante excepción aprobada.

---

## 8. Referencias

- [Docker](./01-docker.md)
- [Gestión de Secretos](./03-secrets-management.md)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose file version 3 reference](https://docs.docker.com/compose/compose-file/compose-file-v3/)
