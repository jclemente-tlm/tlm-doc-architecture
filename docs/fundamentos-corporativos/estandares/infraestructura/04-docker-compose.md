---
id: docker-compose
sidebar_position: 4
title: Docker Compose
description: Estándar para orquestar entornos multi-contenedor en desarrollo local con Docker Compose.
---

# Estándar: Docker Compose

## 1. Propósito

Establecer las mejores prácticas para usar **Docker Compose** en entornos de desarrollo local, facilitando la orquestación de aplicaciones multi-contenedor con configuraciones reproducibles y mantenibles.

## 2. Alcance

- Entornos de desarrollo local y CI/CD
- Orquestación de múltiples servicios (API, BD, cache, colas)
- Configuración de redes, volúmenes y variables de entorno
- Sincronización de código local con contenedores

## 3. Principios

### 3.1 Separación de Entornos

```yaml
# docker-compose.yml - Base para desarrollo
# docker-compose.override.yml - Configuración local (auto-merge)
# docker-compose.ci.yml - Para CI/CD
# docker-compose.prod.yml - Referencia (NO usar en producción)
```

### 3.2 Nomenclatura de Servicios

```yaml
services:
  # Patrón: {proyecto}-{servicio}-{tipo}
  talma-users-api: # API de usuarios
  talma-users-db: # Base de datos
  talma-redis-cache: # Cache compartido
  talma-rabbitmq: # Message broker
```

### 3.3 Uso de Variables de Entorno

```yaml
# .env (NO versionarlo - solo .env.example)
POSTGRES_VERSION=16
POSTGRES_PASSWORD=dev_password_123
REDIS_VERSION=7
API_PORT=5000
```

## 4. Configuración Base

### 4.1 Archivo Principal: docker-compose.yml

```yaml
version: "3.9"

services:
  # API Backend
  api:
    build:
      context: ./src/API
      dockerfile: Dockerfile
      target: development # Multi-stage build
    container_name: talma-users-api
    ports:
      - "${API_PORT:-5000}:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__Default=Host=db;Database=talma_users;Username=postgres;Password=${POSTGRES_PASSWORD}
      - Redis__ConnectionString=cache:6379
      - RabbitMQ__Host=rabbitmq
    volumes:
      - ./src/API:/app # Hot reload
      - /app/bin # Exclude bin
      - /app/obj # Exclude obj
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
      rabbitmq:
        condition: service_healthy
    networks:
      - talma-network
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:${POSTGRES_VERSION:-16}-alpine
    container_name: talma-users-db
    environment:
      - POSTGRES_DB=talma_users
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - talma-network
    restart: unless-stopped

  # Redis Cache
  cache:
    image: redis:${REDIS_VERSION:-7}-alpine
    container_name: talma-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    networks:
      - talma-network
    restart: unless-stopped

  # RabbitMQ
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: talma-rabbitmq
    ports:
      - "5672:5672" # AMQP
      - "15672:15672" # Management UI
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD:-admin123}
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    healthcheck:
      test: rabbitmq-diagnostics -q ping
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - talma-network
    restart: unless-stopped

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  rabbitmq-data:
    driver: local

networks:
  talma-network:
    driver: bridge
```

### 4.2 Override para Desarrollo Local

**docker-compose.override.yml** (auto-merge con docker-compose.yml):

```yaml
version: "3.9"

services:
  api:
    build:
      args:
        - CONFIGURATION=Debug
    environment:
      - ASPNETCORE_URLS=http://+:8080
      - Logging__LogLevel__Default=Debug
    # Hot reload habilitado por volúmenes en base

  db:
    ports:
      - "5433:5432" # Puerto diferente para evitar conflictos locales

  # Servicio adicional solo en local
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: talma-pgadmin
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@talma.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "8081:80"
    depends_on:
      - db
    networks:
      - talma-network
```

### 4.3 Configuración para CI/CD

**docker-compose.ci.yml**:

```yaml
version: "3.9"

services:
  api:
    build:
      target: test # Stage específico para tests
    environment:
      - ASPNETCORE_ENVIRONMENT=Testing
      - ConnectionStrings__Default=Host=db;Database=talma_test;Username=postgres;Password=test_password
    depends_on:
      db:
        condition: service_healthy

  db:
    environment:
      - POSTGRES_DB=talma_test
      - POSTGRES_PASSWORD=test_password
    # Sin puertos expuestos en CI
    ports: []
```

**Uso en pipeline**:

```bash
docker-compose -f docker-compose.yml -f docker-compose.ci.yml up --build --abort-on-container-exit
```

## 5. Mejores Prácticas

### 5.1 Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s # Tiempo inicial antes de checks
```

### 5.2 Depends On con Condiciones

```yaml
depends_on:
  db:
    condition: service_healthy # Espera a que DB esté healthy
  cache:
    condition: service_started # Solo espera a que inicie
```

### 5.3 Volúmenes Nombrados vs Bind Mounts

```yaml
volumes:
  # Named volume - Datos persistentes gestionados por Docker
  - postgres-data:/var/lib/postgresql/data

  # Bind mount - Hot reload desde código local
  - ./src/API:/app

  # Anonymous volume - Excluir directorios específicos
  - /app/bin
  - /app/obj
```

### 5.4 Redes Personalizadas

```yaml
networks:
  # Red para backend services
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

  # Red para frontend
  frontend:
    driver: bridge
```

### 5.5 Recursos y Límites

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
        reservations:
          cpus: "0.25"
          memory: 256M
```

## 6. Comandos Esenciales

### 6.1 Desarrollo Diario

```bash
# Iniciar servicios en background
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f api

# Rebuild después de cambios en Dockerfile
docker-compose up --build

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (reset completo)
docker-compose down -v
```

### 6.2 Debugging

```bash
# Ejecutar comando en contenedor corriendo
docker-compose exec api bash

# Ver estado de servicios
docker-compose ps

# Inspeccionar configuración final (con merges)
docker-compose config

# Reiniciar un servicio específico
docker-compose restart api
```

### 6.3 Cleanup

```bash
# Eliminar contenedores, redes, imágenes anónimas
docker-compose down --rmi local

# Limpiar todo el sistema Docker
docker system prune -a --volumes
```

## 7. Multi-Stage Builds con Compose

### 7.1 Dockerfile Multi-Stage

```dockerfile
# Dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["API.csproj", "./"]
RUN dotnet restore
COPY . .
RUN dotnet build -c Release -o /app/build

# Stage de desarrollo (hot reload)
FROM build AS development
WORKDIR /app
ENTRYPOINT ["dotnet", "watch", "run"]

# Stage de test
FROM build AS test
WORKDIR /src
RUN dotnet test --logger trx --results-directory /testresults

# Stage de producción
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS production
WORKDIR /app
COPY --from=build /app/build .
ENTRYPOINT ["dotnet", "API.dll"]
```

### 7.2 Compose Targeting Stages

```yaml
services:
  api:
    build:
      context: ./src/API
      target: development # Cambia según entorno
```

## 8. Perfiles para Servicios Opcionales

```yaml
services:
  # Servicio principal - siempre activo
  api:
    # ...

  # Servicio opcional - solo con profile
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
    profiles:
      - observability # Solo se inicia con: docker-compose --profile observability up

  monitoring:
    image: prom/prometheus:latest
    profiles:
      - observability
```

**Uso**:

```bash
# Solo servicios sin profile
docker-compose up

# Con profile específico
docker-compose --profile observability up
```

## 9. Ejemplo Completo: Microservicios

**docker-compose.yml**:

```yaml
version: "3.9"

services:
  # API Gateway
  gateway:
    build: ./services/gateway
    ports:
      - "8080:8080"
    environment:
      - SERVICES_USERS=http://users-api:8080
      - SERVICES_ORDERS=http://orders-api:8080
    depends_on:
      - users-api
      - orders-api
    networks:
      - talma-network

  # Users Microservice
  users-api:
    build: ./services/users
    environment:
      - DATABASE_URL=postgresql://db:5432/users
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
    networks:
      - talma-network

  # Orders Microservice
  orders-api:
    build: ./services/orders
    environment:
      - DATABASE_URL=postgresql://db:5432/orders
      - KAFKA_BROKERS=kafka:9092
    depends_on:
      - db
      - kafka
    networks:
      - talma-network

  # Shared Database
  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=talma
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U talma"]
      interval: 10s
    networks:
      - talma-network

  # Shared Cache
  cache:
    image: redis:7-alpine
    networks:
      - talma-network

  # Message Broker
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
    depends_on:
      - zookeeper
    networks:
      - talma-network

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      - ZOOKEEPER_CLIENT_PORT=2181
    networks:
      - talma-network

volumes:
  db-data:

networks:
  talma-network:
    driver: bridge
```

## 10. Integración con Makefile

**Makefile**:

```makefile
.PHONY: up down logs restart clean test

up:
 docker-compose up -d

down:
 docker-compose down

logs:
 docker-compose logs -f

restart:
 docker-compose restart

clean:
 docker-compose down -v --rmi local

test:
 docker-compose -f docker-compose.yml -f docker-compose.ci.yml up --abort-on-container-exit

rebuild:
 docker-compose up --build -d

shell-api:
 docker-compose exec api bash

db-migrate:
 docker-compose exec api dotnet ef database update
```

**Uso**:

```bash
make up
make logs
make test
```

## 11. Troubleshooting

### 11.1 Problemas Comunes

| Problema                           | Solución                                                    |
| ---------------------------------- | ----------------------------------------------------------- |
| Puerto ya en uso                   | Cambiar puerto en `.env` o en `docker-compose.override.yml` |
| Volúmenes con permisos incorrectos | Verificar UID/GID en Dockerfile con `user: "${UID}:${GID}"` |
| Hot reload no funciona             | Verificar bind mounts y reiniciar contenedor                |
| Health check falla                 | Aumentar `start_period` o verificar comando de health check |
| Variables de entorno no se cargan  | Verificar `.env` existe y sintaxis correcta                 |

### 11.2 Debugging de Configuración

```bash
# Ver configuración final después de merge
docker-compose config

# Validar sintaxis YAML
docker-compose config -q

# Ver variables interpoladas
docker-compose config --resolve-image-digests
```

## 12. NO Hacer

❌ **NO** usar Docker Compose en producción (usar Kubernetes, ECS, etc.)
❌ **NO** versionar `.env` con credenciales reales
❌ **NO** usar `network_mode: host` (rompe aislamiento)
❌ **NO** exponer todos los puertos innecesariamente
❌ **NO** usar volúmenes anónimos para datos críticos
❌ **NO** omitir health checks en servicios críticos
❌ **NO** usar `latest` tag sin version pinning en `.env`

## 13. Referencias

### Documentación Oficial

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose File Specification](https://docs.docker.com/compose/compose-file/)
- [Compose CLI Reference](https://docs.docker.com/compose/reference/)

### Lineamientos Relacionados

- [Lineamiento Arq. 03: Diseño Cloud Native](../../lineamientos/arquitectura/03-diseno-cloud-native.md)
- [Lineamiento Op. 02: Infraestructura como Código](../../lineamientos/operaciones/02-infraestructura-como-codigo.md)

### Otros Estándares

- [Docker](./01-docker.md) - Construcción de imágenes
- [Infraestructura como Código](./02-infraestructura-como-codigo.md) - Terraform, AWS CDK
- [Testing](../testing/01-unit-integration-tests.md) - Tests en contenedores
