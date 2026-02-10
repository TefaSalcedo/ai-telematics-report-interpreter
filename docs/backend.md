# Backend API Documentation

## 🐍 Backend FastAPI Development Guide

El backend del proyecto AI Telematics es una API RESTful construida con FastAPI que proporciona servicios de interpretación de reportes telemétricos usando inteligencia artificial.

---

## 🏗️ Arquitectura del Backend

### Estructura del Proyecto
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

### Flujo de Arquitectura
```
HTTP Request → FastAPI → Pydantic Validation → AI Service → Groq API → Response
```

---

## 📦 Dependencias y Tecnologías

### Core Dependencies
```txt
fastapi==0.115.0          # Framework API
uvicorn==0.30.6           # Servidor ASGI
groq==0.15.0              # Cliente Groq API
pydantic==2.9.2           # Validación de datos
python-dotenv==1.0.1      # Variables de entorno
```

### Development Dependencies
```txt
pytest==7.4.0            # Testing
pytest-asyncio==0.21.0   # Async testing
httpx==0.24.0             # HTTP client for tests
black==23.0.0             # Code formatting
flake8==6.0.0             # Linting
```

---

## 🔧 Configuración del Entorno

### Variables de Entorno
```bash
# .env
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
DEBUG=false
LOG_LEVEL=info
CORS_ORIGINS=http://localhost:3001
```

### Configuración de la Aplicación
```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    debug: bool = False
    log_level: str = "info"
    cors_origins: list = ["http://localhost:3001"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🚀 FastAPI Application

### Estructura Principal
```python
# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("AI Telematics API starting up...")
    yield
    # Shutdown
    logging.info("AI Telematics API shutting down...")

app = FastAPI(
    title="AI Telematics API",
    description="API for interpreting telemetry reports with AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Endpoints Principales

#### Health Check
```python
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "AI Telematics API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": "development" if settings.debug else "production"
    }
```

#### Interpretación de Reportes
```python
@app.post("/interpret")
async def interpret_report(request: InterpretRequest):
    try:
        # Validar datos
        validated_data = validate_report_data(request.report)
        
        # Generar interpretación
        interpretation = await generate_interpretation(
            report_data=validated_data,
            profile=request.profile
        )
        
        return {
            "success": True,
            "data": {
                "interpretation": interpretation,
                "metadata": {
                    "profile_used": request.profile,
                    "processing_time": 0.0,  # Calcular tiempo real
                    "model_used": settings.groq_model,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        }
        
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Datos de entrada inválidos",
                "details": str(e)
            }
        )
    except AIServiceError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "AI_SERVICE_ERROR",
                "message": "Error en el servicio de IA",
                "details": str(e)
            }
        )
```

---

## 📋 Modelos de Datos (Pydantic)

### Request Models
```python
# app/models.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class VehicleEvent(BaseModel):
    tipo: str = Field(..., description="Tipo de evento")
    timestamp: str = Field(..., description="Timestamp del evento")
    ubicacion: str = Field(..., description="Ubicación del evento")
    valor: float = Field(..., description="Valor del evento")

class Vehicle(BaseModel):
    placa: str = Field(..., description="Placa del vehículo")
    distancia_km: float = Field(..., ge=0, description="Distancia recorrida en km")
    consumo_litros: float = Field(..., ge=0, description="Consumo en litros")
    excesos_velocidad: int = Field(..., ge=0, description="Número de excesos de velocidad")
    tiempo_ralenti_minutos: int = Field(..., ge=0, description="Tiempo en ralentí")
    frenadas_bruscas: int = Field(..., ge=0, description="Número de frenadas bruscas")
    eventos: Optional[List[VehicleEvent]] = Field(default=[], description="Eventos del vehículo")
    
    @validator('consumo_litros')
    def validate_consumption(cls, v, values):
        if 'distancia_km' in values:
            efficiency = values['distancia_km'] / v if v > 0 else 0
            if efficiency < 3.0 or efficiency > 15.0:
                raise ValueError('Eficiencia de combustible fuera de rango (3-15 km/L)')
        return v

class Indicators(BaseModel):
    distancia_total_km: float = Field(..., ge=0)
    consumo_total_litros: float = Field(..., ge=0)
    excesos_velocidad: int = Field(..., ge=0)
    tiempo_ralenti_minutos: int = Field(..., ge=0)
    frenadas_bruscas: int = Field(..., ge=0)

class TelemetryReport(BaseModel):
    cliente: str = Field(..., min_length=1, max_length=100)
    periodo: str = Field(..., min_length=1)
    indicadores: Indicators
    vehiculos: List[Vehicle] = Field(..., min_items=1)
    
    @validator('vehiculos')
    def validate_vehicles_consistency(cls, v, values):
        if 'indicadores' in values:
            total_distance = sum(v.distancia_km for v in v)
            total_consumption = sum(v.consumo_litros for v in v)
            
            indicators = values['indicadores']
            tolerance = 0.05  # 5% tolerance
            
            if abs(total_distance - indicators.distancia_total_km) > indicators.distancia_total_km * tolerance:
                raise ValueError('Inconsistencia en distancia total')
            if abs(total_consumption - indicators.consumo_total_litros) > indicators.consumo_total_litros * tolerance:
                raise ValueError('Inconsistencia en consumo total')
        
        return v

class InterpretRequest(BaseModel):
    report: TelemetryReport
    profile: str = Field(..., regex="^(gerente|operaciones)$")
```

### Response Models
```python
class VehicleHighlight(BaseModel):
    placa: str
    estado: str
    consumo: str
    recomendacion: str

class InterpretationData(BaseModel):
    resumen_ejecutivo: str
    kpis_principales: Dict[str, str]
    recomendaciones: List[str]
    vehiculos_destacados: List[VehicleHighlight]

class InterpretationResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
```

---

## 🤖 Servicio de IA

### Groq AI Service
```python
# app/ai_service.py
import groq
from typing import Dict, Any
import logging
from .prompts import get_prompt_for_profile

class GroqService:
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = groq.Groq(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    async def interpret_report(
        self, 
        report_data: Dict[str, Any], 
        profile: str
    ) -> Dict[str, Any]:
        try:
            # Generar prompt según perfil
            prompt = get_prompt_for_profile(report_data, profile)
            
            # Llamar a Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis telemétrico de flotas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Procesar respuesta
            raw_response = response.choices[0].message.content
            
            # Parsear respuesta (implementar parsing robusto)
            return self._parse_ai_response(raw_response)
            
        except Exception as e:
            self.logger.error(f"Error en Groq API: {str(e)}")
            raise AIServiceError(f"No se pudo procesar la solicitud: {str(e)}")
    
    def _parse_ai_response(self, raw_response: str) -> Dict[str, Any]:
        # Implementar parsing robusto de la respuesta de IA
        # Por ahora, retorno simple
        return {
            "resumen_ejecutivo": raw_response[:200] + "...",
            "kpis_principales": {},
            "recomendaciones": [],
            "vehiculos_destacados": []
        }

class AIServiceError(Exception):
    pass
```

### System Prompts
```python
# app/prompts.py
from typing import Dict, Any

def get_prompt_for_profile(report_data: Dict[str, Any], profile: str) -> str:
    base_prompt = f"""
Analiza el siguiente reporte telemétrico y genera una interpretación detallada:

DATOS DEL REPORTE:
Cliente: {report_data.get('cliente', 'N/A')}
Período: {report_data.get('periodo', 'N/A')}

Indicadores Generales:
- Distancia total: {report_data.get('indicadores', {}).get('distancia_total_km', 0)} km
- Consumo total: {report_data.get('indicadores', {}).get('consumo_total_litros', 0)} litros
- Excesos de velocidad: {report_data.get('indicadores', {}).get('excesos_velocidad', 0)}
- Tiempo en ralentí: {report_data.get('indicadores', {}).get('tiempo_ralenti_minutos', 0)} minutos
- Frenadas bruscas: {report_data.get('indicadores', {}).get('frenadas_bruscas', 0)}

Vehículos analizados: {len(report_data.get('vehiculos', []))}
"""

    if profile == "gerente":
        return base_prompt + """

PERFIL: GERENTE DE FLOTA
Enfócate en:
1. Resumen ejecutivo conciso (2-3 frases)
2. KPIs clave con valores monetarios cuando sea posible
3. 3-5 recomendaciones estratégicas
4. Identificación de vehículos críticos con impacto en costos
5. Oportunidades de ahorro estimadas

Responde en formato estructurado con:
- resumen_ejecutivo
- kpis_principales (diccionario)
- recomendaciones (lista)
- vehiculos_destacados (lista con placa, estado, consumo, recomendación)
"""

    elif profile == "operaciones":
        return base_prompt + """

PERFIL: JEFE DE OPERACIONES
Enfócate en:
1. Análisis técnico detallado
2. Comportamiento específico por vehículo
3. Acciones correctivas inmediatas
4. Patrones de conducción problemáticos
5. Mantenimiento recomendado

Responde en formato estructurado con:
- analisis_tecnico
- vehiculos_detalle
- acciones_correctivas
- patrones_identificados
- mantenimiento_requerido
"""

def format_report_summary(report_data: Dict[str, Any]) -> str:
    """Formatea reporte para mejor visualización en prompts"""
    summary = []
    summary.append(f"📊 **Reporte de {report_data.get('cliente', 'N/A')}**")
    summary.append(f"📅 Período: {report_data.get('periodo', 'N/A')}")
    
    indicators = report_data.get('indicadores', {})
    summary.append(f"🚗 Distancia total: {indicators.get('distancia_total_km', 0):,.0f} km")
    summary.append(f"⛽ Consumo total: {indicators.get('consumo_total_litros', 0):,.0f} L")
    
    if indicators.get('distancia_total_km', 0) > 0:
        efficiency = indicators.get('distancia_total_km', 0) / indicators.get('consumo_total_litros', 1)
        summary.append(f"⚡ Eficiencia promedio: {efficiency:.1f} km/L")
    
    return "\n".join(summary)
```

---

## 🧪 Testing

### Unit Tests
```python
# tests/test_models.py
import pytest
from app.models import TelemetryReport, Vehicle, InterpretRequest

def test_vehicle_validation():
    # Vehículo válido
    vehicle = Vehicle(
        placa="ABC123",
        distancia_km=1000,
        consumo_litros=100,
        excesos_velocidad=5,
        tiempo_ralenti_minutos=60,
        frenadas_bruscas=3
    )
    assert vehicle.consumo_litros == 100
    
    # Vehículo inválido (eficiencia fuera de rango)
    with pytest.raises(ValueError):
        Vehicle(
            placa="BAD123",
            distancia_km=1000,
            consumo_litros=20,  # 50 km/L - demasiado alto
            excesos_velocidad=5,
            tiempo_ralenti_minutos=60,
            frenadas_bruscas=3
        )

def test_telemetry_report_validation():
    report = TelemetryReport(
        cliente="Test Company",
        periodo="01-02-2025 a 07-02-2025",
        indicadores={
            "distancia_total_km": 2000,
            "consumo_total_litros": 200,
            "excesos_velocidad": 10,
            "tiempo_ralenti_minutos": 120,
            "frenadas_bruscas": 6
        },
        vehiculos=[
            Vehicle(
                placa="ABC123",
                distancia_km=1000,
                consumo_litros=100,
                excesos_velocidad=5,
                tiempo_ralenti_minutos=60,
                frenadas_bruscas=3
            ),
            Vehicle(
                placa="DEF456",
                distancia_km=1000,
                consumo_litros=100,
                excesos_velocidad=5,
                tiempo_ralenti_minutos=60,
                frenadas_bruscas=3
            )
        ]
    )
    assert len(report.vehiculos) == 2

def test_inconsistent_totals():
    # Debe fallar por inconsistencia en totales
    with pytest.raises(ValueError):
        TelemetryReport(
            cliente="Test Company",
            periodo="01-02-2025 a 07-02-2025",
            indicadores={
                "distancia_total_km": 3000,  # Inconsistente
                "consumo_total_litros": 200,
                "excesos_velocidad": 10,
                "tiempo_ralenti_minutos": 120,
                "frenadas_bruscas": 6
            },
            vehiculos=[
                Vehicle(
                    placa="ABC123",
                    distancia_km=1000,
                    consumo_litros=100,
                    excesos_velocidad=5,
                    tiempo_ralenti_minutos=60,
                    frenadas_bruscas=3
                )
            ]
        )
```

### Integration Tests
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_health_detailed():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data

def test_interpret_report_gerente():
    request_data = {
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
    }
    
    response = client.post("/interpret", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "interpretation" in data["data"]
    assert "metadata" in data["data"]

def test_invalid_profile():
    request_data = {
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
            "vehiculos": []
        },
        "profile": "invalid_profile"
    }
    
    response = client.post("/interpret", json=request_data)
    assert response.status_code == 422  # Validation error
```

### Test Configuration
```python
# conftest.py
import pytest
import os
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

@pytest.fixture
def mock_groq_service(monkeypatch):
    """Mock del servicio Groq para testing"""
    class MockGroqService:
        async def interpret_report(self, report_data, profile):
            return {
                "resumen_ejecutivo": "Mock interpretation for testing",
                "kpis_principales": {"eficiencia": "6.7 km/L"},
                "recomendaciones": ["Test recommendation"],
                "vehiculos_destacados": []
            }
    
    from app.ai_service import GroqService
    monkeypatch.setattr(GroqService, "__init__", lambda self, api_key, model: None)
    monkeypatch.setattr(GroqService, "interpret_report", MockGroqService.interpret_report)
```

---

## 🔧 Desarrollo Local

### Setup del Entorno
```bash
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
# Editar .env con tu API key

# Iniciar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Scripts de Desarrollo
```bash
# Formatear código
black app/ tests/

# Linting
flake8 app/ tests/

# Ejecutar tests
pytest tests/ -v

# Tests con coverage
pytest tests/ --cov=app --cov-report=html

# Tests específicos
pytest tests/test_models.py -v
pytest tests/test_api.py -v
```

---

## 🚀 Despliegue

### Docker Deployment
```bash
# Construir imagen
docker build -t ai-telematics-backend .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_api_key \
  ai-telematics-backend

# Con docker-compose
docker-compose up -d backend
```

### Production Considerations

#### Environment Variables
```bash
# Producción
DEBUG=false
LOG_LEVEL=info
GROQ_API_KEY=prod_key
CORS_ORIGINS=https://yourdomain.com
```

#### Performance Optimization
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configuración de Uvicorn para producción
# uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

#### Security Headers
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 📊 Monitoring y Logging

### Structured Logging
```python
# app/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
            
        return json.dumps(log_entry)

# Configuración
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Request Logging Middleware
```python
# app/middleware.py
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host
            }
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time
            }
        )
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

---

## 🔒 Security Best Practices

### Input Validation
- **Pydantic Models**: Validación estricta de tipos y rangos
- **SQL Injection Prevention**: No se usa base de datos SQL directa
- **XSS Prevention**: Sanitización de outputs

### API Security
```python
# Rate limiting (ejemplo con slowapi)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/interpret")
@limiter.limit("10/minute")
async def interpret_report(request: Request, ...):
    # ...
```

### Environment Security
```bash
# .env.example (sin secrets reales)
GROQ_API_KEY=your_api_key_here
DEBUG=false
```

---

## 📈 Performance Optimization

### Async Operations
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_multiple_vehicles(vehicles):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(executor, analyze_vehicle, vehicle)
            for vehicle in vehicles
        ]
        results = await asyncio.gather(*tasks)
    return results
```

### Caching
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def get_cached_prompt(report_hash: str, profile: str):
    # Generar prompt cacheado
    pass

def generate_report_hash(report_data: dict) -> str:
    report_str = json.dumps(report_data, sort_keys=True)
    return hashlib.md5(report_str.encode()).hexdigest()
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Groq API Errors
```python
# Manejo robusto de errores de API
class GroqService:
    async def interpret_report_with_retry(self, report_data, profile, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await self.interpret_report(report_data, profile)
            except groq.RateLimitError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except groq.APIError as e:
                raise AIServiceError(f"Groq API error: {str(e)}")
```

#### 2. Validation Errors
```python
# Logging detallado de errores de validación
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Datos de entrada inválidos",
                "details": exc.errors()
            }
        }
    )
```

#### 3. Performance Issues
```python
# Monitoring de performance
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            process_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {process_time:.2f}s")
            return result
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {process_time:.2f}s: {str(e)}")
            raise
    return wrapper
```

---

## 📚 Referencias y Recursos

### Documentación Oficial
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Groq API Documentation](https://console.groq.com/docs)

### Tutoriales y Guías
- [FastAPI User Guide](https://fastapi.tiangolo.com/tutorial/)
- [Async Python Best Practices](https://docs.python.org/3/library/asyncio.html)

### Herramientas de Desarrollo
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [Pytest Testing Framework](https://docs.pytest.org/)
