# Guía de Desarrollo

## 🚀 Configuración del Entorno de Desarrollo

### Requisitos Previos

#### Software Esencial
- **Docker Desktop** 4.0+ - Contenerización
- **Node.js** 18+ - Desarrollo frontend
- **Python** 3.10+ - Desarrollo backend/MCP
- **Git** - Control de versiones
- **VS Code** (recomendado) - IDE

#### Herramientas Adicionales
- **Postman/Insomnia** - Testing API
- **Docker Compose** - Orquestación
- **Python venv** - Entornos virtuales
- **npm/yarn** - Gestión de paquetes JS

### Configuración Inicial

#### 1. Clonar el Proyecto
```bash
git clone <repository-url>
cd ai-mini
```

#### 2. Configurar Variables de Entorno
```bash
# Backend API
cp backend/.env.example backend/.env
# Editar backend/.env con tu API key de Groq

# Frontend (opcional)
cp frontend/.env.example frontend/.env
```

#### 3. Levantar Servicios con Docker
```bash
# Construir y levantar todos los servicios
docker-compose up --build

# O levantar servicios individuales
docker-compose up -d backend frontend
```

## 🛠️ Desarrollo Local

### Opción 1: Desarrollo con Docker (Recomendado)

#### Ventajas
- **Entorno consistente** - Igual a producción
- **Aislamiento** - Sin conflictos de dependencias
- **Facilidad** - Un comando para todo
- **Hot reload** - Cambios se reflejan automáticamente

#### Comandos Útiles
```bash
# Levantar todos los servicios
docker-compose up --build

# Levantar en background
docker-compose up -d

# Ver logs
docker-compose logs -f [servicio]

# Detener servicios
docker-compose down

# Reconstruir imagen específica
docker-compose build [servicio]

# Limpiar todo
docker-compose down -v --rmi all
```

#### Desarrollo con Hot Reload
```yaml
# En docker-compose.yml
volumes:
  - ./backend:/app          # Backend hot reload
  - ./frontend/src:/app/src  # Frontend hot reload
```

### Opción 2: Desarrollo Nativo

#### Backend (Python + FastAPI)
```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con API key

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (React + Next.js)
```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# O con yarn
yarn dev
```

#### MCP Server (Python)
```bash
cd mcp

# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor MCP
python -m src.mcp_server

# O ejecutar análisis CLI
python -m src.main data/sample_report.json
```

## 📁 Estructura de Proyectos

### Backend API Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app y endpoints
│   ├── models.py            # Pydantic models
│   ├── prompts.py           # Prompts para IA
│   └── ai_service.py        # Servicio Groq
├── .env.example             # Variables de entorno
├── requirements.txt         # Dependencias Python
├── Dockerfile              # Configuración Docker
└── .dockerignore           # Ignorar archivos en Docker
```

### Frontend Structure
```
frontend/
├── public/
│   └── index.html           # HTML template
├── src/
│   ├── index.js             # Punto de entrada Next.js
│   ├── index.css            # Estilos globales
│   └── App.js               # Componente principal
├── package.json             # Dependencias npm
├── Dockerfile              # Configuración Docker
└── .dockerignore           # Ignorar archivos en Docker
```

### MCP Server Structure
```
mcp/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   └── telemetry.py     # Modelos de datos telemétricos
│   ├── validators/
│   │   ├── __init__.py
│   │   └── data_validator.py # Validación de datos
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── performance_analyzer.py
│   │   ├── anomaly_detector.py
│   │   └── company_comparator.py
│   ├── reports/
│   │   ├── __init__.py
│   │   └── report_generator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   ├── main.py              # CLI entry point
│   └── mcp_server.py        # MCP server implementation
├── tests/                   # Unit tests
├── data/                    # Sample data
├── output/                  # Generated reports
├── requirements.txt         # Python dependencies
└── Dockerfile              # Docker configuration
```

## 🔧 Configuración de IDE

### VS Code Extensions Recomendadas
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-json",
    "ms-azuretools.vscode-docker",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag"
  ]
}
```

### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./backend/venv/Scripts/python.exe",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/node_modules": true,
    "**/venv": true,
    "**/__pycache__": true,
    "**/.next": true
  }
}
```

### Git Hooks (Opcional)
```bash
# Instalar pre-commit
pip install pre-commit

# Crear .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        files: ^backend/
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        files: ^backend/
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v2.6.2
    hooks:
      - id: prettier
        files: ^frontend/
```

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Ejecutar tests (cuando existan)
pytest

# Con coverage
pytest --cov=app

# Tests específicos
pytest tests/test_ai_service.py -v
```

### Frontend Tests
```bash
cd frontend

# Ejecutar tests (cuando existan)
npm test

# Tests con coverage
npm run test:coverage

# Tests E2E (cuando existan)
npm run test:e2e
```

### MCP Server Tests
```bash
cd mcp

# Ejecutar todos los tests
python -m pytest tests/ -v

# Tests específicos
python -m pytest tests/test_analyzers.py -v

# Con coverage
python -m pytest tests/ --cov=src
```

### Tests de Integración
```bash
# Tests de API con Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Tests manuales con Postman
# Importar collection desde docs/postman-collection.json
```

## 🐛 Debugging

### Backend Debugging

#### VS Code Debug Configuration
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/app/main.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

#### Debug en Docker
```bash
# Ver logs en tiempo real
docker-compose logs -f backend

# Entrar al contenedor
docker-compose exec backend bash

# Instalar debug tools
pip install ipdb
# Agregar breakpoint: import ipdb; ipdb.set_trace()
```

### Frontend Debugging

#### Browser DevTools
- **Chrome DevTools** - F12
- **React DevTools** - Extension
- **Redux DevTools** - Extension (si aplica)

#### VS Code Debug
```json
{
  "type": "node",
  "request": "launch",
  "name": "Next.js",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["run", "dev"],
  "port": 9229
}
```

### MCP Server Debugging
```bash
# Debug con logging
python -m src.main data/sample_report.json --verbose

# Debug interactivo
python -m ipdb src/main.py

# Ver logs específicos
python -m src.mcp_server 2>&1 | tee mcp.log
```

## 📦 Gestión de Dependencias

### Backend Dependencies
```bash
# Agregar nueva dependencia
pip install <package>
pip freeze > requirements.txt

# Actualizar dependencias
pip install --upgrade <package>

# Eliminar dependencias no usadas
pip-autoremove <package>
```

### Frontend Dependencies
```bash
# Agregar dependencia de producción
npm install <package>

# Agregar dependencia de desarrollo
npm install --save-dev <package>

# Actualizar dependencias
npm update

# Eliminar dependencias no usadas
npm prune
```

### MCP Dependencies
```bash
# Mismos comandos que backend
cd mcp
pip install <package>
pip freeze > requirements.txt
```

## 🔄 CI/CD Pipeline

### GitHub Actions (Ejemplo)
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test

  test-mcp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd mcp
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd mcp
          python -m pytest tests/ -v

  build-and-deploy:
    needs: [test-backend, test-frontend, test-mcp]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker images
        run: |
          docker-compose build
          docker-compose push
```

## 🚀 Despliegue

### Desarrollo/Staging
```bash
# Entorno de desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Entorno de staging
docker-compose -f docker-compose.staging.yml up -d
```

### Producción
```bash
# Entorno de producción
docker-compose -f docker-compose.prod.yml up -d

# Con health checks
docker-compose -f docker-compose.prod.yml up -d --health-timeout 30s
```

### Variables de Entorno por Ambiente
```bash
# .env.development
GROQ_API_KEY=dev_key
DEBUG=true
LOG_LEVEL=debug

# .env.production
GROQ_API_KEY=prod_key
DEBUG=false
LOG_LEVEL=info
```

## 📊 Performance Monitoring

### Backend Monitoring
```python
# app/main.py
from fastapi import FastAPI
import time
import logging

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logging.info(f"Request: {request.url.path} - Time: {process_time:.4f}s")
    return response
```

### Frontend Performance
```javascript
// src/utils/performance.js
export const measurePerformance = (name, fn) => {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  console.log(`${name}: ${end - start}ms`);
  return result;
};
```

## 🔐 Buenas Prácticas de Desarrollo

### Código Limpio
- **PEP 8** para Python
- **ESLint/Prettier** para JavaScript
- **Nombres descriptivos** para variables y funciones
- **Comentarios útiles** cuando sea necesario

### Git Workflow
- **Branches descriptivos** (feature/nombre-feature)
- **Commits atómicos** (un cambio por commit)
- **Pull requests** con descripción clara
- **Code reviews** obligatorios

### Testing
- **Unit tests** para lógica de negocio
- **Integration tests** para APIs
- **E2E tests** para flujos críticos
- **Coverage > 80%** como meta

### Seguridad
- **No commitear secrets**
- **Validar inputs** en todos los endpoints
- **Usar HTTPS** en producción
- **Principio de mínimo privilegio**

## 📚 Recursos de Aprendizaje

### Documentación
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [MCP Documentation](https://modelcontextprotocol.io/)

### Tutoriales
- [FastAPI + React Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Next.js Learn Course](https://nextjs.org/learn)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Comunidades
- [FastAPI Discord](https://discord.gg/VQjSZaeJmf)
- [Next.js GitHub Discussions](https://github.com/vercel/next.js/discussions)
- [Stack Overflow](https://stackoverflow.com/)
