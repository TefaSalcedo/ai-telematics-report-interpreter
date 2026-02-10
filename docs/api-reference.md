# API Reference

## 📡 Backend API Documentation

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

### Authentication
Actualmente sin autenticación (modo demo). En producción se implementará:
- **Bearer Token**: JWT tokens
- **API Key**: Para integraciones externas

---

## 🛠️ Endpoints

### Health Check

#### GET `/`
Health check básico del servidor.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Telematics API",
  "version": "1.0.0"
}
```

#### GET `/health`
Health check detallado para Docker.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-02-10T14:30:00Z",
  "version": "1.0.0",
  "environment": "development"
}
```

---

### Interpretación de Reportes

#### POST `/interpret`
Interpreta un reporte telemétrico usando IA según el perfil de usuario.

**Request Body:**
```json
{
  "report": {
    "cliente": "Empresa Demo S.A.",
    "periodo": "01-02-2025 a 07-02-2025",
    "indicadores": {
      "distancia_total_km": 3200,
      "consumo_total_litros": 450,
      "excesos_velocidad": 12,
      "tiempo_ralenti_minutos": 340,
      "frenadas_bruscas": 8
    },
    "vehiculos": [
      {
        "placa": "ABC123",
        "distancia_km": 1200,
        "consumo_litros": 160,
        "excesos_velocidad": 7,
        "tiempo_ralenti_minutos": 150,
        "frenadas_bruscas": 3,
        "eventos": [
          {
            "tipo": "exceso_velocidad",
            "timestamp": "2025-02-05T14:30:00Z",
            "ubicacion": "Autopista Norte km 45",
            "valor": 120
          }
        ]
      }
    ]
  },
  "profile": "gerente"
}
```

**Parameters:**
- `report` (object, required): Reporte telemétrico completo
- `profile` (string, required): Perfil de interpretación
  - `"gerente"`: Enfoque ejecutivo y estratégico
  - `"operaciones"`: Enfoque técnico y operativo

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "interpretation": {
      "resumen_ejecutivo": "Durante la semana analizada, la flota mostró un rendimiento general bueno con un consumo de 14.1 L/100km, aunque se detectaron 3 vehículos que requieren atención inmediata por consumos elevados.",
      "kpis_principales": {
        "consumo_promedio": "14.1 L/100km",
        "eficiencia_global": "78%",
        "vehiculos_criticos": 3,
        "potencial_ahorro": "$2,340 mensual"
      },
      "recomendaciones": [
        "Revisar sensor de combustible del vehículo ABC123",
        "Implementar programa de mantenimiento preventivo",
        "Capacitar conductores en conducción eficiente"
      ],
      "vehiculos_destacados": [
        {
          "placa": "ABC123",
          "estado": "Crítico",
          "consumo": "18.5 L/100km",
          "recomendacion": "Inspección inmediata"
        }
      ]
    },
    "metadata": {
      "profile_used": "gerente",
      "processing_time": 2.3,
      "model_used": "llama-3.3-70b-versatile",
      "timestamp": "2025-02-10T14:30:00Z"
    }
  }
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Datos de entrada inválidos",
    "details": {
      "field": "profile",
      "issue": "Perfil no válido. Debe ser 'gerente' o 'operaciones'"
    }
  }
}
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": {
    "code": "AI_SERVICE_ERROR",
    "message": "Error en el servicio de IA",
    "details": "No se pudo conectar con el servicio Groq"
  }
}
```

---

## 🤖 MCP Server API

### Conexión MCP
El servidor MCP usa el protocolo Model Context Protocol para comunicación con LLMs.

#### Iniciar Servidor
```bash
python -m src.mcp_server
```

#### Tools Disponibles

##### 1. `validate_telemetry_data`
Valida la estructura y lógica de un reporte telemétrico.

**Parameters:**
```json
{
  "report_data": {
    "cliente": "string",
    "periodo": "string",
    "indicadores": {...},
    "vehiculos": [...]
  }
}
```

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Vehículo XYZ789 tiene consumo fuera de rango"
  ],
  "statistics": {
    "total_vehicles": 5,
    "valid_vehicles": 4,
    "invalid_vehicles": 1
  }
}
```

##### 2. `analyze_performance`
Analiza métricas de rendimiento de combustible.

**Parameters:**
```json
{
  "report_data": {...}
}
```

**Response:**
```json
{
  "performance_metrics": {
    "fleet_average_km_per_liter": 7.1,
    "best_vehicle": {
      "placa": "DEF456",
      "km_per_liter": 8.5
    },
    "worst_vehicle": {
      "placa": "ABC123",
      "km_per_liter": 5.4
    },
    "efficiency_distribution": {
      "excellent": 1,
      "good": 2,
      "fair": 1,
      "poor": 1
    }
  },
  "anomalies": [
    {
      "type": "high_consumption",
      "vehicle": "ABC123",
      "severity": "high",
      "description": "Consumo 40% superior al promedio"
    }
  ]
}
```

##### 3. `detect_anomalies`
Detecta anomalías en patrones de consumo y comportamiento.

**Parameters:**
```json
{
  "report_data": {...}
}
```

**Response:**
```json
{
  "anomaly_summary": {
    "total_anomalies": 8,
    "severity_breakdown": {
      "critical": 2,
      "warning": 4,
      "info": 2
    }
  },
  "anomalies": [
    {
      "id": "ANOM001",
      "type": "fuel_theft_suspicion",
      "severity": "critical",
      "vehicle": "ABC123",
      "description": "Descarga de 50L con motor apagado",
      "location": "Depósito Central",
      "timestamp": "2025-02-05T02:30:00Z",
      "confidence": 0.85
    }
  ]
}
```

##### 4. `compare_reports`
Compara datos entre dos proveedores o períodos.

**Parameters:**
```json
{
  "report_a": {...},
  "report_b": {...}
}
```

**Response:**
```json
{
  "comparison_summary": {
    "report_a_name": "Empresa A - Semana 1",
    "report_b_name": "Empresa B - Semana 1",
    "total_vehicles_a": 10,
    "total_vehicles_b": 12,
    "overall_winner": "Empresa B"
  },
  "metrics_comparison": {
    "efficiency": {
      "a": 7.2,
      "b": 8.1,
      "difference": "+12.5%",
      "winner": "B"
    },
    "consumption": {
      "a": 450,
      "b": 420,
      "difference": "-6.7%",
      "winner": "B"
    }
  }
}
```

##### 5. `generate_full_report`
Genera un reporte completo con todos los análisis.

**Parameters:**
```json
{
  "report_data": {...},
  "include_recommendations": true,
  "format": "json"
}
```

**Response:**
```json
{
  "report": {
    "executive_summary": "...",
    "performance_analysis": {...},
    "anomaly_detection": {...},
    "recommendations": [...],
    "vehicle_rankings": [...],
    "metadata": {
      "generated_at": "2025-02-10T14:30:00Z",
      "analysis_version": "1.0.0"
    }
  }
}
```

---

## 📊 Modelos de Datos

### Report Telemétrico

```typescript
interface TelemetryReport {
  cliente: string;
  periodo: string;
  indicadores: {
    distancia_total_km: number;
    consumo_total_litros: number;
    excesos_velocidad: number;
    tiempo_ralenti_minutos: number;
    frenadas_bruscas: number;
  };
  vehiculos: Vehicle[];
}

interface Vehicle {
  placa: string;
  distancia_km: number;
  consumo_litros: number;
  excesos_velocidad: number;
  tiempo_ralenti_minutos: number;
  frenadas_bruscas: number;
  eventos?: VehicleEvent[];
}

interface VehicleEvent {
  tipo: string;
  timestamp: string;
  ubicacion: string;
  valor: number;
}
```

### Respuesta de Interpretación

```typescript
interface InterpretationResponse {
  success: boolean;
  data?: {
    interpretation: {
      resumen_ejecutivo: string;
      kpis_principales: Record<string, string>;
      recomendaciones: string[];
      vehiculos_destacados: VehicleHighlight[];
    };
    metadata: {
      profile_used: string;
      processing_time: number;
      model_used: string;
      timestamp: string;
    };
  };
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

interface VehicleHighlight {
  placa: string;
  estado: string;
  consumo: string;
  recomendacion: string;
}
```

---

## 🔧 Configuración

### Variables de Entorno

```bash
# Backend
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
DEBUG=true
LOG_LEVEL=info

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development

# MCP
MCP_LOG_LEVEL=info
MCP_CACHE_ENABLED=true
```

### Configuración de Rate Limiting (Futuro)

```python
# app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/interpret")
@limiter.limit("10/minute")
async def interpret_report(request: Request, data: InterpretRequest):
    # ...
```

---

## 🧪 Testing de API

### Ejemplos con curl

#### Health Check
```bash
curl -X GET http://localhost:8000/health
```

#### Interpretación - Perfil Gerente
```bash
curl -X POST http://localhost:8000/interpret \
  -H "Content-Type: application/json" \
  -d '{
    "report": {
      "cliente": "Test Company",
      "periodo": "01-02-2025 a 07-02-2025",
      "indicadores": {
        "distancia_total_km": 1000,
        "consumo_total_litros": 150,
        "excesos_velocidad": 5,
        "tiempo_ralenti_minutos": 120,
        "frenadas_bruscas": 3
      },
      "vehiculos": [
        {
          "placa": "TEST123",
          "distancia_km": 500,
          "consumo_litros": 75,
          "excesos_velocidad": 2,
          "tiempo_ralenti_minutos": 60,
          "frenadas_bruscas": 1
        }
      ]
    },
    "profile": "gerente"
  }'
```

#### Interpretación - Perfil Operaciones
```bash
curl -X POST http://localhost:8000/interpret \
  -H "Content-Type: application/json" \
  -d '{
    "report": {
      "cliente": "Test Company",
      "periodo": "01-02-2025 a 07-02-2025",
      "indicadores": {
        "distancia_total_km": 1000,
        "consumo_total_litros": 150,
        "excesos_velocidad": 5,
        "tiempo_ralenti_minutos": 120,
        "frenadas_bruscas": 3
      },
      "vehiculos": [
        {
          "placa": "TEST123",
          "distancia_km": 500,
          "consumo_litros": 75,
          "excesos_velocidad": 2,
          "tiempo_ralenti_minutos": 60,
          "frenadas_bruscas": 1
        }
      ]
    },
    "profile": "operaciones"
  }'
```

### Testing con Postman

Importar la siguiente collection:

```json
{
  "info": {
    "name": "AI Telematics API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Interpret Report - Manager",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"report\": {\n    \"cliente\": \"Test Company\",\n    \"periodo\": \"01-02-2025 a 07-02-2025\",\n    \"indicadores\": {\n      \"distancia_total_km\": 1000,\n      \"consumo_total_litros\": 150,\n      \"excesos_velocidad\": 5,\n      \"tiempo_ralenti_minutos\": 120,\n      \"frenadas_bruscas\": 3\n    },\n    \"vehiculos\": [\n      {\n        \"placa\": \"TEST123\",\n        \"distancia_km\": 500,\n        \"consumo_litros\": 75,\n        \"excesos_velocidad\": 2,\n        \"tiempo_ralenti_minutos\": 60,\n        \"frenadas_bruscas\": 1\n      }\n    ]\n  },\n  \"profile\": \"gerente\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/interpret",
          "host": ["{{base_url}}"],
          "path": ["interpret"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

## 📝 Códigos de Error

### HTTP Status Codes

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| 200 | Success | Request procesado correctamente |
| 400 | Bad Request | Datos de entrada inválidos |
| 401 | Unauthorized | No autenticado (futuro) |
| 429 | Too Many Requests | Rate limit excedido (futuro) |
| 500 | Internal Server Error | Error del servidor |

### Error Codes Específicos

| Code | Descripción | Solución |
|------|-------------|----------|
| `VALIDATION_ERROR` | Datos de entrada inválidos | Verificar formato y valores |
| `PROFILE_INVALID` | Perfil no válido | Usar 'gerente' u 'operaciones' |
| `AI_SERVICE_ERROR` | Error en servicio IA | Verificar API key y conexión |
| `PROCESSING_ERROR` | Error en procesamiento | Reintentar con datos válidos |
| `TIMEOUT_ERROR` | Timeout del servicio | Reintentar más tarde |

---

## 🔄 Versionamiento de API

### v1.0.0 (Current)
- Endpoint `/interpret`
- Perfiles: gerente, operaciones
- Validación básica

### v1.1.0 (Planned)
- Endpoint `/batch-interpret`
- Perfiles adicionales
- Caching de resultados

### v2.0.0 (Future)
- Autenticación JWT
- Rate limiting
- WebSocket support

---

## 📊 Monitoring y Logging

### Logs de Request
```json
{
  "timestamp": "2025-02-10T14:30:00Z",
  "method": "POST",
  "path": "/interpret",
  "status_code": 200,
  "processing_time": 2.3,
  "user_agent": "Mozilla/5.0...",
  "ip_address": "127.0.0.1"
}
```

### Métricas Disponibles
- **Response time**: Tiempo de procesamiento
- **Error rate**: Tasa de errores
- **Request volume**: Volumen de requests
- **AI service latency**: Latencia del servicio IA

### Health Checks
```bash
# Health check básico
curl -f http://localhost:8000/health

# Health check detallado
curl -f http://localhost:8000/health/detailed
```

---

## 🔒 Consideraciones de Seguridad

### Input Validation
- Todos los inputs validados con Pydantic
- Sanitización de datos peligrosos
- Límites de tamaño de archivos

### Rate Limiting (Planned)
- 10 requests por minuto por IP
- 1000 requests por día por usuario
- Burst protection

### CORS Configuration
```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 SDKs y Clientes

### Python SDK (Future)
```python
from ai_telematics_client import AITelematicsClient

client = AITelematicsClient(base_url="http://localhost:8000")
result = client.interpret_report(report_data, profile="gerente")
```

### JavaScript SDK (Future)
```javascript
import { AITelematicsClient } from 'ai-telematics-js-sdk';

const client = new AITelematicsClient('http://localhost:8000');
const result = await client.interpretReport(reportData, 'gerente');
```

### Postman Collection
Disponible en `docs/postman-collection.json`
