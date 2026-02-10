"""
Pydantic models for fleet telemetry data ingestion and validation.

These models represent the structured JSON data received from telemetry
providers (Empresa A) and fleet clients (TransLogística S.A.).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class AlertLevel(str, Enum):
    """Severity levels for generated alerts."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    CRITICAL = "critical"


class FuelEventType(str, Enum):
    """Types of fuel events detected by sensors."""
    LOAD = "load"
    DISCHARGE = "discharge"
    CONSUMPTION = "consumption"
    IDLE = "idle"


class GeoLocation(BaseModel):
    """Geographic coordinates for an event or reading."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, description="Human-readable address if available")


class FuelEvent(BaseModel):
    """A single fuel event recorded by the sensor."""
    event_id: str = Field(..., description="Unique identifier for the event")
    event_type: FuelEventType = Field(..., description="Type of fuel event")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the event")
    volume_liters: float = Field(..., description="Volume of fuel involved in liters")
    fuel_level_before: float = Field(..., ge=0, description="Fuel level before event in liters")
    fuel_level_after: float = Field(..., ge=0, description="Fuel level after event in liters")
    location: Optional[GeoLocation] = Field(None, description="Location where the event occurred")
    engine_running: bool = Field(True, description="Whether the engine was running during the event")
    odometer_km: float = Field(..., ge=0, description="Odometer reading in kilometers")

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate that the timestamp is a parseable ISO 8601 string."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid ISO 8601 timestamp: {v}")
        return v


class FuelSummary(BaseModel):
    """Aggregated fuel metrics for a reporting period."""
    total_fuel_loaded_liters: float = Field(..., ge=0, description="Total fuel loaded in liters")
    total_fuel_consumed_liters: float = Field(..., ge=0, description="Total fuel consumed in liters")
    total_fuel_discharged_liters: float = Field(0, ge=0, description="Total fuel discharged in liters")
    expected_consumption_liters: float = Field(..., ge=0, description="Expected consumption based on distance and baseline")
    consumption_deviation_liters: float = Field(0, description="Difference between real and expected consumption")
    average_fuel_level_liters: float = Field(0, ge=0, description="Average fuel level during the period")
    number_of_loads: int = Field(0, ge=0, description="Number of fuel load events")
    number_of_discharges: int = Field(0, ge=0, description="Number of fuel discharge events")


class PerformanceMetrics(BaseModel):
    """Vehicle performance metrics for a reporting period."""
    distance_km: float = Field(..., ge=0, description="Total distance traveled in km")
    fuel_consumed_liters: float = Field(..., ge=0, description="Total fuel consumed in liters")
    performance_km_per_gallon: float = Field(0, ge=0, description="Fuel efficiency in km/gallon")
    previous_performance_km_per_gallon: Optional[float] = Field(None, ge=0, description="Previous period performance")
    performance_variation_percent: Optional[float] = Field(None, description="Percent change from previous period")
    number_of_trips: int = Field(0, ge=0, description="Number of trips in the period")
    total_engine_hours: float = Field(0, ge=0, description="Total engine running hours")
    idle_hours: float = Field(0, ge=0, description="Total idle hours")


class VehicleData(BaseModel):
    """Complete telemetry data for a single vehicle in a reporting period."""
    vehicle_id: str = Field(..., description="Unique vehicle identifier (e.g., plate number)")
    vehicle_name: Optional[str] = Field(None, description="Human-readable vehicle name or alias")
    vehicle_type: Optional[str] = Field(None, description="Type of vehicle (truck, van, etc.)")
    tank_capacity_liters: float = Field(..., gt=0, description="Maximum fuel tank capacity in liters")
    fuel_events: list[FuelEvent] = Field(default_factory=list, description="List of fuel events")
    fuel_summary: FuelSummary = Field(..., description="Aggregated fuel summary")
    performance: PerformanceMetrics = Field(..., description="Performance metrics")
    sensor_id: Optional[str] = Field(None, description="Fuel sensor identifier")
    routes: list[str] = Field(default_factory=list, description="Routes assigned or traveled")


class TelemetryReport(BaseModel):
    """Top-level telemetry report from a data provider for a specific client."""
    report_id: str = Field(..., description="Unique report identifier")
    provider: str = Field(..., description="Data provider name (e.g., 'Empresa A')")
    client: str = Field(..., description="Client company name (e.g., 'TransLogística S.A.')")
    period_start: str = Field(..., description="Start of reporting period (ISO 8601)")
    period_end: str = Field(..., description="End of reporting period (ISO 8601)")
    generated_at: str = Field(..., description="Report generation timestamp (ISO 8601)")
    vehicles: list[VehicleData] = Field(default_factory=list, description="Vehicle telemetry data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("period_start", "period_end", "generated_at")
    @classmethod
    def validate_dates(cls, v: str) -> str:
        """Validate date fields are parseable."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid ISO 8601 date: {v}")
        return v


# --- Output / Result Models ---

class ValidationIssue(BaseModel):
    """A single validation error or warning."""
    field: str = Field(..., description="Field path where the issue was found")
    message: str = Field(..., description="Description of the issue")
    severity: str = Field("error", description="'error' or 'warning'")
    vehicle_id: Optional[str] = Field(None, description="Related vehicle if applicable")


class ValidationResult(BaseModel):
    """Result of validating a telemetry report."""
    status: str = Field(..., description="'valid' or 'invalid'")
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)


class AnomalyFinding(BaseModel):
    """A detected anomaly in the telemetry data."""
    anomaly_id: str = Field(..., description="Unique anomaly identifier")
    category: str = Field(..., description="Category: discharge, unauthorized_load, sensor, temporal_pattern")
    severity: AlertLevel = Field(..., description="Severity level")
    vehicle_id: str = Field(..., description="Affected vehicle")
    description: str = Field(..., description="Human-readable description")
    evidence: dict[str, Any] = Field(default_factory=dict, description="Supporting data")
    possible_causes: list[str] = Field(default_factory=list, description="Possible root causes")
    recommendation: str = Field("", description="Recommended action")


class PerformanceAlert(BaseModel):
    """An alert generated from performance analysis."""
    vehicle_id: str
    alert_level: AlertLevel
    metric: str
    current_value: float
    expected_value: float
    deviation_percent: float
    message: str


class ComparisonResult(BaseModel):
    """Result of comparing data between two sources."""
    metric: str
    provider_a_value: float
    provider_b_value: float
    difference: float
    difference_percent: float
    is_coherent: bool
    note: str = ""


class FinalReport(BaseModel):
    """The complete analysis report returned to the user."""
    client: str
    period: str
    validation: ValidationResult
    key_findings: list[str] = Field(default_factory=list)
    performance_alerts: list[PerformanceAlert] = Field(default_factory=list)
    anomalies: list[AnomalyFinding] = Field(default_factory=list)
    critical_vehicles: list[dict[str, Any]] = Field(default_factory=list)
    comparison: list[ComparisonResult] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    executive_summary: str = ""
