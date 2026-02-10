# Arquitectura del Sistema

## Visión General

El **AI Telematics Fleet Management System** es una arquitectura de microservicios diseñada para el análisis inteligente de datos telemétricos de flotas vehiculares. El sistema combina procesamiento local de datos con servicios de IA en la nube para proporcionar insights completos y personalizados.

## 🏗️ Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   React App     │  │   Next.js      │  │   Charts/     │ │
│  │   (UI/UX)       │  │   Framework     │  │   Visuals     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   FastAPI       │  │   REST Endpoints│  │   Validation  │ │
│  │   Server        │  │   (/interpret)  │  │   (Pydantic)  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   AI Service    │ │   MCP Server    │ │   Data Storage  │
│   (Groq API)    │ │   (Local AI)    │ │   (File System) │
│                 │ │                 │ │                 │
│ • Interpretación│ │ • Análisis      │ │ • JSON Reports  │
│ • Perfiles       │ │ • Anomalías     │ │ • Output Files  │
│ • Personalización│ │ • Validación    │ │ • Logs          │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🔄 Flujo de Datos Detallado

### 1. Flujo Principal (Interpretación con IA)

```
Usuario (Frontend)
    ↓ [Upload JSON]
React Component
    ↓ [POST /interpret]
FastAPI Backend
    ↓ [Validate Request]
Pydantic Models
    ↓ [Select Profile]
Profile Manager
    ↓ [Generate Prompt]
Prompt Engine
    ↓ [Call Groq API]
Groq LLM Service
    ↓ [Process Response]
Response Parser
    ↓ [Return Analysis]
Frontend Display
```

### 2. Flujo MCP (Análisis Técnico)

```
LLM Client
    ↓ [MCP Protocol]
MCP Server
    ↓ [Tool Selection]
Tool Router
    ↓ [Data Processing]
┌─────────────────┬─────────────────┬─────────────────┐
│   Validator     │   Analyzer      │   Reporter      │
│                 │                 │                 │
│ • Structure     │ • Performance   │ • Executive     │
│ • Logic         │ • Anomalies     │ • Technical     │
│ • Range         │ • Patterns      │ • Rankings      │
└─────────────────┴─────────────────┴─────────────────┘
    ↓                   ↓                   ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   Validation    │   Analysis      │   Report        │
│   Results       │   Results       │   Generation    │
└─────────────────┴─────────────────┴─────────────────┘
    ↓                   ↓                   ↓
                Combined Results → LLM Client
```

## 🏛️ Componentes Arquitectónicos

### Frontend Layer
- **React 19**: Componentes UI modernos con hooks avanzados
- **Next.js 16**: Framework de producción con SSR/SSG
- **TailwindCSS 4**: Sistema de diseño utility-first
- **Chart.js/Recharts**: Visualización de datos interactiva

**Responsabilidades:**
- Interfaz de usuario intuitiva
- Carga y validación de archivos
- Visualización de resultados
- Gestión de estado de la aplicación

### API Gateway Layer
- **FastAPI 0.115**: Framework API de alto rendimiento
- **Pydantic 2.9**: Validación y serialización de datos
- **Uvicorn**: Servidor ASGI asíncrono
- **Swagger UI**: Documentación automática

**Responsabilidades:**
- Endpoint RESTful `/interpret`
- Validación de datos de entrada
- Enrutamiento a servicios apropiados
- Gestión de errores y logging

### AI Service Layer
- **Groq API**: Servicio de LLM externo (gratuito)
- **Profile Engine**: Gestión de perfiles de usuario
- **Prompt Manager**: Plantillas de prompts optimizadas
- **Response Parser**: Procesamiento de respuestas IA

**Responsabilidades:**
- Interpretación contextual de datos
- Personalización por perfil de usuario
- Generación de insights ejecutivos
- Traducción técnica a lenguaje natural

### MCP Server Layer
- **MCP SDK**: Protocolo Model Context Protocol
- **Analysis Engine**: Motor de análisis local
- **Validation Engine**: Validación de datos telemétricos
- **Report Generator**: Generación de reportes técnicos

**Responsabilidades:**
- Análisis de rendimiento de combustible
- Detección de anomalías y patrones
- Comparación multiempresa
- Integración con LLMs vía MCP

## 🔗 Integración entre Componentes

### Comunicación Frontend-Backend
- **Protocolo**: HTTP/HTTPS REST
- **Formato**: JSON
- **Autenticación**: No requerida (demo)
- **Rate Limiting**: No implementada (demo)

### Backend-AI Service
- **Protocolo**: HTTPS API calls
- **Servicio**: Groq API
- **Autenticación**: API Key
- **Modelos**: Llama 3.3 70B (principal)

### Backend-MCP Server
- **Protocolo**: MCP (Model Context Protocol)
- **Transporte**: stdio (local)
- **Formato**: JSON-RPC 2.0
- **Tools**: 5 herramientas de análisis

## 🗄️ Gestión de Datos

### Estructura de Datos

```json
{
  "report": {
    "cliente": "string",
    "periodo": "string",
    "indicadores": {
      "distancia_total_km": "number",
      "consumo_total_litros": "number",
      "excesos_velocidad": "number",
      "tiempo_ralenti_minutos": "number",
      "frenadas_bruscas": "number"
    },
    "vehiculos": [
      {
        "placa": "string",
        "distancia_km": "number",
        "consumo_litros": "number",
        "excesos_velocidad": "number",
        "tiempo_ralenti_minutos": "number",
        "frenadas_bruscas": "number",
        "eventos": [
          {
            "tipo": "string",
            "timestamp": "string",
            "ubicacion": "string",
            "valor": "number"
          }
        ]
      }
    ]
  },
  "profile": "gerente|operaciones"
}
```

### Almacenamiento
- **Frontend**: Estado local (React state)
- **Backend**: Sin persistencia (stateless)
- **MCP**: Sistema de archivos local
- **Logs**: Docker container logs

## 🔐 Seguridad

### Implementada
- **Validación de entrada**: Pydantic models
- **Sanitización de datos**: Type checking
- **CORS**: Configurado para desarrollo
- **Environment variables**: API keys protegidas

### No Implementada (Demo)
- **Autenticación de usuarios**
- **Autorización por roles**
- **Rate limiting**
- **HTTPS en producción**
- **Input sanitization avanzada**

## 📈 Escalabilidad y Performance

### Estrategias de Escalabilidad

#### Horizontal
- **Frontend**: CDN + Static hosting
- **Backend**: Load balancer + múltiples instancias
- **MCP**: Pool de servidores MCP

#### Vertical
- **Frontend**: Optimización de bundle
- **Backend**: Async processing + caching
- **MCP**: Parallel analysis pipelines

### Optimizaciones de Performance

#### Frontend
- **Code splitting**: Next.js automatic
- **Lazy loading**: Componentes bajo demanda
- **Image optimization**: Next.js Image
- **Bundle size**: Tree shaking

#### Backend
- **Async endpoints**: FastAPI async/await
- **Connection pooling**: HTTP clients reusables
- **Response caching**: In-memory cache
- **Request validation**: Early validation

#### MCP
- **Parallel processing**: Concurrent analysis
- **Memory optimization**: Streaming processing
- **Caching results**: File-based cache
- **Batch operations**: Bulk data processing

## 🚨 Manejo de Errores

### Estrategia de Error Handling

#### Frontend
- **Error boundaries**: React error boundaries
- **User feedback**: Toast notifications
- **Retry mechanisms**: Exponential backoff
- **Fallback UI**: Graceful degradation

#### Backend
- **Exception handling**: Try/catch global
- **HTTP status codes**: Proper error codes
- **Error logging**: Structured logging
- **Validation errors**: Detailed messages

#### MCP
- **Data validation**: Pre-processing validation
- **Graceful failures**: Partial analysis
- **Error recovery**: Fallback methods
- **Debug information**: Verbose logging

## 🔄 Ciclo de Vida de Request

### Request Exitoso
1. **Frontend**: User uploads JSON
2. **Validation**: Client-side validation
3. **API Call**: POST /interpret
4. **Backend**: Request validation
5. **AI Service**: Profile selection + prompt generation
6. **Groq API**: LLM processing
7. **Response**: Parse and format
8. **Frontend**: Display results

### Request con Errores
1. **Validation Error**: Return 400 + details
2. **AI Service Error**: Return 500 + generic message
3. **Groq API Error**: Fallback to local analysis
4. **Network Error**: Retry mechanism
5. **Timeout**: Graceful timeout handling

## 📊 Monitoreo y Observabilidad

### Métricas Disponibles
- **Response times**: Endpoint timing
- **Error rates**: HTTP error tracking
- **Resource usage**: Docker stats
- **AI service latency**: Groq API timing

### Logs Implementados
- **Application logs**: Structured JSON logs
- **Access logs**: HTTP request logging
- **Error logs**: Exception tracking
- **Debug logs**: Verbose development logs

## 🔄 Futuras Mejoras Arquitectónicas

### Corto Plazo
- **Database**: PostgreSQL para persistencia
- **Cache**: Redis para caching distribuido
- **Queue**: RabbitMQ para async processing
- **Monitoring**: Prometheus + Grafana

### Largo Plazo
- **Microservices**: Descomposición adicional
- **Event-driven**: Arquitectura basada en eventos
- **API Gateway**: Kong/AWS API Gateway
- **Service Mesh**: Istio para comunicación

## 📚 Patrones de Diseño Utilizados

### Patrones Arquitectónicos
- **Microservices**: Servicios independientes
- **API Gateway**: Punto de entrada unificado
- **CQRS**: Separación lectura/escritura (futuro)
- **Event Sourcing**: Logging de eventos (futuro)

### Patrones de Diseño
- **Repository**: Abstracción de datos
- **Factory**: Creación de objetos
- **Strategy**: Selección de algoritmos
- **Observer**: Notificación de cambios

### Patrones de Código
- **Dependency Injection**: Inversión de dependencias
- **SOLID Principles**: Diseño robusto
- **DRY**: No repetición de código
- **KISS**: Simplicidad sobre complejidad
