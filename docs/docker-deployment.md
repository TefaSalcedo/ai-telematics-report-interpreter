# Docker y Despliegue

## 🐳 Guía Completa de Docker

Esta guía cubre todo lo necesario para trabajar con Docker en el proyecto AI Telematics Fleet Management System.

---

## 📋 Requisitos Previos

### Software Necesario
- **Docker Desktop** 4.0+ (Windows/Mac) o **Docker Engine** 20.10+ (Linux)
- **Docker Compose** 2.0+
- **Git** para control de versiones
- **Mínimo 4GB RAM** para desarrollo
- **Mínimo 8GB RAM** para producción

### Verificar Instalación
```bash
# Verificar Docker
docker --version
docker run hello-world

# Verificar Docker Compose
docker-compose --version

# Verificar sistema
docker system info
```

---

## 🏗️ Arquitectura Docker

### Servicios Definidos

```yaml
# docker-compose.yml
services:
  # Frontend Web (React + Next.js)
  frontend:
    build: ./frontend
    ports: ["3001:3000"]
    depends_on: [backend]
    
  # Backend API (FastAPI)
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    
  # MCP Analyzer (CLI Analysis)
  mcp-analyzer:
    build: ./mcp
    command: ["data/sample_report.json"]
    
  # MCP Server (LLM Integration)
  mcp-server:
    build: ./mcp
    entrypoint: ["python", "-m", "src.mcp_server"]
    
  # MCP Tests
  mcp-tests:
    build: ./mcp
    entrypoint: ["python", "-m", "pytest"]
```

### Flujo de Red
```
Internet → Frontend (3001) → Backend (8000)
                ↓
         MCP Services (internal)
```

---

## 🐘 Dockerfiles Detallados

### Frontend Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS base

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS production
WORKDIR /app

COPY --from=base /app/public ./public
COPY --from=base /app/.next/standalone ./
COPY --from=base /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
```

### Backend Dockerfile
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### MCP Dockerfile
```dockerfile
# mcp/Dockerfile
FROM python:3.12-slim AS base

LABEL maintainer="Fleet Telemetry Team"
LABEL description="Fleet telemetry analysis MCP server and CLI tool"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY data/ data/
COPY tests/ tests/

# Create output directory
RUN mkdir -p /app/output

# Default: run CLI analysis on sample data
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["data/sample_report.json"]
```

---

## 🚀 Comandos Docker Esenciales

### Desarrollo

#### Levantar Todos los Servicios
```bash
# Construir y levantar
docker-compose up --build

# Levantar en background
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Logs de servicio específico
docker-compose logs -f frontend
docker-compose logs -f backend
```

#### Reconstrucción
```bash
# Reconstruir imágenes específicas
docker-compose build frontend
docker-compose build backend
docker-compose build mcp

# Reconstruir sin cache
docker-compose build --no-cache

# Forzar reconstrucción
docker-compose build --pull --no-cache
```

#### Gestión de Servicios
```bash
# Detener servicios
docker-compose down

# Detener y remover volúmenes
docker-compose down -v

# Reiniciar servicios específicos
docker-compose restart backend

# Escalar servicios
docker-compose up -d --scale backend=2
```

### Producción

#### Despliegue Producción
```bash
# Usar archivo de producción
docker-compose -f docker-compose.prod.yml up -d

# Con health checks
docker-compose -f docker-compose.prod.yml up -d --health-timeout 30s

# Verificar estado
docker-compose ps
```

#### Monitoreo
```bash
# Ver uso de recursos
docker stats

# Inspeccionar contenedor
docker inspect ai-telematics-backend

# Ver procesos en contenedor
docker-compose exec backend ps aux
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

#### .env File
```bash
# .env
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development

# Backend
DEBUG=false
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3001

# MCP
MCP_LOG_LEVEL=info
MCP_CACHE_ENABLED=true
```

#### docker-compose.override.yml (Desarrollo)
```yaml
version: "3.9"

services:
  frontend:
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    environment:
      - CHOKIDAR_USEPOLLING=true
      - WATCHPACK_POLLING=true
    
  backend:
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
    
  mcp-analyzer:
    volumes:
      - ./mcp/data:/app/data
      - ./mcp/output:/app/output
```

#### docker-compose.prod.yml (Producción)
```yaml
version: "3.9"

services:
  frontend:
    environment:
      - REACT_APP_ENV=production
    restart: unless-stopped
    
  backend:
    environment:
      - DEBUG=false
      - LOG_LEVEL=info
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Optimización de Imágenes

#### Multi-stage Builds
```dockerfile
# Ejemplo de optimización
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
CMD ["npm", "start"]
```

#### .dockerignore Files
```
# frontend/.dockerignore
node_modules
.next
.git
.gitignore
README.md
Dockerfile
.dockerignore

# backend/.dockerignore
__pycache__
*.pyc
.pytest_cache
.venv
venv
.git
.gitignore

# mcp/.dockerignore
__pycache__
*.pyc
.pytest_cache
.venv
venv
.git
.gitignore
output/
```

---

## 📊 Monitoring y Logging

### Configuración de Logs

#### Structured Logging
```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service,environment"
```

#### Centralized Logging (Opcional)
```yaml
# Con ELK Stack
version: "3.9"
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
      
  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
```

### Health Checks

#### Health Check Personalizado
```dockerfile
# Backend Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" \
    || exit 1
```

#### Health Check en docker-compose
```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 🔒 Seguridad en Docker

### Best Practices de Seguridad

#### 1. Usar Non-Root Users
```dockerfile
# Crear usuario no root
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app
```

#### 2. Imágenes Base Minimalistas
```dockerfile
# Usar imágenes Alpine o Slim
FROM python:3.12-slim  # En lugar de python:3.12
FROM node:20-alpine    # En lugar de node:20
```

#### 3. Secrets Management
```bash
# Usar Docker secrets (en Swarm)
echo "your_api_key" | docker secret create groq_api_key -

# En docker-compose
services:
  backend:
    secrets:
      - groq_api_key
secrets:
  groq_api_key:
    external: true
```

#### 4. Network Security
```yaml
# Redes aisladas
networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge
    internal: true
    
services:
  frontend:
    networks:
      - frontend-network
      - backend-network
    
  backend:
    networks:
      - backend-network
```

### Escaneo de Seguridad

#### Trivy (Vulnerability Scanner)
```bash
# Instalar Trivy
brew install trivy

# Escanear imágenes
trivy image ai-telematics-frontend:latest
trivy image ai-telematics-backend:latest
trivy image ai-telematics-mcp:latest
```

#### Docker Bench Security
```bash
# Ejecutar Docker Bench
docker run -it --net host --pid host --userns host --cap-add audit_control \
    -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
    -v /etc:/etc:ro \
    -v /usr/bin/containerd:/usr/bin/containerd:ro \
    -v /usr/bin/runc:/usr/bin/runc:ro \
    -v /usr/lib/systemd:/usr/lib/systemd:ro \
    -v /var/lib:/var/lib:ro \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    --label docker_bench_security \
    docker/docker-bench-security
```

---

## 🚀 Despliegue en Producción

### Opción 1: Single Host (Docker Compose)

#### Preparación del Servidor
```bash
# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Configurar firewall
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

#### Despliegue
```bash
# Clonar repositorio
git clone <repository-url>
cd ai-mini

# Configurar variables de entorno
cp .env.example .env
# Editar .env con valores de producción

# Desplegar
docker-compose -f docker-compose.prod.yml up -d

# Verificar
docker-compose ps
curl http://localhost:8000/health
```

### Opción 2: Cloud Deployment

#### AWS ECS
```yaml
# ecs-task-definition.json
{
  "family": "ai-telematics",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ai-telematics-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GROQ_API_KEY",
          "value": "your-api-key"
        }
      ]
    }
  ]
}
```

#### Google Cloud Run
```bash
# Construir y push a GCR
gcloud builds submit --tag gcr.io/project-id/ai-telematics-backend

# Desplegar en Cloud Run
gcloud run deploy ai-telematics-backend \
  --image gcr.io/project-id/ai-telematics-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Opción 3: Kubernetes

#### Kubernetes Manifests
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-telematics

---
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ai-telematics
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ai-telematics-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: groq-api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
# k8s/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: ai-telematics
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

---

## 📈 Performance y Optimización

### Resource Limits

#### Configuración de Recursos
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

#### Monitoreo de Recursos
```bash
# Ver uso en tiempo real
docker stats --no-stream

# Ver histórico
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Optimización de Build

#### Build Cache
```bash
# Usar BuildKit para mejor cache
DOCKER_BUILDKIT=1 docker-compose build

# Ver cache usage
docker builder df
```

#### Parallel Builds
```bash
# Construir en paralelo
docker-compose build --parallel
```

---

## 🐛 Troubleshooting Docker

### Problemas Comunes

#### 1. Contenedor No Inicia
```bash
# Ver logs
docker-compose logs service-name

# Entrar al contenedor
docker-compose exec service-name bash

# Verificar configuración
docker-compose config
```

#### 2. Puertos en Conflicto
```bash
# Ver puertos en uso
netstat -tulpn | grep :8000
lsof -i :8000

# Cambiar puertos en docker-compose.yml
ports:
  - "8001:8000"  # Usar puerto diferente
```

#### 3. Problemas de Red
```bash
# Ver redes Docker
docker network ls

# Inspeccionar red
docker network inspect ai-mini_default

# Test connectivity
docker-compose exec frontend ping backend
```

#### 4. Issues de Permisos
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Verificar Docker daemon
sudo systemctl status docker
```

### Debugging Avanzado

#### Inspección de Contenedores
```bash
# Ver detalles del contenedor
docker inspect ai-telematics-backend

# Ver procesos
docker-compose exec backend ps aux

# Ver variables de entorno
docker-compose exec backend env
```

#### Performance Analysis
```bash
# Ver uso de disco
docker system df

# Limpiar sistema
docker system prune -a

# Ver imágenes no usadas
docker images -f "dangling=true"
```

---

## 🔄 CI/CD con Docker

### GitHub Actions

#### Build y Push
```yaml
# .github/workflows/docker.yml
name: Build and Push Docker Images

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push backend
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/ai-telematics-backend:latest
    
    - name: Build and push frontend
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/ai-telematics-frontend:latest
```

### Automated Testing

#### Tests en Docker
```yaml
# docker-compose.test.yml
version: "3.9"
services:
  backend-test:
    build: ./backend
    command: pytest
    environment:
      - TESTING=true
    
  frontend-test:
    build: ./frontend
    command: npm test
```

```bash
# Ejecutar tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## 📚 Referencias y Recursos

### Documentación Oficial
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Herramientas Útiles
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Portainer](https://www.portainer.io/) - Web UI for Docker
- [Lazydocker](https://github.com/jesseduffield/lazydocker) - Terminal UI

### Community
- [Docker Community Forums](https://forums.docker.com/)
- [r/docker](https://reddit.com/r/docker)
- [Docker Stack Overflow](https://stackoverflow.com/questions/tagged/docker)
