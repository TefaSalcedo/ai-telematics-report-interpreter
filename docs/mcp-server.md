# MCP Server Guide

## 🤖 ¿Qué es el MCP Server?

El **MCP (Model Context Protocol) Server** es un componente que expone herramientas de análisis telemétrico a través del protocolo MCP, permitiendo que LLMs (Large Language Models) puedan realizar análisis complejos de datos de flotas vehiculares de forma nativa.

### Propósito Principal
- **Integración LLM-Nativa**: Permite que asistentes IA usen herramientas de análisis telemétrico
- **Procesamiento Local**: Análisis avanzado sin depender de APIs externas
- **Estandarización**: Usa el protocolo MCP estándar para comunicación
- **Extensibilidad**: Fácil de agregar nuevas herramientas de análisis

---

## 🏗️ Arquitectura del MCP Server

### Componentes Principales

```
LLM Client
    ↓ [MCP Protocol - JSON-RPC 2.0]
MCP Server (Python)
    ↓ [Tool Selection]
Tool Router
    ↓ [Data Processing]
┌─────────────────┬─────────────────┬─────────────────┐
│   Data          │   Analysis      │   Report        │
│   Validation    │   Engine        │   Generator     │
│                 │                 │                 │
│ • Structure     │ • Performance   │ • Executive     │
│ • Logic         │ • Anomalies     │ • Technical     │
│ • Range         │ • Patterns      │ • Rankings      │
└─────────────────┴─────────────────┴─────────────────┘
```

### Flujo de Comunicación

1. **LLM Request**: El LLM envía una solicitud MCP
2. **Tool Selection**: El servidor selecciona la herramienta apropiada
3. **Data Processing**: Procesa los datos telemétricos
4. **Analysis Execution**: Ejecuta el análisis específico
5. **Response Generation**: Genera respuesta estructurada
6. **MCP Response**: Devuelve resultados al LLM

---

## 🛠️ Herramientas Disponibles

### 1. `validate_telemetry_data`
Valida la estructura y lógica de un reporte telemétrico.

**Uso Típico:**
```python
# LLM puede llamar:
validate_telemetry_data(report_data={
  "cliente": "Empresa ABC",
  "periodo": "01-02-2025 a 07-02-2025",
  "indicadores": {...},
  "vehiculos": [...]
})
```

**Validaciones Realizadas:**
- ✅ Estructura JSON válida
- ✅ Campos obligatorios presentes
- ✅ Tipos de datos correctos
- ✅ Valores en rangos lógicos
- ✅ Consistencia entre campos
- ✅ Formato de fechas correcto

**Respuesta:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Vehículo XYZ789 tiene consumo 40% superior al promedio"
  ],
  "statistics": {
    "total_vehicles": 5,
    "valid_vehicles": 4,
    "invalid_vehicles": 1,
    "data_completeness": "92%"
  }
}
```

### 2. `analyze_performance`
Analiza métricas de rendimiento de combustible.

**Métricas Calculadas:**
- **Eficiencia General**: km/litro promedio de la flota
- **Distribución**: Categorización por rendimiento
- **Comparativas**: Mejores y peores vehículos
- **Tendencias**: Patrones de consumo

**Análisis Detallado:**
```json
{
  "performance_metrics": {
    "fleet_average_km_per_liter": 7.1,
    "efficiency_rating": "Bueno",
    "benchmark_comparison": {
      "industry_average": 6.8,
      "fleet_performance": "+4.4%"
    }
  },
  "vehicle_analysis": {
    "top_performers": [
      {
        "placa": "DEF456",
        "km_per_liter": 8.5,
        "rating": "Excelente",
        "fuel_saved_liters": 25
      }
    ],
    "needs_attention": [
      {
        "placa": "ABC123",
        "km_per_liter": 5.2,
        "rating": "Crítico",
        "excess_consumption_liters": 35
      }
    ]
  },
  "efficiency_distribution": {
    "excellent": 1,
    "good": 2,
    "fair": 1,
    "poor": 1
  }
}
```

### 3. `detect_anomalies`
Detecta anomalías y patrones sospechosos.

**Tipos de Anomalías:**

#### 🚨 Anomalías Críticas
- **Robo de Combustible**: Descargas no autorizadas
- **Fugas**: Consumo anómalo sostenido
- **Sensor Dañado**: Datos imposibles

#### ⚠️ Anomalías de Advertencia
- **Consumo Elevado**: Fuera de rango normal
- **Descargas Repetidas**: Misma ubicación
- **Comportamiento Anómalo**: Patrones inusuales

#### ℹ️ Información
- **Mantenimiento**: Necesidad de servicio
- **Optimización**: Oportunidades de mejora

**Ejemplo de Detección:**
```json
{
  "anomaly_summary": {
    "total_anomalies": 8,
    "severity_breakdown": {
      "critical": 2,
      "warning": 4,
      "info": 2
    },
    "risk_level": "Medio"
  },
  "critical_anomalies": [
    {
      "id": "ANOM001",
      "type": "fuel_theft_suspicion",
      "severity": "critical",
      "vehicle": "ABC123",
      "description": "Descarga de 50L con motor apagado",
      "location": "Depósito Central",
      "timestamp": "2025-02-05T02:30:00Z",
      "confidence": 0.85,
      "estimated_loss": "$45 USD",
      "recommendation": "Investigar inmediatamente"
    }
  ],
  "pattern_analysis": {
    "repeated_locations": [
      {
        "location": "Estación Service X",
        "incidents": 3,
        "pattern": "Descargas nocturnas"
      }
    ],
    "temporal_patterns": [
      {
        "pattern": "Descargas fin de semana",
        "frequency": "Alta",
        "risk": "Medio"
      }
    ]
  }
}
```

### 4. `compare_reports`
Compara datos entre dos proveedores o períodos.

**Comparaciones Realizadas:**
- **Eficiencia**: Rendimiento relativo
- **Consumo**: Uso de combustible
- **Costos**: Impacto económico
- **Tendencias**: Evolución temporal

**Ejemplo de Comparación:**
```json
{
  "comparison_summary": {
    "report_a_name": "Empresa A - Semana 1",
    "report_b_name": "Empresa B - Semana 1",
    "comparison_period": "01-02-2025 a 07-02-2025",
    "overall_winner": "Empresa B",
    "confidence": 0.78
  },
  "metrics_comparison": {
    "efficiency": {
      "a": 7.2,
      "b": 8.1,
      "difference": "+12.5%",
      "winner": "B",
      "significance": "Alta"
    },
    "consumption": {
      "a": 450,
      "b": 420,
      "difference": "-6.7%",
      "winner": "B",
      "savings": "$30 USD"
    },
    "vehicle_count": {
      "a": 10,
      "b": 12,
      "difference": "+20%",
      "context": "B tiene más vehículos"
    }
  },
  "insights": [
    "Empresa B muestra mejor eficiencia general",
    "Empresa A podría optimizar rutas para reducir consumo",
    "Diferencia en tamaño de flota debe considerarse"
  ]
}
```

### 5. `generate_full_report`
Genera un reporte completo con todos los análisis.

**Componentes del Reporte:**
- **Resumen Ejecutivo**: Visión general para gerencia
- **Análisis Técnico**: Detalles para operaciones
- **Rankings**: Clasificación de vehículos
- **Recomendaciones**: Acciones específicas
- **Métricas**: KPIs e indicadores

**Estructura del Reporte:**
```json
{
  "report": {
    "executive_summary": {
      "overview": "La flota muestra rendimiento general bueno con oportunidades de mejora en 3 vehículos críticos.",
      "key_metrics": {
        "total_efficiency": "7.1 km/L",
        "potential_savings": "$2,340/mes",
        "critical_vehicles": 3
      },
      "risk_level": "Medio"
    },
    "performance_analysis": {
      "fleet_metrics": {...},
      "vehicle_rankings": [...],
      "efficiency_trends": [...]
    },
    "anomaly_detection": {
      "summary": {...},
      "detailed_findings": [...],
      "risk_assessment": {...}
    },
    "recommendations": {
      "immediate_actions": [...],
      "short_term_goals": [...],
      "long_term_strategy": [...]
    },
    "metadata": {
      "generated_at": "2025-02-10T14:30:00Z",
      "analysis_version": "1.0.0",
      "data_quality": "92%",
      "processing_time": "2.3s"
    }
  }
}
```

---

## 🚀 Uso del MCP Server

### Iniciar el Servidor

#### Modo Desarrollo
```bash
cd mcp
python -m src.mcp_server
```

#### Modo Producción
```bash
cd mcp
python -m src.mcp_server --log-level INFO --cache-enabled
```

#### con Docker
```bash
docker-compose up mcp-server
```

### Configuración

#### Variables de Entorno
```bash
# Nivel de logging
MCP_LOG_LEVEL=INFO

# Habilitar cache
MCP_CACHE_ENABLED=true

# Tamaño máximo de datos (MB)
MCP_MAX_DATA_SIZE=100

# Timeout de procesamiento (segundos)
MCP_PROCESSING_TIMEOUT=300
```

#### Configuración Avanzada
```python
# src/config.py
MCP_CONFIG = {
    "max_vehicles": 1000,
    "analysis_timeout": 300,
    "cache_ttl": 3600,
    "enable_advanced_analytics": True,
    "confidence_threshold": 0.7
}
```

### Ejemplos de Uso

#### Ejemplo 1: Análisis Básico
```python
# LLM puede solicitar:
result = analyze_performance(report_data={
    "cliente": "Transportes XYZ",
    "periodo": "01-02-2025 a 07-02-2025",
    "indicadores": {
        "distancia_total_km": 5000,
        "consumo_total_litros": 700
    },
    "vehiculos": [...]
})

# El LLM recibe análisis detallado para interpretar
```

#### Ejemplo 2: Detección de Anomalías
```python
# LLM sospecha problemas y solicita análisis:
anomalies = detect_anomalies(report_data)

# Basado en resultados, el LLM puede:
# - Generar alertas específicas
# - Recomendar acciones correctivas
# - Priorizar investigaciones
```

#### Ejemplo 3: Comparación Temporal
```python
# LLM compara rendimiento semanal:
comparison = compare_reports(
    report_a=semana_anterior,
    report_b=semana_actual
)

# El LLM identifica tendencias y cambios
```

---

## 🔧 Integración con LLMs

### Protocolo MCP

#### Mensaje de Request
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "analyze_performance",
    "arguments": {
      "report_data": {...}
    }
  },
  "id": 1
}
```

#### Mensaje de Response
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Análisis completado: Eficiencia promedio de 7.1 km/L..."
      }
    ]
  },
  "id": 1
}
```

### Clientes MCP Soportados

#### Claude Desktop
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "telemetry-analyzer": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/mcp"
    }
  }
}
```

#### Custom LLM Client
```python
from mcp import Client

async def analyze_telemetry(report_data):
    async with Client() as client:
        result = await client.call_tool(
            "analyze_performance",
            {"report_data": report_data}
        )
        return result
```

---

## 📊 Capacidades de Análisis

### Motor de Análisis

#### Algoritmos Implementados
- **Statistical Analysis**: Análisis estadístico básico
- **Anomaly Detection**: Detección de outliers
- **Pattern Recognition**: Identificación de patrones
- **Trend Analysis**: Análisis de tendencias
- **Comparative Analysis**: Análisis comparativo

#### Métricas Calculadas
- **Fuel Efficiency**: km/litro, litros/100km
- **Consumption Patterns**: Patrones de consumo
- **Performance Ratios**: Ratios de rendimiento
- **Anomaly Scores**: Puntajes de anomalía
- **Risk Assessments**: Evaluaciones de riesgo

### Validación de Datos

#### Reglas de Validación
```python
VALIDATION_RULES = {
    "required_fields": ["cliente", "periodo", "indicadores", "vehiculos"],
    "numeric_ranges": {
        "distancia_km": (0, 10000),
        "consumo_litros": (0, 1000),
        "eficiencia_minima": 3.0,
        "eficiencia_maxima": 15.0
    },
    "logical_constraints": {
        "consumo_total": "sum(vehiculos.consumo)",
        "distancia_total": "sum(vehiculos.distancia)",
        "eficiencia_coherente": "distancia/consumo in range"
    }
}
```

#### Calidad de Datos
- **Completeness**: Porcentaje de datos completos
- **Accuracy**: Precisión de los valores
- **Consistency**: Coherencia interna
- **Validity**: Cumplimiento de reglas

---

## 🧪 Testing y Validación

### Tests Unitarios
```bash
cd mcp
python -m pytest tests/ -v
```

### Tests de Integración
```bash
# Test de herramientas MCP
python -m tests.test_mcp_integration

# Test con datos reales
python -m tests.test_real_data_analysis
```

### Benchmarking
```bash
# Performance testing
python -m benchmarks.performance_test

# Load testing
python -m benchmarks.load_test --vehicles 1000
```

---

## 🔍 Monitoring y Debugging

### Logging
```python
# Configuración de logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('mcp_server')
```

### Métricas
- **Processing Time**: Tiempo de análisis
- **Memory Usage**: Uso de memoria
- **Tool Usage**: Frecuencia de uso por herramienta
- **Error Rates**: Tasas de error

### Debug Mode
```bash
# Activar debug
python -m src.mcp_server --debug --verbose

# Ver logs detallados
tail -f logs/mcp_server.log
```

---

## 🚀 Optimización y Performance

### Estrategias de Optimización

#### Caching
```python
# Cache de resultados
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_analysis(report_hash):
    return analyze_performance_internal(report_data)
```

#### Parallel Processing
```python
# Procesamiento paralelo de vehículos
from concurrent.futures import ThreadPoolExecutor

def parallel_vehicle_analysis(vehicles):
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(analyze_vehicle, vehicles))
    return results
```

#### Memory Management
```python
# Streaming para datasets grandes
def stream_analysis(report_data):
    for batch in batch_processor(report_data, batch_size=100):
        yield analyze_batch(batch)
```

### Performance Tips

#### Para Grandes Volúmenes
- Procesar en batches
- Usar generators para streaming
- Implementar caching inteligente
- Monitorear uso de memoria

#### Para Análisis Rápidos
- Pre-calcular métricas comunes
- Usar algoritmos optimizados
- Implementar early exit
- Cache de resultados parciales

---

## 🔒 Seguridad y Privacidad

### Consideraciones de Seguridad
- **Data Privacy**: No almacenar datos sensibles
- **Input Validation**: Validar todos los inputs
- **Error Handling**: No exponer información interna
- **Access Control**: Control de acceso (futuro)

### Best Practices
- Sanitizar inputs de usuarios
- Limitar tamaño de datos
- Implementar rate limiting
- Logging seguro (sin datos sensibles)

---

## 📈 Roadmap Futuro

### Próximas Características

#### v1.1
- [ ] Machine Learning models
- [ ] Real-time analysis
- [ ] Advanced visualizations
- [ ] Mobile API

#### v1.2
- [ ] Multi-tenant support
- [ ] Advanced caching
- [ ] Custom metrics
- [ ] Integration APIs

#### v2.0
- [ ] Distributed processing
- [ ] Cloud deployment
- [ ] Advanced security
- [ ] Enterprise features

### Contribuciones
- **Bug Reports**: GitHub Issues
- **Feature Requests**: GitHub Discussions
- **Pull Requests**: GitHub PRs
- **Documentation**: Markdown files

---

## 📚 Recursos Adicionales

### Documentación
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Python Logging Guide](https://docs.python.org/3/library/logging.html)

### Ejemplos
- `examples/basic_usage.py`
- `examples/advanced_analysis.py`
- `examples/custom_tools.py`

### Community
- [Discord Community](https://discord.gg/mcp)
- [GitHub Discussions](https://github.com/mcp-community/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/mcp)
