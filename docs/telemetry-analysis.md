# Telemetry Analysis Documentation

## 📊 Análisis Telemétrico Avanzado

El sistema de análisis telemétrico del proyecto AI Telematics proporciona capacidades avanzadas para el procesamiento, validación e interpretación de datos de flotas vehicuales, con especial énfasis en el análisis de consumo de combustible y detección de anomalías.

---

## 🎯 Objetivos del Sistema de Análisis

### Propósitos Principales
- **Validación de Datos**: Asegurar calidad y consistencia de los reportes
- **Análisis de Rendimiento**: Evaluar eficiencia operativa de la flota
- **Detección de Anomalías**: Identificar patrones sospechosos y posibles fraudes
- **Generación de Insights**: Proporcionar información accionable para la toma de decisiones
- **Comparación Multiempresa**: Benchmarking entre diferentes proveedores

---

## 📋 Estructura de Datos Telemétricos

### Formato del Reporte
```json
{
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
}
```

### Tipos de Eventos
```json
{
  "tipos_eventos": {
    "carga_combustible": "Recarga de combustible",
    "descarga_combustible": "Consumo/descarga",
    "exceso_velocidad": "Velocidad excedida",
    "frenada_brusca": "Frenado repentino",
    "ralenti": "Motor en ralentí",
    "mantenimiento": "Servicio técnico",
    "geocerca_violada": "Salida de zona permitida"
  }
}
```

---

## 🔍 Sistema de Validación

### Reglas de Validación Estructural
```python
# src/validators/data_validator.py
class TelemetryValidator:
    def __init__(self):
        self.validation_rules = {
            'required_fields': {
                'report': ['cliente', 'periodo', 'indicadores', 'vehiculos'],
                'indicadores': ['distancia_total_km', 'consumo_total_litros'],
                'vehicle': ['placa', 'distancia_km', 'consumo_litros']
            },
            'numeric_ranges': {
                'distancia_km': (0, 10000),
                'consumo_litros': (0, 1000),
                'eficiencia_km_per_liter': (3.0, 15.0),
                'velocidad_maxima': (0, 200),
                'tiempo_ralenti': (0, 1440)  # minutos por día
            },
            'logical_constraints': {
                'total_consistency': 'sum(vehiculos.consumo) ≈ indicadores.consumo_total',
                'distance_consistency': 'sum(vehiculos.distancia) ≈ indicadores.distancia_total',
                'efficiency_coherence': 'distancia/consumo in valid_range',
                'temporal_sequence': 'eventos.timestamp en orden cronológico'
            }
        }
    
    def validate_report(self, report_data):
        """Validación completa del reporte telemétrico"""
        validation_result = ValidationResult()
        
        # 1. Validación estructural
        self._validate_structure(report_data, validation_result)
        
        # 2. Validación de rangos
        self._validate_ranges(report_data, validation_result)
        
        # 3. Validación lógica
        self._validate_logic(report_data, validation_result)
        
        # 4. Validación de consistencia
        self._validate_consistency(report_data, validation_result)
        
        return validation_result
```

### Tipos de Errores de Validación
```python
class ValidationErrorType:
    MISSING_FIELD = "missing_field"
    INVALID_TYPE = "invalid_type"
    OUT_OF_RANGE = "out_of_range"
    LOGICAL_INCONSISTENCY = "logical_inconsistency"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    DUPLICATE_DATA = "duplicate_data"

class ValidationError:
    def __init__(self, type, field, message, severity="error"):
        self.type = type
        self.field = field
        self.message = message
        self.severity = severity  # error, warning, info
        self.timestamp = datetime.utcnow()
```

### Ejemplos de Validación
```python
# Validación de eficiencia de combustible
def validate_fuel_efficiency(vehicle):
    """Valida que la eficiencia de combustible sea realista"""
    efficiency = vehicle.distancia_km / vehicle.consumo_litros
    
    if efficiency < 3.0:
        return ValidationError(
            type=ValidationErrorType.OUT_OF_RANGE,
            field="eficiencia_combustible",
            message=f"Eficiencia demasiado baja: {efficiency:.1f} km/L (mínimo: 3.0 km/L)",
            severity="error"
        )
    elif efficiency > 15.0:
        return ValidationError(
            type=ValidationErrorType.OUT_OF_RANGE,
            field="eficiencia_combustible",
            message=f"Eficiencia irrealmente alta: {efficiency:.1f} km/L (máximo: 15.0 km/L)",
            severity="warning"
        )
    
    return None

# Validación de consistencia temporal
def validate_temporal_sequence(events):
    """Valida que los eventos estén en orden cronológico"""
    if not events:
        return []
    
    errors = []
    prev_timestamp = None
    
    for i, event in enumerate(events):
        try:
            current_timestamp = datetime.fromisoformat(event['timestamp'])
            
            if prev_timestamp and current_timestamp < prev_timestamp:
                errors.append(ValidationError(
                    type=ValidationErrorType.TEMPORAL_ANOMALY,
                    field=f"eventos[{i}].timestamp",
                    message=f"Evento fuera de secuencia temporal: {event['timestamp']}",
                    severity="warning"
                ))
            
            prev_timestamp = current_timestamp
            
        except ValueError:
            errors.append(ValidationError(
                type=ValidationErrorType.INVALID_TYPE,
                field=f"eventos[{i}].timestamp",
                message=f"Formato de timestamp inválido: {event['timestamp']}",
                severity="error"
            ))
    
    return errors
```

---

## 📈 Análisis de Rendimiento

### Métricas de Eficiencia
```python
# src/analyzers/performance_analyzer.py
class PerformanceAnalyzer:
    def __init__(self):
        self.benchmarks = {
            'industry_average_km_per_liter': 6.8,
            'excellent_efficiency': 8.5,
            'good_efficiency': 7.0,
            'acceptable_efficiency': 5.5,
            'poor_efficiency': 4.0
        }
    
    def analyze_fleet_performance(self, report_data):
        """Análisis completo del rendimiento de la flota"""
        analysis = PerformanceAnalysis()
        
        # 1. Eficiencia general de la flota
        analysis.fleet_efficiency = self._calculate_fleet_efficiency(report_data)
        
        # 2. Análisis por vehículo
        analysis.vehicle_analysis = self._analyze_vehicles(report_data.vehiculos)
        
        # 3. Distribución de eficiencia
        analysis.efficiency_distribution = self._calculate_distribution(report_data.vehiculos)
        
        # 4. Comparación con benchmarks
        analysis.benchmark_comparison = self._compare_with_benchmarks(analysis.fleet_efficiency)
        
        # 5. Tendencias y patrones
        analysis.trends = self._identify_trends(report_data.vehiculos)
        
        return analysis
    
    def _calculate_fleet_efficiency(self, report_data):
        """Calcula eficiencia promedio de la flota"""
        total_distance = report_data.indicadores.distancia_total_km
        total_consumption = report_data.indicadores.consumo_total_litros
        
        if total_consumption == 0:
            return 0
        
        fleet_efficiency = total_distance / total_consumption
        
        return {
            'km_per_liter': fleet_efficiency,
            'liters_per_100km': (100 / fleet_efficiency) if fleet_efficiency > 0 else 0,
            'rating': self._get_efficiency_rating(fleet_efficiency),
            'percentile': self._calculate_percentile(fleet_efficiency)
        }
    
    def _analyze_vehicles(self, vehicles):
        """Análisis individual de cada vehículo"""
        vehicle_analysis = []
        
        for vehicle in vehicles:
            efficiency = vehicle.distancia_km / vehicle.consumo_litros
            
            analysis = {
                'placa': vehicle.placa,
                'efficiency_km_per_liter': efficiency,
                'efficiency_rating': self._get_efficiency_rating(efficiency),
                'performance_vs_average': self._compare_with_fleet_average(efficiency, vehicles),
                'fuel_cost_estimate': self._estimate_fuel_cost(vehicle),
                'potential_savings': self._calculate_potential_savings(vehicle, vehicles),
                'ranking_position': 0,  # Se calculará después
                'anomalies': self._detect_vehicle_anomalies(vehicle)
            }
            
            vehicle_analysis.append(analysis)
        
        # Ordenar por eficiencia y asignar rankings
        vehicle_analysis.sort(key=lambda x: x['efficiency_km_per_liter'], reverse=True)
        for i, vehicle in enumerate(vehicle_analysis):
            vehicle['ranking_position'] = i + 1
        
        return vehicle_analysis
    
    def _get_efficiency_rating(self, efficiency):
        """Clasifica la eficiencia en categorías"""
        if efficiency >= self.benchmarks['excellent_efficiency']:
            return 'Excelente'
        elif efficiency >= self.benchmarks['good_efficiency']:
            return 'Bueno'
        elif efficiency >= self.benchmarks['acceptable_efficiency']:
            return 'Aceptable'
        elif efficiency >= self.benchmarks['poor_efficiency']:
            return 'Pobre'
        else:
            return 'Crítico'
```

### Análisis de Patrones de Conducción
```python
class DrivingPatternAnalyzer:
    def analyze_driving_patterns(self, vehicles):
        """Analiza patrones de conducción de la flota"""
        patterns = DrivingPatterns()
        
        # 1. Patrones de velocidad
        patterns.speed_patterns = self._analyze_speed_patterns(vehicles)
        
        # 2. Patrones de ralentí
        patterns.idling_patterns = self._analyze_idling_patterns(vehicles)
        
        # 3. Patrones de frenado
        patterns.braking_patterns = self._analyze_braking_patterns(vehicles)
        
        # 4. Patrones temporales
        patterns.temporal_patterns = self._analyze_temporal_patterns(vehicles)
        
        # 5. Patrones geográficos
        patterns.geographic_patterns = self._analyze_geographic_patterns(vehicles)
        
        return patterns
    
    def _analyze_speed_patterns(self, vehicles):
        """Analiza patrones de excesos de velocidad"""
        total_excesses = sum(v.excesos_velocidad for v in vehicles)
        total_distance = sum(v.distancia_km for v in vehicles)
        
        if total_distance == 0:
            excess_rate = 0
        else:
            excess_rate = (total_excesses / total_distance) * 100  # excesos por 100km
        
        return {
            'total_excesses': total_excesses,
            'excess_rate_per_100km': excess_rate,
            'severity_rating': self._get_speed_severity(excess_rate),
            'worst_offenders': self._get_worst_speed_offenders(vehicles),
            'recommendations': self._generate_speed_recommendations(excess_rate)
        }
    
    def _analyze_idling_patterns(self, vehicles):
        """Analiza patrones de tiempo en ralentí"""
        total_idling = sum(v.tiempo_ralenti_minutos for v in vehicles)
        total_distance = sum(v.distancia_km for v in vehicles)
        
        if total_distance == 0:
            idling_rate = 0
        else:
            idling_rate = (total_idling / (total_distance * 60)) * 100  # porcentaje de tiempo
        
        return {
            'total_idling_minutes': total_idling,
            'idling_percentage': idling_rate,
            'estimated_fuel_waste': self._estimate_idling_fuel_waste(total_idling),
            'cost_impact': self._calculate_idling_cost_impact(total_idling),
            'improvement_potential': self._calculate_idling_improvement_potential(total_idling)
        }
```

---

## 🚨 Detección de Anomalías

### Tipos de Anomalías Detectadas
```python
class AnomalyType:
    FUEL_THEFT = "fuel_theft"
    FUEL_LEAK = "fuel_leak"
    SENSOR_MALFUNCTION = "sensor_malfunction"
    DATA_MANIPULATION = "data_manipulation"
    UNUSUAL_CONSUMPTION = "unusual_consumption"
    REPEATED_REFUELING = "repeated_refueling"
    NIGHT_ACTIVITY = "night_activity"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    TEMPORAL_ANOMALY = "temporal_anomaly"
    PERFORMANCE_ANOMALY = "performance_anomaly"

class AnomalyDetector:
    def __init__(self):
        self.anomaly_thresholds = {
            'fuel_theft_confidence': 0.7,
            'efficiency_deviation_percent': 20,
            'unusual_location_frequency': 3,
            'night_operation_hours': (22, 6),  # 10pm - 6am
            'sensor_impossibility_threshold': 50  # km/h instantáneo
        }
    
    def detect_anomalies(self, report_data):
        """Detección completa de anomalías en el reporte"""
        detection_result = AnomalyDetectionResult()
        
        # 1. Anomalías de combustible
        detection_result.fuel_anomalies = self._detect_fuel_anomalies(report_data)
        
        # 2. Anomalías de sensor
        detection_result.sensor_anomalies = self._detect_sensor_anomalies(report_data)
        
        # 3. Anomalías temporales
        detection_result.temporal_anomalies = self._detect_temporal_anomalies(report_data)
        
        # 4. Anomalías geográficas
        detection_result.geographic_anomalies = self._detect_geographic_anomalies(report_data)
        
        # 5. Anomalías de rendimiento
        detection_result.performance_anomalies = self._detect_performance_anomalies(report_data)
        
        # 6. Análisis de patrones sospechosos
        detection_result.suspicious_patterns = self._detect_suspicious_patterns(report_data)
        
        return detection_result
```

### Detección de Robo de Combustible
```python
def _detect_fuel_theft(self, report_data):
    """Detecta posibles robos de combustible"""
    theft_anomalies = []
    
    for vehicle in report_data.vehiculos:
        if not vehicle.eventos:
            continue
        
        # Buscar descargas sospechosas
        suspicious_discharges = self._find_suspicious_discharges(vehicle)
        
        for discharge in suspicious_discharges:
            anomaly = Anomaly(
                type=AnomalyType.FUEL_THEFT,
                vehicle=vehicle.placa,
                severity=self._calculate_theft_severity(discharge),
                description=self._generate_theft_description(discharge),
                evidence=discharge,
                confidence=discharge.get('confidence', 0.5),
                estimated_loss=self._estimate_fuel_loss(discharge),
                recommendations=self._generate_theft_recommendations(discharge)
            )
            
            theft_anomalies.append(anomaly)
    
    return theft_anomalies

def _find_suspicious_discharges(self, vehicle):
    """Busca descargas de combustible sospechosas"""
    suspicious = []
    
    for event in vehicle.eventos:
        if event['tipo'] != 'descarga_combustible':
            continue
        
        # Criterios de sospecha:
        # 1. Descarga con motor apagado
        # 2. Descarga en horario nocturno
        # 3. Descarga en ubicación no autorizada
        # 4. Descarga de volumen anómalo
        # 5. Múltiples descargas en misma ubicación
        
        suspicion_score = 0
        reasons = []
        
        # Análisis temporal
        event_time = datetime.fromisoformat(event['timestamp'])
        if self._is_night_hours(event_time):
            suspicion_score += 0.3
            reasons.append('Descarga en horario nocturno')
        
        # Análisis de ubicación
        if self._is_unauthorized_location(event['ubicacion']):
            suspicion_score += 0.4
            reasons.append('Ubicación no autorizada')
        
        # Análisis de volumen
        if event['valor'] > 100:  # Más de 100L es sospechoso
            suspicion_score += 0.2
            reasons.append('Volumen anómalo')
        
        if suspicion_score >= 0.5:
            suspicious.append({
                **event,
                'suspicion_score': suspicion_score,
                'reasons': reasons,
                'confidence': min(suspicion_score * 1.2, 1.0)
            })
    
    return suspicious
```

### Detección de Fallas de Sensor
```python
def _detect_sensor_malfunctions(self, report_data):
    """Detecta posibles fallas en sensores telemétricos"""
    sensor_anomalies = []
    
    for vehicle in report_data.vehiculos:
        anomalies = []
        
        # 1. Saltos imposibles en odómetro
        odometer_anomalies = self._detect_odometer_anomalies(vehicle)
        anomalies.extend(odometer_anomalies)
        
        # 2. Regresión en odómetro
        regression_anomalies = self._detect_odometer_regression(vehicle)
        anomalies.extend(regression_anomalies)
        
        # 3. Valores fuera de rango físico
        range_anomalies = self._detect_physical_range_anomalies(vehicle)
        anomalies.extend(range_anomalies)
        
        # 4. Datos inconsistentes
        inconsistency_anomalies = self._detect_data_inconsistencies(vehicle)
        anomalies.extend(inconsistency_anomalies)
        
        if anomalies:
            sensor_anomalies.append({
                'vehicle': vehicle.placa,
                'anomalies': anomalies,
                'sensor_health_score': self._calculate_sensor_health_score(anomalies),
                'recommendations': self._generate_sensor_recommendations(anomalies)
            })
    
    return sensor_anomalies
```

### Detección de Patrones Sospechosos
```python
def _detect_suspicious_patterns(self, report_data):
    """Detecta patrones de comportamiento sospechoso"""
    patterns = []
    
    # 1. Patrones de recarga frecuentes
    frequent_refueling = self._detect_frequent_refueling_pattern(report_data)
    if frequent_refueling:
        patterns.append(frequent_refueling)
    
    # 2. Patrones de consumo anómalo
    consumption_patterns = self._detect_anomalous_consumption_patterns(report_data)
    patterns.extend(consumption_patterns)
    
    # 3. Patrones geográficos sospechosos
    geographic_patterns = self._detect_suspicious_geographic_patterns(report_data)
    patterns.extend(geographic_patterns)
    
    # 4. Patrones temporales irregulares
    temporal_patterns = self._detect_irregular_temporal_patterns(report_data)
    patterns.extend(temporal_patterns)
    
    # 5. Patrones de comportamiento coordinado
    coordinated_patterns = self._detect_coordinated_behavior_patterns(report_data)
    patterns.extend(coordinated_patterns)
    
    return patterns
```

---

## 📊 Generación de Reportes

### Estructura del Reporte de Análisis
```python
class ReportGenerator:
    def __init__(self):
        self.report_templates = {
            'executive': ExecutiveReportTemplate(),
            'technical': TechnicalReportTemplate(),
            'operational': OperationalReportTemplate(),
            'compliance': ComplianceReportTemplate()
        }
    
    def generate_comprehensive_report(self, report_data, analysis_results, format='json'):
        """Genera reporte completo con todos los análisis"""
        report = ComprehensiveReport()
        
        # 1. Metadatos del reporte
        report.metadata = self._generate_metadata(report_data)
        
        # 2. Resumen ejecutivo
        report.executive_summary = self._generate_executive_summary(analysis_results)
        
        # 3. Análisis de rendimiento
        report.performance_analysis = analysis_results.performance
        
        # 4. Detección de anomalías
        report.anomaly_detection = analysis_results.anomalies
        
        # 5. Análisis de tendencias
        report.trend_analysis = self._generate_trend_analysis(analysis_results)
        
        # 6. Rankings y comparativas
        report.rankings = self._generate_rankings(analysis_results.performance)
        
        # 7. Recomendaciones
        report.recommendations = self._generate_recommendations(analysis_results)
        
        # 8. Apéndices técnicos
        report.technical_appendices = self._generate_technical_appendices(analysis_results)
        
        return self._format_report(report, format)
    
    def _generate_executive_summary(self, analysis_results):
        """Genera resumen ejecutivo para gerencia"""
        summary = ExecutiveSummary()
        
        # KPIs clave
        summary.key_metrics = {
            'total_vehicles': len(analysis_results.performance.vehicle_analysis),
            'fleet_efficiency': analysis_results.performance.fleet_efficiency['km_per_liter'],
            'critical_anomalies': len([a for a in analysis_results.anomalies.fuel_anomalies if a.severity == 'critical']),
            'potential_savings': self._calculate_total_potential_savings(analysis_results),
            'risk_level': self._calculate_overall_risk_level(analysis_results)
        }
        
        # Hallazgos principales
        summary.key_findings = self._extract_key_findings(analysis_results)
        
        # Recomendaciones estratégicas
        summary.strategic_recommendations = self._generate_strategic_recommendations(analysis_results)
        
        return summary
```

### Visualización de Resultados
```python
class VisualizationGenerator:
    def generate_performance_charts(self, performance_analysis):
        """Genera gráficos de rendimiento"""
        charts = {}
        
        # 1. Gráfico de eficiencia por vehículo
        charts['efficiency_by_vehicle'] = self._create_efficiency_chart(performance_analysis.vehicle_analysis)
        
        # 2. Distribución de eficiencia
        charts['efficiency_distribution'] = self._create_distribution_chart(performance_analysis.efficiency_distribution)
        
        # 3. Comparación con benchmarks
        charts['benchmark_comparison'] = self._create_benchmark_chart(performance_analysis.benchmark_comparison)
        
        # 4. Tendencias temporales
        charts['performance_trends'] = self._create_trends_chart(performance_analysis.trends)
        
        return charts
    
    def generate_anomaly_charts(self, anomaly_detection):
        """Genera gráficos de anomalías"""
        charts = {}
        
        # 1. Gráfico de severidad de anomalías
        charts['anomaly_severity'] = self._create_severity_chart(anomaly_detection)
        
        # 2. Mapa de anomalías geográficas
        charts['anomaly_map'] = self._create_anomaly_map(anomaly_detection.geographic_anomalies)
        
        # 3. Línea de tiempo de anomalías
        charts['anomaly_timeline'] = self._create_timeline_chart(anomaly_detection.temporal_anomalies)
        
        return charts
```

---

## 🔧 Configuración y Personalización

### Configuración de Análisis
```python
# src/config/analysis_config.py
ANALYSIS_CONFIG = {
    'validation': {
        'strict_mode': True,
        'tolerance_percent': 5,
        'required_completeness': 0.9
    },
    'performance': {
        'benchmarks': {
            'industry_average_km_per_liter': 6.8,
            'excellent_efficiency': 8.5,
            'good_efficiency': 7.0,
            'acceptable_efficiency': 5.5
        },
        'efficiency_ratings': {
            'excellent': (8.5, 15.0),
            'good': (7.0, 8.5),
            'acceptable': (5.5, 7.0),
            'poor': (4.0, 5.5),
            'critical': (0.0, 4.0)
        }
    },
    'anomaly_detection': {
        'fuel_theft': {
            'night_hours': (22, 6),
            'suspicious_volume_threshold': 100,
            'confidence_threshold': 0.7
        },
        'sensor_malfunction': {
            'odometer_jump_threshold': 100,  # km
            'physical_speed_limit': 200,     # km/h
            'efficiency_deviation_percent': 30
        }
    },
    'reporting': {
        'include_technical_details': True,
        'generate_visualizations': True,
        'export_formats': ['json', 'pdf', 'excel'],
        'language': 'es'
    }
}
```

### Personalización por Industria
```python
class IndustrySpecificAnalyzer:
    def __init__(self, industry_type):
        self.industry_type = industry_type
        self.config = self._load_industry_config(industry_type)
    
    def _load_industry_config(self, industry_type):
        """Carga configuración específica de la industria"""
        configs = {
            'transport': {
                'efficiency_benchmarks': {
                    'heavy_trucks': {'excellent': 4.0, 'good': 3.2, 'acceptable': 2.5},
                    'light_vehicles': {'excellent': 12.0, 'good': 10.0, 'acceptable': 8.0},
                    'motorcycles': {'excellent': 25.0, 'good': 20.0, 'acceptable': 15.0}
                },
                'anomaly_thresholds': {
                    'fuel_theft_confidence': 0.8,
                    'unusual_idle_time': 180  # minutos
                }
            },
            'construction': {
                'efficiency_benchmarks': {
                    'heavy_machinery': {'excellent': 2.5, 'good': 2.0, 'acceptable': 1.5},
                    'light_equipment': {'excellent': 8.0, 'good': 6.5, 'acceptable': 5.0}
                },
                'anomaly_thresholds': {
                    'fuel_theft_confidence': 0.6,
                    'unusual_idle_time': 240
                }
            },
            'delivery': {
                'efficiency_benchmarks': {
                    'delivery_vans': {'excellent': 10.0, 'good': 8.5, 'acceptable': 7.0},
                    'motorcycles': {'excellent': 30.0, 'good': 25.0, 'acceptable': 20.0}
                },
                'anomaly_thresholds': {
                    'fuel_theft_confidence': 0.7,
                    'unusual_idle_time': 120
                }
            }
        }
        
        return configs.get(industry_type, configs['transport'])
```

---

## 📈 Métricas y KPIs

### KPIs de Rendimiento
```python
class KPICalculator:
    def calculate_fleet_kpis(self, report_data, analysis_results):
        """Calcula KPIs clave para la flota"""
        kpis = {}
        
        # KPIs de eficiencia
        kpis['efficiency'] = {
            'fleet_average_km_per_liter': analysis_results.performance.fleet_efficiency['km_per_liter'],
            'efficiency_trend': self._calculate_efficiency_trend(analysis_results),
            'efficiency_variance': self._calculate_efficiency_variance(analysis_results),
            'top_performer_percentage': self._calculate_top_performer_percentage(analysis_results),
            'underperformer_percentage': self._calculate_underperformer_percentage(analysis_results)
        }
        
        # KPIs operativos
        kpis['operational'] = {
            'total_distance_km': report_data.indicadores.distancia_total_km,
            'total_consumption_liters': report_data.indicadores.consumo_total_litros,
            'total_operating_hours': self._estimate_operating_hours(report_data),
            'vehicle_utilization_rate': self._calculate_utilization_rate(report_data),
            'idle_time_percentage': self._calculate_idle_time_percentage(report_data)
        }
        
        # KPIs de seguridad
        kpis['safety'] = {
            'speeding_incidents_per_1000km': self._calculate_speeding_rate(report_data),
            'harsh_braking_events_per_1000km': self._calculate_braking_rate(report_data),
            'safety_score': self._calculate_safety_score(report_data),
            'at_risk_vehicles': self._count_at_risk_vehicles(analysis_results)
        }
        
        # KPIs de costo
        kpis['cost'] = {
            'estimated_fuel_cost': self._estimate_fuel_cost(report_data),
            'cost_per_km': self._calculate_cost_per_km(report_data),
            'potential_savings_monthly': self._calculate_potential_savings(analysis_results),
            'anomaly_cost_impact': self._calculate_anomaly_cost_impact(analysis_results)
        }
        
        # KPIs de calidad de datos
        kpis['data_quality'] = {
            'completeness_percentage': self._calculate_data_completeness(report_data),
            'consistency_score': self._calculate_data_consistency(report_data),
            'validation_error_count': len(analysis_results.validation.errors),
            'data_quality_grade': self._calculate_data_quality_grade(analysis_results.validation)
        }
        
        return kpis
```

---

## 🚀 Integración y Uso

### Uso vía MCP Server
```python
# Ejemplo de uso del análisis telemétrico
from src.mcp_server import TelemetryMCPServer

# Iniciar servidor MCP
server = TelemetryMCPServer()

# Cliente puede llamar herramientas:
result = server.call_tool('analyze_performance', {
    'report_data': telemetry_report
})

# Resultado incluye análisis completo
print(result['performance_metrics'])
print(result['anomaly_detection'])
print(result['recommendations'])
```

### Uso Directo (Python)
```python
from src.analyzers.performance_analyzer import PerformanceAnalyzer
from src.analyzers.anomaly_detector import AnomalyDetector
from src.reports.report_generator import ReportGenerator

# Cargar datos
with open('telemetry_report.json', 'r') as f:
    report_data = json.load(f)

# Análisis de rendimiento
performance_analyzer = PerformanceAnalyzer()
performance_results = performance_analyzer.analyze_fleet_performance(report_data)

# Detección de anomalías
anomaly_detector = AnomalyDetector()
anomaly_results = anomaly_detector.detect_anomalies(report_data)

# Generar reporte
report_generator = ReportGenerator()
comprehensive_report = report_generator.generate_comprehensive_report(
    report_data, 
    {'performance': performance_results, 'anomalies': anomaly_results}
)
```

---

## 🔮 Futuras Mejoras

### Próximas Características
- **Machine Learning**: Modelos predictivos de mantenimiento
- **Análisis Predictivo**: Anticipación de fallas
- **Integración GPS**: Análisis geográfico avanzado
- **Análisis de Conductores**: Perfiles de comportamiento
- **Integración ERP**: Conexión con sistemas de gestión

### Mejoras Técnicas
- **Procesamiento en Tiempo Real**: Streaming de datos
- **Análisis de Big Data**: Procesamiento de grandes volúmenes
- **Visualización Interactiva**: Dashboards dinámicos
- **Alertas Automáticas**: Notificaciones en tiempo real
- **API RESTful**: Integración con sistemas externos

---

## 📚 Referencias y Recursos

### Documentación Técnica
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Python Data Analysis](https://pandas.pydata.org/)

### Estándares de la Industria
- [ISO 15178] - Telematics and Vehicle Data
- [SAE J1939] - Heavy Vehicle Data Bus
- [OBD-II Standards] - On-Board Diagnostics

### Investigación y Benchmarking
- [Fleet Management Best Practices](https://www.fleetmanagement.com/)
- [Fuel Efficiency Standards](https://www.epa.gov/)
- [Telematics Industry Reports](https://www.telematics-update.com/)
