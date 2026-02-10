"""
Utility functions for the fleet telemetry analysis system.

Provides common helpers for date parsing, distance calculations,
unit conversions, and statistical operations.
"""

from __future__ import annotations

import math
import uuid
from datetime import datetime
from typing import Optional, Sequence


# --- Constants ---

LITERS_PER_GALLON = 3.78541
EARTH_RADIUS_KM = 6371.0


# --- Unit Conversions ---

def liters_to_gallons(liters: float) -> float:
    """Convert liters to US gallons."""
    return liters / LITERS_PER_GALLON


def km_per_gallon(distance_km: float, fuel_liters: float) -> float:
    """Calculate fuel efficiency in km/gallon. Returns 0 if fuel is zero."""
    if fuel_liters <= 0:
        return 0.0
    gallons = liters_to_gallons(fuel_liters)
    return distance_km / gallons if gallons > 0 else 0.0


# --- Date Helpers ---

def parse_iso_date(date_str: str) -> Optional[datetime]:
    """Parse an ISO 8601 date string into a datetime object. Returns None on failure."""
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def format_period(start: str, end: str) -> str:
    """Format a period string from two ISO date strings."""
    s = parse_iso_date(start)
    e = parse_iso_date(end)
    if s and e:
        return f"{s.strftime('%Y-%m-%d')} → {e.strftime('%Y-%m-%d')}"
    return f"{start} → {end}"


# --- Statistics ---

def mean(values: Sequence[float]) -> float:
    """Calculate the arithmetic mean. Returns 0 for empty sequences."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def std_dev(values: Sequence[float]) -> float:
    """Calculate the population standard deviation."""
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def percent_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change from old to new. Returns 0 if old is zero."""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / abs(old_value)) * 100.0


def deviation_percent(expected: float, actual: float) -> float:
    """Calculate deviation percentage of actual vs expected."""
    if expected == 0:
        return 0.0
    return ((actual - expected) / abs(expected)) * 100.0


# --- Geo Helpers ---

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in km."""
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def locations_are_close(lat1: float, lon1: float, lat2: float, lon2: float, threshold_km: float = 1.0) -> bool:
    """Check if two geographic points are within a threshold distance."""
    return haversine_distance(lat1, lon1, lat2, lon2) <= threshold_km


# --- ID Generation ---

def generate_id(prefix: str = "ANM") -> str:
    """Generate a short unique identifier with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
