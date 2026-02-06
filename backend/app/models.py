"""
Pydantic models for request/response validation.

Pydantic is a library that validates data using Python type hints.
It ensures that the data sent to and from the API has the correct format.
"""

from pydantic import BaseModel, Field
from typing import Optional


class VehicleData(BaseModel):
    """Data for a single vehicle in the report."""
    placa: str = Field(..., description="Vehicle license plate")
    distancia_km: float = Field(..., description="Distance traveled in km")
    consumo_litros: float = Field(..., description="Fuel consumption in liters")
    excesos_velocidad: int = Field(..., description="Number of speed violations")


class Indicators(BaseModel):
    """Aggregated fleet indicators."""
    distancia_total_km: float
    consumo_total_litros: float
    excesos_velocidad: int
    tiempo_ralenti_minutos: float
    frenadas_bruscas: int


class TelematicsReport(BaseModel):
    """The full telematics report structure."""
    cliente: str = Field(..., description="Client company name")
    periodo: str = Field(..., description="Report period")
    indicadores: Indicators
    vehiculos: list[VehicleData]


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
