# AI Telematics Report Interpreter

Prototipo de prueba de concepto que demuestra cómo la inteligencia artificial puede interpretar reportes de telemetría vehicular y generar insights personalizados según el perfil del usuario.

## Estructura del Proyecto

```
ai-mini/
├── backend/                    # API en Python + FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # Endpoints de la API
│   │   ├── models.py           # Modelos de datos (Pydantic)
│   │   ├── prompts.py          # Prompts para cada perfil
│   │   └── ai_service.py       # Servicio de conexión con Groq (FREE)
│   ├── .env.example            # Plantilla de variables de entorno
│   ├── requirements.txt        # Dependencias de Python
│   └── Dockerfile
├── frontend/                   # Interfaz en React
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js            # Punto de entrada
│   │   ├── index.css           # Estilos globales
│   │   └── App.js              # Componente principal
│   ├── package.json
│   └── Dockerfile
├── sample_report.json          # Datos de ejemplo
├── docker-compose.yml          # Orquestación de contenedores
└── AI_TELEMATICS_README.md     # Este archivo
```

## Requisitos Previos

- **Docker Desktop** instalado y corriendo
- **API Key de Groq (GRATIS)** (obtener en https://console.groq.com/keys)

## Instalación y Ejecución

### Paso 1: Configurar la API Key

Crea el archivo `backend/.env` copiando el ejemplo:

```bash
cp backend/.env.example backend/.env
```

Edita `backend/.env` y reemplaza con tu API key real de Groq:

```
GROQ_API_KEY=gsk_tu-api-key-real-aqui
GROQ_MODEL=llama-3.3-70b-versatile
```

### Paso 2: Levantar con Docker

```bash
docker-compose up --build
```

Esto levantará:
- **Backend** en http://localhost:8000
- **Frontend** en http://localhost:3001

### Paso 3: Usar la aplicación

1. Abre http://localhost:3001 en tu navegador
2. Verás el JSON de ejemplo precargado
3. Selecciona un perfil: **Gerente de Flota** o **Jefe de Operaciones**
4. Presiona **"Interpretar con AI"**
5. Espera unos segundos y verás el análisis generado

## Ejecución Sin Docker (Opcional)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu API key
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## API Endpoints

| Método | Ruta         | Descripción                          |
|--------|-------------|--------------------------------------|
| GET    | `/`         | Health check                         |
| GET    | `/health`   | Health check para Docker             |
| POST   | `/interpret` | Interpreta un reporte con AI        |

### Ejemplo de petición POST /interpret

```json
{
  "report": {
    "cliente": "Empresa Demo",
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
        "excesos_velocidad": 7
      }
    ]
  },
  "profile": "gerente"
}
```

## Perfiles de Interpretación

### Gerente de Flota
- Lenguaje ejecutivo y conciso
- Enfoque en costos y ROI
- Resúmenes cortos con KPIs clave
- Recomendaciones estratégicas

### Jefe de Operaciones
- Lenguaje técnico y detallado
- Análisis vehículo por vehículo
- Enfoque en comportamiento de conductores
- Acciones correctivas concretas

## Tecnologías

- **Backend**: Python 3.12, FastAPI, Groq API (FREE), Pydantic
- **Frontend**: React 18, Lucide Icons, React Markdown
- **Infraestructura**: Docker, Docker Compose

## Notas

- Este proyecto **NO** se conecta a Wialon. Usa datos simulados.
- El modelo por defecto es `llama-3.3-70b-versatile` (gratuito y potente via Groq).
- Otros modelos disponibles en Groq: `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, `gemma2-9b-it`.
- La documentación automática de la API está en http://localhost:8000/docs
