This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/ap# AI Telematics Fleet Management System

**Sistema integral de gestión telemétrica de flotas con análisis inteligente de datos, interpretación con IA y servidor MCP para integración con LLMs.**

Este proyecto unifica dos componentes principales:
- **AI Telematics Interpreter**: Interfaz web con IA para interpretar reportes telemétricos
- **Fleet Telemetry Analyzer**: Sistema MCP de análisis avanzado de datos de combustible

---

## 🏗️ Arquitectura General

```
ai-mini/
├── backend/                    # API FastAPI con IA
├── frontend/                   # Interfaz React/Next.js
├── mcp/                        # Servidor MCP de análisis telemétrico
├── docs/                       # Documentación detallada
├── docker-compose.yml          # Orquestación de todos los servicios
└── README.md                   # Este archivo
```

### Componentes del Sistema

#### 1. **Backend API** (Python + FastAPI)
- **Propósito**: API RESTful con integración IA para interpretar reportes
- **Tecnologías**: FastAPI, Groq API, Pydantic
- **Puerto**: 8000
- **Características**:
  - Interpretación de reportes con IA según perfil de usuario
  - Soporte para múltiples perfiles (Gerente, Operaciones)
  - API REST con documentación automática

#### 2. **Frontend Web** (React + Next.js)
- **Propósito**: Interfaz de usuario para interactuar con el sistema
- **Tecnologías**: Next.js 16, React 19, TailwindCSS
- **Puerto**: 3001
- **Características**:
  - Interfaz moderna y responsiva
  - Visualización de datos telemétricos
  - Integración con backend API

#### 3. **MCP Server** (Python)
- **Propósito**: Servidor Model Context Protocol para análisis avanzado
- **Tecnologías**: Python 3.12, MCP SDK, Pydantic
- **Características**:
  - Análisis de rendimiento de combustible
  - Detección de anomalías y patrones sospechosos
  - Comparación multiempresa
  - Integración con LLMs vía MCP

---

## 🚀 Inicio Rápido

### Requisitos Previos

- **Docker Desktop** instalado y corriendo
- **API Key de Groq** (gratuita en https://console.groq.com/keys)

### Configuración Inicial

1. **Configurar API Key de Groq**:
```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tu API key
```

2. **Levantar todos los servicios**:
```bash
docker-compose up --build
```

### Accesos

- **Frontend Web**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **MCP Server**: Disponible vía stdio (ver documentación MCP)

---

## 📋 Servicios Disponibles

### Servicios Principales (siempre activos)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver estado de los servicios
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs -f frontend
docker-compose logs -f backend
```

### Servicios MCP (bajo demanda)

```bash
# Analizar datos telemétricos
docker-compose up mcp-analyzer

# Iniciar servidor MCP para LLMs
docker-compose up mcp-server

# Ejecutar tests del MCP
docker-compose up mcp-tests
```

---

## 📚 Documentación Detallada

### Documentación Principal
- [**Arquitectura del Sistema**](docs/architecture.md) - Diseño y flujo de datos
- [**Guía de Desarrollo**](docs/development.md) - Configuración para desarrolladores
- [**API Reference**](docs/api-reference.md) - Documentación completa de APIs
- [**MCP Server Guide**](docs/mcp-server.md) - Uso del servidor MCP

### Guías Específicas
- [**Backend API**](docs/backend.md) - Desarrollo y configuración del backend
- [**Frontend Web**](docs/frontend.md) - Desarrollo de la interfaz
- [ **Análisis Telemétrico**](docs/telemetry-analysis.md) - Funcionalidades del MCP
- [**Docker y Despliegue**](docs/docker-deployment.md) - Guía de contenerización

---

## 🔧 Tecnologías Utilizadas

### Backend
- **Python 3.12** - Lenguaje principal
- **FastAPI 0.115** - Framework API
- **Groq API** - Servicios de IA (gratuito)
- **Pydantic 2.9** - Validación de datos
- **Uvicorn** - Servidor ASGI

### Frontend
- **Next.js 16.1** - Framework React
- **React 19.2** - Librería UI
- **TypeScript** - Tipado estático
- **TailwindCSS 4** - Framework CSS
- **Chart.js/Recharts** - Visualización

### MCP Server
- **Python 3.12** - Lenguaje principal
- **MCP SDK** - Model Context Protocol
- **Pydantic 2.0** - Modelos de datos
- **pytest** - Testing

### Infraestructura
- **Docker** - Contenerización
- **Docker Compose** - Orquestación
- **Multi-stage builds** - Optimización de imágenes

---

## 🎯 Casos de Uso

### 1. **Interpretación de Reportes con IA**
- Carga reportes telemétricos JSON
- Selecciona perfil de usuario (Gerente/Operaciones)
- Obtén análisis personalizado con IA

### 2. **Análisis Avanzado de Combustible**
- Detección de anomalías en consumo
- Análisis de patrones sospechosos
- Comparación entre períodos y empresas

### 3. **Integración con LLMs**
- Usa el servidor MCP para integración con asistentes IA
- Herramientas de análisis disponibles para LLMs
- Procesamiento de datos telemétricos automatizado

---

## 📊 Flujo de Datos

```
Reporte Telemétrico (JSON)
    ↓
Frontend Web (Upload)
    ↓
Backend API (FastAPI)
    ↓
┌─────────────────┬─────────────────┐
│   IA Analysis   │  MCP Analysis   │
│   (Groq API)    │  (Local AI)     │
└─────────────────┴─────────────────┘
    ↓                     ↓
Interpretación          Análisis
Personalizada          Técnico
    ↓                     ↓
Resultes Combinados → Dashboard Usuario
```

---

## 🛠️ Desarrollo

### Estructura de Carpetas

```
ai-mini/
├── backend/
│   ├── app/
│   │   ├── main.py           # Endpoints API
│   │   ├── models.py         # Modelos Pydantic
│   │   ├── prompts.py        # Prompts IA
│   │   └── ai_service.py     # Servicio Groq
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js           # Componente principal
│   │   └── index.js         # Punto entrada
│   ├── package.json
│   └── Dockerfile
├── mcp/
│   ├── src/
│   │   ├── models/          # Modelos telemétricos
│   │   ├── analyzers/       # Análisis de datos
│   │   ├── reports/         # Generación reportes
│   │   └── mcp_server.py    # Servidor MCP
│   ├── tests/               # Tests unitarios
│   └── Dockerfile
└── docs/                    # Documentación
```

### Scripts Útiles

```bash
# Desarrollo backend
cd backend && uvicorn app.main:app --reload

# Desarrollo frontend
cd frontend && npm run dev

# Desarrollo MCP
cd mcp && python -m src.mcp_server

# Tests
cd mcp && python -m pytest tests/ -v
```

---

## 🐛 Troubleshooting

### Problemas Comunes

1. **API Key de Groq no configurada**
   - Verifica `backend/.env` contiene `GROQ_API_KEY`

2. **Puertos en uso**
   - Asegura puertos 8000 y 3001 estén libres
   - Modifica `docker-compose.yml` si es necesario

3. **Build fallido**
   - Limpia caché Docker: `docker system prune -a`
   - Reconstruye: `docker-compose build --no-cache`

4. **Servicios no se comunican**
   - Verifica nombres de contenedores en `docker-compose.yml`
   - Revisa logs: `docker-compose logs`

---

## 📄 Licencia

Proyecto de demostración para análisis telemétrico con IA.

---

## 🤝 Contribuciones

1. Fork del proyecto
2. Feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

---

## 📞 Soporte

Para dudas o soporte técnico:
- Revisa la documentación en `/docs`
- Abre un issue en el repositorio
- Consulta los logs de Docker para diagnóstico
