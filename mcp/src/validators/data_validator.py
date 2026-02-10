"""
Data validation module for fleet telemetry reports.

Validates JSON structure, detects inconsistencies such as negative values,
out-of-range consumption, subtotal mismatches, duplicate units, and
malformed dates.
"""

from __future__ import annotations

from typing import Any

from src.models.telemetry import (
    AlertLevel,
    TelemetryReport,
    ValidationIssue,
    ValidationResult,
    VehicleData,
)
from src.utils.helpers import parse_iso_date


# --- Required top-level keys ---

REQUIRED_REPORT_KEYS = {
    "report_id", "provider", "client", "period_start",
    "period_end", "generated_at", "vehicles",
}

REQUIRED_VEHICLE_KEYS = {
    "vehicle_id", "tank_capacity_liters", "fuel_events",
    "fuel_summary", "performance",
}

REQUIRED_EVENT_KEYS = {
    "event_id", "event_type", "timestamp", "volume_liters",
    "fuel_level_before", "fuel_level_after", "engine_running", "odometer_km",
}


class DataValidator:
    """Validates a telemetry report for structural and logical correctness."""

    def __init__(self) -> None:
        self._errors: list[ValidationIssue] = []
        self._warnings: list[ValidationIssue] = []

    # --- Public API ---

    def validate(self, raw_data: dict[str, Any]) -> ValidationResult:
        """Run all validations on raw JSON data and return a ValidationResult."""
        self._errors = []
        self._warnings = []

        self._check_required_keys(raw_data, REQUIRED_REPORT_KEYS, "report")
        self._check_dates(raw_data)

        vehicles = raw_data.get("vehicles", [])
        if not isinstance(vehicles, list) or len(vehicles) == 0:
            self._add_error("vehicles", "Report must contain at least one vehicle.")
            return self._build_result()

        self._check_duplicate_vehicles(vehicles)

        for idx, vehicle in enumerate(vehicles):
            self._validate_vehicle(vehicle, idx)

        return self._build_result()

    def validate_parsed(self, report: TelemetryReport) -> ValidationResult:
        """Run logical validations on an already-parsed TelemetryReport model."""
        self._errors = []
        self._warnings = []

        self._check_period_order(report.period_start, report.period_end)

        for vehicle in report.vehicles:
            self._validate_vehicle_logic(vehicle)

        return self._build_result()

    # --- Structural Checks ---

    def _check_required_keys(
        self, data: dict[str, Any], required: set[str], context: str
    ) -> None:
        missing = required - set(data.keys())
        for key in missing:
            self._add_error(key, f"Missing required key '{key}' in {context}.")

    def _check_dates(self, data: dict[str, Any]) -> None:
        for field in ("period_start", "period_end", "generated_at"):
            val = data.get(field)
            if val and parse_iso_date(str(val)) is None:
                self._add_error(field, f"Malformed date in '{field}': {val}")

    def _check_duplicate_vehicles(self, vehicles: list[dict[str, Any]]) -> None:
        seen_ids: set[str] = set()
        for v in vehicles:
            vid = v.get("vehicle_id", "")
            if vid in seen_ids:
                self._add_error("vehicle_id", f"Duplicate vehicle_id: {vid}")
            seen_ids.add(vid)

    # --- Per-Vehicle Structural Checks ---

    def _validate_vehicle(self, vehicle: dict[str, Any], idx: int) -> None:
        vid = vehicle.get("vehicle_id", f"vehicle[{idx}]")
        self._check_required_keys(vehicle, REQUIRED_VEHICLE_KEYS, f"vehicle '{vid}'")

        tank = vehicle.get("tank_capacity_liters", 0)
        if isinstance(tank, (int, float)) and tank <= 0:
            self._add_error("tank_capacity_liters", f"Tank capacity must be > 0 for {vid}.", vid)

        for eidx, event in enumerate(vehicle.get("fuel_events", [])):
            self._validate_event(event, vid, eidx)

        self._validate_fuel_summary(vehicle.get("fuel_summary", {}), vid, vehicle.get("fuel_events", []))
        self._validate_performance(vehicle.get("performance", {}), vid)

    def _validate_event(self, event: dict[str, Any], vid: str, eidx: int) -> None:
        eid = event.get("event_id", f"event[{eidx}]")
        self._check_required_keys(event, REQUIRED_EVENT_KEYS, f"event '{eid}' in vehicle '{vid}'")

        # Negative values
        for field in ("volume_liters", "fuel_level_before", "fuel_level_after", "odometer_km"):
            val = event.get(field)
            if isinstance(val, (int, float)) and val < 0:
                self._add_error(field, f"Negative value ({val}) in '{field}' for event {eid} of {vid}.", vid)

        # Timestamp format
        ts = event.get("timestamp")
        if ts and parse_iso_date(str(ts)) is None:
            self._add_error("timestamp", f"Malformed timestamp in event {eid} of {vid}: {ts}", vid)

        # Level consistency
        before = event.get("fuel_level_before", 0)
        after = event.get("fuel_level_after", 0)
        volume = event.get("volume_liters", 0)
        etype = event.get("event_type", "")

        if etype == "load" and after < before:
            self._add_warning("fuel_level_after", f"Load event {eid} in {vid} has lower level after than before.", vid)

        if etype == "discharge" and after > before:
            self._add_warning("fuel_level_after", f"Discharge event {eid} in {vid} has higher level after than before.", vid)

        if etype in ("load", "discharge"):
            expected_diff = abs(after - before)
            if abs(expected_diff - volume) > 1.0:
                self._add_warning(
                    "volume_liters",
                    f"Volume mismatch in event {eid} of {vid}: "
                    f"volume={volume}, level diff={expected_diff:.1f}.",
                    vid,
                )

    def _validate_fuel_summary(
        self, summary: dict[str, Any], vid: str, events: list[dict[str, Any]]
    ) -> None:
        if not summary:
            return

        # Count loads and discharges from events
        actual_loads = sum(1 for e in events if e.get("event_type") == "load")
        actual_discharges = sum(1 for e in events if e.get("event_type") == "discharge")
        reported_loads = summary.get("number_of_loads", 0)
        reported_discharges = summary.get("number_of_discharges", 0)

        if actual_loads != reported_loads:
            self._add_warning(
                "number_of_loads",
                f"Load count mismatch in {vid}: events={actual_loads}, summary={reported_loads}.",
                vid,
            )

        if actual_discharges != reported_discharges:
            self._add_warning(
                "number_of_discharges",
                f"Discharge count mismatch in {vid}: events={actual_discharges}, summary={reported_discharges}.",
                vid,
            )

        # Check totals vs event sums
        total_loaded_events = sum(
            e.get("volume_liters", 0) for e in events if e.get("event_type") == "load"
        )
        reported_loaded = summary.get("total_fuel_loaded_liters", 0)
        if abs(total_loaded_events - reported_loaded) > 2.0:
            self._add_warning(
                "total_fuel_loaded_liters",
                f"Total loaded mismatch in {vid}: events={total_loaded_events:.1f}, summary={reported_loaded}.",
                vid,
            )

        total_discharged_events = sum(
            e.get("volume_liters", 0) for e in events if e.get("event_type") == "discharge"
        )
        reported_discharged = summary.get("total_fuel_discharged_liters", 0)
        if abs(total_discharged_events - reported_discharged) > 2.0:
            self._add_warning(
                "total_fuel_discharged_liters",
                f"Total discharged mismatch in {vid}: events={total_discharged_events:.1f}, summary={reported_discharged}.",
                vid,
            )

    def _validate_performance(self, perf: dict[str, Any], vid: str) -> None:
        if not perf:
            return

        distance = perf.get("distance_km", 0)
        consumed = perf.get("fuel_consumed_liters", 0)

        if isinstance(distance, (int, float)) and distance < 0:
            self._add_error("distance_km", f"Negative distance in {vid}.", vid)

        if isinstance(consumed, (int, float)) and consumed < 0:
            self._add_error("fuel_consumed_liters", f"Negative consumption in {vid}.", vid)

        # Consumption out of range (> 1 liter per km is extremely high)
        if distance > 0 and consumed > 0:
            rate = consumed / distance
            if rate > 1.0:
                self._add_warning(
                    "fuel_consumed_liters",
                    f"Extremely high consumption rate in {vid}: {rate:.2f} L/km.",
                    vid,
                )

    # --- Logical Checks (parsed model) ---

    def _check_period_order(self, start: str, end: str) -> None:
        s = parse_iso_date(start)
        e = parse_iso_date(end)
        if s and e and s > e:
            self._add_error("period_start", "Period start is after period end.")

    def _validate_vehicle_logic(self, vehicle: VehicleData) -> None:
        vid = vehicle.vehicle_id
        tank = vehicle.tank_capacity_liters

        for event in vehicle.fuel_events:
            # Fuel level exceeding tank capacity
            if event.fuel_level_after > tank * 1.05:
                self._add_warning(
                    "fuel_level_after",
                    f"Fuel level ({event.fuel_level_after}L) exceeds tank capacity ({tank}L) "
                    f"in event {event.event_id} of {vid}.",
                    vid,
                )

            # Odometer regression is checked in the anomaly detector for sequential events

        # Deviation check
        summary = vehicle.fuel_summary
        dev = summary.consumption_deviation_liters
        expected = summary.expected_consumption_liters
        if expected > 0:
            dev_pct = abs(dev / expected) * 100
            if dev_pct > 20:
                self._add_warning(
                    "consumption_deviation_liters",
                    f"High consumption deviation ({dev_pct:.1f}%) in {vid}.",
                    vid,
                )

    # --- Helpers ---

    def _add_error(self, field: str, message: str, vehicle_id: str | None = None) -> None:
        self._errors.append(ValidationIssue(field=field, message=message, severity="error", vehicle_id=vehicle_id))

    def _add_warning(self, field: str, message: str, vehicle_id: str | None = None) -> None:
        self._warnings.append(ValidationIssue(field=field, message=message, severity="warning", vehicle_id=vehicle_id))

    def _build_result(self) -> ValidationResult:
        status = "invalid" if self._errors else "valid"
        return ValidationResult(status=status, errors=self._errors, warnings=self._warnings)
