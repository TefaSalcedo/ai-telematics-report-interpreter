"""
Unit tests for utility functions.
"""

import pytest

from src.utils.helpers import (
    deviation_percent,
    haversine_distance,
    km_per_gallon,
    liters_to_gallons,
    locations_are_close,
    mean,
    parse_iso_date,
    percent_change,
    std_dev,
)


class TestUnitConversions:
    def test_liters_to_gallons(self) -> None:
        assert abs(liters_to_gallons(3.78541) - 1.0) < 0.001

    def test_km_per_gallon(self) -> None:
        result = km_per_gallon(100, 37.8541)
        assert result > 0

    def test_km_per_gallon_zero_fuel(self) -> None:
        assert km_per_gallon(100, 0) == 0.0


class TestDateHelpers:
    def test_parse_valid_date(self) -> None:
        dt = parse_iso_date("2025-01-01T00:00:00-05:00")
        assert dt is not None
        assert dt.year == 2025

    def test_parse_invalid_date(self) -> None:
        assert parse_iso_date("not-a-date") is None

    def test_parse_utc_z(self) -> None:
        dt = parse_iso_date("2025-01-01T00:00:00Z")
        assert dt is not None


class TestStatistics:
    def test_mean(self) -> None:
        assert mean([1, 2, 3, 4, 5]) == 3.0

    def test_mean_empty(self) -> None:
        assert mean([]) == 0.0

    def test_std_dev(self) -> None:
        result = std_dev([2, 4, 4, 4, 5, 5, 7, 9])
        assert abs(result - 2.0) < 0.1

    def test_percent_change(self) -> None:
        assert percent_change(100, 110) == 10.0

    def test_percent_change_zero(self) -> None:
        assert percent_change(0, 100) == 0.0

    def test_deviation_percent(self) -> None:
        assert deviation_percent(100, 120) == 20.0


class TestGeoHelpers:
    def test_haversine_same_point(self) -> None:
        assert haversine_distance(4.711, -74.072, 4.711, -74.072) == 0.0

    def test_haversine_known_distance(self) -> None:
        # Bogotá to Bucaramanga ~ 300 km straight line
        dist = haversine_distance(4.711, -74.072, 7.125, -73.120)
        assert 250 < dist < 350

    def test_locations_close(self) -> None:
        assert locations_are_close(4.711, -74.072, 4.711, -74.072)

    def test_locations_far(self) -> None:
        assert not locations_are_close(4.711, -74.072, 7.125, -73.120)
