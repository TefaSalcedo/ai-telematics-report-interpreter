"""
Performance analysis module for fleet telemetry data.

Calculates fuel efficiency metrics, detects deviations from expected
consumption, and generates performance alerts based on business rules.

Business rules:
  - Deviation > 10% from expected → yellow alert
  - Deviation > 20% from expected → red alert
  - Sustained performance drop for 2+ periods → critical anomaly
"""

from __future__ import annotations

from src.models.telemetry import (
    AlertLevel,
    PerformanceAlert,
    TelemetryReport,
    VehicleData,
)
from src.utils.helpers import (
    deviation_percent,
    km_per_gallon,
    percent_change,
)


class PerformanceAnalyzer:
    """Analyzes fuel performance metrics for each vehicle in a report."""

    YELLOW_THRESHOLD_PCT = 10.0
    RED_THRESHOLD_PCT = 20.0

    def analyze(self, report: TelemetryReport) -> list[PerformanceAlert]:
        """Analyze all vehicles and return a list of performance alerts."""
        alerts: list[PerformanceAlert] = []
        for vehicle in report.vehicles:
            alerts.extend(self._analyze_vehicle(vehicle))
        return alerts

    # --- Per-Vehicle Analysis ---

    def _analyze_vehicle(self, vehicle: VehicleData) -> list[PerformanceAlert]:
        alerts: list[PerformanceAlert] = []
        vid = vehicle.vehicle_id
        perf = vehicle.performance
        summary = vehicle.fuel_summary

        # 1. Consumption deviation vs expected
        expected = summary.expected_consumption_liters
        actual = summary.total_fuel_consumed_liters
        if expected > 0:
            dev_pct = deviation_percent(expected, actual)
            abs_dev = abs(dev_pct)

            if abs_dev > self.RED_THRESHOLD_PCT:
                level = AlertLevel.RED
            elif abs_dev > self.YELLOW_THRESHOLD_PCT:
                level = AlertLevel.YELLOW
            else:
                level = AlertLevel.GREEN

            if level != AlertLevel.GREEN:
                alerts.append(PerformanceAlert(
                    vehicle_id=vid,
                    alert_level=level,
                    metric="consumption_deviation",
                    current_value=actual,
                    expected_value=expected,
                    deviation_percent=round(dev_pct, 2),
                    message=(
                        f"Vehículo {vid}: desviación de consumo de {dev_pct:+.1f}% "
                        f"(real={actual:.1f}L vs esperado={expected:.1f}L)."
                    ),
                ))

        # 2. Performance variation vs previous period
        current_kpg = perf.performance_km_per_gallon
        previous_kpg = perf.previous_performance_km_per_gallon

        if previous_kpg is not None and previous_kpg > 0:
            variation = percent_change(previous_kpg, current_kpg)
            abs_var = abs(variation)

            if abs_var > self.RED_THRESHOLD_PCT:
                level = AlertLevel.RED
            elif abs_var > self.YELLOW_THRESHOLD_PCT:
                level = AlertLevel.YELLOW
            else:
                level = AlertLevel.GREEN

            if level != AlertLevel.GREEN:
                alerts.append(PerformanceAlert(
                    vehicle_id=vid,
                    alert_level=level,
                    metric="performance_variation",
                    current_value=current_kpg,
                    expected_value=previous_kpg,
                    deviation_percent=round(variation, 2),
                    message=(
                        f"Vehículo {vid}: rendimiento cambió {variation:+.1f}% "
                        f"({current_kpg:.1f} km/gal vs anterior {previous_kpg:.1f} km/gal)."
                    ),
                ))

        # 3. Recalculate km/gal from raw data and compare with reported
        if perf.fuel_consumed_liters > 0:
            calculated_kpg = km_per_gallon(perf.distance_km, perf.fuel_consumed_liters)
            reported_kpg = perf.performance_km_per_gallon
            if reported_kpg > 0:
                kpg_diff = percent_change(calculated_kpg, reported_kpg)
                if abs(kpg_diff) > 5.0:
                    alerts.append(PerformanceAlert(
                        vehicle_id=vid,
                        alert_level=AlertLevel.YELLOW,
                        metric="reported_vs_calculated_kpg",
                        current_value=reported_kpg,
                        expected_value=round(calculated_kpg, 2),
                        deviation_percent=round(kpg_diff, 2),
                        message=(
                            f"Vehículo {vid}: rendimiento reportado ({reported_kpg:.1f} km/gal) "
                            f"difiere del calculado ({calculated_kpg:.1f} km/gal) en {kpg_diff:+.1f}%."
                        ),
                    ))

        # 4. High idle ratio
        if perf.total_engine_hours > 0:
            idle_ratio = perf.idle_hours / perf.total_engine_hours
            if idle_ratio > 0.30:
                alerts.append(PerformanceAlert(
                    vehicle_id=vid,
                    alert_level=AlertLevel.YELLOW,
                    metric="idle_ratio",
                    current_value=round(idle_ratio * 100, 1),
                    expected_value=30.0,
                    deviation_percent=round((idle_ratio - 0.30) / 0.30 * 100, 1),
                    message=(
                        f"Vehículo {vid}: ratio de ralentí alto ({idle_ratio * 100:.1f}% del tiempo de motor)."
                    ),
                ))

        # 5. Low distance with high consumption
        if perf.distance_km > 0 and perf.fuel_consumed_liters > 0:
            liters_per_km = perf.fuel_consumed_liters / perf.distance_km
            if liters_per_km > 0.5:
                alerts.append(PerformanceAlert(
                    vehicle_id=vid,
                    alert_level=AlertLevel.RED,
                    metric="high_consumption_low_distance",
                    current_value=round(liters_per_km, 3),
                    expected_value=0.5,
                    deviation_percent=round((liters_per_km - 0.5) / 0.5 * 100, 1),
                    message=(
                        f"Vehículo {vid}: consumo excesivo ({liters_per_km:.3f} L/km). "
                        f"Posible falla mecánica o datos incorrectos."
                    ),
                ))

        return alerts
