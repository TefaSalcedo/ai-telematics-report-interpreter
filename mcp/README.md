# Fleet Telemetry Analyzer

**Sistema de análisis inteligente de datos telemétricos de flotas de transporte**, enfocado en sensores de combustible.

Construido como un **MCP Server** (Model Context Protocol) y herramienta CLI en Python.

---

## Características

- **Validación de datos**: Detecta claves faltantes, valores negativos, consumos fuera de rango, subtotales inconsistentes, unidades duplicadas y fechas mal formateadas.
- **Análisis de rendimiento**: Calcula km/gal, desviación de consumo, variación entre periodos, ratio de ralentí.
- **Detección de anomalías**:
  - Descargas repetidas en la misma ubicación
  - Descargas con motor apagado (especialmente nocturnas)
  - Fugas graduales (descargas pequeñas frecuentes)
  - Cargas no autorizadas (ratio cargas/viajes, volúmenes atípicos)
  - Problemas de sensor (saltos imposibles, regresión de odómetro)
  - Patrones temporales y geográficos
- **Comparación multiempresa**: Compara métricas entre dos proveedores de datos.
- **Reportes automáticos**: Resumen ejecutivo, hallazgos clave, ranking de vehículos críticos, recomendaciones.

---

## Estructura del Proyecto

```
mcp-mini/
├── src/
│   ├── models/
│   │   └── telemetry.py        # Pydantic models
│   ├── validators/
│   │   └── data_validator.py   # Data validation
│   ├── analyzers/
│   │   ├── performance_analyzer.py  # Performance metrics
│   │   ├── anomaly_detector.py      # Anomaly detection
│   │   └── company_comparator.py    # Multi-company comparison
│   ├── reports/
│   │   └── report_generator.py # Report generation
│   ├── utils/
│   │   └── helpers.py          # Utility functions
│   ├── main.py                 # CLI entry point
│   └── mcp_server.py           # MCP server
├── tests/
│   ├── test_validators.py
│   ├── test_analyzers.py
│   └── test_utils.py
├── data/
│   └── sample_report.json      # Sample telemetry data
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Ejecución con Docker

### Análisis CLI (recomendado)

```bash
docker compose up analyzer
```

### Ejecutar tests

```bash
docker compose up tests
```

### MCP Server (para integración con LLMs)

```bash
docker compose up mcp-server
```

### Construir la imagen

```bash
docker compose build
```

---

## Ejecución Local (sin Docker)

### Requisitos

- Python 3.10+

### Instalación

```bash
pip install -r requirements.txt
```

### Análisis de datos

```bash
python -m src.main data/sample_report.json
```

### Comparación multiempresa

```bash
python -m src.main data/report_a.json --compare data/report_b.json
```

### Ejecutar tests

```bash
python -m pytest tests/ -v
```

### Iniciar MCP Server

```bash
python -m src.mcp_server
```

---

## MCP Tools Disponibles

| Tool | Descripción |
|------|-------------|
| `validate_telemetry_data` | Valida estructura y lógica de un reporte JSON |
| `analyze_performance` | Analiza métricas de rendimiento de combustible |
| `detect_anomalies` | Detecta anomalías en descargas, cargas, sensores y patrones |
| `compare_reports` | Compara datos entre dos proveedores |
| `generate_full_report` | Genera reporte completo con todos los análisis |

---

## Reglas de Negocio

- Desviación de consumo > 10% → **Alerta amarilla**
- Desviación de consumo > 20% → **Alerta roja**
- Descarga con motor apagado en horario nocturno → **Alerta roja**
- Descargas repetidas en la misma ubicación → **Alerta roja** (3+) o **amarilla** (2)
- Nivel de combustible post-carga excede capacidad del tanque → **Alerta roja**

---

## Tecnologías

- **Python 3.12** (compatible con 3.10+)
- **Pydantic v2** — Validación y modelos de datos
- **MCP SDK (FastMCP)** — Servidor Model Context Protocol
- **pytest** — Tests unitarios
- **Docker** — Contenedorización
