"""
Unit tests for the data validation module.
"""

import pytest

from src.validators.data_validator import DataValidator


def _make_minimal_report() -> dict:
    """Create a minimal valid report for testing."""
    return {
        "report_id": "RPT-TEST-001",
        "provider": "Test Provider",
        "client": "Test Client",
        "period_start": "2025-01-01T00:00:00-05:00",
        "period_end": "2025-01-31T23:59:59-05:00",
        "generated_at": "2025-02-01T08:00:00-05:00",
        "vehicles": [
            {
                "vehicle_id": "V-001",
                "tank_capacity_liters": 400,
                "fuel_events": [
                    {
                        "event_id": "E-001",
                        "event_type": "load",
                        "timestamp": "2025-01-02T06:30:00-05:00",
                        "volume_liters": 350,
                        "fuel_level_before": 50,
                        "fuel_level_after": 400,
                        "engine_running": False,
                        "odometer_km": 120500,
                    }
                ],
                "fuel_summary": {
                    "total_fuel_loaded_liters": 350,
                    "total_fuel_consumed_liters": 100,
                    "expected_consumption_liters": 110,
                    "number_of_loads": 1,
                    "number_of_discharges": 0,
                },
                "performance": {
                    "distance_km": 500,
                    "fuel_consumed_liters": 100,
                    "performance_km_per_gallon": 18.9,
                    "number_of_trips": 3,
                    "total_engine_hours": 20,
                    "idle_hours": 2,
                },
            }
        ],
    }


class TestDataValidator:
    """Tests for DataValidator."""

    def setup_method(self) -> None:
        self.validator = DataValidator()

    def test_valid_report(self) -> None:
        data = _make_minimal_report()
        result = self.validator.validate(data)
        assert result.status == "valid"
        assert len(result.errors) == 0

    def test_missing_required_key(self) -> None:
        data = _make_minimal_report()
        del data["report_id"]
        result = self.validator.validate(data)
        assert result.status == "invalid"
        assert any("report_id" in e.field for e in result.errors)

    def test_malformed_date(self) -> None:
        data = _make_minimal_report()
        data["period_start"] = "not-a-date"
        result = self.validator.validate(data)
        assert result.status == "invalid"
        assert any("period_start" in e.field for e in result.errors)

    def test_duplicate_vehicle_ids(self) -> None:
        data = _make_minimal_report()
        data["vehicles"].append(data["vehicles"][0].copy())
        result = self.validator.validate(data)
        assert any("Duplicate" in e.message for e in result.errors)

    def test_negative_volume(self) -> None:
        data = _make_minimal_report()
        data["vehicles"][0]["fuel_events"][0]["volume_liters"] = -50
        result = self.validator.validate(data)
        assert any("Negative" in e.message for e in result.errors)

    def test_empty_vehicles(self) -> None:
        data = _make_minimal_report()
        data["vehicles"] = []
        result = self.validator.validate(data)
        assert result.status == "invalid"

    def test_load_count_mismatch_warning(self) -> None:
        data = _make_minimal_report()
        data["vehicles"][0]["fuel_summary"]["number_of_loads"] = 5
        result = self.validator.validate(data)
        assert any("Load count mismatch" in w.message for w in result.warnings)

    def test_volume_mismatch_warning(self) -> None:
        data = _make_minimal_report()
        data["vehicles"][0]["fuel_events"][0]["volume_liters"] = 200
        result = self.validator.validate(data)
        assert any("Volume mismatch" in w.message for w in result.warnings)
