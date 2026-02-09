"""
Pydantic models for request/response validation.

Pydantic is a library that validates data using Python type hints.
It ensures that the data sent to and from the API has the correct format.

This model reflects real telematics report data from fleet management
systems like Wialon, including fuel anomalies, unauthorized loads,
and per-vehicle performance metrics.
"""

from pydantic import BaseModel, Field
from typing import Optional


class FuelAnomaly(BaseModel):
    """A single fuel anomaly event (suspected unauthorized discharge)."""
    unidad: str = Field(..., description="Vehicle plate")
    ubicacion_inicial: str = Field(default="", description="Start location")
    ubicacion_final: str = Field(default="", description="End location")
    tanque: str = Field(default="", description="Tank affected (izquierdo, derecho, total)")
    cantidad_gal: float = Field(..., description="Gallons lost in event")


class UnauthorizedLoad(BaseModel):
    """A fuel load at a non-authorized location."""
    unidad: str = Field(..., description="Vehicle plate")
    ubicacion: str = Field(default="", description="Location of unauthorized load")
    cantidad_gal: float = Field(..., description="Gallons loaded")
    num_cargas: int = Field(default=1, description="Number of load events")


class FleetAverages(BaseModel):
    """Aggregated fleet-level metrics."""
    viajes_totales: int = Field(default=0, description="Total trips")
    consumo_viajes_gal: float = Field(default=0, description="Fuel consumed in trips (gal)")
    consumo_movimiento_gal: float = Field(default=0, description="Fuel consumed while moving (gal)")
    consumo_sin_movimiento_gal: float = Field(default=0, description="Fuel consumed while idle (gal)")
    horas_motor_encendido: float = Field(default=0, description="Engine-on hours")
    total_llenados: int = Field(default=0, description="Total authorized fuel loads")
    total_descargas: int = Field(default=0, description="Total suspected discharges")
    distancia_total_km: float = Field(default=0, description="Total distance in km")


class FuelPerformance(BaseModel):
    """Fuel efficiency and comparison metrics."""
    rendimiento_actual_km_gal: float = Field(default=0, description="Current fuel efficiency km/gal")
    rendimiento_anterior_km_gal: float = Field(default=0, description="Previous week fuel efficiency")
    consumo_total_gal: float = Field(default=0, description="Total fuel consumed this period (gal)")
    consumo_semana_anterior_gal: float = Field(default=0, description="Previous week consumption")
    consumo_esperado_gal: float = Field(default=0, description="Expected consumption based on previous efficiency")
    desviacion_gal: float = Field(default=0, description="Deviation from expected consumption")


class VehicleAnomaly(BaseModel):
    """Summary of anomalies per vehicle."""
    unidad: str = Field(..., description="Vehicle plate")
    eventos_descarga: int = Field(default=0, description="Number of discharge events")
    total_descarga_gal: float = Field(default=0, description="Total gallons discharged")
    eventos_carga_no_autorizada: int = Field(default=0, description="Unauthorized load events")
    total_carga_no_autorizada_gal: float = Field(default=0, description="Gallons loaded at unauthorized sites")


class TelematicsReport(BaseModel):
    """
    The full telematics report structure.
    Accepts flexible JSON — all fields except 'cliente' and 'periodo' are optional.
    """
    cliente: str = Field(..., description="Client company name")
    periodo: str = Field(..., description="Report period")
    promedios_flota: Optional[FleetAverages] = None
    rendimiento: Optional[FuelPerformance] = None
    anomalias_combustible: Optional[list[FuelAnomaly]] = None
    cargas_no_autorizadas: Optional[list[UnauthorizedLoad]] = None
    resumen_vehiculos: Optional[list[VehicleAnomaly]] = None


class InterpretRequest(BaseModel):
    """Request body for the interpret endpoint."""
    report: TelematicsReport = Field(..., description="The telematics report data")
    profile: str = Field(
        ...,
        description="User profile: 'gerente' or 'operaciones'",
        pattern="^(gerente|operaciones)$"
    )


class InterpretResponse(BaseModel):
    """Response from the interpret endpoint."""
    profile: str
    interpretation: str
    model_used: str
    tokens_used: Optional[int] = None
